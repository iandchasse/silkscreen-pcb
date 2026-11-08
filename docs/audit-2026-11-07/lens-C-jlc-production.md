# Lens C: will JLCPCB assemble the BQ21040 block correctly from the committed production files?

Auditor: lens C (manufacturing data), 2026-11-07, committed files at 7b7d2fb. claims.md was not read before these results.

## 1. Verdict

Yes, on paper. Every block part (U11, TH1, Q2, C38, R6, R82, plus Q9/R79/R80/R81) has a KiCad land that matches
JLC's own library footprint pin for pin. U11 and Q2/Q9 are JLC's land rotated exactly 180 deg, the 0603s are at 0 deg,
and all have zero origin offset. The CPL rotations in positions.csv come out right by two independent methods:
replaying the Fabrication Toolkit's own code, and placing JLC's footprint at the CPL angle by hand to check that pin 1
lands on the TS pad (U11) or the gate pad (Q2, Q9). U11 needs no 'FT Rotation Offset' (unlike U5 DW01A, whose JLC
land is 90 deg off). The order zip's gerbers carry exactly the committed copper, mask and paste for the block
(0.000 mm deltas), and every block via is in the drill file. Codes, values and quantities agree across the schematic,
part_fields, both BOMs and LCSC. Nothing found would make JLC place this block wrongly or refuse it. The one thing
paper cannot close is JLC's own placement preview at order time. Counts: 0 BLOCKER, 0 MAJOR, 1 MINOR, 6 NOTE.

## 2. Findings

| ID | Sev | Claim | Evidence | Confirmed by | Smallest fix | Conf. |
|---|---|---|---|---|---|---|
| C-1 | MINOR | The Q2/Q5/Q6/Q9 MPN/Manufacturer fields say onsemi BSS138LT1G, but C7420339 is a clone. JLC's page names the maker hongjiacheng, LCSC's JSON brand field says "R+O", and the LCSC datasheet is Zhuhai Hongjiacheng Rev 2.1. part_fields.csv says "clone (hongjiacheng)", so the trail is honest, but anyone buying from the MPN gets a different part from the one JLC fits | extract/lcsc_C7420339.json brandNameEn=R+O; jlcpcb.com/partdetail/C7420339 (hongjiacheng, Extended); datasheets/bss138_c7420339_lcsc p1 | LCSC JSON + JLC page + datasheet | Nothing needed for JLC, which fits by code. Optionally add "R+O" as the LCSC brand alias in the part_fields note. The pinout is the same (1 G, 2 S, 3 D in the datasheet's function diagram), so placement is unaffected | high |
| C-2 | NOTE | The block adds 3 new JLC Extended parts: C202311 (BQ21040DBVR), C13564 (NTC), C107083 (0.22u). C7420339 was already on Rev 1.0. Each new Extended part adds JLC's per-part loading fee | jlcpcb.com/partdetail/C202311 and C13564 (both "Extended"; C202311 PCBA "Economic and Standard", MSL 1); part_fields note for C107083 | JLC pages | Accept, or check the fee in the quote | high |
| C-3 | NOTE | C202311 LCSC stock is 1,500 (0.4175 USD @5). JLC's own stock was not shown on the partdetail page | extract/lcsc_C202311.json | - | Confirm JLC stock (or pre-order) at quote time | medium |
| C-4 | NOTE | The land is KiCad's 'Handsoldering' SOT-23-6: 0.65 x 1.56 mm pads at 2.7 mm row pitch. TI's DBV0006A example is 0.6 x 1.1 at 2.6 mm (SLUSCE2D p.29-30) and JLC's land is 0.6 x 1.1 at 2.7 mm. Paste covers 100 % of the land, about 0.6 mm beyond the lead tips. The mask web between pins is 0.30 mm. Adequate for reflow: the same footprint and paste on U5, Q1 and U6 reflowed fine on the built Rev 1.0 | pcb_block.json pads; gerber apertures RoundRect 0.1625 / 0.6175 (= 0.65 x 1.56) on B_Cu/B_Mask/B_Paste | Datasheet + gerber + Rev 1.0 history | None | high |
| C-5 | NOTE | TH1 B-value: part_fields says B3380, LCSC lists 3455 K. Both are right for NCP18XH103F03RB (B25/50 = 3380 K, B25/100 = 3455 K), so this is not a wrong part | extract/lcsc_C13564.json | Murata series data | Optionally write "B25/50 3380 K" | high |
| C-6 | NOTE | The Toolkit BOM puts BSS138 in 2 rows with the same C7420339 (Q2 on SOT-23_Handsoldering, Q5/Q6/Q9 on SOT-23). jlc_bom.csv merges them into one row of 4. Both are consistent; upload jlc_bom.csv to avoid a duplicate-code warning | head/production/bom.csv l.79/81, jlc_bom.csv | read | None | high |
| C-7 | NOTE | On Rev 1.0, Q2 was an AO3401A (C15127) on the same land, pose and CPL row (90); it is now BSS138 C7420339. Changing the code is enough: both parts have the pinout 1 G / 2 S / 3 D, and JLC's land for C7420339 has the same 180 deg relationship | extract/block_rows.txt l.139 vs l.14; aeb5b39 positions.csv | both methods (below) | None | high |

## 3. Checked and OK

| Check | Result |
|---|---|
| U11 pinout: TI SLUSCE2D pin table (1 TS, 2 OUT, 3 CHG, 4 ISET, 5 GND, 6 IN) vs board pads | 1 TS, 2 P+, 3 CHRG, 4 ISET (R6), 5 GND, 6 USB_VBUS: match |
| U11 KiCad land vs JLC C202311 land | 6 pads, numbered CCW from the top in both; JLC = KiCad rotated exactly 180 deg; origins coincide (pads are symmetric about each origin) |
| Q2/Q9 KiCad land vs JLC C7420339 land | 3 pads; JLC = KiCad rotated 180 deg; origin offset 0. Datasheet pinout 1 G 2 S 3 D matches the board (Q2 G=DET_NODE, S=GND, D=TS; Q9 G=Q9-G, S=B-, D=DET_NODE) |
| TH1, C38, R6, R82 KiCad vs JLC R0603/C0603 lands | 2 pads, pad 1 at -x in both, 0 deg, origin 0; the parts are non-polar |
| CPL method (i): Toolkit source process.py l.222-250 replayed (bottom: (180 - theta) + DB '^SOT-23' 180 + FT field; position = pad-bbox centre, y negated) | U11 -90 -> 90, Q2 -90 -> 90, Q9 90 -> 270, TH1/C38/R6 0 -> 180, R82 90 -> 90; also U5 0 + 90 FT -> 90 and Q1/U6 0 -> 0. Every row equals positions.csv |
| CPL method (ii): JLC's land placed at the CPL angle in JLC's bottom view (CCW seen from below, then mirrored to board view) | U11 @90: JLC pin 1 -> board (-0.95,-1.35) = TS pad, pin 3 -> CHRG, pin 4 -> ISET, pin 6 -> VBUS. Q2 @90: pin 1 -> gate pad, 2 -> GND, 3 -> TS. Q9 @270: pin 1 -> gate, 2 -> B-, 3 -> DET_NODE |
| Calibration against known-good parts | Rev 1.0 (built, works) had Q9 C7420339 @270 and Q2/Q3 on SOT-23_Handsoldering @90, the same rows as now. The Rev 1.01 CPL fix (b448b39) changed only U5, U2, D8, D2, J7, J4 and U4, leaving the SOT-23 3-pin rows and the Q1/U6 SOT-23-6 rows as they were. U5's +90 shows that JLC's SOT-23-6 lands vary, which is why U11 was checked against its own land (180 deg, no FT field needed) |
| CPL positions | Footprint origin = pad centroid for all block parts; positions.csv = board pose (x, -y); no FT Position Offset is present or needed |
| DNP / exclusions | All block footprints have attr=2 (SMD, no exclude-from-pos/BOM, no DNP). Every block part (incl. R10, R12, R17, R67, R70, C23, R79-R86, J1, J5, F1, F2, CR1) is in positions.csv and in both BOMs |
| Value/code consistency (schematic netlist fields, pcb fields, part_fields, bom.csv, jlc_bom.csv, LCSC JSON) | U11 C202311 = TI BQ21040DBVR SOT-23-6; TH1 C13564 = Murata NCP18XH103F03RB 10k 0603 NTC; C38 C107083 = Yageo 220 nF 50 V X7R 10 % 0603; R6 C23162 = 4.7 k 1 % 0603; R82 C25811 = 200 k 1 % 0603; Q2 C7420339 = BSS138 SOT-23. Nothing left over from copied rows (R6 and R82 were 10k C25804 before; both now carry their own codes) |
| Quantities | 1M x8, 100k x6, 0.1u x8, BSS138 x4 (1+3), U11/TH1/C38/R6/R82 x1: Toolkit BOM = jlc_bom |
| Live stock/price (LCSC, 2026-11-07) | C202311 1,500 @0.4175; C13564 320,140; C7420339 459,150; C107083 245,050; C23162 3.69 M; C25811 1.04 M |
| Order zip gerbers vs committed board (method 1: parse the X2 TO.P/TO.C attributes in the zip) | All 20 B_Cu pad flashes of U11/TH1/C38/Q2/R82/R6/Q9 sit at the committed pad centres (delta 0.0000 mm); B_Mask and B_Paste have one flash per pad with the same apertures |
| Order zip drill vs committed board (method 2) | All 47 vias of the block nets in the window are in PTH.drl (0 missing) |
| Mask dams at 0.95 mm pitch | 0.30 mm web (0.95 - 0.65). JLC's minimum is about 0.1 mm, so the dam survives even if JLC enlarges the openings as usual |

## 4. Could not verify on paper

| Item | How to close |
|---|---|
| JLC's placement preview for U11, Q2, TH1 (their DFM view is the final word on rotation, and their engineers may "correct" rows) | At order time, open JLC's component preview. U11's pin-1 dot must sit on the TS pad at board (83.15, 93.45) (top-left pad in board view). Q2's single drain lead must point toward TH1/C38 (y 90.3). Reject any rotation change an engineer applies to U11 |
| JLC (not LCSC) stock of C202311 on the order day | Check in the JLC BOM step; pre-order if short |
| Clone BSS138 parameters (Vth, leakage) as they affect TS/charge enable | Lens A's domain; the same part already works as Q9 on Rev 1.0 |
| First article: U11 fitted the right way round | Before power-up, on the unpowered board: U11 pin 5 to GND < 1 ohm and pin 6 to USB_VBUS < 1 ohm. A 180 deg error would put pins 2/3 there |

## Findings

### Working notes (appended as confirmed)

- N-geom-U11: KiCad lib SOT-23-6_Handsoldering pad1 (-1.35,-0.95), pins 1-3 down the left column; JLC C202311 land pad1 (+1.35,+0.95), pins 1-3 up the right column, 6 pads x=+-1.35, y pitch 0.95, 1.10x0.60. JLC land = KiCad land rotated 180 exactly (pins 2,4,6 also map). Delta = 180 = Toolkit DB '^SOT-23' 180. Origin offset 0 (both pad sets symmetric about origin; EasyEDA head origin (4002.851,3003.351) but pads symmetric about it).
- N-geom-Q2/Q9: KiCad SOT-23(_Handsoldering) pad1 (-1.5|-0.9375,-0.95), pad3 (+x,0); JLC C7420339 pad1 (1.0,0.95), pad2 (1.0,-0.95), pad3 (-1.0,0) = KiCad rotated 180. Delta 180 = DB. Origin offset 0.
- N-geom-0603: JLC R0603/C0603 pad1 at -x; KiCad pad1 at -x. Delta 0, no DB rule matches R_/C_ 0603 (only R_Array/C_Elec/CP rules). Non-polar parts anyway.
- Toolkit math (process.py l.222-250, read): mid=(x, -y) from aux origin; bottom rot = (180 - theta) + DB + 'FT Rotation Offset'; position = pad bbox centre (= footprint origin for all block parts, symmetric lands). Replicated every CPL row: U11 -90 -> 90, Q2 -90 -> 90, Q9 90 -> 270, TH1/C38/R6 0 -> 180, R82 90 -> 90, U5 0 -> 0+90(FT) = 90, Q1/U6 0 -> 0. All match positions.csv exactly.
- Physical check (JLC bottom convention = rotation CCW as seen from below, i.e. board view x-mirrored): U11 at 90 puts JLC pin1 at board (-0.95,-1.35) = KiCad pad 1 (TS), pin3 (0.95,-1.35) = CHRG, pin4 (0.95,1.35) = ISET, pin6 (-0.95,1.35) = USB_VBUS. Q2 at 90: pin1 -> (-0.95,-1) side of pad1 (DET_NODE gate), pin2 -> GND, pin3 -> TS. Q9 at 270: pin1 (0.95,+1) = gate pad, pin2 = B-, pin3 = DET_NODE. All match.
- N-cal: Rev 1.0 (aeb5b39, built, works) CPL had Q9 (BSS138 C7420339, SOT-23) at 270 and Q2/Q3 (then AO3401A C15127, SOT-23_Handsoldering) at 90/90, identical poses and rows to HEAD; b448b39 (the Rev 1.01 CPL fix) changed U5, U2, D8, D2, J7, J4, U4 but left Q1/Q2/Q3/Q5/Q6/Q8/Q9/U6 untouched, i.e. the SOT-23 3-pin rows with the plain DB 180 were judged right against JLC's own lands. Q2 now uses the same C7420339 land as Q9 (verified pad table) in the same orientation family as Rev 1.0 Q3, and BSS138/AO3401A share the 1=G 2=S 3=D pinout, so Q2's 90 is calibrated by both. U5's +90 fix shows a SOT-23-6 JLC land is not always 180 from KiCad, which is why U11 was checked against C202311 directly (it is 180, no FT field needed).
- N-zip: order zip gerbers (KiCad 9.0.6, created 2026-11-07 01:32, X2 comment attributes) parsed independently (reports/C-dl/gerb.py): every B_Cu pad flash of U11/TH1/C38/Q2/R82/R6/Q9 sits at the committed board pad centre with delta 0.0000; pin attributes Q2 1=G,2=S,3=D. B_Mask and B_Paste carry one flash per pad (6/2/2/3/2/2/3) with the same aperture as copper (mask expansion 0 in file, paste 100 %).
- N-mask: U11 mask openings 0.65 wide at 0.95 pitch -> 0.30 mm mask web between adjacent pins (JLC minimum bridge about 0.1 mm green; still >= 0.2 mm if JLC adds its usual ~0.05 mm per side). Paste 0.65 x 1.56 per pin, 100 % of the hand-solder land: toe extends ~0.6 mm beyond the lead tip. Same footprint as U5/Q1/U6 on the built Rev 1.0 boards, which reflowed fine.
