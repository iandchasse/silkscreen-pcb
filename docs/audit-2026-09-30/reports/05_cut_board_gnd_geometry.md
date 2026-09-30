# GND copper-geometry check (independent method, V_geom)

> Run on 2026-09-30 against the committed boards: Rev 1.0 = `aeb5b39` (as ordered), 1.01 = `3edd0c8`.
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Claim under test: cutting the board at KiCad y = 62.00 (keep y >= 62) leaves the power-section GND
(U3/U2/Q1/...) joined to main GND only through J7's microSD shell (pad "9" lands).

Method: pcbnew 9.0.6 on `git show 3edd0c8:silkscreen_pcb.kicad_pcb` (copy in V_geom/). Every GND-net copper
shape per layer (pads via TransformShapeToPolygon, tracks, arcs, vias, zone filled polygons as saved, no refill)
-> union per layer -> clip y >= cut -> islands (outlines) -> F/B islands joined only through GND vias and
plated through-hole pads -> union-find components. Pads with equal numbers are NOT joined unless copper joins them.

## Results (appended as confirmed)

Raw output: `V_geom/out_3edd0c8.txt` (script `V_geom/gndgeom.py`). Runtime 2 s; fills read as saved (IsFilled=True).

### R1. Control: uncut board 3edd0c8 -> ONE component (method validated)
- GND copper collected: 150 GND pads, 52 GND tracks/arcs, 69 GND vias, 3 GND zone fills (main pour on F.Cu and B.Cu,
  small B.Cu pour x 46.7-49.1 y 122.5-124.9). 108 layer links (GND vias + GND PTH pads flashed on both layers).
- No no-net copper graphics; GND/other-net copper overlap 0.0000 mm2 on both layers (no shorts in the geometry).
- Uncut: all 150 GND pads (incl. all 10 J7 pad-"9"/pad-6 lands) in ONE copper component, 0 pad-less islands.

### R2. Cut keep y >= 62.00 (3edd0c8): CLAIM REPRODUCED
- 2 copper components hold GND pads (+2 pad-less floating slivers):
  - G1 main: 124 GND pads, 58 GND vias; F.Cu 9 islands 3397 mm2, B.Cu 27 islands 2401 mm2. Holds U4 (all 15 GND pads),
    J1 A1/A12/B1/B12, J2 8/17/S1/S2, U11 TP4056 (pads 1, 3 and all 8 EP "9" pads), C21.2, J7.6, J7 pad-9 lands #10 #11 #12 #13 #14 #15 #18.
  - G2 power: 16 GND pads, 6 GND vias: C25.1 C26.2 C3.2 C4.2 C6.2 H5.1(x3 PTH) J7.9#16 J7.9#17 Q1.3 R16.1 R51.2 R77.2 U2.1 U3.2.
    F.Cu 3 islands 225.7 mm2 bbox x 62.88-97.51 y 62.00-97.45; B.Cu 4 islands 171.5 mm2 bbox x 67.75-97.30 y 65.38-92.77.
  - pad-less slivers left floating: B.Cu 5.5 mm2 x 83.74-87.20 y 62.00-67.43; F.Cu 2.3 mm2 x 102.55-103.76 y 62.00-64.44.
  - GND pads removed with the cut-off strip: CR2 CR3 D3 D8 H1 J6 U8 (10 pads).
- The only footprint with GND pads in both components is J7 (split_parts check over all footprints).
- Battery path: J5 1=B-, 2=B+; Q1 1=B-, 3=GND -> Q1.3 is in G2, so the battery return enters GND in the power group.

### R3. J7 pad-"9" lands (J7 on B.Cu at (63.05,84.60), orient 0; board-local = library with y mirrored, all 9 lands matched at 0.00 mm)
| land | lib pos | size | board pos | component |
|---|---|---|---|---|
| #11 GCT | (-6.33,2) | 1.1x2.4 | (56.72,82.60) | G1 |
| #10 GCT | (-6.33,11) | 1.1x2.4 | (56.72,73.60) | G1 |
| #18 GCT | (9.82,2) | 1.1x2.4 | (72.87,82.60) | G1 |
| #17 GCT | (9.82,11) | 1.1x2.4 | (72.87,73.60) | **G2** |
| #13 SHOU HAN | (-6.15,1) | 1.3x1.6 | (56.90,83.60) | G1 |
| #12 SHOU HAN | (-6.15,10.6) | 1.3x2.3 | (56.90,74.00) | G1 |
| #15 SHOU HAN | (8.45,1) | 1.7x1.6 | (71.50,83.60) | G1 |
| #16 SHOU HAN | (9.35,10.6) | 1.3x2.3 | (72.40,74.00) | **G2** |
| #14 card-detect | (-4.95,0) | 0.7x1.6 | (58.10,84.60) | G1 |
- GCT MEM2075: 3 tabs on G1, 1 tab (9.82,11) on G2 -> its shell joins the groups (through that one tab).
- SHOU HAN TF PUSH: 3 tabs on G1, 1 tab (9.35,10.6) on G2 -> its shell joins the groups (through that one tab).

### R4. Cut keep y >= 61.86 (docs line): same split, same 16-pad G2, same J7 lands (#16, #17) in G2.

### R5. Where the copper joined them on the uncut board (all of it at y < 62)
- Crossing the line y = 62: G1 F.Cu pour at x 86.00-87.00 and G2 F.Cu pour at x 87.80-89.11 both run up into the same
  discarded top-right GND pour (F.Cu x 85.3-103.8 / B.Cu x 85.4-103.8, y 37.5-62, 8 GND vias/PTH).
- Sweep of the cut line (bisection, 4 um): U3.2 and U4 GND stay copper-joined for any cut at y <= 58.797 and split for
  y >= 58.800. The last joining copper is F.Cu at y ~58.80, x 86.56-92.75: the F.Cu pour loops over the top of whatever
  separates the two legs (x 87.0-87.8). No joining copper at y >= 62 (nor at y >= 58.8).
- G2 copper in detail (3edd0c8, cut 62): F.Cu #9 124.4 mm2 x 87.80-97.51 y 62.00-79.45 (the region the claim names),
  F.Cu #5 72.0 mm2 x 62.88-87.04 y 79.95-97.45, F.Cu #7 29.3 mm2 x 78.46-87.45 y 86.91-94.62; B.Cu #18 98.9 mm2 x 81.41-97.30
  y 65.38-89.00, B.Cu #17 67.6 mm2 x 67.75-82.92 y 71.25-89.02, B.Cu #12 3.5 mm2, B.Cu #21 1.5 mm2. So the isolated copper
  is about 397 mm2 on both layers. That is more than the single F.Cu region the claim names, but the pad list is identical.

### R6. Pre-change board 6871962 (same script, `V_geom/out_6871962.txt`)
- Uncut control: 1 component, all 150 GND pads.
- Cut 62: the same two groups. G2 has the same 16 GND pads and 7 GND vias (F.Cu 4 islands 226.9 mm2, B.Cu 4 islands 191.8 mm2).
  The same J7 lands (#16, #17) sit on G2. The split was already there before 3edd0c8.

### R7. What separates the two legs above the line (`V_geom/probe.py`)
- A P+ track on F.Cu (w 0.40) runs at x = 87.40 from (87.40,66.90) up to a P+ via at (87.40,59.30). That via drops to B.Cu
  and runs to F2 pad 2 (87.00,58.03). The F.Cu GND pour closes over the top of that via, at y ~58.8 (59.30 minus via radius
  and clearance). A 3V3 B.Cu track also runs there: (87.53,63.48)->(87.53,61.72)->(89.00,60.25).

### R8. Saved fills match the committed fab gerbers (`V_geom/gerbcmp.py`)
- I plotted F.Cu/B.Cu fresh from 3edd0c8 with kicad-cli (no refill) and compared them with zip_new. The region contours
  are identical at a 1 nm grid: F.Cu 15 contours / 10933 vertices / 3935.49 mm2, B.Cu 53 / 22201 / 2729.66 mm2.
  Flash and draw counts are identical too (F 302/440, B 783/1310). So the copper analysed here is the copper that was fabricated.
- J7 has no `duplicate_pad_numbers_are_jumpers` / `jumper_pad_groups`, in either board. KiCad therefore treats the pad-"9"
  lands as separate copper items.

### R9. Fix hint (suggestion only; the owner routes in the GUI)
- A tie on the same layer is blocked. The closest F.Cu approach is 0.19 mm, (73.61,88.97)/(73.48,89.12). The closest B.Cu
  approach is 0.13 mm, (84.49,92.76)/(84.41,92.85). Both gaps hold other-net copper.
- One GND stitching via is enough. On the kept part the G2 and G1 pours overlap on opposite layers: 33 mm2 with G2 on
  F.Cu over G1 on B.Cu, and 64 mm2 with G2 on B.Cu over G1 on F.Cu. At each spot below, a 0.6 mm via disk lies inside both
  pours, with no non-GND copper or hole within 0.5 mm, and the spot is outside every courtyard:
  - (86.48, 68.75): G2 B.Cu to G1 F.Cu, 3.3 mm from Q1, which carries the battery return. The area x 84.7-88.3 y 67.4-70.1 fits a 0.9 mm via.
  - (75.03, 74.64), also (75.11,74.74) or (74.55,72.48): G2 B.Cu to G1 F.Cu, just right of J7.
  - (80.56, 92.22): G2 F.Cu to G1 B.Cu.
  - These spots also work electrically but sit inside a courtyard: (91.94,63.39)/(89.17,63.35) under J5 (back),
    (72.59,73.78) under J7, (65.82,96.03) under U4, (90.69,78.79) under Q8.
- The G2 islands are already linked by 6 GND vias and H5, so one via joins them all. Use 2-3 vias spread out for current.
  Refill and run DRC after placing them. The vias do no harm on the uncut board.

### R10. Severity on a cut board
- On battery: the whole 3V3 load returns from G1 to the cell only through J7's shell and its single G2-side tab, then
  G2 -> Q1.3 -> Q1 -> B-. The load is the ESP32-S3 with Wi-Fi TX peaks of a few hundred mA, plus e-paper refresh. The tab is
  at board (72.87,73.60) for GCT or (72.40,74.00) for SHOU HAN.
- Charging: U11 TP4056 has its GND on G1 and PROG R6 = 4.7k, so about 0.26 A. That current returns B- -> Q1 -> G2 -> shell -> G1.
- On USB: the loads return to J1 directly inside G1. Only the U2/U3 ground currents and the return currents of the LDO
  in/out caps cross the shell. C4 22u (LDO_IN) and C6 22u (3V3) decouple against G2; C21 1u decouples against G1.
- With either socket fitted and soldered, the board works; it is not dead. The shell's resistance (a few to tens of mOhm)
  is fine electrically. The weak point is that one push-push socket tab joint is the only battery return.
- If J7 is not fitted, or that tab joint is open, G2 floats. Then the battery cannot run the board or be charged (its
  return is open), and U2/U3 lose their ground so 3V3 is not regulated. The board is dead or out of spec even on USB.
- Minor: after the cut, two pad-less slivers are left as unconnected copper. One is 5.5 mm2 on B.Cu, x 83.74-87.20
  y 62.00-67.43; the other is 2.3 mm2 on F.Cu, x 102.55-103.76 y 62.00-64.44.

## VERDICT: CONFIRMED
The claim reproduces exactly with independent copper geometry, at y = 62.00 and at 61.86, and on both 3edd0c8 and 6871962.
The only difference is the extent: the isolated GND copper is about 397 mm2 across 3 F.Cu and 4 B.Cu islands, not just
the F.Cu region x 87.8-97.5 y 62-79.5.

