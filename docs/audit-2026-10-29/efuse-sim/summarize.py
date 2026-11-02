"""Turns results_*.json into the tables used in BOOST_EFUSE.md. Usage: python summarize.py  (writes summary.md)"""
import collections, contextlib, json, pathlib, re

HERE = pathlib.Path(__file__).parent
J = {g: json.loads((HERE / f'results_{g}.json').read_text()) for g in
     ('threshold', 'normal', 'fault', 'release', 'baseline', 'nuisance', 'variants', 'm2', 'limiter')
     if (HERE / f'results_{g}.json').exists()}
RS = {'A': 2.0, 'M': 2.7, 'B': 3.3}
START_ENVELOPES = ['800mA_0.3ms', '400mA_0.5ms', '400mA_1ms', '200mA_3ms', '100mA_5ms']  # as in run_efuse.py
E_STARTS = ['800mA_0.3mJ', '400mA_0.3mJ', '400mA_0.6mJ', '200mA_0.6mJ']
R_SERIES_EXTRA = 0.5 + 0.08 + 0.45  # source path, M1, L2 DCR (a short on the SW node)


def tripped(r):
    return r.get('vgs_end', -9) > -0.3


def threshold_table():
    th = collections.defaultdict(dict)
    for n, v in J['threshold'].items():
        des, kind, V, T, bj = re.match(r'TH_(\w)_(bat|usb)([\d.]+)_T(-?\d+)_(\w+)', n).groups()
        th[(des, int(T))].setdefault('all', []).append(v['i_at_trip'])
    # M (Rs 2.7 ohm): same trip voltage across Rs as A, so A's currents scaled by 2.0/2.7. Ct does not move the
    # threshold, so A2/M2/B2 share the A/M/B rows.
    for t in (-20, 0, 25, 45, 60, 85):
        th[('M', t)]['all'] = [i * RS['A'] / RS['M'] for i in th[('A', t)]['all']]
    print('## Trip current (A), min-max over BJT models and supplies (M scaled from A by 2.0/2.7)')
    print('| Design | ' + ' | '.join(f'{t} °C' for t in (-20, 0, 25, 45, 60, 85)) + ' |')
    print('|---|' + '---|' * 6)
    for des in 'AMB':
        print(f'| {des} (Rs {RS[des]} Ω) | ' + ' | '.join(
            f"{min(th[(des, t)]['all']):.2f}–{max(th[(des, t)]['all']):.2f}" for t in (-20, 0, 25, 45, 60, 85)) + ' |')
    print()
    print('## Largest SW-node short guaranteed to trip (Ω) and the most an untripped one can dissipate (W)')
    print('| Design | Temp | 3.0 V | 3.4 V | 3.7 V | 4.2 V | 5.0 V (USB) |')
    print('|---|---|---|---|---|---|---|')
    for des in 'AMB':
        for t in (-20, 25, 60):
            imax = max(th[(des, t)]['all'])
            cells = []
            for V in (3.0, 3.4, 3.7, 4.2, 5.0):
                rmax = V / imax - RS[des] - R_SERIES_EXTRA
                cells.append(f'{rmax:.1f} Ω / {imax ** 2 * rmax:.2f} W')
            print(f'| {des} | {t} °C | ' + ' | '.join(cells) + ' |')
    print()


def normal_table():
    N = J['normal']
    print('## Normal operation (25 °C): drop across the fuse, input current, U10 VIN')
    print('| Supply | Duty | As built: I / VIN | A: drop / I / VIN | B: drop / I / VIN |')
    print('|---|---|---|---|---|')
    for k, v in [('bat', 3.0), ('bat', 3.4), ('bat', 3.7), ('bat', 4.2), ('usb', 5.0)]:
        for duty in (50, 100):
            row = []
            for des in ('none', 'A', 'B'):
                r = N[f'N_{des}_{k}{v}_d{duty}']
                if des == 'none':
                    row.append(f"{1e3 * r['irs_end']:.1f} mA / {r['vd_end']:.2f} V")
                else:
                    row.append(f"{1e3 * (r['vin_end'] - r['vd_end']):.0f} mV / {1e3 * r['irs_end']:.1f} mA / {r['vd_end']:.2f} V")
            print(f'| {k} {v} V | {duty} % | ' + ' | '.join(row) + ' |')
    print()
    for n, r in N.items():
        if 'idle' in n:
            print(f"- {n}: fuse ground current {1e9 * r.get('iq_fuse', 0):.2f} nA, LED_MONIT {r['vmon_end']:.3f} V")
    print()


def fault_tables():
    F = J['fault']
    print('## SW-node short at 25 °C (light off): trip delay / peak current / energy into the short')
    sup = [('bat', 3.0), ('bat', 3.4), ('bat', 3.7), ('bat', 4.2), ('usb', 5.0)]
    for des in 'AB':
        print(f'### Design {des}')
        print('| Short | ' + ' | '.join(f'{v} V' for _, v in sup) + ' |')
        print('|---|' + '---|' * len(sup))
        for R in [0.05, 0.5, 1, 2, 3, 5, 7, 8, 10, 12, 15, 20, 30]:
            cells = []
            for k, v in sup:
                r = F[f'F_{des}_sw_{k}{v}_R{R}']
                if tripped(r):
                    cells.append(f"{1e3 * (r['t_off'] - 0.01):.1f} ms / {r['irs_pk']:.2f} A / {1e3 * r['e_fault']:.1f} mJ")
                else:
                    cells.append(f"**no trip**: {1e3 * r['ifault_end']:.0f} mA, {r['ifault_end'] ** 2 * R:.2f} W")
            print(f'| {R} Ω | ' + ' | '.join(cells) + ' |')
        print()
    print('## Other fault cases')
    for n, r in F.items():
        if re.match(r'F_\w_sw_(bat|usb)[\d.]+_R[\d.]+$', n):
            continue
        t0 = 0 if n.startswith('F0') else 0.01
        s = f"trips in {1e3 * (r['t_off'] - t0):.2f} ms" if tripped(r) else f"**no trip**, {1e3 * r['ifault_end']:.0f} mA"
        print(f"- {n}: {s}; peak {r['irs_pk']:.2f} A; {1e3 * r['e_fault']:.2f} mJ into the short; LDO_IN min "
              f"{r['vin_min']:.2f} V; latched draw {1e6 * r.get('iq_fuse', 0):.1f} µA")
    print()
    B = J['baseline']
    print('## As built (no fuse), same shorts')
    for n, r in B.items():
        if '_sw_' in n:
            print(f"- {n}: {1e3 * r['ifault_end']:.0f} mA continuous ({r['ifault_end'] ** 2 * float(n.split('_R')[1]):.2f} W); LDO_IN {r['vin_min']:.2f} V")
    print()


def release_table():
    print('## Latch release (latched at 3.7 V, fault removed, LDO_IN pulled to v_low for 50 ms)')
    for n, r in J['release'].items():
        print(f"- {n}: {'released' if r['vgs_end'] < -0.3 else 'still latched'}")
    print()


def nuisance_tables():
    if 'nuisance' not in J:
        return
    U = J['nuisance']
    bad = [n for n, r in U.items() if tripped(r)]
    print(f'## Nuisance runs: {len(U)}, latched: {len(bad)}')
    for n in bad:
        print(f'- LATCHED: {n}')
    groups = collections.defaultdict(list)
    for n, r in U.items():
        groups[n.split('_')[0] + '_' + n.split('_')[1]].append((n, r))
    print('Groups: U = power-up from 0 V (soft-start and 10 µs), P = USB plug-in with a cell, Q = USB unplug '
          'with a cell, S = one light start, R = five light starts 10 ms apart.\n')
    print('| Group | Design | Worst delay-node peak (trip ≈ 0.46 V) | Worst U10 VIN (V) |')
    print('|---|---|---|---|')
    for g, items in sorted(groups.items()):
        vt = max(r.get('vt_pk', 0) for _, r in items)
        vd = min(r.get('vd_min', 9) for _, r in items if r.get('vd_min') is not None)
        vds = '(power-up from 0 V)' if g.startswith('U_') else f'{vd:.2f}'
        print(f'| {g.split("_")[0]} | {g.split("_")[1]} | {vt:.3f} | {vds} |')
    print()
    print('## Light start-up: lowest U10 VIN (V) and whether the light ran to the end (worst over temperature and BJT corner)')
    sup = ['bat3.0', 'bat3.4', 'bat3.7', 'bat4.2', 'usb5.0']
    envs = ['800mA_0.3ms', '400mA_0.5ms', '400mA_1ms', '200mA_3ms', '100mA_5ms']
    for des in 'AB':
        print(f'### Design {des}')
        print('| Start envelope | ' + ' | '.join(sup) + ' |')
        print('|---|' + '---|' * len(sup))
        for e in envs:
            cells = []
            for s in sup:
                rs = [r for n, r in U.items() if n.startswith(f'S_{des}_') and n.endswith(f'_{s}_{e}')]
                vd = min(r['vd_min'] for r in rs)
                ok = min(r.get('on_frac', 0) for r in rs)
                lat = any(tripped(r) for r in rs)
                cells.append(f"{vd:.2f} V{' UVLO' if vd < 2.17 else ''}{' LATCH' if lat else ''}{'' if ok > 0.99 else f' (on {100 * ok:.0f} %)'}")
            print(f'| {e} | ' + ' | '.join(cells) + ' |')
        print()


def variants_tables():
    if 'variants' not in J:
        return
    V = J['variants']
    sup = ['bat3.0', 'bat3.4', 'bat3.7', 'bat4.2', 'usb5.0']
    envs = ['800mA_0.3ms', '400mA_0.5ms', '400mA_1ms', '200mA_3ms', '100mA_5ms']
    print('# Longer-delay variants (Ct 470 nF): A2 = 2.0 Ω, M2 = 2.7 Ω, B2 = 3.3 Ω')
    for des in ('A2', 'M2', 'B2'):
        print(f'## {des}: light start-up, lowest U10 VIN, worst over −20/25/60 °C and BJT corner')
        print('| Start envelope | ' + ' | '.join(sup) + ' |')
        print('|---|' + '---|' * len(sup))
        for e in envs + ['5x400mA_0.5ms']:
            cells = []
            for s in sup:
                pre = 'R' if e.startswith('5x') else 'S'
                rs = [r for n, r in V.items() if n.startswith(f'{pre}_{des}_') and n.endswith(f'_{s}_{e}')]
                vd = min(r['vd_min'] for r in rs)
                ok = min(r.get('on_frac', 0) for r in rs)
                lat = sum(tripped(r) for r in rs)
                vt = max(r.get('vt_pk', 0) for r in rs)
                cells.append(f"{vd:.2f} V{' UVLO' if vd < 2.17 else ''}"
                             f"{f' LATCH {lat}/{len(rs)}' if lat else f' (T {vt:.2f} V)'}"
                             f"{'' if ok > 0.99 or lat or e.startswith('5x') else f' on {100 * ok:.0f} %'}")
            print(f'| {e} | ' + ' | '.join(cells) + ' |')
        print()
        print(f'## {des}: SW-node shorts, trip delay / energy into the short / energy in Rs (worst over corners)')
        print('| Short | Temp | ' + ' | '.join(sup) + ' |')
        print('|---|---|' + '---|' * len(sup))
        for R in (0.05, 0.5, 3, 7, 10, 12):
            for t in (-20, 25, 60):
                cells = []
                for s in sup:
                    r = V[f'F_{des}_sw_{s}_R{R}_T{t}']
                    if tripped(r):
                        cells.append(f"{1e3 * (r['t_off'] - 0.01):.1f} ms / {1e3 * r['e_fault']:.0f} mJ / {1e3 * r['e_rs']:.0f} mJ")
                    else:
                        cells.append(f"**no trip** {1e3 * r['ifault_end']:.0f} mA")
                print(f'| {R} Ω | {t} °C | ' + ' | '.join(cells) + ' |')
        print()


def m2_tables():
    if 'm2' not in J:
        return
    M = J['m2']
    print('# M2 (Rs 2.7 Ω, Ct 470 nF): checks beyond the variants group')
    nu = {n: r for n, r in M.items() if n[:2] in ('U_', 'P_', 'Q_')}
    print(f"- Supply events (power-up, USB plug-in/unplug; −20/25/60 °C; nom/lo): {len(nu)} runs, "
          f"{sum(tripped(r) for r in nu.values())} latched, worst delay-node peak {max(r.get('vt_pk', 0) for r in nu.values()):.3f} V, "
          f"lowest U10 VIN on plug/unplug {min(r['vd_min'] for n, r in nu.items() if n[0] in 'PQ'):.2f} V")
    print('\n| Supply | Duty | Drop | Input current | U10 VIN |\n|---|---|---|---|---|')
    for n, r in M.items():
        m = re.match(r'N_M2_(bat|usb)([\d.]+)_d(\d+)', n)
        if m:
            print(f"| {m.group(1)} {m.group(2)} V | {m.group(3)} % | {1e3 * (r['vin_end'] - r['vd_end']):.0f} mV | "
                  f"{1e3 * r['irs_end']:.1f} mA | {r['vd_end']:.2f} V |")
    print()
    for n, r in M.items():
        if 'idle' in n:
            print(f"- {n}: fuse ground current {1e9 * r['iq_fuse']:.2f} nA, LED_MONIT {r['vmon_end']:.3f} V")
    print('\n| Fault | Result | Peak | Into the short | In Rs | LDO_IN min | Latched draw |\n|---|---|---|---|---|---|---|')
    for n, r in M.items():
        if n.startswith('F'):
            t0 = 0 if n.startswith('F0') else 0.01
            s = f"trips in {1e3 * (r['t_off'] - t0):.1f} ms" if tripped(r) else f"**no trip**, {1e3 * r['ifault_end']:.0f} mA"
            vmin = f"{r['vin_min']:.2f} V" if not n.startswith('F0') else '(power-up)'
            print(f"| {n} | {s} | {r['irs_pk']:.2f} A | {1e3 * r['e_fault']:.1f} mJ | {1e3 * r['e_rs']:.1f} mJ | {vmin} | "
                  f"{1e6 * r.get('iq_fuse', 0):.0f} µA |")
    print('\n- Release: ' + ', '.join(f"{n.split('vlow')[1]} V {'released' if r['vgs_end'] < -0.3 else 'latched'}"
                                       for n, r in M.items() if n.startswith('L_')))
    print()


def limiter_tables():
    if 'limiter' not in J:
        return
    L = J['limiter']
    sup = ['bat3.0', 'bat3.4', 'bat3.7', 'bat4.2', 'usb5.0']
    print('# 4-part current limiter: L22 / L27 / L33 = Rs 2.2 / 2.7 / 3.3 Ω (Rs, AO3401A, MMBT3906, 1 MΩ)')
    print('## Limit current (A), min–max over BJT models and supplies')
    print('| Design | −20 °C | 25 °C | 60 °C | 85 °C |\n|---|---|---|---|---|')
    for des in ('L22', 'L27', 'L33'):
        cells = []
        for t in (-20, 25, 60, 85):
            v = [r['irs_end'] for n, r in L.items() if n.startswith(f'TH_{des}_') and f'_T{t}_' in n]
            cells.append(f'{min(v):.3f}–{max(v):.3f}')
        print(f'| {des} | ' + ' | '.join(cells) + ' |')
    print('\n## Normal operation (25 °C): drop / input current / U10 VIN')
    print('| Supply | Duty | L22 | L27 | L33 |\n|---|---|---|---|---|')
    for s in sup:
        k, v = s[:3], s[3:]
        for duty in (50, 100):
            cells = []
            for des in ('L22', 'L27', 'L33'):
                r = L[f'N_{des}_{k}{v}_d{duty}']
                ok = '' if r['on_end'] > 0.5 else ' **light off**'
                cells.append(f"{1e3 * (r['vin_end'] - r['vd_end']):.0f} mV / {1e3 * r['irs_end']:.1f} mA / {r['vd_end']:.2f} V{ok}")
            print(f'| {k} {v} V | {duty} % | ' + ' | '.join(cells) + ' |')
    for n, r in L.items():
        if 'idle' in n:
            print(f"- {n}: gate pull-down current {1e9 * r['iq_lim']:.2f} nA, LED_MONIT {r['vmon_end']:.3f} V")
    print('\n## Sustained SW-node short, steady state (25 °C): current / power in M1 / power in the short')
    for des in ('L22', 'L27', 'L33'):
        print(f'### {des}')
        print('| Short | ' + ' | '.join(sup) + ' |\n|---|' + '---|' * len(sup))
        for R in (0.05, 0.5, 1, 2, 3, 5, 7, 10, 15, 20):
            cells = []
            for s in sup:
                r = L[f'F_{des}_sw_{s}_R{R}']
                osc = ' (osc)' if r['irs_max_tail'] - r['irs_min_tail'] > 0.01 else ''
                cells.append(f"{1e3 * r['irs_end']:.0f} mA / {r['p_fet_end']:.2f} W / {r['p_fault_end']:.2f} W{osc}")
            print(f'| {R} Ω | ' + ' | '.join(cells) + ' |')
        print()
        w = [(r['p_fet_end'], n) for n, r in L.items() if n.startswith(f'F_{des}_')]
        pk = max((r['p_fet_pk'], n) for n, r in L.items() if n.startswith(f'F_{des}_'))
        wf = max((r['p_fault_end'], n) for n, r in L.items() if n.startswith(f'F_{des}_'))
        print(f'- worst steady M1 power: {max(w)[0]:.2f} W ({max(w)[1]}); worst transient {pk[0]:.2f} W ({pk[1]}); '
              f'worst power in the short {wf[0]:.2f} W ({wf[1]})')
        osc = [n for n, r in L.items() if n.startswith(f'F_{des}_') and r['irs_max_tail'] - r['irs_min_tail'] > 0.01]
        print(f'- oscillating in the last 2 ms: {osc if osc else "none"}')
        for node in ('d', 'ledsw'):
            for n, r in L.items():
                if n.startswith(f'F_{des}_{node}_'):
                    print(f"- {n}: {1e3 * r['irs_end']:.0f} mA, M1 {r['p_fet_end']:.2f} W, short {r['p_fault_end']:.2f} W")
        print()
    print('## Supply events (25 °C): peak current into the branch / lowest U10 VIN')
    for des in ('L22', 'L27', 'L33'):
        for g, lab in (('U_', 'power-up'), ('P_', 'USB plug-in'), ('Q_', 'USB unplug')):
            rs = [(n, r) for n, r in L.items() if n.startswith(f'{g}{des}_')]
            vd = '' if g == 'U_' else f", lowest U10 VIN {min(r['vd_min'] for _, r in rs):.2f} V"
            print(f"- {des} {lab}: peak {min(r['irs_pk'] for _, r in rs):.2f}–{max(r['irs_pk'] for _, r in rs):.2f} A{vd}")
    print('\n## Light start-up: does the light end up running? (lowest U10 VIN; % of time on after enable)')
    print('Time model: the start current is drawn for a fixed time after every (re)start. Energy model: it is drawn '
          'until the energy to charge C9 has gone in, and that progress survives a UVLO restart.\n')
    for des in ('L22', 'L27', 'L33'):
        print(f'### {des} (worst of 25 °C nominal and 60 °C low-V_BE)')
        print('| Start | ' + ' | '.join(sup) + ' |\n|---|' + '---|' * len(sup))
        for pre, envs in (('S', START_ENVELOPES), ('E', E_STARTS)):
            for e in envs:
                cells = []
                for s in sup:
                    rs = [r for n, r in L.items() if n.startswith(f'{pre}_{des}_') and n.endswith(f'_{s}_{e}')]
                    to = sum(1 for r in rs if 'timeout' in r)
                    rs = [r for r in rs if 'on_end' in r]
                    run_ok = all(r['on_end'] > 0.5 for r in rs)
                    vd = min(r['vd_min'] for r in rs)
                    of = min(r.get('on_frac', 0) for r in rs)
                    cells.append(f"{'runs' if run_ok else '**stuck**'}, {vd:.2f} V, {100 * of:.0f} %"
                                 f"{f' ({to} run timed out)' if to else ''}")
                lab = ('time ' if pre == 'S' else 'energy ') + e
                print(f'| {lab} | ' + ' | '.join(cells) + ' |')
        print()


if __name__ == '__main__':
    with open(HERE / 'summary.md', 'w', encoding='utf-8') as f, contextlib.redirect_stdout(f):
        print('# E-fuse simulation summary (generated by summarize.py from results_*.json)\n')
        threshold_table()
        normal_table()
        fault_tables()
        release_table()
        nuisance_tables()
        variants_tables()
        m2_tables()
        limiter_tables()
