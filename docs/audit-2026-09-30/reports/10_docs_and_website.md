# Docs + site conformity audit (2026-09-30), repo HEAD 3edd0c8

> Run on 2026-09-30 against the committed boards: Rev 1.0 = `aeb5b39` (as ordered), 1.01 = `3edd0c8`.
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Status: complete.

## Findings

### Verified OK (repo)
- Netlist export (scratch copy, kicad-cli 9): 184 refs, 134 nets, DNP = TP3-5, R43 R45 R58 R66 R72 R74, SW6, U14 (matches README/HARDWARE/BOM.md/fab README).
- HARDWARE.md §13 GPIO map: all 39 module pins match the netlist (incl. series-R hops). J6 pins 2/3/7/8/9/10/5 match.
- jlc_bom.csv, Toolkit bom.csv and schematic LCSC fields agree for all 165 fitted refs; values agree; BOM.md part-table LCSC codes agree with jlc_bom. Toolkit: 66 codes / 165 placements (fab README:34 correct).
- R6 4.7k (0.23-0.25 A), R37 15R (13.3 mA), R14 2.2R/C22939, L1 47u, C9 4.7u/50V, U10 C52919131, U4 C2913202 N16R8, R38/R51 300k/100k, USB_STAT ladder values: all as documented.
- Tongue parts (PCB origins y<61.86, x 84-104.5): CR2 CR3 D3 D8 F2 H1 J6 SW10 U8 = exactly the README/HARDWARE list.
- 1.01 3V3 link: new B.Cu 3V3 at y 64.17-65.3 (well clear of a cut at 61.86 or 62.00); crossings at y 62: x 87.53 (vertical) and x 100.60 (diagonal) = commit's bodge coordinates.
- Relative links/anchors in all 40 tracked .md files: none broken.
- No *.bak / caches / lock files tracked.
- Schematic unchanged since aeb5b39, so docs/silkscreen_pcb_schematic.pdf and full-capture.png are still current at 1.01.
- aeb5b39..6871962: no diff in production/, .kicad_pcb, .kicad_sch (as stated).

### Repo-doc findings
- STALE-1.01 README.md:456 and docs/HARDWARE.md:37 - "design content is current to 2026-09-21"; PCB changed 2026-09-30 (3edd0c8).
- STALE-1.01 docs/HARDWARE.md:39-42 and README.md:524-527 - layout PDF claimed current; docs/silkscreen_pcb_layout.pdf last changed aeb5b39 (PCB changed 3edd0c8). Schematic PDF is fine.
- STALE-1.01 README.md:18-20 hero docs/images/board-top.png / board-bottom.png (92b3e74, 2026-09-21): old silkscreen word; bottom lacks new B.Cu 3V3 link.
- STALE-1.01 fabrication/README.md:11, :32, :34 - production regenerated 2026-09-21; zip + netlist.ipc regenerated 2026-09-30 (placement/BOM unchanged).
- STALE-1.01 README.md:375-393 and HARDWARE.md:1570 (cut-line row) - no mention that boards from files before 3edd0c8 (incl. the 2026-09-21 order) lose charge enable when cut (Q2/R81 3V3 feed), nor the bodge.
- NOTE HARDWARE.md:1570 cut line y 61.86 vs x3 build/commit y 62.00; both inside the 61.40-62.50 slot span; new link is >=2.1 mm below either.
- NOTE fabrication/README.md:12,36-39 - release records mention only the 25- and 30-board orders and a Sept-14 matched order; the 2026-09-21 Rev 1.0 order (aeb5b39 files) is not recorded, nor that the 1.01 zip differs from what was ordered.
- NOTE fabrication/BOM.md:321 - off-board panel list omits GDEQ0426T82-T01C (touch-only).
- NOTE fabrication/BOM.md:143 - 30-board cost breakdown still lists "CCTC 22 uF x3" (replaced by C45783 on 2026-09-21; the section is labelled as-costed 2026-09-18).
- NOTE fabrication/BOM.md:146 - "your 30-board quote" (second person; rest is first person).

### More repo-doc findings
- FIX-NOW README.md:204-206 - "fabrication/BOM.md lists an approved alternative for every part"; BOM.md's part tables give one part per position; alternates exist only for U10 (BOM.md:61-64), L2 (:237), SW6 (:295), U13/U14.
- FIX-NOW fabrication/README.md:8 - "the latest pre-order audit is in docs/audit-2026-09-18/"; DESIGN_REVIEW.md:3 points to the later docs/final-review-2026-09-19/FINAL_REVIEW.md.
- NOTE HARDWARE.md:1570 groups D3/D8 as "J6 ... protection parts"; §11 (:1200) says they are the frontlight's own clamps.
- NOTE README.md:42 "As of 21 September 2026 the website is still locked" - still true at site HEAD (teaser gate), date could move to 30 Sept.
- NOTE DESIGN_REVIEW.md:3 status list of later changes could add the 2026-09-30 3V3 link (optional).
- Verified also: J5 1=B-, 2=B+; J6 all 12 pins = HARDWARE §11 table; Q2/R81/R40 pad 2 = 3V3 (bodge text correct); sleep-budget rows re-add to 58 typ / 94.9 max; README cost figures ($223.95/$305.23, ~$150/$77/$50) = site cost-data ($152.62/$77.28/$50.60).
- Old/new silkscreen: aeb5b39 and 6871962 read "maximizing cost and simplicity"; 3edd0c8 reads "maximizing cost-savings and simplicity".

## Site findings (tracked content at site HEAD 978ad04)
- STALE-1.01 public/order/Silkscreen_Reader_PCB_1.0.zip = blob b36c8838 = repo aeb5b39 zip (as ordered); HEAD zip is bbac8f14. Rerun scripts/pricing/order_files.py before ORDER_FILES_OPEN=true. Until then README.md:110 "byte-for-byte the files in production/" holds for BOM/CPL only.
- STALE-1.01 public/docs/silkscreen_pcb.pdf ("PCB plot PDF", App.tsx:223) = repo layout PDF at aeb5b39 (blob 3ed1c5e1).
- STALE-1.01 public/board/board-front.png (+ board-hero.png, same commit 03f1138 2026-09-21 09:29) show "maximizing cost and simplicity"; board-back.png lacks the B.Cu link; board-bare.glb likely same (unverified).
- OK public/docs/silkscreen_pcb_schematic.pdf = repo (bafa3db0, schematic unchanged since aeb5b39); public/kicad/*.png = repo docs/images HEAD blobs; order-data.json BOM 77 rows / CPL 165 rows reproduce production files byte-for-byte (BOM mark, CRLF, quoting emulated).
- OK config-data.ts: GROUP_REFS = README config table; 4 panel MPNs; battery link; RTC handbuild 13.98 (DS3231 $13.85) - $5.50 issue fixed; sources cite part_fields.csv + BOM_handbuild_digikey.csv, no fabrication/BOM.csv refs left; COST.jlc.full 15.95 = cost-data bom sum; 66 part lines = Toolkit 66 codes.
- OK copy: 16 MB/8 MB, 60x111 / 60.05x111.30, 165 fitted, TPS923611+SMAJ33A, Rev 1.0 untested/ordered Sept 21, firmware "built for ... CrossPoint first"/closed beta, never locked, order files paused; README anchors linked from the site resolve.
- NOTE configurator.tsx:1355/:1408 "These are the Rev 1.0 files" + "first Rev 1.0 boards were ordered on September 21": once the 1.01 zip is copied in, say the files include the 30 Sept cut-down charging fix.

Status: COMPLETE.

## Edit list (repo docs, for 1.01)
E1 README.md:456 - replace "The design content is current to **2026-09-21**;" with: "The boards I ordered on 21 September 2026 were made from commit `aeb5b39`. Since then, on 30 September (`3edd0c8`), a 3V3 link lets a board cut down for a smaller display still charge, and one word of the front silkscreen changed. The design content is current to **2026-09-30**;"
E2 docs/HARDWARE.md:37 - same: "The design content is current to **2026-09-30** (the 2026-09-21 order was made from `aeb5b39`; `3edd0c8` added a 3V3 link below the cut line and changed one word of silkscreen);"
E3 docs/HARDWARE.md:39-40 - after re-plotting the layout PDF from HEAD: "**Current full plots:** ... schematic (2026-09-21; unchanged since) ... layout (2026-09-30)". If not re-plotted: "**Full plots:** [schematic] (2026-09-21, still current: the schematic has not changed since) and [layout] (2026-09-21, before the 2026-09-30 3V3 link below the cut line)".
E4 README.md:526-527 - if not re-plotted/re-rendered: "The schematic PDF is current. The layout PDF and the board images at the top date from 21 September, before the 30 September 3V3 link and silkscreen wording; they are not the release record."
E5 README.md, new bullet in "Cutting the board down" (after :383): "- **A board made from files older than 30 September 2026, including my 21 September order, needs one wire after the cut.** The cut takes both 3V3 feeds to the charge-enable switch (`Q2`, `R81`) with it, so the charger never turns on. Bridge the two cut 3V3 stubs at the cut edge (KiCad x 87.53 and 100.60, y 62), or run a wire from `R40` pad 2 to `R81` pad 2. Then, with a correctly oriented cell fitted, check that the TP4056's `CE` pin (pin 8) reads 3.3 V. Boards made from the current files have a 3V3 link below the cut and need nothing."
E6 docs/HARDWARE.md:1570 - "(`U8`, `CR2`, `CR3`, `D3`, `D8`, `F2`), `SW10`" -> "(`U8`, `CR2`, `CR3`, `F2`), the front-light clamps `D3`/`D8`, `SW10`"; append: "On boards made before `3edd0c8` (2026-09-30), including the 2026-09-21 order, the cut also severs both 3V3 feeds to `Q2`/`R81`, so `CE` stays low and the board never charges: bridge the two cut 3V3 stubs (x 87.53 and 100.60) or wire `R40` pad 2 to `R81` pad 2. The current board joins them with a `B.Cu` 3V3 link at y 64.2-65.3, clear of the cut. The x3 build cuts at y 62.00."
E7 fabrication/README.md:11 - "The files in `production/` were regenerated on 2026-09-21 after those changes (see the table below);" -> "The files in `production/` were regenerated on 2026-09-21 after those changes, and that set (`aeb5b39`) is what I ordered that day. On 2026-09-30 (`3edd0c8`) a 3V3 link below the cut line and one silkscreen word were added; the Gerber zip and `netlist.ipc` were regenerated, and the BOM and placement files did not change."
E8 fabrication/README.md:12-13 - append: "The Rev 1.0 order of 2026-09-21 (five boards, two assembled) has all of those but predates the 2026-09-30 3V3 link below the cut line."
E9 fabrication/README.md:32 - "regenerated 2026-09-21 after the slot, ... the `H5` move. Checked against the saved PCB the same day:" -> "regenerated 2026-09-30 after the 3V3 link below the cut line and the silkscreen wording (`3edd0c8`); the 2026-09-21 set (after the slot, ... the `H5` move) is the one ordered that day and was checked against the saved PCB:" (swap in 2026-09-30 if the fab auditor re-ran that check).
E10 fabrication/README.md:34 - "(+ `designators.csv`, `netlist.ipc`)" -> "(+ `designators.csv`, `netlist.ipc`, the latter regenerated 2026-09-30 with the Gerbers)".
E11 fabrication/README.md:7-8 - "the latest pre-order audit is in [...audit-2026-09-18...]" -> "the pre-order audit is in [`../docs/audit-2026-09-18/`](...) and the later block-by-block final review in [`../docs/final-review-2026-09-19/`](../docs/final-review-2026-09-19/FINAL_REVIEW.md)."
E12 README.md:204-206 - "lists an approved alternative for every part on this board. Use that list" -> "lists the exact part for every position, by LCSC code and manufacturer part number, and the few alternates I have checked (`U10`, `L2`, `SW6`, and `U14` for `U13`). Match against that list".
E13 fabrication/BOM.md:321 - insert "GDEQ0426T82-T01C (touch) /" after "GDEY0426T82 (plain) /" (and use "-FL01C" for consistency).
E14 fabrication/BOM.md:146 - "your 30-board quote" -> "my 30-board quote".
Optional: README.md:42 date -> 30 September 2026; DESIGN_REVIEW.md:3 add "and, on 2026-09-30, a 3V3 link below the cut line (`3edd0c8`)"; BOM.md:143 "CCTC 22 uF x3" -> "22 uF x3 (then the CCTC clone)".
Asset actions: re-plot docs/silkscreen_pcb_layout.pdf; re-render docs/images/board-top.png/board-bottom.png. Site: rerun scripts/pricing/order_files.py, copy the new layout PDF to public/docs/silkscreen_pcb.pdf, re-render public/board/*.png (+ board-bare.glb) when convenient.

