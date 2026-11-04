# Trace audit: durability and EMI/EMC (Rev 1.03 working copy, 2026-11-03)

Board-wide check of the routing on branch `1.03`, as of the uncommitted working copy. That copy includes:

- N1–N7;
- the N7 placement fixes;
- the `U10`-corner changes in section 1;
- the free fixes in [section 1b](#1b-free-fixes-applied-after-the-audit), made the same day after the first audit run. The figures and numbers below are from the board after section 1b; where a finding changed, the summary gives both;
- `U10` moved to TI's example land pattern ([section 1c](#1c-u10-on-tis-example-land-pattern)), approved after the TI drawing was checked;
- teardrops, added by the designer in KiCad, and a trace tidy of 19 traces ([section 1d](#1d-teardrops-and-trace-tidy));
- the layout fixes chosen in the owner review ([section 1f](#1f-layout-fixes-applied-after-the-review-2026-11-03)): the `F3` pour keep-out, copper moved off five mounting holes, and the right-edge bundle moved in.

The checks are scripted on the board geometry exported from KiCad (section 7), so every number can be re-run. It is a geometric audit, not a field solver or EMC test.

- Currents and voltages come from the design, not from measurement.
- Spacing limits are IPC-2221B values.
- EMI findings are relative ("largest loop", "longest unreferenced run"), not emission levels.

The cited reference values are collected in [section 6](#6-references).

## 0. Summary

| # | Area | Finding | Severity | Fix | Cost |
|---|---|---|---|---|---|
| T1 | `U10` corner (case 1) | GND pour 0.25 mm and a GND via 0.29 mm from the boost switch node; switch-node trace wrapped the pin-6/pin-5 corner | was Medium | **Done** (section 1): pour pulled back to 0.5 mm, via moved, straight 0.35 mm feed, direct pin 4 → `C9` ground | — |
| T2 | ESD returns | The USB ESD array `U6`'s GND pad is 3.9 mm from the nearest GND via and joins the pour with **one** thermal spoke. `U7` and `U9` are similar (3.2–3.6 mm), and the USB TVS `CR1` is 5.1 mm from a via | was **High** | **Done** for `CR1`, `U6`, `U7` and `D3` (section 1b): a GND via 1.0–1.85 mm from each GND pad, joined by a direct track, and solid pad-to-pour connections. `U9` has no legal via spot (its ground is a 5 mm, 0.2 mm trace); moving it to `J7` (T3) fixes it | — |
| T3 | ESD placement | The microSD ESD arrays `U1`/`U9` sit 17–33 mm of trace from `J7` (11–23 mm straight). `U6` is 12 mm from `J1`, `CR2` 45.6 mm from `J6` pin 7, and `U7` 11–19 mm from `J4` | Medium | **Accepted** (owner, 2026-11-03): the arrays can't be moved to their connectors, and it is not worth a respin. `U9`'s ground stays a trace (T2) | — |
| T4 | Power vias | Every layer change on the main power path is a **single** 0.3 mm via: `VBUS_PRE_FUSE` (×2), `USB_VBUS` (×3), `LDO_IN` (×2, one at `U2`), `P+` (×5), `B+` (×2). One via carries about 1.35 A at a 10 °C rise and 1.8 A at 20 °C (JLC's 18 µm plating), so 1 A in use is fine; 1.8–1.95 A in a fault is at the 20 °C point. Espressif asks for at least two vias where a main power trace changes layer | was Low-Medium | **Done for 10 of 13** (section 1b): a second via, stitched to the first on both layers, at both `VBUS_PRE_FUSE`, all three `USB_VBUS`, `LDO_IN` at `U2`, three `P+` and one `B+`. Still single, with no legal spot within 2 mm: `P+` at (78.6, 86.9) and (88.6, 78.7), `B+` at (90.4, 83.4). The frontlight `LDO_IN` branch (≤ 0.3 A, behind `F3`) stays single on purpose | — |
| T5 | E-paper boost | Largest hot loop on the board: 38.7 mm² switching (`Q4`→`D5`→`C14`→GND→`R14`) and 32.6 mm² input. `C14` is about 8 mm from `D5` | was Medium, now Low | **Left as is** (section 1e). No reference design adds a capacitor here: all use one `PREVGH` capacitor, drawn at the diode, so the faithful fix would be moving `C14`. There is no legal spot by `D5`; it would take a swap with `C20` and two re-routes. A loop estimate puts the emissions far below Class B | — |
| T6 | Teardrops | None on the board: 767 track→pad and 267 track→via joints are narrower than 60 % of the pad or via they enter | Medium | **Done** by the designer in KiCad (section 1d): 871 teardrops. 17 of them were removed with the traces the tidy rewrote and were re-added with the same command on 2026-11-03 (862 on the board after all fixes) | — |
| T7 | Starved thermals | 21 GND pads connect to the pour with one spoke, including power and ESD parts: `U2`, `U3`, `U11`, `C3`, `C4`, `C21`, `C25`, `D3`, `U6`, `U7`, `R37` (frontlight current sense) and `J7`'s shell | was Medium | **Done** (section 1b): solid connection on those 11 pads, plus `C37` (microSD supply), `C27`/`C29` (button filters) and `J7`'s ground pin and shell. Five are left on purpose: `R50`/`R41` (DC only), `J2` pin 17, and the through-hole `J6` pin 4 and `SW9` pin 1 | — |
| T8 | Cut line | When the board is cut at y = 61.86, raw `P+` (0.4 mm, front copper) is cut open at the new edge. `F2` sits above the line, so the stub is unfused. Ten other nets cross too (3V3, `LED_SW` up to 26 V, `C-`/`W-`, I²C, …) | Medium (only for cut boards) | **`F2` cannot move** (checked 2026-11-03, section 2.3): below the line the only room is the strip at `J5`'s mating face, which a fitted battery plug covers. Documented instead: the README's cut instructions now say to deburr, check `P+` to GND and seal the cut edge before reconnecting the battery | docs |
| T9 | Panel decoupling | `J2`'s supply pins (15/16, `VCI`/`VDDIO`, now on `EINK_3V3` behind `F6`) are 13 mm from their capacitor `C22` | was Medium, now Low | **Left as is** (section 1e). Every reference design puts this capacitor on pins 15/16, but the nearest legal spot on the `EINK_3V3` trace is about 11 mm from the pins. The 16 mm of trace adds about 16 nH, which is millivolts at the panel's current steps; `F6` sets anything slower. First-board check: `EINK_3V3` ripple at pins 15/16 ([NEXT_REVISION §6](../NEXT_REVISION.md#6-verification)) | — |
| T10 | Edge copper | The LED cathode `C-` (up to about 26 V, PWM-switched) runs 68.6 mm along the right board edge on F.Cu at 0.476 mm from the edge | was Medium-Low | **Done as far as it goes** (section 1f). The bundle (`C-`, `W-`, `LED_SW`, then `I2C_SDA`) moved 0.27 mm in, and `C-` is now 0.746 mm from the edge. The limit is the `SW` net class's 0.25 mm between `LED_SW` and `SW4`'s pads; 1 mm would need `SW4`/`SW1` moved | — |
| T11 | Stitching | Ground-stitching vias are up to 11.8 mm apart at the top of the `J6` arm (x 92–104, y 37–40) and 11.7 mm along the perimeter; 95th percentile 8.4 mm. Infineon's edge guidance is ≤ 5 mm; λ/20 at 2.4 GHz is 6.2 mm in air and 2.9 mm in FR-4 | Low-Medium | **Partly done** (section 1b): 14 edge GND vias, three across the top of the arm. Worst gap 11.8 → 9.7 mm (perimeter 11.7 → 9.2 mm, 95th percentile 8.4 → 7.1 mm). The rest needs moves: the right edge has no front pour (the `C-` run, T10), and the left-edge gaps sit in switch courtyards and beside the antenna | free (moves) |
| T12 | Antenna | The ESP32 footprint's keep-out forbids tracks and vias but not pours, so 2.2 mm² of GND pour per layer sat inside it | was Low-Medium | **Done.** The keep-out now forbids zone fills (section 1b). The board already has a 6.3 × 18.7 mm cut-out under the antenna (x 44.26–50.6, y 93.3–112.0): the antenna area sits over air except for a 0.15 mm sliver. The first version of this audit missed the cut-out (section 1e) | — |
| T13 | HV spacing at fine-pitch pins | `J2` pins 21/22 put VGH (≈ +22 V) next to VSL (≈ −17 V): about 40 V across 0.2 mm of exposed pad, where IPC-2221B A6 asks for 0.40 mm (B2 0.60). Pins 19–24 and `J3` (≤ 26 V) are 0.2 mm against A6's 0.25. All of this is the 0.5 mm-pitch FPC pinouts. Since section 1c, `U10`'s pins 4/5 (GND/VOUT) and 5/6 (VOUT/SW) are also 0.20 mm apart (TI's land; the part's own leads can be 0.23 mm apart) | Low (inherent) | Keep the area clean (no flux residue); optional local coating (A7: 0.13 mm) | process |
| T14 | HV vs nearby copper | 9 places where mask-covered copper or a tented via passed an exposed high-voltage pad at 0.154–0.248 mm, against A6's 0.25 mm: `COLOR_SEL` at `Q5` pin 3 (`W-`), `/COLOR_SEL_INV` at `Q6` pin 3 (`C-`), VCOM at `D6` pin 2 and at `C16` pin 2, `/P+_FUSE` at `D8` pin 1, a GND via at `Q5` pin 3, a VGH via at `C20` pin 2, the charge-pump node at `D4` pin 2, `BUTTON_ADC_1` at `Q6` pin 3. The first run listed 7; the `Q6` and `C16` spots were hidden by a closer pair of the same nets until the audit ranked pad pairs separately (section 2.2). Separately, `W-`/`C-`/panel rails ran 0.15 mm from the GND pour (fine as mask-covered copper, B4 0.05 mm) | was Low | **Done** (section 1b): all 9 are now 0.263–0.304 mm. The pour is pulled back 0.3 mm from the panel rails and 0.25 mm from the LED-cathode pads | — |
| T15 | DRC hygiene | All 7 DRC errors were built into footprints: `J3`'s 0.5 mm-pitch pads against the SW clearance (3), and `J1`'s peg holes (4) | was Low | **Done** (section 1b): two rules scoped to those footprints, at the as-built values. DRC reports 0 errors, so a new error stands out (section 2.6) | — |
| T16 | Track hygiene | 11 segments lying wholly inside another segment of the same net, 4 zero-length segments, sharp joints, 4 dangling front-copper stubs near the bottom buttons | was Low | **Done** (section 1b): the 15 redundant segments are removed. The 4 stubs stay: they are the landing tabs for front-mounted buttons ([HARDWARE.md, "Things that look like mistakes"](../HARDWARE.md#things-that-look-like-mistakes-and-are-not)). Section 1d also straightens 19 traces with needless kinks | — |
| T17 | Mounting holes | Other-net copper 2.07–2.45 mm from hole centres. The KiCad M2 DIN965 footprint's head circle is Ø3.8 mm and its courtyard Ø4.3 mm (radius 2.15), so `Net-(Q3-G)` at `H5` (2.07 mm) is inside the courtyard. `B+` there is at 2.30 mm | was Low-Medium | **Done for five of eight** (section 1f). `H2`, `H4` and `H6` are clear, and `B+` (`H5`), `I2C_SDA` (`H1`) and `R19`'s net (`H3`) moved out. Three can't move without moving parts: `Net-(Q3-G)` at `H5` (2.075 mm), boxed in by `C34` and the `U5-CS` via; `/P+_FUSE` at `H1` (2.214 mm), by the `C-` routing at `D8`; `Net-(R20-Pad1)` at `H3` (2.15 mm), by the board edge | — |
| T18 | USB pair | `DP` has 5 vias (TI's USB guide: ≤ 4 per trace), `DN` 2. Skew 0.8 mm; coupled for 57 % of the length; no GND return vias at the transitions (Espressif asks for them). Fine at full speed | Low | **Accepted** (owner, 2026-11-03): the USB routing can't change, and it is fine at full speed. One `DN` via has had a GND return via since the certification fixes; the other six have no legal spot ([CERT_REVIEW_AUDIT.md §6](CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)) | — |
| T19 | `U10` land pattern | Pads are 0.813 × 0.229 mm at 1.70 mm centre span. TI's DRL0006A land is 0.67 × 0.30 mm at 1.48 mm. The 0.229 mm pad is narrower than the package's widest lead (0.27 mm), and the toe extends about 0.18 mm further out. That gives smaller solder fillets and a weaker joint and heat path, on the part that failed in case 1 | Medium | **Done** (section 1c): `U10` uses TI's example land, as a new footprint `U_DRL0006A_6L_TI-LAND`. Source checked: SNVSCN8B pp. 29–31 (section 2.7). Still worth a look at `U10`'s joints under the microscope on built boards | — |
| T20 | `F3`'s thermal environment | `F3`'s pads are not tied to the pour, but GND pour wraps them at 0.2–0.3 mm on B.Cu and lies solid under them on F.Cu. A copper-level thermal model puts the PTC about 23 % better cooled than the datasheet's environment. The worst part then trips a case 1 short from a 3.0 V cell in about 30 s instead of 5 s, and not at all at −20 °C below 3.7 V ([BENCH_THEORY.md §2](BENCH_THEORY.md#2-frontlight-ptc-f3-n1)) | was Medium | **Done** (section 1f). A rule area, "F3 thermal keep-out", forbids pour within 1.0 mm of `F3`'s pads on both layers. The modelled cooling factor goes from about 0.77 to 0.94 ([BENCH_THEORY.md §2.4](BENCH_THEORY.md#24-the-studys-model-with-these-numbers)) | — |

Everything else checked passes:

- trace width against current on every power net;
- high-voltage spacing other than T13 (the FPC pins, fixed by the connectors' pitch);
- vias in pads;
- via tenting (tented, both sides);
- frontlight-boost loop areas;
- decoupling of `U2`, `U3`, `U4`, `U10`, `U11` and `U13`;
- crosstalk;
- fast signals near edges.

## 1. Changes made in this pass (U10 corner, case 1 follow-up)

The case 1 charring sat on `U10`'s pins 6 (switch node, to `L2`) and 5 (boost output, to `C9`). The short itself was inside `U10`, between pins 6 and 4 of the removed part ([BOARD_FAILURES.md §3.1](../BOARD_FAILURES.md#31-bench-analysis-of-the-returned-board)). These changes therefore reduce the chance of a second, external short at that corner, and the chance of an internal one spreading through char or flux. They are not a fix for the failure mechanism; `F3` limits that.

| Change | Before | After |
|---|---|---|
| GND via between `L2`'s switch pad and `C9`'s output pad | (47.2, 120.5), 0.29 mm from the switch node | moved to (47.85, 123.05), between `C9`'s and `U10`'s GND pads, ≥ 0.6 mm from both HV nets |
| GND pour next to `TPS_SW_NODE`, `LED_SW`, `EINK_SW` | 0.25 mm (net-class clearance) | 0.5 mm: new rule "SW nets: pour pull-back" in `silkscreen_pcb.kicad_dru` |
| Other nets' vias near the two switch nodes | 0.25 mm | at least 0.4 mm: rule "Switch nodes: via spacing". The `Q4` gate-drive via (`/GDR`) moved 0.08 mm to comply |
| Switch-node trace `L2` → `U10` pin 6 | 0.2 mm, bent diagonally around the pin-6 corner | straight down into pin 6: 0.35 mm from `L2`, necked to 0.2 mm for the last 0.35 mm, so it stays inside the 0.229 mm pad |
| Boost output-loop return | through the pour | direct 0.25 mm GND track `U10` pin 4 → via → `C9` pad 1; the output loop is now 2.4 mm² |
| Solder paste on `U10` | — | not reduced: the 0.229 mm pads give a stencil area ratio of 0.75 at 0.12 mm, and cutting it would drop below 0.66 and hurt paste release |

**Measured afterwards** (B.Cu, excluding `U10`'s own 0.271 mm pad gaps):

| Gap | After |
|---|---|
| Switch node ↔ GND pour | 0.5 mm |
| Switch node ↔ boost output | 0.286 mm (the pin-5 exit between the pin rows) |
| Boost output ↔ GND outside the pads | 0.311 mm |

**Also fixed:** the second `/B-_SENSE` via added during the N7 fixes sat inside `R85`'s pad (via-in-pad, solder wicking). It moved to (81.214, 69.564), 0.2 mm clear of the pad.

**DRC (after section 1):** 7 errors, the same footprint-inherent set as before (T15); section 1b brings this to 0. No unconnected items and no schematic-parity issues.

## 1b. Free fixes applied after the audit

These are the no-cost items from section 4, made in a scratch copy of the project. After every step, DRC (with schematic parity) and this audit were re-run against the starting point.

| Finding | Change | Result |
|---|---|---|
| T2 ESD returns | GND via + direct track at `CR1` (92.435, 100.374), `U6` (95.281, 99.109), `U7` (96.96, 129.932), `D3` (89.636, 58.415); solid pad connections | GND pad → via: `CR1` 5.1 → 1.0 mm, `U6` 3.9 → 1.4, `U7` 3.2 → 1.85, `D3` 2.0 → 1.85. `U9`: no legal spot (T3) |
| T4 power vias | second via, stitched on both layers, at 10 transitions | 10 of 13 doubled: fault current per via 1.8–1.95 A → 0.9–0.97 A |
| T7 starved thermals | solid zone connection on `U2.1`, `U3.2`, `U11.1`, `C3.2`, `C4.2`, `C21.2`, `C25.1`, `D3.2`, `U6.2`, `U7.2`, `R37.2`, `C37.1`, `C27.1`, `C29.2`, `J7` pin 6 and shell | 22 DRC warnings → 5 (left on purpose, see T7) |
| T12 antenna | `U4`'s keep-out also forbids zone fills | GND pour inside it: 2.2 → 0 mm² per layer |
| T14 HV spacing | the 9 spots moved (below); two new pour rules in `silkscreen_pcb.kicad_dru` | all 9 now ≥ 0.263 mm; 0 non-footprint spots below IPC |
| T15 DRC | rules "J3 FPC pad pitch" and "J1 USB-C peg holes" | DRC errors 7 → 0 |
| T16 hygiene | removed 4 zero-length segments and 11 segments lying inside another | sharp joints under 60°: 60 → 45 |
| T11 stitching | 14 GND vias along the board edges (3 across the top of the `J6` arm) | worst gap 11.8 → 9.7 mm, 95th percentile 8.4 → 7.1 mm |

**The 9 HV spots (T14)**, all on B.Cu:

| Spot | Change | Gap, before → after |
|---|---|---|
| `COLOR_SEL` past `Q5` pin 3 (`W-`) | 45° segment moved onto the centre line between `Q5`'s pins 2 and 3 (x + y = 178.92) | 0.154 → 0.277 mm (0.177 mm to pin 2) |
| `/COLOR_SEL_INV` past `Q6` pin 3 (`C-`) | same, between `Q6`'s pins 3 and 2 (x + y = 174.154) | 0.155 → 0.278 mm |
| VCOM past `D6` pin 2 and `C16` pin 2 | diagonal shifted 0.15 mm away from `D6`, vertical 0.1 mm away from `C16` | 0.155 → 0.304 mm and 0.214 → 0.301 mm |
| `/P+_FUSE` past `D8` pin 1 (`C-`) | 0.4 mm run straightened to y = 53.95 instead of dipping towards the pad | 0.201 → 0.304 mm |
| GND via above `Q5` pin 3 | moved 0.07 mm up, to (50.70, 128.73) | 0.203 → 0.273 mm |
| VGH via above `C20` pin 2 (VCOM) | moved to (85.48, 118.54) | 0.205 → 0.270 mm (0.332 mm to the GND pad `C20` pin 1) |
| charge-pump node past `D4` pin 2 (VGL) | bend moved 0.06 mm up | 0.232 → 0.267 mm |
| `BUTTON_ADC_1` past `Q6` pin 3 | 21 mm run tilted 0.022 → 0.005 mm left, so it stays ≥ 0.60 mm from the left edge | 0.248 → 0.263 mm |

**New pour rules:**

- "Panel rails: pour pull-back", 0.3 mm from VGH, VGL, VSH1, VSH2, VSL, VCOM, VPP and the charge-pump node. A GND via at (81.61, 126.43) keeps a pour piece by `J2` connected.
- "LED cathode pads: pour pull-back", 0.25 mm from `W-`/`C-` **pads** only. Pulling back from their mask-covered traces as well would cut the pour feeding `D8`'s ground, and the traces already meet B4.

**Verified (repo board):** DRC 0 errors and 62 warnings (53 silkscreen, the 5 starved thermals kept on purpose, the 4 excluded button stubs). No unconnected items, schematic parity clean.

**Not done here:** teardrops (T6) can only be generated in the KiCad GUI (Edit → Add Teardrops). Add them after section 1c, so they form on `U10`'s new pads.

## 1c. `U10` on TI's example land pattern

Approved on 2026-11-03 after the TI drawing was checked (section 2.7: SNVSCN8B p. 30, drawing 4223266/F).

| Item | Before | After |
|---|---|---|
| Footprint | `TPS923610DRLR:U_DRL0006A_6L_TEX-M` (Ultra Librarian, "most" density) | `TPS923610DRLR:U_DRL0006A_6L_TI-LAND`, a new file beside the vendored ones in `KiCad/9.0/3rdparty/TPS923610DRLR/KiCADv6/footprints.pretty/` |
| Pads | 0.813 × 0.229 mm rectangles, 1.70 mm pad-centre span | 0.67 × 0.30 mm, R0.05 corners, 1.48 mm span (pads 0.111 mm further in) |
| Gap between neighbouring pads | 0.271 mm | 0.20 mm |
| Courtyard | notched outline, ±1.77 × ±1.12 mm (±1.16 × ±1.36 at the body) | rectangle ±1.65 × ±1.10 mm, inside the old one |
| Stencil area ratio at 0.12 mm | 0.75 | 0.86 |

**What changed:**

- **Board.** `U10` was edited in place, so its reference, fields, schematic link, nets and corrected 3D-model placement are kept. Only the pads, courtyard and pin-1 dot changed, plus the library ID.
- **Schematic and library.** The symbol's Footprint field points at the new footprint. Its footprint filter, in the schematic and in the vendored symbol library, also lists the new name, so ERC is unchanged.
- **New rule.** "U10 pad pitch" (clearance 0.2 mm, only between two `U10` pads) in `silkscreen_pcb.kicad_dru`, like `J3`'s. Without it DRC reports exactly the two new 0.20 mm gaps against the SW class's 0.25 mm.
- **`PWM_LED` exit.** It now leaves pin 2 straight out along its centre line, then steps down at 45°. The old 45° jog toward pin 3 came within 0.115 mm of the wider pad.
- **Pin 4 (GND).** Solid connection to the pour, which now reached it with a single spoke. The direct track to `C9` from section 1 is kept.
- **Pin 6 neck.** The 0.2 mm neck into pin 6 is kept. Widening it would bring it within 0.25 mm of pin 5.

**Checked:**

- **DRC and ERC.** DRC is the same as before the change: 0 errors, 62 warnings, no unconnected items, parity clean. ERC is unchanged (46).
- **Library match.** With KiCad's library-mismatch check switched on in a throwaway copy, `U10` matches its new library footprint.
- **Tracks.** Every track end on `U10` falls inside the new pads.
- **This audit.** The two 0.20 mm gaps appear as footprint-limited (T13), with no other spacing change. The frontlight loops move from 2.4/9.7 mm² to 2.5/9.5 mm².

## 1d. Teardrops and trace tidy

**Teardrops (designer, in KiCad).** 871 pad/via teardrops were added. This audit now counts them as copper:

| Joint type | With a teardrop |
|---|---|
| Track→pad (track narrower than 60 % of the pad) | 717 of 758 |
| Track→via | 275 of 277 |

- **DRC:** still 0 errors.
- **The project file:** KiCad dropped the 7 stale `J3`/`J1` exclusions on that save, which the section 1b rules made unnecessary.
- **One new starved thermal:** `C6` pin 2, the LDO output capacitor's GND. It is now solid to the pour, like `C4`.
- **Tightest high-voltage gap:** the teardrop on `J2` pin 22 (VSL) widens toward pin 21 (VGH) and ends 0.30 mm from it. That is no closer than `J2`'s own 0.20 mm pad gap, so the audit counts it as footprint-limited, like a fan-out trace.

**Trace tidy.** Kinks, humps and detours that served no purpose were straightened, on 19 traces at 20 places (map and close-ups with the session notes, not in the repository). Each change had to meet all of these:

- **Shape:** the new run is exactly 0°/45°/90°.
- **What it replaces:** a sub-path that wanders less than 0.8 mm off that line, or a detour of 3 or more bends where a two-segment 45° route is shorter.
- **Visible:** the path moves at least 0.05 mm.
- **Clearance:** every net-class and IPC high-voltage clearance + 0.03–0.05 mm. Nothing is closer to the board edge than before, and nothing already within 0.3 mm gets closer (0.2 mm for the six changes marked †, each checked by eye).
- **Left alone:** USB `DP`/`DN`, the switch nodes, `/B-_SENSE`, ground tracks, and any trace with other copper attached partway along it.

| # | Net (layer) | Where | Bends before → after (whole trace) | Length (mm) |
|---|---|---|---|---|
| 1, 2 | `/P+_FUSE` (B) † | (99.8, 44.5), (96.8, 52.2) | 17 → 15 | 20.53 → 20.44 |
| 3 | `UNUSED_GPIO_45` (F) | (86.3, 62.7) | 10 → 4 | 18.19 → 17.65 |
| 4 | 3V3 (B) | (101.2, 63.0) | 18 → 14 | 29.82 → 28.84 |
| 5 | `UNUSED_GPIO_45` (B) † | (84.5, 68.9) | 14 → 9 | 14.25 → 13.98 |
| 6 | `UNUSED_GPIO_46` (F) | (84.8, 66.5) | 11 → 9 | 27.62 → 27.04 |
| 7 | `P+` (F) † | (89.5, 72.5) | 8 → 4 | 20.82 → 20.63 |
| 8 | `BUTTON_ADC_2` (F) | (46.7, 81.9) | 8 → 6 | 16.15 → 15.73 |
| 9 | `SD_DAT2` (B) | (54.2, 82.5) | 10 → 7 | 7.00 → 6.89 |
| 10 | `SD_DAT3` (B) | (61.9, 81.2) | 12 → 1 | 15.60 → 14.25 |
| 11 | `SD_VDD` (F) | (76.3, 75.3) | 4 → 1 | 3.72 → 3.12 |
| 12 | `SD_DAT2` (B) † | (66.6, 86.4) | 7 → 2 | 4.08 → 3.97 |
| 13 | `P+` (B) | (88.0, 85.2) | 4 → 1 | 3.85 → 3.43 |
| 14 | 3V3 (F) † | (52.9, 104.3) | 3 → 1 | 20.23 → 20.00 |
| 15 | `UNUSED_GPIO_45` (F) | (76.9, 104.2) | 10 → 8 | 40.04 → 38.84 |
| 16 | `ESP32_EN` (B) | (81.5, 103.3) | 7 → 4 | 26.09 → 24.92 |
| 17 | `CC1` (F) | (97.9, 99.9) | 6 → 3 | 9.63 → 9.21 |
| 18 | `LDO_IN` (F) | (68.9, 108.0) | 21 → 13 | 63.29 → 62.02 |
| 19 | `Net-(J1-SHIELD)` (F) | (97.8, 107.0) | 2 → 0 | 10.14 → 8.64 |
| 20 | `I2C_SCL` (B) † | (100.5, 136.7) | 8 → 5 | 35.94 → 35.77 |

**Teardrops to re-add.** 17 teardrops sat on track ends that changed. They were deleted rather than left as stale copper wedges. Re-run the teardrop command to put them back. **Done:** the designer re-ran it on 2026-11-03, after all the fixes; the board then had 862 teardrops.

- 3V3 via (53.60, 96.30)
- `BUTTON_ADC_2` via (45.50, 82.10)
- `CC1` via (98.70, 97.60)
- `ESP32_EN` at `R63` pad 2
- `I2C_SCL` via (100.90, 136.20)
- `Net-(J1-SHIELD)` at `J1` pad S1 (×2)
- `P+` vias (86.49, 86.15) and (87.10, 86.50) (×2)
- `SD_DAT2` at `J7` pad 1
- `SD_DAT3` at `U1` pad 1 and via (68.60, 79.70)
- `SD_VDD` vias (74.99, 75.48) and (78.05, 75.63)
- `UNUSED_GPIO_45` vias (85.64, 68.34) and (73.00, 111.10)

**Checked:**

- **DRC:** 0 errors, 62 warnings (the `C6` thermal gone), no unconnected items, parity clean.
- **This audit, with teardrops:** no spacing below IPC except where a footprint sets it. Joints under 60° drop from 45 to 41.

## 1e. Owner review of the open items (2026-11-03)

| Item | Outcome |
|---|---|
| T3, ESD placement | Accepted: there is no room to move the arrays |
| T18, USB pair | Accepted: the routing can't change |
| T12, antenna | Done: the board already has a cut-out under the antenna, which this audit had missed |
| T5 and T9, e-paper | Left as is (below) |
| T10, edge copper | Done as far as possible: 0.27 mm (section 1f) |
| T17, mounting holes | Done for five of eight (section 1f) |
| T20, `F3`'s cooling (new) | Done: pour keep-out ([BENCH_THEORY.md §2](BENCH_THEORY.md#2-frontlight-ptc-f3-n1), section 1f) |

### T5 and T9 against the reference designs

The owner prefers not to depart from Good Display's reference circuit. Both items were therefore checked against it, and against six published boards that use the same GDR/RESE boost:

| Source | `PREVGH` (T5) | VCI/VDDIO (T9) |
|---|---|---|
| Good Display GDEQ0426T82 spec, Rev 1.1, §8.2 p11 | one 4.7 µF/25 V (`C5`), drawn at the diode | one 1 µF/25 V (`C6`) on pins 15/16 |
| SSD1677 datasheet, Rev 1.0, §13 | one 4.7 µF | 1 µF |
| DESPI-C02; Waveshare HAT and ESP32 driver; LilyGO T5 | one capacitor, 1–4.7 µF | 0.1–22 µF on pins 15/16 |
| Adafruit 2.13" Bonnet and MagTag (layouts measured) | one 1 µF, 6.5 / 2.6 mm from the diode | 10 µF, 4.3–5.0 mm from pins 15/16 |
| This board | `C14` 4.7 µF, 8 mm from `D5` | `C22` 1 µF, 13 mm (16 mm routed) |

None of these documents gives layout guidance. The panel spec only says "The VDD, VCI input must be kept in a stable value; ripple and noise are not allowed" (p7).

**T5.**

- **The faithful fix is a move, not a part.** No reference adds a 0.1 µF, so the reference-faithful fix would be moving `C14` toward `D5`.
- **There is no room.** No legal 0805 spot exists within 4 mm of `D5`'s cathode: `C20` sits directly below it and `Q4` is 0.9 mm to the side. Only swapping `C14` with `C20` (both 0805) would work, and that means re-routing `PREVGH` and `C20`'s net through the capacitor column.
- **The benefit is small.** It is EMI only, and only during refreshes. A small-loop estimate (38.7 mm², a few mA of harmonic current at 30–100 MHz) gives roughly 10–25 dBµV/m at 3 m, against Class B's 40 dBµV/m.
- **Left as is.**

**T9.**

- **A move would match the references** and needs no schematic change.
- **There is no closer spot.** A search with the real courtyards and clearances found nothing on, or within 1 mm of, the `EINK_3V3` trace closer than about 11 mm to the pins. The stretch next to the pins runs under `J2`'s body and between `SW6`/`D6` and `J2`'s fan-out.
- **Electrically the difference is small.** 16 mm of 0.25 mm trace is about 16 nH: about 3 mV for a 10 mA step in 50 ns. For anything slower than about 6 µs, `F6`'s 0.9–6 Ω sets the panel's supply wherever `C22` sits.
- **Left as is.** The first-board ripple check covers it.

### T10: the right-edge bundle

| Trace (F.Cu, 0.2 mm) | Centre x | Gap |
|---|---|---|
| `C-` | 103.66 | 0.476 mm to the edge (x 104.24) |
| `W-` | 103.31 | 0.15 mm |
| `LED_SW` | 102.86 | 0.25 mm |
| `I2C_SDA` (only at y 93–99 and 114–136) | 102.41 | 0.25 mm |

- **The full fix collides with the side buttons.** Bringing `C-` to 1.0 mm from the edge means moving the whole bundle 0.52 mm in. Between y 69.5 and 90, the side buttons' front pads (`SW4` and `SW1`, pins 1/2) end at x 102.19–102.24, so `LED_SW` would land on them.
- **What fits:** about 0.27 mm. `LED_SW` is in the `SW` net class, which keeps 0.25 mm from `SW4`'s plated pads. That puts `C-` 0.75 mm from the edge, and the GND via at (102.5, 67.6) has to move. Below the USB connector (y 114–137) the full shift would fit if `I2C_SDA` moved too, but the bundle moves as one.
- **The gain is mechanical margin** (0.48 → 0.8 mm), not EMI: the strip between the bundle and the edge still can't take pour.

### T17: copper within 2.5 mm of a mounting hole

| Hole | Net (layer) | Distance from centre | If a screw head, washer or standoff shorted it to the GND hole |
|---|---|---|---|
| `H5` | `Net-(Q3-G)` (B) | 2.075 mm | the reverse-polarity FET is held on; harmless with a correctly fitted cell |
| `H5` | `B+` (B) | 2.30 mm | the cell is shorted through the FETs; the `DW01A` trips |
| `H1` | `I2C_SDA` (via) | 2.205 mm | I²C dead: touch, RTC, accessory |
| `H1` | `/P+_FUSE` (B) | 2.215 mm | `F2` trips |
| `H3` | `Net-(R20-Pad1)` (B/F), `Net-(R19-Pad1)` (B) | 2.15 / 2.28 mm | BACK (`SW9`) and OK (`SW8`) read as held down |
| `H2` | `PWR_BUTTON` (B) | 2.30 mm | power button held down |
| `H6` | 3V3 (B) | 2.42 mm | `U3` current-limits, like case 2 |
| `H4` | — | 2.60 mm | clear |

- **Each needs a local nudge of 0.05–0.43 mm.** Three of them end in teardrops that would have to be re-added: the `H1` via, `H2`'s `PWR_BUTTON` stub and `H5`'s `Q3` gate stub.
- **Hardware decides whether it matters.** An M2 head (radius 1.9 mm) clears all of them. A standard M2 washer (radius 2.5 mm) or a hex standoff does not.

## 1f. Layout fixes applied after the review (2026-11-03)

The owner chose T20, T17 and T10.

| Item | Change |
|---|---|
| T20, `F3` | New rule area "F3 thermal keep-out" on F.Cu and B.Cu: x 44.80–49.60, y 114.33–117.28, which is 1.0 mm around `F3`'s pads. It forbids copper pour only; tracks and vias are allowed. Zones refilled |
| T10, right edge | `C-`, `W-`, `LED_SW`, and `I2C_SDA` where it runs alongside (y 93–99 and 114–136), moved 0.27 mm in. Each 45° end slides along its diagonal. The GND via at (102.5, 67.6) moved to (102.2, 67.6). `C-` is now 0.746 mm from the edge (was 0.476) |
| T17, `H6` | 3V3 diagonal moved 0.1 mm out: corners at (68.459, 114.5) and (66.412, 116.547) |
| T17, `H2` | `PWR_BUTTON` corner re-cut: the diagonal now runs (56.25, 71.9) → (55.0, 73.15) |
| T17, `H5` | The `B+` vertical moved from x 97.1 to 97.32. It is still 0.48 mm clear of `SW4`'s pads |
| T17, `H1` | `I2C_SDA` via moved from (91.8, 52.2) to (91.9, 53.3). The F.Cu run moved to x 91.58, and B.Cu now goes straight into `U8` pin 4 |
| T17, `H3` | `Net-(R19-Pad1)` diagonal moved 0.242 mm out: (48.749, 142.307) → (50.66, 144.218) |

**Still within 2.5 mm of a hole centre:**

- `Net-(Q3-G)` at `H5`, 2.075 mm: between `C34`'s pad and the `U5-CS` via there is no 2.5 mm path.
- `/P+_FUSE` at `H1`, 2.214 mm: the `C-` routing around `D8` sits below it.
- `Net-(R20-Pad1)` at `H3`, 2.15 mm: it runs between the hole and the bottom edge. The front-copper landing tab on that net, 2.31 mm away, was left alone deliberately.

**Checked:**

- **DRC:** identical to before. 0 errors; the same 49 warnings plus the 4 excluded stubs; 0 unconnected; parity clean.
- **First attempt:** a 0.30 mm T10 shift broke the `SW` class's 0.25 mm at `SW4` pin 2. That is why the shift is 0.27 mm.
- **Teardrops:** 855 → 851.

**Teardrops to re-add**, on top of section 1d's 17. Re-running the teardrop command restores them; it was re-run on 2026-11-03:

- `I2C_SDA` at the moved via, on F.Cu and B.Cu;
- `I2C_SDA` at `U8` pin 4;
- `PWR_BUTTON` at `R76` pin 1.

## 2. Durability

### 2.1 Current capacity

**How it was checked.** IPC-2221 external-layer formula, 1 oz copper, comparing the narrowest width each net uses with the width needed for a 20 °C rise at the design current.

| Net | Design / fault current | Narrowest width | Rise at narrowest, design / fault |
|---|---|---|---|
| `VBUS_PRE_FUSE` | 1.0 / 1.95 A (`F1`) | 0.40 mm | 6 / 29 °C |
| `USB_VBUS` | 1.0 / 1.95 A | 0.25 mm (57 mm of it) | 14 / 62 °C |
| `LDO_IN` | 1.0 / 1.95 A | 0.25 mm (74 mm) | 14 / 62 °C |
| `P+` | 1.0 / 1.8 A | 0.25 mm (0.8 mm of it; rest 0.4) | 14 / 52 °C |
| `B+`, `B-` | 1.0 / 1.8 A | 0.40 mm | 6 / 24 °C |
| `Net-(Q3-D)`, `Net-(Q8-D)` | 1.0 / 1.8 A | 0.25 mm | 14 / 52 °C (known, BAT-07) |
| `/B-_SENSE` | 1.0 / 1.8 A | 0.5 mm common path; 0.2 mm `R85`→`R86` link | the link carries `R86`'s ≈ 46 %: about 4 °C at 1 A |
| `3V3` | 0.87 A (`U3` limit) | 0.25 mm | 10 °C |
| `TPS_SW_NODE` | 1.0 / 2.1 A | 0.35 mm (0.2 mm only over the last 0.35 mm into the pad) | negligible over that length |

**Trace widths are adequate everywhere.** The fault-current rises on the 0.25 mm power runs (50–62 °C) last only until `F1`, `F2` or the protector trips. Widening `USB_VBUS` and `LDO_IN` to 0.4 mm where there is room would match the rest of the battery path.

**Vias are the weaker link (T4).**

- **Single vias on the power path.** Every power-net layer change uses one 0.6/0.3 mm via.
- **What one via handles.** By the IPC-2221 formula, a 0.3 mm via with JLC's 18 µm average plating carries about 1.35 A at a 10 °C rise and 1.8 A at 20 °C. Its barrel is about 1.9 mΩ.
- **What that means here.** The 1 A design current is comfortable. The 1.8–1.95 A fault currents sit at about a 20 °C rise.
- **Espressif's guidance** is at least two vias where a main power trace changes layer.
- **Most important instance:** `LDO_IN` at (83.2, 86.08) beside `U2`, which carries the whole board's current on USB.
- **Why double them:** it halves the current per via and the barrel resistance, and removes a single point of failure from thermal cycling.
- **Sense path exception:** at the `Q1` end of `/B-_SENSE` (83.5, 70.5) there is no room for a second via.
- **Done in section 1b** for 10 of the 13 transitions, including `LDO_IN` at `U2`. Each pair now carries 0.9–0.97 A per via at the fault current. Still single: `P+` at (78.6, 86.9) and (88.6, 78.7), and `B+` at (90.4, 83.4), with no legal second spot within 2 mm; plus the frontlight's `LDO_IN` branch (46.1, 116.8), which carries at most 0.3 A behind `F3`.

### 2.2 Spacing against voltage

Every pair of different nets with a potential difference of 10 V or more was measured on each layer, including against the GND pour. The voltage ranges assumed are listed in `audit.py`; for example, VGH +25 V, VGL −25 V, VSH +17 V, VSL −17 V and the LED nets 0–26 V.

**Which IPC-2221B column applies:**

- **Mask-covered copper:** B4 (permanent polymer coating), as solder mask is commonly treated.
- **Exposed pads:** A6 (uncoated component leads/terminations).
- **Bare conductors:** B2, kept as the conservative reference.

**How pairs are ranked.** For each pair of nets the audit keeps the closest feature pair in each of four classes:

- an exposed pad against other copper (A6);
- mask-covered copper only (B4);
- two pads of the same footprint;
- a trace passing a neighbouring pad of a footprint it also connects to, no closer than that footprint's own pads (a fan-out).

The last two are fixed by the part, so they are reported as footprint-limited. The first run kept only the single closest pair per net pair. That let a closer mask-covered pair, or a connector's own pad gap, hide an exposed-pad pair slightly further away, and it missed 2 of the 9 T14 spots.

| Pair | ΔV | Gap | B2 / B4 / A6 (mm) | Status |
|---|---|---|---|---|
| `J2` pin 21 (VGH) ↔ pin 22 (VSL) | ≈ 39–42 V | 0.200 mm | 0.60 / 0.13 / **0.40** | below A6: inherent to the 0.5 mm-pitch FPC (T13) |
| `J2` pins 19/20, 20/21, 22/23, 23/24 | 17–30 V | 0.200 mm | 0.10 / 0.05 / **0.25** | below A6: inherent (T13) |
| `J2` VGH/VGL/VCOM fan-out traces past pins 20, 22, 24 | 25–42 V | 0.225 mm | 0.10–0.60 / 0.05–0.13 / **0.25–0.40** | footprint-limited: no closer than `J2`'s own 0.2 mm pad gap (T13) |
| `J3` `LED_SW` ↔ `C-`/`W-` | ≤ 26 V | 0.200 mm | 0.10 / 0.05 / **0.25** | below A6: inherent (T13) |
| `U10` pins 4/5 (GND/VOUT) and 5/6 (VOUT/SW) | ≤ 26 V | 0.200 mm | 0.10 / 0.05 / **0.25** | below A6: TI's land since section 1c (T13); 0.271 mm before |
| 9 trace/via-to-exposed-pad spots (T14) | 25–30 V | 0.154–0.248 → **0.263–0.304 mm** | 0.10 / 0.05 / 0.25 | **fixed** (section 1b) |
| `J2` pins 20/22, 21/23 (VSH1↔VSL, VGH↔VGL) | 34–50 V | 0.700 mm | 0.60 / 0.13 / 0.40 | OK |
| Panel rails ↔ GND pour | 17–30 V | 0.15 → **0.30 mm** | 0.10 / 0.05 / — | OK; rule "Panel rails: pour pull-back" |
| `W-`, `C-` pads ↔ GND pour | ≤ 26 V | 0.15 → **0.25 mm** | 0.10 / 0.05 / 0.25 | OK; rule "LED cathode pads: pour pull-back" |
| `W-`, `C-` traces ↔ GND pour | ≤ 26 V | 0.150 mm | 0.10 / **0.05** / — | OK (mask-covered) |
| `EINK_SW` ↔ `PREVGL` | ≈ 51 V | 1.04 mm | 0.60 / 0.13 / 0.50 | OK |

**Process.** The remaining shortfalls are all at exposed pads, inside the `J2`/`J3` connectors and between `U10`'s pins. Leftover no-clean flux plus humidity across 0.20 mm gaps carrying 17–40 V of DC is the classic setup for slow leakage and electrochemical migration. So:

- **Clean boards after rework.** Case 1's board was reworked by hand.
- **Coat if you want the standard met.** A conformal coat over `J2`/`J3`/`U10` would bring these joints under A7 (0.13 mm), which they all meet.
- **Free layout margin:** done in section 1b (the 9 T14 spots and the two pour pull-back rules).

### 2.3 Board edges, mounting holes and the cut line

- **Board edge:**
  - 53 copper items sit within 0.6 mm of an edge; the nearest is 0.473 mm, at the 0.475 mm board copper-to-edge setting. Eight of them are 4 of the new edge-stitching GND vias (0.55–0.60 mm, counted on each layer); the other 45 were there before section 1b.
  - The notable one is `C-` (T10): 68.6 mm of the LED cathode runs along the right edge on the front.
  - The others are short: an I²C_SCL jog at the cut line, `UNUSED_GPIO_3`, the USB-C shield pads (by design) and the front button pads.
- **Mounting holes (T17):**
  - `H5`: `Net-(Q3-G)` 2.07 mm and `B+` 2.30 mm from the centre.
  - `H1`: `I2C_SDA` via 2.2 mm and `/P+_FUSE` 2.32 mm.
  - `H3`, `H2`, `H6`: 2.15–2.45 mm.
  - The plated ring is 1.9 mm radius, so these are 0.2–0.5 mm beyond it. A larger head or standoff, or a screw driven slightly off-centre, can press through the mask onto them. Keep other nets at least 2.5 mm from the centre.
- **Cut line (T8):** 11 nets cross y = 61.93:
  - 3V3, `C-`, `W-`, `LED_SW`;
  - `P+` (0.4 mm, F.Cu, unfused);
  - `I2C_SCL`, `I2C_SDA`, `UNUSED_GPIO_3`/`45`/`46`, `Net-(R62-Pad1)`.

  HARDWARE.md already covers the 3V3 stubs. `P+` is the one that matters: after a cut it ends at the raw board edge, unfused, protected only by the cell protector. `F2` at (87.0, 56–58) is above the line. Moving it below the line would leave only the fused `/P+_FUSE` crossing.

  **Checked 2026-11-03: `F2` cannot move below the line.** A search of the whole main-board side found no free spot for the 0805 fuse. The only workable place is the strip between the arm's left edge and `J5`'s mating face (x 85.4–88.1, y 62.6–66). Using it would also mean lowering the 3V3 and `PWR_BUTTON` traces under `J5`. But:
  - a battery plug fitted in `J5` (JST PH) sticks out over that strip, low enough to hit a 0.75 mm-tall fuse (confirmed by the designer);
  - the strip carries the `J5` polarity label ("− + CHECK").

  So `F2` stays, and the risk is handled in the build instructions instead. The [README's cutting section](../../README.md#cutting-the-board-down-for-a-smaller-display) tells builders to deburr the cut, check `P+` to GND, and seal the edge before reconnecting the battery.

### 2.4 Copper hygiene

| Check | Result |
|---|---|
| Via tenting | tented on both sides (`m_TentViasFront/Back`) ✔ |
| Vias in SMD pads | none (after the `R85` fix) ✔ |
| Teardrops | 871, added by the designer (T6, section 1d): 717 of 758 track→pad and 275 of 277 track→via joints. The tidy in section 1d removed 17; they were re-added on 2026-11-03 (862 on the board after all fixes) |
| Sharp joints | 41 under 60° after section 1d (45 after 1b, 60 before), mostly 45° bends where a track meets a pad or via, plus 15–27° joints where a power-via stitch leaves its via. Acid traps are a non-issue at modern fabs, but they are also stress risers |
| Overlapping segments | 11 lying wholly inside another segment of the same net (3V3 ×2, `PWR_BUTTON` ×2, `BAT_MONIT`, `I2C_SCL`, `/LED_VIN`, `EINK_SW`, `PREVGH`, `Net-(U5-CS)`, `/PIN_4`): **removed** in section 1b |
| Zero-length segments | 4 (`SD_CMD` and `SD_DAT3` ×2 at the microSD re-route, `Net-(Q5-S)`): **removed** in section 1b |
| Dangling tracks | 4 front-copper stubs, 0.8 mm wide and 1.2–1.7 mm long, from the bottom buttons' pads (`Net-(R18/R19/R20/R60-Pad1)`). Kept: they are the landing tabs for front-mounted buttons (HARDWARE.md §9.1.1), and the project's DRC settings exclude them |

### 2.5 Ground pour

- **Island removal:** set to "always", so no floating copper.
- **Pieces:** F.Cu fills in 19 pieces, B.Cu in 50 pieces, stitched by 95 GND vias (55 pieces and 76 vias before section 1b).
- **Starved thermals (T7):** 21 pads had a single spoke (22 DRC entries, as `J7`'s shell counted twice). The ones that matter were:
  - power parts: `U2`, `U3`, `U11`, `C3`, `C4`, `C21`, `C25`;
  - ESD/TVS: `D3`, `U6`, `U7`;
  - `R37`, the frontlight's LED-current sense.
- **Why it matters:** a single 0.5 mm spoke is about 0.5 nH plus a few mΩ in series with the part's ground, which is the wrong place for it on a TVS or a regulator.
- **Done in section 1b:** solid zone connection on all of those, and on `C37`, `C27`, `C29` and `J7`'s ground pin and shell.
- **Kept on purpose (5):**
  - `R50`/`R41`: DC only.
  - `J2` pin 17: one ground pin of the FPC, where even heating during reflow matters more.
  - `J6` pin 4 and `SW9` pin 1: through-hole, so they also connect on the other layer.

### 2.6 DRC errors (now 0)

Seven errors were built into footprints:

| Error | Where | Why it is acceptable | Rule in `silkscreen_pcb.kicad_dru` |
|---|---|---|---|
| Clearance 0.20 < 0.25 mm (×3) | `J3` pads 1/2, 4/5, 5/6 (`LED_SW` against `C-`, `W-`, NC) | the FPC connector's 0.5 mm pitch; the SW class clearance can't apply between its own pins | "J3 FPC pad pitch": 0.2 mm, only between two `J3` pads |
| Hole clearance 0.194 < 0.25 mm (×4) | `J1` locating-peg NPTH holes against shell/GND pads A1/A12/B1/B12 | GCT USB4105 footprint geometry; GND pads next to a non-plated peg | "J1 USB-C peg holes": 0.19 mm, only within `J1` |
| (since section 1c) Clearance 0.20 < 0.25 mm (×2) | `U10` pads 4/5 and 5/6 (GND, `LED_SW`, `TPS_SW_NODE`) | TI's example land at 0.5 mm pitch | "U10 pad pitch": 0.2 mm, only between two `U10` pads |

**Why rules instead of exclusions.** Each rule is limited to its footprint and set to the as-built value, so the board is DRC-clean and anything closer still fails (T15). The project file already held GUI exclusions for these 7, but they were recorded at older marker positions and no longer matched; the rules make them unnecessary.

### 2.7 `U10`'s land pattern (T19)

| | Old footprint (`U_DRL0006A_6L_TEX-M`) | TI DRL0006A recommended (on the board since section 1c) |
|---|---|---|
| Pad size | 0.813 × 0.229 mm | 0.67 × 0.30 mm |
| Pad-centre span (pin row to pin row) | 1.70 mm | 1.48 mm |
| Gap between neighbouring pads | 0.271 mm | 0.20 mm |
| Stencil | 1:1 (board default) | 1:1 at 0.1 mm |

The package's leads are 0.15–0.27 mm wide, with a lead span of 1.5–1.7 mm.

**Sources (checked 2026-11-03):**

- **TI's land.** TI, *TPS923610/1/2* data sheet, [SNVSCN8B](https://www.ti.com/lit/ds/symlink/tps923610.pdf) (Sept 2025, revised Oct 2026). The package drawing DRL0006A is 4223266/F (11/2024), on pp. 29–31:
  - **p. 29, package outline:** lead width 0.15–0.27 mm, foot length 0.2–0.4 mm, lead span 1.5–1.7 mm; JEDEC MO-293 variation UAAD.
  - **p. 30, "Example board layout":** 6× (0.67 × 0.30) mm pads, 4× (0.5) mm pitch, (1.48) mm pad-centre span, (R0.05) corners. Non-solder-mask-defined pads preferred, with the mask opening at most 0.05 mm around the pad.
  - **p. 31, stencil:** 1:1 apertures, "based on 0.1 mm thick stencil".
  - **TI's own caveats:** note 1 marks dimensions in parentheses as "for reference only". Note 5 says "Publication IPC-7351 may have alternate designs". Note 7 says the land "aligns to IPC-610, Bottom Termination Component (BTC) solder joint inspection criteria".
  - **Page images:** saved with the session notes, not in the repository.
- **The old footprint** (used until section 1c) came from `KiCad/9.0/3rdparty/TPS923610DRLR/`, an Ultra Librarian download (its `ImportGuides.html` points to app.ultralibrarian.com). It has three density variants, all with 0.2286 mm-wide pads:

  | Variant | Pad length | Pad-centre span |
  |---|---|---|
  | `-L` | 0.610 mm | 1.499 mm |
  | nominal | 0.711 mm | 1.600 mm |
  | `-M` (used here) | 0.813 mm | 1.702 mm |

**What switching to TI's land involved** (done in [section 1c](#1c-u10-on-tis-example-land-pattern)):

- **A new footprint** with TI's pads, kept beside the vendored ones so those stay untouched, and `U10` swapped to it.
- **Pad centres move 0.111 mm inward.** The existing track ends at the old centres still fall inside the new 0.67 mm pads, so nothing disconnects. The 0.2 mm neck into pin 6 (section 1) stays at 0.2 mm, because at 0.30 mm it would come within 0.25 mm of pin 5.
- **A footprint rule.** Pins 4/5 (GND/VOUT) and 5/6 (VOUT/SW) end up 0.20 mm apart, under the SW class's 0.25 mm. That needs a rule like `J3`'s, scoped to `U10`'s own pads.
- **Spacing.** Those two gaps carry up to 24.5 V, which is below A6's 0.25 mm, so they join the footprint-limited list (T13). The package's own leads can be as close as 0.23 mm (0.5 mm pitch minus the 0.27 mm maximum lead width).
- **Mask.** With the board's 0 mm mask expansion, the mask web between pads is 0.20 mm. That is above JLC's minimum of 0.10 mm for green mask and 0.13 mm for black or white.
- **Paste.** The stencil area ratio at 0.12 mm rises from 0.75 to 0.86, so paste releases better.

**Trade-off of the old footprint:**

- **Gains creepage:** 0.271 mm between neighbouring pads, which meets A6 at 26 V; TI's 0.20 mm does not.
- **Costs joint quality:**
  - The pad is narrower than the widest lead.
  - The heel fillet is shorter, and the pads run about 0.18 mm further out than TI's.
- **Why that matters for `U10`:** its leads are its only heat path, since it has no exposed pad. Smaller joints mean a weaker joint, a weaker heat path and less tolerance to placement offset.

**Assessment.** Case 1's short was inside the die, and nothing here points at the joints. But this is the part that failed, so:

1. **Look at `U10`'s joints under the microscope** on the repaired board and on any other built board: wetting on all six pins, fillets, offset.
2. ~~**On the next layout pass, prefer TI's land** and rely on flux cleaning (and optionally coating) for the 0.20 mm gaps.~~ Done in section 1c. The middle option considered, 0.27 × 0.67 mm at about 1.5 mm span with 0.23 mm gaps, was not taken.

The old 0.229 mm pads gave a stencil area ratio of 0.75 at 0.12 mm (0.89 at 0.1 mm). That's why the paste was not reduced in section 1. TI's 0.30 mm pads give 0.86 at 0.12 mm.

## 3. EMI / EMC

### 3.1 Switching loops

Areas are from pad-centre polygons, with the ground legs taken through the pour.

| Loop | Area | Perimeter | Note |
|---|---|---|---|
| Frontlight boost, switching: `U10` SW/VOUT → `C9` → GND → `U10` GND | **2.4 mm²** | 6.8 mm | after the section 1 change ✔ |
| Frontlight boost, input: `C12` → `L2` → `U10` SW … GND → `C12` | 9.7 mm² | 13.4 mm | ✔ |
| E-paper boost, switching: `Q4` drain → `D5` → `C14` → GND → `R14` → `Q4` source | **38.7 mm²** | 30.6 mm | largest on the board (T5) |
| E-paper boost, input: `C10` → `L1` → `Q4` → `R14` → GND → `C10` | 32.6 mm² | 31.9 mm | HARDWARE.md quoted 20–27 mm² from pad-centre joins |
| E-paper charge pump: `Q4` → `C11` → `D4` → `C16` → GND → `D6` | 20.2 mm² | 45.2 mm | |

**How to shrink the e-paper loop.** The e-paper boost runs only during refreshes, but its switching loop is 16× the frontlight's. It is long because `C14`, the VGH reservoir, sits next to `J2` about 8 mm from `D5`.

- **Cheapest fix:** add a 0.1 µF / 50 V X7R 0603 from `D5`'s cathode (`PREVGH`) to GND, placed between `D5` and `R14`'s ground. That gives the edge current a loop of a few mm² while `C14` keeps the bulk role. It's one more part, of a type already on the board, and a JLC Basic part.
- **Alternative:** move `R14`'s ground and `C10`'s ground together with a via pair, which also shortens the input loop.

### 3.2 Switching-node copper

| Node | Copper area | Track length | Note |
|---|---|---|---|
| `TPS_SW_NODE` | 3.65 mm² | 1.6 mm | ✔ |
| `EINK_SW` | 10.9 mm² | 15.4 mm | |
| `Net-(D4-K)` (charge pump) | 5.3 mm² | 10.6 mm | |
| `/GDR` (`Q4` gate, driven from the panel) | 10.3 mm² | 36.3 mm | the gate drive comes 36 mm from `J2` pin 2: a fast-edge net with 64 % ground under it |

The LED nets `LED_SW`, `W-` and `C-` are each 175–190 mm long, because they run to both `J3` and `J6`. `LED_SW` is DC with ripple. `W-`/`C-` are PWM-switched at kHz rates, so their edges, not their frequency, are what radiates. This is a consequence of the expansion-header option.

### 3.3 Return paths for fast signals

On a 2-layer, 1.6 mm board the "plane" under a trace is the other layer's pour, 1.5 mm away. The table shows how much of each net's length has GND pour directly under it on the other layer, and the longest stretches without it.

| Net | Length | Ground under it | Longest stretch without | Note |
|---|---|---|---|---|
| `I2C_SDA` / `I2C_SCL` | 183 / 186 mm | 54 / 56 % | 26 mm on B.Cu along y ≈ 138 (under the front art) | low speed; also a long antenna to `J4`/`J6` |
| `/GDR` | 36 mm | 64 % | 1.6 mm | see 3.2 |
| `DP` / `DN` | 47 / 46 mm | 68 / 75 % | 1.0–1.2 mm | USB full speed is tolerant |
| `SD_DAT2` / `SD_CLK` | 35 / 21 mm | 72 / 73 % | 5.1 / 1.3 mm | |
| `PWM_LED` | 16 mm | 73 % | 2.9 mm | |
| SPI to the panel, `EPD_*`, `SD_DAT0/1`, `SD_CMD`, `SD_DAT3` | | 82–94 % | ≤ 1.7 mm | ✔ |

The bottom-edge I²C run is the only long one: the front pour is held back there for the artwork. At 100–400 kHz that matters little for emissions. It matters more for ESD pick-up next to the user-facing buttons, where `U8` only protects the `J6` end.

### 3.4 Stitching and the antenna keep-out

- **Stitching (T11):** 76 GND vias before section 1b. The farthest any point with pour on both layers sat from a stitch was 11.8 mm, at the top of the `J6` arm (x 92–104, y 37–40); along the perimeter, 11.7 mm. The 95th percentile was 8.4 mm.
  - Infineon's 2-layer guidance is an edge ground ring with vias at most 5 mm apart.
  - λ/20 at 2.4 GHz is 6.2 mm in air and 2.9 mm in FR-4.
  - The arm's edges and far end wanted more GND vias: it carries the expansion header, the most likely route for an external disturbance onto the board.
  - **Section 1b added 14 edge vias**, placed greedily on the biggest remaining gap. Each one is:
    - in the GND pour on both layers;
    - outside every courtyard except the plastic `J6` header's, and at least 0.6 mm from `J6`'s pins;
    - at least 1.2 mm from the optional cut line;
    - with its drill at least 0.1 mm clear of the front artwork.

    With the ESD vias that makes 95. Worst gap now 9.7 mm (perimeter 9.2 mm), 95th percentile 7.1 mm.
  - **What is left over 5 mm needs layout moves:**
    - **Right edge** (x ≈ 103, y 75–79 and 110–128): no front pour, because the `C-` run sits on that edge (T10).
    - **Left edge** (y 68–85): `SW5`/`SW7` courtyards.
    - **Edge beside the ESP32** (x ≈ 51, y 92–108): the module's courtyard and antenna.
    - **The arm's right side** (y 45–55): `SW10`'s courtyard.
- **Antenna (T12):** `U4`'s footprint keep-out covers x 30–51, y 92.5–112.5; 15.9 mm² of it is on the board, at the left edge.
  - **The pour inside it.** The keep-out blocked tracks, vias and pads but **not** pours, so 2.2 mm² of GND pour on each layer sat inside it. **Fixed in section 1b**: the rule area now also forbids zone fills, and no pour is left inside.
  - **The board under the antenna.** Correction (section 1e): the board outline already has a 6.3 × 18.7 mm cut-out under the antenna (x 44.26–50.6, y 93.3–112.0).
    - The module's 18 × 6 mm antenna area (x 44.7–50.75) sits over it, with only a 0.15 mm sliver over board.
    - That is Espressif's preferred arrangement after an overhang.
    - The first version of this audit read the antenna as sitting over 6.8 mm of board; it does not.
  - **Nearby test pads.** The UART test pads `TP1`/`TP2` sit about 6–7 mm from the keep-out corner; Espressif asks to keep UART lines and test points away from the antenna.

### 3.5 ESD

**ESD/TVS device distance from its connector (T3).** Routed trace length from the connector pad to the device, straight-line distance in brackets.

| Connector | Device | Distance |
|---|---|---|
| `J1` (USB) | `U6` | `DP` 12.0 mm (6.5), `DN` 12.2 (5.9), `CC1` 16.6 (7.4) |
| `J1` | `CR1` (VBUS) | 7.2 (5.3) |
| `J7` (microSD) | `U1` | `SD_CLK` 17.2 (11.3), `SD_CMD` 32.7, `SD_DAT2` 25.0, `SD_DAT3` 29.1 |
| `J7` | `U9` | `SD_DAT0` 24.2 (19.9), `SD_DAT1` 31.3 (22.5) |
| `J4` (touch) | `U7` | 10.7–18.7 (7.2–9.3) |
| `J6` (expansion) | `U8` | 6.3–11.7 ✔ |
| `J6` | `CR2` (pin 7) | **45.6** (14.8) |
| `J6` | `CR3` (pin 12) | 20.9 (14.6) |
| `J3`/`J6` (frontlight) | `D3` | 14.3 (11.4) |
| `J3`/`J6` | `D8` | 11.6–12.3 |

**ESD device ground pad to the nearest GND via (T2)**, pad centre to via centre:

| Device | Before section 1b | After | Note |
|---|---|---|---|
| `CR1` | 5.1 mm | **1.0 mm** | new via + direct track, solid pad |
| `U6` | 3.9 mm | **1.4 mm** | new via + 0.3 mm track, solid pad (was a single spoke) |
| `U9` | 3.6 mm | 3.55 mm | no legal via spot: its ground is a 5 mm, 0.2 mm trace. Fixed by moving `U9` to `J7` (T3) |
| `U7` | 3.2 mm | **1.85 mm** | new via + direct track, solid pad (was a single spoke) |
| `D3` | 2.0 mm | **1.85 mm** | new via + direct track, solid pad (was a single spoke) |
| `U1`, `U8`, `CR2`, `CR3`, `D8` | 1.1–1.8 mm | 0.9–1.8 mm | |

**Why it matters.** A TVS only clamps well if the path from the connector pin to its ground is short. Each mm of trace is about 1 nH, and at the 1 ns rise of an IEC 61000-4-2 discharge that's tens of volts per mm. TI's TPD4E1U06 data sheet asks for the array "as close to the connector as possible".

- **Ground side:** done in section 1b, except `U9`.
- **Signal side (next layout pass):** move `U6` to `J1`, `U1`/`U9` to `J7`, and `CR2` beside `J6` pin 7.

**The microSD lines.**

- **Termination is right.** The 33 Ω series resistors `R21`–`R26` sit about 1.9 mm from the ESP32's pins, which is what Microchip's 2-layer guidance (AN14.18) asks for: source termination within 10 mm of the driver.
- **The ESD arrays are stubs.** `U1`/`U9` hang off the card-side nets as branches of up to about 25 mm, which also lengthens `SD_CMD`/`SD_DAT*` to 30–43 mm against `SD_CLK`'s 21 mm.
- **Against the published limits:**
  - Microchip's 2-layer limits: CLK ≤ 25.4 mm, data −6…+38 mm relative to CLK. The board meets these.
  - Espressif's 4-layer-style ±1.3 mm length match and "no layer changes": the board does not meet these (`SD_CLK`, `SD_CMD`, `SD_DAT2` and `SD_DAT3` each have 2 vias).
- **Fix:** moving the arrays to `J7` removes the stubs as well.

### 3.6 Decoupling

| IC | Supply | Nearest capacitor, routed (straight) | |
|---|---|---|---|
| `U4` ESP32 module | 3V3 | `C32` 4.9 mm (4.6) | ✔ |
| `U13` RTC | 3V3 | `C30` 2.1 mm | ✔ |
| `U12` inverter | 3V3 | `C24` 9.4 mm (1.8) | the route goes around; low speed, acceptable |
| `U3` LDO | in / out | `C4` 2.2 mm, `C6` 3.2 mm | ✔ |
| `U2` power mux | `USB_VBUS` / `LDO_IN` / `P+` | 1.9 / 3.8 / 3.5 mm | ✔ |
| `U11` charger | `USB_VBUS` / `P+` | 2.6 / 2.4 mm | ✔ |
| `U10` frontlight | `/LED_VIN` | `C12` 4.3 mm | ✔ |
| `U5` DW01A | VCC | `C7` 5.8 mm | acceptable |
| **`J2` panel `VCI`/`VDDIO`** | `EINK_3V3` | **`C22` 16.4 mm (13.2)** | T9 |

`J2`'s supply cap was already 13 mm away on Rev 1.02. Since 1.03 the panel logic sits behind `F6`'s 0.9–6 Ω, so a local capacitor at pins 15/16 now matters more (see the e-paper supply notes in [NEXT_REVISION.md](../NEXT_REVISION.md#n6-panel-logic-supply-from-the-e-paper-ptc)).

### 3.7 Crosstalk, edges and the USB pair

- **Parallel runs** (same layer, within 10° of parallel, edge gap ≤ 0.5 mm, aggressor against a sensitive net): only short ones.
  - `DN`/`CC1`: 3.5 mm at 0.15 mm.
  - `PWM_LED` and `COLOR_SEL` against `TP_INT`: 2.5 mm each.

  None of these needs action.
- **Fast signals within 1 mm of the edge:** only a 2.5 mm `I2C_SCL` jog at the cut line.
- **USB pair:**
  - `DP` 46.9 mm and `DN` 46.1 mm, so 0.8 mm skew.
  - 0.2 mm tracks, coupled for 57 % of the length.
  - `DP` has 5 vias, `DN` 2, partly from the USB-C A/B pin crossover. TI's USB layout guide allows ≤ 4 per trace, and Espressif asks for a GND return via at each transition.
  - **Is it critical?** A full-speed edge (4–20 ns) is about 0.65 m long on FR-4, so these 5 cm runs are electrically short. The 90 Ω impedance and length match are good practice rather than critical.

  Matching the via counts and adding return vias is worth doing only if the pair is touched again (T18).

## 4. Recommendations, in order

**Free, rule-level or one-click, for this revision:**

1. ~~**T2 + T7:** a GND via at the GND pad of `U6`, `U7`, `U9`, `CR1` and `D3`, and solid pad-to-pour connections on the ESD and power parts listed in T7.~~ Done (section 1b), except `U9`'s via (no legal spot; see T3).
2. ~~**T6:** enable teardrops (Board Setup → Teardrops; Edit → Add Teardrops).~~ Done by the designer (section 1d). Re-add the 17 removed by the tidy.
3. ~~**T4:** a second via at each single-via power transition (`VBUS_PRE_FUSE`, `USB_VBUS`, `LDO_IN` at `U2`, `P+`, `B+`).~~ Done for 10 of 13 (section 1b).
4. ~~**T12:** forbid zone fills in `U4`'s antenna keep-out.~~ Done (section 1b).
5. ~~**T14:** nudge the 7 trace/via-to-HV-pad spots to ≥ 0.25 mm. Extend the pour pull-back rule to `W-`, `C-`, `PREVGH`, `PREVGL`, VSH/VSL/VCOM and the charge-pump node.~~ Done (section 1b), all 9 spots.
6. ~~**T15 + T16:** DRC exclusions for the 7 footprint errors; Cleanup Tracks & Vias; delete the 4 dangling stubs.~~ Done (section 1b) as footprint-scoped rules and a cleanup. The 4 stubs are kept, because they are excluded on purpose.
7. ~~**T11:** GND vias along the `J6` arm, aiming at ≤ 5 mm spacing along the edges.~~ Partly done (section 1b): 14 edge vias; the remaining gaps need moves (T10, switch courtyards).
8. **T19:** inspect `U10`'s solder joints on built boards (microscope).
9. ~~**T20 (new):** a 1 mm pour keep-out around `F3` on both layers. It restores the PTC's trip times ([BENCH_THEORY.md §2.4](BENCH_THEORY.md#24-the-studys-model-with-these-numbers)). The prototype passed DRC unchanged. Owner deciding.~~ Done (section 1f).

**One part:**

10. ~~**T5:** 0.1 µF / 50 V at `D5`'s cathode, next to `R14`'s ground.~~ Left as is (section 1e): no reference design adds it, and there is no spot for moving `C14`.
11. ~~**T9:** 0.1–1 µF at `J2` pins 15/16 (or move `C22` there).~~ Left as is (section 1e): no legal spot nearer than about 11 mm; the electrical effect is small.

**Next layout pass (moves):**

12. ~~**T3:** move the ESD arrays to their connectors: `U6` → `J1`, `U1`/`U9` → `J7` (this also removes the microSD stubs), `CR2` → `J6` pin 7.~~ Accepted by the owner (no room).
13. ~~**T8:** move `F2` below the cut line.~~ Not possible (section 2.3); documented in the README instead.
    - ~~**T10:** pull `C-` in from the right edge.~~ Done as far as possible: 0.27 mm, so `C-` is 0.746 mm from the edge (section 1f).
    - ~~**T17:** keep other nets ≥ 2.5 mm from hole centres.~~ Done for five of eight (section 1f); the other three need parts moved.
14. ~~**T19:** use TI's DRL0006A land for `U10` (or the 0.27 mm-wide compromise).~~ Done (section 1c, TI's land).
15. ~~**T12:** a board cut-out under the antenna if the enclosure allows.~~ Already there (section 1e).

**Process:**

16. **Rework hygiene:** wash flux off after any rework, especially around `U10`/`L2`/`C9`, `J2` and `J3`. Optionally coat the high-voltage areas (`U10`/`L2`/`C9`, `J2` pins 18–24, `D4`–`D6`) with acrylic conformal coating, which brings the FPC pin gaps under IPC A7.

## 5. Not covered

- Radiated or conducted emission levels; that needs a pre-scan.
- Impedance from a field solver.
- Thermal simulation of the parts.
- The ESP32 module's own layout.
- The panel and touch FPCs themselves.

## 6. References

The source notes are in [trace-audit/layout_refs.md](trace-audit/layout_refs.md), collected 2026-11-03 with links. IPC-2221B values come from two public transcriptions that agree; the standard itself is paywalled, and IPC-2221C (2023) has since revised it. Values marked "(computed)" there are arithmetic on cited formulas.

| Topic | Value used here | Source |
|---|---|---|
| IPC-2221B Table 6-1 spacing | B2 0.10/0.10/0.60 mm, B4 0.05/0.05/0.13, A6 0.13/0.25/0.40, A7 0.13 (rows 0–15/16–30/31–50 V) | EMA, T61 |
| Trace current | I = 0.048·ΔT^0.44·A^0.725 (external); IPC-2152 is more conservative for external traces on thin boards | AdvancedPCB, smps.us |
| 0.3 mm via | ≈ 1.35 A (10 °C) / 1.8 A (20 °C) at JLC's 18 µm average plating; Espressif: ≥ 2 vias per main power layer change | circuitcalculator method, JLC, Espressif |
| ESP32-S3-WROOM-1 | antenna area 18 × 6 mm; prefer overhang or cut-out; ≥ 15 mm housing clearance; keep UART and test points away | Espressif hardware design guidelines, module datasheet v1.8 |
| TPS923610 | COUT close to VOUT and GND, SW–L short and wide, CIN close; DRL0006A land 0.67 × 0.30 mm at 1.48 mm, stencil 1:1 at 0.1 mm | TI SNVSCN8B |
| SSD1677 / GDEQ0426T82 | no published layout guidance; reference boost parts only | Good Display spec, SSD1677 |
| USB full speed | 90 Ω ±10 % (good practice), ≤ 4 vias per trace, no stubs, ESD at the connector | Espressif, TI SPRAAR7J, TI TPD4E1U06 |
| SD on 2 layers | CLK series R within 10 mm of the driver, CLK ≤ 25.4 mm, data −6…+38 mm relative to CLK | Microchip AN14.18 |
| JLCPCB 2-layer | 0.10/0.10 mm trace/space; mask web 0.10 mm (green/red/…), 0.13 mm (black/white); copper to routed edge ≥ 0.20 mm; vias tented by default | jlcpcb.com capabilities |
| Mounting holes | M2 DIN965 head Ø3.8, KiCad courtyard Ø4.3; extra clearance under metal heads | KiCad library, JLC NPTH guide |
| Stitching | edge ring ≤ 5 mm (Infineon AP24026); λ/20 is a rule of thumb (not found in a primary source) | Infineon |
| Edge routing | "Never run noisy traces on the outside edge of the board" | TI SZZA009 |

## 7. Files and how to re-run

From the repository root:

```
"C:\Program Files\KiCad\9.0\bin\python.exe" docs/audit-2026-11-03/trace-audit/export_geometry.py silkscreen_pcb.kicad_pcb %TEMP%\geometry.json
"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe" pcb drc --schematic-parity --severity-all --format json --output %TEMP%\drc.json silkscreen_pcb.kicad_pcb
python docs/audit-2026-11-03/trace-audit/audit.py %TEMP%\geometry.json %TEMP%\drc.json docs/audit-2026-11-03/trace-audit/out
```

The scripts:

- [trace-audit/export_geometry.py](trace-audit/export_geometry.py) runs under KiCad's Python.
- [trace-audit/audit.py](trace-audit/audit.py) needs shapely, numpy and Pillow. It counts teardrop zones as copper of their net in the spacing checks, and reports how many narrow joints already have a teardrop.

The results are in [trace-audit/results.json](trace-audit/results.json). The figures:

- [trace-audit/fig_return_paths.png](trace-audit/fig_return_paths.png): unreferenced fast-signal runs, the worst stitching gaps, and the antenna keep-out.
- [trace-audit/fig_spacing_loops.png](trace-audit/fig_spacing_loops.png): the HV spacing hot spot and the switching loops.

Both are drawn as viewed from the back (mirrored), like the 3D renders. The design rules are in [`silkscreen_pcb.kicad_dru`](../../silkscreen_pcb.kicad_dru):

- the switch-node pour pull-back and via spacing (section 1);
- the panel-rail and LED-cathode-pad pour pull-backs, and the `J3`/`J1` footprint rules (section 1b);
- the `U10` pad-pitch rule for TI's land (section 1c).
