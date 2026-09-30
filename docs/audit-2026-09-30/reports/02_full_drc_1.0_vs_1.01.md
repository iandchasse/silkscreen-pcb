# Full-board DRC: NEW (working copy) vs OLD (HEAD)

> Run on 2026-09-30, before commit `3edd0c8` existed: **HEAD / OLD / CONTROL = `6871962`** (design and production files
> identical to `aeb5b39`, the Rev 1.0 order) and **working copy / NEW / FIX = the change later committed as `3edd0c8`** (1.01).
> Evidence paths (`A_trim/`, `C_fab/`, `layout/` ...) are under [`../evidence/`](../evidence/), a local-only pack (git-ignored).

Status: complete

## Findings

### [info] Copies built and verified
- B_drc/new = working-copy files; B_drc/old = git HEAD files (git show). Libraries (KiCad/9.0/3rdparty) copied from working tree.
- Board copies match the pre-made new.kicad_pcb / old.kicad_pcb byte-for-byte after CR strip.
- .kicad_pro, .kicad_sch, fp-lib-table, sym-lib-table identical HEAD vs working copy (modulo CRLF); no sub-sheets; no .kicad_dru in repo. git diff --stat: only kicad_pcb, production zip, netlist.ipc changed.

### [info] Raw kicad-cli 9.0.6 DRC totals (--schematic-parity --severity-all, json)
- OLD (HEAD): 102 violations, 0 unconnected, 0 schematic parity
- NEW (working copy): 103 violations, 0 unconnected, 0 schematic parity
- kicad-cli 9.0.6 `pcb drc` has NO --refill-zones option ("Unknown argument: --refill-zones"); refill check done via pcbnew Python instead (see below).

### Diff OLD -> NEW (matched by type+severity+description+item descriptions)
- Per-type counts identical except track_dangling 4 -> 5.
- NEW-only: track_dangling (warning) "Track [3V3] on B.Cu, length 0.1414 mm" end at (101.001, 64.9), uuid 25537799-23f7-4da2-a910-f8d5a5c9f1c0 -- on the new 3V3 x3 bridge. Investigating geometry.
- J1 USB-C pad-pitch clearance pair relabel: OLD reported 2x (B8 <no net> vs B9 VBUS_PRE_FUSE), NEW reports 2x (B12 GND vs B9 VBUS_PRE_FUSE); clearance count 14 in both. Pre-existing footprint pitch issue (0.15 < Power 0.20), not caused by this change; checking J1 unchanged.
- No new clearance/short/unconnected/parity errors; 0 unconnected and 0 parity in both.

### [info] Copper change set (pcbnew diff OLD->NEW, B_drc/geo.out)
- 31 track/via items added, 19 removed; all on 3V3 / PWR_BUTTON / LED_SW / one GND via ((99.3,65.6) -> (98.6,67.4)). Matches the described change. No footprint placement changes; J1 pads identical (so the J1 clearance pair relabel is DRC reporting order, not a change).
- 17 new 3V3 B.Cu 0.25 mm segments. Includes a degenerate 0.001 mm segment (101.0,64.9)->(101.001,64.9) (uuid 157ac2d7) and the bridge ends as a T onto the middle of the split x=101.101 vertical at (101.101,65.0).

### [info] Clearance spot-check of new 3V3 copper (B.Cu) vs board rules
- Rules: 3V3 = Power (0.20), PWR_BUTTON = Default (0.15), LED_SW = SW (0.25), GND = Default (0.15). Required 3V3-to-other = 0.20 mm.
- Measured minimums (analytic seg/via distance; binary-searched SHAPE.Collide for pads and zone fill, 1 um resolution):
  PWR_BUTTON tracks 0.201 mm; PWR_BUTTON pad R62.2 0.202 mm; PWR_BUTTON via (83.08,69.40) 0.224 mm; GND via (99.1,63.9) 0.201 mm; UNUSED_GPIO_3 tracks 0.201 mm; GND B.Cu zone fill >= 0.200 mm (0.200-0.201) on every new segment; no overlap.
- LED_SW reroute is F.Cu only; new 3V3 is B.Cu only, so no same-layer interaction. All at rule minimum, none below; consistent with DRC reporting 0 new clearance errors.

### [warn] NEW-only DRC warning: dangling 3V3 track end at the x=101.101 T-junction
- pcbnew CONNECTIVITY_DATA.TestTrackEndpointDangling(uuid 25537799, (101.001,64.9)->(101.101,65.000)) = True at (101.101000, 65.000000) exactly: the bridge's last 0.141 mm segment ends mid-span on the split vertical 639462e8 ((101.101,64.6)->(101.101,68.5615)) instead of at a vertex. (JSON item pos (101.001,64.9) is just the track start.)
- Electrically harmless: the end point lies exactly on the vertical's centreline, copper overlaps fully, pcbnew unconnected count = 0, DRC unconnected = 0. It is a new, non-excluded warning, so "DRC is clean" is not literally true for warnings (the 4 pre-existing track_dangling are all in drc_exclusions; this one is not).
- Also cosmetic: degenerate 0.001 mm segment 157ac2d7 (101.0,64.9)->(101.001,64.9) not flagged by DRC. Tidy fix if wanted: end the bridge at (101.101,64.6) vertex (or split the vertical at 65.0), delete the 1 um stub; or exclude the warning.

### [info] Zone-fill freshness
- kicad-cli 9.0.6 lacks --refill-zones; used pcbnew ZONE_FILLER.Fill on B_drc/refill copy. Filled-polygon boolean XOR vs saved fill: 0 area change on all 3 zone-layers (GND F.Cu, GND B.Cu, small GND B.Cu zone). Unconnected before/after refill: 0/0. The committed fill is fresh.
- fabrication-toolkit-options.json has "AUTO FILL": true, so the plugin refilled before plotting; since refill == saved fill, the zip was plotted from the same copper as the saved board (timestamps checked below).
- Refilled-copy DRC: 104 vs 103 for NEW; the only differences are J1 USB-C pad-pair clearance entries, which also shuffle between runs on byte-identical copper (see J1 note). No change in unconnected (0) or any 3V3/PWR_BUTTON/LED_SW/GND item. Refill does not change the violation set in any real way.
- Timestamps: board saved 12:21:38; gerber TF.CreationDate 12:22:17 (drill maps 12:22:18); zip 12:22:19; netlist.ipc 12:22:18. Gerbers are KiCad 9.0.6, ProjectId rev 1.0. Consistent with "plotted ~40 s after save" and no later board save.

### [info] Non-excluded DRC (--severity-error --severity-warning; 7 exclusions in .kicad_pro honoured)
- OLD: 96 (12 clearance err, 0 track_dangling). NEW: 96 (11 clearance err, 1 track_dangling = the new 3V3 T-junction end). 0 unconnected, 0 parity in both.
- The 11-15 clearance errors are all J1 USB-C PTH pad pitch (VBUS_PRE_FUSE Power 0.20 rule vs 0.15 actual) or the 3 excluded ones; J1 pads are identical OLD vs NEW and the reported pad pairs vary run-to-run (multi-threaded DRC dedup), so the count jitter (11/12/14/15) is noise, not caused by the change. Pre-existing in HEAD, not excluded -> "DRC is clean" is only true as "no new errors".

### [info] Fab zip copper == saved board copper
- kicad-cli pcb export gerbers -l F.Cu,B.Cu of B_drc/new vs production zip gerbers (G04 comments / X2 attribute lines removed, CRLF normalised, lines sorted to ignore draw order):
  F_Cu.gtl: identical. B_Cu.gbl: identical coordinates; only 3 redundant aperture-select lines (D10*, D79* x2) differ, from draw order. The zip B_Cu contains the new 3V3 bridge (X101001000Y-64900000 ... X101101000Y-65000000).
- (--board-plot-params was not usable: the board's saved plot params are PDF, it wrote PDFs.)

## Verdict
PASS (no blocker). No new error-severity clearance/short/unconnected/parity issue from the change; 0 unconnected, 0 parity in OLD and NEW; new 3V3 copper sits at >= 0.200 mm (the Power rule) from PWR_BUTTON, GND via, GND fill and UNUSED_GPIO_3. One new non-excluded warning (dangling 3V3 end at (101.101,65.0) T-junction), cosmetic. Fill is fresh; zip plotted from the same copper.
"DRC is clean" holds as "no new errors"; literally, both HEAD and NEW carry ~11-12 non-excluded J1 USB-C pad-pitch clearance errors (pre-existing, unchanged) and NEW adds 1 warning.

