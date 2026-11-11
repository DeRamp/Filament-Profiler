# FP-D: Dimensional accuracy

A plate with five round holes and five round pegs at nominal diameters of 3, 5, 8, 10 and 15 mm. Measuring them tells you how much to adjust holes and pegs in CAD so printed parts come out the size you drew.

## Printing

- Print flat, as exported, one per plate, in the centre.
- Fixed settings from the overview. All compensation settings off.
- Print it once with the baseline profile and once with the strength profile.

## Measuring

Let the part cool to room temperature for at least 1 hour (24 hours for nylon, stored dry).

For every hole and every peg:

1. Measure the diameter **along X and along Y** (the plate's long edge is X).
2. For pegs, measure at mid height, not at the base, to avoid first layer squish.
3. For holes, use the inside jaws at mid depth. Close gently; do not force the jaws.
4. Record both numbers to 0.01 mm.

Also record the plate's overall length (100 mm nominal) and width (50 mm nominal).

## Calculation

- `hole offset = mean(measured − nominal)` over all holes. Usually negative: holes print small.
- `peg offset = mean(measured − nominal)` over all pegs. Usually positive.
- `scale error = (measured length − 100) ÷ 100`, as a percentage. This is mostly shrinkage.

## Using the result in CAD

To get a hole of true diameter D, draw `D − hole offset`. To get a peg of true diameter D, draw `D − peg offset`. The exported CAD parameter files contain these as `hole_comp` and `peg_comp`, already sign flipped, so you just add them.
