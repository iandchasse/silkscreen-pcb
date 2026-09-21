# HARDWARE.md — targeted corrections and firmware contract

Change log for the edits applied to `docs/HARDWARE.md` in response to the 2026-09-19 final review and
the author's refutations (`author_refutes.json`). Line numbers are **post-edit** unless stated.
No `*.kicad_*`, `production/`, `fabrication/` or `DESIGN_REVIEW.md` file was touched.

---

## 1. MCU-19 — "GPIO46 is input-only" is factually wrong for the ESP32-S3

The ESP32-S3 has **no input-only pins**; `GPIO34`–`GPIO39` on the *original* ESP32 were the input-only
set. `IO46` is a normal bidirectional GPIO that happens to be a strapping pin with an internal
pull-down, and must read LOW at reset.

| File | Line | Before | After |
|---|---|---|---|
| `docs/HARDWARE.md` | 489 (§4, "Strapping and JTAG-overlapped pins") | `` `IO46` is input-only. `` | `` `IO46` is a **normal bidirectional pin** — the ESP32-S3 has no input-only pins (those were `GPIO34`–`GPIO39` on the original ESP32) — but it *is* a strapping pin with an internal pull-down, and it must read **LOW at reset**. `` |
| `docs/HARDWARE.md` | 1052 (§11, expansion-header pin categories table) | `` \| Spare GPIO \| `IO46` (2, input-only strap), … \| `` | `` \| Spare GPIO \| `IO46` (2, strap — internal pull-down, must be LOW at reset), … \| `` |
| `docs/HARDWARE.md` | 1121 (§13, complete GPIO map, row 16) | `` \| 16 \| IO46 \| — \| Spare → `J6` pin 2 (input-only strap) \| `` | `` \| 16 \| IO46 \| — \| Spare → `J6` pin 2 (strap; must read LOW at reset) \| `` |

**README.md: no change needed.** `grep -n -i "input-only\|input only\|IO46\|GPIO46"` over `README.md`
returns **zero hits** — the claim is not in that file, so nothing was edited there (which also avoids
colliding with the concurrent README restructure).

**Still wrong, and out of my scope:** `DESIGN_REVIEW.md` line 288 still reads *"GPIO46 is input-only."*
That file is on the do-not-touch list. See "Left for the author" below.

---

## 2. Charge current — "255 mA" was being stated as established

| File | Line | Before | After |
|---|---|---|---|
| `docs/HARDWARE.md` | 231–234 (§3.2) | *"…i.e. roughly **234–255 mA** depending on which datasheet constant you trust; treat this as **~0.25 A intended and measure the actual lot** rather than an exact 255 mA."* | *"…i.e. **about 0.23–0.25 A** (the TP4056 datasheet formula, `I = 1100/R_PROG`, gives **234 mA**) depending on which datasheet constant you trust. This is **lot-dependent — measure it** rather than treating any single figure as established."* |

The lead-in "**Charge current ≈ 0.25 A.**" and the dissipation arithmetic that follows were left alone —
both are still correct at 0.23–0.25 A. `grep -n "255"` over `docs/HARDWARE.md` now returns nothing.

---

## 3. §6.2 EPD boost loop area — the ≈33 mm² figure is not reproducible

| File | Line | Before | After |
|---|---|---|---|
| `docs/HARDWARE.md` | 667–670 (§6.2, the `L1` move) | *"The move made the boost loop slightly **larger, not smaller**: `EINK_SW` copper is now 15.4 mm (was 16.5 mm, no vias), but the `C10`→`L1`→`Q4`→`R14` pad-centre loop area **grew from ≈24 mm² to ≈33 mm² (+36 %)**, because the inductor body is bigger."* | *"The move did **not** shrink the boost loop: `EINK_SW` copper is now 15.4 mm (was 16.5 mm, no vias), but the `C10`→`L1`→`Q4`→`R14` pad-centre loop area is **roughly 20–27 mm²** — the exact figure depends on how the four pad centres are joined, and an earlier **≈33 mm² (+36 %)** quoted here is not reproducible — against ≈24 mm² before, because the inductor body is bigger."* |

The sentence's point is kept: the `L1` move did not buy a smaller loop. What changed is that the
board no longer claims a precise +36 % that a pad-centre polygon does not reproduce, and the
following sentence ("a modest EMI/ripple penalty, not a functional problem") still reads correctly.

---

## 4. §9.1.1 front-button solder-bridge tabs — both numbers, as the author asked

Answers **LAY-D1 / LAY-07 / HMI-13**, where the author's refutation was *"the 0.30 mm was designed as
the distance between exposed copper… please report both numbers."* Both are now in the text.

| File | Line | Before | After |
|---|---|---|---|
| `docs/HARDWARE.md` | 913–919 (§9.1.1) | *"Each tab stops **0.3 mm short** of its ring, with the solder mask opened over the tab tip, so a small blob of solder from an iron closes the gap."* | *"Each tab stops short of its ring by two different measurements, and both matter. **Exposed copper to exposed copper is 0.30 mm** — the 0.6 × 0.6 mm `F.Mask` window on the tab tip to the ring's own mask opening, with mask expansion set to 0 — and that is the gap a solder blob actually has to cross. **Copper edge to copper edge, underneath the solder mask, is 0.151–0.188 mm**, because the mask window sits entirely on the 0.8 mm tab; the board's minimum clearance rule is 0.15 mm, so this is inside the rule but with very little to spare. With the solder mask opened over the tab tip, a small blob of solder from an iron closes the gap."* |

---

## 5. New §13.1 — "Firmware contract — things the board needs firmware to do"

No firmware section existed (`grep -n -i "firmware"` found only scattered cautions inside §3.7, §4 and
§7), so this is a **new subsection**, added at the end of §13 rather than as a new top-level section,
so nothing had to be renumbered.

| File | Line | Change |
|---|---|---|
| `docs/HARDWARE.md` | 72 (table of contents) | Added sub-entry `- 13.1 [Firmware contract — things the board needs firmware to do](../../HARDWARE.md#131-firmware-contract--things-the-board-needs-firmware-to-do)` under item 13 |
| `docs/HARDWARE.md` | 1148–1197 | New `### 13.1 Firmware contract — things the board needs firmware to do` inserted after the "All five analog signals are on ADC1" paragraph and before the `---` / `## 14. Design themes` |

### Bullets and the findings they answer

| Bullet | Answers | Checked against |
|---|---|---|
| `USB_STAT` idle threshold `> 2.6 V`, not `> 3.10 V`; nominal 1.98 / 1.19 / 0.60 / 3.3 V | **USB-01** (and its doc half **USB-14**) | `sections/01_usb_input_power_path.md` L296, L322–337, L730 — ATTEN3 range 0–2900 mV ±50 mV (datasheet Table 5-6); nothing between 2.07 V and 3.27 V |
| Accept `0.85–1.35 V` charging and `0.40–0.70 V` complete for the weak-USB cases 0.96 V / 0.53 V | **USB-02** | `sections/01…` L233–238, L297, L731 — state E (`ST`+`CHRG`) = 0.956 V, state F (`ST`+`STDBY`, VBUS < ~4 V) = 0.531 V |
| Require a stable reading for seconds before reporting "charged"; no-battery blink 0.60 V ↔ 0.45 V; cold plug-in with no cell reads a steady 3.3 V | **USB-V02**, **USB-18** | `sections/01…` L317, L613 — 0.595 V "complete" and the blink's high half are *the same pin state* by construction; CHRG+STDBY = 0.450 V; `CE` gate keeps the charger off at a cold plug-in |
| `ADIM` is the enable: first HIGH pulse ≥ 40 µs (`tADIM_EN`), LOW > 2.5 ms (`tADIM_SD`) shuts down; drive HIGH ≥ 100 µs then start the carrier | **LED-14** | `sections/07_led_frontlight_driver.md` L244–255, L297, L611 — TI SNVSCN8 §6.5; 25 kHz/50 % gives only 20 µs |
| OVP latches after three trips; recover with `PWM_LED` LOW > 2.5 ms (≥ 3 ms) or a power cycle; monitor `LED_MONIT`; never enable the boost with `J3` unplugged | **LED-V02** | `sections/07…` L300, L356–366 — SNVSCN8A §7.3.6 / §7.4.2 |
| Colour select only with PWM duty at 0 | **REC-C-01** | `comparison/C_vs_audit_2026-09-16_and_nextpcb.md` L196–215 — `Q5` direct vs `Q6` through `U12`, no guaranteed non-overlap |
| Park the SD bus before gating `SD_VDD` off | **SD-01** | `sections/05_sdmmc_microsd.md` L315, L641 — 3.3 × 100/(100 + 2.007) = **3.235 V** back-feed |
| Deep-sleep wake is RTC-capable `GPIO0`–`GPIO21` only; `IO18` wakes, `IO41` does not, DS3231 `INT`/`SQW` not routed | **HMI-04** (author: *"Doesn't need to. I'm not making an alarm clock."*) | `evidence/blocks/mcu.md` L245 (`IO18` → `PWR_BUTTON`), L268/L542 (`IO41` → `TP_INT`); §13 GPIO map already flags `IO41` as "**not** RTC-wake" |
| 0 V / protection-latched pack will not charge (gate needs ~1.7 V at `J5`); after a protection trip the board restarts only on USB | **REC-A-02**, **REC-B-03** | `comparison/A_vs_DESIGN_REVIEW.md` L273–290 (`Q9` BSS138 Vth 0.5–1.6 V behind a 0.909 divider ⇒ 0.6–1.8 V across the lot, worst case ≈1.7 V); `comparison/B_vs_audit_2026-09-18.md` L308 (`Q8` gate on system `GND`) |

### Pin/net names — all verified, none were wrong

Checked against `evidence/blocks/usb.md`, `led.md`, `sd.md`, `mcu.md`:

| Net | Module pin | Verified in |
|---|---|---|
| `USB_STAT` | `U4.17` = `IO9` (ADC1_CH8) | `usb.md` L239 |
| `PWM_LED` | `U4.35` = `IO42` | `led.md` L206 |
| `COLOR_SEL` | `U4.33` = `IO40` | `led.md` L155 |
| `LED_MONIT` | `U4.38` = `IO2` (ADC1_CH1) | `led.md` L187 |
| `SD_ACTIVATE` | `U4.18` = `IO10` | `sd.md` L126 |
| power button | `U4.11` = `IO18`, net is **`PWR_BUTTON`** (not `PWR_BTN`) | `mcu.md` L245, L486 |
| `TP_INT` | `U4.34` = `IO41` | `mcu.md` L268, L542 |

**One technical refinement to the brief, worth flagging.** The task text said to drive the SD bus
*"LOW or high-impedance"* before gating `SD_VDD` off. High-impedance alone is **not** sufficient if the
ESP32's *internal* pull-ups are left enabled: `sections/05_sdmmc_microsd.md` L641 computes that case
explicitly (5 ∥ 55 kΩ ⇒ `SD_VDD` still sits at **2.97 V**). The bullet therefore says *"LOW as outputs
with the internal pull-ups disabled, hold ≥ 20 ms"*, which is the section's own recommendation.

`SD_ACTIVATE` "HIGH = gate off" is consistent with the §13 GPIO map's existing "(active low)" note —
the gate is *enabled* when the line is low — so both phrasings are kept and do not contradict.

---

## Left for the author (cannot be done from here)

1. **`DESIGN_REVIEW.md` line 288** still says *"GPIO46 is input-only."* — same MCU-19 error, in a
   do-not-touch file.
2. **`DESIGN_REVIEW.md` still describes `Q3`/`Q8` as AO3419** (item 6 of the brief) — do-not-touch file.
   Occurrences: lines **164, 229, 237, 247** (body-diode analysis, the Q8 proposal, the pin table and
   the R<sub>DS(on)</sub>/stress arithmetic). Note the file is already internally inconsistent about
   this: line **201** says *"Applied with `Q_pass` = AO3401A, not the AO3419 named when this table was
   first drafted — AO3401A was already the board's adopted P-channel swap for Q2/Q3/Q7/Q8."* So the
   correction is to make lines 164/229/237/247 agree with line 201, and to re-check the 140 mΩ / 20 V
   numbers on line 247, which are AO3419 figures applied to a part that is not fitted.
3. **The schematic's USB Status note block** still declares `4) Plugged in & Charger Idle/Disabled:
   ~3.30 V [Window: > 3.10 V]` (**USB-14**). `HARDWARE.md` and the schematic now disagree in the
   *opposite* direction from before: the doc is right, the schematic is not. That is a KiCad text-box
   edit (`*.kicad_sch` is on the do-not-touch list).
4. **The `D3` front-light design-note text box** on the schematic says *"Recommended to run between
   10kHz–25kHz via PWM_LED"* without the enable-pulse caveat (**LED-14**) or the OVP latch
   (**LED-V02**). Same KiCad text-box edit.
5. **Measure the actual charge current** on a real board — the §3.2 text now says to, and no document
   can settle it.
