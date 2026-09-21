# Silkscreen

**An open-source, open-hardware e-reader mainboard.**

Silkscreen is the mainboard of a build-it-yourself e-reader. You order the board already
assembled from a factory, add an e-paper display, a battery and a microSD card, and put it in a
case of your own choosing. It is a 2-layer ESP32-S3 board with a 24-pin display connector,
optional touch and frontlight, microSD and single-cell Li-ion/LiPo power.

It is the successor to [de-link](https://de-link.me). This repository was the de-link project hub
until September 2026; the hub's pages and photos are kept on the
[`de-link-old`](https://github.com/iandchasse/silkscreen-pcb/tree/de-link-old) branch. I designed
Silkscreen in KiCad 9.0.6, but
**you do not need KiCad to order a board.** Every file a factory asks for is already in the
`production/` folder of this repository, ready to upload.

| Back (all components) | Front (silkscreen art) |
|:---:|:---:|
| ![Board, bottom view](docs/images/board-bottom.png) | ![Board, top view](docs/images/board-top.png) |

## What it is

- **Brain:** an ESP32-S3 module with 16 MB of flash and 8 MB of PSRAM, with USB built in. You
  plug a USB-C cable straight into it, no adapter.
- **Screen:** a 24-pin connector for SPI e-paper panels. The primary target is the 4.26"
  Good Display `GDEQ0426T82` family, in plain, touch, frontlight, or touch + frontlight versions.
  `GDEQ0426T82` is the base part number and the suffix picks the variant (`-T01C` touch,
  `-FL01C` front light, `-FT01C` both), so always order by the full suffixed number.
- **Power:** charges and runs from a single-cell Li-ion/LiPo pack over USB-C, with charger,
  cell protection and a 3.3 V regulator on board.
- **Storage:** a push-push microSD socket.
- **Buttons:** eight page/navigation buttons, plus power and reset.
- **Size:** 60.05 × 111.30 mm, 1.6 mm thick. Every part is soldered onto the **back** face, so
  the front is clear for the display.

There is **no firmware for this board yet**. Read [Firmware](#firmware) before you order.

Everything about how the board works, pin by pin, is in one document:
[docs/HARDWARE.md](docs/HARDWARE.md). It covers every circuit block, the GPIO map, what firmware
has to do for the hardware, and the dimensions a case needs.

---

## What you need besides the board

The factory sends you a populated circuit board and nothing else. You also need:

| Item | What to get |
|---|---|
| **Display panel** | One of the 4.26" Good Display variants: `GDEQ0426T82` (plain), `-T01C` (touch), `-FL01C` (frontlight), `-FT01C` (touch + frontlight). The panel you pick decides which optional parts you fit. See [Choosing a configuration](#choosing-a-configuration). |
| **Battery** | A **single-cell** (3.7 V nominal / 4.2 V charged) Li-ion or LiPo pack fitted with a **JST-PH 2.0 mm, 2-pin** plug. Read the polarity note below before you plug it in. I use [this 500 mAh `503035` pack (5 × 30 × 35 mm, JST-PH 2.0)](https://www.amazon.com/dp/B0GDQLLF12). It fits the board's 38.75 × 30.50 mm battery bay snugly, with 0.5 mm to spare on the 30 mm side. The board charges at about 0.25 A as built, which is 0.5C for this pack. For a much smaller cell, lower the charge current by raising `R6` ([HARDWARE.md §3.2](docs/HARDWARE.md#32-battery-charger)). Listings change, so check the plug, the polarity and the size of whatever you buy. |
| **microSD card** | Any normal microSD card. The battery normally sits in the board's cut-out directly in front of the card slot, so you lift or slide the cell aside to put a card in or take one out. I designed it that way; the card is not meant to be swapped often. |
| **USB-C cable** | A **data** cable, not a charge-only one, or the board will charge but never appear on your computer. |

**Battery lead order.** On the board, `J5` pin 1 is marked **"-"** and is battery **negative**;
pin 2 is battery **positive**. There is no industry standard for JST-PH battery leads. Packs
ship both ways round, and a red-to-pin-1 pack and a black-to-pin-1 pack look identical in a
photo. Check your pack with a multimeter before you plug it in.

> [!WARNING]
> Lithium cells are a fire risk if reversed, shorted or crushed. Measure the polarity of your
> pack against the "-" mark on `J5` before plugging it in. Do not trust the wire colours. Use a
> pack with its own protection board. Stop using any cell that is puffed, hot or damaged.

**Screws and case are not on this list.** The board has six M2 mounting holes, but which screws
you need depends on the case you use, and no case is supplied here. See
[The board and your case](#the-board-and-your-case).

---

## Order an assembled board, step by step

You do not need KiCad and you do not need to know how a PCB is designed. A factory makes the
board and solders every part onto it. You will be clicking through a web shop and uploading three
files that are already in this repository. Unfamiliar words are defined in
[Words used on the factory's website](#words-used-on-the-factorys-website).

> **Or let the builder make the files.** The *Build one* page at
> [silkscreenreader.com](https://silkscreenreader.com/builder.html) walks you through the panel
> variant and the optional blocks, estimates what the result costs, and gives you the three upload
> files for exactly that build: the same Gerber zip, plus a BOM and CPL with the parts you left off
> already removed (see [Choosing a configuration](#choosing-a-configuration)). For the standard
> build they are byte-for-byte the files in `production/`. The site is still in preview, and the
> steps below are the same either way.

### What it costs and how long it takes

The minimum order is **5 bare boards**, and you choose how many of them the factory assembles:
as few as **2**, all 5, or more boards if you want them. Most of the bill is one-off (the bare
boards, setup, the solder stencil, and a small loading fee for each of about two dozen "Extended"
part types the factory has to fetch), so the price per assembled board falls quickly as you build
more. [silkscreenreader.com/cost](https://silkscreenreader.com/cost) breaks the cost down by
order size and explains where each fee comes from.

For scale, my own order on **21 September 2026** (no coupons, US delivery): five boards with two
assembled came to **$223.95** for boards, parts and assembly, and **$305.23** at checkout once
shipping, US tariffs and tax were added. That is about $150 per working board at two, and the
cost page puts the same build at roughly $77 per board with all five assembled and about $50 at
ten. Prices, shipping and import charges move, so treat every figure as an expectation, not a
promise.

| | |
|---|---|
| Time from clicking *order* to the parcel | about **2 to 3 weeks** |
| Not included | display panel, battery, microSD card, case |

### Step 1: get the three files

Download this repository (green **Code** button, then **Download ZIP**) and unzip it. Everything
you need is in the `production/` folder. You upload exactly three files:

| Upload this | What it is | Where it goes |
|---|---|---|
| `production/Silkscreen_Reader_PCB_1.0.zip` | the **Gerber** files: the board itself, meaning copper layers, outline and hole positions | the *Add Gerber file* box |
| `production/jlc_bom.csv` | the **BOM** (bill of materials): the shopping list of parts | the *Add BOM file* box |
| `production/positions.csv` | the **CPL** (also called the centroid or pick-and-place file): where each part sits and which way it faces | the *Add CPL file* box |

Ignore everything else in that folder. These three belong together and come from the same export.
Do not mix one of them with an older copy of another.

### Step 2: order the bare board

1. Sign in at [jlcpcb.com](https://jlcpcb.com), click **Order now**, then **Add Gerber file** and
   choose `Silkscreen_Reader_PCB_1.0.zip`.
2. The viewer draws the board. Confirm it says **2 layers** and about **60 × 111 mm**. If it does
   not, you uploaded the wrong file.
3. Set **PCB Qty = 5**, **Thickness = 1.6 mm**, **Outer Copper Weight = 1 oz**. Surface finish and
   solder-mask colour are your choice; nothing in this design needs a particular one.
4. Leave everything else at its default.
5. Scroll the viewer to the board edges and check the USB-C cut-out, the microSD opening and the
   two narrow slots on the outline are open, not filled. The long one (47.04 × 1.30 mm) is the
   display-flex slot; the short one at the tongue neck is **5.30 × 1.10 mm**. Both are at or above
   JLCPCB's 1.0 mm minimum routed-slot width, so neither should raise a design-for-manufacture
   (DFM) message. (Earlier revisions had four 0.5 mm perforation slots there; those are gone.)

### Step 3: turn on assembly

**PCBA** means "printed circuit board assembly": the factory buys the parts and solders them on
for you, instead of shipping you a bare board.

1. Switch **PCB Assembly** on.
2. Choose **Standard**, not Economic. JLCPCB runs two assembly services, and the ESP32-S3 module
   this board is built around can only be placed on **Standard**, so for a complete board Standard
   is the one you need. (If you are happy to hand-solder the module yourself, you could leave it
   off the order and use the cheaper Economic service for everything else. That is an experienced
   builder's choice, not the path I recommend.)
3. Because this board is 60 mm wide and Standard's conveyor wants at least 70 mm, the factory may
   add **snap-off edge rails**: narrow strips of extra board material along the edges for the
   machine to grip. There is nothing for you to design. Expect a small fee in the quote, and snap
   the rails off when the boards arrive.
4. Set **Assembly side: Bottom**. Every part on this board is on the back. If you leave this on
   *Top* you will receive blank boards and a bag of parts.
5. Set the assembly quantity to the number of boards you want built, from 2 up to the number of
   bare boards in the order.
6. Leave **Tooling holes** on *Added by JLCPCB*.
7. Set **Confirm Parts Placement** to **Yes**. It costs a small fee and is worth it on a first
   order: it lets you look at a picture of where each part will go before the machine runs.
8. Click **Confirm**, then **Next**.

### Step 4: upload the parts list

1. **Add BOM file**: `production/jlc_bom.csv`
2. **Add CPL file**: `production/positions.csv`
3. Click **Process BOM & CPL**.

### Step 5: check the parts the factory picked

You get a table with one row per part. Most rows will already be matched.

- **Rows with a blank part number are meant to be blank.** Eleven references (`TP3 TP4 TP5`,
  `R43 R45 R58 R66 R72 R74`, `SW6` and `U14`, the alternate clock chip; the board uses `U13`) are
  tagged *"DNP (standard build)"*. **DNP** means "do not populate": a spot on the board
  deliberately left empty. **Leave them unselected.**
- **Every other row must show a match.** If a row says *No Parts Selected* or *out of stock*, or
  shows a manufacturer's part number instead of an **LCSC code** (the `C…` number that identifies a
  part in the factory's own warehouse), click **Search** and look it up.
  [`fabrication/BOM.md`](fabrication/BOM.md) lists an approved alternative for every part on this
  board. Use that list rather than picking a look-alike yourself, because several of these parts
  have near-identical siblings with different pinouts.
- The part most often short is **TPS923610DRLR**, the frontlight driver. Check its stock. If it is
  out and you are not fitting a frontlight panel, untick it along with the rest of the *Frontlight*
  group in [Choosing a configuration](#choosing-a-configuration).
- If you are deliberately leaving a block off, remove its parts from the BOM **and** the CPL, or
  untick them here.
- Click **Next**.

### Step 6: check the placement preview (do not skip this)

You see a drawing of the board with every part on it. This is your last chance to catch a part
that is rotated wrongly, and the factory's own checker has corrected several on this board before.
A matched part code does not prove the part is the right way round.

| Part | What to check |
|---|---|
| `D2` | The USB power LED. **Pad 1 is the cathode** (the marked end). Some part libraries use the opposite convention. |
| `U2`, `U5`, `D8` | Small 3 to 8 pin chips whose rotation the factory has corrected before. |
| `J4` | Its drawn outline sits 0.73 mm off its own pads; the pads are what matter. |
| `U4`, `J7` | The ESP32 module and the microSD socket. Check they are centred on their pad patterns. |

If something looks wrong, use the preview's rotate and move tools to fix it, and **save a
screenshot of the corrected preview**. Click **Next**.

### Step 7: through-hole parts, soldered by the factory or by you

Thirteen parts have legs that pass through the board rather than sitting on its surface. That is
**THT** (through-hole technology), as opposed to **SMD** (surface-mount) for everything else. They
are the USB-C socket `J1`, the battery connector `J5`, the expansion header `J6` and the ten
buttons `SW1` to `SW5` and `SW7` to `SW11`. They are already in the files you uploaded, so this is
a choice, not extra work:

- **Let the factory solder them.** JLCPCB charges a one-off hand-soldering fee (about $3.60 per
  order) plus roughly $0.016 per joint, which is about **$1.20 per assembled board** on top of the
  fee. It adds about a day. Confirm on the quote page that through-hole soldering
  appears as a line item.
- **Solder them yourself.** You get the parts loose and put in 74 joints per board: the USB-C
  shell pins, the JST battery connector, the 12-pin expansion header and ten buttons. The USB-C
  shell is the fiddly one. Worth doing if you own a decent iron and a fine tip; not worth it on a
  first board.

### Step 8: pay, and keep the paperwork

Read the price summary: bare boards, setup fee, per-part-type fees, the parts themselves,
assembly. Place the order. Then keep in one folder the order confirmation, the accepted BOM as the
factory matched it, any substitutions it proposed, and your screenshot of the approved placement
preview. If you order again, you will want to know exactly what was built the first time.

### Using a different factory (PCBWay, NextPCB, others)

Nothing in the design is tied to JLCPCB. Upload files for other assemblers are kept in
[`production/other_fabs/`](production/other_fabs/): a PCBWay BOM with KiCad's own placement file, a
NextPCB BOM and centroid file in NextPCB's template (plus SMD-only and through-hole-only pairs in
`split/`), and a bottom-side assembly drawing. They use the same Gerber zip as the JLCPCB order and
are regenerated from the current design with:

```bash
python fabrication/make_fab_files.py --split
```

Know what you are taking on, though. **JLCPCB is the only factory that has delivered working
Silkscreen boards.** My NextPCB attempt did not end in an order (what went wrong, and what it
would have cost, is in [fabrication/NEXTPCB_REV0_NOTES.md](fabrication/NEXTPCB_REV0_NOTES.md)),
and I have not tried PCBWay. Another factory is a fine choice if you prefer one. You will be doing
the part matching, the rotation check and the back-and-forth with their engineers yourself,
without a known-good order to compare against. Everything else in this guide assumes JLCPCB.

---

## Choosing a configuration

The files in `production/` build the **full standard build**: every block fitted except the DNP
options. The board is a **core** that is always fitted, plus add-on groups you can leave off. For
a reduced configuration, download its files from the
[silkscreenreader.com builder](https://silkscreenreader.com/builder.html), or do it by hand: delete
the listed references from the BOM **and** the CPL and leave the pads empty.

Each group lists every part that exists only to serve it, taken from the schematic netlist (rails
and the shared I²C bus aside), so leaving a group off leaves nothing behind that does no work. The
[silkscreenreader.com](https://silkscreenreader.com) builder uses the same groups.

| Group | References | Fit it when | Works without it? |
|---|---|---|---|
| **Core** (always) | Everything not listed below: ESP32-S3 `U4`, USB-C `J1`/`U6` and protection, charger `U11`, cell protection `U5`/`Q1`/`Q3`/`Q8`, power mux `U2`, LDO `U3` with its input capacitor `C4`, battery monitor, microSD `J7`/`Q7`/`U1`/`U9`, the 24-pin display connector `J2` with its charge pump and boost (`L1`, `Q4`, `D4`-`D6`, `R14`, ...), power button `SW10`, reset `SW11`, LED `D2`, and the I²C pull-ups `R47`/`R48` (shared by touch, clock and `J6`) | Always | This is the minimum working board |
| **Touch** | `J4`, `U7`, jumpers `R42 R44 R46 R52` | The panel has a touch layer (`-T01C`, `-FT01C`) | Yes: omit the whole block on a non-touch panel |
| **Frontlight** | driver `U10` with `L2`, input capacitor `C12` and output capacitor `C9`; current set `R37`; warm/cool select `Q5`, `Q6`, `U12` (with its decoupling `C24`) and `R75`; LED monitor `R39`, `R41`, `C31`; string bleeders `R49`, `R50`; output clamps `D3`, `D8` (`TP3`-`TP5` stay DNP) | The panel has a frontlight (`-FL01C`, `-FT01C`), or you want to drive an external light through `J6` | Yes: omit for a plain or touch-only panel |
| **Frontlight connector** | `J3` | The panel has a bonded frontlight (`-FL01C`, `-FT01C`) | Yes: an external light connects through `J6` instead |
| **Expansion header** | `J6`, `U8`, `CR2`, `CR3`, `F2`, and the GPIO series resistors `R65 R68 R69` | You want spare GPIO, I²C and the external-light output | Yes |
| **Real-time clock** | `U13`, `C30` (or `U14` instead of `U13`) | You want accurate time | Yes: the reader runs without it, and it can be added later by hand |
| **Alternate RTC** | `U14` (**DNP in every standard build**) | You want the cheaper clock instead of `U13` | Fit **either** `U13` **or** `U14`, never both |
| **Side page-turn keys** | per key: `SW1`+`R61` (right-down), `SW4`+`R11` (right-up), `SW7`+`R36`+`R73` (left-up), `SW5`+`R35` (left-down); with any side key, the ladder's pull-up `R28` and filter `C28` | Your case has side keys | Yes: fit any subset |
| **Bottom-row keys** | per key: `SW2`+`R60`, `SW3`+`R18`, `SW8`+`R19`, `SW9`+`R20`; with any bottom key, the ladder's pull-up `R4` and filter `C27` | Your case has bottom keys | Yes: fit any subset; with touch you can drop most keys |

Notes:

- **The panel choice drives touch and frontlight.** The four 4.26" Good Display variants are
  `GDEQ0426T82` (plain), `-T01C` (touch), `-FL01C` (frontlight) and `-FT01C` (touch + frontlight).
  Fit the touch parts only for a touch variant and the frontlight parts only for a light variant.
- **`U8`, `CR2`, `CR3` and `F2` are `J6`'s own protection and come off with it.** `U8` protects only
  `J6` pins; `CR2` and `CR3` clamp the 3V3 and raw-battery pins where they leave the board, and the
  resettable fuse `F2` sits in series with that battery pin and feeds nothing else. The 33 Ω
  series resistors `R65`/`R68`/`R69` only reach `J6` too; they cost nothing, so leaving them fitted
  on a header-less board is harmless. Do **not** remove `U9`, `D3` or `D8` with `J6`. `U9` also
  protects the microSD data lines, and `D3`/`D8` belong to the frontlight: they clamp its nets
  whether or not `J6` is fitted.
- **`C12` belongs to the frontlight.** It is on the shared `LDO_IN` rail but sits beside `U10` as
  the driver's input capacitor; the LDO and power mux have their own, `C4`. Without the frontlight
  it can go.
- **An external light needs `J6`.** `J3` only mates a panel with a bonded light; for any other
  light, the frontlight group drives it through the header.
- **Fit only one of the two touch pin-order options.** The default build fits `R42 R44 R46 R52`.
  The alternate wiring (`R43 R45 R58 R66`, DNP here) is for panels with the swapped pin order.
  Confirm the panel's pinout first.
- Leaving a button off needs nothing else changed. Its ladder resistor then does nothing and can be
  left off with it, but fitting it is harmless. Keep a ladder's pull-up and filter (`R4`/`C27`
  bottom, `R28`/`C28` side) as long as any key on that ladder is fitted.
- `SW6` (boot button) and `TP3`-`TP5` are DNP in every standard build. `R64` (100 Ω) is fitted
  but only connects `SW6`, so it does nothing unless you fit the boot button.
- Per-board part totals are in [`fabrication/BOM.md`](fabrication/BOM.md).

### Getting into download mode

`SW6`, the BOOT button, is left unfitted to save cost. You will normally never need it: the
ESP32-S3 has native USB, so it presents itself to your computer without any button press. If you
ever do need download mode (a firmware that has wedged the USB stack, for instance), bridge the
two `SW6` pads with a pair of metal tweezers while you tap **RESET** (`SW11`).

`SW11` (RESET) is set back from the board edge on purpose: it is meant to be pressed through a
pin-hole in the case with a paperclip, not by a finger.

### Cutting the board down for a smaller display

The back of the board is marked with a line showing where it can be shortened for a smaller panel.
If you do that:

- **Disconnect the battery first.** Battery positive runs across the cut line. Cutting into it
  with a pack connected can short the cell.
- **It will not snap by hand.** More than half the tab width is solid 1.6 mm FR-4, with live
  copper crossing it. Use a rotary tool (Dremel or similar) and cut along the marked line.
- **You lose the expansion header `J6` with its protection parts (`U8`, `CR2`, `CR3`, `F2`), the
  power button `SW10`, mounting hole `H1` (five mounting points remain) and the two frontlight
  clamps `D3`/`D8`**, which sit on that tongue. A cut board therefore runs its frontlight without
  those two clamps; read [HARDWARE.md §7](docs/HARDWARE.md#7-frontlight-driver) before you drive
  a frontlight from one. After the cut, UP(2) can serve as the power button instead: leave `R36`
  and `R73` unpopulated and populate `R72` and `R74`. The same instruction is printed on the
  schematic and on the board.
- Plan the cut before you order, so you can leave the parts you are cutting off out of the BOM.
  `J6`'s series resistors `R65`/`R68`/`R69` stay on the main board near the ESP32 but have nothing
  left to connect to, so they can be left out too.

---

## Firmware

**There is no released firmware for this board yet.** The board is hardware only today.

I plan to port the FreeInk SDK to it and to maintain crosspoint-reader, crossink reader and the
other XTEink X4 firmwares on it. All of that is future work, not something you can download now.
I will write first-power-up instructions once there is firmware to power up into.

If you order a board today, order it because you want the hardware to build on.

If you want to write firmware for it, [docs/HARDWARE.md](docs/HARDWARE.md) is the whole
reference. The GPIO map is section 13, and section 13.1 lists what the board needs firmware to do:
how to decode the charge-status pin, the frontlight driver's enable timing and over-voltage latch,
the microSD power sequence, and the ADC limits.

---

## The board and your case

This board is **not tied to one enclosure**. It is meant to work with many different case designs,
of whatever style you like. No reference enclosure is supplied in this repository, so the case
is yours to design or to take from someone else's.

What you need in order to design around it:

- A 3D model of the board is provided as a STEP file:
  [`docs/mechanical/silkscreen_pcb.step`](docs/mechanical/silkscreen_pcb.step).
- Board outline **60.05 × 111.30 mm**, **1.6 mm** thick.
- **Six M2 mounting holes** (`H1` to `H6`). Use screws with heads of **4 mm or less and no metal
  washers**. Tracks run close to the holes under the solder mask.
- **Every component is on the bottom face.** The top face carries only the silkscreen art and the
  protruding legs of the through-hole parts, so the display sits over a nearly clear surface.
- **Keep the antenna corner clear.** The ESP32 module's PCB antenna overhangs a cut-out in the
  board edge with no copper under it. Do not lay the battery over that corner, and keep screws,
  metal inserts and the display's metal backplane away from it.
- Hole positions, connector locations, cavity heights, apertures and the rest of the mechanical
  reference are in [docs/HARDWARE.md](docs/HARDWARE.md), section 16.

---

## Specifications

| | |
|---|---|
| **MCU** | ESP32-S3-WROOM-1 (**N16R8**, 16 MB flash / 8 MB octal PSRAM), native USB, no UART bridge |
| **Display** | 24-pin 0.5 mm ZIF for SPI e-paper; primary target 4.26" `GDEQ0426T82` family; panel-driven charge pump generates the ±15 to 22 V rails |
| **Frontlight** | TPS923610 constant-current boost, warm/cool selection through one GPIO and an inverter; the warm/cool blend has not been tested on hardware yet |
| **Touch** | Optional I²C capacitive touch (for `-FT01C`-class panels) with a 0 Ω pin-swap mux |
| **Power** | USB-C in, TP4056 charger, DW01A + FS8205A cell protection, TPS2116 priority mux, TLV75533P 3V3 LDO |
| **Battery** | Single-cell 4.2 V-charge Li-ion/LiPo on a JST-PH 2.0 mm 2-pin connector (`J5` pin 1 = negative) |
| **Storage** | push-push microSD in 4-bit SDMMC, power-gated |
| **Input** | 8 buttons on two ADC resistor ladders, a wake/power **button** (`SW10`, a wake input, not a hardware power switch; the 3.3 V rail is always live) and reset (`SW11`); a BOOT button footprint (`SW6`) is left unpopulated because USB-Serial-JTAG makes it unnecessary |
| **RTC** | DS3231MZ (±5 ppm), VBAT-only mode; populated in the standard build, optional. A second footprint (`U14`, Micro Crystal RV-8263-C7) is DNP. Fit either, never both |
| **Revision** | **Rev 1.0.** The revision label on both title blocks and in the name of the release zip changes only when a new board is fabricated; until then every change is folded into Rev 1.0. The design content is current to **2026-09-21**; the title-block date (2026-09-12) is when Rev 1.0 was opened. |
| **Board** | 2-layer, 60.05 × 111.30 × 1.6 mm, 1 oz Cu; 184 references = 165 fitted + 11 DNP + 8 bare-copper (holes `H1` to `H6`, test pads `TP1`/`TP2`) |

Connection and GPIO reference: **[docs/HARDWARE.md](docs/HARDWARE.md)**.

---

## Words used on the factory's website

| Word | What it means |
|---|---|
| **Gerber** | The standard file format for a bare circuit board: one file per copper, mask and silkscreen layer, plus the drill holes. Here they are zipped together in `production/Silkscreen_Reader_PCB_1.0.zip`. |
| **BOM** | Bill of materials: the list of every part on the board and how many of each. |
| **CPL / centroid / pick-and-place** | Three names for the same file: where each part sits on the board, which side it is on, and which way it faces. Here, `production/positions.csv`. |
| **PCBA** | Printed circuit board assembly: the service where the factory buys the parts and solders them on, rather than shipping a bare board. |
| **DNP** | Do not populate: a footprint on the board deliberately left empty. |
| **SMD / SMT** | Surface-mount: parts that sit on top of the copper. Machine-placed. |
| **THT** | Through-hole: parts whose legs go through the board and are soldered on the far side. |
| **LCSC code** | The `C…` number identifying a part in JLCPCB's own warehouse, e.g. `C2913202` for the ESP32 module. The BOM you upload uses these. |
| **Basic / Extended part** | JLCPCB's two stock classes. Extended parts carry a small one-off loading fee per part type, which is why the parts list has been tuned to use fewer of them. |
| **DFM** | Design for manufacture: the factory's automated check, which may raise a note on your order. |
| **Outer copper weight** | How thick the copper on the board is, in ounces per square foot. 1 oz is the normal default and is what this board is designed for. |
| **Tooling holes** | Small extra holes the factory adds so its machines can hold the board during assembly. Let JLCPCB add them. |

---

## Licence

The hardware is licensed under the **CERN Open Hardware Licence Version 2, Strongly Reciprocal
(CERN-OHL-S-2.0)**. See [LICENSE](LICENSE). What that means:

- **You may build this board, use it, modify it and sell it**, including commercially. You do not
  need to ask.
- **If you distribute or sell a board based on this design, you must make your design source
  available under the same CERN-OHL-S v2 licence**, and pass on the copyright and licence notice,
  including any changes you made. That is what "strongly reciprocal" means.
- There is **no warranty of any kind**. If you build one and it does not work, that is your risk.

This is a plain-language summary, not legal advice; the licence text in [LICENSE](LICENSE) governs.

> Copyright © 2026 idc LLC.
> This source describes Open Hardware and is licensed under the CERN-OHL-S v2.
> You may redistribute and modify this source and make products using it under the terms of the
> CERN-OHL-S v2 (https://ohwr.org/cern_ohl_s_v2.txt). This source is distributed WITHOUT ANY
> EXPRESS OR IMPLIED WARRANTY, INCLUDING OF MERCHANTABILITY, SATISFACTORY QUALITY AND FITNESS FOR
> A PARTICULAR PURPOSE. Please see the CERN-OHL-S v2 for applicable conditions.

`SPDX-License-Identifier: CERN-OHL-S-2.0`

Third-party component library files (from SnapEDA, Ultra Librarian and SamacSys) retain their own
terms and are not covered by the project licence. See
[fabrication/THIRD_PARTY.md](fabrication/THIRD_PARTY.md).

---

## Working on the design

Nothing below is needed to order a board.

[docs/HARDWARE.md](docs/HARDWARE.md) is the one document to read before changing anything. It
walks through every block of the schematic, explains why each part is there and what its value
was chosen for, gives the GPIO and connector maps, and ends with the design conventions and the
things that look like mistakes but are deliberate.

### Plots and renders

![Silkscreen full schematic](docs/images/full-capture.png)

**[Schematic PDF](docs/silkscreen_pcb_schematic.pdf)** (single A2 sheet) and
**[PCB layout PDF](docs/silkscreen_pcb_layout.pdf)** (2 pages: the front, then the back as you
see it). Both are plotted from the current source. The board images at the top are renders of the
same files, not the release record.

### Repository layout

```
silkscreen_pcb.kicad_pro / .kicad_sch / .kicad_pcb   KiCad 9 project
sym-lib-table / fp-lib-table                          project-local library tables (${KIPRJMOD}-relative, resolve after a plain clone)
KiCad/9.0/3rdparty/                                   vendored symbols/footprints/3D models actually used by the design
docs/HARDWARE.md                                      hardware documentation
docs/mechanical/                                      board STEP model for case design
docs/images/                                          schematic block crops, full sheet, board renders
docs/silkscreen_pcb_schematic.pdf / _layout.pdf       schematic and PCB plots
fabrication/                                          part_fields.csv + apply script, make_fab_files.py, BOM.md / hand-build BOM, how-to
production/                                           release upload files: JLCPCB gerber zip + jlc_bom.csv + positions.csv; other_fabs/ for PCBWay and NextPCB
LICENSE / NOTICE                                      CERN-OHL-S v2
```

A plain `git clone` opens without missing libraries: every project library path is relative, all
in-repo 3D models resolve, and everything else comes from KiCad's standard libraries (KiCad 9.0.x).

### Bill of materials sources

**[fabrication/BOM.md](fabrication/BOM.md)** is the current, netlist-derived sourcing reference:
the optimized JLC build and the hand-build (DigiKey) list, with prices and the reasons for each
swap. Both come from [`fabrication/part_fields.csv`](fabrication/part_fields.csv), which maps every
reference to its prime manufacturer part number and its LCSC code. Accepted factory changes must
still be frozen in the release records.

### Regenerating the release files

The project and the reviewed exports use **KiCad 9.0.6**. Keep a backup before saving with a newer
major version; newer file formats may not reopen in KiCad 9.

For JLCPCB, use the KiCad **Fabrication Toolkit** plugin for the placement export: it applies JLC's
part-rotation database and reads the `LCSC` field from the footprints (set by
`fabrication/apply_part_fields.py`, see [fabrication/README.md](fabrication/README.md)).
**Regenerate the whole Toolkit set after every schematic or PCB save.** A stale `positions.csv`
silently misses new parts.

Raw `kicad-cli` exports, as a cross-check only and not a replacement for the reviewed Toolkit set:

```bash
kicad-cli pcb export gerbers -o fabrication/gerbers/ \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts \
  --no-protel-ext --subtract-soldermask silkscreen_pcb.kicad_pcb
kicad-cli pcb export drill -o fabrication/gerbers/ --format excellon \
  --drill-origin absolute --excellon-units mm --excellon-separate-th silkscreen_pcb.kicad_pcb
kicad-cli pcb export pos -o fabrication/assembly/cpl.csv --format csv --units mm --side both silkscreen_pcb.kicad_pcb
```

See [fabrication/README.md](fabrication/README.md) for the release-file workflow and the
assembly checklist.

---

Predecessor project: [de-link.me](https://de-link.me).
