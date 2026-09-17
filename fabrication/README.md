# Fabrication & assembly — Silkscreen (silkscreen_pcb)

Active assembly workflow: **JLCPCB**, using KiCad **9.0.6** and the **Fabrication Toolkit**
for placements. Board: 2 layers, 60 × 111 mm, 1.6 mm thickness, 1 oz copper.

**Read [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) before releasing files.** It is the only
engineering verdict/action list. The current source (2026-09-17, with the Fix 4 reverse-battery
circuit) has **179 references = 162 fitted + 10 DNP + 7 bare-copper** (H1–H5, TP1, TP2).
The two previous orders (25 and 30 boards) predate Fix 4, the Q4/R37 changes and the slotted
microSD land; their exports are kept for reference only.

## Authoritative release records

Keep these as one revision, including the accepted factory copies:

| Record | Reviewed local file | Meaning |
|---|---|---|
| Gerbers/drills | `production/Silkscreen_Reader_PCB_1.0.zip` | Local archive checked against the reviewed PCB |
| Upload BOM | `production/bom_JLC_upload_v4_optimized.csv` | Standard JLC build, every part verified against JLC's library (see `BOM.md`); `bom_JLC_upload_v3.csv` is the brand-conservative variant |
| Matched order | `production/bom_JLC_upload-JLCPCB Assembly Order.xls` | Saved JLC selections from the 30-board order (pre-Fix 4); retain subsequent approved changes too |
| Placement | `production/positions.csv` | Toolkit placement file — **regenerate** after the Fix 4 / DNP-flag edits; it must list Q2, Q9, R79–R82 |

The saved matched order is September 14 and the local ZIP September 16. This does not
prove which files are currently accepted at JLC. Preserve approval emails and accepted
assembly previews, including the D2 substitution, with the release record.

`BOM.md` is the current, netlist-derived bill of materials (JLC standard build, brand-conservative
variant, and the hand-build/DigiKey list with its cost comparison). `BOM.csv` and the older
`assembly/` exports are **historical** and not synchronized. Q4 = IRLML6346TRPBF and R37 = 15 Ω
are applied in the source and in the v3/v4 uploads.

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

## Reference files versus generated exports

Tracked in git:
```
fabrication/
  README.md            this file
  BOM.md / BOM.csv      historical sourcing (MPNs, supplier links, alternates, pricing)
  assembly/
    bom_jlcpcb.csv      JLC BOM format (Comment, Designator, Footprint, LCSC Part #)
    cpl_jlcpcb.csv      JLC placement (Designator, Mid X, Mid Y, Layer, Rotation)
    cpl_all.csv         raw KiCad centroid, both sides
```

Gerbers are generated artifacts; there is no requirement to commit them. Preserve the
actual accepted release archive somewhere durable, even if it stays outside Git.

## Regenerate the gerber + drill set

For a raw KiCad cross-check, export:

```bash
kicad-cli pcb export gerbers -o fabrication/gerbers/ \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts \
  --no-protel-ext --subtract-soldermask silkscreen_pcb.kicad_pcb
kicad-cli pcb export drill -o fabrication/gerbers/ --format excellon \
  --drill-origin absolute --excellon-units mm --excellon-separate-th silkscreen_pcb.kicad_pcb
```

Then zip `fabrication/gerbers/` and upload it. Board: 2-layer, 1.6 mm, 1 oz Cu; outline on `Edge.Cuts`.

## Assembly

The CLI can produce a raw centroid for inspection:
```bash
kicad-cli pcb export pos -o fabrication/assembly/cpl_all.csv --format csv --units mm --side both silkscreen_pcb.kicad_pcb
```

- Export the **final CPL through Fabrication Toolkit**, preserving its component-rotation
  corrections. A raw KiCad angle may differ from a JLC assembly angle.
- Reconcile each BOM reference and exact manufacturer/MPN/LCSC code with the accepted order.
  Check the JLC preview for rotation, side and polarity; a matched code alone does not verify these.
- Confirm through-hole soldering for J1, J5, J6 and fitted buttons. They are not all SMT parts.
- Confirm J7's actual locating-peg fit and approved placement before assembly. Do not apply
  the review's possible offset blindly to every socket or factory CPL.
- Save the accepted files and substitutions together. Regenerate/review the complete set
  after source changes rather than mixing a new board with an old placement file.

## Population and origin

- Standard-build DNP: **TP3, TP4, TP5, R43, R45, R58, R66, R72, R74, SW6** — flagged DNP in
  both the schematic and the PCB, so Toolkit exports agree with the BOM. U13 (DS3231MZ+) is
  populated. Keep unselected references in the order when useful for explicit population tracking.
- Holes H1–H5 and bare test points TP1–TP5 need no purchased components.
- Centroid uses the KiCad page origin (same as the gerbers); Y is negative (KiCad Y-up
  convention). Preserve a common origin and check the assembled overlay.
- Never populate both sides of mutually exclusive touch/button link options.
