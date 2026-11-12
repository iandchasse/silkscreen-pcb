# Rev 1.03: hand-off for the user docs and images

**For:** whoever updates the user-facing documentation and images for Rev 1.03, an agent or a person.
**Written:** 2026-11-03, with the commit that brought the `1.03` design files up to date. **Branch:** `1.03`.
**Updated:** 2026-11-04 for the BQ21040 charger (section 3.8).

**Status 2026-11-05: done.** The docs, images, PDFs and production files are Rev 1.03
([REV_1_03_STATUS.md §16](REV_1_03_STATUS.md#16-default-rtc-production-files-docs-and-renders-2026-11-05)). The default RTC
is now `U14` (RV-8263-C7) and the DS3231MZ `U13` is the DNP alternate, so wherever this note says `U14` is DNP, read `U13`;
the DNP count is still 11. This note stays as the record of the task list.

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
| N9 | `R6`: 4.7k → 10k. The charge current drops from about 0.23–0.26 A to about 0.11–0.13 A, and `U11`'s heat halves. **Superseded on 2026-11-04:** with the BQ21040, `R6` is 4.7k again for the same 105–125 mA (see "Charger" below) | [NEXT_REVISION N9](NEXT_REVISION.md#n9-r6-from-47k-to-10k) |
| N10 | Closed: `C36`/`C37` stay where they are | [REV_1_03_STATUS §7](REV_1_03_STATUS.md#7-n10-closed-left-as-is) |
| N11 | Dropped: there are no front test pads (no TP6–TP18) | — |
| `U10` footprint | TI's DRL0006A example land, `U_DRL0006A_6L_TI-LAND`, in `KiCad/9.0/3rdparty/TPS923610DRLR/KiCADv6/footprints.pretty/` | [TRACE_AUDIT §1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern) |
| USB-C shell | Tied straight to GND: `J1`'s four shell tabs sit in both GND pours. `R1` and `C1`, formerly 1 MΩ ∥ 1 nF, are gone | [CERT_REVIEW_AUDIT §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03) |
| Charger (2026-11-04) | `U11` is TI's BQ21040 (SOT-23-6) in place of the TP4056, with a 10 kΩ NTC (`TH1`, 0603, on the board at (100.6, 93.0)) on `TS`: charging only between about 0 and 41 °C at `TH1`, 30 min pre-charge and 10 h fast-charge timers, 6.6 V input OVP. `Q2` (now a BSS138) gates `TS` instead of `CE`; `R6` 4.7k, `R82` 200k, `R71` removed. `USB_STAT` loses its 0.55 V "complete" level | [REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04), section 3.8 |
| Revision | Title blocks read Rev 1.03 / 2026-11-03. The back silkscreen prints "Rev 1.03 2026-11-03" at (87.1, 138.8), from the title block | as above |
| Layout | Trace-audit fixes, `F3`'s pour keep-out, mounting-hole and edge clearances, stitching and return vias, the `C33`/`R7` swap at `U4`, teardrops (862), and reference designators (uniform 0.5 mm, 67 moved, `F5`/`F6` shown) | [TRACE_AUDIT §1–1f](audit-2026-11-03/TRACE_AUDIT.md), CERT_REVIEW_AUDIT §6 |
| DRC rules | New `silkscreen_pcb.kicad_dru`: pour pull-back from the switch nodes and high-voltage nets, plus footprint-scoped rules. `J1`'s peg holes and `J3`'s pitch now pass under these rules instead of project-file exclusions | TRACE_AUDIT §1, §1b, §1c |

**Already done in the docs (check, don't redo):**
- README "Step 2: order the bare board": surface finish.
- HARDWARE.md §3.1 shield handling and §16 antenna paragraph.
- BOARD_FAILURES.md's meter-check row 4.
- HARDWARE.md's header note has a temporary bridge sentence (section 3.1).

The design files also fixed two notes after the independent review:
- the back-silk touch-option note now says "unpopulate F4,R44,46,52";
- the schematic's `R6` note now gives the 10k charge current.

## 3. Tasks by file

### 3.1 `docs/HARDWARE.md`

- **Header note** (around line 31):
  - Make it describe Rev 1.03.
  - Fold the 1.0/1.01/1.02 differences into a short revision history, and add 1.02 → 1.03 from section 2.
    [CHANGELOG.md](CHANGELOG.md) has the full list from the Rev 1.0 order.
  - Drop the "catches up in the 1.03 documentation pass" bridge sentence.
- **§3.2:** rewritten for the BQ21040 (section 3.8). N9's 10k no longer applies: `R6` is 4.7k again.
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
- **Search the whole file** for changed parts and values: `R42`, `R1`, `C1`, `TP4056`, 2.2 nF next to `C34`, `166`, `185`,
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
  - `R6` stays on its 4.7k line (`C23162`), as in Rev 1.02: the charger swap undid N9's move to 10k.
  - `R42` leaves the 0 Ω line, `R1` leaves the 1M line, and the 1n `C1` line goes.
  - The charger's lines: section 3.8.
- **Extended parts and fees:** re-derive them. NEXT_REVISION §2 says "two new Extended parts" (+$6 per order), but N7
  ended up with a Basic part, so the PTC is probably the only new Extended type from N1–N9. The charger swap adds two
  more (`U11` and `TH1`) and drops the TP4056, a JLC Preferred part. Check `part_fields.csv` against JLC.
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

### 3.7 From the independent review

These documentation items come from [TRIAGE.md](independent-review-2026-11-03/TRIAGE.md):

- **M-4, README and HARDWARE.md §3.1:** "5 V USB-C chargers only". There is no input over-voltage protection, so a fixed
  9/12 V supply kills the board.
- **M-6, HARDWARE.md §8:** the alternate touch mapping removes `F4`, `R44`, `R46` and `R52`, and fits `R43`, `R45`, `R58`
  and `R66`. Fit a PTC (MF-FSMF010X-2) on `R66`'s pads, not a 0 Ω link.
- **L-6, HARDWARE.md §4 / README:** fit `SW6` (APEM MJTP1243) if you flash firmware that can turn off USB-Serial-JTAG.
- **L-7, HARDWARE.md §11 and the `J6` pinout table:**
  - accessories must not drive IO45 or IO46 during reset;
  - pin 12 (P+, fused by `F2`) sits next to pin 11 (C−).
- **L-13, HARDWARE.md §16:** washers or standoffs at the mounting holes at most Ø4.4 mm, or nylon.
- **L-17, BOM.md and README:** list every DNP pair that must not be fitted together: `R73`/`R74`, `R66`/`R44`,
  `R45`/`R46` and `R52`/`R58`.
- **I-3, README:** an operating range of 0–50 °C, set by the panel.
- **H-2, README cutting section:** pour-free areas now keep ground about 1 mm from P+ and 3V3 at the cut, both layers.
  Keep the deburr, check and seal steps.
- **L-8, HARDWARE.md §3.3** ("Reverse-polarity intent: `Q3` + `Q8`"): say what each part is for and what it does as
  built ([TRIAGE §5.1](independent-review-2026-11-03/TRIAGE.md#51-l-8-what-q3-and-q8-do)). The owner keeps the circuit as
  it is (2026-11-04), so this is description, not a change.
  - `Q8` is the DW01A's load switch from the EEVblog thread, fitted the other way round to that thread's circuit. The
    DW01A's start-up relies on `C34`, which works on the owner's boards.
  - By the same orientation, `Q8` is the part that blocks a reversed cell. `Q3`'s body diode faces into `B+`, so it
    doesn't.
  - User note for HARDWARE.md and the README troubleshooting text: if the board ever shuts off on battery after an
    overload and stays off, plugging in USB resets the battery protection.

### 3.8 From the BQ21040 charger swap (2026-11-04)

`U11` is now TI's BQ21040 with an NTC; [REV_1_03_STATUS §14](REV_1_03_STATUS.md#14-bq21040-charger-2026-11-04) has the
numbers and their sources (TI SLUSCE2D). The schematic's own notes are already updated.

- **HARDWARE.md §3.1:**
  - `C2` is "the charger's input capacitor", no longer the TP4056's.
  - The hot-plug paragraph's "the TP4056's `VCC` at 7.97 V against its 8 V limit" no longer applies: the BQ21040 is rated
    30 V and stops charging above 6.6 V. `U2`'s 6.0 V limit is still the reason for `R84`.
  - M-4 (section 3.7): the charger now survives a 9–12 V source, but `U2` and what it feeds do not, so "5 V USB-C
    chargers only" stays.
- **HARDWARE.md §3.2,** rewrite for the BQ21040:
  - pins: `TS` (1), `OUT` (2) to `P+`, `CHG` (3) to `CHRG` and `R67`, `ISET` (4) to `R6`, GND (5), `VIN` (6) from
    `USB_VBUS`;
  - `R6` = 4.7k: I = 540 / `R6`, 105–125 mA, about 5 h for 500 mAh; pre-charge at 20 % below 2.5 V; termination at
    10 %;
  - regulation 4.2 V ±1 % (4.16–4.23 V); top-ups start below 4.04–4.16 V;
  - timers: 30 min pre-charge and 10 h fast charge, counting at half speed in thermal regulation or input DPM. Above
    about 1000 mAh a charge may not finish inside 10 h at 115 mA; `R6` = 3.9k (about 140 mA) restores the margin;
  - input: rated 30 V, OVP at 6.6 V, input DPM at 4.24–4.46 V, UVLO 3.15–3.45 V;
  - `TS` with `TH1` and `R82`: the window (about 0–41 °C at `TH1`), the fail-safe for an open NTC, where `TH1` sits
    and why;
  - heat: about 0.28 W worst case, a 37 °C rise;
  - replace the pin table and the "`TEMP` grounded disables cell-temperature monitoring" warning.
- **HARDWARE.md §3.3:** the detector now drives `TS`, not `CE`. `Q2` is a BSS138 N-FET (gate `/DET_NODE`, drain `TS`,
  source GND), and `R82` is 200k on `TS`. Update the mitigation paragraph ("the TP4056 `CE` pin is driven high only
  by…"), its parts list (`Q2` AO3401A → BSS138) and the "Charger enable limitation" note: same mechanism, now through
  `TS`.
- **HARDWARE.md §3.7:**
  - `R71` and `STDBY` are gone, and with them the 0.55 V and 0.51 V rows.
  - New states: 3.30 V with `CHG` off, 2.20 V on battery, 1.11 V charging, 0.95 V charging on a weak source.
  - Explain that `CHG` marks only the first charge after plug-in or cell insertion, and how firmware uses `P+` for the
    3.30 V cases.
  - Replace the no-battery-blink paragraph: a cell pulled with USB in now reads a steady 3.3 V, with `P+` cycling
    3.8–4.2 V.
  - Drop the caution about the two lowest levels being too close to separate.
- **HARDWARE.md §13.1:** the `USB_STAT` bullets, as in NEXT_REVISION F11. Remove the 0.35–0.70 V "complete" window and the
  blink caution; add the `P+` decode.
- **HARDWARE.md §16:**
  - the sleep-budget row for the ladder ("the max assumes the unpowered TP4056 status pins clamp"): TI specifies the
    BQ21040's pins high-impedance when unpowered (§8.3.1);
  - `U11` draws at most 1 µA from the cell when unpowered;
  - recount the parts table (`R71` out, an NTC in).
- **Search HARDWARE.md and README.md** for `TP4056`, `STDBY`, `CE`, `PROG`, `TEMP`, `ESOP`, `R71`, `234 mA`, `0.25 A`,
  `0.23–0.25 A`, and 10k next to `R6`.
- **README:** the charger's name; about 115 mA and 5 h for 500 mAh; charging between about 0 and 41 °C, measured on the
  board.
- **BOM.md and `BOM_handbuild_digikey.csv`:**
  - `U11`: BQ21040DBVR (`C202311`, Extended); drop the "TP4056 Preferred" note;
  - new `TH1`: Murata NCP18XH103F03RB (`C13564`, Extended);
  - `R6` on its 4.7k line (`C23162`);
  - `R82` on the 200k line (`C25811`) that `R71` used;
  - `Q2` on the BSS138 line (`C7420339`);
  - `R71` gone.
  - The population stays 169 + 11 + 8 = 188.
  - Re-derive the cost model. The charging block came to about +$0.20 per board at 500 boards, +$0.30 at 100, +$0.45 at
    30 and +$1.15 at 5, Extended fees included.
- **Images:**
  - `04-charger`: `U11`, `R6`, `TH1` and the notes;
  - `17-usb-status`: no `R71`, the new note;
  - whichever block image shows `Q2`/`R82` (the charge-enable gate);
  - `full-capture.png`;
  - the bottom render.

### 3.9 From the layout pass (2026-11-04, second)

[REV_1_03_STATUS §15](REV_1_03_STATUS.md#15-layout-pass-2026-11-04-after-the-bq21040-commit) has the changes.
HARDWARE.md §9.1.1, the CHANGELOG, NEXT_REVISION's L-16 row and TRIAGE's status table are already updated.

- **HARDWARE.md:** §3.2's `TS` text gets `C38` (0.22 µF, `TS` to GND, the datasheet's optional ESD capacitor) and says
  `TH1` sits beside `R82`, about 7 mm from `U11`, at (91.2, 94.15), not beside the USB-C port at (100.6, 93.0); §16's
  parts table gains `C38`. The charger row of section 2 above still says (100.6, 93.0).
- **BOM.md and `BOM_handbuild_digikey.csv`:** new `C38`: Yageo CC0603KRX7R9BB224 (`C107083`, Extended; DigiKey
  <https://www.digikey.com/en/products/detail/yageo/CC0603KRX7R9BB224/5883804>). The population is now 170 placed + 11 DNP
  + 8 bare-copper = **189**, not 188. Cost model: one more Extended part (the fee applies if `C38` is the order's only
  0.22 µF) and about $0.013 of ceramic. **Since 2026-11-12** JLC fits the Basic Samsung CL10B224KA8NNNC (`C21120`), so
  `C38` adds no Extended fee; hand builds keep the Yageo part
  ([STATUS §20](REV_1_03_STATUS.md#20-review-findings-decisions-and-to-do-2026-11-12)).
- **Production:** the Toolkit's raw `bom.csv` now has two switch lines with the same LCSC (`SW1, SW11, SW2, SW3, SW4, SW5,
  SW8, SW9` on `MJTP1117_FG`; `SW10, SW7` on `MJTP1117`); keep the hand-curated `jlc_bom.csv` on its single `SW_Push` /
  `C557598` line. The CPL changes only for `TH1` (moved) and `C38` (new); the switch rows are identical.
- **Images:** `04-charger` (the `C38` block and the `TH1` note), the bottom render and `full-capture.png` (`TH1` moved,
  `C38` new).
- **Placement preview:** add `C38` to the checks in section 4.

## 4. Production files (a separate job that README depends on)

Done on 2026-11-05 with a headless run of the Fabrication Toolkit (STATUS §16); the steps below are the record. Before that,
`production/` was Rev 1.02. Regenerating it needs the Fabrication Toolkit, a KiCad plugin: the owner's KiCad, or a
headless run of the plugin.

1. **JLC set (Fabrication Toolkit):**
   - the Gerber zip, renamed `Silkscreen_Reader_PCB_1.03.zip`;
   - `bom.csv`, `positions.csv`, `designators.csv` and `netlist.ipc`.
2. **`production/jlc_bom.csv`, edited by hand:**
   - add the new PTC line;
   - take `R42` out;
   - leave `R6` on its 4.7k line (the charger swap undid N9's move to 10k);
   - add the `R85`/`R86` line;
   - move `C34` into the 0.1u line;
   - take `R1` out of the 1M line;
   - remove the `C1` line;
   - the charger: the `U11` line becomes BQ21040DBVR (`C202311`); add a `TH1` line (`C13564`); move `R82` from the 10k
     line to the 200k line (`C25811`) and take `R71` out of that line; move `Q2` from the AO3401A line to the BSS138 line.
3. **Other fabs:** run `python fabrication/make_fab_files.py`, which writes `production/other_fabs/`.
4. **Placement:** check `F3`–`F6`, `R85`/`R86`, `U10`, `U11` (now SOT-23-6) and `TH1` in JLC's placement preview, including the new footprints' rotation.
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
  - ERC: 46 warnings at hand-off; 45 after the charger swap.
  - 862 teardrops at hand-off; 860 after the charger swap (re-run on 2026-11-04). Read the count from the board.
- **Stale strings:** search the living docs for `1.02`, `166`, `185`, `R42`, `` `R1` ``, `` `C1` ``, `C327066`, `TP7`,
  `TP4056`, `STDBY`, `R71`, `234 mA` and `0.25 A`. `4.7k` and `C23162` are `R6`'s again, so they are no longer stale.
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
