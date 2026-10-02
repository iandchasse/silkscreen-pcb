# Front-light driver alternate for U10 (TPS923610)

**Status: study only. Nothing here is on the board.** Studied 2026-10-01 against Rev 1.01 (commit `5809233`) and firmware commit `5d58fdc0`. Stock and prices were fetched that day and must be re-checked before relying on them.

This is a design reference for a future revision. It records why U10 needs an alternate, what the alternate has to satisfy, every part that was considered, and how the recommended option would be placed, routed, built and tested.

---

## 1. Summary

**The problem.** U10, the TPS923610DRLR front-light boost, had **2 pieces** at LCSC/JLC on 2026-10-01. Every part in its family is short as well: TPS923611 97, TPS923611LS 250, TPS923612 361, TPS923621 54. The closest TI twin, TPS61158, had 21. A JLC build therefore means pre-ordering U10 or Global Sourcing it.

**Two studies were run:**

| Study | Constraint | Result |
|---|---|---|
| 1 | One part, built-in rectifier, no diode | **No stocked part meets every requirement.** Best compromise: Diodes AP3036BKTR-G1. It fails the sleep-current requirement, needs D3 changed to SMAJ28A, and dims poorly. |
| 2 | Boost IC + the B5819W already in the BOM (D4-D6) | **TPS61160DRVR + B5819W + 220 nF 0402 COMP cap.** It meets every hard requirement with guaranteed datasheet limits and leaves D3 unchanged. |

**Recommendation: study 2.** Add **U15 TPS61160DRVR (LCSC C165143)**, **D7 B5819W (C8598)** and **C35 220 nF 0402 (C16772)** as DNP parts next to U10. The alternate build fits U15 + D7 + C35 and leaves U10 empty. You fit one driver or the other, never both, because the two SW pins share L2.

What the alternate costs:
- three extra placements;
- about 2-3 h of layout work, which also moves some standard-build copper;
- two mandatory firmware changes (a minimum PWM duty and a decay-based open-load probe);
- a shallower dimming floor: 26-39 µA, against 13-20 µA on the TPS923610;
- per-build paste control, so that the empty driver land gets no solder paste.

---

## 2. Requirements

These come from the TPS923610 datasheet (TI SNVSCN8A), the board netlist, the L2 (TDK VLS252012HBX-100M-1) and D3 (SMAJ26A) datasheets, and the firmware's `BoardConfig.h` and `FrontlightManager.cpp`. H = hard, S = soft.

| # | Requirement | Number | TPS923610 (reference) |
|---|---|---|---|
| R1 H | Built-in rectifier (study 1 only; study 2 allows the B5819W) | synchronous or on-die Schottky | synchronous |
| R2/R7 H | Works with the shared parts; internally compensated (study 2 allows one COMP cap) | L2 10 µH ±20 % (Isat 1.00 A rated / 1.30 A typ, Itemp 0.85 A); C9 4.7 µF/50 V 0805 (about 1-2 µF effective); C12 4.7 µF; R37 15 Ω | yes |
| R3 H | Low-side FB across R37 | FB to GND | yes |
| R4 H | Stock | thousands or more at LCSC/JLC | **2 pcs** |
| R5/R6 H | VIN (LDO_IN) | 2.9-5.5 V operating; UVLO rising ≤ 2.9 V; abs max ≥ 6.0 V | 2.5-5.5 V, abs max 6 V |
| R8/R9 H | Output and duty | regulates 10-22 V; Dmax ≥ 0.90 (2.9 V into the 21.66 V strip at 0.30 W needs 0.89) | 5-24.5 V |
| R10 H | SW abs max | ≥ 30 V (D3 is 77 mm away and absent on the cut-down board) | 32 V |
| R11 H/S | FB voltage | ≤ 0.222 V (keeps the panel under 15 mA with R37 at -1 %); target 0.19-0.21 V, ±3 % | 195/200/206 mV |
| R12 H | FB bias | ≤ about 1 µA | 0.1 µA |
| R13-R16 H | Dimming input | logic PWM (not EasyScale-only or RC-analog); VIH ≤ 2.0 V, VIL ≥ 0.4 V; pull-down or off while floating; enabled within 150 µs | ADIM, 600 kΩ pull-down, 40 µs |
| R17 H | Shutdown on LOW | 40 µs < t_SD ≤ 3 ms; LED current 0 while LOW ≥ 3 ms | 2.5 ms |
| R18 H | PWM frequency | 25 kHz inside the rated range | 10-200 kHz |
| R19-R21 S | Dimming depth | 1 LSB at 25 kHz / 10 bit = 39.1 ns per 40 µs (0.098 %). Target ≤ about 20 µA at the lowest step; acceptable ≤ about 130 µA at the 1 % step | about 13 µA ideal, 20 µA typ at 1 LSB |
| R22 H | OVP window | rising ≥ 22.7 V (highest string); an open load must hold ≥ 23.3 V for the firmware's 23 V probe; OVP max plus overshoot < 28.9 V (SMAJ26A minimum breakdown). S: ≤ 26.0 V and ≤ 27.07 V (ADC full scale) | 24.25-25.5 V, 1 V hysteresis |
| R23/R24 H | Recovery | hiccup, or a latch cleared by EN LOW ≤ 3 ms or by UVLO; survives FB = 0 and an output short | hiccup ×3, then latch cleared by ADIM LOW |
| R25-R27 S | Current limit, fsw, soft start | ILIM ≥ 0.5 A (≤ 1.3 A preferred); fsw ≥ 300 kHz; soft-start peak ≤ about 1 A | 1.6-2.1 A, 1.1 MHz |
| R28 H | Shutdown current (LDO_IN is always on) | ≤ 1 µA typ / ≤ 5 µA max, against a sleep floor of about 58 µA | 0.13 / 0.25 µA |
| R29 H | Off-state output | LED_SW below string conduction (≤ about 5.2 V) | body diode, about VIN - 0.5 V |

Firmware behaviour the driver must work with, unchanged unless stated:
- 25 kHz, 10-bit LEDC PWM on IO42 (`PWM_LED`), clocked from the 40 MHz XTAL, so 1 LSB is a 25 or 50 ns pulse;
- a 150 µs HIGH enable pulse before the PWM handover;
- a 3 ms dark dwell before any re-enable;
- a switch-on probe of 20 ms readings over 500 ms that trips at 23 V on LED_MONIT (IO2);
- `railSafeV` 15 V and `RAIL_WAIT_MAX_US` 4 s.

---

## 3. Study 1: one part with a built-in rectifier

**Search coverage.** The whole JLC "LED Drivers" boost listing, the established brands, the Chinese vendors, and part-number sweeps (about 100 datasheets). Only two stocked parts combine a built-in rectifier with a 200 mV FB, and both are ex-BCD Diodes parts.

| Part | LCSC | Stock LCSC / JLC | Rectifier | FB | OVP vs D3 (28.9 V min) | Verdict |
|---|---|---|---|---|---|---|
| TPS923610DRLR (U10) | C52919131 | 2 / 2 | synchronous | 195/200/206 mV | 24.25-25.5 V, below | reference, no stock |
| **AP3036BKTR-G1** (Diodes) | C526368 | 20,380 / 20,384 | on-die Schottky | 188/200/212 mV | 30 V typ only (graph 29.3-29.65 V), overlaps | best compromise, conditional |
| AP3019AKTR-G1 (Diodes) | C44956 | 16,405 / 16,986 | on-die Schottky | 188/200/212 mV | 30 V typ, overlaps | reject: CTRL rated only to 2 kHz |
| TPS61158DRVR (TI) | C702280 | 21 | integrated | 194/200/206 mV | 27.5-29.0 V | stock |
| TPS923611 / 611LS / 612 / 621 | C52919130 / C52919129 / C53198092 / C52919128 | 97 / 250 / 361 / 54 | synchronous | about 200 mV | 29.6-31.4 V, overlaps (needs SMAJ33A) | stock |
| TPS61080/81 (TI) | C2070657 / C882827 | 2,063 / 9,570 | diode + input disconnect | 1.229 V | 27-29 V | not one part: needs SS resistor and filtered PWM |
| STLD40DPUR (ST) | C2969763 | about 2,250 | on-die Schottky | 165 mV | 36-42 V | reject: D3 clamps every open load |
| RT4526GJ6 (Richtek) | C425168 | 390 | internal | 300 mV | 30 V | reject: stock and FB |
| LT3591 (ADI) | C670991 | 282 | on-die | high-side sense | 40-44 V | reject: topology |

Parts with a built-in rectifier but 0-36 pieces in stock: SGM3725/3726/3727/3749C/3750, FAN5341/5343/5345, MIC2290/2291/2297, LM3503, LT3465A/3466/3491, MAX1561/1599, RT4532, MP3306/3309C, NCP5007, AW9961, TPS61150A and the non-B AP3036.

**AP3036BKTR-G1 in short.** SOT-23-6, pins 1 CTRL, 2 VOUT, 3 VIN, 4 SW, 5 GND, 6 FB (Diodes DS37004). It works with R37, L2, C9, C12 and the existing firmware sequence. What it costs:
- **Sleep.** It draws 45 µA typ / 75 µA max in shutdown from LDO_IN, which is always on. The sleep floor rises from about 58 µA to about 103 µA typ: +1.1 mAh/day. This fails R28.
- **OVP.** About 29.5 V with no guaranteed limits, which is above SMAJ26A's 28.9 V. On AP3036B boards D3 must become **SMAJ28A (C19077545, JLC Preferred)**. Never SMAJ33A: its breakdown reaches 40.6 V, above the AP3036B's 38 V SW abs max. Keep SMAJ26A on TPS923610 boards, because SMAJ28A's 34.4 V maximum breakdown is above the TPS923610's 32 V abs max.
- **Dimming.** At 25 kHz the lowest one or two steps (perhaps up to six) are dark. The floor is somewhere between a few tens of µA and about 0.7 mA. It needs a firmware minimum duty set on the bench.
- **Smaller costs.** LED current ±6 % (12.5-14.1 mA). 3.1 mA quiescent while lit. The datasheet circuit uses 22 µH and 0.22 µF, so 10 µH and C9 need a stability check. Max duty is 90 % min against about 88 % needed. After an open-load trip LED_SW sits near 29.5 V, so `RAIL_WAIT_MAX_US` should rise to 5 s.
- **Upside.** It is hand-solderable, a single part, cheaper ($0.17-0.22), and deeper in stock.

The AP3036B remains the fallback if TPS61160 stock disappears (§9).

---

## 4. Study 2: boost IC plus the B5819W

**Search.** JLC's "LED Drivers" list sorted by stock (1,000 rows, 176 boost parts), then every known family, including OVP and FB variant suffixes. No boost white-LED driver is JLC Basic or Preferred; all are Extended, like U10. An alternate build that leaves U10 empty therefore adds no Extended fee.

The B5819W (40 V VRRM, 1.5 A IFRM) fits every candidate with at least about 8 V of reverse margin.

| Part (maker) | LCSC | Stock LCSC / JLC | FB | OVP vs D3 | Shutdown | Open load | Price 1+ / 100+ | Verdict |
|---|---|---|---|---|---|---|---|---|
| **TPS61160DRVR (TI)** | **C165143** | **9,827 / 9,834** | 196/200/204 mV | **25/26/27 V on SW, guaranteed; below D3** | **≤ 1 µA** | latches off; CTRL LOW ≥ 2.5 ms clears it | $0.461 / $0.258 | **Recommended** |
| MT9201 (Aerosemi) | C182966 | 25,815 / 25,815 | 194/200/206 mV | 28 V typ only, 0.9 V under D3; SW abs max 30 V | 1 µA max | clamps near 28 V, no latch | $0.121 / $0.088 | runner-up (§9) |
| MSAP3032KTR-G1 (MSKSEMI) | C49208388 | 2,110 / 2,112 | same die as MT9201 | as MT9201 | 1 µA | as MT9201 | $0.158 / $0.125 | MT9201 second source |
| MP3202DJ-LF-Z-MS (MSKSEMI) | C52988868 | 2,885 / 2,885 | same die as MT9201 | as MT9201 | 1 µA | as MT9201 | $0.56 | second source; **not** the MPS MP3202 |
| ME2214AM6G (Microne) | C2925759 | 1,730 / 1,733 | 190/200/210 mV | 23/26/30 V: crosses the 23.3 V probe level and D3 | 1/3/5 µA | clamps | $0.139 / $0.110 | fallback only, with a per-board clamp screen |
| LN2120B020MR-G (Natlinear) | C6705236 | 3,000 | 190/200/210 mV | 24 V typ; LX abs max 26 V | ≤ 1 µA | – | $0.105 | reject: Dmax 86 % min |
| AP3032KTR-G1 (Diodes) | C264086 | 19,145 | 188/200/212 mV | 27 V typ | **50 µA** | clamp | $0.25 | reject: sleep current |
| STI9287C (TMI) | C2985059 | 6,355 | 192/200/208 mV | **30 V typ**, above D3 | 0.1/1 µA | clamp | $0.09 | reject: D3 takes 3.5-6.1 W until the firmware trips |
| SY7200AABC / SY7201ABC (Silergy) | C107309 / C82173 | 174k / 29k | 200 mV | 28-33 V | 10-15 µA | – | $0.21 / $0.27 | reject: shutdown current, OVP, 2-3.5 A limit |
| ETA1617S2G (ETA) | C7465515 | 7,895 | 194/200/206 mV | **33 V**, above D3 | – | latches, but D3 clamps first | $0.17 | reject |
| AP3031, RT9284A-20 | C82636 / C250540 | up to 25k | – | 17.5 / 20 V, below the strings | – | – | – | reject |
| MT9284, RY3730, LP3310/LP3320B, AP3127B, MPS MP3202, AP5724, TPS61040/41 clones, RT9293B, BCT3660C | various | up to 72k | 104-300 mV, 1.233 V or none | – | – | – | – | reject: FB or topology |
| TPS61161/65/69, SGM3732/3756/3766, DIO5661, BCT3692B, AW9967, MP3302, UM1663S, SGM3752, AP3128A, RS3750, TPS61042 | various | up to 33k | about 200 mV | 30-40 V, above D3 | – | – | – | reject |
| SGM3733, RT9285B, MP3309, TPS61160ADRVR (C702281) | – | 0-91 | – | – | – | – | – | reject: stock |

**Why "OVP above D3, let the firmware end it" was not accepted as a design basis.** With an OVP of 30-33 V, D3 clamps every open load while the boost runs at its current limit: about 2.1-4.8 W for ETA1617, 3.5-6.1 W for STI9287C, and 4.8-8.5 W for an MT9201 unit whose OVP lands above D3. Each event is short (0.1-0.4 J in the 500 ms probe window), but a firmware hang that does not reset the chip leaves several watts on a part rated about 1 W steady. With an in-window part available, there is no reason to accept that.

---

## 5. Recommended alternate: TPS61160DRVR + B5819W + 220 nF

### 5.1 Electrical fit

All limits are from TI SLVS791E (July 2016).

| Requirement | TPS61160DRVR |
|---|---|
| FB | 196/200/204 mV. With R37 = 15 Ω ±1 %: **12.94-13.74 mA**, under the panel's 15 mA. FB bias 2 µA × 15 Ω = 30 µV |
| OVP | 25/26/27 V measured on SW. It **latches off** after 8 cycles; CTRL LOW for ≥ 2.5 ms clears it, and the existing 3 ms dark dwell does that |
| LED_SW at the latch | 24.6-27.1 V at switch-on. Plan on about 23.8 V at the low end, for ringing on the 18 mm hot loop. 28.1 V worst case if a string is pulled out while lit at full current. All below D3's 28.9 V, so **D3 stays SMAJ26A** |
| Shutdown current | ≤ 1 µA. The sleep floor rises by about 1 µA at most |
| VIN | 2.7-18 V operating, 20 V abs max, UVLO 2.5 V max falling |
| Switch current limit | 0.56/0.70/0.84 A (0.4 A for the first 5 ms), below L2's 1.0 A Isat. The TPS923610's is 1.6-2.1 A |
| Inductor peaks | 0.32-0.40 A nominal, 0.51 A worst (20 mA from 3.0 V, 8 µH, 500 kHz) |
| Dimming | CTRL takes the 25 kHz PWM (rated 5-100 kHz) and turns it into an analog reference, VFB = duty × 200 mV: the same scheme as the TPS923610's ADIM. Internal 400-1600 kΩ pull-down |
| Max duty | 93 % min |
| B5819W | ≤ 28.1 V against 40 V VRRM; ≤ 0.84 A against 1.5 A IFRM; about 10-15 mW of loss |
| Lit quiescent current | 1.8 mA |

### 5.2 Parts

DigiKey MPN is the primary field; LCSC is an extra field.

| Ref | Value | MPN (primary) | Manufacturer | LCSC | JLC class | KiCad footprint |
|---|---|---|---|---|---|---|
| **U15** | TPS61160DRVR | TPS61160DRVR | Texas Instruments | **C165143** | Extended | `Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` |
| **D7** | B5819W | 1N5819HW-7-F (as D4-D6) | Diodes Incorporated | **C8598** (JSCJ B5819W SL) | Basic | `Diode_SMD:D_SOD-123` |
| **C35** | 220n | CL05B224KO5NNNC (16 V X7R) | Samsung Electro-Mechanics | **C16772** | Basic | `Capacitor_SMD:C_0402_1005Metric` |
| C38 (optional, only if it fits) | 1u | CL05A105KA5NQNC (25 V) | Samsung Electro-Mechanics | C52923 | Basic | `Capacitor_SMD:C_0402_1005Metric` |

- **Package.** WSON-6 (TI DRV0006A), 0.65 mm pitch, exposed pad 1.0 × 1.6 mm, marking BZQ, MSL 2. Reflow only; a hand build needs hot air or a hotplate.
- **C35 is 0402** because an 0603 does not fit between R4 and L2. It would be the board's first 0402. TI recommends 220 nF on COMP for most applications. Do not use 1 µF: it slews COMP about 4.5 times slower, which delays light-up and the open-load latch. 0.1 µF is untested.
- **0402 vs the board's 0603 rule.** Every other passive is 0603 or larger, and `R84` was made 0603 rather than 0402 on 2026-10-01 for that reason. The alternate is JLC-assembled only, so an 0402 there is buildable, but it is the one exception to the rule (C38 would be a second). Keeping to 0603 means re-placing C35 (and C38) elsewhere on the COMP and VIN nets; that layout was not studied.
- **DigiKey.** TPS61160DRVR, cut tape 296-22942-1-ND, about $1.35 at quantity 1 (not checked against the live page).
- **JLC footprint.** EasyEDA's `WSON-6_L2.0-W2.0-P0.65-TL-EP` has pin 1 top-left, the same as KiCad's, so no FT Rotation Offset is expected.

### 5.3 Pin map

| U15 pin | Function | Net | U10 pin today |
|---|---|---|---|
| 1 | FB | Net-(Q5-S) (top of R37) | 3 FB |
| 2 | COMP | new net `LED_COMP` → C35 → GND | – |
| 3 + EP | GND | GND | 4 GND |
| 4 | SW | TPS_SW_NODE (L2.2) | 6 SW |
| 5 | CTRL | PWM_LED (IO42) | 2 ADIM |
| 6 | VIN | LDO_IN | 1 VIN |
| D7 A / K | rectifier | TPS_SW_NODE / LED_SW | (U10's synchronous FET) |

### 5.4 Schematic

- Add U15, D7 and C35 next to U10 on the nets above. All three designators are free.
- **Symbol.** KiCad's own if the Driver_LED library has a TPS61160; otherwise import the EasyEDA symbol for C165143 into the project-local library, as for U14, or draw a 7-pin symbol (pins 1-6 plus EP as pin 7, GND).
- **Flags.** DNP = yes and Exclude from BOM = yes, with Exclude from position files = no. That matches U14.
- **Sheet note:** "U15 + D7 + C35 = alternate to U10. Fit U10 OR U15+D7+C35, never both (both SW pins share L2). Alternate build: U10 DNP, U15/D7/C35 fitted, D3 unchanged (SMAJ26A), firmware with MIN_DUTY ≥ 3 LSB and decay probe; paste removed from the empty land."
- **`fabrication/part_fields.csv` rows:**
  ```
  U15,TPS61160DRVR,TPS61160DRVR,Texas Instruments,C165143,yes,Texas Instruments TPS61160DRVR,"same part; DNP alternate to U10 (TPS923610) with D7 and C35 - fit U10 OR U15+D7+C35, never both. Alternate build needs firmware MIN_DUTY >= 3 LSB and the decay probe."
  D7,B5819W,1N5819HW-7-F,Diodes Incorporated,C8598,yes,"Jiangsu Changjing Electronics Technology Co., Ltd. B5819W SL","equivalent (JCET B5819W); same part as D4-D6; U15 rectifier, DNP in the standard build"
  C35,220n,CL05B224KO5NNNC,Samsung Electro-Mechanics,C16772,yes,Samsung Electro-Mechanics CL05B224KO5NNNC,"same part; U15 COMP capacitor (TI 220 nF), 0402 because 0603 does not fit between R4 and L2; DNP in the standard build"
  ```

### 5.5 Placement and routing

This layout was built and DRC-checked on a scripted copy of commit `5809233`. Coordinates are KiCad board mm, y down, all parts on B.Cu. If the area around U10 has changed since, re-derive them.

**Why here.** A free-space scan of B.Cu around U10 (all pads, tracks and vias plus 0.2 mm clearance) found exactly one patch within 8 mm that takes a driver land: directly above L2, bounded by the antenna-notch board edge (y ≈ 113.5), the BUTTON_ADC_1 via (48.3, 113.7), the 3V3 via (49.5, 114.6) and the LED_SW run along y = 117.1. The other patches put SW 6 mm or more from L2.

**Placement.** Do not nudge: the courtyard gaps are 0.02-0.16 mm.

| Ref | Centre (x, y) | Rotation | Key pads |
|---|---|---|---|
| U15 | (47.45, 114.60) | 180 | 1 FB (48.34, 113.95); 2 COMP (48.34, 114.60); 3 GND (48.34, 115.25); 4 SW (46.56, 115.25); 5 CTRL (46.56, 114.60); 6 VIN (46.56, 113.95); EP (47.45, 114.60) |
| D7 | (46.05, 118.45) | 90 (as D4) | K, pad 1 (46.05, 120.10), LED_SW; A, pad 2 (46.05, 116.80), TPS_SW_NODE |
| C35 | (48.55, 116.85) | 180 | pad 1 (49.03, 116.85), COMP; pad 2 (48.07, 116.85), GND |

Tightest courtyard margins: D7 to C9 0.017 mm, D7 to L2 0.06 mm, U15 to D7 0.16 mm.

**Delete (14 items).**
- LED_SW B.Cu top run, 6 segments: (46.48, 121.86) → (46.48, 118.02) → (47.40, 117.10) → (52.60, 117.10) → (53.66, 118.16) → (54.66, 118.16) → (55.50, 119.00). R39.1 keeps LED_SW through the existing (54.94, 119.56) → via (54.94, 120.00).
- GND via (47.20, 120.50).
- BUTTON_ADC_1:
  - vias (48.30, 113.70) and (45.10, 118.00);
  - F.Cu (48.30, 113.70) → (45.10, 116.90) → (45.10, 118.00). This diagonal would split the F.Cu ground under the new IC;
  - B.Cu (50.50, 113.61) → (48.39, 113.61) → (48.30, 113.70);
  - B.Cu (45.10, 118.00) → (45.00, 118.10).

**Add (8 new vias, 0.6/0.3 mm).**
- **SW (B.Cu, no vias):** U15.4 → (46.45, 115.60) at 0.25 mm → (46.30, 116.60) at 0.4 mm into D7's anode; anode → (46.75, 116.80) → (47.75, 117.80) → (47.75, 118.50) into L2.2 at 0.4 mm.
- **D7 cathode (B.Cu 0.3 mm):** (46.05, 120.10) → (46.05, 120.70) → (46.35, 121.00) → (46.35, 121.40) into C9.2.
- **LED_SW link:** new via V1 (47.25, 120.75) with a B.Cu stub into C9.2; F.Cu 0.2 mm (47.85, 120.15) → (54.79, 120.15) → existing via (54.94, 120.00). The C9-to-J3 path drops from about 16 mm to about 9 mm.
- **GND:** EP → new via (47.45, 116.10); C9.1 → new via (47.75, 123.60) for the loop return; C35.2 → (47.45, 116.10).
- **COMP (B.Cu 0.2 mm):** U15.2 → (48.85, 114.60) → (48.85, 116.75) → C35.1.
- **VIN:** U15.6 → via (45.60, 113.90); F.Cu 0.25 mm (48.30, 113.90) → (48.30, 117.00) → (48.55, 117.25) → (51.45, 117.25) → existing LDO_IN via (52.00, 117.80).
- **CTRL:** U15.5 → via (45.60, 114.75); F.Cu (45.35, 115.00) → (45.35, 124.20) → (51.15, 124.20) → via (51.60, 122.75); B.Cu stub to the PWM_LED track at (51.60, 122.20).
- **FB:** U15.1 → via (49.00, 113.60); F.Cu (48.60, 113.20) → (45.30, 113.20) → (44.95, 113.55) → (44.95, 124.35) → (45.30, 124.70) → (48.60, 124.70) → (49.00, 125.10) → via (49.00, 126.50) on the Net-(Q5-S) run between R37.1 and Q6.2.
- **BUTTON_ADC_1 (B.Cu 0.2 mm, no vias):** R4.1 → (49.65, 112.75) → (45.15, 112.75) → (44.90, 113.00) → (44.90, 117.85) → (45.00, 118.10).

**DRC.** Against an unmodified copy: 0 new errors and 0 new unconnected items. Five new silkscreen warnings (the C35 and D7 reference texts, and D7's silk touching U10's reference) need the texts moved. One existing warning (R41.2 starved thermal) clears.

One custom rule is needed, because TPS_SW_NODE is in a 0.25 mm-clearance class but the WSON's lead-to-EP gap is 0.20 mm. Add it in Board Setup → Custom Rules:
```
(version 1)
(rule "U15 WSON lead-to-EP (land pattern gap 0.20 mm)"
  (condition "A.memberOfFootprint('U15') && B.memberOfFootprint('U15')")
  (constraint clearance (min 0.2mm)))
```

Margins to watch:
- BUTTON_ADC_1 runs 0.50 mm from the board edge (rule 0.475 mm);
- it also runs 0.15 mm outside the U4 antenna keepout, where the GND pour already reaches;
- re-run DRC with schematic parity after Update PCB.

### 5.6 Layout compromises

- **Hot loop (SW → D7 → C9 → GND).** The forward path is about 8.8 mm on B.Cu, with the return about 9.5 mm on solid F.Cu directly underneath. That is about 15 mm² and 5-8 nH, against about 2.5 mm² for U10 today. Expect 0.5-0.8 V of extra SW overshoot. A local high-frequency output capacitor would not help, because the IC's GND is at the far end of the loop.
- **VIN decoupling.** U15.6 reaches C12 through about 12 mm of 0.25 mm track and two vias. TI wants the input capacitor close to VIN and GND, so this is not met. Try to fit C38 (1 µF 0402) between U15.6 and GND; only about 0.56 mm is free above U15, so it may not fit. If it does not, VIN ripple at 3.0 V becomes a bench gate (§7). UVLO is 2.5 V max falling, so a few hundred mV of dip at 3.0 V still clears it.
- **Antenna.** U15 and the SW node sit about 1-3 mm from the U4 antenna keepout, against about 5.5 mm today. Check Wi-Fi/BLE RSSI with the light on.
- **Thermal.** No vias in the EP, one beside it. Loss is about 20-35 mW (+2-3 °C), which is acceptable.
- **Standard build (U15/D7/C35 empty).** The SW node gains about 2.7 mm² of copper (3.6 → 6.3 mm²) and about 0.1-0.3 pF. The empty FB, CTRL and VIN stubs sit on low-impedance or DC nodes. Electrically negligible.

### 5.7 Solder paste on the empty land (must be suppressed)

**Finding.** The production `B_Paste` Gerber has apertures on DNP footprints: there are flashes at the DNP U14 pads (64.5, 116.7) and (63.2, 119.4) and at the DNP R43 pad (98.91, 137.2). The Fabrication Toolkit's DNP exclusion drops BOM and CPL rows only; it does not touch the paste layer. JLC cuts the stencil from that file.

**Why it matters here:**
- **Standard build, empty U15.** The SW pad is 0.20 mm from the GND pad. A bridge puts L2 (0.45 Ω) straight across LDO_IN to GND; the DW01A or the source trips and the board does not run.
- **Alternate build, empty U10 (SOT-563, 0.5 mm pitch).** Paste can bridge SW-VOUT or VOUT-GND. LED_SW to GND is a VIN → L2 → D7 → GND path limited only by resistance.

**Fix:**
1. Give the empty-side driver footprints a solder-paste override that removes their apertures: Footprint Properties → Clearance overrides → solder paste relative clearance −100 %. Standard build: U15, D7, C35. Alternate build: U10 only, with U15/D7/C35 back to the default.
2. Plot each build's own Gerber zip. The copper is identical; only the paste layer differs.
3. Verify on the plotted `B_Paste` layer in GerbView that the empty land has no apertures. Do not assume the override works without looking.

**Today's board.** U14 (RV-8263 SON-8, 0.9 mm pitch) has the same exposure: 0.25 mm pad gaps with SCL-SDA adjacent (pads 7-8) and SCL-GND across 0.35 mm (pads 7-2). It is lower risk than a WSON SW pad, but on Rev 1.0 boards inspect U14's empty land and meter SCL-SDA (expect about 4.4 kΩ through the two 2.2 kΩ pull-ups, not 0 Ω) and SCL-GND. If more alternates with tight pads are added, use the per-build paste control above on all of them.

### 5.8 JLC CPL

The Fabrication Toolkit writes bottom-side rotation as (180 − board rotation) mod 360. So U15 at 180 → CPL 0, D7 at 90 → CPL 90 (as D4), C35 at 180 → CPL 0. DNP parts are left out of `positions.csv`, so U15/D7/C35 appear only in the alternate build's regenerated CPL.

In JLC's placement preview, check:
- U15's pin-1 dot is on the FB pad, the corner at (48.34, 113.95);
- D7's cathode bar is toward C9 (pad 1 at y 120.10);
- C35 shows as 0402;
- U10 is not placed and D3 is still C19077543;
- the stencil preview has no paste on the empty land.

### 5.9 Value changes: none

| Part | Change | Why |
|---|---|---|
| R37 15 Ω | none | 12.94-13.74 mA worst case including R37 ±1 % |
| L2 10 µH | none (bench stability) | TI recommends 10-22 µH, so L2 is at the bottom edge. Peaks stay under ILIM min (0.56 A) and Isat (1.0 A) |
| C9 4.7 µF/50 V | none | TI range 0.47-10 µF; about 1-2 µF effective at 22-27 V; 50 V against ≤ 28.1 V |
| C12 4.7 µF | none | TI asks for 1 µF; the distance is the issue, not the value (§5.6) |
| D3 SMAJ26A | none | the latch sits under D3's 28.9 V minimum; D3 stays the clamp if the latch does not fire at deep dim (§8) |
| R39/R41, Q5/Q6 | none | – |

### 5.10 Firmware changes

These are proposals; line numbers refer to firmware commit `5d58fdc0`. No hardware strap tells the firmware which driver is fitted.

**Mandatory 1: minimum duty.**
- **Why.** 1 LSB is a 25 or 50 ns pulse, and TI's minimum CTRL pulse is 50 ns (`tPWM_MIN`). Missed pulses can shut the part down (CTRL LOW ≥ 2.5 ms) or, after a restart, select EasyScale one-wire mode at full scale (CTRL LOW > 260 µs inside the 1 ms detection window). The light would then come on at full brightness at the dimmest setting.
- **Pulse widths.** 2 LSB = 75-100 ns (absolute minimum); 3 LSB = 100-125 ns.
- **Change.** Add `FrontlightConfig::minDutyLsb` (default 1, today's behaviour). Remap non-zero duty onto [k, 1023] rather than clamping: in `perceptualDuty()` (`FrontlightManager.cpp` L45-50), duty = k + round((1023 − k) × GAMMA[pct] / 65535) for pct ≥ 1, and the same in the 0-255 level API. With k = 3 the first steps are 3, 5, 6, 8 LSB …, all distinct and monotonic. **Ship k = 3 for the TPS61160.**

**Mandatory 2: decay-based open-load detection** in `probeTick` (`FrontlightManager.cpp` L729-751).
- **Why.** The TPS61160 latches and does not retry. LED_SW then decays through R39 + R41 and the B5819W's reverse leakage. The 23 V level trip misses an open string at the OVP-min corner, with low effective C9, on a warm board (diode leakage about 0.11 mA at 75 °C), or when ringing latches it near 23.8 V; peak readings in those corners are only 20.7-22.9 V. The result is benign (dark driver, cold D3), but the colour fallback does not run and test T10 step 0 fails.
- **Rule.** After at least 3 readings, if the peak is ≥ 18 V and a reading is ≤ peak − 1.0 V at unchanged duty, call `probeTripped()`. Reset the peak on any duty change (applyGated L505-511), because dimming moves a string's Vf by 1-2.5 V. A lit string stays flat to within about 0.2 V; a latched rail falls 7-33 V/s, so it trips in about 30-150 ms, inside the 500 ms window.
- **Where.** `FrontlightLoad.h`, with host tests. It is harmless on the TPS923610 and also covers that part's own OVP-min corner. Keep the 23 V level trip; it is the protection at the deep-dim floor.

**Not required:**
- **Enable pulse.** Keep `enablePulseUs = 150`. `lightUp()` programs the carrier duty while the GPIO still holds the pad HIGH and then hands the pad to LEDC (L579-590), so no long LOW follows the pulse, and with k ≥ 2-3 every LOW is ≤ 40 µs, far below the 260 µs EasyScale detection time. A 1.2-1.5 ms pulse is optional hardening, decided on the bench (§7, items 8-9); it may cause a brief blip at switch-on at deep dim.
- **No change to** 25 kHz / 10 bit, the 3 ms dark dwell (> 2.5 ms toff, so every enable is a clean restart with a 6.8 ms soft start), the 23 V trip and its `static_assert(< 24250)` (which still guards the TPS923610), the 500 ms / 20 ms probe, or `railSafeV` 15.
- **Rail wait.** `RAIL_WAIT_MAX_US` = 4 s still holds: from 27.1 V the fall to 15 V takes 3.1 s at C9's nameplate 4.7 µF, 3.3 s from 28.1 V, and less at the real effective value. 5 s is harmless if one value should cover every driver (the AP3036B needs it).

**One build for both drivers.**
- Add `-DSILKSCREEN_FRONTLIGHT_DRIVER=tps923610|tps61160|any`, following the `#ifndef SILKSCREEN_FRONTLIGHT_TRIP_MV` pattern in `BoardConfig.h`.
- Make **`any`** (k = 3, decay rule on, 150 µs pulse) the release default. It is safe on both drivers; TPS923610 boards lose only the 13 and 26 µA steps.
- An NVS override set at test T10 step 0 can restore k = 1 on TPS923610 boards.
- Auto-detection is not recommended: it needs a pull-up on IO42 and 1-2 ms of unloaded boost.

**Comments and docs to update when implementing:**
- Firmware comments: `BoardConfig.h` L2244-2258 and the profile text at L2378-2390; `FrontlightManager.cpp` L148-158; `LightCheck.h` L20; `platformio.ini` L455-470.
- Firmware docs: REQUIREMENTS.md L18, L43, L187, L191, L198; POWER.md L47; PORTING.md L87, L118, L120; TEST-SUITE.md L142, L414, L453 (add the TPS61160 answer to T10 step 0).
- [HARDWARE.md](HARDWARE.md) §13.1: the alternate's contract. Open-LED shutdown latches with no retry and CTRL LOW ≥ 2.5 ms clears it; FB/COMP abs max is 3 V; minimum duty is at least 3 LSB; sleep +≤ 1.3 µA; lit quiescent current 1.8 mA.

### 5.11 BOM and builds

**Standard build.** Nothing new to order. The toolkit writes DNP lines:
```
TPS61160DRVR  DNP (standard build),U15,WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm,
B5819W  DNP (standard build),D7,D_SOD-123,
220n  DNP (standard build),C35,C_0402_1005Metric,
```

**Alternate build.** On a branch, flip the DNP flags and the paste overrides, then regenerate BOM, CPL and Gerbers.

| Comment | Designator | Footprint | JLCPCB Part # |
|---|---|---|---|
| TPS923610DRLR  DNP (alternate build) | U10 | SOT-563-6 | – |
| TPS61160DRVR | U15 | WSON-6-EP(2x2) | C165143 |
| B5819W | D4, D5, D6, D7 | SOD-123 | C8598 |
| 220n | C35 | 0402 | C16772 |
| 1u (only if fitted) | C38 | 0402 | C52923 |
| SMAJ26A (unchanged) | D3 | SMAG | C19077543 |

DigiKey hand build: TPS61160DRVR (about $1.35 at 1), 4 × 1N5819HW-7-F, 1 × 220 nF 0402.

### 5.12 Cost (JLC prices, 2026-10-01)

| Per board, alternate build | 5 boards | 25 boards | 125 boards |
|---|---|---|---|
| U15 TPS61160DRVR | $0.4569 | $0.3544 | $0.2553 |
| D7 B5819W | $0.0280 | $0.0280 | $0.0218 |
| C35 220 nF | $0.0051 | $0.0051 | $0.0051 |
| **Driver parts per board** | **$0.490** | **$0.388** | **$0.282** |
| Against the TPS923610 (about $0.53) | −$0.04 | −$0.14 | −$0.25 |

- **JLC Extended fee:** U15 replaces U10 (both Extended), so the net change is $0. D7 and C35 are Basic. JLC may add a few attrition pieces of U15.
- **Optional C38:** +$0.0099 per board.

---

## 6. Comparison of the two alternates

| | **TPS61160 + B5819W + 220 nF** | AP3036BKTR-G1 |
|---|---|---|
| Alternate-build changes | U10 DNP; U15, D7, C35 fitted (3 placements) | U10 DNP; U15 fitted; **D3 → SMAJ28A** |
| New part numbers | TPS61160DRVR, 220 nF 0402 | AP3036BKTR-G1, SMAJ28A |
| Stock (2026-10-01) | 9,827 / 9,834; single source (TI); A-variant only 91 | 20,380 / 20,384 |
| Price per board | $0.28-0.49 incl. diode and capacitor | $0.17-0.22 |
| JLC fee | $0 net | $0 net (SMAJ28A is Preferred) |
| **Sleep (shutdown)** | **≤ 1 µA → floor about 58 µA** | 45 µA typ / 75 µA max → about 103 µA typ (**fails R28**) |
| **OVP vs D3** | **25-27 V on SW, guaranteed, latching; D3 stays SMAJ26A** | about 29.5 V typ clamp, no limits; needs SMAJ28A |
| Dimming floor | 26-39 µA nominal (2-3 LSB); not guaranteed below 10 % duty | 1-2 LSB dark; floor from tens of µA to about 0.7 mA |
| LED current tolerance | ±2 % (12.9-13.7 mA) | ±6 % (12.5-14.1 mA) |
| Lit quiescent current | 1.8 mA | 3.1 mA |
| Current limit vs L2 Isat 1.0 A | 0.56-0.84 A | 550 mA typ |
| Open load | latches; 3 ms dark clears it; probe needs the decay rule | clamps, no latch; firmware ends it |
| Cut-down board (no D3) | latch keeps LED_SW ≤ 28.1 V, but **not guaranteed at the deep-dim floor** (§8) | clamps itself at about 29.5 V (SW abs max 38 V) |
| Firmware | MIN_DUTY 3 LSB + decay rule (both mandatory) | MIN_DUTY 3-30 LSB (bench) + rail wait 5 s |
| Layout | DRC-clean reference (§5.5); also changes standard-build copper; 18 mm hot loop | one SOT-23-6 in the same patch, top LED_SW run moved to F.Cu; never DRC'd |
| Package | WSON-6 2×2 with EP, reflow only | SOT-23-6, hand-solderable |
| Hard requirements failed | none (dimming floor is soft) | sleep current; OVP window unless D3 changes |
| Verdict | **Recommended** | fallback if TPS61160 stock disappears |

Both use the same free patch above L2 and are not pin-compatible, so a board can carry only one of them. Switching later means a new land.

---

## 7. Decisions and checks before relying on it

**Decisions:**
1. Accept three placements and the standard-build copper changes: LED_SW detour off B.Cu, BUTTON_ADC_1 on the board edge, GND via (47.20, 120.50) removed.
2. Accept a dimming floor of 39 µA at 3 LSB, against 13-20 µA on TPS923610 boards.
3. Firmware: accept the two mandatory changes, and choose the `any` default or a per-driver flag.
4. Cut-down board (no D3): do not fit the TPS61160 alternate on it until bench item 6 shows that it latches at MIN_DUTY on every unit tested (§8).
5. Paste: per-build paste overrides and two Gerber zips (§5.7).
6. Package size: accept 0402 for C35 (and C38) as a JLC-only exception, or find 0603 room for them (§5.2).

**KiCad:**
1. Place and route per §5.5; try to fit C38 at U15.6.
2. Add the custom DRC rule and move the silkscreen texts.
3. Run DRC with schematic parity.
4. Check the plotted `B_Paste` layer has no apertures on the empty land, in each build.

**Bench checks on the first alternate boards** (scope on SW, LED_SW and CTRL; µA meter):
1. **Before power-up:** LDO_IN-GND and TPS_SW_NODE-GND are not shorted (no paste bridge).
2. **Sleep and boot:** at 3.7 V with IO42 LOW, sleep current is the standard board's +≤ 1.3 µA. The light stays off with IO42 floating, through reset and download mode.
3. **Full scale:** 12.9-13.7 mA. It must still regulate at 3.0 V into the 21.7 V strip (Dmax 93 % min).
4. **Stability with C35 = 220 nF and L2 = 10 µH:** at 3.0 V into the strip at full current, and at 5.0 V into the panel at MIN_DUTY. No subharmonic oscillation. SW peak in normal running below about 24 V (OVP min is 25 V on SW).
5. **VIN ripple** at 3.0 V input, full load, with the long VIN route. No UVLO dropouts. Skip if C38 fits.
6. **Open load** at 100 %, 10 % and MIN_DUTY, on 3-5 units: does it latch; LED_SW peak (expect 24-27 V); D3 temperature; probe verdict and time with the decay rule; rail fall to 15 V in under 4 s. At MIN_DUTY, if a unit does not latch, LED_SW climbs to D3 and the 23 V trip must end it within 40 ms.
7. **Dimming sweep at 2-10 LSB:** monotonic, no flicker from pulse skipping, no audible noise. Confirm MIN_DUTY = 3 or raise it.
8. **One-wire trap:** 10 switch-ons each at 1-3 % brightness, at 3.0, 4.2 and 5.0 V. None may start at full brightness.
9. **Warm-reset lock-up** (TI E2E thread 1064339, unresolved): 100 or more `esp_restart`, OTA, panic and watchdog resets with the light on at 1 %, 3 % and 100 %, with Restore Light on Wake on. The light must return every time; if it does not, try the 1.2-1.5 ms enable pulse.
10. **Radio:** Wi-Fi/BLE RSSI with the light on and off.
11. **Hot-plug after a failed switch-on:** FB stays under its 3 V abs max. Otherwise document "wait about 5 s after a failed switch-on before plugging in a light".

---

## 8. Uncertainties

**TPS61160:**
- **Dimming floor.** Guaranteed only at the 20 mV point (17-23 mV, about 10 % duty) and at 50 mV. If the ±3 mV were pure offset, the 2-3 LSB floor could land anywhere from 0 to about 220 µA, and a negative-offset unit's lowest steps would be dark. At the floor the part pulse-skips, which TI does not document.
- **Open-LED latch at deep dim.** The "FB below half the regulation voltage" condition is specified only at VREF = 200 mV and 20 mV, that is at 10 % duty or more (about 25 % on the brightness slider). At the 2-3 LSB floor the reference is 0.4-0.6 mV, below plausible comparator offset, so some units may not latch on an open string.
  - **Boards with D3:** D3 clamps at 1-2.7 W until the 23 V trip: 20-40 ms in the probe, up to about 120 ms in use. A firmware hang that does not reset the chip would overheat D3.
  - **Cut-down board without D3:** nothing in hardware limits LED_SW in that corner. Hence decision 4 in §7.
  - Holding CTRL HIGH for about 3 ms at switch-on, so the latch fires during soft start while the reference is high, might close this gap at the cost of a visible blip. Untested.
- **Latch level on LED_SW.** 24.62 V minimum by calculation; about 23.8-24.1 V allowing for ringing on the 18 mm loop. That assumes the SW comparator sees nanosecond spikes, which TI does not say. 23.8 V is the planning number.
- **E2E lock-up after warm resets** (TPS61160A at 12 V): unresolved, no root cause. LDO_IN never cycles while a cell is fitted.
- **FB/COMP abs max is 3 V,** against 5.5 V on the TPS923610's FB. Hot-plugging onto a charged LED_SW is untested.
- **Supply.** One source, 9.8k in stock; the A-variant had 91.

**B5819W:**
- The 12 µA leakage used is the typical curve value; JSCJ's limit is 1 mA max at 40 V (25 °C). A high-leakage unit decays C9 faster after a latch, which the decay rule covers. Not a safety issue.
- D3's breakdown tempco (about +0.1 %/°C) is assumed. The latch could touch a cold D3 only near −20 to −40 °C, which is harmless.

**Board and layout:**
- C9's effective capacitance (1-2 µF) is an estimate.
- The 0.5-0.8 V overshoot estimate depends on edge rates TI does not give.
- The DRC in §5.5 ran on a scripted copy whose footprints were not linked to the schematic. The real change goes through Update PCB plus DRC with parity.
- Whether a −100 % paste override removes the apertures entirely must be checked on the plotted layer.

**Search coverage.** A general-purpose boost with a built-in diode listed outside JLC's LED-driver category could have been missed (TPS61080/81 were found that way, and neither is a one-part swap). Broadchip BCT3662 was excluded on family grounds only; its datasheet did not download.

---

## 9. Fallbacks

**MT9201 (Aerosemi, LCSC C182966): 25.8k in stock, $0.12.** A true two-part fit with the B5819W, and the same die is sold as MSKSEMI MSAP3032KTR-G1 (C49208388) and MP3202DJ-LF-Z-MS (C52988868). Against it:
- its 28 V OVP is typical only, 0.9 V under D3 and about 1.6 V under its own 30 V SW abs max;
- its 2 A current limit has no maximum;
- EN needs a 100 kΩ pull-down;
- it clamps near 28 V with no latch, so only the firmware ends an open load;
- dimming below 10 % is not characterised (estimated 70-400 µA, or a 3-30 LSB dark band).

Use it only after measuring OVP on 10 or more units. It needs its own land and layout.

**AP3036BKTR-G1 (Diodes, LCSC C526368): one part, no diode.** Fails the sleep requirement (§3). If used:
- **Pins** 1 CTRL → PWM_LED, 2 VOUT → LED_SW, 3 VIN → LDO_IN, 4 SW → TPS_SW_NODE, 5 GND, 6 FB → Net-(Q5-S). KiCad `Package_TO_SOT_SMD:SOT-23-6`. JLC's footprint has pin 1 180° from KiCad's, so expect an FT Rotation Offset.
- **Placement:** the same patch above L2, about (47.2-48.0, 115.6-116.6). Pins 3 and 4 face L2, SW on the left over L2.2 and VIN on the right toward L2.1. Move the top LED_SW B.Cu run (46.48, 118.02) → (47.40, 117.10) → about (51.5, 117.10) to F.Cu with two vias, returning to B.Cu before x ≈ 51.7. Never DRC'd.
- **D3 = SMAJ28A** (R+O, C19077545) on AP3036B boards only.
- **Firmware:** `SILKSCREEN_FRONTLIGHT_MIN_DUTY` set from a bench sweep (expect 3 to about 30 LSB), and `RAIL_WAIT_MAX_US` 5 s.
- If the bench shows SW ringing toward 35 V (38 V abs max), add 0.22 µF/50 V at U15 VOUT, alternate build only.
- Its pin k+3 matches the AP3019AKTR-G1's pin k, so an AP3019A rotated 180° fits the same land; it needs a ≤ 2 kHz firmware build and dims far worse.

**Pin-compatible on U10 itself, small runs only.** TPS923611LSDRLR (250 pcs) with D3 = SMAJ33A keeps the sleep current and the deep dimming. It fails only the stock rule.

---

## 10. If the front light is redesigned

What this study suggests for a future layout:
- **Pick the primary driver for stock depth as well as fit.** The TPS92361x family is the best electrical match but has never had deep stock at LCSC.
- **Reserve the alternate's land from the start.** The only free patch near U10 sits beside the antenna keepout and gives an 18 mm hot loop and a 12 mm VIN route. Planned from the start, the alternate could share a tight SW/D/C9 loop and a local VIN capacitor.
- **Size D3 against both drivers.** SMAJ26A's 28.9 V minimum breakdown is what rejected most candidates. An OVP window of roughly 23-28 V is the target any driver must hit.
- **Plan per-build paste control** for every DNP footprint with tight pads.
- **Consider a driver-ID strap** (a resistor or pull on a spare pin) so the firmware does not need a build flag.

---

## Sources

- TI TPS61160/61, SLVS791E: https://www.ti.com/lit/ds/symlink/tps61160.pdf. Pin table p.4; abs max §6.1; recommended operating conditions §6.3; electrical characteristics §6.5; timing §6.6; soft start §7.3.1; open LED §7.3.2; dimming mode §7.3.4; shutdown and PWM dimming §7.4.1-7.4.2; COMP §8.2.1.2.4; layout §10.1.
- TI TPS923610, SNVSCN8A: https://www.ti.com/lit/ds/symlink/tps923610.pdf
- TI TPS61158, SLVSBR3A: https://www.ti.com/lit/ds/symlink/tps61158.pdf
- TI E2E thread 1064339 (TPS61160A warm-reset lock-up).
- Diodes AP3036B, DS37004 Rev 2-2: https://www.diodes.com/assets/Datasheets/AP3036B.pdf; AP3036/A app note AN1054: https://www.diodes.com/assets/App-Note-Files/AP3036-A-AN1.0-101125.pdf; AP3019A DS41298: https://www.diodes.com/datasheet/download/AP3019A.pdf
- JSCJ B5819W (C8598): https://datasheet.lcsc.com/datasheet/pdf/4ac2c059be7c462694ab0715ce987a85.pdf?productCode=C8598
- Samsung CL05B224KO5NNNC (C16772): https://datasheet.lcsc.com/datasheet/pdf/02336ea48ea44ca18c72517dd3cb7b47.pdf?productCode=C16772
- R+O SMAJ series (C19077545): https://datasheet.lcsc.com/datasheet/pdf/f3d2c9df3269749880b305befd579c39.pdf?productCode=C19077545
- TDK VLS252012HBX (C88532): https://datasheet.lcsc.com/datasheet/pdf/de422f385540fd5f1bb91cb97a2c323c.pdf?productCode=C88532
- MT9201 Rev1.0: https://datasheet.lcsc.com/datasheet/pdf/ccdd06ca714f54959542b2a6b3ca7d8e.pdf?productCode=C182966; ME2214 V03: https://datasheet.lcsc.com/datasheet/pdf/967a0c692e06b2a48366d78b1669578f.pdf?productCode=C2925759; MSAP3032: https://datasheet.lcsc.com/datasheet/pdf/ed02f8a7851665cf39b28f7ac311387c.pdf?productCode=C49208388
- LCSC and JLC part pages: https://www.lcsc.com/product-detail/C165143.html, https://www.lcsc.com/product-detail/C526368.html, https://jlcpcb.com/parts
- DigiKey: https://www.digikey.com/en/products/detail/texas-instruments/TPS61160DRVR/1769600, https://www.digikey.com/en/products/detail/diodes-incorporated/AP3036BKTR-G1/4470855
