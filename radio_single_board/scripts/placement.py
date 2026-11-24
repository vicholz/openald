# Board-relative placement (mm). Origin = top-left corner, X right, Y down (KiCad).  side "F" = top (all SMT), "B" =
# bottom (battery holder only).  Orientation in KiCad degrees (CCW positive).
#
# 2026-11-24 unified-envelope redesign (still v1.0): the radio now shares the MI03 case envelope (27.5 W x 89.75 L x
# 34.83 T outside) and docks LYING ON ITS LEFT SIDE with the USB-C on the left long edge, like the MI03:
#   * board 22.5 x 84.75 (was 38 x 87), 0.5 mm from every inner wall of the 23.5 x 85.75 cavity;
#   * y = 0 is the TOP end, y = BOARD_H the jack (bottom) end; x = 0 the USB-C (left, dock) edge, x = BOARD_W the
#     wheel / switch (right) edge -> front view = KiCad top view;
#   * USB-C J1 centred 27.8 mm below the board top (= 30.3 mm from the case's top outer end, MI03 value), mouth 1.5 mm
#     past the left board edge = 1.0 mm inside the case side face (MI03 value);
#   * 18650 holder BT1 on the bottom, + end at the top; it is screwed to the front shell through its own two 3.2 mm
#     floor holes (2 x M2 through holder + PCB into front-shell bosses), so the top side keeps those spots clear;
#   * level bar: three LEDs in a row ACROSS the board near the top-right, so it reads as a vertical bar (D1 lowest)
#     while the radio lies in the dock, and sits well above the pocket rim.
BOARD_W, BOARD_H, CORNER_R = 22.5, 84.75, 2.5
HOLDER_Y0 = 6.0                                  # holder body top end (holder body 77.7: y 6.0 .. 83.7)
BT1_PAD1 = (11.25, HOLDER_Y0 + 3.17)             # + pin (holder model: body 3.17 past pad 1, 1.63 past pad 2)
BT1_PAD2 = (11.25, BT1_PAD1[1] + 72.9)           # - pin
BT1_NPTH = [(11.25, BT1_PAD1[1] + 8.45), (11.25, BT1_PAD1[1] + 64.06)]   # holder floor holes = case screw points
SCREW_KEEP_R = 2.6                               # top-side keep-out radius around each screw point (front-shell boss r 2.2)
HOLES = []                                       # no separate mounting holes any more (H1-H4 removed)
USB_Y = 27.8                                     # J1 centre (from the board top)
USB_OVERHANG = 1.5                               # J1 mouth past the left board edge
J1_X = -USB_OVERHANG + 3.65                      # footprint origin is 3.65 behind the mouth
JACK_X = 4.85                                    # PJ-320D axis (left of the holder's - pin)
PL = {
 # ---- top end: level bar + charge LEDs top-right (rows across the board), reverse-polarity FETs top-left
 "D1":(13.9,3.0,90), "D5":(16.7,3.0,90), "D6":(19.5,3.0,90),             # level bar, vertical in the dock (D1 lowest)
 "D3":(16.7,7.2,90), "D4":(19.5,7.2,90), "R21":(13.9,7.2,90),
 "Q3":(4.6,2.6,0), "Q2":(4.6,7.0,0), "R23":(8.4,2.6,90), "R24":(8.4,6.0,90),
 # ---- right of the top screw boss: wheel-press FET, then two rows of 0603s (LED, UART, I2C series resistors)
 "Q4":(16.4,11.4,0), "R22":(21.0,11.4,90),
 "R11":(14.6,15.3,90), "R12":(16.2,15.3,90), "R13":(17.8,15.3,90), "R25":(19.4,15.3,90), "R19":(21.0,15.3,90),
 "R16":(14.6,18.5,90), "R17":(16.2,18.5,90), "R20":(17.8,18.5,90),
 # ---- USB serial above the USB-C, ESD / CC resistors below it, charger below that (left column)
 "C15":(1.4,11.4,90), "C16":(4.4,11.4,90), "U7":(4.2,17.2,90),
 "J1":(J1_X,USB_Y,-90),
 "U8":(3.0,35.2,0), "R1":(7.6,34.0,0), "R2":(7.6,35.8,0),
 "U1":(5.0,40.8,0), "C1":(1.3,45.6,90), "C2":(5.0,45.4,0), "R3":(8.2,46.2,90), "D7":(10.2,44.4,90),
 # ---- right edge: thumbwheel (dial overhangs the edge), then the power switch
 "SW3":(18.1,26.6,-90),
 "SW1":(20.0,40.6,90),
 # ---- centre: ISP pads under the wheel, then the wheel-press diode / divider beside the switch
 "J3":(11.6,35.0,0),
 "D2":(13.6,44.4,90), "R6":(15.6,44.4,90),
 # ---- MCU (left) with its parts in a 6 x 3 grid to the right of it (U5 takes three cells)
 "U3":(5.8,52.9,0),
 "C7":(12.6,49.1,90), "R10":(14.2,49.1,90), "C19":(15.8,49.1,90), "U5":(19.8,49.6,0),
 "C13":(12.6,52.6,90), "C14":(14.2,52.6,90), "R14":(15.8,52.6,90), "R7":(17.4,53.0,90), "C4":(19.0,53.0,90), "C5":(20.6,53.0,90),
 "R15":(12.6,56.1,90), "C18":(14.2,56.1,90), "R8":(15.8,56.1,90), "R9":(17.4,56.1,90), "C6":(19.0,56.1,90),
 # ---- MCU-only rail + FM supply parts left of the FM module
 "D10":(1.4,60.8,90), "D8":(3.8,60.8,90), "D9":(6.2,60.8,90),
 "U6":(2.6,65.2,0), "C17":(2.6,68.6,0), "R18":(7.6,65.0,90), "C9":(7.6,68.4,90), "C8":(8.4,60.8,90),
 "U4":(16.0,64.1,0),
 # ---- jack (bottom end, left of the holder's - pin) + audio and cell protection right of the - pin
 "J2":(JACK_X,BOARD_H-8.4,90),
 "C10":(16.4,71.6,0), "C11":(16.4,74.2,0), "FB1":(20.8,71.6,0), "FB2":(20.8,74.2,0), "FB3":(14.6,76.6,0), "C12":(17.6,76.6,0), "R5":(20.8,76.6,0),
 "U2":(15.3,79.5,0), "Q1":(19.4,79.6,90), "C3":(14.8,82.8,0), "R4":(18.0,82.8,0),
}
# level-bar window centres in the case top (board coordinates, straight above each LED)
BAR_WIN = {r: PL[r][:2] for r in ("D1","D5","D6")}
# cell-polarity silkscreen marks: (text, x, y, size mm, layer). Bottom marks sit in the strips beyond the holder ends.
POL_MARKS=[("+",3.0,2.6,1.6,"B"),("+",19.5,2.6,1.6,"B"),("BAT+",11.25,1.6,0.8,"B"),("−",14.6,84.0,0.8,"B"),
           ("+",9.0,11.2,1.0,"F"),("−",13.4,84.0,0.8,"F")]
