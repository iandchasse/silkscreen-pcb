# Bench tests in theory: what the datasheets and models already predict (2026-11-03)

[NEXT_REVISION.md §6](../NEXT_REVISION.md#6-verification) lists bench tests to run before ordering Rev 1.03:

- the frontlight PTC test (N1, `F3`);
- the sense-resistor trial (N7/N8, `R85`/`R86` and `C34`), including the coincident-peak measurement;
- a known-good baseline.

This note predicts each result from three sources, to show what the tests can still add:

- **Datasheets:** the manufacturers' primary documents (listed in section 5).
- **A copper model:** a copper-level thermal model of the 1.03 board.
- **The PTC model:** [PTC_THERMAL.md](../audit-2026-10-29/PTC_THERMAL.md)'s own model, re-run with the new numbers.

Board state: branch `1.03` working copy, 2026-11-03 (after the reference-designator cleanup).

## 1. Summary

| Test | What theory now says | What is still unknown | Still worth doing? |
|---|---|---|---|
| **PTC, case 1 short** | As laid out, `F3` is about 23 % better cooled than the datasheet's environment. GND pour wraps its pads. From a 3.0 V cell the worst part takes about 30 s to trip, instead of the study's 5 s. At −20 °C it does not trip below 3.7 V. A 1 mm pour keep-out around `F3` brings it back to 6 s (section 2.4). The keep-out is now on the board ([TRACE_AUDIT.md §1f](TRACE_AUDIT.md#1f-layout-fixes-applied-after-the-review-2026-11-03)) | The PTC's internal thermal resistance, and Bourns's unpublished test environment. Together they put ±0.06 on the cooling factor | **Yes**, on a 1.03 board: it is the only check of the 3.0–3.4 V corner |
| **PTC, normal use** | Unchanged from the study. At 100 % brightness a high-resistance part drops `U10` into UVLO from a cell of 3.7 V or less. Keep the 50 % cap | The real LED power | A quick check only |
| **Trip point** | The sense path as placed is about 62 mΩ, not 50 mΩ. The trip window becomes 0.83–1.68 A with the PUOLOP `DW01A` that JLC fits, or 0.77–1.78 A with Fortune's (section 3.2) | The `DW01A`'s threshold over temperature: no vendor specifies it | **Yes**, quick |
| **Coincident peak** | The datasheets put it at about 0.55 A typical and 0.63–0.69 A worst. That leaves 1.1–1.3× margin at the hot, low-cell corner and 2.4× typical (section 3.3) | The ESP32's maximum (only a typical is published), the SD card, and the Wi-Fi rate | **Yes**: the single most useful number |
| **Insertion** | `C34` = 0.1 µF filters the spike to about 0.04–0.08 V, against a threshold of at least 0.82 V. PUOLOP also needs 400 µs, typical (section 3.4) | Cell and cable | Optional: 3–5 insertions as a sanity check |
| **Hot (60 °C)** | The FETs' resistance rises 5.5–13 %, so the trip current falls 4–7 % (section 3.5) | `DW01A` drift | Optional: fold it into the trip-point run |
| **Known-good baseline** | — | — | Yes: cheap, and the only way to get reference readings |

## 2. Frontlight PTC (`F3`, N1)

### 2.1 Datasheet facts

Bourns MF-FSMF datasheet Rev K (09/26) [B1], unless noted otherwise.

| Item | Value | Notes |
|---|---|---|
| I_hold / I_trip at 23 °C | 0.10 / 0.30 A | I_trip is the guaranteed trip, not the typical |
| Resistance | R_min 0.90 Ω (as supplied); R1max 6.00 Ω (one hour after reflow or a trip) | No as-supplied maximum is published. After a trip, typically +50 % [B5]. One Bourns example went from 0.7 to 2 Ω through soldering [B6] |
| Maximum time to trip | 1.0 s at 0.50 A | At V_max (15 V), 23 °C, still air |
| Typical time to trip, 23 °C | 0.25 A: 2.2 s; 0.3 A: 0.43 s; 0.4 A: 0.11 s; 0.5 A: 0.053 s; 1 A: 0.0095 s | Read from the vector curve; it leaves the 100 s edge at about 0.22 A. Bourns: "typical performance … in a simulated application environment" |
| Hold derating | 0.13 / 0.12 / 0.11 / 0.10 / 0.08 / 0.07 / 0.06 / 0.05 / 0.03 A at −40 / −20 / 0 / 23 / 40 / 50 / 60 / 70 / 85 °C | The study's fit matches |
| Tripped dissipation | 0.5 W typical | |
| Test board | **Not published.** Only "still air" | Bourns publishes no test board for chip PPTC ratings |
| Effect of copper | I_hold ∝ √U, where U is the heat-transfer coefficient [L3] | No vendor gives a "% per trace width" figure |

The study's inputs all match these numbers.

### 2.2 The study's model against the datasheet

The model (`ptc_fit.json`) is fitted to the hold derating, the trip current, the maximum time to trip and Pd. The typical time-to-trip curve was not used, so it is an independent check. Constant current at 23 °C, model by the part's resistance R0:

| Current | Datasheet, typical | Model, 0.9 Ω | 2.0 Ω | 6.0 Ω |
|---|---|---|---|---|
| 0.25 A | 2.2 s | no trip | 2.2 s | 0.55 s |
| 0.30 A | 0.43 s | 5.0 s | 1.3 s | 0.37 s |
| 0.40 A | 0.11 s | 1.8 s | 0.66 s | 0.20 s |
| 0.50 A | 0.053 s (max 1.0 s) | 1.0 s | 0.40 s | 0.13 s |
| 1.0 A | 0.0095 s | 0.22 s | 0.095 s | 0.032 s |

- **Near the trip threshold (0.22–0.3 A)** the model reproduces the typical curve for a part of about 2 Ω. The case 1 short on a battery sits here: 0.21–0.42 A from 3.0–3.7 V.
- **Above about 0.4 A** the model trips 3–20× slower than the typical part.
  - The model's single thermal mass is anchored to the 1.0 s *maximum*.
  - The real device heats a thin polymer core almost adiabatically: the curve follows I²t ≈ 0.01 A²s above 1 A.
  - So the model's USB-side trip times (0.35–0.56 A) are pessimistic. The low-cell times are realistic.

### 2.3 Copper model of the 1.03 board

The study swept the PTC's cooling between "like Bourns's test board" (factor 1.0) and "40 % better cooled" (0.6), because the layout did not exist yet. Now it does. [bench-theory/board_thermal_ml.py](bench-theory/board_thermal_ml.py) solves steady-state conduction on the real copper:

- **Copper:** tracks, pads, the refilled pours and vias on both layers, from [export_copper.py](bench-theory/export_copper.py).
- **Cells:** 0.1 mm across a window around `F3` and `U10`, clipped to the board outline (cut-outs included).
- **FR-4:** split into 7 sublayers through its thickness, thin at the surfaces, with k = 0.8 W/mK in-plane and 0.3 W/mK through-plane.
- **Plated barrels:** 18 µm.
- **Surface losses:** both faces lose h = 12 W/m²K (still-air convection plus radiation).
- **Simplifications:** component bodies are ignored.

| Quantity (K/W unless stated) | 40 mm window | 70 mm window | Calibrated | The study assumed |
|---|---|---|---|---|
| `F3`'s board, as laid out | 180 | 173 | **≈190** | — |
| `F3`'s board with the 1.0 mm pour keep-out (as built, refilled) | 231 | — | **≈245** | — |
| Keep-out 0.75 / 1.5 / 2.5 mm (pour removed in the model) | 237 / 253 / 270 | — | — | — |
| Bare 0603 on 0.25 / 0.5 / 1.0 mm traces (test-board stand-ins) | 285 / 249 / 197 | — | — | — |
| The same lands tied into 10 × 10 mm pours ("heavy copper") | 116 | — | — | — |
| Board under `U10` (θ_ba) | 127 | 111 | **≈119** | 40 or 110 |
| Coupling from `U10`'s heat to `F3` (κ) | 0.50 | 0.41 | **≈0.38** | 0, 0.25, 0.5, 0.75 |

**Checks:**

- **Window:** 40 → 70 mm changes `F3` by −4 % and `U10` by −13 %.
- **Cells:** 0.1 → 0.05 mm adds +10 % (a 20 mm window: 272 → 299 K/W). "Calibrated" applies both corrections.
- **Convection:** at h = 8 / 20 W/m²K, `F3` reads 205 / 159 K/W and the 0.25 mm stand-in 309 / 259 K/W. The ratio between them stays at 0.61–0.66.
- **A two-layer model was not used.** It puts half the FR-4 into each copper layer and gives 101 K/W, because it overstates heat crossing the pour's 0.2–0.3 mm clearance.

**Why `F3` runs cool.**

- Its pads are not tied to the pour, which follows the study's rule.
- But B.Cu GND pour wraps them at 0.2–0.3 mm, and solid F.Cu GND pour lies 1.5 mm below.
- The result sits between a bare-trace board and heavy copper.

**Cooling factor.**

- **Definition:** the study's fitted 325 K/W is the part's total in the datasheet environment. That total is the part's internal resistance plus the board's. The internal part is estimated at 40–80 K/W: about 45 K/W for a 0.25 mm polymer slab heated evenly, plus the terminations.
- **As laid out:** (40–80 + 190) / 325 = **0.71–0.83**, centre 0.77.
- **With a 1 mm keep-out:** **≈0.94**.
- **Cross-check against the stand-ins** (60 K/W internal): 0.70 against the 0.25 mm stand-in, 0.78 against the 0.5 mm one.

### 2.4 The study's model with these numbers

[bench-theory/ptc_rerun.py](bench-theory/ptc_rerun.py) re-runs the model. The table gives the worst case over the PTC's resistance (0.9, 2.5, 6.0 Ω) for the 7 Ω case 1 short: time to trip, or the power left in the short if it never trips.

| Ambient, cell | Study's headline (1.0, κ 0.5, θ_ba 110) | As laid out (0.77, 0.38, 119) | 1 mm keep-out (0.94, 0.38, 119) |
|---|---|---|---|
| 25 °C, 3.0 V | 5.1 s | **29.6 s** | 6.0 s |
| 25 °C, 3.4 V | 2.9 s | 4.1 s | 3.1 s |
| 25 °C, 3.7 V | 2.1 s | 2.7 s | 2.3 s |
| 25 °C, 5.0 V (USB) | 0.9 s | 1.0 s | 0.9 s |
| −20 °C, 3.0 V | no trip, 0.52 W | no trip, 0.68 W | no trip, 0.61 W |
| −20 °C, 3.4 V | 18.8 s | **no trip, 0.65 W** | 29.3 s |
| −20 °C, 3.7 V | 10.2 s | 26.5 s | 13.2 s |
| 45 °C, 3.0 V | 2.2 s | 2.9 s | 2.3 s |

- **At the pessimistic end** (factor 0.71), the 25 °C / 3.0 V case does not trip either. It leaves 0.22 W in the short, with `U10` at 65 °C.
- **"No trip" still protects.** The PTC's rising resistance holds the short to 0.5–0.7 W with `U10` at 95 °C or below. Without the PTC it is 1–2.75 W and 98–433 °C, which is how case 1 charred.
- **10 Ω short at 25 °C / 3.0 V:** no trip in all three columns (0.13–0.47 W).

**The keep-out:**

- **On the board since 2026-11-03** ([TRACE_AUDIT.md §1f](TRACE_AUDIT.md#1f-layout-fixes-applied-after-the-review-2026-11-03)): a rule area forbidding zone fills, 1.0 mm around `F3`'s pads on both layers (x 44.80–49.60, y 114.33–117.28). Zones refilled.
- **DRC:** identical to the board without it; 0 unconnected, parity clean. The "1 mm keep-out" column is now the board as built.
- **Normal use:** keeping the PTC warmer makes 100 % brightness slightly worse. UVLO is also reached at 3.7 V / 25 °C with a 6 Ω part. 50 % is unaffected.

### 2.5 Normal use

TPS923610 facts [T1]:

- **UVLO:** falling 2.05 min / 2.17 V typ; rising 2.3 typ / 2.49 V max.
- **Start-up current limit:** 0.8 A typ, not production tested. TI's scope shot shows 0.69 A at start-up for a 60 mA load.
- **Efficiency:** 86–90 % at 10–15 mA (TPS923611 curves, 3.6 V).

The study's findings stand:

- **At 100 %:** a 6 Ω part drops `U10` into UVLO from a cell of 3.0–3.7 V. The light goes out and comes back.
- **At 50 %:** only at 60 °C on a 3.0 V cell.
- **Firmware rule:** keep the 50 % cap, or allow 100 % only above about 3.8 V.

### 2.6 What the bench test adds

The cooling factor is now the main uncertainty, at about ±0.06, and the test measures it directly. To make the result comparable:

1. **Use a 1.03 board.**
   - A PTC bodged onto an older board sits in different copper, so its trip times will differ.
   - The copper model can be re-run for the bodge if needed.
2. **Measure `F3`'s resistance in place first.** R0 decides which corner of the table applies.
3. **Stand in the short:** a 6.8 Ω 1206 from the `SW` node (`L2` pad 2) to GND, with the light off.
4. **Run it:**
   - Feed `J5` from a bench supply at 3.0, 3.4 and 3.7 V, and USB at 5 V.
   - Log the current. The trip is when it falls below about 0.1 A.
5. **Compare with section 2.4's keep-out column**, which is the board as built.
   - The worst part should trip in about 6 s from 3.0 V.
   - A much slower trip means the board cools `F3` even better than modelled. A larger keep-out (1.5–2.5 mm: section 2.3) is the next step.
6. **Optional:** −20 °C in a freezer.

## 3. Sense resistor (N7/N8)

### 3.1 Datasheet facts

**`DW01A`.** The JLC build fits PUOLOP (LCSC `C351410`). Every value is specified at 25 °C only, and no vendor gives a minimum delay.

| Parameter | Fortune Rev 1.3 [F1] | PUOLOP Rev B [F2] | HMSEMI [F3] |
|---|---|---|---|
| Over-current threshold | 120 / 150 / 180 mV | 130 / 150 / 170 mV | 120 / 150 / 180 mV |
| Over-current delay | — / 10 / 20 ms | — / **7** / 20 ms | — / 10 / 20 ms |
| Short-circuit threshold | 1.00 / 1.35 / 1.70 V | **0.82** / 1.36 / 1.75 V | 1.0 / 1.2 / 1.4 V |
| Short-circuit delay | — / 5 / 50 µs | — / **400** / 600 µs | — / 5 / 50 µs |
| `OD` high level | VCC − 0.1 V min | VCC − **0.4** V min | VCC − 0.1 V min |

Fortune's over-current release: "when the load is released or the impedance between BATT+ and BATT- is larger than 500kΩ".

**FS8205A**, per FET at 25 °C:

| Source | 4.5 V gate | 2.5 V gate | Other gate voltages | 60 °C |
|---|---|---|---|---|
| TECH PUBLIC (LCSC `C2830320`, JLC) [S1] | 19.5 typ / 25 max mΩ | 25 / 31.5 mΩ | — | no curve |
| EVVOSEMI [S2] | 20.5 / 27 mΩ | 27 / 37 mΩ | 22.3 at 4.2 V, 24.9 at 3.0 V (typical curve) | ×1.13 |
| Fortune FS8205 [S3] | 23 / 28 mΩ | 30 / 37 mΩ | — | ×1.055 |

**FET loop (both FETs plus about 10 mΩ of `B−` trace).**

- **The study's range:** 39–84 mΩ.
- **What the datasheets support:** 39–47 mΩ at the low end, 69–89 mΩ at the high end.
- **With PUOLOP's weaker gate drive:** about 94 mΩ from a 3.0 V cell (gate about 2.6 V).

### 3.2 The sense path as placed

`R85` sits at (78.66, 69.11) and `R86` at (75.0, 70.5), west of `Q1`.

| Section | Resistance |
|---|---|
| `Q1` pin 3 → `R85`: B.Cu 0.5 mm, a via, F.Cu 0.5 mm, a via pair, B.Cu 0.5 mm | ≈ 8 mΩ (copper 1.0 + 0.8 + 2.4 + 1.5 mΩ, vias ≈ 1.6 + 1 mΩ) |
| `R85` (100 mΩ) ∥ (`R86` 100 mΩ + 15.8 mΩ of 0.2 mm link) | 53.7 mΩ (`R86` carries 46 %) |
| **Total, `Q1` pin 3 to the pour** | **≈ 62 mΩ ± 3** |

- **Not counted:** the pour between `R85`/`R86` and `R16`'s ground adds 1–3 mΩ, depending on where the load current returns.
- **Expected readings:** 53.7 mV/A across `R85`, and about 62 mV/A from `Q1` pin 3 to ground.

**Trip window:** I = V_threshold / (FET loop + sense path).

| | min (hot, 3.0 V cell, maximum FETs) | typical | max |
|---|---|---|---|
| The study (50 mΩ, generic `DW01A`) | 0.89 A | 1.34 A | 2.02 A |
| As placed, PUOLOP (the JLC part) | **0.83 A** (130 mV / 156 mΩ) | 1.32 A (150 / 114) | 1.68 A (170 / 101) |
| As placed, Fortune or HMSEMI | 0.77 A (120 / 156) | 1.32 A | 1.78 A (180 / 101) |

The as-placed resistance is close to the 68 mΩ the study first recommended, so its "1.31× over 0.6 A" situation applies, not the 50 mΩ pair's 1.49×.

### 3.3 The coincident peak, from datasheets

Battery current is roughly the 3V3 load (the LDO passes current one-for-one) plus the frontlight's input.

| Load | Current | Source |
|---|---|---|
| ESP32-S3 Wi-Fi TX, 802.11b 1 Mbps, 20.5 dBm | 355 mA (11g 297, 11n 286; BLE 344 at 20 dBm). Typical only, "rated at a 100% duty cycle" | WROOM-1 datasheet v1.8, Table 6-4 [E1] |
| microSD write | Specification: 100 mA in default speed, averaged over 1 s (200 mA high speed). Vendors: 50–90 mA typical, 120 mA maximum | SD Physical Layer v9.10 Table 3-6 [SD1]; Swissbit S-56u [SD2] |
| E-paper refresh | 20–60 mA | Estimate (final review 09-19) |
| Frontlight from the battery | about 35 mA at the 50 % cap (0.118 W at 3.4 V); 78–100 mA at 100 % from 3.0 V | PTC_THERMAL §4.3 |
| Everything else | < 5 mA | |

**Coincident peak:**

- **Typical:** 355 + 90 + 60 + 35 + 5 ≈ **0.55 A**.
- **Worst plausible:** **0.63 A** at the 50 % cap, allowing the ESP32 +15 % and the SD card at its 120 mA maximum. At 100 % light it reaches 0.69 A.

**Duration.**

- **The DW01A needs time:** about 7 ms (PUOLOP) or 10 ms (Fortune), typical, with no minimum.
- **A long Wi-Fi frame lasts long enough:** a 1500-byte frame at 802.11b 1 Mbps is 12.2 ms of air time (192 µs preamble).
- **When the ESP32 uses 1 Mbps:** raw frames and ESP-NOW default to it. Data frames drop to it on a weak link.
- **The other loads are long:** SD programming lasts milliseconds; a refresh lasts seconds.

**Margin (lowest trip ÷ worst peak):**

| | 0.63 A (50 % cap) | 0.69 A (100 % light) | Typical (1.32 A ÷ 0.55 A) |
|---|---|---|---|
| PUOLOP | 1.32× | 1.21× | 2.4× |
| Fortune | 1.22× | 1.11× | 2.4× |

- **Where the thin margin lives:** only where every worst case stacks at once: hot, low cell, maximum-resistance FETs, minimum threshold, worst card, a 1 Mbps frame at full power.
- **If the measured peak comes out high:**
  - firmware can cap TX power, avoid 802.11b rates, keep the 50 % light cap, and not write the SD card while transmitting;
  - or lower the sense resistance: wider copper, or three resistors.

### 3.4 Insertion

**The spike.**

- **Cell resistance:** small LiPo cells are 50–80 mΩ at 1 kHz [C1, C2].
- **The study's spike:** 10–15 A for 3–4 µs.
- **Unfiltered at `CS`:** 10–15 A × (FET loop + 62 mΩ) ≈ 1.0–2.3 V. That is above PUOLOP's 0.82 V minimum and Fortune's 1.0 V.

**Why it doesn't trip.**

- **The filter:** `R16` (1 kΩ) and `C34` (0.1 µF) make a 100 µs filter. A 3.5 µs spike reaches about 3.5 / 100 of its height: **0.04–0.08 V**.
- **The delay:** PUOLOP also needs 400 µs (typical) above threshold. Fortune and HMSEMI need only 5 µs (typical), so `C34` matters most with them.

Theory settles this one. A few insertions on the first boards are enough.

### 3.5 Hot

| Contribution | Rise at 60 °C |
|---|---|
| FETs (×1.055–1.13) | +2.3–5.5 mΩ |
| Copper in the loop (about 22 mΩ, +0.39 %/K) | +3 mΩ |
| Resistors | negligible |
| `DW01A` threshold | no vendor specifies its drift |

On 114 mΩ that is +5–8 %, so the trip current falls 4–7 %. Low risk. Repeating the trip-point run warm covers it.

### 3.6 What the trial adds

- **The coincident peak:** the one number theory cannot pin down.
- **The trip point:** confirms the window, and which `DW01A` threshold the board actually got.
- **Insertion and hot runs:** optional (sections 3.4–3.5).

How to probe without the dropped test pads:

- **`/B-_SENSE`:** at `R85` pad 1.
- **`OD`:** at `Q1` pin 6 against `B−`.
- **Bodge on an older board:** lift `Q1` pin 3, and fit the pair and a 0.1 µF `C34` ([FOLLOWUP §3.3](../audit-2026-10-29/PROTECTION_FOLLOWUP.md#33-sense-resistor-implementation-and-bench-check)).

## 4. Known-good baseline

Theory has nothing to add. Record the readings of [FOLLOWUP §8.3](../audit-2026-10-29/PROTECTION_FOLLOWUP.md#83-known-good-baseline) on the repaired case 1 board. The front test pads were dropped, so use component pads: `C4` pad 1 for `LDO_IN`, `C2`/`C3` for `USB_VBUS`, the 3V3 caps, and the PTCs' pads.

## 5. Sources

- **[B1]** Bourns MF-FSMF datasheet Rev K 09/26: https://www.bourns.com/docs/product-datasheets/mf-fsmf.pdf
- **[B5]** Bourns soldering recommendations (e/MF2602): https://www.bourns.com/docs/technical-documents/technical-library/multifuse-pptc-resettable-fuses/publications/bourns_mf_solder_recom.pdf
- **[B6]** Bourns app note, PPTCs for current limit control (e/K1467): https://www.bourns.com/docs/technical-documents/technical-library/multifuse-pptc-resettable-fuses/application-notes/bourns_current_limit_control_pptcs_for_power-supplies_appnote.pdf
- **[L3]** Tyco Electronics, "Fundamentals of PolySwitch" (2008), p4 eq. 4. Third-party mirror: https://www.electrokit.com/upload/product/41012/41012195/circuit-protection-psw-fundamentals-6.pdf
- **[T1]** TI TPS923610 datasheet SNVSCN8B: https://www.ti.com/lit/ds/symlink/tps923610.pdf
- **[F1]** Fortune DW01A Rev 1.3: http://www.ic-fortune.com/upload/Download/DW01A-DS-13_EN.pdf
- **[F2]** PUOLOP DW01A Rev B (LCSC `C351410`): https://datasheet.lcsc.com/datasheet/pdf/0d2b2b5e8d1207bf276387cb4ff3a495.pdf?productCode=C351410
- **[F3]** H&M Semi DW01A: https://hmsemi.com/downfile/DW01A.PDF
- **[S1]** TECH PUBLIC FS8205A (LCSC `C2830320`): https://datasheet.lcsc.com/datasheet/pdf/c060cb7baa8cc2b2d2a0ed3afa443ef8.pdf?productCode=C2830320
- **[S2]** EVVOSEMI FS8205A: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7158/5272_FS8205A.pdf
- **[S3]** Fortune FS8205 Rev 1.9: http://www.ic-fortune.com/upload/Download/FS8205-DS-19_EN.pdf
- **[E1]** ESP32-S3-WROOM-1 datasheet v1.8: https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- **[SD1]** SD Physical Layer Simplified Specification v9.10 (§3.9.6 Table 3-6; §4.3.10.4 "average over 1second"): https://www.sdcard.org/
- **[SD2]** Swissbit S-56u data sheet Rev 1.14, Table 20: https://www.mouser.com/catalog/specsheets/Swissbit_02-03-2025_S-56u_data_sheet.pdf
- **802.11b air time:** TXTIME = preamble + PLCP header + 8 × length / rate; IEEE 802.11-98/029; Linux `net/mac80211/util.c`.
- **Cells:**
  - **[C1]** Sounddon 503562 (≤ 50 mΩ): https://cdn-shop.adafruit.com/datasheets/503562+1200mah.pdf
  - **[C2]** Honcell HCP-113028 (≤ 80 mΩ).

## 6. Files and how to re-run

All in [bench-theory/](bench-theory/):

- **`export_copper.py`** (KiCad 9's Python): `python.exe export_copper.py ..\..\..\silkscreen_pcb.kicad_pcb copper.json`. Refill the zones first.
- **`board_thermal_ml.py`** (numpy, scipy, pyamg, shapely, Pillow): `python board_thermal_ml.py copper.json [win=70] [dx=0.05] [h=8] [keepout=1.0] [tests=0]`.
  - Runs in about 2 minutes at the 40 mm window, 6 at 70 mm.
  - `copper.json` is not committed; it regenerates in seconds.
- **`ptc_rerun.py`:** `python ptc_rerun.py fth=0.77 kappa=0.38 thba=119 fth2=0.94` gives section 2.4.
