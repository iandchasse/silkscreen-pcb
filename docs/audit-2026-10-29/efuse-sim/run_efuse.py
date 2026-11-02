"""Latching electronic fuse on the frontlight boost feed (LDO_IN -> U10 VIN), LTspice study.

Case 1 (docs/BOARD_FAILURES.md) ended with U10's low-side switch shorted SW to GND at about 7 ohm. Nothing on the
boost branch limits current below F1's 1 A hold, and no PTC can guarantee a trip on such a fault from a 3.4-3.7 V cell
(section 6.4). This deck studies a discrete latching e-fuse that needs no GPIO and no BGA part:

    LDO_IN --Rs--+--[M1 AO3401A, S->D]-- LED_VIN (C12, L2, U10 VIN)
                 |
     Q3 (PNP, E = LDO_IN, B = M1 source through Rb3) senses I*Rs; its collector charges Ct through Rt (delay).
     Ct/Rtb sit on Q2's base (NPN). Q2 pulls Q1's base (PNP, E = LDO_IN) down through Rc2; Q1 pulls M1's gate up
     to LDO_IN, turning M1 off. Rf from the gate back to Q2's base holds the latch until LDO_IN falls below ~1 V.
     Rb1/Cb1 hold Q1 off and Rg/Cg hold the gate low (M1 on) at power-up and across supply steps.

Needs LTspice (batch mode); decks and logs go under ./out (git-ignored), results to results_<group>.json.
The 'limiter' group runs the 4-part linear current limiter instead (L22/L27/L33: Rs, M1, Q3 with its collector on
the gate, Rg; no latch), see docs/audit-2026-10-29/BOOST_LIMITER.md. Light starts there also use an energy-based
model: the start current flows until e_st joules have gone into the boost, and that progress survives a UVLO restart.
Usage:  python run_efuse.py threshold | normal | nuisance | fault | release | baseline | variants | m2 | limiter | all

Models: AO3401A as the repo's datasheet-fitted VDMOS (docs/audit-2026-10-15/sch2-sim); MMBT3904/MMBT3906 as the NXP
2N3904/2N3906 parameters from LTspice's standard.bjt with IS scaled for V_BE spread ('lo' = IS x3, 'hi' = IS /3,
about -/+28 mV), plus the NXP BC847B/BC857B set as a second family. U10 is behavioural: UVLO 2.40 V rising /
2.11 V falling (datasheet 2.3-2.49 / 2.05-2.17), body diodes on SW, 280 uA enabled quiescent, and an averaged input
current drawn at the VIN pin: a start-up envelope (constant current I_st for t_st after enable, the soft-start switch
limit being 0.8 A peak) followed by a constant input power. Sources: LDO_IN behind a 0.5 ohm path (cell, Q3/Q8, F2, U2 or cable, F1, U2), 10 uF effective C4 and a
40 mA 3V3 load; TPS2116 soft-start 1.3 ms (battery) / 1.7 ms (USB) from 0 V and an 8 us switchover between supplies.
Not a device qualification: see docs/audit-2026-10-29/BOOST_EFUSE.md for what it does not cover.
"""
import concurrent.futures as cf
import json, os, pathlib, re, subprocess, sys

EXE = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe'
HERE = pathlib.Path(__file__).parent
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)

# Design A (threshold ~0.25 A) and design B (~0.15 A); everything but Rs is shared.
BASE = dict(RB3='1k', RT='100k', CT='100n', RTB='100k', RF='100k', RG='1Meg', CG='10n', RB1='1Meg', CB1='1n',
            RC2='220k')
DESIGNS = {'A': dict(BASE, RS='2.0'), 'B': dict(BASE, RS='3.3'),
           # longer delay (Ct 470 nF) to ride through light start-up; M = middle sense resistor
           'A2': dict(BASE, RS='2.0', CT='470n'), 'M2': dict(BASE, RS='2.7', CT='470n'),
           'B2': dict(BASE, RS='3.3', CT='470n'),
           # 4-part linear current limiter: Rs, M1, Q3 (collector straight to the gate), Rg; no latch
           'L22': dict(topo='limit', RS='2.2', RG='1Meg'), 'L27': dict(topo='limit', RS='2.7', RG='1Meg'),
           'L33': dict(topo='limit', RS='3.3', RG='1Meg')}

BJT = {  # name: (NPN params, PNP params)
    'nom': ('NPN(IS={IS} VAF=100 Bf=300 IKF=0.4 XTB=1.5 BR=4 CJC=4E-12 CJE=8E-12 RB=20 RC=0.1 RE=0.1 TR=250E-9 TF=350E-12 ITF=1 VTF=2 XTF=3)',
            'PNP(IS={IS} VAF=100 BF=200 IKF=0.4 XTB=1.5 BR=4 CJC=4.5E-12 CJE=10E-12 RB=20 RC=0.1 RE=0.1 TR=250E-9 TF=350E-12 ITF=1 VTF=2 XTF=3)'),
    'bc': ('NPN(IS=1.822E-14 NF=0.9932 ISE=2.894E-16 NE=1.4 BF=324.4 IKF=0.109 VAF=82 NR=0.9931 ISC=9.982E-12 NC=1.763 BR=8.29 IKR=0.09 VAR=17.9 RB=10 IRB=5.00E-06 RBM=5 RE=0.649 RC=0.7014 XTB=0 EG=1.11 XTI=3 CJE=1.244E-11 VJE=0.7579 MJE=0.3656 TF=4.908E-10 XTF=9.51 VTF=2.927 ITF=0.3131 CJC=3.347E-12 VJC=0.5463 MJC=0.391 XCJC=0.6193 TR=9.00E-08 FC=0.979)',
           'PNP(IS=2.014E-14 NF=0.9974 ISE=6.578E-15 NE=1.45 BF=315.3 IKF=0.079 VAF=39.15 NR=0.9952 ISC=1.633E-14 NC=1.15 BR=8.68 IKR=0.09 VAR=9.5 RB=10 IRB=5.00E-06 RBM=5.00E-06 RE=0.663 RC=0.718 CJE=1.135E-11 VJE=0.7071 MJE=0.3808 TF=6.546E-10 XTF=5.387 VTF=6.245 ITF=0.2108 CJC=6.395E-12 VJC=0.4951 MJC=0.44 XCJC=0.6288 TR=5.50E-08 XTB=0 XTI=3 EG=1.11 FC=0.9059)'),
}
IS_SCALE = {'nom': 1.0, 'lo': 3.0, 'hi': 1 / 3}

MODELS = [
    # AO3401A from the repo's SCH-2 deck (datasheet fit, C15127)
    '.model P_AO3401A VDMOS(pchan Vto=-0.9 Kp=13.9 Rd=.022 Rs=.018 Rg=7.8 Cgdmin=55p Cgdmax=300p Cgs=590p Cjo=200p M=.5 Vj=.7 Is=1n Rb=.1)',
    '.model DBODY D(Is=1e-12 N=1.2 Rs=0.3 Cjo=50p)',
    '.model SWM SW(Ron=1m Roff=1G Vt=0.5 Vh=0)',
]

P_LED_IN = 0.235  # W at 100 % duty: 15 V x 13.3 mA / 0.85


def bjt_models(variant):
    fam, scale = ('bc', 1.0) if variant == 'bc' else ('nom', IS_SCALE[variant])
    n, p = BJT[fam]
    if fam == 'nom':
        n, p = n.replace('{IS}', f'{1e-14 * scale:.4g}'), p.replace('{IS}', f'{1e-14 * scale:.4g}')
    return [f'.model QN {n}', f'.model QP {p}']


def pwl(points):
    return 'PWL(' + ' '.join(f'{t:.9g} {v:.6g}' for t, v in points) + ')'


def deck(name, src, tend, design='A', fuse=True, rpath=0.5, ild=0.04, light=None, fault=None, iramp=None, temp=25,
         bjt='nom', t_ev=0.0, maxstep='2u'):
    """src: PWL points of the ideal source behind rpath. light: dict(windows=[(t_on, t_off)], ist, tst, duty).
    fault: dict(node, r, tf, tc=None). iramp: (t0, t1, i1) slow extra load on LED_VIN for threshold finding."""
    d = [f'* {name}', f'.temp {temp}', f'Vsrc src 0 {pwl(src)}', f'Rpath src vin {rpath}',
         'C4 vin c4m 10u', 'Rc4 c4m 0 5m', f'B3v3 vin 0 I={ild}*limit((V(vin)-2.5)/0.5,0,1)']
    if fuse and DESIGNS[design].get('topo') == 'limit':
        p = DESIGNS[design]
        d += [f"Rs vin s {p['RS']}", 'M1 d g s P_AO3401A', 'Q3 g s vin QP', f"Rg g 0 {p['RG']}",
              'Bgs gs 0 V=V(g)-V(s)']
        n2 = 's'
    elif fuse:
        p = DESIGNS[design]
        d += [f"Rs vin s {p['RS']}", 'M1 d g s P_AO3401A', f"Rb3 s b3 {p['RB3']}", 'Q3 c3 b3 vin QP',
              f"Rt c3 t {p['RT']}", f"Ct t 0 {p['CT']}", f"Rtb t 0 {p['RTB']}", 'Q2 c2 t 0 QN',
              f"Rc2 c2 b1 {p['RC2']}", 'Q1 g b1 vin QP', f"Rb1 b1 vin {p['RB1']}", f"Cb1 b1 vin {p['CB1']}",
              f"Rg g 0 {p['RG']}", f"Cg g 0 {p['CG']}", f"Rf g t {p['RF']}", 'Bgs gs 0 V=V(g)-V(s)']
        n2 = 's'
    else:  # as built: the 56 mm LDO_IN run straight to the boost
        d += ['Rs vin d 0.11', 'Bgs gs 0 V=-5']
        n2 = 'd'
    d += ['C12 d c12m 2.5u', 'Rc12 c12m 0 10m', 'L2 d sw 10u Rser=0.45', 'Dhs sw ledsw DBODY', 'Dls 0 sw DBODY',
          'C9 ledsw 0 3.5u', 'R39 ledsw mon 1Meg', 'R41 mon 0 120k', 'C31 mon 0 100n']
    # U10: UVLO with hysteresis, enable from ADIM, timer since (re)start, input current drawn at SW
    if light:
        pts = [(0, 0)]
        for a, b in light['windows']:
            pts += [(a, 0), (a + 1e-6, 1), (b, 1), (b + 1e-6, 0)]
        d.append(f'Ven en 0 {pwl(pts)}')
        ist, tst, pss = light['ist'], light['tst'], P_LED_IN * light['duty']
    else:
        d.append('Ven en 0 0')
        ist, tst, pss = 0, 0, 0
    e_st = light.get('e_st') if light else None
    if e_st:
        # energy-based start: draw ist until e_st joules have gone into the boost; C9 keeps its charge, so the
        # progress survives a UVLO restart (V(el) is the energy in joules on a 1 F capacitor)
        start = f'V(el)<{e_st}'
    else:
        start = f'V(tim)<{tst}'
    d += ['Bst st 0 V=if(V(d)>2.40,1,if(V(d)<2.11,0,if(V(stq)>.5,1,0)))', 'Rst st stq 1k', 'Cst stq 0 1n',
          'Bon on 0 V=if(V(en)>.5,1,0)*if(V(stq)>.5,1,0)', 'Boff off 0 V=1-V(on)',
          'Btim 0 tim I=V(on)', 'Ctim tim 0 1', 'Stim tim 0 off 0 SWM',
          # averaged converter: its input current is drawn at the VIN pin (L2's 31 mV DC drop is ignored)
          f'Bin d 0 I=V(on)*(280u+if({start},{ist},{pss}/max(V(d),1)))']
    if e_st:
        d += [f'Bel 0 el I=V(on)*if(V(el)<{e_st},0.85*max(V(d),0)*{ist},0)', 'Cel el 0 1']
    if fault:
        pts = [(0, 0), (fault['tf'], 0), (fault['tf'] + 1e-6, 1)]
        if fault.get('tc'):
            pts += [(fault['tc'], 1), (fault['tc'] + 1e-6, 0)]
        d += [f'Vfc fc 0 {pwl(pts)}', f"Sf {fault['node']} fx fc 0 SWM", f"Rflt fx 0 {fault['r']}"]
    else:
        d += ['Rflt fx 0 1G']
    if iramp:
        t0, t1, i1 = iramp
        d.append(f'Bramp d 0 I={i1}*limit((time-{t0})/({t1}-{t0}),0,1)*limit(V(d),0,1)')
    d += bjt_models(bjt) + MODELS
    limiter = fuse and DESIGNS[design].get('topo') == 'limit'
    # keep the raw file small: only what the .meas statements read
    sv = ['V(gs)', 'V(d)', 'V(vin)', 'V(mon)', 'V(on)', 'V(fx)', 'I(Rs)', 'I(Rflt)', 'I(Vsrc)', f'V({n2})']
    if limiter:
        sv += ['I(Rg)']
    elif fuse:
        sv += ['V(t)', 'I(Rtb)', 'I(Rg)', 'Ie(Q2)']
    d.append('.save ' + ' '.join(sv))
    d.append(f'.tran 0 {tend} 0 {maxstep}')
    te = tend * 0.999
    m = [('vgs_end', f'FIND V(gs) AT={te}'), ('ifault_end', f'FIND I(Rflt) AT={te}'),
         ('e_fault', 'INTEG I(Rflt)*V(fx)'), ('e_rs', f'INTEG I(Rs)*V(vin,{n2})'),
         ('irs_pk', f'MAX I(Rs) FROM={t_ev} TO={te}'), ('irs_end', f'FIND I(Rs) AT={te}'),
         ('vd_min', f'MIN V(d) FROM={t_ev} TO={te}'), ('vin_min', f'MIN V(vin) FROM={t_ev} TO={te}'),
         ('vd_end', f'FIND V(d) AT={te}'), ('vin_end', f'FIND V(vin) AT={te}'),
         ('isrc_end', f'FIND -I(Vsrc) AT={te}'), ('vmon_end', f'FIND V(mon) AT={te}'),
         ('on_end', f'FIND V(on) AT={te}')]
    if limiter:
        # steady state at the end: power in M1, in the short, in Rs; ripple over the last 2 ms (oscillation check)
        t2 = te - 2e-3
        m += [('p_fet_end', f'FIND I(Rs)*V(s,d) AT={te}'), ('p_fault_end', f'FIND I(Rflt)*V(fx) AT={te}'),
              ('p_rs_end', f'FIND I(Rs)*V(vin,s) AT={te}'), ('p_fet_pk', f'MAX I(Rs)*V(s,d) FROM={t_ev} TO={te}'),
              ('irs_max_tail', f'MAX I(Rs) FROM={t2} TO={te}'), ('irs_min_tail', f'MIN I(Rs) FROM={t2} TO={te}'),
              ('iq_lim', f'FIND I(Rg) AT={te}')]
    elif fuse:
        m += [('t_off', f'WHEN V(gs)=-0.3 TD={t_ev} RISE=1'), ('vt_pk', f'MAX V(t) FROM={t_ev} TO={te}'),
              ('iq_fuse', f'FIND I(Rtb)+I(Rg)-Ie(Q2) AT={te}')]
        if iramp:
            m.append(('i_at_trip', f'FIND I(Rs) WHEN V(gs)=-2 RISE=1'))
    if light:
        a = light['windows'][0][0]
        m.append(('on_frac', f'AVG V(on) FROM={a} TO={te}'))
    for k, v in m:
        d.append(f'.meas tran {k} {v}')
    d.append('.end')
    return '\n'.join(d) + '\n'


def run(name, **kw):
    path = OUT / f'{name}.cir'
    path.write_text(deck(name, **kw))
    try:
        subprocess.run([str(EXE), '-b', str(path)], cwd=OUT, timeout=600, check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired:
        return {'timeout': 1.0}
    finally:
        (OUT / f'{name}.raw').unlink(missing_ok=True)  # keep out/ small; rerun a single deck to look at waveforms
    raw = path.with_suffix('.log').read_bytes()
    log = raw.decode('utf-16') if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else raw.decode('utf-8-sig', 'replace')
    if b'\x00' in raw[:200] and not raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        log = raw.decode('utf-16-le', 'replace')
    vals = {}
    for mm in re.finditer(r'^([A-Za-z_0-9]+):\s*(.*)$', log, flags=re.M):
        k, rest = mm.group(1).lower(), mm.group(2)
        if k in ('t_off',):
            a = re.search(r'\bAT\s+([-+0-9.eE]+)', rest, flags=re.I)
            if a:
                vals[k] = float(a.group(1))
            continue
        v = re.search(r'=\s*([-+0-9.eE]+)', rest)
        if v:
            vals[k] = float(v.group(1))
    if not vals:
        print('---- LOG', name, '----'); print(log[-2000:])
    return vals


def batch(jobs, workers=6):
    res = {}
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(run, n, **kw): n for n, kw in jobs.items()}
        for f in cf.as_completed(futs):
            res[futs[f]] = f.result()
    return dict(sorted(res.items()))


# ---- supply profiles (ideal source behind rpath) ----
def ramp(v, tr, t0=100e-6):
    return [(0, 0), (t0, 0), (t0 + tr, v)]


def ramp_step(v1, tr, t_step, v2, ts):
    return ramp(v1, tr) + [(t_step, v1), (t_step + ts, v2)]


BAT_TR, USB_TR, SW_T = 1.3e-3, 1.7e-3, 8e-6
CELLS = [3.0, 3.4, 3.7, 4.2]
SUPPLIES = [('bat', v) for v in CELLS] + [('usb', 5.0)]


def supply(kind, v, fast=False):
    tr = 10e-6 if fast else (USB_TR if kind == 'usb' else BAT_TR)
    return ramp(v, tr)


def tripped(r):
    return 't_off' in r and r.get('vgs_end', -9) > -0.3


# ---- groups ----
def g_threshold():
    """Slowly ramp an extra load on LED_VIN (0 -> 0.6 A in 300 ms) and record the current at trip."""
    jobs = {}
    for des in ('A', 'B'):
        for kind, v in [('bat', 3.0), ('bat', 3.7), ('usb', 5.0)]:
            for temp in (-20, 0, 25, 45, 60, 85):
                for bj in ('nom', 'lo', 'hi', 'bc'):
                    n = f'TH_{des}_{kind}{v}_T{temp}_{bj}'
                    jobs[n] = dict(design=des, src=supply(kind, v), tend=0.32, iramp=(0.01, 0.31, 0.6), temp=temp,
                                   bjt=bj, t_ev=0.01, maxstep='20u')
    return jobs


def g_normal(designs=('A', 'B', 'none')):
    jobs = {}
    for des in designs:
        for kind, v in SUPPLIES:
            for duty in (0.5, 1.0):
                n = f'N_{des}_{kind}{v}_d{int(duty * 100)}'
                jobs[n] = dict(design=des if des != 'none' else 'A', fuse=des != 'none', src=supply(kind, v),
                               tend=0.05, light=dict(windows=[(0.01, 1)], ist=0.1, tst=3e-3, duty=duty), t_ev=0.03)
        for temp in (25, 60):
            n = f'N_{des}_idle_bat3.7_T{temp}'
            jobs[n] = dict(design=des if des != 'none' else 'A', fuse=des != 'none', src=supply('bat', 3.7),
                           tend=0.2, temp=temp, t_ev=0.1)
    return jobs


START_ENVELOPES = {'800mA_0.3ms': (0.8, 0.3e-3), '400mA_0.5ms': (0.4, 0.5e-3), '400mA_1ms': (0.4, 1e-3),
                   '200mA_3ms': (0.2, 3e-3), '100mA_5ms': (0.1, 5e-3)}


def g_nuisance(designs=('A', 'B'), starts=True):
    jobs = {}
    for des in designs:
        for temp in (-20, 25, 60):
            for bj in ('nom', 'lo'):  # 'lo' V_BE is the low-threshold corner
                tag = f'{des}_T{temp}_{bj}'
                kw = dict(design=des, temp=temp, bjt=bj)
                # power-up into a dead board: TPS2116 soft start and a 10 us stress ramp
                for kind, v in SUPPLIES:
                    for fast in (False, True):
                        jobs[f'U_{tag}_{kind}{v}_{"fast" if fast else "ss"}'] = dict(
                            src=supply(kind, v, fast), tend=0.02, **kw)
                # USB plug-in and unplug with a cell present, light off and on (100 %)
                for v in CELLS:
                    for lt in (None, dict(windows=[(0.005, 1)], ist=0.1, tst=3e-3, duty=1.0)):
                        for ts in (SW_T, 1e-6):
                            lab = 'on' if lt else 'off'
                            jobs[f'P_{tag}_bat{v}_plug{ts * 1e6:.0f}us_{lab}'] = dict(
                                src=ramp_step(v, BAT_TR, 0.02, 5.0, ts), tend=0.04, light=lt, t_ev=0.02, **kw)
                            jobs[f'Q_{tag}_bat{v}_unplug{ts * 1e6:.0f}us_{lab}'] = dict(
                                src=ramp_step(5.0, USB_TR, 0.02, v, ts), tend=0.04, light=lt, t_ev=0.02, **kw)
                # light start-up envelopes at every supply
                for kind, v in (SUPPLIES if starts else []):
                    for en, (ist, tst) in START_ENVELOPES.items():
                        jobs[f'S_{tag}_{kind}{v}_{en}'] = dict(
                            src=supply(kind, v), tend=0.04,
                            light=dict(windows=[(0.01, 1)], ist=ist, tst=tst, duty=1.0), t_ev=0.01, **kw)
                    # five starts 10 ms apart (3 ms off: > 2.5 ms ADIM shutdown, so each one soft-starts again)
                    w = [(0.01 + k * 0.01, 0.017 + k * 0.01) for k in range(5)]
                    jobs[f'R_{tag}_{kind}{v}_5x400mA_0.5ms'] = dict(
                        src=supply(kind, v), tend=0.08, light=dict(windows=w, ist=0.4, tst=0.5e-3, duty=1.0),
                        t_ev=0.01, **kw)
    return jobs


FAULT_R = [0.05, 0.5, 1, 2, 3, 5, 7, 8, 10, 12, 15, 20, 30]


def g_fault(designs=('A', 'B'), sweep=True, tl=0.08, tl0=0.06):
    jobs = {}
    for des in designs:
        for kind, v in SUPPLIES:
            for r in (FAULT_R if sweep else []):  # U10 low-side switch short (case 1), light off, after power-up
                jobs[f'F_{des}_sw_{kind}{v}_R{r}'] = dict(design=des, src=supply(kind, v), tend=0.08,
                                                          fault=dict(node='sw', r=r, tf=0.01), t_ev=0.01)
            for node in ('d', 'ledsw'):  # C12 short; LED_SW short (C9, D3, J3) fed through the body diode
                for r in (0.5, 3, 7):
                    jobs[f'F_{des}_{node}_{kind}{v}_R{r}'] = dict(design=des, src=supply(kind, v), tend=tl,
                                                                  fault=dict(node=node, r=r, tf=0.01), t_ev=0.01)
        for temp in ((-20, 60) if sweep else ()):
            for kind, v in [('bat', 3.0), ('bat', 3.4), ('bat', 3.7), ('usb', 5.0)]:
                for r in (5, 7, 10):
                    jobs[f'F_{des}_sw_{kind}{v}_R{r}_T{temp}'] = dict(
                        design=des, src=supply(kind, v), tend=0.08, temp=temp,
                        fault=dict(node='sw', r=r, tf=0.01), t_ev=0.01)
        # fault already present when power arrives; case 1 replay = USB, no battery, 7 ohm on SW, light restored
        for kind, v in [('usb', 5.0), ('bat', 3.7), ('bat', 3.0)]:
            for r in (0.5, 7):
                jobs[f'F0_{des}_sw_{kind}{v}_R{r}'] = dict(design=des, src=supply(kind, v), tend=tl0,
                                                           fault=dict(node='sw', r=r, tf=0), t_ev=0)
        jobs[f'F0_{des}_case1_usb5.0_R7_light'] = dict(
            design=des, src=supply('usb', 5.0), tend=tl0, fault=dict(node='sw', r=7, tf=0),
            light=dict(windows=[(3.5e-3, 1)], ist=0.4, tst=0.5e-3, duty=1.0), t_ev=0)
    return jobs


def g_release(designs=('A', 'B')):
    """Latch on a 7 ohm fault at 3.7 V, clear the fault, pull the supply down to v_low for 50 ms, bring it back."""
    jobs = {}
    for des in designs:
        for vlow in (2.0, 1.5, 1.2, 1.0, 0.8, 0.5, 0.0):
            src = ramp(3.7, BAT_TR) + [(0.05, 3.7), (0.06, vlow), (0.11, vlow), (0.111 + 1.3e-3, 3.7)]
            jobs[f'L_{des}_vlow{vlow}'] = dict(design=des, src=src, tend=0.16,
                                               fault=dict(node='sw', r=7, tf=0.01, tc=0.04), t_ev=0.01)
    return jobs


def g_baseline():
    """As built (no fuse) for comparison: plug-in surges and the case 1 fault energy."""
    jobs = {}
    for v in CELLS:
        jobs[f'B_none_bat{v}_plug8us_off'] = dict(fuse=False, src=ramp_step(v, BAT_TR, 0.02, 5.0, SW_T), tend=0.04,
                                                  t_ev=0.02)
        jobs[f'B_A_bat{v}_plug8us_off'] = dict(design='A', src=ramp_step(v, BAT_TR, 0.02, 5.0, SW_T), tend=0.04,
                                               t_ev=0.02)
    for kind, v in SUPPLIES:
        jobs[f'B_none_{kind}{v}_fast_off'] = dict(fuse=False, src=supply(kind, v, True), tend=0.02)
        for r in (0.5, 7):
            jobs[f'B_none_sw_{kind}{v}_R{r}'] = dict(fuse=False, src=supply(kind, v), tend=0.08,
                                                     fault=dict(node='sw', r=r, tf=0.01), t_ev=0.01)
    return jobs


def g_variants():
    """Longer-delay variants (A2, M2, B2) against the light start-up envelopes, repeated starts and SW-node faults."""
    jobs = {}
    for des in ('A2', 'M2', 'B2'):
        for temp in (-20, 25, 60):
            for bj in ('nom', 'lo'):
                tag = f'{des}_T{temp}_{bj}'
                kw = dict(design=des, temp=temp, bjt=bj)
                for kind, v in SUPPLIES:
                    for en, (ist, tst) in START_ENVELOPES.items():
                        jobs[f'S_{tag}_{kind}{v}_{en}'] = dict(
                            src=supply(kind, v), tend=0.06,
                            light=dict(windows=[(0.01, 1)], ist=ist, tst=tst, duty=1.0), t_ev=0.01, **kw)
                    w = [(0.01 + k * 0.01, 0.017 + k * 0.01) for k in range(5)]
                    jobs[f'R_{tag}_{kind}{v}_5x400mA_0.5ms'] = dict(
                        src=supply(kind, v), tend=0.1, light=dict(windows=w, ist=0.4, tst=0.5e-3, duty=1.0),
                        t_ev=0.01, **kw)
            for kind, v in SUPPLIES:
                for r in (0.05, 0.5, 3, 7, 10, 12):
                    jobs[f'F_{des}_sw_{kind}{v}_R{r}_T{temp}'] = dict(
                        design=des, src=supply(kind, v), tend=0.1, temp=temp,
                        fault=dict(node='sw', r=r, tf=0.01), t_ev=0.01)
    return jobs


def g_m2():
    """The recommended M2 through everything A and B saw that the variants group did not cover."""
    return {**g_normal(('M2',)), **g_nuisance(('M2',), starts=False), **g_fault(('M2',), sweep=False, tl=0.12, tl0=0.1),
            **g_release(('M2',))}


E_STARTS = {'800mA_0.3mJ': (0.8, 0.3e-3), '400mA_0.3mJ': (0.4, 0.3e-3), '400mA_0.6mJ': (0.4, 0.6e-3),
            '200mA_0.6mJ': (0.2, 0.6e-3)}


def g_limiter():
    """The 4-part linear limiter (L22/L27/L33): limit current, normal use, faults, supply events, light starts."""
    jobs = {}
    for des in ('L22', 'L27', 'L33'):
        for kind, v in [('bat', 3.0), ('bat', 3.7), ('usb', 5.0)]:
            for temp in (-20, 25, 60, 85):
                for bj in ('nom', 'lo', 'hi', 'bc'):
                    jobs[f'TH_{des}_{kind}{v}_T{temp}_{bj}'] = dict(
                        design=des, src=supply(kind, v), tend=0.32, iramp=(0.01, 0.31, 0.6), temp=temp, bjt=bj,
                        t_ev=0.01, maxstep='20u')
        jobs.update({k.replace('N_M2', f'N_{des}'): {**v, 'design': des} for k, v in g_normal(('M2',)).items()})
        for kind, v in SUPPLIES:
            for r in (0.05, 0.5, 1, 2, 3, 5, 7, 10, 15, 20):
                jobs[f'F_{des}_sw_{kind}{v}_R{r}'] = dict(design=des, src=supply(kind, v), tend=0.1,
                                                          fault=dict(node='sw', r=r, tf=0.01), t_ev=0.01)
            for temp in (-20, 60):
                for r in (0.05, 7):
                    jobs[f'F_{des}_sw_{kind}{v}_R{r}_T{temp}'] = dict(
                        design=des, src=supply(kind, v), tend=0.1, temp=temp, fault=dict(node='sw', r=r, tf=0.01),
                        t_ev=0.01)
        for kind, v in [('bat', 3.0), ('bat', 3.7), ('usb', 5.0)]:
            for node in ('d', 'ledsw'):
                for r in (0.5, 7):
                    jobs[f'F_{des}_{node}_{kind}{v}_R{r}'] = dict(design=des, src=supply(kind, v), tend=0.1,
                                                                  fault=dict(node=node, r=r, tf=0.01), t_ev=0.01)
        for kind, v in SUPPLIES:
            for fast in (False, True):
                jobs[f'U_{des}_{kind}{v}_{"fast" if fast else "ss"}'] = dict(design=des, src=supply(kind, v, fast),
                                                                            tend=0.02)
        for v in CELLS:
            for lt in (None, dict(windows=[(0.005, 1)], ist=0.1, tst=3e-3, duty=1.0)):
                lab = 'on' if lt else 'off'
                jobs[f'P_{des}_bat{v}_plug8us_{lab}'] = dict(design=des, src=ramp_step(v, BAT_TR, 0.02, 5.0, SW_T),
                                                            tend=0.04, light=lt, t_ev=0.02)
                jobs[f'Q_{des}_bat{v}_unplug8us_{lab}'] = dict(
                    design=des, src=ramp_step(5.0, USB_TR, 0.02, v, SW_T), tend=0.04, light=lt, t_ev=0.02)
        for temp, bj in ((25, 'nom'), (60, 'lo')):
            for kind, v in SUPPLIES:
                for en, (ist, tst) in START_ENVELOPES.items():
                    jobs[f'S_{des}_T{temp}_{bj}_{kind}{v}_{en}'] = dict(
                        design=des, src=supply(kind, v), tend=0.06, temp=temp, bjt=bj,
                        light=dict(windows=[(0.01, 1)], ist=ist, tst=tst, duty=1.0), t_ev=0.01)
                for en, (ist, est) in E_STARTS.items():
                    jobs[f'E_{des}_T{temp}_{bj}_{kind}{v}_{en}'] = dict(
                        design=des, src=supply(kind, v), tend=0.06, temp=temp, bjt=bj,
                        light=dict(windows=[(0.01, 1)], ist=ist, tst=0, e_st=est, duty=1.0), t_ev=0.01)
    return jobs


GROUPS = {'threshold': g_threshold, 'normal': g_normal, 'nuisance': g_nuisance, 'fault': g_fault,
          'release': g_release, 'baseline': g_baseline, 'variants': g_variants, 'm2': g_m2, 'limiter': g_limiter}

if __name__ == '__main__':
    which = sys.argv[1:] or ['all']
    if which == ['all']:
        which = list(GROUPS)
    for g in which:
        jobs = GROUPS[g]()
        print(f'{g}: {len(jobs)} runs', flush=True)
        res = batch(jobs)
        (HERE / f'results_{g}.json').write_text(json.dumps(res, indent=1))
        bad = [n for n, r in res.items() if not r or 'timeout' in r]
        print(f'{g}: done, {len(bad)} empty/timeouts' + (f': {bad[:5]}' if bad else ''), flush=True)
