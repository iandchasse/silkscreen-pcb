# Silkscreen — Bill of Materials

**Board-assembled parts: ~**\$48.24** per board** (163 placed parts, one-off qty-1 pricing). 
Add the off-board items below for a complete unit. Excludes 5 mounting holes and 5 test pads.

> **Pricing sources:** `ODS` = from the project's own DigiKey sourcing sheet (mid-2026). `est` = estimate — **verify at the link before ordering.** Prices are qty-1 unit cost; passives and Chinese-market parts are far cheaper in reels/from LCSC. Links are DigiKey keyword searches (live stock). Sanity-check every MPN against its footprint.


## Integrated circuits

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 1 | U12 | 74LVC1G04 | SN74LVC1G04DBVR | Texas Instruments | — | ~$0.10 | $0.10 | est | [DK](https://www.digikey.com/en/products/result?keywords=SN74LVC1G04DBVR) | inverter |
| 1 | U13 | DS3231MZ | DS3231MZ+ | Analog Devices | LCSC clone (e.g. C9866) far cheaper | ~$5.50 | $5.50 | est | [DK](https://www.digikey.com/en/products/result?keywords=DS3231MZ%2B) | RTC |
| 1 | U5 | DW01A | DW01A | Fortune | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=DW01A) | LCSC C8724; source LCSC |
| 1 | U4 | ESP32-S3-WROOM-1 | ESP32-S3-WROOM-1-N16R8 | Espressif | N8R8 (less flash / cheaper) | $6.50 | $6.50 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=ESP32-S3-WROOM-1-N16R8) | 16 MB flash + 8 MB octal PSRAM; must be an R8 (octal-PSRAM) part |
| 1 | U3 | TLV75533PDBV | TLV75533PDBVR | Texas Instruments | — | ~$0.35 | $0.35 | est | [DK](https://www.digikey.com/en/products/result?keywords=TLV75533PDBVR) | 3.3V LDO |
| 1 | U11 | TP4056-42-ESOP8 | TP4056-42-ESOP8 | Nanjing Extension | — | ~$0.15 | $0.15 | est | [DK](https://www.digikey.com/en/products/result?keywords=TP4056-42-ESOP8) | LCSC C382139; source LCSC |
| 5 | U1 U6 U7 U8 U9 | TPD4E1U06DBVR | TPD4E1U06DBVR | Texas Instruments | — | $0.86 | $4.30 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=296-35965-1-ND) |  |
| 1 | U2 | TPS2116DRL | TPS2116DRL | Texas Instruments | — | ~$0.60 | $0.60 | est | [DK](https://www.digikey.com/en/products/result?keywords=TPS2116DRL) | power-path mux |
| 1 | U10 | TPS923610DRLR | TPS923610DRLR | Texas Instruments | — | ~$0.70 | $0.70 | est | [DK](https://www.digikey.com/en/products/result?keywords=TPS923610DRLR) | frontlight boost |

## Connectors

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 1 | J5 | Conn_01x02 | B2B-PH-K-S(LF)(SN) | JST | A2001WR-2P (LCSC PH equiv) | ~$0.15 | $0.15 | est | [DK](https://www.digikey.com/en/products/result?keywords=B2B-PH-K-S%28LF%29%28SN%29) | 2p PH |
| 1 | J2 | FH34SRJ-24S-0.5SH_50_ | FH34SRJ-24S-0.5SH(50) | Hirose | — | $2.26 | $2.26 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=FH34SRJ-24S-0.5SH%2850%29) | 24p ZIF |
| 2 | J3 J4 | FH34SRJ-6S-0.5SH_50_ | FH34SRJ-6S-0.5SH(50) | Hirose | — | $0.79 | $1.58 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=H125773CT-ND) |  |
| 1 | J7 | Micro_SD_Card | MEM2075-00-140-01-A | GCT | TF PUSH (LCSC C393941, ~$0.06 for JLC) | ~$1.92 | $1.92 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=MEM2075-00-140-01-A) | push-push; unified footprint (DigiKey=MEM2075, JLC=TF PUSH) |
| 1 | J6 | PPPC062LJBN-RC | PPPC062LJBN-RC | Sullins | A2541HWR-2x6P (LCSC, if OOS) | ~$1.50 | $1.50 | est | [DK](https://www.digikey.com/en/products/result?keywords=PPPC062LJBN-RC) | 2x6 header |
| 1 | J1 | USB_C_Receptacle | USB4085-GF-A-060 | GCT | — | $0.91 | $0.91 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=USB4085-GF-A-060) | USB-C; verify suffix |

## Transistors / MOSFETs

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 3 | Q3 Q7 Q8 | AO3419 | AO3419 | Alpha & Omega | IRLML6402 | $0.49 | $1.47 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=AO3419) |  |
| 3 | Q4 Q5 Q6 | BSS138 | BSS138LT1G | onsemi | — | $0.31 | $0.93 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=BSS138LT1G) |  |
| 1 | Q1 | FS8205A | FS8205A | Fortune | — | $0.39 | $0.39 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=FS8205A) | LCSC C32254 |

## Diodes

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 3 | D4 D5 D6 | B5819W | B5819W | MCC | — | $0.22 | $0.66 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=B5819W) | equiv 1N5819HW-7-F |
| 1 | D2 | LED | LED 1206 | — | — | ~$0.10 | $0.10 | est | — | power indicator |
| 1 | D8 | PESD2IVN-UX | PESD2IVN-UX | Nexperia | — | ~$0.20 | $0.20 | est | [DK](https://www.digikey.com/en/products/result?keywords=PESD2IVN-UX) | ESD |
| 1 | D3 | SMAJ26A | SMAJ26A | Littelfuse | — | ~$0.30 | $0.30 | est | [DK](https://www.digikey.com/en/products/result?keywords=SMAJ26A) | TVS |

## TVS / ESD

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 3 | CR1 CR2 CR3 | TSD05CDYFR | TSD05CDYFR | Texas Instruments | GOODWORK SD05C | $0.67 | $2.01 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=TSD05CDYFR) |  |

## Inductors

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 1 | L1 | 22u | VLS3012HBX-220M | TDK | — | ~$0.50 | $0.50 | est | [DK](https://www.digikey.com/en/products/result?keywords=VLS3012HBX-220M) | 22uH shielded |
| 1 | L2 | 4.7u | VLS252010HBU-4R7M | TDK | LCSC C413592 | ~$0.07 | $0.07 | est | [LCSC](https://www.lcsc.com/product-detail/C413592.html) | 4.7uH metal-composite shielded 1008 (2.5×2.0×1.0 mm), Isat 1.55 A, Irms 1.01 A, DCR 274 mΩ |

## Fuse

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 1 | F1 | 0805L100WR | 0805L100WR | Littelfuse | — | ~$0.30 | $0.30 | est | [DK](https://www.digikey.com/en/products/result?keywords=0805L100WR) | 1.0A PPTC |

## Switches

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 10 | SW1 SW2 SW3 SW4 SW5 SW7 SW8 SW9 SW10 SW11 | SW_Push | MJTP1117 | APEM | TS365ZJ (LCSC C557598, drop-in same land) / SKHLLAA010 | ~$0.12 | $1.20 | est | [DK](https://www.digikey.com/en/products/result?keywords=MJTP1117) | 6mm right-angle tactile |
| 1 | SW6 | SW_Push | MJTP1243 | APEM | TS365ZJ (if populating) | — | — | DNP | [DK](https://www.digikey.com/en/products/result?keywords=MJTP1243) | **DNP** — 6x3.5mm side tactile, not populated |

## Resistors

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 6 | R27 R42 R44 R46 R52 R73 | 0 | RES 0 0603 | — | — | $0.10 | $0.60 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%200%200603) | 0 ohm jumper |
| 5 | R43 R45 R58 R66 R74 | 0 | RES 0 0603 | — | — | $0.10 | $0.50 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%200%200603) | 0 ohm jumper · **DNP** |
| 4 | R60 R61 R63 R64 | 100 | RES 100 0603 | — | — | $0.10 | $0.40 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%20100%200603) |  |
| 6 | R40 R51 R70 R75 R76 R77 | 100k | RES 100k 0603 | — | — | $0.10 | $0.60 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%20100k%200603) |  |
| 13 | R4 R5 R7 R8 R9 R13 R15 R28 R53 R54 R55 R56 R62 | 10k | RES 10k 0603 | — | — | $0.10 | $1.30 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2010k%200603) |  |
| 1 | R72 | 10k | RES 10k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2010k%200603) |  · **DNP** |
| 1 | R41 | 120k | RES 120k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%20120k%200603) |  |
| 1 | R11 | 12k | RES 12k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2012k%200603) |  |
| 1 | R37 | 13.3 | RES 13.3 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2013.3%200603) |  |
| 1 | R17 | 150k | RES 150k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%20150k%200603) |  |
| 7 | R1 R10 R12 R39 R49 R50 R57 | 1M | RES 1M 0603 | — | — | $0.10 | $0.70 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%201M%200603) |  |
| 2 | R16 R78 | 1k | RES 1k 0603 | — | — | $0.10 | $0.20 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%201k%200603) |  |
| 2 | R47 R48 | 2.2k | RES 2.2k 0603 | — | — | $0.10 | $0.20 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%202.2k%200603) |  |
| 1 | R19 | 20k | RES 20k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2020k%200603) |  |
| 1 | R71 | 22k | RES 22k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2022k%200603) |  |
| 1 | R59 | 2k | RES 2k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%202k%200603) |  |
| 1 | R14 | 3 | RES 3 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%203%200603) |  |
| 1 | R38 | 300k | RES 300k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%20300k%200603) |  |
| 15 | R21 R22 R23 R24 R25 R26 R29 R30 R31 R32 R33 R34 R65 R68 R69 | 33 | RES 33 0603 | — | — | $0.10 | $1.50 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2033%200603) |  |
| 1 | R35 | 33k | RES 33k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2033k%200603) |  |
| 1 | R6 | 4.7k | RES 4.7k 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%204.7k%200603) |  |
| 2 | R2 R3 | 5.1k | RES 5.1k 0603 | — | — | $0.10 | $0.20 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%205.1k%200603) |  |
| 1 | R18 | 5.6k | RES 5.6k 0603 | — | — | $0.11 | $0.11 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%205.6k%200603) |  |
| 2 | R20 R67 | 56k | RES 56k 0603 | — | — | $0.10 | $0.20 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2056k%200603) |  |
| 1 | R36 | 68k | RES 68k 0603 | — | — | $0.54 | $0.54 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=RES%2068k%200603) |  |

## Capacitors

| Qty | Refs | Value | MPN | Mfr | LCSC alt | Unit | Ext | src | Buy | Notes |
|--:|---|---|---|---|---|--:|--:|:--:|---|---|
| 4 | C7 C30 C33 C36 | 0.1u | CAP 0.1u 0603 | — | — | $0.13 | $0.52 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%200.1u%200603) |  |
| 2 | C24 C31 | 100n | CAP 100n 0603 | — | — | $0.13 | $0.26 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%20100n%200603) |  |
| 2 | C2 C3 | 10u | CAP 10u 0603 | — | — | $0.14 | $0.28 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%2010u%200603) |  |
| 1 | C1 | 1n | CAP 1n 0603 | — | — | $0.10 | $0.10 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%201n%200603) |  |
| 7 | C5 C8 C21 C22 C25 C26 C37 | 1u | CAP 1u 0603 | — | — | $0.10 | $0.70 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%201u%200603) |  |
| 2 | C18 C19 | 1u | CAP 1u 0805 | — | — | $0.10 | $0.20 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%201u%200805) |  |
| 2 | C9 C20 | 1u/50V | CAP 1u/50V 0805 | — | — | $0.15 | $0.30 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%201u/50V%200805) |  |
| 4 | C23 C27 C28 C29 | 2.2n | CAP 2.2n 0603 | — | — | $0.10 | $0.40 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%202.2n%200603) |  |
| 3 | C4 C6 C32 | 22u | CAP 22u 0805 | — | — | $0.14 | $0.42 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%2022u%200805) |  |
| 2 | C10 C12 | 4.7u | CAP 4.7u 0603 | — | — | $0.19 | $0.38 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%204.7u%200603) |  |
| 6 | C11 C13 C14 C15 C16 C17 | 4.7u/50V | CAP 4.7u/50V 0805 | — | — | $0.19 | $1.14 | ODS | [DK](https://www.digikey.com/en/products/result?keywords=CAP%204.7u/50V%200805) |  |

## Complete build — off-board items

| Item | Source | Price | Part / note |
|---|---|--:|---|
| PCB fab (2-layer, ×5 min) | PCBWay | $24.14 / 5 boards | ~$4.83/board at qty 5 |
| 4.26" e-paper w/ frontlight | AliExpress | $29.59 | GDEQ0426T82-FL01C |
| 650 mAh LiPo (<6 mm) | Amazon | $10.06 | battery-agnostic; any 1-cell fits |

**Rough single-unit total:** ~\$47.30 board parts + ~\$4.83 PCB + \$29.59 display + \$10.06 battery ≈ **~\$91.78** (qty 1, DigiKey-sourced, before assembly labor). *(microSD `J7` now the push-push GCT MEM2075 ~\$1.92, down from the \$2.86 Hirose DM3AT.)* JLC-assembled runs are far cheaper — see [`../production/bom-JLCPCB_PriceMaxed.xlsx`](../production/bom-JLCPCB_PriceMaxed.xlsx) (~\$6.86/board in parts at qty 25 with the LCSC-cheap equivalents: TF PUSH microSD, TS365ZJ tactiles, SD05C, etc.).

## Notes & caveats

- **LCSC-cheaper / alternates:** buttons `MJTP1117` → **SKHLLAA010 / TS365ZJ**; JST `S2B-PH-K-S` → **A2001WR-2P**; header `PPPC062LJBN-RC` → **A2541HWR-2x6P** (if PPPC is out of stock at LCSC).
- **LCSC-only** (not DigiKey): `DW01A` (C8724), `TP4056` (C382139), `FS8205A` (C32254). `DS3231MZ` genuine is pricey (~$5–8); LCSC clones are ~$1–2.
- **Verify before ordering:** `J1` USB4085 suffix; `U4` = **N16R8** (JLC C2913202); `B5819W` DigiKey equiv `1N5819HW-7-F`.
- **DNP** (excluded from assembly): `R43 R45 R58 R66 R72 R74`.
- `est` prices are placeholders for parts changed since the sourcing sheet was made (TLV75533P, TPS923610, TP4056, TPS2116, VLS3012HBX, SMAJ26A, PESD2IVN, DS3231MZ, LED, fuse, switches) — confirm at the links.