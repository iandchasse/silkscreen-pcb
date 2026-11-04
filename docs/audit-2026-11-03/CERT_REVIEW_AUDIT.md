# Audit of the PCBA certification-readiness review (2026-11-03)

**What was audited:** `SILKSCREEN_PCBA_CERT_REVIEW.md` ("SilkScreen PCBA: certification-readiness review, with PocketMage V3.6 as reference", 2026-11-03).

- **Where it lives:** in another agent session's files folder, not in this repo.
- **Board it describes:** the board as saved at 18:41.

**What this audit does:**

- re-measures every board claim on the current `1.03` working copy, which now includes the later reference-designator cleanup and the T10/T17/T20 fixes ([TRACE_AUDIT.md §1f](TRACE_AUDIT.md#1f-layout-fixes-applied-after-the-review-2026-11-03));
- checks whether each proposal fits the real layout;
- checks the review's outside claims against primary sources;
- adds what the review missed.

**What it changes:** nothing when written; board, schematic and production files were untouched. Later the same day the owner had the cheap set applied: A1, A2, B2, B5, B7's return vias and the X2/X3/Z1 wording (section 6). The other items are recorded in [NEXT_REVISION.md §9](../NEXT_REVISION.md#9-certification-readiness-items-for-later-recorded-2026-11-03).

Method: board geometry from [bench-theory/export_copper.py](bench-theory/export_copper.py) (KiCad 9 Python), measured with shapely. Sources are in section 5.

## 1. Summary

### 1.1 Verdict per review item

| ID | Proposal | Review's facts | Fits this board? | Verdict | When |
|---|---|---|---|---|---|
| A1 | USB-C shell straight to GND (`R1` → 0 Ω) | Confirmed | Yes: a parts-list change on an existing 0 Ω line | **Do** | 1.03: **applied** as a direct bond, with no `R1`/`C1` (section 6) |
| A2 | Revision and date on the silkscreen from the title block | Confirmed: none of the 52 board texts carries a revision | Yes | **Do**, together with the 1.03 title-block bump | 1.03: **applied** (section 6) |
| A3 | Ship with the cell unplugged | Moot for a board sold without a cell (no coin cell on the board either) | — | Documentation only, if a cell ever ships | docs |
| A4 | 1.0–1.2 mm board | The loop-area estimate is fair | Needs case, button, USB-stake and stiffness checks | **Not now.** Only if a pre-scan shows too little margin | later |
| B1 | Clear pour, tracks and parts beside the antenna | Confirmed, and understated: KiCad 9's own `ESP32-S3-WROOM-1` keep-out is 48 × 21 mm, and eleven parts sit inside it here (section 3.3) | Partly: a pour clear-out of the notch arms plus small moves | **Partly do** now; the full clearance needs `SW5` and the frontlight block moved | 1.03 / next |
| B2 | GND vias at `U4` pins 1 and 40 | Confirmed: 5.56 and 2.45 mm | Yes: legal spots 0.15 mm from each pad | **Do** | 1.03: **applied** (section 6) |
| B3 | Frontlight boost and UART pads 15 mm from the antenna | Distances confirmed. Espressif names UART lines and test points, not switchers | Re-layout for the frontlight block; the test pads are easier | **Measure first** (range/throughput with the light on and off) | later |
| B4 | Panel FPC capacitors at their `J2` pins | Distances confirmed (5.3–17.3 mm) | No: no legal spots without moving parts (TRACE_AUDIT T5/T9) | **No** for 1.03; check `EINK_3V3` ripple on the first boards | later |
| B5 | `C33` (0.1 µF) closer to `U4` pin 2 | Confirmed: 6.05 mm | Yes: swap `C33` and `R7` | **Do** (cheap) | 1.03: **applied** (section 6) |
| B6 | No B.Cu pour under `L1` | Confirmed: 9.2 mm² | Yes: one rule area | Optional (small effect) | not applied; [NEXT_REVISION §9](../NEXT_REVISION.md#9-certification-readiness-items-for-later-recorded-2026-11-03) |
| B7 | Plane-like F.Cu: shorter F.Cu runs, return vias, USB on one layer | Confirmed: 1,541 mm on F.Cu; 25 of 30 fast-signal vias have no GND via within 1.5 mm | Partly: 8 return vias fit; the USB pair can't change (T18); dropping `J6`'s LED copies removes a feature | **Do the 8 return vias**; the rest is the maker's call | 1.03: 8 vias **applied** (section 6) |
| C1 | NTC on TP4056 `TEMP` | Confirmed: `TEMP` is grounded. The divider maths checks out | Needs a part and a route; no free spot at the cell bay (section 3.6) | **Do, high priority**: the test labs' committee does not accept a rated-ambient limit for portable equipment | 1.03 decision |
| C2 | Ferrite bead feeding `U4` | — | Yes | **No**: Espressif recommends 22 µF + 0.1 µF but no bead; the rail is LDO-fed | — |
| C3 | 0.1 µF on `VBUS_PRE_FUSE` at `J1` | — | Yes | Defer: needs the hot-plug study first | later |
| D1–D3 | Charge inhibit, switched rails, second I²C | — | No spare GPIO | Defer | later |
| X1 | TRACE_AUDIT T12 text | Correct | — | Already fixed (TRACE_AUDIT §1e) | done |
| X2 | HARDWARE.md §16: "both boost inductors and every connector" on the far side | Correct: `L2` 6.5 mm, `J7` 10.7 mm, `J3` 12.7 mm from the antenna area | — | Fix in the 1.03 docs pass | **applied** (section 6) |
| X3 | HARDWARE.md §3.1 shield wording ("breaking ground loops") | Correct: there is no chassis | — | Rewrite with A1 | **applied** (section 6) |

### 1.2 What the review missed

| ID | Finding | Why it matters | Fix |
|---|---|---|---|
| Z1 | The README tells builders the surface finish is "your choice" | CE needs RoHS. JLC's quote page still offers "HASL(with lead)", which JLC itself says "does not comply with RoHS" (its default is now OSP) | Name OSP, lead-free HASL or ENIG in the ordering steps. ENIG also suits the 0.5 mm-pitch parts (`J2`–`J4`, `U10`). **Applied** (README "Step 2", section 6) |
| Z2 | The module's FCC grant excludes portable use | Grant note: "Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093". KDB 996369 D01 §5: a host closer than the granted separation needs a C2PC or a Change in ID. The repo's certification plan handles the exposure maths (§2.3, firmware TX cap) but not this filing route | Confirm the route with a TCB/lab before planning lab work: Espressif's C2PC, or the host's own FCC ID |
| Z3 | The board's `U4` antenna keep-out (21 × 20 mm) is an older, smaller copy of KiCad 9's (48 × 21 mm) | Updating the footprint, or adding a board rule area of that size, would flag eleven parts. It is the concrete form of B1/B3 | Decide together with B1 |
| Z4 | E-labelling is allowed, but not alone | FCC KDB 784748 D02 lists "E-readers" as eligible for e-labels. A physical label on the product or its packaging is still required at import and sale (§4.5). ISED allows the same (RSS-Gen Annex B) | Plan the "Contains FCC ID / Contains IC" strings for the screen *and* the box |
| Z5 | UART0 TX has no series resistor (`U4` pin 37 → `TP2` directly) | Espressif: "connect a 499 Ω series resistor to the U0TXD line to suppress harmonics", and keep UART lines and test points away from the antenna | Cheapest: no UART0 logging in production firmware. Hardware: a series resistor (new part) |
| Z6 | C1's NTC is a JLC Extended part | No NTC exists in JLC's Basic library | Budget the $3 Extended fee (for example Murata NCP18XH103F03RB, `C13564`) |
| Z7 | An off-board NTC fails safe, but badly | With C1's divider fitted and no NTC connected, `TEMP` sits at 120 / 125.6 = 96 % of VIN. That is above the 80 % limit, so the board never charges | If the NTC is on a lead or in the pack, document it, or provide a jumper/footprint for a fixed resistor |

### 1.3 Suggested plan

**1.03, cheap and contained** (applied on 2026-11-03 except B6, section 6):

- A1 (`R1` = 0 Ω);
- A2 (revision text plus the title-block bump);
- B2 (two GND vias);
- B5 (swap `C33`/`R7`);
- B7's 8 return vias;
- optionally B6;
- Z1 (README finish wording);
- X2/X3 (wording).

**1.03 decisions needed:**

- **C1:** where the NTC goes (section 3.6).
- **B1 scope:** a pour-only clear-out of the notch arms now, or the full keep-out later.

**Next revision, or after measuring:**

- B1 in full, and B3 (move `SW5` and the frontlight block);
- B4;
- A4;
- C3;
- D1–D3.

**Certification process, not layout:** Z2 (filing route for portable use), Z4 (labels), RoHS documentation.

## 2. Board facts re-measured

| Item | Review | Now | Note |
|---|---|---|---|
| Antenna area over air | 97 % | 97.4 % | Notch at x 44.26–50.60, y 93.3–112.0 |
| GND pour nearest the antenna area | 1.0 mm | 0.31 mm under the module body (x ≥ 51.06); about 1 mm in the notch arms | Measurement convention |
| Pads within 5 mm of the antenna area | `R4` 2.1, `C27` 2.5, `R7` 3.1, `SW5` 3.2, `C31` 4.2, `F3` 4.3, `C32` 4.8 mm | `R4` 1.6, `C27` 1.9, `SW5` 2.3, `R7` 2.5, `C31` 3.5, `F3` 3.8, `C32` 4.0 mm | Measured pad edge to antenna area |
| Tracks within 5 mm | `BUTTON_ADC_1`; the F.Cu 3V3 at x 53.6 | The same, plus `ESP32_EN` (B, 3.6 mm) and `BUTTON_ADC_2` (F, 3.4 mm) | 3V3 F.Cu at x 53.6, y 96.3–110.5 is 25.8 mm of track within 5 mm |
| GND via nearest `U4` pins 1 / 40 | 5.56 / 2.45 mm | 5.56 / 2.45 mm | |
| `C32` / `C33` from `U4` pin 2 | 4.61 / 6.56 mm | 3.83 / 6.05 mm pad edge (4.49 / 6.50 mm centre) | `R7` (EN) is the nearest part, at 2.11 mm |
| Panel caps from their `J2` pins | 6.3–18.6 mm | 5.3–17.3 mm | `C17` at pin 5 is the farthest; `C22` is 12.1–12.4 mm |
| `L1` courtyard: B.Cu / F.Cu GND | 9.2 / 23.3 mm² | 9.2 / 23.3 mm² | `L2`: 0.7 / 7.0 mm² |
| F.Cu track | 1,541 mm, 49 nets | 1,541 mm, 49 nets | `C-` 167, `W-` 150, `LED_SW` 139, 3V3 134, `I2C_SCL` 118, `I2C_SDA` 112 mm |
| GND fill F / B | 73.5 / 50.9 % | 73.2 / 50.7 % | The `F3` keep-out (T20) |
| `C-` from the right edge | 0.48 mm | 0.746 mm | T10, after the review |
| TRACE_AUDIT T12 wording (X1) | wrong | fixed | |

## 3. Notes on the items

### 3.1 A1: shell to GND

**Why the RC is a problem.**

- **Charge sharing:** an 8 kV contact discharge from the IEC 61000-4-2 network (150 pF) shares its charge with `C1` (1 nF), so the shell rises to about 1 kV. That lands across a 50 V 0603 MLCC (CL10B102KB8NNNC).
- **Arcing:** that 1 kV also stands between the shell and the receptacle's own signal contacts.
- **No benefit to keep:** there is no chassis or earth to isolate. Cable ground already joins board ground through `J1`'s A1/A12/B1/B12.

**The change:**

- **Now (parts list only):** `R1` becomes the existing 0 Ω line `C21189`. `C1` ends up shorted; leave it or set it DNP.
- **Later:** take the shell slots straight into both pours. Done on 2026-11-03 in place of the 0 Ω (section 6).
- **Docs:** HARDWARE.md §3.1 "Shield handling" (X3). NEXT_REVISION §7's "`C1` as a 1–2 kV MLCC" becomes moot.

### 3.2 A2: revision on the board

- **What to add:** `Rev ${REVISION} · ${ISSUE_DATE}` on B.Silkscreen. KiCad expands it from the title block, which still says 1.02 / 2026-10-22.
- **Do it with the bump:** the 1.03 bump is an open decision (REV_1_03_STATUS §11).
- **Labels:** the FCC/IC strings belong on the screen and the box (Z4), not necessarily the board.

### 3.3 B1 and Z3: the antenna clearance

**What Espressif says** (ESP32-S3 Hardware Design Guidelines):

- "place the module's on-board PCB antenna outside the base board, and the feed point of the antenna close to the edge of the base board".
- Failing that, "cut off the base board on both sides of the antenna and below it". The keep-out drawing extends the clearance at least 15 mm past the module edge.
- "A clearance of at least 15 mm is recommended in all directions" inside the housing.
- "sufficient ground copper and dense ground vias should be placed on the base board near the antenna".

**What the library encodes.** KiCad 9's footprint carries a 48 × 21 mm keep-out: the 6 mm antenna band plus 15 mm past each side of the module. It forbids tracks, vias, pads, pour and footprints.

**On this board** that band is x ≤ 50.75 from y ≈ 78.5 to 126.5:

- **Inside it:**
  - `SW5`, `R35` and `R36` above the notch;
  - `F3`, `R4`, `L2`, `U10`, `C9`, `R37`, `Q6` and `R73` below it;
  - tracks from 16 nets and 10 vias, over 193 mm² of board.
- **What we have instead:** the board's own copy (21 × 20 mm) covers only the antenna and 1 mm around it.

**The notch is the right idea but narrow.** Its walls are 0.15 and 0.45 mm from the module's sides, with GND pour about 1 mm away on both layers.

**Options:**

1. **Pour clear-out of both notch arms (about 5 mm), as the review proposes.**
   - Upper arm: about 16 mm² of pour per layer, and `SW5`'s GND pad then needs a track.
   - Lower arm: about 9 mm² per layer, already thinned by the `F3` keep-out. Its two stitching vias go, `R4`/`C27` move a few mm to +x, and `BUTTON_ADC_1` and the F.Cu 3V3 run at x 53.6 are re-routed.
   - This is a contained job.
2. **The full 15 mm clearance.**
   - Move `SW5` (whose position the case fixes) with `R35`/`R36`, and the frontlight block (`F3`/`L2`/`U10`/`C9`/`R37`/`Q6`/`R73`) out of the band, or widen the notch.
   - That is a re-layout of the left edge and needs the enclosure; next revision.

Espressif also asks that "the final end product should be tested for throughput and communication range". Doing that on a current board tells whether option 2 is worth it.

### 3.4 B2, B5, B7: the cheap layout items

- **B2:**
  - Pin 1: legal 0.3/0.6 mm via spots sit 0.15 mm from the pad, at (51.79, 92.05) or (51.79, 94.95).
  - Pin 40: at (51.84, 110.05).
  - These spots are in the F.Cu pour but not the B.Cu pour, so each via needs a short stub to its pad. All are outside the footprint keep-out (x ≥ 51.3).
- **B5:**
  - The 3V3 feed already runs down through the column's pads (`C33` → `C32` → `R7` → pin 2), with EN alongside under the part bodies.
  - Swapping `C33` and `R7` brings the 0.1 µF from 6 mm to about 2 mm from pin 2.
  - The cost: `R7`/`C5` (EN, 10 kΩ / 1 µF) end up 6–8 mm from pin 3, which is no worse than `C5` today.
- **B7, return vias:**
  - 30 vias on SD, USB, `/GDR` and I²C; 5 already have a GND via within 1.5 mm.
  - 8 of the other 25 have a legal spot within 1.2 mm in both pours.
  - The rest are boxed in. The USB pair stays as it is (T18).

### 3.5 B3, B4, A4: not for 1.03

- **B3.** Espressif's text names "UART signal lines (including traces, vias, test points…)" and asks for a 499 Ω series resistor on U0TXD (Z5). It says nothing about switching regulators near the antenna. The frontlight boost (7–10 mm away) is a reasonable suspect for desense, but measure it first: compare range and throughput with the light on and off.
- **B4.** Section 1e of TRACE_AUDIT found no legal spot closer than about 11 mm for `C22`, and none near `D5` for `C14`. The column's other capacitors are 5–17 mm from their pins. Moving them all is a re-layout of the e-paper section. The panel spec only asks that VCI be free of "ripple and noise", and the first-board check (NEXT_REVISION §6) measures exactly that.
- **A4.** The estimates (−2.5 dB at 1.2 mm, −4.1 dB at 1.0 mm) cover board-level loops only, not cable common-mode. What a thinner board would change:
  - the button plunger height (HARDWARE.md §16);
  - stiffness under the side buttons;
  - the USB4105 shell-stake fit (GCT sells it in several stake lengths; check the fitted variant);
  - the PTC thermal calibration (BENCH_THEORY used 1.6 mm).

  Keep it in reserve for a failed pre-scan.

### 3.6 C1: charge temperature

**Why it is needed.** IEC 62368-1 M.4.2, as quoted in ETICS OSM-EE 21/1:

- "The battery charging circuit shall stop charging when the temperature of the battery exceeds the highest specified charging temperature…"
- The requirement holds under normal, abnormal and single-fault conditions.
- For portable equipment, "there shall be abnormal testing related to the upper and lower limits of ambient temperature".

With `TEMP` grounded, the TP4056 does neither, so this is the item most likely to fail a safety evaluation.

**The circuit.** TP4056 REV_2.4 trips below 45 % (min 43 %) and above 80 % (max 82 %) of VCC.

- The review's divider: 5.6 kΩ to `USB_VBUS`, 120 kΩ to GND, 10 kΩ NTC to GND.
- It gives about 0.5–0.9 °C to 45.5–45.9 °C for B = 3380–3435, and 62 % at 25 °C. I checked the maths.
- The 0.15 s filter time appears only in the 2008 datasheet.

**Where the NTC goes.** It has to see the cell, which sits in a board cut-out:

- **On-board:** the bay edge (y 67.5) is too crowded. The only free 0603 spot within 4 mm of the cell is (86.5, 61.5) on the arm, about 35 mm of trace from `U11`'s `TEMP` pin. That long, high-impedance trace would want the optional 0.1 µF at `U11`.
- **A 3-wire pack (JST-PH 3-pin with pack NTC).** Best thermally, but it conflicts with 2-wire bring-your-own cells.
- **An NTC on leads, taped to the cell.**

With either off-board option, Z7 applies: no NTC means no charging.

**Part.** JLC has no Basic NTC. Candidates: Murata NCP18XH103F03RB (`C13564`, 10 kΩ ±1 %, B 3380), Sunlord SDNT1608X103F3435FTF (`C525660`), TDK NTCG163JF103FT1S (`C406719`).

### 3.7 Z2: the module grant and portable use

**The grant notes.** For FCC ID 2AC7Z-ESPS3WROOM1:

- "Single Modular Approval".
- "The integrator … should refer to guidance in KDB 996369".
- "Separate approval is required for all other operating configurations, including portable configurations with respect to 2.1093".

**The plan's maths is right but incomplete.** The repo's [CERTIFICATION_AND_TEST_PLAN.md §2.3](../audit-2026-10-15/CERTIFICATION_AND_TEST_PLAN.md) already computes SAR-exemption thresholds for portable use: 2.72 mW at 5 mm. It proposes a firmware TX-power cap. That settles the exposure question, but the grant still doesn't cover a portable host. KDB 996369 D01 §5 points to a Class II permissive change by the grantee, or a Change in ID.

**Next step.** Ask a TCB or test lab which route applies, and whether Espressif offers the C2PC, before budgeting the lab work.

## 4. Documentation fixes queued

**Apply with the 1.03 docs pass** (REV_1_03_STATUS §9). All three were applied on 2026-11-03 (section 6):

- **HARDWARE.md §16 (X2):** replace "Everything on the board — the cell, both boost inductors and every connector — is already on the far side" with the measured distances: the frontlight boost is 6.5–10 mm from the antenna area, `J7` 10.7 mm and `J3` 12.7 mm.
- **HARDWARE.md §3.1 (X3):** rewrite "Shield handling" after the A1 decision.
- **README "Step 2: order the bare board" (Z1):** "Surface finish … your choice" becomes: OSP, lead-free HASL or ENIG; not HASL with lead.

## 5. Sources

- **Espressif**, ESP32-S3 Hardware Design Guidelines, "General Principles of PCB Layout for Modules", RF and UART sections: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
- **Espressif**, ESP32-S3-WROOM-1 datasheet v1.8, Fig. 9-1 (22 µF + 0.1 µF on VDD33; EN 10 kΩ / 1 µF).
- **FCC**:
  - 47 CFR 15.212(a)(1)(vi)(A) and 2.935: https://www.ecfr.gov/current/title-47/section-15.212 and https://www.ecfr.gov/current/title-47/section-2.935
  - KDB 784748 D02 v02r01 §2 and §4.5–4.6.
  - KDB 996369 D01 §3 and §5, D03 §2.8–2.11, D04 §2.0 and §3.4.
- **Module grant notes and modular-approval letter** for 2AC7Z-ESPS3WROOM1, read through the fccid.io mirror: https://fccid.io/2AC7Z-ESPS3WROOM1
- **ISED**, RSS-Gen Issue 6, §4.5, §9.4.4.2 and Annex B.
- **TP4056 REV_2.4** (NanJing Top Power), pp. 5, 7 and 10–11: https://www.lcsc.com/datasheet/C16581.pdf
- **ETICS** OSM-EE 21/1 (M.4.2) and OSM-EE 25/4 (battery temperature limits): https://www.etics.org/doc/doc_17812_main1_OSM-EE%2021%201.pdf and https://www.etics.org/doc/doc_20360_main1_OSM-EE%2025%204.pdf
- **JLCPCB**:
  - quote page (default finish OSP, 2026-11-03);
  - surface-finish help, on leaded HASL and RoHS: https://jlcpcb.com/help/article/jlcpcb-surface-finish
  - parts API (no Basic NTC; the three candidates above).
- **IATA** Lithium Battery Guidance Document 2026, §E.08; 49 CFR 173.185(b).
- **Repo:**
  - [HARDWARE.md](../HARDWARE.md) §3.1, §13, §16;
  - [CERTIFICATION_AND_TEST_PLAN.md](../audit-2026-10-15/CERTIFICATION_AND_TEST_PLAN.md);
  - [TRACE_AUDIT.md](TRACE_AUDIT.md) §1e–1f;
  - [BENCH_THEORY.md](BENCH_THEORY.md).

## 6. Applied on 2026-11-03

The owner asked for every cheap fix and for the rest to be recorded for reference, which is now [NEXT_REVISION.md §9](../NEXT_REVISION.md#9-certification-readiness-items-for-later-recorded-2026-11-03).
B6 was left out: its effect is small either way, because the pour under `L1` also shields.
Everything was scripted on a scratch copy (KiCad 9 Python), checked, and copied back with KiCad closed.

| ID | Change | Result |
|---|---|---|
| A1 | `J1`'s shell (pin S1) on the GND net in the schematic, with a note. `R1`, `C1` and the shell net's 25.6 mm of 0.2 mm track are gone. The four plated shell tabs sit in both GND pours on thermal spokes, so they still solder easily. This replaced a first pass that kept `R1` as a 0 Ω: the thin track to it came to roughly 3–5 nH, about 100–200 V for a nanosecond during an 8 kV strike and about 60 Ω at 2.4 GHz. The pour bond is well under 1 nH | The shell is bonded to both ground planes at the connector edge. Two fewer parts |
| A2 | Both title blocks: 1.02 / 2026-10-22 → 1.03 / 2026-11-03. On the back silkscreen, `Rev ${REVISION} ${ISSUE_DATE}` at 1.0 mm / 0.15 mm, centred at (87.09, 138.75), right-aligned with the pinout notes above it | Prints "Rev 1.03 2026-11-03" and follows later title-block bumps |
| B2 | GND vias at (51.79, 94.95) and (51.84, 110.05), under the module, each with a 0.4 mm stub into `U4` pin 1 / pin 40 | Nearest GND via, centre to centre: pin 1 5.56 → 1.52 mm, pin 40 2.45 → 1.50 mm |
| B5 | `C33` and `R7` swapped. The 3V3 via moved from (53.34, 91.76) to (52.64, 91.95), below `C33` pad 1, and feeds pin 2 from there. `EN` runs down the column between the pads, with a stub into `R7` pad 2, then turns under `C33` into pin 3. `C33`'s ground pad has a 0.3 mm stub to a new GND via at (55.45, 91.01). `R7`'s and `C33`'s references sit to the left of their parts, as `C33`'s did | `C33` pad to pin 2: 6.05 → 1.02 mm, edge to edge. `R7`/`C5` are now 6.5/8.8 mm from pin 3 (centres), which the slow EN RC doesn't mind |
| B7 | 8 GND return vias, 0.75–1.15 mm from a fast-signal via: `DN` (95.63, 107.98); `SD_DAT2` (66.51, 88.82); `SD_CLK` (55.84, 79.52); `I2C_SDA` (92.59, 53.70), (66.08, 132.51) and (92.40, 59.10), the last under `D3`'s body like the `I2C_SDA` via itself; `I2C_SCL` (67.49, 133.96); `/GDR` (90.03, 117.10), between `Q4`'s gate and source pads | Each sits inside both GND pours. Not done: two spots under `J7`, skipped because the card slides over them, and 15 vias with no legal spot |
| X2, X3, Z1 | [HARDWARE.md](../HARDWARE.md) §16 (antenna paragraph) and §3.1 (shield handling); README "Step 2" (surface finish) | — |

**Checks:**

- **DRC with schematic parity:** 0 errors, 0 unconnected, 0 parity issues. Re-run on the files copied into the repo.
  - The warnings are the same 49 as before plus one `starved_thermal`: `J1`'s top-left shell tab gets one spoke on F.Cu, where the `DP` track, the four-track bus and the peg pad box it in. It has full spokes on B.Cu and is plated through, so it is bonded on both layers. A solid connection would only make the tab harder to solder.
  - The first run flagged `R7`'s moved reference over `C28`'s pad; moving it cleared that.
- **ERC:** unchanged at 46.
- **Pours:** all 11 new GND vias touch both pours.
- **Teardrops:** 15 on the re-routed `C33`/`R7`/`U4` pin 2–3 tracks and at the old 3V3 via were removed. The 8 on the deleted shell track went with it (851 → 828). The designer's teardrop run on 2026-11-03 restored the 15 and added ones on the new stubs; the board then had 862.
