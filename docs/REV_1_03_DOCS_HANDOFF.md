# Rev 1.03: hand-off for the user docs and images

**For:** whoever updates the user-facing documentation and images for Rev 1.03, an agent or a person.
**Written:** 2026-11-03, with the commit that brought the `1.03` design files up to date. **Branch:** `1.03`.

The Rev 1.03 design work is finished and checked, but the user docs and images still describe Rev 1.02. This note
lists what changed, what to update in each file, and how to check the result. [REV_1_03_STATUS.md](REV_1_03_STATUS.md)
is the engineering hand-over; this note covers only the docs.

## 1. Ground rules

- **Source of truth:** `silkscreen_pcb.kicad_sch`, `silkscreen_pcb.kicad_pcb` and `fabrication/part_fields.csv`. Where a
  doc disagrees with them, the design files win. Read values, nets and counts from the files (`kicad-cli` exports), not
  from older docs.
- **Docs and images only:**
  - Don't edit the KiCad files or `part_fields.csv`.
  - If something in the design looks wrong, write it down for the owner instead of fixing it.
  - Run `kicad-cli` only with KiCad closed, so nothing fights over the files.
- **Living docs only.** Update these:
  - `README.md` and `docs/HARDWARE.md`;
  - `fabrication/BOM.md`, `fabrication/BOM_handbuild_digikey.csv`, `fabrication/README.md` and `fabrication/THIRD_PARTY.md`;
  - `docs/images/`;
  - `docs/silkscreen_pcb_schematic.pdf` and `docs/silkscreen_pcb_layout.pdf`.
- **Leave dated records as written:** everything under `docs/audit-*/`, and the case write-ups in `docs/BOARD_FAILURES.md`
  (section 3.6 has the one exception).
- **Links:** headings are link targets across the docs, for example `HARDWARE.md#31-usb-c-input--protection`. If you rename
  a heading, fix every link to it, and run the check in section 5 before you finish.
- **Style:** match the existing docs: plain, factual, short sentences, real numbers with units, and references and nets in
  backticks.
- **Line endings:** they don't matter to git, because `.gitattributes` forces LF. Keep each file's current style anyway, to
  avoid noisy diffs.
- **Commits:** only when the owner asks, from his account, with no co-author trailer.
- **Tools on this machine:**
  - `C:\Program Files\KiCad\9.0\bin\kicad-cli.exe`;
  - KiCad's Python with `pcbnew`, in the same folder;
  - system Python with PyMuPDF, Pillow and shapely.

## 2. What changed from Rev 1.02

| Item | Change | Details |
|---|---|---|
| N1 | `F3` feeds the frontlight boost from `LDO_IN` through the new net `/LED_VIN` (`C12`, `L2`, `U10`). It is a PTC with 0.10 A hold and 0.30 A trip (Bourns MF-FSMF010X-2, LCSC `C210355`) | [REV_1_03_STATUS §2](REV_1_03_STATUS.md#2-item-by-item), [NEXT_REVISION N1](NEXT_REVISION.md#n1-frontlight-ptc-f3) |
| N2 | `F4`, the same PTC, replaces `R42` in the touch supply. `R66` (DNP, alternate touch mapping) is unchanged | as above |
| N3 | `F5`, the same PTC, feeds `J6` pin 7 (net `J6_3V3`). Budget: 20 mA on pin 7; heavier loads go to pin 12 | as above |
| N4 | `CR2` is on the `J6` side of `F5`; it did not need to move | as above |
| N5 | `F6`, the same PTC, feeds the e-paper boost (`L1`, `C10`) on the new net `EINK_3V3` | as above |
| N6 | The panel's logic supply (`J2` pins 15/16, `C22`) is on `EINK_3V3`, behind `F6` | as above |
| N7 | DW01A current sense: `R85` ∥ `R86`, two 0.1 Ω 1206 resistors (`C25334`, JLC Basic), 50 mΩ from `Q1` pin 3 (`/B-_SENSE`) to GND. About 62 mΩ with the copper, so the trip window is 0.83–1.68 A with JLC's PUOLOP DW01A | [REV_1_03_STATUS §6](REV_1_03_STATUS.md#6-n7-and-n8-schematic-and-board), [BENCH_THEORY §3.2](audit-2026-11-03/BENCH_THEORY.md#32-the-sense-path-as-placed) |
| N8 | `C34`: 2.2 nF → 0.1 µF | as above |
| N9 | `R6`: 4.7k → 10k. The charge current drops from about 0.23–0.26 A to about 0.11–0.13 A, and `U11`'s heat halves | [NEXT_REVISION N9](NEXT_REVISION.md#n9-r6-from-47k-to-10k) |
| N10 | Closed: `C36`/`C37` stay where they are | [REV_1_03_STATUS §7](REV_1_03_STATUS.md#7-n10-closed-left-as-is) |
| N11 | Dropped: there are no front test pads (no TP6–TP18) | — |
| `U10` footprint | TI's DRL0006A example land, `U_DRL0006A_6L_TI-LAND`, in `KiCad/9.0/3rdparty/TPS923610DRLR/KiCADv6/footprints.pretty/` | [TRACE_AUDIT §1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern) |
| USB-C shell | Tied straight to GND: `J1`'s four shell tabs sit in both GND pours. `R1` and `C1`, formerly 1 MΩ ∥ 1 nF, are gone | [CERT_REVIEW_AUDIT §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03) |
| Revision | Title blocks read Rev 1.03 / 2026-11-03. The back silkscreen prints "Rev 1.03 2026-11-03" at (87.1, 138.8), from the title block | as above |
| Layout | Trace-audit fixes, `F3`'s pour keep-out, mounting-hole and edge clearances, stitching and return vias, the `C33`/`R7` swap at `U4`, teardrops (862), and reference designators (uniform 0.5 mm, 67 moved, `F5`/`F6` shown) | [TRACE_AUDIT §1–1f](audit-2026-11-03/TRACE_AUDIT.md), CERT_REVIEW_AUDIT §6 |
| DRC rules | New `silkscreen_pcb.kicad_dru`: pour pull-back from the switch nodes and high-voltage nets, plus footprint-scoped rules. `J1`'s peg holes and `J3`'s pitch now pass under these rules instead of project-file exclusions | TRACE_AUDIT §1, §1b, §1c |

**Already done in the docs (check, don't redo):**
- README "Step 2: order the bare board": surface finish.
- HARDWARE.md §3.1 shield handling and §16 antenna paragraph.
- BOARD_FAILURES.md's meter-check row 4.
- HARDWARE.md's header note has a temporary bridge sentence (section 3.1).

## 3. Tasks by file

### 3.1 `docs/HARDWARE.md`

- **Header note** (around line 31):
  - Make it describe Rev 1.03.
  - Fold the 1.0/1.01/1.02 differences into a short revision history, and add 1.02 → 1.03 from section 2.
  - Drop the "catches up in the 1.03 documentation pass" bridge sentence.
- **§3.2:** `R6` = 10k and the new charge current (N9), and anything derived from it (charge time, `U11` heat).
- **§3.3:**
  - The sense pair `R85` ∥ `R86`, `C34` = 0.1 µF and the trip window.
  - The probe point for the sense voltage is `R85` pad 1, about 54 mV per amp across `R85`. N11's TP7 was dropped.
- **§5:** N10 is closed, so `C36`/`C37` are unchanged. Describe an SD firmware policy only if NEXT_REVISION §4 F1/F2 have
  been implemented; ask the owner.
- **§6:** `EINK_3V3`, `F6`, and the panel's logic supply behind `F6`.
- **§7:** `F3` and `/LED_VIN`; why `F3` has a 1 mm pour keep-out (it sets the trip time,
  [BENCH_THEORY §2.4](audit-2026-11-03/BENCH_THEORY.md#24-the-studys-model-with-these-numbers)); `U10` on TI's land.
- **§8:** `F4` in place of `R42`; the `R66` alternate.
- **§11:** `J6` pin 7 behind `F5`, the 20 mA budget with pin 12 for heavier loads, and `CR2`.
- **§16:**
  - Re-check the cut-line row: `F2`, `F5` and `CR2` sit above the cut.
  - Re-check the mounting-hole notes.
  - Update "Things that look like mistakes and are not": the `.kicad_dru` rules, and the 6 starved thermals, including
    `J1`'s top-left shell tab on F.Cu.
- **Search the whole file** for changed parts and values: `R42`, `R1`, `C1`, `4.7k`, 2.2 nF next to `C34`, `166`, `185`,
  `1.02`.
- **NEXT_REVISION §5 is out of date in three places.** It asks for:
  - a test-pad table, which is void because N11 was dropped;
  - "TP7 as a current monitor", void for the same reason;
  - `C327066` for the sense resistor, but N7 used two of `C25334` instead.

### 3.2 `fabrication/BOM.md`, `fabrication/BOM_handbuild_digikey.csv`, `fabrication/README.md`

- **Population**, read from the schematic on 2026-11-03: **169 placed + 11 DNP + 8 bare-copper refs = 188**
  (Rev 1.02: 166 + 11 + 8 = 185).
  - The DNP set is unchanged: `R43 R45 R58 R66 R72 R74`, `SW6`, `TP3 TP4 TP5`, `U14`.
  - Bare copper: `H1`–`H6`, `TP1`, `TP2`.
- **BOM lines:**
  - New `F3, F4, F5, F6`: MF-FSMF010X-2, `C210355`, JLC Extended. MF-PSMF010X-2 (`C116171`) is the DigiKey-stocked
    alternate.
  - New `R85, R86`: 0.1 Ω 1206, RL1206FR-070R1L, `C25334`, Basic.
  - `C34` leaves the 2.2n line and joins the 0.1u `C14663` line.
  - `R6` joins the 10k `C25804` line, and the 4.7k line (`C23162`) goes.
  - `R42` leaves the 0 Ω line, `R1` leaves the 1M line, and the 1n `C1` line goes.
- **Extended parts and fees:** re-derive them. NEXT_REVISION §2 says "two new Extended parts" (+$6 per order), but N7
  ended up with a Basic part, so the PTC is probably the only new Extended type. Check `part_fields.csv` against JLC.
- **The hand-build CSV:** the same changes, with DigiKey part numbers.

### 3.3 `README.md`

- **Revision mentions:**
  - The files in `production/` and the zip name (`Silkscreen_Reader_PCB_1.02.zip`) change only when the production files
    are regenerated (section 4).
  - Until then, say that `production/` is still Rev 1.02 rather than renaming anything.
- **Reference and part counts**, wherever they are stated (section 3.2's numbers).
- **The `J6` pinout table:** pin 7 is behind `F5`, with 20 mA available; heavier loads go on pin 12.
- **Build groups** (core and add-ons, at "The files in `production/` are the **full build**"):
  - place `F3` (frontlight), `F4` (touch), `F5` (`J6`), `F6` (e-paper, core) and `R85`/`R86` (core);
  - drop `R1`, `C1` and `R42`.
- **The cutting section:** check it against the board: `F2`, `F5` and `CR2` are above the cut.

### 3.4 `fabrication/THIRD_PARTY.md`

`U10`'s footprint is now `U_DRL0006A_6L_TI-LAND`, drawn from the example land pattern in TI's TPS923610 datasheet
(SNVSCN8B, p. 30), not Ultra Librarian's. The Ultra Librarian symbol stays; so do its footprints, which are now unused.

### 3.5 Images and PDFs

- **Schematic crops** (the 21 block images in `docs/images/` and `full-capture.png`):
  - For Rev 1.02 they were cut from one 400 dpi raster of the schematic PDF, with one background colour (commit
    `c2c1c57`). Re-cut all of them from a 400 dpi raster of the 1.03 schematic (`kicad-cli sch export pdf`), so they match.
  - **Changed blocks:**
    - `01-usb-input`: `R1`/`C1` gone, a new note;
    - `04-charger`: `R6`;
    - `05-battery-prot`: `R85`/`R86`, `C34`;
    - `09-epaper`: `F6`, `EINK_3V3`;
    - `10-led-driver`: `F3`, `LED_VIN`;
    - `15-touch`: `F4`;
    - `16-expansion` and `16b-expansion-esd`: `F5`, `J6_3V3`, `CR2`;
    - possibly `02`, `03` and `07`, where the `3V3`/`LDO_IN` labels changed.
  - **Finding the old rectangles:** rasterise the Rev 1.02 schematic (`git show master:silkscreen_pcb.kicad_sch`) at
    400 dpi and locate each existing image in it. Reuse those rectangles where the frames did not move.
- **Board renders** `board-top.png` and `board-bottom.png`: `kicad-cli pcb render` with a transparent background, at the
  same size and framing as the current files. The bottom render now shows the revision text.
- **PDFs:** `docs/silkscreen_pcb_schematic.pdf` (`kicad-cli sch export pdf`) and `docs/silkscreen_pcb_layout.pdf` (match
  the current file's layers and page setup).
- **Check** that every image reference in the docs still resolves and still shows what the text says.

### 3.6 Other living docs

- **`docs/NEXT_REVISION.md`:** add a status line at the top. N1–N9 are in the Rev 1.03 design (REV_1_03_STATUS.md), and
  this note supersedes §5 where they differ.
- **`docs/BOARD_FAILURES.md`**, as NEXT_REVISION §5 asks:
  - Mark case 1's "design gap" as addressed once 1.03 boards are built and tested, not before.
  - Case 2's "lift `L1`/`C10`" steps can point to the PTC millivolt method for 1.03 boards.
- **`docs/REV_1_03_STATUS.md`:** tick the docs item in §9 and §11 when done.

## 4. Production files (a separate job that README depends on)

`production/` is still Rev 1.02. Regenerating it needs the Fabrication Toolkit, a KiCad plugin: the owner's KiCad, or a
headless run of the plugin.

1. **JLC set (Fabrication Toolkit):**
   - the Gerber zip, renamed `Silkscreen_Reader_PCB_1.03.zip`;
   - `bom.csv`, `positions.csv`, `designators.csv` and `netlist.ipc`.
2. **`production/jlc_bom.csv`, edited by hand:**
   - add the new PTC line;
   - take `R42` out;
   - move `R6` into the 10k line;
   - add the `R85`/`R86` line;
   - move `C34` into the 0.1u line;
   - take `R1` out of the 1M line;
   - remove the `C1` line.
3. **Other fabs:** run `python fabrication/make_fab_files.py`, which writes `production/other_fabs/`.
4. **Placement:** check `F3`–`F6`, `R85`/`R86` and `U10` in JLC's placement preview, including the new footprint's rotation.
5. **Then** update README's file names and its "Rev 1.02" notes.

## 5. Checks before finishing

- **Facts:**
  - counts from the schematic (section 3.2's numbers were read on 2026-11-03);
  - values and LCSC codes from `part_fields.csv`;
  - nets from `kicad-cli sch export netlist`.
- **Board state at hand-off,** for any doc that quotes it:
  - DRC: 0 errors. Warnings: 31 `silk_edge_clearance`, 10 `silk_over_copper`, 3 `silk_overlap` and 6 `starved_thermal`,
    plus 4 excluded `track_dangling` (the button stubs).
  - 0 unconnected; schematic parity clean.
  - ERC: 46 warnings.
  - 862 teardrops.
- **Stale strings:** search the living docs for `1.02`, `166`, `185`, `R42`, `` `R1` ``, `` `C1` ``, `4.7k`, `C327066`,
  `TP7` and `C23162`.
- **Links and anchors:** every relative link and `#anchor` in `README.md`, `docs/*.md`, `docs/audit-*/*.md` and
  `fabrication/*.md` must resolve. This is the check used so far (GitHub-style anchors):

```python
import os, re, glob
root = "."   # repo root
def anchors(path):
    out, seen = set(), {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^(#{1,6})\s+(.*)$", line.rstrip("\r\n"))
        if not m:
            continue
        t = re.sub(r"[^\w\- ]", "", m.group(2).strip().lower().replace("`", "")).replace(" ", "-")
        n = seen.get(t, 0); seen[t] = n + 1
        out.add(t if n == 0 else f"{t}-{n}")
    return out
files = glob.glob("docs/*.md") + glob.glob("docs/audit-*/*.md") + glob.glob("fabrication/*.md") + ["README.md"]
bad = 0
for md in files:
    for m in re.finditer(r"\]\(<?([^)\s#>]*)>?(#([^)\s]+))?\)", open(md, encoding="utf-8").read()):
        f, frag = m.group(1), m.group(3)
        if f.startswith(("http", "mailto")):
            continue
        tgt = os.path.normpath(os.path.join(os.path.dirname(md), f)) if f else md
        if not os.path.exists(tgt):
            bad += 1; print("missing:", md, f)
        elif frag and tgt.endswith(".md") and frag not in anchors(tgt):
            bad += 1; print("anchor:", md, f, frag)
print("problems:", bad)
```
