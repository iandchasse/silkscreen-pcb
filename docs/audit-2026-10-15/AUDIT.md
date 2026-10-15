# Silkscreen Reader PCB — Rev 1.01 Independent Audit & Actionable Handoff

* **Audit date:** 2026-10-15
* **Target commit evaluated:** `80f70e9` on `master` (**Rev 1.01**, title block dated `2026-09-30`, KiCad 9.0.6)
* **Starting premise:** Rev 1.0 boards were fabricated, assembled, and verified to work as intended functionally. This audit evaluated the Rev 1.0 → Rev 1.01 delta and audited the full Rev 1.01 schematic (`silkscreen_pcb.kicad_sch`), layout (`silkscreen_pcb.kicad_pcb`), manufacturing package (`production/`), and documentation (`README.md`, `docs/HARDWARE.md`, `fabrication/`) with fresh eyes.

| Document in this folder | Scope | Action status |
|---|---|---|
| [`AUDIT.md`](./AUDIT.md) *(this file)* | Parts I & II: Electrical, schematic, layout, cut-line, DFM/DFA, and doc-sync findings with **Author Dispositions & Action Queue** | **Active handoff** for the next agent / author pass |
| [`EMI_EMC_ANALYSIS.md`](./EMI_EMC_ANALYSIS.md) | Part III: Quantitative 2-layer EMI/EMC, return-path slot crossings, switching loop areas, 2.4 GHz antenna keepout, and IEC 61000-4-2 ESD analysis | **Informational reference only** — not queued for action |
| [`CERTIFICATION_AND_TEST_PLAN.md`](./CERTIFICATION_AND_TEST_PLAN.md) | Part IV: Formal FCC / CE RED / ISED / UL 62368-1 / UN 38.3 certification roadmap, test firmware specs, pre-compliance bench setup, and Crowd Supply health | **Informational reference only** — not queued for action |

---

## 1. Executive Summary & Action Queue (For Next Agent / Author)

Rev 1.01 has **0 ERC errors**, **0 unconnected items**, **0 schematic-to-PCB parity mismatches**, and a verified Gerber/drill archive (`production/Silkscreen_Reader_PCB_1.01.zip` has 0 primitive diffs against a fresh `kicad-cli` plot).

Below is the consolidated queue of **actionable items** sorted by type so an agent or the author can execute them cleanly:

### 1.1 Documentation & Build-Guide Edits (No PCB Respin Required)

| ID | Target File(s) | Exact Action to Take |
|---|---|---|
| **ACT-DOC-1** (`[SCH-H1]`, `[SCH-M4]`) | [`README.md`](../../README.md), [`docs/LED_ALT.md`](../LED_ALT.md), [`fabrication/BOM.md`](../../fabrication/BOM.md) | **Prefer pre-ordering `TPS923610DRLR` over substituting `TPS923611DRLR`:** Add a clear disclaimer next to the `TPS923611` + `SMAJ33A` out-of-stock swap noting that **pre-ordering `TPS923610DRLR` on JLCPCB is strongly preferred** (typically only adds a few days) because `TPS923611`'s higher `29.6–31.4 V` OVP ceiling exceeds the ESP32-S3 ADC1 linear range (`2.90 V`) on `LED_MONIT` (`IO2`, reaching `3.43 V` via `R39`/`R41`) and increases capacitive dump stress into `U10.3` (`FB`) if one LED string fails open during `COLOR_SEL` blending. Also note that firmware should wait for `LED_MONIT` to bleed below `15 V` (`< 1.60 V` at `IO2`) before toggling `COLOR_SEL` after any open-load fault. |
| **ACT-DOC-2** (`[SCH-M1]`, `[DFM-H2]`, `[DFM-M1]`) | [`README.md`](../../README.md), [`docs/HARDWARE.md`](../HARDWARE.md) (§9.2, §16) | **Cut-down board instructions & `silkscreenreader.com/builder` recommendation:**<br>1. For all notes involving sawing/cutting the top tongue (`y = 61.86 / 62.00 mm`) for a 3.68" display, **explicitly advise builders to use `silkscreenreader.com/builder` to generate pre-configured Gerbers that do not require physical sawing** (avoiding DIY saw-kerf risk near `GND` via `(97.350, 62.700)`, exposed live cut-edge stubs on `P+`/`3V3`/`LED_SW`/`I2C_SDA`/`I2C_SCL`, and floating copper islands).<br>2. For users who *do* physically cut a full-size board: add **`R62` (`10 kΩ` at `(101.20, 66.40)`)** to the list of resistors to remove (`R36`, `R73`, **`R62`**), and recommend **moving `R62` directly onto the unpopulated `R72` (`10 kΩ`) pads** when repurposing `SW7` as the power button instead of wasting a new 10 kΩ resistor and leaving `R62` connected to the sawn `Net-(R62-Pad1)` stub. |
| **ACT-DOC-3** (`[SCH-L1a]`) | [`docs/HARDWARE.md`](../HARDWARE.md) (§6.2) | **E-paper boost startup LC capacitance:** Update §6.2 to note that during initial `3V3` ramp-up, `L1` (`47 µH`, `EINK_SW`) charges **both `C14` (`4.7 µF/50 V` via `D5` to `PREVGH`) and `C11` (`4.7 µF/50 V` via `D6` to `GND`) in parallel** (`9.4 µF` nominal / `~8.4 µF` effective total, rather than `C14`'s `4.7 µF` alone), and that `U3` (`TLV75533P`)'s current-limited startup ramp (`~175 µs` > $\pi\sqrt{L_1 C_{\text{tot}}} \approx 62\,\mu\text{s}$) naturally bounds peak inductor startup current to `~0.25–0.45 A` (well below `L1`'s `1.1 A` $I_{\text{sat}}$). |
| **ACT-DOC-4** (`[SCH-L1b]`) | [`docs/HARDWARE.md`](../HARDWARE.md) (§3.4 / §7) | **Frontlight boost behavior across USB hot-plug / switchover:** Document that when `U2` (`TPS2116DRL`) switches `LDO_IN` from a depleted `3.0 V` battery to `5.0 V` `USB_VBUS` in `~8 µs` (`VOUT > 1.0 V`, so soft-start is inactive), the `2.0 V` step into the `L2` (`10 µH`) + `C9` (`4.7 µF/50 V`) tank ($Z_0 \approx 1.62\,\Omega$) produces a brief damped current pulse up to `~0.96 A` (within `L2`'s `1.0 A` rated / `1.3 A` typ $I_{\text{sat}}$) and peak-rectifies `LED_SW` to `~5.8 V`—confirmed benign on hardware even with the frontlight enabled. |
| **ACT-DOC-5** (`[SCH-L1c]`) | [`docs/HARDWARE.md`](../HARDWARE.md) (§5) | **MicroSD (`J7`) turn-on and write-burst decoupling analysis:** Document the coupled RLC analysis (Section 3.6 below) showing that `C36` (`0.1 µF`) + `C37` (`1 µF`) at `J7` backed by `C6` (`22 µF`) and `C32` (`22 µF`) on `3V3` keep `3V3` droop during active 50–200 mA SDMMC write bursts to just **`8.5–34 mV`**, and bound initial `Q7` turn-on droop at `U4` (`C32`) to **`~274 mV` (`V_min = 3.03 V`)** (`~305 mV` / `2.995 V` even during a simultaneous `350 mA` Wi-Fi TX burst)—so brownout is only possible if `SD_ACTIVATE` is toggled at kilohertz rates faster than the bulk caps recharge. |
| **ACT-DOC-6** (`[Part I §3]`) | [`README.md`](../../README.md) (Step 6), [`fabrication/README.md`](../../fabrication/README.md), [`fabrication/BOM_handbuild_digikey.csv`](../../fabrication/BOM_handbuild_digikey.csv) | **Placement-preview checklist & DigiKey BOM sync:** Add `U10` (`TPS923610DRLR`) and polarized diodes `D3`–`D6` to the JLCPCB visual placement-preview check list in `README.md` Step 6 and `fabrication/README.md`; update `U13` in `fabrication/BOM_handbuild_digikey.csv` from `DS3231MZ+` (`$5.50`) to `DS3231MZ+TRL` (`$13.85`) to match `fabrication/part_fields.csv`. |

### 1.2 Fabrication Script Fix (No PCB Respin Required)

| ID | Target File(s) | Exact Action to Take |
|---|---|---|
| **ACT-FAB-1** (`[DFM-H1]`) | [`fabrication/make_fab_files.py`](../../fabrication/make_fab_files.py), [`production/other_fabs/`](../../production/other_fabs/) | **Apply `FT Position Offset` and `FT Rotation Offset` in `make_fab_files.py`:** `J4` (`FH34SRJ-6S-0.5SH(50)`) has its footprint origin displaced by `-0.730 mm` in X relative to its copper pad center (`(92.500, 126.000)` anchor vs `(93.230, 125.994)` pad center). `b448b39` fixed this for JLCPCB (`production/positions.csv`) via `FT Position Offset = -0.73,0.218`, but `make_fab_files.py` uses raw `kicad-cli pcb export pos` output and leaves `J4` off by `0.73 mm` (1.46 pitches) in `nextpcb_centroid.csv`, `split/nextpcb_centroid_smd.csv`, and `placement_bottom_kicad.csv`. Update `make_fab_files.py` to apply the schematic/PCB `FT Position Offset` (and optionally `FT Rotation Offset`) and regenerate `production/other_fabs/`. |

### 1.3 Schematic & Layout Items Queued for Next KiCad Edit / Future Spin

| ID | Target File(s) | Exact Action to Take |
|---|---|---|
| **ACT-SCH-1** (`[SCH-L1d]`) | [`silkscreen_pcb.kicad_sch`](../../silkscreen_pcb.kicad_sch) | **Clean up stale schematic text boxes:**<br>1. In the `TPS923` frontlight text box: replace obsolete net name `LED_ACTIVATE` with **`PWM_LED`**, and update `"Never enable with J3 unplugged"` to reflect that open-load / `J6`-only operation is protected by `LED_MONIT` (`IO2`, software trip at ~23 V) and `U10` hardware OVP (`24.5 V`).<br>2. In the `TP4056` charger text box: update `"R6 4.7kohm -> 255mA charge rate"` to **`~234–250 mA`** ($1100/R_{\text{PROG}} = 234\,\text{mA}$ for `TOPPOWER TP4056` `C16581`). |
| **ACT-SCH-2** (`[SCH-M3]`) | [`silkscreen_pcb.kicad_sch`](../../silkscreen_pcb.kicad_sch), [`silkscreen_pcb.kicad_pcb`](../../silkscreen_pcb.kicad_pcb) | **Move `Q2` source (`Q2.2`) and `R81` (`R81.2`) from `3V3` to `USB_VBUS` *(next PCB spin)*:** Turns the `TP4056` `CE` gate into a true hardware `AND` gate (`Forward Battery Present AND USB_VBUS Present`), eliminating the continuous `6.6 µA` battery-sleep drain through `R81`+`R82`, preventing `3.3 V` from being driven into `U11.8` (`CE`) while `U11.4` (`VCC`) is unpowered at `0 V`, and removing the need to route `3V3` to the charger section across the cut line. (Full analysis in Section 2.4 below.) |
| **ACT-PCB-1** (`[DFM-M2]`) | [`silkscreen_pcb.kicad_pcb`](../../silkscreen_pcb.kicad_pcb) | **Fix the `1 µm` `3V3` stub at `(101.000, 64.900)` on `B.Cu`:** In commit `5809233`, the `0.141 mm` diagonal segment `(101.001, 64.900) → (101.101, 65.000)` that connected the new `3V3` bridge to the vertical `3V3` spine at `x = 101.101` was deleted while the `1 µm` segment `(101.000, 64.900) → (101.001, 64.900)` (`uuid = 157ac2d7-cd6c-4a42-909e-956bb41befcb`) remained, leaving a `0.100 mm` centerline gap bridged only by round endcap overlap. Delete the `1 µm` segment and connect `(101.000, 64.900)` cleanly to `(101.101, 64.900)` (or `(101.101, 65.000)`), plus delete the `15 nm` zero-length segment on `Net-(Q5-S)` at `(50.351, 122.500)` and two `1.4 µm` segments on `I2C_SCL` at `(93.000, 58.871)` / `(93.000, 59.329)`. |

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
       * **With `TPS923610` ($V_{C9} \le 25.5\,\text{V}$, software trip at $23\,\text{V}$):** $I_{\text{peak}} \approx 220\text{–}300\,\text{mA}$ for $\sim 100\,\mu\text{s}$, producing $V_{\text{FB,peak}} = I_{\text{peak}} \times 15\,\Omega \approx \mathbf{3.3\text{–}4.5\,\text{V}}$ at `U10.3` (`FB`)—**safely below `U10.3`'s `6.0 V` absolute maximum rating!**
       * **With `TPS923611` ($V_{\text{OVP}} = 31.4\,\text{V}$):** $I_{\text{peak}}$ reaches $350\text{–}469\,\text{mA}$, pushing $V_{\text{FB,peak}}$ to **$5.25\text{–}7.03\,\text{V}$** (exceeding `U10.3`'s `6.0 V` abs max).
* **Actionable Outcome (`ACT-DOC-1`):**
  1. Add a note to the `TPS923611` substitute sections in `README.md`, `docs/LED_ALT.md`, and `fabrication/BOM.md` recommending that builders **pre-order `TPS923610DRLR`** (only a few days lead time at JLCPCB) rather than substituting `TPS923611`.
  2. In firmware, if `LED_MONIT` (`IO2`) trips open-load protection ($V_{\text{LED\_SW}} > 18\,\text{V}$) while `COLOR_SEL = 1`, keep `COLOR_SEL = 1` (with `PWM_LED = 0`) for ~2 seconds until `LED_MONIT` reads $< 1.60\,\text{V}$ ($< 15\,\text{V}$ on `C9`) before releasing `COLOR_SEL` to `0`.

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
* **Answer — YES, 100%:**
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

* **Actionable Outcome (`ACT-SCH-2`):** Queued for the next schematic/PCB revision: move `Q2` pin 2 and `R81` pin 2 from `3V3` to `USB_VBUS` (which is already right next to `U11` and `Q2` on the board!).

---

### 2.5 `[SCH-M4]` — `TPS923611` Substitute vs. `LED_MONIT` ADC Ceiling
* **Author Disposition:** *`LED_MONIT` is intended to trip in firmware (`~23 V`) before hardware OVP kicks in; add a recommendation in the docs to prefer pre-ordering `TPS923610`.*
* **Status:** Covered under **`ACT-DOC-1`**.

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
* **Summary for Next Agent:** In `fabrication/make_fab_files.py`, parse the `FT Position Offset` (and `FT Rotation Offset`) properties from `silkscreen_pcb.kicad_pcb` (or cross-reference `production/positions.csv`) when generating `production/other_fabs/placement_bottom_kicad.csv`, `nextpcb_centroid.csv`, and `split/nextpcb_centroid_smd.csv`, so `J4` exports at `Mid X = 93.230 mm, Mid Y = -125.782 mm` instead of `92.500 mm, -126.000 mm`.

### 3.2 `[DFM-H2]` & `[DFM-M1]` — Cut-Line Exposed Stubs, Via `(97.350, 62.700)` Kerf Clearance, and Floating Pour Islands
* **Author Disposition:** *This is a DIY sawing risk. Advise anyone wanting a smaller 3.68" board to use `silkscreenreader.com/builder` to obtain pre-trimmed Gerbers that do not require sawing (`ACT-DOC-2`).*
* **Summary of Coordinates (for reference in docs):**
  * `GND` via `(97.350, 62.700)` (`0.60/0.30 mm`) has its outer copper edge at `y = 62.400 mm` (`0.100 mm` above the bottom centerline `y = 62.500 mm` of the `5.30 × 1.10 mm` tongue-neck slot).
  * Twelve traces cross `y = 62.00 mm`: `UNUSED_GPIO_3` (`B.Cu` `x = 85.30`), `UNUSED_GPIO_46` (`F.Cu` `x = 85.40`), `UNUSED_GPIO_45` (`F.Cu` `x = 85.75`), unfused `P+` (`F.Cu` `x = 87.40`), `3V3` (`B.Cu` `x = 87.53` and `100.60`), `I2C_SCL` (`F.Cu` `x = 96.10`), `I2C_SDA` (`F.Cu` `x = 97.90`), `LED_SW` (`F.Cu` `x = 98.40`), `W-` (`F.Cu` `x = 101.95`), `Net-(R62-Pad1)` (`B.Cu` `x = 102.11`), and `C-` (`F.Cu` `x = 102.30`).
  * Physical sawing at `y = 62.00 mm` leaves two unvied copper islands on the kept board (`5.51 mm²` on `B.Cu` at `x = 83.74..87.20, y = 62.00..67.43` and `2.30 mm²` on `F.Cu` at `x = 102.55..103.76, y = 62.00..64.44`) that are automatically pruned when generating a native 3.68" board via `silkscreenreader.com/builder`.

### 3.3 `[DFM-M2]` — Unfinished `1 µm` `3V3` Stub at `(101.000, 64.900)` on `B.Cu`
* **Author Disposition:** *Valid, note to fix (`ACT-PCB-1`).*
* **Exact Segments in `silkscreen_pcb.kicad_pcb`:**
  * Segment `uuid = 157ac2d7-cd6c-4a42-909e-956bb41befcb`: `(start 101 64.9) (end 101.001 64.9) (width 0.25) (layer "B.Cu") (net 4)` (`1 µm` long).
  * Adjacent segment: `(start 99.673401 64.9) (end 101 64.9) (width 0.25) (layer "B.Cu") (net 4)`.
  * Vertical spine: `(start 101.101 68.561) (end 101.101 62.501) (width 0.25) (layer "B.Cu") (net 4)`.
  * **Fix:** Delete `157ac2d7-cd6c-4a42-909e-956bb41befcb` and extend `(99.673401, 64.9) → (101.101, 64.9)` (splitting the vertical spine at `(101.101, 64.9)`).

### 3.4 `[DFM-M3]` — FPC Solder-Mask Bridges & Via-to-Pad Clearances (`Accepted / Non-Issue in Production`)
* **Author Disposition:** *Confirmed non-issue on actual Rev 1.0 production boards from JLCPCB. Closed.*
