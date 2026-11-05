# Triage of the independent board review (2026-11-03)

**What this is.** The owner-side triage of [BOARD_REVIEW.md](BOARD_REVIEW.md). The reviewer worked from the design files
and datasheets only, by design. This triage adds the context the reviewer did not have: the earlier audits, the
owner's decisions, the case 1 failure history and the bench plan. Each finding gets my severity, a proposed fix, its
difficulty, and a verdict on whether it is worth addressing. **Status:** the four do-now fixes are applied, and the rest
is filed (section 4). Section 5 updates the status on 2026-11-04, after the BQ21040 charger swap closed H-1.

**Scales.**

- **Severity** reflects consequence × likelihood for this product, plus the certification impact. The product is a
  handheld e-reader on one protected Li-ion pack, built and modified by hobbyists. Levels: Critical, High, Medium, Low,
  Info.
- **Difficulty:**

  | Level | Meaning |
  |---|---|
  | 1, trivial | Text or a part value; no copper |
  | 2, easy | A small, contained copper or BOM change, or a firmware change |
  | 3, moderate | New parts with local re-layout, or a circuit change |
  | 4, hard | A new IC or connector, a block re-layout, or a dependency on the enclosure |
  | 5, very hard | An architecture change |

- **Worth score** = severity weight (Critical 5, High 4, Medium 3, Low 2, Info 1) × ease (6 − difficulty).

  | Score | Verdict |
  |---|---|
  | ≥ 15 | Do now |
  | 9–14 | Worth doing when convenient |
  | 6–8 | Decide on data (bench or pre-scan first) |
  | ≤ 5 | Document or accept |

  Overrides are marked and explained. A safety or compliance blocker is required whatever its score.

## 1. Summary

| ID | Reviewer | Mine | Proposed fix | Diff. | Score | Verdict |
|---|---|---|---|---|---|---|
| **H-2** | High | **High** (cut boards) | Pour-free areas about 1 mm around P+ (F.Cu) and 3V3 (B.Cu) where they cross the cut line | 2 | 16 | **Do now** |
| **M-6** | Medium | **Medium** | Back-silk note: "unpopulate F4,R44,46,52" (`R42` became `F4`) | 1 | 15 | **Do now** |
| **L-1** | Low | Low | Schematic note: `R6` 10k → about 0.10–0.13 A. README and HARDWARE.md go in the docs pass | 1 | 10 | **Do now** |
| **L-14** | Low | Low | Second GND via at `U10` pin 4: a legal spot exists at (48.76, 123.10). No room at `J2` pin 17, which stays as is | 2 | 8 | **Do now** (override: cheap and harmless, alongside the others) |
| **H-1** | High | **High** (blocks certification) | NTC at the cell on `TEMP`, plus a firmware-controlled charge-enable override for a charge timer | 4 | 8 | **Required before selling or certifying** (override); next revision |
| **M-5** | Medium | **Medium** | Bench: does a pack in protection lockout wake on USB? If not, a USB-time override of the cell detector | 1 → 3 | 15 → 9 | **Bench now**; fix in the next revision, together with H-1 |
| **M-2** | Medium | Medium | Firmware: don't overlap Wi-Fi TX with SD writes or a refresh; less TX power; no Wi-Fi below about 3.7 V. Hardware (TLV757P, 1 A, same footprint) only if the bench shows the LDO limiting | 2 | 12 | **Firmware**, plus the planned bench measurement |
| **M-1** | Medium | **Low** with the brightness cap | Keep the 0.10 A PTC and firmware's 50 % cap (100 % only above about 3.8 V). **Reject the reviewer's 0.20 A PTC**: it would not trip on the case 1 fault from the battery | 1 | 10 | **Firmware** (already planned as F6), plus bench (planned) |
| **M-3** | Medium | Medium | Range and throughput test, then decide on the notch-arm pour clear-out or the full keep-out | 3–4 | 9 | Bench first (as already decided) |
| **M-4** | Medium | **Low** | Document "5 V USB-C chargers only" now; a 5 V over-voltage switch ahead of `U2`/`U11` in the next revision | 4 | 4 | Document now; next revision |
| L-18 | Low | Low | Firmware puts the touch controller in hibernate before deep sleep | 1 | 10 | **Firmware** |
| I-6 | Info | **Low** | Firmware shuts down at ≥ 3.3 V, with a low-battery screen (F7) | 1 | 10 | **Firmware** |
| L-4 | Low | Low | Read `USB_STAT` with VBUS absent on the bench; firmware decodes what it sees | 1 | 10 | Bench + firmware |
| L-5 | Low | Low | `R36` 68k → 47k and `R35` 33k → 27k, with firmware thresholds to match | 2 | 8 | Only together with a firmware update |
| L-2 | Low | Low | Coincident-peak and trip measurement | 1 | 10 | Bench (already planned) |
| L-3 | Low | Low | Weak source and long cable on the bench. If the mux chatters, add hysteresis (resistor from `ST` to `PR1`) or lower the threshold with `R38` | 1 → 2 | 10 → 8 | Bench first |
| L-11 | Low | Low | Measure the 3V3 dip on `SD_ACTIVATE`. If it exceeds 0.2 V, change `R78` from 1 kΩ to 10–22 kΩ | 1 | 10 | Bench, then a value change |
| L-8 | Low | Low | Reverse-polarity bench test, then decide on `Q3`. **Decided 2026-11-04: keep `Q3`/`Q8` as they are**; the owner's boards start and run fine (section 5.1) | 2 | 8 | Accept |
| L-6 | Low | Low | Document: fit `SW6` if you flash firmware that can turn off USB-JTAG | 1 | 10 | Document |
| L-7 | Low | Low | Header rules: don't drive IO45/IO46 at reset; pin 12 (P+) sits next to C− | 1 | 10 | Document |
| L-13 | Low | Low | Washer or standoff of at most Ø4.4 mm, or nylon | 1 | 10 | Document (HARDWARE.md §16 half says it) |
| L-17 | Low | Low | Document the mutually exclusive pairs now; 3-pad jumpers in the next revision | 1 / 3 | 10 / 6 | Document |
| L-15 | Low | Low | Pre-scan first, then a capacitor at `D5` and a paired GDR/RESE route | 3 | 6 | Defer to the pre-scan |
| L-16 | Low | Low | Tie the tact switches' frame pads to GND | 3 | 6 | Next revision |
| L-10 | Low | Low | No 10 µH part with a higher saturation current fits the 2520 land, and `F3` covers the overload | — | — | Accept |
| L-9 | Low | Info | The charger limits it to about 0.1 A | — | — | Accept |
| L-12 | Low | Info | The worst case is a harmless top-of-charge cycle | — | — | Accept |
| I-3 | Info | Info | State the operating range (panel 0–50 °C) | 1 | 5 | Document |
| I-1, I-2, I-4, I-5 | Info | Info | Design choices, correctly described | — | — | Accept |
| I-7 | Info | Info | Intended: the board's own note says the label is drawn as seen from the top side | — | — | No action |

**Counts by my severity:** High 2 · Medium 4 · Low 19 · Info 8. Against the reviewer, M-1 and M-4 drop to Low, I-6
rises to Low, and L-9 and L-12 drop to Info.

## 2. Notes per finding

### 2.1 Battery and power safety

**H-1: no charge temperature limit and no timer.**

- **Reviewer:** `TEMP` is grounded and the TP4056 has no safety timer.
- **Agree:** this is the same gap as the certification audit's C1 ([CERT_REVIEW_AUDIT §3.6](../audit-2026-11-03/CERT_REVIEW_AUDIT.md#36-c1-charge-temperature)). It is already recorded in [NEXT_REVISION §9](../NEXT_REVISION.md#9-certification-readiness-items-for-later-recorded-2026-11-03).
- **New context:** the only free on-board NTC spot near the cell, (86.5, 61.5), is above the cut line on the snap-off
  arm. It would not exist on a cut board or the 3.68″ build. The NTC therefore belongs on leads, or in a 3-wire pack,
  with a 2-pin NTC connector or a 3-pin battery connector.
- **Timer:** the missing timer needs a charge-enable override that firmware can drive, so firmware can time the charge
  and stop it. The same override fixes M-5 and gives the charge inhibit (D1) that was dropped for lack of a GPIO.
  `IO3`, today only routed to `J6`, could serve if the header gives it up.
- **Rating:** High. It blocks a safety evaluation, though the field risk is moderate, because most charging happens
  indoors.
- **Verdict:** required before selling or certifying, but a design decision (where the NTC sits, which GPIO) and
  difficulty 4, so next revision. For 1.03 prototypes: charge at room temperature.

**H-2: the cut leaves bare battery copper next to ground.**

- **Reviewer:** after the cut, P+ (with `F2` gone with the arm) and 3V3 sit 0.20 mm from GND pour at a rough edge, about
  3 mm from the cell.
- **Context:** the README already says to deburr, check P+ to GND and seal the edge. The 3.68″ build has its own outline
  and needs no cut. `F2` cannot move below the line (no room, per TRACE_AUDIT §2.3).
- **My check:**
  - At the cut band, P+ (F.Cu, x 87.2–87.6) has GND pour at 0.20 mm and its nearest signal, `UNUSED_GPIO_45`, at
    0.55 mm.
  - 3V3 (B.Cu, x 99.9–101.4) has GND pour at 0.20 mm, and the power-button node and `J6_3V3` at 0.57–0.74 mm.
  - A burr to a signal is low-energy. The only high-energy bridge is to GND.
  - GND crosses the band 8.1 mm wide on F.Cu and 10.8 mm on B.Cu, so small pour-free areas around the two power traces
    leave the arm's ground intact.
- **Rating:** High for the boards it applies to. A 4–15 Ω bridge at 1–4 W next to the cell trips nothing.
- **Fix:** about 1 mm of pour-free area around each of the two traces, from y 60.8 to 63.1, on both layers. Rule areas
  only, with no track changes.
- **Verdict:** do now.

**M-4: no input over-voltage protection; the TVS is ahead of the fuse.**

- **Agree on the facts.** Disagree on the likelihood. With no USB-PD on the board, compliant chargers stay at 5 V, and
  QC needs a D+/D− handshake this board never makes. It takes a faulty or non-compliant fixed 9–12 V source.
- **Consequence:** `CR1` fails, normally short, and `U2`/`U3`/`U10` may die. A fire is unlikely; a dead board is likely.
- **Why there is no cheap fix:** swapping `F1` and `CR1` would leave the 6 V PTC holding off a 9–12 V source when
  tripped.
- **Rating:** Low.
- **Verdict:**
  - **Now:** document "5 V USB-C chargers only; no fixed 9/12 V supplies".
  - **Next revision:** a 5 V OVP switch or eFuse (≥ 20 V tolerant, about 6 V trip) ahead of `U2`/`U11`, difficulty 4.

**M-5: the charger cannot wake a pack in protection lockout.**

- **Agree with the mechanism.** In lockout, the pack's discharge FET blocks the board's divider current, so `J5` reads
  about 0 V and `Q9` keeps charge-enable low.
- **Likelihood is real.**
  - After a low-battery shutdown at about 3.3 V, deep sleep draws 50–80 µA. That takes the 10–20 mAh below 3.3 V in
    about 1–2 weeks.
  - A pack whose own protection trips at 2.8–3.0 V then locks out before the board's DW01A, at 2.4–2.6 V.
  - USB then does nothing, and the device looks dead. That is the support case to avoid.
- **Rating:** Medium.
- **Fix:**
  - **First:** a bench check with the packs actually used (difficulty 1).
  - **If confirmed:** an override that forces charge-enable for a few seconds after USB plug-in (an RC pulse), or the
    firmware-driven override from H-1 (difficulty 3).
- **Verdict:** bench now; fix in the next revision, together with H-1.

### 2.2 Power path and function

**M-2: brown-out under coincident peaks.**

- **Agree; known.** BENCH_THEORY put the coincident battery peak at 0.55–0.63 A. The reviewer adds the LDO's 500 mA
  rating and a 0.34–0.48 Ω board battery path.
- **Practical impact:** resets or SD errors during Wi-Fi when the cell is at about 50 % charge or less, if loads
  overlap.
- **Rating:** Medium.
- **Fix, firmware first (difficulty 2):**
  - serialise Wi-Fi TX, SD writes and refreshes;
  - lower TX power, which also helps the FCC exposure route, Z2;
  - no Wi-Fi below about 3.7 V.
- **Fix, hardware, only if the planned peak measurement shows the LDO limiting:** TLV757P. It is TI's 1 A sibling of the
  TLV755P, in the same SOT-23-5 package with the same input range and 25 µA quiescent current. Confirm the pin-out on
  its datasheet before swapping. Removing `Q3` (L-8) also cuts the path by 50–70 mΩ.
- **Verdict:** firmware now, hardware on data.

**M-1: `F3` hold margin.**

- **The reviewer's numbers are right.** The boost draws 56–95 mA at 100 % brightness, against a hold of about 80 mA at
  40 °C, which the keep-out lowers a little further.
- **The reviewer's fix is wrong for this board.** MF-FSMF020X holds 0.20 A and trips at 0.50 A. Case 1's fault was a
  6–7 Ω short inside `U10`, from SW to GND.
  - From the battery, that fault draws about 0.27–0.37 A at 3.0 V (0.38–0.53 A at 4.2 V).
  - The 0.20 A part would not trip, or barely would. That brings back exactly the slow burn N1 exists to stop.
- **The planned mitigation already covers this:** firmware caps brightness at 50 %, allowing 100 % only above about
  3.8 V (NEXT_REVISION F6). That takes the PTC's equivalent current to about 50 mA. The planned 30-minute 100 % bench run
  confirms it.
- **Rating:** Low with the cap.
- **Verdict:** firmware (planned) plus bench (planned). Keep the 0.10 A part.

**L-1: the schematic's `R6` note is stale.**

- **Current text:** "R6 4.7kohm -> ~234mA".
- **Actual:** with 10k the charge current is about 0.10–0.12 A by TP4056 REV 2.4 (0.12–0.13 A by the older sheet).
  That is about 5 h for 500 mAh.
- **Docs:** README and HARDWARE.md are already in the docs hand-off.
- **Verdict:** fix the schematic note now (difficulty 1).

**L-2: DW01A trip margin.** Known. The bench plan measures the coincident peak and the trip point. Low; verdict: bench
(planned).

**L-3: the power mux may chatter on weak USB.**

- **Reviewer:** with no PR1 hysteresis, it may toggle between USB and battery.
- **When it can happen:** only with a source at the 4.75 V minimum, a 0.5 Ω cable loop and a 0.7 A load.
- **Rating:** Low.
- **Fix:** bench with a weak source and a long cable. If it chatters, add a resistor from `ST` to `PR1` for hysteresis,
  or lower the threshold with `R38` (difficulty 2).
- **Verdict:** bench first.

**L-4: the `USB_STAT` level without VBUS depends on the TP4056 status pins.** Bench-read it, and have firmware decode
what it sees. Low; bench plus firmware.

**L-5: ladder 2's UP(2) level sits at the ADC's calibrated limit.**

- **The level:** 2.877 V, against the 2.9 V calibrated limit.
- **Why it matters:** UP(2) is also the power button on cut boards, so a misread matters there.
- **Fix:** `R36` 47k and `R35` 27k recentre it, but firmware thresholds must change with them (difficulty 2).
- **Verdict:** do it only together with a firmware update. Until then, check the raw readings on a board.

**L-8: `Q3` adds resistance but no protection.** *Corrected on 2026-11-04 (section 5): `Q3` and `Q8` were added for
different jobs, and the "flip it" option below does not work. Decided the same day: no change, because the owner's
boards start and run fine (section 5.1).*

- **Reviewer's analysis:** `Q8` alone blocks a reversed cell, and `Q3`'s body diode conducts in the fault direction.
- **Why not act now:** reverse polarity is safety-relevant and the original intent of `Q3` is not recorded, so change
  nothing without the reverse-polarity bench test (7.17).
- **Rating:** Low.
- **Verdict:** bench; next revision (remove `Q3`, which also helps M-2, or flip it for real redundancy).

**L-9: the cell detector is fooled by charger back-feed.** With the cell pulled while charging, `J5` stays live at
3.6–4.2 V, current-limited by the charger to about 0.1 A. The schematic already notes it. Info; accept.

**L-10: `L2` saturates under overload.** Since 1.03, `F3` covers the overload, and no 10 µH part with a higher
saturation current fits the 2520 land. Low; accept.

**L-11: switching on `SD_VDD` can dip 3V3.**

- **Size of the dip:** 0.1–0.4 V estimated, depending on the card's capacitance.
- **Fix:** if the dip exceeds 0.2 V, change `R78` from 1 kΩ to 10–22 kΩ. That gives about a 7–15 µs turn-on with
  Vgs ≈ −3.0 to −2.7 V (value change only).
- **Verdict:** bench, then the value change. Low.

**L-12: an 8 mV gap between the TP4056 float and the DW01A over-charge threshold.** The worst case is the DW01A cutting
at the top of charge and releasing at 4.05–4.15 V. That is harmless. Info; accept.

**L-18: the touch controller is always powered.** Firmware must put it in hibernate before deep sleep (+55 µA instead
of +220 µA), at difficulty 1. Low; firmware.

**I-6: cell cut-off.** Firmware should shut down at ≥ 3.3 V. It protects the cell's cycle life and shortens the time to
M-5's lockout. Raised to Low; firmware (with F7).

**I-1, I-2: no ship mode; no CC current advertisement.** Both are design choices. I-2's 0.7 A peak can matter on PC
ports, see L-3. Accept.

### 2.3 RF, EMC and layout

**M-3: antenna clearance.** Same as the certification audit's B1/Z3. Decided: measure range and throughput first, then
choose between the notch-arm pour clear-out (difficulty 3) and the full keep-out (difficulty 4, with the enclosure).
Medium; bench first.

**L-14: panel and frontlight ground connections.**

- **Panel capacitors:** the distances are T5/T9, left as is by owner decision.
- **Panel VSS (`J2` pin 17):**
  - It keeps its single spoke on purpose (even reflow heating, TRACE_AUDIT §2.5).
  - My via search found no legal spot in its 2.8 mm² island, so it stays as is.
- **`U10`'s ground pin:**
  - Its nearest GND via is 1.06 mm away. A second legal spot exists at (48.76, 123.10): 0.6 mm from the pad centre,
    off the pad, inside its 17 mm² island and the F.Cu plane.
  - A second via halves the return inductance of the frontlight boost's ground.
- **Verdict:** add that via now (difficulty 2). Low.

**L-15: EMC geometry.**

- **What it is:** the e-paper boost's loop is about 39 mm², with long GDR/RESE runs; it is the likeliest source while the
  panel refreshes.
- **Fixes:** a capacitor at `D5` and a paired route are moderate work.
- **Verdict:** pre-scan first. Low.

**L-16: ESD at the buttons.** Floating tact-switch frames and no TVS on the button lines. Tying the frame pads to GND
needs footprint and schematic edits (difficulty 3). Low; next revision.

### 2.4 Usability and documentation

**M-6: the back-silk option note names a part that no longer exists.**

- **What it says:** "unpopulate R42,44,46,52". `R42` became the PTC `F4` in 1.03 (N2).
- **Consequence:** following the note leaves `F4` fitted, which on a swapped-pinout panel ties its INT output to 3V3.
  That can damage the touch controller.
- **Fix:** change the text to "unpopulate F4,R44,46,52" (difficulty 1). It is the same length, so the box doesn't move.
- **Docs:** HARDWARE.md §8 should say to fit a PTC (MF-FSMF010X-2) on `R66`'s pads in that mapping.
- **Verdict:** Medium; do now.

**L-6: no BOOT button fitted.** Document: "fit `SW6` (APEM MJTP1243) if you flash firmware that can disable
USB-Serial-JTAG". Low.

**L-7: the header exposes strapping pins, and P+ sits next to C−.**

- **Document:**
  - accessories must not drive IO45 or IO46 during reset;
  - pin 12 (P+, fused by `F2`) sits next to pin 11 (C−).
- **Why not re-pin:** changing the pin-out would break accessory compatibility.
- **Verdict:** Low; document.

**L-13: washers and standoffs at the mounting holes.** The remaining copper near `H1`/`H5` could not move without moving
parts (TRACE_AUDIT T17). Document a washer or standoff of at most Ø4.4 mm, or nylon. HARDWARE.md §16 already recommends
an M2 cap head or a nylon washer. Low.

**L-17: DNP option pairs that short rails if both are fitted.** Document every exclusive pair; BOM.md already warns about
`R73`/`R74`. Use 3-pad solder jumpers in a later revision. Low.

**I-3: temperature ratings.** State an operating range of 0–50 °C, set by the panel. Info; document.

**I-4, I-5: FPC flip and RTC alarm.** I-4 is already warned on the silkscreen. I-5 is a design choice: the ESP32's own
timer does the waking. Accept.

**I-7: the `J6` legend row order.** The front silk says the label is "from the perspective of looking at the device
straight on from its top side", and Rev 1.01 deliberately swapped the rows. It is intended. No action.

## 3. Proposed plan

**Now, on the `1.03` branch (all difficulty 1–2, about an hour with the usual checks):**

1. M-6: correct the back-silk option note.
2. L-1: correct the schematic `R6` note.
3. H-2: pour-free areas around P+ and 3V3 at the cut line, on both layers.
4. L-14: the second GND via at `U10` pin 4.

The teardrop command needs re-running afterwards only if a track changes. These four don't change tracks.

**Firmware list** (add to NEXT_REVISION §4):

- **Load scheduling and the Wi-Fi floor** (M-2):
  - serialise Wi-Fi TX, SD writes and refreshes;
  - lower TX power;
  - no Wi-Fi below about 3.7 V.
- **Touch hibernate before deep sleep** (L-18).
- **Shutdown at ≥ 3.3 V** (I-6, with F7).
- **Decode `USB_STAT` from bench data** (L-4).
- **Keep the 50 % frontlight cap** (M-1, F6).
- **Ladder thresholds** if `R35`/`R36` change (L-5).

**Bench list** (add to NEXT_REVISION §6):

- **M-5:** a pack in protection lockout, with USB plugged in.
- **L-3:** a weak source and a long cable.
- **L-4:** `USB_STAT` with VBUS absent.
- **L-11:** the 3V3 dip when `SD_VDD` switches on.
- **L-8 and the reverse-polarity cases:** review §7.17.
- **Already planned:** M-1, M-2/L-2 and M-3.

**Next revision** (add to NEXT_REVISION §9):

- H-1, with the NTC on leads or a 3-wire pack, and a firmware-controlled charge-enable override that also serves M-5 and
  D1;
- M-4, an OVP switch;
- L-8, `Q3`;
- L-16, switch frames to GND;
- L-15, after the pre-scan;
- L-17, jumpers.

**Documentation** (add to the docs hand-off):

- M-4: 5 V USB-C chargers only;
- L-6: `SW6`;
- L-7: the header rules;
- L-13: washers;
- L-17: the exclusive pairs;
- I-3: the operating range;
- M-6: the `R66` PTC note in HARDWARE.md §8.

## 4. Applied on 2026-11-03

The owner approved the plan in section 3. It was applied on a scratch copy with KiCad closed, checked, and copied back.

| ID | Change | Verified |
|---|---|---|
| H-2 | Two pour-only rule areas on F.Cu and B.Cu: "Cut line: P+ pour pull-back" (x 86.2–88.6) and "Cut line: 3V3 pour pull-back" (x 98.85–102.45), both y 60.8–63.1 | At the cut itself (y 61.86 and 62.0), GND is now 1.00 mm from P+ and 1.01–1.11 mm from 3V3 on both layers. Before, it was 0.20 mm on the same layer and directly over or under them on the other. GND still crosses the cut 4.3 mm wide on F.Cu and 6.0 mm on B.Cu, so the arm stays grounded (0 unconnected) |
| M-6 | Back-silk note: "unpopulate R42,44,46,52" → "unpopulate F4,R44,46,52" | No new silkscreen warning |
| L-1 | Schematic note: "R6 4.7kohm -> ~234mA charge rate" → "R6 10kohm -> ~110-130mA charge rate" | ERC unchanged |
| L-14 | GND via (0.6/0.3 mm) at (48.76, 123.10), 0.6 mm from `U10` pin 4, off the pad | Sits in pin 4's B.Cu island and the F.Cu plane. `U10`'s ground now has two vias within 1.1 mm |

**Checks:**

- DRC with schematic parity: the same findings as before. 0 errors; 31 `silk_edge_clearance`, 10 `silk_over_copper`,
  3 `silk_overlap` and 6 `starved_thermal` warnings; 4 excluded `track_dangling`. 0 unconnected; parity clean.
- ERC: 46, unchanged.
- No track changed, so the 862 teardrops stand.

**Filed:**

- **NEXT_REVISION.md:**
  - firmware F8–F12 in §4;
  - the review's bench items in §6;
  - H-1's new constraints in §9's C1 row;
  - the next-revision items in a new §10.
- **REV_1_03_DOCS_HANDOFF.md:** the documentation items, in §3.7.

## 5. Status on 2026-11-04

The owner adopted the BQ21040 charger in place of the TP4056 ([REV_1_03_STATUS §14](../REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04)).
This table records what that change and the discussion around it moved. Every finding not listed stands as in sections 1–4.

| ID | Now | What is left |
|---|---|---|
| **H-1** | **Done in 1.03.** `U11` is a BQ21040 with a 10 kΩ NTC (`TH1`) on `TS`: charging only between about 0 and 41 °C at `TH1`, a 30 min pre-charge and a 10 h fast-charge timer, and an open NTC stops charging. The timer is in the chip, so no firmware override is needed for it | `TH1` measures the board, not the cell: the spots near the cell needed a 66 mm `TS` route. Log both through a charge for a lab, or move the NTC to the cell in a later revision (NEXT_REVISION §9, C1) |
| **M-2** | Re-rated **Low.** The owner sees no trouble with Wi-Fi during SD writes and refreshes. The 355 mA in the budget is continuous TX at 21 dBm; real TX is bursty, and the margin only runs out near an empty cell | F8 stands. One bench check: feed `J5` at 3.4 V through 0.2 Ω and run the worst overlap. TLV757P only if that shows the LDO limiting |
| **M-4** | Narrower. `U11` now survives a 9–12 V source: rated 30 V, it stops charging above 6.6 V | `U2` (6.0 V absolute maximum) and everything behind it are still exposed. Keep "5 V USB-C chargers only"; the OVP switch only has to protect `U2` now |
| **M-5** | Unchanged by the swap: the detector now holds `TS` low instead of `CE`, by the same mechanism. HARDWARE.md §3.3 already documents the limitation, with handling guidance ("Charger enable limitation") | Bench with the packs actually used. If they don't wake, an RC pulse that holds `Q2` off for a few seconds after plug-in (next revision) |
| L-1 | Superseded. With the BQ21040 the current is 540 / `R6`, so `R6` is 4.7 kΩ again for the same 105–125 mA. The schematic note says so | — |
| L-4 | TI specifies the BQ21040's pins high-impedance when unpowered, so the on-battery level should be the designed 2.20 V. F11 is rewritten for the new decode: the 0.55 V "complete" level is gone, and firmware uses `P+` to tell "full" from "stopped" | Read the level once on a 1.03 board |
| L-9 | Still accepted. With the cell pulled while charging, the BQ21040's battery detection cycles `J5` between 3.8 and 4.2 V, still limited to 105–125 mA | — |
| L-12 | The gap is now at least 20 mV: the BQ21040 regulates at 4.23 V at most | — |
| L-8 | **Accepted as is (owner, 2026-11-04):** the boards start and run fine. The research behind it is in [section 5.1](#51-l-8-what-q3-and-q8-do). `Q8` is meant as the DW01A's load switch from the EEVblog thread its note links, but it is fitted the other way round to that thread's circuit, so start-up relies on `C34` (0.1 µF in 1.03, 2.2 nF on the working Rev 1.0 boards). By the same orientation `Q8` is what blocks a reversed cell. "Flip `Q3`" is withdrawn | None. If a board ever shuts off on battery after an overload and stays off, plugging in USB resets the DW01A (documented in the hand-off) |
| L-16 | **Frames done in 1.03 (2026-11-04):** pad 3 (the hole beside the GND pad) is tied to GND on `SW1`–`SW5`, `SW8`, `SW9` and `SW11` (footprint `MJTP1117_FG`, solid connection). Pad 4 stays free for the front-mounted bottom buttons ([HARDWARE.md §9.1.1](../HARDWARE.md#911-front-mounted-bottom-buttons-optional-hand-fitted)); `SW7` and `SW10` are unchanged because their pad 1 is not GND | A TVS on the button lines, only if the field shows a problem |

**Still open after this update:**

- **Bench:**
  - M-1: the light at 100 % for 30 min;
  - M-2: the check above;
  - M-3: range and throughput;
  - M-5: pack wake;
  - L-2: the DW01A trip margin;
  - L-3: mux chatter;
  - L-4: the on-battery level;
  - L-11: the SD switch-on dip;
  - the charger checks on the first 1.03 boards (NEXT_REVISION §6).
- **Firmware:** F6 (M-1), F8 (M-2), F9 (L-18), F10 (I-6), F11 (L-4), F12 (L-5).
- **Next revision:** M-4, M-5, L-5 (with F12), L-15 (after a pre-scan), L-16 (the button TVS only; the frames are done) and L-17; M-2's hardware only on data.
- **Documentation:** the hand-off's §3.7 items, and its §3.8 for the charger.


### 5.1 L-8: what `Q3` and `Q8` do

Researched on 2026-11-04, after the owner pointed out that the two parts were added for different reasons.

**Decision (owner, 2026-11-04): no change.** The owner's boards start and run fine, so `Q3`, `Q8`, `R56` and `R83` stay
as they are. The analysis and the change below are kept for reference only.

**What each part is for.**

- **`Q3`:** reverse-polarity protection. The schematic labels it "Reverse polarity protection".
- **`Q8`:** the DW01A's load switch. Its schematic note links the EEVblog thread
  ["Pain and suffering getting the DW01 and 8205A protection circuit work right"](https://www.eevblog.com/forum/projects/pain-and-suffering-getting-the-dw01-and-8205a-protection-circuit-work-right/).
  Post #20 there proposes a P-FET on the battery's positive side with its gate on circuit ground, so the load stays off
  until the DW01's FETs connect ground. Its example circuit ([imgur MrKNLnB](https://imgur.com/MrKNLnB.png)) wires a BSS84
  with the **source on the battery**, the **drain on VCC** and the gate on circuit ground. The DW01 is powered straight
  from the cell.

**Why a DW01 built into a board needs that switch** (Fortune DW01-G Rev 1.1, §11; the fitted PUOLOP DW01A's sheet gives
no description, but its timing diagram 3 shows the same release):

- **Normal condition:** both FETs are on only while `CS` sits between the charger-detect level (about −0.7 V) and 0.15 V.
- **Over-current recovery:** the trip *"returns to the normal mode when the load is released or the impedance between
  BATT+ and BATT− is larger than 500 kΩ"*.
- **First connection:** *"When a battery is connected to DW01-G for the first time, it may not enter the normal
  condition (dischargeable may not be enabled). In this case, short the CS and VSS pins or connect to a charger."*
- **The cause on a board** (thread, post #20): until the FETs connect ground, the load pulls circuit ground up toward the
  cell, `CS` reads that as over-current, and the board's own load is never "released". A switch that drops the load
  while ground is open lets the DW01A reach, and return to, its normal condition. Then the switch turns on and current
  flows.

**As built, `Q8` is the other way round to that circuit.** Its source is on `P+` (the load) and its drain faces the
battery through `R27`/`Q3`. A P-FET's body diode runs drain → source, so:

- **Thread's orientation:** the diode blocks battery → load, and with the channel off the load really is disconnected.
- **`Q8`'s orientation:** the diode conducts battery → load, so the load stays connected whether `Q8` is on or off. Its
  channel only turns on once ground is already connected (it then removes the diode drop). The DW01A never sees its load
  released.
- **Side effect:** that same orientation is the textbook reverse-polarity P-FET (drain toward the battery, source to the
  load, gate to ground). So `Q8`, not `Q3`, is what blocks a reversed cell, as DESIGN_REVIEW §4 found. It holds while
  `P+` stays near ground; the charger-enable gate covers the USB case.
- **`Q3`:** faces the way the thread's FET does, but its gate goes to `B−`, the cell's own negative. It is on whenever a
  cell is in, so it does neither job.

**What that means on this board.**

- **Start-up without USB:** relies on `C34` alone. That is the thread's other fix, a capacitor from `CS` to `BAT−`;
  `C34` is 0.1 µF since N8, against the thread's 1–2 nF minimum. The thread found it less reliable than the FET:
  *"sometimes I would have to pop the battery in, then out, then in again"*. BENCH_THEORY §3.4 checked only the inrush
  spike.
- **After an over-current trip on battery:** the board should stay off until USB is plugged in (charger detection), or
  until the cell is re-plugged. Its standby load (about 50–80 µA, roughly 45–75 kΩ) is far below 500 kΩ, and the
  regulator's 25 µA alone is about 150 kΩ. This raises the stakes of L-2: a coincident peak that trips the DW01A leaves
  the device dead until it is plugged in.
- **The DW01A's supply:** it comes from `P+` through `R83`. At insertion it sees the cell minus `Q8`'s diode drop until
  ground connects.

**For reference, not planned: how the DW01A would get its load switch.** The smallest change uses the parts already
fitted:

- **Tie `Q3`'s gate to circuit ground:** move `R56`'s lower end from `B−` to GND. `Q3` already has its source on the
  battery, so it becomes exactly the thread's FET. `Q8` keeps blocking reversed cells.
- **Power `U5` from the battery side:** move `R83` from `P+` to `B+`, as the thread's circuit and the datasheet's typical
  application do. Otherwise switching the load off would also switch the DW01A off.
- **Trade-offs to test before adopting it:**
  - after a trip the board retries automatically, so a persistent fault gets repeated short-circuit pulses instead of
    staying off;
  - `U5` sits across a reversed cell through `R83`, about 30 mA into its substrate diode, which `Q8` shields today when
    USB is absent.
- **Bench:** the reverse-polarity cases (with an emulator), insertion without USB, trip and recovery on battery, and
  charging an over-discharged cell.
- **Other options:**
  - turn `Q8` around and make `Q3` a detector-driven reverse-polarity switch (DESIGN_REVIEW §4), a bigger change;
  - keep the board as it is;
  - remove `Q3`, which only saves its 50–70 mΩ.

**Optional checks, only if the behaviour ever matters (Rev 1.0 boards have `C34` = 2.2 nF):**

1. **Insertion:** answered in practice. The owner's boards start every time a cell is connected.
2. **Trip and recovery:** put a current-limited bench supply (about 3.8 V, limit about 3 A) in place of the cell. Load
   `P+` to GND with about 1 Ω (a 5 W part) for a fraction of a second. With the path's 0.3–0.5 Ω that is about 2.5 A,
   above the 0.83–1.68 A trip window. Then remove the load and check whether the board comes back by itself or only when
   USB is plugged in.
