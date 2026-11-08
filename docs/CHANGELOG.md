# Silkscreen mainboard: changelog from Rev 1.0 to Rev 1.03

**Baseline:** Rev 1.0 is `aeb5b39`, the files ordered on 2026-09-21: the boards from that order
([audit-2026-09-30/AUDIT.md](audit-2026-09-30/AUDIT.md)). **Current:** Rev 1.03 (2026-11-04). **Written:** 2026-11-04.

Revs 1.01 and 1.02 were never built; their changes are included and marked. Part and connection changes are read from
netlist diffs of each revision, and the board figures from the board files. The details behind each item are in
[REV_1_03_STATUS.md](REV_1_03_STATUS.md), [NEXT_REVISION.md](NEXT_REVISION.md) and the audits linked from them.

## At a glance

- **Unchanged:** the outline (60 × 111.25 mm), cut-outs, mounting holes, layer count and the ESP32-S3 pin map. No
  processor pin changed nets, so firmware pin assignments carry over.
- **Parts:** 184 → 189, with 11 not fitted before and after. Added `R84`, `F3`–`F6`, `R85`, `R86`, `TH1`, `C38`; removed
  `R1`, `C1`, `R42`, `R71`.
- **New footprints:** `J1` (USB-C), `U10` (frontlight driver), `U11` (charger), and `MJTP1117_FG` for eight of the ten
  tact switches.
- **Board:** vias 192 → 251, teardrops 0 → 860, three no-pour zones, and a custom design-rule file
  (`silkscreen_pcb.kicad_dru`).

## Rev 1.01 (never built)

- **`R84` (1 Ω) in series with `C2`'s ground:** damps the voltage spike when a live USB source is plugged in. The modelled
  worst case at the power switch `U2`'s input falls from 7.95 V to 5.60 V.
- **Cut-down boards:** five GND stitching vias below the cut line. The charge-enable switch also keeps its supply after
  the cut (a 3V3 link here, replaced in 1.02).
- **`J6` pinout label:** its two rows were printed the wrong way round on Rev 1.0; now swapped.
- **Production files:** JLC rotation and position offsets for `U2`, `U5`, `D2`, `D8`, `J7`, `J4`, `U4`, so the placement
  file matches JLC's footprints.
- **Silkscreen:** revision label and tidied reference labels.

## Rev 1.02 (never built)

- **`J1`:** the through-hole GCT USB4085 becomes the SMD USB4105 (JLC C2765186). It has hand-solder pad extensions and a
  JLC position offset, and its traces and shield ring were re-routed.
- **Charge-enable switch (`Q2`/`R81`):** fed from `USB_VBUS` instead of 3V3. `R79`/`R80`/`R81`/`R82` go from
  100k/1M/1M/1M to 1M/10M/100k/10k. That saves about 10 µA in sleep, and cut boards need no rewiring.

## Rev 1.03

### Branch protection, from the case 1 repair

- **Resettable fuses (PTCs)** (Bourns MF-FSMF010X-2: 0.10 A hold, 0.30 A trip) on four supply branches:
  - `F3`: the frontlight booster (net `/LED_VIN`), with a 1 mm no-pour zone so it trips as designed;
  - `F4`: the touch supply, replacing `R42`;
  - `F5`: `J6` pin 7 (net `J6_3V3`), budgeted at 20 mA; heavier loads go on pin 12;
  - `F6`: the e-paper booster and the panel's logic supply (net `EINK_3V3`).
- **Battery protection current sense:** `R85` ∥ `R86` (two 0.1 Ω 1206) between `Q1` pin 3 and GND. The DW01A protection
  chip now trips at 0.83–1.68 A; Rev 1.0 sensed only across its FETs. `C34` goes from 2.2 nF to 0.1 µF.
- **USB-C shell:** tied straight into the ground pours; `R1` (1 MΩ) and `C1` (1 nF) removed.

### Charger

- **`U11`:** the TP4056 is replaced by TI's BQ21040 (SOT-23-6), plus `TH1`, a 10 kΩ temperature sensor (NTC) on the
  board ([REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04)):
  - charging only between about 0 and 41 °C at `TH1`;
  - a 30 min pre-charge timer and a 10 h charge timer;
  - input rated to 30 V, and charging stops above 6.6 V;
  - charge current about 115 mA, against about 234 mA from Rev 1.0's TP4056.
- **Charge-enable switch now drives the charger's `TS` pin:** `Q2` goes from AO3401A to BSS138, and `R82` becomes 200k,
  so an unplugged sensor means no charging. `R71` and the `STDBY` status line are removed, so the charge-status ADC
  reading loses its "charge complete" level.
- **`TS` hardening (layout pass, 2026-11-04):** `C38`, the BQ21040 datasheet's optional 0.22 µF ESD capacitor, from
  `TS` to GND, and `TH1` moved from beside the USB-C port to beside `R82` (about 7 mm from `U11`). `TS` is 15.75 mm
  long instead of 23 mm and no longer runs between `F1`'s pads.

### Frontlight driver

- `U10` sits on TI's example land pattern (DRL0006A, 0.20 mm pad gaps, with its own design rule).
- Its corner is re-laid out: GND via moved off the switch node, pour pulled back, pin 4 solid to ground, and a second
  GND via.

### Layout, EMC and durability (no circuit change)

- Ground pours pulled back from switch nodes (0.5 mm) and high-voltage nets; 9 traces and vias moved off high-voltage
  pads.
- New GND vias at:
  - the ESD parts;
  - 10 power layer changes;
  - 14 along the edges;
  - 8 beside fast-signal vias;
  - `U4` pins 1 and 40.
- `C33` and `R7` swapped, so the 0.1 µF sits about 1 mm from the ESP32's 3V3 pin.
- Copper cleared from the mounting holes and the right edge, the antenna keep-out now also blocks pour, and 19 traces
  were straightened.
- Pour-free areas keep ground about 1 mm from `P+` and 3V3 where they cross the cut line.
- To make room for `R85`/`R86`: `R76` relocated, `R8`, `R9` and `U9` moved and rotated, `R72`/`R74` nudged.
- Teardrops on all pads and vias (860).
- Tact-switch metal covers: the leg beside the GND pad (pad 3) is tied to GND on `SW1`–`SW5`, `SW8`, `SW9` and `SW11`.
  The other leg (pad 4) stays free for the front-mounted bottom-button option
  ([HARDWARE.md §9.1.1](HARDWARE.md#911-front-mounted-bottom-buttons-optional-hand-fitted)); `SW7` and `SW10` are
  unchanged.
- The duplicate GND via inside `D3`'s pad is removed; `D3` keeps its own via beside the pad.
- **Side buttons level (2026-11-07):** `SW1`, `SW4`, `SW10` (right) and `SW5`, `SW7` (left) now all sit 2.75 mm behind
  their edge, so the plungers stand out the same 0.97 mm. In Rev 1.0, `SW10` stood out 0.22 mm more than `SW4` and
  `SW1` 0.05 mm less. The copper that ran beside `SW10` (`J6_3V3`, `W-`, `C-`, `R62`, `3V3`) and `SW1` (`R61`) moved with
  them. The 4.26 case draws its power key (`SW10`) from the board file, so a lid printed for Rev 1.0 boards does not
  suit Rev 1.03 boards: regenerate and reprint it with them ([REV_1_03_STATUS §17](REV_1_03_STATUS.md#17-side-buttons-level-straight-left-edge-2026-11-07)).
- **Straight left edge (2026-11-07):** the left edge and the antenna notch's walls leaned 0.045° (the bottom end sat
  0.06 mm further in than the top); they are now exactly vertical, so the main body is 60.000 mm wide from top to
  bottom. The right edge was already straight.

### Silkscreen

The title blocks and back silkscreen print Rev 1.03 and the date 2026-11-04, every reference label is 0.5 mm, and the
touch-option note names `F4`.

### Default build (2026-11-05)

- **RTC:** the default is now `U14`, the Micro Crystal RV-8263-C7 (±20 ppm, about 190 nA, I²C 0x51), in place of `U13`,
  the DS3231MZ (±5 ppm, I²C 0x68). That is about $1.6 less per board at 30 boards. `U13` stays on the board as the DNP
  alternate: fit one RTC or none. The firmware probes 0x68 first and falls back to 0x51. JLC stock of the RV-8263-C7 is
  thin (1,058 on 2026-11-05).
- **Production files:** regenerated for Rev 1.03: the Gerber zip `Silkscreen_Reader_PCB_1.03.zip`, the Toolkit BOM and
  placement, the hand-edited `jlc_bom.csv` and the other-fab files. The Rev 1.02 zip moved to `production/backups/`.
  `U14` carries a JLC rotation correction (the `FT Rotation Offset` field), because JLC's library footprint for the part
  is landscape and KiCad's is portrait.

## Behaviour that differs from Rev 1.0

- **Charging:** slower (about 5 h for 500 mAh, against 2.5–3 h), stops outside about 0–41 °C, and is capped at 10 h.
- **Charge-status reading:** firmware must decode it differently (NEXT_REVISION item F11).
- **Frontlight:** keep the 50 % brightness cap (item F6).
- **Battery protection:** it trips at 0.83–1.68 A, and a trip on battery needs USB to clear
  ([TRIAGE §5.1](independent-review-2026-11-03/TRIAGE.md#51-l-8-what-q3-and-q8-do)).
- **Faults:** on the frontlight, e-paper, touch or `J6` pin 7 branches, a fault now trips that branch's fuse instead of
  loading the whole rail.
- **`J6` pin 12 while charging:** the BQ21040 ends a charge when the current into `P+` falls to about 10 % of 115 mA
  (9–14 mA; the TP4056 ended at about 23 mA). A continuous load of more than about 5 mA on pin 12 while USB is connected
  keeps the charge from terminating, and the 10 h timer then stops it
  ([audit](audit-2026-11-07/BQ21040_AUDIT.md#2-findings-that-matter-merged-across-the-lenses), finding 1).
- **Charging window:** guaranteed only from +1.6 to +37.7 °C at `TH1` (nominal −1.1 to +40.9 °C), and `TH1` reads about
  1.5–3 K warm while charging, so in a warm room or a closed case a charge can pause and resume (audit finding 2).

## Readiness for an order (2026-11-04)

The design is well checked. Every change passed the design-rule check with 0 errors, the schematic and board agree, and
the netlists diff cleanly. Most changes are protective: they close the gap that both field failures fell into, faults
that draw less than 1 A and so never trip the input fuse ([BOARD_FAILURES.md](BOARD_FAILURES.md)). A case-1-style short
in `U10` now trips `F3` in seconds instead of burning.

A batch working like the 1.0 batch is a different question. Rev 1.0 is a proven build. Its record isn't spotless
(case 1 was traced to `U10`, case 2 is still unexplained), but most of the board is proven. In 1.03, several changes
reach every board and none has ever been built:

| Change | If it were wrong | How to retire the risk |
|---|---|---|
| `J1` SMD USB-C and its JLC offset (1.02) | Every board: no USB or charging; weaker mechanical hold than the through-hole part | JLC placement preview; first-article build; plug-cycle and side-load check |
| BQ21040, sensor and switch (1.03) | No charging, or charging at the wrong temperatures | Placement preview (chip rotation); first-article charger checks ([NEXT_REVISION §6](NEXT_REVISION.md#6-verification)) |
| `U10` on the new land pattern (1.03) | Frontlight dead or pins bridged | Placement preview; inspect the solder joints |
| Branch fuses `F3`–`F6` (1.03) | Brown-outs or false trips during refresh, full brightness, or touch | Full refresh, 30 min at 100 % light, touch test |
| Sense resistors and `C34` (1.03) | Protection trips on load peaks, device dead until USB | Measure the combined peak current (review item L-2) |
| Layout edits, vias, teardrops, shield tie | Low; all pass the design-rule check | Visual inspection |

An independent audit of the charger block (2026-11-07: the IC and its power path, the `TS` network and enable logic, the
JLC files, the layout) found no blocker and no major. Its minor findings and the added first-article checks are in
[audit-2026-11-07/BQ21040_AUDIT.md](audit-2026-11-07/BQ21040_AUDIT.md).

**Before any order:**

1. **Production files: regenerated on 2026-11-05.** `production/` is Rev 1.03, with the BQ21040 and the new fuses. What is
   left is the placement preview at JLC: look at the rotation of `U11`, `U14`, `J1`, the fuses `F3`–`F6` and the new
   0.22 µF `C38` before approving the order. The rotation corrections for `U11` and `U14` were derived from JLC's
   library footprints, not from the preview.
2. **Check `U10` stock.** On 2026-11-04 LCSC showed only 68 TPS923610. Everything else new was plentiful (the BQ21040
   at 3,365). Check JLC's own stock against the batch size; the README describes a two-part substitute if it runs out.
3. **Firmware:** the pin map is the same. Add the charge-status decode (F11), keep the 50 % brightness cap (F6), and
   ideally the touch-sleep and low-battery items (F9, F10).

**Recommendation:** build a small first-article run of about five boards and run the checks in
[NEXT_REVISION §6](NEXT_REVISION.md#6-verification) and
[REV_1_03_STATUS §10](REV_1_03_STATUS.md#10-review-checklist-in-kicad) before a full batch. If those pass, 1.03 deserves
at least the confidence 1.0 has, and more on safety.
