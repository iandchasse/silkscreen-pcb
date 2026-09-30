# Fab package + BOM/CPL audit (2026-09-30)

> Run on 2026-09-30 against the committed boards: Rev 1.0 = `aeb5b39` (as ordered), 1.01 = `3edd0c8`.
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Scope: Rev 1.0 (aeb5b39) as ordered, Rev 1.01 (3edd0c8). Repo read-only.

## Findings (appended as confirmed)

### Step 1 - 1.0 as ordered (aeb5b39): re-plot vs committed zip  -> PASS
- aeb5b39 zip sha256 e290d9f8... == 6871962 zip == evidence/C_fab/old.zip (byte-identical through 6871962, as stated).
- kicad-cli 9.0.6 re-plot of `git show aeb5b39:silkscreen_pcb.kicad_pcb` (+ .kicad_pro), `--no-x2 --subtract-soldermask`, 9 layers:
  all 9 Gerbers SAME line-for-line except comment/header lines (copper too, no reordering). Geometry multiset identical on every layer
  (F_Cu 763, B_Cu 2128, F_Silk 3523, B_Silk 7510, F_Mask 109, B_Mask 587, F_Paste 0, B_Paste 635, Edge 28 primitives).
- Drill: `--excellon-oval-format route --excellon-separate-th --generate-map --map-format gerberx2`: PTH.drl, NPTH.drl and both maps SAME except comments;
  sorted hole-line md5 identical. (Without --subtract-soldermask the silk differs, so the zip was plotted with mask subtracted from silk, as expected from FT.)
- Method validated on 3edd0c8: same commands reproduce the 1.01 zip (copper equal as a geometry multiset, all else line-equal), matching the earlier check.
- 1.0 -> 1.01 zip delta (geometry): only F_Cu, B_Cu, F_Silk changed; B_Silk, B_Mask, B_Paste, Edge identical.

### Step 2 - BOM/CPL vs board (aeb5b39; CSVs byte-identical at 3edd0c8)  -> PASS with notes
Script: evidence/fab/bomcheck.py (+ dump_fp.py via pcbnew, schematic via `kicad-cli sch export netlist --format kicadxml`), output bomcheck.out.
- Board 188 footprints = 184 schematic refs + 4 `G***` logos (board-only, excluded). Schematic vs board: 0 mismatches in value, footprint,
  DNP, exclude-from-BOM and every custom field (MPN/Manufacturer/LCSC...). Schematic unchanged aeb5b39..3edd0c8 (netlist XML identical).
- 1.0 vs 1.01 boards: every footprint identical in ref, value, fpid, side, x, y, rotation, attributes, fields and pad-1 position -> the
  1.0 CSVs are valid for 1.01 unchanged.
- Attributes: DNP = R43 R45 R58 R66 R72 R74 SW6 TP3 TP4 TP5 U14 (sch and PCB agree); H1-H6 excl BOM+pos; TP1/TP2 excl pos only.
  fitted = 165 placed parts + TP1/TP2 (bare pads, no LCSC).
- jlc_bom.csv: 77 lines, 176 refs, no duplicates; 165 coded refs == the 165 placed parts exactly; the 11 DNP refs are listed with an
  empty code (by design); every Comment == board value; every code == board LCSC field; 66 distinct codes.
- bom.csv (FT): 67 lines = 66 codes + one blank-code line "TP1, TP2"; qty columns right; codes == jlc_bom.csv for every ref.
- designators.csv: 185 entries = every board ref (G***:4). positions.csv: 165 rows, no dups, set == placed set, all bottom.
- SMD positions == footprint anchor (x, -y) exactly. The 13 THT parts (J1 J5 J6 SW1-5 SW7-11) sit at the pad bounding-box centre,
  which is the Toolkit's THT convention (all 13 match the pad-box centre to 1e-4 mm) - not an error.
- Rotation: JLC = (180 - KiCad) + offset. Offsets come only from the Toolkit's built-in DB (no FT/JLC rotation fields on any footprint):
  180 on SOT-23 / SOT-23-5 / SOT-23-6 (Q1-Q9, U1 U3 U5-U9 U12), 270 on SOIC-8 (U13) and SOIC-8-EP (U11), 180 on JST_PH_S (J5); 0 on the rest.
- part_fields.csv agrees with the board fields for every ref (LCSC, MPN, Manufacturer, Value, DNP). (My first pass flagged J2-J4
  Manufacturer 'HRS' - false positive: that is the SnapEDA `MANUFACTURER` field; `Manufacturer` = 'Hirose' matches.)

### Step 3 - other_fabs (generated 2026-09-21 in aeb5b39)  -> PASS
- placement_bottom_kicad.csv 152 SMD rows, nextpcb_centroid.csv 165, split smd 152 / tht 13: sets == placed parts; x, -y and KiCad
  rotation equal the board footprint anchors for every row; all Bottom. pcbway_bom 66 lines/165 refs, nextpcb_bom 66/165, split 62/152 + 4/13:
  no dups/missing/extras; qty right; MPN == board MPN (NextPCB: J6 + 10 switches use nextpcb_substitutes.csv as designed).
- Footprints unchanged in 1.01, so all other_fabs files remain valid for 1.01. assembly_drawing_bottom.pdf was last committed in aeb5b39 with
  the CSVs (B.Fab + Edge only; 1.01 changed only copper/F.Silk).

### Provenance of the as-ordered set
- production/backups/ (gitignored) holds every FT run. The last run before the order, ..._2026-09-21_02-22-58.zip, equals the aeb5b39
  zip byte-for-byte, and its bom/positions/designators/netlist equal aeb5b39's copies apart from line endings (FT writes CRLF; git stores LF under
  .gitattributes `eol=lf`). The ..._2026-09-30_12-22-23.zip run equals the 3edd0c8 set in the same way. No FT run happened between 02:22 on 09-21 and 09-30.

### Step 4 - docs vs files
- README Step 1-5: the three files, 2 layers, 60.05 x 111.30 mm (job file 60.05 x 111.3001), 1.6 mm, 1 oz, finish free, Standard PCBA,
  Assembly side Bottom (F_Paste empty; every CPL row is bottom), jlc_bom.csv + positions.csv, the 11 DNP rows "DNP (standard build)" with blank code: all match.
- U10 = C52919131 in jlc_bom.csv, board and BOM.md. The TPS923611DRLR + SMAJ33A swap is consistent between README:235-250 and BOM.md:61-62 (same DRL and SMA footprints).
- Step 7: 13 THT parts; 74 plated joints (J1 20, J5 2, J6 12, 10 x 4) - matches. Slots 5.30 x 1.10 and 47.04 x 1.30 (Edge.Cuts, less 0.2 mm line width) - match.
- fabrication/README.md: 184 = 165 + 11 + 8; 165 CPL rows; 66 codes; six 2.2 mm PTH holes (T9, 6 hits) and 36 B.Paste regions in both zips; no FT offset fields - all true.
- BOM.md placed tables: every one of the 165 placed refs listed once; qty, LCSC code == jlc_bom.csv, MPN == board/part_fields; DNP table == the 11 DNP.
  Cosmetic only: L1 "47u" vs value "47uH" (BOM.md:236). Fix-4 parts Q2 Q9 R79-R82 present and fitted. $223.95 quote consistent with README:123.

### Findings
1. [FIX-NEXT-REV] (1.0 order / 1.01 files) positions.csv J4: CPL point = anchor, which sits 0.730 mm (x, along the 0.5 mm pitch) from J4's
   pad-pattern centre (J3, same footprint: 0.000). Without JLC's preview correction J4 would land about 1.5 pitches off. Already flagged in
   README Step 6 and fabrication/README.md:92-93. Fix: re-centre the J4 anchor or add `FT Position Offset`, then re-run FT. For 1.0: confirm the
   approved JLC preview shows J4 on its pads.
2. [FIX-NOW] (docs) README Step 6 table (README.md ~258-265) and fabrication/README.md:91-93 omit U10 (TI U_DRL0006A, SOT-563) and the polar
   diodes D3/D4/D5/D6. The Toolkit DB leaves them uncorrected (offset 0), and FAB-21 (sections/09:394+) and AUTHOR_TODO.md:26 both name them. Add them to both lists.
3. [FIX-NEXT-REV] (1.01 files) Put any rotation/position corrections JLC made in the 1.0 placement confirmation (U2 U5 U10 D8 D2 D3-D6 J4 J7 U4)
   into `FT Rotation Offset` / `FT Position Offset` fields, so positions.csv is right by construction. Today there are none, and all of these depend on the preview.
4. [FIX-NOW] (docs) fabrication/README.md:36-41: the release record has no Rev 1.0 order row. "Matched order" points to a local .xls that is not in
   production/ (30-board, pre-Fix 4), and :39 says the matched order is from September 14. :12 still says "The two previous orders". Add a Rev 1.0 row
   (aeb5b39, zip sha256 e290d9f8..., FT backup 2026-09-21_02-22-58, where the JLC-matched BOM and preview screenshots are kept) and a 1.01 = 3edd0c8 note.
5. [NOTE] (docs) fabrication/README.md:85-86 and README.md:567-575: "raw text diffs ... not meaningful ... different slot encoding" is out of date.
   `pcb export gerbers --no-x2 --subtract-soldermask` (Protel extensions) plus `pcb export drill --excellon-oval-format route --excellon-separate-th
   --generate-map --map-format gerberx2` reproduce the FT files line-for-line except comments. The F.SilkS alias works in 9.0.6 (tested).
6. [NOTE] (1.01 files) bom.csv carries a blank-code "TP1, TP2" line: those pads are excluded from pos but not from BOM. Harmless, because jlc_bom.csv
   omits them. Next rev: tick Exclude from BOM on TP1/TP2.
7. [NOTE] (hygiene) jlc_bom.csv is hand-maintained and no script checks it (make_fab_files.py checks positions.csv only). It matches exactly today;
   consider adding a jlc_bom-vs-board-LCSC check to make_fab_files.py.
8. [NOTE] (docs) fabrication/README.md:7-8 calls docs/audit-2026-09-18 "the latest pre-order audit"; docs/final-review-2026-09-19 is newer.
9. [NOTE] (hygiene) production/ and fabrication/: no stray tracked or untracked files; only the gitignored production/backups/. Keep the 09-21 02:22:58 backup
   as the as-ordered archive. The working-tree CSVs are CRLF and a clone gets LF: same content. The next make_fab_files.py run will redraw
   assembly_drawing_bottom.pdf (the board is newer); expect a PDF-only diff.
Known item confirmed: fabrication/README.md:11 "The files in `production/` were regenerated on 2026-09-21 after those changes (see the table below)"
and :32 "Toolkit output, regenerated 2026-09-21 after the slot, QR code, `U14`, `F2`, `R83`, `C34`, `H6` and the `H5` move. Checked against the saved PCB the same day"
-> should say the zip and netlist.ipc were regenerated 2026-09-30 (FT 12:22:23) for 1.01 and BOM/CPL are unchanged since 2026-09-21. The :32 hole and paste claims still hold.

