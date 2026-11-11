# FP-A: Layer adhesion

A small bar printed standing upright is pulled apart along its length. Because the layers are stacked along the pull direction, it breaks between two layers, and the force it took tells you how well the layers bonded.

## The specimen

- 16 × 6 × 71 mm, about 4 cm³.
- Gauge section (the thin middle): **4.0 × 2.0 mm, 8 mm² nominal**, 20 mm long.
- FP-A-T, the flexible variant: 3.0 × 2.0 mm, 6 mm² nominal.
- The top tab has a teardrop hole for the scale hook. The bottom tab goes in the vise.

A typical PLA part breaks somewhere around 15 to 30 kg on the scale. That is an estimate from published Z-strength figures, not a measured result from this project.

## Printing

1. Print **5 specimens per setting**, all on one plate, standing upright, in a row 30 mm apart, in the centre of the plate. Always print 5, never more or fewer, because the number of parts on the plate changes layer time and cooling, and that changes adhesion.
2. Use the fixed settings from the overview: solid walls, 5 mm brim, seam on a narrow face.
3. Label each specimen with a marker as soon as it comes off the plate: setting code and number, for example `T230-3`.

## Conditioning

- Let specimens rest at room temperature for **at least 24 hours** before testing.
- Nylon and other moisture sensitive materials: store in a sealed bag or dry box with desiccant during the rest, and test within 15 minutes of taking them out. Nylon gets tougher and weaker as it absorbs water, so "dry as printed" is the standard condition.

## Measuring

1. Remove the brim cleanly.
2. Measure the gauge section width and thickness with calipers at mid height. Record both to 0.01 mm. The real area, not the nominal one, is used for the calculation.

## Pulling

1. Clamp the **bottom tab** in the vise with the jaws gripping the wide faces, up to the top edge of the tab and no higher. The taper and gauge must be clear of the jaws.
2. Hook the scale through the hole. Turn on peak hold.
3. Put on safety glasses.
4. Pull **straight up, in line with the bar**, smoothly, building force over about 5 to 10 seconds until it breaks. Do not jerk. A sideways pull bends the bar and gives a falsely low number.
5. Record the peak reading in kg.
6. Record **where it broke**:
   - `gauge`: in the thin section. Valid.
   - `taper`: in the taper. Valid, but note it.
   - `tab` or `hole`: at the vise or the hook. **Invalid.** Exclude it and say why.
7. Record how it broke: `clean` (flat, between layers) or `ragged` (tore across layers, which means adhesion is close to the material's own strength).

## Flexibles (FP-A-T)

TPU often stretches a long way instead of snapping. Pull until it separates or until the scale reaches 40 kg, whichever comes first. Record the peak force and add `stretched` or `delaminated` to the break notes. If it never separates, record the peak and mark it `no-break`; it is reported as "greater than" that value.

## Calculation

For each specimen:

`strength (MPa) = force (kg) × 9.80665 ÷ (width × thickness in mm²)`

Report the **mean and standard deviation** of the valid specimens. A setting needs at least 3 valid specimens to count. If fewer than 3 are valid, reprint.

## What to write down

For each setting: the setting code, what changed from baseline, and for each specimen the width, thickness, peak kg, break location, and break type.
