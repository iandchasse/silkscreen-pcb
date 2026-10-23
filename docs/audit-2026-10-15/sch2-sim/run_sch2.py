"""SCH-2 (move Q2.2 and R81.2 from 3V3 to USB_VBUS) on the repo's own Fix 4 LTspice deck.

Based on docs/audit-2026-09-16/run_revpol2.py (FIX = 4: CE gate only, detector referenced to raw B-); the
as-built variant reproduces that deck's published results.  Needs LTspice (batch mode); writes under ./out
(git-ignored).  Usage:  python run_sch2.py static | plug | leak

  topo  'v33'  = as built: Q2 source and R81 top on 3V3
        'vbus' = SCH-2:    Q2 source and R81 top on USB_VBUS
  The AO3401A (Q2) and BSS138 (Q9) models are generic VDMOS fits to their datasheets (C15127, C7420339); the
  TP4056 is a behavioural current source (CE threshold 1.5 V, UVLO 3.7 V, 20 us soft start, 10 % trickle below
  2.9 V).  Not a device qualification: see docs/audit-2026-10-15/SCH-2_CHARGE_ENABLE.md for what it does not cover.
"""
import json, os, pathlib, re, subprocess, sys

EXE = pathlib.Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe'
OUT = pathlib.Path(__file__).parent / 'out'
OUT.mkdir(exist_ok=True)

MODELS = [
    # AO3401A from the datasheet (C15127): Ciss 645 / Coss 80 / Crss 55 pF at Vds = -15 V, Vth -0.5/-0.9/-1.3 V,
    # Rds(on) 60 mohm @ -4.5 V and 85 mohm @ -2.5 V.  Cgs = Ciss - Crss; Cgd and Cds rise at low |Vds|.
    '.model P_AO3401A VDMOS(pchan Vto={VTH_P} Kp=13.9 Rd=.022 Rs=.018 Rg=7.8 Cgdmin=55p Cgdmax=300p Cgs=590p Cjo=200p M=.5 Vj=.7 Is=1n Rb=.1)',
    # BSS138: Vth .8/1.3/1.5 V, Ciss ~27 pF
    '.model N_BSS138 VDMOS(Vto={VTH_N} Kp=.4 Rd=1 Rs=.5 Rg=10 Cgdmin=4p Cgdmax=15p Cgs=22p Cjo=10p Is=1n Rb=1)',
    # AO3419-ish power FETs and FS8205A exactly as the repo deck
    '.model P_AO3419 VDMOS(pchan Vto=-.85 Kp=10 Rd=.045 Rs=.035 Rg=11 Cgdmin=37p Cgdmax=150p Cgs=288p Cjo=63p Is=1n Rb=.1)',
    '.model N_FS VDMOS(Vto=1.0 Kp=20 Rd=.012 Rs=.012 Rg=5 Cgdmin=30p Cgdmax=60p Cgs=500p Cjo=50p Is=1n Rb=.05)',
    '.model DESD D(Is=1n Rs=5 N=1.5)', '.model SWM SW(Ron=.01 Roff=1G Vt=.5 Vh=0)',
]


def deck(name, topo, VB, USB, LOAD=0, r81='1Meg', r82='1Meg', nobatt=False, ic=None, vth_n=1.3, vth_p=-0.9,
         plug=None, cce='5p', cce_extra=None, vth_ce=1.5, tend='30m', tmeas='29.9m', step='20u', cab_l=None, dce=False, ileak=None, iceleak=None):
    """plug = None for a DC USB level, else dict(tr=..., t0=...) for a ramp (seconds)."""
    src = 'v33' if topo == 'v33' else 'vbus'
    d = [f'* {name} topo={topo} r81={r81} r82={r82}']
    if plug is None:
        d.append(f'.param USB={USB} LOAD={LOAD}')
    else:
        d.append(f'.param USB=1 LOAD={LOAD}')
    if nobatt:
        d.append('Rflt_bp bp 0 1G')
    else:
        d += [f'Vcell bpc bm {VB}', 'Rcell bpc bpx .05', 'S1 bpx bp sw 0 SWM',
              'Vsw sw 0 PULSE(0 1 1u 1u 10 20)', 'Rflt_bp bp 0 1G']
    d.append('Rflt_bm bm 0 1G')
    d += ['Mq3 com q3g bp P_AO3419', 'R27 com com2 1m', 'Mq8 com2 q8g pp P_AO3419', 'R56 q3g bm 10k', 'R57 q3g bp 1Meg',
          'Dsub bm pp DESD', 'Dcs1 cs pp DESD', 'Dcs2 bm cs DESD', 'R16 cs 0 1k', 'Rq5 pp bm 1Meg', 'C7 pp bm .1u',
          'Bod od bm V={if(V(pp,bm)>2.4 & V(pp,bm)<12, V(pp,bm), 0)}',
          'Boc oc bm V={if(V(pp,bm)>2.0 & V(pp,bm)<4.3, V(pp,bm), 0)}',
          'Mq1a q1d od bm N_FS', 'Mq1b q1d oc 0 N_FS',
          'C3 pp 0 10u', 'Rmon pp 0 2Meg', 'Rleak pp 0 5G', 'Rq8g q8g 0 1m']
    # USB_VBUS source
    if plug is None:
        d += ['Vusb vbus 0 {5*USB}', 'C2 vbus 0 10u']
        usb_on = 'USB>.5'
    else:
        t0, tr = plug['t0'], plug['tr']
        d.append(f'Vusb vsrc 0 PWL(0 0 {t0} 0 {t0 + tr} 5)')
        if cab_l:
            d += [f'Lcab vsrc vx {cab_l}', 'Rcab vx vbus .5']
        else:
            d += ['Rcab vsrc vbus .05']
        d += ['C2 vbus c2m 10u', 'R84 c2m 0 1', 'C25 vbus 0 1u', 'Rvcc vbus 0 100k']
        usb_on = 'V(vbus)>3'
    # 3V3 rail: from the battery before USB, from USB (delayed, ramped) when there is no battery
    if plug is None:
        d.append('B33 v33 0 V={if(USB>.5, 3.3, limit(V(pp)-.2,0,3.3))}')
    else:
        # battery-fed 3V3 stays up through the plug-in; with no battery the TPS2116 + LDO bring it up ~1 ms after VBUS
        d.append(f"B33 v33 0 V={{if(V(pp)>3.4, 3.3, limit((time-{t0}-1m)*3.3/{plug.get('v33_ramp', 200e-6)},0,3.3))}}")
    d.append(f'Bload pp 0 I={{if({usb_on}, 0, LOAD*limit(V(pp)/3,0,1))}}')
    # TP4056: charges when CE is high and VCC is above its UVLO
    # enable = CE above its threshold while VCC is above UVLO, smoothed by a 20 us soft start;
    # trickle (10 %) below 2.9 V, constant current to ~4.1 V, then taper
    d += [f'Benc ench 0 V={{if(V(ce)>{vth_ce} & V(vbus)>3.7, 1, 0)}}', 'Rss ench ench2 1k', 'Css ench2 0 20n',
          'Bchg 0 pp I={.25*V(ench2)*limit((4.2-V(pp))*4,0,1)*if(V(pp)<2.9,.1,1)}']
    # detector (B- referenced) and pass element
    d += ['Rdg bp ng 100k', 'Rdpd ng bm 1Meg', 'Mdet x ng bm N_BSS138',
          f'Rxpu {src} x {r81}', f'Mpass ce x {src} P_AO3401A', f'Rcepd ce 0 {r82}',
          f'Cce ce 0 {cce}']
    if dce:
        d.append('Dce ce vbus DESD')
    if cce_extra:
        d.append(f'Cext ce 0 {cce_extra}')
    if ileak:
        d.append(f'Ileak x bm {ileak}')  # Q9 off-state leakage pulling the gate node down
    if iceleak:
        d.append(f'Iceleak {src} ce {iceleak}')  # Q2 off-state (subthreshold) leakage into CE
    for k, thr in (('10', 1.0), ('15', 1.5), ('20', 2.0), ('35', 3.5)):
        d.append(f'Ben{k} en{k} 0 V={{if(V(ce)>{thr} & V(vbus)>3.7, 1, 0)}}')
    d += [m.replace('{VTH_P}', str(vth_p)).replace('{VTH_N}', str(vth_n)) for m in MODELS]
    if ic:
        d.append('.ic ' + ' '.join(f'V({k})={v}' for k, v in ic.items()))
    d.append(f'.tran 0 {tend} 0 {step}')
    m = [('pp_v', f'FIND V(pp) AT={tmeas}'), ('bm_v', f'FIND V(bm) AT={tmeas}'), ('ce_v', f'FIND V(ce) AT={tmeas}'),
         ('ce_pk', 'MAX V(ce)'), ('x_v', f'FIND V(x) AT={tmeas}'), ('vbus_pk', 'MAX V(vbus)'),
         ('i_chg_end', f'FIND I(Bchg) AT={tmeas}'), ('i_chg_pk', 'MAX I(Bchg)'), ('q_chg', 'INTEG I(Bchg)'),
         ('i_xpu_end', f'FIND I(Rxpu) AT={tmeas}'), ('i_cepd_end', f'FIND I(Rcepd) AT={tmeas}'),
         ('t_en10', 'INTEG V(en10)'), ('t_en15', 'INTEG V(en15)'), ('t_en20', 'INTEG V(en20)'), ('t_en35', 'INTEG V(en35)'),
         ('u5_sup_min', 'MIN V(pp,bm)'), ('i_dsub_max', 'MAX I(Dsub)')]
    if not nobatt:
        m.append(('i_cell_end', f'FIND I(Vcell) AT={tmeas}'))
    for k, v in m:
        d.append(f'.meas tran {k} {v}')
    d.append('.end')
    return '\n'.join(d) + '\n'


def run(name, **kw):
    path = OUT / f'{name}.cir'
    path.write_text(deck(name, **kw))
    try:
        subprocess.run([str(EXE), '-b', str(path)], cwd=OUT, timeout=240, check=True,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired:
        return {'timeout': 1.0}
    raw = path.with_suffix('.log').read_bytes()
    log = raw.decode('utf-16') if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else raw.decode('utf-8-sig', 'replace')
    vals = {mm.group(1).lower(): float(mm.group(2)) for mm in
            re.finditer(r'^([A-Za-z_0-9]+):[^\n=]*=([-+0-9.eE]+)', log, flags=re.M)}
    if not vals:
        print('---- LOG', name, '----'); print(log[-2500:])
    return vals


PLUGS = {
    'usbA_hot_2us_L1u': dict(t0=100e-6, tr=2e-6, cab_l='1u'),
    'ideal_2us': dict(t0=100e-6, tr=2e-6),
    'ideal_100us': dict(t0=100e-6, tr=100e-6),
    'usbC_1ms': dict(t0=100e-6, tr=1e-3),
}
BATS = {'nobatt': dict(VB=0, nobatt=True), 'reversed': dict(VB=-4.2), 'good': dict(VB=3.7)}
VARIANTS = {
    'old_1M_1M': dict(topo='v33'),
    'new_1M_1M': dict(topo='vbus'),
    'new_100k_10k': dict(topo='vbus', r81='100k', r82='10k'),
    'new_1M_1M_+1nF': dict(topo='vbus', cce_extra='1n'),
    'new_100k_10k_+1nF': dict(topo='vbus', r81='100k', r82='10k', cce_extra='1n'),
}

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'static'
    results = {}
    if which == 'leak':
        # reversed cell + USB present (Q9 and Q2 must stay off): sweep off-state leakage and Q2 threshold
        for vn, vk in (('old_1M_1M', dict(topo='v33')), ('new_1M_1M', dict(topo='vbus')), ('new_100k_10k', dict(topo='vbus', r81='100k', r82='10k'))):
            for vp in (-0.5, -0.9):
                for il in ('0', '0.2u', '0.5u', '1u', '2u', '5u'):
                    name = f'L_{vn}_vthp{vp}_q9leak{il}'
                    results[name] = run(name, **vk, VB=-4.2, USB=1, LOAD=0, vth_p=vp, ileak=None if il == '0' else il)
        for vn, vk in (('old_1M_1M', dict(topo='v33')), ('new_1M_1M', dict(topo='vbus')), ('new_100k_10k', dict(topo='vbus', r81='100k', r82='10k'))):
            for il in ('0.1u', '0.3u', '1u', '3u'):
                name = f'L2_{vn}_q2leak{il}'
                results[name] = run(name, **vk, VB=-4.2, USB=1, LOAD=0, vth_p=-0.9, iceleak=il)
        (OUT / 'leak.json').write_text(json.dumps(results, indent=1))
        print(f"{'case':46s}{'ce_v[V]':>10s}{'x_v[V]':>9s}{'i_chg[mA]':>10s}{'charger on?':>13s}")
        for n, r in results.items():
            print(f"{n:46s}{r.get('ce_v', float('nan')):10.4f}{r.get('x_v', float('nan')):9.3f}{r.get('i_chg_end', float('nan')) * 1e3:10.2f}{'YES (Fix 4 defeated)' if r.get('i_chg_end', 0) > 1e-3 else 'no':>13s}")
        sys.exit(0)
    if which == 'plug':
        sel_bats = sys.argv[2].split(',') if len(sys.argv) > 2 else list(BATS)
        for vn, vk in VARIANTS.items():
            for pn, pk in PLUGS.items():
                for bn in sel_bats:
                    name = f'P_{vn}_{pn}_{bn}'
                    results[name] = run(name, **vk, **BATS[bn], USB=1, LOAD=0, plug=pk, tend='6m', tmeas='5.9m', step='50n',
                                        cab_l=pk.get('cab_l'))
        (OUT / 'plug.json').write_text(json.dumps(results, indent=1))
        print(f"{'case':58s}{'ce_pk[V]':>9s}{'t>1.0V':>8s}{'t>1.5V':>8s}{'t>2.0V':>8s}{'t>3.5V':>8s}{'q_chg[uC]':>10s}{'ipk[mA]':>8s}{'ce_end':>7s}")
        for n, r in results.items():
            f = lambda k, sc=1e6: f"{r.get(k, float('nan')) * sc:8.1f}"
            print(f"{n:58s}{r.get('ce_pk', float('nan')):9.2f}{f('t_en10')}{f('t_en15')}{f('t_en20')}{f('t_en35')}{r.get('q_chg', float('nan')) * 1e6:10.1f}{r.get('i_chg_pk', float('nan')) * 1e3:8.1f}{r.get('ce_v', float('nan')):7.2f}")
        sys.exit(0)
    if which == 'static':
        # the repo's Fix 4 matrix, once for the as-built wiring and once for SCH-2 (1M/1M) and SCH-2+ (100k/10k)
        variants = {'asbuilt': dict(topo='v33'), 'sch2': dict(topo='vbus'), 'sch2plus': dict(topo='vbus', r81='100k', r82='10k')}
        cases = {
            'A_discharge_3V7': dict(VB=3.7, USB=0, LOAD=.25),
            'A2_sleep_3V7_noload': dict(VB=3.7, USB=0, LOAD=0),
            'B_charge_3V7': dict(VB=3.7, USB=1, LOAD=0),
            'C_charge_2V5': dict(VB=2.5, USB=1, LOAD=0),
            'C_charge_2V5_vth1V5': dict(VB=2.5, USB=1, LOAD=0, vth_n=1.5),
            'C_charge_2V5_vth1V5_pvth1V3': dict(VB=2.5, USB=1, LOAD=0, vth_n=1.5, vth_p=-1.3),
            'D_reversed_USB': dict(VB=-4.2, USB=1, LOAD=0),
            'E_reversed_hotswap': dict(VB=-4.2, USB=1, LOAD=0, ic={'pp': 4.2}),
            'E2_latched_then_reversed': dict(VB=-4.2, USB=1, LOAD=0, ic={'pp': 4.2, 'bp': 3.5, 'ce': 3.3}),
            'F_nobatt_USB_ppcharged': dict(VB=0, USB=1, LOAD=0, nobatt=True, ic={'pp': 4.2}),
            'G_reversed_noUSB': dict(VB=-4.2, USB=0, LOAD=0),
        }
        for vn, vk in variants.items():
            for cn, ck in cases.items():
                name = f'S_{vn}_{cn}'
                results[name] = run(name, **vk, **ck)
        (OUT / 'static.json').write_text(json.dumps(results, indent=1))
        keys = ['pp_v', 'ce_v', 'x_v', 'i_cell_end', 'i_chg_end', 'i_xpu_end', 'i_cepd_end', 'u5_sup_min']
        print(f"{'case':52s}" + ''.join(f'{k:>12s}' for k in keys))
        for n, r in results.items():
            print(f'{n:52s}' + ''.join(f"{r[k]:12.4g}" if k in r else f"{'-':>12s}" for k in keys))
