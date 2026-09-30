# Fab outputs check (C_fab)

> Run on 2026-09-30, before commit `3edd0c8` existed: **HEAD / OLD / CONTROL = `6871962`** (design and production files
> identical to `aeb5b39`, the Rev 1.0 order) and **working copy / NEW / FIX = the change later committed as `3edd0c8`** (1.01).
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Status: complete - PASS, no blockers

## Findings

### 1-2. zip_old (HEAD) vs zip_new (working copy), comment/date lines ignored  [info]
- Same 13 files in both zips. Changed content: B_Cu (+11 lines net), F_Cu (-66 lines net), F_Silkscreen (+474 lines net), PTH.drl (1 hit), PTH-drl_map (10 lines).
- Unchanged content (only G04/TF.CreationDate/';' lines differ): B_Mask, F_Mask, B_Paste, F_Paste, B_Silkscreen, Edge_Cuts, NPTH.drl, NPTH-drl_map. Exactly the expected set; masks unchanged => moved via is tented.
- PTH.drl only real change: `X99.3Y-65.6` removed, `X98.6Y-67.4` added (the moved GND via). Drill origin = absolute (0,0), Y negated.

### 3. Freshness: re-plot of saved board (new.kicad_pcb + repo .kicad_pro) with kicad-cli 9.0.6 vs zip_new  [info - PASS]
- Gerber options used: 9 layers, Protel ext, --no-x2 (matches the zip's `G04 #@!` attribute style), --subtract-soldermask, --use-drill-file-origin (aux origin is (0,0) so moot), precision 6. Drill: excellon, absolute, decimal, mm, PTH/NPTH split, gerberx2 map precision 5.
- F_Silkscreen, B_Silkscreen, F/B_Mask, F/B_Paste, Edge_Cuts, PTH-drl_map, NPTH-drl_map: identical after dropping comment/date lines.
- F_Cu, B_Cu: raw line order differs (the GUI session's track list order vs file-load order), but a parsed geometry multiset (aperture definition + polarity + every D01 draw / D03 flash / G36 region contour) is IDENTICAL: F_Cu 757 = 757 primitives, 0 only-in-either; B_Cu 2146 = 2146, 0 only-in-either. So the zone fills in the zip equal the fills saved in the board (the plugin's AUTO FILL refill did not change anything).
- PTH.drl / NPTH.drl: first run differed only in oval-slot syntax (zip uses route mode G00/M15/G01/M16, kicad-cli default is G85); re-run with --excellon-oval-format route => identical non-comment content for both.
- Conclusion: the zip is exactly what the saved board produces; not stale.

### 3b. Geometry evidence old -> new (gerber coords = KiCad mm, Y negated; aux/drill origin (0,0))  [info]
- B_Cu ADDED (0.25 mm = 3V3): (82.926,68.774)->(86.600,65.100)->(90.200,65.100)->(90.4,65.3)->(91.527,64.173)->(98.488,64.173)->(98.841,64.526)->(99.359,64.526)->(99.485,64.4)->(100.7,64.4)->(100.9,64.6)->(100.9,64.8)->(101.0,64.9)->(101.001,64.9)->(101.101,65.0); x=101.101 vertical now split 68.561->64.6->62.501; old (82.926,68.774)->(87.4,64.299) split at (86.600,65.100). Target segment (91.527,64.173)->(98.488,64.173) present in new, absent in old. Note one 1 um stub (101.0,64.9)->(101.001,64.9) - harmless.
- B_Cu 0.2 mm (PWR_BUTTON) old y~64.2 route (88.2,64.2)->(98.0875,64.2)->... removed; new route via y 65.9 / 65.127 / 64.599 / 64.999 / 65.9 to (100.2875,66.4) added.
- F_Cu 0.2 mm (LED_SW) small jog near (98.65..99.95, 64.8..66.2) replaced by (98.651,64.813)->(98.651,65.151)->(102.859,69.359).
- Via flash 0.6 mm: (99.3,65.6) removed and (98.6,67.4) added on BOTH F_Cu and B_Cu; drill hit likewise. Masks unchanged => tented.
- Zone regions: only the local GND pour pieces around x 81..103, y 54..89 changed (B_Cu) and the F_Cu pour pieces near the via (one small F_Cu island at x 98.45..100.27 y 65.14..67.34 disappeared). No change anywhere else on either copper layer.

### 4. IPC-D-356 netlist  [info - PASS]
- kicad-cli `pcb export ipcd356` of the saved board vs production/netlist.ipc (CR stripped, `C` comment lines dropped): 796 = 796 lines, IDENTICAL in order and content once the VIA soldermask field is masked.
- HEAD vs repo netlist.ipc: the only real change is the moved GND via: `X+039094Y-025827` (99.30, 65.60 mm) -> `X+038819Y-026535` (98.60, 67.40 mm). (IPC-D-356 from KiCad lists pads/vias only, no tracks, so the new 3V3 trace cannot show here.)
- Pre-existing oddity (not introduced by this change): all 192 VIA records end in a garbage soldermask access code instead of S0..S3 - HEAD `S723909427`, repo `S-1014574029`, fresh re-export `S61323747` (value changes every export => uninitialised value in the KiCad 9.0.6 exporter). Pad records are fine (S0/S1/S2/S3). It was already in the file that went to the fab on 2026-09-21 and the order went through, so info only; it is why a raw diff of netlist.ipc shows 192 changed lines.

### 2b. Deltas are confined  [info]
- F_Silkscreen old->new: 167 glyph regions removed, 179 added, all inside the Welcome box (x 52.79..93.97, y 82.32..85.05 = paragraph 2 only). Nothing else on F.SilkS changed.
- PTH-drl_map: only the via marker moved (98.75/98.45, 67.40) replaces (99.45/99.15, 65.60) (drill-map precision 4.5, so X9875000 = 98.75 mm).

### 5. Welcome text box fit (F_Silkscreen gerber, box x 51.2..95.6, y 78.4..113.06, border 0.1 mm dashed, margins 1.0025)  [info - PASS]
- Border: 108 dashes of 0.1 mm in both old and new, outer extents x 51.15..95.65, y 78.35..113.11 (unchanged).
- Text glyphs (all G36 regions; Roboto): old 1486, new 1498, all fully inside the border; 0 straddle the border; 0 clear-polarity (mask-subtract) shapes inside the box; 0 other silkscreen shapes touch the box rectangle.
- Overall text extents identical old vs new: x 52.302..94.486, y 79.293..112.268. Rightmost new glyph in the edited paragraph x 93.965 (< 94.598 margin limit).
- Lowest glyph bottom y = 112.268 in BOTH old and new (region at x 56.65..56.90, last line "project within our community..."). Clearance to box bottom edge 113.06: 0.792 mm to the border centreline, 0.742 mm to the border's inner edge. Unchanged, because the edited paragraph still wraps to 2 lines ("...maximizing cost-savings" / "and simplicity for DIY. Please build...") and nothing below it moved.
- No overflow, no overlap.

## Result
PASS. The committed zip + netlist.ipc are exactly what the saved board produces (geometry-identical re-plot; drill files identical in route-slot mode; IPC netlist identical apart from KiCad's per-export random VIA S-field). Only the expected layers changed; masks/paste/B.SilkS/Edge_Cuts/NPTH unchanged. No blockers.

