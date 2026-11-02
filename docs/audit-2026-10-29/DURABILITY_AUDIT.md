# Part durability and fault containment audit (Rev 1.02, 2026-10-29)

Scope: every part except the frontlight boost, which has its own studies ([PTC_THERMAL.md](PTC_THERMAL.md)
and the two before it). Built from the Rev 1.02 netlist and BOM (`silkscreen_pcb.kicad_pcb`,
`fabrication/part_fields.csv`), a geometric scan of the layout, and every existing stress finding in
[DESIGN_REVIEW.md](../../DESIGN_REVIEW.md), [HARDWARE.md](../HARDWARE.md), the 2026-09-30 and 2026-10-15
audits and [BOARD_FAILURES.md](../BOARD_FAILURES.md). Nothing here is measured; numbers are datasheet
limits or estimates, and each item says which.

**The lesson from cases 1 and 2.** Both failures were a part failing into a few ohms on a rail whose
only protection sits well above the current such a short draws. The short then dissipates watts until
something chars. So this audit asks of every rail: *how much power can a short draw without anything
stopping it?*

## 1. Summary

| # | Finding | Severity | Fix | Parts added |
|---|---|---|---|---|
| 1 | **Battery-fed rails (`P+`, `LDO_IN` on battery):** nothing stops a short of about 2.6 Ω or more; it can dump up to about 5 W, from a cell that holds about 1.8 Wh | High | A PTC at `R27` was studied and rejected. Lean: a 68 mΩ `DW01A` sense resistor plus `C34` raised to 0.1 µF, which cuts the worst case to 3.0 W ([PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) §3) | 1 |
| 2 | **3V3 rail:** `U3`'s 0.56–0.87 A limit is the only protection; a 2–6 Ω short takes 0.6–2.9 W (case 2) | High | Fuse the branches that leave the board (below); the rail itself cannot carry a fuse | — |
| 3 | **Touch connector `J4`:** 3V3 leaves the board on a flex through the 0 Ω link `R42`, unprotected | Medium | Replace `R42` with the frontlight's MF-FSMF010X-2 (simulated: trips ≤ 10 Ω at 25 °C) | 0 (swap) |
| 4 | **Expansion header `J6` pin 7 (3V3):** an accessory or a solder whisker shorts 3V3 straight to `U3`'s limit | Medium | One MF-FSMF010X-2 in series with pin 7; 20 mA accessory budget | 1 |
| 5 | **`USB_VBUS` after `F1`:** shorts of 4.7 Ω or more never trip `F1`; up to 4.7 W (3.1 W at 60 °C) | Medium | None cheap; `F1` must hold the 650 mA USB budget. Keep the bench check | — |
| 6 | **microSD supply (`SD_VDD`, behind `Q7`):** a damaged card or debris shorts to `U3`'s limit; `C36`/`C37` sit 2.2 and 3.7 mm from the socket | Medium | No PTC fits (simulated). Firmware keeps the card off after a brownout during SD use; move `C36`/`C37` away from the socket | 0 |
| 7 | **`J1` shield capacitor `C1`** (1 nF, 50 V, 0603): an ±8 kV contact discharge charges it past 1 kV | Medium | 1–2 kV MLCC (already proposed in EMI_EMC_ANALYSIS) | 0 (swap) |
| 8 | **`J1` (Rev 1.02 SMD receptacle):** overhangs the edge 1.2 mm on stakes and pads; whether reflow fills the shell slots is unverified | Medium | Inspect the first board; a case rib behind the plug | 0 |
| 9 | **`U3` thermal on USB:** passes 125 °C junction near 280 mA continuous (about 240 mA in a warm case) | Medium | Firmware/use: keep sustained 3V3 load on USB under about 250 mA (existing guidance) | 0 |
| 10 | Upstream of `F1` (`J1`, `CR1`, `U6`): only the USB source limits a short | Low | Accept; TVS failures are usually hard shorts that a charger shuts down | — |

**Cheapest wins:** items 3 and 4 reuse the frontlight PTC's part (MF-FSMF010X-2: JLC `C210355`,
DigiKey 118-MF-FSMF010X-2CT-ND; alternate MF-PSMF010X-2). That is one BOM line and one JLC Extended fee for three places, and
item 3 adds no placement at all. Prices, simulated coverage and probe points are in
[PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md).

## 2. Fault containment, rail by rail

"Never stopped" means the short's current stays at or below the protection's guaranteed no-trip
point. Source resistances: 0.3 Ω for USB cable and `F1`, 0.25 Ω for the cell and its FETs.

| Rail | What stops a short | Never stopped | Worst power in a short it does not stop | What can short there |
|---|---|---|---|---|
| `VBUS_PRE_FUSE` (`J1`, `CR1`, `F1` in) | the USB source only | any short the source supplies (0.5 A port to 3 A PD) | source-limited: up to about 5 V × 3 A on a PD charger | `CR1`, `J1` (bent contacts, debris), `U6` |
| `USB_VBUS` (after `F1`) | `F1`: 1.0 A hold (0.65 A at 60 °C), 1.95 A trip | ≥ 4.7 Ω (≥ 7.4 Ω at 60 °C) | 4.7 W at 4.7 Ω; 2.4 W at 10 Ω | `C2` (10 µF, hot-plug stressed), `C25`, `U11` `VCC`, `U2` `VIN1`, `Q2` |
| `P+` and `LDO_IN` on battery | DW01A/FS8205A: 120–180 mV across `Q1` plus sense-loop trace, 39–84 mΩ, so 1.4–4.6 A | ≥ 2.6 Ω (4.2 V cell, hot `Q1`) | about 5.2 W at the edge; 1.3–1.7 W at 10 Ω (revised in [PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) §3.2; first estimate 6.8–7.9 W) | `C3` (10 µF 0603), `C26`, `C4` (22 µF 0805), `U2`, `U3` `IN`, `U11` `BAT` |
| `LDO_IN` on USB | `F1` (as `USB_VBUS`) | as `USB_VBUS` | 4.7 W | `C4`, `U2`, `U3` |
| `/P+_FUSE` (`J6` pin 12) | `F2`: 0.75 A hold PPTC | ≥ 4.7 Ω (3.7 V cell), ≥ 5.4 Ω (4.2 V) | 2.6–3.0 W at those values | `CR3`, accessory |
| `3V3` | `U3` limit 0.56–0.87 A (foldback below 1.32 V), thermal shutdown about 165 °C | 1.5–5.9 Ω sits at the limit | 1.9–2.9 W at 3.8–5.9 Ω (case 2: ≈2 W) | `C6`, `C10`, `C21`, `C22`, `C24`, `C30`, `C32`, `C33`, `CR2`, `U4`, `U12`, `U13`, `L1` branch, `J4`, `J6` pin 7, `SD_VDD` |
| `LED_VIN` / `LED_SW` | the frontlight PTC (proposed) | see [PTC_THERMAL.md](PTC_THERMAL.md) | 0.02–0.09 W after a trip | `U10`, `C12`, `C9`, `D3`, `J3`, `J6` pin 5 |

Notes:

- **`P+` is the largest gap on the board.** `F2` guards only `J6` pin 12, not the main battery path
  (`part_fields.csv`). The cell protector reacts only to amps, and a cracked `C3` or a failed `U2`/`U11`
  at a few ohms would run for as long as the cell lasts. This is case 1's physics with up to about 5 W instead of
  1–3 W, and nobody needs to be holding the board.
- **`3V3` cannot take a fuse on the rail itself** (the ESP32 needs up to about 500 mA peaks), but the
  branches that leave the board can, and those are where external shorts come from.
- **`U3`'s thermal shutdown** limits how long its own dissipation can last, but not the 2–3 W in the
  short (case 2 measured a steady 4.2 V at 0.8 A, with no cycling noted).

## 3. Recommendations

### 3.1 `J4` touch supply: swap `R42` for a PTC (no added placement)

`R42` (0 Ω, 0603) links 3V3 to `J4` pin 2 (`/PIN_2`) in the default touch mapping; the alternate
mapping uses `R66`. Fit an MF-FSMF010X-2 (0603) in whichever link carries 3V3. A touch controller draws a
few mA (55 µA hibernated, HARDWARE.md section 16), far below the 0.1 A hold. A short in the flex or the
controller then meets `U3`'s 0.56–0.87 A through 0.9–6 Ω of PTC. Simulated
([PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) §2): it trips shorts up to 10 Ω at 25 °C (6 Ω at
−20 °C) within 12 s, and leaves at most 0.78 W in a short it never trips (2.27 W today).

### 3.2 `J6` pin 7 (3V3 to accessories): one PTC in series

Same part, between 3V3 and pin 7. HARDWARE.md section 11 already steers accessories that need current
to `P+` (pin 12). The simulated drop at 60 °C is 0.26 V at 20 mA and 0.82 V at 50 mA, so publish 20 mA as
the 3.3 V pin's budget on the silkscreen or in the pinout table. A bridged pin 7 then trips the PTC
instead of loading `U3` to its limit.

### 3.3 Battery path: a PTC at `R27` is rejected; use a `DW01A` sense resistor

Studied in [PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) section 3:

- **A PTC at `R27` fails.** Any PTC that carries the 0.6 A board peak without browning out the board is too low in resistance to trip on a 3–10 Ω short. The 0.75 A parts raise the brownout cell voltage from 3.44 V to 3.63–3.82 V and still leave 4.3–5.8 W.
- **The lean is a 68 mΩ sense resistor** between `Q1` pin 3 and the GND pour, with `C34` raised from 2.2 nF to 0.1 µF. The `DW01A` trip point drops to 0.79–1.68 A. The worst never-tripped short falls from about 5.2 W to 3.0 W, at a 41 mV drop at peak.
- **Side benefit:** a test point with 68 mV/A of battery current.

The original reasoning that ruled out the PTC:

`R27` is the 0805 0 Ω "battery-path service jumper" between `Q3` and `Q8`, in series with everything
the cell feeds (and with the charge current). An 0805 PTC there costs no placement. It is not a free
win:

- **Drop.** On battery the board draws Wi-Fi bursts of about 350 mA plus the e-paper, SD card and
  frontlight. A PTC that holds that has 0.1–0.9 Ω, which takes 0.05–0.5 V off `LDO_IN` at the peaks. At a
  3.4 V cell that pushes `U3` into dropout and can brown out the ESP32 (HARDWARE.md section 3.5 already
  gives only a few hundred mV of headroom).
- **Coverage.** A low-resistance part (the kind the drop allows) heats too little in a 3–10 Ω short to
  trip by itself; the frontlight study's electro-thermal method has to show whether any part both holds
  the peaks and trips on a 2–5 Ω short at 3.4–4.2 V.

The measurement still matters: the sense resistor's 1.31× nuisance margin assumes a 0.6 A coincident
peak, and the `Rs` test point is the place to measure it. Until then, the cheapest mitigation is to
lower the odds of the short: `C3` (10 µF 0603) and `C4` (22 µF 0805) are not in a flex-risk spot today
(section 4.1), so keep them out of one in any re-layout.

### 3.4 microSD supply

A card draws up to roughly 100–200 mA in writes. The follow-up study found no PTC that both keeps
`SD_VDD` at 2.7 V or more at 200 mA and trips on a `U3`-limited short
([PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) section 4). Instead, use what is already there:
`R40` turns `Q7` off whenever a short browns the ESP32 out, and firmware can keep the card off after a
brownout during SD use. Separately,
`C36` (2.2 mm) and `C37` (3.7 mm) are the closest power-rail capacitors to any connector on the board,
and the push-push socket flexes the board at every insertion: move them at least 5 mm away, or turn them
so the socket's bending axis runs along their length.

### 3.5 Already proposed elsewhere, still open

- `C1` to a 1–2 kV MLCC (ESD on the USB shield; EMI_EMC_ANALYSIS section 3.2).
- `J1` mechanical support (J1_USB_C_OPTIONS sections 2 and 7–9).
- `U6` routed flow-through rather than via an 8 mm stub (DESIGN_REVIEW section 11).
- Fit `SW6` on boards that will be flashed (case 2's tweezers).

## 4. Other durability checks

### 4.1 Done in this audit

- **Capacitor voltage ratings:** every capacitor is rated 10 V or more. The lowest margins are `C3`
  (10 V on `P+` ≤ 4.2 V), and `C10`/`C12` (16 V on 3V3 and `LDO_IN` ≤ 5.6 V). The e-paper and frontlight
  capacitors are 50 V parts on rails of ±22 V and ≤ 25.5 V. Margins are adequate; DC-bias loss of
  capacitance is a separate matter, already covered for `C9` and the e-paper rails.
- **MOSFETs:** `Q2`/`Q3`/`Q7`/`Q8` (AO3401A) are rated −30 V V_DS and ±12 V V_GS (datasheet) on rails of
  5.6 V or less; `Q4` (IRLML6346) 30 V on ±22 V-class nodes; `Q5`/`Q6`/`Q9` (BSS138) 50 V.
- **Flex-crack scan:** every power-rail capacitor's distance to the board edge, the six mounting holes
  and the seven connectors. Only three sit close: `C36` and `C37` (`SD_VDD`, 2.2 and 3.7 mm from `J7`)
  and `C9` (`LED_SW`, 2.5 mm from the board edge). The rest are at least 3 mm from an edge and 5 mm from
  a hole or connector. Case 2's suspect `C10` was 8.2 mm from the Rev 1.0 `J1`.
- **ESD:** every user-reachable connector has clamps on its pins: `J1` (`U6`, `CR1`), `J4` (`U7`),
  `J6` (`U8`, `U9`, `CR2`, `CR3`, `D3`, `D8`) and `J7` (`U1`, `U9`). The exceptions are `J5` (the battery
  plug, no clamp), `J4` pin 2 in the alternate touch mapping (HARDWARE.md section 8), and the panel
  connector `J2`, which is internal and unclamped.

### 4.2 Existing findings that are still open (bench checks)

| Part | Stress | Numbers | Source |
|---|---|---|---|
| `U3` | thermal on USB | 125 °C junction near 280 mA at 25 °C (240 mA warm); 163 °C at 350 mA by the JEDEC figure | DESIGN_REVIEW §3, HARDWARE §3.5 |
| `U11` TP4056 | thermal | about 0.5 W at 0.25 A from 5 V into a 3.0 V cell; shares a pour with `U3` 12 mm away. `R6` = 10 kΩ halves it ([PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) §5) | DESIGN_REVIEW §3, HARDWARE §3.2 |
| `U2` | hot-plug | 5.60 V worst on `VIN1` with `R84` (6.0 V absolute maximum) | HARDWARE §3.1, BRING_UP 3.2 |
| `L1` | current | 1.1 A saturation; simulated 0.3 A start-up; a fast 3V3 step could ring towards 1 A | HARDWARE §6.2 |
| `R14` | power | 0.1 W 0603 = 183 mA RMS; modelled safe, not measured | DESIGN_REVIEW §7 |
| `D4`–`D6` | leakage | hot leakage and switching overshoot untested | DESIGN_REVIEW §7 |
| `C2`, `C25` | USB inrush | 11 µF on `VBUS` against the 10 µF USB budget | DESIGN_REVIEW §3 |
| `R27` | current | an 0805 0 Ω jumper in the battery path; its rating is not stated anywhere (typically 2 A for 0805) | DESIGN_REVIEW §4 |
| Connectors | mating cycles | not documented for `J2`–`J4` (FPC), `J5` (PH), `J7` (push-push) | — |

### 4.3 Not covered

Long-term reliability (electromigration, solder fatigue, cell ageing), ESD-gun and EMC testing (planned
in CERTIFICATION_AND_TEST_PLAN), and anything that needs a measured board.
