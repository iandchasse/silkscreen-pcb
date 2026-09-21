# Corpus A — `DESIGN_REVIEW.md` (2026-09-17/18) vs the blind audit of 2026-09-19

Comparison written 2026-09-20 against the 2026-09-19 blind audit (297 findings, 13 sections) and
against ground truth generated from the KiCad files at commit `c0eccde`
(`docs/final-review-2026-09-19/evidence/`). Nothing in the repository was modified.

---

## 1. Summary

`DESIGN_REVIEW.md` is a *circuit-and-sourcing* review: it reasons hard about the battery fault path,
the LDO's thermal budget, charge-pump switching, the front-light driver, ADC ladders and exact vendor
pinouts, and it carries an applied-fix ledger. The 2026-09-19 blind audit is a *whole-deliverable*
review: it adds fabrication output, mechanics/enclosure, silkscreen, documentation and BOM-availability
coverage that the prior corpus never attempted.

The overlap is large and mostly agreeing. Of the **80** distinct prior items I could isolate (A-01…A-80
below), **44 map onto one or more new findings (SAME), 20 are PARTIAL, 7 rows are genuine CONFLICTs
(6 adjudications, C1–C6) and 7 are NOT-IN-NEW-AUDIT.** Thirteen of the SAME/PARTIAL rows are also
prior fix claims, verified applied in §2.
Encouragingly, the prior corpus already knew about **two of the new audit's three most serious
electrical/safety findings** — raw `P+` on `J6` (HMI-01) was described in §10, and D3's inadequate clamp
(BOM-10/HMI-16/LED-V01) in §8 — so those are confirmations, not surprises.

The prior corpus's **applied-fix ledger holds up completely**: all twelve applied/accepted changes
(Fix 4 CE gate, Q4→IRLML6346, R37→15 Ω, L1→47 µH, R14→2.2 Ω, C9→4.7 µF, L2→10 µH, CR1→SMF6.5CA,
D2→C28310439, R27→0805, J7 1.50 mm slots, U13 fitted / SW6 DNP) are present in the design at `c0eccde`
and netlist-verified here. None of the new audit's findings contradicts a fix claim; three of them
(USB-V05, BAT-V03, EPD-V02) are *metadata residue* left behind by those fixes, which is exactly the
class of defect §12 of the prior review predicted would remain.

The new audit's only BLOCKER — **LED-01, missing solder-paste apertures on the FH34SRJ signal pads of
J2/J3/J4** — is **completely absent from the prior corpus**. `DESIGN_REVIEW.md` contains the string
"paste" zero times. It is not a gap the prior review could have closed by accident either: §2 explicitly
scoped the Gerber check as "resolves apertures, drawing primitives, regions and polarity; **it is not a
complete factory CAM/DFM check**", and §11 records that KiCad's footprint-library and solder-mask-bridge
checks are switched off. The prior review named the blind spot and then did not look into it.

Five items the new audit did not reach are recovered below as **REC-A-01 … REC-A-05**; two of them
(no VBUS-sense input, and Fix 4's inability to start a 0 V pack) are MEDIUM and deserve a line in the
final report. A sixth candidate — the prior's "charger VCC has no local input bypass, ≈9.16 mm to C2" —
was checked and **dropped**: on the current board that distance is **2.08 mm**, so the prior's own figure
is the stale one. That is the general shape of this comparison: where old and new disagree on a
measurement, the current design usually settles it against the older document.

---

## 2. Verified state of the prior corpus's applied fixes

Read from `evidence/blocks/*.md` (netlist + footprint fields at `c0eccde`).

| Prior claim | Present truth at `c0eccde` | Holds |
|---|---|---|
| Fix 4 applied: CE gated by B−-referenced detector (Q9, Q2, R79–R82); CE→USB_VBUS tie removed | `Q9` = BSS138/C7420339 present; `R79`=100k, `R80`/`R81`/`R82`=1M present; net `CE` has exactly **3 nodes** — `Q2.3`, `R82.2`, `U11.8`. No USB_VBUS node on CE. | **Yes** |
| Q4 = Infineon IRLML6346TRPBF / C67276 | `Q4 value=IRLML6346TRPBF MPN=IRLML6346TRPBF Mfr=Infineon LCSC=C67276` (symbol lib still `Transistor_FET:BSS138`) | **Yes** (see EPD-V02) |
| R37 = 15 Ω | `R37 value=15 MPN=RC0603FR-0715RL LCSC=C22810` | **Yes** |
| L1 = 47 µH on a 5×5 footprint | `L1 value=47uH fp=Inductor_SMD:L_APV_ANR5040` | **Yes** |
| R14 = 2.2 Ω | `R14 value=2.2` | **Yes** |
| C9 = 4.7 µF/50 V | `C9 value=4.7u/50V MPN=CL21A475KBQNNNE LCSC=C513770` | **Yes** |
| L2 = 10 µH TDK VLS252012HBX-100M-1 | `L2 value=10u MPN=VLS252012HBX-100M-1 LCSC=C88532` | **Yes** |
| CR1 = SMF6.5CA in SOD-123FL (`D_SMF`) | `CR1 value=SMF6.5CA MPN=SMF6.5CA Mfr=Littelfuse LCSC=C19077501 fp=Diode_SMD:D_SMF` — **but symbol lib is still `TSD05CDYFR:TSD05CDYFR`** | **Yes**, with metadata residue (= USB-V05) |
| D2 = C28310439, normal-emitting 1206 | `D2 LCSC=C28310439` (MPN field carries the Lite-On prime `LTST-C150KRKT`) | **Yes** |
| Battery path widened; R27 moved to 0805 | `R27 value=0 fp=R_0805_2012Metric` | **Yes** |
| J7 NPTH slots 1.50 mm tall | consistent with new SD-07 ("slot 0.05 mm wider than the TF PUSH peg hole, at the minimum routed-slot width") | **Yes** — but see conflict C6 |
| U13 fitted, SW6 DNP, R72/R74 DNP | `U13 DS3231MZ flags=-`; `SW6 flags=dnp`; `R72 value=10k flags=dnp`, `R74 value=0 flags=dnp` | **Yes** — but R72/R74 lack `exclude_from_bom` (= HMI-V01) |
| Q1 manufacturer corrected to EVVOSEMI | `Q1 MPN=FS8205A Mfr=EVVOSEMI LCSC=C2830320` — the code delivers TECH PUBLIC | **Partly** (see conflict C2) |

---

## 3. Mapping table — prior corpus item by item

Relation key: **SAME** (new audit covers the same fact), **PARTIAL** (new covers an aspect or a
different slice), **NOT-IN-NEW**, **CONFLICT** (incompatible facts/conclusions), **FIXED** (prior
claimed applied, verified above).

| # | Prior item (section) | Prior status | Rel. | New IDs | Current truth |
|---|---|---|---|---|---|
| A-01 | Battery reverse-insertion fault path; Fix 4 CE gate (§1, §4) | APPLIED, bench-verify pending | FIXED + SAME | BAT-03, BAT-04, BAT-V01, BAT-13, PWR-V02 | Fix 4 netlist-confirmed. New audit re-derives the residual cases (BAT-04 = R82 is the only default-off pull; BAT-V01 = detector self-latches once charging). No contradiction. |
| A-02 | Q4 BSS138 outside panel spec → IRLML6346 (§1, §7) | APPLIED | FIXED + PARTIAL | EPD-03, EPD-V02, BOM-03 | Applied. New raises different aspects: 20.9 V on a 30 V part with no snubber, and stale symbol metadata. |
| A-03 | J7 peg fit / cancelled order (§1, §6) | APPLIED | FIXED + CONFLICT | SD-07, SD-04, SD-08, SD-05, MEC-15, SD-V01 | Slots present. New audit says the *fix itself* sits at fab minimums (C6). |
| A-04 | D2 reverse-mount → C28310439 (§1, §3) | ACCEPTED | FIXED + SAME | BAT-12, DOCS-24, MEC-09 | Applied. New finds the schematic note and README polarity rule still wrong. |
| A-05 | R37 13.3 Ω → 15 Ω (§1, §8) | APPLIED | FIXED + SAME | LED-07, LED-V03 | Applied. LED-07: three different currents still stated in three places. |
| A-06 | U3 500 mA shared budget + thermal scenarios (§1, §3) | OPEN — first-article measurement | SAME | PWR-01, PWR-02, PWR-15 | PWR-01 puts the practical continuous limit at 240–280 mA on USB; consistent with the prior's 250–350 mA "deserves measurement" band. |
| A-07 | No USB-PD/BC1.2; 656 mA illustrative overlap on a 500 mA port | OPEN, accepted | PARTIAL | PWR-02, USB-05 | PWR-02 gives a measured-basis ~515 mA overlap. Same conclusion, better number. |
| A-08 | **Self-powered USB needs VBUS monitoring; no VBUS-sense GPIO** (§3) | ACCEPTED as firmware responsibility | **NOT-IN-NEW** | — | Still true: net `USB_VBUS` has 8 nodes (C2, C25, D2, F1, R38, U2.3, U2.5, U11.4) — no divider to any GPIO. → **REC-A-01** |
| A-09 | F1 1 A hold derates to 0.65 A @ 60 °C (§3) | OPEN | SAME | USB-05, USB-V03 | Same. USB-V03 adds that F1's MPN and LCSC name different makers. |
| A-10 | VBUS hot-plug ringing 6–7.4 V vs TPS2116's 6 V abs-max (§3) | Accepted residual risk; §13 scope check | PARTIAL | USB-V01, BOM-04, USB-16 | New audit covers the DC margin (USB-V01) and the cap rating (BOM-04); the *transient* L-C ring survives only as a documentation-attribution finding (USB-16). |
| A-11 | CR1 SD05C 5.0 V standoff → SMF6.5CA (§3, §12) | APPLIED | FIXED + PARTIAL | USB-04, USB-V05, USB-09 | Applied. USB-04 is the *clamp* voltage, which §3 also flagged ("its surge-clamp specification does not guarantee a 6 V abs-max IC survives"). USB-V05 is residue of the swap. |
| A-12 | TP4056 ICHG ≈ 234 mA at R6=4.7 k; "255 mA" unsupported (§3) | OPEN | CONFLICT (minor) | LAY-V02 | New audit asserts "about 255 mA". Prior's arithmetic is better sourced (C4). |
| A-13 | TEMP grounded, no cell-temperature protection (§3) | OPEN, accepted | SAME | BAT-05 | Same. |
| A-14 | D2 indicates USB power, not charging; ~1.3–1.6 mA (§3) | Documented | SAME | BAT-12 | Same. |
| A-15 | Mux MODE tied to VBUS; R38/R51 → 3.625–4.385 V threshold band (§3) | OPEN | PARTIAL | USB-03, PWR-06 | USB-03 adds "PR1 has no hysteresis → switchover chatter"; PWR-06 adds the missing VBUS bleeder. Prior did not raise either. |
| A-16 | C4/C6 CCTC 22 µF effective capacitance unestablished (§3) | OPEN | PARTIAL | BOM-02, BOM-15 | New audit's concern is availability, not bias derating. Both true. |
| A-17 | Fix 4 idle drain ≈10 µA (corrected from 3.4 µA) (§4) | Documented | SAME | PWR-03 | PWR-03's ~73 µA deep-sleep budget includes it. |
| A-18 | **Fix 4 cannot start with a 0 V / protection-latched pack** (§4) | Known, accepted, "not pursued" | **NOT-IN-NEW** | — | Still true by construction of the detector. → **REC-A-02** |
| A-19 | FS8205A vendor package identity (Fortune is TSSOP-8 only) (§4) | RESOLVED 2026-09-18 → EVVOSEMI | CONFLICT | BAT-V03 | Q1's field is EVVOSEMI; the code C2830320 is TECH PUBLIC. U5's field was never touched (C2). |
| A-20 | DW01A senses P+ after two PMOSs; reference 100 Ω VCC filter absent (§4) | OPEN | SAME | BAT-02, BAT-10, BAT-01 | Same, and BAT-10 quantifies the ~0.4 V cold-start error. |
| A-21 | R56+R57 draw 4.16 µA across the cell after cutoff (§4) | Documented | PARTIAL | BAT-15 | BAT-15 says HARDWARE.md understates the residual (~4 µA quoted vs ~8 µA of resistors). Consistent. |
| A-22 | J5 pin 1 = B−, pin 2 = B+; connector style ≠ cable polarity (§4) | OPEN warning | SAME | BAT-V04, BAT-11, MEC-04 | New audit escalates it to a concrete mismatch against SparkFun's JST-PH convention. |
| A-23 | R27 0 Ω has finite ratings; battery path widened to 0.4 mm (§4, §11) | APPLIED (0805) | FIXED + SAME | BAT-07, PWR-V01, LAY-10 | Applied. New audit finds the residual 0.25 mm necks around R27 that the widening missed. |
| A-24 | 2.5 V DW01A cutoff is last-resort; firmware must stop earlier (§4) | Documented | PARTIAL | PWR-04, BAT-06 | PWR-04 is sharper: 3V3 drops below the ESP32's 3.0 V minimum at ~3.2–3.3 V of cell, before the cutoff. |
| A-25 | SW6 (BOOT) unselected / DNP (§5, §12) | Policy decision | SAME | MCU-01, MEC-13 | Same; new audit rates it MEDIUM because USB-Serial/JTAG is the only remaining route. |
| A-26 | GPIO3/45/46 on J6 are boot straps (§5, §10) | OPEN warning | SAME | HMI-02, MCU-04, HMI-V04 | Same. |
| A-27 | **"GPIO46 is input-only"** (§5) | Stated as fact | **CONFLICT** | MCU-19 | Prior is **wrong** (C1). |
| A-28 | GPIO39–42 overlap JTAG (§5) | OPEN warning | SAME | MCU-07, LED-V04 | Same; LED-V04 adds that JTAG and a working front light are mutually exclusive. |
| A-29 | C22 is 51.84 mm from the module pad, not MCU-local (§5, §12) | Documentation correction | PARTIAL | MCU-16, PWR-09, PWR-14 | New audit phrases it as "the 0.1 µF is farther from the supply pin than the 22 µF bulk". Same geometry, complementary framing. |
| A-30 | Q7 SD-VDD gate has no slow-down; µs turn-on into ~1.1 µF (§6) | OPEN, optional fix offered | **NOT-IN-NEW** (turn-on ramp) | SD-11, MCU-06, SD-15 partially | New audit covers the 60 µs power-up glitch and the small bulk, not the VDD *ramp rate* vs the SD spec. → **REC-A-04** |
| A-31 | Pull-ups return to switched SD_VDD → back-power path (§6) | OPEN, firmware rule | SAME | SD-01, PWR-08 (refuted) | SD-01 quantifies it at 3.24 V. New audit *refuted* the stronger light-sleep claim (PWR-08); prior never made that claim. |
| A-32 | R77 + C36/C37 → 0.11 s no-card discharge (§6) | Documented | SAME | SD-10 | Same (new gives ~0.4 s for a clean cycle). |
| A-33 | No independent firmware card-detect (§6) | Documented | SAME | SD-06 | Same. |
| A-34 | GCT keepout contains vias/traces (matters only for a hand-fitted MEM2075) (§6) | Accepted | SAME | SD-08 | SD-08 adds that the keepout is drawn on F.SilkS so it enforces nothing. |
| A-35 | "DAT0/DAT1 are protected by U9 — they are not missing ESD protection" (§6) | Closed | PARTIAL (not a conflict) | SD-13, SD-02 | New audit agrees the netlist is correct; SD-13 is about the *schematic sheet* being misleading. |
| A-36 | J2 pin 5 is VSH2, not VGH (§7) | Documentation correction | NOT-IN-NEW (benign) | — | Correction stands; no new finding disputes it. Not recovered (no defect). |
| A-37 | EPD_CS has no pull-up (§7) | OPEN, firmware rule | SAME | EPD-06 | Same, and new adds EPD_BUSY. |
| A-38 | R15 = 10 k vs reference 1 M (§7) | OPEN, deliberate | SAME | EPD-05, BOM-12 | Same; still 10 k at `c0eccde`. |
| A-39 | L1 22→47 µH, footprint change, neighbours moved (§7, §12) | APPLIED | FIXED + CONFLICT | BOM-14 | Applied. BOM-14 disputes the "no asymmetry between builds" claim (C5). |
| A-40 | R14 3→2.2 Ω; 0.1 W ↔ 183 mA RMS, pulse rating unverified (§7) | APPLIED, not bench-verified | FIXED + SAME | BOM-11, BOM-01 | BOM-11 is the same wattage question. BOM-01 (12 pieces in JLC stock) is **new**. |
| A-41 | GDR/RESE run ≈18 mm side by side at 0.15 mm; EPD loop grew to ≈33 mm² (§7) | Documented, §13 scope check | CONFLICT | LAY-D2, EPD-13 | New audit's shoelace gives 24–27 mm² (C3). |
| A-42 | FT01C vs FL01C front-light pin conflict; owner's sample matches the board (§8) | OPEN warning, owner-accepted | SAME | LED-12 | LED-12 is the same item, phrased as "unverified from any primary source". |
| A-43 | ADIM needs a >40 µs first pulse; 10–25 kHz note cannot enable (§8) | Documented | SAME | LED-14 | Same. |
| A-44 | OVP latches after three events; shutdown does not isolate VOUT from VIN (§8) | Documented | SAME | LED-V02, LED-02 | Same, and LED-02 extends it to external low-Vf strings on J6. |
| A-45 | C9 1→4.7 µF; effective ≈1.0–1.8 µF at 24 V, "only narrowly" above TI's minimum (§8) | APPLIED | FIXED + SAME | LED-05 | Applied; LED-05 reaches the same conclusion independently. Agreement. |
| A-46 | **U10's current limit exceeds L2's rating; C9 hot-plug ring ≈2.5 A** (§8) | OPEN, §13 check | **NOT-IN-NEW** | LED-03/LED-V05 dispute what a J6 short destroys, not the limit-vs-Isat margin | → **REC-A-03** |
| A-47 | D3 SMAJ26A ~42.1 V clamp does not protect U10's abs-max (§8) | OPEN | SAME | BOM-10, HMI-16, LED-V01 | **Prior already knew this.** New audit rates it LOW three ways. |
| A-48 | LED_MONIT 0.107 ratio, 10.7 ms RC (§9) | Documented | PARTIAL | LED-06 | LED-06 adds the 107 kΩ source impedance vs the SAR's recommendation. |
| A-49 | USB_STAT ladder: 0.531/0.595 V too close; degraded states merge (§9) | OPEN, firmware rule | SAME | USB-02, USB-18, USB-19, USB-V02 | Same. USB-V02 sharpens it: two states are identical *by construction*. |
| A-50 | ">3.10 V idle" requirement can misclassify; ADC saturates (§9, §12) | OPEN, annotation to fix | SAME | USB-01, USB-14, HMI-15 | Same, and USB-14 finds the schematic still declares it. |
| A-51 | Unpowered TP4056 status-pin leakage is unbounded (§9) | OPEN, unverifiable | SAME | PWR-18 | Same, also marked unverifiable. |
| A-52 | C23 = 2.2 nF → 132 µs RC (§9) | Documented | SAME | USB-20 | USB-20 adds that Espressif specifies ADC accuracy with 100 nF. |
| A-53 | Ladder chords alias: SW3+SW9 vs SW3, SW4+SW7 vs SW4 (§9) | Quantified 2026-09-18 | SAME | HMI-05 | Same numbers. |
| A-54 | Only SW1/SW2 give a valid logic low for GPIO wake (§9) | Quantified 2026-09-18 | SAME | HMI-06 | Same. |
| A-55 | R73+R74 both fitted shorts the rails; preserve DNP policy (§9, §12) | Documented | SAME | HMI-07, HMI-V01 | Same; HMI-V01 adds that R72/R74 lack `exclude_from_bom` — **verified true** at `c0eccde`. |
| A-56 | Bottom-switch anchors 12/13/12 mm; **"no remaining asymmetric placement defect"**; TS365ZJ pitch agrees (§9) | Closed | CONFLICT | HMI-10, MEC-08, MEC-11, HMI-13, HMI-14, LAY-07, HMI-V03, HMI-17, BOM-13 | The board now carries **MJTP1117 (APEM/C557598)**, not TS365ZJ — the prior check is stale (C6b). |
| A-57 | Touch link resistors are mutually exclusive, not spare jumpers (§10) | Documented | PARTIAL | HMI-20 (refuted) | New audit tried to find a defect in the alternate-pinout silk recipe and refuted its own claim. Prior's rule stands. |
| A-58 | GPIO41 (TP_INT) is not RTC-capable → no deep-sleep touch wake (§10) | OPEN | SAME | MCU-05 | Same. |
| A-59 | No discrete TP_INT pull-up; controller-dependent (§10) | OPEN, conditional | PARTIAL | HMI-12 | HMI-12 covers J4 pin 2's missing clamp/decoupling, not the pull-up question. Minor; not recovered (conditional on an unknown module). |
| A-60 | I²C 2.2 kΩ pull-ups: 1.32 mA sink, ~161 pF budget (§10) | OPEN, measure at 400 kHz | PARTIAL | MCU-09, LAY-C2 | New audit gives the trace lengths (184/179 mm) that consume that budget. Complementary. |
| A-61 | DS3231MZ: VCC-grounded VBAT mode is manufacturer-supported; no backup, no INT wake, ±5 ppm (§10) | Closed / documented | SAME | MCU-02 (refuted), PWR-12 (refuted), HMI-03, HMI-04, MCU-03 | **Prior is vindicated**: the new audit raised and then refuted the topology concern, and its HMI-03/HMI-04/MCU-03 repeat the prior's own caveats. |
| A-62 | J6 carries LED_SW, switched cathodes and **P+** beside logic; external injection can back-power (§10) | OPEN warning | SAME | **HMI-01 (HIGH)**, LED-03, HMI-V04, LED-V05 | **Prior already knew.** New audit's contribution is the concrete recommendation (0.5–1 A PPTC in series with J6.12). |
| A-63 | Exact vendor pinouts closed: TPD4E1U06, 74LVC1G04GV, PESD2IVN-UX (§10) | Closed | PARTIAL | BOM-06, HMI-11, BOM-V01 | Pinouts stand. New audit's concerns are lifecycle (D8 NFND at DigiKey), symbol shape and cost — not pinout. |
| A-64 | TPD arrays are 5.5 V standoff, not precision 3.3 V limiters (§10) | Documented | SAME | USB-V01, HMI-08 | Same. |
| A-65 | USB D+/D− skew 0.657 mm — "not a compelling failure argument" (§11) | Closed | SAME | USB-12, LAY-C4 | New audit agrees: CERT-LATER, not a defect. |
| A-66 | ESD routes stub ~8 mm toward U6 instead of flow-through (§11) | OPEN | SAME | USB-07 | Same (new measures 9.6 mm). |
| A-67 | Ground gaps interrupt the opposite-layer reference under D+/D− (§11) | OPEN | SAME | LAY-05, LAY-C5, SD-V02 | Same, generalised across the board. |
| A-68 | **No USB series-damping footprints (Espressif checklist)** (§11) | OPEN | **NOT-IN-NEW** | — | Still absent. → **REC-A-06** (CERT-LATER) |
| A-69 | U3, U2, Q1, R37 have one effective thermal spoke; 48 GND vias (§11) | OPEN | SAME | LAY-06, PWR-05, FAB-06, LED-10, SD-V04, LAY-11, LAY-V01 | Same class, far more instances found (25 starved thermals, 14 island fills). Via count is now 68 — design changed. |
| A-70 | Charger VCC–C2+ ≈9.16 mm; a closer input bypass is a next-revision improvement (§11) | OPEN, deferred | NOT-IN-NEW — **but silently resolved** | — | **Not recovered.** `C2.1` is at (81.100, 95.4625) and `U11.4` (VCC) at (82.795, 96.675) → **2.08 mm**. The prior's 9.16 mm is stale; C2 or U11 moved in a later revision and nobody recorded it. The charger now has a proper local input bypass. |
| A-71 | 0.25/0.20 mm trace widths "not automatically inadequate" (§11) | Closed with caveat | PARTIAL | USB-06, PWR-10, PWR-11, MCU-17, LAY-08, LAY-10 | Not a conflict — the new audit rates all of them LOW/MEDIUM and reaches the same "measure it" conclusion, but it *counts* the cost (125.5 mΩ to the boost, ~40 mV at peak). |
| A-72 | Antenna cutout exists; check housing/metal in the final stack (§11) | Closed, deferred | PARTIAL | MCU-14, MCU-15, MCU-21, LAY-C6 | New audit did the deferred check: metal/copper within ~1 mm on both flanks, no stitching vias. This is the prior's open item closed with a bad answer. |
| A-73 | H1–H5 connect to GND; metal standoffs make chassis connections (§11) | OPEN, deferred | PARTIAL | **LAY-03**, LAY-17, MEC-20 | New audit found the specific hazard the prior only gestured at: a screw head at H1/H5 can bridge the LiPo rail to the GND annulus. |
| A-74 | MJTP models vs ordered part need drawing-based fit checks (§11) | OPEN, deferred | SAME | MEC-11, BOM-13, HMI-17, MEC-07, MEC-08 | New audit did the deferred check. |
| A-75 | DRC 87 entries (14 clearance / 24 thermal / 49 silk) are cosmetic, not the release hold (§11) | Closed | SAME + PARTIAL | FAB-04, LAY-16, USB-10, LED-08, FAB-09, LAY-12 | New audit agrees the clearance entries are netclass noise. It disagrees that the silk entries are cosmetic (FAB-02, LAY-04). |
| A-76 | **Footprint-library and mask-bridge DRC checks are switched off** (§11) | Named as a limit | SAME | FAB-03, FAB-12, FAB-02, FAB-20 | The prior named the blind spot; the new audit looked into it and found four real items. |
| A-77 | Substitute metadata: symbols/links describe TI, onsemi or unrelated MOSFETs (§12) | OPEN, class-level | SAME | BAT-V03, EPD-V02, USB-V05, SD-12, HMI-17, LED-09, HMI-11, FAB-12 | **Prior flagged the whole class.** New audit enumerated the instances. |
| A-78 | Assembly counts: 179 refs = 162 fitted + 10 DNP + 7 bare-copper (§12) | Documented | PARTIAL | FAB-17, FAB-11, FAB-19, DOCS-03 | Counts still coherent; the new audit's concern is that the *exported* BOM/CPL files disagree with each other. |
| A-79 | "Pricing/sourcing tables under `fabrication` are historical, not the release BOM" (§12) | Warning | PARTIAL | DOCS-03, BOM-05, FAB-10, FAB-22 | The prior warned; the new audit shows the duplicate-LCSC bug is live in `production/bom.csv`. |
| A-80 | Unpowered review: no thermal, switching, EMC/ESD, reliability or enclosure work (§14) | Stated limit | — | (the whole MEC-*, FAB-*, DOCS-*, LAY-C* families) | The new audit's added value lives almost entirely inside this declared limit. |

---

## 4. Conflicts and adjudications

### C1 — GPIO46 is *not* input-only
- **Prior (§5):** "GPIO46 is input-only."
- **New (MCU-19, DOC):** documentation says so three times; on the ESP32-S3 it is a full bidirectional I/O.
- **Adjudication: the new audit is right.** The ESP32-S3 has no input-only GPIOs at all — that restriction
  belongs to the original ESP32 (GPIO34–39). GPIO46 on the S3 is a normal bidirectional pad; it is a
  strapping pin (ROM message printing) with an internal pull-down, which is the real constraint.
- **Final report should say:** drop "input-only" wherever it appears (DESIGN_REVIEW §5, HARDWARE.md,
  README); replace it with "GPIO46 is a strapping pin with an internal pull-down — it must read low at reset."

### C2 — Battery-IC manufacturer fields
- **Prior (§4):** resolved 2026-09-18 — "`part_fields.csv`, the schematic/PCB fields and
  `fabrication/BOM_handbuild_digikey.csv` all carry EVVOSEMI as of 2026-09-18."
- **New (BAT-V03, DOC):** the Manufacturer/Datasheet fields for **U5 and Q1** do not match the parts their
  LCSC codes deliver.
- **Adjudication: both partly.** Ground truth at `c0eccde`: `Q1 Mfr=EVVOSEMI LCSC=C2830320` and
  `U5 Mfr=Fortune Semiconductor LCSC=C351410`. The prior's Q1 fix *was* applied, and the prior was right
  that the MPN "FS8205A" is legitimate in SOT-23-6 — but EVVOSEMI is the DigiKey-side prime while
  C2830320 ships TECH PUBLIC, so the field still does not describe what the code delivers. **U5 is the
  clean miss**: §4 of the prior review itself names the ordered part "PUOLOP DW01A C351410", yet the
  schematic field was left reading Fortune Semiconductor and the datasheet link points at a third vendor.
- **Final report should say:** BAT-V03 stands. Split the fields into prime vs JLC (as the BOM already does
  for D2 and L1) rather than picking one manufacturer name per line.

### C3 — EPD boost loop area
- **Prior (§7, re-measured 2026-09-18):** the `C10→L1→Q4→R14` pad-centre loop "grew from ≈24 to ≈33 mm² (+36 %)"
  after the 5×5 mm L1 went in. This number is now quoted verbatim in `docs/HARDWARE.md` §6.2.
- **New (LAY-D2, DOC):** shoelace on the pad-centre polygon gives 24.0 / 26.0 / 26.6 mm² depending on which
  pads are used; "I could not verify the 33 mm² figure."
- **Adjudication: the new audit is right, with a caveat.** Running the shoelace on the *component origins*
  from `evidence/blocks/epd.md` — C10 (92.1, 109.8), L1 (88.5, 112.3), Q4 (88.6, 117.0), R14 (89.1, 122.5) —
  gives **20.0 mm²**, and the new audit's pad-centre variants bracket 24–27 mm². I can find no pad
  combination that reaches 33 mm². The prior's own "+36 %" is the suspect step; the pre-move ≈24 mm² figure
  appears to have been carried forward as the post-move number's baseline by mistake.
- **Final report should say:** correct HARDWARE.md §6.2 to ~24–27 mm². The error is in the design's favour,
  so it changes no recommendation — DOC severity.

### C4 — Charge current: 234 mA or 255 mA
- **Prior (§3):** the exact TOPPOWER C16581 sheet gives ICHG ≈ 1100/RPROG = **234 mA** at R6 = 4.7 kΩ; the
  source annotation's "exact 255 mA is not established," and the datasheet's own example table is internally
  inconsistent (250 mA at 5 kΩ).
- **New (LAY-V02, LOW):** "the charger is programmed for about 255 mA, not the 1 A the layout analysis assumed."
- **Adjudication: prior is right on the number, new is right on the point it is making.** LAY-V02's purpose is
  to correct a *1 A* assumption elsewhere in the new audit's own layout section, and for that purpose 234 vs
  255 mA is immaterial. But the final report should quote **≈0.23–0.25 A (lot-dependent, measure it)** and not
  repeat "255 mA" as if it were established.

### C5 — L1's dual-source symmetry
- **Prior (§7, §12):** "Both parts are shielded and the same physical size — no shielding or footprint
  asymmetry between builds."
- **New (BOM-14, LOW):** the Sunltech substitute has 650 mΩ DCR vs the Laird prime's 272 mΩ (2.4×) and
  Isat 940 mA vs 1.1 A; `fabrication/nextpcb_substitutes.csv` justifies the swap only on case size.
- **Adjudication: both partly — the new audit adds what the prior left out.** The prior's claim was
  specifically about *shielding and footprint*, and on that narrow point it is correct and still true
  (`L1 fp=Inductor_SMD:L_APV_ANR5040` serves both). But the prior's own §7 text quotes both parts' DCR
  (272 mΩ vs 650 mΩ) and then does not draw BOM-14's conclusion. BOM-14 is a fair addition, and its
  unresolved height question (the JLC listing does not publish the Sunltech part's height, and 4.2 mm makes
  L1 one of the tallest bottom-side parts) is a real open item for the enclosure.

### C6 — The J7 fix, and the stale button check
**C6a — J7:** the prior closed J7 as "APPLIED — NPTH slots 1.50 mm tall, owner-confirmed against both 3D
models." The new audit (SD-07) agrees the slots exist but points out the *right* slot is only 0.05 mm wider
than the TF PUSH's recommended peg hole and sits at the minimum routed-slot width, and (FAB-23, LAY-01) that
several routed slots on this board are below JLCPCB's and PCBWay's minimum non-plated slot width.
**Adjudication: both partly.** The mechanical fit question the prior closed is genuinely closed; the
*manufacturability* of the slot that closes it was never asked. The final report should keep J7 as resolved
and move the residual into the fab-minimums item.

**C6b — buttons:** the prior (§9) closed button placement — "no remaining asymmetric placement defect was
found. TS365ZJ's 5 mm signal pitch, 7 mm bracket pitch and 2.5 mm row spacing agree with the holes."
Ground truth at `c0eccde`: **SW1/SW2/SW10/SW11 are `MJTP1117` (APEM, LCSC C557598) on footprint
`mjtp1117:MJTP1117`; SW6 is MJTP1243.** There is no TS365ZJ on the board.
**Adjudication: the prior check is stale, not wrong — it verified a part that has since been replaced.**
The new audit's HMI-10, MEC-08, MEC-11, HMI-13, HMI-14, HMI-V03, HMI-17 and BOM-13 are all about the part
that is actually there. The final report must not carry the prior's "no asymmetric placement defect" line
forward: nobody has re-verified button placement against MJTP1117 since the swap, and the new audit finds
the bottom row sits ~1.0 mm closer to the edge and protrudes ~1 mm further than the side buttons.

---

## 5. Recovered findings — open in the prior corpus, absent from the new audit

| ID | Title | Severity |
|---|---|---|
| REC-A-01 | No VBUS-sense input: a self-powered USB device with nothing to monitor | MEDIUM |
| REC-A-02 | Fix 4 cannot start charging a 0 V / protection-latched pack | MEDIUM |
| REC-A-03 | U10's current limit and the C9 hot-plug inrush both exceed L2's saturation rating | LOW |
| REC-A-04 | Q7 switches SD_VDD on in microseconds — far faster than the SD spec's suggested VDD ramp | LOW |
| REC-A-05 | No USB D+/D− series-damping footprints, contrary to Espressif's schematic checklist | CERT-LATER |

One further NOT-IN-NEW item, the prior's "TP4056 VCC has no local input bypass (≈9.16 mm to C2)", was
checked against `c0eccde` and **is not recovered**: `C2.1` (81.100, 95.4625) now sits **2.08 mm** from
`U11.4` (82.795, 96.675). The prior figure is stale. Do not carry it into the final report.

### REC-A-01 — No VBUS-sense input (MEDIUM)
**Refs:** net `USB_VBUS`; `U4` (ESP32-S3-WROOM-1-N16R8) GPIO19/GPIO20; `R17/R67/R70/R71` (USB_STAT ladder).
**Evidence:** `evidence/blocks/usb.md` — net `USB_VBUS` has exactly 8 nodes: `C2.1`, `C25.2`, `D2.2`, `F1.2`,
`R38.1`, `U2.3` (TPS2116 VIN1), `U2.5` (MODE) and `U11.4` (TP4056 VCC). There is no divider, comparator or
any other path from VBUS to a GPIO. The only USB-presence information available to firmware is the analog
`USB_STAT` ladder, which the new audit itself shows is ambiguous (USB-01, USB-02, USB-18, USB-19, USB-V02:
several distinct physical states collapse into the same voltage, and the "idle" window is outside the ADC's
specified range). Espressif's self-powered-device guidance for the S3's USB-OTG peripheral expects a
`vbus_monitor_io`. Searching the new audit's 297 findings for "self-powered", "vbus_monitor", "VBUS sense"
and "detach" returns **zero** hits.
**Prior source:** `DESIGN_REVIEW.md` §3, "Self-powered USB needs a disconnect policy" — raised, then
**Decision (2026-09-17): accepted as a firmware responsibility**, with a §13 step 11 bench check.
**Recommendation:** keep the owner's acceptance, but say so explicitly in the final report rather than
letting it disappear: the board cannot tell firmware, digitally and unambiguously, whether USB is present.
For the prototype this is a firmware constraint (tear down USB on a debounced USB_STAT transition; do not
rely on ST alone). On any revision, add a divided VBUS tap to a spare ADC/GPIO — it costs two resistors.

### REC-A-02 — Fix 4 cannot start charging a 0 V / protection-latched pack (MEDIUM)
**Refs:** `Q9` (BSS138, detector), `R79` 100 k, `R80` 1 M, `Q2` (AO3401A), `R82` 1 M, `U11.8` CE, `J5`.
**Evidence:** net `CE` has three nodes only — `Q2.3`, `R82.2`, `U11.8` — so CE is low (charger disabled)
unless `Q2` is turned on by `/DET_NODE`, which requires `Q9` to conduct, which requires
V(J5 B+ vs B−) × R80/(R79+R80) = 0.909 × V_cell to exceed the BSS138's Vth (0.5–1.6 V). A protected LiPo
pack whose own PCM has latched into over-discharge lockout presents ≈0 V at its leads, as does a bare cell
drained below ~1.1–1.8 V. In both cases the charger never starts, and no amount of USB time will recover the
pack on this board. This is a behaviour *change* introduced by Fix 4 — before it, CE was tied to USB_VBUS
and the charger always tried. Searching the new audit for "flat cell", "over-discharge lock", "revive" and
"rescue" returns **zero** hits; BAT-04 and BAT-V01 cover different corners of the same detector.
**Prior source:** `DESIGN_REVIEW.md` §4, "Known, accepted limitation — not treated as a defect… Judged an
unrealistic/insubstantial scenario for this board's use case and not pursued further."
**Recommendation:** worth one sentence in the user-facing docs, because a dead-pack-in, nothing-happens
board is indistinguishable from a broken board. The prior review already names the cheap fix: a two-pad
manual-override jumper from `/DET_NODE` to GND. Note that this interacts with the new audit's BAT-V04 (a
hobby pack wired to the opposite JST-PH convention will also simply refuse to charge, with no other symptom),
which makes "the charger silently does nothing" a more likely first-boot experience than either finding
alone suggests.

### REC-A-03 — U10's current limit and the C9 inrush exceed L2's saturation rating (LOW)
**Refs:** `U10` TPS923610, `L2` 10 µH TDK VLS252012HBX-100M-1 (C88532), `C9` 4.7 µF/50 V.
**Evidence:** the prior review states in §8 that "U10's maximum current limit exceeds the inductor's rating",
and in the C9 4.7 µF note that at battery hot-plug the `L2 → high-side body diode → C9` path "can ring
briefly to roughly 2.5 A (about 1.3 A with 1 µF) — confirm L2's saturation margin or accept a brief
saturation." The 4.7 µF value is applied at `c0eccde`, so the 2.5 A estimate is the live one. The new audit
discusses L2 in LED-03 ("a short to ground destroys L2") and LED-V05 (which argues R37 dies first), but
nothing in it compares U10's current limit or the inrush to L2's Isat.
**Recommendation:** fold into the first-article scope check that already exists (§13 step 12c). Brief
saturation of a 2520 shielded inductor on a hot-plug transient is normally survivable; the point is that it
has never been checked against a number, and the applied C9 change roughly doubled the estimate.

### REC-A-04 — SD_VDD turn-on ramp is far faster than the SD spec suggests (LOW)
**Refs:** `Q7` AO3401A, `R78` 1 k (gate series), `R40` 100 k (gate pull-up), `C36`+`C37` ≈1.1 µF, `J7` VDD.
**Evidence:** prior §6 (added 2026-09-18): IO10 drives Q7's gate through 1 kΩ with a 100 kΩ hold-off, so the
PMOS turns on in microseconds into ≈1.1 µF plus the card's own capacitance — faster than the SD
specification's suggested minimum VDD ramp (~0.1 ms) and able to dip 3V3 by a few hundred mV briefly. The
new audit's MCU-06 and SD-15 cover the *60 µs power-up glitch* (a different phenomenon — an unintended
momentary enable), and SD-11 covers the small bulk value; the ramp-rate-vs-spec point is not made anywhere.
**Verified at `c0eccde`:** `Q7 = AO3401A`, `R78 = 1k`, `R40 = 100k`, `C36 = 0.1u`, `C37 = 1u` (1.1 µF), and
net `Net-(Q7-G)` has exactly three nodes — `Q7.1`, `R40.1`, `R78.2`. There is still no gate capacitor.
**Recommendation:** the prior already names the optional fix (47–100 nF gate-to-3V3, τ ≈ 50–100 µs with
R78) and correctly gates it on first-article card-init behaviour. Keep it as a conditional, not a change.

### REC-A-05 — No USB series-damping footprints (CERT-LATER)
**Refs:** `J1` → `U4` GPIO19/20; D+ 33.06/34.76 mm, D− 33.72/35.42 mm (prior §11).
**Evidence:** prior §11 — "the source lacks optional USB series-damping footprints recommended in
Espressif's guidance." **Verified still absent at `c0eccde`:** net `DN` has 4 nodes (`J1.A7`, `J1.B7`,
`U4.13`, `U6.1`) and net `DP` has 4 nodes (`J1.A6`, `J1.B6`, `U4.14`, `U6.6`) — connector, module and ESD
array only, with no series element and no unpopulated pads in the path. The new audit's USB-12 and LAY-C4
describe the same routes (not impedance-controlled, via-asymmetric, 46 mm) but do not mention the missing
footprints.
**Recommendation:** CERT-LATER by the owner's standard. At 12 Mbps Full Speed this is a signal-quality
nicety; if a revision ever happens, two 0 Ω 0402 footprints in series cost nothing and buy an option.

---

## 6. The new audit's BLOCKER/HIGH findings — new, or already known?

| New ID | Sev | Known to corpus A? | Where / note |
|---|---|---|---|
| **LED-01** | BLOCKER | **NO — genuinely new** | `DESIGN_REVIEW.md` contains "paste" **zero times**. §2 explicitly scopes the Gerber check as *not* a CAM/DFM check ("resolves apertures, drawing primitives, regions and polarity"), and §11 records that the mask-bridge and footprint-library DRC checks are off. The prior named the blind spot and did not enter it. Nothing in the corpus mentions solder-paste apertures on J2/J3/J4 or anywhere else. |
| BOM-01 | HIGH | **NO** | §7/§12 discuss R14 = C112307 pricing and class, never stock depth. |
| DOCS-01 | HIGH | **NO** (firmware absence) | §5 assumes firmware responsibilities throughout but never observes that no firmware exists or is linked. |
| DOCS-02 | HIGH | **NO** | The corpus is not a README review. |
| DOCS-03 | HIGH | **PARTIAL** | §12 warns "pricing/sourcing tables under `fabrication` are historical references, **not** the current release BOM", and §12 names `bom_JLC_upload_v4_optimized.csv` as *the* upload BOM with v3 as a variant. It never found the duplicate-LCSC defect itself. |
| DOCS-04 | HIGH | **NO** | No off-board shopping list is contemplated anywhere. |
| DOCS-05 | HIGH | **PARTIAL, differently** | The corpus is saturated with lithium-safety caution (§4 "never deliberately reverse a real LiPo", §13 step 9), but it is engineer-facing; it never asks whether the *repository* warns a reader. |
| DOCS-06 | HIGH | **NO — and this is about corpus A itself** | DOCS-06 is the finding that the README's first instruction sends a newcomer into this 100 KB review. |
| DOCS-07 | HIGH | **PARTIAL** | §11/§13 defer enclosure work ("check panel/battery/housing/metal placement in the final stack"); §14 lists enclosure certification as out of scope. The corpus knows mechanics are unresolved; it never frames "case agnostic" as a documentation claim. |
| DOCS-08 | HIGH | **NO** | No URL/branding check anywhere. |
| DOCS-09 | HIGH | **NO** | No JLC tier/size/edge-rail/fiducial discussion; "fiducial" appears zero times in the corpus. |
| **HMI-01** | HIGH | **YES — known** | §10: "J6 is not a generic low-voltage GPIO header. Its pins include LED_SW, switched LED cathodes and **P+** beside logic. External supply injection can back-power rails; there is no general accessory power isolation." The prior framed it as a back-powering/strapping hazard and left it as a warning; HMI-01 reframes it as an unfused battery output and proposes a 0.5–1 A PPTC. **The new audit's contribution is the remedy, not the discovery.** |
| LAY-01 | HIGH | **NO** | "tongue", "cut line" and slot-width minimums appear nowhere; the only slots the corpus discusses are J7's. |
| MEC-01 | HIGH | **NO** | The corpus never measures the flex slot; "FPC" appears only in the front-light pinout and the acceptance plan. |
| MEC-02 | HIGH | **NO** | The "cut for smaller displays" feature is absent from the corpus entirely. |
| MEC-23 | HIGH | **NO** | §11 asks for "drawing-based fit checks" but never measures what protrudes into the panel footprint. |
| SD-V01 | HIGH | **NO** | §6 resolves J7's *peg* mechanics; the card-insertion corridor vs the battery cut-out is never considered. |

**Score: 4 of 16 BLOCKER/HIGH findings were known or partly known to corpus A** (HMI-01 fully; DOCS-03,
DOCS-05, DOCS-07 partly). **Twelve are genuinely new**, and eleven of those twelve fall inside the
mechanical / fabrication-output / documentation space the prior review explicitly declared out of scope.

Also worth recording in the other direction: the new audit **refuted** six of its own findings
(BAT-09, EPD-02, HMI-20, MCU-02, PWR-08, PWR-12). On two of those — MCU-02 and PWR-12, both about the
DS3231MZ's VCC-grounded / VBAT-primary topology — **corpus A had already closed the question correctly**
in §10 with the manufacturer's own Figure 5. A reviewer holding both documents would not have spent the
effort.

---

## 7. Blind spots, both directions

**Corpus A's blind spots (what a circuit review does not see):**
1. **Fabrication output.** Not one word about solder paste, mask dams, annular rings, fiducials, silkscreen
   legibility or slot widths against a fab's stated minimums. §2 and §11 *declare* this limit honestly — and
   the one BLOCKER on the board lives inside it.
2. **Mechanics and enclosure.** Deferred wholesale to "physical qualification" and §13 step 11. The new
   audit's entire MEC-* family (23 findings, three HIGH) is the deferred work actually done.
3. **The repository as a deliverable.** Corpus A reviews the *design*; it never asks what a reader
   receives. All 24 DOCS-* findings are outside its frame — including DOCS-06, which is about corpus A.
4. **Live supply-chain state.** §12 freezes a sourcing snapshot and says so; it cannot catch BOM-01/BOM-02/
   BOM-03 (stock collapse, obsolete MPNs) because those are facts about today, not about the design.
5. **Self-consistency of generated artefacts.** The prior verified the *Toolkit* CPL against the PCB and
   stopped there; the mutual disagreement of the several BOM/centroid exports (FAB-14/15/17/19/22, BOM-05)
   went unexamined.
6. **A few of its own numbers.** The 33 mm² loop area (C3) and the stale TS365ZJ button check (C6b) both
   propagated into HARDWARE.md and would have been carried into the release unchallenged.

**The new audit's blind spots (what corpus A covers better):**
1. **Quantified thermal analysis.** Corpus A's §3 U3 scenario tables (EVM vs JEDEC θJA, per-current junction
   estimates, the ΨJT measurement method and the decision table for what to do with the result) have no
   counterpart. PWR-01's "240–280 mA" is a conclusion; the prior shows the work and tells you how to
   measure it.
2. **Simulation of the battery fault.** The LTspice behavioural decks (§4) are what turned "reverse
   insertion is unsafe" into "0.25 A sustained through the reversed cell, and here is why the obvious
   alternatives deadlock a flat cell". The new audit inherits the fixed circuit and never reasons about
   the rejected alternatives — which is why it misses REC-A-02.
3. **Firmware-facing consequences.** Corpus A consistently states the firmware rule that a hardware
   limitation implies (SD power-down ordering, ADIM enable-pulse sequencing, ADC top-code handling, USB
   teardown on detach). The new audit finds the same hardware facts and files them as hardware findings;
   REC-A-01 fell out entirely because it is a firmware-shaped item.
4. **Part-selection reasoning.** The Q4 replacement table (six candidates with RDS(on)/Qg/Ciss and an
   explicit "SC-70 is not a SOT-23 substitute"), the L1 survey and the C9 COUT analysis are genuine
   engineering that the new audit takes as given.
5. **An acceptance plan.** §13's twelve steps are the bridge from "review" to "board on the bench". The new
   audit has no equivalent; the final report should keep §13 and add LED-01's paste re-check to step 1.

**Net judgement:** the two corpora are complements, not competitors. Corpus A's applied-fix ledger survived
the blind audit intact, which is the strongest evidence that its electrical conclusions were sound. The
blind audit's value is almost entirely in the space corpus A declared out of scope — and one item in that
space (LED-01) would have returned a board with no display, no front light and no touch.
