# Lens D: BQ21040 block physical layout (committed board 7b7d2fb)

## 1. Verdict

The charger block's layout is sound. The board passes KiCad DRC with no violation or warning anywhere in the block, none of the custom rules apply here, and no switching node or noisy net comes within 1.5 mm of the temperature-sense (TS) or current-set (ISET) copper. Both of those nets are short, single-layer, masked, and fenced by the GND pour. Contamination would have to leak at about 30-50 kOhm (to 5 V) or about 13 kOhm (to GND) before TS left its window or went into no-sensor mode. Real flux residue sits in the megohm-to-gigohm range, so this is not a risk. No BLOCKER or MAJOR was found. Two MINOR points remain:
- U11's only real input bypass cap (C25) is about 14.5 mm of trace away.
- TH1 reads board temperature, not the cell. The charger's own heat makes it read about 1.5-3 K warm, which slightly narrows the margin at the cold end.

Counts: 0 BLOCKER, 0 MAJOR, 2 MINOR, 6 NOTE.

## 2. Findings

| ID | Sev | Claim | Evidence | How confirmed | Smallest fix | Conf. |
|---|---|---|---|---|---|---|
| D-1 | MINOR | U11 IN (pin 6) has no low-impedance ceramic at the pin. C25 (1 uF) is about 14.5 mm of trace and 2 vias away (B.Cu 0.3 mm, then F.Cu 0.25 mm x 7.7 mm, then B.Cu 0.4 mm). The only cap near the pin, C2 (2.3 mm), sits behind R84 1 Ohm, so it is a damper, not an HF bypass. This departs from TI SLUSCE2D section 11.1 (IN cap "as close as possible", short IN/GND runs) | `D-assets/place_out.txt` track walk: U11.6 (83.15,96.15) -> via (82.20,95.30) -> F.Cu (82.20,93.65), (83.25,92.60), (86.70,92.60) -> via (87.50,91.80) -> B.Cu (88.50,90.80), (88.50,89.14), (86.90,88.70) -> C25.2 (86.23,88.70). Estimated about 12-15 nH. C25.1 GND to U11.5 is about 7.5 mm through the pour | pcbnew track walk; `raw.py` shows C25/C2/R84 have the same pose and zone settings as in Rev 1.0, where they served the TP4056 (so the pattern was built, but for a different IC) | If a spot exists, add a 0.1-1 uF 0603 directly across U11.6/U11.5, near the GND via (84.05,97.50). Otherwise scope IN on the first article | med |
| D-2 | MINOR | TH1 senses board ambient beside the charger, not the cell. It is 7.13 mm from U11 on the same B.Cu side, joined by the GND pour (TH1.2 thermal relief; U11.5 relief plus via). It is 27.9 mm from the nearest corner of the cell bay (x 44.2-83.0, y 37-67.5) and 26.9 mm from J5. Estimated warm offset from U11 alone: +1.5-3 K (section 5), plus the LDO U3 at 16 mm and the ESP32 at 35 mm when awake. Hot end: conservative, cuts off at a cell temperature of about 38-40 C. Cold end: once charging starts, U11's heat can keep TH1 above 0 C while the cell is about 1.5-3 K below 0 C (the 0 C hysteresis of 100 mV is about 1.7 K) | `cross.py` and `place.py` poses; bay from head/docs/HARDWARE.md mechanical table; datasheet RthJA 130.8 C/W; P = (5 V - Vbat) x 0.115 A = 0.10-0.23 W | Geometry by pcbnew; heat by a fin model, sanity-checked against RthJA | Accept as a documented ambient sensor. Optionally, firmware refuses to start a charge below about 3-5 C board temperature. Bench check with a thermocouple | med |
| D-3 | NOTE | Leakage across the TS gaps cannot plausibly move TS (section 5). Worst gap between two exposed pads: U11.1 to U11.2 (P+) 0.30 mm (pin pitch). The 0.20 mm gaps are to mask-covered copper (VBUS track, P+ teardrop) | `D-assets/gaps_out.txt` | pcbnew polygon distance; widths and length re-read from raw text | none | high |
| D-4 | NOTE | TS runs under the U11 body between the pad rows (y 94.60, x 83.70-86.79), 0.27 mm from the P+ and CHRG pads, under mask. This does not matter electrically. Flux can stay trapped under the body, and U11 rework is fiddlier. Probe TS at C38.1 or TH1.1 instead | `gaps_out.txt` | pcbnew | none | high |
| D-5 | NOTE | C38 (TI's optional 0.22 uF, CTS spec p.6) is about 8.7 mm of trace from the TS pin, beside TH1, not at pin 1. Acceptable because the NTC is on board with no long lead to filter, and the trace is guarded by the pour | trunk lengths in section 3 | pcbnew + raw | optional: move toward pin 1 at the next spin | high |
| D-6 | NOTE | Tombstoning: C25.1 and C3.2 are solid to the pour (zone_connect 2) against 0.4 mm tracks on the other pad. This is identical to Rev 1.0, which was built. The new 0603s (TH1, C38, R82, R6) each have a thermal-relief GND pad (0.5 mm spoke, 0.5 mm gap) against a 0.2 mm trace, a mild and common asymmetry | `place_out.txt`; `raw.py` zone_connect fields, head vs before | two methods | none | high |
| D-7 | NOTE | Reference text on B.Silk is 0.5 mm tall for U11, TH1, C38, R82, R6 and Q2, which is small (JLC suggests 0.8-1.0 mm or more). Cosmetic only; the pin-1 marks are correct | `asm.py` | pcbnew | none | med |
| D-8 | NOTE | Design claim C14 checked. **True:** "TS no longer runs between F1's pads". TS copper stays at x <= 93.2; F1 pads are at x 94.41, y 93.25 and 95.30; no F1 pad is within 1.5 mm of TS. **True:** TH1 "about 7 mm" from U11 (7.13 mm). **Imprecise:** "TS about 14 mm long". It is 15.75 mm in total: 10.3 mm trunk U11 -> R82 -> C38 -> TH1 plus a 5.5 mm branch to Q2. **Consistent:** "1-3 C above the cell" matches my independent estimate, provided the cell sits at board ambient | `gaps_out.txt`, `raw.py` | pcbnew + raw text | none | high |

## 3. Checked and OK

| Item | Result |
|---|---|
| TS copper | B.Cu only, 9 segments, all 0.200 mm, 15.75 mm, 0 vias (pcbnew and raw text agree), plus teardrops. Path: U11.1 (83.15,93.45) -> under body y 94.60 -> R82.2 (88.40,92.99) -> C38.1 (90.34,92.60) -> TH1.1 (90.29,94.15); branch (88.40,92.99) -> (90.47,90.92) -> (92.15,90.92) -> Q2.3 (92.76,90.31) |
| TS: 5 tightest gaps | 1) GND pour 0.150 (all along; acts as a guard). 2) P+ 0.201 (TS teardrop at U11.1 to U11.2 pad). 3) USB_VBUS 0.201 (Q2.3 drain pad to masked 0.4 mm VBUS track (93.22,88.96)-(92.31,88.96)). 4) P+ 0.235 (U11.1 pad to P+ teardrop). 5) CHRG and P+ 0.270 (under-body TS track to U11.3/U11.2 pads). Next: VBUS via 0.615 (from R82.2), ISET 0.670, Q9-G via 0.859 |
| TS: noisy neighbours | No 3V3 or switching node (EINK_SW, TPS_SW_NODE, LED_SW) within 1.5 mm on B.Cu. On F.Cu in plan view, only UNUSED_GPIO_46 (0.44), USB_VBUS (0.53) and UNUSED_GPIO_45 (0.96), all static |
| ISET | B.Cu, 0.2 mm, 3.66 mm, 0 vias, GND pour at 0.15 mm on both sides. R6 is 3.7 mm of trace from pin 4; nearest signal is TS at 0.67 mm (masked); not exposed |
| Power-path widths | IN 0.25-0.4 mm, OUT 0.3-0.4 mm, 1 oz. About 2 mOhm/mm at 0.25 mm, so about 25-30 mOhm on the IN run, a 3-4 mV drop at 125 mA; ampacity is well over 0.5 A |
| OUT caps | C3.1 is 4.9 mm from U11.2 (0.3 mm track); C26.1 about 7.5 mm; returns about 8 mm through the pour to pin 5. Fine with the cell on P+ (datasheet: 1-10 uF) |
| GND pin 5 | Thermal relief to the B.Cu pour plus a 0.3 mm stub to the via at (84.05,97.50); pour contact confirmed (`asm.py`). The DBV package has no thermal pad (the datasheet's thermal-pad text is for MLP). Tj rise is about 0.23 W x 131 C/W, about 30 K, far below the 125 C regulation |
| TH1 self-heating | 50 uA^2 x 10 kOhm = 25 uW; with a dissipation constant of about 1 mW/K, about 0.03 K: negligible |
| Other heat sources vs TH1 | F1 3.2 mm (I^2R a few mW: negligible); CR1 6.3 mm (idle); U2 10.0 mm (small); U3 LDO 16.0 mm (0.1-0.5 W when awake on USB); L1 18.3 mm (only during refresh); ESP32 U4 34.7 mm |
| DRC | kicad-cli 9.0.6, --severity-all --schematic-parity: 0 errors, 55 warnings board-wide (31 silk_edge, 10 silk_over_copper, 6 starved_thermal, 3 silk_overlap, 1 mirrored text, 4 excluded track_dangling). None involve U11, TH1, Q2, C38, R82, R6, R81 or nets TS, ISET, CHRG, /DET_NODE. 0 unconnected, 0 parity (`D-assets/drc.json`). Nearest warnings are the cut-line silk at y about 62 and the J1 S1 starved thermal at (98.66,102.63) |
| Custom DRU rules | None of the 8 applies to the block: the SW and switch-node rules cover nets whose nearest copper is L1 at y > 109; the J1/J3/U10 rules are footprint-local; the LED-cathode and panel-rail pull-backs are elsewhere. The default 0.15 mm netclass governs (the pour's 0.1 mm local clearance is overridden upward) |
| U11 pads and mask | SOT-23-6 hand-solder pads 0.65 x 1.56 mm, gap 0.30 mm, mask expansion 0, so the mask web is 0.30 mm (more than JLC's about 0.1 mm). Q9 web 0.40 mm |
| Pin-1 marks | B.Silk triangle at (82.21-82.54, 93.36-93.84) beside U11 pin 1 (TS), 0.29 mm clear of the pad; Q2 triangle beside its pin 1, clear. No silk on block pads (no silk_over_copper here) |
| Courtyards | DRC courtyard checks are clean. TH1/C38 abut (0.0 mm). The small negative bounding-box gaps between Q2, R81, R80 and Q9 are box artefacts; the real polygons do not overlap |
| Test access | No test points on block nets, but every block pad is exposed on the B side. TS is probe-able at C38.1/TH1.1, IN at C25.2, OUT at C3.1, ISET at R6.1 |
| Unchanged Rev 1.0 parts | C2, C25, C3, C26, R6 (was PROG), R84: identical poses and zone settings (raw-text comparison against before/) |

## 4. Could not verify on paper

| Question | Measurement that settles it |
|---|---|
| IN stability and ringing with C25 14.5 mm away (D-1) | Scope U11.6 against U11.5 with a short ground spring. Hot-plug a 5 V source with a 1 m cable, and also watch at charge start. Look for more than 6.5 V overshoot or sustained oscillation |
| Real TH1-to-cell offset (D-2) | Thermocouple on the cell and on TH1 (or read V(TS) at C38.1) during a full charge in the closed case, with the ESP32 awake and asleep |
| Cold-end behaviour (D-2) | Cold-soak to about 0 C, start a charge, and log V(TS) and the cell temperature for 30 min |
| Flux residue under U11 (D-4) | Visual check after assembly. With a cell attached at 25 C, V(TS) should read about 0.476 V |

## 5. Derivations

### TS thresholds (SLUSCE2D, Electrical Characteristics p.5-6)

- I_NTC: 50 uA (48-53)
- Hot cut V_TS-45C: 0.275 V (0.26-0.29)
- Cold V_TS-0C: 1.25 V (1.22-1.28)
- No-sensor mode (TTDM): 1.60 V (1.55-1.65)
- Enable: 88 mV (80-96)

With R_T = NTC (B 3380) in parallel with 200 kOhm (R82):
- at 25 C, R_T = 9.52 kOhm and V_TS = 0.476 V
- near 41 C, R_T = 5.65 kOhm and V_TS = 0.282 V, which is at the hot cut

### Leakage needed to move TS

Leakage R_L from a source V_s, solved exactly with V = (I + V_s/R_L)(R_T || R_L):

| Leakage | Threshold reached | R_L needed |
|---|---|---|
| From USB_VBUS 5 V | cold pending (1.25 V), at 25 C | 46 kOhm |
| From USB_VBUS 5 V | TTDM (1.6 V), at 25 C | 29 kOhm |
| From USB_VBUS 5 V | TTDM (1.6 V), at 0 C (R_T 23.9 kOhm) | 200 kOhm |
| From P+ 4.2 V | cold pending | about 36 kOhm |
| To GND | hot cut, at 25 C | 13 kOhm |
| To GND | disable (below 88 mV) | about 2 kOhm |
| To GND | at the hot edge, moves the cut by 1 K | 207 kOhm |

Sensitivity at the hot edge: dV/dT is about 11 mV/K, so a 1 K error takes about 2 uA, which is 2.5 MOhm from 5 V.

How that compares with real contamination:
- No-clean flux must pass 100 MOhm or more in J-STD-004 SIR tests, on comb patterns with many squares.
- A 0.2-0.3 mm by about 1 mm gap has far fewer squares, so its resistance is higher still.
- Even a badly contaminated, humid board at 1-10 MOhm gives less than 0.3-2.5 K equivalent.
- All TS traces are under mask, so only pad-to-pad gaps count.

### TH1 offset (fin model)

- The 2-layer 1 oz GND pour acts as a sheet: k*t = 385 x 2 x 35 um = 0.027 W/K.
- With h of about 10 W/m2K per side, L = sqrt(kt/2h), about 37 mm.
- dT(r) = P/(2 pi k t) x K0(r/L). At r = 7.1 mm, K0 is about 1.8.
- That gives dT of about 1.5 K at 0.15 W (Vbat 3.7 V) and about 2.4 K at 0.23 W (Vbat 3.0 V).
- A closed case (lower h) raises the whole board, cell included. Gaps cut in the pour by tracks raise the local rise. Hence 1.5-3 K.

## 6. Raw log (appended as confirmed during the run)

### F-log 1 (TS node geometry, pcbnew, gaps.py -> D-assets/gaps_out.txt)
- TS copper: all B.Cu, 9 track segments of 0.200 mm, 15.75 mm total, 0 vias, plus teardrop zones.
- Tightest gaps to foreign nets: GND 0.150; P+ 0.201; USB_VBUS 0.201; P+ 0.235; CHRG/P+ 0.270; VBUS via 0.615; ISET 0.670; Q9-G 0.859.
- ISET: B.Cu only, 0.200 mm, 3.66 mm, GND on both sides at 0.150 mm.

### F-log 2 (DRC -> D-assets/drc.json)
- 0 errors in the block; custom rules not applicable.

### Scripts
All under `reports/D-assets/`: `gaps.py`, `place.py`, `asm.py`, `cross.py` (pcbnew), `raw.py` (raw-text second method).
