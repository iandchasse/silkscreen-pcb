# BOM audit and diode orientation check (2026-11-12)

**Files audited:** branch `1.03` at `6a1b54a`: `production/jlc_bom.csv`, `production/positions.csv`,
`fabrication/part_fields.csv`, the schematic's netlist and the board. **JLC data:** JLC's parts API (library type, stock,
price tiers, listed attributes) and the EasyEDA symbols and footprints JLC places from, all read on 2026-11-12.
**The audit itself changed no design or production file;** swaps 1–3 were applied afterwards, the same day
([REV_1_03_STATUS.md §20](../REV_1_03_STATUS.md#20-review-findings-decisions-and-to-do-2026-11-12)). Prices and stock
move; re-check them on the order day.

## 1. Diode orientation against the JLC parts

**Method.** For every diode and TVS (`D2`–`D6`, `D8`, `CR1`–`CR3`) and the four-channel arrays (`U1`, `U6`–`U9`):

- where JLC's part has its cathode: from JLC's symbol (pin names, and which pin sits at the bar), its footprint marks,
  and the maker's datasheet where the symbol does not say;
- where our design needs it: the netlist's pad nets;
- what JLC will do with `positions.csv`: every part is on the bottom side, and the correct bottom-side rotation is
  (180 − board rotation − θ) mod 360, where θ turns KiCad's footprint onto JLC's land with JLC's cathode on our cathode
  pad. The same rule gives the rotations in `positions.csv` for `U3`, `Q1` and `Q4`, unchanged since the working Rev 1.0
  boards, and for `U2` and `U5`, which Rev 1.01 corrected to match JLC's footprints
  ([CHANGELOG](../CHANGELOG.md#rev-101-never-built)). It also gives 270 for TI's `U12` in §2.1.

| Ref | JLC part | Kind | JLC cathode | Our cathode pad | `positions.csv` | Verdict |
|---|---|---|---|---|--:|---|
| `D2` | YLED1206R `C28310439` | red LED | pin 2 (datasheet: pin 1 "+", the cathode mark at pin 2) | pad 1 (`Net-(D2-K)` → `R59` → GND) | 90 | **Correct, because of its `FT Rotation Offset` of 180** (added in Rev 1.01 with the other JLC rotation corrections; Rev 1.0's file had 270). KiCad numbers an LED's cathode 1; this part numbers its anode 1. Do not remove the offset |
| `D3` | SMAJ26A `C19077543` | unidirectional TVS | pin 1 (symbol "K") | pad 1 (`LED_SW`) | 0 | Correct |
| `D4` `D5` `D6` | B5819W SL `C8598` | Schottky | pin 1 (symbol "−") | pad 1 (the `D4`/`D6` node, `PREVGH`, GND) | 90 / 90 / 180 | Correct; the e-paper charge pump works on Rev 1.0 with the same rows |
| `D8` | PESD2IVN-UX `C42370512` | dual bidirectional ESD | pin 3 is the common pin (datasheet) | pad 3 = GND; pads 1, 2 = `C-`, `W-` | 180 | Correct (its `FT Rotation Offset` of 180, added in Rev 1.01, is right) |
| `CR1` | SMF6.5CA `C19077501` | bidirectional TVS | — | pad 1 `VBUS_PRE_FUSE`, pad 2 GND | 0 | Correct either way round; land matches |
| `CR2` `CR3` | SD05C-01FTG `C5299440` | bidirectional TVS | — | pad 1 the rail, pad 2 GND | 90 / 0 | Correct either way round |
| `U1` `U6`–`U9` | TPD4E1U06DBVR `C19829453` | 4-channel array | GND is pin 2 (JLC symbol) | pad 2 = GND | 270 / 0 / 0 / 90 / 270 | Correct |

**All correct.** In JLC's placement preview, the marks to look at are `D2`'s cathode mark on the pad toward `R59`,
`D3`'s band on the `LED_SW` pad at (95.45, 58.80), and the `D4`–`D6` bands on pad 1. JLC's footprint for `D2` also
carries a pin-1 dot at its pad 1, which on this LED is the **anode** (datasheet: ① "+", the diode symbol pointing to ②,
the green cathode marks at the ② end; JLC's silkscreen bar is at its pad 2). So if the preview shows that dot, it belongs
on the `USB_VBUS` end, away from `R59`; do not "correct" it onto pad 1. Rev 1.0's file had no offset and would have put
the anode on pad 1, yet `D2` lit on a Rev 1.0 board ([BOARD_FAILURES.md](../BOARD_FAILURES.md)), so that order's
placement was corrected before assembly; Rev 1.01's offset builds the same correction into the file. On the first
article, `D2` lights with USB plugged in.

## 2. BOM audit

**Method.** Every coded line of `production/jlc_bom.csv` (70 lines, 170 placed parts) was looked up on JLC: 29 Extended,
4 Preferred, 37 Basic (the resistors and most capacitors). Each Extended line was searched for alternatives: for the
passives, protection parts, discretes, logic and connectors, a Basic or Preferred part with the same package and spec;
for every line, a cheaper code of the same part; and for each line under about 10,000 in stock, same-footprint parts of
any type. The one exception is `U14`, a single-source part with `U13` as its documented fallback. Savings use
[BOM.md](../../fabrication/BOM.md#cost)'s model: SMD lines bought with 3 % + 4 spares, $1.50 per Extended type per order,
nothing for Basic or Preferred.

### 2.1 Recommended (BOM-only: same footprint, same function, no rotation change)

**Approved by the owner and applied on 2026-11-12.** The rows, steps and checks are in
[REV_1_03_STATUS.md §20.3](../REV_1_03_STATUS.md#203-to-do-agreed-and-done-2026-11-12).

| # | Line | Now | Proposed | Why | Saving per board at 5 / 10 / 30 / 100 boards |
|---|---|---|---|---|---|
| 1 | `C38` (`TS` capacitor) | Yageo CC0603KRX7R9BB224 `C107083`, 50 V, **Extended** | **Samsung CL10B224KA8NNNC `C21120`**, 0.22 µF 25 V X7R ±10 % 0603, **Basic**, 815k in stock | Removes one Extended fee. 25 V is ample: `TS` self-clamps at about 2.0 V ([BQ21040 audit, lens A](../audit-2026-11-07/lens-A-ic-power-path.md)) | $0.31 / $0.16 / $0.05 / $0.02 |
| 2 | `F2` (`J6` pin 12 fuse) | Littelfuse 0805L075WR `C151146`, **1,717 in stock**, $0.146 | **Brightking SMD0805B075TF `C269105`**, 65k in stock, $0.027 | JLC lists the same numbers: 0.75 A hold, 1.5 A trip, 6 V, 40 A, 600 mW, 200 ms, 90–350 mΩ. `F1` already went from Littelfuse to Brightking the same way | $0.24 / $0.18 / $0.14 / $0.10 |
| 3 | `U12` (inverter) | MDD 74LVC1G04GV `C53185133`, **2,908 in stock** | **TI SN74LVC1G04DBVR `C7827`**, 58.7k in stock, cheaper | The genuine TI part. Same pins (1 NC, 2 A, 3 GND, 4 Y, 5 VCC); JLC's land gives the 270° already in `positions.csv`, with no offset. The MDD part has no JLC footprint model, so this also makes `U12`'s placement checkable | $0.02 / $0.01 / $0.01 / $0.01 |

**Together:** $0.56 / $0.35 / $0.20 / $0.12 a board at 5 / 10 / 30 / 100 boards, one Extended type fewer (29 → 28), and
two thin-stock lines gone.

**Note on #3:** HARDWARE.md §16's sleep budget gives `U12` a 4 µA maximum, Nexperia's limit, because the fitted MDD clone
publishes none. With TI's part the documented limit is 10 µA, so that row's maximum becomes 10 µA; the typical figure
(0.1 µA) does not change.

### 2.2 Optional (small savings, a judgment call)

**Recorded for reference on 2026-11-12, not planned.**

| # | Line | Now → proposed | Notes | Saving per board at 5 / 10 / 30 / 100 |
|---|---|---|---|---|
| 4 | `C9` `C11` `C13`–`C17` (×7) | Samwha CS2012X5R475K500NRE `C513770` → **Samsung CL21A475KBQNNNE `C98192`** | Same 4.7 µF 50 V X5R ±10 % 0805, and Samsung's is the part the schematic already names (its MPN field). Samwha's code was used because it was cheaper when chosen ($0.045 against $0.077); Samsung's is now the cheaper ($0.045 against $0.058). Before taking it, compare Samsung's published DC-bias curve with the assumption behind `C9` (frontlight boost output, 15–24 V; [BOM.md "C9: 4.7 µF"](../../fabrication/BOM.md#c9-47-µf)) | $0.11 / $0.10 / $0.07 / $0.06 |
| 5 | `D8` | TECH PUBLIC PESD2IVN-UX `C42370512` (2,856 in stock) → **GOODWORK PESD1CAN-U `C50581526`** (12k) | Same pinout (datasheet: pin 3 common, pins 1 and 2 bidirectional), same 24 V standoff and 28 V breakdown; clamp 35 V against 30 V (`Q5`/`Q6` are 50 V parts). Leakage limit 1 µA against 0.2 µA: with one colour lit, the other string's cathode is held only by its switched-off `Q5`/`Q6` and `D8`, so at the limit that string could carry about 1 µA (a faint glow in the dark is conceivable; typical leakage is far lower) | $0.07 / $0.06 / $0.04 / $0.03 |
| 6 | `D4`–`D6` | B5819W SL `C8598` (Basic) → **MDD B5819W `C64885`** (Preferred) | Both fee-free; already noted in BOM.md | $0.03 / $0.02 / $0.02 / $0.00 |

With 2.1, all three: $0.77 / $0.52 / $0.34 / $0.22 a board.

### 2.3 Supply: lines under about 10,000 in stock, and their fallbacks

| Line | Code | JLC stock (2026-11-12) | Per board | BOM-only fallback |
|---|---|--:|--:|---|
| `U10` TPS923610DRLR | `C52919131` | **77** | 1 | The documented swap, TPS923611DRLR `C52919130` with `D3` → SMAJ33A (for example `C353454`, 88k), has only **46**. Neither covers a batch: pre-order through JLC's parts manager or consign. The biggest supply risk on the board |
| `J6` 2×6 right-angle socket | `C5333437` | **324** | 1 | Hong Cheng HC-PM254-8.5H-2x6PW `C22373932` (9.4k, $0.20). Compare its drawing first (body offset from the pins, height) with `J6`'s footprint and courtyard |
| `U14` RV-8263-C7 | `C5137460` | 943 | 1 | Fit `U13` instead (DS3231MZ+TRL `C107410`), as documented |
| `F2` | `C151146` | 1,717 | 1 | Recommended swap #2; done on 2026-11-12 (`C269105`) |
| `D8` | `C42370512` | 2,856 | 1 | Optional swap #5 |
| `U12` | `C53185133` | 2,908 | 1 | Recommended swap #3; done on 2026-11-12 (`C7827`) |
| `L1` 47 µH, 5 × 5 mm | `C206267` | 3,146 | 1 | cjiang FNR5040S470MT `C167974` (35k, 354 mΩ) or Sunlord SWPA5040S470MT `C86617` (16.7k). Same size; check their pads against `L_APV_ANR5040` first |
| `U1` `U6`–`U9` TPD4E1U06DBVR | `C19829453` | 3,571 (714 boards) | 5 | TECH PUBLIC TPD4E1U06DBVR-TP `C2841427` (5.6k): the same listed specs and price under a second code. TI's own `C124691` (20.5k) costs four times as much |
| `F1` | `C269106` | 5,491 | 1 | LUTE 0805L100/12AR `C7472575` (59k) or Littelfuse 0805L100WR `C80270`; compare the specs first |
| `U11` BQ21040DBVR | `C202311` | 7,657 | 1 | TI BQ21040DBVT `C78978`: the same chip on a 250-piece reel (266 in stock) |
| `J2` FH34SRJ-24S | `C324726` | 8,036 | 1 | Hirose only |
| `J5` A2001WR-2P | `C48579993` | 9,259 | 1 | — |

`SW1`–`SW5`, `SW7`–`SW11` (TS365ZJ, 10 a board) have 20.8k, about 2,000 boards' worth.

### 2.4 Looked at and not recommended

- **`U1` `U6`–`U9` → hongjiacheng SRV05-4 `C7420376` or SRV05-4A `C20615829`** (Preferred: one Extended fee fewer, and
  up to $0.21 a board on the parts). Pin 5 is VDD on these and NC on the TPD4E1U06, so it would float here, and their
  leakage limit is 5 µA a channel against 10 nA. `U8`'s two I²C lines are pulled up and sit high in deep sleep, so on
  paper they alone could add 10 µA to a sleep floor of about 46 µA typical (HARDWARE.md §16).
- **`F3`–`F6` → cheaper 0603 PTCs** (for example TECHFUSE SMD0603-010-24V `C70048`, $0.04). `F3`'s trip time was modelled
  on the Bourns part's resistance and thermal data ([BENCH_THEORY §2](../audit-2026-11-03/BENCH_THEORY.md#2-frontlight-ptc-f3-n1));
  another PTC would void that.
- **`TH1` → APV ANTC1608-103F3380FB `C52155402`** (the same listed 10 kΩ ±1 % and B 3380 K ±1 %; $0.02–0.05 a board). The
  `TS` window was computed on Murata's curve, and Murata is the reference maker. Not worth it.
- **`C9` group → Chinocera `C7472969` or HRE `C6119903`** ($0.031–0.033): unknown DC-bias behaviour at `C9`; Samsung (#4) is
  the better swap if any. JLC's one Basic 4.7 µF 50 V part is a 1206.
- **`D2` → XINGLIGHT XL-3216SURC `C965822`**: still Extended (JLC's Basic red LEDs are 0603 and 0805, none 1206), and saves
  under a cent.
- **`Q4` IRLML6346 → clones** (UMW `C5340724`, $0.045): BOM.md requires the genuine Infineon part.
- **`U5` DW01A and `Q1` FS8205A → cheaper clones** (DW01A from $0.020 against $0.053, for example JSMSEMI `C39846919`;
  8205A from $0.022 against $0.050, for example TF8205A `C43121680`; about $0.03 a board each). The over-current window
  in HARDWARE.md §3.3 (0.83–1.68 A) was worked out from the fitted PUOLOP DW01A's thresholds and the FETs' R_DS(on) in
  series with `R85` ∥ `R86`, and both codes are the ones on the working Rev 1.0 boards. A swap would mean redoing that.
- **`J7` TF PUSH socket → Minlenda MLD-TF PUSH-H18 `C52750848`** ($0.042 against $0.067, 17k in stock): another maker's
  socket, whose land would need checking against `J7`'s footprint, for about $0.02 a board.
- **The ten TS365ZJ switches → TS365CJ `C557597`** ($0.026 against $0.063, about $0.37 a board): a different body (JLC
  lists 6 mm against 7.3 mm, and 30,000 cycles against 50,000) with 1,069 in stock, while the switch footprints and the
  levelled side buttons were set with the TS365ZJ. Not a BOM-only change.
- **`U3`**: `C404027` is already the cheapest TLV75533 code on JLC, and the LDO's quiescent current is the largest term in
  the sleep budget (HARDWARE.md §16), so another LDO would be a design change.
- **The ESP32 module, TPS2116, BQ21040, the Hirose FPC connectors (`J2`–`J4`), `J1` and `L2`:** no cheaper code of the same
  part worth taking. `J1`'s only other code is another maker's with 1.4k in stock, for under a cent (`J1` has 1.07M), and
  JLC has no Basic or Preferred 10 µH inductor in `L2`'s 2520 size.

## 3. To apply a swap

- `fabrication/part_fields.csv`, then `python fabrication/apply_part_fields.py --write` with KiCad closed.
- `production/jlc_bom.csv` by hand, then the Toolkit's `production/bom.csv` and `production/other_fabs/`
  (`fabrication/make_fab_files.py`). `positions.csv` does not change: none of these needs a rotation change.
- `fabrication/BOM.md` (tables, cost, thin-stock list), `fabrication/BOM_handbuild_digikey.csv`, and for #3
  HARDWARE.md §16's `U12` row.
- In JLC's placement preview, check the swapped parts as usual.
