"""Re-run the PTC study's lumped model (../../audit-2026-10-29/ptc-thermal/ptc_thermal.py) with board parameters
calibrated by board_thermal_ml.py. See ../BENCH_THEORY.md section 2.4.

Usage: python ptc_rerun.py fth=0.77 kappa=0.38 thba=119 [fth2=0.94 kappa2=... thba2=...]
  fth    the PTC's thermal resistance as a fraction of the datasheet-fitted 325 K/W (the study's "cooling" factor);
  kappa  how much of the board's rise under U10 reaches the PTC;
  thba   the board under U10 to ambient, K/W.
Prints the worst case over the PTC's resistance (0.9, 2.5, 6.0 ohm) for 7 and 10 ohm shorts inside U10 at -20/25/45 C
and 3.0-5.0 V (time to trip / power left in the short / U10's peak), then normal-use failures at 50 % and 100 % light.
"""
import json, math, pathlib, sys

STUDY = pathlib.Path(__file__).resolve().parents[2] / "audit-2026-10-29" / "ptc-thermal"
sys.path.insert(0, str(STUDY))
import ptc_thermal as M  # noqa: E402

P = json.loads((STUDY / "ptc_fit.json").read_text())


def run_case(fth, kappa, thba):
    _, X = M.grid(V=[3.0, 3.4, 3.7, 4.2, 5.0], rf=[7.0, 10.0], r0=[0.9, 2.5, 6.0], ta=[-20.0, 25.0, 45.0],
                  kappa=[kappa], thba=[thba], fth=[fth])
    F = M.simulate_fault(P, X)
    worst = {}
    for j in range(len(X["V"])):
        k = (X["rf"][j], X["ta"][j], X["V"][j])
        t, pe = F["t_trip"][j], F["p_fault_end"][j]
        cur = worst.get(k)
        if cur is None or t > cur[0] or (t == cur[0] and pe > cur[1]):
            worst[k] = (t, pe, F["tj_pk"][j])
    _, Y = M.grid(V=[3.0, 3.4, 3.7, 4.2], duty=[0.5, 1.0], r0=[0.9, 2.5, 6.0], ta=[25.0, 45.0, 60.0],
                  kappa=[kappa], thba=[thba], fth=[fth])
    N = M.simulate_normal(P, Y)
    normal = {}
    for j in range(len(Y["V"])):
        if N["fail"][j]:
            normal.setdefault((Y["duty"][j], Y["ta"][j], Y["V"][j]), []).append("%s@%.1f ohm" % (N["fail"][j], Y["r0"][j]))
    return worst, normal


def show(name, fth, kappa, thba):
    worst, normal = run_case(fth, kappa, thba)
    print("== %s: fth %.2f (theta_p %.0f K/W), kappa %.2f, theta_ba %.0f K/W" % (name, fth, P["theta"] * fth, kappa, thba))
    for rf in (7.0, 10.0):
        print("  short %.0f ohm, worst over R0: time to trip / power left in the short / U10 peak" % rf)
        for ta in (-20.0, 25.0, 45.0):
            cells = []
            for V in (3.0, 3.4, 3.7, 4.2, 5.0):
                t, pe, tj = worst[(rf, ta, V)]
                cells.append(("%5.1f s/%.2f W/%3.0f C" % (t, pe, tj)) if math.isfinite(t) else ("NO TRIP %.2f W/%3.0f C" % (pe, tj)))
            print("    %4.0f C: %s" % (ta, " | ".join(cells)))
    print("  normal use, trip or UVLO (duty, ambient, cell):")
    for k in sorted(normal):
        print("    %.0f %%, %2.0f C, %.1f V: %s" % (k[0] * 100, k[1], k[2], ", ".join(normal[k])))
    if not normal:
        print("    none")


if __name__ == "__main__":
    a = dict(s.split("=") for s in sys.argv[1:])
    show("case 1", float(a.get("fth", 1.0)), float(a.get("kappa", 0.5)), float(a.get("thba", 110)))
    if "fth2" in a:
        show("case 2", float(a["fth2"]), float(a.get("kappa2", a.get("kappa", 0.5))), float(a.get("thba2", a.get("thba", 110))))
