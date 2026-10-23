# SCH-2: put the charge-enable gate on USB_VBUS instead of 3V3

Analysis of 2026-10-18, following up [`AUDIT.md`](./AUDIT.md) item `ACT-SCH-2`. **Applied 2026-10-22: SCH-2+ and the section 8 `R79`/`R80` option are in the Rev 1.02 schematic, board, part fields, BOM and production files (section 9).** Sections 1–8 are the analysis as written on 2026-10-18; where they say "if adopted", read section 9.

**Result:** the change keeps every behavior of the reverse-battery gate ("Fix 4", [DESIGN_REVIEW.md](../../DESIGN_REVIEW.md) §4), saves the whole 6.6 µA that `R81` and `R82` burn on battery, and removes 24 mm of copper. Without further changes it has one cosmetic side effect: a longer, higher glitch on the TP4056's `CE` pin at USB plug-in, which the current wiring already has in a smaller form. Making `R81` 100 kΩ and `R82` 10 kΩ ("SCH-2+", no new part numbers) removes that glitch and improves the leakage margin tenfold. **Recommended: check it with a bodge on a Rev 1.0 board first (section 6), then fold it into Rev 1.01, which has not been fabricated yet.** (Rev 1.01 got it before that check was done; the check is still to do, on the first Rev 1.01 board: section 9.)

## 1. The change

| | As built | SCH-2 | SCH-2+ (recommended) |
|---|---|---|---|
| `Q2` pin 2 (source) and `R81` pin 2 | `3V3` | `USB_VBUS` | `USB_VBUS` |
| `R81` (gate pull-up of `Q2`) | 1 MΩ | 1 MΩ | **100 kΩ** (`C25803`, Basic, already in the BOM) |
| `R82` (`CE` pull-down) | 1 MΩ | 1 MΩ | **10 kΩ** (`C25804`, Basic, already in the BOM) |
| Schematic | | rename one global label, `3V3` to `USB_VBUS`, at sheet position (114.3, 190.5); it moves exactly those two pins (netlist diff) and adds no ERC finding | the same, plus two values |
| Copper | | delete the 3V3 tail that serves only those two pads, re-net two short segments, add one 1 mm stub (section 5) | the same |

`R81`/`R82` were 1 MΩ to keep their drain on the battery small. With their top ends on `USB_VBUS` they only conduct while USB is present, so that reason is gone.

## 2. What it buys

- **Idle current.** On battery with a good cell, `Q9` is on, `Q2` is on and `CE` sits at 3.3 V, so `R81` and `R82` each pass 3.3 µA from 3V3 (simulated: 3.30 + 3.30 µA). With the gate on `USB_VBUS` both are 0 µA without USB. That is −6.6 µA, 11.4 % of the 58 µA sleep floor, or 0.16 mAh a day: in the battery-life estimate for a 500 mAh cell (450 mAh usable, 1.74 mAh a day in deep sleep) that is about 284 instead of 259 days (155 instead of 147 days with a touch tail). Reading-day battery life does not change (under 1 %). In the [HARDWARE.md §16](../HARDWARE.md#16-design-notes--conventions) sleep budget the Fix 4 row goes from 10.0 to 3.4 µA typical (10.7 to 3.8 maximum) and the total from about 58 to 51.4 µA typical (about 91–95 to 84–88 maximum).
- **`CE` never above the charger's own supply.** Today `CE` is held at 3.3 V while the TP4056's `VCC` is 0 V on battery, a condition no datasheet row covers (HW-08 in the firmware's POWER.md). With the change `CE` is either 0 V or equal to `USB_VBUS`, which is `VCC` (the TP4056 allows 10 V on `CE`).
- **Less copper, and no cut-line dependency.** The 3V3 feed of `Q2`/`R81` is a 24 mm tail from the spine at x = 101.1 down to the two pads. It is the reason a board without `R84` needs the `R40`-to-`R81` wire after the cut (HARDWARE.md §16). With the change the charger gate needs nothing from 3V3, and the 3V3 link at y ≈ 64.4–64.9 only feeds the tongue.
- **One cost, on USB only.** With SCH-2+'s 100 kΩ and 10 kΩ, `R81` (50 µA) and `R82` (0.5 mA at 5 V) draw about 0.55 mA from `USB_VBUS` while USB is present and a cell is detected. It flows only with USB present, where the charger alone can take 250 mA.

## 3. How it was checked

The repo's own Fix 4 LTspice deck ([`run_revpol2.py`](../audit-2026-09-16/run_revpol2.py)) was copied and rewired. Its as-built variant reproduces that deck's published table (CE levels, 0.25 A charging of a good cell, 8 µA into a reversed cell, the −0.14 V U5 dip, 14 µA into a latched empty connector); the one deliberate difference is that a 2.5 V cell now trickle-charges at 25 mA, as the TP4056 does, instead of 0.25 A. Added to it: datasheet-fitted models of the AO3401A (`C15127`: Ciss/Coss/Crss, Rds(on), Vth −0.5/−0.9/−1.3 V) and BSS138 (`C7420339`: Vth 0.8–1.6 V), and a behavioral TP4056 (CE threshold 1.5 V, swept 1.0–3.5 V; UVLO 3.7 V; 20 µs soft start; 10 % trickle below 2.9 V). Decks, scripts and results: [`sch2-sim/`](./sch2-sim/).

**Static (one row per case of the Fix 4 matrix):**

| Case | `CE` as built | `CE` SCH-2 / SCH-2+ | Charger |
|---|---|---|---|
| Cell 3.7 V, no USB (sleep) | 3.3 V, `R81`+`R82` 6.6 µA | 0 V, 0 µA | off |
| Charge a 3.7 V cell | 3.3 V | 5.0 V | 0.25 A, same |
| Charge a 2.5 V cell (also at Q9 Vth 1.5 V and Q2 Vth −1.3 V) | 3.3 V | 5.0 V | 25 mA trickle, same |
| Reversed cell with USB (also hot-swapped in, and reversed after a latch) | 1 mV | 1 mV / 0.01 mV | off, same |
| Reversed cell, no USB | 0 | 0 | off |
| No cell, `P+` already charged (the documented latched empty connector) | 3.3 V | 5.0 V | enabled, 14 µA at the 4.2 V float, same |

**USB plug-in with no cell or a reversed cell (`Q9` off, so `Q2` should stay off).** The gate floats behind `R81` and the source steps, so `Q2`'s gate and drain capacitances couple the step onto `CE`. This exists today: the 3V3 rail rises about 1 ms after `VBUS` and drags `CE` up the same way. Time is spent above the assumed 1.5 V threshold; charge is what the trickle-limited charger would push:

| Wiring | USB-A hot plug / 2 µs edge | 100 µs edge | USB-C, 1 ms ramp |
|---|---|---|---|
| As built (3V3 source, 1 MΩ/1 MΩ) | 2.3 V, 194 µs, 4.8 µC | same | same |
| SCH-2, 1 MΩ/1 MΩ | 4.3–4.7 V, ≈250 µs, 6 µC | 4.1 V, 227 µs, 5.7 µC | 1.1 V, none |
| **SCH-2+, 100 kΩ/10 kΩ** | 2.1–3.3 V, **≤ 2 µs**, ≤ 0.05 µC | 0.15 V, none | 0.02 V, none |
| SCH-2 plus 1 nF on `CE` (either resistor set) | 0.6–0.8 V, none | 0.1–0.8 V, none | 0.02–0.6 V, none |

Nothing latches in any case (`CE` is back at 0 V), and the most the glitch can do is a few microcoulombs of trickle charge. With a good cell `CE` simply follows `VBUS` and charging starts when `VCC` passes 3.7 V.

**Leakage margin (reversed cell with USB; `Q9` and `Q2` must both stay off).** Fix 4 fails if `Q9`'s off-state leakage drags the gate down far enough, or `Q2`'s sub-threshold leakage lifts `CE`. The BSS138 data sheet only guarantees IDSS ≤ 0.5 µA at 50 V and 25 °C, so the first row is not a hypothetical corner:

| Wiring | `Q9` leakage that turns `Q2` on (Vth −0.5 V / −0.9 V) | `Q2` leakage that lifts `CE` to 1 V |
|---|---|---|
| As built, and SCH-2 with 1 MΩ/1 MΩ | 0.5 µA / 1 µA | 1 µA |
| **SCH-2+** | **not reached at 5 µA** (gate node stays at 4.5 V) | **100 µA** (`CE` is 30 mV at 3 µA) |

## 4. Not covered

- The TP4056 data sheet gives no `CE` threshold ("TTL or CMOS level") and no `CE` input structure, so the sweep above is an assumption, not a measurement. The same goes for an internal `CE` clamp to `VCC`: the as-built board would show it as `USB_VBUS` sitting near 2.7 V on battery, which the working prototypes evidently do not.
- AO3401A capacitances are given only at 15 V; the low-voltage values are estimates.
- With `Q2`'s source on `USB_VBUS`, plugging USB into a board whose DW01A has opened `Q1` after an over-current trip with a full cell puts about −9.5 V across `Q2`'s gate-source (rating ±12 V); a `USB_VBUS` overshoot above about 7.8 V in that instant would exceed it. Unlikely and brief (`CE` goes high and charging pulls `B−` back up).
- `USB_VBUS` floating up on battery through `CHRG`/`STDBY` (the rest of HW-08) is untouched. With `R82` at 10 kΩ it cannot rise above about one `Q2` threshold; measure it anyway.
- No thermal, tolerance-stack or ESD-gun simulation; the LDO and TPS2116 are behavioral.

## 5. The board edit, tried on a scratch copy

Applied with pcbnew's API to a copy of the board and the label renamed in a copy of the schematic: **0 unconnected items, 0 parity errors, no violation beyond the existing `J1` pad-pair findings; ERC unchanged (no new violation); the netlist differs in exactly two pins.** [`sch2-sim/proto_layout.py`](./sch2-sim/proto_layout.py) does it. [`sch2-sim/sch2_edit_map.png`](./sch2-sim/sch2_edit_map.png) marks steps 2–4 on the board (red = delete, orange = change net, green = add). By hand in KiCad:

1. Rename the global label `3V3` at (114.3, 190.5) to `USB_VBUS` (optionally `R81` to 100 kΩ and `R82` to 10 kΩ), then *Update PCB from Schematic*.
2. Change the net of the two existing segments that join `R81` pin 2 (94.90, 85.31) to (94.90, 86.12) and on to `Q2` pin 2 (93.71, 87.31) to `USB_VBUS` (UUIDs `08c1c457`, `42601ea0`).
3. Delete the 3V3 tail beyond `R81` pin 2, nine `B.Cu` segments, 20.4 mm: (94.90, 85.31) to (97.30, 82.91) to (97.30, 80.59) to (96.67, 79.96) to (96.67, 79.44) to (98.56, 77.55) to (99.53, 77.55) to (100.41, 76.67) to (100.41, 69.25) to (101.10, 68.56) (UUIDs `20328915`, `80b6194b`, `de30d9aa`, `ebfafa9e`, `6bef1cfc`, `ab780e2a`, `93de4fe7`, `a39d2a59`, `7431d59c`). Shorten the spine `f98f809a` so it starts at the 3V3 link at (101.101, 64.9) instead of (101.101, 68.56). This is a good moment to fix the 1 µm stub (`157ac2d7`, (101.000, 64.900) to (101.001, 64.900)): drag its free end to (101.101, 64.9). It then joins the 45° link (`47cde673`) to the start of the spine as a 0.1 mm segment.
4. Draw one 0.25 mm `USB_VBUS` stub on `B.Cu` from the existing `USB_VBUS` node at (93.57, 89.30) up to the lower edge of the `Q2` pin 2 pad at (93.57, 88.26): 1 mm, 0.5 mm from the nearest ground via.
5. Refill the zones and run DRC with schematic parity. Do **not** run *Cleanup Tracks & Vias*: it deletes the front-button tabs ([HARDWARE.md §9.1.1](../HARDWARE.md#911-front-mounted-bottom-buttons-optional-hand-fitted)).

## 6. Bench check on a Rev 1.0 board (about 30 minutes)

Parts are on the back. Name the pads by part and pin: `Q2` pin 2 is the pad joined by a short track to `R81` pin 2.

1. **Baseline** on battery with USB and any serial adapter unplugged: sleep current (meter in series with the cell), `CE` (`U11` pin 8) and `USB_VBUS` (`F1` pin 2) to ground. Expect `CE` ≈ 3.3 V and `USB_VBUS` near 0.
2. **Bodge.** Cut the 0.25 mm 3V3 track that leaves `R81` pin 2 toward the upper right (about 1 mm from the pad, near (95.6, 84.6)); check with the meter that `R81` pin 2 is no longer joined to 3V3. Scrape the mask off the `USB_VBUS` track at (93.6, 89.4) and tack a 30 AWG wire from there to `Q2` pin 2 (or to `F1` pin 2, 6 mm away).
3. **Expect after the bodge:** `CE` ≈ 0 V on battery; sleep current down by about 6.6 µA; `USB_VBUS` under 50 mV. Plug in USB with a cell: `CE` ≈ 5 V, charging as before (about 234 mA with `R6` = 4.7 kΩ). Plug in without a cell: `CE` stays low, `J5` stays at 0 V. Repeat the DESIGN_REVIEW §13 reversed-cell check with a current-limited emulator, never a real reversed cell.
4. **Glitch.** Scope `CE` at plug-in (no cell, then a reversed-cell emulator), A-to-C cable and USB-C charger; compare with the table above. Then replace `R82` by 10 kΩ and `R81` by 100 kΩ and repeat: the glitch should shrink to a few microseconds.

If the numbers match, SCH-2+ goes into the Rev 1.02 files; if the sleep current does not drop, something other than `R81`/`R82` is feeding `CE` and that is worth finding first.

## 7. If adopted, update

HARDWARE.md §3.2 (the `CE` pin-table row), §3.3 (the "≈10 µA idle" figure in the mitigation note), §16 (the sleep-budget row and totals, the detector paragraph, the "Considered and declined" note, which this makes moot because the idle cost goes away without raising `R79`–`R82`, and the cut-line row with its older-board wire); DESIGN_REVIEW.md §4 (the `R81` and `Q2` wiring-table rows, "CE only ever sees 3V3 or GND", the idle-drain paragraph); README (the cut-down bullet about the `R40`–`R81` wire); `fabrication/part_fields.csv`, `production/jlc_bom.csv` and `fabrication/BOM.md` (the `R81`/`R82` values, for SCH-2+); the regenerated `production/` set and both PDFs; the site's order data and its X3 generator; the firmware's POWER.md sleep budget.


## 8. Optional follow-on: `R79`/`R80` ten times larger (not part of SCH-2)

`R79` (100 kΩ) and `R80` (1 MΩ) bias `Q9`'s gate from the raw cell: gate = 0.909 × cell voltage, which is what turns `Q9` on when a correctly oriented cell is present. After SCH-2 they are the whole idle cost of the detector: Vcell / 1.1 MΩ = 3.4 µA at 3.7 V (3.8 µA at 4.2 V). They sit outside the protection FETs, so they also keep draining a cell after an over-discharge cut-off (≈7 µA together with `R56`/`R57` and the DW01A, [HARDWARE.md §3.3](../HARDWARE.md#33-cell-protection--reverse-polarity)).

**The change:** `R79` to 1 MΩ (`C22935`, what `R80` is today) and `R80` to 10 MΩ (`C7250`, what `R57` already is). The 1:10 ratio is kept, so the thresholds do not move; no new part numbers and no layout change. `R57` went from 1 MΩ to 10 MΩ for the same reason on 2026-09-21.

**What it buys:** 3.0 µA typical (3.4 µA at 4.2 V). With SCH-2 the sleep floor goes from about 58 to 48.4 µA (−17 %), about 259 → 298 days of deep sleep in the 500 mAh estimate, and the resistors across the cell draw less after an over-discharge cut-off (about 2.4 → 0.5 µA at 2.4 V); the whole post-cut-off drain is another matter, see section 9. A ×3 version (`R79` 300 kΩ, `R80` 3 MΩ) saves 2.2 µA.

**Checked** on the SCH-2+ wiring with [`sch2-sim/r79_study.py`](./sch2-sim/r79_study.py) (results in `sch2-sim/results_r79_*.json`):

| Check | 100k / 1M (now) | 300k / 3M | 1M / 10M |
|---|---|---|---|
| Nine static Fix 4 cases | reference | same `CE` levels, same charging currents (0.25 A, 25 mA) and same −0.14 V `U5` dip | same |
| Cell voltage that enables `CE` | 1.6 V at Vth 1.3 V, 1.8 V at Vth 1.6 V | same | same |
| Leakage from `Q9`'s gate to `B−` that stops a 2.4 V cell enabling `CE` (Vth 1.6 V) | still enabled at 3 µA (calculated 9.6 µA) | fails at 3 µA (calculated 3.2 µA) | fails at 1 µA, enabled at 0.3 µA (calculated 0.96 µA) |
| Current into the gate that falsely enables `CE` with no cell (Vth 0.8 V) | fails at 3 µA | fails at 1 µA | fails at 1 µA, fine at 0.3 µA |
| Same injection with a reversed cell | stays off to 3 µA | same | same |

The logic is unchanged; what falls about tenfold is how much leakage the high-impedance gate node tolerates. For scale, the BSS138's gate leakage is at most ±50 nA at VGS = ±10 V (±100 nA at ±20 V; data sheet of C7420339; far less at 3–4 V), and a board whose flux residue passes the usual 100 MΩ surface-insulation test leaks at most about 40 nA at 4 V, so the margin is still roughly 6–19× against the data-sheet figure and 7–24× against the board-leakage figure. A false enable with no cell is the already documented latched empty connector (14 µA, harmless); a false disable would only matter for reviving a cell sitting at the 2.4 V cut-off. The earlier decision to leave these resistors alone ([DESIGN_REVIEW.md](../../DESIGN_REVIEW.md) §4, HARDWARE.md §16) was mostly about `R81`/`R82` at 1 MΩ, which SCH-2+ replaces, but it does spend part of the remaining margin.

**Not covered:** temperature and contamination. Unplugging the cell while charging is not affected by the values: `B−` stays tied to ground through `Q1` and `P+` stays up, so the detector keeps reading a cell, the documented latched empty connector. If adopted, check on the bench that `CE` follows a bench supply on the cell pins from about 2 V up, and that `CE` stays low with no cell and USB present.

**If adopted, also update:** HARDWARE.md §3.3 (the ≈3.8 µA and ≈7 µA figures) and §16 (the detector row, the totals and the "Considered and declined" note); DESIGN_REVIEW.md §4 ("Not worth reducing further"); `fabrication/part_fields.csv` and `fabrication/BOM.md` (`R79` joins the 1 MΩ group, `R80` the 10 MΩ group).

## 9. Applied (2026-10-22)

Done in the repository, in one edit together with the `J1` swap ([`J1_USB_C_OPTIONS.md`](./J1_USB_C_OPTIONS.md) section 9):

- **Schematic.** The global label `3V3` at (114.3, 190.5) is now `USB_VBUS`; `R81` 100 kΩ, `R82` 10 kΩ, `R79` 1 MΩ, `R80` 10 MΩ (Value plus `MPN`/`Manufacturer`/`LCSC` through `fabrication/part_fields.csv` and `apply_part_fields.py`: `R81` `C25803`, `R82` `C25804`, `R79` `C22935`, `R80` `C7250`, no new part numbers). The netlist differs from the previous one in exactly two pins (`Q2.2`, `R81.2`: `3V3` to `USB_VBUS`); ERC is unchanged (41 findings, all warnings, before and after).
- **Board.** Steps 2–4 of section 5 as written (nine `B.Cu` segments and the lower spine deleted, 24.06 mm of 3V3 copper in all; the two short segments re-netted; the 1 mm `USB_VBUS` stub added), plus the `1 µm` stub of `ACT-PCB-1` ended on the spine at (101.101, 64.9). Done with pcbnew's API ([`sch2-sim/proto_layout.py`](./sch2-sim/proto_layout.py) is the same recipe), then the zones were refilled; *Cleanup Tracks & Vias* was not used (the four `track_dangling` exclusions in `.kicad_pro` are untouched).
- **Docs and files.** `README.md` (cut-down bullet, Step 6/7), `docs/HARDWARE.md` (§3.1, §3.2, §3.3, §16: detector row 10.0 → 0.4 µA, totals ≈58 → ≈48 µA typ and ≈91–95 → ≈81–85 µA max, cut-line row), `DESIGN_REVIEW.md` §4 (wiring table, `CE` levels, idle drain), `docs/LED_ALT.md` (sleep floor), `fabrication/BOM.md`, `fabrication/part_fields.csv`, `production/jlc_bom.csv` and the regenerated `production/` set, both PDFs.
- **Found by the 2026-10-22 audit, not fixed: a lock-out loop.** When the DW01A opens `Q1` (over-discharge or over-current cut-off), `B−` floats down to a cell voltage below board GND, while `Q9`, biased from the cell itself, stays on. `R81` and `Q2`/`R82` then close a loop around the open `Q1` through the system load (cell+ → `Q3` → `Q8` → `P+` → load → GND → `R82`/`Q2` → `USB_VBUS` → `R81` → `Q9` → `B−`). An LTspice run with generic models and a 2.5 V cell gives a cell drain of 6.6 µA with a 1 MΩ load on `P+`, 15.8 µA with 100 kΩ and 20.7 µA with 10 kΩ, against 7.6 µA for the Rev 1.0 wiring; a hand estimate of the loop (cell voltage across the load, `R82` and `R81`) agrees within about 30 %, and `USB_VBUS` sits 0.1–0.4 V below GND. Nothing here is measured, and the real load at 0.2–1.8 V is unknown. It matters only after a low-battery cut-off, where it roughly halves the time before the cell is too low for the detector to enable charging. Putting `R81` back to 1 MΩ would cut the loop to about 2–3 µA but give up the plug-in glitch fix and the tenfold `Q9` leakage margin. Bench check: a current-limited supply as the cell, DW01A tripped, USB off; measure the cell current and `USB_VBUS`.
- **Not done / still open:** the bench check of section 6 on a real board (the `CE` threshold of the `TP4056` and the `CHRG`/`STDBY` back-feed are the unmeasured parts). **Done 2026-10-22:** the firmware docs carry the Rev 1.02 values beside the Rev 1.0 ones: both `POWER.md` copies (`silkscreen-firmware/crossink` and `crosspoint-reader`), `REQUIREMENTS.md`, `PORTING.md`, `BATTERY-LOG.md`, the beta-test plan and the beta hardware checklist (whose B-8, the resistance across `J5` with no cell, and B-13, `CE` on battery, would otherwise have rejected a good Rev 1.02 board). `TEST-SUITE.md` and `beta-test/research/C-acceptance-run-design.md` still quote the Rev 1.0 typical ranges (58-73 µA); their pass limits (110 µA, flag at 95 µA) hold for both revisions.
