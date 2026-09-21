# Parts research — BOM-07, BOM-V01, BOM-06, BOM-02, HMI-01, USB-04

> **Resolved by the main reviewer, 2026-09-20 — D8 pinout is correct.** Nexperia PESD2IVN-U datasheet (15 July 2015), Table 2 "Pinning information": pin 1 = K (cathode), pin 2 = K (cathode), pin 3 = CC (common cathode), SOT323. The board wires D8.1 = `C-`, D8.2 = `W-`, D8.3 = `GND`. The open "VERIFY D8 pad 3" item below is closed; a PESD2IVN27-UX would be a true drop-in.

**All figures pulled live on 2026-09-20.** Sources are named inline. Anything I could not confirm
live today is marked **est.** and should be re-checked before you place an order.

Two sources were used for every number:

* **JLC/LCSC** — `https://jlcsearch.tscircuit.com/api/search?q=<MPN>` (JLCPCB's own parts library),
  queried 2026-09-20. Prices are JLC's own per-piece figures. "Basic / Preferred / Extended" is
  JLC's library class — Extended parts attract the per-reel setup fee.
* **DigiKey** — `https://www.digikey.com/en/products/result?keywords=<MPN>`, fetched 2026-09-20.

Standing rule respected: **prime MPN stays DigiKey-sourceable; the LCSC code is the extra field.**

Headline: **one line is worth changing and it is the RTC — about $12 a board.** Everything else is
either already the right call (the ESD arrays, CR1) or a like-for-like swap forced by a dead MPN
(the 22 µF caps) or a small addition (the PPTC).

---

## 1. BOM-07 — the RTC (U13 DS3231MZ)

### What is fitted, and what it actually costs

| | value |
|---|---|
| MPN | DS3231MZ+TRL (Analog Devices / Maxim) |
| Footprint on the board | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` — **narrow** SOIC-8, 3.9 × 4.9 mm (confirmed in `silkscreen_pcb.kicad_pcb`, U13) |
| DigiKey 2026-09-20 | **Active**, 8,369 in stock, **$13.85 @ 1**, $10.90 @ 10, $9.36 @ 100 |
| LCSC | **C107410**, Extended, 11,509 in stock, $2.96 |
| Sleep contribution | 2.0 µA typ / 3.0 µA max of the ~72–73 µA total (`sections/03_ldo_power_tree_sleep_budget.md`, rows 330 and 412 — the RTC is 3 % of the budget) |
| Accuracy | ±5 ppm, −40…+85 °C (integrated MEMS TCXO) |

DigiKey confirms the package as `8-SOIC (0.154", 3.90mm Width)`, which matches the KiCad footprint.
**That rules out every SOP-8-208 mil candidate as a drop-in** (SD3031, SD3078, BL5372 in SOP-8 are
all the wide 208 mil body). There is **no pin-and-footprint drop-in for this part.** Any change here
is a footprint change. Accept that up front and the field opens up a lot.

### Every candidate, checked live

Crystal column: **int.** = 32.768 kHz crystal integrated in the package (your hard requirement);
**ext.** = you must buy and place a separate crystal.

| MPN | XTAL | Package | DigiKey stock | DK $1 / $10 | LCSC | JLC stock | JLC $ | class |
|---|---|---|---|---|---|---|---|---|
| **Micro Crystal RV-8263-C7-32.768kHz-20ppm-TA-QC** | int. | 8-SON 3.2 × 1.5 mm (C7) | **99,462** Active | **$1.64** / ~$1.20 *(est., see note)* | **C5137460** | 472 | $1.61 | Ext |
| Micro Crystal RV-3032-C7-32.768kHz-2.5ppm-TA-QC | int. | same C7 outline | 429 Active | $3.24 / $2.43 | C5366550 | 754 | $3.50 | Ext |
| Micro Crystal RV-3028-C7-32.768kHz-1ppm-TA-QC | int. | same C7 outline | **0** (1,000 past due) | $2.55 / $1.89 | C3019759 | 1,182 | $2.27 | Ext |
| Epson RX8130CE B6 | int. | 10-SMD 3.2 × 2.5 mm | 4,077 Active | $1.39 / ~$0.68 (reel) | C5879784 | 1,986 | $0.85 | Ext |
| Epson RX8130CE:B3 | int. | 10-SMD module | 5,628 Active | $3.03 / $1.76 | — | — | — | — |
| Epson RX8900CE:UB0 (DTCXO) | int. | 10-SMD 3.2 × 2.5 mm | 981 Active | $2.84 / $1.54 | C5903517 | 1,200 | $1.69 | Ext |
| Epson RX8900CE:UB3 | int. | 10-SMD 3.2 × 2.5 mm | 256 Active | $5.83 / $3.56 | C46042255 | 2,159 | $1.63 | Ext |
| Epson RX8025T-UB (TCXO) | int. | SOP-14 208 mil | *not fetched* (est. stocked) | est. | C17353 | **15,639** | $1.39 | Ext |
| NXP PCF85263ATL/AX | **ext.** | DFN-10 2.6 × 2.6 | — | — | C2651523 | 10,221 | $1.07 | Ext |
| NXP PCF2129T (TCXO, int. xtal) | int. | SO-16 300 mil | — | — | C2651522 | **3** | $5.33 | Ext |
| NXP PCF2129AT | int. | SOIC-20 300 mil | — | — | C47508 | 993 | $4.10 | Ext |
| Abracon AB1805-T3 | **ext.** | QFN-16 3 × 3 | — | — | C2649355 | 763 | $2.46 | Ext |
| INS5699S (RX8900 clone) | int. | 3.2 × 2.5 mm | **none — not a DigiKey line** | — | C2924605 | 3,817 | $1.56 | Ext |
| SD3031 (Whwave) | int. | **SOP-8 208 mil** | **none at DigiKey** | — | C2988356 | 713 | $1.58 | Ext |
| SD3078 (Whwave) | int. | **SOP-8 208 mil** | **none at DigiKey** | — | C916255 | **8** | $2.06 | Ext |
| SD2405 | — | — | — | — | **no LCSC hit at all** | — | — | — |
| BL5372 | **ext.** | SOP-8 | **none at DigiKey** | — | C80512 | 3,432 | $0.64 | Ext |

Notes on that table:

* **RV-8263-C7 qty-10 price**: the DigiKey page rendered the qty-10 break as "$0.1197 each", which is
  almost certainly a decimal mis-read of $1.197. Qty 1 at **$1.64** is solid; treat qty 10 as **est.**
* **RV-3028-C7 is out of stock at DigiKey** (1,000 pcs past due, restock estimate was 2026-09-18 and
  had not landed when I checked). It is the part everyone recommends on the internet; today it is
  the one you cannot buy. That is probably part of why your own search felt unsuccessful.
* **PCF85263, AB1805/AB0805 and BL5372 all need an external 32.768 kHz crystal.** They fail your
  stated constraint outright — crossed off, not "considered".
* **INS5699S, SD3031, SD3078, BL5372 are LCSC-only.** They break the DigiKey-primary rule. SD3031 is
  genuinely attractive on paper (TCXO, built-in crystal, 0.8 µA, $1.58) and it is the part the
  Chinese hobby market uses — but there is no Western distributor line for it, so under your own
  convention it can only ever be the LCSC-alternate field, never the prime MPN.
* **PCF2129** is a real DS3231 competitor (integrated TCXO crystal, ±3 ppm) but at $4.10–5.33 and in a
  SO-16/SOIC-20 300 mil body it is bigger *and* dearer than what you have. No.

### Recommendation

**Micro Crystal `RV-8263-C7-32.768kHz-20ppm-TA-QC`, LCSC `C5137460`.**

| | DS3231MZ (fitted) | RV-8263-C7 |
|---|---|---|
| DigiKey qty 1 | $13.85 | **$1.64** |
| DigiKey stock today | 8,369 | **99,462** |
| LCSC | C107410, 11,509, $2.96 | C5137460, 472, $1.61 |
| Timekeeping current | 2.0 µA typ / 3.0 µA max | **0.19 µA typ / 0.24 µA max @ 3 V** |
| Supply range | 2.3–5.5 V | 0.9–5.5 V |
| Interface | I²C | I²C |
| Crystal | integrated MEMS | **integrated** |
| Accuracy | ±5 ppm over −40…+85 °C | ±20 ppm at 25 °C, no temp compensation |
| Package | SOIC-8 3.9 × 4.9 mm | 8-SON **3.2 × 1.5 mm** |

**Saving: $12.21 per board at DigiKey qty 1**, ~$9.70 at qty 10, **$1.35 per board at JLC**. It also
takes ~2.8 µA out of the 73 µA sleep budget (≈ −4 %), and it is a quarter of the board area.

**Footprint consequence — and this is the good news:** KiCad 9 already ships the land pattern. It is
**`Package_SON:MicroCrystal_C7_SON-8_1.5x3.2mm_P0.9mm`**, found on this machine at
`C:\Program Files\KiCad\9.0\share\kicad\footprints\Package_SON.pretty\`. You do not have to draw
anything. You do have to re-place U13, move two I²C tracks and the 3V3 feed, and re-check the
0.9 mm-pitch pads against your fab rules — an hour of work, not a redesign.

**The other half of the argument:** all three Micro Crystal C7 parts use that same 3.2 × 1.5 mm
8-pad outline. Lay the C7 footprint down once and you have **three** DigiKey-stocked, LCSC-coded,
crystal-integrated options on one land pattern at three price/accuracy points — RV-8263-C7 ($1.64,
±20 ppm), RV-3032-C7 ($3.24, ±2.5 ppm over −40…+105 °C, 0.21 µA), RV-3028-C7 ($2.55, ±1 ppm, when it
comes back into stock). That is exactly the "stable sourcing" property you said you were looking for,
and it is the strongest reason to pick this family over Epson's.
*Caveat (**est.**): I did not confirm today that the pin **assignment** is byte-for-byte identical
across RV-8263-C7 / RV-3028-C7 / RV-3032-C7 — the package is common, the pin functions should be
checked against the three datasheets before you rely on the second-source story.*

**If ±20 ppm is not good enough:** go straight to **RV-3032-C7** ($3.24 @ 1, DigiKey 429 pcs, LCSC
C5366550 754 pcs). It beats the DS3231M on accuracy (±2.5 ppm vs ±5 ppm), on temperature range
(−40…+105 °C) and on current (0.21 µA vs 3 µA) — and still saves **$10.61 a board**.

**If you would rather stay on a bigger, easier-to-hand-solder part:** Epson **RX8900CE:UB0** —
DTCXO, ±5 ppm class, integrated crystal (confirmed on Epson's own product page: "Equipped with a
high-precision Digital Temperature Compensated Crystal Oscillator (DTCXO)"), 10-SMD 3.2 × 2.5 mm,
DigiKey 981 pcs at $2.84, LCSC C5903517 1,200 pcs at $1.69 — **and** the INS5699S (C2924605, 3,817
pcs, $1.56) is sold as a pin-compatible replacement for it, which gives you a JLC fallback on the
same footprint. Still saves $11 a board. The cheapest Epson is **RX8130CE B6** at $1.39/4,077 pcs
DigiKey and C5879784 $0.85/1,986 pcs LCSC, but it has no temperature compensation at all.

### The zero-BOM option: delete U13 and use the ESP32-S3's own RTC

Worth taking seriously, because it is free and it removes a part from the sourcing problem entirely.

What Espressif actually publishes (ESP-IDF Programming Guide, *System Time*, esp32s3, fetched
2026-09-20 — <https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/system_time.html>):

* The default `RTC_SLOW_CLK` source is the **internal 150 kHz RC oscillator**, chosen for "lowest deep
  sleep current consumption and no dependence on any external components".
* On accuracy, the documentation says only that **"frequency stability is affected by temperature
  fluctuations, time may drift in both Deep and Light sleep modes."**
  **Espressif publishes no ppm figure for it.** I looked; there isn't one in the S3 datasheet or the
  IDF docs. Anyone quoting you a number for it is quoting a measurement, not a spec.
* The documented alternative, the internal 8.5 MHz oscillator ÷ 256 (~33 kHz), gives "better frequency
  stability than the internal 150 kHz RC oscillator at the expense of higher (by 5 µA) deep sleep
  current consumption".
* The same page notes BLE needs sleep-clock accuracy within **500 ppm** — which is why Espressif wants
  an external 32.768 kHz crystal or RC32K for BLE sleep. The ESP32-S3-WROOM-1 on this board has **no**
  32.768 kHz crystal, so only the two internal sources exist here.

Practical drift for the 150 kHz RC is commonly measured at roughly **1–3 % (10,000–30,000 ppm)**,
i.e. **15–45 minutes a day** — **est.**, a field figure, not an Espressif number. The ÷256 source is
much better but costs 5 µA, which is more than twice what the RV-8263-C7 draws.

**Honest answer to "is a discrete RTC needed at all?":**

* If the reader joins Wi-Fi and runs SNTP **at least once a day**, the internal RTC is fine. Delete
  U13, save the $13.85 *and* the 2–3 µA, and re-sync on wake. The clock is never more than a day of
  drift away from correct.
* If it can sit for a week with no network and must still show a believable time, the internal RC is
  not fine — a week at 2 % is a couple of hours.
* The tie-breaker is that keeping a discrete RTC now costs **$1.64**, not $13.85. At $13.85 the "just
  use the internal one" argument wins easily. At $1.64 it is cheap insurance and I would keep it.

---

## 2. BOM-V01 — the five TPD4E1U06 ESD arrays

### What is actually on the board (read from `silkscreen_pcb.kicad_pcb`, 2026-09-20)

Footprint: `Package_TO_SOT_SMD:SOT-23-6_Handsoldering` on all five. Net per pad:

| ref | pad 1 | pad 2 | pad 3 | pad 4 | pad 5 | pad 6 |
|---|---|---|---|---|---|---|
| U1 (SD) | SD_DAT3 | **GND** | SD_DAT2 | SD_CLK | SD_CMD | SD_CMD |
| U6 (USB) | DN | **GND** | CC2 | CC1 | DP | DP |
| U7 (touch) | /PIN_4 | **GND** | TP_RST | /PIN_5 | /PIN_6 | /PIN_6 |
| U8 (I²C + hdr) | UNUSED_GPIO_45 | **GND** | I2C_SCL | I2C_SDA | UNUSED_GPIO_3 | UNUSED_GPIO_3 |
| U9 (SD + hdr) | SD_DAT1 | **GND** | SD_DAT0 | *(unconnected)* | UNUSED_GPIO_46 | UNUSED_GPIO_46 |

Two things fall out of this, and they decide the whole question:

1. **GND is on pad 2**, and the four protected lines land on pads 1, 3, 4 and 5/6.
2. **Pads 5 and 6 are shorted together** on every one of the five parts. That is a sensible belt-and-
   braces move (it works whether the fourth I/O is on pin 5 or pin 6 and the other is NC), but it has
   a consequence: **any substitute part that uses pin 5 for anything other than an I/O will have that
   function tied straight to a live signal.**

### Why the obvious cheap swap is wrong

**SRV05-4 is not a drop-in.** Its SOT-23-6 pinout is 1 = I/O1, 2 = GND, 3 = I/O2, 4 = I/O3,
**5 = VCC**, 6 = I/O4 *(pinout **est.** — take it from the Semtech/Littelfuse datasheet before acting,
but it is the standard SRV05-4 arrangement)*. Because this board ties pad 5 to pad 6, fitting an
SRV05-4 would make the array's internal steering rail **the signal itself** — SD_CMD on U1, DP on U6,
/PIN_6 on U7, GPIO3 on U8, GPIO46 on U9. Every other channel's upper steering diode would then dump
into that signal, and that signal would sit behind the part's internal ~6 V zener. Don't.

The same objection kills anything with a VCC/rail pin at position 5. **ESDA6V1-5SC6** is a 5-line
part with a completely different arrangement and 35–60 pF per line — far too much for SDMMC at
40 MHz — so it is out on both counts. **USBLC6-2SC6** and **PRTR5V0U2X** are **2-line** parts (and
PRTR5V0U2X is SOT-143, four pads), so you would need two per position.

### Price reality — there is nothing cheaper at DigiKey

| part | pkg | DigiKey stock | DK $1 / $10 / $100 | LCSC | JLC stock | JLC $ |
|---|---|---|---|---|---|---|
| **TPD4E1U06DBVR (TI) — fitted** | SOT-23-6 | 38,253 Active | **$0.94 / $0.587 / $0.3809** | C124691 (genuine TI) | 8,807 | $0.3033 |
| ↳ the code actually in your BOM | SOT-23-6 | — | — | **C19829453** (0.55 pF) | 10,355 | **$0.0564** |
| ↳ another clone | SOT-23-6 | — | — | C2841427 (-TP) | 4,553 | $0.1022 |
| SRV05-4 (Semtech) | SOT-23-6 | in stock | **$1.81** / — | C558418 | 461,674 | $0.0248 |
| SRV05-4 (UMW) | SOT-23-6 | in stock | **$1.23** / — | C7420376 (**Preferred**) | 622,147 | $0.0840 |
| CDSOT23-SRV05-4 (Bourns) | SOT-23-6 | 8,644 Active | **$1.88 / $1.192 / $0.7965** | — | — | — |
| TPD4E05U06DQAR (TI) | **USON-10 1 × 2.5** | — | — | C138714 | 94,387 | $0.0819 |

**Every credible SRV05-4 at DigiKey is more expensive than the TI part you already use** — $1.23 to
$1.88 against $0.94. That is the opposite of what the finding assumed, and it is the single most
useful number in this section.

At JLC you are already buying the $0.0564 clone. Swapping all five to SRV05-4 would save
5 × ($0.0564 − $0.0248) = **$0.16 per board** — and would be electrically wrong. TPD4E05U06DQAR would
save 5 × ($0.0564 − $0.0819) = *nothing*, it is dearer, and it is a different package on all five
positions.

### Verdict: **keep**, and buy at a break

**No position should change part.** The only saving actually available is on the DigiKey side and it
is a quantity break, not a substitution: 5 × $0.94 = **$4.70/board at qty 1**, 5 × $0.587 = **$2.94**
at qty 10, 5 × $0.3809 = **$1.90** at qty 100. Buying strips of 100 instead of singles takes $2.80 a
board off a five-board run. At JLC the five arrays cost **$0.28 a board** and are not worth another
minute of thought.

On necessity: all five sit on user-exposed connectors (microSD contacts, USB-C, the touch flex, the
expansion header). 0.8 pF is the right capacitance class for USB FS and 40 MHz SDMMC, and nothing
cheaper matches it. Your instinct was right; the finding's premise was not.

---

## 3. BOM-06 — D8 PESD2IVN-UX (NRND)

### Fitted

Footprint `Package_TO_SOT_SMD:SOT-323_SC-70_Handsoldering`. Board nets: **pad 1 = C−, pad 2 = W−,
pad 3 = GND**.

DigiKey 2026-09-20: PESD2IVN-UX, SC-70/SOT-323, **16,512 in stock**, $0.49 @ 1, $0.302 @ 10,
status **"Not For New Designs"**. LCSC: your BOM points at **C42370512** (TECH PUBLIC clone), 2,955
pcs, $0.0816; genuine Nexperia is **C552499**, 882 pcs, $0.1757.

So it is NRND but *not* scarce — there are 16.5k pieces sitting at DigiKey right now.

### Candidates, all verified live

| MPN | pkg | V_RWM | V_BR min | V_CL | C | DigiKey | DK $1 / $10 | LCSC | JLC stock | JLC $ |
|---|---|---|---|---|---|---|---|---|---|---|
| PESD2IVN-UX *(fitted)* | **SOT-323** | 26.5 V | 28 V | 53 V | 8.5 pF | 16,512, **NRND** | $0.49 / $0.302 | C552499 / C42370512 | 882 / 2,955 | $0.176 / $0.082 |
| **PESD2IVN27-UX** | **SOT-323** | **27 V** | **28 V** | 45 V | 14 pF | **0** (3,000 due 2027-06-29), **Active** | $0.44 / $0.271 | **C42370511** / C552498 | 1,589 | $0.0816 |
| PESD2IVN24-UX | SOT-323 | 24 V | 25.5 V | 42 V | 14 pF | *not fetched* | est. | C552496 / C54561882 | 2,085 / 3,000 | $0.217 / $0.084 |
| PESD2CANFD24V-UX | SOT-323 | 24 V | 26.7 V | — | **5.2 pF** | **0** (3,000 due 2027-01-20), Active | $0.36 / $0.219 | C46970732 | 2,835 | $0.068 |
| PESD2IVN24-TR / PESD2IVN27-TR | **SOT-23** | 24 / 27 V | 25.5 / 28 V | 42 / 45 V | 14 / 17 pF | — | — | C406047 / C552497 | 38,246 / 22,921 | $0.147 / $0.165 |
| PESD2CANFD24V-TR | **SOT-23** | 24 V | 25.5 V | 42 V | 6 pF | — | — | C552486 | 17,203 | $0.368 |
| PESD24VL2BT | **SOT-23** | 24 V | 26.7 V | 65 V | 12 pF | — | — | C2890125 | 15,937 | $0.057 |

### Verdict

**Use `PESD2IVN27-UX`.** It is the same family, the same SOT-323 package and therefore the same
pinning as the part already fitted — so it is a true drop-in with no layout change — it is **Active**,
and its 27 V standoff / 28 V breakdown is slightly *better* than the 26.5 V part you have.

**Reject anything rated 24 V here.** PESD2IVN24-UX and PESD2CANFD24V-UX both have V_RWM = 24 V with
V_BR min of 25.5 V / 26.7 V. The TPS923610's OVP sits at **24–25.5 V**, i.e. right on top of those
numbers — the TVS would be in or near conduction at the driver's normal open-load limit, leaking and
heating instead of sitting idle. The 5.2 pF of the CANFD part is tempting on the W−/C− lines, but not
at that price.

**The practical snag: DigiKey is at zero on PESD2IVN27-UX**, with 3,000 pcs due 29-Jun-2027. So:

* **For the DigiKey-primary BOM today**, the honest move is to keep **PESD2IVN-UX** (16,512 in stock,
  $0.49) and simply **add the NRND note** to the BOM — which is all BOM-06 actually asked for. It is
  buyable for years of hobby volume.
* **Change the prime MPN to PESD2IVN27-UX at the next revision**, when its stock lands. A web search
  today showed TTI (≈21,000 pcs) and Arrow/Mouser/Newark carrying it — **est.**, not confirmed live.
* **At JLC nothing changes today**: C42370511 (1,589) or C552498 for the 27 V part, versus the 2,955
  pcs of C42370512 you already specify. Both fine for a 10-board run.

Cost impact: essentially zero — $0.49 → $0.44 at DigiKey qty 1.

> **Open item I could not close.** The board wires **GND to pad 3** and the two protected lines to pads
> 1 and 2. I could not retrieve Nexperia's SOT-323 pinning table today (the datasheet PDF 404'd and
> timed out from two mirrors). Nexperia's 3-pin TVS arrays commonly put **GND on pad 2**. If that is
> the case here, D8 is mis-wired — you would have a clamp from C− to W− and one from GND to W−,
> instead of one from each line to GND — and the error would carry straight over to any replacement,
> because every candidate above shares the family pinning. **Five minutes with the PESD2IVN datasheet
> settles it. Do that before the next spin.**

---

## 4. BOM-02 — C4 / C6 / C32, 22 µF

### Fitted

`fabrication/part_fields.csv` line 4: **`CL21A226MAQNNNE`** (Samsung Electro-Mechanics), LCSC field
`C20416420`, JLC alternate "CCTC TCC0805X5R226M250FT".

Spec: 0805 (2012 metric), **22 µF, 25 V, X5R, ±20 %, 1.40 mm max height**.

DigiKey 2026-09-20: **Obsolete, 0 in stock.** Confirmed — the finding is right.
DigiKey's own suggested direct replacement, **CL21A226MAYNNNE**, is Active but **also 0 in stock**,
**61-week lead time**, $0.31 @ 1 / $0.18 @ 10, 1.45 mm max height. Also right.

Worth knowing: **LCSC C45783 is the genuine `CL21A226MAQNNNE` and it is a JLC *Basic* part**, 1,734,789
in stock at $0.1185. Your BOM currently points at the CCTC clone C20416420 instead. If you are
regenerating the BOM anyway, pointing at C45783 costs nothing, avoids a feeder fee, and makes the
LCSC field match the prime MPN exactly.

### Replacement

| MPN | mfr | spec | height | DigiKey | DK $1 / $10 | LCSC | JLC stock | JLC $ | class |
|---|---|---|---|---|---|---|---|---|---|
| **GRM21BR61E226ME44L** | Murata | 0805, 22 µF, 25 V, X5R, ±20 % | **1.45 mm** | **1,751,511, Active** | **$0.36 / $0.216** | **C86816** | 5,187 | $0.1081 | Ext |
| CC0805MKX5R8BB226 | Yageo | 0805, 22 µF, 25 V, X5R, ±20 % | est. 1.25 mm | *not fetched* (est.) | est. | C784585 | 11,464 | $0.3672 | Ext |
| CL21A226MAYNNNE | Samsung | 0805, 22 µF, 25 V, X5R | 1.45 mm | 0, 61 wk | $0.31 / $0.18 | — | — | — |
| KGM21AR51E226MU | KYOCERA AVX | 0805, 22 µF, 25 V | est. | 6,490 | **$1.30** | — | — | — |

**Recommendation: `GRM21BR61E226ME44L` (Murata).** Same case, same voltage, same dielectric,
**1.75 million in stock at DigiKey**, half the price of the Samsung part it replaces, and it has an
LCSC code. It is a like-for-like swap with a **+0.05 mm height** change (1.40 → 1.45 mm max), which
matters only against an enclosure floor — everything on this board is bottom-side, so check it once
against your case gap and forget it.

Keep Yageo `CC0805MKX5R8BB226` (C784585, 11,464 pcs) as the named second source. Skip the KYOCERA
part DigiKey suggests — $1.30 each is 3.6× the Murata.

### DC-bias derating

Neither manufacturer publishes a derating *table* in the datasheet; both publish the curve (Murata
SimSurfing, Samsung's own tool). For an 0805 25 V X5R 22 µF part the published family curve gives
roughly:

| bias | effective C | derating |
|---|---|---|
| 0 V | ~22 µF | — |
| 3.3 V | **~16–17 µF** | **≈ −25 %** |
| 5 V | **~14 µF** | **≈ −35 %** |

**Both figures are est.** — read off the published DC-bias family curve, not a datasheet table, and
not verified against a live SimSurfing session today.

The important point for you: **this is not a change in behaviour.** The Samsung part you fitted
derates essentially the same way — same case, same voltage rating, same dielectric class. Nothing
downstream needs re-sizing; you are replacing a dead MPN with a live one, not changing the circuit.

---

## 5. HMI-01 — one PPTC for expansion-header pin 12 (raw LiPo P+)

### Already in your BOM

F1 = **`0805L100WR`** (Littelfuse, 1.0 A hold, 0805), LCSC **C269106**, JLC alternate
"Brightking SMD0805B100TFT". Staying inside the Littelfuse 0805L family means one land pattern, one
manufacturer and one line-item habit.

### The two smaller members of the same family

| MPN | I_hold | I_trip | V_max | R_min | R1_max | DigiKey | DK $1 | LCSC | JLC stock | JLC $ |
|---|---|---|---|---|---|---|---|---|---|---|
| **0805L075WR** | **0.75 A** | 1.5 A | 6 V | **0.09 Ω** | **0.35 Ω** | in stock, Active | $1.06 | **C151146** | 1,925 | $0.1335 |
| 0805L050WR | 0.50 A | 1.0 A | 6 V | 0.15 Ω | 0.85 Ω | *not fetched* (est. stocked) | est. | C207022 | **14,896** | $0.1208 |

*(DigiKey qty-10 price for 0805L075WR was not shown on the results page — **est.**)*

### Recommendation: **`0805L075WR`**, LCSC `C151146`

Three reasons:

1. **Same family, same 0805 footprint as F1.** One footprint, one vendor, one datasheet — exactly the
   "cheap and convenient" test you set.
2. **Resistance.** This is the one that actually matters on a 3.0–4.2 V cell. At 0.5 A the 075 part
   drops **45–175 mV**; the 050 part drops **75–425 mV**. The 050's 0.85 Ω worst-case initial
   resistance is a lot to put in series with raw battery.
3. **6 V max working voltage** covers 4.2 V with plenty of margin, and 0.75 A hold sits above any
   sane header accessory while still being well under the pack protection's trip point.

Pick `0805L050WR` instead only if you decide the header should never pull more than ~250 mA — it
trips sooner and JLC has 8× the stock (14,896 vs 1,925). **Check C151146's stock before ordering**;
1,925 pcs is thin by JLC standards, though obviously fine for a 10-board run.

Cost: **+$1.06 per board at DigiKey qty 1, +$0.13 at JLC.**

### What it actually buys you (your question: "what does this do for the header?")

It does **not** enable hot-plug, and it does not protect the cell from a wiring mistake — the DW01A
already handles over-current on the pack side. What it adds is a **self-resetting limit on a
user-accessible pin**. Right now a paperclip, a reversed add-on board, or a shorted breadboard wire
on J6-12 has nothing between it and the raw cell except the protection IC's several-amp trip: the
connector, the track and the wire all carry that current until the DW01A decides. A 0.75 A PPTC turns
that from "pack protection trips and something gets hot" into "header goes high-impedance for a few
seconds, you unplug, it recovers". It is a $1 insurance policy on the one pin a stranger is most
likely to short.

---

## 6. USB-04 — CR1 numbers only, no recommendation to change

CR1 = **SMF6.5CA** (Littelfuse), SOD-123FL, on VBUS. LCSC **C19077501** (hongjiacheng SMF6.5CA),
**1,222,840** in stock at $0.0291, JLC **Preferred**.

| | SMF5.0A | SMF6.0A | **SMF6.5CA (fitted)** |
|---|---|---|---|
| Direction | unidirectional | unidirectional | **bi**directional |
| V_RWM | 5.0 V | 6.0 V | **6.5 V** |
| V_BR min / max | 6.40 / 7.00 V | 6.67 / 7.37 V | **7.22 / 7.98 V** |
| **V_C @ I_PP** | **9.2 V @ 21.7 A** | **10.3 V @ 19.4 A** | **11.2 V @ 17.9 A** |
| I_R @ V_RWM | 400 µA (some lots 800 µA) | 100–400 µA | 250 µA (some lots 75 µA) |
| P_PP (10/1000 µs) | 200 W | 200 W | 200 W |
| LCSC (stock, $) | C19077497 (969,692, $0.0273, Preferred); C193402 (402,983, $0.0277) | C2857264 (685,118, $0.0175); C19077499 (637,023, $0.0277, Preferred); C123790 | C19077501 (1,222,840, $0.0291, Preferred); C123793 (161,082, $0.0313) |

*(All three rows from the JLC library, 2026-09-20. V_BR/V_C/I_R figures are the Littelfuse SMF-series
datasheet values as mirrored in those listings; cross-check against Littelfuse's own PDF if a number
is load-bearing.)*

**What the table shows.** The lowest clamp available anywhere in this family is **9.2 V** (SMF5.0A) —
still **3.2 V above the 6.0 V absolute maximum** of the parts on VBUS. Going from 6.5CA to 5.0A buys
2.0 V of clamp and costs 1.5 V of standoff: USB-C VBUS is legal up to 5.5 V, so a 5.0 V-standoff part
sits in its leakage knee at the top of the legal range (400–800 µA at 5.0 V, and climbing steeply
above it). **No swap inside the SMF family gets the clamp under 6 V.** That is the whole answer to
USB-04: a TVS here is surge insurance, not overvoltage protection. Only a clamp / OVP load switch
would give you the latter, and that is a different conversation.

One number that looks alarming and isn't: the 250 µA leakage is specified **at V_RWM = 6.5 V**. CR1 is
on VBUS, which is 0 V whenever the reader is unplugged, so it contributes **nothing** to the 73 µA
sleep budget.

**No change recommended**, as briefed. 6.5CA remains the sensible choice for tolerance.

---

## Summary

| item | keep / change | recommended part | drop-in? | saving per board |
|---|---|---|---|---|
| **BOM-07** RTC U13 | **CHANGE** | Micro Crystal **RV-8263-C7-32.768kHz-20ppm-TA-QC**, LCSC C5137460 | **No** — SOIC-8 → 8-SON 3.2×1.5; footprint `Package_SON:MicroCrystal_C7_SON-8_1.5x3.2mm_P0.9mm` already ships with KiCad 9 | **+$12.21** (DK qty 1) / +$9.70 (qty 10) / +$1.35 (JLC) · also −2.8 µA sleep |
| ↳ accuracy-preserving variant | option | **RV-3032-C7** (±2.5 ppm, 0.21 µA), LCSC C5366550 | same new footprint | +$10.61 (DK qty 1) |
| ↳ zero-BOM option | option | delete U13, use ESP32-S3 internal RTC + SNTP on wake | n/a | +$13.85 — only if it syncs ≥ daily |
| **BOM-V01** 5× ESD arrays | **KEEP** | TPD4E1U06DBVR (LCSC C19829453 as now) | — | $0 by substitution; **+$2.80** by buying qty 100 at DigiKey instead of qty 1 |
| **BOM-06** D8 | **CHANGE (next rev)** | Nexperia **PESD2IVN27-UX**, LCSC C42370511 | **Yes** — same SOT-323, same family pinning | +$0.05; DigiKey stock is 0 until mid-2027, so keep PESD2IVN-UX + an NRND note for now |
| **BOM-02** C4/C6/C32 | **CHANGE (forced)** | Murata **GRM21BR61E226ME44L**, LCSC C86816 | **Yes** — same 0805, 25 V, X5R; +0.05 mm height | −$1.08 (DK qty 1, vs an unbuyable part) — it is a fix, not a saving |
| **HMI-01** new PPTC on J6-12 | **ADD** | Littelfuse **0805L075WR**, LCSC C151146 | new part, 0805 land like F1 | −$1.06 (DK qty 1) / −$0.13 (JLC) |
| **USB-04** CR1 | **KEEP** | SMF6.5CA (LCSC C19077501) | — | $0 — no SMF variant clamps below 6 V |

**Net effect on the DigiKey qty-1 BOM: about −$12.20 a board** (RTC saving, minus the new PPTC, plus
the forced capacitor swap), with the RTC also freeing ~11 mm² of board area and ~4 % of the sleep
budget.

### Things I could not confirm live — do these before ordering

1. ~~**Nexperia SOT-323 pinning for the PESD2IVN family**~~ — **RESOLVED, wiring is correct** (see the note at the top of this file). Original text: vs the board's pad 1 = C−, pad 2 = W−,
   pad 3 = GND. If GND is pad 2 on the real part, D8 is mis-wired today and the replacement would
   inherit it. *(datasheet PDF 404'd / timed out from two mirrors)*
2. **SRV05-4's exact pinout** — my "pin 5 = VCC" statement is the standard arrangement but was not
   read off the datasheet today. It only reinforces the "keep TPD4E1U06" conclusion, so it is not
   load-bearing.
3. **Pin-for-pin compatibility across RV-8263-C7 / RV-3028-C7 / RV-3032-C7.** The package is common;
   confirm the pin *functions* match before relying on the three-way second-source story.
4. **RV-8263-C7 DigiKey qty-10 price** — the page rendered "$0.1197 each", almost certainly $1.197.
5. **DC-bias derating figures** for the 22 µF parts — read off the published family curve, not a
   datasheet table.
6. **RX8025T-UB, PESD2IVN24-UX, 0805L050WR and CC0805MKX5R8BB226 DigiKey stock/price** — LCSC data
   confirmed, DigiKey side not fetched.
