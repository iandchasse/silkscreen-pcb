# Silkscreen Reader PCB — Rev 1.01 Independent Audit & Actionable Handoff

* **Audit date:** 2026-10-15
* **Independent review and corrections:** 2026-10-18. Every claim below was re-checked against the board, the netlist, the datasheets and the firmware. The numbers largely reproduce, but several action items would have gone wrong as written; they are corrected in place and marked **[corrected 2026-10-18]**. The safe documentation fixes (`ACT-DOC-1` to `ACT-DOC-6`) and `ACT-SCH-1` were applied the same day; `ACT-FAB-1` (method corrected) stays open; `ACT-PCB-1` and `ACT-SCH-2` were applied on 2026-10-22. Follow-up analysis of `ACT-SCH-2`: [`SCH-2_CHARGE_ENABLE.md`](./SCH-2_CHARGE_ENABLE.md).
* **Target commit evaluated:** `80f70e9` on `master` (**Rev 1.01**, title block dated `2026-09-30`, KiCad 9.0.6)
* **Starting premise:** Rev 1.0 boards were fabricated and assembled and work as working prototypes in the closed beta; checks so far are surface-level (see the README's status note). This audit evaluated the Rev 1.0 → Rev 1.01 delta and audited the full Rev 1.01 schematic (`silkscreen_pcb.kicad_sch`), layout (`silkscreen_pcb.kicad_pcb`), manufacturing package (`production/`), and documentation (`README.md`, `docs/HARDWARE.md`, `fabrication/`) with fresh eyes.

| Document in this folder | Scope | Action status |
|---|---|---|
| [`AUDIT.md`](./AUDIT.md) *(this file)* | Parts I & II: Electrical, schematic, layout, cut-line, DFM/DFA, and doc-sync findings with **Author Dispositions & Action Queue** | **Active handoff**: `ACT-FAB-1` is open; `ACT-SCH-2` (with `R79`/`R80` ×10) and `ACT-PCB-1` were applied 2026-10-22 together with the `J1` swap; the rest were applied 2026-10-18 |
| [`EMI_EMC_ANALYSIS.md`](./EMI_EMC_ANALYSIS.md) | Part III: Quantitative 2-layer EMI/EMC, return-path slot crossings, switching loop areas, 2.4 GHz antenna keepout, and IEC 61000-4-2 ESD analysis | **Informational reference only** — not queued for action (two figures corrected 2026-10-18) |
| [`CERTIFICATION_AND_TEST_PLAN.md`](./CERTIFICATION_AND_TEST_PLAN.md) | Part IV: Formal FCC / CE RED / ISED / UL 62368-1 / UN 38.3 certification roadmap, test firmware specs, pre-compliance bench setup, and Crowd Supply health | **Informational reference only** — not queued for action (model name and scores qualified 2026-10-18) |
| [`SCH-2_CHARGE_ENABLE.md`](./SCH-2_CHARGE_ENABLE.md) (+ [`sch2-sim/`](./sch2-sim/)) | Follow-up to `ACT-SCH-2` (2026-10-18): simulations of the `TP4056` `CE` gate on `USB_VBUS` (static states, plug-in transient, leakage margin), a layout prototype, a bench plan and a recommendation | **Applied 2026-10-22** (SCH-2+ and the §8 `R79`/`R80` option are in the schematic, board, part fields and production files; bench check pending) |
| [`J1_USB_C_OPTIONS.md`](./J1_USB_C_OPTIONS.md) | Research note (2026-10-20): USB-C receptacle options for `J1` compared by hand-soldering difficulty and price | **Applied 2026-10-22**: `J1` is the 12-pad SMD part (section 9 of the note) |

---

## 1. Executive Summary & Action Queue (For Next Agent / Author)

Rev 1.01 has **0 ERC errors**, **0 unconnected items**, **0 schematic-to-PCB parity mismatches**, and a verified Gerber/drill archive (`production/Silkscreen_Reader_PCB_1.01.zip` has 0 primitive diffs against a fresh `kicad-cli` plot).

Below is the consolidated queue of **actionable items** sorted by type so an agent or the author can execute them cleanly:

### 1.1 Documentation & Build-Guide Edits (No PCB Respin Required)

| ID | Target File(s) | Exact Action to Take |
|---|---|---|
| **ACT-DOC-1** (`[SCH-H1]`, `[SCH-M4]`) | [`README.md`](../../README.md), [`docs/LED_ALT.md`](../LED_ALT.md), [`fabrication/BOM.md`](../../fabrication/BOM.md), [`docs/HARDWARE.md`](../HARDWARE.md) (§13.1) | **Status: applied 2026-10-18 (most of it already existed).** **Prefer pre-ordering `TPS923610DRLR` over substituting `TPS923611DRLR`.** Already in place before this review: the README lists the pre-order as option 1 and the swap as option 2, HARDWARE.md §13.1 documents the `C9` dump and the ~10 s wait, and the firmware (`FrontlightManager`, `railSafeNow()`) holds `COLOR_SEL` after a trip until `LED_MONIT` reads under 15 V (4 s cap) and then tries the other string. Added: a "second choice" sentence at each `TPS923611` swap (README, `fabrication/BOM.md`, `LED_ALT.md` §9) and the wait rule in the §13.1 `COLOR_SEL` bullet. **[corrected 2026-10-18]** The `LED_MONIT` ADC-ceiling argument is moot, because the firmware trips at 23 V (2.46 V at `IO2`), below where the ADC saturates; the real cost of the `TPS923611` is the larger `C9` dump (§2.1). |
| **ACT-DOC-2** (`[SCH-M1]`, `[DFM-H2]`, `[DFM-M1]`) | [`README.md`](../../README.md), [`docs/HARDWARE.md`](../HARDWARE.md) (§9.2, §16) | **Status: applied 2026-10-18.** **Cut-down boards: `R62` and the builder.** The README's cut-down section already pointed builders to the experimental X3-size Gerbers, which need no sawing (no saw-kerf risk, no exposed live stubs on `P+`/`3V3`/`LED_SW`/`I2C_SDA`/`I2C_SCL`). Added for users who do saw a full-size board: **`R62` (`10 kΩ` at `(101.20, 66.40)`, `SW10`'s old series resistor) stays on the main board with one pad on a sawn `B.Cu` stub; remove it with `R36` and `R73`, or move it onto the `R72` pads** (which need exactly a `10 kΩ`), because a saw burr between that stub and `GND` would cap `PWR_BUTTON` at 1.57 V (the ESP32-S3 needs 2.475 V for a high). **[corrected 2026-10-18]** The `GND` via at `(97.350, 62.700)` is not next to the tongue-neck slot (`x` 89.59–94.89, `y` 61.40–62.50); it is 2.5 mm east of it. The real risk is the saw kerf: the via's upper edge is at `y = 62.400`, 0.40 mm below the `y = 62.00` cut, so a kerf wider than about 0.8 mm centred on it clips the via. |
| **ACT-DOC-3** (`[SCH-L1a]`) | [`docs/HARDWARE.md`](../HARDWARE.md) (§6.2) | **Status: applied 2026-10-18.** **E-paper boost start-up.** §6.2 now says that when `3V3` first comes up, `L1` (`47 µH`) charges both `C14` (`4.7 µF/50 V` via `D5` to `PREVGH`) and `C11` (`4.7 µF/50 V` via `D6` to `GND`) in parallel: `9.4 µF` nominal, about `8.4 µF` at bias, an LC half-period of `62–66 µs`. `3V3` itself takes `~165–175 µs` to rise (the `TLV75533P` current limit charging the roughly `28 µF` on the rail), so the start-up peak is about `0.3 A`, well under `L1`'s `1.1 A` Isat. **[corrected 2026-10-18]** A separate simulation gives `0.27–0.30 A`, not the `0.25–0.45 A` first quoted. |
| **ACT-DOC-4** (`[SCH-L1b]`) | [`docs/HARDWARE.md`](../HARDWARE.md) (§7, Monitoring, protection and connector) | **Status: applied 2026-10-18.** **Frontlight boost across a USB hot-plug / switchover.** With the light off and a depleted `3.0 V` cell, `U2` (`TPS2116DRL`) moves `LDO_IN` to `5.0 V` in `~8 µs` (`VOUT > 1.0 V`, so soft-start is inactive). The `2 V` step into the `L2` (`10 µH`) + `C9` (`4.7 µF`) tank (`Z0 ≈ 1.5–1.6 Ω`) gives a damped current pulse of `~0.9–0.97 A` (inside `L2`'s `1.0 A` rating) and charges `C9`, and so `LED_SW`, to `~5.3–5.8 V` through the high-side body diode. **[corrected 2026-10-18]** "Confirmed benign on hardware" is dropped: nothing in the repository records a hardware measurement, and these figures are simulated (own run: `0.89–0.97 A`, `5.3–5.4 V`). With the light on, `C9` sits near the string voltage (`~15 V`), the body diode is reverse-biased and the step does nothing. |
| **ACT-DOC-5** (`[SCH-L1c]`) | [`docs/HARDWARE.md`](../HARDWARE.md) (§5, Power gating) | **Status: applied 2026-10-18.** **MicroSD (`J7`) turn-on and write-burst droop.** §5 now quotes the modelled figures from §2.6: `C36` + `C37` at `J7`, backed by `C6` and `C32` on `3V3`, keep `3V3` within **`10–40 mV`** during 50–200 mA SDMMC bursts with the card on (**[corrected 2026-10-18]** the first summary said `8.5–34 mV`; §2.6 itself gives `9.9–39.5 mV`), and bound the `Q7` turn-on droop at `U4` (`C32`) to **`~274 mV` (`V_min` ≈ 3.03 V)**, or **`~305 mV` (≈ 3.0 V)** with a simultaneous `350 mA` Wi-Fi TX burst. Brownout is only plausible if `SD_ACTIVATE` is toggled at kilohertz rates, faster than the bulk caps recharge. |
| **ACT-DOC-6** (`[Part I §3]`) | [`README.md`](../../README.md) (Step 6), [`fabrication/README.md`](../../fabrication/README.md), [`fabrication/BOM_handbuild_digikey.csv`](../../fabrication/BOM_handbuild_digikey.csv) | **Status: applied 2026-10-18.** **Placement-preview checklist & DigiKey BOM sync.** `U10` (`TPS923610DRLR`) and the polarized diodes `D3`–`D6` (cathode on pad 1) are added to the JLCPCB placement-preview checks in `README.md` Step 6 and `fabrication/README.md`. The `U13` row in `BOM_handbuild_digikey.csv` now reads `DS3231MZ+TRL` at `$13.85` (it was `DS3231MZ+` at an estimated `$5.50`), matching `fabrication/part_fields.csv` and the `$66` hand-build budget in `fabrication/BOM.md`; the other `est` prices in that file remain estimates. |

### 1.2 Fabrication Script Fix (No PCB Respin Required)

| ID | Target File(s) | Exact Action to Take |
|---|---|---|
| **ACT-FAB-1** (`[DFM-H1]`) | [`fabrication/make_fab_files.py`](../../fabrication/make_fab_files.py), [`production/other_fabs/`](../../production/other_fabs/) | **Status: open, low priority. [corrected 2026-10-18] Do not copy the `FT` offsets into `make_fab_files.py`.** The problem is real: `J4` (`FH34SRJ-6S-0.5SH(50)`) has its footprint origin `0.730 mm` west of its copper (`(92.500, 126.000)` anchor; the pad bounding box is centred at `(93.230, 125.994)`), so the raw KiCad rows for it in `nextpcb_centroid.csv`, `split/nextpcb_centroid_smd.csv` and `placement_bottom_kicad.csv` sit `0.73 mm` off the pads. But `FT Position Offset` (`-0.73,0.218`) and `FT Rotation Offset` are JLCPCB-library corrections, and `make_fab_files.py` says in its own docstring that it deliberately does not apply them to other assemblers. Reusing them would also be wrong in Y: JLC's `+0.218` is not the pad-centre offset (`-0.006 mm` in board coordinates), so `J4` would land `0.21 mm` off. If one of these fabs is ever used, correct `J4` only, from its pad geometry (`+0.730` in X, `-0.006` in Y, board coordinates), after that fab's own placement preview confirms its library reference point, or fix it in that preview as for JLC. These files have not been used for an order. |

### 1.3 Schematic & Layout Items Queued for Next KiCad Edit / Future Spin

| ID | Target File(s) | Exact Action to Take |
|---|---|---|
| **ACT-SCH-1** (`[SCH-L1d]`) | [`silkscreen_pcb.kicad_sch`](../../silkscreen_pcb.kicad_sch), [`docs/silkscreen_pcb_schematic.pdf`](../silkscreen_pcb_schematic.pdf) | **Status: applied 2026-10-18 (text only: netlist and ERC unchanged, schematic PDF re-plotted).** **Stale schematic text.** 1. In the `TPS923` frontlight text box, `LED_ACTIVATE` is now `PWM_LED`, and "Never enable with J3 unplugged" now says that with no light connected `LED_MONIT` (software trip ~23 V) and the `U10` OVP latch protect the driver, and to avoid enabling it with `J3` and `J6` empty. 2. In the `TP4056` text, "R6 4.7kohm -> 255mA charge rate" now reads `~234mA` (`IBAT = VPROG/RPROG × 1100`, so 211–257 mA over the 0.9–1.1 V `VPROG` spread; TOPPOWER `TP4056`, `C16581`). |
| **ACT-SCH-2** (`[SCH-M3]`) | [`silkscreen_pcb.kicad_sch`](../../silkscreen_pcb.kicad_sch), [`silkscreen_pcb.kicad_pcb`](../../silkscreen_pcb.kicad_pcb) | **Status: applied 2026-10-22 as SCH-2+ (`R81` 100 kΩ, `R82` 10 kΩ) together with `R79`/`R80` ×10; the bench check on the first Rev 1.02 board is still to do.** **Move `Q2` source (`Q2.2`) and `R81` (`R81.2`) from `3V3` to `USB_VBUS`**, which makes the `TP4056` `CE` gate `(forward battery present) AND (USB present)`, removes the continuous `6.6 µA` sleep drain through `R81`+`R82`, stops `CE` sitting at `3.3 V` while `VCC` is `0 V`, and removes the charger's 3V3 feed across the cut line. **[corrected 2026-10-18]** The static logic table in §2.4 is right, but "100 %" overlooked the plug-in transient: with no or a reversed cell the gate floats behind `R81` and a fast `USB_VBUS` edge couples onto `CE` (the as-built wiring has a smaller version of this). Simulated result: harmless but longer and higher (`~4.3–4.7 V`, `~250 µs`) with `R81`/`R82` unchanged; **`R81` = 100 kΩ and `R82` = 10 kΩ ("SCH-2+", existing Basic parts) shrink it to `≤ 2 µs`** and give 10–100× more leakage margin. Full analysis, layout recipe (DRC-clean on a scratch copy), bench plan and numbers: [`SCH-2_CHARGE_ENABLE.md`](./SCH-2_CHARGE_ENABLE.md). |
| **ACT-PCB-1** (`[DFM-M2]`) | [`silkscreen_pcb.kicad_pcb`](../../silkscreen_pcb.kicad_pcb) | **Status: applied 2026-10-22 (done in the same edit as `ACT-SCH-2`).** **Fix the `1 µm` `3V3` stub at `(101.000, 64.900)` on `B.Cu`.** In commit `5809233` the `0.141 mm` diagonal `(101.001, 64.900) → (101.101, 65.000)` was deleted but the `1 µm` segment `(101.000, 64.900) → (101.001, 64.900)` (`uuid = 157ac2d7-cd6c-4a42-909e-956bb41befcb`) stayed, leaving a `0.100 mm` centreline gap to the spine at `x = 101.101` bridged only by round end caps. **[corrected 2026-10-18]** Drag the stub's free end to `(101.101, 64.900)`; it then joins the 45° link segment `47cde673` (`(100.900, 64.800) → (101.000, 64.900)`) to the spine. The "adjacent segment `(99.673401, 64.9) → (101, 64.9)`" the first version told you to extend never existed in any revision. Four tiny segments were listed, but **45 segments on the board are under 50 µm** (four under 2 µm: this stub, the `15 nm` one on `Net-(Q5-S)` at `(50.351, 122.500)` and the two `1.4 µm` ones on `I2C_SCL`); only the `1 µm` stub is worth touching, and **never use *Cleanup Tracks & Vias***, which deletes the intentional front-button tab stubs. If `ACT-SCH-2` is adopted, do both in the same edit. |

---

## 2. Detailed Schematic & Electrical Findings & Author Dispositions

### 2.1 `[SCH-H1]` — Frontlight `C9` (`4.7 µF/50 V`) Capacitive Dump During Single-String-Open `COLOR_SEL` Blending
* **Author Disposition:** *Noted for documentation and firmware awareness. Hot-plugging during the milliseconds before OVP trips is not physically realistic; for the single-burned-out-string + `COLOR_SEL` blend edge case, document the behavior and add a disclaimer by the `TPS923611` suggestion recommending pre-ordering `TPS923610` instead (which only takes a few days).*
* **Technical Clarification (Why Single-String-Open Differs from Both-Strings-Open):**
  * When **both** LED strings are open (e.g., `J3` unplugged), `LED_SW` rises to `~23 V` (software `LED_MONIT` trip) or `24.5 V` (`U10` hardware OVP) and shuts off boost switching. Because no load path is present, `C9` (`4.7 µF/50 V`) simply holds its charge and bleeds harmlessly down through `R39 + R41 = 1.12 MΩ` ($\tau \approx 5\,\text{s}$).
  * However, if **only one string fails open** (say the warm string on `W-` is open, while the cool string on `C-` is intact with $V_F \approx 15\,\text{V}$), and firmware blends by toggling `COLOR_SEL` (`IO40`):
    1. On the warm phase (`COLOR_SEL = 1` → `Q5` ON, `Q6` OFF), `U10` sees `FB = 0 V` and pumps `C9` up to OVP (`23–25.5 V` on `TPS923610`, or `29.6–31.4 V` on `TPS923611`). Even once software `LED_MONIT` or hardware OVP stops `U10` from switching, **passive capacitor `C9` (`4.7 µF`) is already charged to `23–31.4 V`**.
    2. The instant `COLOR_SEL` drops to `0` (either on the next blend half-cycle OR when firmware disables the frontlight and drives `COLOR_SEL = 0`), inverter `U12` (`74LVC1G04`) immediately drives `COLOR_SEL_INV = 3.3 V`, turning **`Q6` (`C-`) ON** and connecting the intact `15 V` cool LED string directly across the charged `C9` capacitor!
    3. Neither `U10` OVP nor software `PWM_LED = 0` can prevent `C9` from dumping its stored charge through the intact LED string, `Q6` ($R_{DS(\text{on})} \approx 2\,\Omega$), and `R37` ($15\,\Omega$):
       $$I_{\text{peak}} = \frac{V_{C9} - V_{F,\text{string}}}{R_{\text{dyn}} + R_{DS(\text{on})} + R_{37}}$$
       * **[corrected 2026-10-18]** `U10.3` (`FB`) has a **5.5 V** absolute maximum (TPS923610 datasheet, §6.1; 6 V is the `VIN` pin's rating, not `FB`'s), and the result depends heavily on the surviving string's dynamic resistance. Modelled with a 15 V string at 13 mA, `Q6` at 2 Ω and `R37` = 15 Ω, at the **TPS923610's** 25.5 V maximum OVP: `~125 mA` / `1.9 V` at `FB` for a string with 75 Ω of dynamic resistance, `~230 mA` / `3.5 V` at 30 Ω, `~290 mA` / `4.4 V` at 20 Ω and `~390 mA` / `5.9 V` at 10 Ω; at the firmware's 23 V trip, `1.5 V` (75 Ω) to `4.5 V` (10 Ω). So the TPS923610 is **not unconditionally** inside the `FB` rating: a low-resistance string dumped from the OVP ceiling exceeds it.
       * **With `TPS923611`** (31.4 V maximum OVP) the same strings give `~190 mA` / `2.8 V` (75 Ω) to `~610 mA` / `9.2 V` (10 Ω), above `FB`'s rating for any string under about 30 Ω.
* **Actionable Outcome (`ACT-DOC-1`):**
  1. Add a note to the `TPS923611` substitute sections in `README.md`, `docs/LED_ALT.md`, and `fabrication/BOM.md` recommending that builders **pre-order `TPS923610DRLR`** (only a few days lead time at JLCPCB) rather than substituting `TPS923611`.
  2. In firmware, if `LED_MONIT` (`IO2`) trips open-load protection ($V_{\text{LED\_SW}} > 18\,\text{V}$) while `COLOR_SEL = 1`, keep `COLOR_SEL = 1` (with `PWM_LED = 0`) for ~2 seconds until `LED_MONIT` reads $< 1.60\,\text{V}$ ($< 15\,\text{V}$ on `C9`) before releasing `COLOR_SEL` to `0`.
  * **Status 2026-10-18:** item 1 is applied (see `ACT-DOC-1`); item 2 already exists in the firmware (`railSafeNow()`: 15 V, up to 4 s, then the other string is tried) and is now written down in HARDWARE.md §13.1.

---

### 2.2 `[SCH-M1]` — Cut-Down Board: Orphaned `R62` (`10 kΩ`) Re-Use at `R72` & `silkscreenreader.com/builder` Guidance
* **Author Disposition:** *Confirmed that cutting the board works when the documented parts are removed; add `R62` to the list of parts to remove on a cut-down board, and recommend moving `R62` directly to the `R72` pads (saving a 10 kΩ resistor and disconnecting the cut-edge stub). Also advise users to use `silkscreenreader.com/builder` for pre-cut 3.68" Gerbers.*
* **Technical Summary:**
  * On a full-size board cut at `y = 61.86 / 62.00 mm`, `SW10` (`(101.71, 52.25)`) is cut off, but `R62` (`10 kΩ` at `(101.20, 66.40)`) remains on the kept main board with its Pad 1 connected to the sawn `B.Cu` stub `Net-(R62-Pad1)` at `x = 102.112 mm` (`0.151 mm` from `B.Cu` `GND`).
  * So long as the cut is clean (no copper burr shorting `Net-(R62-Pad1)` to `GND` across that `0.151 mm` gap), `R62` Pad 1 floats and does not disturb `PWR_BUTTON`. However, if a saw burr bridges `Net-(R62-Pad1)` to `GND`, `R62` (10 kΩ to `GND`) divides against `R72` (10 kΩ to `3V3`), capping `PWR_BUTTON` at `1.571 V` (below the ESP32-S3's $V_{IH,\min} = 2.475\,\text{V}$).
  * **Desoldering `R62` and moving it onto the adjacent `R72` pads** solves both problems at once: it completely disconnects `PWR_BUTTON` (`IO18`) from the sawn `x = 102.112 mm` edge stub *and* supplies the exact `10 kΩ` pull-up needed at `R72` for repurposing `SW7` without needing a spare resistor (`ACT-DOC-2`).

---

### 2.3 `[SCH-M2]` — `R84` (`1 Ω`) + `TPS2116` Switchover Behavior on Low Battery (`Accepted / Closed`)
* **Author Disposition:** *Accepted as-is (`1 Ω` `C22936` is a JLC Basic part and cheaper than `0.47 Ω`; any brief switchover chatter only occurs when `P+` is near ~3.0–3.3 V and resolves within milliseconds as `LDO_IN` equalizes).*
* **Status:** Closed — no hardware or BOM change required.

---

### 2.4 `[SCH-M3]` — Moving `Q2.2` and `R81.2` from `3V3` to `USB_VBUS`: Full Functional Verification
* **Author Question:** *"I forget the intended idea behind this circuit, only enabling charge when a battery is present? Does moving vbus to the 3v3 slot essentially also functionally take it further by enabling it with a battery present AND usb present?"*
* **Answer — yes for every static state; the plug-in transient needs a check (see the note under the table):**
  1. **Original Purpose of `Q9` + `Q2` ("Fix 4" in commit `0ce9e8f`):**
     * Originally, `U11` (`TP4056`) Pin 8 (`CE`) was tied directly to `USB_VBUS`. That meant `U11` was enabled whenever USB was plugged in—even if **no battery was connected** (causing `TP4056` to cycle on `C3`/`C26`) or if a **battery was plugged in backwards (`B+ < B-`)** (causing `TP4056` to drive charge current against the reversed cell / body diodes).
     * `Q9` (`BSS138`, source on `B-`, gate driven by `R79` `100 kΩ` from `B+` and `R80` `1 MΩ` to `B-`) was added as a **forward-polarity battery detector**: `Q9` only turns ON when $V_{B+} - V_{B-} \ge 2.4\,\text{V}$ in the **correct polarity**. When `Q9` turns ON, it pulls `/DET_NODE` (`Q2` gate) low to `B-`, which turns ON P-FET `Q2` (`AO3401A`) to pull `U11.8` (`CE`) high.
  2. **Why `Q2.2` (Source) and `R81.2` Were Tied to `3V3` in Rev 1.0, and What Goes Wrong:**
     * Because `Q2.2` and `R81.2` were tied to always-on `3V3`, `Q2` is turned ON **24/7 whenever a battery is plugged in—even when USB is unplugged (`USB_VBUS = 0 V`)**!
     * That means while running on battery in deep sleep:
       * `R81` (`1 MΩ` from `3V3` to `/DET_NODE` at `0 V`) and `R82` (`1 MΩ` from `CE` at `3.3 V` to `GND`) each burn `3.3 µA`, wasting **`6.6 µA` continuously** (`11.4%` of the entire `58 µA` sleep budget).
       * `U11.8` (`CE`) is held hard at `3.3 V` through `Q2` (`~60 mΩ`) while `U11.4` (`VCC` = `USB_VBUS`) sits at `0 V` (unpowered IC input driven above its supply rail).
       * On a cut-down board, `3V3` had to be routed up to `Q2`/`R81` (`3edd0c8`).
  3. **What Happens When `Q2.2` and `R81.2` Are Moved from `3V3` to `USB_VBUS`:**
     * It converts the circuit into a true hardware **`AND` gate: `CE = (Forward Battery ≥ 2.4 V) AND (USB_VBUS Present)`**:

| Operating State | `Q9` (`BSS138`) | `Q2` (`AO3401A`, Source on `USB_VBUS`) | `TP4056` Pin 8 (`CE`) | Sleep Drain in `R81` + `R82` |
|---|---|---|---|---|
| **1. On Battery Only (`USB_VBUS = 0 V`), Good Battery (`3.0–4.2 V`)** | ON (`/DET_NODE ≈ 0 V`) | Source is `0 V` ($V_{GS} = 0\,\text{V}$) → **Inactive** | **`0.0 V`** (matches `VCC = 0 V`, zero back-feed risk!) | **`0.0 µA`** (**saves `6.6 µA` in deep sleep!**) |
| **2. USB Plugged In (`USB_VBUS = 5.0 V`), Good Battery (`≥ 2.4 V`)** | ON (`/DET_NODE ≈ 0 V`) | $V_{GS} = -5.0\,\text{V}$ → **Fully ON** | **`5.0 V` (`USB_VBUS`)** → **Charging Enabled** | Powered from USB (`10 µA` from VBUS, `0 µA` from battery) |
| **3. USB Plugged In (`5.0 V`), Good Battery Over-Discharged (`DW01A` tripped, `B- ≈ +0.6 V` via `Q1` charge body diode)** | ON (`/DET_NODE ≈ +0.6 V`) | $V_{GS} = 0.6 - 5.0 = -4.4\,\text{V}$ → **Fully ON** (stronger gate drive than $-2.7\,\text{V}$ from `3V3`!) | **`5.0 V`** → **Wakes & Recharges Tripped Pack** | Powered from USB |
| **4. USB Plugged In (`5.0 V`), Battery Reversed (`B+ < B-`) or Unplugged** | **OFF** | `R81` holds Gate = Source = `5.0 V` ($V_{GS} = 0\,\text{V}$) → **OFF** | **`0.0 V`** (pulled down by `R82`) → **Charger Disabled** | `0.0 µA` |

* **Actionable Outcome (`ACT-SCH-2`):** Move `Q2` pin 2 and `R81` pin 2 from `3V3` to `USB_VBUS` (which is already right next to `U11` and `Q2` on the board). **Status 2026-10-22: applied (SCH-2+).** **[corrected 2026-10-18]** The table above is the static behaviour and is right. What it leaves out is the plug-in moment: with no or a reversed cell `Q9` is off, so `Q2`'s gate floats behind `R81` while `USB_VBUS` steps up, and the gate capacitances couple a pulse onto `CE`. The as-built wiring has a smaller version of the same pulse (`3V3` rising ~1 ms after `VBUS`). Simulated: ~4.3–4.7 V for ~250 µs with `R81`/`R82` at 1 MΩ, nothing latches, and with `R81` = 100 kΩ and `R82` = 10 kΩ it drops to ≤ 2 µs. The `CHRG`/`STDBY` pins' back-feed is a separate bench check. See [`SCH-2_CHARGE_ENABLE.md`](./SCH-2_CHARGE_ENABLE.md).

---

### 2.5 `[SCH-M4]` — `TPS923611` Substitute vs. `LED_MONIT` ADC Ceiling
* **Author Disposition:** *`LED_MONIT` is intended to trip in firmware (`~23 V`) before hardware OVP kicks in; add a recommendation in the docs to prefer pre-ordering `TPS923610`.*
* **Status:** Covered under **`ACT-DOC-1`**. **[corrected 2026-10-18]** The ADC-ceiling concern does not arise: the firmware trips at 23 V (2.46 V at `IO2`), below the ADC's 2.90 V linear limit, and a `TPS923611` simply reads as saturated, which is still "above the trip". The cost of the `TPS923611` is the larger `C9` dump in §2.1.

---

### 2.6 `[SCH-L1]` — Deep-Dive Research: MicroSD (`J7`) Turn-On & Burst Droop (`ACT-DOC-5`)
* **Author Request:** *"do more research on microsd burst. I think the nearby cap should be enough to cover this condition unless toggling insanely fast"*
* **Quantitative Physical & RLC Network Analysis:**
  We extracted the exact coordinates of every `3V3` and `SD_VDD` capacitor on `silkscreen_pcb.kicad_pcb` and simulated the two-port RLC network connecting `U3` (`TLV75533P`), `U4` (`ESP32-S3`), `Q7` (`AO3401A`), and `J7` (`microSD`):
  * **Physical Component Placement on `silkscreen_pcb.kicad_pcb`:**
    * **Node 1 (LDO / `Q7` cluster):** `U3` at `(78.65, 84.15)`, `C6` (`22 µF` 0805, $C_{\text{eff}} \approx 12.0\,\mu\text{F}$ at 3.3 V) at `(75.10, 84.80)` (**`9.95 mm` from `Q7`**), and `C21` (`1 µF` 0603, $C_{\text{eff}} \approx 0.6\,\mu\text{F}$) at `(74.80, 81.20)` (**`7.83 mm` from `Q7`**).
    * **Node 2 (`ESP32-S3` `U4` cluster):** `U4` at `(57.50, 102.50)` is locally decoupled by its own dedicated **`C32` (`22 µF` 0805, $C_{\text{eff}} \approx 12.0\,\mu\text{F}$)** at `(53.50, 89.01)`, `C33` (`0.1 µF`) at `(53.50, 87.00)`, and `C10` (`4.7 µF`, $C_{\text{eff}} \approx 2.5\,\mu\text{F}$) at `(92.10, 110.66)`, separated from Node 1 (`Q7`/`C6`) by `~28 mm` of `0.25 mm` `3V3` trace ($R_{12} \approx 56\,\text{m}\Omega$, $L_{12} \approx 22\,\text{nH}$).
    * **Node 3 (Switched `SD_VDD` at `J7`):** `Q7` at `(81.53, 77.20)` feeds `J7` at `(63.05, 84.60)` via `27.08 mm` of `0.25 mm` `SD_VDD` trace ($R_{\text{trace}} \approx 54\,\text{m}\Omega$, $L_{\text{trace}} \approx 22\,\text{nH}$), with `C36` (`0.1 µF`) at `(62.50, 86.70)` (`2.17 mm` from `J7`) and `C37` (`1 µF`) at `(62.30, 88.20)` (`3.68 mm` from `J7`), plus the microSD card's internal decoupling ($C_{\text{card}} \approx 1.0\text{–}2.2\,\mu\text{F}$ typical).
  * **Case A — Active SDMMC Read/Write Current Bursts (`Q7` Already ON):**
    * Once `Q7` is ON ($R_{DS(\text{on})} \approx 45\,\text{m}\Omega$), `C36` + `C37` + $C_{\text{card}}$ (`~2.2–3.0 µF` effective right at `J7`) are connected in parallel with `C6` + `C32` + `C10` (`~28 µF` effective on `3V3`) through only $R_{\text{path}} = R_{DS(\text{on}),Q7} + R_{\text{trace}} \approx 45 + 54 = \mathbf{99\,\text{m}\Omega}$.
    * High-frequency clock-edge spikes ($40\,\text{MHz}$, `< 5 ns`) are supplied 100% locally by `C36` (`0.1 µF`) and `C37` (`1 µF`) located `2.2–3.7 mm` from `J7`.
    * During a sustained block-write current step ($I_{\text{burst}} = 50\text{–}200\,\text{mA}$) over the `~3 µs` response time of `U3` (`TLV75533P`), the combined `~30.5 µF` effective reservoir and `99 mΩ` path resistance produce a total rail dip of only:
      * **`50 mA` burst:** `5.0 mV` DC IR drop + `4.9 mV` transient droop = **`9.9 mV` total dip**
      * **`100 mA` burst:** `9.9 mV` DC IR drop + `9.8 mV` transient droop = **`19.7 mV` total dip**
      * **`150 mA` burst:** `14.9 mV` DC IR drop + `14.8 mV` transient droop = **`29.7 mV` total dip**
      * **`200 mA` burst:** `19.8 mV` DC IR drop + `19.7 mV` transient droop = **`39.5 mV` total dip**
    * **Conclusion on Read/Write Bursts:** Completely negligible (`< 40 mV`). The local caps + `3V3` bulk caps handle active SDMMC bursts with huge margin.
  * **Case B — Cold Turn-On of `Q7` (`SD_ACTIVATE` Driven Low):**
    * `R78` (`1 kΩ` gate resistor) limits `Q7`'s Miller-plateau turn-on slew time to $t_{\text{fall}} \approx 0.8\,\mu\text{s}$, and the `56 mΩ / 22 nH` `3V3` trace between `C6` (at `Q7`/`U3`) and `C32` (at `U4`) isolates the ESP32-S3 from the initial current spike while `C32` (`22 µF` 0805) holds up `U4`:
      * **Board only (`C36` + `C37`, no card inserted, $C_{\text{SD,eff}} = 0.73\,\mu\text{F}$):** Max dip at `U4` (`C32`) is **`98 mV` (`V_min = 3.202 V`)**.
      * **With typical microSD card ($C_{\text{SD,eff}} = 2.23\,\mu\text{F}$), Wi-Fi idle:** Max dip at `U4` (`C32`) is **`274 mV` (`V_min = 3.026 V`)**.
      * **With typical microSD card ($C_{\text{SD,eff}} = 2.23\,\mu\text{F}$) turned ON at the exact peak of a `350 mA` Wi-Fi TX burst:** Max dip at `U4` (`C32`) is **`305 mV` (`V_min = 2.995 V`)**—still comfortably above the ESP32-S3 brownout threshold (`2.43–2.80 V`)!
    * **Conclusion on `Q7` Turn-On:** As the author noted, `C36`/`C37` + the nearby `C6`/`C32` bulk caps cover even simultaneous `Q7` turn-on + Wi-Fi TX (`V_min ≈ 3.00 V`); brownout could only occur if firmware toggled `SD_ACTIVATE` on and off at kilohertz rates faster than `U3` (`750 mA` current limit, `~150 µs` recovery) can recharge the rails, or when the battery is already depleted below `3.3 V`.

---

## 3. Detailed PCB Layout, Cut-Line & DFM Findings & Author Dispositions

### 3.1 `[DFM-H1]` — `J4` (`-0.730 mm` X Offset) in `production/other_fabs/`
* **Author Disposition:** *Good to note to correct (`ACT-FAB-1`).*
* **Summary for Next Agent [corrected 2026-10-18]:** Do **not** parse the `FT Position Offset` / `FT Rotation Offset` fields in `fabrication/make_fab_files.py`: they are JLCPCB-library corrections, the script's docstring says it deliberately leaves them out for other assemblers, and `J4`'s `+0.218` Y component is not a pad-centre offset (the pad bounding box is centred at `(93.230, 125.994)` against the `(92.500, 126.000)` anchor, i.e. `+0.730` in X and `-0.006` in Y). If a non-JLC fab is ever used for `J4`, correct that one row from the pad geometry after the fab's own placement preview confirms its library reference point. `production/positions.csv` (JLC) is already corrected for JLC's library (`Mid X = 93.230 mm`); the other-fab files have not been used for an order.

### 3.2 `[DFM-H2]` & `[DFM-M1]` — Cut-Line Exposed Stubs, Via `(97.350, 62.700)` Kerf Clearance, and Floating Pour Islands
* **Author Disposition:** *This is a DIY sawing risk. Advise anyone wanting a smaller 3.68" board to use `silkscreenreader.com/builder` to obtain pre-trimmed Gerbers that do not require sawing (`ACT-DOC-2`).*
* **Summary of Coordinates (for reference in docs):**
  * `GND` via `(97.350, 62.700)` (`0.60/0.30 mm`) has its upper copper edge at `y = 62.400 mm`, only `0.40 mm` below the `y = 62.00` cut (`0.54 mm` below the marked `y = 61.86` line), so a saw kerf wider than about `0.8 mm` centred on `y = 62.00` clips it. **[corrected 2026-10-18]** It is not next to the tongue-neck slot (`5.30 × 1.10 mm`, `x` 89.59–94.89, `y` 61.40–62.50): it is `2.5 mm` east of the slot's east end.
  * Twelve traces cross `y = 62.00 mm`: `UNUSED_GPIO_3` (`B.Cu` `x = 85.30`), `UNUSED_GPIO_46` (`F.Cu` `x = 85.40`), `UNUSED_GPIO_45` (`F.Cu` `x = 85.75`), unfused `P+` (`F.Cu` `x = 87.40`), `3V3` (`B.Cu` `x = 87.53` and `100.60`), `I2C_SCL` (`F.Cu` `x = 96.10`), `I2C_SDA` (`F.Cu` `x = 97.90`), `LED_SW` (`F.Cu` `x = 98.40`), `W-` (`F.Cu` `x = 101.95`), `Net-(R62-Pad1)` (`B.Cu` `x = 102.11`), and `C-` (`F.Cu` `x = 102.30`).
  * Physical sawing at `y = 62.00 mm` leaves two unvied copper islands on the kept board (`5.51 mm²` on `B.Cu` at `x = 83.74..87.20, y = 62.00..67.43` and `2.30 mm²` on `F.Cu` at `x = 102.55..103.76, y = 62.00..64.44`) that are automatically pruned when generating a native 3.68" board via `silkscreenreader.com/builder`.

### 3.3 `[DFM-M2]` — Unfinished `1 µm` `3V3` Stub at `(101.000, 64.900)` on `B.Cu`
* **Author Disposition:** *Valid, note to fix (`ACT-PCB-1`).*
* **Exact Segments in `silkscreen_pcb.kicad_pcb`:**
  * Segment `uuid = 157ac2d7-cd6c-4a42-909e-956bb41befcb`: `(start 101 64.9) (end 101.001 64.9) (width 0.25) (layer "B.Cu") (net 4)` (`1 µm` long).
  * Real neighbours **[corrected 2026-10-18]**: the link arrives as `47cde673` `(start 100.9 64.8) (end 101 64.9)` (45°, preceded by `(100.9, 64.6) → (100.9, 64.8)`, `(100.7, 64.4) → (100.9, 64.6)` and `(99.485, 64.4) → (100.7, 64.4)`). The `(99.673401, 64.9) → (101, 64.9)` segment the first version named does not exist in any revision of the board.
  * Vertical spine: `(start 101.101 68.561) (end 101.101 62.501) (width 0.25) (layer "B.Cu") (net 4)`.
  * **Fix [corrected 2026-10-18]:** drag the stub's free end from `(101.001, 64.9)` to `(101.101, 64.9)`, which joins `47cde673`'s end to the spine as a `0.1 mm` segment (do not use *Cleanup Tracks & Vias*). Of the 45 segments under 50 µm only this one has a gap worth closing.

### 3.4 `[DFM-M3]` — FPC Solder-Mask Bridges & Via-to-Pad Clearances (`Accepted / Non-Issue in Production`)
* **Author Disposition:** *Confirmed non-issue on actual Rev 1.0 production boards from JLCPCB. Closed.*
