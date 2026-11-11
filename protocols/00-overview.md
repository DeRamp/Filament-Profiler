# Overview and ground rules

Filament Profiler is a shared, repeatable way to find the strongest and most accurate settings for a filament, and to publish what you found so other people can import it. Results are only comparable if everyone tests the same way, so please follow these protocols exactly and write down anything you did differently.

**Protocol version: 1.0.** Record this version with every result. The test models carry the same version number in their file names.

## What gets tested

| Code | Test | What it tells you | Model |
|---|---|---|---|
| FP-A | Layer adhesion (Z tensile) | How strongly layers bond, in MPa | `FP-A_layer-adhesion` |
| FP-A-T | Layer adhesion for flexibles | Same, for TPU and other flexibles | `FP-A-T_layer-adhesion-tpu` |
| FP-D | Dimensional accuracy | How far holes and pegs are off nominal | `FP-D_dimension-gauge` |
| FP-F | Fit | Which clearance gives a loose, slip, snug or press fit | `FP-F_fit-plate` + `FP-F_fit-peg` |

One **record** is one filament on one nozzle diameter. A filament tested on 0.4 mm and 0.6 mm is two records.

## Equipment

- Digital calipers, 0.01 mm resolution. Zero them before every session.
- A bench vise.
- A digital hanging scale (luggage scale) with **peak hold**, 50 kg range, 10 g or 20 g resolution. Check it once against a known weight, such as 5 L of water in a bucket (5 kg plus the bucket).
- Safety glasses. Specimens snap suddenly.

## Before any test print

1. **Dry the filament** to the maker's recommendation and print from a dry box. Record how it was dried. This matters most for nylon and TPU.
2. **Calibrate the basics** in the slicer for this filament and nozzle: flow dynamics (pressure advance) and flow rate. Record the calibrated flow ratio. That value is your "0%" for the flow sweep.
3. **Use a clean, known build plate** and record which plate it is.
4. **Record room temperature** and whether the printer was enclosed or the door was open.

## Fixed print settings for all tests

These stay the same for every test print so that only the variable under test changes.

| Setting | Value |
|---|---|
| Layer height | 50% of nozzle diameter (0.10 / 0.20 / 0.30 / 0.40 mm for 0.2 / 0.4 / 0.6 / 0.8 nozzles) |
| Line width | Slicer default for the nozzle |
| Wall loops | Enough that FP-A is solid walls (set 99) |
| Infill for FP-D and FP-F | 15% grid or gyroid, 3 walls for 0.2 and 0.4 nozzles, 2 walls for 0.6 and 0.8 |
| Top and bottom layers | Slicer default |
| Seam | Aligned, and for FP-A placed on a narrow face |
| Supports | None. All models print without supports |
| Brim | 5 mm outer brim on FP-A only |
| Scaling, shrinkage compensation, X-Y hole or contour compensation | Off (100%, 0 mm). We are measuring the raw error |
| Orientation | As exported. Do not rotate the models |

## The sweep: one variable at a time

Testing every combination would take hundreds of prints. Instead, change one variable per stage and carry the winner forward.

| Stage | Variable | Levels |
|---|---|---|
| 0 | Baseline | The maker's or slicer's default profile, with your calibrated flow ratio |
| 1 | Nozzle temperature | default −10, default, default +10, default +20 °C. Stay inside the maker's stated range |
| 2 | Speed | Max volumetric speed at 100%, 50% and 25% of the default |
| 3 | Flow ratio | calibrated, +3%, +6% |
| 4 | Part cooling (optional) | default, half, off. Skip for materials that need full cooling to hold shape |

The winner of each stage is the level with the highest mean FP-A strength. If two levels are within one standard deviation of each other, pick the one closer to the default, because it will print cleaner.

After stage 3 you have your **strength profile**. Print FP-D and FP-F once with the baseline profile and once with the strength profile, because overextrusion and heat usually cost accuracy and you want to know how much.

## Nozzle and material limits

- Do not run glass or carbon filled filaments on a 0.2 mm nozzle. Use a hardened nozzle of 0.4 mm at minimum, 0.6 mm preferred.
- TPU on a 0.2 mm nozzle is usually not practical. Skip it unless the maker says otherwise.
- Skipped combinations are simply not recorded. Do not enter guesses.

## Recording and reporting

- Record raw measurements, not just the conclusions. The build script does the math.
- Report every specimen, including bad ones, and mark why a specimen was excluded.
- Never mix results from different protocol versions in one record.
