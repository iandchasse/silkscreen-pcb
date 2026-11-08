# Lens A: BQ21040 (U11) IC and power path

Auditor: lens A (independent). Sources: TI SLUSCE2D text/pdf (page numbers = PDF pages), SLUSCE2C (LCSC copy),
`extract/block_pins_head.txt`, `extract/netlist_head.xml`, `extract/pcb_block_summary.txt`, `easyeda/pads_summary.txt`,
`head/fabrication/part_fields.csv`, BSS138 clone sheet. Derived first; `claims.md` and the design notes' charger sections
read only afterwards (see "Comparison with the design's claims").

## 1. Verdict

The new charger is wired correctly and is safe for a single 500 mAh LiPo on USB-C or USB-A. Every pin matches TI's
datasheet. It charges at about 115 mA (104-127 mA), stops at 4.16-4.23 V, and stops again at about 10-14 mA. A missing,
reversed or 0 V cell leaves it switched off. It survives up to 30 V on the input and stops charging above 6.6 V. It stays
cool. Nothing here should stop an order. Three things deserve a bench check on the first boards. (1) Anything plugged into
the expansion port's battery pin that draws more than ~10 mA while on USB makes the charger's 10-hour safety timer run out.
(2) Recovering a cell that the board's own protection has cut off may stutter, depending on the threshold of one small
transistor (Q2). (3) The board-mounted thermistor stops charging above about 41 C at the board, which a warm closed case
might reach. The firmware's status-voltage thresholds should leave room for the charger's leakage.

## 2. Findings

| ID | Sev | Claim | Evidence | How confirmed | Smallest fix | Conf. |
|---|---|---|---|---|---|---|

(rows appended below as confirmed)

### Working notes (derivations, appended as confirmed)

**Pin map (Q1).** Datasheet p.3 DBV top view and Pin Functions: 1 TS, 2 OUT, 3 CHG (open drain), 4 ISET, 5 GND, 6 VIN.
Netlist libpart `Battery_Management:BQ21040DBV` pins: 1 TS, 2 OUT, 3 ~CHG (open_collector), 4 ISET, 5 GND, 6 VIN; nets:
1 TS, 2 P+, 3 CHRG, 4 Net-(U11-ISET) -> R6 -> GND, 5 GND, 6 USB_VBUS. JLC/EasyEDA land (C202311): pads 1-3 on one side,
4-6 on the other, 6 opposite 1, standard SOT-23-6 ring. All agree. PASS.

**C vs D revision (Q-intro).** Text diff of SLUSCE2C vs SLUSCE2D (headers stripped): the only technical changes are the ESD
ratings (HBM 1000 -> 2000 V, CDM 250 -> 500 V, p.4) plus a re-dated orderable addendum (2017 -> 10-Nov-2025). No electrical,
timing, pinout or application change. The B -> C history (p.2) matters more: it changed the TS pull-down to 237 k, RTS max
to 258 k, and *deleted* "The bq21040 does not have a safety timer" — so the part does have the 30 min / 10 h timers (p.15).

**Charge parameters (Q3).** ISET = KISET/RISET (p.5, p.13). R6 = 4.7 k 1 %: typ 540/4700 = 115 mA; KISET 490-590 (60 mA-1 A
band) and R +-1 % give 104-127 mA. Pre-charge 18-22 % = 19-28 mA below VLOWV 2.4-2.6 V (on OUT). Termination 9-11 % of
ICHG = 9.3-14 mA (about C/45 for 500 mAh: a genuinely full cell). VOUT(REG) 4.16-4.23 V (p.5). Recharge VRCH = VREG -70..-120 mV
(about 4.08-4.16 V), CHG stays off on refresh. Pre-charge timer 30 min, fast-charge timer 10 h, clock halves in thermal
regulation / DPM (p.15). Termination threshold raised ~14 % for the first minute (p.15). OUT < 0.8 V: short-circuit mode,
10-20 mA source (p.5). RISET short detection < 500 ohm: 4.7 k is far away. Cell assumption: 500 mAh LiPo pouch, 4.20 V
+-50 mV max charge, std charge 0.2-0.5 C, 0.1 C below 3.0 V typical maker spec. 115 mA = 0.23 C: inside any such spec;
CC time ~3.5-4 h, full charge ~5-6 h, well inside 10 h with no load.

**Limits (Q2).** IN abs max 30 V, operating 4.45-6.45 V, OVP 6.5-6.8 V with 113 us blanking: USB 5 V and any hot-plug ring
(CR1 SMF6.5CA clamps ~11 V; R84 damps C2) are far inside 30 V. OUT abs max 7 V vs P+ <= 4.23 V. TS abs max 7 V; TS self-clamps
at 1.8-2.0 V; Q2 drain/R82/TH1/C38 never drive it above that. ISET 7 V: only R6. CHG 7 V / 15 mA sink: sees <= 3.3 V through
510 k (< 7 uA). All PASS.

**Capacitors (Q4).** Datasheet p.3: IN and OUT each "expected range 1 uF to 10 uF" ceramic; Fig. 10 uses 1 uF each; p.18 says
values may go up for pulsed loads. CTS optional 0.22 uF is in the TYP column (word positions on p.6: value at x=460 = TYP).
Fitted: IN = C25 1 uF direct + C2 10 uF/25 V behind R84 1 ohm (an ESR-damped bulk; the direct ceramic is 1 uF = TI's value);
OUT = C3 10 uF/10 V X5R 0603 (CL10A106KP8NNNC, ~5-6 uF at 4.2 V bias) + C26 1 uF = ~6-7 uF effective, and the cell is in
parallel. No max ESR or max COUT is specified; the battery-detect routine (25 ms windows, 7-10 mA sink, 400 mV step) only needs
dV = I t / C: 10 mA x 25 ms / 11 uF = 23 V >> 0.4 V, so absent-cell detection still works. C38 0.22 uF = CTS typ. PASS.
Layout NOTE: C26/C3 are ~6-7 mm from U11 pin 2, C25 ~6 mm from pin 6 (pcb_block_summary poses); TI asks for "as close as
possible". Linear charger, low di/dt: NOTE only.

**P+ loads (Q6).** P+ members (netlist): U11.2, C3, C26, R12 (1 M + R10 1 M to GND: 2.1 uA), R83 100 ohm -> DW01A VCC (~3-6 uA),
U2.6 TPS2116 VIN2 (unselected while USB_VBUS present, since PR1 = 5 V x 100k/400k = 1.25 V; sub-uA), Q8 (AO3401A, gate = GND,
source P+, drain -> R27 0 ohm -> Q3 drain; Q3 source = B+): the back-to-back P-FET pair is the cell path itself, F2 -> J6.12.
With USB present the system runs from VIN1, so the DC load on P+ is ~10 uA << ITERM min 9.3 mA: termination, the timers and
CC/CV are unaffected. Without USB, U11's OUT leakage is <= 1 uA (IOUT(PDWN), p.5). Charging-path drop from P+ to the cell
(Q8 + Q3 + FS8205A + R85||R86 + JST): roughly 0.2-0.3 ohm -> ~30 mV at 115 mA, ~3 mV at ITERM: CV on P+ still ends at the cell's
4.2 V, just a few minutes later. PASS. The one load that can break this is an accessory on J6 pin 12 (finding A-01).

**Protection interaction (Q7).** U5 DW01A: VCC from P+ (R83), VSS = B-; OD (pin 1) -> Q1 G1 with S1 = B- (discharge FET),
OC (pin 3) -> Q1 G2 with S2 = /B-_SENSE -> R85||R86 (50 mohm) -> GND (charge FET). Charge current path: P+ -> Q8 -> Q3 -> B+ ->
cell -> B- -> FET1 -> FET2 -> sense -> GND. So the node the charger regulates is P+ = Vcell + I x (high-side pair) + I x (low-side
pair + 50 mohm). DW01A sees P+ - B-, i.e. *below* P+ by the low-side drop: its overcharge detect (DW01A family ~4.25-4.30 V min,
not in pack) sits above VOUT(REG) max 4.23 V; Rev 1.0's TP4056 (4.158-4.242 V) had the same or less margin and works. In
over-discharge lockout (FET1 off) charge current flows through FET1's body diode: P+ = Vcell + ~0.6-0.75 V, so U11 judges
pre-charge vs fast charge on Vcell + 0.7 V: cells from ~1.8 V up get the 104-127 mA fast-charge current (0.21-0.25 C), below that
19-28 mA. Rev 1.0's TP4056 had the same offset. 0.25 C into a 1.8-2.5 V cell is gentle but above the usual 0.1 C pre-charge
spec (finding A-04). DW01A releases OD once the cell recovers, then P+ = Vcell again.

**Missing cell / removal (Q3, Q7).** Q9 (gate from R79 1 M / R80 10 M across B+..B-, source B-) pulls /DET_NODE low when a cell
is present; with no cell R81 100 k (from USB_VBUS) turns Q2 on and Q2 holds TS < VTS-EN (88 mV) = chip disabled (p.6, p.12 flow:
no output until VTS > VEN). Power-up with no cell: P+ never rises, so B+ is never back-fed, Q9 stays off: stable "disabled", P+ = 0,
BAT_MONIT = 0. Good. Cell removed during charge with USB still in: P+ is held by U11 (4.2 V CV), Q8 (gate GND) and Q3's body diode
back-feed B+, the DW01A (powered from P+) keeps both FETs on so B- ~ GND, so Q9 still sees ~3.5-3.8 V and stays on: the detector
does NOT notice the removal. U11 then runs its own battery-detect routine (p.15-16, Fig. 21, TS held in the active region by TH1):
P+ toggles ~3.8 <-> 4.2 V every ~25 ms, CHG high-Z. Harmless (system on VIN1); firmware reading BAT_MONIT sees ~4 V and may show a
"full" battery until USB is unplugged (finding A-05, NOTE). Cell inserted later: detect routine finds it, charge restarts.
Flat cell: Q9 needs Vgs >= Vth (clone sheet: 0.8 / 1.2 / 1.6 V at 250 uA) = 0.909 x Vcell, so cells below ~0.9-1.8 V (typ ~1.3 V)
are not charged at all. For a cell that has sat below the DW01A's 2.4 V OD threshold long enough to reach ~1.5 V, refusing to
charge is arguably the safe behaviour. NOTE.

**Thermal (Q5).** P = (VIN - VOUT) x IOUT (p.23 eq. 8). RθJA 130.8 C/W is the JEDEC high-K figure (p.4); a SOT-23-6 on this
board is more likely 150-200 C/W. Typical (5.0 V, cell 3.4 V per TI's p.23 guidance, 115 mA): 0.18 W -> +24..37 C. Worst USB
(5.25 V, OUT 2.5 V just above VLOWV, 127 mA): 0.35 W -> +46..70 C. Worst adapter still below OVP (6.45 V): 0.50 W -> +65..100 C.
Inside a closed case at ~40 C: TJ ~65-75 C typical, ~110 C worst on USB; only a high, unregulated adapter reaches TJ(REG) 125 C,
where the IC folds the current back and halves the timer clock (p.8, p.15); shutdown 155 C. Safe in all cases. The practical
limit is TH1 (finding A-03), not U11.

**TS window (Q2/Q3).** TS = 50 uA (48-53) into TH1 || R82. Hot trip VTS-45C 0.26-0.29 V -> TH1 4.91-6.04 k in parallel with 200 k
-> TH1 = 5.03-6.23 k -> **38.0-44.2 C (typ 41.0 C)** with B25/50 = 3380. Cold trip 1.22-1.28 V -> 23.0-26.7 k -> TH1 26.0-30.8 k ->
**-1.9..+1.8 C (typ -0.3 C)**. TH1 open: R82 alone holds TS in the INTC fold-back band (~1.45-1.5 V at ~5-7 uA, p.5/p.6), above
the cold trip and below VTTDM 1.55 V -> "cold", no charge (safe; 200 k does what TI's 237 k does). TH1 shorted / Q2 on: TS < 88 mV
-> disabled. C38 = CTS typ 0.22 uF; tau = 9.5 k x 0.22 uF = 2 ms << 30 ms TS deglitch. PASS.

**CHG / USB_STAT (Q8).** CHG: open drain, 7 V abs max, 15 mA abs max sink, VOL 0.4 V @ 5 mA, leakage <= 1 uA @ 5 V (p.3, p.6).
Below UVLO "all the terminals are high impedance" (p.10, 8.3.1); abs max is referenced to VSS only, so no IN-referenced clamp
is implied, and USB_STAT cannot back-feed USB_VBUS through CHG. Through 510 k from a 3.3 V node the pin sees < 7 uA and <= 3.3 V.
Ladder levels (R70 1 M to 3V3, R17 2 M to U2 ST, R67 510 k to CHG): open 3.30 V; CHG low 1.11 V; ST low 2.20 V; both 0.95 V.
A worst-case 1 uA CHG leakage lifts nothing but pulls the node down by up to ~0.67 V (Thevenin 667 k): 3.30 -> 2.63 V, 2.20 ->
1.53 V; still separable from 1.11 / 0.95 if firmware thresholds sit midway (finding A-06). CHG semantics differ from TP4056:
low only during the *first* charge after power-up; high-Z on refresh charges, sleep, OVP, done, no cell and timer fault (p.13,
Table 1). Rev 1.0's STDBY ("full") input to the ladder (R71) is gone.

## 2b. Findings table (final)

No BLOCKER and no MAJOR found. 4 MINOR, 6 NOTE.

| ID | Sev | Claim | Evidence | How confirmed | Smallest fix | Conf. |
|---|---|---|---|---|---|---|
| A-01 | MINOR (MAJOR for any accessory that loads pin 12) | A continuous load on `J6` pin 12 above ITERM (~9-14 mA) while on USB stops charge from ever terminating. After 10 h (up to 20 h with the clock slowed) the safety timer ends charging. From then on the accessory runs off the cell even though USB is plugged in. The datasheet lists only "disable the IC, cycle power, or TTDM" as timer resets, so it is unclear whether the VRCH refresh restarts charging. This is new in 1.03: the TP4056 had no timer. No current accessory uses pin 12 (the light attachment deliberately leaves it unconnected), but HARDWARE.md J6 §4 tells heavier accessories to take power from pin 12. | Datasheet p.1 and p.17: a system load is fine as long as it does not keep the battery from charging fully within the 10 h timer. p.15 §8.4.7: timer resets. p.5: %TERM 9-11 %. Netlist: F2.2 on P+, F2.1 to J6.12. HARDWARE.md lines 1445-1460. | Two independent datasheet passages (load rule, timer/reset rule) plus the netlist path. Ambiguity remains between p.10 §8.3.4 (VRCH starts a new cycle) and p.15. | Docs: in HARDWARE.md J6 §3/§4, limit the average pin-12 load while charging to about 5 mA, or say that the charge stops after 10 h. Optionally firmware: if USB is present, CHG is off and P+ < 4.0 V, warn "unplug and replug". | High (mechanism), medium (whether it restarts) |
| A-02 | MINOR | When the board DW01A is in over-discharge lockout (FET1 off), charge current returns through FET1's body diode, so `B-` sits about 0.6-0.75 V above GND. `Q9`'s source is on `B-`, so `/DET_NODE`, and with it `Q2`'s gate, sits at that level instead of about 0 V. The BSS138 clone's VGS(th) minimum is 0.8 V at 250 uA. A low-threshold `Q2` can sink the ~20 uA that pulls `TS` (50 uA into 9.5 k) under the 0.275 V hot trip, or under 88 mV. Charging then stutters (stop -> `B-` falls -> restart) until the cell climbs out of lockout (~3 V). The same pattern gated the TP4056 CE on Rev 1.0, so it is not new. Recovery from board-level OD has probably never been exercised. | Netlist: Q9.2 = B-, Q9.3 = /DET_NODE = Q2.1, Q2.3 = TS; U5.1 OD -> Q1.6 (G1), Q1.1 (S1) = B-, so FET1 is the discharge FET. Clone sheet: VGS(th) 0.8/1.2/1.6 V. TS: 48-53 uA, VTS-45C 0.26-0.29 V, VTS-EN 80-96 mV (p.5-6). | Method 1: netlist topology and FET orientation. Method 2: DW01A charger-detect logic, which relies on exactly this negative CS-VSS offset. The magnitude depends on subthreshold current and is not verified. | Evaluate taking `Q9`'s source to GND instead of `B-` (no added parts; re-check the reversed-cell case). Or put a 2-resistor divider on `Q2`'s gate (e.g. 100 k series + 100 k to GND: high 2.5 V, low <= 0.4 V). Bench check first (section 4). | Medium-low |
| A-03 | MINOR | The board-mounted NTC sets a hot cut at `TH1` of 38.0-44.2 C (typ 41.0 C), resuming about 2 C cooler. `TH1` is 7.1 mm from `U11` (0.18 W typical, 0.35 W worst) and 3 mm from `F1`, inside a closed case. In a warm room with the radio active, charging may pause or cycle. Safe, but slow. The design documents 0-41 C. | My calculation (section "TS window") matches claim C3. Poses in pcb_block_summary: U11 (84.10, 94.80), TH1 (91.20, 94.15). | Computed from the datasheet thresholds and the NTC B-value. The case temperature is unverified. | None required. If the bench test shows pausing, move `TH1` away from `U11`/`F1` toward the cell, or accept it. | Medium |
| A-04 | NOTE | In DW01A OD lockout, U11 sees Vcell + ~0.7 V, so cells from ~1.8 V up get 104-127 mA (0.21-0.25 C for 500 mAh) rather than the 19-28 mA pre-charge. The same applied on Rev 1.0. | p.5 VLOWV 2.4-2.6 V on OUT; topology as in A-02. | Topology. | Check that the chosen cell's datasheet allows about 0.25 C below 3.0 V (most pouch cells specify 0.1 C, a few 0.2 C); accept. | High |
| A-05 | NOTE | Cell pulled while USB is in: the detector stays released (P+ back-feeds B+ through Q8/Q3, and the DW01A keeps B- at GND). U11 runs its battery-detect routine, cycling P+ between 3.8 and 4.2 V, and BAT_MONIT shows about 4 V. Matches claim C9. | p.15-16, Fig. 9, Fig. 21. | Topology plus datasheet flow. | Firmware: treat "USB present, CHG off, BAT_MONIT jittering around 4.0 V" as "no cell / unknown". | High |
| A-06 | MINOR | The CHG leakage limit of 1 uA (at 5 V, p.6) flows through the ladder's ~667 k Thevenin resistance. On USB with CHG off it can pull USB_STAT from 3.30 V down to about 2.63 V, close to the 2.20 V "on battery" level. A midway threshold of 2.75 V would then misread it. Typical leakage is nA. | Ladder from the netlist: R70 1 M / 3V3, R17 2 M / ST, R67 510 k / CHG. | Arithmetic only. | Firmware: split 3.30 from 2.20 at about 2.45 V, not at the midpoint, and cross-check with BAT_MONIT. | Medium |
| A-07 | NOTE | SLUSCE2C -> D changes only the ESD ratings (HBM 2 kV, CDM 500 V) and the addendum. BQ21040DBVR is Active / Production (addendum dated 10-Nov-2025). B -> C (already in both) is where the timer statement and the 237 k TS value changed. | Text diff, p.2, p.4, addendum. | diff | None | High |
| A-08 | NOTE | Claim C11 (0.28 W, +37 C) uses OUT = 3.0 V and the JEDEC 131 C/W. The fast-charge worst case starts at VLOWV 2.5 V: (5.25 - 2.5) x 0.127 = 0.35 W, and on this board RθJA is probably 150-200 C/W, giving +46..70 C. Still below the 125 C regulation point on USB. An unregulated 6.45 V adapter (0.5 W) can reach thermal regulation, which is benign. | p.4, p.23 eq. 8. | Arithmetic. | Docs wording only. | High |
| A-09 | NOTE | Claim C10 says no 1 uF was added at VIN. The net does have a direct 1 uF ceramic (`C25`, ~6 mm from pin 6), plus `C2` behind `R84`, which meets the p.3 "1 uF to 10 uF" range. Output: `C3` (10 uF/10 V X5R, ~5-6 uF at 4.2 V) plus `C26` 1 uF; the datasheet gives no maximum, and battery detect still works. Both cap groups are ~6 mm from the IC (TI says "as close as possible"). Acceptable for a linear charger. | Netlist; part_fields; p.3, p.18, p.22. | Netlist plus layout poses. | None | High |
| A-10 | NOTE | A pack whose own PCM has latched (0 V at J5), or a bare cell below ~0.9-1.8 V, is never charged: Q9 needs VGS(th)/0.909. This is deliberate and documented (HARDWARE.md ~line 453, ~1622). | Clone sheet; netlist. | Arithmetic. | None (user documentation exists). | High |

## 3. Checked and OK

| Item | Result |
|---|---|
| Pin map (Q1): datasheet DBV pins vs symbol vs netlist vs JLC land | All six agree (TS, OUT=P+, CHG, ISET=R6, GND, VIN=USB_VBUS); `~CHG` typed open_collector |
| IN limits (30 V abs, 4.45-6.45 V op, OVP 6.5-6.8 V) vs USB 5 V, hot-plug ring, CR1 clamp | Wide margin; U2 (6 V), not U11, is the limiting part on VBUS |
| OUT/TS/ISET/CHG abs max 7 V | Max seen: 4.23 / 2.0 (self-clamp) / ~1.2 / 3.3 V |
| Charge current | 115 mA typ, 104-127 mA (KISET 490-590, R6 1 %); claim C2 agrees |
| Pre-charge / termination / VLOWV / VRCH | 19-28 mA below 2.4-2.6 V; 9.3-14 mA; recharge at VREG -70..-120 mV |
| Regulation vs cell and DW01A | 4.16-4.23 V, under a 4.20 +/- 0.05 V cell max; DW01A sees P+ minus the low-side drop; no worse than Rev 1.0's TP4056 (max 4.242 V) |
| Timers | 30 min pre-charge (enough), 10 h fast charge vs ~5-6 h for 500 mAh with no load |
| ISET short detection (< 500 ohm) | 4.7 k: not triggered |
| TS window, open/short TH1, TTDM avoidance with 200 k | Matches claims C3/C4/C5 (76 mV disable = 88 mV minus 12 mV hysteresis) |
| P+ DC loads with USB in | ~10 uA total << ITERM; no effect on CC/CV/termination/timer |
| OUT leakage on battery | <= 1 uA (IOUT(PDWN)) |
| Missing cell at power-up | U11 held disabled by Q2; P+ stays 0 V; stable |
| Reverse cell | Q8's body diode isolates P+ (cannot go below -0.3 V); Q9 off -> U11 disabled |
| CHG with IN absent | High-Z per p.10 §8.3.1; no IN-referenced clamp implied by the abs-max table; claim C8 agrees |
| CTS = 0.22 uF | TYP column (pdf word x-positions) |
| Thermal | Safe in all USB cases; thermal regulation and shutdown cover bad adapters |

## 4. Could not verify on paper

| Question | Measurement that settles it |
|---|---|
| A-02: does Q2 conduct when the DW01A is in OD? | First article: feed J5 from a current-limited supply at 2.2 V so the DW01A latches OD, plug in USB, then log B- to GND, Q2 gate, TS and the charge current for 10 min. Pass: TS stays at about 0.4-0.5 V and the current is steady. |
| A-03: TH1 temperature in the closed case while charging | Closed case at 25 and 30 C room temperature, flat cell, Wi-Fi on: log TS (or TH1 resistance) and charge current. Note whether TS falls below ~0.29 V. |
| A-01: after a 10 h timeout with a P+ load, does VRCH restart charging? | Bench: 30 mA load on J6.12 plus a cell on USB for > 10 h (or a cell emulator); watch CHG and the current after the timeout. |
| Timer behaviour during a TS fault (paused or still counting) | The datasheet is silent; the same long bench run with TH1 warmed. |
| Board RθJA of U11 on this layout | Thermocouple on U11 during a fast charge from 3.0 V at 5.25 V input. |
| The actual CHG leakage on parts as built | Read USB_STAT on USB with a full cell (CHG off); expect about 3.3 V. |
| JLC CPL rotation of U11 (claim C15) | JLC placement preview, outside this lens. |

## 5. Comparison with the design's claims (read after deriving)

C1, C2, C3, C4, C5, C6, C8, C9, C12, C13, C16 agree with my derivation. C7: the ladder levels agree, but the leakage
margin is not discussed (A-06). C10: wording; `C25` 1 uF is on the net (A-09). C11: the optimistic input point, but the same
conclusion (A-08). C14: "TH1 reads 1-3 C above the cell" is an estimate, untestable on paper (A-03). C15: not in this lens.
Not covered by any claim: the pin-12 load vs the 10 h timer (A-01) and the B- offset at Q2's gate in DW01A lockout (A-02).
