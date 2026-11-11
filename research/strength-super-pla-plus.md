# Max-strength settings: Overture Super PLA+ on a Bambu Lab H3C (0.4 and 0.6 mm nozzles)

The presets are in `presets/bambu/`:

- **Filament:** `Overture Super PLA+ Max Strength @BBL H3C`, which inherits `Generic PLA @BBL H3C`
- **Process:** `0.16mm Max Strength (Super PLA+) @BBL H3C`, which inherits `0.16mm Standard @BBL H3C`

These are the best values the research supports. **None of them have been measured on this filament yet.** Use the FP-A protocol to check them before you treat them as final.

## Import

1. In Bambu Studio, go to **File > Import > Import Configs...** and select both `.json` files.
2. Pick the H3C with the 0.4 mm nozzle. Then choose the filament preset and the process preset.
3. Run **Calibration > Flow Dynamics** (pressure advance) with this filament preset. It hasn't been calibrated for your spool.
4. **Dry the filament before printing**, for example 50 to 55 °C for 6 to 8 hours. Wet filament forms bubbles at these temperatures, and those bubbles erase the gains (source 3).

## What matters more than any setting

**Part orientation.** Layer bonds are the weak point. A part printed upright holds about half of what a flat part holds: 31 vs 63 MPa (1), and 19 vs 52 MPa (9). In one study, orientation accounted for 98% of the variation in strength (9). **Orient each part so the main load runs along the layers, not across them.** If you can't, tilting the part 45° recovered about 27% of the loss (1). No slicer preset can do this for you.

## Filament preset

| Setting | Bambu default | Max strength | Why |
|---|---|---|---|
| Nozzle temperature | 220 °C | **225 °C** | Hotter nozzles bond layers better, up to a point. PLA layer adhesion went 20 MPa at 190 °C → 40 MPa peak at 230 °C → 32 MPa at 270 °C (3). On a Bambu X1C, upright PLA at 230 °C held 2 to 4.7 times more than at 190 °C, and it stayed strong even at high speed (7). Infill at 230 °C beat 200 °C (6). Overture rates Super PLA+ at 190 to 220 °C (10), so 225 °C goes just past that toward the CNC Kitchen peak. Raise it to 230 °C if stringing stays acceptable. |
| Bed temperature | 55 °C | **60 °C** | Top of Overture's 40 to 60 °C range (10). Helps the larger, denser parts stay stuck down. This setting is not about strength. |
| Flow ratio | 0.98 | **1.01** (about +3%) | Tensile strength peaked at an extrusion multiplier of 1.03: 51.1 MPa at 0.97 rose to 57.1 MPa at 1.03, then fell at 1.05 as the surfaces got rough. Porosity dropped from 5.8% to almost 0 (8). 0.98 × 1.03 ≈ 1.01. |
| Max volumetric speed | 12 mm³/s | **10 mm³/s** | Slower flow gives the plastic more time to heat, so it bonds better. A CNC Kitchen nozzle test peaked at 36 MPa at 12 mm³/s and fell to 31 MPa as flow rose (index summary, 4). Slower printing also gave modestly higher strength on a Bambu printer (11). This cap is what really limits print speed. |
| Part fan, min / max | 100 / 100% | **30 / 60%** | Less cooling means hotter layers and better bonding. Infill printed with the fan off was 2 to 5% stronger, and the fan cooled the plastic by about 8 °C (6). PLA still needs some airflow for detail, so the fan isn't off. |
| Fan ramp layer time | 100 s | **30 s** | The fan stays at the minimum unless a layer takes less than 30 s. Bambu's default of 100 s keeps the fan near maximum on most parts. |
| Overhang fan | 100% above 50% overhang | **100% above 25% overhang** | Gives overhangs full cooling sooner, to make up for the lower base fan speed. |
| Auxiliary fan | 60% | **0%** | Blows on the whole part and cools layers before they bond. A hot chamber helps layer bonds (ABS: 21 → 29 MPa, 5), but PLA must not run in a heated chamber. Turning off the aux fan keeps more heat without heating the chamber. |

## Process preset

| Setting | Bambu default (0.16 Std) | Max strength | Why |
|---|---|---|---|
| Layer height | 0.16 mm | **0.16 mm** | Layers no thicker than half the nozzle. 0.15 mm gave the best upright strength, and 0.3 mm halved it (2). The best tensile result in another study was also at 0.16 mm (9). |
| Wall loops | 2 | **6** | Strength follows how much material is in the walls (12). Walls add more strength per gram than infill: 2 walls held 20 kg, 4 walls held 33 kg (13). Bambu's own "Strength" preset uses 6 (14). |
| Inner wall / infill / solid infill line width | 0.42 to 0.45 mm | **0.60 mm** (150%) | Layer adhesion peaked near 150% of the nozzle width. 2 walls at 200% held about 39 kg, versus 20 kg at 100%, in similar print time (13). |
| Outer wall line width | 0.42 mm | **0.45 mm** | Kept narrow so the outside stays accurate. Wide lines rough up the surface, and a rough surface concentrates stress (13). |
| Top surface line width | 0.42 mm | 0.42 mm | Unchanged. Keeps the top surface clean. |
| Top / bottom shells | 5 / 3 layers | **7 layers (1.1 mm) / 5 layers (0.8 mm)** | Thicker skins act like extra walls on the top and bottom faces. Bambu's Balanced Strength preset also adds top and bottom layers (14). |
| Sparse infill | 15% grid | **40% gyroid** | More infill adds strength, about 1.5 kg per extra 10% in one simple test (15). Gyroid is strong in every direction, and grid is among the weakest patterns (16). Above about 40%, walls add more strength per gram (12, 13). |
| Infill/wall overlap | 15% | **25%** | Ties the infill into the walls more firmly. This is an engineering judgement; no study tested it. |
| One wall on top surfaces | on | **off** | Puts full walls on top surfaces as well. |
| Wall / infill speeds | 200 to 600 mm/s | **120 to 150 mm/s** | The 10 mm³/s cap limits speed anyway: 0.6 mm × 0.16 mm lines at 10 mm³/s run at about 104 mm/s. Lower speed targets keep the printer from constantly speeding up and slowing down. |
| Seam | aligned | aligned | Unchanged. |

## 0.6 mm nozzle version

Files: `Overture_Super_PLA-plus_Max_Strength_0.6_nozzle.json` (filament preset, same values as the 0.4 version, limited to the H3C 0.6 nozzle) and `0.24mm_Max_Strength_Super_PLA-plus_0.6_nozzle.json` (process preset, inherits `0.24mm Balanced Quality @BBL H3C 0.6 nozzle`, which Bambu describes as its strength profile for the 0.6 nozzle).

The same rules, scaled to the bigger nozzle:

| Setting | Bambu default (0.24 BQ 0.6) | Max strength | Why |
|---|---|---|---|
| Layer height | 0.24 mm | **0.24 mm** | 40% of the nozzle, the same ratio as 0.16 on a 0.4. Stays well under the half-nozzle limit (0.30 mm) (2). |
| Wall loops | 2 | **4** | 0.62 + 3 × 0.9 ≈ 3.3 mm of wall, close to the 0.4 preset's ≈ 3.45 mm. Strength follows wall thickness, not line count (12). |
| Inner wall / infill / solid infill width | 0.62 mm | **0.90 mm** (150%) | Same 150% rule as the 0.4 preset (13). |
| Outer wall / top surface width | 0.62 mm | 0.62 mm | Unchanged, to keep surfaces and outer dimensions clean. |
| Top / bottom shells | 3 / 3 layers | **5 layers (1.2 mm) / 4 layers (0.96 mm)** | Matches the thickness of the 0.4 preset. |
| Sparse infill | 15% grid | **40% gyroid** | Same as the 0.4 preset (15, 16). |
| Infill/wall overlap, one wall on top | 15%, on | **25%, off** | Same as the 0.4 preset. |
| Speeds | 200 to 350 mm/s | **80 to 100 mm/s** | The 10 mm³/s cap limits speed anyway: 0.9 × 0.24 mm lines run at about 46 mm/s. |

Notes for the 0.6 nozzle:
- Max volumetric speed stays at **10 mm³/s**. The melt rate depends on the hotend, not the nozzle size, and strength dropped above about 12 mm³/s (4). A 0.6 nozzle isn't stronger per gram, but it puts down a thick wall in less time (12). Because of the cap, this preset will not be faster than the 0.4 one. Raise the cap to 12 to 14 mm³/s if print time matters more than the last few percent of strength.
- Fine details and small text will be coarser than with the 0.4 nozzle.

## What these presets don't change, and why

- **Annealing:** PLA tensile strength rose about 7.5%, but layer adhesion stayed flat, and parts warped up to 10% (17). Not worth it for strength.
- **Brick layers (staggered walls):** +14% for PLA (18), but Bambu Studio doesn't support it.
- **Ironing:** a marginal gain at most (11). Left off.
- **Heated chamber:** keep the H3C door closed for steady temperatures, but don't heat the chamber for PLA. The CNC Kitchen chamber test advises against it because of heat creep and curling (5).
- **Bigger nozzle:** a 0.6 mm nozzle gets the same strength in less time, not more strength per gram (12). That would need a separate preset.

## Trade-offs to expect

- **Print time** goes up a lot, about 2 to 3 times Bambu's Standard preset, because of the 10 mm³/s cap and the heavier walls and infill.
- **Dimensional accuracy:** the +3% flow and hotter nozzle make parts slightly oversized, and holes come out slightly undersized. Check fits with FP-D and FP-F, and keep a separate accuracy preset for parts that need tight fits.
- **Overhangs and bridges** will be a bit worse because of the lower fan speed. Keep overhangs under about 45° or add supports.
- **Stringing** may increase at 225 °C. Drying the filament helps more than anything else.

## Sources

1. CNC Kitchen, *Stop Printing Flat: The 45° Secret for Stronger Parts* (2025). https://cnckitchen.com/blog/stop-printing-flat-the-45-secret-for-stronger-parts
2. CNC Kitchen, *The influence of layer height on the strength of FDM 3D prints* (2019). https://cnckitchen.com/blog/the-influence-of-layer-height-on-the-strength-of-fdm-3d-prints
3. CNC Kitchen, *The Influence of Extrusion Temperature on Layer Adhesion* (2020). https://cnckitchen.com/blog/the-influence-of-extrusion-temperature-on-layer-adhesion
4. CNC Kitchen blog index, CHT nozzle / flow rate entries. https://www.cnckitchen.com/blog. Index summary only; the full post was not read.
5. CNC Kitchen, *Does a heated chamber make your 3D prints stronger?* (2023). https://www.cnckitchen.com/blog/does-a-heated-chamber-make-your-3d-prints-stronger
6. Croccolo et al., *Effects of infill temperature on the tensile properties and warping of 3D-printed PLA*, Progress in Additive Manufacturing (2023). https://cris.unibo.it/retrieve/3ff285c8-4422-42dd-b114-fb623c66189d/
7. Kruzliak et al., *Effect of selected parameters on FDM high-speed 3D printed specimen properties*, MM Science Journal (Oct 2025), Bambu X1C. https://www.mmscience.eu/journal/issues/october-2025/articles/effect-of-selected-parameters-on-fdm-high-speed-3d-printed-specimen-properties
8. Lendvai et al., Progress in Additive Manufacturing 10:619–629 (2025), extrusion multiplier study. https://link.springer.com/content/pdf/10.1007/s40964-024-00646-5.pdf
9. Megersa et al., Materials 17(23):5951 (2024). https://www.mdpi.com/1996-1944/17/23/5951
10. Overture Super PLA+ technical data sheet v1.1 (Jan 2024). https://cdn.shopify.com/s/files/1/0207/3624/5824/files/OVERTURE_SUPER_PLA__TDS_EN.pdf
11. Sawicki / Lorkowski et al., Materials 18(8):1765 (2025), Bambu A1 mini speed and ironing study. https://www.mdpi.com/1996-1944/18/8/1765
12. CNC Kitchen, *Big nozzles: how do they make your 3D prints stronger?* (2019). https://www.cnckitchen.com/blog/big-nozzles-how-do-they-make-your-3d-prints-stronger
13. CNC Kitchen, *The effect of extrusion width on strength and quality of 3D prints* (2019). https://cnckitchen.com/blog/the-effect-of-extrusion-width-on-strength-and-quality-of-3d-prints
14. Bambu Studio system presets: `0.20mm Strength @BBL X1C` (6 walls, 25% infill) and `0.20mm Balanced Strength @BBL H2D`. https://github.com/bambulab/BambuStudio/tree/master/resources/profiles/BBL/process
15. Raspberry Pi Official Magazine (HackSpace), *Experiments with strong 3D prints*. https://magazine.raspberrypi.com/articles/experiments-with-strong-3d-prints. A simple single-run test.
16. All3DP, *The Strongest Infill Patterns* (2026). https://all3dp.com/2/strongest-infill-pattern/. A review article; it contains no new measurements.
17. CNC Kitchen, *Better performing 3D prints with annealing, part 1: PLA* (2019). https://www.cnckitchen.com/blog/better-performing-3d-prints-with-annealing-but-part-1-pla
18. CNC Kitchen, *Brick Layers: make 3D prints stronger* (2024). https://www.cnckitchen.com/blog/brick-layers-make-3d-prints-stronger

Other context: CNC Kitchen found PLA+ to be tougher but not stronger than plain PLA, with similar layer adhesion, about 75% of flat strength (https://www.cnckitchen.com/blog/the-difference-of-pla-and-pla-tested-feat-polymaker). Filament color alone changed layer adhesion from 31 to 46 MPa (https://www.cnckitchen.com/blog/how-the-color-of-pla-filament-influences-3d-printed-part-strength), so results from one Super PLA+ color may not match another.
