"""OpenALD Dock v1.0 (2026-11-24: 2 x 3 slots, radios lying on their USB-C side) - single source of truth for the dock geometry (mm).
Dock frame: X right, Y toward the back, Z up; origin = front-left-bottom corner of the case.
KiCad board frame: kx = X - PCB_X0, ky = PCB_Y1 - Y (Y down, origin = board top-left = rear-left)."""
# ---- radio envelope (see ../DOCK_INTERFACE.md) ----
# 2026-11-24 unified envelope: the dockable OpenALD radios (single-board, Feather; the MI03 is NOT dock-compatible) are 89.75 long x 34.83 thick with the
# USB-C on its -X long side, centred 30.3 from the top outer end and 7.55 behind the front face, mouth 1.0 inside the
# side face. Widths differ (single-board 30.5, Feather 32.9) and do not matter: radios dock LYING ON THEIR
# USB-C SIDE, front face toward the user, top end to the left, so the pocket footprint is length x thickness.
RL, RT = 89.75, 34.83            # radio length (dock X) x thickness (dock Y)
EDGE_R = 2.0                     # radio edge radius = pocket footprint corner radius
USB_FROM_END = 30.3              # USB-C centre from the radio's top outer end (dock X from the pocket's left end)
USB_FROM_FRONT = 7.55            # USB-C centreline behind the radio front face (dock Y)
MOUTH_UP = 1.00                  # receptacle mouth inside the radio's USB-C side face (above the pocket floor)
MOUTHS = {"single_board": 1.00, "feather": 1.00}
WIDTHS = {"single_board": 30.5, "feather": 32.9}   # height above the pocket floor when docked
# ---- layout ----
COLS, ROWS = 2, 3
GAP = 25.4                       # 1.0 in between radios (X and Y)
SIDE, FRONT, BACK = 6.0, 6.0, 13.5
PITCH_X, PITCH_Y = RL + GAP, RT + GAP
OUT_W = 2*SIDE + COLS*RL + (COLS-1)*GAP          # 216.9
OUT_D = FRONT + BACK + ROWS*RT + (ROWS-1)*GAP     # 174.79
WALL = 2.0                       # outer skirt wall
# ---- pockets (shallow trays: the radio lies on its side) ----
CLR_GUIDE = 0.35                 # radio-to-wall clearance per side
POCKET_WALL = 2.0
FIN_H = 14.0                     # back + end walls rise this far above the pocket floor
FRONT_WALL_H = 6.0               # front wall = deck height above the floor (low, so the front face / LCD stays visible)
CHAMFER = 1.5                    # lead-in on the fin tops
# ---- Z stack ----
BASE_T = 2.0                     # base tray floor
STANDOFF = 4.1                   # 2026-11-12: was 5.0; -0.9 so the +0.9 pad keeps the outer height and pocket depth
PCB_T = 1.6
PCB_Z0 = BASE_T + STANDOFF       # 6.1 PCB bottom
PCB_Z1 = PCB_Z0 + PCB_T          # 7.7 PCB top
PAD_T = 4.6                      # floor pad thickness (2026-11-24: 4.0 -> 4.6 for the 1.0 receptacle mouth of the unified radios)
FLOOR_Z = PCB_Z1 + PAD_T         # 12.3 radio rests here
PLUG_H = 11.6                    # HX TYPE C-M 16P plug height above the PCB (drawing 11.60; see README risk)
PLUG_TOP = PCB_Z1 + PLUG_H       # 19.3
TOP_Z = FLOOR_Z + FRONT_WALL_H   # 18.3 deck top
FIN_Z = FLOOR_Z + FIN_H          # 26.3 top of the pocket back / end walls (overall dock height)
INSERTION = PLUG_TOP - (FLOOR_Z + MOUTH_UP)       # 6.0 past the receptacle mouth (both radios)
# USB Type-C (spec R2.x, sec. 3.2): receptacle effective shell length 6.20 +/- 0.20 = plug travel past the mouth at full
# seat (plug shell 6.65 +/- 0.10, so a seated plug's base stands ~0.45 outside the mouth). Design target: 6.0, i.e. 0-0.4 mm
# short of bottoming, so the radio's weight rests on the printed pad, never on the plug, with the contacts fully engaged.
SEAT_NOM, SEAT_TOL = 6.20, 0.20
TARGET_INSERTION = 6.00
def insertion(radio="single_board", pad_t=None):
    """plug travel past the receptacle mouth for a radio on a pad of thickness pad_t (default PAD_T)"""
    pt = PAD_T if pad_t is None else pad_t
    return PLUG_TOP - (PCB_Z1 + pt + MOUTHS[radio])
# If a real plug measures taller than PLUG_H: pad thickness for the target = PAD_T + (measured - PLUG_H); reprint the
# pads only (FLOOR_Z and the pocket would move up with it unless STANDOFF is lowered by the same amount).
# ---- PCB ----
PCB_X0, PCB_Y0 = WALL + 0.9, WALL + 0.9           # 2.9 (0.9 gap to the skirt inner face)
PCB_X1, PCB_Y1 = OUT_W - PCB_X0, OUT_D - PCB_Y0
PCB_W, PCB_H = PCB_X1 - PCB_X0, PCB_Y1 - PCB_Y0
def radio_box(c, r):
    """radio footprint (x0, y0, x1, y1) in the dock frame; front face at y0"""
    x0 = SIDE + c*PITCH_X; y0 = FRONT + r*PITCH_Y
    return x0, y0, x0 + RL, y0 + RT
def usb_xy(c, r):
    x0, y0, x1, y1 = radio_box(c, r); return (x0 + USB_FROM_END, y0 + USB_FROM_FRONT)
def k(x, y):  return (round(x - PCB_X0, 4), round(PCB_Y1 - y, 4))     # dock -> KiCad
def d(kx, ky): return (kx + PCB_X0, PCB_Y1 - ky)                       # KiCad -> dock
SLOTS = [(c, r) for r in range(ROWS) for c in range(COLS)]   # slot n = index+1: 1-2 front row L->R, 3-4 middle, 5-6 back
POCKET_OUT = CLR_GUIDE + POCKET_WALL                  # pocket tube outer face beyond the radio footprint
if __name__ == "__main__":
    print("outer %.2f x %.2f x %.2f (deck %.2f)" % (OUT_W, OUT_D, FIN_Z, TOP_Z), "pcb %.2f x %.2f" % (PCB_W, PCB_H), "insertion %.2f" % INSERTION)
    for r in MOUTHS: print(r, "insertion %.2f" % insertion(r))
    for n, (c, r) in enumerate(SLOTS, 1): print(n, usb_xy(c, r), k(*usb_xy(c, r)))
