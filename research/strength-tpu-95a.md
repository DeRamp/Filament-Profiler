# Max-strength settings for Overture TPU 95A on the Bambu Lab H3C (0.4, 0.6 and 0.8 mm nozzles)

These presets are in `presets/bambu/`. Each nozzle has one filament preset and one process preset:

| Nozzle | Filament preset (inherits) | Process preset (inherits) |
|---|---|---|
| 0.4 | `Overture TPU 95A Max Strength @BBL H3C` (`Generic TPU @BBL H3C`) | `0.16mm Max Strength (TPU 95A) @BBL H3C` (`0.16mm Standard @BBL H3C`) |
| 0.6 | `… @BBL H3C 0.6 nozzle` (`Generic TPU @BBL H3C 0.6 nozzle`) | `0.24mm Max Strength (TPU 95A) @BBL H3C 0.6 nozzle` (`0.24mm Balanced Quality … 0.6 nozzle`) |
| 0.8 | `… @BBL H3C 0.8 nozzle` (`Generic TPU @BBL H3C 0.8 nozzle`) | `0.32mm Max Strength (TPU 95A) @BBL H3C 0.8 nozzle` (`0.32mm Balanced Quality … 0.8 nozzle`) |

These values come from research. None have been measured on this filament yet. Published strength data for TPU is much thinner than for PLA, so the reasoning behind each value is given in the tables below.

## Before printing

- **Dry the spool at 70 °C for 7 hours** (O3). TPU absorbs moisture quickly, and wet TPU strings badly and forms bubbles. Bambu dries its own TPU at 70 °C for 8 to 12 hours before testing (B1).
- **Feed from an external spool, not the AMS.** 95A TPU is too soft for most AMS paths.
- **Orient parts so the load runs along the layers.** Bambu measured TPU 95A at 29.6 MPa in X-Y but only 23.2 MPa in Z, about 22% weaker across the layers (B1). The gap is much smaller than PLA's, which loses about half its strength across layers, but it still matters.

## Filament preset (same for all three nozzles)

| Setting | Generic TPU default | Max strength | Why |
|---|---|---|---|
| Nozzle temperature | 230 °C | **225 °C** | Overture's range is 210 to 230 °C, and Overture measured its published strength (about 30 MPa) at 225 °C (O1, O2). A TPU 95A study on a Bambu P1S found strength fell slightly as temperature rose from 210 to 230 °C, but the authors called it a screening result and the effect was not significant (p = 0.15) (I1). 225 °C balances good layer bonding against that small downward trend. |
| Temperature range | 200 to 250 °C | 210 to 230 °C | Overture's stated range (O1). |
| Bed | 35 °C | **40 °C** | Within Overture's 25 to 60 °C range (O1). Improves first-layer grip on larger, solid parts. |
| Max volumetric speed | 3.2 mm³/s | **3.2 mm³/s** | Overture specifies 20 to 40 mm/s (O1). On a 0.4 nozzle with 0.6 × 0.16 mm lines, 3.2 mm³/s works out to about 33 mm/s. The P1S study got its best strength at 40 mm/s, and higher speeds reduced it (I1). This limit is set by how fast the extruder can push soft TPU, so it stays the same for the 0.6 and 0.8 nozzles. |
| Flow ratio | 1.00 | 1.00 | No TPU data supports over-extrusion, and extra TPU blobs and strings. Left unchanged. |
| Part fan min / max | 100 / 100% | **50 / 70%** | Less cooling keeps layers hotter so they bond better. This is the same mechanism measured for PLA (6 in the PLA write-up). Overture recommends 50 to 100% fan for TPU (O3), so the minimum stays at 50%. |
| Fan ramp layer time | 100 s | 30 s | Keeps the fan at its minimum except on fast layers. |
| Overhang fan | 100% above 95% overhang | **100% above 25% overhang** | Gives overhangs full cooling sooner, to make up for the lower base fan. |
| Aux fan | 80% | **0%** | Avoids cooling the whole part between layers. |

## Process presets

| Setting | 0.4 | 0.6 | 0.8 | Why |
|---|---|---|---|---|
| Layer height | 0.16 mm | 0.24 mm | 0.32 mm | 40% of the nozzle diameter. In the TPU study, 0.16 mm was best, and strength dropped above the middle setting (I1). The PLA rule (stay under half the nozzle) agrees. |
| Wall loops | 6 | 4 | 3 | About 3.2 to 3.5 mm of wall in every case, the same as the PLA+ presets. |
| Inner wall and infill line width | 0.60 mm | 0.90 mm | 1.20 mm | 150% of the nozzle (CNC Kitchen's extrusion width test). |
| Outer wall line width | 0.45 mm | 0.62 mm | 0.82 mm | Kept close to the nozzle size for a clean outer surface. |
| Infill | **100% rectilinear** | same | same | Overture, Bambu, and the TPU study all measured strength on solid parts (O1, B1, I1). In that study, infill pattern was the second biggest factor, with rectilinear and grid best (I1). **This makes parts as stiff as 95A gets.** If you need the part to squish, use 15 to 30% gyroid instead, but expect much lower strength. |
| Top / bottom layers | 7 / 5 | 5 / 4 | 4 / 3 | Same as the PLA+ presets. With 100% infill these mostly affect the surface finish. |
| Avoid crossing walls | off | **on** | on | Travel moves stay inside the part, which cuts down TPU's surface stringing. |
| Speeds | 40 mm/s | 40 mm/s | 40 mm/s | The 3.2 mm³/s limit sets the real speed: about 33, 15 and 8 mm/s for the 0.4, 0.6 and 0.8 presets. |

## Trade-offs

- **Slow.** The 0.6 and 0.8 nozzles are not faster for TPU, because the extruder limits flow, not the nozzle. Their wider lines just move more slowly. For TPU, the 0.4 preset is the practical choice. The bigger nozzles mainly help if you want thicker walls with fewer lines.
- **Stiff.** 100% infill gives the strongest part, but also the least flexible.
- **Stringing.** Keep the filament dry. Retraction is left at Bambu's TPU defaults.

## Sources

- O1. Overture TPU technical data sheet v2.1 (Jan 2024): nozzle 210 to 230 °C, bed 25 to 60 °C, 20 to 40 mm/s, tensile 29.1 MPa (X-Y), elongation 332%, tested at 225 °C, 30 mm/s, 100% infill. https://cdn.shopify.com/s/files/1/0207/3624/5824/files/OVERTURE_TPU_TDS_EN.pdf
- O2. Overture TPU technical data sheet v5.1 (Aug 2024): 30.1 MPa, same test conditions. https://attachments.gorgias.help/qgaXzxaEa0NxvDWO/hc/MdAV17qLJw2ZWgaX/2024080907-06af96df-6433-4df2-8ec5-134b9c8672e9-overture_tpu_tds_en_v5.1.pdf
- O3. Overture, *TPU filament print settings guide* (2026): start at 225 °C, fan 50 to 100%, dry at 70 °C for 7 h. https://overture3d.com/blogs/overture-blogs/tpu-filament-print-settings-guide
- B1. Bambu Lab TPU 95A technical data sheet v2.0 (third-party mirror): X-Y 29.6 MPa vs Z 23.2 MPa. https://www.3drepublika.com/wp-content/uploads/2023/10/Bambu-TPU-95A-Technical-Data-Sheet.pdf
- I1. Ma et al., RCMA 36(2):243–255 (2026), TPU 95A on a Bambu P1S, Taguchi L9 design. Best result 21.1 MPa at 210 °C, 40 mm/s, 0.16 mm, rectilinear. Factor contributions: temperature 38%, infill pattern 27%, speed 4%, layer height 0.2%. The authors describe it as a screening study. https://iieta.org/download/file/fid/193942
- See also `research/strength-super-pla-plus.md` for the general layer-adhesion research (temperature, cooling, line width, walls).
