# FP-F: Fit

One peg of exactly 10.00 mm nominal diameter, and a plate with eleven holes from 10.00 to 10.50 mm in 0.05 mm steps. Each hole is engraved with its diametral clearance in hundredths of a millimetre (`00`, `05`, `10` … `50`). Trying the peg in each hole tells you what clearance to design for each kind of fit.

## Printing

- Print the plate flat and the peg upright (collar down), as exported, on the same plate.
- Fixed settings from the overview. All compensation settings off.
- Print once with the baseline profile and once with the strength profile.
- Let parts cool for at least 1 hour before testing (24 hours for nylon, stored dry).

## Testing

Start at the largest hole (`50`) and work down. Insert the peg from the top face, straight, without twisting. Classify each hole using the first description that is true:

| Class | Definition |
|---|---|
| **loose** | With the plate held horizontal, the peg drops through under its own weight |
| **slip** | The peg slides in with a light push from one finger, and can rattle |
| **snug** | Needs a firm push by hand, has no rattle, and stays in when the plate is turned upside down and shaken |
| **press** | Cannot be seated by hand, but seats fully when squeezed in the vise |
| **none** | Will not seat in the vise without damage |

Test each hole once. Do not re-test a hole after a press fit, because pressing deforms it.

## What to write down

The class of every hole. The build script reports the **smallest clearance** that gave each class:

- `fit_loose`: smallest clearance that was loose
- `fit_slip`: smallest clearance that was slip
- `fit_snug`: smallest clearance that was snug
- `fit_press`: largest clearance that was press

These are diametral clearances on a 10 mm round feature printed in the XY plane. They include the hole and peg error from FP-D, so use them directly on nominal CAD dimensions and do not add `hole_comp` on top.

## Limits

- Fits change with diameter, orientation and wall count. Treat these as starting values for other sizes, and reprint the gauge if a fit is critical.
- For flexibles the classes still apply, but expect press fits across a wide range.
