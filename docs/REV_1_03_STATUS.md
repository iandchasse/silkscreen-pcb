# Rev 1.03 status: NEXT_REVISION items in the design files

**Branch:** `1.03`, cut from `master` at `4530931` (the Rev 1.02 files). **Written:** 2026-11-03.

**State in one line:** the schematic, board and part fields carry N1–N9 (N7/N8 reached the board on 2026-11-03,
section 6). N10 is closed as "leave as is", and N11 was dropped. The changes are machine-checked (DRC with schematic
parity, ERC, netlist diff, Fabrication Toolkit dry run), and the designer has since worked on the board in KiCad
(`R85`/`R86`, teardrops). Production files and docs are not regenerated; the docs pass is handed off in
[REV_1_03_DOCS_HANDOFF.md](REV_1_03_DOCS_HANDOFF.md). The title blocks read Rev 1.03 (2026-11-03), and the back
silkscreen prints it. At the 2026-11-03 commit, the board passes DRC with 0 errors (the known warnings only), 0
unconnected and clean parity, ERC is at 46, and it has 862 teardrops. On 2026-11-04 the TP4056 charger was replaced by
TI's BQ21040 with an NTC ([section 14](#14-bq21040-charger-2026-11-04)): DRC is unchanged, ERC is at 45, and the
teardrops were re-added the same day (860).

This is the hand-over note. It covers what changed, where it deviates from [NEXT_REVISION.md](NEXT_REVISION.md) and
why, what is parked, how it was checked, and what to do next. The whole change list from the Rev 1.0 order to 1.03,
with an order-readiness note, is in [CHANGELOG.md](CHANGELOG.md).

## 1. What is on this branch

| File | Change |
|---|---|
| `silkscreen_pcb.kicad_sch` | `F3`, `F5`, `F6` added; `R42` became `F4`; `3V3` and `LDO_IN` labels split and renamed; `R6` = 10k. Later: `R1`/`C1` removed and `J1`'s shield tied to GND, title block 1.03 (certification review A1/A2). 2026-11-04: `U11` is a BQ21040 with the NTC `TH1`, `Q2` a BSS138, `R6` 4.7k, `R82` 200k, `R71` removed (section 14) |
| `silkscreen_pcb.kicad_pcb` | footprints, nets and copper as in section 2; zones refilled |
| `silkscreen_pcb.kicad_pro` | three Power net-class patterns for the new nets (`/LED_VIN`, `J6_3V3`, `EINK_3V3`); nothing else, the DRC exclusions are untouched |
| `silkscreen_pcb.kicad_dru` | **new (2026-11-03):** custom DRC rules. GND pours at least 0.5 mm from the SW nets, and other nets' vias at least 0.4 mm from the two switch nodes ([TRACE_AUDIT.md §1](audit-2026-11-03/TRACE_AUDIT.md#1-changes-made-in-this-pass-u10-corner-case-1-follow-up)). Then pours 0.3 mm from the panel rails and 0.25 mm from the LED-cathode pads, and the `J3`/`J1` footprint rules ([§1b](audit-2026-11-03/TRACE_AUDIT.md#1b-free-fixes-applied-after-the-audit)). Then the `U10` pad-pitch rule ([§1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern)) |
| `KiCad/9.0/3rdparty/TPS923610DRLR/` | **new footprint (2026-11-03):** `footprints.pretty/U_DRL0006A_6L_TI-LAND.kicad_mod`, TI's DRL0006A example land for `U10`. The symbol library `2026-09-06_02-10-40.kicad_sym` adds it to `U10`'s footprint filter. The Ultra Librarian footprints are untouched ([§1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern)) |
| `fabrication/part_fields.csv` | one new PTC row; `R42` and `R6` moved to other rows. Later: `R1` and `C1` removed. 2026-11-04: the charger rows (section 14) |
| `docs/REV_1_03_STATUS.md` | this file |

**2026-11-03 additions on the working copy (uncommitted):**

- **N7/N8:** in the schematic and on the board (section 6).
- **`U10` corner:**
  - GND via moved from between `L2`'s switch pad and `C9`;
  - pour pulled back;
  - straight switch-node feed;
  - direct pin-4 → `C9` ground.
- **`Q4` gate-drive via:** moved 0.08 mm.
- **Board-wide trace audit:** [audit-2026-11-03/TRACE_AUDIT.md](audit-2026-11-03/TRACE_AUDIT.md).
- **Bench tests in theory:** [audit-2026-11-03/BENCH_THEORY.md](audit-2026-11-03/BENCH_THEORY.md), with a copper-level thermal model of `F3` and the sense path as placed.
- **Certification-readiness review, audited against this board:** [audit-2026-11-03/CERT_REVIEW_AUDIT.md](audit-2026-11-03/CERT_REVIEW_AUDIT.md). It gives verdicts on the external review's items A1–D3 and adds what that review missed (RoHS finish, the module grant's portable exclusion, the library antenna keep-out).
- **Free fixes from the audit** ([TRACE_AUDIT.md §1b](audit-2026-11-03/TRACE_AUDIT.md#1b-free-fixes-applied-after-the-audit)), copper and rules only, no parts added:
  - GND vias at the ESD/TVS parts `CR1`, `U6`, `U7`, `D3`;
  - second vias at 10 of 13 power layer changes;
  - solid ground connections on 16 pads;
  - the antenna keep-out also forbids pours;
  - 9 traces/vias moved off high-voltage pads (now ≥ 0.263 mm);
  - pour pull-back rules for the panel rails and the LED-cathode pads;
  - footprint-scoped rules for the `J3`/`J1` DRC errors;
  - 15 redundant track segments removed;
  - 14 edge-stitching GND vias.
- **`U10` on TI's land pattern** ([TRACE_AUDIT.md §1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern)):
  - new footprint `U_DRL0006A_6L_TI-LAND` (0.67 × 0.30 mm pads, 1.48 mm span), on the board and in the schematic's Footprint field;
  - "U10 pad pitch" rule for the 0.20 mm gaps;
  - `PWM_LED` exit from pin 2 re-routed;
  - pin 4 solid to the pour.
- **`F2`** stays above the cut line: no room below it. The README's cutting instructions now cover the bare `P+` stub ([TRACE_AUDIT.md §2.3](audit-2026-11-03/TRACE_AUDIT.md#23-board-edges-mounting-holes-and-the-cut-line)).
- **Teardrops** added by the designer in KiCad (871). **Trace tidy:** 19 traces straightened at 20 places; 17 teardrops on changed track ends removed, re-added later; `C6`'s GND pad solid ([TRACE_AUDIT.md §1d](audit-2026-11-03/TRACE_AUDIT.md#1d-teardrops-and-trace-tidy)).
- **Reference designators** (2026-11-03):
  - **Uniform style:** all 187 visible references are on B.Silkscreen at the board's 0.5 mm height and 0.1 mm stroke, not bold, at 0° or 90°.
    - `R85`, `R86`, `F3`, `F5` and `F6` were 1.0 mm.
    - `R84`, `R83`, `C34`, `CR1` and `L1` were bold.
    - 30 were set to 180° or 270°.
  - **67 moved,** each to a spot beside its own part. They had overlapped pads, silk or another reference; sat under another part; were nearer a different part; or sat far from their own.
  - **Newly visible:** `F5` and `F6` are shown, clear of the cut-line marker and `C11`. `H5`'s reference moved off the front artwork to the back.
  - **Kept inside outlines:** the ten through-hole buttons and `U4` keep their references inside the part outline, as before.
  - **Exception:** `R22`/`R23` stay under `U4`'s edge, aligned with their columns. `C37` and `U4`'s pads leave no free spot beside them, so a visible spot needs `C37`/`C36` moved.
  - **Checks:** no reference touches a pad, hole, silk line, edge or another reference. DRC silkscreen warnings went from 53 to 44, none of them on a reference.
- **Layout fixes from the audit review** (2026-11-03, [TRACE_AUDIT.md §1f](audit-2026-11-03/TRACE_AUDIT.md#1f-layout-fixes-applied-after-the-review-2026-11-03)):
  - **`F3` pour keep-out (T20):** a rule area forbidding pour 1.0 mm around `F3`'s pads on both layers, so the PTC trips as the study intended ([BENCH_THEORY.md §2.4](audit-2026-11-03/BENCH_THEORY.md#24-the-studys-model-with-these-numbers)).
  - **Mounting holes (T17):** copper moved out of the 2.5 mm keep-out at `H1`, `H2`, `H3`, `H5` and `H6`. Three nets can't move without moving parts: `Q3`'s gate, `/P+_FUSE` and `R20`'s net.
  - **Right edge (T10):** `C-`, `W-`, `LED_SW` and `I2C_SDA` moved 0.27 mm in, so `C-` is now 0.746 mm from the edge. One GND via moved.
  - **Checks:** DRC identical to before. 4 teardrops removed, re-added later (section 10, step 9).
- **Certification-review cheap set** (2026-11-03, [CERT_REVIEW_AUDIT.md §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)):
  - **A1:** the USB-C shell is tied straight to GND: `J1`'s four shell tabs sit in both GND pours, and `R1`, `C1` and the shell track are gone.
  - **A2:** title blocks 1.03 / 2026-11-03, and `Rev ${REVISION} ${ISSUE_DATE}` on the back silkscreen at (87.09, 138.75).
  - **B2:** GND vias at `U4` pins 1 and 40.
  - **B5:** `C33` and `R7` swapped, so the 0.1 µF is 1.02 mm from `U4` pin 2; the 3V3 via moved and `C33` has its own GND via.
  - **B7:** 8 GND return vias beside fast-signal vias.
  - **Wording:** HARDWARE.md §3.1 and §16, and the README's surface finish.
  - **Not done:** B6 and the rest, recorded in [NEXT_REVISION.md §9](NEXT_REVISION.md#9-certification-readiness-items-for-later-recorded-2026-11-03).
  - **Checks:** DRC as before plus one starved thermal on a `J1` shell tab (front only; it is bonded on both layers), ERC unchanged. 15 teardrops removed, re-added later (section 10, step 9).
- **Independent review** (2026-11-03), [independent-review-2026-11-03/](independent-review-2026-11-03/BOARD_REVIEW.md):
  - **The review:** a block-by-block review, from the design files and datasheets only. No Critical findings; 2 High,
    6 Medium.
  - **The triage:** [TRIAGE.md](independent-review-2026-11-03/TRIAGE.md) re-rates every finding with this project's
    context.
  - **Four cheap fixes applied:**
    - pour-free areas about 1 mm around P+ and 3V3 at the cut line, on both layers (H-2);
    - the back-silk touch-option note now names `F4` instead of `R42` (M-6);
    - the schematic `R6` note gives the 10k charge current (L-1);
    - a second GND via at `U10` pin 4 (L-14).
  - **Checks:** DRC and ERC identical to before; no track changed, so no teardrops to redo.
  - **Filed:** firmware, bench and next-revision items in NEXT_REVISION §4, §6 and §10; documentation items in the
    hand-off.
- **BQ21040 charger** (2026-11-04, [section 14](#14-bq21040-charger-2026-11-04)): `U11` is TI's BQ21040 (SOT-23-6) in
  place of the TP4056, with a 10 kΩ NTC (`TH1`) on its `TS` pin. That closes C1 / H-1: charging only between about 0
  and 41 °C, plus 30 min pre-charge and 10 h fast-charge timers. `Q2`, now a BSS138, gates `TS` instead of `CE`. `R6`
  4.7k, `R82` 200k, `R71` removed. DRC identical, ERC 45; teardrops re-added afterwards (860).
- **DRC:** 0 errors; the 7 footprint-inherent ones now pass under footprint-scoped rules. 0 unconnected; parity clean. ERC 46, and 45 after the charger swap.

The board diff in git is about 7,000 lines because KiCad re-serialises the refilled GND pours. The structural diff is
small (section 5).

## 2. Item by item

Numbering follows [NEXT_REVISION.md](NEXT_REVISION.md). All new footprints are
`Fuse:Fuse_0603_1608Metric_Pad1.05x0.95mm_HandSolder` on B.Cu, part MF-FSMF010X-2 (Bourns, LCSC `C210355`, 0.10 A
hold, 0.30 A trip, JLC Extended).

| Item | Status | What was done, and where it differs from the doc |
|---|---|---|
| [N1](NEXT_REVISION.md#n1-frontlight-ptc-f3) | Done | `F3` at (47.2, 115.8): pad 1 `LDO_IN`, pad 2 `/LED_VIN`. Nothing fits beside `L2`/`C12`/`U10`, so the PTC sits in the pocket above the `LED_SW` run and the copper hops. `LED_VIN`: pad 2 → via (49.65, 116.15) → F.Cu → the old via at (52.0, 117.8) → the existing link to `L2.1`. `LDO_IN`: the F.Cu stub (now ending at (52.9, 117.926)) → west along y 118.5 → via (46.1, 116.8) → pad 1. `C12` stays on the `U10` side. One GND stitching via at (54.1, 113.1) keeps the B.Cu pour pocket above the `LED_SW` run connected; without it `C27.1` and `C31.2` lose their ground. |
| [N2](NEXT_REVISION.md#n2-touch-supply-ptc-f4-replaces-r42) | Done | `F4` replaces `R42` on the same pads and traces, at (91.5145, 120.9255, −90°). `R66` (DNP, alternate touch mapping) is still a 0 Ω; fit a PTC on its pads if that mapping is ever built. |
| [N3](NEXT_REVISION.md#n3-j6-pin-7-ptc-f5) | Done, different place | `F5` at (99.5, 61.0), rotated 180°: pad 1 `3V3` east, pad 2 `J6_3V3` west. Not on the y = 42 spur. `J6` is a right-angle header whose body (courtyard x 87–103, y 35–49) covers every spot beside pin 7 and the y = 42 stretch of the spur, and further down the spur squeezes through a 0.7 mm corridor between `SW10.4` and `SW10.1`/`SW10.2`. See the note below the table. |
| [N4](NEXT_REVISION.md#n4-move-cr2-to-the-j6-side) | Done in effect, `CR2` not moved | `CR2` already sat on the branch that becomes the J6 side of `F5`, so a TVS that fails short is limited by `F5` as intended. The doc's spot beside pin 7 is under `J6`'s body. `CR2`, like `F5` and `J6`, is above the x3 cut (y 62.0). |
| [N5](NEXT_REVISION.md#n5-e-paper-ptc-f6) | Done | `F6` at (83.9, 110.3) in the trunk east of the hub: pad 1 `3V3` west, pad 2 `EINK_3V3` east. `L1.2` and `C10.2` are on `EINK_3V3`. The GND stitching via at (85.0, 111.1) was in the way and moved to (85.9, 111.9). The touch feed is re-tapped upstream of `F6`: B.Cu from (81.61, 110.3) → via (81.5, 111.5) → F.Cu along y ≈ 112.6 → the existing F.Cu feed at (91.17, 112.43). The old B.Cu tap inside `L1`'s pad and the touch via at (91.17, 112.43) are gone. No via or F.Cu copper lies over `F6`'s body. |
| [N6](NEXT_REVISION.md#n6-panel-logic-supply-from-the-e-paper-ptc) | Done | `J2.15`, `J2.16` and `C22.2` are on `EINK_3V3`. The old 3V3 branch to `J2` was cut at (78.0, 112.7); its top end (77.63, 114.3) is fed from `EINK_3V3` by about 12.7 mm: B.Cu (86.6, 110.3) → (84.2, 108.6) → via → F.Cu → via (78.3, 113.6) → B.Cu. `R66` pad 1 stays on 3V3: its F.Cu line (now starting at (91.1, 135.9)) is tied to the touch 3V3 feed by a new 16.6 mm F.Cu run along x ≈ 91.1–91.3 up to the via at (91.3, 119.3). The via at (81.7, 133.6) and the F.Cu links to `R66`'s line were removed. |
| [N7](NEXT_REVISION.md#n7-dw01a-sense-resistor-r85) | Done, different place | `R85` (78.66, 69.11) + `R86` (75.0, 70.5): 2 × 0.1 Ω 1206 in parallel (`C25334` Basic) from `Q1` pin 3 (`/B-_SENSE`) to GND. Placed by hand west of `Q1`, because the pocket by pin 3 had no room. Section 6. |
| [N8](NEXT_REVISION.md#n8-c34-from-22-nf-to-100-nf) | Done | `C34` = 0.1u (`C14663`) in the schematic, the part fields and on the board. |
| [N9](NEXT_REVISION.md#n9-r6-from-47k-to-10k) | Done | `R6` = 10k, RC0603FR-0710KL, `C25804`. The 4.7k line (`C23162`) is gone from `part_fields.csv`. |
| [N10](NEXT_REVISION.md#n10-move-c36-and-c37) | Closed: left as is | Section 7. |
| N11 | Dropped | Ian: "forget the test pads, we'll leave them for later, if at all." |

**How N3 and N4 were done.** The old 3V3 copper in the arm was a loop. A "west branch" ran from the trunk through
`CR2`'s pad 1 and east along y 60.3–60.8; a "south branch" ran up x = 101.1; both met at (99.4, 60.8) in front of
`SW10.2`, and the spur to `J6` pin 7 started at `SW10.2`'s pad. The loop is cut:

- The south branch now feeds `SW10.2` directly and stays 3V3. `SW10` is the power button, so it must not sit behind `F5`.
- `F5` pad 1 taps that feed at (101.32, 61.0).
- `F5` pad 2 leads through the corridor at x = 100.629 into the existing spur, which with `J6` pin 7 and the old B.Cu 3V3
  copper polygon over it is re-netted `J6_3V3`.
- The former west branch, including `CR2`'s pad 1, is also `J6_3V3`. The dead-end trunk stub into `CR2`'s pad was
  removed.

## 3. Nets, schematic and parts

**Pins that moved nets** (checked with a pin-to-net diff of the exported netlists, old against new):

| Pins | From | To |
|---|---|---|
| `C12.2`, `L2.1`, `U10.1` | `LDO_IN` | `/LED_VIN` (a local label, so the board name has the root-sheet slash) |
| `J6.7`, `CR2.1` | `3V3` | `J6_3V3` |
| `L1.2`, `C10.2`, `C22.2`, `J2.15`, `J2.16` | `3V3` | `EINK_3V3` |
| `F3` | new | pin 1 `LDO_IN`, pin 2 `/LED_VIN` |
| `F4` (was `R42`) | new | pin 1 `3V3`, pin 2 `/PIN_2` |
| `F5` | new | pin 1 `3V3`, pin 2 `J6_3V3` |
| `F6` | new | pin 1 `3V3`, pin 2 `EINK_3V3` |

**Schematic placement** (sheet coordinates, mm):

- `F3` at (271.78, 257.81), in line between the `LDO_IN` label (moved to (264.16, 257.81)) and the `C12`/`L2`/`U10`
  node; local label `LED_VIN` at (287.02, 248.92) on the vertical `L2.1`–`U10.1` wire.
- `F4` is `R42`'s symbol converted in place (`Device:Polyfuse`) at (318.77, 369.57).
- `F5` at (433.07, 62.23) inside the `J6` connector box, with global labels `3V3` and `J6_3V3`. The `J6` pin 7 label and
  the `CR2` pin 1 label were renamed `J6_3V3`.
- `F6` at (95.25, 279.4) with global labels `3V3` and `EINK_3V3`. The label at (96.52, 288.29) (`L1.2`, `C10.2`) was renamed
  `EINK_3V3`; the label at (146.05, 284.48) (`C22.2`, `J2` 15/16) was renamed and moved to (140.97, 287.02).
- `R6` value 10k.

**Parts.** `part_fields.csv` has a new row `"F3,F4,F5,F6"` (MF-FSMF010X-2, Bourns, `C210355`); `R42` left the 0 Ω row;
`R6` joined the 10k row. `apply_part_fields.py` run as a dry run on the committed files reports 0 fields to update. Net
effect on the BOM: three more fitted references (`F3`, `F5`, `F6`; `F4` takes `R42`'s place), one more Extended part
type, one fewer distinct 0603 resistor value (the 4.7k). The README's reference count (185 = 166 fitted + 11 DNP + 8 bare-copper)
needs re-deriving.

**Other copper changes.**

- The old 3V3 copper polygon over the J6 spur (B.Cu, 4 points around (89.8, 44.1)–(103.5, 43.1)) is kept but re-netted
  `J6_3V3`.
- Removed vias: (91.171, 112.429) and (81.7, 133.617). Moved: GND via (85.0, 111.1). Added: GND via (54.1, 113.1).
- `F5` and `F6` have no silkscreen outline: `F5` sits on the B.Silkscreen cut-line marker (y 61.3–62.7). Their references
  were hidden at first (`F6`'s collided with `C11`'s). The reference-designator pass of 2026-11-03 shows them, placed clear
  of the marker and `C11`.

## 4. What the layout had to respect (facts for anyone continuing in the GUI)

- `J6`'s courtyard is its real body (x 86.96–103.22, y 35.07–48.99): nothing fits under it.
- The documented x3 cut is at y 61.86 and the build cuts at y 62.0; the cut-line marker on B.Silkscreen spans y 61.3–62.7.
- The board is a single-sided assembly (every real part is on B.Cu); new parts stay on B.Cu so JLC does not need a second pass.
- Net classes: Default 0.15 mm clearance, Power 0.20 mm and 0.25 mm tracks, SW 0.25 mm. The new nets are Power. Zones
  must be refilled with the patched `.kicad_pro` in place, or DRC reports about 60 clearance errors against a stale fill.
- Cutting the B.Cu GND pour can strand a pocket. DRC then shows "Zone [GND] … Missing connection" with no location.

## 5. Verification

Baseline is `master` at `4530931`. Commands (KiCad 9.0.6):

```
kicad-cli pcb drc --severity-all --schematic-parity --format json -o drc.json silkscreen_pcb.kicad_pcb
kicad-cli sch erc --severity-all --format json -o erc.json silkscreen_pcb.kicad_sch
kicad-cli sch export netlist --format kicadsexpr -o out.net silkscreen_pcb.kicad_sch
```

| Check | Result |
|---|---|
| DRC findings | 87 before, 88 after: the same findings, plus one `silk_over_copper` (the cut-line marker over `F5`'s pads) |
| Unconnected items | 0 before and after |
| Schematic parity | 0 issues before and after |
| ERC warnings | 41 before, 45 after: four `footprint_link_issues`, the PTC footprint not matching the Polyfuse symbol's filter, exactly as `F1` and `F2` already do |
| Netlist | the pin-to-net diff is exactly the table in section 3, plus values and fields |
| Board, structural diff | footprints: `R42` out, `F3`–`F6` in; net changes on `C10`, `C12`, `C22`, `CR2`, `J2`, `J6`, `L1`, `L2`, `U10`; `R6` value and fields; one `gr_poly` net; copper segments and vias as described |
| Line endings | `.kicad_pcb` and `.kicad_sch` CRLF, `.kicad_pro` LF, as before; `.gitattributes` normalises on commit |
| Fabrication Toolkit dry run (scratch copy) | BOM line `F3, F4, F5, F6` 0603 × 4 `C210355`; `R6` in the 10k group; CPL rows for `F3`–`F6` on the bottom side |

DRC and ERC were also run on the files copied into the repo, not only on the scratch copy.

## 6. N7 and N8: schematic and board

**Board (2026-11-03).** The designer placed `R85` (78.66, 69.11, 180°) and `R86` (75.0, 70.5, 90°) by hand in KiCad,
west of `Q1`. `Q1` pad 3 is on `/B-_SENSE`, `C34` is 0.1 µF, and parity DRC is clean.
[TRACE_AUDIT.md](audit-2026-11-03/TRACE_AUDIT.md) records two follow-ups. A via that sat in `R85`'s pad was moved out.
The 0.2 mm `R85`→`R86` link, which carries about 46 % of the current, is rated at about 4 °C rise at 1 A. The notes below
are from before the placement.

**Update 2026-11-03: the schematic carries N7 and N8.**

- **Schematic:**
  - `R85` and `R86` (`Device:R`, value 0.1, `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder`, Yageo RL1206FR-070R1L / LCSC `C25334`) sit side by side right of `Q1`, at (64.77, 213.36) and (64.77, 208.28), both rotated 90°.
  - `Q1` pin 3's wire now runs to a node at (60.96, 213.36) and carries the local label `B-_SENSE` (board net `/B-_SENSE`).
  - The GND symbol `#PWR05` moved to (68.58, 213.36) on the far side of the pair.
- **`C34`:** value 0.1u, with the `C14663` fields from `part_fields.csv`.
- **Checks:**
  - ERC: no errors; one new `pin_to_pin` warning (`Q1` pin 3 unspecified meets a passive pin), the same benign type as `J6` pin 7.
  - The netlist diff is exactly `Q1.3` GND → `/B-_SENSE`, plus `R85`/`R86` between `/B-_SENSE` and GND.
- **Until the board caught up,** parity DRC reported four expected items (all gone since the placement):
  - `C34` value;
  - `Q1` pad 3 net;
  - missing `R85`;
  - missing `R86`.
- **On the board:** "Update PCB from Schematic" brings in both footprints and re-nets `Q1` pad 3. The pad then leaves the GND pour on refill and needs its own route to the pair. A layout search on 2026-11-03 found no legal spot for the pair near `Q1` (see below), so placing it needs parts moved. The only single-resistor spot nearby is about 11 mm west of `Q1` pin 3, beside `J7`.

**Original design notes (before parking).** A 50 mΩ sense resistor from `Q1` pin 3 (new net `B-_SENSE`) to GND: two 0.1 Ω 1206 resistors in
parallel (`R85`, `R86`, Yageo RL1206FR-070R1L as the DigiKey part, UNI-ROYAL 1206W4F100LT5E `C25334` as the JLC Basic
part), with `R16` and `U5` unchanged and `C34` raised to 0.1 µF (`C14663`). The pair was chosen over the doc's single
68 mΩ part because the pair needs no Extended fee. (The 68 mΩ parts are in fact stocked: JLC's own part pages showed
`C327066` 4,731 and `C52472` 2,443 on 2026-11-03; the "stock 0" came from jlcsearch.) The schematic part was written and verified, then removed again so that
schematic and board agree. For reference: `R85` (54.61, 213.36) and `R86` (54.61, 205.74), both rotated 90°; the `Q1` pin 3
wire extended to (50.8, 213.36); a bus at x = 50.8 up to a local label `B-_SENSE` at (50.8, 200.66); a GND bus at x = 58.42
with `#PWR05` moved to (58.42, 213.36) (rot 90); junctions at (50.8, 213.36), (50.8, 205.74), (58.42, 213.36). `Q1`'s pin
row is only 4 mm above the section divider (y 217.4), which is why the pair is stacked horizontally.

**Why the pocket by `Q1` did not work.** A search with the real board outline, 0.15–0.25 mm clearances and the other footprints'
courtyards found no legal spot for two 1206 or two 0805 resistors within 22 mm of `Q1` pin 3:

- The doc's pocket above-left of pin 3 ignores the `PWR_BUTTON` diagonal (83.08, 69.32) → (86.5, 65.9), the 3V3 trunk
  diagonal (82.93, 68.77) → (86.6, 65.1), the GND vias at (86.4, 68.8) and (88.5, 70.1), and the `UNUSED_GPIO_45` trace.
- The free band north-east of `Q1` (x 87–91, y 66.2–69) is inside `J5`'s courtyard (x 88.11–96.70, y 63.05–69.94), the
  battery plug area. A 1206 would fit there only by overlapping it (about (88.6–89.2, 67.2–67.4)).
- 0805 spots exist only far away, for example (86.4, 62.4) in the arm.

**Options that were on the table** (the designer placed the pair by hand instead, see above).

1. Re-lay the area by hand in KiCad: re-route `UNUSED_GPIO_45`/`46`, nudge the `B−` jog and the GND vias, or relocate
   `R56`/`C34`. Then re-apply the schematic block above.
2. A single 0805 50 mΩ part: UNI-ROYAL 0805W4F500MT5E (`C247602`, 250 mW, JLC stock about 286,000, Extended) or Panasonic
   ERJ-6BWFR050V (`C2075868`, 500 mW, about 17,700, Extended). Same sensing, less pulse margin, still needs a 3.3 × 1.4 mm pocket.
3. The same sensing with the resistor in the `B−` lead (`Q1` pin 1 instead of pin 3). It still needs a pocket of that size.

Whichever is chosen, N8 (`C34` = 0.1 µF) goes with it.

## 7. N10: closed, left as is

`J7`'s courtyard is x 56.15–73.45, y 69.3–85.6, and its card slot opens at the board's north edge (y 67.5). The card
therefore inserts along y, and the insertion force bends the board about the x axis. `C36` (62.5, 86.7) and `C37` (62.3, 88.2)
already lie along x, parallel to the pad row, which is "the bending axis runs along their length". Rotating them 90° would
put them across it. Moving them 5 mm has no room: the rows below are the `R21`–`R26` resistors (y 89.9 and 91.8).
**Closed 2026-11-03:** both stay as they are.

## 8. Soft-termination and open-mode MLCCs (search of 2026-11-02)

**Decision (2026-11-03): skipped.** Ian: soft-termination MLCCs are not realistic for this board, so the MLCCs stay as
they are. The search is kept for the record.

Ian: "soft termination caps are impossible to find; if you can find them, by all means we can talk about replacing them."
The JLC parts library and LCSC were searched for the same value, voltage and package:

| Slot | Result |
|---|---|
| `C2` 10 µF 25 V X5R 0603 | none |
| `C3` 10 µF 0603 | only Murata GRJ188R61A106ME11D, 10 V, JLC stock 0 |
| `C4`/`C6`/`C32` 22 µF 25 V X5R 0805 | none (soft parts stop at 10 µF in 0805) |
| `C25`/`C26` group, 1 µF 0603 | Murata GCJ188R71E105KA01D (`C908553`: 25 V X7R, AEC-Q200, soft termination, Extended, LCSC stock 13,550, about $0.093 at 10 pcs against $0.014 for the Basic CL10A105KB8NNNC); Samsung CL10B105KA8VPNC (`C307350`: 25 V X7R, design code V = soft termination per Samsung's catalog, JLC stock about 11,800) |

Caveats: LCSC's own catalog search was blocked, so soft parts LCSC stocks but JLC's library lacks are not excluded; Taiyo Yuden
and Walsin were not examined; the 1 µF candidates are 25 V X7R against 50 V X5R today, so check the DC-bias curves; the Samsung
soft-termination reading rests on an older catalog copy. Samsung's open-mode design code (W) has no part in the library at these values.

## 9. Not done yet

- **Teardrops after the charger swap:** done on 2026-11-04 (section 10, step 12); 860 now.
- **Production files:** `production/` is still Rev 1.02. Regenerate with the Fabrication Toolkit after the layout is reviewed,
  edit `production/jlc_bom.csv` by hand (new PTC group, `R42` out, `R1` out of the 1M group, `C1` out, and the charger
  lines of section 14), check the new footprints in JLC's placement preview, and rebuild the layout and schematic PDFs.
- **Docs and images:** handed off. [REV_1_03_DOCS_HANDOFF.md](REV_1_03_DOCS_HANDOFF.md) lists every user-facing change since
  Rev 1.02, the task for each file (HARDWARE.md, README, BOM.md, THIRD_PARTY.md, the images and PDFs) and the checks.
  The certification audit's three wording fixes are done ([CERT_REVIEW_AUDIT.md §4](audit-2026-11-03/CERT_REVIEW_AUDIT.md#4-documentation-fixes-queued)):
  - HARDWARE.md §16, the antenna "far side" claim;
  - HARDWARE.md §3.1, shield handling, after A1;
  - the README's surface-finish line, which now rules out HASL with lead for RoHS.
- **Revision label:** both title blocks now read 1.03 / 2026-11-03, and the back silkscreen prints `Rev ${REVISION} ${ISSUE_DATE}`.
  The README, HARDWARE.md's header note and the `production/` file names still say 1.02 until the docs pass and the
  regenerated production files.
- **Firmware items F3–F7** in NEXT_REVISION §4 are untouched. F11 now describes the BQ21040's `USB_STAT` decode.
- **Pre-order measurements** from NEXT_REVISION §6 (frontlight PTC bench test, sense-resistor trial, the coincident-peak
  measurement) have not been done. [audit-2026-11-03/BENCH_THEORY.md](audit-2026-11-03/BENCH_THEORY.md) predicts their
  results from the datasheets and a copper model of this board. Of them, the PTC test (on a 1.03 board) and the
  coincident peak still matter; insertion and the hot run are covered by theory.

## 10. Review checklist in KiCad

1. Open `silkscreen_pcb.kicad_pro`. Tools → **Update PCB from Schematic** should have nothing to change, since parity DRC is clean.
2. Run DRC with "test for parity". Expect 0 errors. The warnings should be silkscreen ones on artwork and footprint outlines, none on a reference designator (including one `silk_over_copper` at (79.3, 61.4): the cut-line marker over `F5`'s pads, cosmetic), the 5 starved thermals kept on purpose ([TRACE_AUDIT.md §2.5](audit-2026-11-03/TRACE_AUDIT.md#25-ground-pour)) plus a sixth on `J1`'s top-left shell tab on F.Cu ([CERT_REVIEW_AUDIT.md §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)), and the 4 button stubs, which the project excludes.
3. Look at the layout around `F3` (the two hop vias and the F.Cu `LDO_IN` run under `L2`), `F6` (pads, the two new routes
   and the moved GND via), and `F5`/`CR2` in the arm, including the narrow corridor at x = 100.63.
4. Refill all zones (B). The pours should not change.
5. Look over the reference designators on the back (section 1): 67 moved, `F5`/`F6` now shown, `H5`'s moved to the back. `R22`/`R23` are the one pair left under a part (`U4`).
6. Check `F3`–`F6` in JLC's placement preview when the files are regenerated.
7. Look over the free fixes of [TRACE_AUDIT.md §1b](audit-2026-11-03/TRACE_AUDIT.md#1b-free-fixes-applied-after-the-audit) in the 3D viewer, front side. All the new vias are tented and keep their drill holes off the artwork; check you are happy with where they sit.
8. Check `U10` on its new footprint ([§1c](audit-2026-11-03/TRACE_AUDIT.md#1c-u10-on-tis-example-land-pattern)): the 3D model still sits on the pads. When the production files are regenerated, check its rotation in JLC's placement preview; the footprint origin and orientation did not change.
9. Teardrops are on (TRACE_AUDIT T6). **Done 2026-11-03:** after all the fixes, the designer re-ran the teardrop command
   and refilled. The board has 862 teardrops, including the 36 that earlier edits had removed:
   - 17 from the trace tidy ([TRACE_AUDIT.md §1d](audit-2026-11-03/TRACE_AUDIT.md#1d-teardrops-and-trace-tidy));
   - 4 from the layout fixes ([§1f](audit-2026-11-03/TRACE_AUDIT.md#1f-layout-fixes-applied-after-the-review-2026-11-03));
   - 15 from the certification fixes ([CERT_REVIEW_AUDIT.md §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)).

   After any later track edit, re-run the command and refill.
10. Look over the certification fixes ([CERT_REVIEW_AUDIT.md §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)):
    - the `C33`/`R7` column beside `U4` pins 1–3;
    - the two GND vias under `U4` at pins 1 and 40;
    - the 8 return vias;
    - `Rev 1.03 2026-11-03` on the back at (87.1, 138.8);
    - `J1`'s four shell tabs on GND in both pours, with `R1`/`C1` gone.
11. Look over the independent-review fixes ([TRIAGE.md §4](independent-review-2026-11-03/TRIAGE.md#4-applied-on-2026-11-03)):
    - the two pour-free rule areas at the cut line (x 86.2–88.6 and 98.85–102.45, y 60.8–63.1, both layers);
    - the GND via at (48.76, 123.10) beside `U10` pin 4;
    - the back-silk note at (91.7, 136.2), now "unpopulate F4,R44,46,52".
12. Look over the charger swap ([section 14](#14-bq21040-charger-2026-11-04)), then put the teardrops back:
    - `U11` (SOT-23-6; pin 1, `TS`, at (83.15, 93.45)) and its four short routes;
    - the `TS` run from `U11` past `R82` and `Q2` to `TH1` at (100.6, 93.0), which passes between `U11`'s pad rows and
      between `F1`'s pads;
    - the three new GND vias, at `U11` pin 5, `Q2` pin 2 and `TH1` pin 2;
    - then re-run the teardrop command and refill.

    **Done 2026-11-04:** the designer re-ran the teardrop command; the zones were then refilled (until a refill, new
    teardrops are unclipped, and DRC shows about 145 clearance errors against neighbouring copper). The board has 860
    teardrops: against `3c5f234`, 21 around the old charger parts went, 17 came on the new ones, and the L-14 GND via
    beside `U10` gained two. The other 813 are unchanged.

## 11. Decisions needed

- **Production files:** who regenerates them (section 9; [REV_1_03_DOCS_HANDOFF.md §4](REV_1_03_DOCS_HANDOFF.md#4-production-files-a-separate-job-that-readme-depends-on)). The docs pass is handed off.
- **For later, recorded for reference:** the certification items not done in 1.03, including how far to take the antenna
  clearance (B1) ([NEXT_REVISION.md §9](NEXT_REVISION.md#9-certification-readiness-items-for-later-recorded-2026-11-03)).
  The charge-temperature item C1 is done (section 14).

Settled on 2026-11-03:
- The revision is bumped to 1.03 and printed on the back silkscreen (certification review A2).
- The certification review's cheap set is applied; B6 and the rest are recorded for later ([CERT_REVIEW_AUDIT.md §6](audit-2026-11-03/CERT_REVIEW_AUDIT.md#6-applied-on-2026-11-03)).
- The independent review is triaged. Its four do-now fixes are applied, and the rest is filed in NEXT_REVISION §4, §6 and §10 ([TRIAGE.md](independent-review-2026-11-03/TRIAGE.md)).
- N7 is placed on the board (section 6).
- N10 is left as is (section 7).
- Soft-termination MLCCs are skipped (section 8).
- T3 and T18 are accepted as they are. T12 is already done: the board has a cut-out under the antenna. T5 and T9 are left as is ([TRACE_AUDIT.md §1e](audit-2026-11-03/TRACE_AUDIT.md#1e-owner-review-of-the-open-items-2026-11-03)).
- T20 (`F3` keep-out), T17 (hole clearances) and T10 (right edge) are applied ([TRACE_AUDIT.md §1f](audit-2026-11-03/TRACE_AUDIT.md#1f-layout-fixes-applied-after-the-review-2026-11-03)).

Settled on 2026-11-04:
- The TP4056 is replaced by TI's BQ21040 with a board-mounted NTC (owner's choice of "option B" after a cost and
  specification comparison; section 14). The NTC sits on the board as an ambient sensor, not at the cell.

## 12. How the edit was made

All scripts lived in a scratch folder and are not in the repo; the approach, if it has to be repeated:

1. **Scratch copy first.** The repo files were never edited directly. The scratch copy was checked against the baseline
   (DRC, ERC, netlist) before anything was copied back, with KiCad closed.
2. **Schematic:** text-level edits (byte-exact CRLF) anchored on coordinates and asserted, new items inserted at the end of
   their kind group, UUIDs generated deterministically so a re-run reproduces the same file. Fields came from `part_fields.csv`
   through `apply_part_fields.py`. Visual check: `kicad-cli sch export pdf`, then crop with PyMuPDF.
3. **Board:** pcbnew Python in two stages. Stage 1 does the manual edits (re-netting, cuts, footprints). A small A* grid router
   (0.05 mm grid, per-class clearances, board outline, courtyards, keepouts over the PTC bodies) then routes the remaining
   connections on the stage-1 geometry, and stage 2 adds that copper, refills the zones and saves.
4. **pcbnew pitfalls:** cache every net and footprint before the first `Remove`; snapshot any footprint data you will need
   before removing it; keep removed items referenced, or `FootprintLoad` fails later; do footprints last.
5. **Legal-spot search:** the true outline from `GetBoardPolygonOutlines()`, courtyards from `BuildCourtyardCaches()` and
   `GetCourtyard()`, and shapely for the clearances.

## 13. Related loose ends

- `docs/BOARD_FAILURES.md` case 2 still reads the 3.5 kΩ at 3V3 as a 3V3 leak. An `LDO_IN` short also reads about 5.5 kΩ at
  3V3 through `U3`'s body diode, so the first meter checks should be `LDO_IN` (`C4` pad 1) and `USB_VBUS` to GND, and the
  audit's "case 2 = 3V3 rail" wording needs the same caveat.
- NEXT_REVISION §3 N7 still describes the 68 mΩ part first. The chosen 50 mΩ pair is its "No extra Extended fee" bullet, and
  the `C327066` stock note is in section 6 here.

## 14. BQ21040 charger (2026-11-04)

**Why.** The independent review's H-1 and the certification audit's C1: the TP4056 ran with `TEMP` grounded, so nothing
stopped charging in heat or cold, and it has no safety timer. The owner chose to replace it with TI's BQ21040 ("option B")
rather than keep it and add an NTC divider ("option A"), after a cost and specification comparison. The swap was built on
a scratch copy, reviewed by the owner in KiCad, and copied in with KiCad closed.

**What the BQ21040 brings** (TI SLUSCE2D):

- a 10 kΩ NTC input (`TS`) with fixed thresholds, nominally 0 °C and 45 °C;
- a 30 min pre-charge timer and a 10 h fast-charge timer;
- a 30 V input rating, with charging stopped above 6.6 V (OVP);
- 4.2 V ±1 % regulation (4.16–4.23 V);
- at most 1 µA from the cell into `OUT` while USB is absent (the TP4056: under 2 µA).

It is a JLC Extended part (`C202311`). The charging block costs about $0.20 more per board at 500 boards, $0.30 at 100,
$0.45 at 30 and $1.15 at 5, Extended fees included.

**Pins that moved nets** (pin-to-net diff of the netlists exported from `3c5f234` and from this schematic):

| Pins | From | To |
|---|---|---|
| `U11` (ESOP-8 → SOT-23-6) | 1 GND (`TEMP`), 2 `Net-(U11-PROG)`, 3 GND, 4 `USB_VBUS`, 5 `P+`, 6 `STDBY`, 7 `CHRG`, 8 `CE`, 9 GND (pad) | 1 `TS`, 2 `P+` (`OUT`), 3 `CHRG` (`CHG`), 4 `Net-(U11-ISET)`, 5 GND, 6 `USB_VBUS` (`VIN`) |
| `Q2` pins 2, 3 | `USB_VBUS`, `CE` | GND, `TS` |
| `R6` pin 1 | `Net-(U11-PROG)` | `Net-(U11-ISET)` |
| `R82` pin 2 | `CE` | `TS` |
| `TH1` | new | pin 1 `TS`, pin 2 GND |
| `R71` | `STDBY` to `USB_STAT` | removed |

That is all 17 pin changes. The `CE` and `STDBY` nets are gone. `Q2`'s gate stays on `/DET_NODE`, which `R81` still pulls
up to `USB_VBUS`.

**Parts** (`part_fields.csv`):

- **`U11`:** BQ21040DBVR (TI, `C202311`) on `SOT-23-6_Handsoldering`, the footprint the board's other SOT-23-6 parts use.
- **`TH1`:** 10 kΩ 1 % NTC, B3380 (Murata NCP18XH103F03RB, `C13564`, Extended), 0603 because the board has no 0402 parts.
- **`R6`:** 4.7k (`C23162`, Basic). The current is K_ISET / `R6`, with K_ISET 490–590 AΩ: 104–126 mA, about 115 mA. That
  is the current N9 set with the TP4056 and 10k, so N9's intent stands with a different value.
- **`R82`:** 200k (`C25811`, Basic; the line `R71` used). It is the `TS` pull-down, below.
- **`Q2`:** BSS138 (`C7420339`), on the `Q5`/`Q6`/`Q9` line. The AO3401A line keeps `Q3`, `Q7` and `Q8`.
- **`R71`:** removed.
- **Population:** unchanged at 188 references (169 fitted, 11 DNP, 8 bare copper): `R71` out, `TH1` in. Two more Extended
  types (`U11` and `TH1`); the TP4056 was a JLC Preferred part.

**How it works on this board.**

- **Charge enable.** Pulling `TS` to near 0 V (below about 76 mV) disables the BQ21040. `Q2`, now an N-FET (gate
  `/DET_NODE`, drain `TS`, source GND), holds `TS` low until `Q9` sees a correctly oriented cell. It replaces the `CE`
  drive, so the reverse-polarity mitigation of HARDWARE.md §3.3 works as before, and so does its known limitation: a
  pack in protection lockout reads 0 V and is not charged (M-5).
- **Temperature.** `TS` biases `TH1` with 50 µA. With `R82` in parallel, charging runs between about 0 and 41 °C at
  `TH1` (typical; −2 to +2 °C at the cold end and 38 to 44 °C at the hot end over the datasheet tolerances; TI's 0 °C and
  45 °C are nominal for this kind of NTC). Charging resumes about 2 °C inside each limit.
- **Fail-safe.** `R82` makes an open or missing `TH1` read as cold, so nothing charges. Without it, `TS` would float up
  into TI's no-sensor mode (TTDM), which also turns off the timers and termination. It costs about 3 °C at the cold end,
  the trade TI describes for its suggested 237 kΩ. 200 kΩ leaves more margin below the TTDM threshold: holding 1.525 V
  across it takes 7.6 µA, more than the 4–6.5 µA the pin folds back to.
- **Where `TH1` sits.** On the board at (100.6, 93.0), east of `F1`, as an ambient sensor. Spots at the battery bay's
  edge would need a 66 mm `TS` route with four vias around the board's east side, and the `J5` area has no room for an
  0603 plus its ground via. While charging, `TH1` reads an estimated 1–3 °C above the cell.
- **Status output.** `CHG` (open drain) is low only during the charge that starts at USB plug-in, at cell insertion
  (releasing `TS` counts) or when a flat cell enters pre-charge. Later top-ups, which start when the cell falls below
  4.04–4.16 V, run with `CHG` off (SLUSCE2D §8.3.6, §8.4.10, Table 1). `CHG` also stays low if that first charge pauses for
  temperature.
  - **Plug-in at any charge level** shows as charging: every power-up starts a charge (TI Figure 7). On a full cell
    that charge ends within about a minute, or a few minutes for a cell that has rested for hours (§8.4.11).
  - **`USB_STAT`** now has three levels: 2.20 V on battery, 1.11 V charging (0.95 V when a weak source has pushed the
    mux onto the battery), and 3.30 V with `CHG` off. The 0.55 V "complete" level went with `STDBY`.
  - **Firmware** separates the 3.30 V cases with `P+` = 2 × `BAT_MONIT` (NEXT_REVISION F11). TI specifies all pins
    high-impedance when USB is absent (§8.3.1), so the on-battery level should be the designed 2.20 V (L-4).
  - **Cell pulled while USB is in:** the charger's own output keeps the detector released, as with the TP4056. Its
    battery-detect routine then cycles `P+` between 4.2 V and 3.8 V in 25 ms steps, which `BAT_MONIT` averages to about
    4.0 V.
- **Input.** `C2` (10 µF) with its `R84` damper and `C25` are unchanged. TI asks for 1 µF at `VIN`; none was added,
  because a plain ceramic there would undo the hot-plug tuning of `C2`/`R84`/`C25` (HARDWARE.md §3.1), and the 30 V-rated
  BQ21040 does not need it. `U2`'s 6.0 V limit is still the reason for `R84`.
- **Heat.** (5.25 − 3.0) V × 0.125 A ≈ 0.28 W at the start of a fast charge. At TI's 131 °C/W that is about a 37 °C rise,
  far below the 125 °C regulation point.
- **Timer and cell size.** At 115 mA a 500 mAh cell charges in about 5 h. A cell above about 1000 mAh may not finish
  inside the 10 h timer; `R6` = 3.9k (about 140 mA) restores the margin.

**Layout.** Scripted as in section 12: pcbnew for the edits, the grid router for the new copper.

- **Placement:** `U11` at (84.10, 94.80), 270°, on B.Cu. `TS`, `OUT` and `CHG` are on its north row; `VIN`, GND and
  `ISET` on its south row. `TH1` at (100.6, 93.0), 0°, on B.Cu.
- **Removed:** the 34 tracks and vias of the old nets, and the 19 teardrops on the changed pads.
- **New copper,** all on B.Cu:
  - `TS`, about 21 mm with no vias: `U11` → `R82` → `Q2`'s drain, and a branch from that run to `TH1`. It passes
    between `U11`'s pad rows and between `F1`'s pads.
  - `OUT` → `C3` and `VIN` → the `USB_VBUS` copper at `C2`, both 0.3 mm. `ISET` → `R6`, and `CHG` → the existing `CHRG`
    run to `R67`.
  - `R81`'s `USB_VBUS` link, which used to run through `Q2`'s old source pad, is re-made around it.
  - The `USB_STAT` junction at `R67`/`R17` keeps `R71`'s old track as a plain joint.
  - Three GND vias, at `U11` pin 5, `Q2` pin 2 and `TH1` pin 2, each at least 0.2 mm outside its pad's mask opening.
- **References:** `U11` and `TH1` on B.Silkscreen in the board's 0.5 mm style.

**Checks** (on the files in the repo, KiCad 9.0.6):

| Check | Result |
|---|---|
| DRC with parity | 0 errors. The warnings are identical to `3c5f234`'s: 31 `silk_edge_clearance`, 10 `silk_over_copper`, 3 `silk_overlap`, 6 `starved_thermal`, 4 excluded `track_dangling`. 0 unconnected; parity clean |
| ERC | 45, was 46: the four-way junction at `R71`'s old node is gone |
| Netlist | 188 components before and after; the pin-to-net diff is exactly the table above |
| Part fields | `apply_part_fields.py` dry run: 180 parts matched, 0 to update |
| Teardrops | 860, was 862: the designer re-ran the command after the swap. 21 around the old charger parts went, 17 came on the new ones, and the L-14 GND via beside `U10` gained two; zones refilled. DRC as above |
| Renders | before/after crops of the charger area, `TH1`/`Q2` and the schematic, checked by eye |

**Still to do:**

- Bench on the first 1.03 boards (NEXT_REVISION §6): the charge current, the `TS` window, the `USB_STAT` levels, `TH1`
  against the cell's temperature, and the hot-plug check.
- Firmware: F11, the new `USB_STAT` decode.
- Docs: [REV_1_03_DOCS_HANDOFF.md §3.8](REV_1_03_DOCS_HANDOFF.md#38-from-the-bq21040-charger-swap-2026-11-04). Production
  files: §4 there.
