"""Render clipped regions of the schematic PDF to PNG for visual review.

Usage: python render_sch_regions.py <schematic.pdf> <out_dir>
Regions are in PDF points (A2 sheet = 1683.8 x 1190.5 pt).
"""
import os
import sys

import fitz

REGIONS = {
    "01_usbc_conn_esd": (40, 30, 255, 365),
    "02_powerpath": (265, 55, 495, 215),
    "03_charger": (243, 205, 490, 370),
    "04_ldo_batmon": (490, 55, 665, 365),
    "05_sdmmc": (655, 60, 1035, 360),
    "06_ext_conn_esd": (1030, 65, 1335, 400),
    "07_usb_status": (1335, 205, 1615, 440),
    "08_battery": (45, 375, 362, 622),
    "09_buttons": (370, 375, 920, 598),
    "10_rtc": (915, 405, 1137, 610),
    "11_esp32": (1130, 420, 1612, 826),
    "12_eink": (50, 630, 555, 952),
    "13_led": (565, 608, 1078, 958),
    "14_pwr_boot_mount": (45, 950, 510, 1160),
    "15_touch": (570, 980, 1050, 1160),
    "16_titleblock": (1330, 1050, 1670, 1180),
}


def main(pdf, out_dir, dpi=300, only=None):
    doc = fitz.open(pdf)
    page = doc[0]
    os.makedirs(out_dir, exist_ok=True)
    for name, (x0, y0, x1, y1) in REGIONS.items():
        if only and name not in only:
            continue
        pix = page.get_pixmap(dpi=dpi, clip=fitz.Rect(x0, y0, x1, y1))
        pix.save(os.path.join(out_dir, name + ".png"))
        print(name, pix.width, pix.height)


if __name__ == "__main__":
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    main(sys.argv[1], sys.argv[2], dpi, only)
