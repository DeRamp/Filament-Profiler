#!/usr/bin/env python3
"""Build a Bambu Studio project (.3mf) of labeled test parts from a test plan.

Each test plan in test-plans/*.json lists plates; each plate holds one or more
variants. Every printed part has its variant code and specimen number engraved
on it, and the per-part settings (line width, layer height, walls, brim...)
are stored as Bambu Studio per-object settings.

Nozzle temperature cannot be set per part or per plate in Bambu Studio, so
temperature plates say the temperature to use in the plate name and on the
parts. Set it in the filament settings before slicing that plate.

Usage:
    python tools/build_test_plates.py test-plans/overture-super-pla-plus__0.4.json
    python tools/build_test_plates.py --all

Outputs, per plan, in test-plates/<plan id>/:
    <plan id>.3mf           all plates in one project
    plates/<n>_<name>.3mf   each plate on its own (fallback)
    README.md               what is on each plate and how to log it
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_models as gm  # noqa: E402
from text3d import engrave_side, engrave_top  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
APP = "BambuStudio-01.09.00.70"
BED = (256.0, 256.0)  # assumed bed size used to lay out plates
PLATE_GAP = 0.2       # Bambu Studio spaces plates by 20% of the bed size
DEPTH = 0.5           # label engraving depth, mm
COPIES = 5            # specimens per adhesion setting (protocol FP-A)

# per-object settings every FP-A specimen gets (protocol 00-overview "Fixed print settings")
FPA_FIXED = {"wall_loops": "99", "brim_type": "outer_only", "brim_width": "5",
             "seam_position": "aligned"}
ACC_FIXED = {"wall_loops": "3", "sparse_infill_density": "15%", "brim_type": "no_brim"}
LINE_KEYS = ["line_width", "outer_wall_line_width", "inner_wall_line_width",
             "sparse_infill_line_width", "internal_solid_infill_line_width",
             "top_surface_line_width"]


# ------------------------------------------------------------------ geometry

def specimen(code: str, n: int, short: str, tpu: bool) -> gm.Manifold:
    """FP-A specimen with the variant code on the front of the bottom tab and
    'short n' on the back. Labels are inside the bottom tab, clear of the gauge."""
    a = gm.SPEC["adhesion"]
    body = gm.adhesion_specimen(tpu=tpu)
    tt = a["tab_t"]
    zc = a["bottom_tab_h"] / 2 + 0.5
    cut = engrave_side(code, 0, zc, -tt / 2, 4.0, DEPTH, front=True, max_w=a["tab_w"] - 2.5)
    cut += engrave_side(f"{short} {n}", 0, zc, tt / 2, 3.2, DEPTH, front=False, max_w=a["tab_w"] - 2.5)
    return body - cut


def tagged(body: gm.Manifold, text: str, tag_h: float = 10.0, t: float = 4.0) -> gm.Manifold:
    """Add a strip along the -Y edge of a flat part with `text` engraved on top."""
    (x0, y0, _, x1, _, _) = body.bounding_box()
    strip = gm.box(x0, y0 - tag_h, 0, x1, y0 + 1.0, t)
    cut = engrave_top(text, (x0 + x1) / 2, y0 - tag_h / 2, t, 5.0, DEPTH, max_w=(x1 - x0) - 6)
    return (body + strip) - cut


def peg(text: str) -> gm.Manifold:
    """FP-F peg on a labeled rectangular base (the base doubles as the grip)."""
    f = gm.SPEC["fit"]
    d, h, ch = f["nominal_d"], f["peg_h"], f["chamfer"]
    base_w, base_d, base_t = 40.0, 18.0, 4.0
    px = -base_w / 2 + base_d / 2
    base = gm.box(-base_w / 2, -base_d / 2, 0, base_w / 2, base_d / 2, base_t)
    shaft = gm.union([gm.cyl(d, h - ch, base_t, px, 0),
                      gm.cone(d, d - 2 * ch, ch, base_t + h - ch, px, 0)])
    tx = (px + d / 2 + base_w / 2) / 2
    cut = engrave_top(text, tx, 0, base_t, 4.0, DEPTH, max_w=(base_w / 2 - (px + d / 2)) - 4)
    return (base - cut) + shaft


# ------------------------------------------------------------------ settings

def object_settings(plan: dict, plate: dict, variant: dict) -> dict:
    s = dict(FPA_FIXED if plate["test"] == "adhesion" else ACC_FIXED)
    merged = {**plan["baseline"], **variant.get("settings", {})}
    s["layer_height"] = f"{merged['layer_height']:g}"
    for k in LINE_KEYS:
        s[k] = f"{merged['line_width']:g}"
    return s


# ------------------------------------------------------------------ 3MF

def mesh_xml(m: gm.Manifold) -> tuple[str, np.ndarray]:
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].astype(float)
    t = np.asarray(mesh.tri_verts)
    lo, hi = v.min(0), v.max(0)
    shift = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    v = v + shift
    verts = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in v)
    tris = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t)
    return f"<mesh><vertices>{verts}</vertices><triangles>{tris}</triangles></mesh>", hi - lo


def plate_origin(idx: int, count: int) -> tuple[float, float]:
    """Where Bambu Studio puts plate `idx` (0-based) when there are `count` plates."""
    v = count ** 0.5
    cols = int(round(v)) + (1 if v > round(v) else 0)
    row, col = divmod(idx, cols)
    return col * BED[0] * (1 + PLATE_GAP), -row * BED[1] * (1 + PLATE_GAP)


def write_3mf(path: Path, plates: list[dict]):
    """plates: [{name, objects: [{name, manifold, settings, x, y}]}] (x, y relative to the plate)."""
    core = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    prod = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
    files, rels, comps, items, cfg_objs, cfg_plates = {}, [], [], [], [], []
    oid = 0
    for pi, plate in enumerate(plates):
        ox, oy = plate_origin(pi, len(plates))
        inst = []
        for ob in plate["objects"]:
            oid += 1
            mesh_id, obj_id = 2 * oid - 1, 2 * oid
            assert gm.to_trimesh(ob["manifold"]).is_watertight, ob["name"]
            mx, _ = mesh_xml(ob["manifold"])
            fn = f"3D/Objects/object_{oid}.model"
            files[fn] = (
                f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<model unit="millimeter" xml:lang="en-US" xmlns="{core}" xmlns:p="{prod}" requiredextensions="p">'
                f'<metadata name="BambuStudio:3mfVersion">1</metadata><resources>'
                f'<object id="{mesh_id}" p:UUID="{uuid.uuid4()}" type="model">{mx}</object>'
                f'</resources><build/></model>')
            rels.append(f'<Relationship Target="/{fn}" Id="rel-{oid}" '
                        f'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>')
            comps.append(
                f'<object id="{obj_id}" p:UUID="{uuid.uuid4()}" type="model"><components>'
                f'<component p:path="/{fn}" objectid="{mesh_id}" p:UUID="{uuid.uuid4()}" '
                f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>')
            x, y = ox + ob["x"], oy + ob["y"]
            items.append(f'<item objectid="{obj_id}" p:UUID="{uuid.uuid4()}" '
                         f'transform="1 0 0 0 1 0 0 0 1 {x:.3f} {y:.3f} 0" printable="1"/>')
            meta = "".join(f'<metadata key="{k}" value="{v}"/>' for k, v in ob["settings"].items())
            cfg_objs.append(
                f'<object id="{obj_id}"><metadata key="name" value="{ob["name"]}"/>'
                f'<metadata key="extruder" value="1"/>{meta}'
                f'<part id="{mesh_id}" subtype="normal_part"><metadata key="name" value="{ob["name"]}"/>'
                f'<metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/></part></object>')
            inst.append(f'<model_instance><metadata key="object_id" value="{obj_id}"/>'
                        f'<metadata key="instance_id" value="0"/>'
                        f'<metadata key="identify_id" value="{100 + oid}"/></model_instance>')
        cfg_plates.append(
            f'<plate><metadata key="plater_id" value="{pi + 1}"/>'
            f'<metadata key="plater_name" value="{plate["name"]}"/>'
            f'<metadata key="locked" value="false"/>{"".join(inst)}</plate>')

    files["3D/3dmodel.model"] = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<model unit="millimeter" xml:lang="en-US" xmlns="{core}" '
        f'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="{prod}" requiredextensions="p">'
        f'<metadata name="Application">{APP}</metadata>'
        f'<metadata name="BambuStudio:3mfVersion">1</metadata>'
        f'<metadata name="Title">{path.stem}</metadata>'
        f'<resources>{"".join(comps)}</resources><build p:UUID="{uuid.uuid4()}">{"".join(items)}</build></model>')
    files["3D/_rels/3dmodel.model.rels"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(rels) + "</Relationships>")
    files["Metadata/model_settings.config"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>' + "".join(cfg_objs) + "".join(cfg_plates) + "</config>")
    files["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    files["[Content_Types].xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '<Default Extension="config" ContentType="text/xml"/></Types>')
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        order = ["[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "3D/_rels/3dmodel.model.rels"]
        for k in order + sorted(set(files) - set(order)):
            z.writestr(k, files[k])


# ------------------------------------------------------------------ layout

def build_plate(plan: dict, plate: dict) -> dict:
    tpu = plan.get("specimen") == "FP-A-T"
    short = plan["short"]
    objs = []
    cx, cy = BED[0] / 2, BED[1] / 2
    if plate["test"] == "adhesion":
        rows = plate["variants"]
        pitch_x, pitch_y = 30.0, 30.0
        for r, var in enumerate(rows):
            y = cy + (len(rows) - 1) / 2 * pitch_y - r * pitch_y
            for n in range(1, COPIES + 1):
                x = cx + (n - (COPIES + 1) / 2) * pitch_x
                objs.append({"name": f"{var['code']}-{n}", "manifold": specimen(var["code"], n, short, tpu),
                             "settings": object_settings(plan, plate, var), "x": x, "y": y})
    elif plate["test"] == "accuracy":
        var = plate["variants"][0]
        st = object_settings(plan, plate, var)
        nz = f"{plan['nozzle']:g}"
        objs += [
            {"name": f"FP-D {var['code']}", "manifold": tagged(gm.dimension_gauge(), f"FP-D {short} {nz} {var['code']}"),
             "settings": st, "x": cx, "y": cy + 45},
            {"name": f"FP-F plate {var['code']}", "manifold": tagged(gm.fit_plate(), f"FP-F {short} {var['code']}"),
             "settings": st, "x": cx - 25, "y": cy - 30},
            {"name": f"FP-F peg {var['code']}", "manifold": peg(f"{short}"),
             "settings": st, "x": cx + 70, "y": cy - 30},
        ]
    return {"name": plate["name"], "objects": objs}


def readme(plan: dict, out: Path) -> str:
    L = [f"# Test plates: {plan['filament']}, {plan['nozzle']:g} mm nozzle", "",
         f"Generated by `tools/build_test_plates.py` from `test-plans/{plan['id']}.json`. Do not edit by hand.", "",
         plan.get("notes", ""), "",
         f"Maker's range: nozzle {plan['maker_range']['nozzle_temp'][0]}-{plan['maker_range']['nozzle_temp'][1]} C, "
         f"bed {plan['maker_range']['bed_temp'][0]}-{plan['maker_range']['bed_temp'][1]} C "
         f"({plan['maker_range']['source']}).", "",
         f"Baseline: nozzle {plan['baseline']['nozzle_temp']} C, bed {plan['baseline']['bed_temp']} C, "
         f"layer {plan['baseline']['layer_height']} mm, line width {plan['baseline']['line_width']} mm.", "",
         "## Before you slice", "",
         "1. Open the `.3mf` in Bambu Studio and pick your printer, nozzle and the filament preset.",
         "2. **Set the nozzle temperature in the filament settings for each plate** to the value in the plate name. "
         "Bambu Studio cannot change temperature per plate, so this is the one manual step.",
         "3. Check the per-object settings in the object list (line width, layer height, wall loops, brim). "
         "They are already set; do not change them.",
         "4. Slice and print one plate at a time.", "",
         "## Plates", "",
         "| Plate | Nozzle temp | Parts | What changes |", "|---|---|---|---|"]
    for p in plan["plates"]:
        parts = (f"{len(p['variants']) * COPIES} x FP-A" if p["test"] == "adhesion" else "FP-D, FP-F plate, FP-F peg")
        desc = "; ".join(f"`{v['code']}` {v['desc']}" for v in p["variants"])
        L.append(f"| {p['name']} | {p['nozzle_temp']} C | {parts} | {desc} |")
    L += ["", "## Labels", "",
          "- FP-A specimens: variant code on the front of the bottom tab, filament and specimen number (1-5) on the back. "
          "The labels sit in the tab that goes in the vise, so they survive the pull.",
          "- FP-D and FP-F: a strip along one edge with the test, filament and variant. "
          "The strip is outside the measured features.",
          "", "Log results with the codes on the parts, for example `W150-3`, as described in `protocols/01-layer-adhesion.md`."]
    return "\n".join(L) + "\n"


def build(plan_path: Path):
    plan = json.loads(plan_path.read_text())
    out = ROOT / "test-plates" / plan["id"]
    plates = [build_plate(plan, p) for p in plan["plates"]]
    write_3mf(out / f"{plan['id']}.3mf", plates)
    for i, p in enumerate(plates):
        slug = re.sub(r"[^a-z0-9]+", "-", p["name"].lower()).strip("-")
        write_3mf(out / "plates" / f"{slug}.3mf", [p])
    (out / "README.md").write_text(readme(plan, out))
    n = sum(len(p["objects"]) for p in plates)
    print(f"{out.relative_to(ROOT)}: {len(plates)} plates, {n} parts")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plans", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    paths = sorted((ROOT / "test-plans").glob("*.json")) if a.all else [Path(p) for p in a.plans]
    if not paths:
        ap.error("give a plan file or --all")
    for p in paths:
        build(p)


if __name__ == "__main__":
    main()
