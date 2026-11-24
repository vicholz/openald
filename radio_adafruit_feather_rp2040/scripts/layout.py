"""OpenALD Feather RP2040 v1.0 - single source of truth for the mechanical layout.

2026-11-24 UNIFIED ENVELOPE (still v1.0): the Feather radio now shares the MI03 / single-board outside length and
thickness (89.75 L x 34.83 T, plan corner r 5, edge r 2) and their dock port: a USB-C receptacle on the LEFT long side,
centred 30.3 mm from the top outer end and 7.55 mm below the front face, mouth 1.0 mm inside the side face. All three
radios dock lying on that side, so only L, T and the port position have to match; the width does not (it becomes the
height in the dock). This one is wider (32.9 mm) because the 27.25 mm FM module has to fit across it.

Case frame (this variant): X across the case, X = 0 on the centre line, -X = the dock (USB) side; Y along the case,
Y = 0 at the INNER face of the jack (bottom) end wall, +Y toward the top end; Z = 0 at the BACK outer face, +Z toward
the front face (Z = T).

Stack (back to front):  back shell floor | 18650 holder (base on the floor, cell opening toward the front) with the
Feather RP2040 standing on its long edge beside it (left wall) | deck (separate printed plate) | front zone: FM module
at the jack end, USB-C charge-port breakout on the left wall, thumbwheel + power switch on the right wall | front face.
"""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
# ---------------- shared envelope (keep identical to mi03_case.scad / radio_single_board openald_case.scad) -------
T = 34.83                 # outside thickness
L_OUT = 89.75             # outside length
WALL, EDGE_R, OUT_R = 2.0, 2.0, 5.0
IN_R = 1.0                # inner plan corner radius (outside stays r 5; thicker corners let the holder reach the corner)
USB_FROM_TOP = 30.3       # dock USB-C centre from the top outer end
USB_FROM_FRONT = 7.55     # dock USB-C centre below the front face
USB_MOUTH_IN = 1.0        # receptacle mouth inside the side face
USB_W, USB_H, USB_LEN = 8.94, 3.26, 7.35
USB_RECESS = (13.0, 7.6, 3.0)   # cable-plug recess on the side face (along the case x across it, r)
USB_RECESS_GAP = 0.55           # recess floor this far outside the receptacle mouth (MI03)
# ---------------- this variant ----------------
FLOOR_T, FRONT_T = 1.4, 1.6
IN_L = L_OUT - 2*WALL                          # 85.75 inner length (Y 0 .. IN_L)
HOLDER_W, HOLDER_L, HOLDER_H = 20.9, 77.7, 21.31   # MPD BH-18650-PC (datasheet), PC pins 72.9 apart, floor holes 3.2
HOLDER_POCKET = 0.3                            # floor pocket the holder base sits in (locates it; glue optional)
# Feather RP2040 (Adafruit 4884): 50.8 x 22.86 x 1.6, parts up to 5.5 mm (JST-PH) above its top face.
F_LEN, F_W, F_T, F_PARTS_H = 50.8, 22.86, 1.6, 5.5
F_FLOOR_GROOVE = 0.5                           # its lower long edge sits in a floor groove this deep
GAP = 0.3
# widths: [wall clr | Feather parts 5.5 | Feather 1.6 | gap | holder 20.9 | gap] -> inner width
IN_W = GAP + F_PARTS_H + F_T + GAP + HOLDER_W + GAP      # 28.9
W_OUT = IN_W + 2*WALL                                    # 32.9
IN_X0, IN_X1 = -IN_W/2, IN_W/2
# holder against the right wall and the top end wall, base in the floor pocket
HOLDER = dict(x0=IN_X1-GAP-HOLDER_W, x1=IN_X1-GAP, y1=IN_L-0.5, z0=FLOOR_T-HOLDER_POCKET)
HOLDER.update(y0=HOLDER["y1"]-HOLDER_L, z1=HOLDER["z0"]+HOLDER_H)
HOLDER_CX = (HOLDER["x0"]+HOLDER["x1"])/2
HOLDER_PINS = [(HOLDER_CX, HOLDER["y1"]-2.4, "+"), (HOLDER_CX, HOLDER["y0"]+2.4, "-")]   # + end at the top end
# Feather standing on its long edge against the left wall, components facing the wall, USB-C (programming / firmware
# only) facing the top end wall. Feather-local (u along the length from the USB end, v across from the centre, w up
# from its bottom face) -> case: X = F_X_BACK - w, Y = F_USB_FACE_Y - (u + usb_overhang), Z = F_ZC + v.
F_X_BACK = HOLDER["x0"] - GAP                  # Feather bottom face (toward the holder)
F_USB_FACE_Y = IN_L - 0.1                      # its receptacle face, 0.1 inside the top end wall
F_ZC = FLOOR_T - F_FLOOR_GROOVE + F_W/2        # Feather centre line height
# deck (separate plate) over the holder and the Feather's top edge
DECK_Z0 = HOLDER["z1"] + GAP + 0.3             # 0.6 above the cell top
DECK_T = 1.0
DECK_Z1 = DECK_Z0 + DECK_T                     # = front/back split
Z_SPLIT = DECK_Z1
Z_CEIL = T - FRONT_T
# dock USB-C (charge port): a USB-C receptacle breakout in a cradle on the left wall (ASSUMED generic 2-pin/6-pin
# "power only" USB-C breakout with 5.1k CC pull-downs, receptacle on the board edge; measure yours)
DOCK_USB_Y = (IN_L + WALL) - USB_FROM_TOP     # 57.45 (inner frame)
DOCK_USB_Z = T - USB_FROM_FRONT               # 27.28
DOCK_USB_MOUTH_X = IN_X0 - WALL + USB_MOUTH_IN
BRK_W, BRK_D, BRK_T = 12.7, 10.0, 1.0          # ASSUMED breakout PCB: width (Y) x depth (X, from the mouth) x thickness
BRK_PARTS_H = 1.2                              # ASSUMED: CC resistors / pads under the PCB at most this tall (bottom side)
# FM module (Victor, 2026-11-24): 27.25 x 27.25 x 1.6 PCB, 3.8 mm holes in the corners 20 mm apart, standard 6.35 x 14
# headphone jack (centred on the bottom edge, 1 mm past the board) and a 4-pin 90-degree through-board header, also
# centred at the bottom edge. Jack toward the jack end of the case.
FM_S, FM_T = 27.25, 1.6
FM_HOLE_D, FM_HOLE_PITCH = 3.8, 20.0
FM_JACK_D, FM_JACK_L, FM_JACK_OUT = 6.35, 14.0, 1.0
FM_STANDOFF = 0.4                              # printed pads under the four corners
FM = dict(x0=-FM_S/2, x1=FM_S/2, y0=FM_JACK_OUT, z0=DECK_Z1+FM_STANDOFF)
FM.update(y1=FM["y0"]+FM_S, z1=FM["z0"]+FM_T)
FM_CX, FM_CY = 0.0, FM["y0"]+FM_S/2
FM_HOLES = [(FM_CX+sx*FM_HOLE_PITCH/2, FM_CY+sy*FM_HOLE_PITCH/2) for sy in (-1,1) for sx in (-1,1)]
FM_JACK_AXIS_Z = FM["z1"] + FM_JACK_D/2
FM_JACK_HOLE_D = 6.8                           # plug-overmold hole in the end wall
# ASSUMED header: straight pins through the board, plastic + pins BELOW the board (wires soldered underneath), 2.54 mm
# from the bottom edge; the deck has a window there and nothing is below it down to the floor (the holder starts at
# HOLDER y0). If yours has the pins lying flat (right-angle) they must point down through the same window.
FM_HDR = dict(w=4*2.54, d=2.54, below=8.5, y=FM["y0"]+2.54)
# thumbwheel: Mitsumi SIQ-02FVS3 on a cradle on the deck, right wall (same dial protrusion as before: 4.3 in from the wall)
WHEEL = (IN_X1-4.3, 41.0)
WHEEL_R = 7.25
WHEEL_SEAT_Z = DECK_Z1
WHEEL_DIAL_Z = (2.0, 4.0)                      # dial above the seat
WHEEL_BODY = (10.3, 3.85, 7.25)                # across (Y), toward the dial side (+X), toward the terminals (-X)
WHEEL_PUSH = 1.0
# power switch: SS-12F16 SPDT panel slide switch, plate in a groove inside the RIGHT wall of the front shell
SW_L = 4.0                   # knob height above the plate (G4)
SW_Y, SW_Z = 70.0, DECK_Z1 + 0.6 + 5.7/2
SW_PLATE = (19.7, 5.7, 0.5)
SW_BODY = (11.0, 5.7, 5.0)
SW_LUG_L, SW_LUG_P = 3.0, 3.0
SW_ACT = (3.0, 3.0)
SW_TRAVEL = 3.0
SW_SKIN = 1.2                # outer skin in front of the plate -> G4 knob 2.8 mm proud
SW_GROOVE = 0.7
SW_RIB = 0.8
# dock-visible charge LEDs: two 3 mm THT LEDs in sockets in the front face (the Feather's own LEDs face the wall now)
LED3 = [("red","CHG",3.0,80.5),("green","FULL",3.0,75.0)]
LED3_ABOVE_FLANGE = 4.6
FEATHER_DY = -0.9   # legacy: the old case frame used by ref/feather_rp2040_mech.json (feather_data.py); not a case position
# ---------------- Feather geometry from Adafruit's board (scripts/feather_data.py -> ref/feather_rp2040_mech.json) -------
def feather():
    d=json.load(open(os.path.join(ROOT,"ref","feather_rp2040_mech.json")))
    return d
def f2case(u,v,w):
    """Feather-local -> case frame (u from the board's USB-end edge, v from the centre line, w above its bottom face)"""
    d=feather(); ovh=d["usb_overhang"]
    return (F_X_BACK-w, F_USB_FACE_Y-(u+ovh), F_ZC+v)
def feather_boxes():
    """Feather board + every part envelope as case-frame boxes [x0,x1,y0,y1,z0,z1] (from the old case-frame json)."""
    d=feather(); ovh=d["usb_overhang"]; y0b=d["board_case"]["y0"]          # y0b = ovh + old DY
    out=[]
    def conv(x0,x1,y0,y1,z0,z1):
        us=[y0-y0b,y1-y0b]; vs=[19.0-x0,19.0-x1]
        P=[f2case(u,v,w) for u in us for v in vs for w in (z0,z1)]
        return [min(p[0] for p in P),max(p[0] for p in P),min(p[1] for p in P),max(p[1] for p in P),min(p[2] for p in P),max(p[2] for p in P)]
    out.append(("board",conv(d["board_case"]["x0"],d["board_case"]["x1"],d["board_case"]["y0"],d["board_case"]["y1"],0,F_T)))
    for p in d["parts"]: out.append((p["ref"],conv(p["x0"],p["x1"],p["y0"],p["y1"],p["z0"],p["z1"])))
    u=d["usb"]; out.append(("USB",conv(u["center_x"]-u["w"]/2,u["center_x"]+u["w"]/2,u["face_y"],u["face_y"]+u["len"],F_T,F_T+u["h"])))
    return out
def feather_usb():
    d=feather(); ovh=d["usb_overhang"]
    x,y,z=f2case(-ovh, 0.0, F_T+d["usb"]["h"]/2)
    return x,y,z
def feather_holes():
    d=feather(); y0b=d["board_case"]["y0"]
    return [f2case(hy-y0b, 19.0-hx, 0)[1:] for hx,hy in d["holes"]]
if __name__=="__main__":
    print(f"outer {W_OUT:.2f} W x {L_OUT} L x {T} T; holder {HOLDER}; deck {DECK_Z0:.2f}..{DECK_Z1:.2f}; FM {FM}; jack axis {FM_JACK_AXIS_Z:.2f}")
    print("feather usb", feather_usb(), "dock usb", (DOCK_USB_MOUTH_X, DOCK_USB_Y, DOCK_USB_Z))
    for n,b in feather_boxes()[:3]+feather_boxes()[-1:]: print(n,[round(a,2) for a in b])
