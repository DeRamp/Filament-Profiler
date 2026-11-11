# Filament Profiler

A standardized workflow for testing 3D printing filaments and filament profiles for **strength** (layer adhesion) and **accuracy** (hole, peg and fit tolerances), plus a database of the results that exports straight into your slicer and CAD software.

The website (GitHub Pages, served from `docs/`) has the full test protocols, the test models, and every profile as a download.

## How it works

1. Print the standard test models in `models/stl/`.
2. Follow the protocols in `protocols/` and record your measurements in a record file in `data/filaments/` (one file per filament per nozzle diameter).
3. Run `python tools/build.py`. It validates the records, does the math, and regenerates:
   - `exports/bambu/*.json`: Bambu Studio filament profiles
   - `exports/filament-profiler.csv` and `.xlsx`: every record in one table
   - `exports/fusion/*.csv` and `exports/onshape/*.csv`: tolerance parameters for CAD
   - `docs/`: the website

## Layout

| Path | What it is |
|---|---|
| `protocols/` | The test methods, in Markdown. The source of truth for the standard |
| `models/stl/` | Generated test models |
| `data/filaments/` | The database: one JSON record per filament and nozzle |
| `templates/` | A filled example record and a printable workbench log |
| `tools/generate_models.py` | Parametric source for the test models |
| `tools/new_filament.py` | Creates blank records for a new filament |
| `tools/build.py` | Validates, computes, exports, and builds the site |
| `presets/bambu/` | Hand-tuned Bambu Studio presets (filament + process), ready to import |
| `research/` | The research and reasoning behind each preset |
| `exports/`, `docs/` | Generated. Do not edit by hand |

## Bambu Studio presets

`presets/bambu/` holds complete presets you can import with **File > Import > Import Configs** in Bambu Studio. Each one is a filament preset plus a matching process preset. `research/` explains every value and where it came from.

## Setup

```
pip install -r requirements.txt
python tools/build.py
```

To publish the site: repository Settings, Pages, deploy from branch `main`, folder `/docs`.

See `protocols/04-add-a-filament.md` for adding a filament or a new test.

## Status

Protocol v1.0. The starter records are untested placeholders with generic starting values. The Bambu Studio, Fusion and Onshape export formats have not yet been verified by importing them into those programs.
