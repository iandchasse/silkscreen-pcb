# Checkpoint 2 — full re-review after L1 / R14 / C9 / Q1 changes (2026-09-18)

Second full review of the saved design, run after the owner applied the L1 (47 µH), R14 (2.2 Ω), C9 (4.7 µF) and Q1
manufacturer changes, regenerated the JLC/Toolkit set, and re-plotted the schematic and PCB PDFs. Items already found
in [`PREORDER_CONFIRMATION_AUDIT.md`](PREORDER_CONFIRMATION_AUDIT.md) were not re-derived unless their status changed.
Hardware only; no firmware was read. Evidence is in [`checkpoint-2/`](checkpoint-2/).

## 1. Verdict

**No blocker. The production set is current and the design imports cleanly from a plain clone.** Nothing found in this
pass changes the go/no-go from the first audit; the new items are medium/low and mostly first-article measurements.

| Check | Result |
|---|---|
| ERC / DRC on the saved files | ERC 39 warnings (unchanged, none real). DRC 0 unconnected, 0 parity issues; 14 clearance "errors" are the same fixed J1 pin-pitch (11) and J3 pad-gap (3) items; 26 starved thermals (was 27), 32 silk-edge (was 36), 12 silk-over-copper (was 11), 5 silk-overlap. No routing regression |
| Production Gerbers / drills vs the saved PCB | **Identical geometry** on all nine layers (0.000 mm² difference at 20 px/mm) and identical 288 PTH hits, tools and slots; the zip (12:22) is current although the PCB was re-saved at 12:23 |
| `positions.csv` (CPL) | 162 rows, all bottom side, 0 differences against a Toolkit emulation; Q2, Q9, R79–R82 present; SW6, TP3–TP5 and the DNP resistors absent |
| `bom.csv` | Equals the emulated BOM and `part_fields.csv` for every fitted part (61 codes over 162 placements) |
| Clean-clone import test | A copy of exactly what git would contain loads with identical ERC, DRC-equivalent results and a working 3D STEP export; every library path is `${KIPRJMOD}`-relative and all in-repo 3D models resolve |

## 2. The changes themselves

**Parity:** schematic and PCB agree for L1 (`Inductor_SMD:L_APV_ANR5040`, 47uH, Laird `TYS5040470M-10`, LCSC `C206267`),
R14 (2.2 Ω `RC0603FR-072R2L` / `C112307`), C9 (4.7u/50V `CL21A475KBQNNNE` / `C513770`) and Q1 (EVVOSEMI).

**L1 footprint:** 1.4 × 4.2 mm pads at ±1.85 mm (2.3 mm gap, 5.1 mm span). Both parts solder correctly — Laird's
terminal dimensions match exactly and Sunltech's (1.25 wide, 4.0 long) overlap both pads. Paste is a plain 5.9 mm²
aperture per pad; bridging and tombstoning are unlikely. Nearest different-net copper to the pads is ≥0.87 mm; no vias
under the part; no thermal starvation on L1, Q4, R14, D5 or C11.

**Placement/loop:** `EINK_SW` copper is 15.4 mm (was 16.5 mm) but the C10→L1→Q4→R14 loop area grew from ≈24 to ≈33 mm²
(+36 %), Q4→D5→C14 from ≈23 to ≈26 mm²; C10 is now ≈4.1 mm from L1 (≈3.1 mm). GDR/RESE are untouched by the move.

**Electrical:** peak inductor current scales by 3/2.2 ≈ 1.36× but is self-limited by Q4's gate drive (≈0.8 A), under the
1.1 A (Laird) / 1.3 A (Sunltech) Isat; R14 dissipation is only tens of mW; L1 DCR loss (0.27 / 0.65 Ω) is a few mW.
C9's effective capacitance at 24 V is estimated at 1.0–1.8 µF, so it meets TI's 1 µF minimum only narrowly.

## 3. New findings

| Sev | Finding | Fix / action |
|---|---|---|
| Medium | Only two of the eight ladder buttons can wake the ESP32 from sleep: both ladders idle at 3.3 V, and only `SW2` and `SW1` (≈33 mV) give a valid logic low; `SW3` (1.19 V) is in the undefined band and the rest read high | Use the power button / `SW1` / `SW2` as wake keys; for wake on every button add a diode-OR "any press" line on a future revision. Documented in HARDWARE.md §9 and DESIGN_REVIEW.md §9 |
| Medium | Boost loop area +36 % after the L1 move, and `GDR`/`RESE` still run ≈18 mm side by side on one layer at a 0.15 mm gap | Scope `GDR`, `RESE` and `EINK_SW` on the first article (DESIGN_REVIEW.md §13 step 12); on a revision, route RESE to J2 with a ground guard or a wider gap |
| Low | `Q7` (SD VDD switch) has no gate slow-down and turns on in microseconds into ≈1.1 µF plus the card | If card init glitches: 47–100 nF from gate to 3V3 (τ ≈ 50–100 µs with R78) |
| Low | Two ladder chords alias single keys inside tolerance (`SW3`+`SW9` vs `SW3`; `SW4`+`SW7` vs `SW4`) | Firmware: reject any ADC reading not close to one of the six clean levels of its ladder |
| Low | With the bigger C9 and L1 at power-up/hot-plug: 47 µH + 4.7 µF can ring toward 0.8–1.0 A on a fast 3V3 step (Isat 1.1 A), and the L2→body-diode→C9 path can ring to ≈2.5 A at battery hot-plug (≈1.3 A with 1 µF) | Check the 3V3 ramp and L2 saturation margin (`VLS252012HBX-100M-1`) on the bench, or accept brief saturation |
| Low | The `L1` reference text at (91.95, 112.3) is now clipped by mask (the one new silk-over-copper warning) | Nudge or shrink the reference text |
| Low | `L1`'s 3D model (`L_APV_ANR5040.step`) comes from KiCad's standard library, not the repo | Fine on KiCad 9.0.x, where it ships; mention in the README (done) |
| Info | DS3231M runs VCC-grounded from VBAT; the DC table specifies VIH relative to VCC | Confirm I²C reads/writes on the first article |

Verified clean in the pin-by-pin ESP32-S3 pass: reserved octal-PSRAM pins IO35–37 unconnected; strap pins
(IO0/3/45/46) see only their defaults, 33 Ω/ESD and the dev header; EN 10 k + 1 µF; ADC users (IO1, 2, 4, 8, 9) are
all ADC1; SD/EPD pins avoid the straps; every used pin's divider stays within 3.3 V; pinouts of U1/U2/U3/U5/U6–U13/Q1
match their datasheets; TP4056 CE (−0.3…10 V) is safe driven from 3V3 with USB absent; R72/R74 DNP leaves no leakage path.

## 4. Status of the earlier 113 findings

83 high/medium/low findings were tracked ([`checkpoint-2/status_table.md`](checkpoint-2/status_table.md)) — at the time of
that scan: 6 fixed, 10 partly, 5 owner-accepted (won't fix), 62 open. Since then the stale-documentation and stale-BOM
items were fixed in this same pass (v3/v4 upload BOMs, hand-build BOM, all Markdown files, images, part fields), so the
remaining **open items are physical** and were deliberately left for the owner:

- **Silkscreen:** no +/− marks at J5 (the schematic symbol has them), text below JLC's 0.15 mm stroke (all 175 refdes at 0.10 mm and the small back notes), the "GDEQ426T82" typos and "SW1-SW8" welcome text, credits-box overlaps at SW11/SW6, clipped `^` marks and the "3v3" label at the board edge, the new L1 reference clip.
- **Copper:** U9's isolated 2.4 mm² GND island, the R37/C9 sense return joined only through a shared boundary, seven starved decoupling-cap GND thermals (C3, C4, C21, C26, C27, C29, C37; C10 was fixed by its move), U11's thermal vias under paste windows, unenforced antenna keepout. *(Battery-path traces widened to 0.4 mm and `R27` changed to 0805 `C17477` later on 2026-09-18 — closed.)*
- **Fab:** the four 0.5 mm perforation polygons (below JLC's 1.0 mm minimum, unchanged from the accepted orders) and no `FT Rotation/Position Offset` fields for U2, U5, D8, D2, J4, U4, J7 (JLC's DFM has corrected these before).

## 5. Cost

Recomputed from the production `bom.csv` and live JLC prices (Extended-type count unchanged at 26; L1 and R14 swap one
Extended part for another and C9 joins the existing `C513770` line): **$33.23 / $22.70 / $16.25 / $12.61 per board**
at 5 / 10 / 30 / 100 boards (was $33.52 / $22.93 / $16.41 / $12.74), and $41.03 / $26.60 / $17.55 / $13.00 at a $3
Extended fee. Brand-conservative variant: $36.40 / $24.78 / $17.62 / $13.72. Scripts and prices are in
[`checkpoint-2/`](checkpoint-2/). Stock to watch: TPS923610DRLR (189 pcs, ≈107 needed at 100 boards); SLW5040S470MST 1.9 k.

## 6. Repository hygiene done in this pass

- Library tables trimmed to what the design uses (`fp-lib-table`: 6 libraries; `sym-lib-table`: 7); unused vendored files (the old `SRN3010C-100M` L1 land, the TSD05/TPD4E1U06/FS8205A footprints and models, legacy KiCad-5 MJTP1117 files, an unrelated STEP, an orphan `logo.kicad_sym`) were moved out of the repo.
- Stale clutter moved to `../de-link_pcb_pruned_2026-09-18/` (nothing deleted): old board STEP/GLB exports, another project's `minRead_pcb.*` and backups, NextPCB plugin output (`nextpcb/`, `database/`), stale Sept-12 Gerbers, `fabrication/BOM.csv` and `assembly/` exports, the first-order upload BOM and two unreferenced BOM spreadsheets. `nextpcb/` and `database/` are now gitignored.
- `docs/images/` regenerated from the new schematic PDF (all 21 block crops + full sheet at 400 dpi, indexed PNG) plus new `board-top.png` / `board-bottom.png` renders; README, HARDWARE.md, DESIGN_REVIEW.md, BOM.md, `fabrication/README.md`, THIRD_PARTY.md and this folder updated to the current values.
