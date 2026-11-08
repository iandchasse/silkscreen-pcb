# Lens B: BQ21040 TS network, charge enable, status interface (Rev 1.03, 7b7d2fb)

Auditor: independent, read-only. Everything below was derived from the datasheets and the netlist before `claims.md` was opened, then compared with it (section 5).
Scripts: `reports/B-dl/ts_window.py` (TS window, faults, leakage, C38) and `reports/B-dl/stat_ladder.py` (USB_STAT bands). TPS2116 datasheet fetched to `reports/B-dl/tps2116/` (TI SLVSF..., `tps2116.txt`).

## 1. Verdict

No blocker and no major problem in this lens. The temperature sensor, its 200k fail-safe resistor and the cell-detect switch all behave as the design says. Every single-part failure on the TS pin ends with the charger off (cold fault or disabled), never with an unsupervised charge. Charging is guaranteed between about +2 C and +38 C at TH1 on every board, and runs nominally from -1 C to 41 C. The 45 C that TI prints is not reached even with TI's own NTC, so this is the IC's limit, not a design error. Because TH1 sits on the board 7 mm from the charger and 3 mm from F1, a warm room plus board self-heating could stop charging early on some boards. The status line gives four usable levels. On paper two pairs can overlap: "USB in, charge off" against "on battery", but only at the datasheet's worst CHG leakage, and "charging" against "charging from a weak source", where the gap is 30 mV. The decode table in section 2b works with realistic parts. The findings are minor: charging an over-discharged cell might stall on a low-threshold Q2; a self-protected pack in lockout can never be revived on this board; there is a cold-start case for the cell-removed latch; and some states cannot be told apart. All of them can be checked on the first boards.

## 2. Findings

| ID | Sev | Claim | Evidence | How confirmed | Smallest fix | Conf. |
|---|---|---|---|---|---|---|
| B1 | MINOR | The hot cutoff is guaranteed only down to **37.7 C** at TH1 (nominal 40.9 C, band 37.7-44.9 C). Resume is at 35.7-42.6 C. TH1 is a board sensor 7 mm from U11 (84.1, 94.8) and 3.2 mm from F1 (94.4, 94.3). At a 30-33 C ambient, a low-tolerance board can pause charging when it warms by 5 C. | SLUSCE2D p.6: VTS-45C 260/275/290 mV, hyst 20 mV, I_NTC 48/50/53 uA. Murata XH103 table: 40 C 5.834k, 45 C 4.917k. All 16 corners of R25 +-1 %, B +-1 %, R82 +-1 % and I_NTC. | Script, plus a hand check (0.275 V / 50 uA = 5.50k, so TH1 = 5.656k, so 40.9 C) | None needed if accepted. To recover about 2 C at the hot end, move TH1 away from U11 and F1, toward the cell. Do not change R82: it barely affects the hot end (-0.8 C). | high |
| B2 | MINOR | While an over-discharged cell is charged in **DW01A over-discharge lockout** (OD FET off), the charge current flows through Q1's body diode. That lifts B- about 0.6-0.75 V above GND, and Q9 passes B- to Q2's gate. The clone's Vth is 0.8 V min at 250 uA and falls about 3 mV/C. A low-Vth Q2 could then sink the 23 uA (25 C) to 46 uA needed to force a false hot fault or a disable. Charging would stall or cycle in the 2.4-3.0 V window. It is harmless with a typical part (1.2 V). | Netlist: Q9.S = B-, Q2.S = GND, Q1 S1 = B-, S2 via R85//R86 to GND. BSS138 clone p.2: Vth 0.8/1.2/1.6 V. HARDWARE.md l.372 confirms the over-discharged cell is charged through the body diode. ts_window.py: Q2 sink for TS < 0.26 V = 22.7 uA, for disable 45.9 uA. | One method only, with an estimated subthreshold slope. It depends on whether the DW01A releases OD on charger detection (CS = R16 to GND sits -0.7 V below VSS), which I could not verify here. | Bench: charge a cell held at 2.6 V in OD lockout and log B- to GND and TS. Fix if needed: source Q9 at GND instead of B- is wrong (it breaks the cell sense). Better: add 1 M from Q2 gate to GND, or use a higher-Vth part for Q2 (Vth min >= 1.0 V). | medium |
| B3 | MINOR | A **self-protected pack** whose own PCM is in lockout reads about 0 V at J5. Q9 sees < 0.9-1.76 V, Q2 holds TS low, and the board never applies the voltage that wakes the PCM, so the pack looks dead for good. A deeply discharged bare cell between 0.9 and 1.76 V may or may not be charged, depending on Q9's Vth. | Q9 Vgs = 0.909 (B+ - B-), Vth 0.8-1.6 V. The PCM's open P- floats up through the 5 Mohm-class loads (R79+R80 11M, R57 10M). | Topology + datasheet (the design states it on purpose, claim C5) | Document it for users ("revive in an external charger"). Same pattern as Rev 1.0. | high |
| B4 | MINOR | The no-cell disable only works when USB arrives with no cell **and** P+ already discharged. If a cell is pulled while charging, Q8 (G = GND, S = P+) and Q3 (S = B+, its body diode or channel) back-feed P+ into B+. Q9 then sees 0.91 x P+ (about 3.4-3.8 V) and stays on, so the charger keeps running its battery-detect loop. The same happens if USB is plugged in while P+ still holds above about 1.8 V just after a cell was removed (seconds in deep sleep; ms if the ESP32 runs from P+). | Netlist: Q8 1 = GND, 2 = P+, 3 = R27, then Q3.3; Q3.2 = B+ = R79.1. SLUSCE2D 8.4.8/8.4.9: the detect routine runs continuously without a battery. | Two paths agree: netlist topology, and the design's own claim C9 (they noted it independently). | Accept (benign, same as Rev 1.0). Firmware must read "USB_STAT = C and P+ about 4.0 V" as "full **or no cell**". | high |
| B5 | MINOR | USB_STAT, "USB in, CHG off" (state C): with the datasheet's ILEAK max of 1 uA into CHG, the band falls to 2.16 V and overlaps "on battery" (A, 2.05-2.29 V). With realistic leakage (< 0.1 uA) it is 3.07-3.40 V and clearly separate. C also sits above the ESP32-S3 12 dB range (about 2.9-3.1 V), so it reads as saturated. | SLUSCE2D p.6: CHG ILEAK 1 uA max at 5 V. stat_ladder.py over every corner (R +-1 %, 3V3 3.25-3.35 V, CHG/ST VOL, ST leak 0.03 uA [TPS2116 p.6], pin leak +-50 nA). | Script plus a hand check (1 uA x 1 Mohm = 1.0 V drop) | Firmware threshold A/C at 2.60 V, which tolerates CHG leakage up to about 0.55 uA. A cheaper hardware margin, if wanted: R70 to 470k (C min 2.78 V at 1 uA; adds about 2.4 uA when charging). | high |
| B6 | MINOR | "Charging" (B, 1.056-1.196 V) and "charging from a weak source, mux on the cell" (D, 0.911-1.026 V) are only 30 mV apart worst case, so a +-50 mV ADC cannot split them reliably. Both mean "charging", so the impact is cosmetic. | stat_ladder.py | Script | Split at 1.04 V and accept errors. Optionally read IO9 at 6 dB attenuation for this decision (better mV accuracy). | high |
| B7 | NOTE | Some states cannot be told apart by USB_STAT + P+ at all. See section 2b. | SLUSCE2D Table 1 (TEMP FAULT: CHG ON for the 1st charge), 8.3.6, 8.4.7 | Datasheet | Firmware wording only | high |
| B8 | NOTE | There is no firmware control of charge enable or timer reset. The 10 h fast-charge timer and a "stopped" state clear only on USB re-plug or cell re-insert (the TS low/release from Q2). | SLUSCE2D 8.4.7 (timer reset by disable/power cycle/TTDM) | Datasheet + netlist (Q2 gate only from Q9/R81) | Accept, or route a spare GPIO to Q2's gate through 100k in a later spin | high |
| B9 | NOTE | The BSS138 at C7420339: the LCSC JSON brand is "R+O" but its PDF is Zhuhai Hongjiacheng Rev 2.1. The specs used here come from that PDF. No leakage spec is given above 25 C. | extract/lcsc_C7420339.json, datasheet p.1-2 | Read both | Lens C / sourcing | high |

### 2b. Proposed USB_STAT decode (calibrated mV on IO9 = ADC1_CH8, 12 dB atten), then P+ = 2 x BAT_MONIT (R12/R10 1M/1M, tau 0.5 s with C8)

Nominal values and bands from stat_ladder.py (R +-1 %, 3V3 3.25-3.35 V, CHG leakage <= 0.1 uA realistic, ESP32 pin +-50 nA). Add about +-50 mV for ADC error. C23 time constants are 29-100 ms, so wait at least 0.5 s after a state change before trusting a reading.

| USB_STAT reading | State | Nominal / band | then P+ | Meaning |
|---|---|---|---|---|
| < 0.70 V | fault | | | ladder open / C23 short / 3V3 low |
| 0.70-1.04 V | D: weak USB (mux on cell), CHG low | 0.954 / 0.911-1.026 | cell + CV | charging from a weak source (B/D split unreliable, B6) |
| 1.04-1.45 V | B: USB good, CHG low | 1.115 / 1.056-1.196 | 3.0-4.23 V | first charge after plug-in or cell insertion, **including a TS temperature pause** and pre-charge |
| 1.45-1.85 V | invalid | | | re-read |
| 1.85-2.60 V | A: ST low, CHG off | 2.200 / 2.05-2.29 | cell | on battery; **or** weak USB with the charger asleep/stopped (indistinguishable) |
| >= 2.60 V or saturated | C: USB good, CHG off | 3.30 / 3.07-3.40 | < 1.0 V | no cell, charger disabled by Q2 (also TS shorted, Q2 stuck on, with no cell) |
| | | | 3.95-4.25 V | full, **or** top-up charge running (CHG stays off), **or** cell pulled under USB (B4, detect loop averages about 4.0 V) |
| | | | 1.0-3.95 V | charge stopped: safety timer (30 min pre / 10 h fast), or TS fault during a top-up, or TS shorted/C38 short/Q2 stuck on with a cell present |

Cannot be told apart: (1) on battery vs weak USB with the charger asleep; (2) full vs top-up charging vs no cell after removal under USB; (3) charging vs a first charge paused for temperature (CHG stays low by datasheet Table 1); (4) timer stop vs TS stop during a top-up vs a dead TS pin with a cell present; (5) B vs D within ADC error.

## 3. Checked and OK

| Item | Result |
|---|---|
| TS datasheet values (SLUSCE2D p.5-6, 7.6) | I_NTC 48/50/53 uA; I_DIS 27/30/34 uA at 0 V; fold-back 4/5/6.5 uA at 1.525 V (around 1.475 V); TTDM 1.55/1.60/1.65 V, hyst 100 mV; clamp 1.8-2.0 V; cold 1.22/1.25/1.28 V, hyst 100 mV; hot 260/275/290 mV, hyst 20 mV; enable 80/88/96 mV, disable 12 mV lower; tDGL(TS) 30 ms; CTS 0.22 uF "optional ESD" |
| Window at TH1 (all corners) | cold stop -3.3..+1.6 C (nom -1.1), cold resume -1.2..+3.8 C; hot stop 37.7..44.9 C (nom 40.9), hot resume 35.7..42.6 C. Guaranteed +1.6 to 37.7 C. TH1 alone would give +2.0 / 41.7 C; R82 costs 3 C cold and 0.8 C hot. |
| TTDM from a cold thermistor | Impossible: Rp <= 200k and 6.5 uA x 202k = 1.31 V < 1.525 V, so TS stays in the fold-back band (cold fault) at any temperature |
| TH1 open/missing | cold fault (TS about 1.43-1.52 V), not TTDM. Fail-safe. |
| TH1 short, R82 short, C38 short, Q2 stuck on | TS = 0, charger disabled. Fail-safe. |
| R82 open | normal; needs a second fault (TH1 open) to reach TTDM |
| C38 open | no DC change; loses ESD/noise filter only |
| C38 dynamics | tau 2.1 ms (25 C) to 5.3 ms (0 C); release passes the hot threshold within 2 ms, much less than the 30 ms deglitch; monotonic, no false cold/TTDM |
| Leakage into TS | needs <= 48k from 5 V at 25 C (<= 18k at 45 C) to fake cold, <= 31k for TTDM; 1-5 uA to GND moves the hot stop 0.6-3.1 C cooler; Q2 IDSS <= 0.5 uA (50 V, 25 C) |
| Q2 on strength | needs < 1.3k at 53 uA to get below 68 mV; has <= 3 ohm at Vgs 4.5 V; fine at 4 V weak USB |
| Q9 off/on | cell detect at 0.88-1.76 V; 2.5/3.0/3.7/4.2 V cells give Vgs 2.3-3.8 V; IGSS error <= 91 mV; references B-, so the DW01A state does not affect detection |
| B- vs GND, normal charging and discharging | +12 mV at 115 mA charge; negative on discharge, so Q2 Vgs <= 0.02 V and stays off (exception: B2) |
| DW01A overcharge (charge FET off) | B- cannot rise (P+ 4.2 V < cell OCV), so no wrong Q2 state |
| Reversed cell | Q9 off, charger disabled |
| Plug-in race | none: Q9 is set by the cell before USB_VBUS rises; with no cell, Q2 is on at USB_VBUS = 0.8-1.6 V, before the BQ21040 UVLO |
| TS low then release (datasheet 8.3.4, 8.3.6, 8.4.7) | counts as a new charge cycle: CHG goes low again ("first charge"), the fast timer resets, battery detect runs, normal power-up with the ISET/OUT short tests (flow chart p.11) |
| CHG behaviour (Table 1, 8.3.6) | low only on the first charge; off on top-up, sleep, OVP; stays ON during a temperature fault in the first charge; off after a timer timeout |
| USB absent: CHG high-Z | yes, SLUSCE2D 8.3.1 l.1277 "all the terminals are high impedance"; TI allows a pull-up to the host VCC (8.4.1) |
| TPS2116 ST | open drain, low when VIN2 is used or both are off; VOL 0.1 V at 1 mA; leakage 0.03 uA (TPS2116 7.3.3, p.6) |
| Mux switchover | VREF 0.92/1.0/1.08 V x 4 (R38/R51) = 3.68-4.32 V on USB_VBUS, so "weak USB about 4 V" sits right on the boundary |
| USB_STAT levels | A 2.200 V, B 1.115 V, C 3.300 V, D 0.954 V (nominal) with the bands in 2b; ladder draw 1.1 uA on battery |
| IO9 | ADC1_CH8, not a strapping pin; C23 makes the ESP32's sample charge negligible |

## 4. Could not verify on paper

| Question | Measurement |
|---|---|
| B2: does Q2 conduct while an over-discharged cell is charged through Q1's body diode, and does the DW01A release OD on charger detection? | Hold a cell at 2.6 V (or a supply plus a series 10 ohm) in OD lockout, plug in USB, log B- to GND, TS and the charge current at 25 C and 45 C |
| B1: real TH1 rise above ambient while charging, and in the enclosure | Thermocouple at TH1 and at the cell, charging at 115 mA in a 30 C room; note the TS voltage when charging pauses |
| B5: real CHG off-state leakage | USB in, full cell: USB_STAT should read >= 3.2 V; anything under 2.8 V means leakage > 0.4 uA |
| ESP32-S3 ADC accuracy near 1.0 V and 2.2 V on these boards | Read IO9 in the B/D states against a DMM; set the 1.04 V split from data |
| B4 latch | Pull the cell while charging: expect P+ to cycle 3.8-4.2 V and USB_STAT = C; confirm firmware wording |
| ESP32-S3 12 dB range and calibrated error (taken from the Espressif datasheet from memory as about 0-2.9 V, +-50 mV; the IDF page fetched did not list it) | Bench read of a known 2.2 V and 3.3 V |

## 5. Comparison with claims.md (read after the derivation)

| Claim | My result |
|---|---|
| C3 window 0-41 C typ, -2..+2 cold, 38..44 hot, resume about 2 C inside | **Agrees** on nominal (-1.1 / 40.9 C) and on resume (+2.2 / -2.1 C). My bands are slightly wider (-3.3..+1.6, 37.7..44.9) because I also vary B +-1 % and the hysteresis. |
| C4 R82 fail-safe, 7.6 uA vs 4-6.5 uA, about 3 C cold cost | Agrees exactly |
| C5 TS < about 76 mV disables; Q2/Q9 hold TS low until a correct cell; a pack in lockout reads 0 V and is not charged | Agrees; the consequence (pack never revived) is B3. Not covered: the B- elevation in on-board OD lockout (B2). |
| C6 CHG first-charge only, stays low during a temperature pause | Agrees (Table 1, 8.3.6) |
| C7 levels 2.20 / 1.11 / 0.95 / 3.30 V and the P+ split | Agrees on nominals. Additions: worst-case bands, A/C overlap at the datasheet's max leakage (B5), the 30 mV B/D gap (B6), and "P+ >= 4.0 V" also covers top-up and no cell after removal (B4/B7). |
| C8 pins high-Z with USB absent | Agrees (8.3.1) |
| C9 cell pulled under USB keeps the detector released | Agrees (found independently as B4); added the plug-in-while-P+-still-charged case |
| C14 TH1 7 mm from U11, C38 0.22 uF | Agrees; the hot-margin consequence is B1 |
| C16 all BSS138 = C7420339 clone | Agrees; brand field mismatch is B9 |
