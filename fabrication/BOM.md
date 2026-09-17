# Silkscreen — bills of materials

Two BOMs are maintained, both generated from the schematic netlist (2026-09-17, 179 references):

| BOM | Who it's for | File |
|---|---|---|
| **JLCPCB optimized (standard)** | anyone ordering assembled boards from JLCPCB — the cheapest *verified* parts at every position, checked against JLC's live library on 2026-09-17 | [`production/bom_JLC_upload_v4_optimized.csv`](../production/bom_JLC_upload_v4_optimized.csv) |
| JLCPCB brand-conservative | same population with the originally specified brands (Samsung 50 V caps, Littelfuse PTC, TECH PUBLIC SD05C, AO3419, cut-tape DS3231) — costs ≈ $1.50/board more | [`production/bom_JLC_upload_v3.csv`](../production/bom_JLC_upload_v3.csv) |
| **Hand-build (DigiKey-style)** | building one or a few boards yourself from easily found Western-distributor parts (GCT MEM2075 microSD, APEM switches, Hirose, TI, onsemi, ADI…) | [`BOM_handbuild_digikey.csv`](BOM_handbuild_digikey.csv) |

Population (all BOMs): **162 placed**, **10 DNP** (`TP3 TP4 TP5`, `R43 R45 R58 R66 R72 R74`, `SW6`), 7 bare-copper refs
(`H1–H5`, `TP1`, `TP2`). The DNP set is flagged in both the schematic and the board, so the Fabrication
Toolkit CPL agrees with the BOM. `U13` (DS3231MZ+) is populated and optional; `SW6` (APEM MJTP1243 BOOT button)
is DNP because USB-Serial-JTAG makes it unnecessary. Never fit `R73` and `R74` together.

Regenerate the CPL with the Fabrication Toolkit after any schematic/PCB change — it must contain the six
Fix 4 parts (`Q2 Q9 R79 R80 R81 R82`). The schematic carries no LCSC field, so these files are the source of
truth for part numbers; JLC's automatic matching is what put a reverse-mount LED on `D2` in the first order.

## What the optimized BOM changes, and why

Every part in the population was crawled on JLC (library type, stock, price tiers) and LCSC (attributes), and
every Extended part was searched for Basic/Preferred and cheaper same-spec alternates. JLC charges a loading fee
per **Extended** part type per order (no fee for **Basic** or **Preferred**), so at small quantities a
slightly dearer Basic part is often cheaper overall. Seven cost swaps survived review, plus two engineering
changes (`CR1`, `L2`) that came out of the same pass:

| Ref(s) | Was | **Now** | Why (verified 2026-09-17) |
|---|---|---|---|
| `U13` | DS3231MZ+ `C722467` cut tape, $3.53, **373 in stock** | **DS3231MZ+TRL `C107410`**, $2.44, 11k stock | identical ADI part on reel — **−$1.10/board**, removes a stock risk |
| `Q2 Q3 Q7 Q8` | AO3419 `C88053`, Extended, 2.4k stock | **AO3401A `C15127`**, **Basic**, 441k stock | same price; −30 V P-ch, 85 mΩ @ 2.5 V vs 140 mΩ, Vgs(th) ≈ −0.9 V — a drop-in improvement for these load switches; no feeder fee. **Change the schematic Value on Q2/Q3/Q7/Q8 to AO3401A when adopting** (same SOT-23 pinout) |
| `D4 D5 D6` | B5819W `C64885`, Extended | **B5819W SL `C8598`**, **Basic** | +$0.03/board on the part, −$1.50/order in fees — cheaper below ~55 boards, and a Basic part never needs a feeder |
| `D3` | SMAJ26A `C1509531`, Extended | **SMAJ26A `C19077543`**, **Preferred** (no fee) | $0.036 vs $0.054, 57k stock, same 26 V/400 W spec |
| `F1` | Littelfuse 0805L100WR `C80270` | **Brightking SMD0805B100TFT `C269106`** | 1 A hold / 1.95 A trip / 6 V max — the same numbers — at $0.033 vs $0.138 |
| `CR2 CR3` | SD05C TECH PUBLIC `C907858`, 4k stock | **SD05C-01FTG DOWO `C5299440`**, 99k stock | $0.025 vs $0.035; on 3V3 and P+ (≤4.2 V) a 5.0 V standoff has real margin, and the higher capacitance (60 pF) is irrelevant on a rail |
| `CR1` (VBUS) | SD05C-class, **5.0 V** standoff, SOD-323 | **SMF6.5CA `C19077501`** (hongjiacheng, **Preferred** — no fee, 1.75 M stock, $0.029), **SOD-123FL** | a USB-C source may legally sit at 5.5 V; "05" parts specify leakage only at 5.0 V and clones break down from 6 V. TI's TSD05C is genuinely rated ±5.5 V, but anything sold under an "05" name at LCSC is a 5.0 V part — prime and clone disagree on exactly the spec that matters. **SMFxx is a standardized ladder where the name is the spec**: every SMF6.5CA, official (Littelfuse) or clone, is 6.5 V standoff, V_BR 7.22–7.98 V, ≤11.2 V clamp @ 17.9 A (10/1000 µs), 200 W, bidirectional. 1 V of real margin over 5.5 V, clamp as low as TSD05C's, 40 JLC listings / 2.9 M pcs. **Needs CR1's footprint changed to `Diode_SMD:D_SMF`** (fits the same spot: 4.2 × 2.2 mm courtyard vs the present 4.1 × 1.9 mm hand-solder SOD-323) |
| `C11 C13–C17` | Samsung CL21A475KBQNNNE `C98192` | **Samwha CS2012X5R475K500NRE `C513770`** | 4.7 µF **50 V** X5R 0805 from a reputable maker, $0.045 vs $0.077, 209k stock |
| `L2` | **4.7 µH** TDK VLS252010HBU-4R7M `C413592` (schematic), 1.0k stock | **10 µH TDK VLS252012HBX-100M-1 `C88532`**, 20.7k stock, $0.068 | value change — see "L2: 4.7 µH → 10 µH" below. **Change the schematic Value to 10u and the MPN to match.** If L2 must stay 4.7 µH, use HBX-4R7M-1 `C88528` (what both earlier orders were built with: cheaper than HBU at every tier, 208 vs 274 mΩ, 2× the stock) |

Evaluated and **not** taken: TP4056 clones ($0.037 vs $0.146 — but the TOPPOWER original is a *Preferred* part with
no fee, and charge termination/thermal regulation of clones is unverified; the swap would actually add a fee at
small quantities); 74LVC1G04 clones (saves $0.02/board); a second, cheaper TPD4E1U06 type for the non-USB
positions (saves $0.16/board but adds a part type — only pays above ~10 boards); 2N7002 for the BSS138
positions (Basic, but its Vgs(th) can reach 2.5 V and Q9's detector must turn on at a 2.4 V cell); a 6.3 V 0603
22 µF Basic cap (wrong footprint, and `C4` sits on 5 V). The CCTC 22 µF (`C20416420`) stays: it is $0.12 —
not the $0.04 the earlier sheet claimed — but still beats the Samsung Basic part at $0.24 even after its fee.

**Stock to watch (JLC, 2026-09-17):** TPS923610DRLR `C52919131` **189 pcs** — order promptly or consign;
A2541HWR-2x6P `C5333437` 1.2k; IRLML6346TRPBF `C67276` 5.7k; USB4085-GF-A `C7095263` 4.4k.

### L2: 4.7 µH → 10 µH

The TPS923610 is a peak-current-mode, internally compensated boost that runs **forced-continuous at 1.1 MHz at
every load** (datasheet §7.3.4/§7.4.1). Its ripple current therefore does not shrink when the LEDs are dimmed,
and TI sizes L to keep that ripple small: **every** 1.1 MHz characterization in the datasheet — efficiency vs
dimming, FB accuracy from 0.1–100 %, dimming transient, start-up — is taken with **10 µH and 1 µF** (this board's
`C9` is already 1 µF). 4.7 µH is not prohibited, but it is outside what TI characterized, and it doubles the
inductor slopes that the fixed internal slope compensation has to cover at this board's 75–80 % duty.

Loss model at 3.7 V in / 15 V out, using **TDK's measured Rac(f)** for each part (harmonics to 7.7 MHz), TI's
typical FET resistances, and the same fixed switching loss for all options:

| | ripple p-p | core/AC | copper | FET | battery draw @ 13.3 mA / 6.6 / 3.0 / 1.3 mA LED |
|---|--:|--:|--:|--:|---|
| 4.7 µH HBX-4R7M-1 (as built) | 0.60 A | 21 mW | 7 mW | 12 mW | 68.9 / 40.9 / 25.9 / 18.9 mA |
| 4.7 µH HBU-4R7M | 0.54 A | 20 mW | 8 mW | 10 mW | 68.1 / 40.1 / 25.1 / 18.1 mA |
| **10 µH VLS252012HBX-100M-1** | 0.27 A | 9 mW | 4 mW | 3 mW | **62.4 / 34.3 / 19.3 / 12.3 mA** |
| 10 µH VLS252010HBU-100M (1.0 mm) | 0.26 A | 8 mW | 5 mW | 3 mW | 62.3 / 34.1 / 19.1 / 12.0 mA |
| 10 µH VLS252012CX-100M-1 (ferrite) | 0.30 A | 27 mW | 5 mW | 4 mW | no gain — Rac 3.5 Ω @ 1.1 MHz, hard saturation; rejected |

The saving is a nearly constant **≈6–7 mA of battery current whenever the frontlight is on** — about 10 % at
full brightness and 25–35 % at reading-in-the-dark levels. Absolute numbers carry model uncertainty (small-signal
Rac, assumed LED V_f); the *difference* between inductors is the robust part. Dimming is analog and DC in both
cases, so neither value flickers; 10 µH additionally lowers 1.1 MHz output ripple by about a third and puts the
loop on TI's characterized operating point at the 1–2 mV FB levels of deep dimming.

Part choice: `C88532` has the same measured Rac as the 1.0 mm HBU-100M (`C2042741`, $0.11, 1.6k stock) with lower
DCR (450 vs 580 mΩ), 13× the stock and 40 % lower price; its guaranteed Isat (1.0 A, 1.3 A typ, soft
saturation) clears the 0.8 A soft-start limit and the ≈0.2 A running peak. It is 1.2 mm tall — lower than the
0805 capacitor (`C9`) beside it. Same 2.5 × 2.0 mm land.

**Bench check on an existing board (5 minutes):** swap L2, run from 3.7 V, and compare supply current at 100 %,
25 % and 10 % ADIM duty against the table. Also confirm clean start-up and a steady `LED_SW` at 1 % duty.

**Next-revision savings that need a footprint change:** a $0.10 THT USB-C exists (HDGC 1.0-B-16P `C2915479`,
staggered-pin 16P) against the $1.04 GCT — worth $0.93/board if its land is adopted; a Basic red 0805 LED
(NationStar `C84256`, $0.013) if `D2` becomes 0805.

## Cost

JLC part prices at each order size (≈3 % + 4 pcs attrition on SMD parts, as JLC applies), plus the Extended
loading fee. The model reproduces the line prices on both previous order exports to within cents.

| Per board, parts + fees | 5 boards | 10 | 30 | 100 |
|---|--:|--:|--:|--:|
| v3 brand-conservative (28 Extended types) | $36.78 | $25.10 | $17.90 | $13.89 |
| **v4 optimized (26 Extended types)** | **$33.52** | **$22.93** | **$16.41** | **$12.74** |
| …if JLC's fee is $3.00 instead of $1.50 | $41.32 | $26.83 | $17.71 | $13.13 |

Where the money goes at 30 boards (optimized, $16.41/board): ESP32-S3-WROOM-1-N16R8 $4.03 · DS3231MZ+ $2.71 ·
USB-C receptacle $1.04 · TPS923610 $0.59 · ten TS365ZJ switches $0.52 · CCTC 22 µF ×3 $0.40 · TPS2116 $0.27 ·
Hirose FH34SRJ-24S $0.31 · fees $1.30 · everything else ≈ $5. Consigning the module and the RTC removes $6.74.

**PCB + assembly** is not in those files: your 30-board quote was $624.08 total against $338.12 of parts, i.e.
≈ **$9.5/board** for PCB, SMT, hand-soldered THT and setup at that quantity (roughly $15–20/board at 5 boards,
where the fixed setup dominates). All-in at 30 boards ≈ **$26/board**.

**Hand-build** (one board, DigiKey-style parts, reference qty-1 prices from the owner's mid-2026 DigiKey sourcing
sheet or catalog estimates — DigiKey itself could not be crawled this session): ≈ **$48 in parts** before the
PCB (≈$5–10 each at qty 5) and your time. The three LCSC-only parts (TP4056, DW01A, FS8205A) are cheap enough to
order from LCSC alongside; everything else is a stock DigiKey/Mouser line. Roughly three times the JLC per-board
parts cost at 30 boards, which is the expected premium for building singles.

## Review of the earlier "price-maxed" sheet

`production/bom-JLCPCB_PriceMaxed.xlsx` (25-board basis) got the big things right and was the basis of the
second order: TS365ZJ switches (−$1.17/board), TF PUSH microSD (−$1.23/board), SD05C TVS (−$0.35/board) and
the unmatched-line fills. Its misses, now corrected in v4:

- **`L2` "SWAP ~$0" to HBU** — proposed only to match the schematic's MPN, at +$0.0035 by its own numbers. HBX `C88528` was, and is, the cheaper and lower-DCR 4.7 µH part, and both orders kept it. (v4 now moves L2 to 10 µH — see above.)
- **`CR1` "SD05C, −$0.35/board"** — right for CR2/CR3, but on VBUS it traded the schematic's 5.5 V-rated TSD05C for a 5.0 V-rated part on a rail that may legally sit at 5.5 V. v4 moves CR1 to SMF6.5CA (6.5 V standoff by family definition, JLC Preferred) — cheaper than either.

- **`D2` endorsed as "floor"** — the $0.009 part it kept (`C2827254`) is a *reverse-mount* LED that needs a board cutout; JLC flagged it. Now YLED1206R (`C28310439`), standard top-emitting.
- **22 µF "$0.04"** — the CCTC part is $0.12 at JLC. Still the right choice, but the projected saving was overstated by ~$0.25/board.
- **B5819W and SMAJ26A "floor/keep"** — missed that a Basic B5819W and a Preferred SMAJ26A exist (two feeder fees).
- **AO3419 "verify AO3401A"** — AO3401A is Basic, equal-priced, better R_DS(on) and stocked 200× deeper; it should have been a swap, not a caution.
- **"R14/R37 may be Basic"** — checked: no Basic 3 Ω or 15 Ω 0603 exists; but the 15 Ω UNI-ROYAL is *Preferred* (no fee), so R37 costs nothing extra.
- **DS3231 "consigned, no knock-off worth it"** — true, but JLC's own cut-tape listing is 45 % dearer than the reel listing of the same part.
- **"No viable THT USB-C"** — one exists at $0.10 (different land; next rev).
- Its "OPP" rows for TPD4E1U06/AO3419/F1: F1 adopted (spec-identical Brightking); AO3419 adopted via AO3401A; TPD4E1U06 declined (see above).

## Placed parts (optimized BOM)

### ICs

| Qty | Refs | Value | JLC/LCSC | MPN / manufacturer | Notes |
|--:|---|---|---|---|---|
| 1 | U4 | ESP32-S3-WROOM-1 | `C2913202` | Espressif ESP32-S3-WROOM-1-N16R8 | 16 MB flash / 8 MB octal PSRAM — must be an R8 part |
| 1 | U3 | TLV75533PDBV | `C404027` | TI TLV75533PDBVR | 3.3 V LDO, 500 mA |
| 1 | U2 | TPS2116DRL | `C3235557` | TI TPS2116DRLR | power-path mux |
| 1 | U11 | TP4056-42-ESOP8 | `C16581` | TOPPOWER TP4056-42-ESOP8 (JLC Preferred) | Li-ion charger; R6 = 4.7 kΩ ≈ 0.25 A |
| 1 | U5 | DW01A | `C351410` | PUOLOP DW01A | cell protection controller |
| 1 | U10 | TPS923610DRLR | `C52919131` | TI TPS923610DRLR | frontlight boost driver — **low JLC stock** |
| 1 | U12 | 74LVC1G04 | `C53185133` | MDD 74LVC1G04GV | inverter (warm/cool select) |
| 1 | U13 | DS3231MZ | `C107410` | ADI DS3231MZ+TRL (reel) | RTC, VBAT-only wiring; optional |
| 5 | U1 U6 U7 U8 U9 | TPD4E1U06DBVR | `C19829453` | TECH PUBLIC TPD4E1U06DBVR | ESD arrays: SD (U1, U9), USB (U6), touch (U7), expansion (U8) |

### Transistors

| Qty | Refs | Value | JLC/LCSC | MPN / manufacturer | Notes |
|--:|---|---|---|---|---|
| 4 | Q2 Q3 Q7 Q8 | AO3401A | `C15127` | AOS AO3401A P-ch (Basic) | Q3/Q8 battery series, Q7 SD power switch, Q2 Fix 4 3V3→CE pass. Schematic Value still reads AO3419 — update it when adopting |
| 3 | Q5 Q6 Q9 | BSS138 | `C7420339` | hongjiacheng BSS138 N-ch (Preferred) | Q5/Q6 frontlight string select, Q9 Fix 4 polarity detector (source → B−) |
| 1 | Q4 | IRLML6346TRPBF | `C67276` | Infineon IRLML6346TRPBF N-ch | EPD charge-pump switch — genuine Infineon, do not accept a clone |
| 1 | Q1 | FS8205A | `C2830320` | TECH PUBLIC FS8205A | dual N-FET, cell protection |

### Diodes / TVS

| Qty | Refs | Value | JLC/LCSC | MPN / manufacturer | Notes |
|--:|---|---|---|---|---|
| 3 | D4 D5 D6 | B5819W | `C8598` | Jiangsu Changjing B5819W SL, 40 V Schottky (Basic) | EPD charge-pump rectifiers |
| 1 | D2 | LED | `C28310439` | YONGYUTAI YLED1206R red | USB-present indicator, standard top-emitting; pad 1 = cathode |
| 1 | D3 | SMAJ26A | `C19077543` | hongjiacheng SMAJ26A (Preferred) | TVS on LED_SW |
| 1 | D8 | PESD2IVN-UX | `C42370512` | TECH PUBLIC PESD2IVN-UX | ESD on the LED returns |
| 1 | CR1 | **SMF6.5CA** | `C19077501` | hongjiacheng SMF6.5CA (Preferred); prime part Littelfuse SMF6.5CA | VBUS TVS ahead of F1, **SOD-123FL**, bidirectional: 6.5 V standoff, V_BR 7.22–7.98 V, ≤11.2 V @ 17.9 A. Schematic/PCB still show TSD05CDYFR in SOD-323 — change the footprint to `Diode_SMD:D_SMF` |
| 2 | CR2 CR3 | TSD05CDYFR | `C5299440` | DOWO SD05C-01FTG | 5.0 V-standoff bidirectional TVS on 3V3 and P+ (≤4.2 V) — adequate margin on these rails |

### Connectors

| Qty | Refs | Value | JLC/LCSC | MPN / manufacturer | Notes |
|--:|---|---|---|---|---|
| 1 | J1 | USB_C_Receptacle | `C7095263` | GCT USB4085-GF-A, THT | confirm THT soldering is in the JLC job |
| 1 | J2 | FH34SRJ-24S-0.5SH_50_ | `C324726` | Hirose FH34SRJ-24S-0.5SH(50) | 24-pin e-paper FPC |
| 2 | J3 J4 | FH34SRJ-6S-0.5SH_50_ | `C224194` | Hirose FH34SRJ-6S-0.5SH(50) | frontlight (J3), touch (J4) |
| 1 | J5 | Conn_01x02 | `C48579993` | CJT A2001WR-2P (JST PH 2-pin right-angle equivalent) | battery; pin 1 = B−, pin 2 = B+ |
| 1 | J6 | PPPC062LJBN-RC | `C5333437` | CJT A2541HWR-2x6P | 2×6 expansion header — low JLC stock |
| 1 | J7 | Micro_SD_Card | `C393941` | SHOU HAN TF PUSH | push-push microSD; slotted dual-source land also fits GCT MEM2075 |

### Switches

| Qty | Refs | Value | JLC/LCSC | MPN / manufacturer | Notes |
|--:|---|---|---|---|---|
| 10 | SW1 SW2 SW3 SW4 SW5 SW7 SW8 SW9 SW10 SW11 | SW_Push | `C557598` | SHOU HAN TS365ZJ right-angle THT tactile | MJTP1117 land |
| — | SW6 | SW_Push | **DNP** | APEM MJTP1243 (6 × 3.5 × 4.3 mm vertical 2-pin THT, 6.5 mm pitch) | BOOT button; different land, TS365ZJ does not fit |

### Inductors / fuse

| Qty | Refs | Value | JLC/LCSC | MPN / manufacturer | Notes |
|--:|---|---|---|---|---|
| 1 | L1 | 22u | `C350879` | TDK VLS3012HBX-220M | EPD charge-pump inductor, 3 × 3 mm shielded |
| 1 | L2 | **10u** | `C88532` | TDK VLS252012HBX-100M-1 | frontlight boost inductor, 2.5 × 2.0 × 1.2 mm (schematic still reads 4.7u / HBU — update it; 1.0 mm alternative VLS252010HBU-100M `C2042741`) |
| 1 | F1 | 0805L100WR | `C269106` | Brightking SMD0805B100TFT | 1 A hold / 1.95 A trip / 6 V PTC (≈0.65 A hold at 60 °C) |

### Resistors (all 0603, 1 %; all Basic except R14 Extended and R37 Preferred)

| Qty | Refs | Value | JLC/LCSC |
|--:|---|---|---|
| 6 | R27 R42 R44 R46 R52 R73 | 0 | `C21189` |
| 4 | R60 R61 R63 R64 | 100 | `C22775` |
| 2 | R16 R78 | 1k | `C21190` |
| 1 | R59 | 2k | `C22975` |
| 2 | R47 R48 | 2.2k | `C4190` |
| 1 | R14 | 3 | `C22356394` |
| 1 | R6 | 4.7k | `C23162` |
| 2 | R2 R3 | 5.1k | `C23186` |
| 1 | R18 | 5.6k | `C23189` |
| 13 | R4 R5 R7 R8 R9 R13 R15 R28 R53 R54 R55 R56 R62 | 10k | `C25804` |
| 1 | R11 | 12k | `C22790` |
| 1 | R37 | 15 | `C22810` |
| 1 | R19 | 20k | `C4184` |
| 1 | R71 | 22k | `C31850` |
| 15 | R21 R22 R23 R24 R25 R26 R29 R30 R31 R32 R33 R34 R65 R68 R69 | 33 | `C23140` |
| 1 | R35 | 33k | `C4216` |
| 2 | R20 R67 | 56k | `C23206` |
| 1 | R36 | 68k | `C23231` |
| 7 | R40 R51 R70 R75 R76 R77 R79 | 100k | `C25803` |
| 1 | R41 | 120k | `C25808` |
| 1 | R17 | 150k | `C22807` |
| 1 | R38 | 300k | `C23024` |
| 10 | R1 R10 R12 R39 R49 R50 R57 R80 R81 R82 | 1M | `C22935` |

### Capacitors

| Qty | Refs | Value | Pkg | JLC/LCSC | MPN |
|--:|---|---|---|---|---|
| 1 | C1 | 1n | 0603 | `C1588` | Samsung CL10B102KB8NNNC 50 V X7R (Basic) |
| 4 | C23 C27 C28 C29 | 2.2n | 0603 | `C1604` | FH 0603B222K500NT 50 V X7R (Basic) |
| 6 | C7 C24 C30 C31 C33 C36 | 0.1u / 100n | 0603 | `C14663` | Yageo CC0603KRX7R9BB104 50 V X7R (Basic) |
| 7 | C5 C8 C21 C22 C25 C26 C37 | 1u | 0603 | `C15849` | Samsung CL10A105KB8NNNC 50 V X5R (Basic) |
| 2 | C10 C12 | 4.7u | 0603 | `C19666` | Samsung CL10A475KO8NNNC 16 V X5R (Basic) |
| 2 | C2 C3 | 10u | 0603 | `C19702` | Samsung CL10A106KP8NNNC 10 V X5R (Basic) |
| 4 | C9 C18 C19 C20 | 1u (C9/C20 marked 50 V) | 0805 | `C28323` | Samsung CL21B105KBFNNNE **50 V** X7R (Basic) |
| 6 | C11 C13 C14 C15 C16 C17 | 4.7u/50V | 0805 | `C513770` | Samwha CS2012X5R475K500NRE **50 V** X5R |
| 3 | C4 C6 C32 | 22u | 0805 | `C20416420` | CCTC TCC0805X5R226M250FT 25 V X5R |

## DNP in every build

| Refs | Value | Purpose |
|---|---|---|
| R43 R66 | 0 | touch VDD/INT swap (alternate to R42/R44) |
| R45 R58 | 0 | touch SDA/SCL swap (alternate to R46/R52) |
| R72 R74 | 10k / 0 | UP(2) as power button (alternate to R36/R73) — **never fit R73 and R74 together** |
| TP3 TP4 TP5 | pin header | frontlight test pins (LED_SW, C−, W−) |
| SW6 | APEM MJTP1243 | BOOT button. Not needed for flashing (USB-Serial-JTAG). LCSC equivalents if fitting: ALPS SKHLACA010 `C382056`, HYP 1TS002A-1600-4300 `C255782` — confirm the 6.5 mm pin pitch |

## Hand-build (DigiKey-style) parts

Full list with reference prices: [`BOM_handbuild_digikey.csv`](BOM_handbuild_digikey.csv). Same lands as the
JLC build; search DigiKey/Mouser by the manufacturer part number.

| Refs | Part | Note |
|---|---|---|
| J7 | GCT MEM2075-00-140-01-A | push-push, fits the slotted dual-source land |
| J1 | GCT USB4085-GF-A | THT USB-C |
| J2, J3/J4 | Hirose FH34SRJ-24S-0.5SH(50), FH34SRJ-6S-0.5SH(50) | |
| J5, J6 | JST S2B-PH-K-S(LF)(SN), Sullins PPPC062LJBN-RC | |
| SW1–SW5, SW7–SW11 / SW6 | APEM MJTP1117 / MJTP1243 (DNP) | |
| Q2 Q3 Q7 Q8 / Q4 / Q5 Q6 Q9 / Q1 | AOS AO3401A (or AO3419) / Infineon IRLML6346TRPBF / onsemi BSS138LT1G / FS8205A (LCSC) | |
| U2 U3 U10 U12 / U13 / U1 U6–U9 | TI TPS2116DRLR, TLV75533PDBVR, TPS923610DRLR, SN74LVC1G04DBVR / ADI DS3231MZ+ / TI TPD4E1U06DBVR | |
| U11 / U5 | TP4056-42-ESOP8 / DW01A | LCSC-only; order from LCSC |
| D2 / D3 / D4–D6 / D8 / CR1–CR3 | Lite-On LTST-C150KRKT (red 1206, pad 1 = cathode) / Littelfuse SMAJ26A / Diodes B5819W or 1N5819HW-7-F / Nexperia PESD2IVN-UX / Littelfuse SMF6.5CA (CR1) and TI TSD05CDYFR (CR2, CR3) | |
| L1 / L2 / F1 | TDK VLS3012HBX-220M / VLS252012HBX-100M-1 (10 µH; or VLS252010HBU-100M) / Littelfuse 0805L100WR | |
| passives | 0603 1 % thick film; Samsung CL10/CL21 — keep the 50 V parts 50 V | |

## Off-board items

| Item | Note |
|---|---|
| 4.26" e-paper panel | GDEQ0426T82 / -FL01C (frontlight) / -FT01C (frontlight + touch); check the J3 pin order for FT01C lots (DESIGN_REVIEW §8) |
| Battery | single-cell Li-ion/LiPo, 4.2 V charge; 500 mAh charges in ≈2.5–3 h at the default 0.25 A; verify cable polarity (pin 1 = B−) |
