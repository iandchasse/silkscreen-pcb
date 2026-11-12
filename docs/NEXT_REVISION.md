# Next revision: decided changes (after Rev 1.02)

Status: **decided 2026-11-02; N1–N9 are implemented in the Rev 1.03 design files** ([REV_1_03_STATUS.md](REV_1_03_STATUS.md);
N10 is closed, N11 was dropped, and the BQ21040 charger swap of 2026-11-04 supersedes N9). Where section 5 and the status
note differ, the status note wins. Base: Rev 1.02 (`silkscreen_pcb.kicad_pcb`). Everything below comes
from the case 1 repair ([BOARD_FAILURES.md](BOARD_FAILURES.md#case-1-rev-10-frontlight-boost-fault)) and the studies it
led to in [audit-2026-10-29/](audit-2026-10-29/). Section 2 is the checklist, and section 3 gives each change's exact
references, nets, footprints, coordinates and BOM rows, with one link target per change (`#n1-…` to `#n11-…`). The
studies behind them are linked from each item.

## 1. Why: what the case 1 repair concluded

- **The failed part:** `U10` (TPS923610 frontlight boost). Its internal low-side switch was shorted `SW` to `GND` at
  about 7 Ω, measured on the removed part. Nothing else was damaged: `L2`, `C12`, `C4`, `U2`, `U3`, the `LDO_IN` trace,
  `F1`, `C9`, the LED output and the laminate all checked clean.
- **The repair:**
  - A new `U10` was fitted and the original `L2` refitted.
  - The board then ran after a reflash in download mode (hold BOOT). The browser flasher's earlier failure was a
    missing application image, not hardware.
- **Why it failed is not established.** The lean is a weak or damaged part (ESD while the case was open, a defect or a
  bad lot) over overstress in operation. Still open: decapping or photographing the removed part, its lot and sourcing,
  and scope checks of the plug-in surge and blend mode.
- **Why it smoked is a design gap, and Rev 1.02 has it too.** Nothing on the boost branch limits current below `F1`'s
  1 A hold. A 7 Ω short draws about 0.75 A from USB and dissipates 1–3 W until something chars.
- **The same gap exists elsewhere.** A board-wide audit found it on every rail whose only protection sits far above
  what a few-ohm short draws:
  - the battery rails (up to about 5 W);
  - 3V3 behind `U3`'s 0.56–0.87 A limit, case 2's rail;
  - the touch, `J6` and e-paper branches.
- **The "dead" morning needed no hardware fault.** A pack at 3.26 V with no USB is put back to sleep at boot, and the
  screen keeps its last image.
- **Still unexplained:** why the 67 W charger did not power the board.

**The response.** Make every likely short stop itself cheaply:

- one PTC part number, reused on four branches;
- a sense resistor that makes the battery protector see smaller shorts;
- front-side test pads so a short can be located with a meter (N11, dropped 2026-11-02).

## 2. Hardware changes

| # | Change | Schematic | Layout | BOM | Details |
|---|---|---|---|---|---|
| **[N1](#n1-frontlight-ptc-f3)** | **Frontlight PTC** | MF-FSMF010X-2 between `LDO_IN` and a new net `LED_VIN` (`C12` pin 2, `L2` pin 1, `U10` `VIN`). `C12` stays on `LED_VIN`, at `U10` | Replaces the via (52.00, 117.80) → `L2` pad 1 link; nearest land is about (48.4, 116.3). Thermally light: 0.25 mm traces, no pour, no thermal vias, close to `U10`/`L2` and away from `U3` and the charger | +1 MF-FSMF010X-2 | [PTC_THERMAL §2](audit-2026-10-29/PTC_THERMAL.md#2-where-it-goes) |
| **[N2](#n2-touch-supply-ptc-f4-replaces-r42)** | **Touch supply PTC** | `R42` (0 Ω) becomes MF-FSMF010X-2. Use `R66` instead in the alternate touch mapping | Same 0603 pads | `R42` moves to the PTC line | [FOLLOWUP §2](audit-2026-10-29/PROTECTION_FOLLOWUP.md#2-cheap-wins-touch-supply-and-j6-pin-7) |
| **[N3](#n3-j6-pin-7-ptc-f5)** | **`J6` pin 7 PTC** | MF-FSMF010X-2 between 3V3 and `J6` pin 7 | New 0603 in the B.Cu segment (92.1, 42.1) → pin 7 (88.7, 45.4), thermally light | +1 MF-FSMF010X-2 | [FOLLOWUP §2](audit-2026-10-29/PROTECTION_FOLLOWUP.md#2-cheap-wins-touch-supply-and-j6-pin-7) |
| **[N4](#n4-move-cr2-to-the-j6-side)** | **Move `CR2`** to the pin side of N3 (as `CR3` already sits after `F2`) | `CR2` from 3V3 to the `J6` pin 7 net | Next to `J6` pin 7 | — | [FOLLOWUP §7.3](audit-2026-10-29/PROTECTION_FOLLOWUP.md#73-move-cr2-to-the-pin-side-of-the-j6-ptc) |
| **[N5](#n5-e-paper-ptc-f6)** | **E-paper PTC** feeding a new net `EINK_3V3` | MF-FSMF010X-2 from the 3V3 trunk to `EINK_3V3`: `L1` pad 2 and `C10` pad 2 | Re-tap the touch branch upstream (e.g. (86.75, 110.45)) so it is not behind this PTC. `C10` stays on the PTC's output | +1 MF-FSMF010X-2 | [FOLLOWUP §7.1](audit-2026-10-29/PROTECTION_FOLLOWUP.md#71-e-paper-boost-feed-add-the-same-ptc) |
| **[N6](#n6-panel-logic-supply-from-the-e-paper-ptc)** | **Panel logic on `EINK_3V3`** | `J2` pins 15/16 (`VDDIO`/`VCI`) and `C22` move from the 3V3 trunk to `EINK_3V3` | New trace of about 25 mm from the `L1` area to `J2`; remove the old 3V3 branch | — | [FOLLOWUP §7.2](audit-2026-10-29/PROTECTION_FOLLOWUP.md#72-panel-logic-supply-j2-pins-1516) |
| **[N7](#n7-dw01a-sense-resistor-r85)** | **`DW01A` sense resistor** | 68 mΩ 1 % `Rs` from `Q1` pin 3 (new net `B-_SENSE`) to GND. `R16` stays on GND | Isolate `Q1` pin 3 from the pour. Put `Rs` in the pocket above-left of pin 3 (move the `UNUSED_GPIO_45` trace), with ≥ 0.4 mm copper and ≥ 2 vias to GND | +1 RL1206FR-070R068L (or 2 × `C25334` 0.1 Ω Basic in parallel) | [FOLLOWUP §3.2–3.3](audit-2026-10-29/PROTECTION_FOLLOWUP.md#32-dw01a-sense-resistor-the-lean) |
| **[N8](#n8-c34-from-22-nf-to-100-nf)** | **`C34` 2.2 nF → 0.1 µF** (required with N7: keeps the cell-insertion spike off the short-circuit threshold) | value only | — | `C34` moves to the `C14663` line | [FOLLOWUP §3.2](audit-2026-10-29/PROTECTION_FOLLOWUP.md#32-dw01a-sense-resistor-the-lean) |
| **[N9](#n9-r6-from-47k-to-10k)** | **Charge current: `R6` 4.7 kΩ → 10 kΩ** (about 0.12 A; halves `U11`'s heat) | value only | — | `R6` joins the 10 kΩ `C25804` line; the 4.7 kΩ line goes | [FOLLOWUP §5](audit-2026-10-29/PROTECTION_FOLLOWUP.md#5-charge-current-r6) |
| **[N10](#n10-move-c36-and-c37)** | ~~**Move `C36`/`C37`** (`SD_VDD`) out of the socket's flex zone~~ **Closed 2026-11-03: left as is** ([REV_1_03_STATUS §7](REV_1_03_STATUS.md#7-n10-closed-left-as-is)) | — | At least 5 mm from `J7`, or turned so the socket's bending axis runs along their length | — | [DURABILITY_AUDIT §3.4](audit-2026-10-29/DURABILITY_AUDIT.md#34-microsd-supply) |
| **[N11](#n11-front-test-pads-tp6-to-tp18)** | ~~**13 front-side test pads**, TP6–TP18 (bare F.Cu, no paste, no F.SilkS labels)~~ **Dropped 2026-11-02** | new nets as above; most pads join existing nets | Positions are checked clear of the artwork by [tp_front.py](audit-2026-10-29/test-pads/tp_front.py) (map: [tp_front.png](audit-2026-10-29/test-pads/tp_front.png)). Watch TP7 (shares N7's pocket), TP8 (stub on F.Cu) and TP16 (on N6's trace) | — | [FOLLOWUP §8.2](audit-2026-10-29/PROTECTION_FOLLOWUP.md#82-test-pads-front-side-decided-2026-11-02) |

**Test pads (N11, dropped 2026-11-02; kept for reference).**

| Pad | Net | Pad | Net |
|---|---|---|---|
| TP6 | `LED_VIN` | TP13 | `LDO_IN` |
| TP7 | `B-_SENSE` | TP14 | 3V3 (by `U3`) |
| TP8 | `DW01A` `OD` | TP15 | 3V3 (touch/e-paper side) |
| TP9 | `B−` | TP16 | `EINK_3V3` |
| TP10 | `SD_VDD` | TP17 | `/PIN_2` |
| TP11 | `USB_VBUS` | TP18 | GND (optional) |
| TP12 | `P+` | | |

**Cost** (JLC, 2026-11-02):

- **Per board:** about $0.27 in parts and assembly.
- **Per order:** plus $6, for two new Extended parts.
- **Effective per-board total:** about $1.50 at 5 boards, $0.30 at 100.
- **Hand-built from DigiKey:** $2.49 in parts per board.
- Breakdown and cheaper variants: [FOLLOWUP §0](audit-2026-10-29/PROTECTION_FOLLOWUP.md#0-summary).

**After layout**, re-run `python docs/audit-2026-10-29/test-pads/tp_front.py`, then DRC.

**From the 2026-11-03 trace audit.** These are listed with severity and cost in [TRACE_AUDIT.md §0](audit-2026-11-03/TRACE_AUDIT.md#0-summary) and ordered in [§4](audit-2026-11-03/TRACE_AUDIT.md#4-recommendations-in-order).

**The free ones are now on `1.03`** ([§1b](audit-2026-11-03/TRACE_AUDIT.md#1b-free-fixes-applied-after-the-audit)):

- ESD grounds;
- the second power vias (10 of 13);
- solid ground pads;
- no pours in the antenna keep-out;
- the high-voltage spacing fixes and pour pull-backs;
- DRC rules for the footprint errors;
- track cleanup;
- edge stitching.

**Teardrops still need the KiCad GUI** (Edit → Add Teardrops).

**Not decided yet:**

- **Two would add one 0603 each:** an HF capacitor at `D5` for the e-paper boost loop, and a capacitor at `J2`'s supply pins.
- **Two are moves for the next layout pass:** the ESD arrays to their connectors, and `C-` off the edge (which would also let the right edge be stitched). TI's land pattern for `U10` is already on `1.03` ([TRACE_AUDIT.md §1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern)).
- **`F2` stays above the cut line.** No room was found below it: the only strip, at `J5`'s mating face, is covered by a fitted battery plug and carries the polarity label. The cut-edge risk is documented in the README's cutting instructions instead ([TRACE_AUDIT.md §2.3](audit-2026-11-03/TRACE_AUDIT.md#23-board-edges-mounting-holes-and-the-cut-line)).

The `U10`-corner layout changes from that audit are already on `1.03` (T1).

## 3. Implementation details, item by item

Each heading below is a stable link target (for example `docs/NEXT_REVISION.md#n7-dw01a-sense-resistor-r85`).

**Conventions:**

- **Coordinates:** Rev 1.02 board coordinates in mm.
- **New references:** continue the existing numbering (F3–F6, R85, TP6–TP18).
- **Footprints:** hand-solder variants, matching the rest of the board.
- **The four PTCs** are one BOM line:
  - **Symbol / footprint:** `Device:Polyfuse` / `Fuse:Fuse_0603_1608Metric_Pad1.05x0.95mm_HandSolder`.
  - **Part:** MF-FSMF010X-2, Bourns, LCSC `C210355`.
  - **DigiKey alternate:** MF-PSMF010X-2, `C116171`. It is 0805, so it needs `Fuse_0805_2012Metric_Pad1.15x1.40mm_HandSolder`.
- **Every PTC is thermally light:**
  - 0.25 mm traces on both pads for at least a few mm.
  - No pour or plane on either pad.
  - No vias under the body.

  It trips on its own heat, and copper takes that heat away ([PTC_THERMAL §2](audit-2026-10-29/PTC_THERMAL.md#2-where-it-goes)).

### N1: Frontlight PTC (F3)

- **Schematic:** `F3` from `LDO_IN` to a new net `LED_VIN`. Move `C12` pin 2, `L2` pin 1 and `U10` pin 1 (`VIN`) onto `LED_VIN`.
  - `C12` must stay on `LED_VIN`, right at `U10`: it is `U10`'s input capacitor, and its ripple must not run through the PTC.
- **Layout:**
  - The feed reaches `L2` pad 1 (50.64, 119.13) on B.Cu from the via at (52.00, 117.80). Cut that link and insert `F3`.
  - There is no room in the 1.9 mm link itself. The nearest free 0603 land is about (48.4, 116.3), 2.8 mm from `L2`'s `SW` pad. Reaching it needs a two-via hop across the `LED_SW` run at y = 117.1, or a move of `R39`/`R41`.
  - Keep it within a few mm of `U10`/`L2`, and away from `U3` and `U11`.
- **Check:** `LDO_IN` and `LED_VIN` are separate nets in DRC; TP6 lands on `LED_VIN` (N11).

### N2: Touch supply PTC (F4, replaces R42)

- **Schematic:** delete `R42` (0 Ω) and put `F4` in the same place, from 3V3 to `/PIN_2` (`J4` pin 2).
- **Layout:** swap the footprint on `R42`'s pads at (91.5, 120.9) and keep the existing traces.
- **Alternate touch mapping:** in that mapping 3V3 reaches `J4` pin 4 through `R66` (DNP). If you build it, fit an MF-FSMF010X-2 on `R66`'s pads instead of the 0 Ω link.
- **`R66`'s 3V3 pad** currently hangs off the `J2` 3V3 branch. Keep it on plain 3V3 when N6 moves `J2` (see N6).

### N3: J6 pin 7 PTC (F5)

- **Schematic:** `F5` from 3V3 to a new net `J6_3V3`, with `J6` pin 7 moved onto it.
- **Layout:**
  - The only copper to pin 7 is the B.Cu segment from (92.12, 42.05) to (88.74, 45.43). Insert `F5` in it.
  - Stay above the cut line (y = 61.86) so a shortened board loses `F5` together with `J6`.
- **Docs:** state a 20 mA budget for pin 7 (section 5).

### N4: Move CR2 to the J6 side

- **Schematic:** `CR2` (TSD05CDYFR) pin 1 moves from 3V3 to `J6_3V3`; pin 2 stays on GND.
- **Layout:** move `CR2` from (89.0, 59.0) to beside `J6` pin 7, still above the cut line, with a short GND connection.
- **Why:** a TVS that fails short after a hit is then current-limited by `F5`, as `CR3` already is by `F2`.

### N5: E-paper PTC (F6)

- **Schematic:** `F6` from 3V3 to a new net `EINK_3V3`, with `L1` pin 2 and `C10` pin 2 moved onto it.
- **Layout:** today 3V3 runs along B.Cu y ≈ 110.3–110.45 *through* `L1` pad 2 (88.5, 110.45), to a junction at (89.19, 110.45). From there it goes to `C10` (92.1, 109.8) and, through the via at (91.17, 112.43), up the F.Cu touch feed to `R42`/`F4`.
  1. Break the trunk west of `L1`, e.g. at (86.75, 110.45), and insert `F6` there.
  2. `L1` pad 2 and `C10` become `EINK_3V3` only.
  3. Reconnect the touch feed (the via at (91.17, 112.43)) to the trunk *upstream* of `F6`, so a touch fault does not take the display down and vice versa.
- **Check:** `C10` is on the PTC's output side. TP15 (3V3) and TP16 (`EINK_3V3`) sit either side of `F6`.

### N6: Panel logic supply from the e-paper PTC

- **Schematic:** `J2` pins 15 (`VDDIO`) and 16 (`VCI`), and `C22` pin 2, move from 3V3 to `EINK_3V3`.
- **Layout:**
  - Route `EINK_3V3` from the `F6` output to `J2` (73.5, 125.8), about 25 mm. TP16 at (85.25, 115.5) lies on this route.
  - Remove the old 3V3 branch to `J2`, but **keep `R66` pad 1 on 3V3**. It shares that branch today, at (98.0, 135.7).
  - `C22` stays next to `J2`.

### N7: DW01A sense resistor (R85)

- **Schematic:** `R85`, 68 mΩ 1 % (`Device:R`, `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder`):
  - `Q1` pin 3 moves from GND to a new net `B-_SENSE`;
  - `R85` runs from `B-_SENSE` to GND;
  - `R16` and `U5` are unchanged (`R16` already references GND, after `R85`).
- **Layout:**
  1. `Q1` pin 3 (85.1, 71.05) is in the GND pour today. Its net change isolates it on refill.
  2. Place `R85` in the pocket above-left of pin 3 (about x 83.4–86.4, y 68.9–70.4). The `UNUSED_GPIO_45` trace from (84.78, 68.42) to (83.63, 69.57) must move, and a 1206 also needs the `B−` jog nudged about 0.5 mm. If space is short, an 0805 fits (`0805W4F680MT5E`, `C52472`).
  3. Copper: pin 3 → `R85` 0.4 mm or wider and short; `R85` → GND with at least two vias (reuse the one at (86.4, 68.8)).
- **No extra Extended fee:** two 0.1 Ω `1206W4F100LT5E` (`C25334`, JLC Basic) in parallel, as `R85` and `R86`. **Chosen 2026-11-03** and in the `1.03` schematic and board: `R85` (78.66, 69.11) and `R86` (75.0, 70.5), west of `Q1`, because the pocket by pin 3 has no room (see [REV_1_03_STATUS.md §6](REV_1_03_STATUS.md#6-n7-and-n8-schematic-and-board)).
- **Requires N8.** Details: [FOLLOWUP §3.3](audit-2026-10-29/PROTECTION_FOLLOWUP.md#33-sense-resistor-implementation-and-bench-check).

### N8: C34 from 2.2 nF to 100 nF

- **Change:** value only (CS to `B−`, same 0603 footprint). Move `C34` from the `C27,C28,C29,C34` 2.2 nF line to the 0.1 µF `C14663` line.
- **Why:** with `R85` fitted, the 10–15 A, 3–4 µs cell-insertion spike would reach the `DW01A`'s 1.0 V short-circuit threshold and latch the board off. With 0.1 µF it peaks at about 0.06 V.

### N9: R6 from 4.7k to 10k

- **Change:** value only. The charge current drops from about 0.23–0.26 A to about 0.11–0.13 A, and `U11`'s heat halves.
- **BOM:** `R6` joins the existing 10 kΩ line (`C25804`), and the 4.7 kΩ line (`C23162`) is removed.
- **Docs:** update HARDWARE.md §3.2.
- **Superseded in 1.03 (2026-11-04):** `U11` is now a BQ21040, whose current is 540 / `R6`. `R6` is 4.7 kΩ again
  (`C23162`) and gives the same 105–125 mA ([REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04)).

### N10: Move C36 and C37

**Status: closed 2026-11-03, left as is.** `C36`/`C37` already lie along the bending axis, and there is no room to move
them 5 mm ([REV_1_03_STATUS §7](REV_1_03_STATUS.md#7-n10-closed-left-as-is)). The plan below is kept for reference.

- **Today:** `C36` (62.5, 86.7) and `C37` (62.3, 88.2) on `SD_VDD` sit 2.2 and 3.7 mm from the push-push socket `J7` (63.0, 84.6). That is the board's worst flex-crack spot.
- **Change:** move them at least 5 mm from `J7`'s outline, or rotate them so the socket's bending axis runs along their length. They stay on `SD_VDD`; their role is local decoupling for the card.
- **Pad clash:** TP10 at (63.65, 86.2) is next to `C36` today. Move TP10 with the capacitors if it ends up in the way, and re-run the pad checker.

### N11: Front test pads (TP6 to TP18)

**Status: dropped 2026-11-02.** Ian: "forget the test pads, we'll leave them for later, if at all." The plan below is
kept for reference.

**Symbol and footprint:** `Connector:TestPoint`, `TestPoint:TestPoint_Pad_D1.5mm` (or `_D1.0mm`, which also clears everything).

**Footprint settings:**

- Place on **F.Cu**. The footprint has no paste layer.
- No F.SilkS reference: hide it, or move it to F.Fab.
- Set *Exclude from BOM* and *Exclude from position files*. The same is due on `TP1`/`TP2` (audit 2026-09-30, report 09).

**Via-in-pad:** 0.6 mm via with a 0.3 mm drill. These are probe pads, not soldered pads, so open vias are fine.

| Ref | Net | x, y | Connection |
|---|---|---|---|
| TP6 | `LED_VIN` | 46.5, 117.0 | via in pad, about 2 mm B.Cu stub to the `F3` / `C12` node |
| TP7 | `B-_SENSE` | 85.4, 69.6 | via in pad at the `Q1` end of `R85` (place with N7) |
| TP8 | `Net-(U5-OD)` | 90.8, 71.5 | via in pad, about 2.6 mm stub from `Q1` pin 6, **run on F.Cu** (the B.Cu path crosses the `OC` trace) |
| TP9 | `B−` | 91.5, 68.65 | via in pad on the `B−` trace |
| TP10 | `SD_VDD` | 63.65, 86.2 | via in pad on the `SD_VDD` trace (re-check after N10) |
| TP11 | `USB_VBUS` | 82.75, 96.75 | on the existing F.Cu trace |
| TP12 | `P+` | 90.5, 81.4 | via in pad on the `P+` trace |
| TP13 | `LDO_IN` | 79.74, 96.66 | on the existing F.Cu feed |
| TP14 | 3V3 | 74.6, 85.8 | on the existing F.Cu trace by `U3`/`C6` |
| TP15 | 3V3 | 91.3, 116.0 | on the F.Cu touch feed, upstream of `F4`/`F6` (after N5's re-tap) |
| TP16 | `EINK_3V3` | 85.25, 115.5 | via in pad on N6's route |
| TP17 | `/PIN_2` | 92.25, 129.25 | via in pad on the `/PIN_2` trace. It is 0.24 mm from the "Thank you all" text; nudge it if it looks crowded |
| TP18 | GND | 82.25, 81.25 | on the F.Cu GND pour (optional) |

**Clearances.** Every position above clears the front silkscreen, the existing mask openings and other-net copper by at least 0.2 mm, and the board edge by at least 1 mm (checked against Rev 1.02). After N1, N5, N6, N7 and N10 are laid out, run `python docs/audit-2026-10-29/test-pads/tp_front.py` (edit its `PADS` list if a pad moved), then DRC.

### BOM changes

Changes to `fabrication/part_fields.csv` (columns `Refs,Value,MPN,Manufacturer,LCSC,DNP,LCSC part,Note`), then run `apply_part_fields.py`:

```csv
"F3,F4,F5,F6",MF-FSMF010X-2,MF-FSMF010X-2,Bourns,C210355,,BOURNS MF-FSMF010X-2,"same part; 0.10 A hold / 0.30 A trip 0603 PPTC on the frontlight, touch, J6 pin 7 and e-paper feeds (docs/NEXT_REVISION.md N1-N6). DigiKey alternate MF-PSMF010X-2 (C116171, 0805 footprint)"
R85,0.068,RL1206FR-070R068L,Yageo,C327066,,YAGEO RL1206FR-070R068L,"same part; DW01A over-current sense resistor, Q1 pin 3 to GND (docs/NEXT_REVISION.md N7)"
```

- **`C34`:** remove it from the 2.2 nF line `"C27,C28,C29,C34"` and add it to a 0.1 µF `C14663` line, e.g. `"C7,C30,C33,C34,C36"`.
- **`R6`:** remove the 4.7 kΩ `R6` line and add `R6` to the 10 kΩ `C25804` line.
- **`R42`:** remove it from the 0 Ω line `"R42,R44,R46,R52,R73"`.
- **TP6–TP18:** add them to the test-point handling, excluded from BOM and positions.
- **Applied on 2026-11-12:** three BOM-only swaps from the [BOM audit](audit-2026-11-12/BOM_AUDIT.md):
  `C38` → `C21120`, `F2` → `C269105`, `U12` → `C7827`. The rows, steps and checks are in
  [REV_1_03_STATUS.md §20.3](REV_1_03_STATUS.md#203-to-do-agreed-and-done-2026-11-12).

## 4. Firmware changes (no hardware)

| # | Change | Why |
|---|---|---|
| **F1** | Set an RTC-memory flag before asserting `SD_ACTIVATE` and clear it after a good mount. If the next boot is a brownout reset with the flag set, keep the card off and report a card fault | A card short that browns out the board is already cut by `R40` at reset; this keeps it cut |
| **F2** | Release `SD_ACTIVATE` after a failed mount or command | Higher-resistance card shorts do not brown the board out |
| **F3** | Boot-loop guard: after three consecutive brownout resets, show a power-fault screen (if the panel works) and deep-sleep | A remaining 3V3 trunk short otherwise reboots forever |
| **F4** | Boot self-test: report touch I²C, `J6` accessory, SD mount and panel `BUSY` | "Branch dead, board fine" is the signature of a tripped PTC, so this gives field diagnosis without tools |
| **F5** | Flag "frontlight commanded on but `LED_MONIT` ≈ 0" | The signature of a tripped N1 |
| **F6** | Keep the 50 % brightness cap; allow 100 % only above about 3.8 V on battery | With N1, a high-resistance PTC can put `U10` into UVLO at 100 % from a low cell |
| **F7** | Show a low-battery message before the boot-time check sleeps the board | Case 1's "dead" morning |
| **F8** | Don't overlap Wi-Fi TX bursts with SD writes or a panel refresh. Lower the Wi-Fi TX power, and keep Wi-Fi off below about 3.7 V on battery | Coincident peaks can exceed the 500 mA LDO and brown out 3V3 at mid to low charge (independent review M-2) |
| **F9** | Put the touch controller (FT6336U) in hibernate before deep sleep | It is always powered: +220 µA in its power-on monitor mode against a 50 µA sleep budget (L-18) |
| **F10** | Shut down at ≥ 3.3 V on battery, together with F7 | Protects cycle life, and delays a pack's own protection locking out in storage (I-6, M-5) |
| **F11** | Decode `USB_STAT` for the BQ21040 (Rev 1.03): 1.80–2.60 V on battery; 0.80–1.35 V charging. Above 2.6 V `CHG` is off: split it with `P+` = 2 × `BAT_MONIT`. About 4.0 V or more is full, near 0 V is no cell, and a cell present below about 4.0 V is a stopped charge (10 h timer, input above 6.6 V, or `TS` out of range). Confirm the levels on a board, including with VBUS absent | `CHG` marks only the charge started by plug-in or cell insertion, and the 0.55 V "complete" level went with `STDBY` ([REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04)). TI specifies the pins high-impedance when unpowered, so the on-battery level should be 2.20 V (L-4) |
| **F12** | If `R35`/`R36` change (section 10), move the ladder 2 thresholds with them | UP(2) sits at 2.877 V, at the edge of the ADC's calibrated range (L-5) |

F8–F12 come from the independent review ([TRIAGE.md](independent-review-2026-11-03/TRIAGE.md)).
[BOARD_REVIEW §4.8](independent-review-2026-11-03/BOARD_REVIEW.md#48-firmware-obligations-imposed-by-the-hardware) lists
the other obligations the hardware puts on firmware:
- `ADIM` timing;
- `COLOR_SEL` changes only at zero duty;
- SD pins low before `SD_VDD` goes off;
- `EPD_RST` kept high in sleep.

## 5. Documentation to update with the implementation

- **HARDWARE.md:**
  - §3.2: `R6` and the charge current.
  - §3.3: `Rs`, `C34`, the new trip range, TP7 as a current monitor.
  - §5: SD firmware policy, `C36`/`C37`.
  - §6: `EINK_3V3`, e-paper PTC.
  - §7: frontlight PTC.
  - §8: touch PTC in `R42`/`R66`.
  - §11: `J6` pin 7 PTC, 20 mA budget, `CR2`.
  - Add a test-pad table.
- **`fabrication/part_fields.csv` and BOM.md:** the new lines (MF-FSMF010X-2 `C210355`, sense resistor `C327066`) and the
  `C34`/`R6` moves. Note MF-PSMF010X-2 (`C116171`) as the DigiKey-stocked alternate, since DigiKey stock for
  MF-FSMF010X-2 was unconfirmed on 2026-11-02.
- **The `J6` pinout table and README:** 20 mA on pin 7; heavier loads go to pin 12.
- **BOARD_FAILURES.md:**
  - Mark case 1's "design gap" as addressed in this revision once built.
  - Replace case 2's "lift `L1`/`C10`" steps with the PTC millivolt method ([FOLLOWUP §8.1](audit-2026-10-29/PROTECTION_FOLLOWUP.md#81-the-ptcs-are-built-in-current-shunts)).

## 6. Verification

**Before ordering** (on a Rev 1.0 board, by bodge where possible). [BENCH_THEORY.md](audit-2026-11-03/BENCH_THEORY.md)
predicts each result from the datasheets and the board's copper, and says which parts still add something.

1. **Frontlight PTC bench test** ([PTC_THERMAL §8](audit-2026-10-29/PTC_THERMAL.md#8-bench-test); predictions in
   [BENCH_THEORY §2.4–2.6](audit-2026-11-03/BENCH_THEORY.md#26-what-the-bench-test-adds)):
   - **Where:** best on a 1.03 board, because a bodge on an older board sits in different copper. Measure `F3`'s
     resistance first.
   - **Fault:** a 6.8 Ω stand-in for the short, from the `SW` node to GND, fed at 3.0–5.0 V. Expected worst-part trip
     from 3.0 V: about 6 s now that `F3` has its pour keep-out
     ([TRACE_AUDIT T20](audit-2026-11-03/TRACE_AUDIT.md#0-summary)); about 30 s without it.
   - **Normal use:** the light at 100 % for 30 min from 3.0 and 3.7 V.
2. **Sense-resistor trial** ([FOLLOWUP §3.3](audit-2026-10-29/PROTECTION_FOLLOWUP.md#33-sense-resistor-implementation-and-bench-check)).
   - **Basis:** these numbers are for the pair as placed. With the copper it is about 62 mΩ from `Q1` pin 3 to ground
     ([BENCH_THEORY §3.2](audit-2026-11-03/BENCH_THEORY.md#32-the-sense-path-as-placed)); FOLLOWUP gives them for 68 mΩ.
   - **Probing:** with no TP7/TP8 (N11 was dropped), read `/B-_SENSE` at `R85` pad 1 (53.7 mV per amp across `R85`),
     and `OD` at `Q1` pin 6 against `B−`.
   - **Peak current:** measure the coincident battery peak (Wi-Fi TX + SD write + light).
     - The datasheets put it at about 0.55 A, 0.63 A worst at the 50 % light cap.
     - The lowest trip point is 0.83 A with the PUOLOP `DW01A` JLC fits, 0.77 A with Fortune's.
     - If the peak is much lower, a higher resistance becomes possible.
     - **How:** on the cell with USB unplugged (with USB in, `U2` takes the load from `USB_VBUS`). Put a 0.05–0.1 Ω shunt in
       the cell's positive lead (outside the `DW01A`'s sense loop) and read it with a differential probe or two scope
       channels, triggered at 0.4 A and band-limited to about 1 kHz: the `DW01A` trips on an overcurrent of 7–20 ms, so
       peaks of a few milliseconds are what count. A power profiler (PPK2 class) does the same. A multimeter in series
       reads only the average, a few readings a second, and on its mA range the burden voltage (often several tenths of a
       volt at 400 mA) can starve the board and hide the peak; if it is all there is, use its 10 A range. Worst case: a
       cell at 3.4–3.6 V, Wi-Fi transmitting, an SD write, a full refresh and the light at 50 %.
   - **Trip point:** expect 0.83–1.68 A, about 1.32 A typical (PUOLOP; Fortune 0.77–1.78 A).
   - **Insertion:** theory says no risk with `C34` = 0.1 µF (BENCH_THEORY §3.4), so 3–5 insertions are enough.
   - **Hot:** theory says the trip falls 4–7 % at 60 °C (§3.5). Optional: repeat the trip point warm.
3. **Known-good baseline:** record the rail and PTC-pad readings from the repaired case 1 board
   ([FOLLOWUP §8.3](audit-2026-10-29/PROTECTION_FOLLOWUP.md#83-known-good-baseline)).

**On the first boards of the new revision:**

- The e-paper rails come up through N5 (scope `GDR`/`RESE` and `VGH`/`VGL`).
- The touch, `J6` accessory and SD all work through their PTCs.
- The frontlight runs normally at each level and in blend mode.
- Measure `EINK_3V3` current and ripple at `J2` pins 15/16 during a full refresh (the panel's logic supply now sits behind `F6`).
- **Charger (`U11`, BQ21040, [REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04)):**
  - the charge current with a meter in series with the cell: 105–125 mA in the constant-current phase;
  - `USB_STAT` at 1.11 V while the first charge runs and about 3.3 V once it ends, with `P+` then between 4.04 and 4.2 V;
  - the `TS` window: warm `TH1` with hot air until charging stops (about 41 °C at `TH1`) and check it resumes as it cools
    (about 39 °C); freeze spray for the cold end (about 0 °C); with `TH1` not fitted, nothing charges;
  - log `TH1` and the cell's temperature through a full charge, the evidence C1 needs (§9);
  - repeat the hot-plug check of HARDWARE.md §3.1: `VIN1` stays at or below 5.6 V.
  - from the 2026-11-07 audit ([BQ21040_AUDIT.md §4](audit-2026-11-07/BQ21040_AUDIT.md#4-first-article-checks-added-by-this-audit)):
    - on the bare board before first power-up: `U11` pin 5 to GND and pin 6 to `USB_VBUS` each under 1 Ω (a 180° placement
      error would put pins 2 and 3 there); with a cell attached, `TS` at `C38` pin 1 reads about 0.476 V at 25 °C;
    - `USB_STAT` with USB in and a full cell reads 3.2 V or more (under 2.8 V means `CHG` leakage above about 0.4 µA); read
      `IO9` at about 1.0 V and 2.2 V against a meter and set the F11 thresholds from the data;
    - `TH1` and the cell with thermocouples in a 30 °C room and in the closed case during a charge, noting whether it pauses;
    - revive a cell held at 2.2–2.6 V in the `DW01A`'s over-discharge lockout: log `B-` to GND, `TS` and the charge current at
      25 and 45 °C. `Q2`'s gate sits near 0.7 V there and a low-threshold part could stutter the charge (audit finding 3; if
      it does, use a `Q2` with a gate threshold of at least 1.0 V);
    - scope `U11` pin 6 against pin 5 during a hot-plug with a 1 m cable and at charge start (`C25` is 14.5 mm of trace
      from the pin, and `C2` sits behind `R84`; audit finding 5);
    - pull the cell while charging: `P+` should cycle 3.8–4.2 V and `USB_STAT` read 3.3 V;
    - optional, over 10 h: 30 mA on `J6` pin 12 with a cell on USB, to see whether the charger restarts after its timer
      (audit finding 1);
    - in JLC's placement preview: `U11`'s pin-1 dot sits on the `TS` pad at (83.15, 93.45).
- **Grounded switch frame legs** ([REV_1_03_STATUS §20](REV_1_03_STATUS.md#20-review-findings-decisions-and-to-do-2026-11-12),
  finding 4): on the eight `MJTP1117_FG` legs (`SW1`–`SW5`, `SW8`, `SW9`, `SW11`), solder fills the hole and wets the ring
  on both sides, and no switch rocks when pressed hard. These legs join the ground pour solid on both layers, which can
  leave a hole partly filled.

**From the independent review (2026-11-03;** [BOARD_REVIEW §7](independent-review-2026-11-03/BOARD_REVIEW.md#7-bench-tests-for-the-suspected-items) **has the set-ups):**

- **M-5, pack wake:** use a pack of the kind actually fitted. Let its own protection lock out by discharging it below its
  cut-off, then plug USB in. If it does not wake, the board needs a USB-time override of the cell detector (section 10).
- **L-3, mux chatter:** feed a 4.75 V source through a long, thin cable with a 0.7 A load. Check whether the TPS2116
  toggles between inputs.
- **L-4, `USB_STAT` with VBUS absent:** read the level firmware will see (F11). Expect 2.20 V on a 1.03 board (the
  BQ21040's pins are high-impedance when unpowered); on a Rev 1.0 board it depends on the TP4056.
- **L-11, SD switch-on dip:** measure 3V3 at `C32` when `SD_ACTIVATE` powers the card. If it dips by more than 0.2 V, set
  `R78` to 10–22 kΩ.
- **L-8 (`Q3`/`Q8`):** no bench test needed. Decided 2026-11-04 to keep the circuit as it is, because the owner's boards start and run fine ([TRIAGE §5.1](independent-review-2026-11-03/TRIAGE.md#51-l-8-what-q3-and-q8-do)).

**Process (any board, any revision):** after rework, wash off the flux. This matters most around `U10`/`L2`/`C9`, `J2` pins 18–24 and `J3`, where 17–40 V sits across 0.20–0.27 mm gaps ([TRACE_AUDIT.md §2.2](audit-2026-11-03/TRACE_AUDIT.md#22-spacing-against-voltage)).

## 7. Considered and not adopted

| Option | Why not | Where |
|---|---|---|
| PTC in place of `R27` (battery path) | Any PTC that carries the 0.6 A peak without brownout is too low in resistance to trip on a 3–10 Ω short | [FOLLOWUP §3.1](audit-2026-10-29/PROTECTION_FOLLOWUP.md#31-ptc-in-place-of-r27-rejected) |
| PTC on `SD_VDD` | None keeps the card at 2.7 V or more at 200 mA and also trips on a `U3`-limited short | [FOLLOWUP §4](audit-2026-10-29/PROTECTION_FOLLOWUP.md#4-microsd-supply) |
| Latching electronic fuse on the boost branch | 14 parts | [BOOST_EFUSE.md](audit-2026-10-29/BOOST_EFUSE.md) |
| 4-part current limiter on the boost branch | More parts than the PTC; **kept as the fallback** if N1's bench test fails | [BOOST_LIMITER.md](audit-2026-10-29/BOOST_LIMITER.md) |
| Low-quiescent load switch | BGA only | — |
| Ferrite bead in `U4`'s supply (certification review C2) | Espressif's reference design uses 22 µF + 0.1 µF and no bead, and the rail is LDO-fed | [CERT_REVIEW_AUDIT §1.1](audit-2026-11-03/CERT_REVIEW_AUDIT.md#11-verdict-per-review-item) |
| Shipping with the cell unplugged (certification review A3) | The board is sold without a cell and has no coin cell; it matters only if a cell ever ships | [CERT_REVIEW_AUDIT §1.1](audit-2026-11-03/CERT_REVIEW_AUDIT.md#11-verdict-per-review-item) |

**Still open from earlier reviews, not decided here:**

- `C1` as a 1–2 kV MLCC: moot from Rev 1.03, which ties the USB-C shell straight into the GND pours and removes `R1` and `C1` ([CERT_REVIEW_AUDIT §3.1](audit-2026-11-03/CERT_REVIEW_AUDIT.md#31-a1-shell-to-gnd)).
- `J1` mechanical support.
- `U6` routed flow-through.
- Fitting `SW6` on boards that will be flashed.

See [DURABILITY_AUDIT §3.5](audit-2026-10-29/DURABILITY_AUDIT.md#35-already-proposed-elsewhere-still-open).

## 8. Still open from case 1 (bench and owner)

- **The repaired board:** record frontlight operation at each level, both colours and blend, and `U10`'s temperature
  after a soak.
- **The removed `U10`:** photograph its marking, compare the lot, and decap it if possible.
- **Sourcing:** establish how `U10` reached the JLC build.
- **Other boards:** screen them with `LDO_IN` to GND ≥ 100 kΩ, `LED_SW` to GND ≈ 1.1–1.2 MΩ, and idle current with the
  light off and on.
- **Scope:** the plug-in and hot-plug surge, and blend mode.
- **The 67 W charger:** test it over C–C.
- **The owner's remaining answers:** see [BOARD_FAILURES.md §7](BOARD_FAILURES.md#7-open-items).

## 9. Certification-readiness items for later (recorded 2026-11-03)

From the audit of the external certification-readiness review, [CERT_REVIEW_AUDIT.md](audit-2026-11-03/CERT_REVIEW_AUDIT.md).
The cheap set is on the `1.03` branch: A1, A2, B2, B5, B7's return vias, and the X2/X3/Z1 wording ([CERT_REVIEW_AUDIT §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)).
C1 followed on 2026-11-04 with the BQ21040 charger. The rest is recorded here for reference; none of it is decided.

| ID | Item | Why it matters | What it takes | Details |
|---|---|---|---|---|
| C1 | Charge temperature limit and charge timer (independent review H-1). **Done in 1.03 (2026-11-04):** `U11` is a BQ21040 with a 10 kΩ NTC (`TH1`) on `TS`, in place of the TP4056 with `TEMP` grounded | **Needed before a safety evaluation.** IEC 62368-1 M.4.2 wants charging stopped when the cell is too hot, and portable equipment is tested beyond its rated ambient | **Done:** charging runs between about 0 and 41 °C at `TH1` (−2…+2 °C and 38…44 °C over tolerances), with a 30 min pre-charge and a 10 h fast-charge timer, and an open NTC stops charging. **Left:** `TH1` sits on the board at (100.6, 93.0), not at the cell, because the spots near the cell needed a 66 mm `TS` route. For a lab, log the cell against `TH1` through a charge (§6), or move the NTC to the cell (leads or a 3-wire pack) in a later revision. The firmware charge-enable override this row used to ask for is no longer needed for the timer; M-5 still wants one (section 10) | [REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04), [§3.6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#36-c1-charge-temperature), [TRIAGE](independent-review-2026-11-03/TRIAGE.md) |
| B1, Z3 | Antenna clearance | GND pour sits about 1 mm from the antenna's sides. Espressif, and KiCad 9's footprint for the module, keep 15 mm clear, which would flag 11 parts here | Step 1: clear the pour from the notch arms (contained). Step 2: move `SW5` and the frontlight block, a re-layout done with the enclosure | [§3.3](audit-2026-11-03/CERT_REVIEW_AUDIT.md#33-b1-and-z3-the-antenna-clearance) |
| B3 | Frontlight boost 6.5–10 mm from the antenna | Possible Wi-Fi desense | Measure range and throughput with the light at full and off first. The fix is B1 step 2 | [§3.5](audit-2026-11-03/CERT_REVIEW_AUDIT.md#35-b3-b4-a4-not-for-103) |
| B4 | Panel capacitors at their `J2` pins (now 5–17 mm away) | Closer to the reference circuit | No legal spots without moving parts (TRACE_AUDIT T5/T9). Check `EINK_3V3` ripple on the first boards (§6) | [§3.5](audit-2026-11-03/CERT_REVIEW_AUDIT.md#35-b3-b4-a4-not-for-103) |
| A4 | 1.0–1.2 mm board | −2.5 to −4.1 dB on board-level loops | Changes button plunger heights, stiffness, the `J1` stake fit and the PTC calibration. Only if a pre-scan fails | [§3.5](audit-2026-11-03/CERT_REVIEW_AUDIT.md#35-b3-b4-a4-not-for-103) |
| B6 | No B.Cu pour under `L1` | Small either way: the pour also shields | One rule area | [§1.1](audit-2026-11-03/CERT_REVIEW_AUDIT.md#11-verdict-per-review-item) |
| B7, rest | Return vias at the other 17 fast-signal vias | Return-path loop area | Two spots under `J7` were skipped because the card slides over them. The other 15 have no legal spot, and the USB pair stays as it is (T18) | [§6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03) |
| C3 | 0.1 µF on `VBUS_PRE_FUSE` at `J1` | Input filtering | A hot-plug study first: a ceramic at the connector rings with the cable's inductance | [§1.1](audit-2026-11-03/CERT_REVIEW_AUDIT.md#11-verdict-per-review-item) |
| D1–D3 | Charge inhibit, switched rails, second I²C bus | Power and bus control | No spare GPIO | [§1.1](audit-2026-11-03/CERT_REVIEW_AUDIT.md#11-verdict-per-review-item) |
| Z5 | 499 Ω in series with UART0 TX (`U4` pin 37 → `TP2`) | Espressif: it suppresses harmonics | Cheapest: production firmware doesn't log on UART0 and uses USB-Serial-JTAG instead. In hardware it is a new part | [§1.2](audit-2026-11-03/CERT_REVIEW_AUDIT.md#12-what-the-review-missed) |

**Paperwork, not layout:**

- **Z2, FCC filing route.** The module's FCC grant excludes portable use: "Separate approval is required for all other
  operating configurations, including portable configurations with respect to 2.1093". Ask a TCB or test lab which route
  applies: a Class II permissive change filed by Espressif, or the host's own FCC ID. The TX-power cap in the certification
  plan settles the exposure maths, not the filing ([§3.7](audit-2026-11-03/CERT_REVIEW_AUDIT.md#37-z2-the-module-grant-and-portable-use)).
- **Z4, labels.** E-labels are allowed for e-readers, but the box still needs "Contains FCC ID: 2AC7Z-ESPS3WROOM1" and
  "Contains IC: 21098-ESPS3WROOM1", or the host's own IDs if Z2 ends there.
- **RoHS.** The README now rules out leaded HASL (Z1). Keep the board house's RoHS statement with the technical file.

## 10. Independent review items for later (recorded 2026-11-03)

These come from the independent board review, [BOARD_REVIEW.md](independent-review-2026-11-03/BOARD_REVIEW.md), as
triaged in [TRIAGE.md](independent-review-2026-11-03/TRIAGE.md).
- **Already on the `1.03` branch:** the four cheap fixes (TRIAGE section 4).
- **Covered elsewhere:** firmware items in §4 (F8–F12), bench items in §6, and H-1, done in 1.03 with the BQ21040
  (C1 in §9).

The rest is recorded here for reference. None of it is decided.

| ID | Item | Why it matters | What it takes |
|---|---|---|---|
| M-5 | The charger cannot wake a pack whose own protection has locked out: the cell detector sees about 0 V | After a week or two in storage the device can look dead, and USB does nothing | If the §6 bench check confirms it: force the charger on for a few seconds after USB plug-in (an RC pulse that holds `Q2` off), or a firmware-driven override. `IO3`, today only on `J6`, could drive it if the header gives it up. The BQ21040 swap does not change the mechanism (the detector now holds `TS` low instead of `CE`), and HARDWARE.md §3.3 already documents the limitation, with handling guidance |
| M-4 | No input over-voltage protection ahead of `U2`, and `CR1` sits ahead of `F1` | A non-compliant 9–12 V source kills `U2`/`U3`/`U10` and burns `CR1`. Since 2026-11-04 `U11` survives it: the BQ21040 is rated 30 V and stops charging above 6.6 V | A 5 V OVP switch or eFuse (≥ 20 V tolerant, trip about 6 V) ahead of `U2`. Until then, the docs say "5 V USB-C chargers only" |
| M-2 (hardware) | 3V3 headroom under coincident peaks | Brown-outs at mid to low charge | Only if the §6 peak measurement shows the LDO limiting: TLV757P (1 A, same SOT-23-5; check the pin-out), remove `Q3` (L-8), widen the 0.25 mm battery tracks |
| L-8 | `Q3` and `Q8` in the battery path. `Q8` is the DW01A's load switch from the EEVblog thread, fitted the other way round to that thread's circuit; by that orientation it is what blocks a reversed cell | — | **Decided 2026-11-04: no change.** The owner's boards start and run fine. The analysis and a reference change are in [TRIAGE §5.1](independent-review-2026-11-03/TRIAGE.md#51-l-8-what-q3-and-q8-do) |
| L-3 | The power mux may chatter on a weak USB source | Brief input switching | If the bench shows it: hysteresis from `ST` to `PR1`, or a lower threshold through `R38` |
| L-11 | SD switch-on dip on 3V3 | Possible brown-out at card power-up | If above 0.2 V: `R78` → 10–22 kΩ (value only) |
| L-5 | Ladder 2's UP(2) level is at the ADC's calibrated limit | Misread power key on cut boards | `R36` 47k and `R35` 27k, together with F12 |
| L-15 | The e-paper boost loop is about 39 mm², and GDR/RESE run 36 mm | EMI while the panel refreshes | After a pre-scan: a 1 µF/50 V capacitor at `D5`, and GDR/RESE routed as a pair |
| L-16 | Tact-switch frames are floating, and the button lines have no TVS | ESD at the buttons | **Frames: done in 1.03 (2026-11-04).** Pad 3 (the hole beside the GND pad) is tied to GND on `SW1`–`SW5`, `SW8`, `SW9` and `SW11` through the footprint `MJTP1117_FG`; pad 4 stays free for the front-mounted bottom buttons ([HARDWARE.md §9.1.1](HARDWARE.md#911-front-mounted-bottom-buttons-optional-hand-fitted)); `SW7` and `SW10` keep floating frames (their pad 1 is not GND). A TVS on the button lines is still open |
| L-17 | Some DNP option pairs short rails if both parts are fitted | Builder error | 3-pad solder jumpers |
