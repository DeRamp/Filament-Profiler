# Add a filament or a test

Everything on this site is generated from plain files in the repository, so adding a filament means adding a data file and running one command.

## Add a filament

1. Get the tools: clone the repository and run `pip install -r requirements.txt`.
2. Create the records, one per nozzle diameter:

   ```
   python tools/new_filament.py --brand "Bambu Lab" --name "PLA Basic" --material PLA \
       --nozzles 0.2 0.4 0.6 0.8 --nozzle-temp 220 --bed-temp 55 --max-vol-speed 21
   ```

   This writes `data/filaments/<brand>-<name>__<nozzle>.json` with status `untested`.
3. Download the test models from the Downloads page and follow the protocols.
4. Type your measurements into the record's `tests` section. `templates/record-example.json` shows a fully filled record, and `templates/test-log.csv` is a printable sheet for the workbench.
5. Put the winning settings in `settings`, and set `status` to `tested`.
6. Run `python tools/build.py`. It checks the record, does the math, and regenerates the slicer profiles, spreadsheet, CAD files and website.
7. Commit and open a pull request.

## Import into your tools

- **Bambu Studio:** File, Import, Import Configs, then pick the `.json` from `exports/bambu/`. Each profile inherits from a built-in preset named in the record's `bambu.inherits` field, which must match a preset that exists for your printer and nozzle.
- **Fusion:** Modify, Change Parameters, then the import button, and pick the `.csv` from `exports/fusion/`.
- **Onshape:** open a Variable Studio and import or paste the table from `exports/onshape/`.
- **Spreadsheet:** `exports/filament-profiler.xlsx` or `.csv` has every record in one table.

## Add a new test

1. Add the model to `tools/generate_models.py` and give it an `FP-` code.
2. Write its protocol as a new file in `protocols/`. It appears on the site automatically.
3. Add its fields to `tools/build.py` so the results are computed and exported.
4. Bump the protocol version if an existing test changed. Old results stay tagged with the version they were measured under.
