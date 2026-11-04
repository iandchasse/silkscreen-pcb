<!-- Collected 2026-11-03 by a research pass for docs/audit-2026-11-03/TRACE_AUDIT.md. Values are quoted from the
     linked sources unless marked (computed); IPC-2221B values come from two public transcriptions (the standard
     itself is paywalled). Notes: in IPC labels A6 = uncoated component leads, A7 = conformal-coated. -->

# Layout audit reference numbers — 2-layer, 1.6 mm, 1 oz FR-4 ESP32-S3 e-reader (JLCPCB)

Compiled 2026-11-03. Every value is quoted from the cited source unless marked **(computed)**.
"Not verified" = no primary source found or the source was unreachable. PDF page numbers are the printed page numbers.

## Summary table

| # | Item | Number(s) | Src |
|---|---|---|---|
| 1 | IPC-2221B T6-1 **B2** ext. uncoated ≤3050 m (0–15 / 16–30 / 31–50 / 51–100 V) | **0.10 / 0.10 / 0.60 / 0.60 mm** | EMA, T61 |
| 1 | **B4** ext. conductors, permanent polymer coating | 0.05 / 0.05 / 0.13 / 0.13 mm | EMA, T61 |
| 1 | **A6** ext. component lead/termination, **uncoated**, ≤3050 m | 0.13 / 0.25 / 0.40 / 0.50 mm | EMA, T61 |
| 1 | **A7** ext. component lead/termination, **conformal-coated** | 0.13 / 0.13 / 0.13 / 0.13 mm | EMA, T61 |
| 2 | IPC-2221 trace current | I = k·ΔT^0.44·A^0.725 (A mil², ΔT °C); k = 0.048 ext / 0.024 int | APCB |
| 2 | 1 oz external trace, ΔT 10 °C (computed) | 0.25 mm ≈ 0.88 A · 0.5 mm ≈ 1.45 A · 1.0 mm ≈ 2.4 A | APCB |
| 2 | Via 0.3 mm drill / 25 µm (computed) | ≈1.7 A @ΔT10 · ≈2.3 A @ΔT20; JLC 18 µm avg plating → ≈1.35 / 1.8 A | CC, JLC |
| 3 | ESP32-S3-WROOM-1 antenna | antenna area 18×6 mm; clearance ≥15 mm beside antenna (non-feed side); board ≤2 mm past module on feed side; ≥15 mm clearance all round in housing | ESP, WROOM |
| 4 | TPS923610 / DRL0006A | fSW 1.1 MHz; land 6×(0.67×0.30) mm, 0.5 pitch, 1.48 mm pad-centre span, NSMD (mask ≤0.05 mm); stencil 1:1 @ 0.1 mm | TPS |
| 5 | SSD1677 / GDEQ0426T82 boost | **no published layout notes**; ref 47 µH, Si1308EDL (GD) / Si1304BDL (SSL), 3× MBR0530, 2.2 Ω sense | GD, SSD |
| 6 | USB 2.0 FS D+/D− | 90 Ω ±10 % (Espressif); FS edges 4–20 ns; TI: skew ≤50 mil, 0 stubs, ≤4 vias; ESD at connector | ESP, TUSB, SPRAAR7 |
| 7 | SD / SDIO | ±50 mil vs CLK, 50 Ω ±10 %, ≤2000 mil, no layer change (Espressif); 2-layer: CLK series-R ≤400 mil from driver, CLK ≤1000 mil (Microchip) | ESP, AN1418 |
| 8 | JLCPCB 2-layer 1 oz | trace/space 0.10/0.10 mm; via 0.15/0.25 mm min (0.20 hole preferred); PTH ring 0.25 rec/0.18 min; mask web 0.10 mm (green, red, yellow, blue, purple) / 0.13 mm (black, white); Cu–routed edge ≥0.20 mm (V-cut ≥0.40) | JLC |
| 9 | Mounting/mechanical | M2 DIN965 head Ø3.8 (KiCad courtyard Ø4.3); NPTH Cu ≥0.2–0.3 mm, more under metal head/washer; MLCC "e.g. 10 mm or more" from screw holes/edges | KICAD, NPTH, MUR1 |
| 10 | EMI | edge ground-ring via pitch ≤5 mm (Infineon); λ/20 @2.4 GHz = 2.9 mm in FR-4 / 6.2 mm in air (computed) | IFX |

## 1. IPC-2221B Table 6-1 — electrical conductor spacing (mm)

| V (DC / AC peak) | B2 | B4 | A6 | A7 |
|---|---|---|---|---|
| 0–15 | 0.10 | 0.05 | 0.13 | 0.13 |
| 16–30 | 0.10 | 0.05 | 0.25 | 0.13 |
| 31–50 | 0.60 | 0.13 | 0.40 | 0.13 |
| 51–100 | 0.60 | 0.13 | 0.50 | 0.13 |

- **Column definitions** (EMA):
  - B2 = uncoated external conductors, ≤3050 m.
  - B4 = polymer-coated external conductors, any elevation.
  - A6 = uncoated external component lead/termination, ≤3050 m.
  - A7 = conformal-coated external component lead/termination, any elevation.
  - ⚠ The request had A6/A7 swapped. The values above follow the IPC labels.
- **Sources:** two transcriptions agree (EMA; T61, which calls itself "not an official IPC table"). IPC-2221B itself is paywalled and was not read.
- **B4 and solder mask:** Sierra Circuits' calculator labels B4 "External conductors SM (solder mask) coated" (SIERRA). Treat mask-covered traces as B4. Exposed pads and untented vias fall under B2 (conductors) or A6 (leads).
- **Revision:** IPC-2221C (Dec 2023) supersedes 2221B and revises "minimum electrical clearance" (DIN). Rev C values not checked.
- **This board:**
  - SSD1677 VGH is 15–20 V and VGL = −VGH (SSD, Features). Up to about 40 V can sit between the VGH/VGL nets, so use the 31–50 V row: B2 0.60, B4 0.13, A6 0.40 mm.
  - TPS923610 VOUT is ≤24.5 V (TPS p.1), so use the 16–30 V row: B2 0.10, A6 0.25 mm.

## 2. Current capacity (traces and vias)

- **Formula** (APCB): I = 0.048·ΔT^0.44·A^0.725 for external layers (internal k = 0.024). A is in mil²; 1 oz = 1.378 mil thick.
  - smps.us calls this the fit of IPC-2221B Fig. 6-4 (SMPS).
  - The source charts only cover ≤35 A, ≤0.4 in width, ΔT 10–100 °C and 0.5–3 oz.
  - "In vacuum, or in a potted assembly, you should use the internal layer guidelines even for the external layers" (APCB).
- **(computed) 1 oz external, ΔT 10 / 20 °C:** 0.20 mm 0.74/1.01 A · 0.30 mm 1.00/1.36 A · 0.50 mm 1.45/1.96 A · 1.0 mm 2.39/3.24 A.
- **IPC-2152 vs IPC-2221 for external traces:**
  - smps.us: "the old PCB design standard overstated current carrying capacity of external tracks". So IPC-2221 external sizing can be non-conservative on small boards without planes, while the old internal chart was conservative.
  - smps.us also: boards <70 mil thick without a plane may run hotter than IPC-2152 Fig. 5-2 predicts. This board is 63 mil.
  - Altium/Jouppi: IPC-2152 nomographs "tend to overestimate the PCB trace width" (conservative) on real boards with planes (ALT).
  - **(computed, smps.us IPC-2152 fit, ΔT 10 °C):** at 1 A both need about the same area (15.5 vs 16.3 mil²). IPC-2152 needs 1.29× the area at 2 A and 1.53× at 3 A.
- **Via (computed)** using the circuitcalculator method (CC): A = π·(d_inner + t)·t, then the IPC-2221 external formula, ρ = 1.9 µΩ·cm.
  - 0.3 mm drill, 25 µm plating (ID 0.25 mm): A = 33.5 mil² → **1.69 A @ΔT10, 2.29 A @ΔT20**; R ≈ 1.4 mΩ per 1.6 mm barrel.
  - If 0.3 mm is the finished hole: 1.90 / 2.58 A.
  - JLCPCB's "Average Hole Plating Thickness 18 μm" (JLC) gives 1.35 / 1.83 A and ≈1.9 mΩ.
  - Espressif: use at least two vias where a main power trace changes layers (ESP).

## 3. ESP32-S3-WROOM-1 placement and antenna keep-out

- **Preferred placement** (ESP §Positioning a Module): antenna outside the base board, feed point close to the edge. The ✓ positions are corner placements with the antenna overhanging.
- **If the antenna can't overhang** (ESP):
  - Keep the feed point at the edge.
  - "Cut off the base board on both sides of the antenna and below it."
  - "The module should not be placed in the center of the board with clearance created by hollowing out on all four sides."
  - Add "sufficient ground copper and dense ground vias" on the base board near the antenna.
- **Keep-out figure, mm** (ESPFIG):
  - The clearance (no board material) spans the 6 mm antenna height.
  - It extends **≥15 mm** past the module on the non-feed side.
  - The board may extend **≤2 mm** past the module on the feed side.
  - "Max 1" between the module end and the board-edge line — I read this as the module inset ≤1 mm.
- **In the housing:** "A clearance of at least 15 mm is recommended in all directions" (ESP).
- **RF section:** keep USB, USB-to-serial and UART lines, test points and headers as far from the antenna as possible (ESP §RF).
- **Datasheet v1.8** (WROOM):
  - Fig. 11-1 (p.45): module 18×25.5 mm with an 18×6 mm "Antenna Area" at the top.
  - §11.2 (p.46) defers to the hardware design guidelines.
  - p.10: WROOM-1U "has no antenna keepout zone".
- **Two-layer, chip-level advice:** "complete GND plane for the chip, RF, and crystal"; bottom layer: no components, minimal traces (ESP §General).

## 4. TI TPS923610 (SNVSCN8B, Rev B, Oct 2026)

- **§8.5.1 Layout Guidelines** (p.19):
  1. COUT close to VOUT, with its ground close to the GND pin, because large ground return current flows there.
  2. FB resistor (RSET) close to the FB and GND pins.
  3. SW-to-inductor connection "as short and wide as possible".
  4. CIN close to the VIN and GND pins; "if possible, choose a capacitance of higher value".
  5. Signal ground on short traces separate from power ground, tied at a single point near GND.
- **Fig. 8-12** (p.20):
  - VOUT–COUT–GND: minimum parasitic inductance (spikes/ringing).
  - SW–L: minimum parasitic resistance (efficiency).
  - FB–RSET–GND: minimum parasitic resistance (current accuracy).
- **Ratings:** fSW is 1.1 MHz for TPS923610DRLR, 0.4 MHz for the LS variants (p.5). Switch current limit 1.8 A; LED string up to 24.5 V (p.1).
- **DRL0006A** (drawing 4223266/F, pp.29–31):
  - Land pattern: **6×(0.67×0.30) mm pads, 4×0.5 mm pitch, 1.48 mm pad-centre span**, R0.05 corners.
  - Solder mask: NSMD preferred (opening ≤0.05 mm around the pad); SMD alternative (≥0.05 mm mask overlap).
  - Stencil: 1:1 apertures 6×(0.67×0.30) mm, "based on 0.1 mm thick stencil". IPC-7351/7525 may give alternates.
  - Package: lead span 1.5–1.7 mm, lead width 0.15–0.27 mm, foot 0.2–0.4 mm, 0.6 mm max height.

## 5. SSD1677 / GDEQ0426T82 external boost

- **GDEQ0426T82 spec §8.2 "Reference Circuit"** (p.11/23, GD):
  - L1 47 µH 500 mA ("refer to NR3015").
  - Q1 Si1308EDL: VDS ≥30 V, Vgs(th) ≤1.5 V, RDS(on) ≤400 mΩ.
  - D1–D3 MBR0530: ≥30 V, ≥500 mA, VF ≤430 mV.
  - R2 2.2 Ω sense on RESE; R1 1 MΩ gate pull-down.
  - Caps 0603/0805 X5R/X7R, ≥25 V.
  - A full-text search of the spec found **no layout guidance**.
- **SSD1677 Rev 1.0 §13** (SSD):
  - L1 47 µH (CDRH2D18/LDNP-470NC), Q1 Si1304BDL, D1–D3 MBR0530, R1 2.2 Ω 0805 1 %, C2–C7 4.7 µF 0805 25 V.
  - "Component value is subjected to change and depends on panel loading."
  - No layout section.
- **Inference (not vendor-stated):** apply the TPS923610 boost-loop rules above. Keep the switch node (inductor, MOSFET drain, diodes) small and the sense-resistor path to GND short.

## 6. USB 2.0 full-speed (the ESP32-S3 USB is FS)

- **Espressif §USB** (ESP):
  - Reserve R/C footprints near the chip.
  - Route the pair parallel and equal-length at **90 Ω ±10 %**.
  - Minimise vias; add a pair of GND return vias at each transition.
  - Keep a continuous GND reference underneath and surround the pair with GND copper.
- **TI SPRAAR7J Table A-1** (p.16; USB2.0 including HS — conservative for FS):
  - Differential impedance 81/90/99 Ω; intra-pair skew ≤50 mil.
  - **0 stubs**, ≤4 vias per trace, 0 test points.
  - ≥50 mil to clocks/periodic signals, ≥30 mil to other signals.
- **SPRAAR7J §3.14** (p.15): ESD/EMI parts "as close as possible to the connector"; keep unprotected traces away from protected ones.
- **TPD4E1U06** (SLVSBQ9E p.11, TPD):
  - Place "as close to the connector as possible".
  - Keep unprotected traces away from the protected segment between TVS and connector.
  - Route protected traces straight, with rounded corners.
  - 0.8 pF typical.
- **How critical is 90 Ω at FS:**
  - TUSB1106 FS driver tFR/tFF = **4–20 ns** (TUSB).
  - **(computed)** Knee ≈ 0.35/tr ≈ 88 MHz (bandwidth rule from SNLA288). A 4 ns edge spans ≈0.65–0.69 m on FR-4 microstrip (εeff 3.0–3.4).
  - A D+/D− run of a few cm is therefore electrically short (≪ tr/6 ≈ 11 cm). 90 Ω and length matching are good practice, not critical; return path and ESD placement still matter.
- JLCPCB offers controlled impedance only on 4+ layers (JLC).

## 7. SD card / SDIO (25 / 50 MHz)

- **Espressif §SDIO** (ESP):
  - CMD and DATA0–3 within **±50 mil** of the SDIO_CLK length (serpentine if needed).
  - **50 Ω ±10 %** single-ended; total length ideally ≤**2000 mil**.
  - No layer changes, over a continuous (preferably GND) reference.
  - GND copper around SDIO_CLK; minimise parasitic capacitance.
- **Microchip AN14.18** (DS50002291A p.2, AN1418):
  - Solid, continuous GND under the SD lines, with no cuts.
  - **2-layer:** SD_CLK series termination "within 400 mils to the SD_CLK pin" of the driver. On 4-layer boards: within 400 mil of the socket.
  - Buffer SD_CLK beyond 1000 mil (buffer with <2.5 ns delay, e.g. 74AHC1G125).
  - Table 1, 2-layer: CLK ≤1000 mil at 100–130 Ω; DAT/CMD ≤2500 mil at 80–150 Ω.
  - DAT tolerance ±750 mil; −250…+1500 mil relative to CLK. "Skew control between data lines is not critical within the limits given."
- **Not verified:** AN14.18 gives no resistor value. The common 22–33 Ω was not confirmed in a primary source.

## 8. JLCPCB rigid capabilities (fetched 2026-11-03, JLC)

- **Trace/space:** 1 oz, 1–2 layer: **0.10 / 0.10 mm (4/4 mil)**; width tolerance ±20 %.
- **Vias:**
  - Minimum hole/diameter **0.15 / 0.25 mm**.
  - Via Ø should be the hole +0.10 mm (+0.15 preferred), i.e. a 0.05/0.075 mm ring.
  - Preferred minimum hole 0.20 mm; 0.2–0.25 mm holes with Ø <0.45 mm cost extra.
- **Annular ring:**
  - PTH ≥0.20 mm; 2-layer 1 oz: **recommended ≥0.25 mm, absolute minimum 0.18 mm**.
  - NPTH pad ring ≥0.45 mm.
  - PTH hole tolerance +0.13/−0.08 mm.
- **Clearances:** pad–track 0.10 mm; SMD pad–pad (different nets) 0.15 mm; via hole–track 0.20 mm; PTH–track 0.28 mm (0.35 recommended); NPTH–track 0.20 mm.
- **Solder mask:**
  - LDI 1:1 expansion (since June 2025); keep ≥0.09 mm from a mask opening to neighbouring traces.
  - **Bridge, 1 oz: 0.10 mm (green, red, yellow, blue, purple) / 0.13 mm (black, white).** 2 oz: 0.20 mm, any colour.
- **Edges:** Cu to routed edge ≥**0.20 mm** (also routed slots); V-cut ≥0.40 mm; mouse-bite ≥0.20 mm. Routed tolerance ±0.2 mm (±0.1 high precision).
- **Via tenting** (JLCVIA, JLC5):
  - "Most PCBs use tented vias by default."
  - Tented holes ideally ≤0.4 mm and never >0.5 mm, otherwise tenting may be incomplete. Slight yellowing is normal.
  - Exposed or tented vias may retain solder beads.
- **Via plugging and via-in-pad:**
  - Ink plugging needs ≥0.35 mm clearance to mask openings.
  - Via-in-pad cannot be ink-plugged; it needs epoxy or copper filling with a plated cap (POFV).
  - POFV is the free default on ≥6 layers, for vias Ø 0.15–0.55 mm (JLC, POFV).
  - The POFV guide warns that open via-in-pad causes solder wicking.
  - **2-layer POFV availability is not stated** (unverified).
- **Teardrops:** not a capability rule.
  - JLCPCB's blog recommends them where the trace-to-pad ratio is small, on dense boards (to keep annular ring), at pad/via exits, and where a trace narrows.
  - "No need to add teardrops when the conductor is more than 20 mils" (JLCTD).

## 9. Mechanical keep-outs and teardrops

- **KiCad M2 footprints** (KICAD):
  - `MountingHole_2.2mm_M2_DIN965_Pad_TopBottom`: head circle Ø3.8 (lines 40–48), courtyard Ø4.3 (lines 50–58), PTH Ø2.6/2.2 drill, top/bottom pads Ø3.8 (lines 70–86).
  - Sibling footprints: ISO7380 Ø3.5 head / Ø4.0 courtyard; ISO14580 Ø3.8 / Ø4.3; `_M2_Pad` Ø4.4 / Ø4.9.
- **JLCPCB NPTH guide** (NPTH):
  - "Keep copper features clear of the drilled edge by at least about 0.2-0.3 mm, and more if a metal screw head or washer will contact the surface."
  - Use a "copper-free and component-free ring around each mounting hole".
  - Keep holes far enough from the edge to avoid fragile laminate.
- **Murata MLCC strain cracks** (MUR1, MUR2):
  - Keep "distance from board edges, screw holes and connectors (… for example, 10 mm or more)".
  - Lay parts parallel to separation lines; avoid corners and the bends of L-shaped boards.
  - "Slits are better than perforations"; land width should be less than the chip width.
- **Teardrops** (SUMMIT, a fab):
  - "Class 2 allows for 90 degree breakout as long as there is a teardrop/filleting/keyholing at the land conductor junction."
  - Class 3 tangency is only AABUS (as agreed between user and supplier), with teardrops.
- **Not verified:** an IPC-2221 numeric conductor-to-edge minimum; standoff and washer dimensions.

## 10. EMI on 2-layer boards

- **TI SZZA009** (1999, SZZA):
  - §2.1.2: "A two-layer board can achieve 95% of the effectiveness of a four-layer board" by:
    - routing ground under power;
    - gridding power and ground;
    - routing returns "directly under the signal trace";
    - putting a solid ground under the MCU.
  - §2.1: power/ground trace length:width ≤3:1 between the IC and its source.
  - §2.2.3: "Gridding is the most critical design technique for two-layer boards."
  - §2.4 (crosstalk): "Never run noisy traces on the outside edge of the board."
  - §2.4.2: trace length becomes important above λ/10 (FCC), λ/20–λ/30 (military) and λ/50 (consumer 2-layer, unshielded).
- **Infineon AP24026 V3.5** (IFX):
  - p.40: on 2-layer boards, "provide power and ground nets close to the high-speed trace". A smaller return loop gives lower emission.
  - p.40: edge ground ring, vias "not … longer than 5mm" apart, closer for very high frequencies.
  - p.12: keep crystals and oscillators away from I/O and board edges.
- **TI SLLA414A** (§3.4–3.5, p.12):
  - High-speed signals over solid GND, not across splits or voids; use stitching capacitors if unavoidable.
  - Keep pairs ≥90 mil from the reference-plane edge.
- **TI SNLA288** (p.6): maximum stitching-via spacing = λ/4 at BW = 0.35/tr, tightened for harmonics.
- **(computed) λ/20**, using λ = c/(f·√εr), εr 4.5 (JLC's 2-layer Dk):

| f | 1 GHz | 2.4 GHz (Wi-Fi/BLE) | 4.8 GHz (2nd harm.) |
|---|---|---|---|
| λ/20 in FR-4 | 7.1 mm | 2.9 mm | 1.5 mm |
| λ/20 in air | 15.0 mm | 6.2 mm | 3.1 mm |

- **Not verified:** "stitching vias ≤ λ/20" was not found in a primary Ott, TI or ADI document (hottconsultants.com 403; analog.com timed out). Treat it as a rule of thumb; Infineon's 5 mm is the closest verified figure.

## Cross-checks in this repo (observations, not references)

- **TPS923610 footprint** `U_DRL0006A_6L_TEX-M` is on **B.Cu** (`silkscreen_pcb.kicad_pcb:28472-28473`).
  - Pads are 0.8128×0.2286 mm at x = ±0.8509 (1.70 mm centre span) (`:28802-28851`).
  - TI specifies 0.67×0.30 mm at 1.48 mm; the 0.229 mm pad is narrower than the 0.27 mm max lead width.
  - *Later on 2026-11-03 `U10` moved to TI's land as `U_DRL0006A_6L_TI-LAND` (TRACE_AUDIT.md §1c). The line numbers above are from before that change.*
- **Mounting holes:** `MountingHole_2.2mm_M2_DIN965_Pad_TopBottom` ×6 (`silkscreen_pcb.kicad_pcb:3247, 5167, 12381, 12510, 36241, 49140`) → Ø3.8 head / Ø4.3 courtyard.

## Gaps / unreachable sources

- IPC-2221B/C originals (paywalled).
- ST AN4879 (timeout), SiLabs AN0046 (403), NXP AN11392 (404).
- ADI AN-1349, AN-1109, MT-095 (timeouts); hottconsultants.com (403); TDK flex-crack guide (403).
- UltraCAD via-current PDF (404), so the via numbers are IPC-2221-formula estimates, not measured data.

## Sources

- **EMA** — EMA Design Automation, "PCB Clearance and Creepage Distance Table": https://www.ema-eda.com/ema-resources/blog/pcb-clearance-and-creepage-distance-table/
- **T61** — IPC-2221 Table 6-1 transcription (smps.us-derived): http://www.magma.ca/~legg/TVS/IPC_2221_Table_6-1_track_spacing.pdf
- **SIERRA** — https://www.protoexpress.com/tools/pcb-conductor-spacing-and-voltage-calculator/
- **DIN** — IPC-2221C listing: https://www.dinmedia.de/en/standard/ipc-2221c/377902590
- **APCB** — AdvancedPCB (ex-4pcb) trace width calculator: https://www.advancedpcb.com/en-us/tools/trace-width-calculator/
- **SMPS** — https://www.smps.us/pcb-calculator.html
- **ALT** — https://resources.altium.com/p/using-ipc-2152-calculator-designing-standards
- **CC** — https://circuitcalculator.com/wordpress/2006/03/12/pcb-via-calculator/
- **ESP** — https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
- **ESPFIG** — https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/_images/esp32s3-module-clearance.png
- **WROOM** — ESP32-S3-WROOM-1/1U datasheet v1.8: https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- **TPS** — https://www.ti.com/lit/ds/symlink/tps923610.pdf
- **GD** — https://www.good-display.com/companyfile/991.html (PDF https://v4.cecdn.yun300.cn/100001_1909185148/GDEQ0426T82.pdf needs a good-display.com referer)
- **SSD** — SSD1677 Rev 1.0, third-party mirror: https://github.com/CursedHardware/epd-driver-ic/blob/master/SSD1677.pdf
- **SPRAAR7** — TI SPRAAR7J: https://www.ti.com/lit/pdf/spraar7
- **TPD** — https://www.ti.com/lit/ds/symlink/tpd4e1u06.pdf
- **TUSB** — https://www.ti.com/lit/ds/symlink/tusb1106.pdf
- **SNLA288** — https://www.ti.com/lit/pdf/snla288
- **AN1418** — Microchip AN14.18: https://ww1.microchip.com/downloads/en/AppNotes/50002291A.pdf
- **JLC** — https://jlcpcb.com/capabilities/pcb-capabilities
- **JLCVIA** — https://jlcpcb.com/help/article/pcb-via-covering
- **JLC5** — https://jlcpcb.com/blog/five-via-finishes
- **POFV** — https://jlcpcb.com/help/article/via-in-pad-pofv-guide
- **JLCTD** — https://jlcpcb.com/blog/PCB-Teardrop-You-Should-Know
- **NPTH** — https://jlcpcb.com/blog/npth-design-guide
- **KICAD** — https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/MountingHole.pretty/MountingHole_2.2mm_M2_DIN965_Pad_TopBottom.kicad_mod
- **MUR1** — https://article.murata.com/en-global/article/strain-crack-mechanism-and-preventive-measures-for-mlcc
- **MUR2** — https://article.murata.com/en-us/article/layout-helps-prevent-chip-mlcc-from-cracking
- **SUMMIT** — https://summitinterconnect.com/blog/article/drill-plated-hole-ipc-rule-land-sizes/
- **SZZA** — https://www.ti.com/lit/an/szza009/szza009.pdf
- **IFX** — Infineon AP24026: https://www.infineon.com/assets/row/public/documents/30/42/infineon-ap2402635-general-pcb-applicationnotes-en.pdf
- **SLLA414** — https://www.ti.com/lit/pdf/slla414
