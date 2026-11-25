"""OpenALD Feather RP2040 v1.0 - single source of truth for the mechanical layout.

t116u (2026-11-24) BOTTOM-END USB-C: the radio stands upright in the charging dock, plugged straight down onto the
dock's USB-C plug. The Feather lies FLAT on the deck at the bottom end and its OWN USB-C is the dock / charging port
(no breakout, no Schottky diode): the receptacle is centred across the case, DOCK_USB_FROM_FRONT below the front face,
mouth 1.0 mm inside the bottom end face -- the same spot as the single-board radio, which also has the same outside
width and thickness (31.9 x 33.86), so both fit the same dock pocket. This case is longer (the wheel sits between the
Feather and the FM module); length does not matter in the dock. The Feather's CHG LED, red LED and NeoPixel face the
front and are seen through light tunnels / holes in the front face. The MI03 keeps its side USB-C (not docked).

Case frame: X across the case, X = 0 on the centre line (+X = right side in the front view: wheel); Y along the case,
Y = 0 at the INNER face of the bottom (USB-C / dock) end wall, +Y toward the top (jack) end; Z = 0 at the BACK outer
face, +Z toward the front face (Z = T).

Stack (back to front): back shell floor | 18650 holder lying on the floor (centred, base in a floor pocket) | deck
(separate printed plate) | front zone: Feather (bottom end, flat, components up), thumbwheel (right wall) + power switch
(left wall) between the Feather and the FM module, FM module at the top end (jack through the top end wall) | front face.
"""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
# ---------------- dock interface (keep identical to radio_single_board openald_case.scad / charging_dock geom.py) -------
W_OUT = 35.9              # outside width  (dock pocket width). t122u: 31.9 -> 35.9 (Victor: 2 mm more room beside the
                          # Feather on the battery-connector side and the same on the other side, Feather still centred)
T = 33.86                 # outside thickness (dock pocket depth front-back)
DOCK_USB_FROM_FRONT = 6.62    # USB-C centre below the front face
USB_MOUTH_IN = 1.0        # receptacle mouth inside the bottom end face
WALL, EDGE_R, OUT_R = 2.0, 2.0, 5.0
IN_R = 1.0                # inner plan corner radius (outside stays r 5)
USB_W, USB_H, USB_LEN = 8.94, 3.26, 7.35
USB_RECESS = (13.0, 7.6, 3.0)   # cable-plug recess on the bottom end face (X across, Z, r) -- same as the single board
USB_RECESS_GAP = 0.55           # recess floor this far outside the receptacle mouth
# ---------------- this variant ----------------
FLOOR_T, FRONT_T = 1.4, 1.6
IN_W = W_OUT - 2*WALL                          # 31.9 (t122u; was 27.9): Feather edge to inner wall 4.52 on both sides
IN_X0, IN_X1 = -IN_W/2, IN_W/2
HOLDER_W, HOLDER_L, HOLDER_H = 20.9, 77.7, 21.31   # MPD BH-18650-PC (datasheet), PC pins 72.9 apart
HOLDER_POCKET = 0.5                            # floor pocket the holder base sits in (locates it; glue optional)
DECK_GAP = 0.4                                 # cell top to deck underside
DECK_T = 1.0
F_STANDOFF = 0.4                               # printed pads under the Feather's four holes
FM_GAP_FRONT = 1.5                             # t122u: FM module FLIPPED, flat (solder) side toward the front face, held
                                               #   this far below the ceiling by short front-shell standoffs (cut the
                                               #   header pins / jack tails on that side to <= 1.2 mm)
FM_PEG_D = 3.4                                 # centring pegs in its 3.8 holes (front standoffs and deck posts)
FM_PEG_IN = 0.6                                #   each peg reaches this far into the 1.6 mm hole
# Feather RP2040 (Adafruit 4884): 50.8 x 22.86 x 1.6, parts up to 5.5 mm (JST-PH) above its top face.
F_LEN, F_W, F_T, F_PARTS_H = 50.8, 22.86, 1.6, 5.5
# Z stack
HOLDER = dict(x0=-HOLDER_W/2, x1=HOLDER_W/2, z0=FLOOR_T-HOLDER_POCKET)
HOLDER["z1"] = HOLDER["z0"]+HOLDER_H
DECK_Z0 = HOLDER["z1"] + DECK_GAP
DECK_Z1 = DECK_Z0 + DECK_T                     # = front/back split
Z_SPLIT = DECK_Z1
F_Z0 = DECK_Z1 + F_STANDOFF                    # Feather bottom face
F_Z1 = F_Z0 + F_T                              # Feather top face
DOCK_USB_Z = F_Z1 + USB_H/2                    # Feather USB-C centre
Z_CEIL = T - FRONT_T
assert abs((T - DOCK_USB_Z) - DOCK_USB_FROM_FRONT) < 0.01, (T - DOCK_USB_Z)
# FM module (Victor, 2026-11-24): 27.25 x 27.25 x 1.6 PCB, 3.8 mm holes in the corners 20 mm apart, standard 6.35 x 14
# headphone jack (centred on the bottom edge, 1 mm past the board) and a 4-pin 90-degree through-board header, also
# centred at that edge. That edge faces the TOP end wall of the case (jack through the top end wall).
FM_S, FM_T = 27.25, 1.6
FM_HOLE_D, FM_HOLE_PITCH = 3.8, 20.0
FM_JACK_D, FM_JACK_L, FM_JACK_OUT = 6.35, 14.0, 1.0
FM_JACK_HOLE_D = round(FM_JACK_D + 2*0.3, 2)   # t122u: 6.95 = jack barrel + 0.3 per side (was 6.8 + a 1.8 mm outer chamfer);
                                               #   the barrel now reaches 1.5 mm into the end wall
FM_SHIFT = 1.5                                 # t122u: module 1.5 mm toward the top end (case length unchanged)
# Feather along Y: its USB-C mouth USB_MOUTH_IN inside the bottom outer face (Y = -WALL)
DOCK_USB_MOUTH_Y = -WALL + USB_MOUTH_IN        # -1.0
DOCK_USB_X = 0.0
# thumbwheel: Mitsumi SIQ-02FVS3 on a cradle on the deck at the right wall, just past the Feather's far end
WHEEL_R = 7.25
WHEEL_GAP = 0.45                               # dial edge to the Feather's far edge
WHEEL_SEAT_Z = DECK_Z1
WHEEL_DIAL_Z = (2.0, 4.0)                      # dial above the seat
WHEEL_BODY = (10.3, 3.85, 7.25)                # across (Y), toward the dial side (+X), toward the terminals (-X)
WHEEL_PUSH = 1.0
# FM module: jack at the top end; the case's inner length follows from Feather + wheel + module
def _f_far_y():
    d=json.load(open(os.path.join(ROOT,"ref","feather_rp2040_mech.json")))
    return DOCK_USB_MOUTH_Y + d["usb_overhang"] + F_LEN
F_Y0 = DOCK_USB_MOUTH_Y + json.load(open(os.path.join(ROOT,"ref","feather_rp2040_mech.json")))["usb_overhang"]
F_Y1 = F_Y0 + F_LEN
WHEEL = (IN_X1-4.3, round(F_Y1 + WHEEL_GAP + WHEEL_R, 2))
FM_Y0_BASE = round(WHEEL[1] + WHEEL_R + 0.5, 2)
IN_L = round(FM_Y0_BASE + FM_S + FM_JACK_OUT, 2)   # inner length unchanged by t122u (jack face was flush with the inner face)
FM_Y0 = round(FM_Y0_BASE + FM_SHIFT, 2)        # jack face now 1.5 into the 2.0 end wall, board edge 0.5 into it (relief slot)
FM = dict(x0=-FM_S/2, x1=FM_S/2, y0=FM_Y0, y1=FM_Y0+FM_S, z1=Z_CEIL-FM_GAP_FRONT)
FM["z0"] = FM["z1"]-FM_T
assert FM["z0"] - FM_JACK_D > DECK_Z0 + 0.15, "jack hits the deck underside / ledges"
L_OUT = IN_L + 2*WALL
FM_CX, FM_CY = 0.0, FM["y0"]+FM_S/2
FM_HOLES = [(FM_CX+sx*FM_HOLE_PITCH/2, FM_CY+sy*FM_HOLE_PITCH/2) for sy in (-1,1) for sx in (-1,1)]
FM_JACK_AXIS_Z = FM["z0"] - FM_JACK_D/2       # jack under the flipped board (it dips through a notch in the deck)
# t122u header: Victor's 4-pin header sticks out of the module's centre on the flat side, i.e. toward the front face
# after the flip; he cuts it back to the 1.5 mm gap (modelled as 1.2 mm stubs over the centre of the module).
FM_HDR = dict(w=4*2.54, d=2.54, stub=1.2, y=FM["y0"]+FM_S/2)
# holder: centred, 2.5 mm from the bottom end wall (wire room at both ends), + end at the BOTTOM (near the Feather BAT pin)
HOLDER.update(y0=2.5); HOLDER["y1"] = HOLDER["y0"]+HOLDER_L
assert HOLDER["y1"] < FM["y1"] + FM_JACK_OUT - FM_JACK_L - 1.0, "holder runs under the FM jack"
HOLDER_CX = 0.0
HOLDER_PINS = [(HOLDER_CX, HOLDER["y0"]+2.4, "+"), (HOLDER_CX, HOLDER["y1"]-2.4, "-")]
# power switch: SS-12F16 SPDT panel slide switch, plate in a groove inside the LEFT wall of the front shell, beside the
# wheel (geometry is built for the right wall and mirrored in the SCAD)
SW_L = 4.0                   # knob height above the plate (G4)
# switch: Y so its plate groove ends before the FM module; Z so its body clears the Feather's far edge (it rides above it)
SW_Y, SW_Z = round(FM_Y0_BASE - 0.4 - 19.7/2 - 0.2, 2), F_Z1 + 0.4 + 5.7/2
SW_PLATE = (19.7, 5.7, 0.5)
SW_BODY = (11.0, 5.7, 5.0)
SW_LUG_L, SW_LUG_P = 3.0, 3.0
SW_ACT = (3.0, 3.0)
SW_TRAVEL = 3.0
SW_SKIN = 1.2                # outer skin in front of the plate -> G4 knob 2.8 mm proud
# t122u (Victor: "not possible to insert ... It can have stands/studs where the holes are on the switch and I can melt
# them down"): the plate sits in a 0.8 mm pocket in the inner face of the left wall (put in from inside, no groove to
# slide along) on two heat-stake studs through its M2 holes (15 mm apart), melted over; deck ribs back up both plate ends.
SW_HOLE_P = 15.0             # SS-12F16 plate holes: M2 x 0.4 tapped (minor dia ~1.57), 15 mm apart
SW_STUD_D = 1.4              # heat-stake stud through the hole
SW_STUD_OUT = 1.5            # stud length past the 0.5 plate (material for the melted head)
SW_BACK_RIB = 2.0            # deck backing ribs at both plate ends (thickness across)
# Feather LEDs / RESET seen through the front face (light tunnels from the ceiling down to just above each part)
LED_TUN = dict(chg=(1.6, 0.6, 0.8), red=(1.6, 0.6, 0.8), neo=(2.6, 0.6, 1.3))   # bore d, wall, wall bottom above the Feather top
RESET_TUBE = (1.6, 0.6, 2.7)                   # bore d, wall, tube bottom above the Feather top (KMR2 button is 1.9 tall)
F_POST_D = 4.0                                 # front-shell hold-down posts on the Feather's four holes (t122u: 3.0 -> 4.0,
F_POST_SOCKET = (2.7, 1.3)                     #   with a 2.7 x 1.3 socket for the peg tip)
F_PEG_D = 2.2                                  # deck pegs through the Feather's 2.5 holes (0.15 clearance per side)
F_PEG_OUT = 1.0                                # t122u: pegs stick 1.0 mm out of the Feather's top face (centring)
FEATHER_DY = -0.9   # legacy: the case frame of ref/feather_rp2040_mech.json (feather_data.py); not a case position
# ---------------- Feather geometry from Adafruit's board (scripts/feather_data.py -> ref/feather_rp2040_mech.json) -------
def feather():
    d=json.load(open(os.path.join(ROOT,"ref","feather_rp2040_mech.json")))
    return d
def f2case(u,v,w):
    """Feather-local -> case frame (u from the board's USB-end edge, v from the centre line toward its JP3 (BAT/EN/USB)
    header edge, w above its bottom face). Components up, USB-C toward -Y, JP3 header on the left (-X)."""
    return (-v, F_Y0+u, F_Z0+w)
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
def feather_point(case_old):
    """a point given in the json's old case frame (X_old, Y_old) -> new case frame (X, Y)"""
    d=feather(); y0b=d["board_case"]["y0"]
    return f2case(case_old[1]-y0b, 19.0-case_old[0], 0)[:2]
def feather_leds():
    d=feather(); return {k: feather_point(d["leds"][n]) for k,n in (("chg","CHG"),("red","RED_D13"),("neo","NEOPIXEL"))}
def feather_reset():
    return feather_point(feather()["buttons"]["RESET"])
def feather_holes():
    d=feather(); y0b=d["board_case"]["y0"]
    return [f2case(hy-y0b, 19.0-hx, 0)[:2] for hx,hy in d["holes"]]
if __name__=="__main__":
    print(f"outer {W_OUT:.2f} W x {L_OUT:.2f} L x {T} T; holder {HOLDER}; deck {DECK_Z0:.2f}..{DECK_Z1:.2f}; FM {FM}; jack axis {FM_JACK_AXIS_Z:.2f}")
    print("feather usb", feather_usb(), "dock usb", (DOCK_USB_X, DOCK_USB_MOUTH_Y, DOCK_USB_Z), "wheel", WHEEL, "IN_L", IN_L)
    print("feather leds", feather_leds())
    for n,b in feather_boxes()[:3]+feather_boxes()[-1:]: print(n,[round(a,2) for a in b])
