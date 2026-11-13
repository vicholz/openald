# Board-relative placement (mm). Board outline 38 x 85, origin top-left, Y down.
# side "F" = top (all SMT), "B" = bottom (battery holder only).
# Orientation in KiCad degrees (CCW positive).
BOARD_W, BOARD_H, CORNER_R = 38.0, 87.0, 3.0
HOLES = [(3.2,3.2),(34.8,3.2),(3.2,83.8),(34.8,83.8)]
PL = {
 "H1":(3.2,3.2,0),"H2":(34.8,3.2,0),"H3":(3.2,83.8,0),"H4":(34.8,83.8,0),
 # --- top edge: headphone jack; wheel-press power FET Q4 + gate pull-up R25 where the old battery-check button SW2
 #     (29.4,1.6) sat (removed 2026-11-11, still v1.0: the wheel press does the battery check now)
 "J2":(11.5,8.4,-90), "Q4":(29.4,2.6,0), "R25":(25.8,2.2,0),
 # --- protection next to the cell negative terminal (BT1 pin 2 at x=19,y=6.05)
 "Q1":(28.8,9.6,0), "U2":(33.4,9.6,0), "C3":(33.4,12.9,0), "R4":(33.4,14.6,0), "R5":(29.0,12.9,0),
 # --- rev 4.2 reverse-polarity protection: Q3 (orientation sense) by the cell - terminal / DW01A, Q2 (series P-FET) by the
 #     cell + terminal (BT1 pin 1 at x=19,y=75.4) next to the TP4056, R23/R24 at the left edge below R3
 "Q3":(29.2,17.4,0), "Q2":(11.3,76.0,0), "R23":(2.9,75.7,0), "R24":(2.9,78.5,0),
 # --- battery level bar (2026-11-11 update, still v1.0): 3x 0603 LED in a VERTICAL column CENTRED across the board
 #     (x = 19.0, the board/case centreline) and moved up toward the jack end, so the whole bar sits ~25-32 mm above the
 #     dock rim when the radio stands USB-C-down in the dock. The centreline is shared with the holder's - pad (19,2.5,
 #     3.0 pad) and its locating-peg hole (19,11.34, 3.2 NPTH), so the LEDs go D6 (full) just below the - pad, D5 just
 #     above the peg hole and D1 (lowest level) just below it. A centred HORIZONTAL row up here was tried and rejected:
 #     the jack's courtyard (to x = 16.53) leaves too little width for three LEDs with printed tunnel walls.
 #     The case windows are evenly spaced (BAR_WIN_Y, 2.8 mm pitch); D1's light tunnel leans 2.3 mm up to its window.
 #     Previous spot (dock update): x = 24.0, y = 15.4/12.4/9.4. R11-R13 stay where they were.
 "D6":(19.0,6.1,0), "D5":(19.0,8.9,0), "D1":(19.0,14.0,0),
 "R11":(26.4,68.2,90), "R12":(28.1,68.2,90), "R13":(29.8,68.2,90),
 # --- FM module + audio / antenna network
 # FB1/FB2 moved from (22.4,5.0/6.8) into the old LED column (2026-11-11) to free the centred LED row
 "U4":(10.5,23.6,0), "FB1":(24.0,10.4,0), "FB2":(24.0,12.4,0), "FB3":(4.2,12.2,90), "C12":(4.2,8.6,90),
 "C10":(19.6,20.0,90), "C11":(22.6,20.0,90), "R18":(12.4,31.6,0), "C8":(5.6,31.8,0), "C9":(9.2,31.6,0),
 "R16":(2.0,20.2,90), "R17":(2.0,23.6,90),
 # --- right edge: thumbwheel encoder (wheel overhangs edge) and recessed power switch
 "SW3":(33.6,26.0,-90), "SW1":(35.5,64.0,90),
 # --- MCU block
 # --- MCU block (rev 4: ATmega328PB TQFP-32). Decoupling next to VCC (pin 4, left), AVCC (18) and AREF (20) on the right
 "U3":(11.5,45.5,0), "C7":(5.2,45.5,90), "C13":(18.6,47.7,0), "C14":(18.6,46.0,0),
 "C6":(18.6,44.3,0), "R9":(18.6,42.6,0), "R8":(18.6,40.9,0),
 "R10":(10.0,37.4,90), "C19":(8.3,37.4,90), "R19":(6.6,37.4,90), "R14":(12.0,37.4,90), "R15":(13.7,37.4,90), "R20":(15.4,37.4,90),
 "J3":(33.0,44.6,0),
 # --- power path
 "U5":(22.0,50.5,0), "C4":(19.2,50.5,90), "C5":(24.8,50.5,90),
 "D2":(22.0,56.5,0), "R6":(17.8,56.0,90), "R7":(15.8,56.0,90),
 # --- charger block, bottom edge USB-C
 "U1":(8.0,71.5,0), "R3":(2.2,71.5,90), "C1":(33.6,77.6,90), "C2":(8.0,66.6,0), "D7":(12.6,65.4,90),
 "J1":(19.0,84.25,0),   # 2026-11-12: +0.9 toward the USB edge (was 83.35): receptacle front 0.9 past the board edge -> mouth 1.60 inside the case bottom face, like the Feather
 "R1":(15.4,76.6,0), "R2":(22.6,76.6,0),
 # TP4056 charge LEDs (visible with the power switch off), each in its own light tunnel left of the USB-C
 "D3":(7.4,81.8,0), "D4":(11.4,81.8,0), "R21":(7.4,78.6,0), "R22":(11.4,78.6,0),
 # --- rev 4 USB serial: ESD array right next to the USB-C data pins, CH340K (VBUS-powered) right of it
 #     USB pair: J1 fan-out + bottom-layer pair to U7 is pre-routed in route_pcb.py (USB_PREROUTE)
 "U8":(26.6,80.6,0), "U7":(29.4,74.0,90), "C15":(33.6,73.9,90), "C16":(25.8,74.6,90),   # C16 position kept from the pre-dock layout (was clear of the old D6 tunnel)
 # --- rev 4 MCU-only 3.3 V rail: D8 (VSYS) + D9 (VBUS) diode-OR into U6, between the LDO/D2 block and the power switch
 "D10":(28.0,56.3,0), "D8":(28.0,58.9,0), "D9":(28.0,61.5,0), "U6":(27.2,64.6,0), "C17":(24.3,64.6,90), "C18":(30.2,64.6,90),
}
# Battery holder on the bottom: pad 1 (+) at (19, 75.4), pad 2 (-) at (19, 2.5); body spans y 0.87..78.57,
# leaving room for the centred USB-C receptacle (signal pads at y~80.2, shell pegs from y 80.1 since J1 moved +0.9 on 2026-11-12)
# level-bar window centres in the case top (board y, same x as the LED): evenly spaced, D1's tunnel is slanted
BAR_WIN_Y={"D6":6.1,"D5":8.9,"D1":11.7}
BT1_PAD1=(19.0,75.4); BT1_PAD2=(19.0,2.5)
# rev 4.2 cell-polarity silkscreen marks: (text, x, y, size mm, layer).  Bottom marks sit in the strips beside the holder
# (holder courtyard x 7.77..30.24), level with the + contact (USB end) and the - contact (jack end).
POL_MARKS=[("+",4.4,74.6,3.0,"B"),("+",33.6,74.6,3.0,"B"),("−",4.4,8.0,3.0,"B"),("−",33.6,8.0,3.0,"B"),
           ("BAT+",4.4,77.7,1.0,"B"),("BAT+",33.6,77.7,1.0,"B"),("BAT−",4.4,12.2,1.0,"B"),("BAT−",33.6,12.2,1.0,"B"),
           ("+",21.5,74.3,1.6,"F"),("−",21.9,1.7,2.0,"F")]
