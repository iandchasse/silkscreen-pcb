# Silkscreen Reader PCB (Rev 1.01) — Quantitative EMI/EMC & Signal Integrity Analysis

> **Status: INFORMATIONAL REFERENCE ONLY — NOT QUEUED FOR ACTION.**
> This document captures the Part III board-level electromagnetic compatibility (EMC), return-path, switching-loop, 2.4 GHz RF keepout, and IEC 61000-4-2 ESD analysis extracted from `silkscreen_pcb.kicad_pcb` (`master` @ `80f70e9`, Rev 1.01). It is preserved as an engineering reference for future revisions or pre-compliance testing and is **not** part of the active change queue in [`AUDIT.md`](./AUDIT.md).

---

## 1. 2-Layer Stackup & Return-Path Integrity

### 1.1 Inverted Layer Geometry & Routing Totals
Because `silkscreen_pcb.kicad_pcb` ($h = 1.60\,\text{mm}$ FR-4 core, $\varepsilon_r \approx 4.4$) uses the front face (`F.Cu` / `F.SilkS`) as a clean visual bezel, **components and primary routing live on `B.Cu`**:

| Layer | Footprints | Track Segments | Total Track Length | Nets Routed | `GND` Pour Islands (`filled_polygon`) |
|---|---:|---:|---:|---:|---:|
| **`B.Cu`** (Component & Primary Routing) | 181 | 1,298 | **2,200.26 mm** | 91 | 53 islands |
| **`F.Cu`** (Bezel Face & Secondary Routing) | 8 | 437 | **1,493.83 mm** | 46 | 16 islands |
| **Total** | **189** | **1,735** | **3,694.08 mm** | — | — |

* **Via Count:** **197 vias** ($0.60\,\text{mm}$ pad / $0.30\,\text{mm}$ drill) — **74 `GND` stitching vias** and **123 signal/power vias**, plus 39 through-hole `GND` pads (including 12 × $0.20\,\text{mm}$ thermal vias in `U4.41` and 6 × $0.20\,\text{mm}$ thermal vias in `U11.9`).
* **Characteristic Impedance:** Over a $1.60\,\text{mm}$ FR-4 core, a $0.20\,\text{mm}$ microstrip trace backed by an unbroken opposite plane has $Z_0 \approx 126\,\Omega$ ($0.25\,\text{mm} \implies Z_0 \approx 119\,\Omega$), with return current spreading across $\pm 2h = \pm 3.2\,\text{mm}$. Because both `F.Cu` and `B.Cu` carry dense orthogonal routing, **neither layer acts as an unbroken reference plane**.

### 1.2 Opposite-Layer Reference-Plane Void Coverage

| Net | Total Length (mm) | `F.Cu` (mm) | `B.Cu` (mm) | Vias | Length Over Opposite-Layer GND Void | % Unbacked by Opposite Plane |
|---|---:|---:|---:|---:|---:|---:|
| **`SD_CLK`** (up to 40 MHz) | 20.77 | 8.00 | 12.77 | 2 | **5.15 mm** | **24.8%** |
| **`SD_CMD`** | 43.30 | 2.70 | 40.60 | 2 | **7.54 mm** | **17.4%** |
| **`SD_DAT0`** | 38.79 | 0.00 | 38.79 | 0 | **3.37 mm** | **8.7%** |
| **`SD_DAT1`** | 44.41 | 0.00 | 44.41 | 0 | **8.15 mm** | **18.3%** |
| **`SD_DAT2`** | 35.15 | 10.17 | 24.98 | 2 | **10.47 mm** | **29.8%** |
| **`SD_DAT3`** | 41.03 | 3.45 | 37.58 | 2 | **6.39 mm** | **15.6%** |
| **`SPI_SCK`** (10–20 MHz) | 23.80 | 0.00 | 23.80 | 0 | **1.74 mm** | **7.3%** |
| **`SPI_MOSI`** | 25.38 | 0.00 | 25.38 | 0 | **1.99 mm** | **7.8%** |
| **`DP`** (USB 12 Mbps FS) | 45.76 | 7.28 | 38.48 | 3 | **13.91 mm** | **30.4%** |
| **`DN`** (USB 12 Mbps FS) | 46.24 | 7.90 | 38.34 | 1 | **12.05 mm** | **26.1%** |
| **`TPS_SW_NODE`** (`3031_SW`) | 2.50 | 0.00 | 2.50 | 0 | **0.00 mm** | **0.0% (100% solid `F.Cu` GND)** |
| **`EINK_SW`** | 15.38 | 0.00 | 15.38 | 0 | **0.00 mm** | **0.0% (100% solid `F.Cu` GND)** |
| **`LED_SW`** | 179.52 | 137.46 | 42.07 | 6 | **62.56 mm** | **34.8%** |
| **`/GDR`** | 36.31 | 28.01 | 8.29 | 3 | **12.26 mm** | **33.8%** |
| **`/RESE`** | 36.63 | 28.43 | 8.20 | 2 | **10.13 mm** | **27.7%** |
| **`W-`** | 172.93 | 149.15 | 23.77 | 2 | **58.68 mm** | **33.9%** |
| **`C-`** | 188.47 | 165.21 | 23.26 | 3 | **41.19 mm** | **21.9%** |

### 1.3 Key Slot Crossings (`F.Cu` Signals Crossing `B.Cu` Slots & Vice Versa)
* **`SD_CLK` (`F.Cu` segment `(60.85, 82.80) → (56.70, 81.15)`):** Crosses `SD_DAT0` at `(60.85, 82.80)` ($d_{\text{via}} = 0.81\,\text{mm}$), `SD_DAT1` at `(59.87, 82.80)` ($1.64\,\text{mm}$), two explicit `GND` traces at `(58.10, 82.80)` ($2.63\,\text{mm}$) and `(57.35, 82.35)` ($1.85\,\text{mm}$), and `SD_DAT3` at `(56.70, 81.15)` ($1.75\,\text{mm}$).
* **`SPI_SCK` & `SPI_MOSI` (`B.Cu`):** Cross 3 orthogonal `F.Cu` slots: `LDO_IN` at `(74.05, 103.05)` / `(74.80, 102.30)` ($d_{\text{via}} = 6.70 / 5.66\,\text{mm}$), `UNUSED_GPIO_45` at `(76.60, 107.50)` / `(77.00, 107.10)` ($6.84 / 6.58\,\text{mm}$), and `3V3` at `(76.60, 112.70)` / `(77.20, 112.70)` ($7.42 / 6.89\,\text{mm}$).
* **`DP` & `DN` (`B.Cu` main trunk):** Cross 10 orthogonal `F.Cu` traces between `U4` and `J1`: `USB_STAT` `(71.75, 91.28)`, `SD_ACTIVATE` `(72.90, 91.28)`, `UNUSED_GPIO_3` `(73.70, 91.28)`, `3V3` `(76.78, 92.73)`, `LDO_IN` `(80.23, 96.18)`, `UNUSED_GPIO_45` `(81.13, 97.08)`, `USB_VBUS` `(83.70, 99.65)` ($d_{\text{via}} = 6.28\,\text{mm}$), `UNUSED_GPIO_46` `(90.40, 106.35)` ($7.19\,\text{mm}$), `I2C_SCL` `(93.40, 106.53)` ($8.14\,\text{mm}$), and `VBUS_PRE_FUSE` `(95.25, 106.53)` ($6.84\,\text{mm}$).

---

## 2. Switching Converter Hot Loops & Unintended Stubs

### 2.1 Frontlight Boost (`U10` `TPS923610DRLR`, $f_{\text{sw}} = 1.1\,\text{MHz}$)
* **Local Switching Node & Output Loop (Excellent):**
  * `TPS_SW_NODE` (`3031_SW`) is routed 100% on `B.Cu` in 2 segments totaling **`2.495 mm`** (`3.820 mm²` total pad+trace area) over unbroken `F.Cu` `GND` ($C_{\text{par}} \approx 0.093\,\text{pF}$).
  * Output commutation loop (`U10.6 [SW] → U10.5 [VOUT] → C9.2 → C9.1 [GND] → U10.4 [GND]`): `C9.1` `(46.759, 123.825)` is `2.31 mm` from `U10.4` `(48.649, 122.500)` on `B.Cu`, joined directly by a priority-1 solid-connect (`connect_pads yes`) `B.Cu` `GND` zone (`X=[46.7, 49.1], Y=[122.5, 124.9]`). Loop perimeter = **`7.79 mm`**, enclosed area = **`2.43 mm²`** ($L \approx 2.1\,\text{nH}$).
  * Input loop (`C12 → L2 → U10.6 → U10.4 → C12`): Perimeter = **`13.48 mm`**, enclosed area = **`10.02 mm²`**.
* **150 mm Board-Perimeter Stub (`J3` → `J6`):**
  * While the frontlight FPC `J3` `(54.24, 126.00)` sits only `6 mm` from `U10`, `LED_SW` (`179.52 mm`), `W-` (`172.93 mm`), and `C-` (`188.47 mm`) also route on `F.Cu` along the bottom and right edges of the PCB to `J6` `(98.90, 47.97)`.
  * When `J6` is left open, this `~150 mm` branch acts as an open-circuit $\lambda/4$ stub antenna with quarter-wave resonance at:
    $$f_{\lambda/4} = \frac{c}{4 L_{\text{stub}} \sqrt{\varepsilon_{\text{eff}}}} \approx \mathbf{219\text{–}275\,\text{MHz}}$$

### 2.2 E-Paper Inductive Boost / Charge Pump (`L1`, `Q4`, `R14`, `D4`–`D6`, `C11`, `C14`, `C16`)
* **`dV/dt` Node (`EINK_SW`):** `15.38 mm` total trace length on `B.Cu`, `11.93 mm²` net copper area (`3.08 mm²` trace + `9.55 mm²` pads `L1.1`, `C11.2`, `D5.2`, `Q4.3`), backed 100% by solid `F.Cu` `GND` ($C_{\text{tot}} \approx 0.9\,\text{pF}$).
* **High-$dI/dt$ Loop Areas:**
  1. **Loop 1 (`C10 → L1 → Q4 → R14 → GND`):** Perimeter = **`32.18 mm`**, enclosed area = **`30.94 mm²`** (AC switch branch `L1 → Q4 → R14`: `8.60 mm²`; `R14` at `(89.07, 122.51)` sits `4.75 mm` south of `Q4.S` at `(89.50, 117.96)`, adding `5.11 mm` / `~4 nH` source inductance on `/RESE`).
  2. **Loop 2a (`Q4 → D5 → PREVGH → C14 → GND → R14`):** Perimeter = **`36.04 mm`**, enclosed area = **`32.90 mm²`** (`C14` at `(85.50, 125.55)` is `7.90 mm` south of `D5`).
  3. **Loop 2b (`Q4 → C11 → D6 → GND` & `D4 → PREVGL → C16`):** Enclosed area = **`60.50 mm²`** (`D6` at `(79.77, 121.81)` is `9.36 mm` from `C11`) and **`45.65 mm²`**.
  4. **Parallel Vertical Slots Under Cap Bank:** `PREVGH` (`9.40 mm` on `F.Cu` at `X = 85.40`) and `PREVGL` (`6.64 mm` on `F.Cu` at `X = 83.13`) cut two parallel vertical slots in the `F.Cu` ground plane directly underneath `C13`–`C16` and `C20`.

---

## 3. High-Speed Clocks & USB Cable Radiation

1. **SDMMC 4-Bit Bus (`SD_CLK` up to 40 MHz) & EPD SPI (`SPI_SCK`):**
   * Series termination resistors `R21`–`R26` and `R29`–`R34` ($33\,\Omega$) are placed `1.81–2.38 mm` from `U4` pads (slowing edge rates to $t_r \approx 1.8\text{–}2.0\,\text{ns}$, spectral knee $f_{\text{knee}} \approx 160\text{–}175\,\text{MHz}$).
   * After reaching `J7` (`5.5–6.1 mm` from `R21`–`R26`), the SD nets fork into two long branches (`13.8–18 mm` west to `U1` at `(54.0, 79.8)` and `16–36 mm` east to pull-ups `R8`/`R9`/`R53`–`R55` at `X = 78.0` and `U9` at `(79.6, 70.5)`).
2. **USB 2.0 Full-Speed (`DP`/`DN`) & Shield Termination (`R1` $1\,\text{M}\Omega \parallel$ `C1` $1\,\text{nF}$ 0603):**
   * Trunk skew is only `0.89 mm` (`5.4 ps`), negligible for 12 Mbps Full-Speed.
   * `U6` (`TPD4E1U06DBVR` at `(98.00, 99.40)`) is wired as a `7.80–7.89 mm` parallel stub north of `J1`.
   * `J1` shield pads `S1` connect through a `20.40 mm × 0.20 mm` trace ($L \approx 5.5\,\text{nH}$) to `C1` (`1 nF` 50 V 0603, $f_{\text{SRF}} \approx 68\,\text{MHz}$). Under an IEC 61000-4-2 $\pm 8\,\text{kV}$ contact strike ($150\,\text{pF}$ generator), capacitive division charges `C1` to $> 1,040\,\text{V}$ (exceeding a 50 V 0603 MLCC's dielectric breakdown).

---

## 4. 2.4 GHz RF Coexistence & Antenna Keepout (`U4` `ESP32-S3-WROOM-1`)

* **Lateral Clearance in the `Edge.Cuts` Antenna Notch:**
  * `U4` (`(57.50, 102.50)`, $\text{rot} = -90^\circ$) spans $Y \in [93.500, 111.500]\,\text{mm}$ ($18.00\,\text{mm}$ wide), while the `Edge.Cuts` notch spans $Y \in [93.300, 112.000]\,\text{mm}$ ($18.70\,\text{mm}$), leaving `0.200 mm` north and `0.500 mm` south clearance to the FR-4 notch walls.
  * Inside `U4`'s footprint keepout zone (`X=[30.0, 51.0], Y=[92.5, 112.5]`), `(copperpour allowed)` is enabled, allowing `F.Cu` and `B.Cu` `GND` pours to reach within `0.3–0.6 mm` of both flanks of the PCB antenna along $X = 44.3\text{..}50.6\,\text{mm}$.
* **Counterpoise Slot & Throat Vias:**
  * An `F.Cu` `3V3` trace at `X = 52.200 mm` (`Y = 97.700..112.300 mm`) cuts a `14.6 mm × 0.45 mm` vertical slot across `F.Cu` `GND` behind the antenna feedpoint.
  * Antenna-throat ground pads `U4.1` `(52.24, 93.50)` and `U4.40` `(52.24, 111.50)` have their nearest `GND` vias at `5.56 mm` `(55.50, 89.00)` and `9.35 mm` `(51.30, 120.80)`.

---

## 5. Reference Priority List (If Future EMC-Hardening Spin Is Ever Desired)

1. Set `U4` keepout to `(copperpour not_allowed)` on `F.Cu`/`B.Cu`, widen the `Edge.Cuts` antenna notch laterally by $\ge 5\text{–}10\,\text{mm}$, reroute the `X = 52.20 mm` `F.Cu` `3V3` trace east of `U4`, and place `GND` vias beside `U4.1` and `U4.40`.
2. Gate or isolate the `150 mm` `J3`→`J6` `LED_SW`/`W-`/`C-` traces at `J3` (or drop `J6` frontlight pins) and add `100 pF` C0G RF bypass caps at `J3`.
3. Move `R14` north beside `Q4.S`, move `C14`/`C16`/`D6` beside `D5`/`D4`/`C11`, and route `PREVGH`/`PREVGL` on `B.Cu` to keep `F.Cu` unbroken under the EPD cap bank.
4. Move `U1` and pull-ups `R8`/`R9`/`R53`–`R55` adjacent to `J7` to eliminate SDMMC star-stubs.
5. Upgrade `C1` (`J1` shield) to a 1–2 kV MLCC (or `0 Ω` direct bond) with a wide pour and add stitching vias along `DP`/`DN`.
