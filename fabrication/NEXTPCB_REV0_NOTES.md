# NextPCB "Rev0" assembly upload: findings (2026-09-19 / 20)

What happened when this board was uploaded to NextPCB's Rev0 PCBA flow, what was fixed on our side, what could not
be fixed, and what it cost. Nothing here was an accepted or paid order; it is a record of a quote and its preview.
Everything about NextPCB's behaviour comes from what their site returned for our files, not from their documentation
(which says very little about bottom-side parts). Where something is a guess it says so.

Files involved: `fabrication/make_fab_files.py`, `fabrication/nextpcb_substitutes.csv`, `production/other_fabs/`
(`nextpcb_bom.csv`, `nextpcb_centroid.csv`, `split/`). How to regenerate: `python fabrication/make_fab_files.py --split` (see the root README, "Using a different factory").

## 1. What Rev0 is, and the format it wants

- **Submit as is.** Unlike JLCPCB, there is no "we will fix it" review: you upload, look at the quote and the preview,
  and either accept or re-upload. Plan on getting the files right yourself.
- **BOM.** NextPCB's Rev0 sample (`Rev0_Bom.xls`): `Designator*, Quantity*, Manufacturer Part Number*, Manufacturer,
  Package/Footprint, Description, Procurement Type, Customer Note`. Our `nextpcb_bom.csv` (with an extra `S/N` column
  and the manufacturer/package in the note) was parsed fine.
- **Rev0 rules, from the sample's header:** customer-supplied parts are *not* accepted; matched parts are bought by
  default; **unmatched parts stay unpopulated**; `DNP` means do not populate.
- **Centroid.** NextPCB's sample (`Rev0_Centroid.csv`) is a plain **`.csv`, not a zip**: `Designator, Mid X, Mid Y,
  Layer, Rotation`, coordinates with an `mm` suffix (4 decimals), `Top`/`Bottom`, integer rotation, LF line ends, no
  BOM. (An earlier reading of their standard quote page suggested zip/xlsx only; the Rev0 flow takes the csv.)
- **BOM and centroid designators must match** or the upload fails with "Designators in the PnP file do not match those
  in the BOM file (Missing/Inconsistent)".
- The centroid numbers are just KiCad's own position export. A `.pos` exported from KiCad's menu was numerically
  identical to `nextpcb_centroid.csv` for all 162 fitted parts, so the export is not the problem.

## 2. Problems found and how they were handled

| Problem | Cause | Fix |
|---|---|---|
| Error listing `J1 J5 J6 SW1-SW5 SW7-SW11` | BOM had the 13 through-hole parts, our centroid was SMD-only | `nextpcb_centroid.csv` now covers every fitted BOM part (162 rows at the time of the upload; 165 as regenerated 2026-09-21) |
| **DNP parts came back fitted** | NextPCB's importer **merges lines that share an MPN and drops the `DNP` mark**. `R43 R45 R58 R66 R74` were merged into the fitted 0 Ω line and `R72` into the 10 k line. Fitting `R74` beside `R73` shorts 3V3 to GND; `R43/R66` and `R45/R58` would put 3V3/`TP_INT` on the same pin as `R42/R44` and short SDA to SCL | DNP parts are left **out** of the BOM entirely. After every upload, check the matched BOM for `R43 R45 R58 R66 R72 R74 SW6` |
| `L1`, `J6` and the switches unmatched | The prime MPNs were not in NextPCB's stock | `fabrication/nextpcb_substitutes.csv` swaps them **for NextPCB only**: `J6` CJT `A2541HWR-2x6P`, `SW*` ALPS `SKHLLAA010`, `L1` Sunltech `SLW5040S470MST`. The prime table and the PCBWay BOM keep the prime parts |
| Duplicate JLC part numbers (found in the same session) | `bom_JLC_upload_v4_optimized.csv` (now `jlc_bom.csv`) listed `C14663` and `C28323` on two lines each, so JLC left `C24 C31 C20` unmatched | Lines merged. (`bom_JLC_upload_v3.csv`, which had the same duplicates, was deleted 2026-09-21) |

**Matched-BOM check** (our upload vs NextPCB's matched result, after the fixes): all 162 designators present, none
extra, no DNP refs, every requested MPN matched as requested (no silent substitutions), quantities and 10-board
overage consistent, resistor/capacitor values and packages agree. Third-party brands attached to generic parts
(`U3` TLV75533PDBVR as "DYW" rather than TI, `U5` Slkor, `Q2/3/7/8` "BY", `CR1` HXY, `D3` JXND) are what their stock
offered; `U3` matters because the sleep-current budget assumes TI's ~25 µA.

**ALPS `SKHLLAA010` as a substitute:** ALPS drawing No. 3 gives the same land as the MJTP1117/TS365ZJ (2 x d1.3 holes
7 mm apart, 2 x d1.0 holes 5 mm apart, 2.5 mm offset). Differences: catalog depth 7.22 mm vs 6 mm for the TS365ZJ, and
0.98 N vs about 2.5 N. Check the stem clearance and the feel.

## 3. The placement preview

NextPCB's preview is a **view from the back** (mirrored left to right), which makes a correct placement look wrong.
Un-mirrored and compared with the real footprints:

- **SMD parts and most through-hole parts land correctly:** `U4` within 0.5 mm, `U11` 0.1 mm, `L1`, `J1`, `J2`,
  `J3/J4`, `U13`, `D2` and the four bottom switches within about 1 mm, `SW4/5/11` within about 2 mm (`SW10` looked
  correct on an enlarged crop; its body merges with `J6`'s in the image). So front/back handling is not the problem.
- **Wrong or missing:** `J6` (body drawn flipped, on the opposite side of its pins), `SW1` and `SW7` (body rotated
  90 degrees, pin 1 still on pad 1), `J5` (about 90 degrees, weakest evidence). `J7` and `U10` have no body because
  they are not in NextPCB's DFA library.
- Their tool appears to put a THT model's **pin 1 at the centroid**; KiCad's origin for `J5`, `J6` and the switches is
  pin 1, so X/Y are right and the errors are rotations.
- **Rotation experiments changed nothing.** Two test centroids that changed only those four rotations (+90/+180 and
  -90/+180) produced an identical preview. `SW1` and `SW4` have identical input (270 degrees) yet render differently,
  so the tool is not a simple function of our numbers. A diagnostic that moves `U4`, `SW1` and `J6` by several
  millimetres was prepared to tell "tool ignores THT coordinates" from "preview not refreshed"; its result was not
  recorded. Conclusion so far: do not spend more time tuning THT coordinates.

## 4. The DFA error list, and our reading

| # | NextPCB message | Our reading |
|---|---|---|
| 1 | SMT/THT interference | Probably a knock-on of the misplaced THT bodies |
| 2 | Pad edge clearance under 0.15 mm | The only real pad pairs under 0.2 mm are `J1`'s USB-C pins, 0.15 mm apart: the connector maker's land pattern. Confirm |
| 3 / 4 | SMT / THT pin count does not match pad count | Likely the switches: our land has 4 holes, the ALPS model 2 terminals plus snap-in legs. Could not reproduce |
| 5 | `J7`, `U10` not in the DFA library | Informational |
| 6 / 7 | Hole smaller than the square pin's diagonal; pin too short to protrude | Their model-based checks; could not reproduce and no part was identified |

Their "preview" for each item only highlights an area of the board, not the part.

## 5. Cost and recommendation

- NextPCB Rev0 quote for 10 boards including shipping: about **$296** (as quoted to us), with the through-hole parts
  bought separately.
- The 13 through-hole parts from DigiKey (list prices 2026-09-20): `J1` USB4085-GF-A $0.772, `J5` S2B-PH-K-S $0.099,
  `J6` PPPC062LJBN-RC $0.984, `SW` MJTP1117 $0.5102 at 100. For 10 boards that is about **$70** before shipping and
  tax; the actual DigiKey order for 12 boards was about $102.
- Total about **$400**: roughly the same as, and slightly under, JLCPCB's price with through-hole assembly included.
  The NextPCB route leaves 74 hand-soldered joints per board (about 800 for 10) and the unresolved DFA and
  sourcing questions above.

**Recommendation:** for a full build, use JLCPCB with through-hole included. Use NextPCB Rev0 only for an SMD-only
order: generate with `python fabrication/make_fab_files.py --split` and upload `split/nextpcb_bom_smd.csv` +
`split/nextpcb_centroid_smd.csv` (152 parts as of 2026-09-21, designators identical), and hand-solder the through-hole parts. Whether
NextPCB would ship the through-hole parts loose was not established; Rev0 has no field for "buy but do not solder".
