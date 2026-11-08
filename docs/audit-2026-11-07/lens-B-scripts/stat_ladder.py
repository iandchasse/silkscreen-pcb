import itertools
# USB_STAT node: R70 to 3V3, R67 to CHG (open drain), R17 to ST (open drain), ESP32 pin leakage
# Open drain "low" = voltage source v_ol (0..max) through the resistor; "off" = current sink i_leak into the pin.
def node(v33, r70, r67, r17, chg, st, i_chg, i_st, v_chg, v_st, i_pin):
    G = 1/r70; I = v33/r70 - i_pin
    if chg == 'low': G += 1/r67; I += v_chg/r67
    else: I -= i_chg
    if st == 'low': G += 1/r17; I += v_st/r17
    else: I -= i_st
    return I/G
tol = 0.01
states = {
 'A  USB absent (ST low, CHG off)':            ('off','low'),
 'B  USB good, charging (CHG low, ST off)':    ('low','off'),
 'C  USB good, CHG off (full/no cell/TS/timer)':('off','off'),
 'D  weak USB on cell, charging (both low)':   ('low','low'),
}
for leakmax, label in ((1e-6, 'CHG leakage 0..1 uA (datasheet max, at VCHG=5 V)'), (0.1e-6, 'CHG leakage 0..0.1 uA (plausible typical)')):
    print('---', label)
    for name,(chg,st) in states.items():
        vals=[]
        for v33 in (3.25,3.35):
            for r70,r67,r17 in itertools.product(*[(r*(1-tol), r*(1+tol)) for r in (1e6,510e3,2e6)]):
                for i_chg in (0, leakmax):
                    for i_st in (0, 0.03e-6):
                        for v_chg in (0, 0.05):
                            for v_st in (0, 0.01):
                                for i_pin in (-50e-9, 50e-9):
                                    vals.append(node(v33,r70,r67,r17,chg,st,i_chg,i_st,v_chg,v_st,i_pin))
        nomv = node(3.30,1e6,510e3,2e6,chg,st,0,0,0,0,0)
        print('%-46s nominal %.3f V  band %.3f .. %.3f V' % (name, nomv, min(vals), max(vals)))
print('C23 time constants: B %.0f ms, A %.0f ms, D %.0f ms, C %.0f ms' % tuple(x*0.1e-6*1e3 for x in (1e6*510e3/1.51e6, 1e6*2e6/3e6, 1/(1/1e6+1/510e3+1/2e6), 1e6)))
print('ladder current from 3V3: B %.2f uA, A %.2f uA, D %.2f uA' % (3.3/1.51e6*1e6, 3.3/3e6*1e6, (3.3-0.954)/1e6*1e6))
