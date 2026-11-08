import math, itertools
# Murata NCP18XH103 R-T table (kOhm), -40..125 C step 5 (datasheet txt lines 2944-2977)
tab = [195.652,148.171,113.347,87.559,68.237,53.650,42.506,33.892,27.219,22.021,17.926,14.674,12.081,10.000,
       8.315,6.948,5.834,4.917,4.161,3.535,3.014,2.586,2.228,1.925,1.669,1.452,1.268,1.110,0.974,0.858,0.758,0.672,0.596,0.531]
temps = [-40+5*i for i in range(len(tab))]
def rth(T, r25=1.0, dB=0.0):
    # log-interpolate the table, then apply R25 and B tolerance
    i = min(int((T+40)//5), len(tab)-2)
    t0 = temps[i]; f = (T-t0)/5
    lr = math.log(tab[i])*(1-f) + math.log(tab[i+1])*f
    R = math.exp(lr)*1e3*r25
    Tk = T+273.15
    return R*math.exp(dB*(1/Tk-1/298.15))
def vts(T, r25=1, dB=0, r82=200e3, i=50e-6, ileak=0.0):
    R = rth(T, r25, dB); Rp = R*r82/(R+r82)
    return (i+ileak)*Rp
def solve(target, **kw):
    # TS falls with T: find T where vts == target
    lo, hi = -40.0, 120.0
    for _ in range(80):
        m = (lo+hi)/2
        if vts(m, **kw) > target: lo = m
        else: hi = m
    return (lo+hi)/2
corners = list(itertools.product([0.99,1.01],[-33.8,33.8],[198e3,202e3],[48e-6,53e-6]))
def band(target_lo, target_hi, **extra):
    vals=[]
    for r25,dB,r82,i in corners:
        for tg in (target_lo,target_hi):
            vals.append(solve(tg, r25=r25, dB=dB, r82=r82, i=i, **extra))
    return min(vals), max(vals)
nom = dict(r25=1, dB=0, r82=200e3, i=50e-6)
print("V_TS at 25C nominal = %.3f V; at 0C %.3f; at 45C %.3f" % (vts(25), vts(0), vts(45)))
print("TH1 alone (no R82) nominal: cold stop %.2f C, hot stop %.2f C" % (solve(1.25, r82=1e15), solve(0.275, r82=1e15)))
for name, nomv, lo, hi in [("cold stop (rising V 1.250)",1.250,1.220,1.280),
                           ("cold resume (1.150 = 1.25-0.10)",1.150,1.120,1.180),
                           ("hot stop (falling V 0.275)",0.275,0.260,0.290),
                           ("hot resume (0.295)",0.295,0.280,0.310),
                           ("TTDM enter 1.600",1.600,1.550,1.650),
                           ("foldback 1.475",1.475,1.425,1.525)]:
    b = band(lo, hi)
    print("%-34s nominal %6.2f C  worst band %6.2f .. %6.2f C" % (name, solve(nomv, **nom), b[0], b[1]))
# leakage into TS from a 5 V (USB_VBUS) or 4.2 V (P+) node through R_leak, at several temperatures
print("\nLeakage resistance from 5.0 V that moves TS to the cold threshold (1.22 V) / TTDM (1.55 V):")
for T in (0, 10, 25, 45):
    R = rth(T); Rp = R*200e3/(R+200e3)
    for tgt in (1.22, 1.55):
        # (50uA + (5-V)/Rl)*Rp = V  -> Rl = (5-V)/(V/Rp - 50uA)
        need = tgt/Rp - 50e-6
        rl = (5-tgt)/need if need>0 else float('inf')
        print("  T=%3d C  Rp=%6.0f  target %.2f V -> R_leak <= %8.0f ohm" % (T, Rp, tgt, rl))
# shift of the hot and cold stop points for a 1 uA and 5 uA sink (Q2 leakage) or source
for ia in (-5e-6, -1e-6, 1e-6, 5e-6):
    print("extra current %+.0f uA: cold stop %.2f C, hot stop %.2f C" % (ia*1e6, solve(1.25, ileak=ia), solve(0.275, ileak=ia)))
# Q2 sink needed to force hot fault / disable at 25 C
Rp = rth(25)*200e3/(rth(25)+200e3)
print("\n25C: Q2 sink for TS<0.26 V: %.1f uA; for TS<0.068 V (disable): %.1f uA" % ((50e-6-0.26/Rp)*1e6, (53e-6-0.068/Rp)*1e6))
# TH1 open: R82 alone with fold-back
print("TH1 open: R82 needs %.1f uA at 1.425 V, %.1f uA at 1.525 V (foldback I at 1.525 V = 4..6.5 uA)" % (1.425/200e3*1e6, 1.525/200e3*1e6))
print("R82*I_fldbk max = %.2f V (must stay < 1.55 V TTDM min)" % (6.5e-6*202e3))
# C38 settling
for T in (0, 25, 44):
    R = rth(T); Rp = R*200e3/(R+200e3); tau = Rp*0.22e-6; V = 50e-6*Rp
    print("T=%d: tau=%.2f ms, final %.3f V, time to pass 0.29 V from 0: %.2f ms" % (T, tau*1e3, V, (-tau*math.log(1-0.29/V))*1e3 if V>0.29 else float('nan')))
