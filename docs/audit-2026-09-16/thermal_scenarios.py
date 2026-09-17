"""U3 steady-state sensitivity calculations; not a measured PCB thermal model.

No design/order writes. Two TI DBV reference-board theta-JA values are scenarios,
not guaranteed bounds for this board. High calculated junction temperatures are
extrapolations; thermal shutdown prevents that regulated steady state.
"""
import json, pathlib

out = pathlib.Path(__file__).parent
theta = {'TI_DBV_EVM': 100.8, 'TI_DBV_JEDEC': 231.1}
rows = []
for current_ma in (100, 150, 250, 350, 500):
    for vin in (3.7, 4.2, 5.0, 5.25, 5.5):
        power = (vin - 3.3) * current_ma / 1000
        rows.append({
            'sustained_3V3_mA': current_ma, 'U3_input_V': vin,
            'U3_power_W_ignoring_Iq': round(power, 6),
            'Tj_C_at_25C_ambient': {
                name: round(25 + power * value, 3) for name, value in theta.items()
            },
            'interpretation': {
                name: ('exceeds_typical_shutdown_no_regulated_equilibrium' if 25 + power * value >= 165
                       else 'exceeds_125C_recommended_limit' if 25 + power * value > 125
                       else 'below_125C_in_this_scenario_only')
                for name, value in theta.items()
            }
        })
result = {
    'date': '2026-09-17', 'formula': 'Tj = Tamb + (Vin - 3.3) * I_3V3 * theta_JA',
    'ambient_C': 25, 'theta_JA_C_per_W': theta,
    'recommended_Tj_max_C': 125, 'typical_shutdown_C': 165,
    'assumptions': [
        'Fixed nominal 3.3V output; not all component tolerances included.',
        'Actual sustained board load and actual thermal resistance are unknown.',
        'Input values are at U3; neglecting cable/fuse/mux/PMOS drops is conservative for its heating.',
        'No charging or main frontlight current flows through U3.',
        'Other heat sources and enclosure coupling are not modeled.',
        'Short pulses do not produce the full steady-state rise calculated here.',
        'Numbers above shutdown are mathematical extrapolations, not operating temperature predictions.',
        'At 40C local ambient, add 15C to the 25C calculations before interpreting limits.',
        '4.2V is a nominal fully charged cell; 5.5V is the USB upper-voltage design case.'
    ],
    'sources': [
        'https://www.ti.com/lit/ds/symlink/tlv755p.pdf',
        'https://compliance.usb.org/index.asp?UpdateFile=Electrical'
    ], 'rows': rows
}
(out/'thermal-scenarios.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
for ma in (150, 250, 350, 500):
    print(ma, {r['U3_input_V']:r['Tj_C_at_25C_ambient'] for r in rows
               if r['sustained_3V3_mA'] == ma and r['U3_input_V'] in (4.2, 5.0, 5.5)})
