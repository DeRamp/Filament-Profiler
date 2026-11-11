#!/usr/bin/env python3
"""Generate the standard Filament Profiler test models as STL files.

Every dimension lives in the SPEC dict below, so the models are fully
parametric. Changing a value here changes the standard, so bump
SPEC["version"] whenever you do, and record that version with every result.

Usage:
    pip install manifold3d trimesh numpy
    python tools/generate_models.py            # writes models/stl/*.stl
    python tools/generate_models.py --out DIR
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold

SEG = 128  # circle resolution

SPEC = {
    "version": "1.0",
    # FP-A: layer adhesion (Z-tensile) specimen, printed standing up
    "adhesion": {
        "tab_w": 16.0,       # width of grip tabs (X)
        "tab_t": 6.0,        # thickness of grip tabs (Y)
        "gauge_w": 4.0,      # gauge section width (X)
        "gauge_t": 2.0,      # gauge section thickness (Y) -> area = 8 mm^2
        "gauge_w_tpu": 3.0,  # TPU variant (FP-A-T) -> area = 6 mm^2
        "bottom_tab_h": 15.0,
        "taper_h": 8.0,
        "gauge_h": 20.0,
        "top_tab_h": 20.0,
        "hole_d": 8.0,       # hook hole (teardrop, prints without supports)
    },
    # FP-F: fit gauge, one peg + one plate with graded holes
    "fit": {
        "nominal_d": 10.0,
        "clearances": [round(0.05 * i, 2) for i in range(11)],  # 0.00 .. 0.50 diametral
        "plate_t": 6.0,
        "pitch": 16.0,
        "peg_h": 20.0,
        "chamfer": 0.5,
    },
    # FP-D: dimensional accuracy gauge (holes + pegs of several sizes)
    "dimension": {
        "sizes": [3.0, 5.0, 8.0, 10.0, 15.0],
        "plate_l": 100.0,
        "plate_w": 50.0,
        "plate_t": 4.0,
        "peg_h": 10.0,
    },
    "label": {"h": 4.0, "w": 2.4, "stroke": 0.6, "depth": 0.6},
}

# ---------------------------------------------------------------- helpers

def box(x0, y0, z0, x1, y1, z1) -> Manifold:
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cyl(d, h, z0=0.0, x=0.0, y=0.0) -> Manifold:
    return Manifold.cylinder(h, d / 2, d / 2, SEG).translate((x, y, z0))


def cone(d0, d1, h, z0=0.0, x=0.0, y=0.0) -> Manifold:
    return Manifold.cylinder(h, d0 / 2, d1 / 2, SEG).translate((x, y, z0))


# seven-segment digits for engraved labels (no font dependency)
_SEGS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
}


def _digit(ch: str, x0: float, y0: float) -> list[Manifold]:
    L = SPEC["label"]
    w, h, s, dep = L["w"], L["h"], L["stroke"], L["depth"]
    hh = h / 2
    seg = {
        "a": (0, h - s, w, h), "g": (0, hh - s / 2, w, hh + s / 2), "d": (0, 0, w, s),
        "f": (0, hh, s, h), "b": (w - s, hh, w, h),
        "e": (0, 0, s, hh), "c": (w - s, 0, w, hh),
    }
    out = []
    if ch == ".":
        out.append(box(x0, y0, -dep, x0 + s, y0 + s, dep))
        return out
    for k in _SEGS[ch]:
        a, b, c, d = seg[k]
        out.append(box(x0 + a, y0 + b, -dep, x0 + c, y0 + d, dep))
    return out


def label(text: str, cx: float, cy: float, top_z: float) -> Manifold:
    """Engraving cutter for `text`, centred at (cx, cy), cutting down from top_z."""
    L = SPEC["label"]
    gap = 0.8
    widths = [L["stroke"] if c == "." else L["w"] for c in text]
    total = sum(widths) + gap * (len(text) - 1)
    x = cx - total / 2
    parts = []
    for c, wdt in zip(text, widths):
        parts += _digit(c, x, cy - L["h"] / 2)
        x += wdt + gap
    return Manifold.batch_boolean(parts, manifold3d_add()).translate((0, 0, top_z))


def manifold3d_add():
    from manifold3d import OpType
    return OpType.Add


def union(parts):
    return Manifold.batch_boolean(parts, manifold3d_add())


def to_trimesh(m: Manifold) -> trimesh.Trimesh:
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))


# ---------------------------------------------------------------- models

def adhesion_specimen(tpu: bool = False) -> Manifold:
    """FP-A. Upright bar that fails between layers. Bottom tab goes in the vise,
    the scale hooks through the top hole. tpu=True gives the thinner FP-A-T."""
    a = SPEC["adhesion"]
    tw, tt, gt = a["tab_w"], a["tab_t"], a["gauge_t"]
    gw = a["gauge_w_tpu"] if tpu else a["gauge_w"]
    z1 = a["bottom_tab_h"]
    z2 = z1 + a["taper_h"]
    z3 = z2 + a["gauge_h"]
    z4 = z3 + a["taper_h"]
    z5 = z4 + a["top_tab_h"]
    eps = 0.01

    def slab(w, t, z):  # thin slice used to hull tapers
        return box(-w / 2, -t / 2, z, w / 2, t / 2, z + eps)

    body = union([
        box(-tw / 2, -tt / 2, 0, tw / 2, tt / 2, z1),
        Manifold.batch_hull([slab(tw, tt, z1 - eps), slab(gw, gt, z2)]),
        box(-gw / 2, -gt / 2, z2, gw / 2, gt / 2, z3),
        Manifold.batch_hull([slab(gw, gt, z3 - eps), slab(tw, tt, z4)]),
        box(-tw / 2, -tt / 2, z4, tw / 2, tt / 2, z5),
    ])

    # teardrop hole along Y, point upward so it prints without support
    r = a["hole_d"] / 2
    zc = z5 - a["top_tab_h"] / 2 + 1.0
    tear = CrossSection.circle(r, SEG)
    tip = CrossSection.square((r, r)).rotate(45)  # square rotated -> 45 deg roof
    tear = CrossSection.batch_hull([tear, tip])
    cutter = tear.extrude(tt + 2).translate((0, 0, -(tt + 2) / 2))
    # extrude is along Z; rotate so the extrusion runs along Y and the tip points +Z
    cutter = cutter.rotate((90, 0, 0))
    cutter = cutter.translate((0, 0, zc))
    return body - cutter


def fit_plate() -> Manifold:
    """FP-F plate: holes of nominal_d + clearance, labelled in hundredths of a mm."""
    f = SPEC["fit"]
    cl = f["clearances"]
    n = len(cl)
    cols = math.ceil(n / 2)
    p = f["pitch"]
    t = f["plate_t"]
    row_h = p + 6  # room for label under each hole
    L = cols * p + 6
    W = 2 * row_h + 2
    plate = box(0, 0, 0, L, W, t)
    cuts = []
    for i, c in enumerate(cl):
        row, col = divmod(i, cols)
        x = 3 + p / 2 + col * p
        y = W - (1 + row * row_h + p / 2)
        d = f["nominal_d"] + c
        ch = f["chamfer"]
        cuts.append(cyl(d, t + 2, -1, x, y))
        # chamfers at both faces so elephant foot / burrs don't skew the result
        cuts.append(cone(d + 2 * ch, d, ch, 0 - 0.001, x, y))
        cuts.append(cone(d, d + 2 * ch, ch, t - ch + 0.001, x, y))
        cuts.append(label(f"{round(c * 100):02d}", x, y - p / 2 - 2.6, t))
    return plate - union(cuts)


def fit_peg() -> Manifold:
    """FP-F peg: exactly nominal_d, with a grip collar so it can be pushed and pulled."""
    f = SPEC["fit"]
    d, h, ch = f["nominal_d"], f["peg_h"], f["chamfer"]
    collar = cyl(d + 8, 4)
    shaft = union([
        cyl(d, h - ch, 4),
        cone(d, d - 2 * ch, ch, 4 + h - ch),
    ])
    return collar + shaft


def dimension_gauge() -> Manifold:
    """FP-D: one row of holes and one row of pegs at several nominal sizes."""
    g = SPEC["dimension"]
    L, W, t, ph = g["plate_l"], g["plate_w"], g["plate_t"], g["peg_h"]
    sizes = g["sizes"]
    n = len(sizes)
    pitch = L / n
    plate = box(0, 0, 0, L, W, t)
    cuts, adds = [], []
    for i, s in enumerate(sizes):
        x = pitch / 2 + i * pitch
        cuts.append(cyl(s, t + 2, -1, x, W * 0.75))
        cuts.append(label(f"{s:g}", x, W / 2, t))
        adds.append(cyl(s, ph, t - 0.001, x, W * 0.22))
    return (plate - union(cuts)) + union(adds)


MODELS = {
    "FP-A_layer-adhesion": adhesion_specimen,
    "FP-A-T_layer-adhesion-tpu": lambda: adhesion_specimen(tpu=True),
    "FP-F_fit-plate": fit_plate,
    "FP-F_fit-peg": fit_peg,
    "FP-D_dimension-gauge": dimension_gauge,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "models" / "stl"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in MODELS.items():
        m = fn()
        tm = to_trimesh(m)
        assert tm.is_watertight, name
        path = out / f"{name}_v{SPEC['version']}.stl"
        tm.export(path)
        ext = tm.bounds[1] - tm.bounds[0]
        print(f"{path.name}: {ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f} mm, volume {tm.volume / 1000:.2f} cm3")


if __name__ == "__main__":
    main()
