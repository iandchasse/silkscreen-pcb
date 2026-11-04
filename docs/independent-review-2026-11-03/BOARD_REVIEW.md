# Independent engineering review: Silkscreen e-reader mainboard

| | |
|---|---|
| Design | Silkscreen Reader PCB, Rev 1.03 (title block 2026-11-03), branch `1.03`, commit `95a6d8d` |
| Files reviewed | `silkscreen_pcb.kicad_sch` (single A2 sheet), `silkscreen_pcb.kicad_pcb`, `.kicad_pro`, `.kicad_dru`, `fabrication/part_fields.csv`, project libraries under `KiCad/`, README.md for product context only |
| Reviewer stance | First look at the board. No prior audits or design notes outside the schematic and silkscreen were read. |
| Emphasis | Safety first, then function, then EMI/EMC |
| Date | 2026-11-03 |

**Conventions.** Schematic locations are given as sheet zone (letter row A–H, column 1–12 of the A2 frame) plus the symbol anchor in mm, for example `B3 (129.5, 102.9)`. Board coordinates are KiCad board mm (x right, y down, viewed from the front through the board). Every part is on B.Cu. Track resistances assume **1 oz (35 µm) copper**, because the board file has no stack-up. Where JLC fits an LCSC substitute (`part_fields.csv`, column "LCSC part"), that substitute's datasheet was used, for example the Brightking PTC for F1, the TECH PUBLIC FS8205A, the PUOLOP DW01A, the Sunltech L1 and the DOWO SD05C for CR2/CR3. **Verified** means the issue follows directly from the design files and datasheet values. **Suspected** means it needs a bench check (section 7).

---

## 1. Executive summary

The board is carefully designed. Every pin mapping I checked against its datasheet is correct, the default configuration has no wiring error, and DRC shows 0 errors, 0 unconnected items and 0 schematic-parity issues. The zone fills are current. The cell-protection chain (DW01A + FS8205A, with a 50 mΩ added sense resistance) and the reverse-polarity scheme work as drawn. The e-paper booster follows Good Display's reference circuit.

The two most important problems are both Li-ion safety issues outside the default electrical path:

1. **The charger has no temperature qualification and no safety timer** (H-1).
2. **The documented "snip the header arm" modification leaves unfused battery copper exposed 0.2 mm from GND at a rough edge, about 3 mm from the cell** (H-2).

The Medium items are functional and robustness margins:

- The frontlight PTC is undersized (M-1).
- The 3V3 power budget and dropout margin are thin (M-2).
- The ESP32 antenna keep-out does not follow Espressif's placement guidance (M-3).
- There is no input over-voltage protection (M-4).
- The charger cannot wake a pack whose own protection has latched (M-5).
- An on-board silkscreen instruction would damage the touch panel if followed (M-6).

### Findings (sorted by severity)

| ID | Severity | Block | Finding | Confidence | Status |
|---|---|---|---|---|---|
| H-1 | **High** | Charger / Li-ion | TP4056 TEMP pin is grounded, the 2-wire pack has no NTC, and the TP4056 has no safety timer. The cell will be charged at any temperature, including below 0 °C and above 45 °C, and indefinitely if it never reaches termination. | High | Verified |
| H-2 | **High** | Expansion arm / battery | The silkscreen marks a snap line for cutting off the J6 arm. After the cut, P+ (battery, with F2 left on the removed arm) and 3V3 copper sit 0.20 mm from GND pour at the rough edge, about 3 mm from the battery bay. A 4–15 Ω burr or contamination short dissipates 1–4 W without tripping the DW01A (0.77–1.8 A). | Med | Geometry verified, consequence suspected |
| M-1 | Medium | Frontlight | F3 (MF-FSMF010X, 0.10 A hold, 0.08 A at 40 °C, up to 6 Ω) feeds a boost that draws about 55–95 mA at full brightness. The thermal keep-out around F3 makes it run hotter. Expect nuisance trips and flicker when warm or at low battery. | Med | Numbers verified, behaviour suspected |
| M-2 | Medium | Power tree | 3V3 budget: Wi-Fi TX (355 mA) + SD write + EPD refresh comes to about 515–615 mA against the TLV755's 500 mA rating (560 mA minimum limit). The board battery path is 0.34–0.48 Ω, so 3V3 leaves regulation below about 3.8–4.0 V cell OCV at 0.5–0.65 A. Expect brown-outs during Wi-Fi at mid/low charge. | Med | Suspected |
| M-3 | Medium | ESP32 RF | The antenna sits in an 18.7 × 6.3 mm edge notch with board and GND pour about 0.7–1.0 mm away on both sides, and the display panel covers it. Espressif requires ≥15 mm clearance on one side and no "hollowed-out" placement. Expect reduced range. | High (deviation) / Low (impact) | Suspected |
| M-4 | Medium | USB input | No input OVP. CR1 (SMF6.5CA, Vbr 7.2–8.0 V, 0.4 W) sits upstream of F1, so a sustained >7 V source burns CR1 instead of tripping F1. The TPS2116, TLV755, TPS923610 and F1 are all 6 V parts. | High | Verified |
| M-5 | Medium | Charger enable | CE is gated by the Q9 cell-voltage detector (needs about 0.9–1.8 V at J5). A protected pack whose own PCM has latched after over-discharge shows about 0 V, so the charger never applies voltage to wake it. The device then looks dead. | Med | Suspected (pack dependent) |
| M-6 | Medium | Touch options | The back-silk instruction "unpopulate R42,44,46,52 / populate R43,45,58,66" names R42, which does not exist. Touch VDD comes from F4, which stays fitted, so the alternate panel's INT output ends up tied to 3V3 through 0.9–6 Ω. | High | Verified |
| L-1 | Low | Charger | R6 = 10 kΩ gives 99–121 mA (TP4056 REV2.4: 1100·VPROG/R). The schematic note says "R6 4.7kohm -> ~234mA" and README says about 0.25 A. Charging takes about 5 h, not 2–2.5 h. | High | Verified |
| L-2 | Low | Cell protection | DW01A over-current trip is 0.77–1.80 A (typ 1.44 A) against a ~0.65 A coincident peak load. Margin is thin at the hot / low-cell corner. | Med | Suspected |
| L-3 | Low | Power mux | TPS2116 priority switchover is at VBUS = 3.68–4.32 V with no added hysteresis. A weak USB source or cable carrying 0.7 A can chatter between USB and battery. | Med | Suspected |
| L-4 | Low | Status ADC | The USB_STAT battery-only level (2.2 V) assumes TP4056 CHRG/STDBY are high-Z with VCC = 0. Any clamp to VCC pulls it to about 0.8 V, which would misread as charging or done. | Low | Suspected |
| L-5 | Low | Buttons | BUTTON_ADC_2 "UP(2)" sits at 2.877 V, at the ESP32-S3 ATTEN3 calibrated limit (0–2.9 V, ±50 mV). | High | Verified |
| L-6 | Low | MCU | BOOT button SW6 is DNP and IO0 has no pad. Recovering from firmware that disables USB-Serial-JTAG needs soldering. | High | Verified |
| L-7 | Low | Expansion header | J6 exposes the strapping pins GPIO45 (VDD_SPI select) and GPIO46, plus P+ and the 25 V LED rail. P+ (pin 12) is next to C− (pin 11): a bridge drains about 80 mA and heats Q6 (~0.24 W). | Med | Verified |
| L-8 | Low | Reverse polarity | Q3's body diode conducts in the reverse-fault direction. Q8 alone blocks reverse current, so Q3 adds 50–70 mΩ and no redundancy. | Med | Verified by analysis |
| L-9 | Low | Charger | The cell-presence detector is fooled by charger back-feed through Q8/Q3. With the cell pulled, the charger keeps running and J5 is live at 3.6–4.2 V. | High | Verified by analysis |
| L-10 | Low | Frontlight | L2 Isat is 1.0 A (spec) but the TPS923610 switch limit is 1.6–2.1 A, so L2 saturates under overload or short. F3 is then the only protection. | High | Verified |
| L-11 | Low | microSD | Q7 switches SD_VDD hard (1 kΩ gate drive), charge-sharing 1.1 µF plus the card's capacitance off 3V3. Expect a 0.1–0.4 V dip. | Low | Suspected |
| L-12 | Low | Charge vs protection | TP4056 VFLOAT max is 4.242 V and DW01A VOC min is 4.25 V: an 8 mV gap. The older TP4056 sheet (4.263 V max) overlaps. Possible nuisance over-charge trips. | Med | Verified |
| L-13 | Low | Mechanical | M2 mounting-hole pads are Ø2.6 mm. P+_FUSE copper is 0.91 mm (H1) and B+ 1.22 mm (H5) from the pad edge, so washers or standoffs larger than about Ø4.4 mm rest on mask-only copper. | High | Verified |
| L-14 | Low | E-paper / GND | J2 decoupling caps sit 6–18 mm from the FPC pins (VSH2 18.6 mm, VCI 13.2 mm, VDD 11 mm). Panel VSS (J2.17) reaches GND through one 0.2 mm trace and a 2.8 mm² island. The TPS923610 GND has a single via. | High | Verified |
| L-15 | Low | EMI | EPD boost hot loop is about 39 mm². GDR and RESE are 36 mm long each (28 mm on F.Cu). SD_CLK changes layer twice. USB D± cross about 11 F.Cu plane slots. | Med | Verified geometry |
| L-16 | Low | ESD | U6 (USB ESD) sits on 5–7 mm stubs. Tact-switch metal frames (pads 3/4) are floating. The button lines have no TVS. | Med | Verified |
| L-17 | Low | DNP options | Several DNP options short rails if fitted without removing their counterpart: R74 + R73 shorts 3V3 to GND; R66 + R44 ties TP_INT to 3V3; R45 + R46 and R52 + R58 short SDA to SCL. | High | Verified |
| L-18 | Low | Touch / sleep | The touch controller (FT6336U) is always powered through F4: +55 µA in hibernate, +220 µA in monitor mode (its power-on default), against a 50 µA board budget. There is no gate. | High | Verified |
| I-1 | Info | Power | The LDO is always on and there is no ship mode. Deep sleep is about 50 µA typ / 80 µA max (LDO 25 µA), giving about 260–420 days on 500 mAh. About 5 µA residual drain remains after the DW01A trips. | Med | Verified (budget) |
| I-2 | Info | USB | CC advertisement is not sensed. Peaks of about 0.7 A exceed the 500 mA USB 2.0 default power. | Med | Verified |
| I-3 | Info | Environment | ESP32-S3-WROOM-1-**N16R8** is rated −40…65 °C ambient. The panel is rated 0…50 °C. | High | Verified |
| I-4 | Info | Connectors | FH34SRJ is top-and-bottom contact, so a flipped FPC still mates with reversed pin order. The silkscreen warns about this. | High | Verified |
| I-5 | Info | RTC | DS3231M INT/SQW is not connected, so an RTC alarm cannot wake the MCU. The VBAT-only supply configuration is valid. | High | Verified |
| I-6 | Info | Cell | A representative 503035 cell is rated 1 C (500 mA) continuous with a 3.0 V cut-off. DW01A VOD is 2.4–2.6 V, so firmware must enforce the cut-off. | High | Verified |
| I-7 | Info | Labelling | The front-silk J6 pin legend lists the pins-1–6 row above the pins-7–12 row, which is the reverse of the physical order in the same view. Confirm the intent. | Med | Verified |

**Count per severity:** Critical 0 · High 2 · Medium 6 · Low 18 · Info 7 (33 findings).

---

## 2. Board overview

### 2.1 Blocks (all 188 schematic symbols mapped; `scripts/block_map.py`)

| Block | Parts | Schematic zone | Board area (mm) |
|---|---|---|---|
| USB-C input & protection | J1 F1 CR1 U6 R2 R3 C2 R84 C25 D2 R59 | A1–C1, B3 | x 92–104, y 92–112 |
| Charger & enable logic | U11 R6 C3 Q2 R81 R82 Q9 R79 R80 | B3, D2 | x 84–95, y 84–98 |
| Cell connector, reverse polarity, protection | J5 Q3 R56 R57 R27 Q8 U5 R83 C7 R16 C34 Q1 R85 R86 | C1–E2, D3 | x 74–102, y 64–82 |
| Power mux | U2 C26 C4 R38 R51 | A3 | (85, 86) |
| 3V3 LDO | U3 C6 C21 | A4 | (78.7, 84.2) |
| Battery monitor / status divider | R12 R10 C8 / R70 R17 R67 R71 C23 | B4 / B11 | x 68–80, y 86–91 |
| MCU | U4 R7 C5 R13 SW11 R63 SW6(DNP) R64 C32 C33 TP1 TP2 R65 R68 R69 | D10 | U4 at (57.5, 102.5), antenna toward x = 44.75 |
| microSD | J7 Q7 R40 R78 R77 R8 R9 R53–R55 R21–R26 C36 C37 U1 U9 | B5–C8 | (63, 84.6) |
| E-paper connector & booster | J2 Q4 L1 D4 D5 D6 C10 C11 R14 R15 F6 C13–C20 C22 R5 R29–R34 | F2–F4 | x 66–93, y 108–136 |
| Frontlight driver | U10 L2 C12 C9 F3 R37 Q5 Q6 U12 R75 C24 R49 R50 R39 R41 C31 J3 TP3–5(DNP) | E5–F7 | x 45–57, y 114–137 |
| Touch connector & option links | J4 F4 U7 R43(DNP) R44 R45(DNP) R46 R52 R58(DNP) R66(DNP) | H5–H7 | (92.5, 126) |
| RTC | U13, U14(DNP), C30 | D7 | (61.9, 125) |
| Buttons / ladders / power button | SW1–SW5 SW7–SW10 R4 R28 R11 R18–R20 R35 R36 R60–R62 R72(DNP) R73 R74(DNP) R76 C27–C29 | C6–D6, G1 | board perimeter |
| I2C pull-ups | R47 R48 | E10 | (63–67, 114.5) |
| Expansion header | J6 F2 F5 CR2 CR3 U8 D3 D8 | A8–C9 | arm x 86–104, y 37–62 |
| Mechanical | H1–H6 (plated, GND) | G1 | |

Parts with no identifiable function: **Q3** (L-8) and U9 channel 4 (pin 4 not connected). The DNP parts are SW6, R43, R45, R58, R66, R72, R74, TP3–TP5 and U14. Every other part has a purpose that matches the schematic.

### 2.2 Power tree

```
USB-C J1 (A4/A9/B4/B9) ─ VBUS_PRE_FUSE ─┬─ CR1 SMF6.5CA → GND            (upstream of the fuse)
                                        └─ F1 SMD0805B100 PTC 1.0 A hold / 1.95 A trip, Vmax 6 V
USB_VBUS ─┬─ C25 1 µF ; C2 10 µF + R84 1 Ω (damped bulk)
          ├─ U11 TP4056 VCC ── BAT ──────────────────────────────┐  (CE = Q2 drain; Q2 on only if Q9 sees cell volts)
          ├─ U2 TPS2116 VIN1 + MODE ; PR1 = VBUS·100k/400k       │
          ├─ D2 + R59 (USB LED)  ;  R38/R51, R81/Q2              │
Cell J5: 2 = B+ ─ Q3 (P-FET, S=B+) ─ R27 0 Ω ─ Q8 (P-FET, G=GND) ─ P+ ─┼─ C3 10 µF, C26 1 µF
         1 = B- ─ Q1 FS8205A [FET1 G=OD | FET2 G=OC] ─ /B-_SENSE ─ R85‖R86 (50 mΩ) ─ GND (= pack P-)
                       DW01A U5: VCC = P+ via R83 100 Ω, GND = B-, VM = GND via R16 1 kΩ (C34 0.1 µF to B-)
P+ ─┬─ U2 VIN2 ;  R12/R10 → BAT_MONIT ;  R83 → U5
    └─ F2 0805L075 PTC 0.75 A ─ /P+_FUSE ─ J6.12 (CR3 SD05C)           (F2 is on the snap-off arm)
U2 VOUT = LDO_IN (C4 22 µF) ─┬─ U3 TLV75533 (EN = IN, always on) → 3V3 (C6 22 µF, C21 1 µF)
                              └─ F3 MF-FSMF010X 0.10 A → /LED_VIN (C12) → U10 TPS923610 boost → LED_SW (C9, D3)
                                     → J3 C+/W+ and J6.5 → strings → C-/W- → Q6/Q5 → FB (R37 15 Ω)
3V3 ─┬─ U4 ESP32-S3 (C32 22 µF, C33 0.1 µF)        ├─ F6 → EINK_3V3 → J2 VCI/VDDIO + Q4/L1 boost → PREVGH ≈ +22 V,
     ├─ Q7 (SD_ACTIVATE) → SD_VDD → J7               │      C11/D4/D6 charge pump → PREVGL ≈ −22 V
     ├─ F4 → J4.2 (touch VDD)    ├─ F5 → J6_3V3 → J6.7 (CR2)
     └─ U13 DS3231M VBAT pin (VCC grounded), U12, pull-ups, ADC ladders, USB_STAT divider
```

### 2.3 Operating modes (by analysis)

| Mode | Path | Notes |
|---|---|---|
| USB only | VBUS → F1 → U2 VIN1 → LDO_IN = 5 V → U3 | Charger disabled by Q9, unless the cell was pulled while charging (L-9). The LDO dissipates (5 − 3.3)·I. |
| Battery only | P+ → U2 VIN2 (MODE low, PR1 low → highest input) | About 50 µA deep sleep (I-1). |
| Both | U2 selects VIN1 once VBUS > 3.68–4.32 V; the TP4056 charges P+ with no system load | Good: termination sees only the cell. |
| Neither | Off | |
| USB plug-in | MODE high at ~1 V; VIN2 is held until PR1 > 1 V, then break-before-make (t_SW about 8 µs, C4 holds LDO_IN) | Switching to VIN1 has no soft start (VOUT > 1 V); the step is about 1.3 V into C4. |
| USB unplug | PR1 < VREF or RCB → VIN2. C4 bridges the gap. | OK |
| Deep sleep | 3V3, panel and touch rails stay on; only SD_VDD is gated | Firmware obligations in §4.8. |

---

## 3. Per-block review

### 3.1 USB-C input and protection (J1, F1, CR1, U6, R2/R3, C2/R84, C25, D2/R59)

**Function.**

- CC1/CC2 each have Rd = 5.1 kΩ to GND (R3, R2; A1 (33.0, 45.7)), so the board is a correct default sink.
- D+ (A6/B6) and D− (A7/B7) are tied together and routed to U4 pins 14 and 13 (IO20/IO19).
- The shield (S1) goes straight to GND.
- D2 + R59 give a 1.5 mA "USB present" LED.
- C2 (10 µF/25 V) with R84 (1 Ω) is a damped bulk capacitor. Its characteristic impedance roughly matches about 1 µH of cable against C25 (1 µF), which keeps hot-plug ringing low.
- Nominal VBUS capacitance is 11 µF, about 8 µF effective at 5 V. That is at the 10 µF USB 2.0 limit, but the 1 Ω series resistor limits the inrush.

**Safety.**

- F1 (fitted part: Brightking SMD0805B100TFT): Ihold 1.00 A, Itrip 1.95 A, **Vmax 6 V**, Rmin 0.04 Ω, R1max 0.23 Ω (Brightking SMD0805 datasheet p.2; Littelfuse 0805L derating: 0.82 A at 40 °C, 0.74 A at 50 °C).
- Normal USB load is ≤0.13 A charge plus about 0.6 A system peak, so F1 is fine.

**Finding M-4 (no input OVP; TVS upstream of the PTC).**

- The VBUS track from J1 passes over CR1 pad 1 at (94.35, 100.2) and only then reaches F1 at (94.41, 94.27). CR1 is therefore in front of the fuse.
- CR1 (SMF6.5CA, fitted Hongjiacheng part): Vrwm 6.5 V, Vbr 7.22–7.98 V, Vc 11.2 V at 17.9 A, PM(AV) **0.4 W** (datasheet p.1–2).
- Every downstream part is a 6 V part:
  - TPS2116 VIN/VOUT abs max 6 V (SLVSFG1A §6.1).
  - TLV755P 6 V (SBVS320D §5.1).
  - TPS923610 VIN 6 V (SNVSCN8B §6.1), fed from LDO_IN, which equals VBUS when USB is present.
  - TP4056 VCC 8 V.
  - F1 Vmax 6 V.
- A source that sits above 6 V (a faulty adapter, a bench supply, or a fixed 9/12 V "USB-C" supply) damages U2, U3 and U10.
- If it sits above about 7.5 V, CR1 conducts several amps with no fuse in its path. It will overheat and fail, normally short.
- If U2 fails short, VBUS reaches P+, and the DW01A over-charge cut-off (4.25–4.35 V) plus the pack PCM become the only cell protection.
- Fix (smallest change): place a TVS after F1 (keep CR1 for ESD) so a sustained over-voltage trips the PTC. Better: add a 5 V OVP switch or eFuse with ≥20 V tolerance and a 5.8–6 V threshold ahead of U2/U11. The probability is low, but the consequence is board loss and a hot component near the connector.

**Layout.**

- J1 → F1 is 15.6 mΩ and F1 → U2 VIN1 is 20.9 mΩ (`net_resistance.py`); tracks are 0.40/0.25 mm. Fine.
- U6 sits on stubs about 7 mm from J1 (L-16). This works, but in-line placement is better for ESD.

### 3.2 Charger (U11 TP4056, R6, C3, CE logic Q2/Q9/R79–R82)

**Function.**

- PROG: TP4056 REV 2.4 (LCSC) gives I_BAT = 1100·V_PROG/R_PROG with V_PROG 0.9–1.1 V (p.5, p.9). With R6 = 10 kΩ that is **99/110/121 mA**. The older NanJing sheet (1200/R, table value 130 mA at 10 k) gives about 120–130 mA.
- Termination is at C/10, about 11 mA. Trickle is below 2.9 V. VFLOAT is 4.158–4.242 V (REV 2.4) or 4.137–4.263 V (older sheet).
- **L-1:** the schematic text at B3 says "R6 4.7kohm -> ~234mA charge rate" and README says about 0.25 A. The fitted value gives half that. This is safe, but charge time is about 5 h for 500 mAh and the documentation disagrees with the BOM.
- CE logic:
  - Q9 (BSS138; VGS(th) 0.8/1.2/1.6 V, Hongjiacheng datasheet p.2) is gated by R79/R80 across J5, so Vgs = 0.909·V(J5).
  - With a cell present, Q9 pulls DET_NODE to B-, Q2 (AO3401A) turns on, and CE = VBUS.
  - With no cell, R81 holds Q2 off and R82 pulls CE low.
  - A reversed cell gives negative Vgs on Q9, so CE stays low. Good.
  - A shorted cell (0 V) also keeps CE low. Good.
- **L-9:** if the cell is removed during charging, the TP4056 output back-feeds B+ through Q8 (on, because its Vgs = −P+) and Q3 (body diode, then channel). Q9 stays on and CE stays high, so the charger keeps cycling with no cell, which the schematic note at B11 acknowledges. J5 is then live at about 3.6–4.2 V.
- **M-5:** Q9 needs about 0.9–1.8 V at J5. A protected pack in PCM over-discharge lockout has its discharge FET off, and that FET's body diode blocks current from the board's 10–11 MΩ dividers. P- therefore floats up to P+, J5 reads about 0 V, CE stays low and the pack is never woken. Fix: let firmware override the detector, for example an ESP32 GPIO driving an N-FET in parallel with Q9 to pull DET_NODE low for a few seconds. The TP4056 trickle current (C/10) then provides a safe wake current.

**Safety, finding H-1.**

- U11 pin 1 (TEMP) is tied to GND (netlist U11.1 = GND; symbol at B3 (129.5, 102.9)). TP4056 p.7 (REV 2.4) and p.2 (older sheet): "The temperature sense function can be disabled by grounding the TEMP pin."
- J5 is a 2-pin PH connector with no thermistor contact.
- The TP4056 has no charge timer. Its state diagram (REV 2.4 p.10) has no timeout, and "C/10 termination is disabled in trickle charging and thermal limiting modes" (p.9).
- Consequences:
  - The cell is charged at any cell temperature. A representative 500 mAh 503035 cell (PKCELL LP503035) specifies **charge 0–45 °C**. Charging below 0 °C plates lithium, which is a latent internal-short hazard. Charging above 45 °C accelerates swelling.
  - A cell with a soft internal short that never reaches C/10 is charged forever at up to 121 mA, about 0.5 W into the defective cell.
  - Nothing else on the board knows the cell temperature. The pack PCM does not either.
- This is the main compliance gap for a consumer Li-ion product (cell-maker charge window, IEC 62133-2 / IEC 62368-1 Annex M expectations).
- Fix (smallest): add an NTC thermally coupled to the cell in the bay, wired as a divider to TEMP. TEMP abs max is 10 V. The window is 45–80 % of VCC. Example: a 10 kΩ, B = 3950 NTC to GND with an 8.2 kΩ top resistor gives about a 0 °C cold cut-off and about a 34 °C hot cut-off; add a parallel resistor to tune the hot limit. Also add a firmware CE override (as for M-5) so firmware can impose a timer and use the DS3231M's on-chip temperature (±3 °C) as a sanity check. Better: use a 3-wire pack with an NTC, or a charger with JEITA support and a safety timer.

**Ratings.**

- VCC abs max 8 V against USB ≤5.5 V. OK.
- Worst-case dissipation: (5.25 − 3.0) V × 0.121 A = 0.27 W in an ESOP-8 whose exposed pad has a solid zone connection and 6 vias (0.2 mm). OK.
- The die thermal regulation at 145 °C is a backstop.
- C3 is 10 µF/10 V on P+ (≤4.2 V; 5 V under a single fault). OK.

**Layout.**

- C3 is 2.35 mm from BAT and C2 is 2.08 mm from VCC. OK.
- The exposed pad has a solid zone connection plus vias to F.Cu GND. OK.

### 3.3 Cell connector, reverse polarity and protection (J5, Q3, Q8, R27, U5, Q1, R85/R86, R16/C34, R83/C7)

**Topology.** The board GND is the pack P-. The cell's B- reaches GND through Q1, a common-drain pair whose FET1 is driven by OD and FET2 by OC. Its pin-out was checked against the TECH PUBLIC FS8205A datasheet p.1: 1 = S1, 2/5 = D, 3 = S2, 4 = G2, 6 = G1. The DW01A (PUOLOP datasheet p.2) is wired in the standard way: OD pin 1, VM pin 2, OC pin 3, VCC pin 5 through 100 Ω (R83) with 0.1 µF (C7), GND pin 6 = B-, and VM through 1 kΩ (R16). C34 (0.1 µF from VM to B-) is non-standard. It forms a 100 µs filter that stops hot-plug inrush (11 µF on P+ through about 0.3 Ω, peaks around 12 A for a few µs) from tripping short-circuit detection. That is a sensible choice.

**Thresholds** (DW01A datasheet p.4): VOC 4.25/4.30/4.35 V (delay 110 typ / 200 max ms), release 4.05–4.15 V; VOD 2.40/2.50/2.60 V, release 2.8–3.0 V; VEDI 130/150/170 mV (T_EDI 7 typ / 20 max ms); short circuit 0.82/1.36/1.75 V (T_short 400/600 µs); ICC 3/6 µA; IPD ≤4 µA.

- Sense resistance = 2 × FS8205A (19.5 mΩ typ at 4.5 V, 31.5 mΩ max at 2.5 V; datasheet p.2) + R85‖R86 (50 mΩ) + traces.
- Measured traces: /B-_SENSE from Q1.3 to R85 is 8.0 mΩ, to R86 is 23.8 mΩ.
- Result: 95–170 mΩ, so the trip current is **0.77–1.80 A, typ 1.44 A** (`calc_budget.py`).
- **L-2:** the board's coincident peak is about 0.65 A (§4.3). The hot, low-cell corner leaves little margin. A spurious trip latches the system off until the load is removed. Bench test 7.7.

**Reverse polarity (by analysis).**

- Q3 (S = B+, gate to B- through R56) and Q8 (S = P+, gate = GND) are back-to-back P-FETs with a common drain.
- With a reversed cell, the fault current would enter B+ from the board side. Q3's body diode (anode at drain/mid, cathode at B+) conducts in exactly that direction. Q8 is the only blocker: its gate sits at GND, which is above P+ in the fault.
- Result: no USB → only the 10–21 MΩ divider currents flow (<1 µA). USB present → P+ is not driven (CE low), so leakage only. The corner case "charger running with J5 open (L-9), then a reversed cell inserted" lets about 11–13 mA (TP4056 trickle) flow while Q8 acts as a source follower holding P+ near Vth. Not hazardous.
- **L-8:** Q3 therefore adds 50–70 mΩ (AO3401A RDS(on) < 60 mΩ at −4.5 V, < 85 mΩ at −2.5 V; AOS datasheet p.1) without adding protection or redundancy.
- Fix: either remove Q3 (0 Ω) to cut path resistance (helps M-2), or flip it (drain to B+, source to mid). Flipped, its body diode blocks the reverse-fault direction and it becomes a true second blocker.

**Ratings.**

- FS8205A: 20 V, ±10 V Vgs, 6 A, EAS 7.4 mJ.
- A hard short through about 0.4 Ω gives about 9 A, which gives VM ≈ 0.8–1.0 V. That may sit below the DW01A short threshold (0.82–1.75 V), in which case the over-current path trips after 7–20 ms. Energy in the FETs then: 3.6 W × 20 ms ≈ 73 mJ total, spread over Q1/Q3/Q8, which is a short pulse within the SOT-23 transient capability.
- R85/R86 (1206, 0.25 W): about 2 W each for 20 ms. Acceptable as a single pulse.
- At a sustained current just under the trip, the 0.25 mm Net-(Q3-D) and Net-(Q8-D) tracks rise about 50 °C (IPC-2221 external, 1 oz, 1.8 A). Widening them to ≥0.5 mm is cheap insurance.

**Layout.** J5 → Q3 is 18 mΩ, Q3 → R27 is 16.5 mΩ, R27 → Q8 is 4.4 mΩ, Q8 → U2 is 20 mΩ, J5 → Q1 (B-) is 16 mΩ. See figure `figures/fig3_battery_path.png`.

**Finding L-12.** TP4056 VFLOAT max (4.242 V) is only 8 mV below DW01A VOC min (4.25 V). The older TP4056 sheet's 4.263 V max overlaps it. The worst case is a nuisance over-charge latch, not a hazard.

### 3.4 Power mux (U2 TPS2116) and 3V3 LDO (U3 TLV75533)

**TPS2116.**

- Pins checked against SLVSFG1A Table 5-1: 1 GND, 2/7 VOUT, 3 VIN1, 4 PR1, 5 MODE, 6 VIN2, 8 ST.
- MODE tied to VIN1 gives priority mode (§7.6.1).
- PR1 = VBUS × 100k/400k with VREF 0.92/1.0/1.08 V, so switchover is at **3.68/4.00/4.32 V**.
- RON is 40/48 mΩ; reverse-current blocking at 42 mV; Iq on VIN2 is 1.35 µA.
- **L-3:** the datasheet lists no PR1 hysteresis. VBUS at the device under 0.7 A through a 0.5 Ω cable loop is about 4.75 − 0.35 − 0.16 ≈ 4.24 V, which sits inside the switchover band. The mux can toggle, each toggle a break-before-make gap that C4 bridges. Fix: add hysteresis (a high-value resistor from ST to PR1) or lower the threshold to about 3.8 V. The TP4056 UVLO is 3.5–3.9 V, so charging still starts.

**TLV755P.**

- Pins checked (DBV: 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT). EN = IN, so the LDO is always on (I-1).
- IOUT ≤ 500 mA. Current limit 560/720/865 mA at VOUT = 0.9·VOUT. Short-circuit (foldback) 355 mA. Dropout ≤ 215 mV at 500 mA (85 °C). IGND 25 µA typ / 31 µA max. Thermal shutdown 165 °C (SBVS320D §5.5).
- Caps: C4 22 µF in (2.9 mm away), C6 22 µF + C21 1 µF out (2.3/2.8 mm). The GND pin has a solid zone connection to a 31.7 mm² B.Cu island with 3 vias.
- Thermal: from VBUS at 150 mA average (Wi-Fi transfer) the LDO dissipates 0.29 W, a rise of about 29–68 °C (RθJA between the 100.8 °C/W EVM figure and the 231 °C/W JEDEC figure). At 300 mA sustained it would be 0.59 W and a 59–135 °C rise, so long Wi-Fi sessions while charging run U3 hot. Thermal shutdown protects it. Info.
- **M-2:** see §4.3.

### 3.5 ESP32-S3 module (U4) and boot, reset, USB, UART

**Function.**

- EN: R7 10 kΩ / C5 1 µF (τ = 10 ms, the Espressif RC). SW11 through R63 100 Ω (33 mA discharge).
- IO0: R13 10 kΩ pull-up. SW6 (BOOT) is DNP (**L-6**). Without SW6, download mode relies on USB-Serial-JTAG auto-reset. Firmware that disables that peripheral (for example TinyUSB MSC) or that crashes early leaves no recovery path without soldering. Fix: fit SW6, or at least add an IO0 test pad next to a GND pad.
- Strapping on the board (WROOM-1 datasheet Table 4-1/4-3/4-4):
  - GPIO0: pull-up → SPI boot.
  - GPIO45 and GPIO46: no pulls on the board. They go to J6 through 33 Ω and TPD4E1U06 (≤10 nA leakage), so the internal pull-downs win and VDD_SPI = 3.3 V. Correct for N16R8.
  - GPIO3: floating, only matters if the JTAG-select eFuse is burnt.
  - **L-7:** an accessory that drives GPIO45 high at reset selects 1.8 V VDD_SPI and the module will not boot. GPIO46 = 1 with GPIO0 = 0 is an invalid boot combination.
- IO35–37 are not connected, which is correct for octal PSRAM (WROOM-1 Table 3-1 note b).
- All analog inputs are on ADC1 (IO1, IO2, IO4, IO8, IO9), so there is no conflict with Wi-Fi (ADC2).
- UART0 goes to TP1/TP2. USB connects directly with no series resistors (fine for full speed).

**Decoupling.** C33 0.1 µF is 2.6 mm and C32 22 µF is 4.6 mm from pin 2. The exposed pad has 12 via-in-pad holes (0.2 mm) to F.Cu GND. OK.

**RF, finding M-3.**

- The antenna end of U4 is at x = 44.75. Pads 15–26 are at x = 70.1, so the antenna faces the left edge.
- The board notch (Edge.Cuts) is x 44.27–50.60, y 93.30–112.00. The module spans y 93.5–111.5, so the notch walls are 0.2 mm (top) and 0.5 mm (bottom) from the module sides.
- After the 0.475 mm edge clearance, GND pour sits about 0.7–1.0 mm from the antenna's long sides on both layers, for 25 mm above and 36 mm below.
- GND copper within 5 mm of the antenna area: 59.6 mm² (F.Cu) and 39.5 mm² (B.Cu). Within 15 mm: 418 and 191 mm² (`figures/fig2_antenna_notch.png`).
- Espressif HWDG §1.4.7, Fig. 24–26: keep ≥15 mm clear on the side opposite the feed point (max 2 mm on the feed side) and do not place the module "in the center of the board with clearance created by hollowing out". Here both sides are flanked at about 1 mm.
- The 4.26" panel (105.33 × 62.37 mm) mounts on the front over the whole board, including the antenna.
- Expect detuning and several dB lower efficiency. Fix: extend the notch ≥15 mm along the edge on one side (SW5 would move), or pull the pour back ≥5 mm. Alternatively, use WROOM-1U with an antenna outside the display shadow. Verify by over-the-air throughput (bench test 7.3).

**I-3:** the N16R8 is a 65 °C-ambient module (WROOM-1 Table 1-1).

### 3.6 microSD (J7, Q7, pull-ups, U1/U9)

- The pin-out matches the fitted SHOU HAN TF PUSH (1 DAT2, 2 CD/DAT3, 3 CMD, 4 VDD, 5 CLK, 6 VSS, 7 DAT0, 8 DAT1). The dual-source footprint also carries the MEM2075 pegs. The TF PUSH "Cd" pad is tied to GND, so there is no card-detect signal and firmware must probe.
- Pull-ups are 10 kΩ to the **switched** SD_VDD, and CLK has no pull-up. That is correct.
- 33 Ω series resistors are fitted. ESD covers all six lines: U1 on DAT2, DAT3, CMD, CLK and U9 on DAT0, DAT1.
- Q7 (AO3401A) defaults off through R40 100 kΩ while IO10 is high-Z. R77 bleeds SD_VDD.
- **L-11:** R78 = 1 kΩ into about 650 pF Ciss turns Q7 on in about 1 µs. SD_VDD then charge-shares C36 + C37 (1.1 µF) plus the card's internal capacitance (unknown, often a few µF) off the 3V3 bulk (about 30 µF effective), giving an estimated 0.1–0.4 V dip. Fix: add 10–47 nF gate-to-source on Q7 or raise R78 to about 47 kΩ for a soft start.
- Firmware obligation: drive CMD/DAT/CLK low or high-Z before switching SD_VDD off, otherwise the card is back-powered through its I/O clamps. The schematic note says this.

### 3.7 E-paper connector and booster (J2, Q4, L1, D4–D6, C10–C22, F6)

**Function.**

- Pin-out matches GDEQ0426T82 §5: 2 GDR, 3 RESE, 5 VSH2, 8 BS = GND (4-wire SPI), 9 BUSY … 24 VCOM.
- The booster and charge pump match the reference in §8.2: L 47 µH ≥ 500 mA, Q with Vds ≥ 30 V, Vgs(th) ≤ 1.5 V and RDS(on) ≤ 400 mΩ, diodes ≥ 30 V/500 mA, caps X5R ≥ 25 V, R1 1 MΩ, R2 2.2 Ω.
- Fitted parts: SLW5040S470MST (47 µH, **Isat 1.30 A**, Irms 0.94 A, DCR 0.283 Ω; Sunltech p.9). IRLML6346 (30 V, ±12 V, Vth 0.5–1.1 V, RDS(on) ≤ 63/80 mΩ at 4.5/2.5 V). B5819W (40 V/1 A). 50 V caps.
- Diode reverse stress is about 22 V on 40 V parts.
- R5 (10 kΩ) pulls EPD_RST high through sleep.
- The panel's VCI has 2.2–3.6 V operating and 4.0 V absolute maximum. Its 8 mA typical load through F6 (≤6 Ω) is fine.

**HV clearance.** The minimum gap between PREVGH/PREVGL/VSH/VSL and other copper is 0.15–0.30 mm. On J2 itself (VGH next to VSL, 37 V apart) the pad gap is 0.20 mm. IPC-2221B B4 (coated) and A6 (uncoated terminations) both require 0.13 mm for 31–50 V. OK (`hv_clearance.py`).

**Layout (L-14, L-15).**

- J2 caps sit 6–18 mm from their pins: C17 (VSH2) 18.6 mm, C22 (VCI) 13.2 mm, C18 (VDD) 11 mm. The FPC adds more length, so place them at the connector.
- Panel VSS (J2.17) connects through one 0.2 mm × 3.2 mm trace and a 2.8 mm² island with no via. DRC also flags it as a starved thermal. BS (J2.8) does land on the main island.
- Booster hot loop Q4 → D5 → C14 → GND → R14 is about 39 mm². C14 (the PREVGH reservoir) is 7.9 mm from D5.
- GDR and RESE are each 36 mm long, 28 mm on F.Cu.
- Fix: add a 1 µF/50 V cap at D5's cathode, run GDR and RESE as a tight pair, and move C17, C18 and C22 to J2.

**I-4:** the FH34SRJ is a top-and-bottom contact connector (Hirose/LCSC datasheet), so an FPC inserted flipped still mates, with the pin order reversed. The back silkscreen warns about this.

### 3.8 Frontlight driver (U10 TPS923610, L2, F3, Q5/Q6, U12, R37)

**Function.**

- LED current = VFB/R37 = 200 mV/15 Ω = 13.3 mA; 13.9 mA at worst case (206 mV, 1 %) (SNVSCN8B §6.5, §7.3.7).
- The GDEQ0426T82-FL01C drawing gives two strings of 5 LEDs each, **VF ≤ 15 V, IF ≤ 15 mA**, FPC pin-out 1 C+, 2 C−, 5 W+, 6 W−. J3 matches.
- OVP is 24.25–25.5 V, latching after three trips (§7.3.6). That is below D3's breakdown (SMAJ26A Vbr 28.9 V min) and D8's (PESD2IVN 26 V min). OK.
- U12 inverts COLOR_SEL so exactly one string is always selected.
- In shutdown, LED_SW ≈ VIN − 0.6 V through L2 and the high-side body diode (§7.3.3). That is too low to light a 5-LED string. OK.
- LED_MONIT = LED_SW × 0.107, so 25.5 V reads 2.73 V, inside the ADC range.
- COUT (4.7 µF/50 V 0805 X5R) is estimated at 1.2–1.6 µF effective at 25 V. The ≥1 µF requirement (§6.3) is met, marginally.

**Finding M-1.**

- Boost input power = (15 + 0.2) V × 13.3 mA / η ≈ 0.25 W, so I_IN ≈ 56 mA at 4.2 V, 77 mA at 3.3 V and 84 mA at 3.0 V (η = 0.8). At η = 0.7 (FCCM at light load) it reaches about 95 mA.
- F3 (MF-FSMF010X): Ihold 0.10 A at 23 °C, 0.08 A at 40 °C, 0.07 A at 50 °C. R between 0.90 Ω min and 6.0 Ω R1max (Bourns MF-FSMF p.1–2).
- The "F3 thermal keep-out" (44.8–49.6 × 114.3–117.3 mm, no pour on either layer) deliberately reduces heat-sinking, which lowers the effective hold current further.
- The IR drop across F3 (up to about 0.5 V) raises I_IN further.
- Result: in a warm case or at low battery, F3 trips. The light goes out or flickers as the PTC cools and re-trips. Not a safety issue.
- Fix: MF-FSMF020X (0.20 A hold, 0.50 A trip, 0.55–3.5 Ω). It still trips quickly on an output short, where the current through L2 and the body diode is amps.

**L-10.** L2 (VLS252012HBX-100M-1: 10 µH, **Isat 1.00 A spec / 1.30 A typ**, Itemp 0.85 A; TDK table) is below the switch limit (1.6–2.1 A). Normal peak is about 0.3 A. Only an overload saturates L2.

**Layout.** Output loop is 2.6 mm² and input loop is 9.5 mm². Good. The U10 GND pin reaches its local island (shared with C9 and R37) through a 0.25 mm trace and a single via (L-14).

### 3.9 Touch connector (J4) and option links

- The default pin-out matches the Good Display GDEQ0426T82-T01C drawing (1 GND, 2 VDD 3.3 V, 3 RST, 4 INT, 5 SDA, 6 SCL; FT6336U; 2.8–3.6 V). The FT6336U address (0x38) does not clash with the DS3231 (0x68). U7 protects RST, INT, SDA and SCL.
- **M-6:**
  - The back silkscreen at (95.9, 137.4) reads "some displays are different / they swap INT/VDD and SCL/SDA / if so, unpopulate R42,44,46,52 / then, populate R43,45,58,66".
  - There is no R42. VDD to J4.2 comes from **F4** (schematic H7, (318.8, 369.6)), and R43 connects TP_INT to the same pin.
  - A user who follows the board leaves F4 in place, so the alternate panel's INT output pin is tied to 3V3 through 0.9–6 Ω. When INT pulls low it sinks up to about 3.7 A (3.3 V / 0.9 Ω) until F4 trips, which is enough to damage the touch controller.
  - Fix: change the silkscreen to "remove F4, R44, R46, R52; fit R43, R45, R58, R66" and the schematic note to match.
- **L-17:** make each option pair mutually exclusive in hardware, for example with 3-pad solder jumpers. The same applies to R73/R74 in the button ladder, where fitting R74 with R73 present shorts 3V3 to GND.
- **L-18:** the touch VDD is always on (F4 from 3V3). FT6336U draws 4.32 mA active, **220 µA monitor (default after power-up)** and 55 µA hibernate (FocalTech datasheet). A touch variant therefore adds 55–220 µA to a 50 µA sleep budget. Fix: gate it like SD_VDD, or make firmware put the controller in hibernate before deep sleep.

### 3.10 RTC (U13 DS3231MZ; U14 DNP)

- VCC (pin 2) is grounded and VBAT (pin 6) is on 3V3 with C30 0.1 µF. That is the documented "single supply using VBAT only" configuration (DS3231M Fig. 5, Table 1). The I2C interface is active on VBAT. Timekeeping current is 2–3.5 µA, and temperature conversion runs every 10 s. Pin-out checked: 1 32KHZ, 2 VCC, 3 INT/SQW, 4 RST, 5 GND, 6 VBAT, 7 SDA, 8 SCL. OK.
- **I-5:** INT/SQW is not connected, so the RTC cannot wake the MCU. That is a design choice; the ESP32 RTC timer does the waking.

### 3.11 Buttons, ADC ladders, power button, battery monitor, status divider

- **Ladder 1 (IO1):** 0.033 / 1.185 / 2.20 / 2.80 V, idle 3.3 V.
- **Ladder 2 (IO4):** 0.033 / 1.80 / 2.533 / **2.877 V**, idle 3.3 V.
- The ESP32-S3 ATTEN3 calibrated range is 0–2900 mV with ±50 mV total error (ESP32-S3 datasheet Table 5-6). UP(2) sits at the edge of that range (**L-5**). Fix: change R36 from 68 kΩ to 47 kΩ (2.72 V) and R35 from 33 kΩ to 27 kΩ (2.40 V) to recentre.
- The 2.2 nF caps at the MCU provide filtering.
- PWR_BUTTON pressed = 3.3 × 100k/110k = 3.0 V, above VIH (0.75·VDD = 2.48 V). Pins IO1, IO4 and IO18 are RTC-capable, so they can wake the chip. OK.
- **BAT_MONIT:** 1 MΩ/1 MΩ on P+, so 4.2 V reads 2.1 V, with C8 1 µF. OK. Note that it reads P+, which is the charger voltage while charging.
- **USB_STAT** states are 2.20 / 1.115 / 0.55 / 3.3 V, well separated. C23 gives τ ≈ 17–100 ms depending on state, so the node settles within about 0.5 s.
- **L-4:** with VBUS absent the TP4056 is unpowered, but R67 and R71 still pull its CHRG/STDBY pins toward 2.2 V. If those pins have ESD diodes to VCC, the node drops to about 0.8 V and reads as "charging" or "done". The datasheets do not specify this, so a bench test is needed.

### 3.12 Expansion header J6 and the snap-off arm

- Pin rows: 1–6 at y = 47.97 (GND, IO46, IO45, GND, LED_SW, W−) and 7–12 at y = 45.43 (J6_3V3, SDA, IO3, SCL, C−, P+_FUSE).
- Protection: U8/U9 cover the signals, CR2/CR3 (SD05C, bidirectional, Vrwm 5 V; DOWO datasheet p.2) cover the rails, D3 covers LED_SW and D8 covers C−/W−.
- Fuses: F2 (0805L075: 0.75 A hold, Vmax 6 V) on P+ and F5 (0.10 A) on 3V3.
- **L-7, adjacency checks:**
  - LED_SW (pin 5) next to GND (pin 4): F3 trips. Safe.
  - LED_SW next to W− or C−: shorts one string at 13.3 mA. Harmless.
  - P+ (pin 12) to C− (pin 11) or W− (pin 6): Q6/Q5 act as a source follower (gate 3.3 V), so about (3.3 − 2.1)/15 Ω ≈ 80 mA flows continuously. R37 sits at about 0.1 W (its rating) and Q6 at about 0.24 W (RθJA 357 °C/W, roughly +85 °C), until the cell is flat. Fix: series resistance or a separate fuse on pin 12, or move P+ away from the LED pins.
- **H-2 (snap line):**
  - The arm is designed to be cut. F.Silkscreen reads "DISCONNECT BATTERY BEFORE CUTTING" (82.2–106.1 × 62.1–69.7). Dashed text-box borders mark the line on both silkscreens (y 61.27–62.70). The Edge.Cuts slot is 89.49–94.99 × 61.30–62.60. B.Silkscreen reads "extra LED outputs here in case header is snipped".
  - Copper crossing y = 61.95: **P+ (F.Cu 0.40 mm at x 87.40)**, **3V3 (B.Cu 0.25 mm at 101.32)**, LED_SW, C−, W−, SCL, SDA, IO3, IO45, IO46, the power-button node, and the GND pour on both layers (8.1 mm on F.Cu, 10.8 mm on B.Cu).
  - P+ and 3V3 are **0.20 mm** from the GND pour at the cut; the other nets are 0.15 mm.
  - F2 (87.0, 57.0) and F5 (99.5, 61.0; its pads overlap the cut band by 0.2 mm) both leave with the arm. The remaining P+ stub is protected only by the DW01A (0.77–1.8 A after 7–20 ms) and the pack PCM, and it is about 3 mm from the battery bay edge.
  - A snapped FR4 edge with copper burrs can bridge 0.2 mm. A resistive bridge of 4–15 Ω dissipates 1–4 W without tripping anything.
  - The power button SW10 also leaves with the arm. That is expected, since UP(2) is offered as an alternative.
  - Fix: place F2 and F5 on the main-board side of the line, or route P+ and 3V3 through 0 Ω links there that the user removes before cutting. Pull both GND pours back ≥1 mm from the line. Change the instruction to add "seal the edge and check P+–GND > 1 MΩ before reconnecting". See `figures/fig1_snap_line.png`.
- **I-7:** the front J6 legend is a two-row table ("GND 46 45 GND LED+ W−" above "3V3 SDA 3 SCL C− BAT+") placed above the header. In the same front view the physical row nearer the legend is pins 7–12, so the table rows are in reverse order. Confirm this is intended.

### 3.13 Mechanical, mounting, battery bay

- H1–H6 are M2 (2.2 mm drill, Ø2.6 mm pads) tied to GND. Non-GND copper lies 0.77–1.3 mm from the pad edge.
- **L-13:** H1 has P+_FUSE at 0.91 mm. H5 has B+ at 1.22 mm and the Q3 gate at 0.77 mm. H6 has 3V3 at 1.22 mm. A DIN 125 M2 washer (Ø5 mm) or a 4.5–5 mm standoff rests on mask-only copper. Because the pads are P- (GND), the board DW01A still protects a B+–GND contact. Fix: a copper keep-out ring of about Ø5.5 mm, or a documented screw-head limit.
- Battery-bay edge: the nearest copper is 0.5–0.8 mm from the bay edge (IO3, PWR_BUTTON, R85/R86 pads), all under mask. OK.
- J5 (fitted CJT A2001WR-2P: 2.0 mm, 3 A, 100 V) has no hold-down tabs. Cable strain goes into the two joints, so strain-relieve the battery lead in the case.

---

## 4. Cross-block interactions

### 4.1 Power sequencing

- 3V3 rises through the TPS2116 soft start (about 1.3 ms) and the TLV755 start-up (550 µs).
- EN then follows the 10 ms RC.
- The panel, touch, RTC and expansion rails come up with 3V3 (no sequencing needed). SD_VDD stays off until firmware asserts it. OK.

### 4.2 Back-power and leakage paths

- VBUS is not back-driven: TPS2116 reverse leakage is 0.001 µA, the TP4056 BAT→VCC path is < 2 µA, and no other path exists. OK.
- SD lines can back-power the card when SD_VDD is off (§3.6, firmware).
- EPD_RST is pulled up by R5. If firmware holds it low in sleep it costs 330 µA.
- The LED_MONIT divider always sits on LED_SW (about VIN − 0.6 V), costing about 3 µA (I-1).
- L-4 (TP4056 status pins when VBUS is absent).

### 4.3 Brown-out under coincident peak loads (M-2)

- Coincident 3V3 load: ESP32 TX 355 mA (WROOM-1 Table 6-4) + SD write (assumed 100 mA typ, up to about 200 mA) + EPD refresh (assumed about 50 mA) + 10 mA misc ≈ **515–615 mA**. The TLV755 is rated 500 mA and limits at 560 mA minimum. The frontlight (up to about 90 mA) draws from LDO_IN on top of that.
- Board battery path, J5 → LDO input and back, is **344 mΩ typ / 478 mΩ max**: Q3 + Q8 + Q1 + R85‖R86 + TPS2116 + measured traces (`calc_budget.py`).
- With a 0.15–0.30 Ω cell plus PCM, 3V3 stays in regulation only above these cell OCVs:

  | Load | Cell OCV needed |
  |---|---|
  | 0.30 A | 3.58–3.68 V |
  | 0.50 A | 3.76–3.93 V |
  | 0.65 A | 3.90–4.12 V |

- Below those voltages 3V3 follows VIN − dropout. The ESP32 minimum is 3.0 V (WROOM-1 Table 6-2).
- Expected symptoms: resets or SD write errors during Wi-Fi at about ≤50 % charge if transfers overlap SD writes or refreshes.
- Fix:
  - Firmware: never overlap TX bursts with SD writes or refresh, and disable Wi-Fi below about 3.7 V.
  - Hardware: remove Q3 (L-8, −50 mΩ), widen the 0.25 mm battery tracks, and consider a 1 A LDO or a buck-boost.

### 4.4 Deep-sleep budget (battery only, no touch panel; `calc_budget.py`)

| Item | µA typ / max |
|---|---|
| TLV755 IGND | 25 / 31 |
| ESP32-S3 deep sleep (RTC timer) | 8 / 15 |
| DW01A | 3 / 6 |
| TPS2116 VIN2 | 1.35 / 3.7 |
| BAT_MONIT divider (2 MΩ) | 1.9 / 2.1 |
| USB_STAT divider (3 MΩ) | 1.1 / 1.1 |
| Q3 and Q9 gate dividers (10 + 11 MΩ) | 0.7 / 0.8 |
| LED_MONIT divider on LED_SW | 2.9 / 3.3 |
| DS3231M on VBAT | 2.6 / 4.1 |
| EPD deep sleep | 2 / 6 |
| TP4056 BAT, TPS923610 shutdown, 74LVC1G04 | ~1.2 / 6.5 |
| **Total** | **≈ 50 / 80 µA → 419 / 262 days on 500 mAh** |

- A touch variant adds 55 µA (hibernate) or 220 µA (monitor) (L-18).
- There is no ship mode. After the DW01A over-discharge trip, about 5 µA (DW01A power-down plus dividers) keeps draining the cell, so a dead device left for months pushes the cell into deep discharge. Store devices charged, and have firmware stop at ≥3.3–3.4 V (I-1, I-6).

### 4.5 Fault propagation (single faults)

| Fault | Outcome |
|---|---|
| TP4056 VCC→BAT short | VBUS drives P+. The DW01A sees P+ (VCC) > 4.3 V and opens FET2 within 110–200 ms; the pack PCM is a second layer. P+ = 5 V is within the ratings of C3 (10 V), TPS2116 (6 V), DW01A (10 V) and CR3. |
| TPS2116 VIN1–VIN2 short | Same as above. VBUS is also back-driven from the cell when unplugged. |
| 3V3 short | TLV755 folds back to 355 mA and cycles in thermal shutdown. Shorts at J6_3V3 or J4 trip F5/F4 within about 1 s at ≥0.5 A. |
| LED_SW short to GND | F3 trips. L2 saturates (L-10). |
| EINK_3V3 short | F6 trips. |
| Q8 short | Reverse-polarity protection is lost, because Q3's body diode conducts (L-8). |

### 4.6 Logic levels and I2C

- I2C pull-ups are 2.2 kΩ to 3V3. Bus length is about 185 mm of copper (118 mm on F.Cu, 6 vias) plus the touch FPC and any accessory, roughly 50–100 pF total, giving a rise time of about 0.19 µs. That is under the 0.3 µs fast-mode limit. OK.
- The DS3231M tolerates up to 5.5 V on SDA and SCL regardless of supply.
- SSD1677 VIH is 0.8·VDDIO. VDDIO (EINK_3V3) sits up to about 0.05–0.5 V below 3V3 because of F6. Logic margins are OK.

### 4.7 GPIO strapping and boot

The on-board defaults are correct. The risks come from the exposed strapping pins on J6 (L-7) and the missing BOOT button (L-6).

### 4.8 Firmware obligations imposed by the hardware

1. ADIM must stay high ≥40 µs to enable and low ≥2.5 ms to shut down or clear the OVP latch.
2. Change COLOR_SEL only at zero duty.
3. Disable the frontlight if LED_MONIT exceeds about 23 V.
4. Drive SD pins low before removing SD_VDD.
5. Keep EPD_RST high in sleep and put the panel in deep sleep.
6. Put the touch controller in hibernate before deep sleep.
7. Use only settled USB_STAT readings (about 0.5 s).
8. Avoid overlapping TX, SD and refresh loads at low cell voltage.
9. Shut down at about 3.3–3.4 V.
10. Treat BAT_MONIT as P+, which reads the charger voltage while charging.
11. If an override is added, apply a charge timer and temperature limits.

---

## 5. EMI/EMC notes

1. **Switch nodes.**
   - The frontlight boost runs at 1.1 MHz with small loops (2.6 and 9.5 mm²). It is 7–10 mm from the antenna notch. Low risk.
   - The SSD1677 booster has a hot loop of about 39 mm² and 36 mm GDR/RESE runs (L-15). It is the likeliest source of conducted and radiated noise up to about 100 MHz while the panel refreshes. A local cap at D5 and pairing GDR with RESE are cheap fixes.
2. **Reference plane.**
   - F.Cu is the main GND plane (about 3.3k mm² continuous). B.Cu GND is split into 52 islands, several stitched by only 0–1 via.
   - Long F.Cu traces cut the plane: LDO_IN runs 62 mm diagonally, I2C 118 mm, the LED lines 139–166 mm around the perimeter, and 3V3.
   - USB D± each cross about 11 such slots and SD lines cross 2–7. This is acceptable for 12 Mb/s USB and default/HS SD, but adds stitching vias where B.Cu signals cross F.Cu traces would help.
3. **Antenna.** See M-3: notch flanked by GND, display on top.
4. **ESD entry points.**
   - USB is protected (CR1, U6), with the shell bonded straight to GND (good for ESD).
   - microSD, J4 and J6 are protected.
   - Buttons are not protected, and the tact-switch iron covers (TS365ZJ material list) are floating on pads 3/4 (L-16). Tying pads 3/4 to GND gives ESD a path that bypasses the ladder nets.
5. **Cable/shield bonding.** The USB shield goes directly to GND. There is no separate chassis, which is appropriate for a battery handheld.
6. **Board edges.** GND pour reaches 0.475 mm from the edge. LED_SW (DC with ripple) runs along the perimeter. There are 4 dangling F.Cu stubs of ≤1.7 mm on the button nets (DRC warnings), which are negligible.

---

## 6. Checked and found OK (brief)

- **Design rule checks:** DRC run on the board as saved shows 0 errors, 0 unconnected and 0 parity issues. The 54 warnings are silkscreen and starved-thermal warnings, including J2.17 (see L-14). Zone fills are current (a refill changes nothing).
- **Pin maps:** checked against the datasheets of the fitted parts: J1, J2, J3, J4, J5, J7, Q1–Q9, U2, U3, U5, U10, U11, U12, U13, D2–D6, CR1–CR3, D8, U1/U6–U9 (TPD4E1U06 pin 5 = NC).
- **Footprints:** Shou Han USB-C (pads and slots per the LCSC drawing; 3 A, 5 V), TF PUSH microSD dual-source, CJT PH wafer.
- **USB-C:** sink Rd, D± tied, damped VBUS bulk, CC/VBUS adjacency covered by U6 (≥6.5 V).
- **Charger ratings and thermal:** detection of a reversed, shorted or deeply discharged cell disables CE. Good.
- **DW01A/FS8205A:** wiring, delays and VM filter. Reverse polarity is blocked (by Q8) with and without USB.
- **TPS2116:** priority wiring and status; LDO caps and stability window (1–200 µF).
- **ESP32:** EN RC, IO0 pull-up, PSRAM pins, ADC1 only, decoupling, exposed-pad vias.
- **microSD:** pull-ups to the switched rail, default-off gate, ESD.
- **E-paper:** booster parts and ratings against the Good Display reference; HV clearances meet IPC-2221B.
- **Frontlight:** current set-point within IF ≤15 mA, OVP below the TVS breakdowns, string selection logic, shutdown path, LED_MONIT scaling.
- **Touch:** default pin-out against the T01C drawing; I2C address map.
- **RTC:** the VBAT-only configuration is valid.
- **Capacitor voltage ratings** including DC bias (all 50 V parts on the ±15–25 V rails), resistor power, diode Vr, MOSFET Vds/Vgs, connector ratings (FH34SRJ 0.5 A/50 Vrms; PH 3 A).
- **Current paths:** B+/B− (0.40 mm), USB_VBUS, P+, LDO_IN and 3V3 (0.25–0.40 mm) carry their normal currents with < 10 °C rise.

### 6.1 Not checked, and why

- **RF performance:** no measurement is possible from files. M-3 is a geometric deviation from Espressif's guidance.
- **Thermal behaviour:** not measured. The estimates use datasheet θJA values.
- **Pack and PCM behaviour** (M-5, I-6): depends on the pack fitted. The README pack has no datasheet, so a representative 503035 datasheet was used.
- **Firmware:** not available. The hardware-imposed obligations are listed in §4.8.
- **SSD1677 booster internals** (RESE threshold, switching frequency): the controller datasheet was not reviewed. The circuit was checked against Good Display's reference only.
- **Standards text** (IEC 62133-2, IEC 62368-1, USB-IF specifications): not accessible. They are cited only as context.
- **Copper weight and stack-up:** not in the board file, so 1 oz was assumed. Mechanical stack (case, display position, screws) is also not in the design files.
- **Clone parametrics:** the TECH PUBLIC TPD4E1U06 sheet is image-only and was not reviewed in detail; TI's TPD4E1U06 figures were used. (The MDD 74LVC1G04 sheet was checked: SOT23-5 pin-out 1 NC, 2 A, 3 GND, 4 Y, 5 VCC matches.) Capacitor DC-bias derating is estimated, not taken from vendor curves.

---

## 7. Bench tests for the suspected items

| # | Item | Set-up | Measure | Pass / expected |
|---|---|---|---|---|
| 7.1 | H-1 | Thermocouple on the cell. Charge at −5 °C and at 50 °C ambient. | I(J5) | Today: charges (fails the cell spec). After the fix: charging stops outside 0–45 °C. |
| 7.2 | M-2 | Battery emulator (supply + 0.25 Ω) at 3.6/3.7/3.8/4.0 V. iperf TX at max power, SD write and EPD refresh together. | 3V3 at C32 and LDO_IN at C4 on a scope (100 µs/div); reset reason; DW01A OD (U5.1) | 3V3 ≥ 3.0 V; no resets; no DW01A trip |
| 7.3 | M-3 | Assembled unit with panel and case | RSSI and TCP throughput at 1/5/10 m against a reference WROOM-1 board | Within about 3 dB / 20 % of reference |
| 7.4 | M-1 | Full brightness, VIN from emulator at 3.3 V, ambient 25 °C then 45 °C, 60 min | I(F3), V across F3, LED_SW, light output | No drop-outs; F3 drop < 0.3 V |
| 7.5 | M-5 | Discharge a protected 503035 until its PCM trips (P+/P− ≈ 0 V), insert, plug USB | U11.8 (CE), I(J5), DET_NODE | Today: CE stays low and the pack never wakes |
| 7.6 | M-4 (sacrificial board) | VBUS from a current-limited supply at 6.0 / 7.0 / 8.0 / 9.0 V | IR camera on CR1/F1, U2/U3 survival | Shows the over-voltage behaviour |
| 7.7 | L-2 | Electronic load on P+ (via J6.12 with F2 bypassed), board at 25 °C and 60 °C | Trip current and delay | 1.0–1.8 A, 7–20 ms |
| 7.8 | L-3 | USB source through 0.5 Ω, 0.1 → 0.7 A load steps | ST (U2.8), LDO_IN | No repetitive toggling |
| 7.9 | L-4 | Battery only, USB unplugged | USB_STAT, USB_VBUS | 2.2 V and < 0.1 V |
| 7.10 | H-2 (sacrificial board) | Snap the arm as instructed | Microscope on the edge; insulation P+–GND and 3V3–GND; IR camera with a deliberate 10 Ω bridge | > 10 MΩ; with the bridge, about 0.4 A, no trip (demonstrates the risk) |
| 7.11 | L-1 | Partially discharged cell | I_BAT in CC and termination | About 110 mA, about 11 mA |
| 7.12 | I-1, L-18 | Deep sleep, panel in deep sleep, touch hibernate/monitor | I(J5) with a µA meter | 50–80 µA (+55/+220 µA with touch) |
| 7.13 | L-11 | Card inserted, toggle SD_ACTIVATE | 3V3 dip at C32 | < 0.2 V |
| 7.14 | USB hot-plug | 1 m cable, 5 V/3 A source | USB_VBUS at C25 | Peak < 6 V |
| 7.15 | Thermal | USB charging + continuous Wi-Fi transfer, 25 °C | U3, U11 case temperature | < 85 °C |
| 7.16 | L-15 EMI | Panel refreshing | Near-field probe over Q4/L1/D5 and the GDR/RESE route; pre-scan 0.15–300 MHz | Locate hot spots |
| 7.17 | Reverse polarity | Reversed 4.0 V source (1 A limit) on J5, with and without USB, and with the charger "fooled" (L-9) | I(J5) | < 10 µA, or ≤ about 15 mA in the fooled case |

---

## 8. Sources

Datasheets (page or section numbers as cited above):

1. TP4056 (NanJing Top Power, English): https://dlnmh9ip6v2uc.cloudfront.net/datasheets/Prototyping/TP4056.pdf (p.1 abs max; p.2 TEMP/PROG, electrical characteristics; p.3 RPROG table)
2. TP4056 REV 2.4 (TOPPOWER, LCSC C16581): https://datasheet.lcsc.com/datasheet/pdf/d328ee101cbb1f3719611cd61db479c2.pdf?productCode=C16581 (p.2, p.5, p.7, p.9, p.10)
3. DW01A (PUOLOP, LCSC C351410): https://datasheet.lcsc.com/datasheet/pdf/0d2b2b5e8d1207bf276387cb4ff3a495.pdf?productCode=C351410 (p.2 pins, p.3 application/abs max, p.4 characteristics)
4. FS8205A (TECH PUBLIC, LCSC C2830320): https://datasheet.lcsc.com/datasheet/pdf/c060cb7baa8cc2b2d2a0ed3afa443ef8.pdf?productCode=C2830320 (p.1–2)
5. AO3401A (AOS): https://www.aosmd.com/res/datasheets/AO3401A.pdf (p.1–2)
6. BSS138 (Hongjiacheng, LCSC C7420339): https://datasheet.lcsc.com/datasheet/pdf/514e3e5ec4f4cdec2b1076b59af25652.pdf?productCode=C7420339 (p.1–2)
7. IRLML6346 (Infineon): https://www.infineon.com/dgdl/irlml6346pbf.pdf?fileId=5546d462533600a4015356686fed261f (p.1–2)
8. TPS2116 (TI SLVSFG1A): https://www.ti.com/lit/ds/symlink/tps2116.pdf (§5, §6.1, §6.5, §6.6, §7.3–7.6)
9. TLV755P (TI SBVS320D): https://www.ti.com/lit/ds/symlink/tlv755p.pdf (§5.1, §5.3–5.5)
10. TPS923610/1/2 (TI SNVSCN8B): https://www.ti.com/lit/ds/symlink/tps923610.pdf (§6.1, §6.3, §6.5, §7.3.3, §7.3.6, §7.3.7)
11. ESP32-S3-WROOM-1/1U datasheet v1.8: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf (Table 1-1; §4 Tables 4-1, 4-3, 4-4; Table 6-2; Table 6-4; Table 6-7; §11)
12. ESP32-S3 Series datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf (DC characteristics; Table 5-6 ADC)
13. ESP32-S3 Hardware Design Guidelines: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/esp-hardware-design-guidelines-en-master-esp32s3.pdf (§1.4.7 Fig. 24–26; §1.4.8)
14. DS3231M (LCSC C107410): https://datasheet.lcsc.com/datasheet/pdf/a13630e1494a9129cb1340130e3d9e82.pdf?productCode=C107410 (pin description; Power-Supply Configurations, Fig. 5, Table 1; VBAT current table)
15. TPD4E1U06 (TI): https://www.ti.com/lit/ds/symlink/tpd4e1u06.pdf (§4, §5)
16. TSD05C (TI): https://www.ti.com/lit/ds/symlink/tsd05c.pdf ; SD05C-01FTG (DOWO, LCSC C5299440): https://datasheet.lcsc.com/datasheet/pdf/56a6ef45381a96bd55bd4a94c5e4929d.pdf?productCode=C5299440 (p.1–2)
17. SMF6.5CA (Hongjiacheng, LCSC C19077501): https://datasheet.lcsc.com/datasheet/pdf/fa41ee376507916bceb7512729759974.pdf?productCode=C19077501
18. SMAJ26A (Hongjiacheng, LCSC C19077543): https://datasheet.lcsc.com/datasheet/pdf/f3d2c9df3269749880b305befd579c39.pdf?productCode=C19077543
19. PESD2IVN-UX (TECH PUBLIC, LCSC C42370512): https://datasheet.lcsc.com/datasheet/pdf/142c8eb0016167b0aa120767942fede2.pdf?productCode=C42370512
20. SMD0805B100TFT (Brightking, LCSC C269106): https://datasheet.lcsc.com/datasheet/pdf/1f9f1003a75effea10bcf8c5507d7438.pdf?productCode=C269106
21. 0805L series PTC (Littelfuse, LCSC C151146): https://datasheet.lcsc.com/datasheet/pdf/c1633066ff911e714178a6666bd78932.pdf?productCode=C151146
22. MF-FSMF series PTC (Bourns): https://www.bourns.com/docs/Product-Datasheets/mf-fsmf.pdf (p.1 table, p.2 derating)
23. 1N5819HW (Diodes): https://www.diodes.com/assets/Datasheets/1N5819HW.pdf ; B5819W (JSCJ, LCSC C8598): https://datasheet.lcsc.com/datasheet/pdf/4ac2c059be7c462694ab0715ce987a85.pdf?productCode=C8598
24. SLW5040S470MST (Sunltech, LCSC C206267): https://datasheet.lcsc.com/datasheet/pdf/16a34ec7a15bbf521004d23a01bc844f.pdf?productCode=C206267 (p.9 SLW5040S table)
25. VLS252012HBX (TDK, LCSC C88532): https://datasheet.lcsc.com/datasheet/pdf/de422f385540fd5f1bb91cb97a2c323c.pdf?productCode=C88532 (rating table)
26. Good Display GDEQ0426T82 specification: https://v4.cecdn.yun300.cn/100001_1909185147/GDEQ0426T82.pdf (from https://www.good-display.cn/companyfile/895.html; §5, §6–7.1, §8.2)
27. Good Display GDEY0426T82-FL01C specification: https://v4.cecdn.yun300.cn/100001_1909185148/GDEY0426T82-FL01C_Specification.pdf (§2 "5 dies in serial, 15V") and GDEQ0426T82-FL01C drawing: https://v4.cecdn.yun300.cn/100001_1909185148/GDEY0426T82-FL01C.pdf (LED VF ≤ 15 V, IF ≤ 15 mA, FPC pins). Product page: https://www.good-display.com/product/880.html
28. Good Display GDEQ0426T82-T01C drawing: https://v4.cecdn.yun300.cn/100001_1909185148/GDEQ0426T82-T01C-Drawing.pdf ; FT6336U datasheet: https://v4.cecdn.yun300.cn/100001_1909185148/FT6336U-DataSheet-V1.0.pdf (current consumption table). Product page: https://www.good-display.com/product/371.html
29. Hirose FH34SRJ (LCSC C324726): https://datasheet.lcsc.com/datasheet/pdf/4fa13630ce538d3df6cea685e5f75b4e.pdf?productCode=C324726
30. SHOU HAN TYPE-C 16PIN 2MD(073) (LCSC C2765186): https://datasheet.lcsc.com/datasheet/pdf/2d53d8d8199c9dd6666d9bc9ac7c3a1e.pdf?productCode=C2765186
31. SHOU HAN TF PUSH (LCSC C393941): https://datasheet.lcsc.com/datasheet/pdf/dc83ceb7bc09989eab2815b685da60e4.pdf?productCode=C393941
32. CJT A2001WR-2P (LCSC C48579993): https://datasheet.lcsc.com/datasheet/pdf/3aec8702163b54f9ee372bbb9366c72b.pdf?productCode=C48579993
33. SHOU HAN TS365ZJ (LCSC C557598): https://datasheet.lcsc.com/datasheet/pdf/b013d4d9ebc4e5638457e18601f6fd8a.pdf?productCode=C557598
34. 74LVC1G04 (MDD, LCSC C53185133, fitted part): https://datasheet.lcsc.com/datasheet/pdf/8f62b9f8a41f534c1286677e2e022a7e.pdf?productCode=C53185133 (Table 2 pin description); SN74LVC1G04 (TI): https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf
35. Representative cell, PKCELL LP503035 500 mAh: https://www.batterypkcell.com/uploads/LP503035-500mAh-3.7V.pdf (spec table items 3–9)
36. UNI-ROYAL 1206W4F100LT5E (R85/R86, LCSC C25334): https://datasheet.lcsc.com/datasheet/pdf/0a975aaa49b7c97f38a963127be4a823.pdf?productCode=C25334 (power code W4 = 1/4 W)

---

## Appendix: reproducing the numbers (`scripts/`)

| Script | Purpose |
|---|---|
| `sexpr.py`, `netlist_dump.py` | Parse the exported netlist (components, nets, pins) |
| `block_map.py` | Proves every reference designator is assigned to one block |
| `render_sch_regions.py` | Rasterises schematic regions for visual review |
| `board_dump.py` | KiCad Python: exports footprints, pads, tracks, vias, zones and outline to JSON |
| `refill_copy.py` | KiCad Python: refills zones on a **copy** to confirm fills are current |
| `net_resistance.py` | Track and via resistance between pads (1 oz Cu; pass-through pads not modelled) |
| `hv_clearance.py` | Clearance of HV nets against IPC-2221B |
| `plot_region.py` | Annotated layout plots (figures) |
| `calc_budget.py` | Charge current, DW01A trip, battery path / brown-out, F3 load, deep-sleep budget, USB_STAT, TPS2116, ADC ladders, LDO thermal |
| `render_pcb.py`, `pdf2txt.py`, `dspages.py`, `lcsc_fetch.py` | Rendering and datasheet helpers |

Typical sequence (KiCad 9.0.6):

1. `kicad-cli sch export netlist --format kicadsexpr -o net.net silkscreen_pcb.kicad_sch`
2. `python netlist_dump.py net.net out`
3. `"C:\Program Files\KiCad\9.0\bin\python.exe" board_dump.py silkscreen_pcb.kicad_pcb board.json`
4. `python net_resistance.py board.json "B+" "J5.2>Q3.2"` (quote the pad pair so the shell does not treat `>` as a redirect)
5. `python calc_budget.py`
