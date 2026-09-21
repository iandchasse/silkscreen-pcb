# Remaining findings, pruned against the author's answers

Scope: the 204 LOW / DOC / CERT-LATER findings and the 22 recovered ones — everything you have **not** yet answered in `FINDINGS_TABLE_author_refute.md`.
Each was read against the answers you gave to the HIGH and MEDIUM rows. **Only the first table needs you.**

## Still open — a one-line answer closes each (17)

| ID | Sev | Finding | Note |
|---|---|---|---|
| BAT-01 | LOW | No capacitor from DW01A CS to its GND pin - first-connection inrush can latch the protection off | Optional 1-part hardening (1-10 nF, DW01A CS to B-). Your earlier board worked without it; say "skip" and it is closed. |
| BAT-04 | LOW | R82 = 1 MOhm is the only default-off pull-down on CE, and CE-low is the sole barrier to reverse-charging a backwards cell | R82 1 M -> 100-220 k. The one cheap, safety-relevant value change you have not addressed: CE-low is the only thing stopping the charger driving a reversed cell. |
| BOM-04 | LOW | C2 USB VBUS bulk capacitor is 10 V rated on a 5 V hot-pluggable rail and loses ~65 % to DC bias | C2 (VBUS bulk) is 10 V on a hot-plugged 5 V rail, ~3.5 uF effective. Same footprint in 16/25 V. Cheap; your call. |
| BOM-08 | LOW | The hand-build DigiKey BOM understates parts cost by about 38 %, mostly on two lines | Hand-build DigiKey BOM total is ~$63-66, not ~$48 (stale 'est' prices). Matters for the cost expectation you agreed to add (DOCS-10). |
| DOCS-19 | LOW | The project is named five different ways across repo, files, title block and board | Project is named five ways (Silkscreen Reader / de-link / silkscreen_pcb / minRead URL...). Goes with your DOCS-08 link fix. |
| EPD-05 | LOW | R15 = 10 kohm on GDR where the panel maker's reference circuit specifies 1 Mohm | R15 is 10 k where Good Display's reference shows 1 M on GDR. Did you choose 10 k deliberately? One word closes it. |
| EPD-06 | LOW | No pull on EPD_CS (floats during ESP32 boot with the panel powered) and none on EPD_BUSY | No pull-up on EPD_CS - it floats while the ESP32 boots with the panel powered. A firmware early-init or a 10 k would close it. |
| HMI-22 | LOW | README's optional expansion-header block omits the protection parts that exist only for J6 | README's optional 'expansion header' block does not list the protection parts that exist only for J6 (so a builder omitting J6 still buys them). |
| LAY-03 | LOW | Metal screw/washer at H1 or H5 can short the LiPo rail to the GND mounting annulus | A metal screw/washer at H1 or H5 can bridge the LiPo rail to the grounded mounting annulus. Either a note for case designers (nylon washer) or pull the track back. Your call. |
| MEC-20 | LOW | H2 and H5 are 1.500 mm out of level, so the upper boss pair is skewed | Mounting holes H2 and H5 are 1.500 mm out of level with each other. If that is not deliberate it is a 10-second fix; if it is, ignore. |
| PWR-03 | LOW | Deep-sleep budget is ~73 uA typical; ~21 uA is recoverable with four resistor value changes | Optional: four value changes recover ~21 uA of the ~73 uA sleep budget (scale all four status-ladder resistors together). Say "later" and it is closed. |
| USB-08 | LOW | Status ladder draws 13.2 uA continuously from 3V3 on battery, comparable to the MCU's whole deep-sleep budget | Same decision as PWR-03 (the status ladder is 13 uA of the sleep budget). |
| LAY-D3 | DOC | HARDWARE.md 16 warns about a conductive case bridging HV nets but not about a screw shorting the battery at H1/H5 | Goes with LAY-03. |
| MCU-21 | DOC | Neither document mentions the PCB antenna, the outline notch that serves it, or the keep-out an enclosure must respect | Neither doc mentions the antenna keep-out a case must respect. One paragraph for case designers - goes with DOCS-07. |
| MEC-21 | DOC | The enclosure section of HARDWARE.md contains none of the dimensions a case designer needs | HARDWARE.md's enclosure section has none of the dimensions a case designer needs. The STEP file now covers most of it; a short table would finish it. |
| SD-V03 | DOC | Neither HARDWARE.md nor README.md connects the battery cut-out to the card slot | Neither doc says the battery must move before the card can be ejected. You said this is fine - it just needs the sentence (goes with your HMI-V02 'battery ejection will be documented'). |
| REC-B-02 | MEDIUM (recovered) | U11's exposed pad has 4 of 6 via-in-pad vias directly under solder-paste windows; U4's 12 are correctly windowpaned | TP4056 thermal pad: 4 of 6 vias sit under paste windows (I re-measured this myself). Nudge the vias into the gaps, or accept - at <= 0.59 W it is margin, not failure. |

## Clean-ups — no decision needed, just do them when the file is next open (30)

| ID | Sev | Finding | Note |
|---|---|---|---|
| FAB-07 | LOW | Four dangling top-layer track stubs at the bottom button row | Four dangling F.Cu stubs at the bottom button row (they are the unbridged front-button tabs' tails). Delete or exclude. |
| FAB-08 | LOW | One empty, mirrored text box on the front silkscreen | One empty mirrored text box on F.Silkscreen. Delete. |
| FAB-13 | LOW | One wire carries two names (PIN_3 and TP_RST on J4 pin 3) | One wire carries two names (PIN_3 and TP_RST at J4 pin 3). Harmless; remove one label when convenient. |
| HMI-14 | LOW | Front silkscreen names the wrong switches for the front-mount tabs | Front silkscreen names the wrong switches for the front-mount tabs. Fix next time the silkscreen is touched. |
| LAY-09 | LOW | One via on the board has no net assigned | One via has no net. Delete or assign. |
| LED-09 | LOW | lib_symbol_mismatch ERC warnings on U10 and J3 - cached schematic symbols differ from their libraries | U10 and J3 cached symbols differ from their libraries. 'Update symbols from library' when convenient. |
| SD-12 | LOW | Q7's symbol, description and datasheet field are the IRLML6402's, not the AO3401A's | Q7's symbol description/datasheet are the IRLML6402's. Field tidy-up. |
| BAT-12 | DOC | Schematic note on D2 contradicts its own arithmetic, and D2 is a USB indicator inside a block titled 'Battery Charger' | Schematic note beside D2 contradicts its own arithmetic. Text fix. |
| BAT-14 | DOC | HARDWARE.md says over-current opens both protection FETs; the DW01A opens only the discharge FET | HARDWARE.md says over-current opens both FETs; the DW01A opens only the discharge FET. One-word doc fix. |
| BAT-15 | DOC | HARDWARE.md understates the residual drain that survives an over-discharge cutoff (~4 uA quoted, ~8 uA of resistors actual) | HARDWARE.md quotes ~4 uA residual drain after cut-off; resistors alone are ~8 uA. Doc fix. |
| DOCS-21 | DOC | The display part number is written three different ways across the repo and the board | Display part number is written three ways. Pick one. |
| DOCS-22 | DOC | fabrication/README.md's release-record table cites dates and a file that do not match the repository | fabrication/README.md release-record table cites dates/a file that do not match the repo. |
| EPD-V02 | DOC | Q4 and D4-D6 still carry the library symbols' Description/Datasheet fields, which describe different parts (BSS138 50 V; MBR0520 30 V/0.5 A) | Q4 and D4-D6 still carry the library symbols' description/datasheet (BSS138, MBR0520). Field tidy-up. |
| LAY-D4 | DOC | HARDWARE.md calls the bottom-centre button CONFIRM; the board silk prints OK | HARDWARE.md says CONFIRM, board silk says OK. |
| LED-07 | DOC | Three different LED currents stated in three places; only docs/HARDWARE.md is correct | LED current stated three different ways; HARDWARE.md is the correct one (13.3 mA). |
| LED-15 | DOC | The LTspice file in simulations/led_driver models a superseded discrete boost, not the TPS923610 as built | simulations/led_driver models the superseded discrete boost. Delete, or label as historical. |
| MCU-20 | DOC | Documentation calls R72 a 0 ohm jumper; it is 10 kOhm | Docs call R72 a 0 ohm jumper; it is 10 k. |
| MCU-22 | DOC | README calls SW10 a power switch; HARDWARE.md correctly calls it a wake input | README says SW10 is a power switch; it is a wake input. |
| PWR-15 | DOC | HARDWARE.md points the thermal qualification at the battery case; the worst case is USB | HARDWARE.md points thermal qualification at the battery case; worst case is USB. Doc fix. |
| PWR-16 | DOC | HARDWARE.md claims bulk capacitance can ride out a Wi-Fi TX pulse; it holds for microseconds | HARDWARE.md says bulk capacitance rides out a Wi-Fi TX pulse; it holds for microseconds. Doc fix. |
| PWR-17 | DOC | HARDWARE.md understates the battery-gauge load offset by roughly 2x | HARDWARE.md understates the battery-gauge load offset ~2x. Doc fix. |
| PWR-19 | DOC | HARDWARE.md's SD rule covers the power-off transition only and does not mention light sleep | HARDWARE.md's SD rule does not mention light sleep. Covered by the new firmware-contract bullet. |
| USB-15 | DOC | HARDWARE.md calls J1 a 14-pin receptacle; the ordered GCT USB4085-GF-A has 16 contacts | HARDWARE.md calls J1 14-pin; USB4085-GF-A has 16 contacts. |
| USB-16 | DOC | HARDWARE.md attributes hot-plug damping advice to "TI's own TP4056 datasheet"; the TP4056 is not a TI part | HARDWARE.md attributes TP4056 advice to 'TI'. Not a TI part. |
| USB-17 | DOC | HARDWARE.md's "~1 nA" TPS2116 reverse leakage is the 25 C figure only | '~1 nA' reverse leakage is the 25 C figure. |
| USB-18 | DOC | HARDWARE.md's "No battery fitted \| CHRG + STDBY \| ~0.45-0.53 V" row merges two unrelated states | HARDWARE.md's 'No battery fitted' row merges two states - rewrite with the re-evaluated logic (firmware contract has the wording). |
| USB-19 | DOC | HARDWARE.md's USB_STAT state table has no named row for ST+STDBY (0.531 V) or all-three-low (0.404 V) | State table lacks rows for the weak-USB combinations (0.53 V / 0.96 V). Same rewrite as USB-18. |
| USB-V05 | DOC | CR1's schematic symbol is out of sync with its library and is named for a different part than the one fitted | CR1's symbol is out of sync with its library. Field tidy-up. |
| REC-B-04 | DOC (recovered) | DESIGN_REVIEW.md still analyses Q3/Q8 and the Fix-4 pass FET as AO3419 | DESIGN_REVIEW.md still says AO3419 in five places; the board fits AO3401A. |
| REC-B-05 | DOC (recovered) | U12 is inconsistent across the two BOMs and has no JLC footprint model | U12 has a different prime MPN in the two BOMs; its JLC part has no footprint model, so check its rotation in JLC's preview (goes with FAB-21). |

## Done in this pass (15)

| ID | Sev | Finding | Note |
|---|---|---|---|
| BAT-V01 | LOW | Fix-4 cell detector is self-latching once the charger runs: unplugging the cell with USB present leaves the charger running into an empty connector and BAT_MONIT reading a full battery | This is the mechanism behind the no-battery blink (see USB-V02 re-evaluation). Now in HARDWARE.md firmware contract. |
| DOCS-23 | LOW | No table of contents and no quick-path / deep-dive split in the README | README restructure adds the quick path / deep-dive split. |
| MCU-05 | LOW | Touch interrupt is on GPIO41, which is not RTC-capable, so touch cannot wake from deep sleep | Documented in the firmware contract (touch cannot wake from deep sleep). |
| MEC-13 | LOW | No mechanical bootloader entry and no reachable reset with the case closed; only the BOOT half is documented | Bootloader entry (tweezers on SW6 pads) and pin-hole RESET are now documented in the README. |
| BAT-13 | DOC | HARDWARE.md documents a 'No battery fitted (blinks)' USB_STAT state that the Fix-4 CE gate makes unreachable | Covered by the USB_STAT re-evaluation: the blink state is reachable only by unplugging the cell while on USB. In the firmware contract. |
| DOCS-20 | DOC | The board silkscreen documents a board-shortening modification that no document mentions and that contradicts the BOM's DNP guidance | The board-shortening option is now described in the README. |
| LAY-D1 | DOC | HARDWARE.md 9.1.1 states the front-button solder tabs stop 0.3 mm short; the real gap is 0.151-0.188 mm | HARDWARE.md 9.1.1 now gives both numbers. |
| LAY-D2 | DOC | HARDWARE.md 6.2 claims the EPD boost loop is ~33 mm2; every measurement I can make gives 24-27 mm2 | HARDWARE.md 6.2 loop area corrected. |
| LAY-D5 | DOC | HARDWARE.md never states the board dimensions, stackup or any of the outline features | Board STEP exported to docs/mechanical/ and referenced from the README; dimensions stated. |
| LAY-D6 | DOC | The tongue-removal procedure exists only on unprintable silkscreen, not in HARDWARE.md | Tongue-removal procedure is now in the README. |
| MCU-19 | DOC | Documentation states three times that IO46 is input-only; on the ESP32-S3 it is a full bidirectional I/O | 'GPIO46 is input-only' corrected in HARDWARE.md and README. |
| USB-14 | DOC | Schematic still declares the "> 3.10 V" idle window that HARDWARE.md §3.7 explicitly warns against | Schematic note now says '> 2.60 V'. |
| REC-A-02 | MEDIUM (recovered) | Fix 4 cannot start charging a 0 V / protection-latched pack | Dead / protection-latched pack will not start charging - now in the firmware contract as a 'tell users' item. |
| REC-B-01 | MEDIUM (recovered) | Fix-4 CE gate cannot revive a 0 V or protection-latched pack | Same as REC-A-02. |
| REC-B-03 | MEDIUM (recovered) | After any DW01A protection trip the board cannot restart from the cell alone, and nothing documents it | After a protection trip the board restarts only on USB - now in the firmware contract as a 'tell users' item. |

## Withdrawn or corrected by the reviewer (10)

| ID | Sev | Finding | Note |
|---|---|---|---|
| FAB-04 | LOW | 12 live DRC clearance errors, all inside J1's own USB-C footprint | Counts reconciled - see section 11 of FINAL_REVIEW. One item (= LAY-16 = USB-10), footprint-inherent, accepted as in FAB-01. |
| FAB-V01 | LOW | 18 unfilled via-in-pad holes inside the exposed thermal pads of U4 and U11, with no plugged-via request anywhere in the ordering files | Re-checked per your method note. U4: 0 of 12 vias under paste. U11: 4 of 6 ARE under paste windows (both footprints use pad-based paste, no graphic paste, so the method holds). Now = REC-B-02, LOW. |
| HMI-13 | LOW | Front-mount solder-bridge tabs clear their rings by 0.152-0.195 mm against a 0.15 mm rule | Corrected as you asked: 0.30 mm exposed-copper to exposed-copper (your design intent - HARDWARE.md is right in that sense) and 0.151-0.188 mm copper to copper under mask. Same item as LAY-07 / LAY-D1. |
| HMI-23 | LOW | NextPCB substitute for J6 may be a male wafer, not a female socket | Refuted by you - NextPCB's export says female header. Also moot once other_fabs goes. |
| LAY-07 | LOW | Front-button solder-bridge tabs sit 0.151-0.188 mm from their rings, not the documented 0.3 mm | See HMI-13. |
| LAY-10 | LOW | Power rails are 0.25 mm where a 1 A charge current gives a 13.5 C rise; P+ has a 0.25 mm neck and B- has no vias | Premise corrected (charge current is ~0.23-0.25 A, not 1 A). The remaining 0.25 mm necks are merged into USB-06. |
| LAY-16 | LOW | All 15 DRC clearance errors are inside the fixed USB-C footprint and are netclass noise | See FAB-04. |
| LAY-V01 | LOW | The tongue's 120.2 mm2 B.Cu ground island has zero stitching vias - it is the worst case, not the button strip | Re-checked: the tongue's B.Cu island is tied to F.Cu through J6's grounded through-hole pins (thermal-relieved, which the first test missed). Withdrawn. |
| USB-10 | LOW | Sixteen J1 DRC clearance errors are footprint-inherent 0.15 mm pad gaps flagged against a 0.20 mm netclass rule | See FAB-04. |
| PWR-14 | DOC | README calls C12 the 'LDO-input capacitor'; it is the LED boost's input capacitor | Two sections disagreed; both descriptions are defensible (C12 sits on the LDO_IN net, physically at U10's VIN). The README's 'keep C12' guidance is correct. Withdrawn. |

## Pruned — already settled by an answer you gave (78)

| ID | Sev | Finding | Note |
|---|---|---|---|
| BAT-05 | LOW | No cell-temperature protection during charge: TP4056 TEMP grounded and J5 is a 2-pin connector | By design - 2-pin packs have no NTC. Same stance as your DOCS-05 / BAT-V04 answers (known-good protected pack). |
| BAT-07 | LOW | Battery path narrows to 0.25 mm either side of R27 while the rest of it is 0.40 mm | Merged into your USB-06 "worth a look": when you widen the USB path, also widen the 0.25 mm Q3-R27-Q8 link. |
| BAT-11 | LOW | J5 polarity silkscreen is correct but sits ~7 mm from the pin row, at the far end of the connector body | Silkscreen - same as your FAB-02 / LAY-04 answer (ignore). The polarity mark itself is correct. |
| BOM-10 | LOW | D3 SMAJ26A clamps above the TPS923610's absolute maximum, so it cannot protect the driver it sits beside | Same physics as USB-04 / USB-V01 - the TVS is a surge clamp, no swap brings it under abs-max. Accepted; nothing to do. |
| BOM-12 | LOW | R15 is a 10 k GDR pull-down where the SSD1677 reference specifies 1 M - a 100x heavier load on the panel's gate driver | Duplicate of EPD-05 (answer it once there). |
| BOM-13 | LOW | The three documented build routes give three different button feels spanning 2.5:1, and half the cycle life on one | Settled by HMI-10 (bottom row is actuated differently) and DOCS-13 (other-fab routes are being dropped). |
| BOM-15 | LOW | Four of nine capacitor part numbers are unbuyable at DigiKey today and the BOM gives no specification to substitute against | Same answer as BOM-02 ("will substitute if needed"). Candidates are in responses/PARTS_RESEARCH.md. |
| EPD-01 | LOW | No mechanical definition of the panel or its FPC path; reach budget has only ~5 mm slack | Panel/flex mechanics - same as your MEC-01 / MEC-06 / MEC-23 answers (fine; enclosure's job). |
| EPD-11 | LOW | J2 pad 17 (VSS) reaches the GND pour through a single thermal spoke | Thermal spokes - your FAB-06 answer (ignore). |
| EPD-V01 | LOW | Panel tail flares to 31.3 mm; C17, C22 and through-hole pads TP3/TP4/TP5 sit under it - the 'clear corridor' only covers the 12.5 mm neck | Parts under the panel tail - your MEC-23 answer (screen is buffered, need not be flat). |
| FAB-05 | LOW | The SW netclass imposes 0.250 mm clearance on J3, a connector whose pads are inherently 0.200 mm apart | J3 netclass artefact, already excluded in your project - as you said. |
| FAB-09 | LOW | 49 silkscreen DRC items: 32 clipped by the board edge, 12 printed over exposed copper, 5 overlapping each other | Silkscreen - your FAB-02 / LAY-04 answer. |
| FAB-11 | LOW | production/bom.csv contains a BOM line with no part number (TP1, TP2) | bom.csv is not the upload file (DOCS-03 / BOM-05). |
| FAB-15 | LOW | The Toolkit and the NextPCB/PCBWay centroids place the 13 through-hole parts up to 6.5 mm apart, by design | By design (your answer) - and the other-fab files are being dropped. |
| FAB-17 | LOW | Both hand-made JLC BOMs list the 10 DNP parts as rows with a blank part number | By design, no exposure (your answer; I checked positions.csv - agreed). |
| FAB-18 | LOW | placement/silkscreen_pcb-top-pos.csv is a header-only file, and the whole placement/ folder is untracked in git | By design (your answer). |
| FAB-19 | LOW | PCBWay's BOM and PCBWay's placement file do not cover the same parts (162 vs 149) | Other-fab files are being dropped (DOCS-13). |
| HMI-08 | LOW | ESD/TVS ground pads connect to the pour through a single thermal spoke, two to isolated islands | Thermal spokes - FAB-06 answer. |
| HMI-16 | LOW | D3's clamping voltage exceeds the TPS923610's VOUT absolute maximum | Same as BOM-10 (surge clamp, accepted). |
| HMI-17 | LOW | MJTP1117 BOM rows pair an APEM MPN with a SHOU HAN LCSC code without saying so | By design (your answer). Your suggested one-line BOM note is on the to-do list. |
| HMI-21 | LOW | J6 is a right-angle socket overhanging the top edge, with pin labels only on the opposite face | J6 overhang - enclosure's problem (MEC-04 stance). |
| HMI-24 | LOW | DS3231MZ is the most expensive IC here but is wired to deliver only accuracy | RTC usage - your BOM-07 / HMI-03 / HMI-04 answers. |
| HMI-V06 | LOW | The front silkscreen's actuator marks on the four bottom switches sit outside the switch body | Silkscreen. |
| LAY-06 | LOW | 25 GND pads are starved thermals, including the USB-C ground pad, the charger, the LDO and the power-path mux | Thermal spokes - FAB-06 answer. |
| LAY-11 | LOW | The small GND pour at the front-light boost has zero vias to the F.Cu plane | Your LAY-05 answer - and my re-check agrees (see FINAL_REVIEW section 11). |
| LAY-12 | LOW | Silkscreen collisions: references printed over each other and over exposed pads, which mask-clipping will erase | Silkscreen. |
| LAY-13 | LOW | The dashed cut-line textbox is mirrored on the front silk layer and overhangs the board edge by 3 mm | The cut-line text box - you are reworking that area anyway (one slot + battery disclaimer). |
| LAY-14 | LOW | J6 pin-label table uses a 2.77 mm column pitch against the header's 2.54 mm pitch | Silkscreen. |
| LAY-17 | LOW | Four mechanical overhangs and one recess the enclosure must accommodate | Overhangs - enclosure's problem. |
| LED-03 | LOW | LED+ on expansion header J6 is a low-impedance path to the battery rail; a short to ground destroys L2 | J6 exposure - part of the HMI-01 decision. |
| LED-04 | LOW | 24.5 V driver leaves only ~2 V of OVP headroom for the 22 V string the silkscreen invites | Your LED-V02 answer: firmware watches LED_MONIT and never lets OVP trip. |
| LED-08 | LOW | Three KiCad DRC clearance errors at J3 are netclass artefacts, not real spacing problems | Same as FAB-05. |
| LED-10 | LOW | Starved thermal relief on the GND pads of R37, R41 and R50 (one spoke instead of two) | Thermal spokes - FAB-06. |
| LED-V01 | LOW | D3 (SMAJ26A) clamps at 42.1 V, above U10's 32 V VOUT absolute maximum - the TVS guarding the exposed LED+ pin cannot keep the driver inside its ratings during a real surge | Same as BOM-10. |
| LED-V05 | LOW | The two most likely accidental shorts on J6 destroy R37 (the current-sense resistor), not L2 - and both fault pins are nearest neighbours of LED+ | Part of the HMI-01 / J6 decision. |
| MCU-03 | LOW | DS3231 INT/SQW is a no-connect — the external RTC cannot wake the MCU | By design (your HMI-04 answer). |
| MCU-04 | LOW | All three spare GPIOs on the expansion header are strapping pins; GPIO3 has no pull at all | Strapping pins on J6 - see the HMI-02 explanation. |
| MCU-11 | LOW | U4 silkscreen outline is clipped by the antenna notch | Silkscreen. |
| MCU-15 | LOW | No ground stitching vias anywhere near the antenna cut-out or around the module | Your MCU-14 answer (accepted RF risk). |
| MEC-08 | LOW | Button plunger protrusion is inconsistent between groups — bottom row +1.95 mm, side buttons +0.95 to +1.21 mm | Your HMI-10 answer. |
| MEC-12 | LOW | J6 is a right-angle socket whose mouth faces out of the top edge and whose body overhangs it by 1.69 mm — undocumented | Enclosure's problem. |
| MEC-14 | LOW | The right board edge is unsupported for 73.25 mm between H5 and H4 while carrying four buttons, the USB port and the status LED | Enclosure's problem. |
| MEC-15 | LOW | microSD card exits toward the left wall from a mouth 11.89 mm inside the edge; socket fit is still an open item | Your SD-05 / SD-V01 answers. |
| MEC-16 | LOW | The spare front-light output pads TP3/TP4/TP5 are through-holes sitting under the display panel | Your MEC-23 answer. |
| MEC-17 | LOW | Flex tail slack is only 2.5–4.1 mm and the panel tail length could not be verified from a printed dimension | Your MEC-01 / MEC-06 answers. |
| MEC-19 | LOW | Status LED D2 is on the back face 0.59 mm from the right edge — it lights the inside of the case and will glow through the seam | D2 light leak - enclosure's problem. |
| PWR-02 | LOW | Coincident Wi-Fi TX + SD write + e-paper refresh (~515 mA) sits only ~8% under the LDO's 560 mA minimum, foldback current limit | Your USB-05 answer (not everything is active at once). |
| PWR-05 | LOW | U3's GND pad (and C21's) reaches the ground pour through a single thermal spoke | Thermal spokes - FAB-06. |
| PWR-11 | LOW | USB_VBUS is narrower (0.25 mm) than the battery path it parallels (0.4 mm) despite carrying charger plus system current | Duplicate of USB-06. |
| PWR-V01 | LOW | The Q3 -> R27 -> Q8 link in the battery path was left at 0.25 mm when the rest of the path was widened to 0.4 mm | Duplicate of BAT-07 -> merged into USB-06. |
| SD-09 | LOW | J7's ground and shield pads reach the GND zone through a single thermal spoke | Thermal spokes - FAB-06. |
| SD-V04 | LOW | U9's ground pad reaches the GND zone through a single thermal spoke - the ESD array's own discharge return | Thermal spokes - FAB-06. |
| USB-07 | LOW | U6 ESD array hangs off a ~9.6 mm stub from the connector instead of sitting on the data line | ESD placement - same stance as your SD-02 answer. |
| USB-11 | LOW | J1 silkscreen is clipped by the board edge and the connector body overhangs the outline by 1.72 mm | Silkscreen. |
| USB-V03 | LOW | F1's MPN and LCSC fields name two different manufacturers' parts | Same prime-vs-LCSC convention as your SD-04 / HMI-17 answers. |
| BAT-V03 | DOC | Manufacturer/datasheet fields for U5 and Q1 do not match the parts their LCSC codes deliver | Prime-vs-LCSC convention (your SD-04 answer). Only residue: U5's Manufacturer field still says Fortune while the code ships PUOLOP - tidy if you care. |
| EPD-12 | DOC | Silkscreen clipped on J2's outline, and the key build warning sits where the FPC will cover it | Silkscreen. |
| MEC-22 | DOC | Nearly all front silkscreen is under the panel, and the J6 pinout label also runs 5.46 mm off the board | Silkscreen. |
| EPD-13 | CERT-LATER | Minimum 0.201 mm copper gaps between the +/-20 V nets and their neighbours | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| EPD-14 | CERT-LATER | The boost pulls pulsed current from the shared 3V3 rail that also feeds the panel's VCI | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| HMI-18 | CERT-LATER | U7 sits 8.3 mm from J4, and open ladder legs leave floating stubs up to 64 mm long | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C1 | CERT-LATER | Front-light taps to J6 form a ~170 mm out-and-back loop on PWM-switched nets, mostly on the ground-plane layer | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C2 | CERT-LATER | I2C runs 179/184 mm with ~110 mm of each on the top-layer ground plane | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C3 | CERT-LATER | 68 GND stitching vias and no edge via fence on a 60 x 111 mm 2-layer board | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C4 | CERT-LATER | USB differential pair has asymmetric via counts (DP 3 vias, DN 1 via) | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C5 | CERT-LATER | Narrow single-point-connected GND slivers on F.Cu act as resonant stubs | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C6 | CERT-LATER | The ESP32 antenna sits in a recess with ground pour ~0.5 mm away on three sides | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LAY-C7 | CERT-LATER | SD bus length skew of 23.6 mm between SD_CLK and SD_DAT1 | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| LED-11 | CERT-LATER | 25 V, 1.1 MHz-rippled LED nets routed ~180 mm across the board on the outer layer | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| MCU-12 | CERT-LATER | No series resistor on U0TXD | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| PWR-13 | CERT-LATER | LDO input/output loops and ground returns are routed for convenience, not for loop area | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| SD-14 | CERT-LATER | 33 Ohm series resistors are well below the ~138 Ohm trace impedance, so the bus is under-damped - and HARDWARE.md states the opposite | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| SD-V02 | CERT-LATER | The F.Cu ground pour under the socket and the SD bus is cut by several signal traces (the original review's 'continuous return path' is wrong) | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| USB-12 | CERT-LATER | D+/D- are not impedance-controlled, via-asymmetric and 46 mm long; U6's CC channels have only 5.5 V standoff | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| USB-13 | CERT-LATER | Shield RC network is 20.4 mm of thin trace from the shell pad and the shell is DC-isolated by 1 MΩ | Parked by your own standard (EMC/certification only). No response needed for a prototype. |
| REC-C-02 | LOW (recovered) | SW6 carries flags=dnp without exclude_from_bom - a third DNP leak that HMI-V01 does not list | Your HMI-V01 answer: set exclude-from-BOM on R72, R74 and SW6 in the next revision. |
| REC-C-05 | LOW (recovered) | The documented button mechanics do not hold for the NextPCB build route | NextPCB substitute switch depth - moot once other_fabs goes (DOCS-13). |
| REC-A-05 | CERT-LATER (recovered) | No USB D+/D- series-damping footprints, contrary to Espressif's schematic checklist | CERT-LATER. |

## Information only — no action expected (76)

| ID | Sev | Finding | Note |
|---|---|---|---|
| BAT-06 | LOW | DW01A/FS8205A over-current trip computes to 2.0-4.6 A - a short-circuit protection, not an overload protection | Over-current trip is 2-4.6 A, i.e. short-circuit protection only. Informational. |
| BAT-08 | LOW | DW01A GND reference taps the B- run ~8 mm upstream of Q1's S1 pad, putting trace resistance inside the current-sense loop | DW01A sense tap 8 mm upstream - small sense error, no action. |
| BAT-10 | LOW | On a battery-only cold start the DW01A measures the cell through Q8's body diode and reads it ~0.4 V low | Cold-start reads the cell ~0.4 V low through Q8's body diode until Q8 turns on. Informational. |
| BAT-V02 | LOW | Q3 provides no reverse-polarity blocking as oriented; Q8 alone does the job | Supports your BAT-03 answer in effect: the reverse path IS blocked (by Q8; Q3 is oriented so its body diode conducts toward the cell). |
| BOM-11 | LOW | R14 is a 100 mW 0603 carrying the EPD boost's switched inductor current; wattage unverified | R14 dissipation unverified; average boost current is small. Bring-up: touch-test R14 during a refresh. |
| BOM-14 | LOW | The L1 substitute is materially worse than the prime part and the substitutes file justifies it only on case size | JLC's L1 (Sunltech) has 2.4x the DCR and 0.94 A Isat vs 1.1 A - still well above the 0.5 A need. Informational. |
| BOM-16 | LOW | The public JLC search API never reports the fee-free Preferred class, so any re-crawl over-counts Extended parts and over-states fees | Note about the JLC search API not reporting 'Preferred' parts. Informational. |
| BOM-V02 | LOW | ESP32 module variant, Hirose FH34 connectors and the expansion socket were priced but not cost-critiqued | Module / Hirose / header were priced but not cost-critiqued. Informational. |
| EPD-03 | LOW | Q4 sits at 20.9 V of a 30 V rating with no snubber and unmeasured switch-node ringing | Q4 at 20.9 V of 30 V, ringing unmeasured. Bring-up scope check only. |
| EPD-04 | LOW | Panel decoupling and rail-stabilising capacitors are 13-20 mm from the pins they serve | Decoupling 13-20 mm from the connector. Works per reference; CERT-LATER flavour. |
| EPD-07 | LOW | The +/-20 V reservoir caps are 8-9 mm and 2 vias from their rectifiers, so the diodes have no local capacitor | Reservoir caps 8-9 mm from their rectifiers. Informational. |
| EPD-08 | LOW | J2 pins 6/7 labelled TSCL/TSDA and left open; touch is assumed to be on a separate 6-pin tail | J2 pins 6/7 (TSCL/TSDA) left open by design. |
| EPD-09 | LOW | D4/D5/D6 use 1N5819HW, whose reverse leakage is several times the reference MBR0530's | 1N5819HW leaks more than MBR0530. Informational. |
| EPD-10 | LOW | Seven vias sit under J2's body or in the corridor the FPC lies on | Seven vias under J2 / the flex corridor. They are tented; informational. |
| FAB-12 | LOW | 25 footprints differ from their library copy, and the check that reports this is switched off | 25 footprints differ from their library copies (expected for locally edited footprints). |
| FAB-20 | LOW | The board's minimum-track-width constraint is set to 0.000 mm, so KiCad never checks track width | Min-track-width DRC constraint is 0. No effect on this board (min track is 0.20 mm). |
| HMI-05 | LOW | Two-button chords on ladder 1 are only 24-41 mV apart worst case | Two-button chords are 24-41 mV apart. Only matters if firmware wants chords. |
| HMI-06 | LOW | Only two of eight buttons produce a valid logic level for deep-sleep wake | Only two buttons can wake from deep sleep at logic level. Firmware fact. |
| HMI-09 | LOW | GPIO46's ESD clamp is 25 mm away at the SD card, behind 93 mm of routed track | GPIO46's clamp is far away. CERT-LATER flavour. |
| HMI-11 | LOW | D8 uses a project-local D_TVS_Dual_ACA whose pin 3 is common, unlike the stock KiCad symbol | Project-local D8 symbol pin order differs from stock KiCad. Correct as drawn. |
| HMI-12 | LOW | J4 pin 2 has neither an ESD clamp nor any local decoupling capacitor | J4 pin 2 has no clamp/decoupling. Informational. |
| HMI-15 | LOW | Released-state ladder voltage saturates the ADC, so it cannot be used as a rail reference | Released ladder level saturates the ADC. Firmware fact. |
| HMI-19 | LOW | DS3231M powers up with EN32KHZ set, above the quoted timekeeping current | DS3231M powers up with the 32 kHz output enabled; firmware should clear EN32kHz to get the quoted current. |
| HMI-V04 | LOW | J6 exposes 3V3 and the I2C bus with no series resistance or current limit, unlike the three GPIOs | 3V3 and I2C reach J6 with no series element. Same family as HMI-01/HMI-02; see the explanation there. |
| HMI-V05 | LOW | The top three ladder-2 codes sit above 2.5 V, in the ESP32-S3 SAR's compressed region | Top three ladder-2 codes sit in the ADC's compressed region. Firmware: use calibrated reads. |
| LAY-08 | LOW | LDO_IN reaches the front-light boost through 125.5 mOhm of 0.25 mm track, 56 mm of it on the top layer | LDO_IN to the LED boost is 125 mOhm of 0.25 mm track. Fine at 13 mA LED current. |
| LAY-15 | LOW | Eighteen footprint thermal vias use a 0.20 mm drill, the smallest holes on the board | 0.20 mm thermal-via drills are the smallest holes on the board; within JLC capability. |
| LAY-V02 | LOW | The charger is programmed for about 255 mA, not the 1 A the layout analysis assumed throughout | Charge current ~0.23-0.25 A. |
| LED-05 | LOW | C9 effective capacitance at operating bias sits close to TI's 1 uF minimum for loop stability | C9 effective capacitance near TI's 1 uF minimum at bias. It was raised to 4.7 uF already. |
| LED-06 | LOW | LED_MONIT presents 107 kOhm to the ESP32 SAR ADC, ~10x the recommended source impedance | LED_MONIT source impedance 107 k. Firmware: average several reads. |
| LED-13 | LOW | TP3 puts up to 25 V on an exposed top-side pad in the visible decorative area | TP3 (DNP) would carry 25 V on a top-side pad. Only if fitted. |
| LED-V03 | LOW | The 13.33 mA set point holds only at 100 % duty - reference tolerance widens to -28 %/+26 % at 10 % duty, so dim settings are far less accurate than the headline number | LED current tolerance widens at low duty. Firmware/UX fact. |
| LED-V04 | LOW | COLOR_SEL and PWM_LED occupy two of the four ESP32-S3 JTAG pins, so an external JTAG probe and a working front light are mutually exclusive | COLOR_SEL / PWM_LED sit on JTAG pins; native USB JTAG still works. |
| MCU-06 | LOW | SD power gate gets a 60 us on-pulse at power-up, and the net name implies the wrong polarity | SD gate sees a 60 us on-pulse at power-up. Harmless. |
| MCU-07 | LOW | All four JTAG pins reused for board functions — no hardware JTAG probe possible | JTAG pins reused; native USB JTAG covers it. |
| MCU-08 | LOW | Front-light enable/PWM line is held off only by the driver's 600 kOhm internal pull-down while the MCU is in reset | ADIM held low only by the driver's internal 600 k during reset. OK. |
| MCU-09 | LOW | I2C bus is 184 mm / 179 mm of 0.2 mm track with 5-6 vias each | I2C is ~180 mm long. Works at 100/400 kHz with 2.2 k pull-ups. |
| MCU-10 | LOW | UART test points TP1/TP2 have no ground pad next to them | No ground pad beside TP1/TP2. Convenience. |
| MCU-16 | LOW | The 0.1 uF decoupling cap is farther from the module supply pin than the 22 uF bulk cap | 0.1 uF further from the module pin than the 22 uF. The module has its own internal decoupling. |
| MCU-17 | LOW | 3V3 feed to the module is 0.25 mm wide, well under Espressif's 25 mil guidance | 3V3 feed is 0.25 mm (~40 mV at peak). Consider widening in the same pass as USB-06. |
| MCU-18 | LOW | Unused octal-PSRAM pads sit directly between GPIO0 and I2C_SDA on the same pad row | Unused PSRAM pads between GPIO0 and SDA. Informational. |
| MCU-V01 | LOW | Nothing tells a hand-assembler that the module's centre ground pad (EPAD, pin 41) is optional to solder | EPAD soldering is optional for hand assembly. Could be one README line. |
| MEC-10 | LOW | The bottom bezel is a 5.75 mm wide, 47 mm long bridge carrying four through-hole buttons | Bottom bezel is a 5.75 x 47 mm bridge. Support it in the case. |
| MEC-11 | LOW | Optional front-mounted MJTP1243 buttons overlap the panel's footprint by 0.30 mm and need 4.3 mm of front cavity | Optional front buttons need 4.3 mm of front cavity. |
| MEC-18 | LOW | Four different corner radii on the outline | Four different corner radii. Cosmetic. |
| PWR-04 | LOW | Wi-Fi TX drops 3V3 below the ESP32-S3's 3.0 V minimum at ~3.2-3.3 V of cell; the default brown-out detector can never fire | 3V3 sags below 3.0 V on Wi-Fi TX under ~3.2-3.3 V of cell. Firmware: stop Wi-Fi below ~3.4 V. |
| PWR-06 | LOW | USB_VBUS has no bleeder and can be floated up by leakage into the unpowered TP4056 status pins, and it drives the mux's MODE pin | Bring-up check: on battery only, USB_VBUS should read ~0 V and D2 stay dark. |
| PWR-09 | LOW | The 0.1 uF module decoupling cap is further from the ESP32's 3V3 pad than the 22 uF bulk cap | Duplicate of MCU-16. |
| PWR-10 | LOW | 3V3 is 0.25 mm everywhere including the long trunk from the LDO to the module, costing ~40 mV at peak load | Duplicate of MCU-17. |
| PWR-18 | LOW | HARDWARE.md's USB_STAT ladder assumes the TP4056 status pins are true high-Z with VCC at 0 V - unverified | Bring-up check (same measurement as PWR-06). |
| PWR-V02 | LOW | TP4056 CE pin is driven hard to 3V3 (no series resistor) while the charger's VCC is 0 V on battery - the stiff, unexamined back-feed path in the sleep budget | Bring-up check (same measurement as PWR-06). |
| SD-03 | LOW | Dual-source footprint leaves four unused shell ground lands with solder-paste apertures whichever socket is fitted | Re-checked per your method note: J7 uses pad-based paste (no graphic paste), so the finding stands as written - four unused shell lands get paste whichever socket is fitted. Harmless solder dots. |
| SD-06 | LOW | Card-detect is discarded: the socket's detect terminal is tied to GND with the shell | Card-detect not used. By design. |
| SD-07 | LOW | The tight locating slot is only 0.05 mm wider than the TF PUSH's recommended peg hole and sits at the minimum routed-slot width | J7 locating slot is tight but both sockets were shown to fit. |
| SD-08 | LOW | The GCT body keep-out is drawn as a rule area on the F.SilkS layer, so it enforces nothing | Keep-out drawn on a silk layer enforces nothing. Cosmetic. |
| SD-10 | LOW | A clean SD power-cycle needs about 0.4 s if the bus is left high-impedance | Clean SD power-cycle needs ~0.4 s. Firmware fact (in the contract). |
| SD-11 | LOW | Local SD_VDD bulk is 1.1 uF, below the ~10 uF typically shown in SD host reference designs | 1.1 uF local bulk on SD_VDD. Works with most cards; if a card browns out at init, add bulk. |
| SD-13 | LOW | The SDMMC schematic block shows ESD protection for only four of the six bus lines | Schematic block shows 4 of 6 ESD channels; the other two are on U9. |
| SD-15 | LOW | IO10 has a documented 60 us low-level power-up glitch that briefly switches the card on at every cold boot, contradicting HARDWARE.md | Same 60 us glitch as MCU-06. |
| SD-16 | LOW | SD_CMD and SD_DAT3 occupy GPIO15/GPIO16, the ESP32-S3's only 32.768 kHz crystal pins | SD_CMD/DAT3 use the 32 kHz crystal pins - irrelevant, you have an external RTC. |
| USB-09 | LOW | CR1 sits on the cable side of F1, so a shorted TVS is not current-limited by the fuse | CR1 sits on the cable side of F1. Informational. |
| USB-20 | LOW | C23 is 2.2 nF but the ESP32-S3's published ADC accuracy is specified with 100 nF on the input | C23 is 2.2 nF vs Espressif's 100 nF for published ADC accuracy. Firmware: average. |
| USB-V04 | LOW | TPS2116 recommends ~100 uF on VOUT where reverse-current blocking is expected; the board has 26.7 uF and enters RCB on every unplug | TPS2116 suggests ~100 uF on VOUT; board has ~27 uF. Works; informational. |
| REC-C-01 | LOW (recovered) | Q5/Q6 colour-select pair has no guaranteed non-overlap, and nobody has measured it | Bring-up check or next-revision clean-up; no decision needed. |
| REC-C-03 | LOW (recovered) | The deep-sleep budget assumes TI's LDO quiescent current, and fabs substitute the brand | Bring-up check or next-revision clean-up; no decision needed. |
| REC-C-04 | LOW (recovered) | CR2/CR3 cannot hold the 3V3 or battery rails inside the absolute maximum of what they protect on J6 | Bring-up check or next-revision clean-up; no decision needed. |
| REC-A-01 | MEDIUM (recovered) | No VBUS-sense input: a self-powered USB device with nothing to monitor | No digital VBUS-present signal. Your earlier review accepted it; now stated in the firmware contract. |
| REC-A-03 | LOW (recovered) | U10's current limit and the C9 hot-plug inrush both exceed L2's saturation rating | Bring-up check or next-revision clean-up; no decision needed. |
| REC-A-04 | LOW (recovered) | Q7 switches SD_VDD on in microseconds - far faster than the SD spec's suggested VDD ramp | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-06 | LOW (recovered) | Several 0603 passives sit 0.24-0.60 mm from the routed board edge | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-07 | LOW (recovered) | 0.14 mm dangling copper tail on the PREVGH (15-22 V) net | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-08 | LOW (recovered) | J2's shield/mount pads are 1.5 x 1.5 mm where Hirose's land is 0.4 x 0.9 mm, so pasted copper runs under the housing | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-09 | LOW (recovered) | U10's custom DRL0006A footprint uses 0.229 mm-wide pads against TI's 0.30 mm example land pattern | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-10 | LOW (recovered) | EPD rail capacitors C11/C13-C17 retain only about 0.7-1.1 uF of their 4.7 uF at 15-22 V | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-11 | LOW (recovered) | L2's saturation current is below the TPS923610's cycle-by-cycle current limit | Bring-up check or next-revision clean-up; no decision needed. |
| REC-B-12 | LOW (recovered) | Silkscreen and mechanical cosmetics the new audit dropped | Bring-up check or next-revision clean-up; no decision needed. |
