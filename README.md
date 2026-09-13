# Silkscreen

**An open-source, open-hardware e-reader base board.**
Display-agnostic · case-agnostic · firmware-agnostic · battery-agnostic.

Successor to [de-link](https://de-link.me). Designed in **KiCad 9.0.6**.

Silkscreen is a base board for e-ink development: one 2-layer PCB that aims to drive
essentially any 24-pin SPI e-paper panel, from any battery, in any enclosure, under any
firmware — so the interesting work (display, case, software) isn't gated on redesigning power
and interface electronics every time.

![Silkscreen — full schematic](docs/images/full-capture.png)

Current full plots: **[schematic PDF](docs/silkscreen_pcb_schematic.pdf)** ·
**[PCB layout PDF](docs/silkscreen_pcb_layout.pdf)**.

---

## At a glance

| | |
|---|---|
| **MCU** | ESP32-S3-WROOM-1 (**N16R8**, 16 MB flash / 8 MB octal PSRAM), native USB — no UART bridge |
| **Display** | 24-pin 0.5 mm ZIF for SPI e-paper; primary target 4.26" GDEQ426T82 family; panel-driven charge pump generates the ±15–22 V rails |
| **Frontlight** | TPS923610 constant-current boost, warm/cool CCT blending via a single GPIO + inverter |
| **Touch** | Optional I²C capacitive touch (for `-FT01C`-class panels) with a 0 Ω pin-swap mux |
| **Power** | USB-C in → TP4056 charger → DW01A + FS8205A cell protection → TPS2116 priority mux → TLV75533P 3V3 LDO |
| **Battery** | Bring-your-own single-cell LiPo; full on-board protection makes a bare cell safe |
| **Storage** | push-push microSD in 4-bit SDMMC, power-gated |
| **Input** | 8 buttons on two ADC resistor ladders + power/boot/reset |
| **RTC** | DS3231MZ (±2 ppm), VBAT-only mode |
| **Board** | 2-layer, 60 × 111 mm, 1 oz Cu, 173 components |

Full block-by-block description: **[docs/HARDWARE.md](docs/HARDWARE.md)**.
Schematic review, margins and design rationale: **[DESIGN_REVIEW.md](DESIGN_REVIEW.md)**.

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

You need **KiCad 9.0.x** (the files are 9.0 format; opening in 10.x upgrades them one-way).

### Fabrication (bare board)

Generate a gerber + drill set (JLCPCB, PCBWay and NextPCB all accept the same standard set):

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

- **JLCPCB:** prefer the KiCad **Fabrication Toolkit** plugin — it applies JLC's part-rotation
  database and fills LCSC part numbers automatically. See [`fabrication/README.md`](fabrication/README.md).
- **PCBWay / NextPCB:** upload the gerber zip + the centroid + [`fabrication/BOM.csv`](fabrication/BOM.csv);
  they quote against the manufacturer part numbers.

See **[fabrication/README.md](fabrication/README.md)** for the full per-house process and caveats.

## Bill of materials

**[fabrication/BOM.md](fabrication/BOM.md)** — full BOM with manufacturers, MPNs, DigiKey/LCSC
links, LCSC-cheaper alternates, and per-part pricing with quantity break costs (board + a
"complete build" section covering PCB fab, display and battery).

## Documentation

- **[docs/HARDWARE.md](docs/HARDWARE.md)** — how every block works, GPIO map, design themes.
- **[DESIGN_REVIEW.md](DESIGN_REVIEW.md)** — net-by-net schematic review, margin analysis, and
  the layout spot-review.

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
