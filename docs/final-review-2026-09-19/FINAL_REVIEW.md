# Silkscreen Reader PCB — final review

Review date 2026-09-19/20 · design at commit `c0eccde` (branch `06_2026`) · KiCad 9.0.6 · nothing in this folder is committed.

> **Revision 2 — 2026-09-20, after the author's response.** The review's only BLOCKER (LED-01, "no solder paste on the FPC connectors") was **wrong and is withdrawn**: the Hirose footprints draw their paste as 36 graphic polygons on the paste layer, which the pad-layer and aperture-flash checks used by the auditor, the verifier *and my own re-check* cannot see. Paste is present on every signal pad. **There is now no blocker.** Every answer the author gave is evaluated in [`AUTHOR_RESPONSE_EVALUATION.md`](AUTHOR_RESPONSE_EVALUATION.md); what is left for him is in [`AUTHOR_TODO.md`](AUTHOR_TODO.md); the not-yet-answered LOW/DOC/CERT rows are pruned in [`REMAINING_PRUNED.md`](REMAINING_PRUNED.md). See [§11](#11-author-response-and-re-evaluation-2026-09-20).

This is an independent, from-scratch review of the schematic, layout, BOM, manufacturing outputs, mechanics and
documentation. It was done **blind**: no reviewer was allowed to read `DESIGN_REVIEW.md` or `docs/audit-*` until the
whole audit was finished. Those earlier audits were only opened afterwards, for the comparison in
[§9](#9-comparison-with-the-earlier-audits).

Severity is calibrated to what you asked for: a **prototype spin**. Routing purity, matched pairs and EMC are not counted
as problems; they are parked under `CERT-LATER` for the day you pursue FCC/CE/UL.

| Where to look | What it is |
|---|---|
| this file | verdict, the short list that matters, numbers worth knowing, comparison with earlier audits |
| [`FINDINGS_TABLE.md`](FINDINGS_TABLE.md) | all 297 findings in one table with verifier verdicts |
| [`sections/`](sections/) | 13 report sections — one per schematic block group / discipline, each with walk-through, calculations, findings, "checked and found OK", documentation cross-check, sources, verification log |
| [`comparison/`](comparison/) | new audit vs each body of earlier audit work |
| `evidence/` | the ground-truth pack everything was derived from, plus the scripts that made it — about 38 MB, kept locally and git-ignored, so it is not in a clone |

---

## 1. Verdict

**Revision 2: no blocker remains. Nothing electrical is wrong, and nothing in the manufacturing data will produce a dead board.** ~~Do not place the assembly order yet~~ — that sentence rested on LED-01, which was a reviewer error (see the banner above). What is left is the R14 stock swap (done in this pass), your own planned outline change (one slot instead of four), and documentation.

Across the eight circuit blocks (USB/power-path, charger/protection, LDO, ESP32, microSD, e-paper, front-light,
buttons/RTC/touch/expansion) the review found **no electrical blocker and no electrical HIGH**. Pinouts were checked
against manufacturer datasheets part by part, the 24-pin panel connector was checked pad by pad against the
GDEQ0426T82 datasheet, the FS8205A/DW01A, TPS2116, TPS923610 and TLV75533 circuits match their reference designs, all
five analog nets are on ADC1, the octal-PSRAM pins are left alone, and the antenna cut-out is textbook.

~~What stands between you and an order is one manufacturing-data defect that guarantees a dead board from a PCBA house~~ *(withdrawn)*. What remains: a few board-outline/mechanical decisions (most of which the author has since answered as deliberate), a BOM stock problem (fixed), and documentation gaps that would stop a replicator (being fixed). Totals after verification **and after the author's response**:

| BLOCKER | HIGH | MEDIUM | LOW | DOC | CERT-LATER | refuted by verifiers |
|---|---|---|---|---|---|---|
| ~~1~~ **0** | 16 → see §11 | 70 → see §11 | 150 | 37 | 17 | 6 + LED-01, FAB-23, LAY-V01, PWR-14 withdrawn in rev 2 |

Plus 22 items **recovered from the earlier audits** after the blind phase (4 distinct MEDIUM, 14 LOW, 2 DOC,
1 CERT-LATER) — see [§9.2](#92-recovered--real-items-earlier-audits-had-that-the-new-audit-dropped).

---

## 2. Fix before ordering

Ranked. "Effort" assumes you are in KiCad already.

| # | What | Why it matters | Fix | Effort | IDs |
|---|---|---|---|---|---|
| ~~1~~ | **WITHDRAWN — reviewer error. Paste IS present** (36 polygons, 0.25 × 0.65 mm, one centred on every signal pad; ≈ 47 % of pad area, a sensible reduction for 0.5 mm pitch). **Do not apply the "fix" in this row** — a full-pad aperture on top of the polygons would invite bridging. Original text kept for the record: ~~The three Hirose FPC connectors (J2 24-pin panel, J3 front-light, J4 touch) have no solder paste on any signal pad~~ — 36 pads. Only the two anchor tabs get paste. | The stencil will have no apertures there, so a fab-assembled board comes back with the display, front-light and touch connectors held on by their tabs and **no signal pin soldered**. Confirmed three ways: pad layer sets read with `pcbnew`, zero flashes on the pad row in the production `B_Paste` gerber, and the cause traced to the vendor footprints in `KiCad/9.0/3rdparty/FH34SRJ_*/*.kicad_mod` (signal pads are `F.Cu F.Mask` only). | Add `F.Paste` to pads 1–N in both library footprints, *Update footprints from library*, re-export, and confirm flashes now appear on the connector rows of `B_Paste`. Because the defect is in the library it will silently come back on any re-import unless fixed there. | 10 min | LED-01 |
| 2 | **Four perforation slots at the tongue neck are 0.516 mm wide** (measured on the Edge.Cuts centre-line; they are also drawn with a 0.20 mm line where the rest of the outline is 0.05 mm, so the intended edge is ambiguous). *Already known to you: the README documents it and notes JLC accepted earlier orders with them — so this is an accepted risk at JLC, not a surprise. It is ranked here because it is a 15-minute fix and the other fabs you now document have not been tried.* | JLCPCB's published minimum for non-plated routed slots is 1.0 mm. Possible silent outcomes at a new fab: widened, or not cut at all. | Widen to ≥ 1.0 mm (or replace with mouse-bites), redraw all five internal cut-outs at 0.05 mm line width. If you leave them, ask NextPCB/PCBWay explicitly. | 15 min | LAY-01, FAB-23, MEC-03 |
| 3 | **The silkscreened "cut here for smaller displays" line crosses raw battery positive** (`P+`, 0.40 mm F.Cu track at x = 89.39) with ground pour 0.15–0.20 mm away on both layers; 12 live nets cross it; 57 % of the neck is solid FR-4 so it cannot be snapped, only sawn. The cut also removes the PWR button (SW10), not just the expansion header. | Sawing smears copper across the cut face. A smeared short on a connected LiPo is a fire, not an inconvenience. | Minimum: silkscreen "DISCONNECT BATTERY BEFORE CUTTING". Better: a ~2 mm copper keep-out band on the cut line and route `P+` so it does not cross it. Document that cutting removes SW10. | 5–30 min | MEC-02, MEC-V02, LAY-02, HMI-V02 |
| 4 | **Raw LiPo `P+` is on expansion header J6 pin 12 with no fuse/PTC.** The DW01A is the only protection and it is a threshold trip in the negative lead, not a fuse curve. | A sustained 1–2 A accessory fault can sit under the trip point and cook a wire. Also: anything that *drives* that pin reaches the cell through Q3's body diode, bypassing the reverse-battery CE gate. | 0.5–1 A PPTC (1206) in series with pin 12, plus a `BAT+` silkscreen warning; document the pin as output-only. | 20 min | HMI-01, BAT-04 |
| 5 | **R14 (2.2 Ω, the e-paper boost sense resistor) — its LCSC code C112307 fell from ~94,900 to 12 in stock in two days.** Without R14 the panel's gate rails do not exist. | The order will stall or the part will be substituted. | Change the LCSC field to **C22939** (0603WAF220KT5E, 2.2 Ω 1 %, JLC *Basic*, ~11.7 k in stock, half the price, saves an Extended fee). Keep the Yageo MPN as the DigiKey-primary part. Correct the "no Basic 2.2 Ω exists" line in `fabrication/BOM.md`. Also re-check the two other thin lines before paying: the 22 µF MPN for C4/C6/C32 (obsolete, zero at DigiKey) and U10 (78 pcs at JLC). | 10 min | BOM-01, BOM-02, BOM-03 |
| 6 | **Make exactly one BOM the upload file.** `production/bom.csv` and `bom_JLC_upload_v3.csv` still carry the duplicate-LCSC-code lines (C28323, C14663) that left parts unmatched at JLC before; only `v4_optimized` is clean — and `bom.csv` regenerates the bug. Separately, `R74` (which **shorts 3V3 to GND** if fitted alongside R73) and `R72` are flagged DNP but *not* exclude-from-BOM, so they appear in the v4 upload as no-part-number lines; today only their absence from `positions.csv` keeps them off the board. | One wrong file choice = unmatched parts; one over-helpful BOM importer = dead short. You already saw this with NextPCB's importer. | Delete or clearly archive `v3`; fix the generator so `bom.csv` merges duplicate codes; set *exclude from BOM* on R72/R74 (as the touch-mux alternates already are); name the single upload file in the README. | 20 min | FAB-10, FAB-22, BOM-05, DOCS-03, HMI-07, HMI-V01 |
| 7 | **Mechanical decisions that are cheap now and a respin later** — see [§4](#4-physical-layout-enclosure-and-cable-routing). The flex slot width, the through-hole leads under the panel, and the microSD corridor through the battery bay. | They decide whether the display sits flat, whether the flexes survive, and which batteries fit. | Decide each before releasing gerbers. | — | MEC-01, MEC-06, MEC-23, SD-V01, SD-05, MEC-04 |
| 8 | **Public-facing documentation** — the URL printed on the board lands on the *old* project's default branch; no firmware is linked; no LiPo safety warning; no "what else to buy" list; the README's "recommended" ordering route is a configurator that is not live. | A replicator cannot currently get from the board's QR code to a working device. See [§6](#6-documentation-and-replicability). | — | 1–2 h | DOCS-01…09 |

---

## 3. Block by block

Each row links to the full section. Counts are B/H/M/L after verification.

| § | Block | Health | B/H/M/L | The things to know |
|---|---|---|---|---|
| [01](sections/01_usb_input_power_path.md) | USB-C inlet, ESD, TPS2116 power-path, USB/charge status ADC | Sound | 0/0/8/8 | Connector map, CC pull-downs, ESD array, mux priority strap all correct. **USB_STAT ladder:** the "> 3.10 V charger idle" window is beyond the ESP32-S3 ADC's specified 0–2.9 V range, and "fully charged" is *by construction* the same voltage as the no-battery oscillation high — firmware must not trust those two states (USB-01/02/V02). F1's 1.0 A hold is thin against ~0.86 A worst case and derates with heat; USB path is 0.25 mm while the battery path was widened to 0.40 mm. |
| [02](sections/02_battery_charger_protection.md) | TP4056, DW01A + FS8205A, reverse-battery PFETs + CE gate, J5, battery monitor | Good | 0/0/3/10 | Reverse-insertion was walked through semiconductor by semiconductor: only the DW01A ends up outside abs-max, at leakage current. Cheap robustness adds: the datasheet's 100 Ω in DW01A VCC (BAT-02), 1–10 nF CS-to-B− (BAT-01), R82 1 M → 100–220 k since CE-low is the *only* barrier to reverse-charging (BAT-04). **J5 is pin 1 = B−** — common hobby packs come both ways (BAT-V04). |
| [03](sections/03_ldo_power_tree_sleep_budget.md) | TLV75533, power tree, brown-out, sleep budget | Good | 0/0/2/11 | Feeding the LED boost from `LDO_IN` rather than 3V3 is what makes a 500 mA LDO viable. On USB the SOT-23-5 is **thermally limited to ~240–280 mA continuous** (PWR-01). Below ~3.2–3.3 V cell, 3V3 sags under 3.0 V on Wi-Fi TX. Panel + touch are permanently powered (PWR-07). **Deep-sleep budget ≈ 73 µA → ≈ 11.5 months on 1000 mAh**; ≈ 52 µA with value changes only — but scale *all four* status-ladder resistors together or you break the ladder (PWR-V02). Bring-up check: on battery only, `USB_VBUS` must read ≈ 0 V and D2 stay dark. |
| [04](sections/04_esp32_core_gpio_map.md) | ESP32-S3-WROOM-1-N16R8, straps, buttons, UART TPs, antenna | Good | 0/0/3/14 | Full GPIO table in the section. IO35–37 correctly unused, all analog on ADC1, reset-time state of every gated circuit is safe. BOOT button SW6 is DNP — fine while native USB works, no fallback when it does not (MCU-01). **The sibling firmware's `DE_LINK` pin profile does not match this PCB** (MCU-13). `TP_INT` is on IO41 (not an RTC GPIO): touch cannot wake from deep sleep. |
| [05](sections/05_sdmmc_microsd.md) | microSD, SD power gate, ESD | Good | 0/1/4/12 | The dual-source socket footprint was measured against both manufacturers' drawings: the NPTH slots sit at the exact midpoint of the two peg rows, **both parts fit**. Pull-ups correctly return to switched `SD_VDD`; firmware must drive the bus low/Hi-Z before gating off or the card is back-fed to 3.24 V (SD-01). The J7 BOM row names three different manufacturers (SD-04). Mechanical: see §4. |
| [06](sections/06_eink_driver_connector.md) | E-paper boost + 24-pin FPC | Very good | 0/0/0/11 | Faithful, slightly over-rated copy of Good Display's reference circuit; all 24 pins match; ratings exceed reference. Residual risk is that **nothing in the design data records where the panel sits or which way its tail folds** — add a User-layer drawing. ~~(And see fix #1: J2 has no paste.)~~ *(withdrawn — paste is present)* |
| [07](sections/07_led_frontlight_driver.md) | TPS923610 LED boost, warm/cool select, J3 | Sound | ~~1~~ 0/0/4/12 | 13.3 mA set-point, OVP/TVS pairing, LED_MONIT divider (2.73 V worst case) and power-on defaults all check out. Firmware notes: **ADIM is also the enable and needs a > 40 µs first pulse** — a bare 10–25 kHz PWM will not start it (LED-14); **open-load OVP latches after three trips** and re-applying PWM does not restart it (LED-V02). J3 pin mapping to the front-light flex is unverified from any primary source (LED-12). |
| [08](sections/08_buttons_rtc_touch_expansion.md) | ADC button ladders, DS3231MZ, touch + 0 Ω mux, J6 + ESD | Sound | 0/1/8/19 | Every single-button code separable by ≥ 204 mV worst case; ladders draw zero at rest. DS3231 wiring (VCC→GND, VBAT→3V3) is the datasheet's own single-supply figure — but there is **no backup cell** and **INT/SQW is unrouted**, so no alarm wake (HMI-03/04). Three strapping pins reach J6 behind 33 Ω (HMI-02). MJTP1117 metal covers float, with I²C 0.15 mm from two of them (HMI-V03). |
| [09](sections/09_erc_drc_fab_outputs.md) | ERC/DRC triage, fab capability, output consistency | Good paperwork, hidden issues | 0/0/10/14 | 0 unconnected, 0 parity errors, gerber zip proven current. All 39 ERC warnings benign; the 12 DRC errors are inside J1's own land pattern. **Nine DRC checks are set to "ignore"** — re-enabling them goes 94 → 366 items: 185 undersized silkscreen texts (incl. the battery polarity mark), no solder-mask dam between the 0.5 mm FPC pads, 25 starved thermal reliefs. Smallest annular ring 0.150 mm vs JLC's 0.18 mm; no fiducials; two opposite bottom-side rotation conventions across the centroid files; no JLC rotation-DB entry for U2/U10/D8. |
| [10](sections/10_layout_area_walk.md) | Layout, nine areas | Competent | 0/1/3/15 | See §5. Tight hot loops on both converters, EPD SPI entirely on B.Cu over solid F.Cu. B.Cu ground is 50 separate fills, 14 with no via to the F.Cu plane (LAY-05). |
| [11](sections/11_mechanical_enclosure_assembly.md) | Mechanics, enclosure, cables, assembly | Needs decisions | 0/3/8/12 | See §4. Contains an ASCII board map, overhang table, height table, hobbyist assembly sequence and an **enclosure designer's cheat-sheet**. |
| [12](sections/12_bom_function_and_cost.md) | BOM function + cost | Good, stock moved | 0/1/7/10 | See §7. |
| [13](sections/13_docs_end_user_readability.md) | Docs for replicators | Accurate, not yet a guide | 0/9/10/2 | See §6. *Not verifier-checked — editorial judgement.* |

---

## 4. Physical layout, enclosure and cable routing

Full treatment in [section 11](sections/11_mechanical_enclosure_assembly.md). The concept is coherent: the outline is
sized to the GDEQ0426T82 panel to within 0.17 mm, the L-shaped top leaves a ~38.75 × 30.5 mm battery bay, all three FPC
mouths face the flex slot, the bottom button row is symmetric to 0.000 mm, and there are zero mechanical DRC items.
The issues, in the order they bite:

| Issue | Detail | Options |
|---|---|---|
| **Flex slot is 47.04 × 1.30 mm in a 1.60 mm board** (MEC-01, MEC-06) | The three tails fit side by side (12.5 + 4 + 4 mm in 47 mm) and pass through with ~1 mm to spare, but each must be creased over a raw routed FR-4 lip to run back up to J2/J3/J4. Polyimide guidance is a static bend radius ≥ ~6× thickness ≈ 1.8 mm. | Widen to 2.5–3 mm and chamfer/round both lips (3 mm still leaves ~4 mm of bezel strip), or plan a printed radius insert in the case. |
| **The top face is not flat** (MEC-23) | 58 through-hole leads (USB-C, J6, six side switches, J5) come through *inside the panel footprint*, ~0.9 mm proud plus fillet, under a panel the silkscreen promises sits on a component-free face. Standing the panel off 1.5 mm eats flex-tail slack (≈ 22.8 mm needed of a 23.86 mm tail). | Make "clip and file flush, check with a straightedge" an explicit build step; or design the case to carry the panel on a ≥ 1.5 mm ledge and re-check tail length. Next spin: SMD side switches. |
| **microSD opens into the battery bay** (SD-V01) and sits 1.78 mm inside the board edge (SD-05) | The card's 15 mm insertion corridor plus finger room runs through the middle of the cut-out the battery lives in. | Confine the cell to the upper-left of the bay and publish the resulting max cell size; or rotate J7 on a respin. |
| **J5 faces +x, away from the battery bay** (MEC-04) | Cell leads must U-turn 180° and run ~18 mm back across the tongue. | Case needs a wire channel and strain relief there; keep leads away from the antenna notch. Or flip J5 on a respin. |
| Touch flex connector spacing is 0.79 mm wider than the panel's (MEC-05); J4's footprint origin is 0.73 mm off its pad centroid (MEC-V01) | Within flex compliance, but it side-loads the ZIF; any position-derived drawing mislocates J4. | Note for the case; fix the footprint origin next spin. |
| Side-button plungers vs panel edge: about ±0.25 mm of plan-view daylight (MEC-07). Bottom-row buttons sit ~1.0 mm closer to the edge than the side buttons (HMI-10). RESET (SW11) stops 3.54 mm short of the edge with D2 in its plunger path (MEC-09). | Tolerance stack for button caps; RESET needs a pin-hole/long plunger. | Enclosure cheat-sheet has every dimension. |
| Antenna | Notch and zero-copper region are correct; metal/copper within ~1 mm on both flanks (MCU-14). | Keep battery, panel backplane and screws out of the zone shown in section 04. |

---

## 5. Board areas (layout walk)

From [section 10](sections/10_layout_area_walk.md); coordinates are KiCad board mm, all parts on the bottom face.

| Area | Region | Contents | Notes |
|---|---|---|---|
| A1 | x 84–104, y 37–63 | Top tongue: J6 expansion header, its ESD cluster, PWR button, the "cut" neck | Fix #2–#4 all live here. |
| A2 | x 84–100, y 63–92 | J5, DW01A/FS8205A, reverse-battery PFETs, charger | Tidy; battery path 0.40 mm with two 0.25 mm links either side of R27. |
| A3 | x 73–88, y 79–92 | TPS2116, LDO, bulk caps | LDO has little copper to sink into — hence the ~250 mA thermal cap on USB. |
| A4 | x 52–82, y 68–92 | microSD + pull-ups + gate | ESD clamps 11–23 mm from the contacts (SD-02). |
| A5 | x 78–104, y 92–112 | USB-C, fuse, TVS, ESD, status ladder | 0.25 mm VBUS path (USB-06); J1 land pattern is the source of all 12 DRC errors. |
| A6 | module + left-edge recess | ESP32-S3, decoupling, series resistors | Antenna overhangs a 6.3 × 18.7 mm notch with no copper beneath — the best-executed thing on the board. |
| A7/A8 | lower third | EPD boost, LED boost, J2/J3/J4 | Hot loops 2.5 mm (LED) and 15.4 mm (EPD). No mask dams between FPC pads (FAB-03). |
| A9 | below the flex slot | Four bottom buttons | Mechanically decoupled from the main board by the slot; mounting holes at both ends. |
| — | whole board | Ground | F.Cu is the real plane; B.Cu is 50 islands, 14 un-stitched. Harmless at these speeds; add stitching vias when convenient. Silkscreen is ~half the minimum printable size almost everywhere. |

---

## 6. Documentation and replicability

From [section 13](sections/13_docs_end_user_readability.md), which also contains two persona walk-throughs, a
**proposed README outline**, and a fully written draft of **"Order an assembled board — step by step, no experience
needed"** you can lift. The mechanical checks all passed (88 link/image targets, 0 broken; every part-count claim
correct; "which parts are optional" table correct including the C12 trap). The problems are at the two ends of the
replication path:

1. **The printed URL / QR lands on the old project.** The repo's default branch is `master` (the predecessor `minRead`
   files); this design exists only on `06_2026`. Fix this before anything else (DOCS-08).
2. **No firmware is named anywhere**, and the board's own silkscreen tells the owner to flash it (DOCS-01). If it is not
   released, say so in the first 20 lines.
3. **The "recommended" route is a configurator at silkscreenreader.com that is not live** (DOCS-02).
4. **Three BOM files are offered as interchangeable** (DOCS-03) — see fix #6.
5. **No shopping list** for the panel SKU, front-light/touch variants, battery (capacity, JST-PH 2.0, **pin 1 = negative**),
   microSD, screws, case (DOCS-04); **no LiPo safety box** at all (DOCS-05).
6. **The first instruction sends a newcomer into the 100 KB design review**; the first step a non-KiCad reader can act on
   is 44 % of the way down (DOCS-06). README never says KiCad is not required (DOCS-17).
7. **JLCPCB "Standard" PCBA** needs 70 mm minimum width, edge rails and fiducials; the board is 60 mm and has no
   fiducials — warn the reader that rails will be added (DOCS-09, FAB-16).
8. No enclosure files or published mechanics despite "case agnostic" (DOCS-07); no cost/lead-time expectation
   (DOCS-10); no first-power-up checklist or troubleshooting (DOCS-12); README gives the wrong polarity rule for D2
   (DOCS-24); licence section does not say whether a reader may build or sell one (DOCS-15).

---

## 7. BOM: function and cost

From [section 12](sections/12_bom_function_and_cost.md). The population reconciles exactly (183 footprints = 162 placed
+ 10 DNP + 11 non-electrical), all 62 unique part numbers resolve to real parts, and **every MPN ↔ LCSC code ↔
value/voltage/package triple matched** — the highest-value check in the BOM, and it passed. 470 SMD + 92 THT joints per
board; everything machine-placed is on one side.

| Number | Value |
|---|---|
| JLC/LCSC parts, single-piece prices | ≈ **$15.56 / board** |
| DigiKey parts, buying for 5 boards | ≈ **$47 / board** (3.6× the LCSC figure) |
| Hand-build from DigiKey at qty 1 | ≈ **$63–66 / board**, not the ≈ $48 in `BOM_handbuild_digikey.csv` (its `est` prices are stale: U13 $5.50 → $13.85, ten switches $0.12 → $0.72) |

Critique that survived verification:

* **DS3231MZ is ~25 % of the DigiKey BOM.** The section's recommendation for the next revision is RV-3028-C7 (better
  accuracy, ~50× lower standby current, ≈ $11 / board cheaper) or, if ppm accuracy is not needed, PCF85063ATL at ≈ $0.60.
  Meanwhile the DS3231's two distinguishing features — backup supply and alarm interrupt — are not wired here
  (BOM-07, HMI-03/04).
* **Five TPD4E1U06 arrays** are the 4th-largest cost line and were never justified channel by channel (BOM-V01).
* **C2** (VBUS bulk) is 10 µF **10 V** 0603: ~3.5 µF effective at 5 V and only 2× headroom against hot-plug overshoot —
  the only genuinely tight capacitor rating on the board. Same footprint in 16/25 V (BOM-04).
* The charge/protect chain (TP4056, DW01A, FS8205A) is clone-market silicon with no Western distributor source — fine for
  a JLC build, a sourcing problem for the DigiKey-primary rule (BOM-09). D8 PESD2IVN-UX is NRND at DigiKey (BOM-06).
* Stock moved since the 2026-09-18 crawl: R14 (fix #5), the 22 µF MPN (BOM-02), U10 at 78 pcs (BOM-03).

---

## 8. Things that are right (so you know they were looked at)

Each section has a "Checked and found OK" list; highlights: USB-C pin map and CC resistors · TPS2116 priority strap,
reverse-current blocking and ST polarity · FS8205A pinout against the *ordered* part's datasheet · battery monitor taken
from `P+` so a reversed cell can never drive GPIO8 negative · TLV75533 caps are 25 V parts so DC-bias is a non-issue ·
LED boost fed from `LDO_IN` · octal-PSRAM pins untouched, every analog net on ADC1, power button on an RTC GPIO ·
reset-time state of all four MCU-gated circuits is safe · SD pull-ups on the switched rail · dual-source microSD
footprint fits both parts · e-paper connector pad-by-pad and every boost part ≥ reference ratings · LED_MONIT cannot
exceed GPIO abs-max even during an open-LED OVP event · TVS/ESD standoff correct on every expansion channel · both
ADC ladders separable with margin and zero static current · 0 unconnected nets, 0 parity errors · **production gerber
zip is byte-for-byte current with the board** (`evidence/gerber_fresh/COMPARISON.txt`, local evidence pack).

Six auditor claims were **refuted** by verification and are struck through in their sections — including an original
HIGH ("light sleep back-powers the gated-off SD card") and a claim that the touch-mux silkscreen recipe omitted R66.

---

## 9. Comparison with the earlier audits

Done only after the blind audit was complete. Three agents each took one body of earlier work, inventoried every
finding in it, mapped it to the new findings, and — for anything the new audit had not covered, and for the most
consequential "fixed" claims — re-checked the **current** design. Full mapping tables are in
[`comparison/`](comparison/); recovered findings are appended to [`FINDINGS_TABLE.md`](FINDINGS_TABLE.md).

| Earlier work | Items | Same | Partial | Not in new audit | Conflict | "Fixed" claims re-checked |
|---|---|---|---|---|---|---|
| [A — `DESIGN_REVIEW.md`](comparison/A_vs_DESIGN_REVIEW.md) | 80 | 44 | 20 | 7 | 7 | 12 hold, 2 half-done |
| [B — `docs/audit-2026-09-18/`](comparison/B_vs_audit_2026-09-18.md) | 113 | 64 | 20 | 17 | 10 | 9 hold, 4 do not fully |
| [C — `docs/audit-2026-09-16/` + NextPCB Rev0 notes](comparison/C_vs_audit_2026-09-16_and_nextpcb.md) | 52 | 20 | 14 | 5 | 5 | 8 hold, 1 half-done, 1 refuted |

### 9.1 What the comparison says about the big items

* ~~**The missing solder paste on J2/J3/J4 (LED-01) is genuinely new. None of the three earlier audits caught it.**~~ **Withdrawn in revision 2: the earlier audits did not "miss" it — there was nothing to catch.** The paste is drawn as polygons; this review's method could not see them. Original text: ~~The
  word "paste" appears in the earlier corpus only for the TP4056/ESP32 thermal pads and once in a J2 shield-pad finding
  that asserts "JLC paste will print the full 1.5 × 1.5 pad" — true of the tabs, silent about the 36 signal pads.
  The NextPCB SMD-only route the earlier notes recommend would have returned boards with all three connectors unsoldered.
  The earlier audits compared like with like (old gerber vs new gerber, CPL vs CPL, BOM vs schematic), which structurally
  cannot see a defect that is present in both.~~
* Also new: the top face is not flat (MEC-23), the microSD corridor through the battery bay (SD-V01), the flex *bend*
  problem at the slot (MEC-06), the USB_STAT windows the ADC cannot read (USB-01/02), R14's stock collapse and the Basic
  alternative, and the entire documentation-for-replicators family (the earlier audits reviewed the design, never what
  a reader receives).
* **Already known to you** (so treat my ranking as a second opinion, not news): raw `P+` on J6 (HMI-01); the 0.5 mm
  perforation slots (rated medium before, accepted carry-over); live nets across the cut line — the earlier audit had
  `P+`, 3V3 and 25 V `LED_SW` crossing, the new measurement is that `P+` is 0.15–0.20 mm from ground on both layers
  (MEC-02); the duplicate-LCSC BOM problem (DOCS-03).
* The 1.30 mm flex slot was explicitly *cleared* before — as a fab-capability question, correctly (1.3 mm > JLC's 1.0 mm).
  The new finding is about the flex fold, a different question. Both stand.

### 9.2 Recovered — real items earlier audits had that the new audit dropped

Each was re-checked against the current design before being accepted.

| ID | Sev | Item | Note |
|---|---|---|---|
| REC-A-02 / REC-B-01 | MEDIUM | **The Fix-4 CE gate cannot start charging a 0 V or protection-latched pack.** CE stays low until ~1.65–1.76 V appears at J5 (Q9's threshold through the detector), so a deeply discharged protected cell plugged in = nothing happens, indistinguishable from a broken board. | Owner-accepted limitation; put one sentence in the user docs. Earlier review already names the cheap fix (a two-pad manual override). |
| REC-B-03 | MEDIUM | **After any DW01A trip the board cannot restart from the cell alone** — Q8's gate reference floats with system ground, so recovery needs USB. Undocumented. | One paragraph in HARDWARE.md §3 and the troubleshooting list. |
| REC-A-01 | MEDIUM | **No digital VBUS-present signal.** `USB_VBUS` reaches no GPIO; the only USB-presence information is the analog USB_STAT ladder — the same ladder whose top two windows the ADC cannot resolve. | State it explicitly; firmware must treat USB presence as inferred. |
| REC-B-02 | MEDIUM | **TP4056 (U11) thermal pad: 4 of its 6 via-in-pad vias sit directly under paste windows**, while the ESP32's 12 are correctly between them. Solder wicks down the vias → starved thermal joint. *Here the earlier audit was right and more precise than the new one, which lumped U4 and U11 together.* | Nudge the six vias into the gaps between paste windows, or ask for via plugging. At ≤ 0.59 W it is a margin issue, not a failure. |
| REC-B-04, -05 | DOC | `DESIGN_REVIEW.md` still analyses Q3/Q8 as AO3419 (board fits AO3401A) at five places; U12 is a different prime MPN in the two BOMs and its JLC part has no footprint model, so its rotation cannot be checked in the preview. | |
| REC-C-02 | LOW | `SW6` is a third DNP part without *exclude from BOM* (alongside R72/R74). | Fold into fix #6. |
| REC-B-06…12, REC-A-03/04, REC-C-01/03/04/05 | LOW | 0603s 0.24–0.60 mm from the routed edge; 0.14 mm dangling stub on the 15–22 V `PREVGH` net; J2 shield pads 1.5 mm vs Hirose 0.4 × 0.9 mm; U10 pads 0.229 mm vs TI's 0.30 mm; EPD rail caps retain ~0.7–1.1 µF of 4.7 µF at bias; L2 Isat below U10's current limit (scope at hot-plug); Q7 turns SD_VDD on in µs; Q5/Q6 colour-select overlap never measured; sleep budget assumes genuine-TI LDO Iq; J6 TVS diodes clamp above what they protect; NextPCB substitute switch changes button depth; silkscreen proofreading. | Bring-up checks and next-revision clean-ups. |
| REC-A-05 | CERT-LATER | No USB D+/D− series-damping footprints (Espressif checklist). | |

### 9.3 Where old and new disagreed

| Topic | Verdict |
|---|---|
| Perforation slot width — 0.5 (old) vs 0.716 (one new agent) | **0.516 mm.** Old was right; the 0.716 figure added the line width. My own measurement agrees. Already struck in section 09. |
| "Production gerbers may be stale" (old: 1,995 differing lines) | **New is right — they are current.** The old diff compared X2-attribute output against X1 output; with export flavour matched the layers are identical. |
| "GPIO46 is input-only" (stated in DESIGN_REVIEW, HARDWARE.md, README) | **Wrong.** The ESP32-S3 has no input-only pins; GPIO46 is a strapping pin with a pull-down. Replace the wording (MCU-19). |
| EPD boost loop "grew to ~33 mm²" (quoted in HARDWARE.md §6.2) | Not reproducible; pad-centre shoelace gives 20–27 mm². Error is in the design's favour. |
| Charge current | Quote **≈ 0.23–0.25 A, lot-dependent, measure it.** The datasheet formula gives 234 mA; "255 mA" is the annotation the earlier review declined to endorse. |
| Via-in-pad under paste | **Old is right** — U11 has the problem, U4 does not (see REC-B-02). |
| USB/charge-status divider "verified" | **New is right.** The old check verified the arithmetic, never whether the ADC can read it or whether states are distinct. |
| "All ERC warnings cosmetic — zero real" | Overstated: one wire carries two names (`PIN_3` and `TP_RST` on J4.3, FAB-13) and U10/J3 cached symbols differ from their libraries (LED-09). Neither breaks connectivity. |
| "Floating" ground islands | Both right: nothing is electrically unconnected; many B.Cu fills simply lack an interlayer via. |
| D4–D6 identity | Three identities on one component: value `B5819W`, MPN `1N5819HW-7-F`, datasheet link for MBR0520. Tidy the fields. |
| J3 front-light pinout | Old holds the better evidence (a measured physical sample); new is right that no document confirms it. State both. |
| BOOT button DNP | New's risk analysis stands; old's mitigation (the through-hole pads exist, fit one if needed) should be in the docs. |

### 9.4 "Fixed" claims that are only partly true today

* **Battery path "widened to 0.40 mm — closed":** the Q3 → R27 → Q8 link is still 0.25 mm either side of R27 (BAT-07, PWR-V01).
* **"Stale BOMs fixed":** `v3` still has the duplicate-code defect and `bom.csv` still regenerates it (FAB-10/22, BOM-05).
* **"AO3419 → AO3401A in docs":** done in HARDWARE.md, still outstanding in DESIGN_REVIEW.md.
* **Q1/U5 manufacturer fields:** Q1 was corrected; U5 still says Fortune against an LCSC code that ships PUOLOP (BAT-V03).
* **SW6/U13 DNP disagreement:** U13 resolved; SW6 still DNP without exclude-from-BOM.

Everything else re-checked holds — all twelve applied changes in `DESIGN_REVIEW.md` (Fix-4 CE gate, Q4 → IRLML6346, R37
15 Ω, L1 47 µH, R14 2.2 Ω, C9, L2 10 µH, CR1, D2, R27 0805, J7 1.50 mm slots, U13 fitted) are present and
netlist-verified, and one deferred item was silently resolved (the charger's input bypass is now 2.08 mm from U11, not
the 9.16 mm the earlier review measured).

### 9.5 Blind spots, both directions

* **Earlier audits:** fabrication-output completeness (paste, mask dams, annular ring, silk size, fiducials), mechanics
  and the display stack-up, the repository as a deliverable to a replicator, and whether the ADC can actually read what
  the dividers produce. Their verification was largely self-referential (file vs file).
* **This audit:** weaker on history-dependent behaviour the earlier audits had reasoned through — dead-pack start-up and
  post-trip recovery, hot-plug transients, colour-switch overlap — and it lumped the two thermal pads together. It had no
  physical samples; the earlier work did (the front-light flex).

---

## 10. Method, evidence and limits

* **Ground truth** was regenerated from the KiCad files: XML netlist → per-component and per-net connectivity; `pcbnew`
  extract of every footprint, pad, track, via, zone and edge cut; ERC/DRC with all severities; per-net routing stats;
  schematic block crops, layer plots, zoom tiles and ray-traced renders; read-only checks through the KiCAD MCP server
  (always on a scratch copy — KiCad was open on the real project). Scripts are in `evidence/tools/` (local evidence pack).
* **13 auditors**, one per block group / discipline, each forbidden from reading earlier audits, each required to
  verify against manufacturer datasheets and show calculations. **12 adversarial verifiers** then re-derived every
  BLOCKER/HIGH/MEDIUM from the netlist and datasheets, re-graded severities, struck what they could not reproduce and
  added what was missed (36 findings were added by verifiers). Section 13 (documentation) had no verifier.
* I re-checked the headline items myself — **and on the headline item I repeated the auditor's method instead of challenging it**: I read pad layer sets and concluded there was no paste, when the footprint draws paste as graphic polygons. The lesson, now applied: paste and mask must be checked on the *plotted layer* (regions as well as flashes), not on pad properties. Other re-checks: the TP4056 exposed pad,
  the slot dimensions (three agents reported 0.50 / 0.516 / 0.716 mm — **0.516 mm** is the Edge.Cuts centre-line value;
  0.716 wrongly adds the line width), the ESP32 pin map, the DNP-jumper exposure in the upload BOM, and the gerber diff.
* **Limits.** No SPICE runs and nothing was measured on hardware. Stock and prices are a 2026-09-20 snapshot. Fab
  capability numbers are the fabs' published pages, not a DFM reply. The run was interrupted three times by usage
  limits; all sections were eventually completed, auditors and most verifiers ran on Claude Opus rather than the
  session's top model to fit. Front-light and touch flex pinouts could not be confirmed from any primary source.

---

## 11. Author response and re-evaluation (2026-09-20)

The author answered every HIGH and MEDIUM finding in [`FINDINGS_TABLE_author_refute.md`](FINDINGS_TABLE_author_refute.md).
Each answer is evaluated row by row in [`AUTHOR_RESPONSE_EVALUATION.md`](AUTHOR_RESPONSE_EVALUATION.md). Summary:

* **Withdrawn — the review was wrong:** LED-01 (paste is drawn as polygons; present on all 36 pads), FAB-23 (same slots as
  LAY-01, wrong width), LAY-V01 (the tongue's ground island is tied through J6's ground pins), PWR-14 (two sections
  contradicted each other), HMI-23 (substitute is a female header). The "41 pads carry no paste layer" count is void.
* **Re-evaluated and downgraded to LOW:** LAY-05 (pours are stitched: all 14 F.Cu islands tied; 6 of 50 B.Cu fills, 11.5 mm²
  in total, lack their own via and connect through SMD pads), USB-02 / USB-V02 (the "colliding" states need a sagging USB
  source and still decode to the right charge state; the no-battery blink is reachable only by pulling the cell while on
  USB — firmware note, no board change), USB-04 (no TVS swap helps; keep SMF6.5CA), PWR-01 (231 °C/W is TI's JEDEC figure
  and limits *continuous* current on USB to ≈ 240 mA; 500 mA bursts are fine), BAT-02, BAT-03, FAB-03, FAB-16, HMI-02,
  HMI-07, HMI-V03, LED-12, MEC-V01.
* **DRC clearance-error counts reconciled:** 12 live at J1 + 3 excluded at J3 with `--all-track-errors`; 11 + 3 with
  default flags; the author's 10 + 3 is the same population. One LOW item, footprint-inherent, accepted.
* **Front-button tab gap:** both numbers — 0.300 mm exposed copper to exposed copper (the author's design intent),
  0.151–0.188 mm copper to copper under mask.
* **Confirmed from the datasheet at the author's request:** TPS923610 tADIM_EN = 40 µs, tADIM_SD = 2.5 ms (SNVSCN8 p.5, §7.3.1).
* **Done in this pass:** R14 → LCSC C22939; duplicate-LCSC BOM bug fixed at its source (four Value strings normalised);
  both schematic design notes corrected; README rewritten; HARDWARE.md corrected and given a firmware-contract section;
  board STEP exported. Details and the remaining work: [`AUTHOR_TODO.md`](AUTHOR_TODO.md).
* **Remaining 226 unanswered rows pruned:** 17 still want a one-line answer, 30 are no-decision clean-ups, the other 179
  are settled by answers already given, done, withdrawn, or informational — [`REMAINING_PRUNED.md`](REMAINING_PRUNED.md).
* Parts alternatives the author asked for (RTC, ESD arrays, D8, 22 µF, a PPTC): [`responses/PARTS_RESEARCH.md`](responses/PARTS_RESEARCH.md).
