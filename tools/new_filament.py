#!/usr/bin/env python3
"""Scaffold untested records for a filament, one per nozzle diameter."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--material", required=True, help="PLA, PETG, TPU, PA-GF ...")
    ap.add_argument("--nozzles", nargs="+", type=float, default=[0.4])
    ap.add_argument("--printer", default="Bambu Lab H3C")
    ap.add_argument("--nozzle-temp", type=int, required=True)
    ap.add_argument("--bed-temp", type=int, required=True)
    ap.add_argument("--max-vol-speed", type=float, required=True, help="mm3/s")
    ap.add_argument("--inherits", default="", help="Bambu Studio preset to inherit from")
    ap.add_argument("--flexible", action="store_true", help="use FP-A-T instead of FP-A")
    a = ap.parse_args()

    for nz in a.nozzles:
        rid = f"{slug(a.brand)}-{slug(a.name)}__{nz:g}"
        path = ROOT / "data" / "filaments" / f"{rid}.json"
        if path.exists():
            print(f"skip {path.name} (exists)")
            continue
        rec = {
            "schema": 1,
            "id": rid,
            "protocol_version": "1.0",
            "status": "untested",
            "filament": {"brand": a.brand, "name": a.name, "material": a.material,
                         "flexible": a.flexible, "drying": ""},
            "printer": {"model": a.printer, "nozzle_diameter": nz, "nozzle_type": "",
                        "build_plate": "", "enclosure": "", "room_temp_c": None},
            "bambu": {"inherits": a.inherits},
            "settings": {
                "nozzle_temp": a.nozzle_temp,
                "nozzle_temp_initial_layer": a.nozzle_temp,
                "bed_temp": a.bed_temp,
                "flow_ratio": None,
                "max_volumetric_speed": a.max_vol_speed,
                "pressure_advance": None,
                "fan_min_speed": None,
                "fan_max_speed": None,
                "layer_height": round(nz / 2, 2),
            },
            "tests": {"adhesion": [], "dimension": {}, "fit": {}},
            "notes": "",
            "tested_by": "",
            "tested_on": "",
        }
        path.write_text(json.dumps(rec, indent=2) + "\n")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
