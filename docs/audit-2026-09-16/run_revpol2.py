"""Round 2: B- referenced detector (FIX4 = CE-gate only, FIX5 = det->Q8 gate + CE-gate).
Adds E2 (latched empty connector then reversed insert) and an as-built variant where the
unpowered DW01A leaves the FS8205A gates floating instead of driven to B-.
"""
import json, os, pathlib, re, subprocess

EXE = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe'
OUT = pathlib.Path(__file__).parent
TEND, TMEAS = '30m', '29.9m'
FIX_NAMES = {0: 'as-built', 4: 'CE-gate, det ref B-', 5: 'det ref B- -> Q8 gate + CE-gate'}

def deck(name, VB, USB, LOAD, FIX, nobatt=False, ic=None, vth_det=1.3, ocfloat=False):
    d = [f'* {name} FIX={FIX}', f'.param USB={USB} LOAD={LOAD}']
    if nobatt:
        d.append('Rflt_bp bp 0 1G')
    else:
        d += [f'Vcell bpc bm {VB}', 'Rcell bpc bpx .05', 'S1 bpx bp sw 0 SWM',
              'Vsw sw 0 PULSE(0 1 1m 1u 1u 10 20)', 'Rflt_bp bp 0 1G']
    d.append('Rflt_bm bm 0 1G')
    d += ['Mq3 com q3g bp P_AO3419', 'R27 com com2 1m', 'Mq8 com2 q8g pp P_AO3419',
          'R56 q3g bm 10k', 'R57 q3g bp 1Meg']
    # U5 DW01A behavioral
    d += ['Dsub bm pp DESD', 'Dcs1 cs pp DESD', 'Dcs2 bm cs DESD', 'R16 cs 0 1k',
          'Rq5 pp bm 1Meg', 'C7 pp bm .1u']
    if ocfloat:
        d += ['Bod odd bm V={if(V(pp,bm)>2.4 & V(pp,bm)<12, V(pp,bm), 0)}',
              'Boc ocd bm V={if(V(pp,bm)>2.0 & V(pp,bm)<4.3, V(pp,bm), 0)}',
              'Bval val 0 V={if(V(pp,bm)>2.0 & V(pp,bm)<12, 1, 0)}',
              'Sod odd od val 0 SWM', 'Soc ocd oc val 0 SWM', 'Rodl od bm 1G', 'Rocl oc 0 1G']
    else:
        d += ['Bod od bm V={if(V(pp,bm)>2.4 & V(pp,bm)<12, V(pp,bm), 0)}',
              'Boc oc bm V={if(V(pp,bm)>2.0 & V(pp,bm)<4.3, V(pp,bm), 0)}']
    d += ['Mq1a q1d od bm N_FS', 'Mq1b q1d oc 0 N_FS']
    d += ['C3 pp 0 10u', 'Rmon pp 0 2Meg', 'Rleak pp 0 5G', 'Vusb vbus 0 {5*USB}', 'C2 vbus 0 10u',
          'B33 v33 0 V={if(USB>.5, 3.3, limit(V(pp)-.2,0,3.3))}',
          'Bload pp 0 I={if(USB>.5, 0, LOAD*limit(V(pp)/3,0,1))}']
    if FIX == 0:
        d.append('Bchg 0 pp I={if(USB>.5, limit((4.2-V(pp))*4,0,.25), 0)}')
        d += ['Rq8g q8g 0 1m', 'Rce ce vbus 1', 'Rng ng 0 1Meg']
    else:
        d.append('Bchg 0 pp I={if(USB>.5, limit((V(ce)-1.0)*5,0,1)*limit((4.2-V(pp))*4,0,.25), 0)}')
        # detector referenced to raw B-: senses (B+ - B-) only
        d += ['Rdg bp ng 100k', 'Rdpd ng bm 1Meg', 'Mdet x ng bm N_BSS138',
              'Rxpu v33 x 1Meg', 'Mpass ce x v33 P_AO3419', 'Rcepd ce 0 1Meg']
        if FIX == 4:
            d.append('Rq8g q8g 0 1m')
        else:
            d += ['Mq8det q8g ng bm N_BSS138', 'Roff pp q8g 1Meg']
    d += ['.model P_AO3419 VDMOS(pchan Vto=-.85 Kp=10 Rd=.045 Rs=.035 Rg=11 Cgdmin=37p Cgdmax=150p Cgs=288p Cjo=63p Is=1n Rb=.1)',
          f'.model N_BSS138 VDMOS(Vto={vth_det} Kp=.4 Rd=1 Rs=.5 Rg=10 Cgdmin=5p Cgdmax=15p Cgs=30p Cjo=10p Is=1n Rb=1)',
          '.model N_FS VDMOS(Vto=1.0 Kp=20 Rd=.012 Rs=.012 Rg=5 Cgdmin=30p Cgdmax=60p Cgs=500p Cjo=50p Is=1n Rb=.05)',
          '.model DESD D(Is=1n Rs=5 N=1.5)', '.model SWM SW(Ron=.01 Roff=1G Vt=.5 Vh=0)']
    if ic:
        d.append('.ic ' + ' '.join(f'V({k})={v}' for k, v in ic.items()))
    d.append(f'.tran 0 {TEND} 0 20u')
    m = [('pp_v', f'FIND V(pp) AT={TMEAS}'), ('bp_v', f'FIND V(bp) AT={TMEAS}'), ('bm_v', f'FIND V(bm) AT={TMEAS}'),
         ('u5_sup_v', f'FIND V(pp,bm) AT={TMEAS}'), ('u5_sup_min', 'MIN V(pp,bm)'),
         ('ce_v', f'FIND V(ce) AT={TMEAS}'), ('q8_vgs', f'FIND V(q8g,pp) AT={TMEAS}'),
         ('i_r27_end', f'FIND I(R27) AT={TMEAS}'),
         ('i_dsub_max', 'MAX I(Dsub)'), ('i_r16_max', 'MAX abs(I(R16))'), ('i_r16_end', f'FIND I(R16) AT={TMEAS}'),
         ('i_chg_end', f'FIND I(Bchg) AT={TMEAS}')]
    if not nobatt:
        m += [('i_cell_end', f'FIND I(Vcell) AT={TMEAS}')]
    if FIX:
        m += [('i_det_div', f'FIND I(Rdg) AT={TMEAS}'), ('det_vgs', f'FIND V(ng,bm) AT={TMEAS}')]
    for k, v in m:
        d.append(f'.meas tran {k} {v}')
    d.append('.end')
    return '\n'.join(d) + '\n'

def run(name, **kw):
    path = OUT / f'{name}.cir'
    path.write_text(deck(name, **kw))
    try:
        subprocess.run([str(EXE), '-b', str(path)], cwd=OUT, timeout=90, check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired:
        print('TIMEOUT', name)
        return {'timeout': 1.0}
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

add('D_reversed_USB_fix0_ocfloat', VB=-4.2, USB=1, LOAD=0, FIX=0, ocfloat=True)
for fix in (4, 5):
    add(f'A_discharge_3V7_fix{fix}', VB=3.7, USB=0, LOAD=.25, FIX=fix)
    add(f'B_charge_3V7_fix{fix}', VB=3.7, USB=1, LOAD=0, FIX=fix)
    add(f'C_charge_2V5_fix{fix}', VB=2.5, USB=1, LOAD=0, FIX=fix)
    add(f'C_charge_2V5_fix{fix}_vth1V5', VB=2.5, USB=1, LOAD=0, FIX=fix, vth_det=1.5)
    add(f'D_reversed_USB_fix{fix}', VB=-4.2, USB=1, LOAD=0, FIX=fix)
    add(f'E_reversed_hotswap_fix{fix}', VB=-4.2, USB=1, LOAD=0, FIX=fix, ic={'pp': 4.2})
    add(f'E2_latched_then_reversed_fix{fix}', VB=-4.2, USB=1, LOAD=0, FIX=fix, ic={'pp': 4.2, 'bp': 3.5, 'ce': 3.3})
    add(f'F_nobatt_USB_ppcharged_fix{fix}', VB=0, USB=1, LOAD=0, FIX=fix, nobatt=True, ic={'pp': 4.2})
    add(f'G_reversed_noUSB_fix{fix}', VB=-4.2, USB=0, LOAD=0, FIX=fix)

(OUT / 'results2.json').write_text(json.dumps(results, indent=1))
keys = ['pp_v', 'bp_v', 'bm_v', 'u5_sup_v', 'u5_sup_min', 'ce_v', 'q8_vgs', 'det_vgs', 'i_cell_end',
        'i_r27_end', 'i_chg_end', 'i_dsub_max', 'i_r16_max', 'i_r16_end', 'i_det_div']
print(f"{'case':36s}" + ''.join(f'{k:>11s}' for k in keys))
for n, r in results.items():
    print(f'{n:36s}' + ''.join(f"{r[k]:11.4g}" if k in r else f"{'-':>11s}" for k in keys))
