# Silkscreen Reader PCB (Rev 1.01) — Formal Certification Roadmap & Pre-Compliance Testing Plan

> **Status: INFORMATIONAL REFERENCE ONLY — NOT QUEUED FOR ACTION.**
> This document captures the Part IV regulatory certification roadmap (FCC, ISED, CE RED, UL/IEC 62368-1, IEC 62133-2, UN 38.3, EU Battery Regulation 2023/1542), pre-compliance test plan, and Crowd Supply commercial readiness evaluation for Silkscreen Rev 1.01 (`master` @ `80f70e9`). It is preserved for future reference and is **not** part of the active change queue in [`AUDIT.md`](./AUDIT.md).

---

## 1. Regulatory Scope & Commercialization Matrix

The applicable regulatory requirements depend directly on whether Silkscreen is sold as:
* **Model A — Bare Populated PCBA / Developer Subassembly:** Buyer receives the populated Silkscreen mainboard (`60.05 × 111.30 mm`) and supplies their own display panel, Li-Po battery, microSD card, and 3D-printed enclosure.
* **Model B — Complete Consumer E-Reader or Full Bundled Kit:** Seller ships either an assembled handheld e-reader or a complete kit containing all parts in one box.

| Jurisdiction / Domain | Model A: Bare Populated PCBA ("BYO Battery, Display, Case") | Model B: Complete Consumer E-Reader or Full Bundled Kit | Governing Standards & Clauses |
|---|---|---|---|
| **US — FCC Unintentional (EMC)** | **Subassembly** under 47 CFR § 15.101(e) / § 15.103(c); **Part 15B Class B SDoC** strongly recommended once marketed to general DIY consumers | **Mandatory FCC Part 15 Subpart B Class B SDoC** (47 CFR §§ 15.107, 15.109, 2.906) tested per **ANSI C63.4-2014** | 47 CFR Part 15 Subpart B; ANSI C63.4-2014 |
| **US — FCC Intentional (Radio)** | **Modular Grant Leverage** (`FCC ID: 2AC7Z-ESPS3WROOM1`); Host Radiated Spurious Spot-Check per **KDB 996369 D04** | **Modular Grant Leverage** + **Mandatory Host Radiated Spurious Spot-Check** (47 CFR §§ 15.247(d), 15.205, 15.209) + **Portable SAR / RF Exposure** (47 CFR § 1.1307(b)(3)) | 47 CFR § 15.212, § 15.247; ANSI C63.10-2020; KDB 996369 D04; KDB 447498 D04 |
| **Canada — ISED** | Subassembly under ICES-Gen § 2.2(d); Host label `Contains IC: 21098-ESPS3WROOM1` | **Mandatory ICES-003 Issue 7 Class B** + **RSS-247 Issue 3** host spot-check + **RSS-102 Issue 6** portable RF exposure | ICES-Gen; ICES-003; RSS-Gen; RSS-247; RSS-102 |
| **EU / UK — CE / UKCA (RED, EMC, Safety)** | **CE Marking Mandatory** if sold commercially to hobbyists/consumers in EU/UK (RED Annex I(4) exemption applies *only* to B2B professional R&D kits; open-source GitHub files self-ordered by individuals for personal use are not "placed on the market") | **Mandatory CE Marking (RED 2014/53/EU)**: Art. 3.1(a) Safety & SAR, Art. 3.1(b) EMC, Art. 3.2 Radio, Art. 3.3(d/e/f) Cybersecurity (`EN 18031`) | `EN IEC 62368-1`; `EN 50566`/`EN 50663`; `EN 301 489-1/-17`; `EN 55032`/`55035`; `EN 300 328 v2.2.2` |
| **EU — Environmental (RoHS / WEEE / Battery Reg)** | **RoHS 3 (`2015/863/EU`)** + **WEEE (`2012/19/EU`)** + **REACH** mandatory. EU Battery Reg not triggered if shipped without a cell | **RoHS 3** + **WEEE** + **REACH** + **EU Battery Regulation `(EU) 2023/1542`** (Art. 11 user-replaceability mandatory from **18 Feb 2027**) | `EN IEC 63000:2018`; `EN 50419`; Reg. `(EU) 2023/1542` |
| **Electrical & Battery Safety (NRTL / UN)** | Specify **UL 94 V-0** PCB laminate; all rails are **ES1 / PS1** (`IEC 62368-1`). No cell shipped = no `UN 38.3` hazmat transport | **`IEC/UL 62368-1` Ed. 3/4** report + pre-certified cell (`IEC 62133-2`, `UL 1642`/`2054`, and `UN 38.3` Test Summary under **IATA PI 967 Sec II**) | `IEC 62368-1:2020/2023`; `IEC 62133-2:2017+A1:2021`; `UL 1642`; `UN 38.3` |

---

## 2. United States (FCC) & Canada (ISED) Requirements

### 2.1 Leveraging the `ESP32-S3-WROOM-1` Modular Grant (`2AC7Z-ESPS3WROOM1`)
* Under **47 CFR § 15.212** and **KDB 996369 D04**, integrating the pre-certified `ESP32-S3-WROOM-1` (`U4`, `FCC ID: 2AC7Z-ESPS3WROOM1`, `IC: 21098-ESPS3WROOM1`) avoids all conducted antenna-port measurements (6 dB bandwidth, peak/avg conducted output power, PSD, conducted band-edge).
* **Host Radiated Spurious Spot-Check:** An accredited lab performs a radiated spurious emissions spot-check (`ANSI C63.10-2020`) on the host board with `U4` transmitting on worst-case channels (`2412, 2437, 2462 MHz` Wi-Fi and `2402, 2480 MHz` BLE), verifying restricted-band band-edges ($2310\text{–}2390\,\text{MHz}$ and $2483.5\text{–}2500\,\text{MHz} \le 54\,\text{dB}\mu\text{V/m}$ Avg / $74\,\text{dB}\mu\text{V/m}$ Peak at 3 m) and harmonics up to $25\,\text{GHz}$.

### 2.2 Part 15 Subpart B (Unintentional Radiator, Class B)
* **Radiated Emissions (47 CFR § 15.109(a), 30 MHz – 12.5 GHz at 3 m):**
  * $30\text{–}88\,\text{MHz}$: $40.0\,\text{dB}\mu\text{V/m}$ QP
  * $88\text{–}216\,\text{MHz}$: $43.5\,\text{dB}\mu\text{V/m}$ QP
  * $216\text{–}960\,\text{MHz}$: $46.0\,\text{dB}\mu\text{V/m}$ QP
  * $> 960\,\text{MHz}$: $54.0\,\text{dB}\mu\text{V/m}$ Avg / $74.0\,\text{dB}\mu\text{V/m}$ Peak
* **AC Mains / USB Conducted Emissions (47 CFR § 15.107(a), 150 kHz – 30 MHz):**
  * Tested via a representative USB wall adapter plugged into a $50\,\Omega / 50\,\mu\text{H}$ LISN ($0.15\text{–}0.5\,\text{MHz}$: $66\rightarrow 56\,\text{dB}\mu\text{V}$ QP / $56\rightarrow 46\,\text{dB}\mu\text{V}$ Avg; $0.5\text{–}5\,\text{MHz}$: $56$ QP / $46$ Avg; $5\text{–}30\,\text{MHz}$: $60$ QP / $50$ Avg).

### 2.3 Portable RF Exposure / SAR Exemption Math (47 CFR § 1.1307(b)(3)(i)(B) & KDB 447498 D04)
Because Espressif's modular grant was evaluated for **Mobile** separation ($d \ge 20\,\text{cm}$) whereas a handheld e-reader is **Portable** ($d \approx 5\text{–}10\,\text{mm}$), the SAR-based exemption threshold $P_{\text{th}}$ at $2.48\,\text{GHz}$ is:

| Separation Distance $d$ (Antenna to Outer Case) | US FCC **47 CFR § 1.1307(b)(3)(i)(B)** Max Time-Averaged Power $P_{\text{th}}$ | Canada ISED **RSS-102 Issue 6** Exemption | EU **`EN 50663:2017` / `EN 62479`** Low-Power Exclusion |
|---|---|---|---|
| **$d = 5\,\text{mm}$** | **$2.72\,\text{mW}$ (`+4.35 dBm`)** | **$4.0\,\text{mW}$ (`+6.0 dBm`)** | **$20.0\,\text{mW}$ (`+13.0 dBm`)** |
| **$d = 10\,\text{mm}$** | **$10.19\,\text{mW}$ (`+10.08 dBm`)** | **$7.0\,\text{mW}$ (`+8.45 dBm`)** | **$20.0\,\text{mW}$ (`+13.0 dBm`)** |
| **$d = 15\,\text{mm}$** | **$22.07\,\text{mW}$ (`+13.44 dBm`)** | **$15.0\,\text{mW}$ (`+11.76 dBm`)** | **$20.0\,\text{mW}$ (`+13.0 dBm`)** |

* **Zero-Lab-Cost Firmware Path:** Capping `ESP32-S3` TX power (`esp_wifi_set_max_tx_power()`) and/or time-averaged TX duty cycle in firmware so time-averaged output power stays $\le 2.7\,\text{mW}$ (US/Canada) and $\le 20\,\text{mW}$ (EU) qualifies for **100% SAR test exclusion** across all three jurisdictions.
* **Full-Power Path:** A single-band 2.4 GHz flat-phantom Body/Limb SAR measurement (`~$1,200–$2,000` at an Asian lab) allows unrestricted $+20\,\text{dBm}$ continuous TX.

### 2.4 Required Labeling String (PCB Silkscreen / Enclosure / E-Label per 47 CFR § 2.935)
```text
Silkscreen E-Reader Mainboard (Model: SS-REV1.01)
Contains FCC ID: 2AC7Z-ESPS3WROOM1
Contains IC: 21098-ESPS3WROOM1
CAN ICES-003(B) / NMB-003(B)
```

---

## 3. European Union & UK — CE Marking (RED 2014/53/EU, RoHS, Battery Reg)

1. **Delta Testing Approach (`ETSI EG 203 367`):** Reuse Espressif's `ETSI EN 300 328 v2.2.2` conducted report in the Technical Documentation file to cover antenna-port parameters (output power, PSD, adaptivity/LBT, occupied bandwidth) and run only **Radiated Spurious Emissions ($30\,\text{MHz}\text{–}12.75\,\text{GHz}$) + Receiver Blocking** on the Silkscreen host.
2. **RED Art. 3.1(b) EMC (`EN 301 489-1 v2.2.3` + `EN 301 489-17 v3.2.4`):**
   * **Emissions (`EN 55032` Class B):** $40\,\text{dB}\mu\text{V/m}$ ($30\text{–}230\,\text{MHz}$, 3.5–6 dB stricter than FCC Part 15B above 88 MHz!) and $47\,\text{dB}\mu\text{V/m}$ ($230\text{–}1000\,\text{MHz}$) at 3 m; AC/USB conducted emissions ($150\,\text{kHz}\text{–}30\,\text{MHz}$).
   * **Immunity (`EN 55035` / `EN 61000-4-x`):**
     * **ESD (`EN 61000-4-2`):** $\pm 4\,\text{kV}$ contact / $\pm 8\,\text{kV}$ air (Criterion B).
     * **Radiated RF Immunity (`EN 61000-4-3`):** $80\,\text{MHz}\text{–}6\,\text{GHz}$ at $3\,\text{V/m}$, 80% AM 1 kHz (Criterion A).
     * **EFT (`EN 61000-4-4`):** $\pm 1\,\text{kV}$ on AC mains adapter; **Surge (`EN 61000-4-5`):** $\pm 1\,\text{kV}$ L-L / $\pm 2\,\text{kV}$ L-E; **Conducted RF (`EN 61000-4-6`):** $0.15\text{–}80\,\text{MHz}$ at $3\,\text{V}_{\text{rms}}$; **Voltage Dips (`EN 61000-4-11`):** automatic pass via `U2` (`TPS2116`) $8\,\mu\text{s}$ battery handover.
3. **RED Art. 3.3(d/e/f) Cybersecurity (`EN 18031-1/-2:2024`):** Avoid default universal passwords, store Wi-Fi credentials in encrypted NVS, and verify signatures on OTA updates.
4. **EU Battery Regulation `(EU) 2023/1542` (Article 11 — Mandatory Feb 18, 2027):** Requires portable batteries to be user-removable and replaceable with standard tools and without software pairing locks. Silkscreen's open battery bay, standard M2 screws, 2-pin `JST-PH` (`J5`), and pure analog `BAT_MONIT` (`IO8`) natively satisfy Article 11.

---

## 4. Electrical & Battery Safety (`UL / IEC 62368-1`, `IEC 62133-2`, `UN 38.3`)

* **Hazard Classification (`IEC 62368-1:2020/2023`):**
  * **USB Input (`USB_VBUS`):** $5\,\text{VDC}$, limited by `F1` (`0805L100WR` 1.0 A hold / 1.95 A trip) → **ES1 / PS1** ($<60\,\text{VDC}, <15\,\text{W}$).
  * **Battery Rail (`B+`/`B-` & `P+`):** $3.0\text{–}4.2\,\text{VDC}$, protected by `U5` (`DW01A`) + `Q1` (`FS8205A`, $\sim 2.7\,\text{A}$ overcurrent trip) + `Q3`/`Q8` (`AO3401A` reverse-polarity) + `F2` (`0805L075WR` on `J6.12`) → **ES1 / PS1**.
  * **Frontlight Boost (`LED_SW`):** $15\,\text{VDC}$ normal ($13.3\,\text{mA}$), $24.25\text{–}25.5\,\text{VDC}$ OVP clamped by `D3` (`SMAJ26A`) → **ES1 / PS1** ($<60\,\text{VDC}$).
  * **E-Paper Charge Pump (`VGH`/`VGL`):** $\pm 22\,\text{VDC}$ ($44\,\text{VDC}$ rail-to-rail) at $<2\,\text{mA}$ DC touch current → **ES1 / PS1**.
* **PCB Laminate:** Specify **`UL 94 V-0`** flammability rating on fabrication orders.
* **Battery Pack Certifications (When Shipping With a Cell):** Require a cell/pack carrying **`IEC 62133-2:2017+A1:2021`** (CB Certificate + Report), **`UL 1642` / `UL 2054`**, and a **`UN 38.3` Test Summary** (shipped installed inside the device under **IATA PI 967 Section II**).

---

## 5. Pre-Compliance Bench Setup, Test Firmware & Lab Cost Summary

### 5.1 Dedicated Test Firmware Images
1. **`silkscreen_emc_stress.bin` (Unintentional / Charging / Immunity Mode):**
   * Alternates full/partial e-paper checkerboard refreshes every 3–5 s (keeps `Q4`/`L1` charge pump active).
   * Writes/reads/CRC32-verifies a 64 KB buffer on microSD `J7` and prints live pass/error counters (`SD CRC OK | I2C RTC OK | ADC OK`) on the e-paper screen for camera-monitored immunity verification.
   * Drives `PWM_LED` (`IO42`) at `20 kHz` (button-toggleable between 100% duty and 50% + `COLOR_SEL` blend) while charging a $\sim 3.5\,\text{V}$ Li-Po over USB-C.
2. **`esp_phy_cert_test.bin` (RF Intentional Mode):**
   * Button-stepped wrapper around Espressif's `esp_phy_cert_test` API cycling through **802.11b `1 Mbps`, 802.11g `6 Mbps`, 802.11n `MCS0` on Ch 1 (`2412`), Ch 6 (`2437`), Ch 11 (`2462 MHz`)**, **BLE `1M/2M` on `2402 / 2440 / 2480 MHz`**, and **Continuous RX**, displaying the active test mode on the e-paper screen so no UART wires are needed on the chamber turntable.

### 5.2 Ballpark Cost & Turnaround Table

| Scope | DIY Pre-Compliance Bench (`tinySA ULTRA` + H-Probes + $5\,\mu\text{H}$ LISN) | US / EU Accredited Lab | Tier-1 Asian Accredited Lab (BACL, SGS, TÜV CN, Sporton) | Time & Samples |
|---|---:|---:|---:|---|
| **In-House Pre-Compliance Kit** | `$450 – $1,200` | — | — | 2 days |
| **US + Canada (FCC 15B SDoC + ICES-003 + KDB 996369 Host Spot-Check + SAR Exclusion)** | — | `$4,000 – $7,000` | `$1,200 – $2,500` | 1.5–2 wks, 2 units |
| **EU + UK CE RED (`EN 301 489-1/-17`, `EN 55032`/`55035`, `EN 300 328` Delta, `EN IEC 62368-1`, `EN 50663`)** | — | `$8,500 – $15,000` | `$3,000 – $5,200` | 2–3 wks, 2 units + 2 bare PCBs |
| **Optional 1-Band 2.4 GHz Lab SAR + FCC C2PC** *(if full $+20\,\text{dBm}$ continuous TX desired)* | — | `+$4,500 – $7,500` | `+$1,200 – $2,000` | +1 wk, 1 unit |
| **Combined US + Canada + EU/UK Package** | **`~$450 – $1,200`** | **`~$12,500 – $22,000`** | **`~$4,200 – $7,700`** | **3–4 weeks, 4 total units** |

---

## 6. Crowd Supply Commercial Readiness Summary (Rev 1.01 As-Is: **8.5 / 10**)

* **Dropping the "sawed-off board" marketing and leaving `J6` unpopulated** immediately removes all cut-edge burr hazards, floating cut-edge copper islands, and external header hot-plug/short risks at zero hardware cost.
* **Electrical & Field Reliability (`9.0 / 10`), JLCPCB Turnkey Manufacturability (`8.5 / 10`), and Open-Source Documentation (`9.5 / 10`)** are ready for a Crowd Supply campaign today without another board spin.
* **Zero-Respin EMC Levers (If Needed During Pre-Compliance):** Run SDMMC at `20 MHz` (`SDMMC_FREQ_DEFAULT`), bump `R24` (`SD_CLK`) and `R30` (`SPI_SCK`) from `33 Ω` to `68 Ω` in the BOM, and replace `C1` (`J1` shield) with a high-voltage 0603 cap (`250–630 V`) or `0 Ω` resistor.
