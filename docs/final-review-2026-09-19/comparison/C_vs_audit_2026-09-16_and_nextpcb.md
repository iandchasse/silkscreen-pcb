# Corpus C vs the blind final review — `docs/audit-2026-09-16/` + `fabrication/NEXTPCB_REV0_NOTES.md`

Compared against: `docs/final-review-2026-09-19/` (297 findings, 13 sections), ground truth from
`docs/final-review-2026-09-19/evidence/` at commit `c0eccde`.
Written 2026-09-20. Nothing in the repository was modified to produce this.

---

## 1. Summary

Corpus C is not a narrative audit. It is a **machine-verification corpus**: a per-component review table
(173 rows), a per-block membership map, netlist/board metric dumps, an LTspice reverse-polarity study, an
LDO thermal sweep, an SD-socket mechanical overlay, a gerber-vs-gerber differ, a BOM cross-check, and an
old DRC/ERC snapshot — plus one genuinely field-derived document, the NextPCB Rev0 upload notes. I
extracted **52 distinct items** from it (42 from the audit folder, 10 from the NextPCB notes).

The headline result is that **corpus C and the new audit agree almost everywhere they overlap, and corpus
C's recommendations were largely acted on.** Of the ten most consequential things corpus C asked for or put
on HOLD, **eight are implemented in the current design** — R37 13.3 Ω → 15 Ω (`C22810`), Q4 BSS138 →
IRLML6346TRPBF (`C67276`), L1 22 µH → 47 µH to match the panel reference, R27 0603 → 0805 jumper, L2 LCSC
disagreement resolved, J5 CJT `A2001WR-2P` → genuine JST `S2B-PH-K` (`C48579993`), D2 reverse-mount part →
Lite-On `LTST-C150KRKT` (`C28310439`, the exact part corpus C said the owner had asked for), and U13 lifted
out of its DNP/order contradiction. The two that were *not* acted on are the Q5/Q6 non-overlap measurement
and the third-party-brand-substitution risk on U3.

Where corpus C and the new audit disagree, **the new audit is right in every case I could adjudicate** —
mostly because corpus C was reading a BOM that has since changed (D4–D6, Q4, L1), or because it compared
the released gerbers against a *regenerated* set using a different export flavour and read the diff as a
stale-output risk when it was not.

Two things corpus C contributes that the new audit does not have:

* **The NextPCB DNP-merge failure is field evidence, not theory.** `R43 R45 R58 R66 R72 R74` came back
  *fitted* in a real fab's matched BOM because their importer merges lines sharing an MPN and drops the DNP
  mark. The new audit reaches the same place analytically (HMI-V01, HMI-07) and even cites the README
  record of it, but corpus C is the primary source — and it names a seventh designator the new audit misses
  (`SW6`).
* **A DRC/ERC baseline.** Old DRC 87 violations vs new 94. The delta is not noise: **4 `track_dangling`
  warnings and 1 `mirrored_text_on_front_layer` did not exist on 2026-09-16.** They are regressions
  introduced by the later "optional front-mounted bottom buttons" commit (`b1d839c`). The new audit reports
  them (FAB-07, FAB-08) as static facts; corpus C lets you date them, which tells the owner *which* edit to
  look at. ERC went 37 → 39 (+1 `pin_to_pin`, +1 `lib_symbol_mismatch` — the new audit's LED-09/FAB-13).

**On LED-01 (the new audit's only BLOCKER — no solder-paste apertures on J2/J3/J4 signal pads): corpus C
never mentions it, and could not have.** Its only paste-layer work is
`gerber-geometry-comparison.json`, which compares the *archived* `B_Paste.gbp` against a *regenerated*
`B_Paste.gbp` and reports `geometry_equal: true, objects_old: 607, objects_new: 607`. Both copies are
missing the same 36 apertures, so an old-vs-new differ can never see it. `component-review.csv` reviewed J2,
J3 and J4 for **electrical** pin mapping only. No file in corpus C ever asks "does every SMD pad have a
paste aperture?". LED-01 is genuinely new, and it lands hardest exactly where corpus C's recommendation
points — see the adjudication in §3.

---

## 2. Mapping table

Relation key: **SAME** (new audit covers it), **PARTIAL** (new audit covers part of it),
**FIXED** (corpus C asked for it; the current design has it), **CONFLICT**, **NOT-IN-NEW**.

| # | Prior item (short title) | Prior status | Relation | New IDs | Current truth |
|---|---|---|---|---|---|
| C-01 | C4/C6/C32 22 µF X5R: effective capacitance at bias not established | open (qualify) | PARTIAL | BOM-02, BOM-04, EPD-04 | Still 22 µF/25 V X5R 0805. New audit covers DC-bias derating (BOM-04, on C2) and the obsolete MPN, not these three specifically |
| C-02 | C11–C17 4.7 µF/50 V X5R on HV nodes: verify effective C under bias | open (qualify) | PARTIAL | EPD-04, EPD-07 | Unchanged. New audit attacks placement distance instead of bias derating |
| C-03 | C22 1 µF on 3V3 sits 51.84 mm from U4's supply pad, "not MCU-local decoupling" | open | CONFLICT | EPD-04, EPD-V01, MCU-16, PWR-09 | C22 is the **panel** VDDIO/VCI decoupler at (85.47, 133.62), ~16 mm of 0.25 mm track from J2.15. New audit is right; see §3.2 |
| C-04 | CR2/CR3 5 V TVS: surge clamp is not a precision rail limit | open (accepted) | NOT-IN-NEW | — | Still `TSD05CDYFR` (`C5299440`) on 3V3 and on the J6 battery rail. → **REC-C-04** |
| C-05 | D2 on HOLD: saved order is a reverse-mount LED; owner asked for `C28310439` | HOLD | FIXED | MEC-19, DOCS-24, BAT-12 | D2 = Lite-On `LTST-C150KRKT` / `C28310439`, 1206 top-emitting. Fix confirmed — and it is *why* MEC-19 exists (see §3.6) |
| C-06 | D3 SMAJ26A 42.1 V clamp does not guarantee IC protection | open | SAME | BOM-10, HMI-16, LED-V01 | Unchanged. New audit gives the same 42.1 V number independently |
| C-07 | D4/D5/D6: qualify reverse overshoot and hot leakage | open (qualify) | SAME / CONFLICT on part id | EPD-09, EPD-03, EPD-V02 | Fitted part is `1N5819HW-7-F` (`C8598`), 40 V/1 A. Corpus C's "B5819W" is the schematic **value** field, not the MPN. New audit right; see §3.3 |
| C-08 | D8: TECH PUBLIC 24 V dual TVS, signal1/2 common3, verified compatible | verified OK | SAME | HMI-11, BOM-06 | Confirmed by the new audit's symbol check. New audit adds that the part is NFND at DigiKey (BOM-06) — that is new |
| C-09 | F1 1 A hold derates to ~0.65 A at 60 °C / 0.55 A at 70 °C | open | SAME | USB-05 | Unchanged |
| C-10 | J1: tight pad gaps are footprint geometry, not shorts; confirm THT in the assembly scope | resolved-as-benign | SAME | FAB-04, LAY-16, USB-10, DOCS-14 | Identical conclusion, 12–16 clearance errors all inside J1 |
| C-11 | J2: 24-pin mapping checked; confirm FPC thickness / contact orientation / panel variant | open (qualify) | PARTIAL | EPD-01, EPD-02 (refuted), MEC-01, MEC-05, EPD-V01 | New audit refuted the pin-1-reversal worry (EPD-02) and replaced it with the flex-slot and corridor mechanics |
| C-12 | J3/FT01C: supplier drawing conflicts with the owner's physical sample; a drawing-conforming unit reverse-biases a string → boost OVP → LED damage | open, lot check required | SAME | LED-12, LED-V02 | Same conclusion. Corpus C carries the stronger evidence (a measured sample); new audit carries the better framing (bring-up gate). See §3.5 |
| C-13 | J4: default links give GND/3V3/RST/INT/SDA/SCL; alternates must stay DNP | open | SAME | HMI-07, HMI-V01 | Unchanged; the alternates are `dnp,exclude_from_bom` and safe |
| C-14 | J5: CJT 2 mm right-angle in a JST-PH footprint; pin 1 = B-, pin 2 = B+; verify cable polarity | open | FIXED (part) + SAME (polarity) | BAT-V04, BAT-11 | J5 is now a genuine JST `S2B-PH-K-S` (`C48579993`) in its own footprint — footprint/part mismatch gone. The pin-1 convention question is still open and is BAT-V04 |
| C-15 | J6 exposes the HV LED rail and boot straps; not a generic GPIO header | open | SAME | HMI-01, HMI-02, LED-03, HMI-V04, MCU-04 | Unchanged. New audit escalates the raw-LiPo pin to HIGH (HMI-01) |
| C-16 | J7 TF PUSH: peg-hole Y offset 0.22 mm; assembly fit confirmation required | open | SAME | SD-05, SD-07, SD-08 | Unchanged. New audit adds SD-V01 (insertion corridor crosses the battery cut-out), which corpus C did not reach |
| C-17 | L1 22 µH vs the panel reference's 47 µH — needs qualification | open | **FIXED** | BOM-14 | L1 is now 47 µH (`C206267`, Sunltech `SLW5040S470MST`, footprint `L_APV_ANR5040`). New BOM-14 critiques the substitute's DCR, not the value |
| C-18 | L2 LCSC disagreement: order `C88528` vs upload `C413592` | open | **FIXED / moot** | — | L2 is now 10 µH `C88532` and appears on exactly one BOM line. Disagreement gone |
| C-19 | Q3 body diode can conduct into a reversed cell even with the channel off; reverse-insertion safety not established | open | SAME | BAT-V02, BAT-03, BAT-04 | New audit reaches the same place: Q3 blocks nothing as oriented; Q8 + the CE gate do the work |
| C-20 | Q4 HOLD on BSS138; preferred replacement IRLML6346TRPBF `C67276` | HOLD | **FIXED** | EPD-03, EPD-V02 | Q4 = `IRLML6346TRPBF` / `C67276`. The 30 V rating the new audit measures against is a direct consequence of adopting corpus C's recommendation |
| C-21 | Q6/U12: inversion does not guarantee transient exclusivity; static complementary logic does not guarantee non-overlap during Q5/Q6 switching | open (measure) | **NOT-IN-NEW** | — | Topology unchanged: U12 `74LVC1G04` inverts COLOR_SEL into Q6's gate while Q5 takes COLOR_SEL direct; both sources share `Net-(Q5-S)` into R37. → **REC-C-01** |
| C-22 | R14 3 Ω 0.1 W; full-rated continuous RMS is 183 mA | open | SAME | BOM-11 | Unchanged |
| C-23 | R27 0 Ω battery-path jumper: check current rating and drop | open | **FIXED** | BAT-07, PWR-V01 | R27 is now an 0805 0 Ω (`C17477`). The remaining issue is the 0.25 mm trace either side of it, which is what the new audit reports |
| C-24 | R37 13.3 Ω gives 14.52–15.65 mA; recommend 15 Ω 1 % `C22810` | recommendation | **FIXED** | LED-07, LED-V03 | R37 = 15 Ω `C22810`. Exactly the recommended part. The docs did not follow (LED-07) |
| C-25 | SW6 and U13: PCB DNP flag disagrees with the order's population | open | PARTIAL | MCU-01, HMI-V01 | U13 resolved (fitted, `C107410`). **SW6 still carries `flags=dnp` without `exclude_from_bom`** and still appears as a DNP row in `bom_ungrouped.csv` — the HMI-V01 defect class, but HMI-V01 names only R72/R74. → **REC-C-02** |
| C-26 | U5 DW01A: no reference series VCC filter; USB-present reverse battery can force VCC negative | open | SAME | BAT-02, BAT-03 | Unchanged. New audit quantifies it (VCC below GND, outside abs max) |
| C-27 | U11 TP4056 R6 = 4.7 k → ~234 mA, not 1 A; datasheet formula vs table disagree | open | SAME | LAY-V02 | New audit independently lands on ~255 mA and notes the whole layout analysis had assumed 1 A |
| C-28 | U1/U6/U7/U8/U9 TPD4E1U06: pin-compatible, but not TI performance nor system ESD certification | verified OK | PARTIAL | BOM-V01, SD-13, HMI-08, SD-V04 | New audit critiques the five arrays on cost/necessity (BOM-V01) and on grounding, not on brand equivalence |
| C-29 | U12 MDD 74LVC1G04 pinout verified (NC1 A2 GND3 Y4 VCC5) | verified OK | SAME | — | Confirmed in the current netlist |
| C-30 | LDO thermal sweep: Tj vs sustained 3V3 load, two θJA values | open (budget) | SAME | PWR-01, PWR-02, PWR-15 | New audit's ~240–280 mA continuous-on-USB limit is the same calculation |
| C-31 | USB_STAT ladder: weak-source near-full states overlap after real errors | open | SAME | USB-01, USB-02, USB-V02, USB-18, USB-19 | Unchanged. New audit goes further (the >3.10 V window is outside the ADC range at all) |
| C-32 | Button ladder nominal voltages per press | reference data | SAME | HMI-05, HMI-06, HMI-15, HMI-V05 | Same resistor values; new audit adds chord separation and ADC-region analysis |
| C-33 | Power-mux threshold spread 3.63–4.39 V | reference data | PARTIAL | USB-03, PWR-06 | New audit attacks the missing hysteresis and the floating MODE pin instead |
| C-34 | LED current alternatives table (13.3 / 14.3 / 15 / 16 / 18 Ω) | recommendation | superseded | LED-07, LED-V03 | Superseded by the C-24 fix |
| C-35 | Rev-pol study: an enabled no-battery operating point exists — USB holds B+ through the pass channel; an empty connector is not de-energized | open (warning) | SAME | BAT-V01, BAT-13, HMI-01 | The shipped Fix-4 CE gate has exactly this property; BAT-V01 states it independently |
| C-36 | Rev-pol proposal costs +42 µA at 4.2 V (~30 mAh/30 days) | proposal, not built | superseded | PWR-03, BAT-04 | The shipped gate uses R82 = 1 M, far lighter. The 42 µA concept was never built |
| C-37 | Regenerated Fabrication-Toolkit gerbers differ from the archived ones (1995 diff lines) | open | **CONFLICT** | — (evidence/gerber_fresh/COMPARISON.txt) | The committed zip **is** current with the board file. See §3.1 |
| C-38 | Gerber geometry old vs new: all layers equal; `F_Paste` 0 objects, `B_Paste` 607 | verified OK | **blind spot** | LED-01 | Both copies share the same missing apertures. See §1 and §3.4 |
| C-39 | CPL: 157 rows vs 174 footprints, no differences | verified OK | PARTIAL | FAB-14, FAB-15, FAB-18, FAB-19 | New audit finds the *conventions* disagree between files, which a single-file self-check cannot see |
| C-40 | DRC baseline: 87 violations (32 silk-edge, 24 starved thermal, 14 clearance, 11 silk-over-copper, 6 silk-overlap) | baseline | SAME + dating | FAB-04, FAB-06, FAB-07, FAB-08, FAB-09, LAY-06, LAY-12, LAY-16 | Now 94. **`track_dangling` ×4 and `mirrored_text_on_front_layer` ×1 are new since 2026-09-16** |
| C-41 | ERC baseline: 37 violations | baseline | SAME + dating | LED-09, FAB-13, HMI-11 | Now 39 (+1 pin_to_pin, +1 lib_symbol_mismatch) |
| C-42 | BOM cross-check: 60 order rows vs 173 refs; FIT 155 / MECH 10 / DNP 8; no duplicate refs, no passive value errors | verified OK | PARTIAL | BOM-05, FAB-11, FAB-17, FAB-22 | The check never looked at LCSC-code *collisions across rows*, which is the defect that actually bit at JLC |
| N-01 | NextPCB importer merges lines sharing an MPN and drops DNP → `R43 R45 R58 R66 R72 R74` came back fitted; R73+R74 shorts 3V3 to GND | **observed at a fab; fixed by removing DNP rows** | SAME (field evidence) | HMI-07, HMI-V01, FAB-17 | Still live: R72/R74 carry `dnp` only. New audit's recommendation (set `exclude_from_bom`) is the right permanent fix |
| N-02 | Duplicate LCSC codes (`C14663`, `C28323`) left `C24 C31 C20` unmatched at JLC; v3 still carries them | fixed in v4, v3 not | SAME | DOCS-03, BOM-05, FAB-10, FAB-22 | `production/bom.csv` still regenerates the fault |
| N-03 | BOM/centroid designator mismatch: THT parts absent from the SMD-only centroid | fixed (162-row centroid) | PARTIAL | FAB-18, FAB-19 | New audit finds the *PCBWay* pair still mismatched (162 vs 149) |
| N-04 | `L1`, `J6`, switches unmatched in NextPCB stock → `nextpcb_substitutes.csv` | fixed by substitution | SAME | BOM-14, BOM-13, HMI-23 | Substitutes file present and current |
| N-05 | ALPS `SKHLLAA010`: same land, but 7.22 mm catalog depth vs 6 mm and 0.98 N vs ~2.5 N | accepted, "check stem clearance and feel" | PARTIAL | BOM-13, MEC-08, MEC-11 | New audit's protrusion numbers (MEC-08: +1.95 / +0.95–1.21 mm) are for the MJTP1117 only → **REC-C-05** |
| N-06 | Third-party brands on generic parts (`U3` "DYW" not TI, `U5` Slkor, `Q2/3/7/8` "BY", `CR1` HXY, `D3` JXND); U3 matters because the sleep budget assumes TI's ~25 µA | accepted with a caveat | NOT-IN-NEW (for U3) | BOM-09 (covers U5/Q1 only) | `U3` is specified as TI `TLV75533PDBVR` / `C404027`; nothing warns that a brand substitution invalidates PWR-03 → **REC-C-03** |
| N-07 | DFA: pad-edge clearance under 0.15 mm = J1's USB-C land pattern | resolved-as-benign | SAME | FAB-04, USB-10, LAY-16 | Same conclusion from two independent tools |
| N-08 | DFA: `J7`/`U10` absent from NextPCB's library; preview puts a THT model's pin 1 at the centroid; rotation experiments changed nothing | unresolved, "stop tuning" | PARTIAL | FAB-21, FAB-14 | Fab-tool quirk, not a board defect. FAB-21 reports the analogous JLC rotation-DB gap for U10/U2/D8 |
| N-09 | NextPCB Rev0 ≈ $296 + ~$70 THT ≈ $400; recommend JLC with THT included, NextPCB only for the SMD-only split | recommendation | **CONFLICT with LED-01** | DOCS-10, DOCS-13, DOCS-14 | The SMD-only split is the route LED-01 breaks. See §3.4 |
| N-10 | Rev0 rules: no customer-supplied parts; unmatched parts stay unpopulated | documented | PARTIAL | BOM-03, DOCS-16 | Still true and still only documented here |

---

## 3. Conflicts and adjudications

### 3.1 Are the committed gerbers stale? — **new audit right**

* Prior: `production-verification.json` regenerated the fab outputs with the Fabrication Toolkit and
  reported `equal_ignoring_creation_time: false, diff_lines: 1995` on `B_Cu.gbl` alone, with aperture
  definitions differing (`TA.AperFunction,SMDPad,CuDef` + `RoundRect` vs `ComponentPad` + `R,1.7X1.7`).
  Read on its own that says "the released zip does not match the board".
* New: `evidence/gerber_fresh/COMPARISON.txt` re-exported with `--no-x2` and `--subtract-soldermask`,
  stripped the date headers, and got **identical** on every copper, mask, paste and outline layer; the drill
  files differ only in slot encoding (routed `G00/M15` vs `G85`), same tools and hits.
* **Adjudication:** the new audit is right — the committed `production/Silkscreen_Reader_PCB_1.0.zip` is
  current with `c0eccde`. Corpus C's 1995 diff lines are an X2-vs-X1 attribute-flavour artefact of
  regenerating through a different exporter, not a stale-output risk. The final report should say the
  fab archive is verified current and should **not** carry a stale-gerber caveat.

### 3.2 C22 — **new audit right**

Corpus C flagged C22 as a 1 µF on 3V3 sitting 51.84 mm from U4's supply pad and concluded it is "not
MCU-local or RTC decoupling". That is a role misread: C22 is the **panel's VDDIO/VCI decoupler**, at
(85.47, 133.62), about 16 mm of 0.25 mm 3V3 track from J2 pins 15/16. The new audit identifies it correctly
(EPD-04, with EPD-V01 noting the panel tail flares over it). The underlying concern — a decoupler far from
what it decouples — is real and survives as EPD-04. The MCU's own decoupling order problem is a separate,
correctly-stated finding (MCU-16 / PWR-09: C33 0.1 µF is farther from the 3V3 pad than C32 22 µF).

### 3.3 D4/D5/D6 part identity — **new audit right**

Corpus C's tables say "40 V B5819W" (from `Ordered MPN = B5819W`). Current ground truth: schematic
**value** = `B5819W`, **MPN** = `1N5819HW-7-F`, **Mfr** = Diodes Incorporated, **LCSC** = `C8598`, while the
Description/Datasheet fields still describe a 30 V/0.5 A MCC MBR0520. So three different part identities
live on the same three components. The new audit's EPD-09 (1N5819HW reverse leakage vs the reference
MBR0530) and EPD-V02 (stale description fields) are both correct; corpus C was reading the value field.
The final report should note that on D4–D6 the **value** field is wrong too, not only Description/Datasheet
— EPD-V02's fix list should include it.

### 3.4 NextPCB SMD-only route vs LED-01 — **new audit right, and it invalidates the prior recommendation**

`NEXTPCB_REV0_NOTES.md` §5 recommends: for an SMD-only order, upload `split/nextpcb_bom_smd.csv` +
`split/nextpcb_centroid_smd.csv` (149 parts) and hand-solder the 13 THT parts. J2, J3 and J4 are SMD and
are in that 149. LED-01 shows their signal pads carry `{B.Cu, B.Mask}` and no `B.Paste`, confirmed in the
fab output (0 flashes on the J3 signal row at Y-124575000 where B_Cu has 11). **A board built through the
route corpus C recommends comes back with the display, front-light and touch connectors unsoldered** — and
0.5 mm-pitch FPC connectors with no mask dam between the pads (FAB-03) are among the least pleasant things
to hand-rework.
Corpus C could not have caught this: its only paste work is an old-vs-new gerber differ over two copies
that share the same omission. The final report should carry LED-01 as a hard gate on **both** ordering
routes, and `NEXTPCB_REV0_NOTES.md` §5 should get a pointer to it.

### 3.5 J3 front-light pinout — **both partly right**

Corpus C: "User confirms physical FT01C sample matches schematic: C+,C-,NC,NC,W+,W-. Supplier drawing
conflicts; no wiring change recommended for this sample. A unit following the drawing would reverse-bias
the selected LED string; boost can reach OVP and damage LEDs. Retain lot/FPC check."
New LED-12: "unverified from any primary source", recommend a bring-up diode test.
**Adjudication:** corpus C holds the stronger evidence (a measured physical sample, which the new audit
could not obtain — the vendor PDF is login-gated and the CDN 403s). The new audit is right that no primary
document supports it and that the supplier drawing disagrees. The final report should state both: the
schematic matches one verified sample, no document confirms it, the failure mode is a reverse-biased string
driving the boost to OVP (and LED-V02's three-strike latch), and the mitigation is a per-lot diode test at
bring-up — not a wiring change.

### 3.6 D2 — prior fix confirmed, and it created MEC-19

Corpus C put D2 on HOLD because the saved order was a **reverse-mount** LED while the owner had asked for
`C28310439`. The current BOM is `LTST-C150KRKT` / `C28310439`, a normal top-emitting 1206 on the bottom
face. The fix is real. Note the consequence: a reverse-mount part would have emitted *through* the board
toward the front; the top-emitting part emits out of the back, which is precisely what MEC-19 reports.
The final report should present MEC-19 as a deliberate trade with a known origin, not as an oversight.

### 3.7 Q4 / BSS138 — prior fix confirmed

Corpus C's HOLD and its specific replacement (`IRLML6346TRPBF`, `C67276`, 80 mΩ at 2.5 V, 2.9 nC) were
adopted. EPD-03's "30 V rating" and EPD-V02's "Description says 50 V BSS138" are both downstream of that
change. No conflict — worth recording so the owner knows EPD-V02 is a leftover field, not a part error.

---

## 4. Recovered findings

### REC-C-01 — Q5/Q6 colour-select pair has no guaranteed non-overlap, and nobody has measured it — **LOW**

*Refs:* U12 (74LVC1G04, `SOT-23-5`), Q5, Q6 (BSS138), R37, nets `COLOR_SEL` / `/COLOR_SEL_INV` /
`Net-(Q5-S)`. Prior source: `component-review.csv` rows U12 ("Static complementary logic does not guarantee
nonoverlap during Q5/Q6 switching") and Q6 ("Inversion does not guarantee transient exclusivity; measure
branch current during color changes. ADIM PWM low phases do not guarantee zero current").

*Evidence (current design, `evidence/blocks/led.md`):* `COLOR_SEL` drives Q5.1 directly **and** U12.2;
U12.4 = `/COLOR_SEL_INV` drives Q6.1. Q5.2 and Q6.2 share `Net-(Q5-S)`, which is the driver's single sense
node through R37; Q5.3 = `W-`, Q6.3 = `C-`. So one string is selected by an un-delayed GPIO and the other
by the same GPIO through an inverter's propagation delay. During a colour change there is a short window in
which either both strings conduct (R37 then regulates their *sum*, so each string momentarily runs at about
half current) or neither does (the driver sees an open load). The second case interacts with LED-V02: the
TPS923610's open-load OVP latches after three trips and nothing on the board or in the docs restarts it.
The new audit covers the latch (LED-V02) and the ADIM enable pulse (LED-14) but never examines the Q5/Q6
transition that can provoke it.

*Recommendation:* bring-up item, not a board change. Scope `Net-(Q5-S)` (across R37) and the boost output
through a colour change at several PWM duties and confirm the transition does not trip OVP; if it does, gate
colour changes to happen only while ADIM is low, or add a small RC on the U12 input to make the inverted
edge lead rather than lag. Record the result in HARDWARE.md next to the LED-V02 latch note.

### REC-C-02 — SW6 carries `flags=dnp` without `exclude_from_bom`, a third DNP leak HMI-V01 does not list — **LOW**

*Refs:* SW6 (`MJTP1243`, BOOT button). Prior source: `bom-verification.json`
`dnp_flag_disagreements: ["SW6","U13"]`, and `NEXTPCB_REV0_NOTES.md` §2, whose standing instruction is
"after every upload, check the matched BOM for `R43 R45 R58 R66 R72 R74` **SW6**".

*Evidence:* `evidence/sch/connectivity_by_component.txt:998` gives SW6 `flags=dnp` with no
`exclude_from_bom`; `evidence/sch/bom_ungrouped.csv:148` accordingly carries SW6 as a row with the DNP
marker as a **column value**. That is exactly the HMI-V01 mechanism, but HMI-V01's evidence names only R72
and R74 and describes "the six DNP jumpers", so SW6 falls outside it. U13, the other half of the prior
disagreement, is resolved — it is fitted (`DS3231MZ+TRL`, `C107410`).

*Severity note:* unlike R74, a wrongly-fitted SW6 is harmless — it would actually cancel MCU-01 by giving
the board a real BOOT button. The value of the item is consistency: the fix for HMI-V01 should cover SW6 in
the same edit, and the NextPCB post-upload checklist should stop being the only place SW6 is protected.

*Recommendation:* set `exclude_from_bom` on SW6 at the same time as R72/R74, so all DNP parts are handled
one way and no importer can leak any of them.

### REC-C-03 — the deep-sleep budget assumes TI's LDO quiescent current, and fabs substitute the brand — **LOW**

*Refs:* U3 `TLV75533PDBVR` / `C404027`. Prior source: `NEXTPCB_REV0_NOTES.md` §2, matched-BOM check:
"Third-party brands attached to generic parts (`U3` TLV75533PDBVR as 'DYW' rather than TI … `U3` matters
because the sleep-current budget assumes TI's ~25 µA."

*Evidence:* `evidence/sch/bom_ungrouped.csv:161` specifies TI as the manufacturer, and PWR-03 builds the
~73 µA typical deep-sleep budget (and the ~21 µA of recoverable savings) on that part's datasheet. The new
audit's BOM-09 raises untraceable clone-market silicon for the **charge and protect** subsystem (U5, Q1)
but never extends the argument to U3, and no project document says the LDO's brand is budget-critical. A
real fab has already offered a "DYW"-branded part against this line.

*Recommendation:* one line in the BOM notes and in HARDWARE.md §sleep: "U3 must be the genuine TI part —
the sleep budget depends on its ~25 µA Iq; reject brand substitutions on this line." Cheap insurance, and it
turns a footnote in a fab-order log into a design constraint.

### REC-C-04 — CR2/CR3 cannot hold the 3V3 or battery rails inside the abs-max of what they protect — **LOW**

*Refs:* CR2, CR3 = TI `TSD05CDYFR` (`C5299440`, SOD-323), on 3V3 and on the J6 battery rail. Prior source:
`component-review.csv`: "5 V TVS on 3.3 V rail: no normal-DC stress; surge clamp is not a precision 3.3 V
overvoltage limit" / "5 V TVS on ≤4.2 V battery rail: … not a battery overcharge controller."

*Evidence:* the new audit makes exactly this argument twice — USB-04 ("CR1 clamp voltage is above the
absolute maximum of the parts it protects", MEDIUM) and BOM-10 / LED-V01 / HMI-16 (D3 SMAJ26A clamps at
42.1 V above the TPS923610's 32 V VOUT abs max) — but never applies it to CR2/CR3, the two clamps that sit
on the **user-accessible expansion header**. A 5 V-standoff SOD-323 TVS clamps in the 9–10 V region at
rated peak pulse current; the 3V3 loads behind CR2 have a 3.6 V absolute maximum. So a surge that CR2
"survives" still puts several times abs max across the ESP32 and the RTC for the duration.

*Recommendation:* treat it the way the new audit treats USB-04 — document it as a known limit rather than
respinning. A line in HARDWARE.md §protection saying the header TVS diodes are surge clamps and not rail
limiters, plus a note that J6 is not hot-plug-rated, is proportionate for a prototype. If a revision
happens, a lower-standoff part or a series element on the header pins is the real answer (and would also
help HMI-01 and HMI-V04).

### REC-C-05 — the documented button mechanics do not hold for the NextPCB build route — **LOW**

*Refs:* SW1–SW5, SW7–SW11; `fabrication/nextpcb_substitutes.csv` (ALPS `SKHLLAA010` for `SW*`). Prior
source: `NEXTPCB_REV0_NOTES.md` §2: "ALPS drawing No. 3 gives the same land … Differences: catalog depth
7.22 mm vs 6 mm for the TS365ZJ, and 0.98 N vs about 2.5 N. Check the stem clearance and the feel."

*Evidence:* the new audit's mechanical numbers are all computed for the MJTP1117 — MEC-08 (bottom row
+1.95 mm, side buttons +0.95 to +1.21 mm protrusion), MEC-07 (±0.25 mm of plan-view daylight to the panel
edge), MEC-11 (front-mount option needs 4.3 mm of cavity). BOM-13 notices that "three documented build
routes give three different button feels spanning 2.5:1" but stays on actuation force and cycle life; it
does not carry the **+1.22 mm body depth** forward into the protrusion and enclosure figures. Anyone
building the NextPCB variant and cutting a case to the new audit's numbers gets eight buttons that stand
more than a millimetre proud of the documented value.

*Recommendation:* add the depth delta to the Reason column of `nextpcb_substitutes.csv` (BOM-14 already
asks for the same treatment on L1), and add one sentence to the enclosure section: the MEC-07/MEC-08
protrusion figures apply to the MJTP1117 build only; re-derive them if the ALPS substitute is used.

---

## 5. New in this audit — the BLOCKER and HIGH findings vs corpus C

| New ID | Sev | Known to corpus C? | Where |
|---|---|---|---|
| LED-01 | BLOCKER | **No — genuinely new** | Corpus C's only paste work is an old-vs-new gerber differ (`gerber-geometry-comparison.json`, `B_Paste` 607 = 607, `geometry_equal: true`); both copies share the omission. `component-review.csv` reviewed J2/J3/J4 electrically only |
| BOM-01 | HIGH | No | R14 stock/orderability was never examined; corpus C reviewed R14 only for wattage (= new BOM-11) |
| DOCS-01…09 | HIGH ×9 | No | Corpus C contains no documentation review of any kind. Its entire scope is design data and one fab-order log |
| HMI-01 | HIGH | **Partly** | `component-review.csv` J6: "high voltage LED rail and boot straps exposed; do not treat as generic GPIO header". Corpus C named the exposure; the new audit names the missing fuse/PTC on raw P+ |
| LAY-01 | HIGH | No | Corpus C measured no slot widths; `geometry_review.py` compared gerber objects, not manufacturability minima |
| MEC-01 | HIGH | No | Corpus C has no flex-slot or panel-mechanics analysis at all |
| MEC-02 | HIGH | No | The "cut for smaller displays" line is absent from corpus C |
| MEC-23 | HIGH | **Partly, indirectly** | `NEXTPCB_REV0_NOTES.md` establishes the 13 THT parts and the ~75–80 hand-soldered joints per board, but never asks what the protruding leads do to the panel-side flatness |
| SD-V01 | HIGH | No | `sd-mechanical-comparison.json` studied peg holes and land overlap; the insertion corridor vs the battery cut-out is new |

So of the 16 HIGH/BLOCKER findings, **one is partly anticipated (HMI-01), one is indirectly touched
(MEC-23), and 14 are new to corpus C** — nine of them because corpus C had no documentation scope and four
because it had no mechanical/manufacturability scope.

---

## 6. Blind spots

**Corpus C's blind spots.** It is a verification harness, and it verifies what it was pointed at. It has
no documentation review, no enclosure or flex mechanics, no manufacturability minima (slot width, annular
ring, silk size, mask dam), no layout-quality analysis (pour fragmentation, thermal relief, return paths),
and no pad-vs-aperture completeness check — which is why LED-01 slipped through a corpus that
*did* open the paste gerber. Its comparison methods are self-referential in a way that hides shared
defects: old-gerber vs new-gerber, CPL vs CPL, BOM vs schematic. Every one of those passes when both sides
carry the same fault. It also carries component data that was already going stale as the design moved
(D4–D6, Q4, L1, L2, J5, D2), so several of its "open" rows are answers to a board that no longer exists.

**The new audit's blind spots, seen from here.** It is analysis-only and has no field channel: everything
corpus C learned by actually uploading to a fab — that an importer silently merges MPN-matched lines and
drops DNP, that a DFA tool renders THT bodies from its own library and ignores your rotations, that stock
substitutes arrive under third-party brands, that $400 is the real number — the new audit can only
approximate or misses. It does not date its own findings, so it cannot tell the owner that FAB-07 and
FAB-08 are *regressions from a specific recent commit* rather than long-standing debt. It applies its own
best arguments unevenly: the "this TVS clamps above what it protects" analysis is made three times (CR1,
D3) and never extended to CR2/CR3; the "DNP without exclude_from_bom" analysis is made for R72/R74 and
never extended to SW6; the clone-silicon-sourcing argument is made for U5/Q1 and never for U3. And it lost
one thing corpus C had: a *measured physical sample* of the FT01C front-light flex, which is the only real
evidence anyone has about the J3 pinout.

**Net.** Corpus C's recommendations were largely implemented, its remaining open items are minor, and it
adds field facts plus a DRC/ERC baseline that the new audit cannot generate. The new audit supersedes it
almost everywhere else. The five recovered items above are all LOW on the owner's prototype standard —
none of them should hold up a spin. LED-01 should.
