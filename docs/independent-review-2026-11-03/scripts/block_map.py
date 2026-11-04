"""Block partition of every reference designator; verifies that all netlist refs are assigned exactly once.

python block_map.py <netlist.json>
"""
import json
import re
import sys

BLOCKS = {
    "USB-C input & protection": "J1 F1 CR1 U6 R2 R3 C2 R84 C25 D2 R59",
    "Charger (TP4056) & enable logic": "U11 R6 C3 Q2 R81 R82 Q9 R79 R80",
    "Cell connector, reverse-polarity & protection (DW01A/FS8205A)": "J5 Q3 R56 R57 R27 Q8 U5 R83 C7 R16 C34 Q1 R85 R86",
    "Power mux (TPS2116)": "U2 C26 C4 R38 R51",
    "3V3 LDO & bulk": "U3 C6 C21",
    "Battery monitor": "R12 R10 C8",
    "USB/charge status divider": "R70 R17 R67 R71 C23",
    "MCU (ESP32-S3) boot/reset/decoupling/UART": "U4 R7 C5 R13 SW11 R63 SW6 R64 C32 C33 TP1 TP2 R65 R68 R69",
    "microSD": "J7 Q7 R40 R78 R77 R8 R9 R53 R54 R55 R21 R22 R23 R24 R25 R26 C36 C37 U1 U9",
    "E-paper connector & boost/charge pump": "J2 Q4 L1 D4 D5 D6 C10 C11 R14 R15 F6 C13 C14 C15 C16 C17 C18 C19 C20 C22 R5 R29 R30 R31 R32 R33 R34",
    "Frontlight driver": "U10 L2 C12 C9 F3 R37 Q5 Q6 U12 R75 C24 R49 R50 R39 R41 C31 J3 TP3 TP4 TP5",
    "Touch connector & jumper mux": "J4 F4 U7 R43 R44 R45 R46 R52 R58 R66",
    "RTC": "U13 U14 C30",
    "Buttons / ADC ladders / power button": "SW1 SW2 SW3 SW4 SW5 SW7 SW8 SW9 SW10 R4 R28 R11 R18 R19 R20 R35 R36 R60 R61 R62 R72 R73 R74 R76 C27 C28 C29",
    "I2C pull-ups": "R47 R48",
    "Expansion header J6 & its protection": "J6 F2 F5 CR2 CR3 U8 D3 D8",
    "Mechanical": "H1 H2 H3 H4 H5 H6",
}


def main(path):
    comps = json.load(open(path))["components"]
    seen = {}
    for blk, refs in BLOCKS.items():
        for r in refs.split():
            if r in seen:
                print("DUPLICATE", r, blk, seen[r])
            seen[r] = blk
    missing = sorted(set(comps) - set(seen), key=lambda r: (re.sub(r"\d", "", r), int(re.sub(r"\D", "", r) or 0)))
    extra = sorted(set(seen) - set(comps))
    print("components in netlist:", len(comps), "assigned:", len(seen))
    print("unassigned:", missing)
    print("assigned but not in netlist:", extra)
    for blk, refs in BLOCKS.items():
        print(f"{blk}: {len(refs.split())} parts")


if __name__ == "__main__":
    main(sys.argv[1])
