# a3 fabout (prod set verify)
- Gerbers zip vs gerbers_now: all 9 layers identical (raster diff 0.000 mm2 @20px/mm and normalized text identical). Drill hole sets identical (PTH 288 holes, NPTH). Slots identical, only encoding (zip G00/M15/G01/M16 routed, now G85).
- positions.csv == emulation for 162 rows, 0 diffs; DNP/SW6/TP3-5 absent; Q2,Q9,R79-82 present; all bottom.
- bom.csv == emulated bom == part_fields for fitted parts; v4 upload stale for C9,L1,R14. 61 codes/162 placements.
- No FT fields in PCB; CPL risk rows unchanged (U2 270, U5 0, D8 0, D2 270, J4 anchor 92.5 vs 93.23, U4 270, J7 180).
- Live: 26 Extended (unchanged), preferred: C19077501 C19077543 C7420339 C22810 C16581. Cost $33.23/22.70/16.25/12.61.
- Edge_Cuts: perforation polys shortened by 0.2 mm vs Sep16 (still 0.5 wide); slot unchanged.
