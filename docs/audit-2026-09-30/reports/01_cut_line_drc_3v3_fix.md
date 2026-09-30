# Trim-at-y62 DRC acceptance test (x3 3V3 island fix)

> Run on 2026-09-30, before commit `3edd0c8` existed: **HEAD / OLD / CONTROL = `6871962`** (design and production files
> identical to `aeb5b39`, the Rev 1.0 order) and **working copy / NEW / FIX = the change later committed as `3edd0c8`** (1.01).
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Scratch: evidence/A_trim. CONTROL = trimmed old.kicad_pcb (HEAD), FIX = trimmed new.kicad_pcb (working copy).

## Method
- A_trim/trim.py (KiCad 9 pcbnew), identical for both copies, each loaded next to a copy of silkscreen_pcb.kicad_pro (no .kicad_dru exists in the repo):
  footprints with position y < 62 deleted (9 in each; no kept footprint has a pad above 62); tracks/vias entirely above deleted (190 tracks, 16 vias each);
  12 tracks crossing y 62 CLIPPED at y 62 (same 12 in both copies, incl. the two 3V3 feeds x 87.526 and (101.101,62.501)->(99.4,60.8));
  Edge.Cuts: lines clipped at y 62 (x 84.409 and x 104.237), shapes above deleted, new edge at y 62 closing the outline;
  the filled Edge.Cuts rect slot (x 89.586..94.886, y 61.4..62.5) that straddles the cut becomes a 0.5 mm notch in the new edge;
  zone outlines intersected with y >= 62 (GND zone now y 62.0..148.72), refilled with pcbnew.ZONE_FILLER, saved.
- kicad-cli 9.0.6 `pcb drc --format json --severity-all --units mm` (no parity) on control, fix, and untrimmed full_old / full_new as baselines.
- Raw: A_trim/drc_{control,fix,full_old,full_new}.json, A_trim/drcdiff.txt

## Findings

### F1 (info) CONTROL reproduces the 3V3 island
drc_control.json unconnected_items (2): (a) 3V3 "Missing connection" Track B.Cu 0.7085 mm @(101.101,62.501) [island side, clipped stub of (101.101,62.501)->(99.4,60.8)]
<-> Track B.Cu 1.4765 mm @(87.526,63.476) [main side, clipped x 87.526 feed]; (b) GND zone-to-zone (trim artefact, see F4).
Ratsnest endpoints differ from the owner's earlier run (which reported both at Q2 pad 2) because this trim CLIPS crossing tracks, so the stubs are the nearest island/main items; island membership confirmed by connectivity below.

### F2 (info) FIX: zero unconnected 3V3 items
drc_fix.json unconnected_items (1): only "Pad 2 [GND] of C21 @(74.800,80.338) <-> Zone [GND]" (see F4). No 3V3 item.

### F3 (info/warn) DRC diff FIX-trim vs CONTROL-trim
- copper_edge_clearance 14 vs 14 (all from tracks clipped to the cut line + the pre-existing x=101.101 3V3 vertical ending at y 62.501, 0.376 mm from the cut; same in both).
- J1 (USB-C) PTH pad clearance 0.15 < 0.2 mm: 11 vs 12 reported, pairs shuffle between runs (full_old 12 vs full_new 10 too); pre-existing footprint issue, not from this change.
- NEW in FIX (also in untrimmed full_new, absent in full_old): track_dangling warning "Track [3V3] on B.Cu, length 0.1414 mm @(101.001,64.900)" -- in the new fix path.

### F4 (warn) GND unconnected in BOTH trims = same pre-existing split, not a FIX regression
- Geometric GND clustering (A_trim/gnd3.py: pads/tracks/vias + zone-fill islands, layer-aware) on the REFILLED trims: 2 GND clusters in CONTROL and in FIX, 1 on full_new.
  The minor cluster is the same in both: U3.2 (LDO GND), U2.1, Q1.3, J7.9, H5.1, C3.2, C4.2, C6.2, C25.1, C26.2, R16.1, R51.2, R77.2 + vias (84.32,89.68) (83.40,85.10) (76.20,85.80) (77.80,84.10) (80.10,87.70) (82.10,82.20) [+ (99.30,65.60) in CONTROL only: the via the owner moved].
- DRC shows this one split with different ratsnest endpoints: CONTROL "Zone<->Zone", FIX "C21.2 (main side) <-> Zone (minor side)". So the new C21 item is NOT a new disconnection.
- Caveat: refill pulls the pour 0.475 mm back from the new y62 edge; physically the fab copper keeps the ORIGINAL fill up to the cut. Re-checked with the original fill clipped at y62 (no refill) -> F5: identical result.

### F6 (info) 3V3 copper connectivity (independent of DRC, A_trim/analyze.py geometric union-find on 3V3 pads/tracks/vias; 3V3 has no zone)
- 3V3 source: U3 TLV75533PDBV (3.3 V LDO), pad 5 OUT @(77.300,83.200).
- CONTROL: 3 clusters -- main (U3.5 + 27 other pads), island {Q2.2, R81.2, 15 items}, singleton R48.1 (modelling gap, same in FIX; DRC reports no R48 issue in any run).
- FIX: 2 clusters -- main contains U3.5, Q2.2 AND R81.2 (30 pads); singleton R48.1 (same modelling gap). PASS.

### F7 (info) New 3V3 copper vs the y62 cut (edge of copper = centreline minus 0.125 mm)
- Genuinely new path segments: minimum 2.048 mm (y 64.173 run x 91.527..98.488 and (90.4,65.3)-(91.527,64.173)); vs the 0.5 mm slot-notch floor at y 62.5 (x 89.586..94.886): 1.548 mm. No warn.
- The split-off upper piece of the existing x=101.101 vertical, (101.101,64.6)-(101.101,62.501), is 0.376 mm from the cut -- same geometry as HEAD (flagged copper_edge_clearance in both trims); on a real x3 cut it is a dead 3V3 spur whose stub continues to the cut edge (exposed 3V3 copper at the edge, pre-existing).
- 1 um micro-segment in the new path: (101.000,64.900)-(101.001,64.900), then (101.001,64.9)-(101.101,65.0); DRC flags "Track has unconnected end" (track_dangling warning) on the untrimmed full_new too. Electrically connected (copper overlaps; DRC and geometry agree), cosmetic.

### F5 (warn) Physically faithful re-trim (original fab fill clipped at y62, no refill): same outcome
- trim.py mode `clipfill` -> A_trim/cf_control / cf_fix, DRC: drc_cf_control.json = 2 unconnected (the 3V3 island + GND zone<->zone), drc_cf_fix.json = 1 unconnected (GND C21.2 <-> zone). 133 violations each.
- A_trim/gnd4.txt: on both, GND pads OFF the main GND cluster = U3.2 (TLV75533 LDO GND), U2.1 (TPS2116 power mux), Q1.3 (FS8205A battery-protection FET), C3.2 10u, C4.2 22u, C6.2 22u, C25.1, C26.2, R16.1, R51.2, R77.2, H5.1, and two J7 shell pads "9".
  Main cluster holds U4 (ESP32) 1/40/41, J1 USB-C GND, C21.2, and J7 pads 6 and 9.
- So on an x3 board the power-section GND reaches the rest of GND ONLY through the micro-SD socket J7 metal shell (duplicate pad "9" tabs, not a copper connection KiCad counts).
  The battery return current (and the charge current) would flow through the SD socket shield. Pre-existing on HEAD, not introduced or worsened by this change; not part of the 3V3 pass criteria.
  Suggest a GND tie below the cut before the next rev (the minor F.Cu island spans x 87.8..97.5, y 62..79.5 right next to main-GND copper), or at least document it.

## Verdict
PASS for the 3V3 acceptance test: CONTROL reproduces the island (3V3 unconnected, Q2.2 + R81.2 isolated); FIX has zero unconnected 3V3 items in both trim variants, and geometry puts Q2.2 and R81.2 in the U3 (TLV75533PDBV) pad-5 3V3 cluster.
No FIX-only unconnected items or new error classes. FIX-only: one track_dangling warning (1 um micro-segment at (101.000..101.001, 64.900)), also present on the untrimmed board.
Warn: pre-existing x3 GND split bridged only by the J7 shell (F4/F5).
Note: kicad-cli on the untrimmed boards reports 10 (new) / 12 (HEAD) non-excluded J1 USB-C pad-to-pad clearance errors (0.15 vs 0.2 mm Power netclass); pre-existing, the pairs reshuffle between runs.

