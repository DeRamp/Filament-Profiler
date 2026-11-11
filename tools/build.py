#!/usr/bin/env python3
"""Validate records, compute results, and regenerate every export and the website.

    python tools/build.py

Reads   data/filaments/*.json, protocols/*.md, models/stl/*.stl, templates/*
Writes  exports/  (Bambu Studio profiles, CSV, XLSX, Fusion and Onshape parameters)
        docs/     (the GitHub Pages site, including a copy of all downloads)
"""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
import statistics
import sys
from pathlib import Path

import markdown
from openpyxl import Workbook
from openpyxl.styles import Font

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "filaments"
EXPORTS = ROOT / "exports"
DOCS = ROOT / "docs"
G = 9.80665
FIT_CLASSES = ["loose", "slip", "snug", "press", "none"]
BREAKS = ["gauge", "taper", "tab", "hole", "no-break"]

# ------------------------------------------------------------ compute


def adhesion_stats(run: dict) -> dict | None:
    vals = []
    for s in run.get("specimens", []):
        if s.get("exclude") or s.get("break") in ("tab", "hole"):
            continue
        vals.append(s["kg"] * G / (s["w"] * s["t"]))
    if len(vals) < 3:
        return None
    return {
        "code": run["code"],
        "n": len(vals),
        "mean": statistics.mean(vals),
        "sd": statistics.stdev(vals),
        "lower_bound": any(s.get("break") == "no-break" for s in run["specimens"]),
    }


def compute(rec: dict) -> dict:
    """Derived values for one record. Missing tests give None."""
    out: dict = {k: None for k in (
        "base_mpa", "base_sd", "best_mpa", "best_sd", "best_code", "gain_pct",
        "hole_offset", "peg_offset", "hole_comp", "peg_comp", "scale_error_pct",
        "fit_loose", "fit_slip", "fit_snug", "fit_press")}
    t = rec.get("tests", {})

    runs = [(r, adhesion_stats(r)) for r in t.get("adhesion", [])]
    runs = [(r, s) for r, s in runs if s]
    if runs:
        base = next((s for r, s in runs if r.get("stage") == 0), None)
        sel = next((s for r, s in runs if r.get("selected")), None) or max(
            (s for _, s in runs), key=lambda s: s["mean"])
        if base:
            out["base_mpa"], out["base_sd"] = base["mean"], base["sd"]
        out["best_mpa"], out["best_sd"], out["best_code"] = sel["mean"], sel["sd"], sel["code"]
        if base and base["mean"]:
            out["gain_pct"] = (sel["mean"] / base["mean"] - 1) * 100

    d = t.get("dimension") or {}
    for key, name in (("holes", "hole"), ("pegs", "peg")):
        rows = d.get(key) or []
        if rows:
            off = statistics.mean((r["x"] + r["y"]) / 2 - r["nominal"] for r in rows)
            out[f"{name}_offset"] = off
            out[f"{name}_comp"] = -off
    if d.get("length"):
        out["scale_error_pct"] = (d["length"] - 100.0) / 100.0 * 100

    holes = (t.get("fit") or {}).get("holes") or {}
    by_class: dict[str, list[float]] = {}
    for cl, cls in holes.items():
        by_class.setdefault(cls, []).append(float(cl))
    for cls in ("loose", "slip", "snug"):
        if cls in by_class:
            out[f"fit_{cls}"] = min(by_class[cls])
    if "press" in by_class:
        out["fit_press"] = max(by_class["press"])
    return out


# ------------------------------------------------------------ validate


def validate(rec: dict, path: Path) -> list[str]:
    e = []
    if rec.get("id") != path.stem:
        e.append(f"id must equal file name ({path.stem})")
    if rec.get("status") not in ("untested", "tested"):
        e.append("status must be 'untested' or 'tested'")
    for k in ("filament", "printer", "settings", "tests"):
        if k not in rec:
            e.append(f"missing '{k}'")
    if e:
        return e
    t = rec["tests"]
    for run in t.get("adhesion", []):
        for i, s in enumerate(run.get("specimens", []), 1):
            for k in ("w", "t", "kg", "break"):
                if k not in s:
                    e.append(f"adhesion {run.get('code')} specimen {i}: missing '{k}'")
            if s.get("break") not in BREAKS:
                e.append(f"adhesion {run.get('code')} specimen {i}: break must be one of {BREAKS}")
    for cl, cls in ((t.get("fit") or {}).get("holes") or {}).items():
        if cls not in FIT_CLASSES:
            e.append(f"fit {cl}: class must be one of {FIT_CLASSES}")
    if rec["status"] == "tested":
        if not any(adhesion_stats(r) for r in t.get("adhesion", [])):
            e.append("status is 'tested' but no adhesion run has 3 or more valid specimens")
        if rec["settings"].get("flow_ratio") is None:
            e.append("status is 'tested' but settings.flow_ratio is empty")
    return e


# ------------------------------------------------------------ exports


def display_name(rec: dict) -> str:
    f, p = rec["filament"], rec["printer"]
    return f"{f['brand']} {f['name']} {p['nozzle_diameter']:g} mm"


def bambu_profile(rec: dict) -> dict:
    s = rec["settings"]
    name = f"FP {display_name(rec)}"
    prof = {
        "type": "filament",
        "name": name,
        "from": "User",
        "inherits": rec.get("bambu", {}).get("inherits", ""),
        "filament_settings_id": [name],
        "filament_notes": f"Filament Profiler record {rec['id']}, protocol v{rec.get('protocol_version', '?')}",
    }
    mapping = {
        "nozzle_temp": ["nozzle_temperature"],
        "nozzle_temp_initial_layer": ["nozzle_temperature_initial_layer"],
        "bed_temp": ["hot_plate_temp", "hot_plate_temp_initial_layer",
                     "textured_plate_temp", "textured_plate_temp_initial_layer"],
        "flow_ratio": ["filament_flow_ratio"],
        "max_volumetric_speed": ["filament_max_volumetric_speed"],
        "pressure_advance": ["pressure_advance"],
        "fan_min_speed": ["fan_min_speed"],
        "fan_max_speed": ["fan_max_speed"],
    }
    for src, keys in mapping.items():
        if s.get(src) is not None:
            for k in keys:
                prof[k] = [f"{s[src]:g}"]
    if s.get("pressure_advance") is not None:
        prof["enable_pressure_advance"] = ["1"]
    return prof


CAD_PARAMS = [
    ("hole_comp", "Add to a nominal hole diameter so it prints true size"),
    ("peg_comp", "Add to a nominal peg diameter so it prints true size"),
    ("fit_loose", "Diametral clearance for a loose fit (peg drops through)"),
    ("fit_slip", "Diametral clearance for a slip fit (light finger push)"),
    ("fit_snug", "Diametral clearance for a snug fit (firm hand push, holds)"),
    ("fit_press", "Diametral clearance for a press fit (needs a vise)"),
]


def write_cad(rec: dict, c: dict):
    rows = [(n, c[n], d) for n, d in CAD_PARAMS if c[n] is not None]
    if not rows:
        return
    src = f"{display_name(rec)}, {rec['id']}"
    p = EXPORTS / "fusion" / f"{rec['id']}.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Unit", "Expression", "Value", "Comments", "Favorite"])
        for n, v, d in rows:
            w.writerow([n, "mm", f"{v:.3f} mm", f"{v:.3f}", f"{d} ({src})", "true"])
    p = EXPORTS / "onshape" / f"{rec['id']}.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Name", "Type", "Value", "Description"])
        for n, v, d in rows:
            w.writerow([n, "Length", f"{v:.3f} mm", f"{d} ({src})"])


COLUMNS = [
    ("id", "Record"), ("status", "Status"), ("brand", "Brand"), ("name", "Filament"),
    ("material", "Material"), ("printer", "Printer"), ("nozzle", "Nozzle (mm)"),
    ("protocol_version", "Protocol"),
    ("nozzle_temp", "Nozzle temp (C)"), ("bed_temp", "Bed temp (C)"), ("flow_ratio", "Flow ratio"),
    ("max_volumetric_speed", "Max vol. speed (mm3/s)"), ("pressure_advance", "Pressure advance"),
    ("layer_height", "Layer height (mm)"),
    ("base_mpa", "Baseline Z strength (MPa)"), ("base_sd", "Baseline SD"),
    ("best_mpa", "Tuned Z strength (MPa)"), ("best_sd", "Tuned SD"), ("best_code", "Tuned setting"),
    ("gain_pct", "Gain (%)"),
    ("hole_offset", "Hole offset (mm)"), ("peg_offset", "Peg offset (mm)"),
    ("scale_error_pct", "Scale error (%)"),
    ("fit_loose", "Loose fit (mm)"), ("fit_slip", "Slip fit (mm)"),
    ("fit_snug", "Snug fit (mm)"), ("fit_press", "Press fit (mm)"),
    ("tested_by", "Tested by"), ("tested_on", "Tested on"), ("notes", "Notes"),
]


def flat_row(rec: dict, c: dict) -> dict:
    f, p, s = rec["filament"], rec["printer"], rec["settings"]
    row = {"id": rec["id"], "status": rec["status"], "brand": f["brand"], "name": f["name"],
           "material": f["material"], "printer": p["model"], "nozzle": p["nozzle_diameter"],
           "protocol_version": rec.get("protocol_version"), "tested_by": rec.get("tested_by"),
           "tested_on": rec.get("tested_on"), "notes": rec.get("notes")}
    row.update({k: s.get(k) for k in ("nozzle_temp", "bed_temp", "flow_ratio",
                                      "max_volumetric_speed", "pressure_advance", "layer_height")})
    row.update({k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()})
    return row


def write_tables(rows: list[dict]):
    with (EXPORTS / "filament-profiler.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([h for _, h in COLUMNS])
        for r in rows:
            w.writerow(["" if r.get(k) is None else r.get(k) for k, _ in COLUMNS])
    wb = Workbook()
    ws = wb.active
    ws.title = "Records"
    ws.append([h for _, h in COLUMNS])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for r in rows:
        ws.append([r.get(k) for k, _ in COLUMNS])
    ws.freeze_panes = "A2"
    for i, (_, h) in enumerate(COLUMNS, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = max(12, len(h) + 2)
    wb.save(EXPORTS / "filament-profiler.xlsx")


# ------------------------------------------------------------ site

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1b1f24;--mute:#5d6672;--line:#dfe2e6;--accent:#0b6e4f;--accent-ink:#fff;--warn:#8a5a00;--warn-bg:#fff4d6}
@media (prefers-color-scheme:dark){:root{--bg:#14171a;--card:#1c2025;--ink:#e8eaed;--mute:#9aa3ad;--line:#2e343b;--accent:#4cc79a;--accent-ink:#0c1512;--warn:#f0c869;--warn-bg:#3a2f12}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--accent)}
header{border-bottom:1px solid var(--line);background:var(--card)}
.wrap{max-width:1040px;margin:0 auto;padding:0 16px}
header .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:8px 24px;padding-top:14px;padding-bottom:14px}
.brand{font-weight:700;font-size:1.1rem;text-decoration:none;color:var(--ink)}
nav{display:flex;flex-wrap:wrap;gap:4px 16px}
nav a{text-decoration:none;color:var(--mute);padding:2px 0;border-bottom:2px solid transparent}
nav a.on,nav a:hover{color:var(--ink);border-color:var(--accent)}
main{padding:28px 0 64px}
h1{font-size:1.8rem;line-height:1.2;margin:0 0 12px}
h2{font-size:1.25rem;margin:32px 0 10px}
h3{font-size:1.05rem;margin:22px 0 6px}
.lead{color:var(--mute);max-width:68ch}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card);margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:.93rem}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.8rem;text-transform:uppercase;letter-spacing:.03em;color:var(--mute);white-space:nowrap}
tr:last-child td{border-bottom:0}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
code{background:rgba(127,127,127,.15);padding:1px 5px;border-radius:4px;font-size:.9em}
pre{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}
pre code{background:none;padding:0}
.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:.78rem;font-weight:600}
.pill.tested{background:var(--accent);color:var(--accent-ink)}
.pill.untested{background:var(--warn-bg);color:var(--warn)}
.btn{display:inline-block;padding:6px 12px;border-radius:6px;border:1px solid var(--line);background:var(--card);text-decoration:none;font-size:.9rem;margin:2px 4px 2px 0}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin:14px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px}
.card h3{margin:0 0 4px}
.card p{margin:0 0 8px;color:var(--mute);font-size:.93rem}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
select,input{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
.empty{color:var(--mute)}
footer{border-top:1px solid var(--line);color:var(--mute);font-size:.85rem;padding:18px 0}
"""

NAV = [("index.html", "Filaments"), ("protocols.html", "Test protocols"),
       ("downloads.html", "Downloads"), ("add.html", "Add a filament")]


def page(title: str, active: str, body: str) -> str:
    nav = "".join(f'<a href="{h}"{" class=on" if h == active else ""}>{t}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Filament Profiler</title>
<link rel="stylesheet" href="style.css"></head>
<body><header><div class="wrap"><a class="brand" href="index.html">Filament Profiler</a><nav>{nav}</nav></div></header>
<main><div class="wrap">{body}</div></main>
<footer><div class="wrap">Generated by <code>tools/build.py</code> from the files in <code>data/</code> and <code>protocols/</code>. Protocol v1.0.</div></footer>
</body></html>"""


def md(text: str) -> str:
    out = markdown.markdown(text, extensions=["tables", "fenced_code"])
    return out.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")


def fmt(v, nd=2, plus=False):
    if v is None:
        return '<span class="empty">–</span>'
    if isinstance(v, (int, float)):
        return f"{v:+.{nd}f}" if plus else f"{v:.{nd}f}"
    return html.escape(str(v))


def build_site(recs: list[tuple[dict, dict]], model_files: list[Path]):
    if DOCS.exists():
        shutil.rmtree(DOCS)
    dl = DOCS / "downloads"
    (dl / "models").mkdir(parents=True)
    for m in model_files:
        shutil.copy(m, dl / "models" / m.name)
    shutil.copytree(EXPORTS, dl / "exports")
    shutil.copytree(ROOT / "templates", dl / "templates")
    (DOCS / "style.css").write_text(CSS)
    (DOCS / ".nojekyll").write_text("")

    # ---- index
    rows = []
    for rec, c in recs:
        f, p, s = rec["filament"], rec["printer"], rec["settings"]
        rid = rec["id"]
        links = [f'<a class="btn" href="downloads/exports/bambu/{rid}.json" download>Slicer profile</a>']
        if (EXPORTS / "fusion" / f"{rid}.csv").exists():
            links.append(f'<a class="btn" href="downloads/exports/fusion/{rid}.csv" download>Fusion</a>')
            links.append(f'<a class="btn" href="downloads/exports/onshape/{rid}.csv" download>Onshape</a>')
        strength = fmt(c["best_mpa"], 1)
        if c["best_mpa"] is not None:
            strength += f" ± {c['best_sd']:.1f}"
            if c["gain_pct"] is not None and abs(c["gain_pct"]) >= 0.05:
                strength += f" <small>({c['gain_pct']:+.0f}% vs baseline)</small>"
        rows.append(
            f'<tr data-mat="{html.escape(f["material"])}" data-noz="{p["nozzle_diameter"]:g}" data-status="{rec["status"]}">'
            f'<td><strong>{html.escape(f["brand"])} {html.escape(f["name"])}</strong><br><small>{html.escape(f["material"])}</small></td>'
            f'<td class="num">{p["nozzle_diameter"]:g}</td>'
            f'<td><span class="pill {rec["status"]}">{rec["status"]}</span></td>'
            f'<td class="num">{fmt(s.get("nozzle_temp"), 0)}</td>'
            f'<td class="num">{fmt(s.get("flow_ratio"), 3)}</td>'
            f'<td class="num">{fmt(s.get("max_volumetric_speed"), 1)}</td>'
            f'<td class="num">{strength}</td>'
            f'<td class="num">{fmt(c["hole_comp"], 2, True)}</td>'
            f'<td class="num">{fmt(c["fit_slip"])}</td>'
            f'<td class="num">{fmt(c["fit_press"])}</td>'
            f'<td>{"".join(links)}</td></tr>')
    mats = sorted({r["filament"]["material"] for r, _ in recs})
    nozs = sorted({r["printer"]["nozzle_diameter"] for r, _ in recs})
    n_tested = sum(r["status"] == "tested" for r, _ in recs)
    body = f"""
<h1>Filament profiles tuned for strength and accuracy</h1>
<p class="lead">Every profile here was found with the same published <a href="protocols.html">test protocols</a>, so results from different people and printers can be compared. Each row is one filament on one nozzle size. Download the slicer profile for Bambu Studio and the fit tolerances for Fusion or Onshape.</p>
<p><a class="btn primary" href="downloads/exports/filament-profiler.xlsx" download>Download all data (.xlsx)</a>
<a class="btn" href="downloads/exports/filament-profiler.csv" download>.csv</a>
<a class="btn" href="downloads.html">Test models and templates</a></p>
<p class="lead">{len(recs)} records, {n_tested} tested. Records marked <span class="pill untested">untested</span> hold starting values only and have no measurements yet.</p>
<div class="filters">
<select id="fm" aria-label="Material"><option value="">All materials</option>{''.join(f'<option>{html.escape(m)}</option>' for m in mats)}</select>
<select id="fn" aria-label="Nozzle"><option value="">All nozzles</option>{''.join(f'<option value="{n:g}">{n:g} mm</option>' for n in nozs)}</select>
<select id="fs" aria-label="Status"><option value="">Any status</option><option>tested</option><option>untested</option></select>
</div>
<div class="tablewrap"><table id="t"><thead><tr><th>Filament</th><th>Nozzle</th><th>Status</th><th>Temp °C</th><th>Flow</th><th>mm³/s</th><th>Z strength MPa</th><th>Hole comp mm</th><th>Slip fit mm</th><th>Press fit mm</th><th>Downloads</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="lead"><small>Z strength is layer adhesion from test FP-A, mean ± standard deviation. Hole comp is what to add to a nominal hole diameter in CAD. Slip and press fit are diametral clearances on a 10 mm round feature from test FP-F.</small></p>
<script>
const f=['fm','fn','fs'].map(i=>document.getElementById(i));
function go(){{document.querySelectorAll('#t tbody tr').forEach(r=>{{
r.hidden=(f[0].value&&r.dataset.mat!==f[0].value)||(f[1].value&&r.dataset.noz!==f[1].value)||(f[2].value&&r.dataset.status!==f[2].value)}})}}
f.forEach(e=>e.addEventListener('change',go));
</script>"""
    (DOCS / "index.html").write_text(page("Filaments", "index.html", body))

    # ---- protocols (all on one page) + add
    protos = sorted((ROOT / "protocols").glob("*.md"))
    parts, toc = [], []
    for p in protos:
        text = p.read_text()
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        anchor = p.stem
        if p.stem.endswith("add-a-filament"):
            (DOCS / "add.html").write_text(page(title, "add.html", md(text)))
            continue
        toc.append(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>')
        body_html = md(text).replace("<h1>", f"<h2 id=\"{anchor}\" style=\"font-size:1.5rem\">", 1).replace("</h1>", "</h2>", 1)
        parts.append(f"<section>{body_html}</section><hr style='border:0;border-top:1px solid var(--line);margin:36px 0'>")
    body = ('<h1>Test protocols</h1><p class="lead">These are the standard test methods. Follow them exactly so your results '
            'can be compared with everyone else\'s. <a href="downloads.html">Get the test models here.</a></p>'
            f"<ul>{''.join(toc)}</ul>" + "".join(parts))
    (DOCS / "protocols.html").write_text(page("Test protocols", "protocols.html", body))

    # ---- downloads
    desc = {
        "FP-A_": ("Layer adhesion bar", "Print 5 upright per setting. Pulled apart with a hanging scale."),
        "FP-A-T": ("Layer adhesion bar, flexibles", "Thinner variant for TPU and other flexibles."),
        "FP-D": ("Dimension gauge", "Holes and pegs at 3, 5, 8, 10 and 15 mm."),
        "FP-F_fit-plate": ("Fit plate", "Eleven 10 mm holes with 0.00 to 0.50 mm clearance."),
        "FP-F_fit-peg": ("Fit peg", "The 10 mm peg that goes with the fit plate."),
    }
    cards = []
    for m in model_files:
        t, d = next(v for k, v in desc.items() if m.name.startswith(k))
        cards.append(f'<div class="card"><h3>{t}</h3><p>{d}</p>'
                     f'<a class="btn primary" href="downloads/models/{m.name}" download>{m.name}</a></div>')
    body = f"""
<h1>Downloads</h1>
<h2>Test models (STL)</h2>
<p class="lead">Print them as exported, without rotating or scaling. They are generated by <code>tools/generate_models.py</code>, where every dimension is a parameter.</p>
<div class="grid">{''.join(cards)}</div>
<h2>Data</h2>
<p><a class="btn primary" href="downloads/exports/filament-profiler.xlsx" download>All records (.xlsx)</a>
<a class="btn" href="downloads/exports/filament-profiler.csv" download>All records (.csv)</a></p>
<h2>Templates</h2>
<p><a class="btn" href="downloads/templates/test-log.csv" download>Workbench test log (.csv)</a>
<a class="btn" href="downloads/templates/record-example.json" download>Filled example record (.json)</a></p>
<h2>Slicer profiles and CAD parameters</h2>
<p class="lead">These are per filament and nozzle. Use the buttons on the <a href="index.html">Filaments</a> page. Import steps are on <a href="add.html">Add a filament</a>.</p>"""
    (DOCS / "downloads.html").write_text(page("Downloads", "downloads.html", body))


# ------------------------------------------------------------ main


def main() -> int:
    recs, errors = [], []
    for path in sorted(DATA.glob("*.json")):
        try:
            rec = json.loads(path.read_text())
        except json.JSONDecodeError as ex:
            errors.append(f"{path.name}: invalid JSON: {ex}")
            continue
        errs = validate(rec, path)
        if errs:
            errors += [f"{path.name}: {m}" for m in errs]
            continue
        recs.append((rec, compute(rec)))
    if errors:
        print("Validation failed:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1

    if EXPORTS.exists():
        shutil.rmtree(EXPORTS)
    for sub in ("bambu", "fusion", "onshape"):
        (EXPORTS / sub).mkdir(parents=True)
    for rec, c in recs:
        (EXPORTS / "bambu" / f"{rec['id']}.json").write_text(json.dumps(bambu_profile(rec), indent=4) + "\n")
        write_cad(rec, c)
    write_tables([flat_row(r, c) for r, c in recs])

    models = sorted((ROOT / "models" / "stl").glob("*.stl"))
    build_site(recs, models)
    print(f"{len(recs)} records, {sum(r['status'] == 'tested' for r, _ in recs)} tested. "
          f"Wrote exports/ and docs/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
