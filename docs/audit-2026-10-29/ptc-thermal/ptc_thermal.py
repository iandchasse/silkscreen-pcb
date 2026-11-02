"""Electro-thermal model of a Bourns MF-FSMF010X-2 PTC protecting the frontlight boost against a shorted U10.

Usage:  python ptc_thermal.py calibrate   (fit the PTC model to the datasheet and print how well it matches)
        python ptc_thermal.py run         (fault and normal-use scenarios -> results.json, tables in results.md)

PTC model (one thermal node):  C_p dT/dt = I^2 R(T) - (T - T_env)/theta_p,
    R(T) = R0 * exp(b (T - 23)) * (1 + K / (1 + exp(-(T - T_m) / w)))
R0 is the part's room-temperature resistance (datasheet spread 0.90-6.00 ohm). b, T_m, w and theta_p are fitted to
the datasheet's hold-current derating table (for the 6.0 ohm part), its 0.30 A trip current (for the 0.9 ohm part)
and its 0.5 W tripped dissipation; C_p is set so the 0.9 ohm part takes the datasheet's maximum 1.0 s to trip at 0.5 A.

Board model: U10 junction (C_j, theta_jb to the board under it), the board under U10 and the PTC (C_b, theta_ba to
ambient), and the PTC's surroundings at T_amb + kappa (T_b - T_amb): kappa is how much of the board's rise under U10
reaches the PTC (0 = far away, 1 = on the same copper as U10). Electrical: the source behind 0.5 ohm (also feeding a
40 mA 3V3 load), the PTC, L2's 0.45 ohm, and the short inside U10 (R_f). Generic estimates, not a measured board.
"""
import itertools, json, math, pathlib, sys

import numpy as np
from scipy.optimize import least_squares

HERE = pathlib.Path(__file__).parent

# ---- datasheet: Bourns MF-FSMF010X (MF-FSMF series sheet) ----
DS = dict(ih=0.10, it=0.30, rmin=0.90, r1max=6.00, vmax=15.0, t_trip_i=0.50, t_trip_s=1.0, pd_tripped=0.5, r_pd=2.0,
          derate={-40: 0.13, -20: 0.12, 0: 0.11, 23: 0.10, 40: 0.08, 50: 0.07, 60: 0.06, 70: 0.05, 85: 0.03})
K_SWITCH = 1e4


def g(T, b, tm, w):
    return np.exp(b * (T - 23.0)) * (1.0 + K_SWITCH / (1.0 + np.exp(-(T - tm) / w)))


def i_runaway(r0, ta, b, tm, w, theta):
    """Largest current with a stable equilibrium below the switch: sqrt(max over T of (T - ta) / (theta r0 g(T)))."""
    T = np.linspace(ta + 0.01, tm + 3 * w, 4000)
    F = (T - ta) / (theta * r0 * g(T, b, tm, w))
    # first local maximum (the low-temperature branch)
    k = np.argmax(np.diff(F) < 0) if np.any(np.diff(F) < 0) else len(F) - 1
    return math.sqrt(max(F[k], 0.0))


def tripped_power(v, r0, b, tm, w, theta, ta=23.0):
    T = np.linspace(tm, tm + 120, 20000)
    resid = v * v / (r0 * g(T, b, tm, w)) - (T - ta) / theta
    k = np.argmax(resid < 0)
    return (T[k] - ta) / theta, T[k]


def fit(ds=None):
    ds = ds or DS
    temps = sorted(ds['derate'])
    r_mid = ds.get('r_pd') or math.sqrt(ds['rmin'] * ds['r1max'])

    def res(p):
        b, tm, w, lt = p
        theta = math.exp(lt)
        r = [math.log(i_runaway(ds['r1max'], t, b, tm, w, theta) / ds['derate'][t]) for t in temps]
        # the lowest-resistance part must run away at or below the trip current (weight it like a derating point)
        r.append(max(0.0, math.log(i_runaway(ds['rmin'], 23, b, tm, w, theta) / ds['it'])) * 3)
        if ds.get('pd_tripped') and ds.get('vmax'):
            pd, _ = tripped_power(ds['vmax'], r_mid, b, tm, w, theta)
            r.append(math.log(pd / ds['pd_tripped']))
        return r

    best = None
    for b0, tm0, w0, th0 in itertools.product((0.005, 0.02), (95, 120), (3, 8), (100, 300, 900)):
        try:
            sol = least_squares(res, [b0, tm0, w0, math.log(th0)],
                                bounds=([0.0, 70, 0.5, math.log(20)], [0.08, 140, 20, math.log(5000)]))
        except Exception:
            continue
        if best is None or sol.cost < best.cost:
            best = sol
    b, tm, w, lt = best.x
    return dict(b=b, tm=tm, w=w, theta=math.exp(lt), cost=best.cost)


def time_to_trip_const_i(i, r0, P, cp, ta=23.0, tmax=60.0, dt=1e-3):
    T = ta
    for n in range(int(tmax / dt)):
        T += dt * (i * i * r0 * g(T, P['b'], P['tm'], P['w']) - (T - ta) / P['theta']) / cp
        if T > P['tm']:
            return (n + 1) * dt
    return float('inf')


def calibrate(ds=None):
    ds = ds or DS
    P = fit(ds)
    # C_p: the slowest part (lowest resistance) trips at the datasheet's test current in its maximum time
    lo, hi = 1e-5, 1.0
    for _ in range(40):
        mid = math.sqrt(lo * hi)
        if time_to_trip_const_i(ds['t_trip_i'], ds['rmin'], P, mid, tmax=ds['t_trip_s'] * 3,
                                dt=min(1e-3, ds['t_trip_s'] / 2000)) > ds['t_trip_s']:
            hi = mid
        else:
            lo = mid
    P['cp'] = lo
    return P


def report_calibration(P):
    print(f"fit: b={P['b']:.4f}/C  T_m={P['tm']:.1f} C  w={P['w']:.2f} C  theta_p={P['theta']:.0f} C/W  "
          f"C_p={P['cp'] * 1e3:.2f} mJ/K  (cost {P['cost']:.3g})")
    print('hold current for the 6.0 ohm part vs ambient (model / datasheet):')
    for t, ih in sorted(DS['derate'].items()):
        print(f"  {t:>4} C: {i_runaway(DS['r1max'], t, P['b'], P['tm'], P['w'], P['theta']):.3f} / {ih:.3f} A")
    print(f"runaway current, 0.9 ohm part, 23 C: {i_runaway(DS['rmin'], 23, P['b'], P['tm'], P['w'], P['theta']):.3f} A "
          f"(datasheet trip 0.30 A)")
    pd, tt = tripped_power(DS['vmax'], 2.0, P['b'], P['tm'], P['w'], P['theta'])
    print(f"tripped at 15 V (2 ohm part): {pd:.2f} W at {tt:.0f} C (datasheet 0.5 W typ)")
    for r0 in (0.9, 2.5, 6.0):
        print(f"time to trip at 0.5 A, {r0} ohm part: {time_to_trip_const_i(0.5, r0, P, P['cp']):.2f} s")


# ---- board ----
R_PATH, I_3V3, R_L2 = 0.5, 0.04, 0.45
THETA_JB, C_J, C_B = 31.6, 3e-3, 0.35      # TPS923610 SOT-563 theta_JB (datasheet); estimates for the rest
T_UVLO = 2.17                                # worst-case falling threshold


def grid(**axes):
    keys = list(axes)
    combos = list(itertools.product(*axes.values()))
    return keys, {k: np.array([c[i] for c in combos], dtype=float) for i, k in enumerate(keys)}


def simulate_fault(P, X, tend=300.0, dt=2e-3):
    """Short of R_f inside U10 from t = 0, everything at ambient. Returns per-scenario metrics."""
    n = len(X['V'])
    ta = X['ta']; Tj = ta.copy(); Tb = ta.copy(); Tp = ta.copy()
    thp = P['theta'] * X['fth']
    vs = X['V'] - R_PATH * I_3V3
    t_trip = np.full(n, np.inf); tj_pk = ta.copy(); tb_pk = ta.copy(); e_f = np.zeros(n); tripped = np.zeros(n, bool)
    i0 = None
    for k in range(int(tend / dt)):
        rp = X['r0'] * g(Tp, P['b'], P['tm'], P['w'])
        i = vs / (R_PATH + rp + R_L2 + X['rf'])
        if i0 is None:
            i0 = i.copy()
        pf, pl, pp = i * i * X['rf'], i * i * R_L2, i * i * rp
        Tj += dt * (pf - (Tj - Tb) / THETA_JB) / C_J
        Tb += dt * (pl + (Tj - Tb) / THETA_JB - (Tb - ta) / X['thba']) / C_B
        tenv = ta + X['kappa'] * (Tb - ta)
        Tp += dt * (pp - (Tp - tenv) / thp) / P['cp']
        # "tripped": the power in the short has fallen below a quarter of its starting value (the PTC is then far up
        # its resistance curve; the model's tripped state sits near 100-115 C, below the fitted T_m)
        now = (~tripped) & (pf < 0.25 * i0 * i0 * X['rf'])
        t_trip[now] = (k + 1) * dt
        tripped |= now
        live = ~tripped
        e_f[live] += pf[live] * dt
        tj_pk = np.maximum(tj_pk, Tj); tb_pk = np.maximum(tb_pk, Tb)
    return dict(i0=i0, t_trip=t_trip, tj_pk=tj_pk, tb_pk=tb_pk, e_fault=e_f, i_end=i, tj_end=Tj, tp_end=Tp, p_ptc_end=pp,
                p_fault_end=pf, p_fault_0=i0 * i0 * X['rf'])


def simulate_normal(P, X, tend=1800.0, dt=1e-2):
    """Light running at a duty (constant input power 0.235 W x duty) for 30 min; looks for a trip or UVLO."""
    n = len(X['V'])
    ta = X['ta']; Tj = ta.copy(); Tb = ta.copy(); Tp = ta.copy()
    thp = P['theta'] * X['fth']
    vs = X['V'] - R_PATH * I_3V3
    pin = 0.235 * X['duty']
    fail = np.full(n, '', dtype=object); t_fail = np.full(n, np.inf)
    i = np.zeros(n)
    for k in range(int(tend / dt)):
        rp = X['r0'] * g(Tp, P['b'], P['tm'], P['w'])
        rt = R_PATH + rp
        disc = vs * vs - 4 * rt * pin
        ok = disc > 0
        i = np.where(ok, (vs - np.sqrt(np.maximum(disc, 0))) / (2 * rt), 0.0)
        vin = vs - i * rt
        loss_u10 = 0.15 * pin * ok
        Tj += dt * (loss_u10 - (Tj - Tb) / THETA_JB) / C_J
        Tb += dt * (i * i * R_L2 + (Tj - Tb) / THETA_JB - (Tb - ta) / X['thba']) / C_B
        tenv = ta + X['kappa'] * (Tb - ta)
        Tp += dt * (i * i * rp - (Tp - tenv) / thp) / P['cp']
        # a trip: the PTC's resistance has run away to 4x its value at ambient (normal use moves it a few %)
        bad = (fail == '') & ((rp > 4 * X['r0'] * np.exp(P['b'] * (ta - 23))) | (vin < T_UVLO) | ~ok)
        for j in np.nonzero(bad)[0]:
            fail[j] = 'UVLO' if (vin[j] < T_UVLO or not ok[j]) else 'trip'
            t_fail[j] = (k + 1) * dt
    return dict(fail=fail, t_fail=t_fail, i_end=i, tp_end=Tp, vin_end=vs - i * (R_PATH + X['r0'] * g(Tp, P['b'], P['tm'], P['w'])))


def as_built(X):
    """No PTC: the short runs until something gives. Steady junction temperature from the same board model."""
    vs = X['V'] - R_PATH * I_3V3
    i = vs / (R_PATH + R_L2 + X['rf'])
    pf = i * i * X['rf']
    return dict(i=i, p_fault=pf, tj_ss=X['ta'] + pf * (THETA_JB + X['thba']) + i * i * R_L2 * X['thba'])


def run():
    P = json.loads((HERE / 'ptc_fit.json').read_text())
    keys, X = grid(V=[3.0, 3.4, 3.7, 4.2, 5.0], rf=[3.0, 7.0, 10.0, 15.0], r0=[0.9, 2.5, 6.0], ta=[-20.0, 25.0, 45.0],
                   kappa=[0.0, 0.25, 0.5, 0.75], thba=[40.0, 110.0], fth=[1.0, 0.6])
    F = simulate_fault(P, X)
    B = as_built(X)
    keysn, Y = grid(V=[3.0, 3.4, 3.7, 4.2, 5.0], duty=[0.5, 1.0], r0=[0.9, 2.5, 6.0], ta=[25.0, 45.0, 60.0],
                    kappa=[0.0, 0.5, 0.75], thba=[40.0, 110.0], fth=[1.0, 0.6])
    N = simulate_normal(P, Y)
    out = dict(params=P, fault=[{**{k: float(X[k][j]) for k in keys}, **{m: (float(v[j]) if not isinstance(v[j], str) else v[j])
                                                                       for m, v in F.items()},
                                 'asbuilt_p': float(B['p_fault'][j]), 'asbuilt_tj': float(B['tj_ss'][j])}
                                for j in range(len(X['V']))],
               normal=[{**{k: float(Y[k][j]) for k in keysn}, 'fail': N['fail'][j], 't_fail': float(N['t_fail'][j]),
                        'i_end': float(N['i_end'][j]), 'tp_end': float(N['tp_end'][j]), 'vin_end': float(N['vin_end'][j])}
                       for j in range(len(Y['V']))])
    def rnd(o):
        if isinstance(o, float):
            return None if math.isinf(o) else float(f'{o:.4g}')
        if isinstance(o, dict):
            return {k: rnd(v) for k, v in o.items()}
        if isinstance(o, list):
            return [rnd(v) for v in o]
        return o

    (HERE / 'results.json').write_text(json.dumps(rnd(out), separators=(',', ':')))
    print(f"fault scenarios: {len(X['V'])}, normal scenarios: {len(Y['V'])}")


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'calibrate'
    if what == 'calibrate':
        P = calibrate()
        (HERE / 'ptc_fit.json').write_text(json.dumps(P, indent=1))
        report_calibration(P)
    elif what == 'run':
        run()
