# J1: USB-C receptacle options, compared by hand-soldering and price

Research note of 2026-10-20. The question: is the through-hole GCT `USB4085-GF-A` actually easier to solder than a receptacle whose pads are exposed at the rear with locating pegs? **Applied on 2026-10-22: `J1` is now the 12-pad SMD part (section 9); sections 1–8 are the research and checks as written on 2026-10-20.** Prices are a snapshot (LCSC and DigiKey, 2026-10-20); the solderability evidence is anecdotal (blogs, forum threads, vendor drawings), not a bench test.

## 1. Short answer

- The evidence does **not** show the exposed-pad hybrids are easier by hand. Three independent builders call the `USB4085-GF-A` easy (all pins through-hole, visible, self-locating); the hybrids are described as "hand-solderable", but their signal pads are 0.5 mm pitch. Receptacles with a second row of pads hidden under the body are the ones everyone says to avoid.
- On **every** option the stainless shell tabs are the fiddly joint, so a hybrid does not remove that step.
- The hybrids win on **factory assembly and cost**: about $0.07–0.19 against $1.05–1.42 for the connector, no through-hole labor (JLC lists the `USB4085-GF-A` as manual "wave soldering", about $0.33 a board for its 20 joints), and several makers share one land pattern.
- So the answer depends on who solders `J1`: if the factory does, a hybrid is better; if builders do it by hand, the `USB4085-GF-A` is at least as easy.

## 2. The two families that can carry USB 2.0 plus CC

| | `USB4085-GF-A` (through-hole) | 12-pad hybrid ("exposed pads and pegs") |
|---|---|---|
| Parts | GCT `USB4085-GF-A` | GCT `USB4105-GF-A`, Korean Hroparts `TYPE-C-31-M-12`, Shou Han `TYPE-C 16PIN 2MD(073)`, XUNPU `TYPEC-304J-BCP16` (near-identical land in their drawings); HCTL `HC-TYPE-C-16P-01A` and Palconn `UTC16-G` have similar lands in KiCad's library (not compared) |
| Signal joints | 16 round pins, Ø0.40 mm holes, 0.85 mm pitch in two straight rows 1.35 mm apart; pad gap 0.15–0.20 mm | 12 SMD pads in one row at the rear: eight 0.30 mm pads at 0.50 mm pitch (CC, D±, SBU) and four 0.60 mm pads (VBUS, GND); gap 0.20 mm |
| Reach | All joints visible from the solder side; nothing hidden | All pads exposed behind the shell (pads 1.15–1.45 mm long) |
| Locating | Pins in holes | Two Ø0.65 mm pegs plus four shell tabs in plated slots |
| Shell tabs | Four, stainless, slots 0.6 × 1.4 and 0.6 × 2.1 mm | The same four tabs |
| Body | 8.94 × 9.17 mm, PCB top mount | 8.94 × 7.35 mm |
| Where the joints are on this board | `J1` is on `B.Cu`, so the pins come through to `F.Cu` and are soldered there; on a 1.6 mm board they end flush | All on `B.Cu` with the other parts |

The hybrids share one land pattern: KiCad's stock `USB_C_Receptacle_HRO_TYPE-C-31-M-12` and `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` differ by a few tenths of a millimetre in pad length (1.45 and 1.15 mm) and position, and use the same pad names (`A1` to `B12`, `S1`) as the symbol `J1` has now. The pads interleave `DN, DP, DN, DP` (`B7, A6, A7, B6`), so tying the two `D+` pads and the two `D−` pads means each pair crosses the other.

## 3. What builders say

| Part or class | Statement | Source |
|---|---|---|
| `USB4085-GF-A` | "hand-soldering is a breeze"; all pins through-hole, needs 6/6 mil fab; backordered at the time (2020) | [medo64](https://medo64.com/posts/easy-type-c-finally) |
| `USB4085-GF-A` | finest through-hole pitch seen (0.85 mm), "still pretty easy to hand solder" | [EEVblog, ve7xen](https://www.eevblog.com/forum/projects/hobbyist-soldering-of-usb-c-connectors) |
| `USB4085-GF-A` | "all pins are through hole and hand solderable", but the data pins "barely break the surface of 1.6 mm PCB" | [ai03 Type-C.pretty](https://github.com/ai03-2725/Type-C.pretty) |
| `TYPE-C-31-M-12` | "hand-solderable" single-row design, extremely cheap; legs too short to officially support 1.6 mm boards (soldered in anyway, ending short of the far side) | [ai03 Type-C.pretty](https://github.com/ai03-2725/Type-C.pretty) |
| `TYPEC-304J-BCP16` | used for everything, USB 2.0 over Type-C, "quite easy to solder down"; shield legs short | [EEVblog, NorthernWing](https://www.eevblog.com/forum/projects/hobbyist-soldering-of-usb-c-connectors) |
| A pad row under the body (Amphenol `12401598E4#2A`, the Molex `105450-0101` type) | needs a reflow station for the pins under the barrel; fully SMD Type-C is "impossible to solder by iron"; concealed pads are "more like BGA" (said of vertical mixed parts) | [ai03 Type-C.pretty](https://github.com/ai03-2725/Type-C.pretty), [ai03 wiki](https://wiki.ai03.com/books/pcb-design/page/usb-type-c), [medo64](https://medo64.com/posts/easy-type-c-finally), [EEVblog](https://www.eevblog.com/forum/eda/usb-c-2-0-routing-of-hybrid-smt-through-hole-connector/) |
| Full 24-pin SMD, iron | split: "useless for SMT pins" against one poster who did it pin by pin with a chisel tip and a lot of flux | [EEVblog tips thread](https://eevblog.com/forum/projects/tips-on-hand-soldering-usb-type-c-receptacles) |
| Würth `632723100011` (hybrid with through-hole secondary pins) | those pins are "not meant to be wave or hand soldered"; fill the holes with paste | [EEVblog hybrid thread](https://www.eevblog.com/forum/eda/usb-c-2-0-routing-of-hybrid-smt-through-hole-connector/) |
| JLCPCB listing | `USB4105-GF-A` assembly difficulty "High" (machine); `USB4085-GF-A` assembly type "Wave Soldering" (manual) | [C3020560](https://jlcpcb.com/partdetail/3542626-USB4105_GFA/C3020560), [C7095263](https://jlcpcb.com/partdetail/C7095263) |

Technique advice from the same threads: chisel tip, plenty of tacky flux, tack one shell tab first, keep solder to a minimum and use wick on bridges, and clean the flux off (it gets inside the connector and makes insertion sticky).

## 4. Price (snapshot 2026-10-20)

| Part | Type | DigiKey (qty 1 / 10 / 100) | LCSC (qty 1 / 10 / 100) | LCSC / JLC stock | JLC library |
|---|---|---|---|---|---|
| GCT `USB4085-GF-A` | through-hole | $0.91 / $0.77 / $0.66 (85,598 in stock, 7 weeks) | `C7095263` $1.42 / $1.18 / $0.90 | 1,352 / 3,769 | Extended, manual |
| GCT `USB4105-GF-A` | hybrid | $0.80 / $0.68 / $0.57 (91,609 in stock, 7 weeks) | `C3020560` $1.31 / $1.09 / $0.83 | 0 | Extended |
| Korean Hroparts `TYPE-C-31-M-12` | hybrid | not listed | `C165948` $0.19 (from 5) / $0.15 (from 50) / $0.13 (from 150) | 322,040 / 359,904 | Extended, SMT |
| Shou Han `TYPE-C 16PIN 2MD(073)` | hybrid | not listed | `C2765186` $0.075 (from 20) / $0.061 (from 200) | 820,820 / 944,395 | Extended, SMT |
| XUNPU `TYPEC-304J-BCP16` | hybrid | not listed | `C2835315` $0.50 / $0.41 / $0.31 | 20,444 / 20,862 | Extended, SMT |
| Amphenol `12401610E4#2A` | two-row SMD | $1.43 (80,284) | n/a | | |
| Molex `1054500101` | two-row SMD | $2.74 | n/a | | |
| Würth `632723300011` | hybrid, through-hole secondary pins | $4.37 / $4.05 / $3.15 (15,864) | n/a | | |
| Kycon `KUSBX-SL-CS1N14-B` | through-hole, 14 pins | $2.43 (37,101) | n/a | | |

`C2915479` (HDGC `1.0-B-16P`), which `fabrication/BOM.md` used to name as a $0.10 through-hole USB-C, is a 1 mm FFC connector, not a USB-C receptacle. The note is corrected.

**Per board at JLC** (connector at the LCSC price for the quantity, SMD parts bought with BOM.md's 3 % plus 4 pieces of attrition, plus through-hole labor of $0.0164 a joint for the 20 joints of `J1`, or $0.015 at 150 boards where the order passes 10,000 through-hole joints; the $3.58 flat hand-soldering fee stays either way because `J5`, `J6` and the ten buttons remain through-hole, and all of these are Extended parts):

| Boards | `USB4085-GF-A` (part + labor) | Shou Han `C2765186` (pieces bought) | Saving per board | Saving per order |
|---|---|---|---|---|
| 5 | $1.42 + $0.33 = $1.75 | 10 pcs, $0.15 | **$1.60** | $8 |
| 30 | $1.05 + $0.33 = $1.38 | 35 pcs, $0.09 | **$1.29** | $39 |
| 150 | $0.90 + $0.30 = $1.20 | 159 pcs, $0.08 | **$1.12** | $168 |

With the Hroparts `C165948` instead ($0.19 up to 49 pieces, $0.15 from 50, $0.13 from 150) the saving is $1.37, $1.16 and $1.06 a board. Two assumptions move the numbers a little: if JLC bills the 20-piece minimum at 5 boards, Shou Han costs $0.30 a board and the saving is $1.45; and if JLC charges an SMT part's feeder-loading fee ($1.53 a part for Standard PCBA) that a hand-soldered through-hole part does not pay, the saving drops by $0.31, $0.05 and $0.01 a board. About 5 % of the all-in cost at 30 boards. For a hand-build from DigiKey (`USB4105-GF-A` against `USB4085-GF-A`) the difference is $0.11, $0.09 and $0.08 a board.

## 5. What switching would involve

- **Footprint and routing.** Swap `J1` to the 12-pad footprint (nets follow the pad names), re-route 12 pads where 16 holes were, and tie the interleaved `D+`/`D−` pads past the pad ends with short jumps or vias. The body is 1.8 mm shorter (7.35 against 9.17 mm), so the pads sit roughly 1–2 mm nearer the edge for the same mouth position.
- **Enclosure.** Checked against `case-426` and `case-368` in section 8: the mouth plane, centre line, shell and opening can be matched exactly; the opening centre sits 0.14 mm lower, which uses up the case's margin on one side of the plug.
- **JLC.** Add `J1` to the placement-preview checks (the Toolkit corrects rotation only for SOT-23, SOIC and JST parts). Confirm the shell tabs are soldered: forum posts say the tabs carry the mechanical load, and whether JLC's reflow fills the slots was not verified.
- **Part fields.** Keep the DigiKey-primary rule: `MPN` `USB4105-GF-A`, Manufacturer GCT, with `C165948` or `C2765186` as the JLC equivalent (`C3020560` has no stock).
- **Single source.** The `USB4085-GF-A` is made by GCT only; the 12-pad land appears on drawings from GCT, Hroparts, Shou Han and XUNPU.

## 6. Recommendation

Switch only if the factory is the normal path for `J1`: it saves $1.2–1.6 a board, removes `J1` from the through-hole list and adds second sources, at the cost of a layout edit, a case check and one more preview item. If builders solder `J1` themselves, keep the `USB4085-GF-A`: it is at least as easy, and the shell tabs are fiddly either way. Rev 1.02 is not fabricated yet, so this is the cheap moment to switch.


## 7. Sourcing rule and footprint check

Ian's rule (2026-10-20): a part bought from LCSC/JLC needs an equivalent that is not LCSC-exclusive, on the same footprint. DigiKey stock counts, so GCT qualifies. (GCT is headquartered in Hong Kong and makes its parts in mainland China, per the [Design News directory](https://directory.designnews.com/global-connector-technology-comp232359.html) and [Octopart](https://octopart.com/zh/part/gct/USB4105-GF-A); "Western" here means distributed, not American-made.)

**Shou Han against KiCad's GCT `USB4105` footprint.** KiCad has no Shou Han footprint, so the recommended layout in its datasheet was measured (the drawing's vector geometry, calibrated on its 8.64 mm slot spacing) and overlaid on the stock `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`: [overlay](./j1_shouhan_vs_gct_overlay.png). The Hroparts footprint is added for comparison.

| Feature (distances measured back from the mouth-side slot centres, mm) | Shou Han drawing | KiCad GCT `USB4105` | KiCad Hroparts `TYPE-C-31-M-12` |
|---|---|---|---|
| Pad centres across | ±0.25, ±0.75, ±1.25, ±1.75, ±2.40, ±3.20 | same | same, except the wide pads at ±2.45 and ±3.25 |
| Pad widths | 8 × 0.30, 4 × 0.60 | same | same |
| Pad near edge / far edge | 4.17 / 5.32 (measured 4.166 / 5.314) | 4.18 / 5.33 | 4.37 / 5.82 |
| Slots beside the pads (x ±4.32) | hole 0.6 × 1.7, outer 2.10, 4.18 back (measured 4.183) | same | same |
| Mouth-side slots (x ±4.32) | hole 0.6 × 1.4, outer 1.80 | same | hole 0.6 × 1.2, outer 1.6 |
| Pegs | 2 × Ø0.65 at x ±2.89 (measured ±2.897), 3.68 back (measured 3.686) | same | Ø0.65, 3.65 back |

**Result: every feature of the Shou Han land coincides with KiCad's GCT footprint to within 0.02 mm** (the limit of the drawing's line coordinates). The Hroparts footprint is the one that differs: its pads are 1.45 mm long and start 0.2 mm further back, and its mouth-side slot is 0.2 mm shorter. The GCT footprint is the common denominator; if the extra room for an iron matters, a union land that keeps GCT's pad start and ends the pads at 5.82 mm (about 1.65 mm long) fits all three.

Differences that are not in the footprint: Shou Han's datasheet rates it 3 A / 5 V (GCT 5 A / 48 V, Hroparts 5 A / 20 V), its outline is 3.16 mm tall against 3.31 mm in GCT's drawing, its tab spacing is 4.20 against 4.18 mm, and its layout is drawn for 0.80 mm boards (GCT shows a 0.95 mm stake), so on a 1.6 mm board the legs end short for all three.

**For the rule:** Shou Han passes, with GCT `USB4105-GF-A` (DigiKey) as the equivalent on the same footprint. The US-brand alternatives do not help: Same Sky `UJ20-C-H-G-SMT-*-P16-TR` has the same 12-pad row but a different land (no peg holes, a 1.1 mm hole beside the pads against GCT's 1.7, a 6.5 mm body, datasheets for 0.6–1.0 mm boards), and Molex `2169890001` and Amphenol `12402054M611A` are 14-pin through-hole parts with their own footprints.

The current `USB4085-GF-A` sidesteps the rule: the JLC part (`C7095263`) and the DigiKey part are the same GCT part.


## 8. Placement check against the enclosures and the board (scratch copy only)

Done 2026-10-20 on a copy of the board; nothing in the repo's board, schematic or the sibling case repos was changed. The enclosure source (`case-426` and `case-368`, which record identical J1 data) derives its USB-C features from J1's 3D model: `body.usb()` slices the model 0.2 mm behind the mouth for the shell and the socket opening, and the tub hole is the opening plus 0.10 mm a side. The same slice was run on KiCad's models; for the `USB4085-GF-A` it reproduces the case's recorded J1 numbers exactly (shell z −3.535 to −0.375, mouth at x 105.435, 8.94 mm wide), so the method is sound. The `USB4105` footprint was then placed on B.Cu, rotated like J1, with its mouth plane at x 105.435 and its centre line at y 106.95 (origin 101.76, 106.95).

| Enclosure-relevant geometry | `USB4085-GF-A` (J1 now) | GCT `USB4105` (Shou Han has the same land and a 3.16 mm shell) |
|---|---|---|
| Mouth plane (board x) | 105.435 | 105.435 (matched by placement) |
| Centre line along the edge (board y) | 106.95 | 106.95 |
| Shell, outer | 8.94 × 3.16 | 8.94 × 3.16 |
| Socket opening | 8.34 × 2.56 | 8.34 × 2.56 |
| Opening centre above the seating plane | 1.87 | 1.73 (**−0.14**) |
| Opening centre in the case frame (z) | −1.955 | −1.815 |
| Body depth, rear edge (board x) | 9.17 mm, 96.27 | 7.35 mm, 98.09 |

Only the height differs. Effect on the existing case (hole 8.54 × 2.76 mm centred at z −1.955):
- The plug (8.25 × 2.40 nominal) sits centred in the new opening, so its PCB-side face lands 0.04 mm from the hole's edge (was 0.18 mm) and its far side 0.32 mm (was 0.18 mm). It passes, with the margin used up on one side; a hole printed small would rub.
- The lid block that closes the hole's far edge stays 0.24 mm clear of the opening (was 0.10 mm), and the shell's far face is 0.36 mm from the parting plane at z −3.75 (was 0.215 mm).
- The mouth plane, the centre line, the shell and the opening size are unchanged, so the recess, the floor position, the block gap (0.055 mm in front of the mouth) and the insertion corridor (0.115 mm) do not move. A case follows the 0.14 mm only after the board copy it is built from is replaced: both case repositories read a frozen copy of the 2026-09-21 board (`hardware/board-2026-09-21`, with the `USB4085`), and `prepare_hardware.py` has to be re-run on the new board.
- The shorter body only frees room behind J1; the stakes (0.95 mm) no longer stand proud of the board's front face as the through-hole legs do (+0.5 mm).

Not known: Shou Han's drawing gives the 3.16 mm shell but not its seat height above the board, so its opening centre must be checked on a sample (the case needs it within about ±0.1 mm of 1.87 mm above the seating plane, or 1.73 mm if the case is regenerated). The older `silkscreen-enclosure-*` repos use the same `body.usb()`; `silkscreen-case` hard-codes its own USB numbers; neither was checked.

**Board.** [`j1_swap_land_map.png`](./j1_swap_land_map.png) overlays the new land (blue) on the existing copper, with the old land dashed red.
- The new land is 12 pads at x 97.5–98.65 (centre 98.08), rear slots at x 98.655, front slots at x 102.835 and two pegs at x 99.155; the courtyard is x 97.0–105.94 by y 101.64–112.27 (the old one starts at 95.77). No courtyard overlap and no copper-to-edge violation (the front slots end 0.5 mm from the edge).
- Every J1 net has to be re-routed, as for any footprint change, and the GND stitching via at (99.6, 111.8) and the DP via at (99.81, 103.3) conflict with the new rear slots and peg.
- **The real conflict:** the new front slots are 1.65 mm further forward than the old ones (2.6 mm behind the mouth instead of 4.25 mm), which puts them on four long F.Cu traces that run down the board edge between the old slots and the edge: `I2C_SDA` (x 102.41), `LED_SW` (102.86), `W-` (103.31) and `C-` (103.66). They have to be re-routed around the slots: the F.Cu corridor between the rear and front slots (x 99.8–101.8) is free once the old shield bars go, and the jogs fit just above and below the slot pairs.

## 9. Applied in Rev 1.02 (2026-10-22)

`J1` is now the 12-pad SMD hybrid land (KiCad's `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`; schematic `Footprint` field changed, `MPN` `USB4105-GF-A`, `Manufacturer` `GCT`, `LCSC` `C2765186`).

[`j1_applied_layout.png`](./j1_applied_layout.png) shows the result (left `F.Cu`, right `B.Cu`, GND pour in green, shield in teal, `DP` green, `DN` blue, `CC1`/`CC2` orange, `VBUS` red).

- **Position.** Origin (101.76, 106.95), `B.Cu`, rotation −90: the mouth plane (x 105.435) and centre line (y 106.95) are exactly where the `USB4085` had them, checked on the footprint's `B.Fab` outline before and after. The body is 7.35 mm deep (outline lines at x 98.085 and 105.435; the 98.035–105.485 box of the outline includes its 0.1 mm line width).
- **Routing** (done with a small grid router for the three hard nets plus hand-placed copper, all DRC-checked):
  - the four long edge traces (`I2C_SDA`, `LED_SW`, `W-`, `C-`) step 2.16 mm left on 45° jogs into the corridor between the slot pairs (x 100.25–101.50), through both slot bands, and step back out below (y 99.2–101.9 and 112.1–114.8, parallel offsets so the 0.451 mm pitch holds);
  - the shield: the four slots are joined in a ring (east `B.Cu` vertical at x 103.3, bottom `B.Cu` link at y 111.27, west `F.Cu` bar at x 97.45) and tied to `C1`/`R1` as before; the ring is open on its north side so `DP`/`CC2` can leave through the corridor;
  - `VBUS` and `CC1` reuse the old copper; `DN` and `DP` use the open side of the pad row (a `B.Cu` loop on the mouth side for `B7`/`A7`, three vias for `DP`); `CC2` runs up the corridor on `B.Cu`. 5 new vias in all (0.5/0.3 mm, none on a pad);
  - the GND via at (99.6, 111.8) and the `DP` via at (99.81, 103.3) were on the new rear slots and are gone; `A8`/`B8` stay unconnected.
- **Edits Ian made in KiCad afterwards (2026-10-22).** The top `VBUS` run was straightened: `B.Cu` now runs along y 104.55 from x 94.85 straight to the pad (it came in on a 45° diagonal before) and `F.Cu` runs down x 94.6 (was x 95.249); a GND via (0.6/0.3 mm) was added at (102.3, 104.9) (item 5 below); the `J1` reference text moved. DRC with parity and ERC were re-run on the saved board: nothing new (0 unconnected, 0 parity, the same 41 ERC warnings, the 3 older clearance errors and the 4 `hole_clearance` errors all excluded).
- **Paste.** KiCad's footprint already puts `B.Paste` on the four plated shield slots and on all twelve pads, so nothing was added; the extension pads below carry none.
- **Hand-soldering extension (added 2026-10-22, at Ian's request).** Behind each of the twelve lands there is an extra rectangular pad, copper and mask only (`B.Cu` + `B.Mask`, no paste, no mask margin), the land's width, reaching 0.3 mm behind the original pad's rear edge and overlapping it by 0.05 mm (0.2 mm at `A8`: the neighbouring `DP` via at (96.9, 107.9) allows no more under the 0.25 mm hole rule). Same pad number and net as its land, a solid zone connection on the GND ones. The original pads, so the library land, the paste apertures and the JLC placement, are untouched. The exposed tail behind the housing's rear wall (x 98.085) grows from 0.58 to 0.88 mm, which lets an iron touch copper without touching the plastic. Checked on the plotted layers: the mask openings are 1.45 mm long (1.35 at `A8`) with the 0.2 mm dams between neighbours unchanged, only own-net stubs lie inside them, no via is uncovered, and `B_Paste` and every other layer except `B.Cu`, `B.Mask` and the clear-polarity knock-outs in `B.Silkscreen` are identical to the version without the extension. DRC shows nothing new (0 live errors, 0 unconnected, 0 parity); the `B.Cu` pour loses 0.6 mm² beside the pads, and the project ignores `lib_footprint_mismatch`, so the changed footprint instance raises no warning. A mask margin like the ribbon connectors' (+0.102 mm) was not used: on 0.3 mm pads at 0.5 mm pitch it would close the mask dams.
- **Checks.** DRC with schematic parity: 0 unconnected items, 0 parity findings, no new clearance, short or edge finding. **Four `hole_clearance` errors are new and come from the footprint itself**: each of the two pegs (Ø0.65 NPTH) sits 0.194 mm from the stacked GND pads beside it, against the board's 0.25 mm hole rule (the GCT drawing's own land; the Shou Han part has the same). Ian excluded all four in KiCad on 2026-10-22 (they are in `silkscreen_pcb.kicad_pro`); a manufacturer-approved override would be the alternative. The GND pads got a solid zone connection (thermal relief starved them).
- **Production files.** `production/` regenerated (the Toolkit's CPL row for `J1` is (100.455, −106.95, 270): the footprint origin 101.76 plus `FT Position Offset` `0,1.305`, see item 1 below); `jlc_bom.csv`, `other_fabs/`, the BOMs and both PDFs updated.
- **Still unverified.**
  1. JLC's own footprint for `C2765186`, read on 2026-10-22 from EasyEDA's public API (`USB-C-SMD_TYPE-C-16PIN-2MD-073`): the same pad order and orientation as KiCad's land (`A1`/`B12` at the left end, mouth toward +y in both frames, pegs 1.07 mm in front of the row, body 7.35 mm), so no rotation offset; but its origin is 2.375 mm in front of the pad row where KiCad's is 3.68 mm. JLC places a part by that origin, so the CPL point moves 1.305 mm toward the pad row: `FT Position Offset` `0,1.305` on `J1` (schematic symbol and footprint), CPL x 101.76 → 100.455. The same reading reproduces the checked `J4` offset (its CPL point lands on the EasyEDA origin, 1.25 mm in front of the signal row), and `J3`, which needs none, has the same origin in both. Not yet seen in JLC's own preview: check `J1` there. The community table (matthewlai/JLCKicadTools) needs 180° for the different HRO `TYPE-C-31-M-12` footprint; that does not apply to this part.
  2. Whether JLC reflows the shield-slot tabs from the paste apertures; look at the first assembled board.
  3. Shou Han's seat height (the case needs the opening centre within about ±0.1 mm of 1.73 mm above the seating plane): measure a sample, and, if you want the case exact, replace the cases' frozen board copy with the new board and re-run `prepare_hardware.py` (section 8).
  4. The case repositories were not touched. Both still read their frozen 2026-09-21 board copy, so a case follows Rev 1.02's `J1` (the opening 0.14 mm lower, section 8) only after that copy is replaced and `prepare_hardware.py` is re-run.
  5. Ground stitching at the connector (layout audit, re-checked on the saved board 2026-10-22): the new GND pads are SMD on `B.Cu` only, and all four sit in the same 462 mm² `B.Cu` pour. `A1`/`B12` hang in a pocket joined to that pour by a neck about 0.2 mm wide; no via fits inside it (the `DP` and `CC1` runs on `F.Cu` box it in). The pour reaches the 3,357 mm² `F.Cu` main plane through the thermal spokes of `SW11` pin 1, 9.8 mm from `J1`'s centre, and otherwise only through three `F.Cu` fragments of 171, 167 and 15 mm². The via Ian added at (102.3, 104.9) ties the pour to the 15 mm² fragment, so it is not a path to the main plane; a via by the lower pair (about (96.6, 110.2)) would land in the 171 mm² fragment, also not the main plane. DC is unaffected; this concerns only the connector's ESD return path. Not changed further.
  6. The receptacle overhangs the board edge by 1.2 mm (edge x 104.237, mouth plane x 105.435), as the `USB4085` did, but the GCT and Shou Han drawings put the PCB edge flush with the shell front. Its front 1.2 mm is carried by the stakes and pads only: check that the case supports it (a rib above or below the shell), or add a 1.2 mm board tab under `J1` if the case allows.
  7. JLC's DFM view of the extension pads (copper-only pads overlapping the land, 0.2 mm mask dams, paste unchanged) has not been seen; nothing in it should draw a warning.
