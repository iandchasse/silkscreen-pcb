# BQ21040 charger block: independent audit (2026-11-07)

**Files audited:** the committed Rev 1.03 design, `7b7d2fb` (branch 1.03). **Written:** 2026-11-07.

**Method.** Four independent auditors (Claude Opus subagents), one lens each, read-only, working from an evidence pack
built from the committed files: netlists before and after the charger swap, TI's current datasheet (SLUSCE2D), the Murata
NTC and BSS138-clone sheets, and JLC's own footprints. Each derived its numbers from primary sources before reading the
design's claims, and had to confirm any BLOCKER or MAJOR by a second method. The findings that carry a decision were
re-checked afterwards (marked "re-checked" below). One round, no fix loop. Nothing in the design files was changed.

| Lens | Question | Result | Report |
|---|---|---|---|
| A | The IC and its power path: pinout, ratings, charge parameters, capacitors, loads, protection interplay, heat | 0 blocker, 0 major, 4 minor, 6 note | [lens-A](lens-A-ic-power-path.md) |
| B | The `TS` network, the charge-enable logic and the status ladder | 0, 0, 6 minor, 3 note | [lens-B](lens-B-ts-enable-status.md) |
| C | JLC footprints, the placement file, the BOMs and the order zip | 0, 0, 1 minor, 6 note | [lens-C](lens-C-jlc-production.md) |
| D | Physical layout, DRC and the thermal position of `TH1` | 0, 0, 2 minor, 6 note | [lens-D](lens-D-layout-physical.md) |

The lens reports are verbatim. The paths they cite (`reports/`, `extract/`, `D-assets/`) point into the session's evidence
pack, which is not in the repo; the two Lens B scripts are in [lens-B-scripts/](lens-B-scripts/).

## 1. Verdict

The block is correct as drawn and as exported for JLC. All six pins agree between the datasheet, the KiCad symbol, the
netlist and JLC's own land. It charges at about 115 mA (104-127 mA), regulates to 4.16-4.23 V and terminates at 9-14 mA.
Every single-part fault on the `TS` pin (`TH1` open, shorted or missing, `R82` or `C38` shorted, `Q2` stuck on) leaves the
charger off. JLC's placement rotations for `U11`, `Q2` and the passives come out right by two methods, the order zip
matches the board to 0.000 mm, and DRC reports nothing in the block. **Nothing found should stop a five-board first
article.** The findings are all minor: a documentation limit on `J6` pin 12, a narrower charging window at `TH1` than
documented, a new enable-logic sensitivity when a deeply discharged cell is revived, firmware thresholds, and an
input-capacitor position to scope.

## 2. Findings that matter (merged across the lenses)

| # | Lens IDs | Sev | Finding | Re-checked | Action |
|---|---|---|---|---|---|
| 1 | A-01 | MINOR (MAJOR for an accessory on pin 12) | A continuous load on `J6` pin 12 (`P+` through `F2`) above the charger's termination current (9.3-14 mA, 10 % of the charge current) keeps the charge from ever terminating. The 10 h fast-charge timer then ends charging and the accessory runs off the cell although USB is in. New with the BQ21040: the TP4056 terminated at about 23 mA. HARDWARE.md J6 section 4 sends heavier accessories to pin 12. The light attachment does not use pin 12. | Mechanism in TI's text (termination is 10 % of the fast-charge current; a system load must not keep the battery from charging fully within the 10 h timer) and in the netlist (`F2` pin 2 on `P+`, pin 1 to `J6` pin 12). Whether charging restarts after the timeout is not specified. | Docs: limit the average pin-12 load while charging to about 5 mA, or state that charging stops after 10 h. Optional firmware warning. |
| 2 | B1, A-03, D-2 | MINOR | Charging is guaranteed at `TH1` only from about +1.6 to +37.7 C (nominal -1.1 to +40.9 C), not 0-45 C. `TH1` is 7.1 mm from `U11`, 28 mm from the cell bay and reads about 1.5-3 K warm while charging, so in a 30-35 C room or a closed case charging can pause and resume; at the cold end the cell can be 1.5-3 K colder than `TH1` reads. Fail-safe both ways. | Hot threshold by hand: 275 mV / 50 uA gives `TH1` = 5.66 kOhm, 40.8 C on the B3380 curve; the earliest stop (290 mV, 48 uA) gives 38.0 C. | Bench: thermocouple on `TH1` and the cell in a 30 C room. If charging pauses, move `TH1` away from `U11` and `F1`, or accept it. Optional firmware: no charge start below about 3-5 C board temperature. |
| 3 | B2, A-02 | MINOR | **New in 1.03:** `Q2` changed from a P-FET referenced to `USB_VBUS` (gate `/DET_NODE`, source `USB_VBUS`) to a GND-referenced N-FET. While a cell sitting in the board `DW01A`'s over-discharge lockout is charged, the current goes through `Q1`'s body diode and `B-` sits about 0.6-0.75 V above GND; `Q9` passes that level to `Q2`'s gate. The BSS138 clone's gate threshold is 0.8 V minimum (typ 1.2 V), so a low-threshold part can sink the 23-46 uA that pulls `TS` under the hot or disable threshold, and charging stutters until the cell leaves lockout. Fail-safe (the charger stops) and rare (a deeply self-discharged cell and a low-threshold part). Lens A called it "not new"; the old netlist shows it is new. | Old netlist: `Q2` pin 2 = `USB_VBUS`, pin 3 = `CE`. Sink currents recomputed: 22.7 uA (hot) and 41 uA (disable) at 25 C. `DW01A` (PUOLOP, Rev B): over-discharge 2.4-2.6 V, release 2.8-3.0 V; its timing figure releases at the release voltage unless `VM` dips below an unnumbered charger-detect level, so whether `B-` stays elevated until about 2.5 V or about 2.9 V cannot be settled on paper (minutes of charging either way). | Bench: hold a cell at 2.2-2.6 V in lockout, plug in USB, log `B-`, `TS` and the charge current at 25 and 45 C. If it stutters, change `Q2` to an N-FET with Vth(min) of at least 1.0 V (a BOM-only change, same pinout; check JLC's land for the new code). Lens B's other suggestion, 1 MOhm from `Q2`'s gate to GND, would not work because `Q9` drives that node. |
| 4 | B5, A-06, B6, B7 | MINOR | The `USB_STAT` ladder gives four levels (nominal 0.95 / 1.115 / 2.20 / 3.30 V). At the datasheet's worst `CHG` leakage (1 uA) the "USB in, charge off" level falls from 3.30 V to about 2.2-2.6 V and meets "on battery" (2.20 V); typical leakage (nA) leaves it above 3.2 V. "Charging" and "charging from a weak source" are 30 mV apart. Five pairs of states cannot be told apart from `USB_STAT` plus `P+` (section 5). | 3.3 V - 1 uA x 1 MOhm = 2.30 V before tolerances. | Firmware F11: split "on battery" from "USB in, charge off" at 2.45-2.6 V, set from the measured leakage, and cross-check with `P+`. Bench: USB in with a full cell should read 3.2 V or more. |
| 5 | D-1 | MINOR | `U11`'s IN pin has no capacitor at the pin. `C25` (1 uF) is 14.5 mm of trace and two vias away; `C2` (10 uF) is 2.3 mm away but sits behind `R84`'s 1 Ohm. TI asks for the IN capacitor close to the pin. The datasheet gives no ESR limit, and the same `C2`/`C25`/`R84` arrangement served the TP4056 on Rev 1.0. | Track length re-summed from the reported path: 14.4 mm. | Scope `U11` pin 6 on the first article (hot-plug with a 1 m cable, and at charge start; look for more than 6.5 V or sustained oscillation). If needed, add 0.1-1 uF across pins 6 and 5 (a GND via sits at (84.05, 97.50)). |
| 6 | B3, A-10, B4, A-05 | NOTE | Known limits, no regression. A pack whose own protection has tripped reads about 0 V and is never charged (same as Rev 1.0, documented). A cell pulled while charging leaves `P+` cycling 3.8-4.2 V (`BAT_MONIT` about 4.0 V) with the charger in its battery-detect loop, so firmware must read "`USB_STAT` 3.30 V and `P+` about 4.0 V" as "full or no cell". | The design's own claim C9 agrees. | Firmware wording only. |
| 7 | C-1, B9 | MINOR | The BSS138 fields (`Q2`, `Q5`, `Q6`, `Q9`) name onsemi's BSS138LT1G, but C7420339 is a clone (JLC: hongjiacheng; LCSC brand field "R+O"). Placement is unaffected. The threshold and leakage numbers come from the clone's sheet, which gives no leakage above 25 C. | LCSC JSON, JLC page and datasheet. | Optional: note "R+O" in `part_fields.csv`. |
| 8 | D-8, A-08, A-09, C-2, C-3 | NOTE | Wording: `TS` is 15.75 mm long (the changelog says about 14 mm). Worst-case `U11` dissipation on USB is 0.35 W (+46 to +70 K at 150-200 C/W), still below the 125 C regulation point. `C25`'s 1 uF is on the input net (STATUS section 14 means none was added at the pin). Three new Extended parts (C202311, C13564, C107083); LCSC holds 1,500 BQ21040. | | Docs wording. Confirm JLC stock at quote time. |

## 3. Checked and OK

- **Pinout and ratings.** Pins agree across datasheet, symbol, netlist and JLC's land. IN is rated 30 V with OVP at
  6.5-6.8 V against a 5 V source and the damped hot-plug; `OUT`, `TS`, `ISET` and `CHG` stay inside their 7 V limits.
  SLUSCE2C to D changes only the ESD ratings (A).
- **Charging.** 115 mA (104-127), regulation 4.16-4.23 V against a 4.20 +/- 0.05 V cell, termination 9.3-14 mA,
  pre-charge 19-28 mA, timers 30 min and 10 h against about 5-6 h for 500 mAh, the ISET short test not triggered (A).
- **TS and enable.** Every single fault leaves the charger off. A cold thermistor cannot reach the no-sensor mode
  (6.5 uA x 202 kOhm = 1.31 V, below 1.525 V). `C38`'s time constant (2.1-5.3 ms) is far under the 30 ms deglitch. `Q2`
  pulls `TS` down hard enough (3 Ohm against the 1.3 kOhm needed). `Q9` detects a cell at 0.88-1.76 V; a reversed cell
  disables the charger; there is no plug-in race (B).
- **JLC.** Footprints equal JLC's lands (`U11` and `Q2`/`Q9` rotated 180 deg, the 0603s at 0 deg). The placement rotations
  reproduce by replaying the Toolkit's code and by placing JLC's land by hand, and Rev 1.0's identical `Q9`/`Q2` rows work.
  Order-zip pad flashes sit at the committed positions (0.000 mm) and all 47 block vias are in the drill file. The mask web
  between `U11` pins is 0.30 mm. Codes, values and quantities agree across schematic, `part_fields.csv`, both BOMs and LCSC (C).
- **Layout.** DRC: 0 errors and no warning in the block; none of the custom rules apply. `TS` is B.Cu only, 0.2 mm wide,
  15.75 mm, no vias. Its tightest gaps are 0.150 mm (GND pour, acting as a guard) and 0.201 mm (`P+`, `USB_VBUS`).
  `TS` would need about 46 kOhm of leakage from `USB_VBUS` (29 kOhm for the no-sensor mode) to leave its window, against
  flux residue in the MOhm-GOhm range. `ISET` is short and shielded. `TS` no longer runs between `F1`'s pads (D).

## 4. First-article checks added by this audit

1. Unpowered: `U11` pin 5 to GND under 1 Ohm and pin 6 to `USB_VBUS` under 1 Ohm (a 180 deg placement error would put
   pins 2 and 3 there). With a cell attached, `TS` at `C38` pin 1 should read about 0.476 V at 25 C.
2. Charge current 105-125 mA in constant current; `USB_STAT` 1.11 V while charging; 3.2 V or more with a full cell and USB
   in (under 2.8 V means `CHG` leakage above about 0.4 uA).
3. `TS` window with hot air and freeze spray; thermocouples on `TH1` and the cell in a 30 C room and in the closed case.
4. Over-discharge-lockout revival (finding 3).
5. Scope `U11` pin 6 against pin 5 (finding 5).
6. Pull the cell while charging: `P+` cycles 3.8-4.2 V and `USB_STAT` reads 3.3 V.
7. Optional, long: 30 mA on `J6` pin 12 with a cell on USB for more than 10 h (finding 1).
8. Read `IO9` at about 1.0 V and 2.2 V against a meter and set the firmware thresholds from data.
9. In JLC's placement preview: `U11`'s pin-1 dot sits on the `TS` pad at (83.15, 93.45); `Q2`'s single drain lead points
   toward `TH1` and `C38`.

## 5. Firmware F11: proposed `USB_STAT` decode (Lens B)

`IO9` = ADC1 channel 8, calibrated millivolts at 12 dB attenuation, add about 50 mV for ADC error; wait at least 0.5 s
after a state change (`C23` time constants 29-100 ms). `P+` = 2 x `BAT_MONIT` (`R12`/`R10` 1M/1M, time constant 0.5 s).
Lens A would put the 3.30 / 2.20 split at about 2.45 V, Lens B at 2.60 V; both assume the datasheet's worst-case leakage,
so set it from the measured value.

| USB_STAT | State | Nominal / band | then `P+` | Meaning |
|---|---|---|---|---|
| under 0.70 V | fault | | | ladder open, `C23` short or 3V3 low |
| 0.70-1.04 V | D: weak USB (mux on the cell), `CHG` low | 0.954 / 0.911-1.026 | cell, CV | charging from a weak source (B/D split unreliable) |
| 1.04-1.45 V | B: USB good, `CHG` low | 1.115 / 1.056-1.196 | 3.0-4.23 V | first charge after plug-in or cell insertion, including a `TS` temperature pause and pre-charge |
| 1.45-1.85 V | invalid | | | re-read |
| 1.85-2.60 V | A: `ST` low, `CHG` off | 2.200 / 2.05-2.29 | cell | on battery, or weak USB with the charger asleep or stopped (indistinguishable) |
| 2.60 V or more, or saturated | C: USB good, `CHG` off | 3.30 / 3.07-3.40 | under 1.0 V | no cell, charger disabled by `Q2` (also `TS` shorted, `Q2` stuck on, with no cell) |
| | | | 3.95-4.25 V | full, or a top-up charge running (`CHG` stays off), or a cell pulled under USB |
| | | | 1.0-3.95 V | charge stopped: safety timer, or a `TS` fault during a top-up, or `TS` shorted, `C38` short or `Q2` stuck on with a cell present |

Cannot be told apart: (1) on battery against weak USB with the charger asleep; (2) full against a top-up charge against no
cell after removal under USB; (3) charging against a first charge paused for temperature; (4) a timer stop against a `TS`
stop during a top-up against a dead `TS` pin with a cell present; (5) B against D within ADC error. The firmware tree
(`silkscreen-firmware`) has no BQ21040 code yet.

## 6. What this audit could not settle on paper

- JLC's own placement preview (the final word on rotation) and JLC's own stock of C202311 on the order day.
- Everything in section 4: real `TH1` rise above ambient, real `CHG` leakage, the over-discharge revival, the input ringing.
- The `DW01A`'s charger-detect level (unnumbered in its sheet).
- Whether charging restarts after the 10 h timeout when a load keeps the cell below the recharge threshold (the datasheet is
  ambiguous), and the ESP32-S3 12 dB range (taken from memory by Lens B).
- This is a paper audit of the committed files. Rev 1.0's unchanged circuitry was treated as proven, not re-audited.
