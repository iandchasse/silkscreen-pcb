# Silkscreen — Hardware Design Documentation

**An open-source, open-hardware e-reader base board.**
Display agnostic · case agnostic · firmware agnostic · battery agnostic.

Successor to [de-link](https://de-link.me).

---

> ### ⚠️ About this document
>
> **This documentation was written *after* the board was designed. It was not used to design it.**
>
> Silkscreen was designed by its author working from datasheets, reference designs and
> hands-on iteration. This document is a **post-hoc explanation and review aid**, produced
> by tracing the finished schematic net-by-net and checking each block against the
> manufacturers' datasheets. Its purpose is to (a) make the board understandable to
> newcomers, and (b) support review and incremental tweaking — whether you are building it,
> modifying it, or writing firmware for it.
>
> Nothing here should be read as "the design rationale that produced the board." Where this
> document explains *why* something is the way it is, that is a reconstruction — informed by
> the designer's own schematic annotations and by what the circuit demonstrably does, but a
> reconstruction nonetheless.
>
> **Open issues, component qualification, proposed changes and the assembly decision live in a
> separate document: [`DESIGN_REVIEW.md`](../DESIGN_REVIEW.md).** This file describes the board
> *as it is* and flags — inline, where it matters for understanding or firmware — the places
> where the review found something that needs attention (reverse-battery path, the `Q4`
> switching device, the microSD socket fit, frontlight current margin). It does not repeat the
> review's analysis; it points to it.
>
> Connection facts were re-checked against the KiCad netlist on **2026-09-17**; designed in
> **KiCad 9.0.6**. The ordered module is **ESP32-S3-WROOM-1-N16R8**.
> 173 references, 126 nets, single A2 sheet.
>
> **Current full plots:** [`silkscreen_pcb_schematic.pdf`](silkscreen_pcb_schematic.pdf)
> (schematic) is the authoritative, up-to-date view. [`silkscreen_pcb_layout.pdf`](silkscreen_pcb_layout.pdf)
> **predates the reviewed PCB** — use the KiCad source and the review's current copper exports
> for layout decisions. The per-block screenshots in `images/` are illustrative and may lag the
> latest revision — regenerate them from KiCad if a block looks out of date.

---

## Table of contents

1. [What Silkscreen is](#1-what-silkscreen-is)
2. [System overview](#2-system-overview)
3. [Power chain](#3-power-chain)
   - 3.1 [USB-C input & protection](#31-usb-c-input--protection)
   - 3.2 [Battery charger](#32-battery-charger)
   - 3.3 [Cell protection & reverse polarity](#33-cell-protection--reverse-polarity)
   - 3.4 [Power-path mux](#34-power-path-mux)
   - 3.5 [3.3 V regulation](#35-33-v-regulation)
   - 3.6 [Battery monitoring](#36-battery-monitoring)
   - 3.7 [USB / charge status](#37-usb--charge-status)
4. [The processor](#4-the-processor)
5. [Storage — 4-bit SDMMC](#5-storage--4-bit-sdmmc)
6. [Display interface](#6-display-interface)
   - 6.1 [24-pin e-paper connector](#61-24-pin-e-paper-connector)
   - 6.2 [Charge pump](#62-charge-pump)
7. [Frontlight driver](#7-frontlight-driver)
8. [Touch interface](#8-touch-interface)
9. [Human input](#9-human-input)
   - 9.1 [Button ladders](#91-button-ladders)
   - 9.2 [Power button](#92-power-button)
   - 9.3 [Boot & reset](#93-boot--reset)
10. [Real-time clock](#10-real-time-clock)
11. [Expansion header](#11-expansion-header)
12. [Test points & mounting](#12-test-points--mounting)
13. [Complete GPIO map](#13-complete-gpio-map)
14. [Design themes](#14-design-themes)
15. [What changed from de-link](#15-what-changed-from-de-link)
16. [Design notes & conventions](#16-design-notes--conventions)

---

## 1. What Silkscreen is

Silkscreen is a **base board for e-ink development**. The goal is that one PCB should support
essentially any 24-pin SPI e-paper panel, any battery, any enclosure, any button layout and
any firmware — so that the interesting work (the display, the case, the software) is not
gated on redesigning power and interface electronics every time.

**Primary target:** 4.26" GDEQ426T82 family
- `GDEQ426T82` — plain
- `GDEQ426T82-FL01C` — with bonded frontlight
- `GDEQ426T82-FT01C` — with bonded frontlight **and** capacitive touch

**Also supports:** most 24-pin SPI e-paper panels, larger or smaller, given a suitable enclosure.
A 24-pin connector alone does not establish compatibility — check the panel's pinout, drive
requirements and voltage rails.

### The four "agnostic" goals, and how the hardware delivers them

| Goal | Mechanism |
|---|---|
| **Display agnostic** | Standard 24-pin 0.5 mm ZIF (`J2`) carrying SPI + the full HV rail set. The panel's own controller drives the charge pump, so the board adapts to the panel rather than the reverse. |
| **Case agnostic** | Five `MountingHole_Pad`s; no fixed button positions — buttons reach the outside world through connectors and a resistor-ladder scheme that costs only one pin per group. |
| **Firmware agnostic** | Nothing on the board requires a specific software stack. Every peripheral is a standard interface (SDMMC, SPI, I²C, ADC, native USB) with no board-specific handshake. |
| **Battery agnostic** | On-board DW01A + FS8205A protection for a single 4.2 V-charge Li-ion/LiPo cell; a pack with its own protection also works — the two cascade. **Reverse-insertion tolerance is *not* established when USB is present** — verify cable polarity and see [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §4 before relying on it. |

### Optional-by-design

Several blocks are populated only if the chosen panel needs them:

- **Frontlight** (`U10` boost + `J3`) — only if the panel has no bonded light, or has one needing external drive
- **Touch** (`J4` + `U7`) — only for `-FT01C`-class panels
- **RTC** (`U13`) — always useful, but not required to boot (populated in the standard build; omit it if you don't need it)

---

## 2. System overview

![Full schematic sheet](images/full-capture.png)

The whole design is a single A2 sheet. It divides into four domains:

| Stage | Path |
|---|---|
| Input | USB-C → PPTC fuse → `USB_VBUS` |
| Charging | `USB_VBUS` → TP4056 → `P+` (protected cell) |
| Source select | TPS2116 picks `USB_VBUS` or `P+` → `LDO_IN` |
| Regulation | `LDO_IN` → TLV75533P → `3V3` (everything digital) |
| Frontlight | `LDO_IN` → TPS923610 boost → up to 24.5 V (bypasses the LDO) |
| Panel HV | `3V3` → charge pump driven by the panel → ±15–22 V |

The processor sits on `3V3` and reaches the outside world through native USB (no UART bridge),
4-bit SDMMC to the microSD, SPI to the e-paper ZIF, I²C to the RTC and touch panel, and five
ADC channels for the buttons, battery, USB status and frontlight monitor.


**Voltage domains:**

| Domain | Range | Feeds |
|---|---|---|
| `USB_VBUS` | ~4.4–5.5 V | charger, mux input 1 |
| `P+` / `LDO_IN` | 3.0–5 V | mux output → LDO, frontlight boost |
| `3V3` | 3.3 V | everything digital |
| *(local)* `LED_SW` | up to 24.5 V | frontlight LEDs only |
| *(local)* panel HV | ±15–22 V | e-paper gate/source rails only |

---

## 3. Power chain

### 3.1 USB-C input & protection

![USB-C input](images/01-usb-input.png)

`J1` is a 14-pin USB 2.0 Type-C receptacle (through-hole). Both VBUS pins and both GND pins are
paralleled, and D+/D− from both sides are tied together — standard for a USB 2.0 sink in a
reversible connector.

**`R2` / `R3` = 5.1 kΩ from CC1 / CC2 to ground.** This is what makes the board a
USB-C *sink*. A source detects those pull-downs and enables VBUS. Two separate 5.1 k
resistors (not one shared) is correct — it lets the source determine cable orientation.

**Input protection chain:** `VBUS_PRE → F1 → USB_VBUS`

- **`F1` `0805L100WR`** — resettable PPTC, **1.0 A hold / ~1.95 A trip at 25 °C**. The hold
  current is temperature-dependent: the Littelfuse derating table gives roughly **0.65 A at
  60 °C**, so a warm enclosure matters even when room-temperature current is below 1 A. A PTC
  does not negotiate USB current. See [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §3.

> **`D1` (the former series Schottky) has been removed.** The design review found it redundant:
> the TPS2116 specifies ~1 nA reverse leakage out of an unselected input, and the TP4056
> datasheet states outright that *"No blocking diode is required due to the internal PMOSFET
> architecture."* Both paths off `USB_VBUS` already block. `D1` also dropped 0.3–0.6 V and, at
> the ~1 A `F1` passes, would have exceeded its own SOD-123 rating. With it gone, `F1` feeds
> `USB_VBUS` directly and `R38` was raised to 300 k (§3.4), recovering that headroom.

**Shield handling:** `R1` (1 MΩ) ∥ `C1` (1 nF) from shell to GND. The classic arrangement —
DC-isolates chassis from signal ground (breaking ground loops) while giving high-frequency
noise a low-impedance path.

**Power LED:** `D2` + `R59` (2 kΩ) across `USB_VBUS`. At 5 V this is **~1.3–1.6 mA** —
deliberately dim. **`D2` indicates USB power present, *not* charging state**; it lights whenever
USB is attached, so it never costs battery runtime. It is a conventional outward-emitting red
1206 (the ordered part and its accepted factory substitution are tracked in
[DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §3 / the BOM).

![USB-C ESD](images/01b-usb-esd.png)

**`U6` `TPD4E1U06`-class array** clamps D+, D−, CC1 and CC2 — a 4-channel, ultra-low-capacitance
(~0.7 pF) TVS array. Low capacitance matters here: anything heavier would distort USB
full-speed edges. **`CR1`** clamps the VBUS rail itself. The ordered `CR1` is an SD05C-class
part with a 5.0 V working standoff on a rail that can reach 5.25–5.5 V; its leakage/standoff
margin is a qualification item — see [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §3.

---

### 3.2 Battery charger

![Charger](images/04-charger.png)

**`U11` `TP4056`-class (ESOP-8)** — a standalone linear Li-ion charger, 4.2 V float.

| Pin | Connection | Meaning |
|---|---|---|
| `VCC` (4) | `USB_VBUS` | charge only from USB |
| `BAT` (5) | `P+` | charges the protected cell |
| `PROG` (2) | `R6` = 4.7 kΩ | **I ≈ 0.25 A** (see below) |
| `TEMP` (1) | GND | NTC thermistor disabled (datasheet-sanctioned) |
| `CE` (8) | `USB_VBUS` | always enabled when USB present |
| `EPAD` (9) | GND | thermal path |

**Charge current ≈ 0.25 A.** `R6` = 4.7 kΩ sets the constant-current phase from
`I ≈ (1100–1200)/R_PROG`, i.e. roughly **234–255 mA** depending on which datasheet constant you
trust; treat this as **~0.25 A intended and measure the actual lot** rather than an exact 255 mA.
Dissipation stays modest — `(5 V − 3.0 V) × 0.25 A ≈ 500 mW` worst case in an ESOP-8 with thermal
vias. `R6` is the knob: a small 300–500 mAh cell wants it higher (`R6` = 12 kΩ ≈ 100 mA) to stay
near 0.25C. **`TEMP` grounded disables cell-temperature monitoring**, so choose the cell and its
charge-temperature range accordingly.

**`CE` tied to `VCC`** means charging cannot be inhibited in firmware — a deliberate
simplification: charging is automatic whenever USB is present.

The `CHRG` and `STDBY` open-drain status outputs feed the status ladder ([§3.7](#37-usb--charge-status)).

---

### 3.3 Cell protection & reverse polarity

![Battery protection](images/05-battery-prot.png)

**`U5` DW01A + `Q1` FS8205A** — the standard 1-cell protection pair.

The DW01A monitors cell voltage and current and drives two N-channel MOSFETs inside the
FS8205A (a common-drain dual):

| Condition | Threshold (typical) | Action |
|---|---|---|
| Over-charge | 4.30 V | `OC` opens the charge FET |
| Over-discharge | 2.40 V | `OD` opens the discharge FET |
| Over-current / short | 150 mV across R_DS(on) | both open |

The FETs are back-to-back so that blocking one direction still permits the other through the
opposite body diode — an over-discharged cell can still be charged, and an over-charged cell
can still be discharged.

**Two details that are easy to get wrong, and are right here (both verified in the netlist):**

1. **`R16` (1 kΩ) from `CS` to the pack-negative side.** The DW01A senses current as the
   voltage across *both* FETs' R_DS(on); its `GND` sits at `B−`. The 1 k also provides
   latch-up protection when a charger meets an over-discharged pack.
2. **`C7` (0.1 µF) between `P+` and `B−`.** It is not tied to system ground — the DW01A's
   ground reference *is* `B−`, so this is exactly the datasheet's recommended VCC decoupling
   cap. (Note the DW01A reference circuit also calls for a 100 Ω VCC filter resistor that is
   absent here; the review treats sense-point/filtering as part of the battery rework — §4.)

**Reverse-polarity intent: `Q3` + `Q8` (AO3419 P-channel).** As built (per netlist): `Q3`
source = `B+`, drain toward `R27`/`Q8`, gate pulled toward `B−` through `R56` (10 kΩ) with
`R57` (1 MΩ) to `B+`; **`Q8` source = `P+`, drain toward `R27`/`Q3`, gate permanently at board
GND.** The design intent is that a correctly polarized cell enhances the series PMOS path and a
reversed cell does not.

> ### ⚠️ Reverse insertion is **not** safe with USB present
>
> The design review identified a fault path that the "reverse-polarity protection" label does
> not cover. **With USB powering the charger, `Q8` can turn on even with a reversed cell**;
> `Q3`'s body diode then leaves a path toward `B+`, and `U5` (VCC = `P+`, GND = `B−`) can be
> driven with a strongly **reversed supply**. "`Q3` is off" does not establish isolation from
> the charger, because a P-channel body diode conducts drain-to-source. Selecting USB in the
> mux does *not* disconnect the charger branch, so normal USB operation does not make this
> harmless.
>
> **Practical guidance:** for a controlled prototype, **verify battery-cable polarity before
> connecting, and disconnect USB during any battery work.** Do not describe the board as
> providing bare-cell / USB-present reverse-insertion protection. **Decided remedy for the next
> spin ("Fix 4"):** the TP4056 `CE` pin is driven high only by a cell-polarity detector referenced
> to raw `B−` (BSS138 + AO3419 + four resistors, ≈3.4 µA idle), so the charger — the only thing
> that energizes the fault path — never runs into a reversed cell. Analysis, simulation and the
> wiring table are in [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §4. **Do not test this by reversing
> a real LiPo** — use a current-limited emulator.

`J5` is a 2-pin battery connector: **pin 1 = `B−`, pin 2 = `B+`.** A matching connector housing
does not guarantee cable polarity — check it electrically. The `R56`+`R57` divider draws ~4 µA
across the cell even after low-side cutoff, because it sits **outside** the protection FETs
where the DW01A can never disconnect it.

---

### 3.4 Power-path mux

![Power path](images/02-power-path.png)

**`U2` `TPS2116DRL`** — a 2:1 priority power multiplexer choosing between USB and battery.

| Pin | Connection |
|---|---|
| `VIN1` (3) | `USB_VBUS` |
| `VIN2` (6) | `P+` (protected cell) |
| `VOUT` (2, 7) | `LDO_IN` |
| `MODE` (5) | `USB_VBUS` → **priority mode** |
| `PR1` (4) | `R38`/`R51` divider from `USB_VBUS` |
| `ST` (8) | status → ladder |

**Priority mode with a threshold divider.** `R38` = 300 k, `R51` = 100 k, `V_REF` = 1.00 V:

```
V_switchover = 1.00 V × (300k + 100k) / 100k = 4.00 V   (≈3.63–4.39 V worst case)
```

Above ~4.0 V on USB, the board runs from USB and the battery is untouched; below it, the mux
hands over to the cell. **Break-before-make** switching (~8 µs) prevents the two sources
shorting; `C4` (22 µF) on the output holds the rail up across the gap. The device also blocks
reverse current at ~42 mV, so a charged battery cannot back-feed a collapsed USB rail.

Lowering `R38` is *not* a free improvement — the threshold spread is already wider than a narrow
LDO-headroom guard band. `ST` is a selection/status output, **not a USB-present comparator**: it
can also read low when a channel is disabled or in thermal shutdown (see §3.7).

**Why a mux rather than diode-OR?** A diode-OR wastes a forward drop continuously and cannot
express priority. The TPS2116's ~40 mΩ FET path costs almost nothing, and priority means the
battery genuinely rests while USB is present.

---

### 3.5 3.3 V regulation

![LDO](images/03-ldo.png)

**`U3` `TLV75533PDBVR`** — 500 mA LDO, fixed 3.3 V, ~25 µA quiescent. *(Replaces the original
AP2112K-3.3 for battery-life reasons. The TLV75533P's pins 1/5 (OUT/IN) are swapped vs the
AP2112K, so the footprint pin-map and `VIN`/`VOUT` routing were adjusted to suit.)*

`EN` is tied to `VIN`, so the rail is **always live** whenever any source is present. There is
no hardware off switch — "off" means ESP32 deep sleep. This is a deliberate simplification
consistent with an e-paper device: the display holds its image with zero power, so "off" and
"asleep" look identical to the user.

Decoupling is generous: `C4` 22 µF in, and on the output `C6` 22 µF, `C32` 22 µF, `C10`
4.7 µF, plus 1 µF and 0.1 µF locals. (`C37`, formerly on this rail, is now 1 µF on the switched
`SD_VDD` rail — see [§5](#5-storage--4-bit-sdmmc).)

**The frontlight boost does *not* run from 3V3** — it is fed from `LDO_IN`, upstream of the LDO.
Boosting to ~20 V from a rail an LDO has already dropped would be a pointless double conversion,
and it would put ~130 mA through a small SOT-23-5. The designer's schematic note says exactly
this: *"Powered via LDO_IN source instead of 3V3 to reduce stress on LDO output power."*

> **U3 shares a 500 mA budget** between the ESP32, SD card, panel logic and touch. That is the
> module's own recommended-supply figure for the MCU alone, so there is no established worst-case
> margin, and the LDO's dropout/thermal behavior on battery at high sustained load is a
> qualification item. The review's owner-stated duty cycle (transient SD/Wi-Fi, no continuous
> refresh) makes this likely fine, but it is measured, not assumed — see
> [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §3 for the full thermal treatment and the thermocouple
> plan.

---

### 3.6 Battery monitoring

![Battery monitor](images/06-batt-monitor.png)

`R12` / `R10` (1 M / 1 M) divide `P+` by two into `IO8` (`BAT_MONIT`), with `C8` (1 µF) as a
reservoir.

- 4.2 V (full) → 2.10 V
- 3.0 V (empty) → 1.50 V

Both sit comfortably inside ADC1's range.

**Why 1 MΩ resistors?** Idle current. 2 MΩ total draws ~2 µA — significant when the whole
board sleeps in the tens of µA. The trade-off is ~500 kΩ source impedance, well above the
ESP32 ADC's ~10 kΩ preference, which is what `C8` compensates for: it holds charge during the
sampling window (RC ≈ 0.5 s). The designer's note reads *"High resistor values → low idle
current."*

**It measures `P+`, not `B+`** — downstream of the protection and reverse-polarity FETs. That
is the right choice: the divider current flows *through* the protection (so the DW01A can cut
it at over-discharge), and a reversed cell cannot drive the ADC pin positive through this path.
The cost is a small load-dependent offset (~7 mV at 50 mA, ~73 mV at 500 mA), so sample when
the radio is quiet. This is a slow monitor, not a fast brownout detector.

---

### 3.7 USB / charge status

![USB status ladder](images/17-usb-status.png)

Three open-drain status signals are encoded onto **one ADC pin** (`IO9`, `USB_STAT`) through a
resistor ladder — a neat piece of pin economy. Each asserted signal pulls its resistor to ground
against the 100 kΩ pull-up (`R70`); `C23` = 2.2 nF filters it (ideal RC ≈ 132 µs).

| State | Asserted | `USB_STAT` (ideal) |
|---|---|---:|
| Idle (USB healthy, charger between states) | none | **3.30 V** |
| On battery (unplugged, or USB too weak to charge) | ST | **1.98 V** |
| Charging | CHRG | **1.19 V** |
| Weak USB: charging while on battery | ST + CHRG | **0.96 V** |
| Charge complete (battery full) | STDBY | **0.60 V** |
| No battery fitted (blinks) | CHRG + STDBY | **~0.45–0.53 V** |

**`ST` reports which input the mux picked, not whether a cable is attached** — it asserts
whenever the mux is on the battery. So `ST`+`CHRG` is not a contradiction: it means **"USB is
attached and charging, but too weak to run the load, so the load is on the battery"** — a
genuine "weak charger/cable" diagnostic. With `D1` removed, a compliant source keeps `USB_VBUS`
above the switchover even at 1 A, so this state appears only with a marginal source.

The "no battery" state is a real TP4056 behaviour — with capacitance on `BAT` but no cell it
cycles between charge and termination, blinking `CHRG` at 1–4 s while `STDBY` stays low. Detect
it by the *transition*, not the level.

> **Firmware cautions (from the review, §9):**
> - The two lowest states (~0.53 V and ~0.60 V) are **too close to separate reliably** after
>   ADC error, output-low voltage, leakage and rail tolerance. Merge uncertain readings into a
>   single **degraded/unknown band** and debounce, rather than trusting an exact level.
> - **Idle 3.3 V can top-code** the ESP32-S3 calibrated ADC range — do not require a reading
>   *above* ~3.10 V to recognize idle, or you will misclassify it.
> - `ST` low is **not** proof of physical USB absence (it also covers disabled/thermal states),
>   and `CHRG`+`STDBY` simultaneously low is not a normal steady charger state. Calibrate on the
>   real device over source voltage. Do not invent an exact "no-battery oscillation" voltage from
>   the ideal ladder.

---

## 4. The processor

![MCU](images/07-mcu.png)

**`U4` ESP32-S3-WROOM-1-N16R8** — dual-core Xtensa LX7, Wi-Fi + BLE, with **16 MB flash + 8 MB
octal PSRAM**. PSRAM matters here: a 4.26" panel at 800×480 needs meaningful framebuffer space,
and e-reader firmware wants room for page rendering and font caches.

**Native USB.** `IO19`/`IO20` connect directly to the USB-C connector's D−/D+ — the S3 has a
USB OTG peripheral, so there is **no CH340/CP2102 bridge**. That removes a part, its power draw
and its driver headaches, and it enables USB Mass Storage (exposing the SD card to a host) and
native DFU. `EN` has 10 kΩ / 1 µF (`R7`/`C5`) startup timing, with `SW11` reset through 100 Ω
(`R63`). There is **no UART DTR/RTS auto-reset circuit** — UART RX/TX come out on `TP1`/`TP2`.

> **Self-powered USB needs a disconnect policy.** After USB removal the MCU stays powered from
> the battery, and there is **no dedicated VBUS-sense GPIO**. Espressif's self-powered
> USB-OTG/TinyUSB configuration expects VBUS monitoring; `USB_STAT` is an analog status mixture,
> not a drop-in digital `vbus_monitor_io`. Firmware may implement a qualified software
> detect/disconnect path but must not equate `ST` with physical USB presence. See
> [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §3.

### Strapping and JTAG-overlapped pins

Boot straps `IO0`, `IO3`, `IO45`, `IO46` must be at valid levels at reset; attached accessories
on the expansion header must respect this (setting a software pull afterward cannot repair a
wrong sampled strap). `IO46` is input-only. **`IO39`–`IO42` overlap JTAG roles**, so firmware
must configure them for their board functions (`I2C_SCL`, `COLOR_SEL`, `TP_INT`, `PWM_LED`);
do not assume a debug configuration is harmless to the connected peripherals.

### `IO35`/`IO36`/`IO37` — the PSRAM pins

`IO37`/`IO36`/`IO35` are consumed internally by the PSRAM bus on **octal-PSRAM** parts (the
`R8` variants, including the `N16R8` fitted here) and **must not be connected or probed**. On
every other S3 variant they are ordinary free GPIO. They are **not broken out** on this board —
IO35–37 have no pads or vias. (The `TP3`–`TP5` designators serve the frontlight driver, not
these pins — see [§12](#12-test-points--mounting).) If a future revision exposes IO35–37 for
non-octal builds, keep the stubs short so an `R8` build cannot load a DDR PSRAM line.


## 5. Storage — 4-bit SDMMC

![SD card](images/08-sdcard.png)

`J7` is a **push-push** microSD socket wired for **4-bit SDMMC**, not SPI. That is a deliberate
performance choice: 4-bit at ~40 MHz is roughly 8× the throughput of 1-bit SPI, which matters
when loading page images or large fonts.

**Contact pinout (identical across the original, TF PUSH and GCT parts):**
`1 DAT2, 2 DAT3, 3 CMD, 4 SD_VDD, 5 CLK, 6 GND, 7 DAT0, 8 DAT1`. Shield/detect pins are
grounded — there is **no independent firmware card-detect signal**.

**Bus conditioning (verified against the netlist):**

| Function | Parts |
|---|---|
| Series termination, all 6 lines | `R21`–`R26` = 33 Ω |
| Pull-ups on DAT0–3 + CMD (to `SD_VDD`) | `R8`, `R9`, `R53`, `R54`, `R55` = 10 kΩ |
| ESD on **CLK, CMD, DAT2, DAT3** | `U1` TPD4E1U06 |
| ESD on **DAT0, DAT1** | `U9` TPD4E1U06 (its spare channel covers expansion `IO46`) |

**33 Ω series resistors** damp reflections — the ESP32's ~30–40 Ω output impedance plus 33 Ω
brings the source close to the ~60 Ω trace impedance (slightly over-damped, good for EMC).
**Pull-ups on data and command, none on clock** — per the SD spec, DAT/CMD are bidirectional
and idle high while CLK is always driven. The pull-ups return to switched **`SD_VDD`**, not
`3V3` (see below). CLK has no pull-up.

### Power gating

The card's `VDD` is **switched** — `Q7` (AO3419 P-FET) with `R40` (100 k) holding the gate off
by default, driven from `IO10` (`SD_ACTIVATE`) through `R78` (1 k). Polarity, stated plainly on
the schematic: **`SD_ACTIVATE` LOW = ON, HIGH (or high-impedance with internal pulls disabled)
= OFF** through `R40`. No actively latched high GPIO is required during sleep — the 100 k pull-up
wins uncontested, and `IO10` (not a strapping pin, no power-up glitch, no reset pull) comes out
of reset with the card unpowered until firmware asks for it.

**Why gate it?** An idle-but-powered SD card draws 0.2–2 mA depending on brand — up to ~20× the
board's sleep budget, with no reliable "sleep" command in SD mode. Cutting power is the only
deterministic fix.

**Everything on the card's rail is switched with it.** All five pull-ups and both decoupling
caps (`C36`, `C37`) connect to `SD_VDD`. If the pull-ups stayed on the always-on rail they would
inject current into the card's I/O pins while its supply was at 0 V, phantom-powering it through
its ESD structures. `R77` (100 k) bleeds the rail down when gated off (RC ≈ 0.11 s no-card;
the card adds capacitance). SD cards need `VDD` below ~0.5 V for a true reset, so the schematic
requires **all data signals driven low before power-off**; verify `SD_VDD` actually reaches a
low level before assuming a short off interval is a real power cycle.

> ### Socket footprint — an open mechanical item
>
> `J7` uses a project-local **dual-source** land
> (`microSD_dualsource:microSD_PushPush_TFPUSH-MEM2075`) intended to accept either the SHOU HAN
> **TF PUSH** (LCSC `C393941`, for JLC-assembled builds) or the GCT **MEM2075** (DigiKey, for
> hand builds). The electrical contacts match, but the **mechanical fit is not yet resolved**:
> the two parts' locating pegs and keepouts differ, and the first assembled build was halted
> over peg-vs-hole fit. The current board uses a slot + round-hole compromise; the saved library
> footprint still differs from the board and the GCT keepout is not fully clear. **Confirm the
> actual socket's pegs/feet against the board before ordering assembly.** Full measurements and
> disposition are in [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §6.

---

## 6. Display interface

### 6.1 24-pin e-paper connector

![E-paper interface](images/09-epaper.png)

`J2` is a 24-pin, 0.5 mm-pitch ZIF (`FH34SRJ-24S-0.5SH`) — the de-facto standard for this
panel class, which is what makes the board display-agnostic.

| Pin | Signal | Connection |
|---|---|---|
| 1, 4 | NC | — |
| 2 | `GDR` | gate driver → `Q4` gate |
| 3 | `RESE` | current sense → `R14` / `Q4` source |
| 5 | `VSH2` | `C17` 4.7 µF/50 V |
| 6, 7 | `TSCL`, `TSDA` | NC (touch uses `J4`) |
| 8 | `BS` | **GND** → 4-wire SPI mode |
| 9 | `BUSY` | `IO48` |
| 10 | `RST` | `IO47`, + `R5` 10 k pull-up |
| 11 | `DC` | `IO21` |
| 12 | `CS` | `IO14` |
| 13 | `SCLK` | `IO13` |
| 14 | `SDI` | `IO12` |
| 15, 16 | `VDDIO`, `VCI` | 3V3 |
| 17 | `VSS` | GND |
| 18–24 | `VDD`,`VPP`,`VSH1`,`VGH`,`VSL`,`VGL`,`VCOM` | decoupling / charge-pump rails |

All SPI and control lines carry 33 Ω series resistors (`R29`–`R34`), matching the SD bus.

**`BS` tied to GND** selects 4-wire SPI (separate D/C pin), letting the panel use a normal
hardware SPI peripheral. **`R5` (10 k) pull-up on `RST`** — the annotation explains it:
*"pull-up on RST recommended to avoid epd wakes when in deep sleep."* Without it a floating
reset can let the panel self-wake and silently drain the battery. **`CS` has no discrete
pull-up** — firmware should establish an inactive `CS` before clock activity and hold defined
panel control levels in sleep (a `CS` pull-up is an optional next-revision improvement, not a
wiring defect).

**Every panel rail is decoupled**, with the HV rails explicitly rated **50 V**: `C13`–`C17`
(4.7 µF/50 V), `C18`–`C20` (1 µF). **Keep the 50 V rating** on any substitution — effective
capacitance under bias is a separate qualification. (Pin 5 is `VSH2`, not `VGH`; the RTC
decoupler is `C30`, not `C22` — see [§10](#10-real-time-clock).)

### 6.2 Charge pump

The e-paper panel needs roughly **±22 V** gate rails and ±15 V source rails, generated on-board.
`L1` and `Q4` form a boost stage whose switch node (`EINK_SW`) feeds two rectifier legs: `D5`
produces the positive rail (`PREVGH` → `VGH`), while `C11` with `D6`/`D4` forms an inverting
charge pump for the negative rail (`PREVGL` → `VGL`). `D4`–`D6` are B5819W (40 V Schottky).

**The panel drives its own supply.** `GDR` (panel pin 2) switches `Q4`'s gate; `RESE` (pin 3)
is the panel's current-sense return through `R14` (3 Ω). The panel's internal controller decides
switching frequency and peak current — the board only supplies the passive power train. This is
architecturally important: the HV rails automatically match whatever panel is fitted, which is a
large part of how one board supports many displays. `R15` (10 k) pulls `Q4`'s gate down so the
pump stays off when the panel is unpowered or high-Z.

**`R14` = 3 Ω** sets the panel's peak switching current. The value comes from a Waveshare
e-paper board (switch-selectable 3 Ω / 0.47 Ω) and has proven reliable at 3 Ω. A **larger** sense
resistor terminates each pulse at a **lower** peak current — less ripple, lower EMI, gentler duty
on `Q4`/`L1` — at the cost of less energy per cycle, so the rails come up more slowly. 0.47 Ω
suits a larger panel needing more gate-drive current; 3 Ω suits a 4.26" panel and is quieter on
a 2-layer board. If a future display shows slow refreshes or sagging gate rails, this is the
resistor to lower.

**`L1`** is a 22 µH metal-composite shielded inductor (3.0 × 3.0 mm) — markedly lower fringing
flux than a ferrite drum, worthwhile on a 2-layer board.

> **`Q4` = Infineon IRLML6346TRPBF (JLC `C67276`).** The first build specified a **BSS138**, which
> does not meet the panel supplier's switch-device criterion (`R_DS(on)` ≤ 0.4 Ω with a low
> gate-drive guarantee; the BSS138 is 3 Ω max at 4.5 V). The IRLML6346 (80 mΩ at 2.5 V) sits on
> the same SOT-23 pads; make sure the factory BOM carries `C67276`. Verify panel-driven switching
> on the bench. `Q5`/`Q6` only select the ~15 mA frontlight branches and stay BSS138. See
> [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §7.

---

## 7. Frontlight driver

![LED driver](images/10-led-driver.png)

Optional block, for panels with a bonded frontlight (or an external light strip).

**`U10` `TPS923610DRLR`** — a synchronous boost LED driver, up to 24.5 V. It boosts `LDO_IN` to
the string's forward voltage on `LED_SW`, which feeds the anodes of both LED strings; each
string's cathode returns through its own N-FET (`Q5` warm, `Q6` cool) to the shared sense
resistor `R37`.

**Constant-current, not constant-voltage.** `U10` regulates `FB` to a ~195–206 mV reference
across `R37`:

```
I_LED = ~200 mV / 15 Ω ≈ 13.3 mA   (nominal 13.3, up to ~13.9 mA with reference + R tolerance)
```

**Target load:** the GDEQ bonded frontlights are **V_f ≈ 15 V, I_f ≤ 15 mA** per channel.
`R37` = 15 Ω sets a ~13.3 mA ceiling (≈13.9 mA worst case) — deliberately under the panel's
maximum; the first build's 13.3 Ω sat right at the limit. The boost runs at ~15 V out from a
3–5 V input, well inside the 24.5 V ceiling. Brightness is dimmed from that ceiling by `ADIM`.

### Warm / cool selection

Both LED strings share **one boost and one sense resistor**; colour is selected by which
string's return path is closed:

- `COLOR_SEL` (`IO40`) → `Q5` gate (warm)
- `COLOR_SEL` → `U12` (74LVC1G04 inverter) → `COLOR_SEL_INV` → `Q6` gate (cool)

Because `U12` inverts, the **static** case is one string on and one off — using an inverter
rather than two GPIOs makes "both strings driven on" impossible in steady state and frees a pin.
The shared `R37` sets total steady current regardless of which string conducts, so a firmware
fault cannot double the *steady* load.

> **What the inverter does *not* guarantee.** On a colour transition, propagation delay and gate
> charge can produce a brief **overlap** or a brief **both-off** interval — the "exactly one
> string ever conducts at every instant" claim is too strong. This matters only transiently, but
> qualify it if you drive fast colour blending. (Review §8.)

`R49`/`R50` (1 M) bleed the two cathode nets so neither floats when its FET is off (so "off" is
microamp-leaky, not mathematically zero). `R75` (100 k) holds `COLOR_SEL` low at boot so the
inverter never sits at mid-rail (which would draw shoot-through).

### Colour-temperature blending

Intermediate CCT is produced by **time-multiplexing `COLOR_SEL`** — the duty cycle becomes the
warm/cool mix. Because total current is set by the shared sense resistor, CCT and brightness are
close to orthogonal (`COLOR_SEL` duty → colour, `ADIM` duty → brightness), the main coupling
being a 10–20 % efficacy difference between warm and cool dies.

The binding constraint on blend frequency is `C9` re-slew: on a colour switch the boost must move
`LED_SW` to the new string's forward voltage, and it can only *discharge* `C9` (= **1 µF**)
through the LED current, so `t ≈ C9 × ΔV_f / I_LED`.

> **Blending is a qualification item, not a solved recipe.** Earlier fixed blend-frequency /
> settling-time tables assumed an obsolete `C9` value and were not backed by board waveforms.
> **Start with fixed warm/cool selection.** Before enabling blending, measure ΔV_f between the
> two strings and each branch's current and output voltage at full and low brightness, and derive
> any needed blanking/dwell from those results. If ΔV_f turns out large, prefer reducing `C9`
> over slowing `COLOR_SEL` into the flicker-visible region. (Review §8.)

### Brightness and enable

`PWM_LED` (`IO42`) drives `ADIM`. Despite being a PWM input this is **analog** dimming: the part
chops its internal reference at the PWM duty and low-pass filters it, so `V_FB = duty × V_ref`
and the LED current is genuinely DC — **no visible flicker**, which matters for a reading light.
TI's recommended carrier is **10–200 kHz**.

> **Two timing facts firmware must honor (review §8):**
> - **`ADIM` is also the enable, and enabling needs an initial HIGH pulse longer than ~40 µs.**
>   At 20 kHz/50 % each high pulse is only 25 µs — *insufficient to enable*. Give an explicit
>   enable pulse with margin first, *then* apply the dimming waveform.
> - **`ADIM` held low longer than ~2.5 ms shuts the part down** (into a ~130 nA state) and resets
>   latched protection.

### Monitoring, protection and connector

`R39`/`R41` (1 M / 120 k) divide `LED_SW` into `LED_MONIT` (`IO2`) with `C31` (100 nF), letting
firmware watch the boost output and apply a software over-voltage limit. `D3` (SMAJ26A) clamps
transients at the connector and `D8` (PESD2IVN-UX) protects the return lines. `U10`'s own OVP is
~25 V typical.

> **Firmware note — off-state is not zero.** A boost always has a DC path from input to output
> through the inductor and the high-side FET's body diode, so with `U10` disabled `LED_SW` sits
> at roughly `LDO_IN` minus **a diode drop** (not a fixed 0.7 V; the exact idle voltage depends
> on leakage/load). `LED_MONIT` therefore reads a small non-zero voltage tracking the battery
> when the frontlight is off — the healthy off state, not a fault. The LED string sees far below
> its ~15 V forward voltage, so nothing lights.

**`J3`** is a 6-pin ZIF. **Owner-confirmed sample mapping:**
`1 C+, 2 C−, 3 NC, 4 NC, 5 W+, 6 W−` — both positive pins to `LED_SW` (common anode), `C−`/`W−`
the switched returns.

> **Procurement warning.** A supplier FT01C drawing shows a **different, reversed** mapping. The
> owner's physical sample matches the schematic above — **keep this wiring for the checked
> sample** — but a genuinely differently-wired panel would reverse-bias the LEDs (not merely
> swap colours), which the TVS parts do not make safe. Record the FPC revision and re-check later
> lots. (Review §8.)

---

## 8. Touch interface

![Touch connector](images/15-touch.png)

Optional block for `-FT01C`-class panels with bonded capacitive touch.

`J4` is a 6-pin 0.5 mm ZIF. **Default pins: `1 GND, 2 3V3, 3 RST, 4 INT, 5 SDA, 6 SCL`** — a
standard I²C touch-controller interface. `TP_RST` (`IO11`) and `TP_INT` (`IO41`) are dedicated;
SDA/SCL join the shared I²C bus (pull-ups `R47`/`R48` = 2.2 kΩ, sized for fast-mode with the
extra FFC/header capacitance). `U7` (TPD4E1U06) provides ESD protection on the four signal lines.

![Touch jumper mux](images/15b-touch-jumpers.png)

**The jumper mux.** Touch panels are inconsistent about pin order, so a re-map is built from
0 Ω resistors — swapping **VDD and INT** between connector pins 2 and 4:

| Config | Fitted | Not fitted (DNP) |
|---|---|---|
| **Default** | `R42` (3V3→PIN_2), `R44` (TP_INT→PIN_4) | `R43`, `R66` |
| **Alternate** | `R43` (TP_INT→PIN_2), `R66` (3V3→PIN_4) | `R42`, `R44` |

Also `R46`/`R52` (default SDA/SCL) vs `R45`/`R58` (swapped). **Choose exactly one option in each
pair** — these are mutually exclusive wiring choices, not spare jumpers to fit together. Confirm
the whole mapping against the specific panel before changing them.

> **`TP_INT` on `IO41` is *not* an RTC-domain wake pin.** It cannot provide ordinary EXT0/EXT1
> deep-sleep wake on the ESP32-S3 (light-sleep GPIO wake is a separate option). Do not confuse an
> external I²C touch-controller interrupt with the ESP32's internal touch-wake hardware; if
> deep-sleep wake from panel touch is required, revise the pin assignment. There is also no
> discrete `TP_INT` pull-up here — if the controller's INT is open-drain, provide a pull-up or
> configure an MCU pull. (Review §10.)

---

## 9. Human input

### 9.1 Button ladders

![Buttons](images/11-buttons.png)

Eight buttons are read on **two ADC pins** using resistor ladders. Each button connects its own
resistor from the ADC node to ground; a 10 kΩ pull-up holds the node at 3.3 V when idle.

**Ladder 1 — `BUTTON_ADC_1` (`IO1`), pull-up `R4` 10 kΩ — the four bottom-edge buttons:**

| Button | Function | Resistor | Voltage |
|---|---|---|---:|
| `SW2` | RIGHT | `R60` 100 Ω | 0.03 V |
| `SW3` | LEFT | `R18` 5.6 kΩ | 1.19 V |
| `SW8` | CONFIRM | `R19` 20 kΩ | 2.20 V |
| `SW9` | BACK | `R20` 56 kΩ | 2.80 V |
| — | idle | — | 3.30 V |

Bottom row, as the user faces the screen: **BACK · CONFIRM · LEFT · RIGHT**.

**Ladder 2 — `BUTTON_ADC_2` (`IO4`), pull-up `R28` 10 kΩ — the four side buttons:**

| Button | Function | Side | Resistor | Voltage |
|---|---|---|---|---:|
| `SW1` | DOWN(1) | right | `R61` 100 Ω | 0.03 V |
| `SW4` | UP(1) | right | `R11` 12 kΩ | 1.80 V |
| `SW5` | DOWN(2) | left | `R35` 33 kΩ | 2.53 V |
| `SW7` | UP(2) | left | `R36` 68 kΩ | 2.88 V |
| — | idle | — | — | 3.30 V |

The `(1)` pair is the **right** edge and `(2)` the **left**, so page-turns work one-handed from
either side. Grouping both sides onto one ADC pin lets a build populate one side, the other, or
both without electrical change.

**Why ladders?** Pin economy — 8 buttons on 2 pins. On a board that already commits pins to
SDMMC (6), SPI (6), I²C (2) and USB (2), that is the difference between fitting and not.

These are **single-press** inputs: both ladders idle high, and multiple keys form parallel
combinations that can alias other keys (the 100 Ω buttons dominate any combination, usable as a
deliberate priority scheme). Single-press levels decode reliably at ±1 % resistors / ±1.5 % rail;
below regulation the levels move with the rail. `C27`/`C28` (2.2 nF) are anti-aliasing, **not
debounce** — mechanical bounce (1–10 ms) is handled in software. Both caps are placed at the
ESP32 per the schematic annotations. The bottom-switch anchors are spaced 12 / 13 / 12 mm with a
common actuator offset that preserves mirror symmetry (no placement asymmetry remains).

### 9.2 Power button

![Power button](images/12-power-button.png)

`SW10` connects `3V3` through `R62` (10 k) to `PWR_BUTTON` (`IO18`), with `R76` (100 k)
pull-down: pressing gives ~3.00 V logic high, releasing a defined 0 V. Because 3V3 is always
live, the power button is a **wake source**, not a true power switch — `IO18` is RTC-capable and
can trigger `ext0` wake from deep sleep.

`R72`/`R73`/`R74` are 0 Ω configuration jumpers. Annotation: *"UP(2) can serve as a power button
if R36/R73 are unpopulated and R72/R74 are populated."* In the reviewed build **`R36`/`R73` are
fitted for normal `SW7`; `R72`/`R74` are DNP.** **Never fit both `R73` and `R74`** — that shorts
the rails through the alternate link.

### 9.3 Boot & reset

![Boot buttons](images/13-boot-buttons.png)

Standard ESP32 programming interface:

| Signal | Circuit | Purpose |
|---|---|---|
| `ESP32_EN` | `R7` 10 k pull-up, `C5` 1 µF, `SW11` via `R63` 100 Ω | reset, ~10 ms RC (**populated**) |
| `ESP32_IO0` | `R13` 10 k pull-up, `SW6` via `R64` 100 Ω | boot mode select (**`SW6` = DNP**; APEM MJTP1243 if fitted) |

Holding `IO0` low during reset enters the ROM bootloader; the 100 Ω series resistors limit
current if firmware ever drives these pins.

**`SW6` (BOOT/`IO0`) is DNP in the standard build** — its land is left unpopulated. It uses a
different land from the side buttons: a vertical 6 × 3.5 × 4.3 mm two-pin THT tactile (**APEM
MJTP1243**, 6.5 mm pin pitch), not the right-angle `TS365ZJ`. Leaving it off is fine for normal
flashing: the ESP32-S3's **USB-Serial-JTAG** lets `esptool` trigger download mode over USB-C
with no BOOT button. The one caveat is recovery — if application firmware fully claims the
USB-OTG peripheral and hangs, forcing download mode then means momentarily grounding `IO0` by
hand (it's on `R64`/`R13`). Fit an MJTP1243 (or an equivalent 6 × 3.5 × 4.3 mm part such as ALPS
SKHLACA010) if you want hardware boot-mode entry.

---

## 10. Real-time clock

![RTC](images/14-rtc.png)

**`U13` `DS3231MZ`** — a temperature-compensated RTC, **±5 ppm (about ±2.6 minutes/year)**.
Populated in the standard build (LCSC `C722467`, DS3231MZ+); omit it if you don't need a clock.

The wiring looks wrong at first glance but is correct (verified in the netlist):

- **`VBAT` (6) → 3V3**
- **`VCC` (2) → GND**

This is the datasheet's **Figure 5 single-supply VBAT-only configuration**, which explicitly
requires `VCC` grounded, not floating. Three consequences firmware must know:

1. The oscillator **does not start until a valid I²C write occurs**, because `VCC` never rises
   above the power-fail threshold. Init code must touch the RTC and check the oscillator-stop
   flag rather than assume valid time at first power-up.
2. `RST` (pin 4) and `INT`/`SQW` (pin 3) are **unconnected** — so there is **no RTC interrupt /
   wake output** to the MCU.
3. There is **no independent time backup**: with no coin cell, time is lost if the battery is
   removed or fully discharged. For an e-reader that is an acceptable trade to avoid a coin-cell
   holder that would fight the "case agnostic" goal.

The RTC's local decoupler is **`C30` = 0.1 µF** (not `C22`). `R47`/`R48` (2.2 kΩ) pull up the
shared I²C bus. (`C22` = 1 µF is a separate 3V3 decoupler in the display area, not an RTC part —
an earlier draft mislabeled it.)

---

## 11. Expansion header

![Expansion](images/16-expansion.png)

**`J6` `PPPC062LJBN-RC`** — a 2×6, 0.1"-pitch female header.

| | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| **row 1** | GND | IO46 | IO45 | GND | LED_SW | W− |
| | **7** | **8** | **9** | **10** | **11** | **12** |
| **row 2** | 3V3 | SDA | IO3 | SCL | C− | P+ |


What it exposes:

| Category | Pins |
|---|---|
| Power | `3V3` (7), `P+` raw battery (12), 2× `GND` (1, 4) |
| I²C | `SDA` (8), `SCL` (10) — shared bus, already pulled up |
| Spare GPIO | `IO46` (2, input-only strap), `IO45` (3, strap), `IO3` (9, strap) |
| Frontlight | `LED_SW` (5), `W−` (6), `C−` (11) — drive external LED strips |

**Pin ordering groups signals by voltage domain**, which matters on a 0.1" header a user can
bridge with a solder whisker. `LED_SW` (pin 5) — the only net that can reach 24.5 V — is bounded
by `GND` (4), `W−` (6) and `C−` (11), all LED-domain or ground. No logic pin touches it.
Likewise `P+` (raw cell) sits at the corner where its only neighbours are the LED returns.

`W−` and `C−` are low-voltage in normal operation (`R49`/`R50` bleed them to ground; the
conducting one sits at the `FB` sense voltage).

![Expansion ESD](images/16b-expansion-esd.png)

**Every signal pin is ESD-protected:** `U8` covers `IO45`/`IO3`/`SDA`/`SCL`, `U9`'s spare
channel covers `IO46`, `CR2` protects the 3V3 pin, `CR3` protects `P+`, `D3` (SMAJ26A) clamps
`LED_SW`, and `D8` (PESD2IVN-UX) covers the `C−`/`W−` returns. The three GPIOs carry 33 Ω series
resistors (`R65`, `R68`, `R69`).

**This is not a general-purpose isolated GPIO header.** It exposes `LED_SW`, switched LED
cathodes and raw `P+` beside logic; external supply injection can back-power rails, and the
strap pins (`IO3`/`IO45`/`IO46`) need boot-time care. Exposing `P+` is deliberate — it lets a
daughterboard draw meaningful current or add its own regulation rather than being limited by the
LDO's remaining headroom.

---

## 12. Test points & mounting

Five test points are fitted:

| TP | Net | Purpose |
|---|---|---|
| `TP1` | `RX` | UART0 RX — ROM bootloader / early boot messages |
| `TP2` | `TX` | UART0 TX — serial debug |
| `TP3` | `LED_SW` | Frontlight boost output (probe the LED rail / software OVP) |
| `TP4` | `C−` | Cool-string cathode return (frontlight bring-up / CCT tuning) |
| `TP5` | `W−` | Warm-string cathode return |

`TP1`/`TP2` are useful even though programming is over native USB, since boot messages come out
on UART. `TP3`–`TP5` make the frontlight driver measurable — handy for setting current, checking
the CCT blend, and confirming the boost output. `IO35`–`IO37` (PSRAM pins on `R8` modules) are
**not broken out** — see [§4](#4-the-processor).

![Mounting](images/19-mounting.png)

`H1`–`H5` are `MountingHole_Pad`s tied to GND — plated holes, so a metal standoff bonds the
enclosure to ground. (Make that a deliberate EMC choice — see [§16](#16-design-notes--conventions).)

---

## 13. Complete GPIO map

Every ESP32-S3 pin, as used (SD series resistors verified against the netlist):

| Pin | GPIO | Net | Function |
|---|---|---|---|
| 3 | EN | `ESP32_EN` | Reset (SW11) |
| 4 | IO4 | `BUTTON_ADC_2` | Side button ladder (ADC1_CH3) |
| 5 | IO5 | — | SD DAT1 (via `R26`) |
| 6 | IO6 | — | SD DAT0 (via `R25`) |
| 7 | IO7 | — | SD CLK (via `R24`) |
| 8 | IO15 | — | SD CMD (via `R23`) |
| 9 | IO16 | — | SD DAT3 (via `R22`) |
| 10 | IO17 | — | SD DAT2 (via `R21`) |
| 11 | IO18 | `PWR_BUTTON` | Power button / wake |
| 12 | IO8 | `BAT_MONIT` | Battery voltage (ADC1_CH7) |
| 13 | IO19 | `DN` | USB D− |
| 14 | IO20 | `DP` | USB D+ |
| 15 | IO3 | — | Spare → `J6` pin 9 (strap) |
| 16 | IO46 | — | Spare → `J6` pin 2 (input-only strap) |
| 17 | IO9 | `USB_STAT` | Charger status ladder (ADC1_CH8) |
| 18 | IO10 | `SD_ACTIVATE` | microSD power gate (active low) |
| 19 | IO11 | `TP_RST` | Touch reset |
| 20 | IO12 | — | EPD SDI (via `R29`) |
| 21 | IO13 | — | EPD SCLK (via `R30`) |
| 22 | IO14 | — | EPD CS (via `R31`) |
| 23 | IO21 | — | EPD DC (via `R32`) |
| 24 | IO47 | — | EPD RST (via `R33`) |
| 25 | IO48 | — | EPD BUSY (via `R34`) |
| 26 | IO45 | — | Spare → `J6` pin 3 (strap) |
| 27 | IO0 | `ESP32_IO0` | Boot mode (SW6, DNP) |
| 28–30 | IO35–37 | `IO3x_PSRAM` | Octal PSRAM on `R8`; not broken out |
| 31 | IO38 | `I2C_SDA` | I²C data |
| 32 | IO39 | `I2C_SCL` | I²C clock (JTAG-overlapped) |
| 33 | IO40 | `COLOR_SEL` | Frontlight warm/cool (JTAG-overlapped) |
| 34 | IO41 | `TP_INT` | Touch interrupt (JTAG-overlapped; **not** RTC-wake) |
| 35 | IO42 | `PWM_LED` | Frontlight brightness / ADIM enable (JTAG-overlapped) |
| 36 | RXD0 | `RX` | UART0 → `TP1` |
| 37 | TXD0 | `TX` | UART0 → `TP2` |
| 38 | IO2 | `LED_MONIT` | Frontlight voltage sense (ADC1_CH1) |
| 39 | IO1 | `BUTTON_ADC_1` | Bottom button ladder (ADC1_CH0) |

**All five analog signals are on ADC1.** ADC2 is unusable while Wi-Fi is active on the
ESP32-S3, so this is a necessary constraint — and with five analog functions it consumes a
substantial share of ADC1's channels.

---

## 14. Design themes

Reading the board as a whole, several consistent principles emerge.

**1. Pin economy as an enabler.** The button ladders (8→2), the status ladder (3→1) and the
shared I²C bus are all the same move. The ESP32-S3-WROOM-1 has ~35 usable GPIO; SDMMC, SPI, I²C
and USB claim 16 before any user interface exists. Multiplexing onto ADC pins is what leaves
room for expansion.

**2. Idle current treated as a first-class constraint.** 1 MΩ dividers, a 100 k gate pull-up, a
power-gated SD card, a ~130 nA-shutdown LED driver, and a 100 k (not 10 k) rail bleed. On an
e-paper device the display costs nothing to hold an image, so standby current *is* battery life.

**3. Defense in depth on power.** PPTC → TVS on the input; DW01A + FS8205A on the cell; a
priority mux that blocks reverse current; back-to-back FETs *intended* for reverse-polarity
blocking. That last item is the qualifier: as-built it does **not** hold when USB is present
(§3.3 / review §4). The rest genuinely make "bring your own cell" a defensible proposition once
polarity is verified.

**4. ESD on everything a user can touch.** USB (`U6`), SD (`U1` + `U9`), touch (`U7`), expansion
GPIO (`U8`), plus `CR1`/`CR2`/`CR3` on rails and `D3`/`D8` on the LED lines. Six arrays on a
board this size directly serves the "hand it to anyone" goal.

**5. Configuration by resistor.** Touch pin swap, power-button reassignment, LED colour routing.
Each is a 0 Ω jumper or DNP option that lets one PCB serve several builds.

**6. Let the peripheral drive itself.** The e-paper charge pump is the clearest case: the panel's
own controller runs the switching, so the board's HV rails adapt to whatever display is fitted —
the single biggest contributor to display agnosticism.

---

## 15. What changed from de-link

Silkscreen is a substantial revision of [de-link](https://de-link.me) rather than a new board.
The predecessor's history lives largely in backups, so this is a summary of the material changes
rather than a commit-level changelog:

| Area | Change |
|---|---|
| **Accessory header** | Refined into the current 12-pin `J6`, grouped by voltage domain and fully ESD-protected |
| **Power path** | Reworked around the TPS2116 priority mux; idle-current behaviour tightened throughout (high-value dividers, power-gated SD, low-shutdown LED driver) |
| **Touch** | Added — `J4` plus the `U7` ESD array and the 0 Ω pin-swap jumpers |
| **RTC** | Added — `U13` DS3231MZ on the shared I²C bus |
| **Frontlight** | Moved from the AP3012 to the TPS923610, gaining proper dimming; the two colour-select GPIOs became one GPIO plus the `U12` inverter |
| **ESD** | Expanded and refined — now six arrays plus three rail clamps |
| **Charge reporting** | Added the `USB_STAT` resistor ladder |
| **Mechanical** | The battery now sits in a cut-out *in* the PCB rather than stacked on top |

The through-line is that de-link proved the concept and Silkscreen makes it a **base board**:
more of the board is optional, more of it is protected, and much more of it is configurable
without a respin.

---

## 16. Design notes & conventions

**Sleep current target.** No numeric spec — the goal is "as low as practical." Estimated
contributors total roughly 65 µA; with the `TLV75533P` (~25 µA quiescent) no single term
dominates (the `USB_STAT` ladder ~13 µA and ESP32-S3 deep-sleep ~13 µA are comparable). The
board is designed so no *avoidable* load remains: the SD card is power-gated, the LED driver
drops to a sub-µA shutdown, and every monitoring divider is 1 MΩ-class.

**Enclosure.** The reference enclosure is 3D-printed, but the board is meant to be housed in
anything. Two implications for a custom case:

- The five `MountingHole_Pad`s are **plated and GND-connected**, so a conductive enclosure will
  be bonded to signal ground through the standoffs — usually good for EMC, but make it deliberate
  (use one bonded standoff and three isolated ones if a chassis ground loop is a concern).
- A conductive case must not bridge the exposed high-voltage nets: `LED_SW` (up to 24.5 V) and
  the panel's ±22 V rails are the ones to keep clear of metalwork.

**Frontlight load.** The GDEQ bonded frontlights are V_f ≈ 15 V at I_f ≤ 15 mA per channel;
`R37` = 15 Ω sets ~13.3 mA at full `ADIM` duty, under the panel's 15 mA maximum (§7).

**Button geometry.** Bottom edge, left-to-right facing the screen: BACK · CONFIRM · LEFT ·
RIGHT. Sides: UP(1)/DOWN(1) on the right edge, UP(2)/DOWN(2) on the left edge.

---

## Appendix — component summary

| Type | Count | Notable |
|---|---:|---|
| Resistors | 82 | all **0603**; incl. 15× 33 Ω series, 6× DNP config jumpers, 4× Fix 4 (R79–R82) |
| Capacitors | 35 | 22× **0603**, 13× **0805** (HV / bulk — see below); 7× 50 V-rated |
| ICs | 13 | see below |
| Switches | 11 | 8 ladder + power + reset (right-angle `TS365ZJ`) + boot `SW6` (APEM MJTP1243, **DNP** → 10 populated) |
| Diodes | 6 | 3× B5819W, SMAJ26A, PESD2IVN-UX, LED |
| Connectors | 7 | USB-C, 24p ZIF, 2× 6p ZIF, microSD, 2-pin battery, 2×6 header |
| Transistors | 9 | 4× AO3419 (Q2/Q3/Q7/Q8; AO3401A is the JLC Basic drop-in — see `fabrication/BOM.md`), 3× BSS138 (Q5/Q6/Q9), IRLML6346 (Q4), FS8205A (Q1) |
| Test points | 5 | UART RX/TX (`TP1`/`TP2`) + frontlight `LED_SW`/`C−`/`W−` (`TP3`–`TP5`) |
| Mounting | 5 | plated, GND |
| TVS | 3 | `CR1`–`CR3` SD05C-class (ordered) |
| Inductors | 2 | 22 µH (charge pump), 4.7 µH (frontlight) |
| Fuse | 1 | 0805L100WR PPTC (0805) |
| **Total** | **179** | standard build: 162 fitted + 10 DNP (TP3–TP5, R43/R45/R58/R66/R72/R74, SW6) + 7 bare-copper refs (H1–H5, TP1, TP2); includes the six Fix 4 parts Q2/Q9/R79–R82 |

**Passive case sizes.** The board standardised on **0603** for hand-solderability at the smallest
comfortable size. **Thirteen capacitors remain 0805** because the value does not exist in 0603 or
DC-bias derating would gut it:

| Refs | Value | Reason |
|---|---|---|
| `C11`, `C13`–`C17` | 4.7 µF @ 15–23 V | **4.7 µF/50 V does not exist in 0603**; the 0603/50 V ceiling is ~2.2 µF (X5R) / 1 µF (X7R) |
| `C4`, `C6`, `C32` | 22 µF | 0603 22 µF/6.3 V delivers only ~6.7 µF at 3.3 V vs ~12.7 µF for the 0805 part |
| `C9` | 1 µF/50 V | Boost output; 0603 holds ~0.19 µF at 25 V bias |
| `C18`–`C20` | 1 µF @ 15 V | Kept with the rest of the `J2` HV cluster |

`F1` (fuse) stays 0805 and `D2` (power LED) is 1206.

**Integrated circuits:**

| Ref | Part | Function |
|---|---|---|
| `U1`, `U6`–`U9` | TPD4E1U06DBVR | ESD arrays (SD data DAT2/3+CLK/CMD on `U1`; SD DAT0/1 + expansion on `U9`; USB `U6`; touch `U7`; expansion `U8`) |
| `U2` | TPS2116DRL | Power-path mux |
| `U3` | TLV75533PDBVR | 3.3 V LDO |
| `U4` | ESP32-S3-WROOM-1-N16R8 | Processor |
| `U5` | DW01A | Cell protection controller |
| `U10` | TPS923610DRLR | Frontlight boost driver |
| `U11` | TP4056-class | Li-ion charger |
| `U12` | 74LVC1G04 | Inverter (colour select) |
| `U13` | DS3231MZ | Real-time clock (populated in the standard build; optional) |

> **Manufacturer note.** Several ordered parts are house-brand equivalents (TECH PUBLIC, MDD,
> PUOLOP, TOPPOWER, etc.) rather than the TI/Onsemi/Nexperia parts the schematic labels suggest.
> The review verified the exact ordered parts' pinouts and keeps their datasheets with the frozen
> order — see [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) §10 and §12.

---

*Silkscreen is open-source hardware. Predecessor project: [de-link.me](https://de-link.me).*
*This file describes the board as it is; open issues and the assembly decision are in
[DESIGN_REVIEW.md](../DESIGN_REVIEW.md).*
