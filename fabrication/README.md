# Fabrication & assembly — Silkscreen (silkscreen_pcb)

Active assembly workflow: **JLCPCB**, using KiCad **9.0.6** and the **Fabrication Toolkit**
for placements. Board: 2 layers, 60 × 111 mm, 1.6 mm thickness, 1 oz copper.

**Read [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) before releasing files.** It is the only
engineering verdict/action list; the latest pre-order audit is in
[`../docs/audit-2026-09-18/`](../docs/audit-2026-09-18/PREORDER_CONFIRMATION_AUDIT.md).
The current source (2026-09-18, with the Fix 4 reverse-battery circuit, L1 47 µH, R14 2.2 Ω and C9 4.7 µF)
has **179 references = 162 fitted + 10 DNP + 7 bare-copper** (H1–H5, TP1, TP2).
The two previous orders (25 and 30 boards) predate Fix 4, the Q4/R37 changes and the slotted
microSD land.

The step-by-step JLCPCB upload flow and the optional/base part groups are in the root [README](../README.md#ordering-from-jlcpcb-step-by-step).
For PCBWay or NextPCB, `python fabrication/make_fab_files.py` builds their BOMs, a raw KiCad placement file and a bottom-side
assembly drawing into `production/other_fabs/` (see the root [README](../README.md#ordering-from-pcbway-or-nextpcb-alternative-to-jlcpcb)).

## Release records

Keep these together as one revision, including the accepted factory copies:

| Record | Local file | Meaning |
|---|---|---|
| Gerbers/drills | `production/Silkscreen_Reader_PCB_1.0.zip` | Toolkit output. The 2026-09-18 12:22 zip was verified geometrically identical to the saved PCB (all nine layers 0.000 mm² difference, identical drill hits) |
| Placement | `production/positions.csv` | Toolkit CPL: 162 rows, all bottom side, including Q2, Q9 and R79–R82; SW6, TP3–TP5 and the DNP resistors are absent |
| Factory BOM | `production/bom.csv` (+ `designators.csv`, `netlist.ipc`) | Toolkit BOM, populated from the footprints' `LCSC` field — 61 codes over 162 placements |
| Upload BOMs | `production/bom_JLC_upload_v4_optimized.csv` (standard) and `..._v3.csv` (brand-conservative) | Every part verified against JLC's library (see `BOM.md`); both updated 2026-09-18 for L1/R14/C9 |
| Matched order | `production/bom_JLC_upload-JLCPCB Assembly Order.xls` | Saved JLC selections from the 30-board order (pre-Fix 4); retain later approved changes too |

The Toolkit files are regenerated locally and are not the same thing as an accepted factory release: the saved
matched order is from September 14, and matching local files does not prove which revision, CAM edits, rotation edits
or substitutions JLC has accepted. Preserve approval emails and accepted assembly previews (including the D2
substitution) with the release record.

[`BOM.md`](BOM.md) is the current, netlist-derived bill of materials (JLC standard build, brand-conservative
variant, and the hand-build/DigiKey list with its cost comparison). The old `BOM.csv` and `assembly/` exports from
September 12–13 were removed on 2026-09-18 because they described the pre-Fix 4 board.

## Part fields (MPN / Manufacturer / LCSC)

[`part_fields.csv`](part_fields.csv) maps every reference to its **prime part** (genuine manufacturer MPN — what a
hand-builder orders from DigiKey/Mouser) and its **LCSC code** (what JLCPCB actually places; same part where LCSC
stocks the original, otherwise the vetted equivalent — the last two columns say which). `J7` is the one deliberate
mismatch: prime = GCT MEM2075, LCSC = SHOU HAN TF PUSH, on the dual-source footprint.

```bash
python fabrication/apply_part_fields.py          # dry run: lists what would change, warns about drift
```
```bash
python fabrication/apply_part_fields.py --write  # apply — KiCad must be closed (the script checks the lock file)
```

The script writes only the `MPN`, `Manufacturer` and `LCSC` fields (hidden) and the DNP flag from the CSV's `DNP`
column; Value, Footprint and vendor fields are untouched, and re-running is a no-op. Afterwards open the schematic
and run **Update PCB from Schematic** with *Update footprint fields* ticked — the Fabrication Toolkit reads `LCSC`
from the footprints, so its `bom.csv` then carries the right part numbers without hand-editing. To change a part,
edit the CSV row and re-run. A fitted part with an MPN but an empty LCSC makes the Toolkit export the MPN as the
JLC part number; the dry run warns about that.

## Generated exports

Gerbers are generated artifacts; there is no requirement to commit them (`fabrication/gerbers/` and
`fabrication/*.zip` are gitignored). Preserve the actual accepted release archive somewhere durable, even if it
stays outside Git.

For a raw KiCad cross-check (not a replacement for the Toolkit set):

```bash
kicad-cli pcb export gerbers -o fabrication/gerbers/ \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts \
  --no-protel-ext --subtract-soldermask silkscreen_pcb.kicad_pcb
kicad-cli pcb export drill -o fabrication/gerbers/ --format excellon \
  --drill-origin absolute --excellon-units mm --excellon-separate-th silkscreen_pcb.kicad_pcb
kicad-cli pcb export pos -o fabrication/gerbers/cpl_all.csv --format csv --units mm --side both silkscreen_pcb.kicad_pcb
```

Raw text diffs against the Toolkit's Gerbers are not meaningful (it adds attributes and uses a different slot
encoding); compare geometry (rasterize or use a viewer) instead.

## Assembly checklist

- Export the **final CPL through Fabrication Toolkit**, preserving its component-rotation corrections. A raw KiCad
  angle may differ from a JLC assembly angle. **Known placement-preview items** (JLC's DFM usually corrects these,
  but confirm in the preview): U2 (TPS2116, SOT-583) and U5 (DW01A) rotation, D8 (SOT-323) rotation, D2 LED
  pad-1/anode convention, J4's footprint anchor being 0.73 mm off its pad pattern, and U4/J7 origin offsets. No
  `FT Rotation Offset` / `FT Position Offset` fields are set on any footprint.
- Reconcile each BOM reference and exact manufacturer/MPN/LCSC code with the accepted order.
  Check the JLC preview for rotation, side and polarity; a matched code alone does not verify these.
- Confirm through-hole soldering for J1, J5, J6 and fitted buttons. They are not all SMT parts.
- Confirm J7's actual locating-peg fit and approved placement before assembly.
- The four 0.5 mm "perforation" polygons on `Edge.Cuts` are below JLC's 1.0 mm minimum routed slot; the earlier
  orders went through with them, so check how those boards turned out.
- Save the accepted files and substitutions together. Regenerate/review the complete set after **every** source
  change rather than mixing a new board with an old placement file (`production/positions.csv` older than the PCB
  is stale by definition).

## Population and origin

- Standard-build DNP: **TP3, TP4, TP5, R43, R45, R58, R66, R72, R74, SW6** — flagged DNP in
  both the schematic and the PCB, so Toolkit exports agree with the BOM. U13 (DS3231MZ+TRL) is
  populated. Keep unselected references in the order when useful for explicit population tracking.
- Holes H1–H5 and the bare test pads TP1/TP2 need no purchased components; TP3–TP5 are 1-pin header footprints,
  DNP in the standard build.
- Centroid uses the KiCad page origin (same as the gerbers); Y is negative (KiCad Y-up
  convention). Preserve a common origin and check the assembled overlay.
- Never populate both sides of mutually exclusive touch/button link options.
