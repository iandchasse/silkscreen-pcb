# Evaluation of the author's response (2026-09-20)

Source: the "Author refute" column of [`FINDINGS_TABLE_author_refute.md`](FINDINGS_TABLE_author_refute.md) — 99 answers
(1 BLOCKER, 16 HIGH, 70 MEDIUM, 10 LOW, 2 DOC). Every item tagged REFUTED / PARTLY DISPUTED, and every item where you
asked for a re-evaluation, a source or an explanation, was re-checked against the design files and datasheets — by me,
directly, not by re-reading the auditors. Where you were right I say so plainly.

**Outcome:** 0 BLOCKER. **HIGH (16):** BOM-01 done; eight documentation items done in the README; DOCS-08, LAY-01 and MEC-02 are on your to-do because you said you will do them; MEC-01, MEC-23 and SD-V01 are closed as design intent; **HMI-01 is the one open decision.** **MEDIUM (70):** FAB-23 withdrawn; 14 downgraded to LOW after re-evaluation (BAT-02, BAT-03, FAB-03, FAB-16, HMI-02, HMI-07, HMI-V03, LAY-05, LED-12, MEC-V01, PWR-01, USB-02, USB-04, USB-V02); the rest are closed by your answer, done in this pass, or on your to-do. Nothing left in the list blocks an order.

Status key — **WITHDRAWN** reviewer was wrong · **CLOSED** your answer settles it · **DONE** fixed in this pass ·
**TODO-you** you said you will do it · **DOWNGRADED** re-evaluated, lower severity · **STANDS** still recommended, explanation given.

## 1. Where you were right and the review was wrong

| ID | Your point | Re-check | Result |
|---|---|---|---|
| **LED-01** (BLOCKER) | Paste is present, drawn as polygons | `HRS_FH34SRJ-*.kicad_mod` contains `fp_poly … (layer F.Paste)` 0.25 × 0.65 mm, one per signal pad. `pcbnew` on the board: 24 / 6 / 6 graphic B.Paste shapes on J2 / J3 / J4, **every one centred on a numbered signal pad**. The auditor, the verifier and my own "confirmation" all read *pad* layer sets and counted *flashes*; region-drawn paste is invisible to both. | **WITHDRAWN.** My error, compounded by re-using the method I was supposed to be checking. You are also right that the proposed "fix" would have been harmful. All dependent text struck in `FINAL_REVIEW.md`. |
| Method note | Re-check anything else that relied on pad-layer paste | Graphic paste exists on **only** J2/J3/J4 (scan of every footprint). SD-03 (J7) and FAB-V01 (U4/U11) use pad-based paste, so their method is valid. FAB-V01 re-measured: **U4 0 of 12** thermal vias under paste, **U11 4 of 6**. The "41 SMD pads carry no paste layer" count is meaningless and is withdrawn. | SD-03 stands (harmless). FAB-V01 corrected to U11 only → LOW. |
| **FAB-23** | Same four slots as LAY-01; 0.716 mm was wrong | Agreed — 0.516 mm centre-line; 0.716 added the 0.2 mm stroke. | **WITHDRAWN**, merged into LAY-01. |
| **LAY-05** | "False positive, all ground pours are stitched" | Re-tested every GND fill island for a GND via **or a grounded through-hole pin** (the first test ignored thermal-relieved pins). F.Cu: 14 islands, **all tied**. B.Cu: 50 islands, 44 tied; the 6 that are not total **11.5 mm²** (largest 6 mm²) and connect through their SMD ground pads — DRC shows 0 unconnected. The "120 mm² tongue island with zero vias" (LAY-V01) is tied through J6's ground pins. | **DOWNGRADED to LOW / cosmetic.** LAY-V01 **WITHDRAWN.** You were essentially right. |
| **USB-02**, **USB-V02** | "States will not collide, and if they do they are not physically possible" | Redone from the netlist (R70 100 k pull-up; R17 150 k/ST, R67 56 k/CHRG, R71 22 k/STDBY). Normal states: 1.98 / 1.19 / 0.60 / 3.30 V — cleanly separated. The "collisions" need **ST low at the same time as a charger output**, which only happens with VBUS sagging into the ~3.7–4.0 V band between the TP4056's UVLO and the mux's 4.0 V threshold (a bad source, as you say for USB-03) — and even then 0.96 V still decodes as *charging* and 0.53 V as *charged*: **the charge state comes out right; only "which source" is lost.** CHRG+STDBY both low (0.45 V) is the TP4056 no-battery blink; with your CE gate a cold plug-in with no cell reads 3.3 V (charger off), so the blink is reachable **only by unplugging the cell while on USB** (the detector self-latches once the charger holds `P+` up — BAT-V01). | **Both DOWNGRADED to LOW, firmware-only.** Nothing sticks out at board level. Firmware: widen the windows slightly and require a stable reading before saying "charged" — written into HARDWARE.md's firmware contract and the schematic note. |
| **BAT-03** | Reversed-pack voltage should not reach the DW01A | In effect, yes. The reverse path is blocked (by Q8; Q3's body diode points toward the cell — BAT-V02 — but the pair still isolates), so the DW01A's VCC-below-GND condition is fed only by µA of leakage. | **DOWNGRADED to LOW / informational.** |
| **HMI-13 / LAY-07 / LAY-D1** | 0.30 mm was designed as exposed-copper to exposed-copper | Both numbers, as requested: **0.300 mm** between the 0.6 × 0.6 mm F.Mask window on the tab and the ring's mask opening (mask expansion is 0) — *your recollection is right*; **0.151–0.188 mm** copper-to-copper under the mask (SW2 0.151/0.151, SW3 0.188/0.151, SW8 0.188/0.151, SW9 0.151/0.163). | **CORRECTED.** HARDWARE.md §9.1.1 now states both. |
| **FAB-04 / LAY-16 / USB-10** | Counts disagree (12 / 15 / 16); you get 13 | My `drc.json` was run with `--all-track-errors`: **12 live at J1 + 3 excluded at J3 = 15**. With default flags I get **11 live at J1** (+ the 3 excluded J3 = 14). Your 10 + 3 = 13 is the same population; ±1 depends on DRC flags and how excluded items are counted. 16 was a miscount. All are inside J1's own land pattern or are the already-excluded J3 netclass artefact. | **One item, LOW, accepted** (same reasoning as your FAB-01). |
| **HMI-23** | NextPCB's J6 substitute is a female header | Your export text (排母 … 弯插) is unambiguous. | **WITHDRAWN.** |
| **PWR-14** (found while pruning) | — | Two sections contradicted each other about C12; it sits on the `LDO_IN` net at U10's VIN, so both labels are defensible and the README's "keep C12" is correct. | **WITHDRAWN.** |

## 2. Things you asked me to explain, source or re-evaluate

| ID | You asked | Answer |
|---|---|---|
| **PWR-01** | "I need a source for this. We've been designing for 500 mA." | TI TLV755P datasheet **SBVS320, §5.4 Thermal Information**: DBV (SOT-23-5) RθJA = **231.1 °C/W** on the JEDEC board, **100.8 °C/W on TI's own EVM** (same package, more copper). On USB the LDO drops ≈ 4.85 − 3.3 = 1.55 V, so P = 1.55 × I. With TJ(max) 125 °C and 40 °C ambient: 85 °C ÷ 231 °C/W = 0.37 W → **≈ 240 mA continuous**; at 100 °C/W it would be ≈ 550 mA. **Your 500 mA design target is fine for what the board actually does:** this is a *continuous average* limit; Wi-Fi TX bursts are milliseconds against a thermal time constant of seconds, and the ESP32's average with Wi-Fi up is ~100–150 mA. It only bites with a *sustained* > ~250 mA average while on USB. On battery the drop is 0.2–0.9 V and it is a non-issue. **DOWNGRADED to LOW.** Free improvement if you are in the layout anyway: give U3's IN/OUT/GND pins pours instead of 0.25 mm tracks and a single spoke — copper is the whole difference between TI's two numbers. |
| **LED-14** | "Confirm with datasheet." | Confirmed from the PDF itself (TI TPS923610/1/2, SNVSCN8, Electrical Characteristics p.5): **tADIM_EN — "ADIM first pulse high time to enable device" = 40 µs; tADIM_SD — "ADIM logic low time to shutdown" = 2.5 ms; tADIM_PWM min on-time 20 ns.** §7.3.1: "can be enabled by driving the ADIM pin higher than VADIM_H for a period longer than tADIM_EN." At 25 kHz/50 % the high time is 20 µs, so a bare PWM in the schematic note's 10–25 kHz range may never start the chip. **STANDS as a firmware instruction** (drive HIGH ≥ 100 µs, then start PWM) — now in the firmware contract. No board change. |
| **USB-04** | "If it's a simple switch that makes sense then sure. Re-evaluate." | It is **not** a simple switch, so keep the SMF6.5CA. Anything that stays off at the 5.5 V a legal USB source may deliver has a breakdown ≥ ~6.4 V and clamps at 9–11 V under surge; an SMF5.0A clamps at ~9.2 V instead of ~11.2 V — still far above the 6 V abs-max — and leaks more at 5.25 V. The earlier review's tolerance argument for 6.5 V was sound. Datasheet table in `responses/PARTS_RESEARCH.md`. **DOWNGRADED to LOW / accepted.** |
| **USB-V01** | "Explain this issue." | It is the *reason* USB-04 has no fix. USB allows VBUS up to 5.5 V; the TPS2116 and LDO are rated 6 V abs-max. There is only 0.5 V between "must not conduct" and "must already be clamping", and no TVS is that sharp. So the TVS here protects against nanosecond ESD and cable-inductance spikes (which silicon survives), **not** against a charger that sits at 7 V or 9 V. That is true of almost every 5 V USB gadget without an OVP switch IC. Nothing to do for a prototype. **Informational.** |
| **HMI-01** | "What does this do for the use-case of the header? Would this enable hot plugging?" | No — a PPTC does nothing for hot-plug (it is a slow thermal device; hot-plug inrush needs a load switch). What it does: it is the only thing that turns *"accessory or stray wire shorts BAT+ to GND"* from a hot wire into a click-off. Your DW01A trips at 2–4.6 A (BAT-06), so a 1–1.5 A fault never trips it and just cooks. A 0.5 A-hold PPTC opens in seconds at ~1 A. Cost ≈ $0.05–0.10, one 0805/1206 in series with pin 12, ~0.2–0.5 Ω (≈ 50–100 mV drop at 200 mA). **Worth it if anyone but you will plug things into J6; skip it if J6 is your own dev port.** Candidate part in `responses/PARTS_RESEARCH.md`. **STANDS — your decision.** |
| **HMI-02** | "If you think they'll help avoid strapping conditions while not affecting I2S … explain." | **Bigger resistors will not help, so change nothing.** The risk is only at reset: GPIO45 selects the flash voltage (must read LOW for this module) and GPIO46 takes part in boot-mode selection (must read LOW). An accessory that pulls either HIGH at power-up — e.g. a 10 k pull-up — beats the chip's weak ~45 k pull-down no matter whether your series part is 33 Ω or 1 kΩ, and the board will not boot until it is unplugged. Nothing is damaged. 33 Ω is right for I2S edges. The fix is one sentence of documentation: *"Accessories must not pull or drive GPIO45 or GPIO46 HIGH during power-up/reset; use GPIO3 for anything that idles high."* **DOWNGRADED to LOW / doc line.** |
| **FAB-16** | "Do not know what fiducials are. Explain." | Small bare-copper dots (1 mm copper, ~2–3 mm mask opening, nothing else near) that the pick-and-place camera uses to find the board's exact position and rotation before placing parts. JLC's *Standard* PCBA page lists them as required, but in practice JLC adds its own on the edge rails it attaches, or aligns on pads/holes — which is why your two earlier orders went through. **DOWNGRADED to LOW.** Optional next revision: three 1 mm dots in empty corners cost nothing and slightly improve placement of the 0.5 mm-pitch parts. |
| **FAB-03** | "Explain benefit, if any." | A solder-mask *dam* is the sliver of mask between neighbouring pads; it stops molten solder wicking pad-to-pad. On these connectors the vendor footprint opens the mask as one window per row ("gang relief") — normal practice at 0.5 mm pitch, because a 0.2 mm dam is at the edge of what fabs can hold and they would delete it anyway. Your paste is already reduced to ~47 % of the pad, which is what actually controls bridging. Built fine once. **DOWNGRADED to LOW / no action.** |
| **HMI-V03** | "Don't know the benefit. Weigh." | Benefit of grounding the MJTP1117 covers: an ESD strike to the metal cover goes to ground instead of jumping 0.15 mm to the nearest track (I²C runs past two of them). With plastic button caps in a plastic case nobody touches the cover, so the benefit is small. **Cost is not zero here:** your optional front-button solder-bridge feature *uses those rings as un-netted landing pads* on SW2/SW3/SW8/SW9, so grounding them would break it. **Leave as is. DOWNGRADED to LOW.** |
| **MEC-V01** | "It seems fine? What's wrong?" | Nothing is wrong with the copper or the part. The footprint's *origin* is 0.73 mm away from the centre of its pads, so the pick-and-place coordinate (which is the origin) is 0.73 mm off from where JLC's model of the part expects it. You will see J4 sitting slightly off its pads in JLC's placement preview; their engineers nudge it, as your own notes say they have before. **DOWNGRADED to LOW.** Goes on the same to-do as FAB-21 (check J4, U2, U10, D8, U12 in the preview). |
| **DOCS-09** | "The rails … unsure what that has to do with anything?" | Nothing you need to design. JLC's Standard assembly line needs a board ≥ 70 mm wide to ride its conveyor; yours is 60 mm, so they clip temporary break-off strips ("rails") onto the long edges, charge a few dollars, and you snap them off. The only reason to mention it is so a first-time buyer is not surprised by the line item or the strips. Your reading is right: say Standard is needed because of the ESP32 module, and that hand-soldering the module would allow the cheaper Economic service. README updated that way. **DOWNGRADED to MEDIUM-doc → DONE.** |
| **SD-01** | "If there's a simple solution, let me know." | Firmware only, zero parts: before driving `SD_ACTIVATE` off, de-initialise SDMMC and set CLK/CMD/DAT0-3 to output-LOW (or input with pulls off). Otherwise the five 10 k pull-ups hold the "off" card at ~3.2 V and the gate saves nothing. In the firmware contract. **CLOSED.** |
| **BAT-02** | "100 Ω between Q8 and pin 5 produced voltage drop to P+ … Unsure what this gains." | If it dropped `P+`, the resistor was in the **load path**. In the reference circuit it sits only in the branch feeding DW01A pin 5 (with C7 on the pin side) and carries ~3–6 µA, i.e. 0.6 mV. It buys an RC filter so load/charger transients do not false-trip the protector, and it limits current into the pin in a fault. Your earlier board works without it, so: **DOWNGRADED to LOW / optional** — if you ever add it, put it in the pin-5 branch only. |
| **BOM-07** | "Look into alternatives, I'm open to them." | See `responses/PARTS_RESEARCH.md` §1 (no external crystal, stocked at both DigiKey and JLC). |
| **BOM-V01**, **BOM-06**, **BOM-02** | Open to alternatives / will look | See `responses/PARTS_RESEARCH.md` §2–§4. |
| **DOCS-24** | "Fix if it needs to be." | Checked and fixed in README — see `responses/README_CHANGES.md`. |

## 3. Every answer, one line each

| ID | Sev was | Your answer (short) | Evaluation | Now |
|---|---|---|---|---|
| LED-01 | BLOCKER | Refuted — paste is polygons | You are right (§1) | **WITHDRAWN** |
| BOM-01 | HIGH | Valid | R14 LCSC → `C22939` (Basic, 11.7 k stock, verified live) in `part_fields.csv`, schematic field (via your `apply_part_fields.py`), v4 upload BOM, `bom.csv`, `BOM.md`. Yageo stays the DigiKey-primary MPN. | **DONE** (PCB fields: *Update PCB from Schematic* — on your to-do) |
| DOCS-01 | HIGH | Firmware is future work (FreeInk SDK port; crosspoint-reader, crossink reader, XTEink X4 firmwares) | README now says exactly that | **DONE** |
| DOCS-02 | HIGH | Configurator exists behind site preview | README: "coming — if not live, use the manual steps"; manual path is first-class | **DONE** |
| DOCS-03 | HIGH | One file, the v4 | README names only v4; deleting v3 / fixing `bom.csv` is on your to-do | **DONE** (docs) |
| DOCS-04 | HIGH | Good point; battery lead order, microSD, USB-C cable; screws/case belong to case designs | "What else you need" added; placeholder for your known-good pack link | **DONE** (link: TODO-you) |
| DOCS-05 | HIGH | +/- and CHECK are on the board; unaware of a standard warning | There is no standard; one 3-line callout at the battery item is proportionate. Added, no lecture. | **DONE** |
| DOCS-06 | HIGH | Valid | README restructured | **DONE** |
| DOCS-07 | HIGH | Reword; STEP should be available | Reworded; `docs/mechanical/silkscreen_pcb.step` exported (7.7 MB, all 3D models resolved) | **DONE** |
| DOCS-08 | HIGH | Will change the GitHub link | Only you can (default branch / URL on silkscreen, NOTICE, title blocks) | **TODO-you** |
| DOCS-09 | HIGH | Don't understand the rails point | Explained (§2); README reworded your way | **DONE** |
| HMI-01 | HIGH | Add if cheap; what does it do? | Explained (§2) | **STANDS — your call** |
| LAY-01 | HIGH | Will replace the four slots with one wide slot | Good. Make it ≥ 1.0 mm and draw it at 0.05 mm line width like the rest of the outline | **TODO-you** |
| MEC-01 | HIGH | Fine, fabricates fine | Fabrication was never the issue (1.3 mm > JLC's 1.0 mm); the point was the flex fold. You have handled the real panel through it. | **CLOSED — accepted** |
| MEC-02 | HIGH | Will add disclaimer, no keep-out | Sufficient | **TODO-you** (README already warns) |
| MEC-23 | HIGH | Doesn't have to be flat; screen is buffered | Design intent; case designers get it from the STEP file | **CLOSED — by design** |
| SD-V01 | HIGH | Battery must move before ejecting the card; fine | Needs one sentence in the docs (SD-V03) | **CLOSED — by design** |
| BAT-02 | MED | 100 Ω caused a drop before | Explained (§2) | **DOWNGRADED → LOW, optional** |
| BAT-03 | MED | Q3/Q8 block the reverse path | Right in effect (§1) | **DOWNGRADED → LOW** |
| BAT-V04 | MED | Known-good pack will be listed; no standard exists | Agreed; README states the lead order | **CLOSED** |
| BOM-02 | MED | Will substitute if needed | Candidates in PARTS_RESEARCH | **CLOSED** |
| BOM-03 | MED | Always double-check stock | — | **CLOSED** |
| BOM-05 | MED | `bom.csv` won't be used; will revise | — | **TODO-you** (low priority) |
| BOM-06 | MED | Will look into alternatives | Candidates in PARTS_RESEARCH | **OPEN — research delivered** |
| BOM-07 | MED | Open to alternatives; no external crystal, must be stocked | PARTS_RESEARCH §1 | **OPEN — research delivered** |
| BOM-09 | MED | Sold on DigiKey, good enough | Fair | **CLOSED** |
| BOM-V01 | MED | All user-exposed; open to cheap alternatives | PARTS_RESEARCH §2 | **OPEN — research delivered** |
| DOCS-10 | MED | Valid | Cost/lead-time paragraph added | **DONE** |
| DOCS-11 | MED | Define all, remove "Fix 4" | Done | **DONE** |
| DOCS-12 | MED | After firmware | Stub added pointing to future firmware | **CLOSED — deferred by you** |
| DOCS-13 | MED | `other_fabs` will be deleted | README is now JLCPCB-only. Folder, `make_fab_files.py` outputs, `fabrication/README.md`, `NEXTPCB_REV0_NOTES.md`, `nextpcb_substitutes.csv` are yours to delete | **TODO-you** |
| DOCS-14 | MED | Valid | THT presented as a costed choice | **DONE** |
| DOCS-15 | MED | Valid | Plain-language licence summary from LICENSE/NOTICE | **DONE** |
| DOCS-16 | MED | Valid | 5 bare boards, assembly from 2 | **DONE** |
| DOCS-17 | MED | Sure; KiCad, no plans to port | "KiCad not required to order" up top; commands moved to engineers' section | **DONE** |
| DOCS-18 | MED | Slots will be replaced by one | README notes it; update once the board changes | **TODO-you** (after LAY-01) |
| DOCS-24 | MED | Fix if needed | Fixed | **DONE** |
| FAB-01 | MED | Accepted risk — GCT's land pattern | Agreed | **CLOSED — accepted** |
| FAB-02 | MED | Haven't been told no; ignore | Fabs print what they can and silently drop the rest; nothing fails. Note the battery polarity mark is among the small text. | **CLOSED — accepted** |
| FAB-03 | MED | Explain benefit | Explained (§2) | **DOWNGRADED → LOW** |
| FAB-06 | MED | Thermal relief unnecessary; ignore | For machine reflow, fine. (Hand-soldering J1/J5/J6 ground pins is easier *with* spokes, which you have.) | **CLOSED** |
| FAB-10 | MED | v3 irrelevant; one BOM | — | **TODO-you** (delete v3) |
| FAB-14 | MED | By design, documented | Agreed | **CLOSED — by design** (moot once other_fabs goes) |
| FAB-16 | MED | Explain fiducials | Explained (§2) | **DOWNGRADED → LOW** |
| FAB-21 | MED | Valid. Fine fix. | I cannot derive JLC's per-part offsets offline. Check U2, U10, D8, U12, J4 and the diodes/LED in JLC's placement preview; if any is off, add `FT Rotation Offset` / `FT Position Offset` fields so it sticks. | **TODO-you** (at order time) |
| FAB-22 | MED | Valid. Fix. | Root cause is two *Value* spellings sharing one LCSC code (so the Toolkit groups them separately). Normalise the Values of C18/C19 vs C20, and C24/C31 vs C30/C33/C36/C7 | **TODO-you** (or tell me to do it via the schematic) |
| FAB-23 | MED | Refuted as separate finding | Right | **WITHDRAWN** |
| HMI-02 | MED | Explain | Explained (§2) — no hardware change | **DOWNGRADED → LOW, doc line** |
| HMI-03 | MED | Intentional | — | **CLOSED — by design** |
| HMI-04 | MED | Not an alarm clock | — | **CLOSED — by design** |
| HMI-07 | MED | DNP, cannot occur in standard build | Agreed (checked: R74 has no placement row) | **DOWNGRADED → LOW** |
| HMI-10 | MED | Bottom buttons actuated differently | Design intent | **CLOSED — by design** |
| HMI-V01 | MED | Next-revision hardening | Agreed; includes SW6 (REC-C-02) | **TODO-you** (next rev) |
| HMI-V02 | MED | Line is drawn; battery ejection will be documented | — | **TODO-you** (docs) |
| HMI-V03 | MED | Weigh | Weighed (§2) — leave as is | **DOWNGRADED → LOW** |
| LAY-02 | MED | Dremel, not hand-snapped | README says so now, with "disconnect the battery first" | **DONE** |
| LAY-04 | MED | Ignore for now | Same as FAB-02 | **CLOSED — accepted** |
| LAY-05 | MED | False positive | Essentially right (§1) | **DOWNGRADED → LOW** |
| LED-02 | MED | Valid | One doc line: strings with Vf below the battery voltage are not regulated (they conduct through L2 and the body diode) | **TODO — doc line** |
| LED-12 | MED | Earlier audit has a measured sample | Agreed: schematic matches one verified physical sample; no document confirms it; diode-test at bring-up | **DOWNGRADED → LOW** |
| LED-14 | MED | Confirm with datasheet | Confirmed (§2) | **STANDS as firmware note — DONE in docs** |
| LED-V02 | MED | Shouldn't trip if firmware monitors; document | Agreed; documented | **DONE** |
| MCU-01 | MED | DNP for cost; tweezers | Documented in README | **DONE** |
| MCU-13 | MED | Ignore; firmware won't relate to this prototype | — | **CLOSED** |
| MCU-14 | MED | Accepted RF risk | — | **CLOSED — accepted** |
| MEC-03 | MED | Same as others | — | **CLOSED** (with LAY-01/LAY-02) |
| MEC-04 | MED | Enclosure's problem | — | **CLOSED — accepted** |
| MEC-05 | MED | More tolerance is better; real panel passes | You have tested it; fine | **CLOSED** |
| MEC-06 | MED | Fine | — | **CLOSED — accepted** |
| MEC-07 | MED | Fine; allows smaller displays | — | **CLOSED — by design** |
| MEC-09 | MED | Pin-hole; document | Documented in README | **DONE** |
| MEC-V01 | MED | What's wrong? | Explained (§2) | **DOWNGRADED → LOW** |
| MEC-V02 | MED | UP(2) can be the power button; document | Documented in README | **DONE** |
| PWR-01 | MED | Need a source | Given (§2); your 500 mA target is fine | **DOWNGRADED → LOW** |
| PWR-07 | MED | Both use sleep modes | Fair; measure once at bring-up | **CLOSED** |
| SD-01 | MED | Simple solution? | Firmware only (§2) | **CLOSED — firmware contract** |
| SD-02 | MED | Ignore | — | **CLOSED** |
| SD-04 | MED | By design, dual-source | Agreed; your convention is documented | **CLOSED — by design** |
| SD-05 | MED | Fine | — | **CLOSED — accepted** |
| USB-01 | MED | Go with recommendation | Schematic note changed to "> 2.60 V" with the reason; firmware contract says the same | **DONE** |
| USB-02 | MED | Re-do the logic | Done (§1) — nothing sticks out | **DOWNGRADED → LOW, firmware** |
| USB-03 | MED | Only a bad source chatters | Agreed; consistent with §1 | **CLOSED** |
| USB-04 | MED | Re-evaluate | Done (§2) — keep the part | **DOWNGRADED → LOW** |
| USB-05 | MED | 1 A never happens here | Agreed; the 0.86 A figure stacked every load at once | **CLOSED** |
| USB-06 | MED | Worth a look | Widen `USB_VBUS` / fused VBUS to 0.40 mm like the battery path; while there, the two 0.25 mm links either side of R27 (BAT-07/PWR-V01) and U3's copper (PWR-01) | **TODO-you** (layout) |
| USB-V01 | MED | Explain | Explained (§2) | **Informational** |
| USB-V02 | MED | Re-evaluate | Done (§1) | **DOWNGRADED → LOW, firmware** |
| FAB-04, LAY-16, USB-10 | LOW | Count is 13 | Reconciled (§1) | **One item, accepted** |
| FAB-15, FAB-17, FAB-18, HMI-17 | LOW | By design | Agreed (FAB-17 checked against `positions.csv`) | **CLOSED** |
| HMI-13, LAY-07, LAY-D1 | LOW/DOC | Measurement definition | Both numbers given (§1) | **CORRECTED / DONE** |
| HMI-23 | LOW | Refuted | Right | **WITHDRAWN** |
| USB-18 | DOC | *(your cell reads "confirmed-with-corrections" — looks like a column slip)* | Covered by the USB_STAT re-evaluation | — |
