# Repository documentation: can an amateur or non-technical person replicate this?

*Final review 2026-09-19 · reviewer key `docs` · finding prefix `DOCS-`*

## What this part of the board does

Nothing on the board — this section reviews the **words**, not the copper.

The owner's question was narrow and practical: *"Repo end-user readability in .md documents, especially
the readme, when it comes to simple as possible replication for electronics amateurs or otherwise
non-technical people who are not comfortable with ordering their own PCBA."*

So the test applied here is not "is the documentation accurate?" (mostly, it is — see
[Checked and found OK](#checked-and-found-ok)). The test is: **if a stranger clones this repository,
can they end up holding a working reader?** That path has eight steps, and a document set is only as
good as its weakest one:

1. Find the project at all.
2. Understand what the thing is and decide they want one.
3. Work out which files to upload, where.
4. Work out which options to click in the fab's web form.
5. Buy everything that is *not* on the PCB — panel, battery, cable, card, screws, case.
6. Receive the parcel and know what, if anything, they still have to solder.
7. Power it up and put software on it.
8. When it doesn't work, find help.

Two imaginary readers walk that path below:

* **Persona A — "Arduino Andy."** Comfortable with a soldering iron, has flashed an ESP32, owns a
  multimeter. Has **never ordered a PCB**, has never heard of a centroid file, does not own KiCad.
* **Persona B — "Interested Bea."** Wants the device, not the hobby. Can follow a recipe and click
  through a web shop. Is **nervous about ordering PCBA** and will abandon at the first screen she
  cannot interpret.

**Jargon defined once, for the rest of this section.** *Gerber* = the image files that tell a factory
where the copper goes. *BOM* (bill of materials) = the shopping list of parts. *CPL* / *centroid* /
*pick-and-place* = the file that tells the robot where each part sits and which way round it faces.
*PCBA* = "printed circuit board **assembly**", i.e. the factory also solders the parts on, rather
than shipping you a bare board. *DNP* = "do not populate" — a part drawn on the board that is
deliberately left off. *THT* / *through-hole* = a part with legs that go through holes, as opposed to
*SMD*, which sits flat on the surface. *LCSC* = the parts distributor JLCPCB buys from; an "LCSC
code" like `C2913202` is how you name a part to JLCPCB. *Basic / Extended* = JLCPCB's two part tiers;
Extended parts carry a one-off loading fee per part type.

---

## Document walk-through

Every `.md` file a replicator could reach, what it is for, and whether its claims were checked
against the evidence pack rather than taken on trust.

| File | Size | What it is | Role for a replicator | Checked against ground truth? |
|---|---:|---|---|---|
| `README.md` | 298 lines / ~3 175 words | Front door | **The** document that has to carry Persona B | Yes — counts, board size, sides, DNP list, file names, all links |
| `docs/HARDWARE.md` | 1 286 lines / ~12 277 words | Post-hoc block-by-block hardware explanation, with a table of contents | Deep dive for Persona A; irrelevant to B | Spot-checked (part counts, enclosure notes, power-button jumper) |
| `fabrication/README.md` | 108 lines | Release-file workflow: what to regenerate, what to keep | Only useful to the owner or a forker | Yes — release-record table vs actual repo contents |
| `fabrication/BOM.md` | 305 lines | Three bills of materials, cost model, swap rationale, hand-build list, off-board items | Contains the only cost numbers and the only "what else to buy" table in the repo | Yes — cost figures, DNP table, off-board table |
| `fabrication/NEXTPCB_REV0_NOTES.md` | 92 lines | Record of a NextPCB Rev0 quote attempt | Alternative-fab path; also hides one JLCPCB-critical fact (see DOCS-03) | Read in full |
| `fabrication/THIRD_PARTY.md` | ~60 lines | Vendored library files and their licences | Answers "may I fork / sell this?" better than the README does | Read in full |
| `LICENSE` | 13 419 bytes | CERN-OHL-S v2 full text | Legally complete, humanly unreadable | Present, correct SPDX id |
| `NOTICE` | 31 lines | Copyright, licence summary, source URL | Clear. **But its source URL lands on the wrong project** — DOCS-08 | Yes — URL fetched |
| `docs/images/*.png` | 23 files | Schematic block crops + two board renders | All referenced images exist | Yes — automated link check |
| `production/`, `production/other_fabs/` | 15 tracked files | The actual upload artefacts | The heart of the replication path | Yes — row counts, designator sets, duplicate codes |

Deliberately **not** read for this review (earlier audits, excluded by the review protocol):
`DESIGN_REVIEW.md`, `docs/audit-2026-09-16/`, `docs/audit-2026-09-18/`. Their *existence and their
prominence in the README* is in scope and is discussed under DOCS-06; their contents are not.

---

## Where the documentation lives & layout notes

### Shape of the README

```
lines   1– 28   What it is, "read DESIGN_REVIEW.md before assembly", images, plot links
lines  31– 47   "At a glance" spec table (12 rows of engineering)
lines  51– 70   Repository layout tree
lines  72–105   "Building the board": kicad-cli command lines
lines 107–178   >>> Ordering from JLCPCB, step by step  <<<   (the part Bea needs)
lines 180–207   Which parts are optional? (configurations)
lines 209–262   Ordering from PCBWay or NextPCB
lines 264–298   BOM pointer, documentation pointers, licence
```

The ordering path — the only section either persona actually needs — **starts 36 % of the way down
the page**, after two command-line code blocks. Everything before it is written for someone who
already owns KiCad. There is no table of contents, so on GitHub the reader must scroll past it.

### What the board itself says

The physical board carries a surprisingly good onboarding paragraph on the **front silkscreen**
(read out of `silkscreen_pcb.kicad_pcb` with `pcbnew`, text box at 51.2, 78.4 mm, 0.9 mm tall):

> "Welcome to Silkscreen, the open-source ESP32 reading/devkit platform. All components will be on
> the back of this board, maximizing cost and simplicity for DIY. Please build and repair as you
> please! … Please flash firmware via the USB-C port, insert a micro-SD card, attach a 3.7 V LiPo
> battery, assemble with a screen and case, and enjoy de-linking with Silkscreen! Help can be found
> at the same places you can support/participate the project within our community at the QR codes on
> this board below!"

This is warmer, plainer and better sequenced than the README's opening — and it is printed on a
board the reader can only have *after* completing the hard part. The silkscreen also directs the
reader to `silkscreenreader.com` ("Please refer to docs at silkscreenreader.com for more specific
info"), which is empty (DOCS-02), and to QR codes for "Website:", "GitHub:" and "Ko-Fi:", whose
GitHub target has the problem described in DOCS-08.

There is also a B-side silkscreen instruction the repository never mentions:

> "this long end of the board can be cut for smaller displays / if so, unpopulate R36 and R73 / and
> then, populate R72/R74 / this will swap power button to UP2 / depopulate SW5 (DOWN2) if you please"

(B.Silkscreen, 103.6, 65.3 mm.) See DOCS-20.

### Supporting image

`img/battery_j5_silk.png` (produced by the battery reviewer) shows the `J5` land and its `- +` /
`CHECK` silkscreen, which is the only polarity guidance a builder gets. Referenced here as the
evidence for DOCS-05.

---

## Calculations

**1. How much of the README a newcomer must read before the first actionable instruction.**
First imperative a non-KiCad reader can execute = line 133 ("Sign in at jlcpcb.com…").
132 / 298 = **44 % of the file is preamble** for Persona B. The first *thing they are told to do*
(line 12, "read DESIGN_REVIEW.md") points at a 100 414-byte document.

**2. Undefined jargon density in the README.** Term occurrences, and whether the README ever defines
the term in plain words:

| Term | Occurrences in README | Defined? |
|---|--:|---|
| DNP | 12 | No |
| Toolkit / Fabrication Toolkit | 13 | Named at line 98, never explained as "a KiCad plugin you must install" |
| CPL | 9 | Half — "Pick-and-place (CPL)" at line 120, but first used at line 102 |
| through-hole / THT | 9 / 1 | No |
| LCSC | 6 | No |
| Extended (part tier) | 4 | No |
| Basic | 1 | No |
| Gerber | 6 | No |
| "Fix 4" | 1 (line 13) | No — defined only inside the excluded DESIGN_REVIEW.md |
| Warning / ⚠ safety callout | **0** | — |

**3. Cost of five assembled boards** (the smallest order a reader can place), assembled from the
owner's own figures in `fabrication/BOM.md`:

```
parts + JLC fees, v4 optimized, 5 boards   $33.23/board × 5  = $166.15
PCB + SMT + THT + setup at 5 boards        ~$15–20/board × 5 = $ 75–100
                                                             -----------
subtotal                                                      $241–266
shipping (typical DHL to US, 5 small boards)                  $ 20– 40
                                                             -----------
all-in, five assembled boards                               ≈ $260–305
```

Cross-check against the owner's real order: 30 boards quoted **$624.08** total against **$338.12**
of parts ⇒ $285.96 of PCB+assembly+setup = $9.53/board at qty 30, consistent with the $15–20/board
used above at qty 5 where fixed setup dominates. **None of these numbers appear in the README.**

**4. Hand-soldering exposure if THT assembly is declined.** 13 through-hole parts
(`J1`, `J5`, `J6`, `SW1`–`SW5`, `SW7`–`SW11`) with 20 + 2 + 12 + (10 × 4) = **74 joints per board**
— verified from `evidence/pcb/board_extract.json` pad types. At 5 boards that is 370 hand joints.
The README mentions the 13 parts but never states the joint count or offers the choice explicitly.

**5. Board size against JLCPCB's Standard PCBA envelope.** Board outline
**60.05 × 111.30 mm** (`evidence/pcb/board_summary.md`). JLCPCB's current capability page gives
Standard PCBA single-PCB size **"70x70mm - 460x500mm"**. 60.05 mm < 70 mm ⇒ the board is
**under the stated minimum in its narrow dimension**, and the same table marks Edge Rails and
Fiducials "Necessary" for Standard (vs "Not necessary" for Economic). The board carries **no
fiducial footprints and no edge rails**. See DOCS-09.

---

## Findings

| ID | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| DOCS-01 | HIGH | **There is no firmware, and no document says so.** A reader who completes the entire ordering path has a board with nothing to run. | `grep -i "firmware\|esptool\|platformio\|arduino"` across `README.md`, `docs/HARDWARE.md`, `fabrication/*.md`: the README's only hit is the phrase "custom enclosures and firmware" (line 4). No repository link, no flashing command, no "firmware is not written yet". `HARDWARE.md:983` mentions `esptool` only as an electrical aside. | Add a **Software** section to the README stating plainly what exists today, where it lives (or "not yet released"), and the literal first-power-up command. If nothing exists, say "this is a bare board; you will need to write or port firmware" in the first 20 lines. |
| DOCS-02 | HIGH | **The README's recommended route is a configurator that does not exist.** Two sections push the reader to silkscreenreader.com's "*Build one*" tool, one of them calling it "the easiest, least error-prone route". | `README.md:109–113` and `README.md:186`. `https://silkscreenreader.com` fetched 2026-09-20: renders only the title "Silkscreen \| Open hardware reader project" — no navigation, no configurator, no tutorials, no shop. Same result on a second fetch during the prior session. The board's own front silkscreen also points there. | Demote to a one-line "a configurator is planned at silkscreenreader.com" note, and make the manual path in §1–§7 the primary, unqualified instruction. Do not describe an unavailable tool as the recommended route. |
| DOCS-03 | HIGH | **The README offers three BOM files as interchangeable, and two of them are known to break the upload.** `bom.csv` and `bom_JLC_upload_v3.csv` each list an LCSC code on two separate lines; JLCPCB left `C20`, `C24`, `C31` unmatched because of exactly this. Only `v4_optimized` is clean. | Parsed from the repo: `bom.csv` duplicates `C28323` (lines `C18,C19` and `C20`) and `C14663` (lines `C24,C31` and `C30,C33,C36,C7`); `v3` duplicates the same two; `v4_optimized` duplicates none. The failure is recorded in `fabrication/NEXTPCB_REV0_NOTES.md:35` — **not** in the README. README `:146` says "(`bom.csv` or a `bom_JLC_upload_v*` file)"; `:128–129` says "Pick one BOM, not all three" without saying which. JLCPCB's own help page confirms "When the same component is matched across multiple BOM rows, a warning will appear". | Name **one** file: "Upload `production/bom_JLC_upload_v4_optimized.csv`." Move the other two to a "for reference" note. State the duplicate-code failure mode in the README where the reader will meet it. |
| DOCS-04 | HIGH | **No shopping list for the things that are not on the PCB.** The reader is never told which panel to buy, where, which FPC cables, which battery, which connector and polarity, what size screws, what USB cable, or what microSD. | The only "Off-board items" table in the repo is `fabrication/BOM.md:300–304` — **two rows** (panel, battery), at the bottom of a 305-line fabrication document, with no vendor, no price and no link. README line 10 says only "Check the selected panel's pinout and drive requirements, battery specification and enclosure fit." | Add a "What else you must buy" table to the README: panel variant ↔ which optional blocks to fit ↔ vendor link ↔ approximate price; battery (cell chemistry, capacity, **JST-PH 2.0 connector, pin 1 = B−**); microSD; USB-C cable; M2 screws and standoffs (five `MountingHole_Pad` at 2.2 mm); case. |
| DOCS-05 | HIGH | **No safety warning anywhere, on a board that charges a LiPo cell.** The README contains zero warning callouts. Reverse-connecting a single-cell LiPo is the single most damaging mistake an amateur can make here, and the guidance is one clause in a spec table. | `grep -c "[Ww]arning"` on `README.md` = **0**; no `⚠`, no "Caution", no "Danger". `J5` is `JST_PH_S2B-PH-K` with **pin 1 = `B−`, pin 2 = `B+`** (`evidence/sch/connectivity_by_component.txt:364–368`; pads at 94.85, 67.5 / 94.85, 65.5). The board silk says only `- +` and `CHECK` (`img/battery_j5_silk.png`). Cell vendors wire JST-PH pigtails in **both** polarities. README's only mention: "verify cable polarity" inside the At-a-glance table (line 40). | Add a boxed safety block near the top of the README: LiPo polarity is **not** standardised; `J5` pin 1 (the pin nearest the board edge, marked `−`) is battery negative; **meter the cell's pigtail before plugging it in**; use a cell with its own protection circuit; do not charge unattended; do not use a puffed cell. Repeat it in the first-power-up section. |
| DOCS-06 | HIGH | **The README's first instruction sends a newcomer into a 100 KB engineering review.** Lines 12–17 make "read DESIGN_REVIEW.md" the gate on assembly and reference an audit folder, before the reader knows what the device is or what it costs. | `README.md:12–17`; `DESIGN_REVIEW.md` is 100 414 bytes. The same pointer is repeated at lines 47 and 274, and 13 more times from `docs/HARDWARE.md`. Neither persona can act on it. | Re-order the README (outline proposed below). Keep the DESIGN_REVIEW pointer, but under "For engineers / before you modify this design", not as step 0 for a builder. |
| DOCS-07 | HIGH | **"Case agnostic" means there is no case.** No enclosure model, board STEP export, DXF outline or mechanical drawing is published, and no dimensions are tabulated for someone who wants to design one. | `git ls-files` finds no `.stl`, `.f3d`, `.scad`, `.dxf` and no mechanical folder. The only five `.step`/`.stp` files tracked are **vendor component models** under `KiCad/9.0/3rdparty/` (Hirose `FH34SRJ`, APEM `MJTP1117`, Sullins `PPPC062LJBN-RC`, TI `SOT563`) — not the board and not an enclosure. `docs/HARDWARE.md:1215` says "The reference enclosure is 3D-printed, but the board is meant to be housed in anything" and then gives only two EMC-flavoured cautions. Mounting-hole coordinates exist in the design (`H1`–`H5`, 2.2 mm M2, at 94.24/51.65, 53.90/70.50, 47.99/145.25, 100.49/145.25, 94.10/72.00 mm) but appear in no document. The board's own silkscreen tells the reader to "assemble with a screen and case". | Either publish the reference enclosure (even a rough STL), or add a **Mechanical** section: outline 60.05 × 111.30 × 1.6 mm, the five M2 hole coordinates, the connector and button edge positions, the battery cut-out, and a link to an exported STEP. State explicitly that no case is supplied. |
| DOCS-08 | HIGH | **The public URL printed on the board and in `NOTICE` lands on a different, undocumented project.** `github.com/iandchasse/silkscreen-pcb` defaults to branch `master`, which contains the old `minRead_pcb` project, no README and no description. This design lives only on branch `06_2026`. | Fetched 2026-09-20: default branch `master`; top level = `KiCad/9.0`, `simulations/led_driver`, `.gitignore`, `fabrication-toolkit-options.json`, `fp-info-cache`, `minRead_pcb.kicad_{pcb,prl,pro,sch}`; "No description, website, or topics provided"; no README rendered. The URL is in `NOTICE:15`, in the schematic **and** PCB title blocks (`comment 4 "github.com/iandchasse/silkscreen-pcb"`), and on the board's front silkscreen next to a QR code. | Before any board is handed to anyone: merge `06_2026` to `master` (or change the repository's default branch), add a repository description and topics, and confirm the README renders on the landing page. Everything else in this section is worthless if the reader cannot find the files. |
| DOCS-09 | HIGH | **The README tells the reader to pick JLCPCB "Standard" PCBA without preparing them for what Standard requires.** This board is 60.05 mm wide against Standard's stated 70 mm minimum, and Standard lists edge rails *and* fiducials as "Necessary"; the board has neither. | `README.md:142` — "Switch on **PCB Assembly** and choose **Standard**." JLCPCB capabilities page (fetched 2026-09-20): Standard PCBA single PCB "70x70mm - 460x500mm", Edge Rails "Necessary", Fiducials "Necessary"; Economic PCBA "10x10mm - 470x500mm", both "Not necessary", and Economic supports "Single sided placement (SMT/Thru-hole)" — which this board is (162 of 162 placed parts on the bottom). Board is 60.05 × 111.30 mm (`evidence/pcb/board_summary.md`); no fiducial footprints exist in the design. Standard is nonetheless *forced* here because `ESP32-S3-WROOM-1-N16R8` (`C2913202`) is marked **"Standard Only"** on its JLCPCB part page. | Say **why** Standard is mandatory (the ESP32-S3 module is Standard-only), and warn that JLCPCB will add edge rails to reach the Standard minimum — expect a rail on each long edge, a small extra cost, and a board you may have to break or file off. Ask the reader to check in the DFM preview that the rails do not cross the four 0.5 mm perforation slots or the USB-C / microSD edge features. **Confidence: medium** on how JLC applies the rule in practice — I verified the published capability table, not JLC's behaviour on this specific board. |
| DOCS-10 | MEDIUM | **No cost and no lead time in the README.** The reader cannot decide whether to start. | The only cost figures in the repo are `fabrication/BOM.md:117–147` (parts-only per board at 5/10/30/100, plus one real $624.08 quote for 30 boards) and `NEXTPCB_REV0_NOTES.md:79–86`. Neither is linked from the ordering section. No document states a lead time. The README's only figure, "$29.55", is core *parts* in a model on a website that has no content. | Put a two-line expectation at the top of the ordering section: "About **$260–305** for five assembled boards including shipping; about **2–3 weeks** from upload to parcel. The panel, battery and case are extra." |
| DOCS-11 | MEDIUM | **Undefined jargon throughout the ordering path.** DNP (12×), Toolkit (13×), CPL (9×), LCSC (6×), Extended (4×), Gerber (6×), "Fix 4" (1×) are all used without definition. | Counts in the Calculations section above. `README.md:102` uses "CPL" 18 lines before the parenthetical gloss at line 120. "Fix 4" (line 13) is defined only inside the excluded `DESIGN_REVIEW.md`. | Add a short glossary box immediately before the ordering steps, defining exactly these seven terms in one line each. Replace "Fix 4" with what it is ("the reverse-battery protection change"). |
| DOCS-12 | MEDIUM | **No first-power-up checklist and no troubleshooting or support route.** The path ends at "Approve, order, and record". | `README.md:174–178` is the last ordering step. No section covers unboxing, visual inspection, first USB connection, expected current, LED behaviour, or what to do if nothing happens. No Discord, forum, issue tracker or email address appears anywhere in `README.md`. (The board silkscreen promises "Help can be found … at the QR codes on this board", and `de-link.me` mentions a Discord — but the repository does not link one.) | Add "**First power-up**" (inspect → USB-C only, no battery → does the red LED light / does a serial device enumerate → then battery) and "**It doesn't work**" (five most likely causes, ranked) plus a single **Where to get help** line with a real URL. |
| DOCS-13 | MEDIUM | **The one artefact that lets a novice audit the placement preview is hidden in the wrong section.** `assembly_drawing_bottom.pdf` — five A3 pages of part outlines, designators and polarity marks seen from below, with DNP parts crossed out — is described only under PCBWay/NextPCB. | `README.md:233`. The JLCPCB placement-preview step (`README.md:160–165`) instead asks the reader to check rotation of `U2`, `U5`, `D8`, `D2`, `J4`, `U4`, `J7` with no reference to compare against. | Reference the drawing in the JLCPCB step 5 as well: "open `production/other_fabs/assembly_drawing_bottom.pdf` beside the preview and compare part by part." Consider renaming it out of `other_fabs/`, since it is fab-independent. |
| DOCS-14 | MEDIUM | **The through-hole decision is presented as a checkbox, not a choice with consequences.** | `README.md:167–172` lists the 13 THT parts and says "Confirm at the quote that through-hole assembly is included and priced." It never says what happens if it is not: 74 hand joints per board (calculated above), including a 20-pad USB-C connector, or ~$70 of DigiKey parts for 10 boards if bought separately (`NEXTPCB_REV0_NOTES.md:81–83`). | State both options explicitly with their numbers: "(a) let JLCPCB solder them — adds a hand-soldering labour fee and about a day; (b) decline, and solder 13 parts / 74 joints per board yourself, including a 20-pad USB-C. For a first board, choose (a)." |
| DOCS-15 | MEDIUM | **The licence section does not answer the two questions a builder actually asks.** "May I build one for myself?" and "May I sell them?" | `README.md:280–296` quotes the CERN-OHL-S v2 boilerplate and the SPDX id. The word "reciprocal" appears in the licence name only; the practical obligation (publish your modified sources under the same licence, and pass the notice on with the product) is never stated in plain English. Ironically `fabrication/THIRD_PARTY.md:8–20` **does** do this well, with ✅/⚠️ bullets — but it is about library files, not the board. | Add three plain sentences: you may build it, use it and sell it; if you modify the design and distribute or sell the result you must publish your modified source under CERN-OHL-S v2; keep the `NOTICE` with it. Link the `THIRD_PARTY.md` note for the vendored symbol/footprint caveat. |
| DOCS-16 | MEDIUM | **"Minimum quantity is 5" is true for the bare board and misleading for assembly.** The reader will conclude they must pay to assemble five. | `README.md:136`. JLCPCB's capability table gives PCBA order volume "2 - 50 pcs" (Economic) / "2 - 80000 pcs" (Standard), against a bare-board MOQ of 5. | Reword: "You must buy at least **5 bare boards**, but you can choose to have only **2** of them assembled — the cheapest way to get a working prototype, with three spares for later." |
| DOCS-17 | MEDIUM | **The README never tells the reader that KiCad is not required.** It opens with two `kicad-cli` code blocks and a repository tree, which reads as "install KiCad first". | `README.md:72–105` precedes the ordering section. In fact every file needed to order is pre-generated and committed: `production/Silkscreen_Reader_PCB_1.0.zip`, `positions.csv`, `bom_JLC_upload_v4_optimized.csv`. The fresh-export comparison in `evidence/gerber_fresh/COMPARISON.txt` confirms the committed zip is current with the board file (all copper, mask, paste and outline layers identical; drill differs only in slot encoding). | First line of the ordering section: "**You do not need KiCad.** Everything you upload is already in the `production/` folder — download the repository as a ZIP and you are ready." Move the `kicad-cli` blocks to a "Regenerating the files (maintainers)" section near the end. |
| DOCS-18 | MEDIUM | **The four 0.5 mm perforation slots are raised as a risk and then left unresolved.** | `README.md:137–138` — "Those 0.5 mm `Edge.Cuts` polygons are below JLC's 1.0 mm routed-slot minimum; earlier orders were accepted with them, but read any DFM message about them." `fabrication/README.md:93–94` repeats it and adds "check how those boards turned out" — i.e. the owner does not know either. | Decide and document one outcome: either "accepted on two previous orders, proceed and ignore the DFM warning", or "if JLC queries them, reply X". A reader who is already nervous will stop at an unresolved warning they cannot evaluate. |
| DOCS-19 | LOW | **Naming is inconsistent in five directions**, which makes searching and asking for help harder. | Product "Silkscreen" (README title); title block "Silkscreen Reader PCB" (`kicad_sch`/`kicad_pcb` line 8/11); files `silkscreen_pcb.*`; release zip `Silkscreen_Reader_PCB_1.0.zip`; GitHub repo `silkscreen-pcb`; working folder `de-link_pcb`; predecessor "de-link". README uses `silkscreen_pcb` 7× and `de-link` 4×, and never writes "Silkscreen Reader". | Pick one public name ("Silkscreen"), state the relationship to de-link once, and add a one-line note that the KiCad files are named `silkscreen_pcb` for historical reasons. |
| DOCS-20 | DOC | **The board's silkscreen documents a board-shortening modification that no document mentions, and that contradicts the BOM's DNP guidance.** | B.Silkscreen at 103.6, 65.3 mm: "this long end of the board can be cut for smaller displays / if so, unpopulate R36 and R73 / and then, populate R72/R74 / this will swap power button to UP2 / depopulate SW5 (DOWN2) if you please". No `.md` in the repository mentions cutting the board. `docs/HARDWARE.md:961–963` documents the `R72`/`R73`/`R74` jumper only as a power-button reassignment, and `fabrication/BOM.md:277` lists `R72 R74` under "**DNP in every build**" with "**never fit R73 and R74 together**". A reader following the silkscreen has no way to confirm the cut line, the resulting board length, or what else is lost. | Either document the short-board variant properly (where the cut line is, which displays it suits, the full population delta) in the configurations table, or remove the instruction from the silkscreen on the next revision. Flagging it as "undocumented, not verified" in the README is the cheap interim fix. |
| DOCS-21 | DOC | **The panel part number is written three different ways across the repo and the board.** | `README.md` uses both `GDEQ426T82` (line 36) and `GDEQ0426T82` (line 200); `docs/HARDWARE.md` uses `GDEQ426T82` 4×; `fabrication/BOM.md:302` uses `GDEQ0426T82`; the B-side silkscreen says `GDEQ426T82FT01` twice. Good Display's own product pages use **`GDEQ0426T82`** with the leading zero. | Normalise every occurrence to `GDEQ0426T82` and to the exact suffixes `-T01C` / `-FL01C` / `-FT01C`. A reader searching the wrong string finds nothing. |
| DOCS-22 | DOC | **`fabrication/README.md`'s release-record table describes files and dates that do not match the repository.** | It cites "The 2026-09-18 12:22 zip" (`fabrication/README.md:26`) and "The current source (2026-09-18 …)" (`:9`), while the committed `production/Silkscreen_Reader_PCB_1.0.zip` is dated 2026-09-19 18:42 at commit `c0eccde`. Its "Matched order" row points at `production/bom_JLC_upload-JLCPCB Assembly Order.xls`, which is **not tracked in git** (`git ls-files production` lists 15 files; that is not one of them) and is not marked local-only there, although the root README does mark it so. | Refresh the dates to the current commit, and mark the `.xls` row "local only, not in the repository", matching `README.md:125`. |
| DOCS-24 | MEDIUM | **The README tells the reader the wrong rule for checking the LED's polarity, and contradicts the repo's own BOM.** Twice, in the step where the reader is told to verify polarity in the factory's preview, it says "LED **pad 1 is the anode**". Pad 1 is the **cathode**. | Ground truth: `evidence/sch/connectivity_by_component.txt:229–230` — `D2 pin 1 K → Net-(D2-K)`, `pin 2 A → USB_VBUS`; the footprint's pad `1` carries the cathode net (`board_extract.json`: pad 1 at 102.8, 116.86 on `Net-(D2-K)`). The repository's own BOM says the opposite of the README twice: `fabrication/BOM.md:196` "pad 1 = cathode" and `:296` "(red 1206, pad 1 = cathode)". The wrong statement is at `README.md:163` (JLCPCB preview step) and `README.md:249` (other-fabs preview step) — i.e. in exactly the two places a reader is told to use it. `fabrication/README.md:87` hedges as "D2 LED pad-1/anode convention". | Correct both README occurrences to "**pad 1 is the cathode**". Consequence if uncorrected is cosmetic rather than damaging — `D2` is the USB-present indicator, so a reversed part simply never lights — but it is the *one* concrete polarity rule given to a novice, and it is inverted. |
| DOCS-23 | LOW | **No table of contents and no quick-path / deep-dive split in the README.** | 298 lines, 15 second-level headings, no TOC. By contrast `docs/HARDWARE.md:44` has one and is easier to navigate despite being four times longer. | Add a TOC, and put a three-line "I just want one → jump to §Order an assembled board" signpost above it. |

### The findings that actually decide whether this works

**DOCS-08 gates everything.** The repository's own `NOTICE`, the schematic title block, the PCB title
block and the printed silkscreen all publish `github.com/iandchasse/silkscreen-pcb`. Fetched today,
that URL's default branch is `master`, holding the predecessor `minRead_pcb` project, no README and
no description. A person holding one of these boards, or reading the NOTICE, cannot reach this
design. It is a five-minute fix (merge or re-point the default branch) and no documentation work
matters until it is done.

**DOCS-03 is the one that costs money.** The README presents `bom.csv`, `bom_JLC_upload_v3.csv` and
`bom_JLC_upload_v4_optimized.csv` as three ways of saying the same thing. They are not: the first
two put `C28323` and `C14663` on two BOM lines each, and the repository's own record
(`NEXTPCB_REV0_NOTES.md:35`) says JLCPCB left `C20`, `C24` and `C31` unmatched as a result. An
amateur who picks `bom.csv` — the most obviously-named file, and the one the README lists first —
meets three "No Parts Selected" rows and has no idea that the fix is to switch files. JLCPCB's help
page confirms the behaviour: "When the same component is matched across multiple BOM rows, a warning
will appear". Name one file.

**DOCS-01 and DOCS-04 together are the difference between a project and a product.** Today the
documentation takes the reader with great care up to the moment a parcel arrives, and then stops.
There is no firmware named anywhere, no panel vendor, no battery spec beyond "single-cell", no cable
part number, no screw size, no case. Persona A can improvise most of it; Persona B cannot start.

**DOCS-05 is the safety one.** `J5` is a 2-pin JST-PH with pin 1 = `B−`. Pigtails from cell vendors
come in both polarities, the board's only guidance is `- +` and `CHECK` in 1 mm silkscreen, and the
README has not one warning callout. This is a lithium cell; the warning should exist whether or not
anyone reads it.

---

## Persona walk-throughs

### Persona A — "Arduino Andy" (can solder, has never ordered a PCB)

| Step | What happens | Verdict |
|---|---|---|
| Find the project | Clones from a link a friend sent. If instead he types the URL on the board → wrong project (DOCS-08) | ⚠ |
| Understand it | "At a glance" table is excellent for him — module variant, flash/PSRAM, power chain, button count all there | ✅ |
| Which files where | Gets there, but must first decide between three BOM files (DOCS-03) and skip past two `kicad-cli` blocks that imply he needs KiCad (DOCS-17) | ⚠ |
| Which options | Steps 2–4 are genuinely good: layers, thickness, copper weight, **Assembly side: Bottom**, Confirm Parts Placement = Yes. Stops cold at the rails/fiducials and 70 mm questions he cannot evaluate (DOCS-09), and the unresolved 0.5 mm slot warning (DOCS-18) | ⚠ |
| What else to buy | Has to reverse-engineer it from `fabrication/BOM.md:300`, two rows (DOCS-04) | ❌ |
| What to solder | Knows the 13 THT parts are listed; does not know it is 74 joints or that declining assembly is an option with a price (DOCS-14) | ⚠ |
| Power up & flash | Dead end — no firmware (DOCS-01) | ❌ |
| It doesn't work | No troubleshooting, no support link (DOCS-12) | ❌ |

**Andy gets a board.** He does not get a reader.

### Persona B — "Interested Bea" (wants the device, nervous about PCBA)

| Step | What happens | Verdict |
|---|---|---|
| Find the project | Same problem, and no repository description on GitHub to reassure her she is in the right place (DOCS-08) | ❌ |
| Understand it | Line 12 tells her to read a 100 KB design review before assembly; line 13 mentions "Fix 4", "the Q4 replacement" and "the slotted microSD land". She does not know whether the board is finished or broken (DOCS-06, DOCS-11) | ❌ |
| Which files where | She is told the easiest route is a configurator (DOCS-02) that is not there | ❌ |
| Which options | "Leave **Tooling holes** on *Added by JLCPCB*" is the right level of instruction — the rest of the section assumes she knows what a Gerber, a CPL and an Extended part are | ⚠ |
| What else to buy | Nothing usable (DOCS-04) | ❌ |
| What to solder | Reads that 13 parts are through-hole. Has no iron (DOCS-14) | ⚠ |
| Power up & flash | No firmware, no instructions (DOCS-01) | ❌ |
| It doesn't work | No help route (DOCS-12) | ❌ |
| Safety | Plugs in a LiPo with no warning that polarity is not standardised (DOCS-05) | ❌ |

**Bea abandons at line 12.** She never reaches the ordering section, which is the part of the README
that would actually have served her.

---

## Checked and found OK

These were verified against the evidence pack, not taken on trust. They are correct and should not be
changed.

* **Every relative link and image reference in every non-excluded `.md` resolves.** A script walked
  all tracked markdown and resolved 88 link/image targets: **0 broken, 0 bad anchors, 0 targets
  outside git**. Including the cross-file anchor `../README.md#ordering-from-jlcpcb-step-by-step`.
  All 23 files in `docs/images/` that are referenced exist.
* **Part-count arithmetic is exactly right.** README line 44: "179 references = 162 fitted + 10 DNP +
  7 bare-copper (holes `H1`–`H5`, test pads `TP1`/`TP2`)". Netlist: 179 components. DNP set from
  `evidence/sch/bom_ungrouped.csv` = `R43 R45 R58 R66 R72 R74 SW6 TP3 TP4 TP5` = **10**. Placed rows
  in `production/positions.csv` = **162**. 162 + 10 + 7 = 179. ✅ (The 183 footprints in the board
  extract are these 179 plus four logo graphics.)
* **"Every component … is on the back copper layer" is true.** All 162 rows of `positions.csv` are
  `bottom`. The only top-side items are four logos, mounting hole `H5` and the DNP test points
  `TP3`–`TP5`. ✅
* **The through-hole list is complete and correct.** `J1`, `J5`, `J6`, `SW1`–`SW5`, `SW7`–`SW11` =
  13 parts, confirmed from pad types in `evidence/pcb/board_extract.json`. ✅
* **The DNP list is stated identically in all four places it appears** (README ×2,
  `fabrication/README.md:101`, `fabrication/BOM.md:11`). ✅
* **Board size and stackup claims are right.** "2-layer, 60 × 111 mm, 1.6 mm, 1 oz" vs measured
  60.05 × 111.30 mm, 2 copper layers, 1.6 mm. ✅
* **The committed Gerber zip is current with the board file.** `evidence/gerber_fresh/COMPARISON.txt`:
  all nine layers identical, same drill tools and hits (slot encoding differs only in syntax). The
  README's repeated "regenerate after every save" warning is sound advice and the repository is in
  fact in the correct state. ✅
* **`bom_JLC_upload_v4_optimized.csv` is clean and complete** — 172 designators, no duplicate LCSC
  codes, the 10 DNP refs present as blank-part-number lines exactly as the README describes at
  line 154. ✅
* **The Fabrication Toolkit vs raw-KiCad rotation warning is real and correctly stated.**
  README line 244: "93 of its 162 rows differ from KiCad's values". Spot-checked: `U2` is
  `-90.0°` in `evidence/pcb/positions_all.csv` and `270°` in the KiCad placement export, and the
  README is right that `production/positions.csv` must not be used at other fabs. ✅
* **The "Which parts are optional?" table is correct, including its one genuine trap.** This is the
  riskiest table in the repository — it is the only place the README tells a reader to *delete*
  references from the BOM and CPL — so every group was checked against
  `evidence/blocks/_block_membership.csv`:
  * **Frontlight** — all 14 listed refs (`J3 U10 U12 L2 Q5 Q6 C9 C24 R37 R39 R41 R49 R50 R75`) are
    members of schematic block `16_led_driver_connector`. ✅
  * **The trap, handled correctly:** that block also contains **`C12`**, which is *not* a frontlight
    part — it is the LDO input capacitor. The README does not list it under Frontlight and instead
    names it explicitly in the **Core** row ("the shared parts `R47`/`R48` (I²C pull-ups) and `C12`
    (LDO-input capacitor)"). A reader deleting the frontlight block will therefore keep it. This is
    the single most dangerous deletion available to a replicator, and the documentation gets it
    right. ✅
  * **Touch** — `J4`, `U7` are exactly the two members of `20_touch_connector_esd`; `R42 R44 R46 R52`
    are exactly the four *fitted* members of `21_touch_jumper_mux`, whose other four members are the
    DNP alternates `R43 R45 R58 R66` the README separately warns about. ✅
  * **RTC** — `U13`, `C30` are exactly the two members of `13_external_rtc`. ✅
  * **Expansion** — `J6` (`08_ext_peripheral_connector`), `U8` (`09_ext_peripheral_esd`). ✅
  * **No optional group over-lists a core part.** Where the README under-lists (the frontlight's
    `TP3`–`TP5` are covered by the parenthetical "`TP3`-`TP5` stay DNP"), the consequence is only a
    part left fitted on a dead net — harmless. ✅
* **`fabrication/THIRD_PARTY.md` is a model of plain-language licensing.** Its ✅/⚠️ bullets answer
  "can I use this, can I sell this, what may I not redistribute" in three lines. This is the register
  the README's own licence section should copy.
* **`docs/HARDWARE.md`'s framing note is honest and well judged** — it says up front that the
  document was written after the board, that its rationale is reconstruction, and where the open
  issues live. That disclaimer is worth keeping.
* **`fabrication/NEXTPCB_REV0_NOTES.md` is exemplary failure-reporting** — it distinguishes what was
  observed from what was inferred, records what could not be reproduced ("its result was not
  recorded"), and ends with a clear recommendation. The only problem is that one of its findings
  (DOCS-03) belongs in the README too.
* **The placement-preview checklist names the right parts.** `U2`, `U5`, `D8`, `D2`, `J4`, `U4`, `J7`
  match the footprints whose anchors/conventions are genuinely at risk. ✅ *(But the polarity rule it
  gives for `D2` is inverted — see DOCS-24.)*
* **JLCPCB "Assembly side: Bottom" is the correct instruction**, and JLCPCB does support single-sided
  bottom placement with THT under both service tiers. ✅

---

## Proposed README outline

Reordered for the two personas, deep material preserved but moved below the fold.

```
Silkscreen — an e-reader you build yourself
  one paragraph: what it is, one photo of a finished unit
  a 6-line "what you get / what you must add" box
  three links: [I want one] [I want to understand it] [I want to modify it]

⚠ Before you start        (LiPo polarity, lithium safety, "this is a bare board, firmware is …")

Order an assembled board — step by step, no experience needed     <- the draft below
  0. What this costs and how long it takes
  1. Download the files (no KiCad needed)
  2. Order the bare board
  3. Turn on assembly
  4. Upload the two files
  5. Fix the BOM matches
  6. Check the placement preview
  7. Pay, and what to expect

What else you must buy    (panel · battery · microSD · cable · screws · case — table with links)

When the parcel arrives
  first power-up checklist
  putting firmware on it
  it doesn't work → ranked causes → where to get help

Choosing a configuration  (the existing optional-blocks table, unchanged — it is good)

Building it by hand       (the DigiKey route, hand-build BOM, 74 THT joints)

Other factories           (PCBWay / NextPCB, unchanged)

For engineers
  At a glance · HARDWARE.md · DESIGN_REVIEW.md · repository layout · regenerating the files

Licence · credits
```

Rules of thumb for the rewrite: **every instruction that requires KiCad moves below "For
engineers"**; **every number a reader must type or click is bold**; **every file the reader uploads
is named exactly once and never offered as a choice**.

---

## Draft: "Order an assembled board — step by step, no experience needed"

*Written to be pasted into the README as a replacement for the current §"Ordering from JLCPCB, step
by step". It is a draft for the owner to edit — this review did not modify `README.md`.*

---

### Order an assembled board — step by step, no experience needed

You do **not** need KiCad, and you do not need to know how a PCB is designed. A factory will make
the board and solder every part onto it. You will be clicking through a web shop and uploading three
files that are already in this repository.

**What it costs and how long it takes.** About **$260–305** for five boards with everything soldered
on, including shipping — roughly **$50–60 each**. Allow **2–3 weeks** from clicking "order" to the
parcel arriving. The display panel, battery and case are **not** included; budget for those
separately (see *What else you must buy*).

> **Why five?** The factory's minimum for bare boards is 5. You can choose to have only **2** of them
> assembled, which is the cheapest way to get one working reader plus a spare, and leaves you three
> bare boards for later.

#### Step 1 — Get the files

Download this repository (green **Code** button → **Download ZIP**) and unzip it. Everything you need
is in the `production/` folder. You will upload exactly three files:

| Upload this | It is | Where it goes |
|---|---|---|
| `production/Silkscreen_Reader_PCB_1.0.zip` | the board itself (copper layers and hole positions) | the "Add Gerber file" box |
| `production/bom_JLC_upload_v4_optimized.csv` | the shopping list of parts | the "Add BOM file" box |
| `production/positions.csv` | where each part sits and which way it faces | the "Add CPL file" box |

Ignore everything else in that folder. In particular **do not upload `bom.csv` or
`bom_JLC_upload_v3.csv`** — they list two parts on duplicate lines, and the factory's matcher will
leave `C20`, `C24` and `C31` unselected if you use them.

#### Step 2 — Order the bare board

1. Sign in at [jlcpcb.com](https://jlcpcb.com) and click **Order now**, then **Add Gerber file** and
   choose `Silkscreen_Reader_PCB_1.0.zip`.
2. The viewer will draw the board. Confirm it says **2 layers** and about **60 × 111 mm**. If it does
   not, you uploaded the wrong file.
3. Set **PCB Qty = 5**, **Thickness = 1.6 mm**, **Outer Copper Weight = 1 oz**. Surface finish and
   solder-mask colour are entirely your choice — nothing in this design needs a particular one.
4. Leave everything else at its default.
5. Scroll the Gerber viewer to the board edges and look at the USB-C cut-out, the microSD opening and
   the four narrow slots along the outline. They should be open, not filled. Those four slots are
   0.5 mm wide, which is narrower than the factory's usual 1.0 mm minimum for a routed slot; two
   previous orders of this board were accepted with them. If the site shows a DFM (design-for-
   manufacture) message about them, it is safe to accept and continue.

#### Step 3 — Turn on assembly

1. Switch **PCB Assembly** on.
2. Choose **Standard** — not Economic. This is not optional: the ESP32-S3 module used here
   (`C2913202`) is only available on the Standard service.
3. Because it is Standard, the factory will add **edge rails**: two strips of extra board material
   along the long edges, which it uses to hold the board in the machine. They cost a little extra and
   arrive attached; you snap or file them off. This is normal.
4. Set **Assembly side: Bottom**. Every single part on this board is on the back. If you leave this
   on "Top" you will receive five blank boards and a bag of parts.
5. Set **PCBA Qty** to **2** (or 5 if you want them all built).
6. Leave **Tooling holes** on *Added by JLCPCB*.
7. Set **Confirm Parts Placement** to **Yes**. This costs a small fee and is worth every cent on a
   first order — it lets you look at a picture of where the robot will put each part before it does.
8. Click **Confirm**, then **Next**.

#### Step 4 — Upload the parts list

1. **Add BOM file** → `production/bom_JLC_upload_v4_optimized.csv`
2. **Add CPL file** → `production/positions.csv`
3. Click **Process BOM & CPL**.

#### Step 5 — Check the parts the factory picked

You will get a table with one row per part. Most rows will already be matched.

* **Rows with a blank part number are meant to be blank.** Ten of them
  (`TP3 TP4 TP5`, `R43 R45 R58 R66 R72 R74`, `SW6`) are marked *"DNP (standard build)"* — DNP means
  "do not populate", i.e. a spot on the board deliberately left empty. **Leave them unselected.**
* **Every other row must show a green match.** If a row says *No Parts Selected*, *out of stock* or
  shows a manufacturer's part number instead of a `C…` code, click **Search** and look the part up.
  [`fabrication/BOM.md`](../../../fabrication/BOM.md) lists an approved alternative for every part on this
  board — use that list, not your own judgement, because some of these parts have look-alikes with
  different pinouts.
* The part most likely to be short is **TPS923610DRLR** (the frontlight driver). If it is out of
  stock and you are not fitting a frontlight panel, you can untick it and the parts listed under
  *Frontlight* in the configuration table.
* Click **Next**.

#### Step 6 — Check the placement preview (do not skip this)

You will see a drawing of the board with every part on it. This is your last chance to catch a part
that is rotated wrongly, and the factory's own checker has corrected several on this board before.

Open `production/other_fabs/assembly_drawing_bottom.pdf` from the repository next to the preview —
it shows the same view (from underneath), at about 6.5× magnification, with polarity marks, so you
can compare part by part.

Look specifically at:

| Part | What to check |
|---|---|
| `D2` | The LED. Pad 1 is the **cathode** (the flat/marked end). This is the opposite of some libraries' convention. |
| `U2`, `U5`, `D8` | Small 3–8 pin chips whose rotation the factory has corrected before. |
| `J4` | Its outline sits 0.73 mm off its own pads in the drawing — the pads are what matter. |
| `U4`, `J7` | The ESP32 module and the microSD socket; check they are centred over their pad patterns. |

If something looks wrong, use the preview's rotate/move tools to correct it, and **save a screenshot
of the corrected preview** — you will want it if a later order behaves differently. Click **Next**.

#### Step 7 — Through-hole parts

Thirteen parts have legs that pass through the board — the USB-C socket (`J1`), the battery connector
(`J5`), the expansion header (`J6`) and the ten buttons (`SW1`–`SW5`, `SW7`–`SW11`). They are already
in the files you uploaded.

* **Recommended:** let the factory solder them. Confirm on the quote page that through-hole soldering
  appears as a line item. It adds a one-off hand-soldering fee and about a day.
* **If you decline**, you will receive the parts loose and must solder **74 joints per board**
  yourself, including a 20-pad USB-C connector. Only choose this if you are confident with an iron
  and a fine tip.

#### Step 8 — Pay, and keep the paperwork

Read the price summary: bare boards, setup fee, per-part-type fees, the parts themselves, assembly.
Place the order. Then **save, in one folder**: the order confirmation, the accepted BOM as the
factory matched it, any part substitutions it proposed, and your screenshot of the approved
placement preview. If you ever order again, you will want to know exactly what was built the first
time.

---

## Documentation cross-check

Performed after the findings above were written, per the review protocol. Each row is a place where
the prose says something the design does not do, or makes a claim I could not confirm.

| Document | Claim | Reality / status |
|---|---|---|
| `README.md:109–113`, `:186` | silkscreenreader.com has a "*Build one*" configurator and it is "the easiest, least error-prone route" | The site renders a title and nothing else (fetched 2026-09-20). **DOCS-02** |
| `README.md:4`, `docs/HARDWARE.md:3` | "custom enclosures and firmware", "case agnostic · firmware agnostic" | No enclosure files and no firmware exist or are linked anywhere in the repository. **DOCS-01, DOCS-07** |
| `README.md:128–129`, `:146` | `bom.csv` and the two `bom_JLC_upload_v*` files are interchangeable — "Pick one BOM, not all three" | `bom.csv` and `v3` contain duplicate LCSC codes that are recorded elsewhere in this same repository as having caused unmatched parts at JLCPCB. Only `v4_optimized` is clean. **DOCS-03** |
| `README.md:142` | "choose **Standard**" | Correct and in fact mandatory (module is Standard-only), but Standard's published envelope is 70 × 70 mm minimum with edge rails and fiducials "Necessary"; this board is 60.05 mm wide with neither. The README does not prepare the reader. **DOCS-09** |
| `README.md:136` | "Minimum quantity is **5**" | True for bare boards; JLCPCB's PCBA minimum is 2. Reads as "you must assemble five". **DOCS-16** |
| `README.md:13` | "the Q4 replacement and the slotted microSD land are all applied in the source" | Not verifiable from this section's scope — it depends on `DESIGN_REVIEW.md`, which this review is blind to. Other reviewers in this pack own `Q4` and `J7`. **Could not verify.** |
| `README.md:190` | Core configuration costs "about **$29.55** of parts at quantity 1 in the site's model" | Traceable to no artefact in the repository; the site hosting "the site's model" has no content. `fabrication/BOM.md` gives $33.23/board for the *full* build at qty 5, which is a different figure for a different thing. **Could not verify** — recommend removing or sourcing it. |
| `README.md:163`, `:249` | "`D2` (LED **pad 1 is the anode**)" | Pad 1 is the **cathode** (`D2 pin 1 = K`, and `fabrication/BOM.md:196`/`:296` say "pad 1 = cathode"). The README contradicts its own BOM, in the step where the reader is told to verify polarity. **DOCS-24** |
| `README.md:158` | "Watch stock on **TPS923610DRLR** (about 189 pcs at last check)" | Undated stock figure; will be wrong by the time anyone reads it. Reword to "check stock" without a number. |
| `fabrication/README.md:9`, `:26` | "The current source (2026-09-18 …)"; "The 2026-09-18 12:22 zip was verified geometrically identical" | The committed zip is dated 2026-09-19 18:42 at commit `c0eccde`. Independently re-verified as current today (`evidence/gerber_fresh/COMPARISON.txt`), so the *substance* holds and only the dates have drifted. **DOCS-22** |
| `fabrication/README.md:30` | Release record "Matched order — `production/bom_JLC_upload-JLCPCB Assembly Order.xls`" | Not tracked in git. The root README marks it local-only; `fabrication/README.md` does not. **DOCS-22** |
| `fabrication/BOM.md:277`, `docs/HARDWARE.md:961–963` | `R72`/`R74` are "DNP in every build"; "never fit `R73` and `R74` together" | Correct as written — but the board's own B-side silkscreen instructs the reader to populate `R72`/`R74` (after unpopulating `R36`/`R73`) as part of an undocumented board-shortening option. The two sources contradict each other in spirit. **DOCS-20** |
| `README.md:36`, `docs/HARDWARE.md` ×4 | Panel is "`GDEQ426T82`" | Good Display's part number is `GDEQ0426T82`. `fabrication/BOM.md:302` and `README.md:200` use the correct form; the silkscreen uses a third form. **DOCS-21** |
| `NOTICE:15`, schematic/PCB title block `comment 4`, front silkscreen | "Source location: https://github.com/iandchasse/silkscreen-pcb" | That repository's default branch contains a different project, no README and no description. **DOCS-08** |
| `README.md:44`, `fabrication/README.md:10`, `fabrication/BOM.md:11` | "179 references = 162 fitted + 10 DNP + 7 bare-copper" | **Confirmed correct** against the netlist and `positions.csv`. |
| `README.md:120`, `:143` | `positions.csv` is "162 rows, all on the bottom side"; "Every component … is on the back copper layer" | **Confirmed correct.** |
| `README.md:244` | "93 of its 162 rows differ from KiCad's values" | **Spot-confirmed** (e.g. `U2` −90° vs 270°); the full 93-row count was not recomputed. |

---

## Open questions for the designer

1. **Is there firmware?** If it exists, where, and under what licence? If it does not, the README
   must say so in its first paragraph — it changes who should attempt this build.
2. **Is there a reference enclosure?** `HARDWARE.md` says one is 3D-printed. Can it be published,
   even roughly? If not, may the mounting-hole coordinates and outline at least be tabulated?
3. **Is the silkscreen's "cut the long end" option real and tested?** If yes it needs documenting; if
   no it should come off the next board revision (DOCS-20).
4. **What is the intended public name and the canonical URL?** The answer determines the fix for
   DOCS-08 and DOCS-19, and it is printed on physical boards.
5. **When JLCPCB adds edge rails to reach the Standard minimum, where do they land?** I verified the
   published capability table, not the behaviour on this outline. If a previous order already went
   through Standard assembly, the answer is in that order's DFM record and should go in the README.
6. **Where should a reader ask for help?** There is no support route in the repository. A Discord
   invite, a GitHub Discussions tab or an email address — any one of them — closes DOCS-12.
7. **Should `assembly_drawing_bottom.pdf` move out of `other_fabs/`?** It is fab-independent and is
   the single most useful artefact for a novice checking a placement preview (DOCS-13).

### What I did not get to

* I did not open `DESIGN_REVIEW.md` or `docs/audit-*` (excluded by protocol), so I cannot say whether
  the README's summaries of them are faithful.
* I did not test an actual JLCPCB upload, so DOCS-09's practical consequence (rails on this specific
  outline) is inferred from the published capability table, not observed.
* I did not check the QR codes printed on the board — no decoder was available in this environment —
  so I cannot confirm what URLs they encode. Given DOCS-08 and DOCS-02, they are worth decoding
  before any board is handed out.
* I did not review `docs/HARDWARE.md` line by line for technical accuracy; that belongs to the
  block reviewers. I reviewed only its navigability and its framing.

---

## Sources

* Repository documents read in full: `README.md`, `fabrication/README.md`, `fabrication/BOM.md`,
  `fabrication/NEXTPCB_REV0_NOTES.md`, `fabrication/THIRD_PARTY.md`, `NOTICE`, plus the headings,
  framing note and enclosure/power-button sections of `docs/HARDWARE.md`.
* Ground truth: `docs/final-review-2026-09-19/evidence/` — `pcb/board_summary.md`,
  `pcb/board_extract.json`, `pcb/positions_all.csv`, `sch/connectivity_by_component.txt`,
  `sch/bom_ungrouped.csv`, `gerber_fresh/COMPARISON.txt`; and the repository's own
  `production/*.csv`, `production/other_fabs/*.csv`, `git ls-files`.
* Board silkscreen text extracted from `silkscreen_pcb.kicad_pcb` (scratch copy) with KiCad 9.0.6
  `pcbnew`, enumerating `PCB_TEXT` and `PCB_TEXTBOX` items on `F.Silkscreen` / `B.Silkscreen`.
* JLCPCB, *PCB Manufacturing & Assembly Capabilities* —
  https://jlcpcb.com/capabilities/pcb-assembly-capabilities (fetched 2026-09-20): Economic vs
  Standard PCBA table — assembly sides, single-PCB size 10×10–470×500 mm vs **70×70–460×500 mm**,
  order volume 2–50 vs 2–80000 pcs, Edge Rails / Fiducials "Not necessary" vs **"Necessary"**; THT
  supported under both.
* JLCPCB, *How do I place a PCBA order?* — https://jlcpcb.com/help/article/how-do-i-place-a-pcba-order
  (step sequence and the exact control names used in the draft above).
* JLCPCB, *Common BOM and CPL matching issues* —
  https://jlcpcb.com/help/article/common-bom-and-cpl-matching-issues-and-explanations : "When the
  same component is matched across multiple BOM rows, a warning will appear"; "Repeated Designator";
  inconsistent-designator handling.
* JLCPCB, *PCB Assembly Cost* — https://jlcpcb.com/help/article/pcb-assembly-price : Economic setup
  $8.18 / stencil $1.53 vs Standard $25.56 single-side / stencil $8.21; hand-soldering labour $3.58
  per order.
* JLCPCB part page for `C2913202` (ESP32-S3-WROOM-1-N16R8) — https://jlcpcb.com/partdetail/C2913202 :
  assembly restriction **"Standard Only"**.
* https://silkscreenreader.com (fetched 2026-09-20): title only, no content.
* https://github.com/iandchasse/silkscreen-pcb (fetched 2026-09-20): default branch `master`,
  top-level `minRead_pcb.*`, no README rendered, "No description, website, or topics provided".
* Good Display product pages for the `GDEQ0426T82` family (`-T01C`, `-FL01C`, `-FT01C`) —
  https://www.good-display.com/product/957.html and related, for the canonical part-number spelling.
