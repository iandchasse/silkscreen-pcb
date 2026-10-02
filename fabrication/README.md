# Fabrication & assembly — Silkscreen (silkscreen_pcb)

Active assembly workflow: **JLCPCB**, using KiCad **9.0.6** and the **Fabrication Toolkit**
for placements. Board: 2 layers, 60 × 111 mm, 1.6 mm thickness, 1 oz copper.

**Read [DESIGN_REVIEW.md](../DESIGN_REVIEW.md) before releasing files.** It is the only
engineering verdict/action list. The pre-order audit is in
[`../docs/audit-2026-09-18/`](../docs/audit-2026-09-18/PREORDER_CONFIRMATION_AUDIT.md), the final review in
[`../docs/final-review-2026-09-19/`](../docs/final-review-2026-09-19/FINAL_REVIEW.md), and the audit of the Rev 1.0
order and of Rev 1.01 in [`../docs/audit-2026-09-30/`](../docs/audit-2026-09-30/AUDIT.md).
The current source (with the USB-present reverse-battery gate, L1 47 µH, R14 2.2 Ω and C9 4.7 µF)
has **185 references = 166 fitted + 11 DNP + 8 bare-copper** (H1–H6, TP1, TP2) as of 2026-10-01. The 2026-09-21 revision added
the `U14` RTC alternate (DNP), the `F2` PPTC on `J6` pin 12, `R83` + `C34` on the DW01A (VCC filter and CS filter), mounting hole `H6`, and rescaled the `USB_STAT` ladder (`R17`/`R67`/`R70`/`R71`/`C23`) and `R57` for sleep current. The files in `production/` were regenerated on 2026-09-21 after those changes, and that set (`aeb5b39`, 184 references, 165 fitted) is what I ordered as Rev 1.0. Rev 1.01 adds a 3V3 link and GND stitching vias below the cut line, one silkscreen word and the revision label (2026-09-30), then `R84` (1 Ω 0603 in series with `C2`'s ground leg, a USB hot-plug damper) and corrected JLC placement rows for seven parts (2026-10-01). The Gerber zip, BOM, placement and `netlist.ipc` were regenerated on 2026-10-01 after those changes (see the table below). Regenerate them again after any further schematic or PCB edit.
The two orders before Rev 1.0 (25 and 30 boards) predate the reverse-battery gate, the Q4/R37 changes and the
slotted microSD land; the Rev 1.0 order of 2026-09-21 (five boards, two assembled) has all of them.

The step-by-step JLCPCB upload flow and the optional/base part groups are in the root
[README](../README.md#order-an-assembled-board-step-by-step).
**JLCPCB is the only route that has produced working boards.** Other factories are supported in the sense that
their upload files are generated and kept current — `python fabrication/make_fab_files.py --split` writes a
PCBWay BOM + placement file, a NextPCB BOM + centroid and an assembly drawing into
[`production/other_fabs/`](../production/other_fabs/) (last regenerated 2026-10-01, 166 placed parts). My NextPCB attempt did not end in a
successful order and I have not tried PCBWay. What was learned from the NextPCB
Rev0 upload (DNP lines merged into fitted ones, through-hole previews, error list, cost) is in
[NEXTPCB_REV0_NOTES.md](NEXTPCB_REV0_NOTES.md). Which factory to use is the builder's choice; only the JLCPCB flow
has a known-good order behind it.

## Release records

Keep these together as one revision, including the accepted factory copies:

| Record | Local file | Meaning |
|---|---|---|
| Gerbers/drills | `production/Silkscreen_Reader_PCB_1.01.zip` | Toolkit output for Rev 1.01, regenerated 2026-10-01 after `R84` and small silkscreen, via and track moves (SHA-256 `5b819f118d68fdfb66f1a2b9730adf1a03a037deb35db2c6806597da54fc15bf`; the 2026-09-30 build, after the 3V3 link, the GND stitching vias and the revision label, was `b5dd45717a1f020ebb1ed955d8a57220b5b45561654b625995147a747c2d12c4`). Checked against the saved PCB the same day: DRC with schematic parity shows 0 unconnected items and 0 parity errors, every Gerber and both drill files match a fresh `kicad-cli` export as sets of shapes, six 2.2 mm mounting holes in the PTH drill file, 36 drawn paste regions for the FPC connectors, and `netlist.ipc` matches a fresh IPC-D-356 export. Re-verify after any board change |
| Rev 1.0 order | `aeb5b39` in git history (`production/Silkscreen_Reader_PCB_1.0.zip`, SHA-256 `e290d9f8c06ecd16648d669e4c9031dfae5897e00b27bb2fdbdec81dc83f471c`); the Toolkit run `production/backups/Silkscreen_Reader_PCB_1.0_2026-09-21_02-22-58.zip` — **local only** | The set ordered from JLCPCB on 2026-09-21, regenerated that day after the slot, QR code, `U14`, `F2`, `R83`, `C34`, `H6` and the `H5` move. Checked against the saved PCB: identical coordinate operations on `B.Cu`, `F.Cu`, `B.Mask`, `B.Paste`, `F.Silkscreen` and `Edge.Cuts` versus a fresh `kicad-cli` export, six 2.2 mm mounting holes in the PTH drill file, 36 drawn paste regions for the FPC connectors; re-checked in the 2026-09-30 audit |
| Placement | `production/positions.csv` | Toolkit CPL: 166 rows, all bottom side; `U14`, `SW6`, `TP3`–`TP5` and the DNP resistors are absent, and so are the bare-copper `TP1`/`TP2` and `H1`–`H6`. The rows for `U2`, `U5`, `D2`, `D8`, `J4`, `J7` and `U4` come out corrected for JLC's library footprints from the Toolkit offset fields (see the assembly checklist) |
| Factory BOM | `production/bom.csv` (+ `designators.csv`, `netlist.ipc`) | Toolkit BOM, populated from the footprints' `LCSC` field — 67 codes over 166 placements |
| Upload BOM | `production/jlc_bom.csv` | **The single BOM to upload** (called `bom_JLC_upload_v4_optimized.csv` until 2026-09-21; the older brand-conservative `..._v3.csv` was deleted the same day). Every part verified against JLC's library (see `BOM.md`); every fitted reference's value and part code cross-checked against the schematic and against the Toolkit's `bom.csv` on 2026-09-21, and against `bom.csv` again on 2026-10-01 after `R84` (`C22936`, Basic) was added. DNP parts are listed with an empty part number so JLC skips them |
| Matched order | `production/bom_JLC_upload-JLCPCB Assembly Order.xls` — **local only, not tracked in this repository** | Saved JLC selections from the 30-board order (pre-Fix 4); retain later approved changes too |

The Toolkit files are regenerated locally and are not the same thing as an accepted factory release: the saved
matched order is from September 14, and matching local files does not prove which revision, CAM edits, rotation edits
or substitutions JLC has accepted. Preserve approval emails and accepted assembly previews (including the D2
substitution) with the release record.

[`BOM.md`](BOM.md) is the current, netlist-derived bill of materials (the JLC standard build and the
hand-build/DigiKey list with its cost comparison). The old `BOM.csv` and `assembly/` exports from
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
  angle may differ from a JLC assembly angle. **Seven parts' rows did not match JLC's library footprints** (U2
  TPS2116 SOT-583 and U5 DW01A rotation, D8 SOT-323 rotation, D2 LED polarity, J4's footprint anchor 0.73 mm off its
  pad pattern, U4/J7 origin offsets). Since 2026-10-01 they carry Toolkit fields on both the schematic symbol and
  the footprint, so every Toolkit run writes the corrected rows: `FT Rotation Offset` -90 on U2, 90 on U5, 180 on
  D2 and D8; `FT Position Offset` `1.6,-5.3` on J7, `-0.73,0.218` on J4, `0,-3.664` on U4. D2's KiCad **pad 1 is
  the cathode**; JLC's pin 1 for it is the anode, hence its 180°. Still set JLC's **Confirm Parts Placement** to
  Yes and check these parts in the preview.
- Reconcile each BOM reference and exact manufacturer/MPN/LCSC code with the accepted order.
  Check the JLC preview for rotation, side and polarity; a matched code alone does not verify these.
- Confirm through-hole soldering for J1, J5, J6 and fitted buttons. They are not all SMT parts.
- Confirm J7's actual locating-peg fit and approved placement before assembly.
- The tongue neck is now a **single 5.30 × 1.10 mm slot** on `Edge.Cuts` (x 89.59–94.89, y 61.40–62.50), at or
  above JLC's 1.0 mm minimum routed slot, as is the 47.04 × 1.30 mm display-flex slot. The four 0.5 mm
  "perforation" polygons the earlier orders went through with are gone; no slot DFM note is expected now.
- Save the accepted files and substitutions together. Regenerate/review the complete set after **every** source
  change rather than mixing a new board with an old placement file (`production/positions.csv` older than the PCB
  is stale by definition).

## Population and origin

- Standard-build DNP: **TP3, TP4, TP5, R43, R45, R58, R66, R72, R74, SW6, U14** — flagged DNP in
  both the schematic and the PCB, so Toolkit exports agree with the BOM. U13 (DS3231MZ+TRL) is
  populated; `U14` (RV-8263-C7) is its DNP alternate — fit one or the other, never both. Keep unselected references in the order when useful for explicit population tracking.
- Holes H1–H6 and the bare test pads TP1/TP2 need no purchased components; TP3–TP5 are 1-pin header footprints,
  DNP in the standard build.
- Centroid uses the KiCad page origin (same as the gerbers); Y is negative (KiCad Y-up
  convention). Preserve a common origin and check the assembled overlay.
- Never populate both sides of mutually exclusive touch/button link options.
