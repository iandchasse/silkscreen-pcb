"""Branch PTC studies on top of ptc_thermal.py's PTC model: 3V3 branches fed by U3's current limit (touch J4, J6 pin 7,
microSD) and the battery path (a PTC in place of R27). Usage: python branches.py fit|cheap|sd|battery  (reads
candidates.json, caches fits in candidates_fit.json, writes branches_<mode>.json and prints the tables used in
PROTECTION_FOLLOWUP.md)

Sources
  ldo  : U3 TLV75533P, 3.3 V with a brick-wall limit ICL (0.56 / 0.72 / 0.87 A) above 0.4 x 3.3 V and a foldback to
         I_SC = 0.355 A at 0 V below it (datasheet 6.3.3). Dropout and U3's thermal shutdown are ignored.
  cell : a cell at V behind R_path = 0.40 ohm (cell, Q3, Q8, Q1, U2) with the board's 40 mA awake load downstream of
         the PTC (it flows through it). The short sits on P+, after the PTC.
The PTC's surroundings stay at ambient: in every case here the fault is away from the PTC (in the flex, the accessory,
the card, or 12-19 mm away for the battery path).
"""
import json, math, pathlib

import numpy as np

import ptc_thermal as pt

HERE = pathlib.Path(__file__).parent
ISC, VFB, V33 = 0.355, 1.32, 3.3
ICL = {'min': 0.56, 'typ': 0.72, 'max': 0.87}
R_PATH_BAT, I_BG = 0.40, 0.04


def ldo_current(r_tot, icl):
    """Steady current into r_tot from U3 with brick-wall limit icl and foldback below VFB."""
    i_reg = V33 / r_tot
    i_lim = np.where(icl * r_tot >= VFB, icl, ISC / np.maximum(1 - (icl - ISC) * r_tot / VFB, 1e-6))
    return np.minimum(i_reg, i_lim)


def fault_sim(P, r0, rf, ta, src, tend=120.0, dt=1e-3):
    """Short of rf after the PTC; arrays broadcast. Returns trip time (power in the short below a quarter of its start),
    the power in the short and the PTC temperature at the end, the time 3V3 (ldo) or P+ (cell) spends below a level."""
    r0, rf, ta = np.broadcast_arrays(np.asarray(r0, float), np.asarray(rf, float), np.asarray(ta, float))
    T = ta.copy()
    t_trip = np.full(r0.shape, np.inf); i0 = p0 = None; low_t = np.zeros(r0.shape); e_f = np.zeros(r0.shape)
    for k in range(int(tend / dt)):
        rp = r0 * pt.g(T, P['b'], P['tm'], P['w'])
        if src[0] == 'ldo':
            i = ldo_current(rp + rf, src[1]); v_rail = np.minimum(V33, i * (rp + rf)); pf = i * i * rf
            low = v_rail < 3.0           # the rest of 3V3 (ESP32) is below its 3.0 V minimum
        else:
            v, rs = src[1], R_PATH_BAT + rp
            rfx = np.maximum(rf, 1e-3)
            vp = (v - rs * I_BG) / (1 + rs / rfx); i = vp / rfx + I_BG; pf = vp * vp / rfx
            low = vp < 3.2               # LDO_IN too low for a regulated 3V3
        pp = i * i * rp
        if p0 is None:
            p0, i0 = pf.copy(), i.copy()
        T += dt * (pp - (T - ta) / P['theta']) / P['cp']
        # tripped: current below half its start, i.e. a quarter of the short's starting power (works for rf = 0 too)
        now = np.isinf(t_trip) & (i < 0.5 * i0)
        t_trip[now] = (k + 1) * dt
        live = np.isinf(t_trip)
        e_f[live] += pf[live] * dt; low_t += low * dt
    return dict(t_trip=t_trip, p0=p0, p_end=pf, t_ptc=T, low_s=low_t, e_f=e_f)


def hold_sim(P, r0, i_load, ta, tend=1800.0, dt=0.01):
    """Constant load current through the PTC for tend: final PTC temperature and resistance, and whether it ran away."""
    r0, i_load, ta = np.broadcast_arrays(np.asarray(r0, float), np.asarray(i_load, float), np.asarray(ta, float))
    T = ta.copy()
    for _ in range(int(tend / dt)):
        rp = r0 * pt.g(T, P['b'], P['tm'], P['w'])
        T += dt * (i_load * i_load * rp - (T - ta) / P['theta']) / P['cp']
        T = np.minimum(T, 200.0)
    rp = r0 * pt.g(T, P['b'], P['tm'], P['w'])
    return dict(t_ptc=T, r_ptc=rp, runaway=rp > 4 * r0 * np.exp(P['b'] * (ta - 23)))


def load_candidates(names=None):
    c = json.loads((HERE / 'candidates.json').read_text())
    if names:
        c = {k: v for k, v in c.items() if k in names}
    cache_f = HERE / 'candidates_fit.json'
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
    fits = {}
    for name, ds in c.items():
        ds['derate'] = {int(k): v for k, v in ds['derate'].items()}
        if name == 'MF-FSMF010X-2':
            fits[name] = json.loads((HERE / 'ptc_fit.json').read_text())
        elif name in cache:
            fits[name] = cache[name]
        else:
            fits[name] = {k: float(v) for k, v in pt.calibrate(ds).items()}
            cache[name] = fits[name]
            cache_f.write_text(json.dumps(cache, indent=1))
    return c, fits


RF = np.array([0, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30])
TA = (-20.0, 25.0, 45.0)


def ldo_branch(name, ds, P, tend=120.0):
    """Short at the far end of a 3V3 branch (touch flex, J6 pin 7, card) for both resistance corners, ICL corners, TA."""
    out = []
    for r0 in (ds['rmin'], ds['r1max']):
        for icl_k, icl in ICL.items():
            res = fault_sim(P, r0, RF[:, None], np.array(TA)[None, :], ('ldo', icl), tend=tend)
            for i, rf in enumerate(RF):
                for j, ta in enumerate(TA):
                    out.append(dict(part=name, r0=r0, icl=icl_k, rf=float(rf), ta=ta,
                                    t_trip=float(res['t_trip'][i, j]), p0=float(res['p0'][i, j]),
                                    p_end=float(res['p_end'][i, j]), t_ptc=float(res['t_ptc'][i, j]),
                                    brown_s=float(res['low_s'][i, j]), e_f=float(res['e_f'][i, j])))
    return out


def ldo_hold(name, ds, P, loads):
    out = []
    for r0 in (ds['rmin'], ds['r1max']):
        for ta in (25.0, 45.0, 60.0):
            h = hold_sim(P, r0, np.array(loads), ta)
            for k, il in enumerate(loads):
                out.append(dict(part=name, r0=r0, ta=ta, i=il, r_ptc=float(h['r_ptc'][k]), t_ptc=float(h['t_ptc'][k]),
                                drop=il * float(h['r_ptc'][k]), runaway=bool(h['runaway'][k])))
    return out


def coverage(rows, key=('ta', 'r0')):
    """Per corner: largest short that trips, smallest that does not, and the most power a never-tripped short keeps."""
    corners = {}
    for r in rows:
        corners.setdefault(tuple(r[k] for k in key), []).append(r)
    out = []
    for k, rs in sorted(corners.items()):
        fails = [r for r in rs if not math.isfinite(r['t_trip']) and r['p0'] >= 0.1]
        ok = [r for r in rs if math.isfinite(r['t_trip'])]
        out.append(dict(corner=k, trips_to=max([r['rf'] for r in ok], default=None),
                        gap_from=min([r['rf'] for r in fails], default=None),
                        gap_to=max([r['rf'] for r in fails], default=None),
                        p_untripped=max([r['p0'] for r in fails], default=0.0),
                        t_trip_worst=max([r['t_trip'] for r in ok], default=float('nan'))))
    return out


def battery_fault(name, ds, P, tend=120.0):
    out = []
    for r0 in (ds['rmin'], ds['r1max']):
        for v in (3.4, 3.7, 4.2):
            res = fault_sim(P, r0, RF[:, None], np.array(TA)[None, :], ('cell', v), tend=tend)
            for i, rf in enumerate(RF):
                for j, ta in enumerate(TA):
                    out.append(dict(part=name, r0=r0, v=v, rf=float(rf), ta=ta, t_trip=float(res['t_trip'][i, j]),
                                    p0=float(res['p0'][i, j]), p_end=float(res['p_end'][i, j])))
    return out


def battery_normal(name, ds, P):
    """Sustained current (charging 0.26 A, heavy use 0.25 A) at 25/45/60 C, then a 0.6 A peak on top of that state:
    the lowest cell voltage that still keeps LDO_IN >= 3.2 V at the peak, versus 3.44 V with R27 = 0 ohm today."""
    out = []
    for r0 in (ds['rmin'], ds['r1max']):
        for ta in (25.0, 45.0, 60.0):
            h = hold_sim(P, r0, np.array([0.26]), ta)
            rp = float(h['r_ptc'][0])
            out.append(dict(part=name, r0=r0, ta=ta, r_ptc=rp, runaway=bool(h['runaway'][0]),
                            v_cell_min=3.2 + 0.6 * (R_PATH_BAT + rp)))
    return out


def sd_normal(name, ds, P):
    """Sustained 0.10 A card average at 25/45/60 C, then a 0.20 A burst: SD_VDD = 3.3 - I (R_ptc + 0.1 ohm Q7/trace)."""
    out = []
    for r0 in (ds['rmin'], ds['r1max']):
        for ta in (25.0, 45.0, 60.0):
            h = hold_sim(P, r0, np.array([0.10]), ta)
            rp = float(h['r_ptc'][0])
            out.append(dict(part=name, r0=r0, ta=ta, r_ptc=rp, runaway=bool(h['runaway'][0]),
                            sd_vdd_burst=V33 - 0.20 * (rp + 0.1)))
    return out


def main(argv):
    what = argv[1] if len(argv) > 1 else 'cheap'
    out_f = HERE / f'branches_{what}.json'
    results = {}
    if what == 'fit':
        c, fits = load_candidates()
        for k, f in fits.items():
            ds = c[k]
            print(f"{k:15s} b={f['b']:.4f} tm={f['tm']:.0f} w={f['w']:.1f} theta={f['theta']:.0f} cp={f['cp'] * 1e3:.2f}mJ/K "
                  f"cost={f['cost']:.3f} hold23 model {pt.i_runaway(ds['r1max'], 23, f['b'], f['tm'], f['w'], f['theta']):.2f} "
                  f"vs {ds['derate'].get(23, ds['derate'].get(20)):.2f}")
    if what in ('cheap', 'sd'):
        names = ['MF-FSMF010X-2', 'MF-PSMF010X-2'] if what == 'cheap' else \
            ['MF-FSMF020X-2', 'MF-PSMF020X-2', 'MF-NSMF020X-2', 'MF-FSMF025X-2', 'MF-PSMF035X-2', '1206L035YR']
        c, fits = load_candidates(names)
        res = {}
        for name in names:
            rows = ldo_branch(name, c[name], fits[name])
            cov = coverage(rows)
            normal = ldo_hold(name, c[name], fits[name], [0.005, 0.02, 0.05, 0.08]) if what == 'cheap' \
                else sd_normal(name, c[name], fits[name])
            res[name] = dict(fault=rows, coverage=cov, normal=normal)
            print(f'== {name}')
            for cv in cov:
                print(f"  ta {cv['corner'][0]:5.0f} r0 {cv['corner'][1]:.2f}: trips <= {cv['trips_to']} ohm, gap (>=0.1 W) "
                      f"{cv['gap_from']}..{cv['gap_to']}, untripped P <= {cv['p_untripped']:.2f} W, slowest {cv['t_trip_worst']:.1f} s")
            for n in normal:
                extra = f"SD_VDD@0.2A {n['sd_vdd_burst']:.2f} V" if 'sd_vdd_burst' in n else \
                    f"{n['i'] * 1e3:.0f} mA drop {n['drop'] * 1e3:.0f} mV"
                print(f"  normal ta {n['ta']:.0f} r0 {n['r0']:.2f}: R {n['r_ptc']:.2f} runaway {n['runaway']} {extra}")
        results[what] = res
    if what == 'battery':
        names = ['MF-FSMF050X-2', 'MF-PSMF050X-2', 'MF-PSMF075X-2', 'MF-NSMF075-2', '1206L075THYR', '0805L100WR',
                 '0805L110WR', 'MF-NSMF110-2', '1206L110THYR']
        c, fits = load_candidates(names)
        res = {}
        for name in names:
            rows = battery_fault(name, c[name], fits[name])
            cov = coverage(rows, key=('ta', 'r0', 'v'))
            normal = battery_normal(name, c[name], fits[name])
            res[name] = dict(fault=rows, coverage=cov, normal=normal)
            print(f'== {name}')
            for cv in cov:
                print(f"  ta {cv['corner'][0]:5.0f} r0 {cv['corner'][1]:.2f} V {cv['corner'][2]}: trips <= {cv['trips_to']}, "
                      f"gap (>=0.1 W) {cv['gap_from']}..{cv['gap_to']}, untripped P <= {cv['p_untripped']:.2f} W")
            for n in normal:
                print(f"  normal 0.26 A ta {n['ta']:.0f} r0 {n['r0']:.2f}: R {n['r_ptc']:.3f} runaway {n['runaway']} "
                      f"cell min @0.6 A {n['v_cell_min']:.2f} V")
        results['battery'] = res
    if what != 'fit':
        out_f.write_text(json.dumps(results, separators=(',', ':')))


if __name__ == '__main__':
    import sys
    main(sys.argv)
