# Silkscreen mainboard: bench bring-up (2026-09-30)

These are the checks that need a meter, a supply or a scope; software can't make them. Work in order and stop at the first wrong value.
- **Board:** Rev 1.0 (`aeb5b39`), the boards from the 2026-09-21 order. Rev 1.01 (2026-09-30) has the same schematic and parts, and its copper changes only near the cut line, so it matters only in §10. Differences are marked **[1.01]**.
- **Coordinates:** KiCad board mm, front view (from netlist.ipc / positions.csv). Every part is on the back, so mirror x when you look at the back.
- **Notation:** `ref.pin`. **[FW]** = needs firmware; unmarked steps work with any image or a blank module.
- **Sources:** HW = docs/HARDWARE.md, AT = AUTHOR_TODO.md, FR = FINAL_REVIEW.md (both in docs/final-review-2026-09-19), RM = README.md, E/L/F = reports 07/08/09 of this audit, GND = reports 05/06. Probe points were checked against `production/netlist.ipc`.

## 0. Tools
- **Meter:** DMM with a 200 mV range, an A range and a low-burden µA range. A µCurrent or PPK2-class meter is better for sleep current.
- **Supplies:** a 2-channel bench supply with current limit. One channel stands in for the cell on a JST-PH lead of checked polarity; the other feeds USB through a USB-C breakout.
- **Also:** an inline USB-C power meter, a 2-ch scope with **10x probes** rated ≥ 50 V, a thermocouple, 28-30 AWG wire, Kapton and a real 1-cell LiPo.
- **High-Z nodes read low.** `USB_STAT`, `BAT_MONIT` and `LED_MONIT` sit behind 1 MΩ-class resistors (values below computed from the ladder).
  - On a 10 MΩ DMM, `USB_STAT` 3.30/2.20/1.11/0.55 V read ≈3.0/2.06/1.08/0.54 V, and `BAT_MONIT` reads about 5 % low.
  - A x1 (1 MΩ) scope probe is useless on these nodes.

## 1. Visual and orientation (unpowered; loupe or microscope)
The Fabrication Toolkit corrects rotation only for SOT-23, SOIC and JST parts; everything else relied on JLC's preview (RM Step 6, F findings 1-3).
- **`D2`** (102.8, 118.3): pad 1 is the cathode (marked end); `D2.2` = `USB_VBUS`. Reversed means dark on USB: harmless, but the preview check missed it.
- **Pin 1 vs silk:** `U2` (85.1, 86.2), `U5` (86.9, 76.6), `D8` (94.5, 55.3). JLC has corrected these before.
- **`U10`** (49.5, 122.0): pin 1, plus the joints. Its pads are 0.229 mm wide vs TI's 0.30 mm (FR REC-B).
- **Diode bands:** `D3` SMAJ26A (93.4, 58.8), band (pad 1) to `LED_SW`; `D4`/`D5`/`D6` B5819W (82.1, 116.0 / 84.6, 116.0 / 79.8, 121.8).
  - None of these is in RM Step 6 or the Toolkit's corrections (F finding 2).
  - Reversed D4-D6: no panel HV rails. Reversed D3: shorts `LDO_IN` through `L2` and U10's body diode (§2 catches this).
- **`J4`** (92.5, 126.0): contacts on the pads. The CPL anchor is 0.73 mm off, which is 1.5 pitches if uncorrected.
- **`U4`** (57.5, 102.5) and **`J7`** (63.05, 84.6): centred on their pads.
- **Present:** late parts `R83` (88.4, 83.9), `C34`, `C7`, `F2` (AT rounds 4-5).
- **Empty:** `R72`, `R74`, `SW6`, `U14`, `TP3`-`TP5`. **Fitted:** `R36`, `R73`. **Never fit `R73` and `R74` together** (HW §9.2).
- **Solder:** `J1` (0.15 mm annular rings), the `U11` and `U4` thermal pads, and the THT joints on `J1`, `J5`, `J6` and the switches.
- **`J5`** (94.85, 66.5): back silk `-  +  CHECK`, with `+` beside pad 2 (`B+`, y 65.5) and `-` beside pad 1 (`B-`, y 67.5) (L §3).
  - Before any cell comes near the board, meter the pack's plug: + must land on pin 2 (RM:63-75, HW §3.3).

## 2. Unpowered resistance (no USB, no cell; `J2`/`J3`/`J4` empty; black on GND at `U3.2` (80.00, 84.15); let the caps charge)
| Rail | Probe (red) | Expect | Wrong means |
|---|---|---|---|
| `USB_VBUS` | `U2.3` / `U11.4` / `C2.1` | climbs to ≈300-400 kΩ (`R38`+`R51` = 400 k ∥ IC pins) | < 1 kΩ: short in `CR1`, `C2`/`C25`, `U2` or `U11` |
| `F1` | `F1.1` to `F1.2` | < 1 Ω | open: `F1` missing or unsoldered |
| `P+` | `U2.6` / `U11.5` | ≈1-2 MΩ (`R12`+`R10` = 2 M) | < 10 kΩ: short on `P+` |
| `LDO_IN` | `U3.1` (80.00, 83.20) | high, climbing; diode test reads OL or > 1.5 V | ≈1.0-1.4 V on diode test: `D3` reversed |
| `3V3` | `U3.5` (77.30, 83.20) | > 1 kΩ, usually tens of kΩ or more, climbing (~60 µF) | < 100 Ω: bridge at `U4`, `U3` or a cap |
| `LDO_IN`-`3V3` | `U3.1` to `U3.5` | not ≈0 Ω | ≈0 Ω: `U3` bridged |
| `LED_SW` | `U10.5` / `TP3` | ≈1.1 MΩ (`R39`+`R41`) | low: `D3` or `C9` short |
| `B+`-`B-` | `J5.2` (red) to `J5.1` | **≈0.99 MΩ** (`R79`+`R80` 1.1 M ∥ `R57`+`R56` 10.01 M; a meter with a high test voltage may read lower) | ≈10 MΩ: `R79`/`R80` open, so Fix 4 is dead and the board never charges. ≈1.1 MΩ: `R56`/`R57` open. < 100 kΩ: something across the cell |
| `B-`-GND | `U3.2` (red) to `J5.1` | open: the FS8205A is off unpowered (the reverse polarity may show a diode via `U5`/`R16`) | ≈0 Ω: `Q1` shorted or bridged, so the protection is bypassed |

## 3. First power (bench supply, current-limited)
**3.1 USB input, no cell.** 5.00 V through the breakout; limit 100 mA, then 500 mA.
- **Current:** tens of mA (an estimate; the docs give no idle figure). At the limit, or a hot part: stop.
- **`D2` lit:** 2.6-3.2 V across `R59` (103.0, 113.3-115.1), i.e. 1.3-1.6 mA. It means USB is present, not charging (HW §3.1).
- **Expect:** `USB_VBUS` `U2.3` ≈5.0 V; `LDO_IN` `U3.1` ≈5.0 V; `3V3` `U3.5` 3.30 V ±1.5 %; `P+` `U2.6` ≈0 V; `CE` `U11.8` **≈0 V**; `USB_STAT` `C23.1` (74.50, 88.28) steady 3.3 V.
- **`CE` at 3.3 V with no cell:** the Fix 4 gate (`Q2`/`Q9`) is stuck on. Fit no cell until fixed (HW §3.3).
- **Missing rails:** no `LDO_IN` points at `U2` rotation; `LDO_IN` but no 3V3 points at `U3`.

**3.2 USB hot-plug transient (scope).**
- **Set-up:** probe `USB_VBUS` at `U2.3`/`C2.1`; short, thick A-to-C cable; stiff 5 V source; trigger on the rise.
- **Pass:** peak ≤ 6.0 V (the TPS2116 absolute maximum). `CR1` clamps only from 7.22 V, and the model's worst case is 6-7.4 V.
- **Over 6 V:** record the source and cable; the next rev adds 1-1.5 Ω of damping (HW §3.1).

**3.3 Battery input** (supply in place of the cell, USB unplugged): 3.80 V, limit 100 mA, + to `J5.2`.
- **Pass:** current = §3.1 minus `D2`; `3V3` = 3.30 V; `J5.1`-GND a few mV.
- **Dead board?** The DW01A can start with its discharge FET open, and after any protection trip only USB restarts the board (HW §13.1). Plug USB in once.
- **Sweep 4.20 to 3.30 V:** `3V3` holds until `LDO_IN` ≈3.3-3.35 V, then tracks it (dropout, HW §16). Log where 3V3 drops below 3.2 V.
- **[FW] Brown-out:** repeat while pulsing Wi-Fi TX and scope `U3.5` for dips below 3.0 V and resets. Expect sag once the cell is below about 3.2-3.3 V (HW §3.5, FR §03).
- **Optional:** with a real cell, sweep USB down from 5 V. The mux moves to the battery at ≈4.00 V (3.63-4.39 V), and `USB_STAT` goes 1.11 to 0.95 V (HW §3.4).

## 4. Battery only: rails and back-feed (USB cable and UART adapter unplugged)
- **`USB_VBUS`** `U2.3`/`U11.4` **≈0 V**, and **`D2` dark** (≈0 mV across `R59`; 0.2 V = 0.1 mA).
  - 2-3 V, or a faint glow, is back-feed into the unpowered TP4056. The likely path is `CE`, which `Q2` drives to 3V3 on battery.
  - It blows the sleep budget. Next rev: feed `Q2`/`R81` from `USB_VBUS` (E §5, AT §F, FR §03).
- **`USB_STAT`** `C23.1` **2.20 V** (≈2.06 V on a 10 MΩ DMM).
  - 0.7-1.2 V: the unpowered TP4056 clamps `CHRG`/`STDBY`, so firmware can't tell battery from USB (E §5).
  - 3.3 V: `ST` is not asserting (`U2.8`/`R17`).
- **`CE`** `U11.8` ≈3.3 V is **expected** on battery (this is `R82`'s 3.3 µA). 0 V with a good cell means Fix 4 (`Q9`, `R79`/`R80`) misses the cell: no charging.
- **`BAT_MONIT`** `C8.1` (68.22, 90.36) = `P+`/2 (HW §3.6).
- **Light off:** `LED_SW` (`TP3`) ≈ `LDO_IN` minus a diode drop, and `LED_MONIT` `C31.1` (55.36, 114.50) ≈ 0.107 × that. Normal (HW §7).
- **[FW, deep sleep] `IO47`/`IO48` back-feed into `VDD_SPI` (HW §6.1):**
  - Across `R5` (73.59 to 75.41, 114.50; the 10 k `RST` pull-up): ≈0 mV. Each 0.1 V = 10 µA into `IO47`.
  - Across `R34` (72.17 to 74.00, 109.00; 33 Ω in `BUSY`): ≈0 mV. Each 1 mV = 30 µA into `IO48`.
  - Sleep current with the `J2` flex in vs out should differ by only a few µA (the panel draws 2-6 µA).
  - A 100-300 µA gap is back-feed: no firmware fix, and the next rev moves `RST`/`BUSY`. A ≈40-70 µA gap means the panel never reached deep sleep.

## 5. Charging (real cell at 3.5-3.9 V; USB through the power meter)
- **Charge current:** DMM A range in series with the cell + lead, or `PROG` at `U11.2` (≈1.0 V in CC, I ≈ V_PROG / 4.7 k × 1100-1200).
  - Expect **0.23-0.25 A**. It varies by lot, so record it. The USB meter shows charge current plus board load.
  - 0 A: check `CE` and `U11.4`. Well above 0.26 A: check `R6` (89.2, 97.1) (AT §F, HW §3.2).
- **`U11` temperature:** up to ≈0.5 W with a 3.0 V cell. The thermocouple also checks the thermal-pad joint.
- **`USB_STAT`:** charging 1.11 V; done 0.55 V (at about C/10, with `PROG` ≈0.1 V); weak USB 0.95/0.51 V. Float at `J5` 4.2 V ±1 % (TP4056 datasheet) (HW §3.7).
- **Pull the cell on USB:** `USB_STAT` alternates **≈0.55 V (`STDBY`) / ≈0.41 V (`CHRG`+`STDBY`)**. If it goes to a steady 3.3 V instead, Fix 4 has switched the charger off, which is also safe: note which one you see for the firmware.
  - These are the ideal values for the ×10 ladder on Rev 1.0; AT §F's 0.59/0.45 V is the pre-2026-09-21 ladder.
  - Scope with a 10x probe at 0.5-1 s/div and **record the period and duty** for the firmware. The datasheet says 1-4 s; unmeasured.
  - A steady 3.3 V when USB is plugged in with no cell is correct (Fix 4).
- **Protection (optional):** supply in place of the cell, USB unplugged, limit 200 mA. **Never with a real cell; never reverse a LiPo** (HW §3.3).
  - **Over-discharge:** ramp to 2.3 V. Below ≈2.40 V the current drops to a few µA and `J5.1`-GND opens. Only USB restarts it.
  - **Over-charge:** ramp to 4.35 V. At ≈4.30 V (after ≤ ~1 s) the charge FET opens and the load runs through its body diode, so GND-`J5.1` reads ≈0.6 V (a clone may cycle). Lower the supply to recover.

## 6. Sleep current [FW]
- **Firmware state:** `ext1` wake on `IO18`; panel in deep sleep; `ADIM` low; SD gated with the bus parked; touch hibernated with `TP_RST` high.
- **Set-up:** meter in series with the cell + lead. USB and UART unplugged, `J6` empty, no touch tail, `U13` fitted. Short the meter during boot (tens to hundreds of mA).
- **Expect:** ≈58 µA typ (3.7 V, 25 °C), ≈91-95 µA max (4.2 V), ≈56 µA without the panel (HW §16). Log at 3.7 and 4.2 V. AT §F's 73 µA is superseded.
- **Outside the budget:**
  - `U3`'s extra ground current at its real load: +0-20 µA.
  - A cell below 3.3-3.35 V: +190-260 µA (LDO dropout).
  - `U3`'s 25 µA is the largest term and assumes a genuine TI part (FR REC-C).
- **High readings:**
  - +100-300 µA: the §4 back-feed.
  - +18 µA: `R36` and `R72` both fitted.
  - Touch controller: +55 µA hibernated, +220 µA if not, ≈1.1 mA with `TP_RST` low.
  - mA: the `CE`/`D2` back-feed, or an unparked SD bus (`SD_VDD` ≈3.2 V).

## 7. Frontlight (`U10`; `J3` pins: 1 C+, 2 C-, 3/4 NC, 5 W+, 6 W-)
- **7.1 Flex map, before the first enable (LED-12).** A DMM diode test can't forward-bias a ≈15 V string: it reads OL both ways and proves nothing.
  - Board unpowered, flex in `J3`. Use a *floating* supply at 1 mA, ramping to ≤ 16 V, on the through-hole pads.
  - + `TP3` (`LED_SW`, 65.3, 135.4), - `TP4` (`C-`, 61.6, 135.4): the cool string glows at ≈13-15 V. - `TP5` (`W-`, 58.0, 135.4): the warm string.
  - Lights only with the leads swapped: the flex uses the reversed FT01C map. **Don't enable it**; the boost would reverse-bias it (HW §7).
- **7.2 First enable [FW].** `ADIM` (`U10.2`) HIGH ≥ 100 µs, then 10-200 kHz PWM.
  - Across `R37` (50.35 to 48.53, 124.12): ≈0.195-0.206 V × duty, and I = V / 15 Ω ≈ 13.3 mA at 100 % (≤ 13.9).
  - `TP3` shows the string's forward voltage (≈15 V). Record both strings at 100 % and ≈10 % for ΔVf.
  - Optional: hot-plug USB with the light on and watch `LED_SW` for a dropout or restart (`L2` Isat is below U10's current limit, FR REC-C).
- **7.3 Colour change [FW] (AT §F, REC-C-01).** CH1 `TP3`, CH2 `COLOR_SEL` (`U12.2`/`Q5.1`), at 100/50/10 % duty.
  - **Pass:** `LED_SW` re-slews by ΔVf in ≈100-150 µs (≤ ~350 µs) and stays below 23 V (the firmware trip; OVP is 24.25-25.5 V). The light must not latch off.
  - A spike at the switch is the both-off gap: change colour only at duty 0 (HW §13.1).
- **7.4 Open load (optional) [FW],** `J3` and `J6` empty.
  - **Expect:** `LED_SW` climbs to 24.25-25.5 V, retries twice, then latches off. `LED_MONIT` ≈2.6-2.7 V; `D3` stays off (breakdown ≥ 28.9 V).
  - **Recovery:** only `ADIM` LOW for more than 2.5 ms clears the latch.
  - **After:** `C9` decays with τ ≈ 5.3 s. **Wait ≥ 10 s before plugging in a light**; keep hands off `TP3`/`J3` at 25 V (HW §13.1).

## 8. E-paper power [FW: during a refresh; the panel runs the pump]
- **Rails** (10x probes; two are negative):
  - `PREVGH` `C14.2` (84.47, 125.55) / `J2.21`: ≈+22 V. `PREVGL` `C16.2` / `J2.23`: ≈-22 V.
  - `VSH1` `C13.2`: ≈+15 V. `VSL` `C15.2`: ≈-15 V.
  - `VSH2` `C17.2`, `VDD` `C18.2`, `VPP` `C19.2`, `VCOM` `C20.2`: the docs give no values.
  - The exact limits are in SSD1677 Table 11-1, which the docs don't copy (HW §6.2).
- **`GDR`** (`Q4.1`) **and `RESE`** (`Q4.2` / `R14.2`, 88.15, 122.51):
  - **Pass:** clean pulses, with `RESE` peaks well under Isat × `R14` (1.1 A × 2.2 Ω ≈ 2.4 V).
  - **Fail:** runaway or ringing means saturation. `R14` 2.2 Ω and `L1` 47 µH are not bench-verified.
- **`3V3` rise** at `U3.5` at plug-in with the panel connected: if it is faster than ~50 µs, `L1`/`C14` can ring toward 0.8-1.0 A (HW §6.2).

## 9. RTC and miscellaneous
- **RTC** `U13` runs VBAT-only: `U13.6` (61.27, 122.55) = 3.3 V and `U13.2` (62.54, 127.50) = 0 V. There is no backup cell, so no backup current. **[FW]** The oscillator starts only after the first I²C write (HW §10).
- **Power button** (uncut board): `IO18` at `R76.1` (76.30, 69.40) is 0 V idle and ≈3.0 V pressed. 1.76 V idle means `R36` and `R72` are both fitted (HW §9.2).
- **QR codes** (front, y ≈ 132-140): phone-scan all four. Six tented 0.3 mm vias sit inside them (≤ ~1.9 modules per code), so they should still decode (L).
- **UART:** `TP1` RX (57.4, 116.0), `TP2` TX (57.4, 113.9).
- **[FW] LDO temperature:** under sustained load, on USB, in the case, thermocouple on `U3`. The ceiling on USB is ≈250 mA continuous (HW §3.5).
- **[FW] SD switch-on:** scope `U3.5` as `SD_VDD` switches on (`Q7` switches in µs). `3V3` must stay above 3.0 V (FR REC-C).

## 10. Cut-down (x3) boards
The documented cut runs at y 61.86, x 84.42-104.24; the x3 build cuts at y 62.00. It removes `J6`, `U8`, `CR2`, `CR3`, `D3`, `D8`, `F2`, `SW10` and `H1` (HW §16).
- **Before cutting:** unplug USB and disconnect the battery. The cut crosses raw `P+` and other live nets, so saw it rather than snap it (FR §2 item 3).
- **3V3 wire (1.0).** The cut leaves `Q2.2` (Q2's source) and `R81.2` without 3V3, so `CE` never goes high and the board never charges (E §4).
  - Either bridge the two cut 3V3 stubs at the cut edge (x 87.53 and 100.60), or run a wire of about 17 mm from a main 3V3 pad (`R40.2` (82.44, 73.50), `U3.5` (77.30, 83.20) or `C6.1` (75.10, 83.76)) to `Q2.2` (93.71, 87.31) or `R81.2` (94.90, 85.31).
  - Check: with a correctly oriented cell, `CE` (`U11.8`) = **3.3 V**.
  - **[1.01]** 3V3 is rerouted along y 64.2-65.1, so no wire is needed. Still check `CE`.
- **GND wire (boards made before Rev 1.01).** After the cut, the power group (`U3.2`, `U2.1`, `Q1.3`, `C3`, `C4`, `C6`, `C25`, `C26`, `R16`, `R51`, `R77`, `H5`) meets main GND only through **one `J7` shell tab**.
  - **Fit a short wire** from `C6.2` (75.10, 85.84, power-side GND) to `C21.2` (74.80, 80.34, main GND): 5.5 mm, both on the back (GND §2 of the audit).
  - `U3.2` (80.00, 84.15) to `U4.1` (52.24, 93.50) reads ≈0 Ω while J7's shell tab is soldered, so a meter cannot prove the copper is continuous; open means that tab joint is bad.
  - **[1.01]** GND stitching vias below the cut join the two grounds, so no wire is needed.
- **Power button (`SW10` is cut off).** Remove `R36` (46.5, 79.0) and `R73` (49.9, 79.0) **first**, then fit `R72` (10 k) and `R74` (0 Ω).
  - 3V3 to GND must not be a short.
  - `R76.1` should read 0 V idle and ≈3.0 V with UP(2) pressed (HW §9.2).
- **Seal the cut edge.** Live nets reach it, including 3V3 at x ≈101.1 (about 2 mm on 1.01, 6.1 mm on 1.0) (E §4).
- **`LED_SW` has no TVS** once `D3`/`D8` are cut off; U10's OVP (≤ 25.5 V) is the only limit.

## Not faults
- `D2` lights on any USB, charging or not.
- `U13.2` is at 0 V.
- `LED_SW` is non-zero with the light off.
- Plugging in USB with no cell gives no blink.
- `B-`-GND reads open unpowered.
- After a protection trip, only USB restarts the board.
- The dangling F.Cu stubs in the bottom button row carry no net (HW "Things that look like mistakes").
