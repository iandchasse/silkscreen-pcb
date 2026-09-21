# U14 (Micro Crystal RV-8263-C7) independent check

**VERDICT: PROBLEMS — one real wiring defect, and it is the classic last-minute one.**

`CLKOE` is **pin 3** on the RV-8263-C7. The custom symbol numbers its CLKOE pin **`8`**, duplicating
SDA. Net effect: the symbol has **no pin 3 at all**, so **board pad 3 carries no net and CLKOE is a
floating CMOS input** — which per the datasheet may leave a 32.768 kHz push-pull CLKOUT running and
wipe out the entire power reason for fitting this part. ERC already flags the duplicate pin as an
**error**; DRC cannot see the floating pad (0 unconnected, 0 parity errors).

Everything else is right: SDA/SCL not swapped, VDD/VSS not swapped, footprint pad count and
numbering correct, placement DRC-clean, I2C addresses compatible. Ten findings below, F1–F4
actionable before fab, F5–F10 minor.

Scope: the read-only snapshot taken when KiCad was closed
(`scratchpad/snap_0921/silkscreen_pcb.kicad_sch` / `.kicad_pcb`), netlist exported with
`kicad-cli sch export netlist --format kicadxml`. Datasheet evidence: Micro Crystal
**RV-8263-C7 datasheet Rev. 1.0 / 01.2019** and **RV-8263-C7 Application Manual Rev. 1.0,
January 2019** (61 pp), both downloaded from microcrystal.com.

The good news up front: the author's instinct was right. The stock KiCad `Timer_RTC:RV-3028-C7`
symbol is pin-for-pin identical to the RV-8263-C7 **on 7 of 8 pins**. The one pin that differs is
the one he added — and he gave it the wrong number.

---

## 1. Pin table

Datasheet pinout (RV-8263-C7 datasheet p.1 "PIN CONNECTIONS TOP VIEW"; App. Manual §2.2
"PIN DESCRIPTION"):

| Pin | Datasheet name + function | Symbol pin name (U14) | Net on board (pad) | Verdict |
|---|---|---|---|---|
| 1 | **NC** — "Not connected. Is internally connected and should be left floating." | `NC` (type `no_connect`, NC flag) | `unconnected-(U14-NC-Pad1)` | **OK** — datasheet explicitly wants it floating; do *not* tie to GND |
| 2 | **VSS** — Ground (metal lid is bonded to pin 2) | `VSS` (`power_in`) | `GND` | **OK** |
| 3 | **CLKOE** — Clock Output Enable input. HIGH → CLKOUT drives; tied to Ground → CLKOUT LOW | **pin 3 does not exist in the symbol** | **pad 3 has NO NET — floating** | **DEFECT — see F1** |
| 4 | **INT** — Interrupt Output; open-drain; active LOW; requires pull-up resistor | `~{INT}` (`open_collector`, NC flag) | `unconnected-(U14-~{INT}-Pad4)` | **OK** (accepted, see F7) |
| 5 | **VDD** — Power Supply Voltage | `VDD` (`power_in`) | `3V3` | **OK** |
| 6 | **CLKOUT** — Clock Output; push-pull; controlled by CLKOE; default 32.768 kHz | `CLKOUT` (`output`, NC flag) | `unconnected-(U14-CLKOUT-Pad6)` | OK as a net, but see F1 — this pad is what CLKOE gates |
| 7 | **SCL** — I2C Serial Clock Input; requires pull-up | `SCL` (`input`) | `I2C_SCL` | **OK** — not swapped |
| 8 | **SDA** — I2C Serial Data I/O; open-drain; requires pull-up | `SDA` (`bidirectional`) **and a second pin also numbered 8 named `CLKOE`** | pad 8 = `I2C_SDA` | **OK electrically, but see F2** |

SDA/SCL are **not** swapped, VDD/VSS are **not** swapped. Pull-ups R47/R48 (2.2 k) are present on
`I2C_SCL` / `I2C_SDA` and are shared with U4 (ESP32-S3 IO39/IO38), U8, U13 and the J6 expansion header.

U13 for comparison (netlist + board, unchanged today):

| Pin | Name | Net | Note |
|---|---|---|---|
| 1 | 32KHZ | unconnected | |
| 2 | VCC | **GND** | the deliberate VCC-grounded / VBAT-primary topology closed as **A-61** — not relitigated here |
| 3 | ~INT/SQW | unconnected | no RTC wake path |
| 4 | ~RST | unconnected | |
| 5 | GND | GND | |
| 6 | VBAT | 3V3 | |
| 7 | SDA | I2C_SDA | |
| 8 | SCL | I2C_SCL | |

---

## 2. Findings, by severity

### F1 — BLOCKING: CLKOE (pin 3) is unwired and floating; CLKOUT may free-run at 32.768 kHz

**Evidence.** In `pcbnew`, U14 pad 3 at (64.5, 118.5) mm reports **`<NO NET>`** — not even an
`unconnected-` placeholder, because the symbol has no pin numbered 3 at all. The custom symbol's
pins are numbered 1, 2, 4, 5, 6, 7, 8, **8** — the author typed `8` for the CLKOE pin he added
instead of `3`.

**Why it matters.** App. Manual §2.2: *"CLKOE / 3 / Input to enable the CLKOUT pin. If CLKOE is
HIGH, the CLKOUT pin is in output mode. When CLKOE is tied to Ground, the CLKOUT pin is LOW."*
§2.2 for pin 6 adds: *"If CLKOE is HIGH (VDD), the CLKOUT pin drives the square wave of 32.768 kHz
… **(Default value is 32.768 kHz)**."* The datasheet specifies **no internal pull resistor** on
CLKOE. So a floating CLKOE is an undriven CMOS input: indeterminate level, input-buffer
shoot-through current, and a real chance the part powers up driving a 32.768 kHz **push-pull**
square wave out of pad 6 — which on this board goes to an isolated, unterminated copper stub.
That is exactly what App. Manual §7.1 note 3 warns against: *"If not used, it is recommended to
disable CLKOUT for optimized current consumption by setting FD to 111b or by pulling CLKOE LOW."*

On a board whose whole point is a ~73 µA deep-sleep budget, this silently throws away the entire
reason for fitting an RV-8263-C7 (190 nA) instead of the DS3231M.

**Nothing on the board catches this.** I ran `kicad-cli pcb drc` on the snapshot: **0 unconnected
items, 0 schematic-parity errors**. A pad with *no net assigned at all* is not an "unconnected"
pad as far as DRC is concerned, and parity is clean because the board faithfully matches a
schematic that has no pin 3. The only tool that hints at the problem is ERC, and only indirectly,
via the `duplicate_pins` error in F2. That is why this needs fixing by hand rather than waiting
for a checker to complain.

**Exact fix.**
1. In the symbol, change the CLKOE pin's **number from `8` to `3`** and **remove its
   no-connect flag** (see F3).
2. In the schematic, wire U14 pin 3 to **GND**. Do not leave it, and do not tie it to 3V3.
3. On the board this is a ~1 mm run: pad 3 (64.5, 118.5) sits directly between pad 2 (`GND`, at
   64.5, 117.6) and pad 4, same row, 0.9 mm pitch — a short B.Cu stub from pad 3 to pad 2, or a
   via into the GND pour, does it. No re-route of anything else is needed.

Belt-and-braces (firmware, not a substitute for the strap): also set FD = 111b in the control
register to disable CLKOUT, and per §7.1 note 3 turn the timer off (TE = 0) with TD = 11b for
minimum current.

### F2 — BLOCKING: duplicate pin number in the custom symbol; KiCad reports an ERC **error** right now

`kicad-cli sch erc` on the snapshot returns 40 violations, and one of them is at **`error`**
severity and belongs to U14:

```
error duplicate_pins | Symbol 'RV-3028-C7' has multiple pins with the same pin number
      Symbol U14 [RV-3028-C7]
```

Two pins numbered 8 (`SDA`, bidirectional, on `I2C_SDA`; and `CLKOE`, input, no-connect) land on
**different nets in the same netlist** — the exporter emits both nodes for pin 8. Pad 8 happened to
take `I2C_SDA`, which is the right answer, but it is the right answer by accident, not by design.
Fixing F1 (renumber to 3) removes this error.

### F3 — HIGH: the no-connect flag on CLKOE is what hid this from ERC

The CLKOE pin is declared `input` and carries a **no-connect flag** (netlist shows
`input+no_connect`). A no-connect flag on an input pin suppresses the "input pin not driven" check
that would otherwise have caught a floating CLKOE the moment it was numbered correctly. So even
after renumbering the pin to 3, if the NC flag stays, **ERC will still say nothing** and the pin
will still be floating. Delete the flag and wire the pin.

Pin 1's `no_connect` type + NC flag, by contrast, is **correct** and should be kept — the datasheet
wants pin 1 left floating.

### F4 — HIGH: the custom symbol is schematic-embedded only, and it shadows the stock library part

- `lib_id` is still **`Timer_RTC:RV-3028-C7`** while `Value` is `RV-8263-C7`.
- The modified definition exists **only** in the schematic's `lib_symbols` block. `sym-lib-table`
  in the snapshot lists seven 3rd-party libraries (FH34SRJ, FS8205A, PPPC_12, TPD4E1U06DBVR,
  TSD05CDYFR, TPS923610DRLR) and **no** project RTC library; nothing under `KiCad/9.0/3rdparty/`
  holds it either. The author's own note — *"should update sym lib with custom symbol"* — is
  correct and is not optional here.
- **Consequence:** because the lib_id still points at a *real* stock symbol, any "Update Symbols
  from Library" / library refresh will silently overwrite U14 with the genuine RV-3028-C7 symbol
  and **delete the CLKOE pin entirely** (the stock symbol has pins 1,2,4,5,6,7,8 and no pin 3).
  The corrected wiring would revert without a warning.
- Two stale inherited fields on U14: `Datasheet` = `…/RTC/Datasheet/**RV-3028-C7**.pdf`, and
  `Description` = "Extreme Low Power, **1.1 V to 5.5 V**, MicroCrystal C7". The RV-8263-C7 is
  0.9–5.5 V timekeeping / 1.8–5.5 V with the I2C bus active.

**Fix.** Save the edited symbol into a project library (e.g.
`${KIPRJMOD}/KiCad/9.0/3rdparty/MicroCrystal/RV-8263-C7.kicad_sym`, registered in `sym-lib-table`)
under its **own name** `RV-8263-C7`, re-point U14's `lib_id` at it, and correct the `Datasheet` and
`Description` fields.

### F5 — MEDIUM: U14 carries no MPN / Manufacturer / LCSC

U13 has `MPN = DS3231MZ+TRL`, `Manufacturer = Analog Devices`, `LCSC = C107410`. U14 has **none of
the three**. Combined with `in_bom no` + `exclude_from_bom`, U14 is invisible to every BOM path, so
the alternate cannot be ordered or even documented as an option.

Excluding a DNP alternate from the *fitted* BOM is correct, but the identity fields should still be
populated so `fabrication/part_fields.csv` and the docs can carry the option. Per the
DigiKey-primary convention, set `Manufacturer = Micro Crystal AG` and `MPN` to the Micro Crystal
ordering code, with LCSC as the extra field. **See "could not verify" §5 — I did not confirm an
exact orderable part number or LCSC code, so do not copy one from this report.**

### F6 — LOW / informational: shared 100 nF, 3.0 mm away

App. Manual §7.1 note 1: *"A 100 nF decoupling capacitor is recommended close to the device."*
The nearest 3V3/GND cap is **C30 (0.1 µF), 3.01 mm from U14's VDD pad** (and 7.2 mm from U13). Since
U13 and U14 are mutually exclusive by construction, one shared 100 nF is reasonable and 3 mm on a
2-layer board is workable. Not a defect; noted only because the part draws 190 nA and the I2C edges
are the only real transient. No change recommended.

### F7 — LOW: INT (pin 4) left floating — acceptable, and consistent with U13

Datasheet: *"Interrupt Output; open-drain; active LOW; requires pull-up resistor."* It is left
unconnected with an NC flag. A floating **open-drain output** is electrically harmless (unlike the
floating CLKOE **input** in F1) — the "requires pull-up" applies only if you intend to read it. U13's
`~INT/SQW` is likewise unconnected, so this matches the board's existing, already-closed decision
that there is **no RTC interrupt wake path** (A-61: "no backup, no INT wake"). No action; flagged
only so it is a conscious choice rather than an oversight carried over by copying U13.

### F8 — LOW: U14 pad 2 has a starved thermal relief to the GND pour

`kicad-cli pcb drc` on the snapshot reports, against U14:

```
warning starved_thermal | Thermal relief connection to zone incomplete
                          (layer B.Cu; zone min spoke count 2; actual 1)
      Zone [GND] on F.Cu and B.Cu, priority 0
      Pad 2 [GND] of U14 on B.Cu
```

Pad 2 is VSS (and the package's metal lid bonds to it). One spoke instead of two is electrically
irrelevant for a 190 nA part, but it is a genuine hand-soldering/reflow thermal-relief concern on a
0.95 × 0.65 mm SON pad, and it is in exactly the copper you will be editing for the F1 fix. Deal
with both in one pass: give pad 2 a second spoke, and bring pad 3 into the same GND pour (a via
under/beside pad 3 into the pour is cleaner here than a pad-3-to-pad-2 stub, and avoids making the
starved-spoke situation worse).

### F9 — LOW: U14's reference designator silkscreen is clipped and collides with R47

Four more DRC warnings against U14, all cosmetic:

```
warning silk_over_copper | Silkscreen clipped by solder mask — Reference field of U14
warning silk_overlap     | Reference field of U14  vs  Reference field of R47
warning silk_overlap     | Reference field of U14  vs  Segment of R47 on B.Silkscreen
warning silk_overlap     | Reference field of R47  vs  Segment of U14 on B.Silkscreen
```

The "U14" label is partially unreadable and overlaps R47's. For a DNP alternate that someone will
be hand-placing — and choosing *between* U13 and U14 while doing it — a legible designator and a
clear pin-1 mark are worth the two minutes. Nudge the U14 and R47 reference fields apart.

### F10 — LOW: DNP flags are right; position-file exclusion relies on the export checkbox

Board attributes: `DNP=True`, `exclude_from_BOM=True`, **`exclude_from_pos_files=False`**
(attr bits `0x10a`). Schematic flags: `(in_bom no)`, `(dnp yes)`, `(on_board yes)`. Consistent.

The `exclude_from_pos_files=False` is **the board's existing house style** — every other DNP part
(SW6, R43, R45, R58, R66, R72, R74, TP3/4/5) has the same setting. And the current
`production/positions.csv` contains **none** of them (verified: 0 rows for each), so the author's
export is using KiCad's "Exclude DNP" option and U14 will be filtered the same way. So U14 will not
leak into positions.csv **as long as that box stays ticked**. Setting
`exclude_from_pos_files=True` on U14 would make it robust regardless, but it is a consistency
choice, not a defect.

Note U14 appears in **no** current production file (`bom.csv`, `positions.csv`,
`bom_JLC_upload_v*.csv`, `designators.csv`) simply because those were generated before today's
addition. Regenerate after fixing F1/F2.

---

## 3. PCB parity and package check

**Netlist ↔ board parity: matches on all 7 pins that exist**, and pad 3 correctly shows no net
because no symbol pin claims it — i.e. the board faithfully reproduces the schematic's defect.

| Pad | XY (mm) | Board net |
|---|---|---|
| 1 | 64.5, 116.7 | unconnected-(U14-NC-Pad1) |
| 2 | 64.5, 117.6 | GND |
| 3 | 64.5, 118.5 | **&lt;NO NET&gt;** |
| 4 | 64.5, 119.4 | unconnected-(U14-~INT-Pad4) |
| 5 | 63.2, 119.4 | 3V3 |
| 6 | 63.2, 118.5 | unconnected-(U14-CLKOUT-Pad6) |
| 7 | 63.2, 117.6 | I2C_SCL |
| 8 | 63.2, 116.7 | I2C_SDA |

**Placement:** (63.85, 118.05) mm, **B.Cu** (bottom, consistent with "all fitted parts on the
bottom"), orientation 180°. U13 is 7.24 mm away at (61.905, 125.025); C30 4.2 mm; R47 3.6 mm;
R48 4.7 mm; TP1 6.8 mm; TP2 7.7 mm.

**Courtyards:** I ran `kicad-cli pcb drc` on the snapshot — **93 violations board-wide, 0
unconnected items, 0 schematic-parity errors**. (The "DRC parity was 0" in the brief refers to the
parity count, which I confirm; the board does carry 93 other DRC warnings, none of them new
today.) **No courtyard-overlap or clearance violation is reported against U14.** The only U14
entries in the DRC report are the starved thermal relief (F8) and four silkscreen warnings (F9).
My earlier bounding-box sweep flagged TP1/TP2/R47/R48/C30/U13 as inside U14's *bounding box*, but
bounding boxes are far coarser than courtyards and DRC clears them — **U14's placement is fine.**

**Package / pad numbering:** footprint `Package_SON:MicroCrystal_C7_SON-8_1.5x3.2mm_P0.9mm`,
**8 pads**, each 0.95 × 0.65 mm, two rows 1.3 mm apart, **0.9 mm pitch**. Pads 1→4 run down one
row (y 116.7 → 119.4) and 5→8 back up the other (y 119.4 → 116.7), i.e. counter-clockwise with
pads 4 and 5 adjacent at the same end. This matches the datasheet's top-view corner labels
**#1 / #4** on one edge and **#5 / #8** on the other, and the datasheet package drawing
(3.2 × 1.5 × 0.8 mm, 0.9 mm pad pitch, 0.9 × 0.5 mm pads). **Pad count and numbering orientation
are correct.** The C7 footprint is the shared Micro Crystal package used by the RV-3028-C7,
RV-8263-C7 and RV-8803-C7, so reusing it here is right. (Datasheet drawings are top view and this
part is on B.Cu; KiCad handles the mirroring, and the pin-1 index on the silk will land correctly.)

---

## 4. Coexistence and power

**I2C addresses — no conflict.** App. Manual §5.6: *"the 7-bit slave address **1010001b** is
reserved for the RV-8263-C7"* — i.e. **0x51**, accessed as A2h (write) / A3h (read). The DS3231M is
fixed at **0x68** (D0h/D1h). The two can share the bus with both fitted, let alone with one
unpopulated. Both support 400 kHz Fast Mode.

**An unpopulated U14 leaves nothing floating that matters.** Its pads land only on `GND`, `3V3`,
`I2C_SCL`, `I2C_SDA` — all four nets exist and are driven independently of U14 — plus pads 1/3/4/6
which connect to nothing else on the board. There is **no pull-up, strap or divider that exists
solely for U14**: R47/R48 are the shared bus pull-ups serving U4, U8, U13 and J6. An unfitted U14
contributes only a few short unterminated pad stubs to SDA/SCL, which is negligible against the
400 pF bus budget. The F1 fix (pad 3 → GND) adds nothing when the part is absent. Symmetrically,
nothing on the board exists solely for U13, so leaving U13 off and fitting U14 strands nothing
either.

**Deep-sleep budget.** Datasheet Electrical Characteristics @ 25 °C: *Current consumption, Time
keeping mode, I2C-bus inactive, VDD = 3 V: **190 nA typ / 240 nA max***. VDD range 0.9–5.5 V
timekeeping, 1.8–5.5 V with I2C active — 3V3 is comfortably inside both. The datasheet quotes only
the 3 V figure; at 3.3 V expect the same order (well under 0.5 µA).

Against the board's ~73 µA total and U13's assumed ~1–3 µA, swapping U13 → U14 **saves roughly
1–3 µA, about 2–4 % of the deep-sleep budget** — real but modest.

**Two caveats on that number, both worth stating plainly:**
1. The 190 nA figure holds **only with CLKOUT disabled**. With CLKOE floating (F1), a 32.768 kHz
   push-pull output plus an undriven input buffer can eat the entire saving and then some. **Fix
   F1 or the swap is pointless.**
2. Accuracy regresses: RV-8263-C7 is **±20 ppm @ 25 °C** (plus ±3 ppm first-year aging, and an
   uncompensated tuning-fork parabola of −0.035·(T−25)² ppm) versus the DS3231M's TCXO **±5 ppm**.
   That is roughly **±10 min/year** versus ±2.6 min/year, and materially worse away from room
   temperature — at 0 °C the parabola alone is about −22 ppm. For a reader that syncs over Wi-Fi
   this is a non-issue; if it must free-run for months, it is the real trade. Author's call.

One incidental benefit of the swap: the RV-8263-C7 runs normally from VDD with the I2C interface
fully specified down to 1.8 V, so it sidesteps the VCC-grounded / VBAT-primary topology that U13
uses (closed item A-61). The RV-8263-C7 has no battery-backup pin at all; App. Manual §7.2 covers
backup via an external diode + capacitor, which this board does not implement and does not need,
since 3V3 is the always-on rail either way.

---

## 5. What I could not verify

- **Exact orderable part number / distributor codes for the RV-8263-C7.** The datasheet's ordering
  section gives the form `RV-8263-C7 TA QC` with reel-quantity suffixes (`20xxxx-MG01` = 1 000 pcs,
  `-MG03` = 3 000 pcs) but states *"A unique part number will be generated for each product
  specification"*. I did not check DigiKey/LCSC stock, so I deliberately did not invent an MPN or
  LCSC code for F5 — confirm against the distributor before entering the fields.
- **Whether CLKOE has any undocumented internal pull.** The datasheet and 61-page application
  manual specify none, and I found no input-leakage/pull-down entry for CLKOE in the DC
  characteristics. Absence of a spec is the reason to strap it, not a reason to assume it is safe.
- **The 93 board-wide DRC warnings** other than U14's five are outside this task's scope and were
  not triaged. Re-run DRC after adding the CLKOE connection.
- **U13's VCC-grounded VBAT-primary topology (A-61)** — treated as closed per
  `comparison/A_vs_DESIGN_REVIEW.md`, not independently re-derived. It matters here only as the
  baseline the ~1–3 µA figure comes from.
- **The ~1–3 µA figure for U13** is taken from the task statement, not read out of the DS3231M
  datasheet in this pass.
- **The other 39 ERC violations** are outside this task's scope; I filtered for U13/U14 and pin
  issues only. All of the ones I saw besides U14's `duplicate_pins` were `pin_to_pin` warnings
  about Unspecified-type pins on 3rd-party symbols (CR1/CR2/CR3, J6, U10). I am not claiming
  U14's is the only error-severity violation on the board.

---

## 6. Minimum fix list

1. **Renumber the CLKOE pin from 8 to 3** in the U14 symbol, and remove its no-connect flag. *(F1, F2, F3)*
2. **Wire U14 pin 3 to GND** in the schematic; on B.Cu bring pad 3 into the GND pour (a via beside
   pad 3 is cleaner than a stub to pad 2), and while there give pad 2 its second thermal
   spoke. *(F1, F8)*
3. **Save the symbol to a project library under its own name `RV-8263-C7`**, add it to
   `sym-lib-table`, re-point U14's `lib_id`, and fix the `Datasheet` and `Description` fields. *(F4)*
4. Add `MPN` / `Manufacturer` / `LCSC` to U14 once confirmed with the distributor. *(F5)*
5. Nudge the U14 / R47 reference designators apart. *(F9)*
6. Re-run ERC (the `duplicate_pins` error must clear) and DRC, then regenerate production files.

*Checked against the snapshot at `scratchpad/snap_0921/`. No repository file other than this report
was modified; nothing was staged or committed.*
