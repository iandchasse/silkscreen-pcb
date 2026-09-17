"""Cross-reference every ordered component with the freshly exported netlist."""
import pathlib,json,xml.etree.ElementTree as E,csv,re,collections,itertools,math
out=pathlib.Path(__file__).parent;root=out.parents[1]
components={c.attrib['ref']:c for c in E.parse(out/'netlist.xml').findall('./components/comp')}
board=json.loads((out/'board.json').read_text());footprints={f['ref']:f for f in board['footprints']}
upload=list(csv.DictReader((root/'production/bom_JLC_upload.csv').open(encoding='utf-8-sig')))
saved={ref:r for r in upload for ref in r['Designator'].split(',')}
rows=json.loads((out/'order-bom.json').read_text())[5:]
ordered={ref:r for r in rows if r[0] for ref in r[0].split(',')}
findings={
 'Q4':'HOLD on existing BSS138. Preferred replacement: genuine Infineon IRLML6346TRPBF C67276, SOT-23 G1/S2/D3; 80mohm max at 2.5V and 2.9nC typical gate charge. Split from Q5/Q6; verify panel-driven VGS/VDS/current waveforms. See root DESIGN_REVIEW.md section 7.',
 'Q5':'Reasonable for 15mA color selection; do not apply Q4 boost-switch judgement to this low-current role.',
 'Q6':'Reasonable for 15mA color selection. Inversion does not guarantee transient exclusivity; measure branch current during color changes. ADIM PWM low phases do not guarantee zero current.',
 'D2':'HOLD if unchanged: saved order is reverse mount. User requested C28310439; factory approval/current BOM not available locally.',
 'L2':'Order is C88528 HBX-4R7M-1; upload is C413592 HBU-4R7M. Both 4.7uH, but release record must specify the actual part.',
 'R37':'Existing 13.3 ohm 1%: 14.52..15.65mA at full scale. Recommend common 15 ohm 1% 0603 (C22810): 13.33mA nominal, 13.87mA upper from VFB/R tolerances; not yet substituted. 15 ohm 5% also stays below 15mA before drift/transients.',
 'R14':'3 ohm / 0.1W sense resistor; verify pulse/RMS heating. Full-rated continuous RMS is 183mA; not peak-current limit.',
 'CR1':'SD05C rated 5.0V stand-off on USB VBUS; use 5.5V-rated alternative or confirm leakage over allowed source maximum.',
 'CR2':'5V TVS on 3.3V rail: no normal-DC stress; surge clamp is not a precision 3.3V overvoltage limit.',
 'CR3':'5V TVS on <=4.2V battery rail: no normal-DC stress; surge clamp not a battery overcharge controller.',
 'U3':'500mA SOT-23-5 LDO; require load/thermal measurement at 5V USB with WiFi+SD+display.',
 'U2':'TPS2116: VIN1=MODE=USB_VBUS, VIN2=P+, PR1=300k/100k divider; 4V nominal threshold, 3.625..4.385V including reference/resistor tolerance. Measure hot-plug and source transitions.',
 'Q7':'PMOS SD gate: source 3V3, drain SD_VDD, external gate pull-up. LOW on; high or high-Z without internal pulls off. Stop bus and avoid signal back-power before switching off.',
 'U5':'USB-present reverse-battery concern: supply can be forced negative through Q8-on/Q3-body-diode path. VCC=P+, GND=B-. No reference series VCC filter; sensing includes PMOS drops. See DESIGN_REVIEW.md section 4.',
 'Q3':'Source=B+, gate referenced to B-. When USB enhances Q8, Q3 body diode can conduct into reversed cell even with Q3 channel off; reverse-insertion safety is not established.',
 'Q8':'Source=P+, gate=GND. Charger can enhance it independently of battery polarity, defeating the assumed reverse blocking with Q3. Redesign/validate or restrict prototype battery handling.',
 'Q1':'TECH PUBLIC 6-pin FS8205A pinout checked against manufacturer drawing; common-drain pins 2/5 internal.',
 'U4':'N16R8 order: leave GPIO35/36/37 unused (source does). Boot strap GPIO3/45/46 exposed on header.',
 'U11':'R6=4.7k: ordered sheet formula gives 234mA; its low-current example table differs. About 0.25A intended; measure actual. TEMP grounded.',
 'U12':'Exact MDD drawing verified: NC1 A2 GND3 Y4 VCC5, compatible at 3.3V. Static complementary logic does not guarantee nonoverlap during Q5/Q6 switching.',
 'U10':'TPS923610 ADIM first high >40us, then recommended 10..200kHz dimming; low >2.5ms shutdown/latch reset. Shutdown retains input/output diode path. Qualify color-change stored-energy pulses; 25V typical OVP.',
 'C22':'1uF connected to 3V3, but 51.84mm from U4 supply pad near panel; not MCU-local or RTC decoupling. RTC bypass is C30.',
 'J1':'GCT THT USB-C; verify connector soldering included in JLC scope. Tight pad gaps are footprint geometry, not unrouted shorts.',
 'J2':'24-pin electrical mapping checked; confirm actual FPC thickness/contact orientation and panel variant.',
 'J3':'User confirms physical FT01C sample matches schematic: C+,C-,NC,NC,W+,W-. Supplier drawing conflicts; no wiring change recommended for this sample. A unit following drawing would reverse-bias selected LED string; boost can reach OVP and damage LEDs. Retain lot/FPC check.',
 'J4':'Default links give GND,3V3,RST,INT,SDA,SCL. Mutually exclusive alternative links must stay DNP.',
 'J5':'CJT 2mm right-angle connector in JST-PH footprint; pin1 B-, pin2 B+. Verify cable polarity and factory THT scope.',
 'J6':'CJT right-angle 2x6 female header; high voltage LED rail and boot straps exposed; do not treat as generic GPIO header.',
 'J7':'TF PUSH: matching data pin order, but peg-hole Y offset 0.22mm at nominal pad alignment. Assembly fit confirmation required.',
 'D3':'Actual unidirectional SMAJ26A, pad1 cathode on LED output. 42.1V surge clamp does not guarantee IC protection.',
 'D8':'Exact TECH PUBLIC 24V bidirectional drawing verified: signal1/2 common3, compatible. Not a precision 3.3V clamp or system ESD certification.',
 'L1':'22uH TDK in Bourns-named footprint; ratings reasonable; panel waveform/reference 47uH differs and needs qualification.',
 'F1':'1A hold at 20C derates to about 0.65A at 60C/0.55A at 70C. Qualify full USB workload/temperature/drop; no USB current negotiation.',
 'R27':'Zero-ohm battery path: check jumper current rating and voltage drop in first-article load test.',
}
for ref in ['U1','U6','U7','U8','U9']:findings[ref]='Exact TECH PUBLIC TPD4E1U06DBVR sheet verified: independent signal pins 1/3/4/6, GND2, NC5; assignments compatible. Pin compatibility is not identical TI performance or system ESD certification.'
for ref in ['D4','D5','D6']:findings[ref]='40V B5819W charge-pump diode polarity/topology checked; qualify reverse overshoot and hot leakage during panel startup/refresh.'
for ref in ['C4','C6','C32']:findings[ref]='22uF/25V X5R CCTC matches nominal value/package. Effective capacitance at bias and temperature not established from catalog.'
for ref in ['C11','C13','C14','C15','C16','C17']:findings[ref]='4.7uF/50V X5R retained for e-paper high-voltage nodes; verify effective capacitance under DC bias.'
for ref in ['C9','C18','C19','C20']:findings[ref]='1uF/50V X7R retained. C9 needs sufficient effective output capacitance for LED converter.'
for ref in ['SW1','SW2','SW3','SW4','SW5','SW7','SW8','SW9','SW10','SW11']:findings[ref]='TS365ZJ: 5mm signal pitch and 7mm bracket pitch match board holes; housing/actuator enclosure fit is separate.'
def scalar(s):
 s=s.split('/')[0].strip().replace('µ','u')
 m=re.fullmatch(r'([0-9.]+)([pnumkM]?)',s)
 return float(m[1])*{'':1,'p':1e-12,'n':1e-9,'u':1e-6,'m':1e-3,'k':1e3,'M':1e6}[m[2]] if m else None
passive_errors=[];seen=[];result=[]
for r in rows:
 if not r[0]:continue
 refs=r[0].split(',');seen+=refs
 no_part=r[5]=='No Part Selected'
 for ref in refs:
  c=components.get(ref);value=c.findtext('value') if c is not None else 'MISSING'
  checked='not applicable'
  if ref.startswith(('R','C','L')) and not ref.startswith('CR') and not no_part:
   unit='Ω' if ref.startswith('R') else ('F' if ref.startswith('C') else 'H')
   matches=re.findall(r'(?<![A-Za-z0-9.])([0-9.]+)([pnumkMµ]?)'+unit,str(r[8]))
   vals=[scalar(n+k) for n,k in matches];expected=scalar(value)
   checked='match' if any(math.isclose(expected,v,rel_tol=1e-8) for v in vals) else 'CHECK'
   if checked=='CHECK':passive_errors.append([ref,value,r[8]])
  note=findings.get(ref,'Nominal value/package and connected role reviewed; see block-coverage.csv and root DESIGN_REVIEW.md for operating limits.')
  if no_part:note='Explicitly unselected in order. Set source DNP flag for reproducibility; bare pads remain useful.'
  result.append({'Ref':ref,'Schematic value':value,'Ordered MPN':r[5] or '', 'Manufacturer':r[6] or '', 'Ordered LCSC':r[11] or '', 'Upload LCSC':saved.get(ref,{}).get('JLCPCB Part #',''),'Population':'DNP' if no_part else 'FIT','PCB DNP flag':footprints.get(ref,{}).get('dnp','missing'),'Passive value check':checked,'Review':note,'Order description':r[8] or ''})
for ref,c in components.items():
 if ref in ordered:continue
 expected=ref.startswith(('H','TP')) or footprints.get(ref,{}).get('dnp',False)
 result.append({'Ref':ref,'Schematic value':c.findtext('value'),'Ordered MPN':'','Manufacturer':'','Ordered LCSC':'','Upload LCSC':saved.get(ref,{}).get('JLCPCB Part #',''),'Population':'MECHANICAL/BARE PAD' if ref.startswith(('H','TP')) else 'DNP','PCB DNP flag':footprints.get(ref,{}).get('dnp','missing'),'Passive value check':'not applicable','Review':'Expected order exclusion' if expected else 'UNEXPLAINED EXCLUSION','Order description':''})
result.sort(key=lambda r:(re.match(r'[A-Z]+',r['Ref'])[0],int(re.search(r'\d+',r['Ref'])[0])))
with (out/'component-review.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
summary={'schematic_refs':len(components),'order_rows':sum(bool(r[0]) for r in rows),'duplicate_order_refs':[r for r,n in collections.Counter(seen).items() if n>1],'order_refs_missing_schematic':sorted(set(ordered)-set(components)),'passive_value_errors':passive_errors,'counts':dict(collections.Counter(r['Population'] for r in result)),'unexplained_exclusions':[r['Ref'] for r in result if r['Review']=='UNEXPLAINED EXCLUSION'],'dnp_flag_disagreements':[r['Ref'] for r in result if r['Population']=='DNP' and not r['PCB DNP flag']],'lcsc_disagreements':[{'ref':r['Ref'],'upload':r['Upload LCSC'],'order':r['Ordered LCSC']} for r in result if r['Population']=='FIT' and r['Ordered LCSC']!=r['Upload LCSC']]}
(out/'bom-verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
def ladder(active,pullup=100000,supply=3.3):return supply/(1+pullup*sum(1/r for r in active))
state_defs={'USB idle/no active status':[], 'battery selected':[150000], 'USB charging':[56000], 'USB charged':[22000], 'weak USB; battery selected and charging':[150000,56000], 'weak USB; battery selected and charged':[150000,22000]}
analog={}
for name,rs in state_defs.items():
 vals=[ladder([r*t for r,t in zip(rs,tols)],100000*tup) for tols in itertools.product([.99,1.01],repeat=len(rs)) for tup in [.99,1.01]]
 analog[name]={'nominal_V':ladder(rs),'resistor_only_min_V':min(vals),'resistor_only_max_V':max(vals)}
buttons={}
for name,rs in {'BUTTON_ADC_1':[100,5600,20000,56000],'BUTTON_ADC_2':[100,12000,33000,68000]}.items():
 buttons[name]=[{'resistor_ohm':r,'nominal_V':ladder([r],10000)} for r in rs]
limits={'USB_STAT':analog,'USB_STAT_limitations':'Ideal low outputs; fixed 3.3V supply; only resistor tolerance included. ADC error, supply error, status output VOL/leakage excluded. Not production firmware thresholds. Weak-source near-full states can overlap after real errors.','buttons_single_press':buttons,'mux_threshold_V':{'nominal':4,'min':.92*(1+300000*.99/(100000*1.01)),'max':1.08*(1+300000*1.01/(100000*.99))},'LED_current_mA':{'nominal':200/13.3,'min':195/(13.3*1.01),'max':206/(13.3*.99),'14.3ohm_max':206/(14.3*.99)},'LDO_power_at_5V_W':{str(i):1.7*i for i in [.15,.25,.35,.4,.5]},'RC_time_s':{'BAT_MONIT':500000*1e-6,'LED_MONIT':1/(1/1e6+1/120000)*.1e-6,'SD_VDD_bleeder_no_card':100000*1.1e-6}}
limits['LED_current_alternatives']=[
 {'R_ohm':r,'R_tolerance_fraction':tol,'nominal_mA':200/r,
  'min_mA':195/(r*(1+tol)),'max_mA':206/(r*(1-tol)),
  'max_resistor_power_mW':.206**2/(r*(1-tol))*1000}
 for r,tol in [(13.3,.01),(14.3,.01),(15,.01),(15,.05),(16,.01),(18,.01),(18,.05),(22,.01)]]
limits['LED_current_alternatives_limitations']='Steady full-scale VFB=195..206mV and initial resistor tolerance. Excludes resistor drift, aging and transients. Optional 15 ohm / 1% / 100ppm per C temperature example below is a bounded calculation, not a board measurement.'
limits['LED_15ohm_1pct_100ppm_60C_delta_upper_mA']=206/(15*.99*(1-100e-6*60))
limits['Q4_source_degenerated_drive_examples']={
 'limitations':'Illustrative GDR-to-ground voltages, not guaranteed controller specifications or measured current limits. VGS=VGDR-I*3ohm; assumes R14=3ohm nominal.',
 'rows':[{'GDR_to_ground_V':vg,'current_A':i,'source_V':i*3,'VGS_V':vg-i*3}
         for vg in [3.3,3.0] for i in [.1,.2,.3,.4]]}
(out/'electrical-calculations.json').write_text(json.dumps(limits,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2));print(json.dumps(limits,indent=2))
