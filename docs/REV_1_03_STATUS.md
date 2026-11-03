# Rev 1.03 status: NEXT_REVISION items in the design files

**Branch:** `1.03`, cut from `master` at `4530931` (the Rev 1.02 files). **Written:** 2026-11-03.

**State in one line:** the schematic, board and part fields carry N1–N6 and N9. N7 and N8 are parked, N10 is
deliberately unchanged, and N11 was dropped. The changes are machine-checked (DRC with schematic parity, ERC, netlist
diff, Fabrication Toolkit dry run). Nobody has opened them in KiCad yet. Production files and docs are not
regenerated, and the title block still says Rev 1.02.

This is the hand-over note. It covers what changed, where it deviates from [NEXT_REVISION.md](NEXT_REVISION.md) and
why, what is parked, how it was checked, and what to do next.

## 1. What is on this branch

| File | Change |
|---|---|
| `silkscreen_pcb.kicad_sch` | `F3`, `F5`, `F6` added; `R42` became `F4`; `3V3` and `LDO_IN` labels split and renamed; `R6` = 10k |
| `silkscreen_pcb.kicad_pcb` | footprints, nets and copper as in section 2; zones refilled |
| `silkscreen_pcb.kicad_pro` | three Power net-class patterns for the new nets (`/LED_VIN`, `J6_3V3`, `EINK_3V3`); nothing else, the DRC exclusions are untouched |
| `fabrication/part_fields.csv` | one new PTC row; `R42` and `R6` moved to other rows |
| `docs/REV_1_03_STATUS.md` | this file |

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
| [N7](NEXT_REVISION.md#n7-dw01a-sense-resistor-r85) | Parked | No legal place for the resistor near `Q1` pin 3. Section 6. |
| [N8](NEXT_REVISION.md#n8-c34-from-22-nf-to-100-nf) | Parked with N7 | `C34` stays 2.2 nF; the doc makes N8 conditional on N7. |
| [N9](NEXT_REVISION.md#n9-r6-from-47k-to-10k) | Done | `R6` = 10k, RC0603FR-0710KL, `C25804`. The 4.7k line (`C23162`) is gone from `part_fields.csv`. |
| [N10](NEXT_REVISION.md#n10-move-c36-and-c37) | Left alone | Section 7. |
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
- `F5` and `F6` have no silkscreen outline and a hidden reference: `F5` sits on the B.Silkscreen cut-line marker (y 61.3–62.7)
  and `F6`'s reference collided with `C11`'s.

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

## 6. N7 and N8: parked, and why

**What was designed.** A 50 mΩ sense resistor from `Q1` pin 3 (new net `B-_SENSE`) to GND: two 0.1 Ω 1206 resistors in
parallel (`R85`, `R86`, Yageo RL1206FR-070R1L as the DigiKey part, UNI-ROYAL 1206W4F100LT5E `C25334` as the JLC Basic
part), with `R16` and `U5` unchanged and `C34` raised to 0.1 µF (`C14663`). The pair was chosen over the doc's single
68 mΩ part because both 68 mΩ candidates (`C52472`, `C327066`) show JLC stock 0 on jlcsearch while LCSC lists 2,400 and
4,720, and the pair needs no Extended fee. The schematic part was written and verified, then removed again so that
schematic and board agree. For reference: `R85` (54.61, 213.36) and `R86` (54.61, 205.74), both rotated 90°; the `Q1` pin 3
wire extended to (50.8, 213.36); a bus at x = 50.8 up to a local label `B-_SENSE` at (50.8, 200.66); a GND bus at x = 58.42
with `#PWR05` moved to (58.42, 213.36) (rot 90); junctions at (50.8, 213.36), (50.8, 205.74), (58.42, 213.36). `Q1`'s pin
row is only 4 mm above the section divider (y 217.4), which is why the pair is stacked horizontally.

**Why it is not on the board.** A search with the real board outline, 0.15–0.25 mm clearances and the other footprints'
courtyards found no legal spot for two 1206 or two 0805 resistors within 22 mm of `Q1` pin 3:

- The doc's pocket above-left of pin 3 ignores the `PWR_BUTTON` diagonal (83.08, 69.32) → (86.5, 65.9), the 3V3 trunk
  diagonal (82.93, 68.77) → (86.6, 65.1), the GND vias at (86.4, 68.8) and (88.5, 70.1), and the `UNUSED_GPIO_45` trace.
- The free band north-east of `Q1` (x 87–91, y 66.2–69) is inside `J5`'s courtyard (x 88.11–96.70, y 63.05–69.94), the
  battery plug area. A 1206 would fit there only by overlapping it (about (88.6–89.2, 67.2–67.4)).
- 0805 spots exist only far away, for example (86.4, 62.4) in the arm.

**Options.**

1. Re-lay the area by hand in KiCad: re-route `UNUSED_GPIO_45`/`46`, nudge the `B−` jog and the GND vias, or relocate
   `R56`/`C34`. Then re-apply the schematic block above.
2. A single 0805 50 mΩ part: UNI-ROYAL 0805W4F500MT5E (`C247602`, 250 mW, JLC stock about 286,000, Extended) or Panasonic
   ERJ-6BWFR050V (`C2075868`, 500 mW, about 17,700, Extended). Same sensing, less pulse margin, still needs a 3.3 × 1.4 mm pocket.
3. The same sensing with the resistor in the `B−` lead (`Q1` pin 1 instead of pin 3). It still needs a pocket of that size.

Whichever is chosen, N8 (`C34` = 0.1 µF) goes with it.

## 7. N10: left unchanged

`J7`'s courtyard is x 56.15–73.45, y 69.3–85.6, and its card slot opens at the board's north edge (y 67.5). The card
therefore inserts along y, and the insertion force bends the board about the x axis. `C36` (62.5, 86.7) and `C37` (62.3, 88.2)
already lie along x, parallel to the pad row, which is "the bending axis runs along their length". Rotating them 90° would
put them across it. Moving them 5 mm has no room: the rows below are the `R21`–`R26` resistors (y 89.9 and 91.8). If the
doc's axis assumption is right and rotation is wanted anyway, rotate both in place (`TP10` existed only in the dropped N11 plan).

## 8. Soft-termination and open-mode MLCCs (search of 2026-11-02)

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

- **Production files:** `production/` is still Rev 1.02. Regenerate with the Fabrication Toolkit after the layout is reviewed,
  edit `production/jlc_bom.csv` by hand (new PTC group, `R42` out, `R6` into the 10k group), check the new footprints in
  JLC's placement preview, and rebuild the layout and schematic PDFs.
- **Docs** ([NEXT_REVISION.md §5](NEXT_REVISION.md#5-documentation-to-update-with-the-implementation)): `HARDWARE.md` §3.2
  (`R6`, charge current), §5 (`C36`/`C37`, SD policy), §6 (`EINK_3V3`, e-paper PTC), §7 (frontlight PTC), §8 (touch PTC),
  §11 (`J6` pin 7 PTC, 20 mA budget, `CR2`); `fabrication/BOM.md`; the README counts and the `J6` pinout table; a status
  note in `NEXT_REVISION.md`. §3.3 (`Rs`, `C34`) waits for N7. The images in `docs/images` need re-rendering.
- **Revision label:** the title block, README and silkscreen still say Rev 1.02. The branch is named 1.03, so the bump is
  presumably wanted; the 2026-10-22 bump was a byte-exact edit of the `(date …)` and `(rev …)` title-block lines.
- **Firmware items F3–F7** in NEXT_REVISION §4 are untouched.
- **Pre-order measurements** from NEXT_REVISION §6 (frontlight PTC bench test, sense-resistor trial, the coincident-peak
  measurement) have not been done.

## 10. Review checklist in KiCad

1. Open `silkscreen_pcb.kicad_pro`. Tools → **Update PCB from Schematic** should have nothing to change, since parity DRC is clean.
2. Run DRC with "test for parity". Expect the baseline plus one `silk_over_copper` at (79.3, 61.4); that is the cut-line
   marker over `F5`'s pads and is cosmetic.
3. Look at the layout around `F3` (the two hop vias and the F.Cu `LDO_IN` run under `L2`), `F6` (pads, the two new routes
   and the moved GND via), and `F5`/`CR2` in the arm, including the narrow corridor at x = 100.63.
4. Refill all zones (B). The pours should not change.
5. Decide whether `F5` and `F6` need visible references. They were hidden to keep clear of the cut-line marker and `C11`.
6. Check `F3`–`F6` in JLC's placement preview when the files are regenerated.

## 11. Decisions needed

- **N7:** which of the options in section 6?
- **N10:** leave as is, or rotate anyway?
- **Revision label and docs:** bump to 1.03 now, and regenerate production files and docs next?
- **MLCCs:** is the 1 µF soft-termination option (Extended, about 7× the price) worth taking for the 1 µF group?

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
- NEXT_REVISION §3 N7 still describes the 68 mΩ part; the 50 mΩ pair and the `C327066` stock question belong in section 6 here
  or in that doc once N7 is decided.
