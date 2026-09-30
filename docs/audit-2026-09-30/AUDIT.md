# Silkscreen Reader PCB — audit of Rev 1.0 (as ordered) and 1.01

Audit date 2026-09-30 · Rev 1.0 = `aeb5b39` (ordered 2026-09-21; design and production files identical through `6871962`)
· 1.01 = `3edd0c8` · KiCad 9.0.6.

A quick full audit, deliberately **not** blind: it builds on the
[2026-09-19 final review](../final-review-2026-09-19/FINAL_REVIEW.md) and its follow-up rounds 3–7 in
[`AUTHOR_TODO.md`](../final-review-2026-09-19/AUTHOR_TODO.md), and checks that their conclusions still hold for the files
that were ordered and for the 1.01 change. It covers the schematic, layout and manufacturability, the fab package and
BOM/CPL, the docs and the website, the 1.01 change itself, and boards that are cut down for a smaller display.

| Where to look | What it is |
|---|---|
| this file | verdict, cut-down boards, what is left before 1.01 is ordered |
| [`BRING_UP.md`](BRING_UP.md) | bench checks for the first boards (meter, supply, scope) |
| [`reports/`](reports/) | ten reports, listed at the end |
| `silkscreen-firmware/NOTICE.md` (sibling folder, not in this repo) | the checks firmware can do itself, and the firmware-side findings |
| `evidence/` | scripts, DRC JSON and netlists the reports cite — about 31 MB, kept locally and git-ignored |

---

## 1. Verdict

**Rev 1.0: fine. No blocker, and nothing in the files that were ordered will produce a wrong or dead full-size board.**

- **The files you ordered are the design.** The zip in the repo at the order is byte-identical to the last Fabrication
  Toolkit run before the order (`production/backups/…_2026-09-21_02-22-58`), and a fresh kicad-cli plot of `aeb5b39`
  reproduces all nine Gerbers and both drill files apart from comment lines. `jlc_bom.csv` and `positions.csv` match the
  board and schematic for all 165 placed parts: values, LCSC codes, DNP, positions, rotation rules
  ([09](reports/09_fab_bom_cpl.md)).
- **Electrical.** ERC: 0 errors (the same 41 known warnings). Every critical path checks out against the netlist: USB-C
  sink and flashing path, TPS2116 mux, TP4056 (R6 = 4.7 k, ≈ 0.25 A) with the reverse/absent-pack CE gate, DW01A/FS8205A,
  LDO, EN and strapping pins, the 24-pin panel connector and boost, microSD, both button ladders, the front-light boost
  (13.3 mA) and both RTC options. The `aeb5b39` revision changes (R83/C7/C34, F2, U14, the USB_STAT ×10 ladder) are right,
  and the doc claims added since (ladder wake thresholds, the R72/R36 hazard, open-load boost, sleep budget) match the
  schematic values ([07](reports/07_electrical.md)).
- **Layout.** DRC with parity: 0 unconnected, 0 parity. The only live errors are the known J1 USB-C land-pattern
  clearances (0.150 mm, above JLC's 0.127 mm minimum). All seven `.kicad_pro` exclusions are still justified. Every measured
  minimum is within JLC's standard 2-layer limits except the two items accepted in the final review (J1 annular ring
  FAB-01, small silkscreen FAB-02). No copper under the antenna; power-path widths fine; 0 courtyard overlaps
  ([08](reports/08_layout_manufacturability.md)).
- **What is left is risk, not file errors:** (a) the Toolkit does not correct rotation for U2, U10, D2–D6 and D8, and J4's
  placement point sits 0.73 mm from its pad centre, so those parts depend on JLC's placement preview having been checked;
  (b) the bring-up measurements in [`BRING_UP.md`](BRING_UP.md) have never been done.

**1.01 (`3edd0c8`): better than 1.0.** Same schematic, and every footprint is identical (reference, value, position,
rotation, fields), so the unchanged BOM, CPL and other-fab files stay valid. The only change is copper: the 3V3 link below
the cut line, PWR_BUTTON and LED_SW moved around it, one GND via moved, and one silkscreen word. No new DRC error; one new
cosmetic warning ([02](reports/02_full_drc_1.0_vs_1.01.md), [03](reports/03_fab_outputs_1.01.md)).

---

## 2. Boards cut down for a smaller display

Cutting at the x3 line (KiCad y 62.00) or at the documented cut line (y 61.86) removes the tongue. Two things run through
the tongue that the rest of the board needs:

| | 1.0 (`aeb5b39`, the 2026-09-21 order) | 1.01 (`3edd0c8`) | 1.01 + GND vias (§3) |
|---|---|---|---|
| 3V3 to the charge-enable switch Q2/R81 | cut off: the board never charges | **fixed** | fixed |
| GND between the power section and the rest | joined only through one J7 shell tab | same | **joined** |

**The ground split** ([05](reports/05_cut_board_gnd_geometry.md), [06](reports/06_cut_board_gnd_bridges.md)). On a cut
board the ground of U3 (LDO), U2 (power mux), Q1 (FS8205A, so the whole battery return), C3, C4, C6, C25, C26, R16, R51,
R77 and H5 is no longer joined by copper to the ground of the ESP32, USB-C, charger, display and everything else. On the
full board the two grounds meet only in the F.Cu pour of the tongue, through a 1.3 mm neck between the `P+` track at
x 87.40 and the slot. After the cut, the only link is the metal shell of the microSD socket J7, through **one** rear tab
(either socket option has three tabs on the main ground and one on the power ground).

- **Was it an issue on the 1.0 boards?** Only if a board is cut. The pre-change board gives exactly the same split, so the
  1.01 edits did not cause it. On a full-size board the tongue joins the grounds; the neck is narrow, but its resistance
  is a few milliohms, so it drops a few millivolts at most at these currents.
- **On a cut board** it works while J7 is fitted and that one tab is soldered, but that tab carries all battery discharge
  current (≈ 0.3–0.6 A peaks) and the whole charge current (≈ 0.25 A). Without J7, or with that joint open, the battery
  return is open and the LDO and mux lose their ground: a dead board.
- **KiCad agrees.** On a trimmed copy of 1.01 the unconnected count is 1; one GND via at any of the suggested spots clears
  it, and a control via inside the main ground does not (`evidence/gnd_via_test.py`):

| trimmed copy | no via | one GND via at (86.48, 68.75), (75.03, 74.64) or (80.56, 92.22) | control via at (60, 120) |
|---|---|---|---|
| 1.01 | 1 unconnected | **0** | 1 |
| 1.0 | 2 (3V3 island + GND) | 1 (the 3V3 island) | 2 |

**Boards already built from files before `3edd0c8`** (including the 2026-09-21 order), if you cut one — after
disconnecting the battery, as the final review's cut-line item says:

- 3V3: bridge the two cut 3V3 stubs at the edge (x 87.53 and 100.60, y 62), or wire `R40` pad 2 to `R81` pad 2. With a
  correctly oriented cell fitted, the TP4056 `CE` pin (U11 pin 8) should then read 3.3 V.
- GND: keep J7 fitted with all its shell tabs soldered, and preferably add a short wire from `C6` pad 2 (75.10, 85.84) to
  `C21` pad 2 (74.80, 80.34), both on the back, 5.5 mm apart.

---

## 3. Before you order 1.01 (KiCad)

| # | What | Why | Effort |
|---|---|---|---|
| 1 | **Two GND stitching vias (0.6/0.3 mm) at (86.48, 68.75) and (75.03, 74.64)**, optionally a third at (80.56, 92.22). Refill, DRC, then DRC a copy trimmed at y 62: expect no GND unconnected. | Makes a cut board's battery return independent of the SD socket. Each spot is inside both pours, outside every courtyard, ≥ 0.5 mm from other-net copper. Harmless on the full board. | 10 min |
| 2 | **Delete the 1 µm 3V3 segment (101.000 → 101.001, 64.9) and end the new route on a segment endpoint** (e.g. split the x 101.101 vertical at y 65.0). | The only new DRC item in 1.01 (`track_dangling`). Copper is continuous; cosmetic. | 2 min |
| 3 | **Mark the revision when you order:** title blocks rev 1.01 and date (the Toolkit's zip name follows the title block, `…_1.0.zip` today, so update the zip name in the README and `GERBER` in the site's `scripts/pricing/order_files.py`), plus a small rev text on the silkscreen. | A 1.0 and a 1.01 board otherwise differ by one silkscreen word, and the cut-down bodge depends on knowing which one you hold. | 10 min |
| 4 | Optional hygiene: redraw the two internal cut-outs at 0.05 mm (the 0.2 mm stroke leaves the cut-line slot 0.9 mm wide at its inner edge; 1.0 passed DFM); set U4's keep-out to disallow copper pour; put J4's 0.73 mm offset and any rotation fixes JLC made into `FT Position Offset` / `FT Rotation Offset` fields; exclude TP1/TP2 and R72/R74/SW6 from the BOM; clear the `PIN_3`/`TP_RST` double label; a `.kicad_dru` rule so the J1 items stop cluttering DRC: `(rule J1_landpattern (condition "A.memberOfFootprint('J1') && B.memberOfFootprint('J1')") (constraint clearance (min 0.15mm)))`. | Cleaner DRC and CPL; nothing here changes how the board works. | 30 min |
| 5 | **Decide after 1.0 bring-up:** feed Q2 pin 2 and R81 pin 2 from `USB_VBUS` instead of 3V3. | CE could then only be high while the charger is powered (removes the TP4056 back-feed path on battery), saves ≈ 6.6 µA of the 58 µA sleep floor, and a cut board no longer needs a 3V3 feed to Q2/R81. Worth doing if the back-feed check in `BRING_UP.md` shows anything. | 20 min |
| 6 | Then regenerate the Toolkit outputs, re-plot `docs/silkscreen_pcb_layout.pdf` and re-render the board images. | The layout PDF and the README/site renders predate 1.01. | — |

---

## 4. Docs and website

- **Repo docs** agree with the design on every hard fact checked (GPIO map, part numbers and values, J5/J6 pinouts,
  tongue parts, sleep-budget arithmetic, links). What is wrong is dating and records after 1.01, two false sentences, and
  the cut-down section. The ready-to-apply edit list is in [10](reports/10_docs_and_website.md) (E1–E14), plus from
  [09](reports/09_fab_bom_cpl.md): add U10 and D3–D6 to the placement-preview list (README Step 6,
  `fabrication/README.md`), add a Rev 1.0 order row to the release record, and `BOM.md` L1 "47uH"; and from
  [07](reports/07_electrical.md): a first-article line for the TP4056 back-feed check in `HARDWARE.md`. The cut-down text
  should say both the 3V3 and the GND points of §2, and its wording depends on whether §3 item 1 goes in, so do it after
  the board is final.
- **Website** matches the repo in copy, parts, configuration groups and costs (the stale RTC cost from the handoff is
  fixed), and its schematic PDF and block images are current. Stale against 1.01 only: the order zip, the "PCB plot" PDF,
  the board renders (probably the bare-board GLB too) and the "These are the Rev 1.0 files" wording. Refresh them once,
  after the board is final.
- **Light-strip repo:** `docs/DESIGN.md` (:34, :331) and `enclosures/case-368/README.md` (≈ :826–838, :985) still call the
  charge-enable problem unfixed and point to the deleted `NOTICE.md`; they should also get the GND note.

---

## 5. Prior-review items still open

HMI-V01 (R72/R74/SW6 not excluded from BOM; harmless today), FAB-13 (`PIN_3`/`TP_RST` double label), MCU-08 (optional
PWM_LED pull-down), BOM-06 (D8 NRND, kept), BOM-07 (DS3231MZ fitted, RV-8263-C7 alternate DNP), PWR-06 / PWR-V02 / PWR-18
and LED-12 (bring-up measurements), and the sleep budget (unmeasured). Accepted as before: FAB-01, FAB-02, the J1 land
pattern. Full status list in [07 §6](reports/07_electrical.md).

---

## 6. Method, evidence and limits

- Four read-only auditors (electrical, layout/manufacturability, fab/BOM/CPL, docs/website) plus, for the 1.01 change,
  a trimmed-board DRC, a full DRC against the pre-change board, a fab-output check and a docs sweep, and two independent
  verifiers for the cut-board GND split. Everything ran on scratch copies of `aeb5b39`, `6871962` and `3edd0c8` with
  kicad-cli 9.0.6 and KiCad's `pcbnew` Python; nothing in the repo was modified.
- Cut boards were simulated by clipping the saved zone fills at the cut line (what a sawn board keeps), not by refilling,
  and the saved fills were matched against the fab Gerbers, so the copper analysed is the copper that was made.
- [07](reports/07_electrical.md) first read the cut-board GND item as a DRC artefact; that was wrong, and an erratum at the
  top of the report says why.
- Limits: nothing was measured on hardware and nothing was simulated (no SPICE). JLC's placement preview for the 1.0 order
  was not available. The QR codes were not decoded this time (no decoder installed); their footprints are byte-identical
  to the ones decoded on 2026-09-21, and six tented vias inside them cost at most ≈ 1.9 modules per code, well inside
  error-correction level L — scan one with a phone on the first board. External links, stock and prices were not
  re-checked.

### Reports

| # | Report | What it covers |
|---|---|---|
| 01 | [Cut-line DRC, 3V3 fix](reports/01_cut_line_drc_3v3_fix.md) | trimmed-board DRC before and after the 1.01 change; first sight of the GND split |
| 02 | [Full DRC, 1.0 vs 1.01](reports/02_full_drc_1.0_vs_1.01.md) | all-severity DRC with parity, zone-fill freshness, clearances of the new trace |
| 03 | [Fab outputs, 1.01](reports/03_fab_outputs_1.01.md) | the 1.01 zip and netlist against a fresh plot; which layers changed; text-box fit |
| 04 | [Docs sweep, 1.01](reports/04_docs_sweep_1.01.md) | what the 1.01 change made stale, in this repo and the sibling repos |
| 05 | [Cut-board GND, geometry](reports/05_cut_board_gnd_geometry.md) | copper-geometry islands; J7 tab table; via spots |
| 06 | [Cut-board GND, bridges](reports/06_cut_board_gnd_bridges.md) | where the grounds join on the full board; trim-artefact audit; severity |
| 07 | [Electrical](reports/07_electrical.md) | ERC, netlist walk, doc-claim checks, prior-review status (with erratum) |
| 08 | [Layout and manufacturability](reports/08_layout_manufacturability.md) | DRC classes, exclusions, measured minima, antenna, QR vias |
| 09 | [Fab package and BOM/CPL](reports/09_fab_bom_cpl.md) | 1.0 zip provenance, BOM/CPL against the board, other-fab files, ordering guide |
| 10 | [Docs and website](reports/10_docs_and_website.md) | repo docs and site against the design; the edit list |
