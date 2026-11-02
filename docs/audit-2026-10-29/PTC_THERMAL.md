# Frontlight boost: a thermally placed PTC (electro-thermal study, 2026-10-29)

The lean after the [latching fuse](BOOST_EFUSE.md) and the [4-part limiter](BOOST_LIMITER.md): one PTC,
**Bourns MF-FSMF010X-2** (0603, 0.10 A hold / 0.30 A trip, 15 V), in the boost feed, placed close to `U10`
on thermally light pads. This study models how it behaves with the case 1 short (a failed low-side switch
inside `U10`) using a coupled electrical and thermal simulation. **It is a model fitted to a datasheet and
a generic board, not a measurement.**

## 1. Summary

- **Part:** MF-FSMF010X-2, JLC/LCSC `C210355` (Extended, 26 658 in stock on 2026-11-02, $0.058 each;
  the "70 700" first quoted here was a related part's stock field), DigiKey 118-MF-FSMF010X-2CT-ND
  ($0.54 each, $0.32 at 100; DigiKey's stock could not be confirmed on 2026-11-02, as searches disagreed
  between about 100 000 and backorder). **Drop-in alternate on both:** MF-PSMF010X-2 (0805, 1.0/7.5 Ω),
  JLC `C116171` (Extended, about 95 600, $0.052), DigiKey MF-PSMF010X-2CT-ND (about 31 000, $0.38). It is
  slightly heavier and slower; see [PROTECTION_FOLLOWUP.md](PROTECTION_FOLLOWUP.md) section 1.
- **Where:** between `LDO_IN` and a new net `LED_VIN` that carries `C12`, `L2` pad 1 and `U10` `VIN`
  (section 2).
- **Case 1 short, 25 °C:** the PTC cuts the 7 Ω short back at every supply from a 3.0 V cell to USB,
  in 0.9–5.1 s. The power in the short falls from 0.8–2.2 W to 0.02–0.09 W and `U10` peaks at 50–88 °C.
  Without it the short takes 1.0–2.75 W and `U10` would reach roughly 100–430 °C.
- **The datasheet arithmetic was too pessimistic.** "Guaranteed only above 4.07 V" combined the
  highest-resistance part (least current) with the trip current set by the lowest-resistance part
  (least heating). A PTC trips on its own heat (I²R); the simulation shows every part from 0.9 to 6.0 Ω
  heating enough at 3.0 V.
- **What matters most is keeping the PTC thermally light** (small pads, thin traces, no pour on its
  pads). On 40 % better-cooled copper it no longer trips at 3.0–3.4 V without help. Placement next to
  `U10` helps at the margin (slightly faster trips, less power left in a short it cannot fully trip) but
  cannot rescue a PTC on heavy copper.
- **Where it falls short:** at −20 °C ambient it does not trip from a 3.0 V cell (0.74 W left in the
  short) and takes 26 s at 3.4 V. Shorts of 10 Ω need 3.4 V or more, 15 Ω need 4.2 V or more at 25 °C.
- **After it trips** it sits at 100–112 °C passing 50–115 mA until the short or the supply goes:
  0.02–0.09 W in the short, a 500 mAh cell flat in roughly 4–10 h.
- **Normal use:** no trip at the 50 % brightness cap at 25 and 45 °C. At 100 % duty, a high-resistance
  part (6 Ω) can drop `U10` into UVLO from a cell of 3.7 V or less: the light cuts out and comes back.
  Keep the 50 % cap, or allow 100 % only above about 3.8 V.

## 2. Where it goes

**Nets.** Split `LDO_IN` at the boost branch:

| PTC pin | Net | What is on it |
|---|---|---|
| 1 | `LDO_IN` (unchanged) | `U2` `VOUT` (pins 2, 7), `C4`, `U3` `IN`/`EN`, and the 56.5 mm front-copper feed |
| 2 | `LED_VIN` (new) | `C12` pin 2, `L2` pin 1, `U10` pin 1 (`VIN`) |

Keep `C12` on `LED_VIN`, at `U10`: `U10` needs at least 1 µF effective right at `VIN` (datasheet 6.3).
With `C12` on the other side, `U10`'s 1.1 MHz input ripple would flow through the PTC.

**Rev 1.02 copper.** The feed arrives on the back through the via at (52.00, 117.80). From `L2` pad 1
(50.64, 119.13) three 0.25 mm back-side traces fan out: to that via, to `C12` (52.38, 118.91) and to
`U10` pin 1 (50.35, 121.50). The PTC replaces the via-to-`L2` link. There is no room for a 0603 in that
1.9 mm link. The nearest free 0603 land found earlier, about (48.4, 116.3) north-west of `L2`, is
about 2.8 mm from `L2`'s `SW` pad (where case 1 charred) and needs a two-via hop across the `LED_SW` run
at y = 117.1 or a move of `R39`/`R41` (BOARD_FAILURES section 6.4).

**Thermal rules for the layout** (from section 4):

1. **Thermally light:** the PTC's two pads on 0.25 mm traces for at least a few mm, no pour or plane
   tied to either pad, no thermal vias under it. This matters more than anything else here.
2. **Close to `U10`/`L2`:** within a few mm of `U10` and `L2`'s `SW` pad, sharing the board area (not the
   copper) with them.
3. **Away from other heat** in normal use: not next to `U3` or the charger.

## 3. Model

[`ptc-thermal/ptc_thermal.py`](ptc-thermal/ptc_thermal.py) (numpy and scipy; `python ptc_thermal.py
calibrate`, then `run`).

**The PTC.** One thermal node: C dT/dt = I²R(T) − (T − T_env)/θ, with
R(T) = R0 · e^{b(T − 23)} · (1 + 10⁴ / (1 + e^{−(T − T_m)/w})). R0 is the part's room-temperature
resistance (datasheet spread 0.90–6.00 Ω). Fitted to the MF-FSMF010X datasheet:

| Datasheet point | Model | Datasheet |
|---|---|---|
| Hold current of the 6.0 Ω part at 0 / 23 / 40 / 60 / 85 °C | 0.122 / 0.097 / 0.081 / 0.061 / 0.030 A | 0.11 / 0.10 / 0.08 / 0.06 / 0.03 A |
| Hold current at −40 / −20 °C | 0.18 / 0.15 A | 0.13 / 0.12 A (the model is harder to trip in the cold) |
| Runaway current of the 0.9 Ω part, 23 °C | 0.25 A | trips at 0.30 A |
| Time to trip at 0.5 A, 0.9 Ω part | 1.0 s (fitted) | ≤ 1.0 s |
| Tripped dissipation at 15 V | 0.36 W | 0.5 W typical |

Fit: b = 0.020 /°C, θ = 325 °C/W (on Bourns's test board), C = 4.7 mJ/K. In this model the "tripped"
state is a high-resistance equilibrium near 100–112 °C rather than a jump at a fixed temperature.

**The board** (estimates, swept):

- `U10` junction: 3 mJ/K, 31.6 °C/W to the board (the TPS923610's θJB for SOT-563).
- The board under `U10` and the PTC: 0.35 J/K, 40 or 110 °C/W to ambient (so `U10`'s θJA is 72–142 °C/W;
  the JEDEC figure for a sparse board is 142.7).
- The PTC's surroundings sit at ambient + κ × (the board's rise under `U10`): κ = 0 (far), 0.25, 0.5,
  0.75 (beside `U10`).
- The PTC's own cooling: as on Bourns's test board (factor 1.0), or 40 % better (0.6, heavier copper).
- Electrical: source behind 0.5 Ω (also feeding a 40 mA 3V3 load), the PTC, `L2`'s 0.45 Ω, the short
  inside `U10` (3, 7, 10 or 15 Ω). Ambient −20, 25 and 45 °C. 2 880 fault cases for 300 s each.
- Normal use: the light at 50 % and 100 % duty (0.235 W × duty, constant power), 1 080 cases for
  30 minutes, at 25, 45 and 60 °C ambient.

"Tripped" below means the power in the short has fallen under a quarter of its starting value.

## 4. Results

### 4.1 The case 1 short and its neighbours (thermally light PTC, κ = 0.5)

Worst case over the PTC's resistance (0.9, 2.5, 6.0 Ω) and the board (40, 110 °C/W): time to trip /
power in the short at the start → at the end / `U10`'s peak junction temperature.

**25 °C ambient:**

| Short | 3.0 V | 3.4 V | 3.7 V | 4.2 V | 5.0 V (USB) |
|---|---|---|---|---|---|
| 3 Ω | 0.9 s / 1.12 → 0.03 W / 55 °C | 0.7 s / 1.44 → 0.02 W / 62 °C | 0.5 s / 1.70 → 0.02 W / 67 °C | 0.4 s / 2.20 → 0.01 W / 76 °C | 0.3 s / 3.12 → 0.01 W / 90 °C |
| **7 Ω (case 1)** | **5.1 s / 0.79 → 0.09 W / 50 °C** | **2.9 s / 1.01 → 0.06 W / 56 °C** | **2.1 s / 1.20 → 0.05 W / 62 °C** | **1.5 s / 1.55 → 0.04 W / 71 °C** | **0.9 s / 2.20 → 0.02 W / 88 °C** |
| 10 Ω | not tripped: 0.63 → 0.48 W / 71 °C | 11.6 s / 0.81 → 0.12 W / 58 °C | 6.1 s / 0.96 → 0.08 W / 57 °C | 3.3 s / 1.24 → 0.06 W / 64 °C | 1.9 s / 1.76 → 0.04 W / 79 °C |
| 15 Ω | not tripped: 0.47 → 0.44 W / 84 °C | not tripped: 0.60 → 0.55 W / 94 °C | not tripped: 0.71 → 0.62 W / 89 °C | 26.6 s / 0.92 → 0.12 W / 77 °C | 6.0 s / 1.30 → 0.06 W / 73 °C |

**7 Ω short at other ambients:**

| Ambient | 3.0 V | 3.4 V | 3.7 V | 4.2 V | 5.0 V |
|---|---|---|---|---|---|
| −20 °C | not tripped: 0.90 → 0.74 W | 25.6 s → 0.25 W | 10.8 s → 0.15 W | 5.4 s → 0.10 W | 2.8 s → 0.06 W |
| 45 °C | 2.2 s → 0.04 W | 1.5 s → 0.03 W | 1.2 s → 0.03 W | 0.8 s → 0.02 W | 0.6 s → 0.01 W |

**As built (no PTC), 7 Ω, 25 °C:** 0.98 W (3.0 V) to 2.75 W (5.0 V) in the short, and `U10` would settle
at 98–171 °C (3.0 V) up to 229–433 °C (5.0 V) on this board model, which is how case 1 charred.

### 4.2 What the placement does (7 Ω, 25 °C, worst over the PTC's resistance and the board)

| PTC cooling | κ (coupling to `U10`) | 3.0 V | 3.4 V | 3.7 V |
|---|---|---|---|---|
| test-board-like (thermally light) | 0 / 0.5 / 0.75 | 5.8 / 5.1 / 4.9 s | 3.0 / 2.9 / 2.8 s | 2.2 / 2.1 / 2.1 s |
| 40 % better cooled (heavy copper) | 0 | not tripped (0.65 W left) | not tripped (0.70 W) | |
| 40 % better cooled | 0.75 | not tripped (0.23–0.49 W) | 5.6–10.8 s | |

The PTC's own thermal isolation decides whether it trips at a low cell; coupling to `U10` shortens slow
trips and lowers what is left, but the heat from `U10` spreads into the board and falls as soon as the
PTC starts limiting, so it cannot replace isolation.

### 4.3 Normal use (30 minutes)

- **50 % duty:** no trip and no UVLO at 25 and 45 °C ambient, for every part and board. The PTC stays
  below 79 °C. At 60 °C ambient a 6 Ω part on a 3.0 V cell drops `U10` into UVLO.
- **100 % duty:** a 6 Ω part drops `U10` into UVLO from a cell of 3.0–3.7 V at 25 °C, and 2.5 Ω parts do so
  at 45–60 °C from a 3.0–3.4 V cell. The PTC's resistance adds to the drop and it self-heats: at 100 %
  the light draws about 100 mA from a 3.0 V cell through the PTC, right at its 0.10 A hold.
- None of this damages anything: the light goes out and comes back as the PTC cools. Keep the 50 % cap,
  or allow 100 % only above about 3.8 V.

## 5. Effects on the rest of the circuit

- **`U10`:** its input sees the PTC's 0.9–6.0 Ω in series: 0.04–0.25 V at the 50 % cap, up to about
  0.65 V at 100 % from a 3.0 V cell with a 6 Ω part (section 4.3).
- **Start-up:** the light's start-up current flows through the PTC's resistance too; a large start (0.4 A)
  through a 6 Ω part drops `U10` into UVLO. It restarts by itself; the bench start-up measurement in
  the other studies applies here too.
- **Surges into the branch** (`L2` → body diode → `C9` on plug-in and hot-plug) are damped by the PTC's
  resistance, as with the limiter.
- **`LDO_IN`, `U2`, `U3`:** unchanged in normal use. During a short `LDO_IN` stays up (the branch takes
  at most about 0.6 A from a cell for a few seconds), so the ESP32 keeps running and can warn the user.
- **Sleep current:** none.
- **`LED_MONIT`:** after a trip, `LED_SW` decays through `R39`/`R41` and `C9` (τ ≈ 4 s) towards `LED_VIN`'s
  low tripped level, so firmware can detect it the same way as in the limiter study.
- **Protection devices:** `F1`, `F2` and the DW01A are not reached.

## 6. Cases 1 and 2, and what else it covers

**Case 1 replayed with the PTC fitted.** The board was plugged into USB with no battery; `U10`'s
low-side switch was (or became) a short of about 7 Ω. Without the PTC that short took 2–3 W for 30–60 s
until it smoked. With it:

1. The short draws about 0.35–0.56 A on 5 V, depending on the PTC's own resistance. The PTC (0.9–6.0 Ω)
   heats itself, and in under a second (0.9 s worst case in the model) its resistance runs up and the
   current falls to about 60 mA.
2. `U10` peaks below about 90 °C and the short then takes about 0.02 W. Nothing chars.
3. `LDO_IN` stays up, so the board boots and runs normally; only the frontlight is dead. The PTC sits
   at about 110 °C under the board while USB is connected.
4. Unplugged, the PTC cools and resets within seconds; plugged in again, it trips again within about
   a second. With the battery fitted instead, it trips in 2–3 s from a 3.4–3.7 V cell and about 5 s
   from a 3.0 V cell.
5. If the switch failed harder at first (a lower resistance), the trip is faster: 0.3 s at 3 Ω on USB.

**Case 2 is not covered.** That short was on 3V3, upstream of the frontlight; `U3`'s current limit was
the only thing in its way. See [DURABILITY_AUDIT.md](DURABILITY_AUDIT.md) for the 3V3 rail.

**Everything downstream of the PTC is covered**, with the same physics:

- `LED_VIN`: a cracked `C12`; a `VIN`-to-`GND` short inside `U10`.
- `SW`: `U10`'s low-side switch (case 1); char or a solder bridge at `L2` pad 2.
- `LED_SW`, fed through `L2` and `U10`'s high-side body diode even with the light off: a cracked `C9`, a
  shorted `D3`, a damaged frontlight flex or `J3`, a short at `J6` pin 5 (an accessory or a solder
  whisker on the expansion header), or `TP3`.
- With the light on, any of these also drives `U10` into its 1.6–2.1 A switch limit, which trips the PTC
  faster still.

**Not covered:** a low-forward-voltage LED string on `J6` (HARDWARE.md section 11, rule 2) draws about
43 mA, under the hold current, so it can still overdrive the external LEDs (the board is not stressed);
and anything upstream of the PTC (`LDO_IN` trunk, `C4`, `U2`, `U3`, 3V3).

## 7. Limits

- One-node PTC and three-node board: no heat spreading geometry, no convection detail, no measured
  board data. The board parameters are swept, not known.
- The PTC fit is good from 0 to 85 °C and optimistic about hold below 0 °C (the model is harder to trip
  in the cold than the real part should be).
- The short is modelled as a fixed resistor inside `U10`; a short that changes as it heats is not.
- Tripped-state numbers depend on the fit's 0.36 W tripped dissipation (datasheet 0.5 W typical): a
  real part may sit hotter and pass a little more current once tripped.

## 8. Bench test

1. Fit the PTC in its planned place on a board (or a board with the same pads and traces), with a 6.8 Ω
   1206 standing in for `U10`'s failed switch between `SW` and `GND`.
2. Feed it from 3.0, 3.4, 3.7 and 5.0 V; record the time until the current falls below about 0.1 A,
   the PTC's temperature, and the temperature at `U10`'s footprint (IR camera or thermocouple).
3. Repeat in a freezer (−20 °C) and an oven (45 °C) if possible.
4. Normal use: light at 100 % from 3.0 V and 3.7 V for 30 minutes at room temperature and at 45 °C;
   check for drop-outs.
5. Compare with section 4; if the 3.0 V trip is slow or absent, the PTC is too well cooled.
