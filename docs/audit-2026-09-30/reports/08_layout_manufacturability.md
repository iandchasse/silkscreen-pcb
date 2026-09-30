# Layout / DRC / Manufacturability audit (2026-09-30)

> Run on 2026-09-30 against the committed boards: Rev 1.0 = `aeb5b39` (as ordered), 1.01 = `3edd0c8`.
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Scope: Rev 1.0 (aeb5b39) and 1.01 (HEAD 3edd0c8). Work copies in evidence/layout.

## Findings (appended as confirmed)

### 1. DRC with schematic parity (kicad-cli 9.0.6, --severity-all, stored zone fills)

Copies: layout/v10 (git archive aeb5b39), layout/v101 (git archive 3edd0c8 = HEAD worktree modulo CRLF). .kicad_pro and .kicad_sch byte-identical between the two.

| | 1.0 (aeb5b39) | 1.01 (3edd0c8) |
|---|---|---|
| violations total | 102 | 104 |
| unconnected / parity | 0 / 0 | 0 / 0 |
| clearance, live (all J1 USB-C land pattern, 0.150 vs Power 0.200) | 11 | 12 |
| clearance, excluded (J3) | 3 | 3 |
| track_dangling, excluded (F.Cu button-row stubs) | 4 | 4 |
| track_dangling, live | 0 | 1 (3V3 B.Cu 0.1414 mm @101.001,64.900) |
| starved_thermal (warn) | 25 | 25 |
| silk_edge_clearance (warn) | 33 | 33 |
| silk_over_copper (warn) | 15 | 15 |
| silk_overlap (warn) | 10 | 10 |
| mirrored_text_on_front_layer (warn; empty text box @83.9,61.6) | 1 | 1 |

- Only-in-1.01: the 3V3 stub. J1 pair sets differ between runs (1.0 run: A1-A4 x2, A4-A5, A8-A9, A9-A12, B1-B4, B4-B5 x2, B8-B9, B9-B12 x2); J1 footprint is unchanged -> run-to-run DRC reporting variance, not a layout change. Actual 0.150 mm > JLC 0.127 mm, so fab-OK.
- Because the reported J1 pairs vary run to run, position/UUID exclusions cannot make this deterministic. A one-line custom rule would: `(rule J1_landpattern (condition "A.Parent == 'J1' && B.Parent == 'J1'") (constraint clearance (min 0.15mm)))` in silkscreen_pcb.kicad_dru.
- The 7 .kicad_pro exclusions, all still matching the same UUIDs in both revs:
  - 3 x clearance, J3 pads 1-2, 4-5, 5-6 (SW netclass 0.25 vs 0.20 actual; 0.5 mm-pitch FPC land pattern): STILL JUSTIFIED. 0.20 mm is inherent to the connector and above JLC 0.127.
  - 4 x track_dangling F.Cu, Net-(R20/R19/R18/R60-Pad1) @ y 144-145.5 (bottom button row): STILL JUSTIFIED. These are the intentional front-button tab stubs ending in 0.6 x 0.6 mm F.Mask windows (prior review FAB-07 / HMI-13 / LAY-07). Geometry identical in 1.0 and 1.01.

Non-excluded warnings by class (identical in both revs): starved_thermal 25 (U2.1, U3.2, U11.1, U6/U7/U9 pad 2, C3/C4/C21/C25/C27/C29/C37, R37/R41/R50, J7.6, J7.9 x2, J2.17, J6.4, D3.2, J1.A1 on F.Cu; SW4.1 and SW9.1 spoke to an isolated island; none is a power-path pad); silk_edge_clearance 33 (switch/J1/J6/U4 outlines over the edge, cut-line text boxes, dev-header label, F.Silk polygons at J7 pegs); silk_over_copper 15 (designators R8/CR2/CR3/R38/R83/C34, 3 J2 outline segments, 3 F.Silk polygons at J7 pegs, 3 F.Silk text boxes); silk_overlap 10 (designator/outline and text-box overlaps); mirrored_text_on_front_layer 1 (empty text box). Courtyard overlaps: 0 (check enabled as error).

### 1.0 vs 1.01 plotted-output diff (fresh kicad-cli gerbers + drill, same options)
- B.Silk, F/B.Mask, F/B.Paste, Edge.Cuts, NPTH drill: identical. PTH drill: 1 via moved.
- F.Cu changes only in x 84.3-100.3, y 64.5-67.4; B.Cu only in x 82.5-101.1, y 63.9-68.1.
- F.Silkscreen changes only in x 52.8-94.0, y 82.3-85.1 (the reworded front text line). QR codes (y 132-140) untouched; the 4 LOGO/QR footprint blocks are byte-identical 1.0 vs 1.01. No QR decoder is installed here (no cv2/pyzbar/jsQR), so the 2026-09-21 decode carries over by identity.

### 2. Manufacturability minima (measured; probe DRC with raised custom rules + pcbnew scan; both revs identical)
| item | actual min | where | JLC std 2-layer |
|---|---|---|---|
| track width | 0.200 mm | many | 0.127 OK |
| copper clearance | 0.150 mm | J1 pads, Default-class items | 0.127 OK |
| copper to board edge | 0.475 mm | GND via (82.52,67.80) vs cut-line arc | 0.2-0.3 OK |
| via | 0.6/0.3 mm x192, annular 0.150 | all vias | standard OK |
| copper to hole | 0.300 mm | track vs via hole (Q9-G via) | 0.254 OK |
| hole to hole (wall) | 0.450 mm | J1 pins; GND via (84.32,89.68) vs CHRG via (85.00,90.00) | ~0.45-0.5, at limit (accepted FAB-01) |
| PTH drill | 0.200 mm x18 | U4 EP (12) and U11 EP (6) thermal vias | below 0.3 std via drill; JLC min 0.15 (may carry small-hole fee) |
| PTH annular | 0.150 mm | J1 16 pins + shell slots | below JLC 0.18 guidance; accepted FAB-01 |
| plated slot | 0.60 mm | J1 shell | OK |
| NPTH | 1.05 x 1.5 slot | J7 | 1.0 OK |
| routed cut-outs | 1.30 / 1.10 mm (centre line) | flex slot / cut-line slot | 1.0 OK on centre line; both drawn with 0.20 mm stroke (inner edge 1.10 / 0.90) |
| silk line | 0.10 mm (40 B.Silk), mostly 0.12 | footprint outlines | 0.153 recommended |
| silk text | 0.40-0.50 mm high / 0.10 stroke (191 of 231 texts) | designators, pin labels | 1.0/0.153 recommended; accepted FAB-02 |

### 3. Layout sanity
- Power path widths: VBUS_PRE_FUSE 0.40; USB_VBUS 0.25-0.40; P+ 0.40 (one 0.25 seg); /P+_FUSE, B+, B- 0.40; LDO_IN 0.25; 3V3 0.25 (18 vias). 1 oz outer: 0.25 mm ~0.87 A, 0.40 mm ~1.2 A at 10 C rise (IPC-2221) vs <=0.5 A USB, ~0.25 A charge. OK. GND pour: thermal, 0.5 mm gap / 0.5 mm spokes; no power-path GND pad is starved.
- Antenna (U4 WROOM-1, rot -90, B side): antenna zone x 44.70 to ~50.7, y 93.45-111.55; board notch x 44.24-50.59, y 93.3-112.0 removes all board under it; nearest pour starts x ~51.06 on both layers (edge clearance 0.475). No copper under the antenna. Note the U4 footprint keepout bans tracks/vias/pads but has (copperpour allowed): the notch, not the keepout, keeps the pour out.
- USB: DP 45.76 mm (3 vias), DN 46.24 mm (1 via), 0.20 mm, edge gap >=0.26 mm, <=0.5 mm gap over 59% of length. Fine for ESP32-S3 full-speed USB.
- FPCs: J2/J3/J4 are FH34SRJ (top and bottom contact), so the fold through the slot cannot present the wrong contact face. J2 pin 1 proven (EPD-02 refuted); J3 mapping rests on the owner-verified light-strip flex (LED-12, known); J4 pinout documented (08). Not touched by 1.01.
- Battery legend: B.Silk "-  +  CHECK" (1.0 mm TrueType) at x 85.5-88.0: '+' glyph centre y 65.63 beside J5 pad 2 = B+ (y 65.5), '-' glyph y 67.68 beside pad 1 = B- (y 67.5). Correct.

### 5. Fab-order facts
Board: 2 copper layers, 1.6 mm, no (stackup) block, so finish, copper weight and mask colour are not in the board. README/fabrication README: 1 oz outer copper, 1.6 mm; finish and mask colour "your choice". Vias tented both sides, mask expansion 0, min web 0. Title block (both revs, and schematic identical): "Silkscreen Reader PCB", rev 1.0, 2026-09-12, idc LLC, CERN-OHL-S-2.0, github.com/iandchasse/silkscreen-pcb. No revision text on either silkscreen layer.

## Findings
- [FIX-NOW] (1.01) Revision still labelled 1.0: title block rev 1.0 / 2026-09-12 in HEAD pcb and sch, production zip still Silkscreen_Reader_PCB_1.0.zip, no rev text on silk; only a reworded front-text word tells boards apart. Fix: rev 1.01 + date, rename zip, add small "v1.01" silk text.
- [FIX-NOW] (1.01) Known 3V3 dangling stub 0.141 mm @(101.001,64.9): only new live DRC item; snap/delete the 1 um stub or exclude.
- [FIX-NEXT-REV] (1.0/1.01) Six tented vias inside the four F.Silk QR codes: (47.50,135.60) (50.90,134.70) (54.14,133.60) in QR x47.4-55.3; (68.38,133.22) in QR x68.3-76.1; (81.70,133.62) in QR x78.3-86.1; (94.30,137.20) in QR x88.3-96.1. (54.14,133.60) sits on the top-right finder's lower edge, (68.38,133.22) on the top-left finder's left edge, (81.70,133.62) on the timing row. Plotted-silk decode cannot see drill holes. Each 0.3 mm hole ~1 module (0.271 mm); EC-L should absorb it. Scan the first boards with a phone; next rev move these vias out of the QR areas.
- [FIX-NEXT-REV] (1.0/1.01) Both internal cut-outs are Edge.Cuts polygons with a 0.20 mm stroke (rest of outline 0.05): cut-line slot 5.30 x 1.10 centre line = 0.90 mm inner edge. Centre-line routing and the accepted 1.0 order make this fine; redraw at 0.05 mm (AUTHOR_TODO item 2).
- [NOTE] (1.0/1.01) J1 clearance items cannot be pinned by .kicad_pro exclusions (pairs change run to run); a .kicad_dru rule would: (rule J1_landpattern (condition "A.memberOfFootprint('J1') && B.memberOfFootprint('J1')") (constraint clearance (min 0.15mm))).
- [NOTE] (1.0/1.01) U4 keepout allows copper pour; add copperpour not_allowed as a guard in case the notch ever changes.
- [NOTE] (1.0/1.01) 18 x 0.2 mm drills (U4/U11 EP thermal vias) are below the 0.3 mm standard 2-layer via drill; JLC builds them (min 0.15) but they may carry a small-hole charge on the 1.01 quote.
- UPDATE to the QR/via finding (qrvia.py, ink under each 0.3 mm hole intersected with the QR's own F.Silk polygons): 3V3 (81.70,133.62) 0.85 module; GND (94.30,137.20) 0.29; 3V3 (50.90,134.70) 0.61; 3V3 (47.50,135.60) 0.38; LED_SW (54.14,133.60) 0.89; I2C_SCL (68.38,133.22) 0.87. At most ~1.9 module-equivalents per code (the x47-55 code), far inside EC-L's 7-codeword margin, and no finder loses more than one module. Severity lowered to NOTE: expected to scan; move the vias only if a rev touches that area anyway.

