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
BASE_W = 25.5                                    # t116u: the coordinates below are laid out on a 25.5 mm board
# t116u (2026-11-24): USB-C moved to the BOTTOM END (centred) so the radio stands upright in the dock, plugged
# straight down onto the dock's USB-C plug. The ends are swapped relative to t115u:
#   * y = 0 is the TOP end (jack, level bar, FM module), y = BOARD_H the BOTTOM end (USB-C J1, centred, mouth
#     USB_OVERHANG past the bottom edge = 1.0 mm inside the case's bottom end face);
#   * 18650 holder BT1 on the bottom side, + end at the BOTTOM (USB) end now, - end at the top (jack) end; the holder
#     is still screwed to the front shell through its own two 3.2 mm floor holes, so the top side keeps those clear;
#   * level bar: three LEDs in a COLUMN along the board at the top-right (D6 top, D1 lowest), so it reads as a
#     vertical bar while the radio stands in the dock, well above the pocket rim.
import os as _os
BOARD_W = float(_os.environ.get("OPENALD_BOARD_W", "26.9"))   # case 31.9 wide = the Feather radio (FM module 27.25 across)
BOARD_H, CORNER_R = 84.75, 2.5
USB_OVERHANG = 1.5                               # J1 mouth past the bottom board edge
J1_Y = BOARD_H + USB_OVERHANG - 3.65             # footprint origin is 3.65 behind the mouth
BT1_PAD1 = (BOARD_W/2, 75.0)                     # + pin, toward the USB end (clear of J1's pads and shell legs)
BT1_PAD2 = (BOARD_W/2, BT1_PAD1[1] - 72.9)       # - pin, toward the jack end
HOLDER_Y0 = BT1_PAD2[1] - 1.63                   # holder body top end (body 77.7 long: 1.63 past pad 2, 3.17 past pad 1)
BT1_NPTH = [(BOARD_W/2, BT1_PAD1[1] - 64.06), (BOARD_W/2, BT1_PAD1[1] - 8.45)]   # holder floor holes = case screw points
SCREW_KEEP_R = 2.6                               # top-side keep-out radius around each screw point (front-shell boss r 2.2)
HOLES = []
USB_X = BOARD_W/2                                # J1 centred across the width
JACK_X = 5.5                                     # PJ-320D axis (left of the holder's - pin), mouth at the top edge
PL = {
 # ---- top end: jack (left), holder - pin (centre), charge LEDs + level bar column + cell protection (right)
 "J2":(JACK_X,8.4,-90),
 "D3":(19.6,2.4,0), "D4":(19.6,5.0,0), "R21":(16.0,2.4,0), "R22":(16.0,5.0,0),
 "D6":(23.4,2.4,0), "D5":(23.4,5.0,0), "D1":(23.4,7.6,0),               # level bar column, D1 lowest
 "U2":(17.6,9.6,0), "Q1":(22.3,11.0,0), "C3":(17.0,13.2,0), "R4":(20.4,14.0,0), "R5":(23.6,14.0,0),
 # ---- FM module right, audio coupling / ferrites left (under the jack), FM supply + I2C series below them
 "U4":(18.6,21.4,0),
 "C10":(3.0,16.2,0), "FB1":(7.6,16.2,0), "C11":(3.0,18.8,0), "FB2":(7.6,18.8,0),
 "FB3":(2.2,21.3,0), "C12":(5.4,21.3,0), "C9":(8.7,21.3,90), "C8":(10.7,21.3,90),
 "R16":(2.0,23.6,0), "R17":(5.1,23.6,0), "R18":(8.2,23.6,0),
 "R14":(2.2,25.4,0), "R15":(5.4,25.4,0), "R10":(8.6,25.4,0),
 "R19":(2.2,27.2,0), "C19":(8.6,27.2,0),
 # ---- MCU (left) under them, thumbwheel (right edge, dial overhangs), then the power switch
 "U3":(6.4,34.5,0),
 "SW3":(21.1,33.8,-90),
 "SW1":(23.0,48.0,90),
 "J3":(14.9,42.2,0),
 "C7":(2.0,43.0,0), "C13":(5.2,43.0,0), "C14":(8.4,43.0,0), "C18":(11.6,43.0,0),
 "R11":(2.0,44.8,0), "R12":(5.2,44.8,0), "R13":(8.4,44.8,0), "R7":(11.6,44.8,0),
 "R8":(2.0,46.6,0), "R9":(5.2,46.6,0), "C6":(8.4,46.6,0), "R6":(11.6,46.6,0),
 "C4":(2.0,48.4,0),
 "U5":(3.0,52.4,0), "C5":(6.6,51.6,90), "D2":(10.0,52.4,90), "Q4":(13.0,53.0,0), "R25":(17.0,53.0,90),
 # ---- MCU-only rail (diode OR + LDO)
 "D10":(1.7,59.5,90), "D8":(4.3,59.5,90), "D9":(6.9,59.5,90), "U6":(10.6,58.4,0), "C17":(10.6,61.4,0),
 "D7":(21.9,62.0,0),
 # ---- bottom end: USB-C centred, ESD + CC left of it, USB serial left, charger right, reverse-polarity FETs
 #      between the bottom screw point and the holder + pin
 "J1":(USB_X,J1_Y,0),
 "U8":(3.0,80.0,90), "R1":(5.9,79.0,90), "R2":(5.9,82.3,90),
 "U7":(3.6,73.0,90), "R20":(2.2,65.6,0), "C15":(2.2,67.4,0), "C16":(5.4,67.4,0),
 "U1":(21.9,73.0,90), "C1":(19.4,79.6,90), "C2":(22.0,79.6,90), "R3":(24.2,79.6,90),
 "Q2":(9.2,71.4,0), "Q3":(16.3,71.4,0), "R23":(12.75,70.6,0), "R24":(12.75,72.4,0),
}
# ---- stretch to BOARD_W: right-edge parts move with the right edge, J1 stays put, everything else scales in x
_K = BOARD_W / BASE_W; _DW = BOARD_W - BASE_W
_RIGHT = ("SW3", "SW1")
for _r, (_x, _y, _a) in list(PL.items()):
    if _r == "J1": PL[_r] = (USB_X, _y, _a); continue
    PL[_r] = (round(_x + _DW, 3) if _r in _RIGHT else round(_x * _K, 3), _y, _a)
JACK_X = PL["J2"][0]
# level-bar window centres in the case top (board coordinates, straight above each LED)
BAR_WIN = {r: PL[r][:2] for r in ("D1","D5","D6")}
# cell-polarity silkscreen marks: (text, x, y, size mm, layer). Bottom marks sit in the strips beyond the holder ends.
POL_MARKS=[(t, round(x*_K,3), y, sz, l) for (t,x,y,sz,l) in [("+",3.0,83.2,1.6,"B"),("+",22.5,83.2,1.6,"B"),
           ("+",10.2,75.0,1.0,"F"),("−",15.0,0.9,0.8,"F")]]
