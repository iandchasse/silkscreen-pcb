# README changes — response to the 2026-09-19 final review

Scope: `README.md` (rewritten) and `fabrication/README.md` (four consistency edits).
Nothing else was touched. No git operations were run.

The README was restructured around the author's refutations in `author_refutes.json`. The old
document opened with an engineering review pointer and buried the ordering path; the new one leads
with what the device is, a picture, what else you have to buy, and the ordering path, and moves
every engineer-only pointer into a final section.

## New structure

```
Silkscreen  (what it is, one paragraph, board photos, "you do not need KiCad")
What it is                                (plain-language bullets)
What you need besides the board           (panel · battery · microSD · USB-C cable + WARNING callout)
Order an assembled board, step by step    (JLCPCB only, 8 steps, cost/lead-time box first)
Choosing a configuration                  (optional-parts table, preserved)
  Getting into download mode
  Cutting the board down for a smaller display
Firmware
The board and your case
Specifications                            (the old "At a glance" table)
Words used on the factory's website       (glossary)
Licence
For engineers / before you modify this design
  Read the review first · Plots and renders · Repository layout · BOM sources · Regenerating the release files
```

## Finding-by-finding

| ID | What was done |
|---|---|
| **DOCS-06** | Restructured as above. `DESIGN_REVIEW.md`, `docs/audit-2026-09-18/` and `docs/HARDWARE.md` pointers now live under *For engineers / before you modify this design*, with a one-line note that nothing there is needed to order a board. The old "Before assembly: read DESIGN_REVIEW.md" opener is gone. |
| **DOCS-11** | Removed the bare terms **"Fix 4"**, **"the Q4 replacement"** and **"the slotted microSD land"** from user-facing text. Added a glossary section (*Words used on the factory's website*) defining Gerber, BOM, CPL/centroid/pick-and-place, PCBA, DNP, SMD/SMT, THT, LCSC code, Basic/Extended part, DFM. Each term is also defined inline the first time it appears in the ordering steps. |
| **DOCS-03 / FAB-10** | The only BOM named anywhere is `production/bom_JLC_upload_v4_optimized.csv`, uploaded with `production/positions.csv` and `production/Silkscreen_Reader_PCB_1.0.zip`. `bom.csv` and `bom_JLC_upload_v3.csv` are no longer presented as options; the old "Pick one BOM, not all three" file table was deleted. No files were deleted from disk. |
| **DOCS-13** | README is now a JLCPCB-only ordering guide. The whole "Ordering from PCBWay or NextPCB" section, the `other_fabs/` file table, the `make_fab_files.py` invocation and the `assembly_drawing_bottom.pdf` reference were removed from `README.md`. `production/other_fabs/` and `fabrication/NEXTPCB_REV0_NOTES.md` were not touched. |
| **DOCS-01 / DOCS-12** | New *Firmware* section: no released firmware for this board yet; planned work is porting the FreeInk SDK and maintaining crosspoint-reader, crossink reader and the other XTEink X4 firmwares; all future work. First-power-up instructions will follow once firmware exists. A one-line pointer to this section sits at the end of *What it is*, so a reader meets it before the ordering path. |
| **DOCS-02** | The silkscreenreader.com *Build one* configurator is presented as "built but behind a site preview, not live yet — if it is not live when you read this, use the steps below". The manual JLCPCB steps are the complete first-class path. The `$29.55` core-configuration price quoted from the site's model and the "Prices in the site's model exclude…" note were removed. |
| **DOCS-04** | New *What you need besides the board* table: display panel variants (as already described), single-cell LiPo with JST-PH 2.0 mm 2-pin plug, microSD card, data-capable USB-C cable. Lead order is stated explicitly: **`J5` pin 1, marked "-", is battery negative; pin 2 is positive; there is no standard, packs ship both ways, check with a meter.** The visible placeholder `TODO(author): link to a known-good pack` is left in the battery row. One line says screws and case belong to individual case designs. |
| **DOCS-05** | One compact `> [!WARNING]` callout (4 lines) directly under the battery lead-order note: reversed/shorted/crushed cells are a fire risk, measure against the "-" mark, use a protected pack, stop using a puffed cell. No further lecturing. |
| **DOCS-07** | "Case agnostic" is gone. *The board and your case* now says the board is meant to work with many case designs of any style, that no reference enclosure is supplied here, gives the STEP path `docs/mechanical/silkscreen_pcb.step`, and lists 60.05 × 111.30 × 1.6 mm, five M2 holes (`H1`–`H5`) and all-parts-on-the-bottom, pointing at `docs/HARDWARE.md`. |
| **DOCS-08** | No URL was invented or changed. Existing links left as they are. Listed for the author. |
| **DOCS-09** | Step 3 now explains it in plain terms: JLCPCB runs two assembly services; **Standard** is needed because the ESP32-S3 module is only placeable under Standard; a builder happy to hand-solder the module could leave it off and use the cheaper Economic service. One sentence on rails: the board is 60 mm wide against Standard's 70 mm conveyor minimum, so JLCPCB may add snap-off edge rails for a small fee — nothing to design, just snap them off. No fiducial talk anywhere. |
| **DOCS-10** | New *What it costs and how long it takes* box, marked a September 2026 snapshot: about **$230–260** for five boards all assembled including parts and shipping, roughly **$47–53 per board**; about **$75** of that is one-off setup/stencil/part-type fees; **2–3 weeks**; panel, battery, microSD and case not included. Numbers from `sections/12_bom_function_and_cost.md` (the bottom-up 5-board model, ≈$233 → $47/board, cross-checked against `fabrication/BOM.md`'s $48–53 from a real 30-board quote). |
| **DOCS-14** | Step 7 is now a costed choice: (a) let JLCPCB solder the 13 THT parts — about $3.60 per-order hand-soldering fee plus ~$0.016 per joint, roughly **$11 of the ~$230 five-board total**, plus about a day; or (b) take them loose and put in about 92 joints per board yourself — USB-C shell pins, JST, 12-pin header, ten switches — with the USB-C shell called out as the fiddly one. |
| **DOCS-15** | Licence section now opens with three plain statements read from `LICENSE`/`NOTICE`: you may build, use, modify and sell it without asking; if you distribute or sell a board based on this design you must publish your design source under CERN-OHL-S v2 and pass on the copyright and licence notice; there is no warranty. Flagged as a plain-language summary, not legal advice, with the licence text governing. The CERN boilerplate block and SPDX id are kept verbatim. |
| **DOCS-16** | The cost box and step 2 now say the bare-board minimum is **5** but assembly can be ordered for as few as **2** — one working reader, one spare, three bare boards left over. The old bare "Minimum quantity is 5" line is gone. |
| **DOCS-17** | "**you do not need KiCad to order a board**" is in the third paragraph of the README, and repeated at the top of the ordering section. Both `kicad-cli` blocks moved to *For engineers → Regenerating the release files*, where they are also labelled a cross-check rather than a replacement for the Toolkit set. |
| **DOCS-18 / LAY-01** | The perforation-slot caution is kept (the current release files still contain the slots) but cut to two sentences, and now ends "**They are to be replaced by a single wider slot in the next revision of the board.**" Same sentence added to `fabrication/README.md`'s assembly checklist, replacing "check how those boards turned out". |
| **DOCS-24** | **Corrected.** The README said "LED pad 1 is the anode" twice. Ground truth: `evidence/sch/connectivity_by_component.txt` has `D2 pin 1 = K`, and `fabrication/BOM.md:196`/`:296` say "pad 1 = cathode"; `fabrication/part_fields.csv:15` confirms `D2` is the `LTST-C150KRKT` / `YONGYUTAI YLED1206R` red 1206. The surviving occurrence (step 6 placement preview) now reads "**Pad 1 is the cathode** (the marked end)". The second occurrence was in the other-fabs section, which is gone. `fabrication/README.md`'s hedged "D2 LED pad-1/anode convention" was corrected to "D2 LED polarity (**pad 1 is the cathode**)". |
| **MCU-01** | New *Getting into download mode* subsection: normally never needed because the ESP32-S3 has native USB; if it is, bridge the two `SW6` (BOOT) pads with metal tweezers while tapping RESET. `SW6` is DNP to save cost. |
| **MEC-09** | One line in the same subsection: `SW11` (RESET) is set back from the edge on purpose, to be pressed through a pin-hole in the case. |
| **LAY-02 / MEC-02 / MEC-V02 / HMI-V02** | New *Cutting the board down for a smaller display* subsection, placed under *Choosing a configuration*: disconnect the battery first (battery positive crosses the cut line); it will not snap by hand, use a rotary tool along the marked line; the cut removes `J6` **and** the power button `SW10`, after which UP(2) serves as the power button with `R36`/`R73` unpopulated and `R72`/`R74` populated, as printed on the schematic and the board; plan the cut before ordering so the removed parts can be left off the BOM. |

## Facts kept unchanged (verified correct by section 13)

- `179 references = 162 fitted + 10 DNP + 7 bare-copper (H1–H5, TP1, TP2)` — kept verbatim.
- `positions.csv` is 162 rows, all bottom side; "Assembly side: Bottom" is the correct instruction.
- The whole optional-parts / configuration table, including the DNP notes and the touch pin-order
  warning, is preserved word for word except for the removed configurator price.
- Every pre-existing link target still resolves. A link and anchor checker
  (`<scratch>/agents/followup_readme/linkcheck.py`) was run over `README.md` and
  `fabrication/README.md` after the edits: **0 broken file links, 0 broken anchors.**

## Other small corrections made in passing

- Panel part number normalised to `GDEQ0426T82` (the README previously used `GDEQ426T82` in the
  spec table and `GDEQ0426T82` further down; Good Display's own part number has the leading zero).
- The undated stock figure "about 189 pcs at last check" for `TPS923610DRLR` was replaced with
  "check its stock" — it would be wrong by the time anyone read it.
- Board dimensions given as 60.05 × 111.30 × 1.6 mm where mechanical precision matters, and
  "about 60 × 111 mm" where the reader is comparing against JLCPCB's Gerber viewer.
- Repository-layout block updated: `docs/mechanical/` added, `production/other_fabs/` row removed,
  `production/` described as "release upload files".

## `fabrication/README.md` edits (4)

1. "the Fix 4 reverse-battery circuit" → "the USB-present reverse-battery gate" (twice); DOCS-11.
2. Root-README anchor `#ordering-from-jlcpcb-step-by-step` → `#order-an-assembled-board-step-by-step`,
   and the dead `#ordering-from-pcbway-or-nextpcb-alternative-to-jlcpcb` pointer replaced with a
   line saying JLCPCB is the only supported route, keeping the `NEXTPCB_REV0_NOTES.md` link.
3. Release-record table: "Upload BOMs … v4 (standard) and v3 (brand-conservative)" →
   "Upload BOM … `bom_JLC_upload_v4_optimized.csv`, **the single BOM to upload**", noting v3 is
   superseded; DOCS-03 / FAB-10.
4. Assembly checklist: D2 polarity corrected (DOCS-24) and the perforation-slot line given the
   next-revision outcome (DOCS-18).

## Left for the author

- **DOCS-08** — the public URL on the board, in `NOTICE` and in both KiCad title blocks points at a
  repository whose default branch holds the old project. No URL was invented or changed here.
- **DOCS-13** — actually deleting `production/other_fabs/`. The README no longer references it, so
  the folder can go whenever you like. `fabrication/NEXTPCB_REV0_NOTES.md` was left in place and is
  still linked from `fabrication/README.md`.
- ~~**DOCS-07** — exporting `docs/mechanical/silkscreen_pcb.step`.~~ The file appeared during this
  pass (7.6 MB, exported 2026-09-20 21:04), so the README now links to it directly and the link
  check passes. Nothing left to do unless the export needs re-doing after a board change.
- **DOCS-04** — replacing the visible `TODO(author): link to a known-good pack` placeholder in the
  battery row.
- **DOCS-02** — taking the silkscreenreader.com configurator out of site preview, after which the
  "not live yet" wording in the ordering section should be softened.
- **DOCS-01 / DOCS-12** — the firmware itself, and the first-power-up / troubleshooting section that
  depends on it.
- **DOCS-18 / LAY-01** — the actual board change (four 0.5 mm slots → one wider slot) in KiCad, and
  regenerating `production/` afterwards.
- The **$230–260 / 2–3 weeks** figures are a September 2026 snapshot from the review's cost model,
  not a quote you have placed. Worth confirming against your own next order and re-dating the line.
