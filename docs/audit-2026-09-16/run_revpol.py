"""Behavioral LTspice check of the Silkscreen battery path (as-built nets) + candidate fixes.

Models are generic approximations (VDMOS, ideal-ish ESD diodes), NOT vendor models.
Purpose: compare topologies for (a) normal charge/discharge, (b) reversed cell + USB,
(c) reversed cell hot-swapped while P+ is still charged, (d) no-battery latch-up.
"""
import json, os, pathlib, re, subprocess

EXE = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe'
OUT = pathlib.Path(__file__).parent
TEND = '30m'
TMEAS = '29.9m'

FIX_NAMES = {0: 'as-built (CE=VBUS, Q8 gate=GND)',
             1: 'CE-gate only (BSS138 det + AO3419 pass -> CE)',
             2: 'Q8 gate -> B- (+1M B- pulldown), CE=VBUS',
             3: 'det -> Q8 gate (Roff 1M) + CE-gate'}

def deck(name, VB, USB, LOAD, FIX, nobatt=False, ic_pp=None, vth_det=1.3):
    d = [f'* {name}  FIX={FIX}']
    d.append(f'.param USB={USB} LOAD={LOAD}')
    # ---- cell + connector (S1 closes at 1 ms) ----
    if nobatt:
        d.append('Rflt_bp bp 0 1G')
    else:
        d += [f'Vcell bpc bm {VB}', 'Rcell bpc bpx .05',
              'S1 bpx bp sw 0 SWM', 'Vsw sw 0 PULSE(0 1 1m 1u 1u 10 20)',
              'Rflt_bp bp 0 1G']
    d.append('Rflt_bm bm 0 1G')          # board leakage; avoids floating-node singularity
    # ---- Q3 / R27 / Q8 exactly as netlisted ----
    d += ['Mq3 com q3g bp P_AO3419',     # S=B+, D=Net-(Q3-D), G=Net-(Q3-G)
          'R27 com com2 1m',             # 0R link, current sense
          'Mq8 com2 q8g pp P_AO3419',    # S=P+, D=Net-(Q8-D)
          'R56 q3g bm 10k', 'R57 q3g bp 1Meg']
    # ---- U5 DW01A behavioral (GND pin = B-, VCC = P+) ----
    d += ['Dsub bm pp DESD',             # substrate/ESD: conducts when B- > P+ + Vf
          'Dcs1 cs pp DESD', 'Dcs2 bm cs DESD',   # CS pin ESD diodes
          'R16 cs 0 1k', 'Rq5 pp bm 1Meg', 'C7 pp bm .1u',
          'Bod od bm V={if(V(pp,bm)>2.4 & V(pp,bm)<12, V(pp,bm), 0)}',
          'Boc oc bm V={if(V(pp,bm)>2.0 & V(pp,bm)<4.3, V(pp,bm), 0)}']
    # ---- Q1 FS8205A: S1=B- (G1=OD), S2=GND (G2=OC), common drain ----
    d += ['Mq1a q1d od bm N_FS', 'Mq1b q1d oc 0 N_FS']
    # ---- P+ rail: C3, BAT_MONIT divider, charger, mux/load ----
    d += ['C3 pp 0 10u', 'Rmon pp 0 2Meg', 'Rleak pp 0 5G',
          'Vusb vbus 0 {5*USB}', 'C2 vbus 0 10u',
          'B33 v33 0 V={if(USB>.5, 3.3, limit(V(pp)-.2,0,3.3))}',
          'Bload pp 0 I={if(USB>.5, 0, LOAD*limit(V(pp)/3,0,1))}']
    # charger enable: as-built/FIX2 -> CE=VBUS ; FIX1/3 -> CE node
    if FIX in (0, 2):
        d.append('Bchg 0 pp I={if(USB>.5, limit((4.2-V(pp))*4,0,.25), 0)}')
    else:
        d.append('Bchg 0 pp I={if(USB>.5, limit((V(ce)-1.0)*5,0,1)*limit((4.2-V(pp))*4,0,.25), 0)}')
    # ---- Q8 gate per fix ----
    if FIX in (0, 1):
        d.append('Rq8g q8g 0 1m')
    elif FIX == 2:
        d += ['Rq8g q8g bm 1m', 'Rbmpd bm 0 1Meg']
    elif FIX == 3:
        d += ['Mq8det q8g ng 0 N_BSS138', 'Roff pp q8g 1Meg']
    # ---- CE-gate detector (FIX 1,3) ----
    if FIX in (1, 3):
        d += ['Rdg bp ng 100k', 'Rdpd ng 0 1Meg',
              'Mdet x ng 0 N_BSS138', 'Rxpu v33 x 1Meg',
              'Mpass ce x v33 P_AO3419', 'Rcepd ce 0 1Meg']
    else:
        d += ['Rce ce vbus 1', 'Rng ng 0 1Meg']   # dummies so .meas nodes exist
    # ---- models ----
    d += ['.model P_AO3419 VDMOS(pchan Vto=-.85 Kp=10 Rd=.045 Rs=.035 Rg=11 Cgdmin=37p Cgdmax=150p Cgs=288p Cjo=63p Is=1n Rb=.1)',
          f'.model N_BSS138 VDMOS(Vto={vth_det} Kp=.4 Rd=1 Rs=.5 Rg=10 Cgdmin=5p Cgdmax=15p Cgs=30p Cjo=10p Is=1n Rb=1)',
          '.model N_FS VDMOS(Vto=1.0 Kp=20 Rd=.012 Rs=.012 Rg=5 Cgdmin=30p Cgdmax=60p Cgs=500p Cjo=50p Is=1n Rb=.05)',
          '.model DESD D(Is=1n Rs=5 N=1.5)',
          '.model SWM SW(Ron=.01 Roff=1G Vt=.5 Vh=0)']
    if ic_pp is not None:
        d.append(f'.ic V(pp)={ic_pp}')
    d.append(f'.tran 0 {TEND} 0 20u')
    m = [('pp_v', f'FIND V(pp) AT={TMEAS}'),
         ('bp_v', f'FIND V(bp) AT={TMEAS}'),
         ('bm_v', f'FIND V(bm) AT={TMEAS}'),
         ('u5_sup_v', f'FIND V(pp,bm) AT={TMEAS}'),
         ('u5_sup_min', 'MIN V(pp,bm)'),
         ('ce_v', f'FIND V(ce) AT={TMEAS}'),
         ('q8_vgs', f'FIND V(q8g,pp) AT={TMEAS}'),
         ('i_r27_end', f'FIND I(R27) AT={TMEAS}'),
         ('i_r27_max', 'MAX I(R27)'), ('i_r27_min', 'MIN I(R27)'),
         ('i_dsub_end', f'FIND I(Dsub) AT={TMEAS}'), ('i_dsub_max', 'MAX I(Dsub)'),
         ('i_r16_end', f'FIND I(R16) AT={TMEAS}'), ('i_r16_max', 'MAX abs(I(R16))'),
         ('i_chg_end', f'FIND I(Bchg) AT={TMEAS}')]
    if not nobatt:
        m += [('i_cell_end', f'FIND I(Vcell) AT={TMEAS}'),
              ('i_cell_max', 'MAX I(Vcell)'), ('i_cell_min', 'MIN I(Vcell)')]
    if FIX in (1, 3):
        m += [('i_det_div', f'FIND I(Rdg) AT={TMEAS}')]
    for k, v in m:
        d.append(f'.meas tran {k} {v}')
    d.append('.end')
    return '\n'.join(d) + '\n'

def run(name, **kw):
    path = OUT / f'{name}.cir'
    path.write_text(deck(name, **kw))
    subprocess.run([str(EXE), '-b', str(path)], cwd=OUT, timeout=120, check=True,
                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    raw = path.with_suffix('.log').read_bytes()
    log = raw.decode('utf-16') if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else raw.decode('utf-8-sig', 'replace')
    vals = {mm.group(1).lower(): float(mm.group(2)) for mm in
            re.finditer(r'^([A-Za-z_0-9]+):[^\n=]*=([-+0-9.eE]+)', log, flags=re.M)}
    if not vals:
        print('---- LOG', name, '----'); print(log[-3000:])
    return vals

results = {}
def add(name, **kw):
    results[name] = {'fix': FIX_NAMES[kw['FIX']], **run(name, **kw)}

for fix in (0, 1, 2, 3):
    add(f'A_discharge_3V7_fix{fix}', VB=3.7, USB=0, LOAD=.25, FIX=fix)
    add(f'B_charge_3V7_fix{fix}', VB=3.7, USB=1, LOAD=0, FIX=fix)
    add(f'C_charge_2V5_fix{fix}', VB=2.5, USB=1, LOAD=0, FIX=fix)
    add(f'D_reversed_USB_fix{fix}', VB=-4.2, USB=1, LOAD=0, FIX=fix)
    add(f'E_reversed_USB_hotswap_fix{fix}', VB=-4.2, USB=1, LOAD=0, FIX=fix, ic_pp=4.2)
    add(f'F_nobatt_USB_ppcharged_fix{fix}', VB=0, USB=1, LOAD=0, FIX=fix, nobatt=True, ic_pp=4.2)
    add(f'G_reversed_noUSB_fix{fix}', VB=-4.2, USB=0, LOAD=0, FIX=fix)
# worst-case detector threshold with a deeply discharged cell
add('C_charge_2V5_fix1_vth1V5', VB=2.5, USB=1, LOAD=0, FIX=1, vth_det=1.5)
add('C_charge_2V5_fix3_vth1V5', VB=2.5, USB=1, LOAD=0, FIX=3, vth_det=1.5)

(OUT / 'results.json').write_text(json.dumps(results, indent=1))
keys = ['pp_v', 'u5_sup_v', 'u5_sup_min', 'ce_v', 'q8_vgs', 'i_cell_end', 'i_cell_max', 'i_cell_min',
        'i_r27_end', 'i_dsub_max', 'i_dsub_end', 'i_r16_max', 'i_chg_end', 'i_det_div']
print(f"{'case':38s}" + ''.join(f'{k:>11s}' for k in keys))
for n, r in results.items():
    row = ''.join(f"{r[k]:11.4g}" if k in r else f"{'-':>11s}" for k in keys)
    print(f'{n:38s}{row}')
