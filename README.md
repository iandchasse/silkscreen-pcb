# Silkscreen

**An open-source, open-hardware e-reader base board.**
Designed for compatible SPI e-paper panels, custom enclosures and firmware.

Successor to [de-link](https://de-link.me). Designed in **KiCad 9.0.6**.

Silkscreen is a 2-layer ESP32-S3 base board for e-ink development, with a 24-pin display
interface, optional touch/frontlight, microSD and single-cell Li-ion/LiPo power.
Check the selected panel's pinout and drive requirements, battery specification and enclosure fit.

**Before assembly:** read **[DESIGN_REVIEW.md](DESIGN_REVIEW.md)**. This is the single source
for the current assembly decision, required corrections and first-article tests. The review
identifies an unresolved USB-present reverse-battery fault path, a Q4 replacement requirement,
and an SD-socket fit check; the source is not an unconditionally qualified production design.

![Silkscreen — full schematic](docs/images/full-capture.png)

Published plots: **[schematic PDF](docs/silkscreen_pcb_schematic.pdf)** ·
**[PCB layout PDF](docs/silkscreen_pcb_layout.pdf)**. The layout PDF predates the reviewed PCB;
use the source and the review's current copper exports for layout decisions. The image above
is illustrative, not the release record.

---

## At a glance

| | |
|---|---|
| **MCU** | ESP32-S3-WROOM-1 (**N16R8**, 16 MB flash / 8 MB octal PSRAM), native USB — no UART bridge |
| **Display** | 24-pin 0.5 mm ZIF for SPI e-paper; primary target 4.26" GDEQ426T82 family; panel-driven charge pump generates the ±15–22 V rails |
| **Frontlight** | TPS923610 constant-current boost, warm/cool selection through one GPIO + inverter; blending requires qualification |
| **Touch** | Optional I²C capacitive touch (for `-FT01C`-class panels) with a 0 Ω pin-swap mux |
| **Power** | USB-C in → TP4056 charger → DW01A + FS8205A cell protection → TPS2116 priority mux → TLV75533P 3V3 LDO |
| **Battery** | Specified single-cell 4.2 V-charge Li-ion/LiPo; verify cable polarity and observe the review's protection limitations |
| **Storage** | push-push microSD in 4-bit SDMMC, power-gated |
| **Input** | 8 buttons on two ADC resistor ladders + power/boot/reset |
| **RTC** | DS3231MZ (±5 ppm), VBAT-only mode; populated in the standard build, optional |
| **Board** | 2-layer, 60 × 111 mm, 1 oz Cu; 173 references including DNP, holes and test pads |

Connection/GPIO reference: **[docs/HARDWARE.md](docs/HARDWARE.md)**.
All engineering conclusions and release actions: **[DESIGN_REVIEW.md](DESIGN_REVIEW.md)**.

---

## Repository layout

```
silkscreen_pcb.kicad_pro / .kicad_sch / .kicad_pcb   KiCad 9 project
sym-lib-table / fp-lib-table                          project-local library tables
KiCad/9.0/3rdparty/                                   vendored symbols/footprints/3D models
docs/HARDWARE.md                                      hardware documentation
DESIGN_REVIEW.md                                      schematic + layout review
fabrication/                                          BOM, assembly data, how-to (gerbers gitignored)
LICENSE                                               CERN-OHL-S v2
```

## Building the board

The project and reviewed exports use **KiCad 9.0.6**. Keep a backup before saving with a
newer major version; newer file formats may not reopen in KiCad 9.

### Fabrication (bare board)

The active assembly workflow is **JLCPCB**. Generate a Gerber + drill set, or use the
Fabrication Toolkit workflow below:

```bash
kicad-cli pcb export gerbers -o fabrication/gerbers/ \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts \
  --no-protel-ext --subtract-soldermask silkscreen_pcb.kicad_pcb
kicad-cli pcb export drill -o fabrication/gerbers/ --format excellon \
  --drill-origin absolute --excellon-units mm --excellon-separate-th silkscreen_pcb.kicad_pcb
```

Zip `fabrication/gerbers/` and upload. Board is 2-layer, 1.6 mm, 1 oz copper; outline on `Edge.Cuts`.

### Assembly

```bash
kicad-cli pcb export pos -o fabrication/assembly/cpl.csv --format csv --units mm --side both silkscreen_pcb.kicad_pcb
```

- **JLCPCB:** use the KiCad **Fabrication Toolkit** plugin for the final placement export;
  it applies JLC's part-rotation database. Keep the upload BOM separate from the factory's
  matched/accepted BOM and save approved substitutions. The raw CLI centroid above is a
  cross-check, not a replacement for the reviewed Toolkit CPL.
- Historical sourcing and per-house exports may differ from the current order. Do not
  upload them as a new release without reconciling the review's action list and DNP policy.

See **[fabrication/README.md](fabrication/README.md)** for the release-file workflow.

## Bill of materials

**[fabrication/BOM.md](fabrication/BOM.md)** is the historical sourcing/pricing reference,
with DigiKey/LCSC links and build estimates. It is not the current factory BOM. The review
cross-checks every reference against the saved JLC matched order; accepted factory changes
must be frozen in the release records.

## Documentation

- **[DESIGN_REVIEW.md](DESIGN_REVIEW.md)** — authoritative 18-block review, assembly decision,
  critical layout measurements, component recommendations and acceptance plan.
- **[docs/HARDWARE.md](docs/HARDWARE.md)** — GPIO/connector maps, population and operating reference.

---

## License

Hardware licensed under the **CERN Open Hardware Licence Version 2 – Strongly Reciprocal
(CERN-OHL-S-2.0)** — see [LICENSE](LICENSE).

> Copyright © 2026 idc LLC.
> This source describes Open Hardware and is licensed under the CERN-OHL-S v2.
> You may redistribute and modify this source and make products using it under the terms of the
> CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt). This source is distributed WITHOUT ANY
> EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR
> A PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable conditions.

`SPDX-License-Identifier: CERN-OHL-S-2.0`

Third-party component library files (from SnapEDA / Ultra Librarian / SamacSys) retain their own
terms and are not covered by the project license — see
[fabrication/THIRD_PARTY.md](fabrication/THIRD_PARTY.md).

Predecessor project: [de-link.me](https://de-link.me).
