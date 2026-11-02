# Protection follow-up: cheap wins, battery path, microSD, charge current, test points (2026-11-02)

Follow-up to [DURABILITY_AUDIT.md](DURABILITY_AUDIT.md) section 3. The decisions taken here are collected as a checklist in [NEXT_REVISION.md](../NEXT_REVISION.md). It answers four questions:

1. What do the cheap PTC wins (`R42`, `J6` pin 7) cost, and which faults do they actually contain?
2. Can the battery path and the microSD supply be protected?
3. Should the charge current come down using a resistor already in the BOM?
4. For every protected location, which nets do you probe, powered and unpowered, and where should test pads go?

**Method.** I used the electro-thermal PTC model from [PTC_THERMAL.md](PTC_THERMAL.md), generalised so it can fit any PTC from its datasheet ([ptc-thermal/branches.py](ptc-thermal/branches.py)). It was fitted to 17 parts and run against two kinds of source:

- **3V3 branches:** fed by `U3`'s current limit. That limit is 0.56 / 0.72 / 0.87 A, folding back to 0.355 A below 1.32 V.
- **The battery path:** the cell behind 0.40 Ω, with the board's own 40 mA flowing through the PTC.

In every case the short sits away from the PTC, so the PTC sees ambient temperature. The `DW01A` sense-resistor option is worked by hand in [ptc-thermal/battery_sense.py](ptc-thermal/battery_sense.py).

Two things about the inputs:

- **Part data.** All part data was re-verified on 2026-11-02 and is stored in [ptc-thermal/parts_sourcing.json](ptc-thermal/parts_sourcing.json). The JLC figures were read live from the parts' own pages; the DigiKey figures come from web search, because DigiKey blocks direct fetches.
- **Limits of the model.** These are models fitted to datasheets, not measurements. Each PTC is bounded by its Rmin and R1max, meaning the lowest-resistance part as delivered and the highest-resistance part an hour after a trip.

## 0. Summary

| Location | Change | Added cost (JLC / DigiKey) | What it contains | Verdict |
|---|---|---|---|---|
| Touch `J4` (`R42`) | `R42` 0 Ω becomes MF-FSMF010X-2, same 0603 pads | +$0.058 / +$0.54 (no new placement) | Trips shorts up to 10 Ω (25 °C) or 6 Ω (−20 °C) in the flex, the connector or the touch controller. The worst short it never stops takes 0.78 W, down from 2.27 W today. The rest of the board recovers once it trips. | **Do** (decided 2026-11-02) |
| `J6` pin 7 (3V3 out) | MF-FSMF010X-2 in series, a new 0603 in the existing 4.8 mm trace | +$0.058 / +$0.54 plus one placement | Same as the touch row, for accessories, whiskers and probe slips. Budget 20 mA per accessory on pin 7. | **Do** (decided 2026-11-02) |
| Battery path, PTC in place of `R27` | — | — | Nothing useful. Any PTC that survives the 0.6 A peaks without browning out the board is too low in resistance to trip. 0.75 A parts still leave 4.3–5.8 W and raise the brownout point from 3.44 V to 3.63–3.82 V. | **Reject** |
| Battery path, `DW01A` sense resistor | 68 mΩ between `Q1` pin 3 and GND, and `C34` changed from 2.2 nF to 0.1 µF | 1206 68 mΩ: +$0.029 / +$0.33; `C34` moves to an existing BOM line | Sure-trip range goes from shorts below 0.25 Ω to shorts below 1.32 Ω. The worst never-tripped short drops from 5.2 W to 3.0 W. You also get a 68 mV/A battery-current test point for free. | **Do** (decided 2026-11-02) |
| microSD (`SD_VDD`) | No PTC. Firmware: brownout plus SD flag means the card stays off. Move `C36`/`C37`. | $0 | A short low enough to brown out the board (about 3–5 Ω or less) is already cut, because `R40` turns `Q7` off at reset. Firmware keeps it off. Higher-resistance shorts are left; the firmware's mount-failure power-off covers those. | **Do** (decided 2026-11-02, including the `C36`/`C37` move) |
| Charge current | `R6` changed from 4.7 kΩ to 10 kΩ (the existing `C25804` line) | Saves one BOM line | Halves `U11`'s heat (0.5 W to 0.26 W worst case) beside `U3`, and keeps a small cell at 0.25 C or less. | **Do** (decided 2026-11-02) |
| E-paper boost feed (`L1`/`C10`) | MF-FSMF010X-2 between the 3V3 trunk and a new net `EINK_3V3` | +$0.058 / +$0.54 plus one placement | `C10` and the `Q4`/`R14`/`C14` boost section (case 2's top two suspects). A `Q4` short trips in 0.8 s or less at 25 °C, where today it holds 1.4 W in `R14` indefinitely (section 7) | **Do** (decided 2026-11-02) |
| E-paper panel logic supply (`J2` pins 15/16) | Fed from `EINK_3V3` | $0 (shares the boost PTC) | A cracked panel or COG, or a pinched FPC, shorting `VCI` | **Do** (decided 2026-11-02) |
| `CR2` (`J6` pin 7 TVS) | Move it to the pin side of the `J6` PTC, as `CR3` already sits after `F2` | $0 | A TVS that failed short after an ESD hit | **Do** (decided 2026-11-02) |

**Overall cost** (prices as of 2026-11-02; JLC fees are $3 per unique Extended part per order and $0.0017 per SMT joint):

| Change | JLC per board (1–99 / 100+) | New joints | DigiKey per board (1 / 100) |
|---|---|---|---|
| 4 × MF-FSMF010X-2 (frontlight, touch, `J6` pin 7, e-paper; `J2` shares the e-paper one) | $0.232 / $0.194 | 6 (the touch PTC reuses `R42`'s pads) | $2.16 / $1.28 |
| `Rs` RL1206FR-070R068L | $0.029 | 2 | $0.33 / $0.11 |
| `R42` 0 Ω removed | −$0.0005 | — | — |
| `C34` 2.2 nF to 0.1 µF, `R6` 4.7 kΩ to 10 kΩ | about $0 (both Basic; `R6` drops a BOM line) | — | about $0 |
| `CR2`, `C36`/`C37` moves, 13 test pads and vias, new traces | $0 (JLC does not price vias, and the pads take no paste) | — | $0 |
| Assembly, 8 joints | $0.014 | — | — |
| **Per board** | **$0.27 / $0.24** | | **$2.49 / $1.39** |
| **Per order** | **+$6** (two new Extended parts) plus a few attrition spares (about $0.30) | | — |

**Per-board total at JLC, including the per-order fees:**

| Order size | Extra cost per board |
|---|---|
| 5 boards | $1.50 |
| 10 boards | $0.90 |
| 50 boards | $0.40 |
| 100 boards | $0.30 |

**Cheaper variants:**

- **Use two 0.1 Ω JLC Basic resistors for `Rs`** (`C25334` in parallel, section 3.2). That removes one $3 fee, for about $0.92 a board at 5.
- **Hand-built from DigiKey:** MF-PSMF010X-2 (0805) in place of MF-FSMF010X-2 brings the parts to $1.85 / $0.99 per board.

## 1. Sourcing corrections (2026-11-02)

- **JLC stock was read from the wrong field earlier.** The first `stockCount` on a JLC part page belongs to the "related parts" list. The real stock is `overseasStockCount` in the main part's record.
  - MF-FSMF010X-2 (`C210355`): 26 658 in stock, not "70 700".
  - MF-PSMF010X-2 (`C116171`): 95 608 in stock. The "10 pcs" that ruled it out earlier was the same mistake.
- **DigiKey stock for MF-FSMF010X-2 is unconfirmed.** Two searches on 2026-11-02 disagreed: about 102 000 in stock versus backorder. Check before ordering. MF-PSMF010X-2 is stocked at both and is the drop-in alternate. It is 0805, so check its footprint before swapping, and it is slower (section 2).

| Part | Size | Hold / trip | Rmin / R1max | JLC | DigiKey |
|---|---|---|---|---|---|
| MF-FSMF010X-2 | 0603 | 0.10 / 0.30 A | 0.9 / 6.0 Ω | `C210355`, Ext, 26 658, $0.058 | 118-MF-FSMF010X-2CT-ND, $0.54 / $0.32 @100, stock unconfirmed |
| MF-PSMF010X-2 | 0805 | 0.10 / 0.30 A | 1.0 / 7.5 Ω | `C116171`, Ext, 95 608, $0.052 | MF-PSMF010X-2CT-ND, about 31 000, $0.38 / $0.22 @100 |
| 0603L010YR (Littelfuse) | 0603 | 0.10 / 0.30 A | 0.9 / 6.0 Ω | `C207010`, Ext, 11 967, $0.156 | F2900CT-ND, about 109 000, $1.43 / $0.84 @100 |

## 2. Cheap wins: touch supply and `J6` pin 7

**Where.**

- **Touch:** `R42` (0603, 3V3 to `J4` pin 2 `/PIN_2`) becomes the PTC on its own pads. In the alternate touch mapping, fit the PTC in `R66` instead (3V3 to pin 4; HARDWARE.md section 8).
- **`J6` pin 7:** a new 0603 in the single B.Cu 3V3 segment from (92.1, 42.1) to pin 7 at (88.7, 45.4). Keep its pads thermally light, the same as the frontlight PTC: no pour, and 0.25 mm traces. The rail clamp `CR2` (89, 59) stays on the board side, so ESD on pin 7 reaches the rest of 3V3 only through the PTC and `CR2`.

**Fault containment.** A short of R ohms at the far end of the branch (flex, controller, accessory), running for 120 s, compared across all three `U3` limit corners. The results did not depend on the limit corner.

| Ambient | Part | Trips shorts up to | Worst never-tripped short | Slowest trip | Power left after a trip | 3V3 below 3.0 V |
|---|---|---|---|---|---|---|
| −20 °C | FSMF010X, 0.9 Ω / 6.0 Ω | 6 / 8 Ω | 1.24 / 0.69 W (at 8 / 10 Ω) | 12 s | ≤ 0.16 W | up to 12 s, shorts ≤ 4 Ω |
| 25 °C | FSMF010X, 0.9 / 6.0 Ω | 10 / 12 Ω | 0.78 / 0.36 W | 11 s | ≤ 0.13 W | up to 1.0 s |
| 45 °C | FSMF010X, 0.9 / 6.0 Ω | 12 / 15 Ω | 0.61 / 0.25 W | 6 s | ≤ 0.08 W | up to 0.4 s |
| 25 °C | PSMF010X, 1.0 / 7.5 Ω | 6 / 8 Ω | 1.07 / 0.34 W | 3 s | ≤ 0.12 W | up to 1.4 s |

For comparison, today any short of 1.5 Ω or more sits at `U3`'s limit. A 3–4 Ω short there takes 2.27 W, and the whole board is down for as long as it lasts.

**Two effects of the trip:**

- **The board recovers.** A short of 4 Ω or less browns out the ESP32 until the PTC trips. After that the rest of 3V3 recovers and the board boots normally, with only touch or the accessory dead.
- **The fault becomes visible to firmware.** The touch controller or accessory stops answering on I²C while 3V3 is normal.

**Faults it covers:**

- A pinched or cracked touch flex.
- A shorted touch controller.
- ESD damage on `J4` that leaves pin 2 low-ohmic. `U7` clamps the signals, not the supply.
- An accessory or cable miswired on pin 7.
- A probe slipping from pin 7 to pin 1 (GND) or to pin 8.
- A solder whisker on the header.

**What it does not cover:** shorts above about 10–15 Ω. These take 0.36 W or less at 3.3 V and are close to harmless.

**Normal-use drop** (steady load for 30 min, then the drop across the PTC):

| Load | FSMF010X 0.9 Ω, 25 / 45 / 60 °C | FSMF010X 6.0 Ω, 25 / 45 / 60 °C |
|---|---|---|
| 5 mA (touch active) | 5 / 7 / 9 mV | 31 / 47 / 63 mV |
| 20 mA | 19 / 28 / 38 mV | 127 / 191 / 259 mV |
| 50 mA | 48 / 71 / 97 mV | 350 / 556 / 818 mV |
| 80 mA | 78 / 119 / 164 mV | 728 mV / **trips** / **trips** |

The touch controller is no issue. For `J6` pin 7, publish **20 mA** as the 3.3 V accessory budget (0.26 V or less at 60 °C). Anything heavier should use `P+` on pin 12, as HARDWARE.md section 11 already advises.

## 3. Battery path

### 3.1 PTC in place of `R27`: rejected

`R27` carries everything the cell feeds plus the 0.23–0.26 A charge current. Results (charge current held for 30 min, then a 0.6 A board peak on top; fault sweep over 3.4/3.7/4.2 V, −20/25/45 °C, both resistance corners):

| Part | Lowest cell that survives a 0.6 A peak, 25 / 60 °C (today 3.44 V) | Trips shorts up to (25 °C, 3.4 V) | Worst never-tripped short, all corners |
|---|---|---|---|
| MF-FSMF050X-2 / MF-PSMF050X-2 | **4.05–4.09 / 4.59–4.73 V** | 2 Ω | 4.3–4.5 W |
| MF-PSMF075X-2, MF-NSMF075-2, 1206L075THYR | 3.63–3.70 / 3.77–3.82 V | 1.5–2 Ω | 5.8 W |
| 0805L100WR, 0805L110WR, MF-NSMF110-2, 1206L110THYR | 3.54–3.57 / 3.61–3.67 V | 1 Ω | 7.0–8.7 W |

Some context on these results:

- The `DW01A` already trips anything below about 2.5 Ω, so most of each PTC's tripping range overlaps it.
- Whatever extra range a PTC adds costs the bottom 10–40 % of the cell's charge to brownout.

The physics: to trip, a PTC must heat itself (I²R). The only parts with enough resistance to do that on a 3–10 Ω short drop too much voltage at the board's own 0.6 A peaks.

### 3.2 `DW01A` sense resistor: the lean

The `DW01A` opens the discharge FET when V(CS) − V(B−) exceeds 120 / 150 / 180 mV for 10–20 ms. Today CS sees only `Q1`'s two channels plus about 10 mΩ of `B−` trace inside the sense loop (BAT-08). I took that as 39–84 mΩ:

- **Low corner:** 0.8 × typical R_DS(on) at a 4.2 V gate.
- **High corner:** maximum R_DS(on) at a 3.0 V gate, at 60 °C.

A resistor `Rs` from `Q1` pin 3 (S2) to the GND pour adds to that:

- `Q1` pin 3 currently lands directly in the pour, so the only layout change is to isolate that one pad and route it to GND through `Rs`.
- `R16` already lands on the pour, i.e. after `Rs`, so the CS reference works without rerouting `R16`.

| `Rs` | Trip current min / typ / max | Margin over the 0.6 A peak | Drop at 0.6 A | Always trips shorts ≤ | Never trips shorts ≥ | Worst never-tripped short | CS spike at cell insertion, `C34` 2.2 nF / 0.1 µF (`V_SIP` ≥ 1.0 V) |
|---|---|---|---|---|---|---|---|
| none (today) | 1.42 / 2.43 / 4.59 A | 2.37× | 0 | 0.25 Ω | 2.56 Ω | **5.16 W** | 0.58 / 0.04 V |
| 50 mΩ (2 × 0.1 Ω Basic) | 0.89 / 1.34 / 2.02 A | 1.49× | 30 mV | 1.04 Ω | 4.26 Ω | 3.39 W | 0.84 / 0.06 V |
| **68 mΩ** | **0.79 / 1.16 / 1.68 A** | **1.31×** | **41 mV** | **1.32 Ω** | **4.87 Ω** | **3.02 W** | 0.92 / 0.06 V |
| 82 mΩ | 0.72 / 1.04 / 1.49 A | 1.20× | 49 mV | 1.54 Ω | 5.34 Ω | 2.78 W | 0.98 / 0.07 V |
| 100 mΩ | 0.65 / 0.93 / 1.29 A | 1.08× | 60 mV | 1.82 Ω | 5.96 Ω | 2.52 W | 1.05 / 0.08 V |

The 5.16 W "today" figure uses this wider `Q1` range. It replaces the 6.8–7.9 W estimate in DURABILITY_AUDIT section 2.

**Recommendation.** Use a 68 mΩ, 1 %, 1206 resistor:

- JLC: RL1206FR-070R068L, `C327066`, Extended, about 4 700 in stock, $0.029.
- DigiKey: 311-.068LWCT-ND, more than 23 000 in stock, $0.33 / $0.11 at 100.

Change `C34` from 2.2 nF to 0.1 µF. That moves it to the existing `C14663` line, so no new BOM line. **The `C34` change is required with any `Rs`**:

- **Why:** without it, the cell-insertion spike reaches 0.84–1.05 V against the `DW01A`'s 1.0 V short-circuit threshold.
- **Effect:** with it the spike is 0.06 V. The 100 µs filter is negligible next to the 10–20 ms over-current delay.

**Ratings.**

- **Steady:** the worst sustained current just under the trip point is 1.68 A, which puts 0.19 W into the resistor (rated 0.25 W).
- **Short-time:** a hard short (about 8 A for at most 20 ms) is roughly 90 mJ, far inside the 5 s overload rating (about 1.5 W for 5 s).
- **If it fails open:** the board disconnects from the cell, which is fail-safe.

**Two cheaper or more aggressive variants:**

- **No extra Extended fee:** two 1206W4F100LT5E in parallel (`C25334`, JLC Basic, $0.008 each). That gives 50 mΩ: 3.39 W worst case and 1.49× margin, at the cost of one extra placement.
- **More coverage:** 82 mΩ (RL1206FR-070R082L, `C705560`; DigiKey 13-RL1206FR-070R082LCT-ND). Use it only after measuring that the real coincident peak stays under 0.5 A.

**Limits.**

- **The window only shrinks.** A 4.9–30 Ω short on `P+` still runs, at up to 3 W.
- **A nuisance trip latches the board off on battery** until USB is plugged in (existing `DW01A` behaviour). So the 1.31× worst-corner margin assumes Wi-Fi TX, an SD write and the frontlight do not all run at once for 10 ms or more. Measure the coincident peak on the `Rs` test point (section 6) before committing.
- **Charge current** flows backwards through `Rs`: −18 mV at 0.26 A, harmless. The `DW01A` has no charge over-current function.

### 3.3 Sense resistor: implementation and bench check

**Schematic.**

- `Q1` pin 3 (S2, the charge-FET source) moves from `GND` to a new net `B-_SENSE`.
- `Rs` goes from `B-_SENSE` to `GND`, with TP7 on `B-_SENSE`.
- `R16` stays on `GND`, `C34` stays from CS to `B−` but becomes 0.1 µF, and nothing else changes.

```
cell− ── B− ──[Q1 pin 1 │ FET1 (OD) │ FET2 (OC) │ pin 3]── B-_SENSE ──[ Rs 68 mΩ ]── GND (pour, board, USB, P− side)
                                                             TP7                      │
U5 GND pin ── B−                                                               R16 1 kΩ
U5 CS  ──────────────────────────────────────────────────────────────────────── CS ──┘
C34 0.1 µF: CS to B−      →  V(CS) − V(B−) = I_discharge × (R_Q1 + Rs)
```

**Layout (Rev 1.02 coordinates, B.Cu).**

- **Isolating pin 3.** `Q1` pin 3 (85.1, 71.05) currently lands straight in the GND pour. Once its net changes, the zone fill isolates it automatically.
- **Where `Rs` fits.** The free pocket is just above and left of pin 3, about x 83.4–86.4 by y 68.9–70.4. Its edges:
  - `UNUSED_GPIO_45` runs diagonally through it, from (84.78, 68.42) to (83.63, 69.57). It is an unused GPIO routed to `J6` pin 3, so it can move.
  - The `B−` jog runs from (86.44, 70.56) to (87.6, 69.4).
  - A GND via sits at (86.4, 68.8).
- **Which footprint fits.**
  - An 0805 sits there horizontally once GPIO45 is nudged.
  - A 1206 also needs the `B−` jog moved by about 0.5 mm.
- **Copper.**
  - Pin 3 to `Rs`: 0.4 mm or wider and as short as possible.
  - `Rs` to GND: at least two vias, reusing the via at (86.4, 68.8).
- **`R16`.**
  - `R16` (85.36, 80.2) can stay on the pour. The pour's few mΩ between `Rs` and `R16` shifts the threshold by about 2 %.
  - A dedicated trace from `R16` pad 1 to `Rs`'s GND pad makes it exact.

**Parts.**

| Choice | JLC | DigiKey | Notes |
|---|---|---|---|
| 68 mΩ 1206 (lean) | RL1206FR-070R068L, `C327066`, Extended, about 4 700 in stock, $0.029 | 311-.068LWCT-ND, more than 23 000, $0.33 / $0.11 @100 | same MPN at both; 0.25 W |
| 68 mΩ 0805 (if the 1206 doesn't fit) | 0805W4F680MT5E, `C52472`, Extended, 2 443 | RL0805FR-7W0R068L, about 15 000, $0.53 | different MPN at each distributor (same value and 0.25 W) |
| 50 mΩ, no extra Extended fee | 2 × 1206W4F100LT5E, `C25334`, **Basic** | 2 × RL1206FR-070R1L, 311-0.1LWCT-ND | 1.49× margin, 3.4 W worst case; needs room for two |
| `C34` 0.1 µF | `C14663` (already the `C7`/`C30`… line) | CC0603KRX7R9BB104 | 2.2 nF to 0.1 µF; it leaves the `C27`–`C29` line |

**Side effects.**

- **None on USB power**, because USB current does not return through `Rs`. **None on sleep current.**
- **`BAT_MONIT` reads low** by I × (R_Q1 + `Rs`): 3 mV awake, 41 mV at a peak. Sample at rest, as now.
- **The cell finishes about 2 mV below 4.2 V** at TP4056 termination (13 mA × 0.15 Ω). The constant-voltage phase starts marginally earlier.

**Trial on a built board.** This can be done before any respin:

1. Lift `Q1` pin 3 off its pad.
2. Solder an 0805 or 1206 68 mΩ resistor from the lifted leg to scraped GND copper, or to the via at (86.4, 68.8).
3. Fit `C34` = 0.1 µF. If the board has no `C34`, bridge `R16` pad 2 to `C7` pad 2; they are 1.7 mm apart (final review BAT-01).

**Bench check.**

1. **Peak current.** On battery, read TP7 (or the lifted leg) against GND in mV: 68 mV per amp. Scope it during Wi-Fi TX plus an SD write plus the light. The 1.31× margin assumes this stays at 0.6 A or less (−41 mV).
2. **Trip point.** Feed `J5` from a bench supply at 3.7 V (limit 3 A) and load `P+` to GND with an electronic load in constant-current mode. Ramp up slowly. `OD` (TP8 against `B−`) falls to 0 V at the trip, expected 0.8–1.7 A, about 1.16 A typical. Repeat at 3.0 and 4.2 V.
3. **No false trip on insertion.** Plug a charged cell in 20 times. The board must never latch off: `OD` stays high, and it boots without USB.
4. **Hot.** Warm the area to about 60 °C and repeat step 1's heavy load for several minutes with no trip.

## 4. microSD supply

**PTC after `Q7`: no part works.**

The constraint is the card's 2.7 V minimum. With a 200 mA write burst on top of a 100 mA average, `SD_VDD` = 3.3 V − I × (R_PTC + 0.1 Ω).

| Part | `SD_VDD` at 200 mA, highest-resistance part, 25 / 60 °C | Worst never-tripped short (lowest-resistance part) |
|---|---|---|
| MF-FSMF020X-2, MF-PSMF020X-2, MF-NSMF020X-2 (0.2 A) | **2.48–2.50 / 1.67–2.01 V** (fails) | 1.5–2.4 W |
| MF-FSMF025X-2 (0.25 A) | 2.97 / **2.68 V** | 1.65–2.59 W |
| MF-PSMF035X-2, 1206L035YR (0.35 A) | 3.03 / 2.87–2.91 V | 1.87–2.52 W |

Parts with resistance low enough for the card barely heat on a short that `U3` limits to 0.36–0.87 A. They leave as much power in the short (1.9–2.6 W) as no PTC does (2.27 W).

**What already protects the card supply, and a zero-part fix:**

- **`Q7` already acts as a crude fuse.** `R40` (100 kΩ) pulls `Q7`'s gate to 3V3, so `Q7` is off whenever the ESP32 is in reset.
- **Shorts of about 3–5 Ω or less** pull 3V3 into `U3`'s limit low enough (below about 2.7 V) to brown the ESP32 out. That turns `Q7` off and removes the short.
- **The firmware fix:**
  - Set an RTC-memory flag before asserting `SD_ACTIVATE`, and clear it after a good mount.
  - If the next boot's reset reason is brownout with the flag still set, keep `SD_ACTIVATE` high (card off) and report a card fault.
  - For higher-resistance shorts (no brownout, up to about 2.3 W), release `SD_ACTIVATE` whenever a mount or command fails.
- **`C36`/`C37`:** move them at least 5 mm from `J7`, or turn them so the socket's bending axis runs along their length (DURABILITY_AUDIT section 3.4). That cuts the odds of the most likely `SD_VDD` short: a cap cracked by insertion flexing.

## 5. Charge current (`R6`)

TP4056: I ≈ 1100–1200 / R_PROG (the datasheet table gives 130 mA at 10 kΩ and 250 mA at 5 kΩ), with about 10 % tolerance between lots. `U11` dissipates (V_BUS − V_cell) × I: worst case is the start of constant-current charging from 3.0 V; typical is a 3.7 V cell. All four values below are already in the BOM.

| `R6` | Already in BOM as | Charge current | `U11` heat, worst / typical | C-rate, 500 / 1000 mAh | Time to full, 500 / 1000 mAh |
|---|---|---|---|---|---|
| 4.7 kΩ (today) | `R6`, `C23162` | 0.23–0.26 A | 0.51 / 0.33 W | 0.5 C / 0.25 C | about 2.5 / 5 h |
| 5.6 kΩ | `R18`, `C23189` | 0.20–0.21 A | 0.43 / 0.28 W | 0.4 C / 0.2 C | about 3 / 6 h |
| **10 kΩ** | `R4`…`R82`, `C25804` (Basic) | **0.11–0.13 A** | **0.26 / 0.17 W** | **0.25 C / 0.13 C** | **about 5 / 9.5 h** |
| 12 kΩ | `R11`, `C22790` | 0.09–0.10 A | 0.20 / 0.13 W | 0.2 C / 0.1 C | about 6 / 12 h |

Recommendation:

- **10 kΩ while the cell is unknown or 500 mAh or less.** It halves `U11`'s heat on the pour it shares with `U3`, 12 mm away; `U3` is already the board's thermal limit on USB (DURABILITY_AUDIT item 9). It also keeps a small cell, which has no NTC since `TEMP` is grounded, at 0.25 C or less. Fitting it moves `R6` onto the existing 10 kΩ BOM line and removes the 4.7 kΩ line.
- **5.6 kΩ if the cell is 1000 mAh or more** and overnight charging is too slow.

How it interacts with protection:

- **Battery path:** the charge current does not change the battery-path picture. The board's 0.6 A peak sets what any battery-path part must carry (section 3).
- **Sense resistor:** with `Rs` fitted, charge current shows on the test point as +68 mV/A.
- **USB:** a lower charge current leaves more of `F1`'s 0.65 A (60 °C) hold for the board on USB.

## 6. Diagnosis: nets to probe and proposed test pads

**Ground reference.** Every voltage below is measured against GND unless it says `B−`. The `DW01A` side (`OD`, `CS`) must be measured against `B−`, because once `OD` opens, board GND floats away from `B−`.

### 6.1 Frontlight PTC (`LDO_IN` to `LED_VIN`)

| Measurement | Where | Healthy | PTC tripped / fault |
|---|---|---|---|
| Powered: drop across the PTC | PTC pad 1 (`LDO_IN`, also `C4` pad 1 at 82.1, 85.1) to PTC pad 2 (`LED_VIN`, `C12` pad 2 at 52.4, 118.9) | about 0 V with the light off; tens to a few hundred mV at the 50 % cap | `LED_VIN` 0.3–0.8 V, the drop roughly equal to `LDO_IN`; the PTC body is 100–112 °C (thermal camera) |
| Powered: boost running | `LED_SW` (TP3) or firmware `LED_MONIT` (IO2, which reads `LED_SW`/9.3) | `LED_SW` well above `LED_VIN` with the light on | `LED_MONIT` about 0 while the light is commanded on: **firmware can flag a tripped PTC** |
| Unpowered: PTC itself | across its pads | 0.9–6 Ω (MF-FSMF010X-2; reads higher for about an hour after a trip) | open or MΩ = damaged PTC |
| Unpowered: the boost side | `LED_VIN` to GND, and `TPS_SW_NODE` (`L2` pad 2 at 48.3, 119.1) to GND | 100 kΩ or more (as the existing `LDO_IN` screening) | a few ohms = case 1 (`U10` low-side switch); `LED_VIN` reads the same through `L2` |

### 6.2 Touch PTC (`R42`) and `J6` pin 7

| Measurement | Where | Healthy | Tripped / fault |
|---|---|---|---|
| Powered: drop | touch: `R42` pad 1 (3V3, 91.5, 120.0) to pad 2 (`/PIN_2`, 91.5, 121.8). J6: the PTC's pads, then `J6` pin 7 | ≤ 0.05 V (touch); ≤ 0.26 V at 20 mA (J6) | `/PIN_2` or pin 7 below about 1 V and the drop about 2.5–3.3 V; the PTC is warm |
| Unpowered: branch to GND | `R42` pad 2, or `J6` pin 7, to GND, with the flex or accessory unplugged | open (nothing else is on the net) | anything below about 1 kΩ with nothing plugged in = board-side fault (`J4`, the pad, a whisker); measure again with it plugged in to blame the flex, controller or accessory |
| Unpowered: PTC itself | across its pads | 0.9–6 Ω | open = damaged |
| Firmware | touch: no I²C ACK and `TP_INT` idle; J6: no ACK from the accessory, while 3V3 is normal | — | "branch dead, board fine" is the tripped-PTC signature |

### 6.3 microSD supply

| Measurement | Where | Healthy | Fault |
|---|---|---|---|
| Powered: switch state | `Net-(Q7-G)` at `R78` pad 2 (80.7, 81.1) | 0 V = card on, 3.3 V = off | — |
| Powered: card supply | `SD_VDD` at `R77` pad 1 (78.9, 80.9) or `C37` pad 2 (63.2, 88.2) | within 0.05 V of 3V3 when on; about 0 V when off (bled by `R77`) | when on: 3V3 itself sagging or the ESP32 resetting = card-side short (section 4) |
| Unpowered | `SD_VDD` to GND, card out | about 100 kΩ (`R77`) | tens of ohms or less = `C36`/`C37`/`J7`; normal with the card out but low with it in = the card |
| Firmware | reset reason brownout with the SD flag set (section 4) | — | card fault |

### 6.4 Battery path (with `Rs`)

| Measurement | Where | Healthy | Fault |
|---|---|---|---|
| Powered on battery: current | the new net between `Q1` pin 3 and `Rs` (call it `B-_SENSE`) to GND | −68 mV per amp of discharge (about −3 mV awake, −40 mV at a 0.6 A peak); +68 mV/A while charging | a steady −70 mV or more with the board idle = a short drawing 1 A or more |
| Powered: has the `DW01A` tripped? | `Net-(U5-OD)` at `Q1` pin 6 (87.8, 73.0), **against `B−`** (`J5` pin 1 or `Q1` pin 1) | about the cell voltage | about 0 V = over-current or over-discharge latch; plug in USB to re-arm |
| Powered: CS | `R16` pad 2 (85.4, 79.3) against `B−` | I × (R_Q1 + `Rs`): 0.11–0.15 V per amp | — |
| Powered: path drop | `B+` (`J5` pin 2), `Net-(Q3-D)` and `Net-(Q8-D)` at `R27`'s pads (91.5, 75.6 / 77.6), `P+` at `C3` pad 1 (81.0, 90.2) | a few tens of mV per link at awake current | one link dropping volts = a damaged FET or a cracked `R27` |
| Unpowered | `Rs` end to end; `P+` and `LDO_IN` to GND | `Rs` reads near 0 Ω on a DMM (check it is not open); `P+`/`LDO_IN` 100 kΩ or more | a few ohms = the `P+`/`LDO_IN` short this whole study is about (`C3`, `C26`, `C4`, `U2`, `U11`) |
| Board dead on battery, fine on USB | — | — | first check `OD` against `B−` |

### 6.5 Proposed test pads

Superseded by the front-side set in section 8.2 (decided 2026-11-02). The pad numbers TP6–TP10 keep their meaning there.

## 7. 3V3 rail: what else needs protection

**How the rail is built.** 3V3 is a tree of 0.25 mm traces, 374 mm in total, with no pour. `U3`'s current limit is the only protection on it.

**Where it leaves the board or feeds an exposed section:**

| Branch | Protection after this follow-up |
|---|---|
| Touch flex (`R42`/`R66`) | PTC (section 2) |
| `J6` pin 7 | PTC (section 2) |
| microSD (`Q7`) | `R40` turns `Q7` off at reset, plus firmware (section 4) |
| E-paper boost (`L1`, `C10`, `Q4`, `R14`, `D4`–`D6`, `C11`, `C14`, `C16`, and the panel's HV rails) | **None** |
| E-paper panel logic (`J2` pins 15/16 `VDDIO`/`VCI`, plus `C22`, and `R66` in the alternate touch map) | **None** |

### 7.1 E-paper boost feed: add the same PTC

**Why.**

- **The boost hangs off 3V3 even when it isn't switching.** A boost converter always has a DC path from input to output (3V3 → `L1` → `D5` → `PREVGH`), and `Q4` has its own path to ground through `R14`.
- **Credible faults:**
  - a cracked `C10`;
  - a shorted `C14`/`C11`/`C16` or diode;
  - `Q4` failing short, or the panel's `GDR` stuck high. 3V3 then runs through `L1` (0.27–0.65 Ω), `Q4` and `R14` (2.2 Ω) to ground: about 2.5–2.9 Ω, which puts 1.4 W into an 0603 rated 0.1 W, indefinitely.
- **These are case 2's top two suspects** (BOARD_FAILURES.md section 5).

**Sizing.**

- The panel draws about 26 mW per refresh (≈8 mA at 3.3 V, GDEQ0426T82 product data). The boost's pulse current comes from `C10`, which will sit on the PTC's output.
- Hold margin is therefore more than 10× even at 60 °C, where the part holds 60 mA.
- The start-up surge that charges `C10`, `C14` and `C11` goes through the PTC's 0.9–6 Ω. That also damps the `L1` start-up ringing that HARDWARE.md section 6.2 flags.

**Results** (from the section 2 simulation, short of 2–3 Ω):

| | Trip time | Energy into the short before the trip |
|---|---|---|
| 25 °C | 0.7–0.8 s | — |
| Worst corner (−20 °C, 0.9 Ω part) | 2.9 s | 2.6 J or less (about 80 % of it in `R14`) |

Today the same short holds 1.4 W indefinitely. Resistive shorts up to 10 Ω trip at 25 °C (section 2 table).

**Where.**

- 3V3 arrives along y ≈ 110.4 and splits at (89.19, 110.45). One way runs to `L1` pad 2 (88.5, 110.45) and `C10` (92.1, 109.8); the other runs through a via (91.17, 112.43) to the touch feed (`R42`).
- **Re-tap the touch branch upstream**, e.g. at (86.75, 110.45). Then put the PTC between the trunk and a new net `EINK_3V3` that carries only `L1` pad 2 and `C10` pad 2. That keeps the touch feed off this PTC, so a touch fault does not kill the display.
- **`C10` must be on the PTC's output**, since it is the boost's local reservoir.

### 7.2 Panel logic supply (`J2` pins 15/16)

**The fault:** a dropped e-reader that cracks the panel or its COG, or a pinched FPC, can short `VCI`/`VDDIO` inside the panel.

**Load:** the COG draws a few mA, so the same PTC holds it with a drop of 0.05 V or less.

**Decided 2026-11-02: `J2` shares the e-paper PTC.** Route `J2` pins 15/16 from `EINK_3V3` (section 7.1), so one PTC guards the whole display. A panel fault then trips the PTC and the board reports "display dead" instead of browning out.

- **Cost:** a trace of about 25 mm from the `L1` area to `J2`. TP16 sits on that trace (section 8.2).
- **`C22`:** keep it with `J2`, downstream.
- **Old `J2` 3V3 branch:** remove it from the trunk.

The drop at the COG's few mA is 0.05 V or less, well inside the panel's logic-supply range.

### 7.3 Move `CR2` to the pin side of the `J6` PTC

`CR2` (TSD05CDYFR) exists only to clamp `J6` pin 7 (HARDWARE.md section 11), but today it sits on the 3V3 trunk at (89, 59). TVS diodes that absorb a big hit tend to fail short.

**The change:** put `CR2` on the `J6` side of the new pin 7 PTC, the same arrangement `CR3` already has after `F2`. A clamped surge and a failed-short `CR2` are then both limited by the PTC, and the clamp sits right at the pin, where it works best.

### 7.4 What stays protected only by `U3`'s limit

**What is left on the trunk:**

- `U3`'s own output capacitors: `C6` (22 µF), `C21`, `C32` (22 µF), `C33`.
- `U4` (ESP32 module), `U13` RTC (and alternate `U14`), `U12`.
- `Q7` itself, pull-ups, `SW10` and `R70`.

**Why that is acceptable:**

- All of it is on-board, and none of it was flagged by the flex-crack scan (DURABILITY_AUDIT section 4.1).
- The rail cannot take a fuse anyway: the ESP32 needs about 500 mA peaks.
- Accept it, but add a **firmware boot-loop guard**: count consecutive brownout resets in RTC memory, and after three, show a "power fault" screen (if the panel still works) and go to deep sleep instead of rebooting forever.
- **Free diagnostics:** a boot-time self-test can list which 3V3 branches stopped answering. Touch I²C, `J6` accessory I²C, SD mount and panel `BUSY` each point at a tripped PTC with no tools.

## 8. Fast short diagnosis: test pads and method

### 8.1 The PTCs are built-in current shunts

Every branch PTC (frontlight, touch, `J6` pin 7, e-paper) is 0.9–6 Ω. That turns "which branch is shorted?" into a millivolt reading. With the board unpowered (USB and battery out):

1. Measure each rail to GND at the rail pads (section 8.2), against the known-good table (section 8.3).
2. **For a low rail, inject current.** Set a bench supply to **1.0 V or less** (below IC and diode conduction) and 0.2–0.3 A. Connect it to the low rail's pad and GND.
3. **Read the millivolts across each PTC on that rail.** The shorted branch shows I × R_PTC: 0.1–1 V, because at 1.0 V the current limits itself through the PTC. Healthy branches show roughly 0 mV.
4. **If every PTC reads about 0 mV, the short is on the trunk.** At the same injected current, find the hot spot with a thermal camera or a drop of isopropyl alcohol.
5. **On the battery side:**
   - Inject into `P+` and read across the frontlight PTC (`LDO_IN` to `LED_VIN`).
   - With the cell out, the sense resistor is out of the loop. Instead, its test point (TP7) gives the live battery current when the board is running on battery.

This replaces case 2's "lift `L1` pad 2, then lift `C10`" isolation steps with meter readings.

### 8.2 Test pads (front side, decided 2026-11-02)

**Why the front.** All the parts are on B.Cu, so front pads can be probed without lifting the board off whatever covers its components.

**The rule:** pads must not touch the front artwork. Every pad below was checked by [test-pads/tp_front.py](test-pads/tp_front.py) against the Rev 1.02 front:

- **Silkscreen:** 0.20 mm or more from the pad edge.
- **Existing mask openings:** 0.20 mm or more.
- **Board edge:** 1 mm or more.
- **Other-net copper:** 0.20 mm or more.
- **Back side, where a via is needed:** 0.20 mm or more at the via.

All 13 pass at 1.5 mm diameter, so a smaller 1.0 mm pad also fits and is less visible.

**Pad details.**

- Bare round F.Cu pads with no paste, no BOM line and no cost, like `TP1`/`TP2`.
- **No F.SilkS labels.** The names go on F.Fab and in the docs. The map is [test-pads/tp_front.png](test-pads/tp_front.png).

Most pads sit in the gaps between paragraphs of the welcome text.

| Pad | Net | At (mm) | Connection | Use |
|---|---|---|---|---|
| TP6 | `LED_VIN` (new) | 46.5, 117.0 | via in pad, about 2 mm B.Cu stub to the frontlight PTC / `C12` node | frontlight PTC output (with TP13: drop across it) |
| TP7 | `B-_SENSE` (new) | 85.4, 69.6 | via in pad at the `Q1` end of `Rs`. It shares the `Rs` pocket, so place `Rs` and this via together | battery current, −68 mV/A against GND |
| TP8 | `Net-(U5-OD)` | 90.8, 71.5 | via in pad, about 2.6 mm from `Q1` pin 6. The B.Cu path crosses the OC trace, so run the stub on F.Cu | `DW01A` tripped? (against TP9) |
| TP9 | `B−` | 91.5, 68.65 | via in pad on the `B−` trace | reference for TP8 and CS |
| TP10 | `SD_VDD` | 63.65, 86.2 | via in pad on the `SD_VDD` trace by `C36` | card supply |
| TP11 | `USB_VBUS` | 82.75, 96.75 | on the existing F.Cu `USB_VBUS` trace | rail check |
| TP12 | `P+` | 90.5, 81.4 | via in pad on the `P+` trace | rail check |
| TP13 | `LDO_IN` | 79.74, 96.66 | on the existing F.Cu `LDO_IN` feed | rail check; frontlight PTC input |
| TP14 | `3V3` | 74.6, 85.8 | on the existing F.Cu 3V3 trace by `U3`/`C6` | rail check; `J6`-PTC and SD reference |
| TP15 | `3V3` | 91.3, 116.0 | on the F.Cu 3V3 touch feed, upstream of the touch and e-paper PTCs | input side of those two PTCs |
| TP16 | `EINK_3V3` (new) | 85.25, 115.5 | via in pad on the new `EINK_3V3` feed to `J2` | e-paper PTC output |
| TP17 | `/PIN_2` | 92.25, 129.25 | via in pad on the `/PIN_2` trace (0.24 mm from "Thank you all": legal, but nudge it if it looks crowded) | touch PTC output |
| TP18 | `GND` | 82.25, 81.25 | F.Cu GND pour (optional) | probe ground in the power cluster |

**Ground and existing front access.** No other GND pads are needed:

- **GND rings:** `J6` pins 1 and 4, the mounting-hole rings (`H5` beside the battery cluster, `H6` mid-board, `H2`), and the button "G" pads are all GND on the front.
- **`J6` itself** is already a front test header:
  - pin 7 = 3V3 after its PTC;
  - pin 12 = `/P+_FUSE`;
  - pins 5/6/11 = `LED_SW`/`W−`/`C−`, also on `TP3`–`TP5`.

**Probing each PTC from the front:**

| PTC | Probe across |
|---|---|
| Frontlight | TP13 → TP6 |
| E-paper | TP15 → TP16 |
| Touch | TP15 → TP17 |
| `J6` pin 7 | TP14 → `J6` pin 7 |
| SD switch `Q7` | TP14 → TP10 |
| Battery current | TP7 → `H5` |
| `DW01A` state | TP8 → TP9 |

**After any layout change** near these spots (the PTCs, `Rs`, the `J2` feed), run `python docs/audit-2026-10-29/test-pads/tp_front.py` again, then KiCad DRC.

### 8.3 Known-good baseline

Test pads only help with numbers to compare against. On the repaired case 1 board (now healthy), record each rail pad (TP11–TP14) and each PTC's output pad (TP6, TP16, TP17, `J6` pin 7, TP10) to GND:

- **Unpowered:** both probe polarities, settled.
- **Powered:** the idle voltages.

Put them in a table in BOARD_FAILURES.md section 8 (failure report). From then on a field board is diagnosed by comparing against that table.

## 9. Files

- [test-pads/tp_front.py](test-pads/tp_front.py) checks the front test pads against the artwork, mask, edge and copper, and draws [test-pads/tp_front.png](test-pads/tp_front.png). It needs kicad-cli 9 and PyMuPDF.
- [ptc-thermal/branches.py](ptc-thermal/branches.py) runs the branch studies: `python branches.py fit|cheap|sd|battery`.
  - **Inputs:** [ptc-thermal/candidates.json](ptc-thermal/candidates.json) holds the datasheet parameters. [ptc-thermal/candidates_fit.json](ptc-thermal/candidates_fit.json) holds the fitted model parameters, cached.
  - **Outputs:** `branches_cheap.json`, `branches_sd.json` and `branches_battery.json` hold every simulated case.
- [ptc-thermal/battery_sense.py](ptc-thermal/battery_sense.py) and `battery_sense.json`: the `DW01A` sense-resistor table.
- [ptc-thermal/parts_sourcing.json](ptc-thermal/parts_sourcing.json): JLC and DigiKey data for 30 PTCs and 10 sense resistors, as verified on 2026-11-02.
- [ptc-thermal/ptc_thermal.py](ptc-thermal/ptc_thermal.py): `fit()` and `calibrate()` now take any datasheet. Refitting MF-FSMF010X-2 reproduces [ptc-thermal/ptc_fit.json](ptc-thermal/ptc_fit.json) exactly.
