# Doc clean-ups — every modification, one line each

Format: `file §section — before → after — why (finding ID)`
Four files touched: `README.md`, `docs/HARDWARE.md`, `fabrication/README.md`, `NOTICE` (no change needed).
Nothing was committed. No KiCad, BOM, production or fabrication CSV/py file was touched.

## docs/HARDWARE.md

1. §1 What Silkscreen is — `GDEQ426T82` (x4) → `GDEQ0426T82`; added the missing `-T01C` row and a sentence saying the base number is `GDEQ0426T82` and the suffix picks the variant — base part number was wrong and the scheme was never stated (DOCS-21)
2. §1 Optional-by-design — "Touch — only for `-FT01C`-class panels" → "only for `-T01C` / `-FT01C` panels" — `-T01C` is also a touch panel (DOCS-21)
3. §1 Optional-by-design — RTC line now names `U14` as the alternate footprint; added an "Expansion header (`J6` + `U8`/`CR2`/`CR3`)" bullet — U14 exists now; J6's protection was not associated with J6 (HMI-22, item 8)
4. §3.1 USB-C input — "`J1` is a 14-pin USB 2.0 Type-C receptacle" → "a USB 2.0 Type-C receptacle … the ordered GCT `USB4085-GF-A` has **16 contacts**, not 14" — wrong contact count (USB-15)
5. §3.1 `D1` blockquote — "~1 nA reverse leakage" → "~1 nA … **at 25 °C** (0.05 µA at 85 °C, 0.15 µA at 105 °C)" — that was the 25 °C figure only (USB-17)
6. §3.1 hot-plug blockquote — "TI's own TP4056 datasheet" → "the TP4056 datasheet … (the TP4056 is not a TI part)" — wrong attribution (USB-16)
7. §3.3 protection table — one row "Over-current / short | 150 mV | both open" → two rows: over-current (V_OIP 120/150/180 mV) opens the **discharge FET only**, and a separate short-circuit row (V_SIP 1.00–1.35 V) — the DW01A does not open both FETs, and the two thresholds were merged (BAT-14)
8. §3.3 residual drain — "`R56`+`R57` divider draws ~4 µA" → "≈**8 µA of resistors** (~10 µA with the DW01A's standby)", naming `R79`/`R80` as the second network outside the FETs — understated by 2x (BAT-15)
9. §3.5 LDO blockquote — "thermal behavior **on battery** at high sustained load is a qualification item" → "**on USB** … ≈1.55 V drop, T_J past 125 °C at ~280 mA, treat ~250 mA as the USB ceiling; on battery it is a non-issue" — the thermocouple was pointed at the benign case (PWR-15)
10. §3.5 headroom blockquote — deleted "the bulk capacitance … should ride out a short Wi-Fi-TX current pulse" → "**do not expect the bulk capacitance to cover a Wi-Fi TX burst** — 40 µF holds 355 mA for ~5.6 µs; the LDO supplies the whole burst" — the capacitors hold for microseconds, not for the pulse (PWR-16)
11. §3.6 battery monitoring — "(~7 mV at 50 mA, ~73 mV at 500 mA)" → "≈0.24–0.27 Ω → **12–14 mV at 50 mA, 120–135 mV at 500 mA** (up to ≈175 mV)", noting the old figure wrongly counted `U2` — offset understated ~2x (PWR-17)
12. §3.7 USB_STAT table — replaced the "No battery fitted (blinks) | CHRG + STDBY | ~0.45–0.53 V" row with "Charge complete, weak USB | ST + STDBY | 0.53 V", renamed the idle row, and added a paragraph naming the four normal levels 1.98 / 1.19 / 0.60 / 3.30 V — the old row merged two unrelated states and there was no row for ST+STDBY (USB-18, USB-19)
13. §3.7 no-battery paragraph — "The 'no battery' state is a real TP4056 behaviour … blinking CHRG" → "**There is no steady 'no battery fitted' level**: no cell at plug-in reads a steady **3.3 V**; the **0.60 / 0.45 V** alternation happens only if the cell is unplugged while USB is present" — now agrees with §13.1's firmware contract (USB-18, USB-19)
14. §6.2 charge pump — "`R15` (10 k) pulls `Q4`'s gate down" → "`R15` (**1 MΩ**) … **changed from 10 kΩ**; 1 MΩ matches Good Display's reference circuit (`GDEQ0426T82` datasheet §8.2, `R1` = 1 M)" — part changed today (item 8)
15. §5 Storage — new paragraph before the socket-footprint block: the battery sits in the cut-out in front of `J7`, so it is lifted or slid aside to change the card, and that is intended — author's intent was undocumented (SD-V03)
16. §7 frontlight — "`R37` = 15 Ω sets a ~13.3 mA ceiling" → "… **at full `ADIM` duty**" — the figure only holds at 100 % duty (LED-07)
17. §9.1 ladder table — `SW8` "CONFIRM" → "OK"; the row-order line now says "BACK · OK · LEFT · RIGHT (the board silkscreen prints `OK`)" — board silk says OK (LAY-D4)
18. §9.1.1 front-mounted buttons — `SW8` "CONFIRM" → "OK" in the intro and in the idle-current table — same (LAY-D4)
19. §9.1.1 tab paragraph — added: the four netless `F.Cu` tabs are intentional, KiCad's dangling-track warnings are expected, and they are a DIY hand-solder feature, not something a fab should populate — author's intent (item 10)
20. §9.2 power button — "`R72`/`R73`/`R74` are 0 Ω configuration jumpers" → "`R73`/`R74` are 0 Ω jumpers; **`R72` is 10 kΩ, not a 0 Ω link**" — wrong value (MCU-20)
21. §10 RTC — lead-in now says the three VBAT-only consequences apply to `U13`; added a paragraph for **`U14` `RV-8263-C7`**: DNP by default, fit either `U13` or `U14` never both, addresses 0x68 vs 0x51 so no bus conflict, marked `<!-- confirm once U14 is final -->` — new footprint added today (item 8)
22. §11 expansion header pin table — Power row: "`P+` raw battery (12)" → "(12, PPTC-fused — see the rules below)" — new `F2` in series with pin 12 (item 7c)
23. §11 ESD paragraph — added "Which of those go away with `J6`": **`U8`, `CR2`, `CR3` come off with `J6`**; `U9` does not (it also covers SD `DAT0`/`DAT1`); `D3`/`D8` do not (they clamp the front-light nets `LED_SW`/`W−`/`C−`) — protection was not tied to J6's optionality (HMI-22)
24. §11 — new subsection "Rules for anything you plug into `J6`": (1) never pull/drive `IO45` or `IO46` HIGH at power-up or reset, the module will not boot until the accessory is unplugged, use `IO3` for anything that idles high; (2) an external LED string with V_f below the battery voltage is unregulated — it conducts through `L2` and `U10`'s body diode with the driver off, ~43 mA into a single 3 V LED on USB, so use ≥3 LEDs / V_f > 6 V; (3) pin 12 is raw battery positive, **fused by a 0.75 A PPTC** (`0805L075WR`), marked `<!-- confirm once F2 is on the board -->` — rules were undocumented (HMI-02, LED-02, item 7c)
25. §16 Enclosure — added a bullet: the module's PCB antenna overhangs a cut-out with no copper beneath it; keep ~10 mm of air, do not lay the battery over it, no screw bosses, metal inserts, magnets or display backplane in that corner — case designers had no warning (MCU-21)
26. §16 Enclosure — added a bullet: the battery sits in front of the microSD slot, design for lifting it aside (SD-V03)
27. §16 — new "Enclosure dimensions" table (21 rows: outline, cavities, panel, bosses, button centres, apertures, battery bay, antenna keep-out, both slots, cut line) pointing at `mechanical/silkscreen_pcb.step` as authoritative — section had no dimensions (MEC-21)
28. §16 dimensions table — tongue-neck slot listed as the **single 5.30 × 1.10 mm** slot at x 89.59–94.89, y 61.40–62.50; the old four 0.5 mm slots are quoted nowhere — board changed after the review evidence (MEC-21)
29. §16 Frontlight load — added "**13.3 mA at full `ADIM` duty is the correct figure everywhere**", noting the schematic's ~14 mA and the silk's 15 mA are older numbers — three figures in three places (LED-07)
30. §16 Button geometry — "BACK · CONFIRM · LEFT · RIGHT" → "BACK · OK · LEFT · RIGHT", with a parenthetical that earlier drafts said CONFIRM (LAY-D4)
31. §16 — new subsection "Things that look like mistakes and are not": the four dangling `F.Cu` stubs, the empty mirrored silk text box at the tongue neck = the cut line, `H2`/`H5` intentionally out of line, `D2` is a USB-power-present indicator not a charge indicator, and `U10`/`J3`/`U14` use modified stock symbols so `lib_symbol_mismatch` ERC warnings are expected — author's intent notes (item 10)
32. Appendix passive-case table — `C4`/`C6`/`C32` row now names the Murata `GRM21BR61E226ME44L` prime (Samsung `CL21A226MAQNNNE` obsolete at DigiKey) and JLC `C45783`; added a `C2` row: **now a 25 V part** (Samsung `CL10A106MA8NRNC`, LCSC `C96446`, JLC Basic), was 10 V — parts changed today (item 8)
33. Appendix IC table — added the `U14` `RV-8263-C7` row, DNP, "fit either `U13` or `U14`, never both", marked `<!-- confirm once U14 is final -->` (item 8)

## README.md

34. What it is → Screen — added "`GDEQ0426T82` is the base part number and the suffix picks the variant — `-T01C` touch, `-FL01C` front light, `-FT01C` both — so always order by the full suffixed number" (DOCS-21)
35. What you need → microSD card — added that the battery sits in the cut-out in front of the card slot and is lifted or slid aside to change the card, and that this is intended (SD-V03)
36. Step 2 item 5 — "the four narrow slots … 0.5 mm wide, narrower than the factory's usual 1.0 mm minimum … a DFM message … is safe to accept" → "the **two** narrow slots … the long one 47.04 × 1.30 mm, the tongue-neck one **5.30 × 1.10 mm**, both at or above JLCPCB's 1.0 mm minimum, so neither should raise a DFM message" (MEC-21)
37. Choosing a configuration → Core row — "power switch `SW10`" → "power button `SW10`" (MCU-22)
38. Choosing a configuration table — Expansion header references "`J6`, `U8`" → "`J6`, `U8`, `CR2`, `CR3`" (HMI-22)
39. Choosing a configuration table — RTC row now reads "`U13`, `C30` (or `U14` instead of `U13`)"; added an "Alternate RTC | `U14` (**DNP in every standard build**)" row marked `<!-- confirm once U14 is final -->` (item 8)
40. Choosing a configuration → Notes — added a bullet: `U8`/`CR2`/`CR3` come off with `J6`; do **not** remove `U9`, `D3` or `D8` and why (HMI-22)
41. The board and your case — added a bullet: the module's PCB antenna overhangs a cut-out with no copper under it; no battery over that corner, no screws, metal inserts or display backplane near it (MCU-21)
42. Specifications → Input — "power (`SW10`)" → "a wake/power **button** (`SW10` — a wake input, not a hardware power switch; the 3.3 V rail is always live)" (MCU-22)
43. Specifications → RTC — added "A second footprint (`U14`, Micro Crystal RV-8263-C7) is DNP — fit either, never both", marked `<!-- confirm once U14 is final -->` (item 8)

## fabrication/README.md

44. Intro — dropped the stale "(2026-09-18, …)" date from "The current source"; added "Re-count after the in-progress revision: it adds the `U14` RTC alternate (DNP) and an `F2` PPTC on `J6` pin 12" — the date did not match the repo (DOCS-22)
45. Release records → Gerbers/drills — "The 2026-09-18 12:22 zip was verified …" → "The committed zip (2026-09-19, commit `c0eccde`) was verified … at that commit. Re-verify after any board change" (DOCS-22)
46. Release records → Matched order — the `.xls` row is now labelled "**local only, not tracked in this repository**", matching what the root README already says (DOCS-22)
47. Assembly checklist — "The four 0.5 mm 'perforation' polygons … below JLC's 1.0 mm minimum … to be replaced by a single wider slot in the next board revision" → "The tongue neck is now a **single 5.30 × 1.10 mm slot** (x 89.59–94.89, y 61.40–62.50) … no slot DFM note is expected now" (MEC-21)

## NOTICE

48. No change. Checked for naming: the title says "Silkscreen", the source location is `https://github.com/iandchasse/silkscreen-pcb`. Both are the right names in the right context.

## Naming sweep (DOCS-19) — what was checked and left alone

- `de-link` / `de-link.me` in `README.md:10` and `:439`, and `docs/HARDWARE.md` §15 "What changed from de-link" — correct context (de-link is the earlier prototype), left as is.
- `silkscreenreader.com` in `README.md` — the site, correct.
- `silkscreen-pcb` in `NOTICE` — the repo, correct.
- `silkscreen_pcb.kicad_*`, `silkscreen_pcb_schematic.pdf`, `silkscreen_pcb_layout.pdf`, `silkscreen_pcb.step`, `Silkscreen_Reader_PCB_1.0.zip` — file names, left as is.
- No occurrence of `minRead` / `minread` in any of the four files.
