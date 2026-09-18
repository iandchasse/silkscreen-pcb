# a3 sch pin-by-pin notes
- U4 pin table (netlist) checked vs WROOM-1: 28-30 (IO35-37) NC ok; IO45/46/3 strap pins only reach 33R+ESD+J6 (float -> internal defaults); IO0 10k+SW6(DNP); EN 10k+1u (+100R/SW11) ok; ADC users IO1,2,4,8,9 all ADC1.
- SD = IO5/6/7/15/16/17 (no strap conflicts), EPD = IO12/13/14/21/47/48, 33R each.
- Pinouts verified vs datasheets: U6-9/U1 TPD4E1U06 (1,3,4,6 IO, 2 GND, 5 NC), U2 TPS2116 (MODE=VIN1 priority ok), U10 TPS923610 (ADIM has 600k internal PD), U11 TP4056 (TEMP to GND legal), U13 DS3231M (VCC=GND, VBAT=3V3 = Fig.5), U12, U3, U5, Q1.
- R72/R74 DNP -> no ladder2/PWR_BUTTON leakage path (checked; not an issue).
- Ladder chord table computed: SW3+SW9 1.113V vs SW3 1.185V; SW4+SW7 1.666 vs SW4 1.80.
- Findings: ladder buttons cannot wake from sleep (only SW1/SW2 at 33 mV); Q7 no soft-start; chord aliasing; DS3231M VIH ref.
