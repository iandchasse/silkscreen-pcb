# To-do list from the author's response (2026-09-20)

Built from what you wrote in `FINDINGS_TABLE_author_refute.md`. Your words are quoted where they were an instruction.
Nothing is committed. `git diff` shows every change; `git checkout -- <file>` undoes any of them.

## A. Done in this pass

| What | Your instruction | Files touched |
|---|---|---|
| **R14 → LCSC `C22939`** (JLC Basic, 11.7 k in stock, verified live; Yageo RC0603FR-072R2L stays the DigiKey-primary MPN) | BOM-01 "Valid - should be addressed" | `fabrication/part_fields.csv` → `silkscreen_pcb.kicad_sch` via your own `apply_part_fields.py --write` (1 field changed; backup `silkscreen_pcb.kicad_sch.pre-fields.bak`), `production/bom_JLC_upload_v4_optimized.csv`, `production/bom.csv`, `fabrication/BOM.md` (3 lines, incl. the wrong "no Basic 2.2 Ω exists") |
| **Duplicate-LCSC BOM bug fixed at the source** — it was two spellings of the same value. `C24`,`C31`: `100n` → `0.1u`; `C18`,`C19`: `1u` → `1u/50V`. A schematic-side BOM now groups `C14663` ×6 and `C28323` ×3 on one line each. | FAB-22 "Valid. Fix." / BOM-05 "will revise" | `silkscreen_pcb.kicad_sch` (4 Value properties), `fabrication/part_fields.csv` |
| **USB_STAT schematic note**: idle window `> 3.10 V` → `> 2.60 V` with the reason; fault line corrected to the re-evaluated logic | USB-01 "Sure, go with recommendation." | `silkscreen_pcb.kicad_sch` (note text; fits its frame — I rendered it to check) |
| **Front-light schematic note**: added the ≥ 40 µs enable pulse, the 2.5 ms shutdown time, the three-trip OVP latch and "change COLOR_SEL at duty 0 / never enable with J3 unplugged" | LED-14 "Can put in for instruction in firmware", LED-V02 "should be documented" | `silkscreen_pcb.kicad_sch` (text box enlarged to fit) |
| **README rewritten** for a first-time builder, JLCPCB-only, one BOM file, glossary, firmware status, what-else-you-need, battery lead order + one warning callout, cost/lead time, THT as a costed choice, licence in plain words, 5 bare / 2 assembled, KiCad not required, tweezers-BOOT, pin-hole RESET, cutting-down procedure, D2 polarity fixed. 0 broken links. | DOCS-01…07, -09…-18, -24, MCU-01, MEC-09, MEC-V02, LAY-02 | `README.md`, `fabrication/README.md` — change log: `responses/README_CHANGES.md` |
| **HARDWARE.md**: GPIO46 "input-only" corrected (3 places); charge current "≈ 0.23–0.25 A, measure it"; EPD loop area 20–27 mm²; front-button tab gap now gives **both** numbers you asked for; new **§13.1 Firmware contract** (USB_STAT decoding, ADIM enable, OVP latch recovery, colour-select, SD bus parking, wake sources, dead-pack / post-trip behaviour) | MCU-19, HMI-13/LAY-07/LAY-D1, USB-02/V02, SD-01 … | `docs/HARDWARE.md` — change log: `responses/HARDWARE_CHANGES.md` |
| **Board STEP model** for case designers (7.7 MB, DNP parts omitted, every 3D model resolved) | DOCS-07 "The board's STEP file should be available to everyone" | `docs/mechanical/silkscreen_pcb.step` |
| **Review corrected**: LED-01 withdrawn everywhere; FAB-23, LAY-V01, PWR-14 withdrawn; 12 MEDIUMs downgraded after re-evaluation; DRC counts reconciled | the refutation file's header | `FINAL_REVIEW.md`, `AUTHOR_RESPONSE_EVALUATION.md`, `REMAINING_PRUNED.md` |

## B. Yours — needs the KiCad GUI

1. **Open the schematic, then *Update PCB from Schematic* with "Update footprint fields" ticked.** This carries R14's new LCSC code and the four normalised Values onto the footprints. Until you do, the PCB (and anything the Fabrication Toolkit generates from it) still has the old R14 code. Then re-run the Fabrication Toolkit and check `production/bom.csv` now has one line per LCSC code.
2. **Replace the four 0.5 mm perforation slots with one wide slot** — "I will remove these slots in favor of one wide slot" (LAY-01 / DOCS-18 / FAB-23 / MEC-03). Make it ≥ 1.0 mm and draw it with the same 0.05 mm Edge.Cuts line as the rest of the outline (the five cut-outs are currently drawn at 0.20 mm). Afterwards: regenerate `production/`, and shorten the README's slot caution (it is worded for the current files).
3. **Silkscreen disclaimer at the cut line** — "I will add disclaimer. No keepout." (MEC-02). Suggested text: `DISCONNECT BATTERY BEFORE CUTTING`. While you are in that text box: it is mirrored on the front silk and overhangs the edge by 3 mm (LAY-13).
4. **USB input path width** — "Worth a look. Valid." (USB-06). `USB_VBUS` / fused VBUS are 0.25 mm; the battery path is 0.40 mm. Same pass, if you like: the two 0.25 mm links either side of R27 that the earlier widening missed (BAT-07 / PWR-V01), and pours instead of 0.25 mm tracks on U3's IN / OUT / GND pins (that copper is the whole difference between TI's 231 °C/W and 100 °C/W — PWR-01).
5. **Change the GitHub link** — "I should probably change the github link, valid." (DOCS-08). It is on the board silkscreen/QR, in `NOTICE`, and in comment 4 of both title blocks; or simply make `06_2026` the repo's default branch.
6. **At order time, in JLC's placement preview** (FAB-21 "Valid. Fine fix.", MEC-V01): check rotation/position of **U2, U10, D8, U12, J4**, the diodes and D2. If any is off, add `FT Rotation Offset` / `FT Position Offset` fields to that symbol so the correction sticks.

## C. Yours — decisions still open (my recommendation in brackets)

| Item | Decision | |
|---|---|---|
| HMI-01 | PPTC in series with J6 pin 12 (raw battery +)? It does **not** help hot-plug; it turns a shorted accessory from a hot wire into a click-off. | [Fit it if anyone but you will use J6. **Littelfuse 0805L075WR** (LCSC C151146) — same family and 0805 land as F1, 0.09–0.35 Ω. §5.] |
| BOM-07 | Replace the DS3231MZ? | [**Yes, next revision: Micro Crystal RV-8263-C7** — integrated crystal, $1.64 vs $13.85 at DigiKey (≈ 99 k in stock), LCSC C5137460, 0.24 µA vs ~3 µA, ±20 ppm; KiCad 9 already ships the footprint (`Package_SON:MicroCrystal_C7_SON-8_1.5x3.2mm_P0.9mm`). Not a drop-in — ~1 h of layout. RV-3032-C7 (TCXO, ≈ $3.24) on the same outline if you want DS3231-class accuracy. The SOIC-8 "drop-ins" all fail your rules (wide-body, or need a crystal). Verify pin functions across the C7 family before relying on it as a second source. Caveat I checked live: JLC holds only 472 of them today (Extended), so your 'well stocked at both' rule is met at DigiKey but only thinly at JLC. `responses/PARTS_RESEARCH.md` §1.] |
| BOM-V01 | Cheaper ESD arrays in some of the five positions? | [**Keep the TPD4E1U06.** Every credible SRV05-4 costs *more* at DigiKey ($1.23–1.88 vs $0.94), and on this board pads 5 and 6 are tied together on all five arrays, so an SRV05-4 (pin 5 = VCC) is not a drop-in. The real saving is the qty-100 price break. Your instinct was right. §2.] |
| BOM-06 | D8 PESD2IVN-UX is NRND | [**Keep it for now** — NRND but ≈ 16.5 k in stock at DigiKey. The true drop-in, PESD2IVN27-UX (Active, same SOT-323 and pinout), is at zero until mid-2027. Do **not** use a 24 V-rated part: the LED driver's OVP is 24–25.5 V. I checked D8's pinout against Nexperia's table — the board is wired correctly. Add a one-line BOM note. §3.] |
| BOM-02 | 22 µF for C4/C6/C32 is obsolete at DigiKey | [**Murata GRM21BR61E226ME44L** (0805, 25 V, ≈ 1.75 M in stock, $0.36, LCSC C86816; 0.05 mm taller). Only matters for a DigiKey hand-build. Separately: the JLC code in use is a CCTC clone `C20416420` (Extended); the Samsung original is `C45783` and is JLC **Basic** with 1.7 M in stock (verified live), while the clone is down to **396 pcs** — switching saves a loading fee and removes a stock risk, at +$0.25/board. Say the word and I will change it through `part_fields.csv` like R14. §4.] |
| 17 short ones | The only LOW/DOC rows that still want a word from you | [`REMAINING_PRUNED.md`, first table. Most are "skip" / "later".] |

## D. Yours — facts only you have

- **Known-good battery link** — README has the visible placeholder `TODO(author): link to a known-good pack` (DOCS-04 / BAT-V04).
- **Configurator go-live** — README says "not live yet"; soften it when silkscreenreader.com leaves preview (DOCS-02).
- **Firmware + first-power-up section** — "will be provided later after firmware work is done" (DOCS-12).
- **Battery-ejection / SD-card sentence** — "instructions for battery ejection will be documented" (HMI-V02); the docs also never say the battery must move before the card comes out (SD-V03).
- **Confirm the cost box** in the README against your next real quote (it is the review's 2026-09 cost model: ≈ $230–260 for five assembled, 2–3 weeks).
- **HMI-17 / SD-04 one-liner** — you suggested "a one-line note in the BOM" that prime MPN ≠ LCSC maker is deliberate (J7, the switches, F1).

## E. Yours — repo housekeeping (I did not delete anything)

- `production/bom_JLC_upload_v3.csv` — "v3 irrelevant. There should be 1 BOM" (FAB-10).
- `production/other_fabs/` — "other_fabs folder will be deleted, as the other fabs suck" (DOCS-13). Goes with it: the other-fab half of `fabrication/make_fab_files.py`, `fabrication/NEXTPCB_REV0_NOTES.md`, `fabrication/nextpcb_substitutes.csv`, and the matching paragraphs in `fabrication/README.md`. The README no longer mentions any of them.
- `DESIGN_REVIEW.md` — still says "GPIO46 is input-only" (line 288) and analyses Q3/Q8 as AO3419 (lines 164, 229, 237, 247) while line 201 says AO3401A. I left it alone as a historical document; say the word and I will fix those five spots.
- Next revision: *exclude from BOM* on R72, R74, SW6 (HMI-V01 "valid hardening … for the next revision").
- `silkscreen_pcb.kicad_sch.pre-fields.bak` was refreshed by `apply_part_fields.py`; it is untracked noise.

## F. Bring-up checks (when boards arrive) — from your answers

- Battery only, no cable: `USB_VBUS` ≈ 0 V and D2 dark; then deep-sleep current against the ≈ 73 µA budget (PWR-06 / PWR-V02 / PWR-07 "both modules' sleep modes taken advantage of").
- Measure the real charge current (≈ 0.23–0.25 A expected).
- Diode-test J3 against the front-light flex before first enable (LED-12).
- Scope the LED boost through a colour change at a few duties — no OVP trip (REC-C-01).
- Pull the cell while on USB and watch `USB_STAT` alternate ≈ 0.59 / 0.45 V — note the real period for the firmware (the 1–4 s figure is from the TP4056 datasheet, not measured).

## G. Things I can still do if you say so

- Fix the five stale spots in `DESIGN_REVIEW.md`.
- The ~30 no-decision clean-ups in `REMAINING_PRUNED.md` that are text/field edits (HARDWARE.md one-liners, symbol Description/Datasheet fields for Q4, Q7, D4–D6, CR1; the D2 schematic note; the duplicate `PIN_3`/`TP_RST` label).
- Set *exclude from BOM* on R72 / R74 / SW6 now rather than next revision (it would drop their no-part-number lines from BOM exports, which you currently list on purpose — so I left it).
- Delete `other_fabs` and strip the generator script, once you confirm.

---

# Round 3 — 2026-09-21 (KiCad was closed; edits made directly and verified)

Verification after all edits: ERC **0 errors**; DRC **0 unconnected, 0 schematic-parity issues**, only the J1 land-pattern clearance items remain; all four QR codes decode from the *plotted* F.Silkscreen layer.

## Done

| What | Where |
|---|---|
| **GitHub QR code replaced in place** — it pointed at `https://github.com/iandchasse/de-link`; now `https://github.com/iandchasse/silkscreen-pcb`. Same footprint, position, 7.86 mm size and 29 × 29 modules (0.271 mm) as its siblings, EC level L (your website code is also L; level M would need 33 modules = smaller dots). Tool: `evidence/tools/swap_github_qr.py`. | `silkscreen_pcb.kicad_pcb` |
| **U14 (RV-8263-C7) fixed.** Your custom symbol had CLKOE numbered **8** (duplicate of SDA) instead of **3** → ERC error, and pad 3 had no net, so CLKOE floated (CLKOUT may free-run at 32.768 kHz — defeats the 190 nA part). Now: CLKOE = pin 3, NC flag removed, wired to GND; PCB pad 3 = GND with a 0.9 mm B.Cu link to pad 2; symbol saved as its own library `KiCad/9.0/3rdparty/RV-8263-C7/RV-8263-C7.kicad_sym`, registered in `sym-lib-table`, U14 re-pointed at it (it was shadowing the stock `Timer_RTC:RV-3028-C7`, which an "update symbols from library" would have silently restored). MPN / Manufacturer / LCSC `C5137460` added, DNP. Full report: `responses/RTC_U14_CHECK.md`. | `.kicad_sch`, `.kicad_pcb`, `sym-lib-table`, `part_fields.csv` |
| **R15 10 k → 1 M** (Good Display datasheet §8.2 reference circuit shows R1 = 1 M on GDR — I looked at the drawing). Joins the existing 1 M BOM line. | sch + pcb + all BOM files |
| **C2 → 25 V** Samsung CL10A106MA8NRNC, LCSC `C96446`, JLC Basic, 2.8 M in stock. Value shown as `10u/25V`; C3 stays the 10 V part. | sch + pcb + all BOM files |
| **C4/C6/C32 22 µF**: prime MPN → Murata GRM21BR61E226ME44L; LCSC → `C45783` (Samsung, JLC Basic, 1.7 M). Note in `BOM.md`: the old CCTC clone is only cheaper above ~12 boards. | sch + pcb + all BOM files |
| **D2 schematic note**: "2.5mA" → "1.5mA" (its own arithmetic and R59 = 2 k give 1.5 mA). | `.kicad_sch` |
| **47 doc edits**, one line each in `responses/DOC_CLEANUP_CHANGES.md`. | `README.md`, `docs/HARDWARE.md`, `fabrication/README.md` |
| **STEP re-exported** with the new slot. | `docs/mechanical/` |

## Still yours

1. **Re-run the Fabrication Toolkit** — `production/` gerbers/positions predate the new slot, the disclaimer, the QR code and U14. (I edited the BOM CSVs by hand so they are right today, but the zip and `positions.csv` are stale.)
2. **F2 (PPTC)** — copy F1's symbol, value `0805L075WR`, same 0805 footprint, **in series with J6 pin 12 only** (see chat). Tell me the ref when placed and I will add its `part_fields.csv` row. HARDWARE.md already says "PPTC-fused" inside `<!-- confirm once F2 is on the board -->` markers — remove the markers or the sentence.
3. **USB path widening (your item 4)** — optional; my advice is to skip all widening this spin (numbers in chat).
4. **Part counts** — "179 references = 162 fitted + 10 DNP + 7 bare-copper" in `README.md` and `fabrication/README.md` is stale once U14 (DNP) and F2 (fitted) are in. Tell me when F2 is placed and I will recount.
5. **Two leftover "LED current" numbers in KiCad text**: schematic note says "~14mA", front silkscreen says "at least 15mA"; the real set-point is 13.3 mA.
6. **Sleep-current option** (PWR-03 / USB-08) — explained in chat; say "do it" and I will apply it everywhere.
7. `simulations/led_driver` models the old discrete boost — delete it or let me add a one-line "historical" README.
8. `de-link.me` is still linked (correctly, as the predecessor) in README and HARDWARE.md — remove if that domain is going away.

---

# Round 4/5 — 2026-09-21 (after F2, H6, R83, C34 and the C7 move were placed in the GUI)

## Done

| What | Where |
|---|---|
| **Removed a leftover `P+` copper branch** (4 B.Cu segments + the via at 89.374, 74.6) that ran straight into `U5` pad 5 and shorted across the new `R83`. DRC had flagged it as `shorting_items`. | `silkscreen_pcb.kicad_pcb` |
| **`F2`** value/MPN/LCSC → `0805L075WR` / Littelfuse / `C151146` (0.75 A hold, 1.5 A trip, 6 V). | sch, pcb, `part_fields.csv`, all BOMs |
| **`R83`** fields corrected — it carried the 10 k part number (`RC0603FR-0710KL` / `C25804`); now the 100 Ω part `RC0603FR-07100RL` / `C22775`. | sch, pcb, `part_fields.csv`, all BOMs |
| **`USB_STAT` ladder rescaled ×10** for sleep current: `R70` 100k→1M (`C22935`), `R17` 150k→2M (`C22976`), `R67` 56k→510k (`C23192`), `R71` 22k→200k (`C25811`), `C23` 2.2n→0.1u (`C14663`). All JLC Basic, all checked live. 13.2 µA → 1.1 µA on battery. | sch, pcb, BOMs |
| **`R57`** 1M → 10M (`C7250`, Basic): `Q3` gate-bleed drain ≈3.7 → 0.4 µA, permanently off the cell. | sch, pcb, BOMs |
| **`PWR_FLAG` (#FLG05) on `Net-(U5-VCC)`** — with `R83` in the way ERC reported "power pin not driven" on `U5` pin 5. ERC is back to 0 errors. | sch |
| Schematic notes: USB_STAT note rewritten with the new levels/windows and the current draw; "2.2n cap placed near ESP32" → "0.1u" beside the ladder. Rendered and checked — both fit their frames. | sch |
| BOM CSVs: `R83`, `F2`, `C34`, new ladder values, `U14` DNP line; comments aligned with schematic values (`1u/50V`, `47uH`). **Cross-check script: every fitted ref's value + LCSC code matches the schematic in both CSVs, and all 184 PCB footprints match the schematic's Value/MPN/LCSC (0 mismatches).** | `production/*.csv`, `fabrication/BOM.md`, `BOM_handbuild_digikey.csv` |
| HARDWARE.md: §3.3 (R83/C7 filter, C34, R57, standing drain ≈10 → ≈7 µA), §3.7 (new ladder table), §13.1 (new decode windows + "slow, high-impedance node, no internal pulls"), §16 (sleep floor ~75 → ~60 µA; six holes; screw-head rule; H5/H6 coordinates), CR3 now on `/P+_FUSE`, appendix counts. README + fabrication README counts: **184 references = 165 fitted + 11 DNP + 8 bare-copper, 134 nets**. | docs |
| Five schematic screenshots regenerated at the same 400 dpi crop style. | `docs/images/05, 16, 16b, 17, 19` |
| STEP re-exported (H5 move, H6, F2, R83, C34). | `docs/mechanical/` |

Final state: ERC 0 errors (41 warnings, all the known kinds); DRC 0 unconnected, 0 parity, no shorts; the only un-excluded errors are the 9–13 `J1` USB-C pad-to-pad clearances that have always been there.

## Still yours

1. **Re-run the Fabrication Toolkit before ordering.** `production/` gerbers, drill and `positions.csv` predate the slot, the disclaimer, the QR code, `U14`, `F2`, `C34`, `H6`, `R83` and the moved `H5`. The BOM CSVs are right today; the Toolkit will regenerate `bom.csv` anyway. Then check `R83`, `C34`, `F2` and `C7` in JLC's placement preview.
2. Open the schematic once and look at the new `PWR_FLAG` next to `U5` pin 5 — move its label if you dislike where I put it.
3. Firmware: the `USB_STAT` thresholds in HARDWARE.md §13.1 are the contract now (idle > 2.6 V, battery 1.80–2.60, charging 0.80–1.35, done 0.35–0.70 *and stable*); sample ≤ 1 Hz, internal pulls off.
4. Unchanged from round 3: LED-current wording in the schematic note ("~14mA") and front silkscreen ("at least 15mA") vs the real 13.3 mA; `simulations/led_driver`; `de-link.me` links; stale spots in `DESIGN_REVIEW.md`; `bom_JLC_upload_v3.csv` and `production/other_fabs/` do **not** carry this round's changes (delete or tell me to update them).

---

# Round 6 — 2026-09-21 (after the Fabrication Toolkit re-run)

## Done

| What | Where |
|---|---|
| **Regenerated fab outputs verified.** Gerber zip vs a fresh `kicad-cli` export of the saved board: identical coordinate operations on `B.Cu`, `F.Cu`, `B.Mask`, `B.Paste`, `F.Silkscreen`, `Edge.Cuts`; 5.30 × 1.10 mm slot present; six 2.2 mm mounting holes in the PTH drill; 36 drawn paste regions (FPC connectors). `positions.csv` = 165 rows = every fitted part. Toolkit `bom.csv` matches the schematic on every value and LCSC code, and agrees with the upload BOM. | `production/` |
| **`bom_JLC_upload_v4_optimized.csv` → `jlc_bom.csv`**; `bom_JLC_upload_v3.csv` deleted; every live reference updated (README, fabrication/README, BOM.md, NEXTPCB notes, DESIGN_REVIEW). Historical audit folders still use the old names, on purpose. | `production/`, docs |
| **Other-fab files regenerated** with `python fabrication/make_fab_files.py --split` — they were two days stale (no F2/R83/C34, old ladder values, old H5). 165 placed parts. | `production/other_fabs/` |
| README + fabrication/README now say plainly: other factories are supported (files kept current), only JLCPCB has produced working boards, the NextPCB attempt did not end in a successful order, PCBWay is untried, and the choice is the builder's. | docs |
| `simulations/` removed from the README's folder listing. `de-link.me` links left as they are. | README |
| Schematic PDF, full-sheet capture, both board renders and seven more block screenshots (USB input, charger, MCU, e-paper, LED driver, boot buttons, RTC) regenerated from the current files. The old bottom render still showed the four perforation slots. | `docs/` |
| DESIGN_REVIEW.md: "GPIO46 is input-only" corrected (that is an ESP32-classic rule, not S3); AO3419 section marked as written before the AO3401A swap. BOM.md: hand-build parts cost now says "budget ≈ $66", not ≈ $48. | docs |

## Still yours

1. `docs/silkscreen_pcb_layout.pdf` is from 2026-09-18 — it is a GUI plot (File → Plot → PDF, two pages), so re-plot it when convenient.
2. Optional, both "margin, not failure": widen the `USB_VBUS` trunk 0.25 → 0.40 mm (done 2026-09-21: fuse → TPS2116 is now 0.40 mm. Correction: the "0.9 A worst case" I quoted was wrong — `R6` = 4.7 k sets the charge current to ≈0.25 A, so the real worst case is ≈0.55 A and the old 0.25 mm trace was only a few °C warm), and nudge the four TP4056 thermal-pad vias out from under the paste windows (REC-B-02).
3. Cosmetic symbol fields (`Q4`, `Q7`, `D4`–`D6`, `CR1` descriptions/datasheets) and the doubled `PIN_3`/`TP_RST` label.
4. At order time: JLC placement preview for `R83`, `C34`, `F2`, `C7`, `U12`; F2 (`C151146`) is an Extended part with ~1.9 k in stock — check it is still there.

---

# Round 7 — 2026-09-21 (repo cleanliness mini-audit and its fixes)

Report: `repo_hygiene/REPO_HYGIENE_AUDIT.md` (83 findings: 54 confirmed, 28 adjusted, 1 refuted).

## Done

| What | Where |
|---|---|
| 47 doc-level findings fixed (U14 missing from three DNP lists incl. README Step 5; the "production/ is out of date" contradiction; R14's retired `C112307`; five-vs-six mounting holes; 50 V cap count; C2 in the 0805 table; cut-line consequences; NextPCB counts; dead `.gitignore` lines; layout PDF re-plotted as front + back). | README, HARDWARE.md, fabrication/*.md, DESIGN_REVIEW.md, .gitignore |
| **KiCad tidy (text-level, KiCad closed; `evidence/tools/r9_kicad_tidy.py`):** `Sim.*` properties carrying a local Windows path to `irlml6402.spi` removed from Q2/Q3/Q7/Q8 (sch + pcb); Description/Datasheet corrected on Q2 Q3 Q7 Q8 (AO3401A), Q4 (IRLML6346), D4–D6 (1N5819HW), CR1–CR3, U1/U6–U9, J2–J4, J6, J7, Q1 — every URL checked live; silkscreen display part number → `GDEQ0426T82-FT01C` (3 places) and welcome text `SW1-SW8` → `SW1-SW5 and SW7-SW9`; the frontlight label nudged 0.2 mm so the longer name clears U13 pad 4's mask opening; the Q8 note now names the EEVblog thread and its link points at the real URL; TPD4E1U06DBVR symbol's default footprint fixed (library + cached copy); two stale ERC exclusions (L1, L2) removed — the third (Q1) turned out to be live and was kept; last STEP path no longer "delink". | sch, pcb, pro, `KiCad/9.0/3rdparty/TPD4E1U06DBVR` |
| Verified after the edits: nets and value/footprint of all 184 parts **identical** before/after; ERC 0 errors, same 41 warnings; DRC 0 unconnected / 0 parity, only the J1 clearances; silkscreen re-rendered and inspected (Roboto is installed; the stale glyph caches of the three edited texts were dropped so KiCad rebuilds them on the next save). | — |
| Owner's decisions applied: battery link + charge-rate note; real cost quote ($223.95, $305.23 at checkout, two assembled); **Rev 1.0 stays** — one explicit statement in README and HARDWARE.md; DESIGN_REVIEW.md status banner (+ R57 note); BOM.md cost-table note; `evidence/`, raw agent output, `*.json` and `placement/` git-ignored; final-review reports listed in the README; three local paths and two broken links inside the review reports cleaned; local path scrubbed from `docs/audit-2026-09-16/netlist.xml`. | docs, .gitignore |
| `KiCad/de-link just parts.ods` removed: it is the BOM of the old de-link prototype (AP2112K, AP3012, MCP73832, DM3AT…). Its still-relevant alternates (S2B-PH-K-S / A2001WR-2P, SKHLLAA010 / TS365ZJ, A2541HWR-2x6P, SD05C) are all already in `part_fields.csv`, `nextpcb_substitutes.csv` or BOM.md. Restore with `git checkout -- "KiCad/de-link just parts.ods"` if wanted. | — |
| Regenerated from the edited design: schematic PDF, full-sheet capture, battery-protection screenshot, layout PDF, both board renders, STEP (H6 now at 69.200, 117.500). | docs/ |

## Still yours

1. **Open the PCB once, save, and re-run the Fabrication Toolkit** — the silkscreen text changed, so the gerber zip is stale again (and saving rebuilds the text glyph caches). Then tell me and I will re-verify the zip against the board.
2. Delete the stray `placement/` folder yourself (it is git-ignored now, so it cannot be committed by accident).
3. Deliberately left alone (cosmetic, your call): mixed capacitor value formats (`4.7u` vs `4.7u/50V`), `CR` vs `D` designators for TVS parts, the unused vendored `MJTP1117.kicad_sym`, three spellings of "frontlight", dated change-log parentheticals in HARDWARE.md's appendix tables, the bulky intermediates inside `docs/audit-2026-09-16/`.
