# Strength per gram: how many walls and top/bottom layers to use, with 12% gyroid infill

Question: with 12% gyroid infill fixed, at what point do extra walls and extra top/bottom layers stop being worth the extra weight?

## Short answer

| Setting | Light and efficient | Diminishing returns begin | Max-strength presets (for comparison) |
|---|---|---|---|
| Walls (0.4 nozzle) | **3 walls**, with inner walls at 0.6 mm: 0.45 + 2 × 0.6 ≈ **1.65 mm** | Wall thickness above about **10% of the part's narrowest cross-section** | 6 walls (≈ 3.45 mm) |
| Top shell | **4 to 5 layers, ≈ 0.8 to 1.0 mm** (enough to cover 12% gyroid cleanly) | Above about 1.0 to 1.2 mm on most parts | 7 layers (1.1 mm) |
| Bottom shell | **3 layers, ≈ 0.5 to 0.6 mm** | Above about 0.8 mm | 5 layers (0.8 mm) |
| Infill | 12% gyroid (your choice) | | 40% gyroid |

Two walls is the lower limit. Going from 2 to 4 walls raised CNC Kitchen's hook strength about 65%, from 20 kg to 33 kg (S1). That is the steepest part of the curve.

## What the evidence says

### Walls are the cheapest strength there is

- **Walls give about 2.5 times more strength per metre of filament than infill.** In a simple hanging-bar test, each extra 10% of infill added 1.5 kg of breaking force for 0.96 m of filament, which is 0.64 m per kg of force. Each extra 2 perimeters added 1.67 kg for 0.42 m, which is 0.25 m per kg (S2). The test is crude, but it is the only direct per-filament comparison found.
- **Strength follows the amount of material in the walls.** At the same wall thickness, 0.4 and 0.8 mm nozzles gave the same strength. At 0.84 mm of wall, both held about 140 N. At 1.68 mm, every variant held 347 to 380 N (S3). Wall thickness matters, not how many lines it takes to build it.
- **Wide lines get you more strength for the same weight.** 2 walls at 200% width held about 39 kg. 4 walls at 100% width hold roughly the same amount of plastic, but held only 33 kg (S1). Wider lines bond better. **To save weight, make fewer, wider inner walls rather than more thin ones.**
- **A shell matters most when infill is sparse.** In a PLA bending study, adding an outer shell greatly improved stiffness and strength, and the best stiffness per weight came from **10% infill with a shell** (S4). In another study, at 25% infill, one extra perimeter matched 40% infill with three perimeters (S5).
- **There is a balance point.** A video test (summarized secondhand, not verified) found the best strength per weight around 3 walls and 20% infill. Beyond that, strength kept rising with more walls, but strength per weight fell (S6).

### Where the diminishing returns start: a simple bending model

Most real parts fail in bending. In bending, material far from the centre of the part does almost all the work, and material near the centre does almost nothing. So the first walls are very efficient. Each later wall sits closer to the centre and adds less. I modelled square bars with 0.45 mm walls and a 12% gyroid core (the core's stiffness was taken as roughly the square of its density) and compared each extra wall's strength per gram with the average so far:

| Bar size | Best strength per gram at | An extra wall is worth less than average after | Shell thickness at that point |
|---|---|---|---|
| 10 mm | 2 to 3 walls | 3 walls | ≈ 1.35 mm (13%) |
| 20 mm | 4 to 5 walls | 5 walls | ≈ 2.25 mm (11%) |
| 40 mm | 8 to 9 walls | 10 walls | ≈ 4.5 mm (11%) |

**Rule of thumb: walls stop paying for their weight once the shell is about 10% of the part's narrowest cross-section.** Below that, every gram of wall adds more strength than the average gram already in the part. Most small and medium functional parts have features 10 to 25 mm wide. That puts the sweet spot at **1.2 to 2.5 mm of shell, which is 3 to 4 walls on a 0.4 nozzle with 0.6 mm inner walls**. This is a geometry model, not a print test. It agrees with S2, S4 and S6, but check it on your own parts with FP-A or a hook test.

A sandwich-beam simulation of PLA backs up the same idea for top and bottom skins. Specific load capacity peaked at a particular skin-to-core split and then "declined considerably" with thicker skins, most sharply at low infill (S7).

### Top and bottom layers

- No study measured top and bottom thickness on its own. The same bending logic applies. For a part loaded in bending across its height, the top and bottom skins act like a beam's flanges, and the 10% rule applies to the part's height.
- **On sparse infill, the real lower limit is print quality, not strength.** Top layers have to bridge the gaps in 12% gyroid without pillowing. That takes about 0.8 to 1.0 mm (4 to 5 layers at 0.2 mm), which is what Bambu's default top shell of 1.0 mm is built around. Going thinner saves very little weight and risks holes in the top surface.
- **Bottom layers** sit on the bed and don't need to bridge, so 3 layers (≈ 0.6 mm) is enough unless the bottom face carries load.
- **Weight impact:** on tall parts, top and bottom skins are only a few percent of the mass. Walls and infill dominate, so start with walls. On flat, plate-like parts, the skins are most of the part, and the 10%-of-height rule matters more.

## Suggested lightweight settings (0.4 nozzle)

- Walls: **3**, with outer wall at 0.45 mm and inner walls at **0.6 mm** (≈ 1.65 mm total). Use **4** on parts thicker than about 20 mm, or anywhere near screw holes and pins.
- Top: **5 layers / 1.0 mm** at 0.2 mm layers, or 6 layers at 0.16 mm.
- Bottom: **3 layers / 0.6 mm**.
- Infill: **12% gyroid** with 0.6 mm lines and 25% infill/wall overlap, so the sparse infill stays tied to the walls.
- Keep the filament settings from the max-strength presets (temperature, cooling, flow). They make every gram stronger at no weight cost.

Compared with the max-strength process preset (6 walls, 40% infill), this should use roughly half the material on a typical 20 to 30 mm part. That figure is an estimate from the model above, not a measurement.

## Sources

- S1. CNC Kitchen, *The effect of extrusion width on strength and quality of 3D prints*. https://cnckitchen.com/blog/the-effect-of-extrusion-width-on-strength-and-quality-of-3d-prints
- S2. Raspberry Pi Official Magazine (HackSpace), *Experiments with strong 3D prints*. https://magazine.raspberrypi.com/articles/experiments-with-strong-3d-prints
- S3. CNC Kitchen, *Big nozzles: how do they make your 3D prints stronger?* https://www.cnckitchen.com/blog/big-nozzles-how-do-they-make-your-3d-prints-stronger
- S4. *Effect of Infill Density and Outer Shell on Flexural Behavior of FFF Printed PLA Samples*, Materials Science Forum 1167:39 (abstract only). https://www.scientific.net/MSF.1167.39
- S5. Journal of Emerging Investigators (2020), PLA tensile vs infill and shells. https://emerginginvestigators.org/articles/20-052/pdf
- S6. 3printr, summary of a video on ideal infill settings (secondary, not verified). https://www.3printr.com/video-examines-the-ideal-3d-printer-infill-settings-1269176/
- S7. Dobos et al., Journal of Polymer Engineering (2022), PLA sandwich specific load capacity. https://www.degruyterbrill.com/document/doi/10.1515/polyeng-2021-0223/html
- Also consulted: Kyushu Univ. Evergreen (2025), PLA sandwich bending, in which 10% infill had higher specific stiffness than 40%. https://catalog.lib.kyushu-u.ac.jp/opac_download_md/7342475/p564-573.pdf
