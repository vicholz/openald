"""OpenALD Dock v1.0 (t121u 2026-11-24: FLAT dock - a closed box with six RECESSED pockets, 25 mm deep, in an aligned
3 x 2 grid; radios stand upright on their bottom-end USB-C. t120u had 50.8 mm pocket walls on a low deck, t116u a
half-pitch back-row offset) - single source of truth for the dock geometry (mm).
Dock frame: X right, Y toward the back, Z up; origin = front-left-bottom corner of the case.
KiCad board frame: kx = X - PCB_X0, ky = PCB_Y1 - Y (Y down, origin = board top-left = rear-left)."""
# ---- radio envelope (see ../DOCK_INTERFACE.md) ----
# t116u: the dockable OpenALD radios (single-board, Feather; the MI03 is NOT dock-compatible) are 31.9 wide x 33.86
# thick, with the USB-C in the BOTTOM END face, centred across the width, 6.62 behind the front face, mouth 1.0 inside
# the face. They stand upright (USB-C down, front face toward the user), so the pocket footprint is width x thickness.
# Lengths differ (single-board 89.75, Feather 98.71) and do not matter.
RL, RT = 31.9, 33.86             # pocket footprint: radio width (dock X) x thickness (dock Y)
EDGE_R = 2.0                     # radio edge radius = pocket footprint corner radius
USB_FROM_END = RL / 2            # USB-C centre from the pocket's left end (dock X): centred across the radio width
USB_FROM_FRONT = 6.62            # USB-C centreline behind the radio front face (dock Y)
MOUTH_UP = 1.00                  # receptacle mouth inside the radio's bottom end face (above the pocket floor)
MOUTHS = {"single_board": 1.00, "feather": 1.00}
LENGTHS = {"single_board": 89.75, "feather": 98.71}   # height above the pocket floor when docked
# ---- layout ----
COLS, ROWS = 3, 2
GAP = 25.4                       # 1.0 in between radios (X and Y)
SIDE, FRONT, BACK = 6.0, 6.0, 13.5
PITCH_X, PITCH_Y = RL + GAP, RT + GAP
STAGGER = 0.0                    # t120u: aligned grid (t116u had the front row shifted by half a pitch)
OUT_W = 2*SIDE + STAGGER + COLS*RL + (COLS-1)*GAP     # 158.5
OUT_D = FRONT + BACK + ROWS*RT + (ROWS-1)*GAP         # 112.62
WALL = 2.0                       # outer skirt wall
# ---- pockets (t121u: recessed into a flat top; Victor: "The dock should be flat with recessed square holes that are
# 2-4cm deep to act as a guide") ----
CLR_GUIDE = 0.35                 # radio-to-wall clearance per side
POCKET_WALL = 2.0
POCKET_DEPTH = 25.0              # flat top above the pocket floor (pad top). 25 mm: the radio is guided for 18 mm before
                                 #   the plug tip enters its opening and stands 25 mm deep (tilt <= ~1.6 deg in the clearance)
CHAMFER = 1.5                    # lead-in on the pocket rims
# Sight windows (the Feather's CHG / red LEDs sit 4 mm and its NeoPixel 20 mm above the floor, all below the top):
# each pocket's front wall has a WIN_W wide window from WIN_Z above the floor up through the top. Front row: the window
# runs straight out through the dock's front face. Back row: it opens into a closed trench in the top between the rows
# whose floor rises toward the front at TRENCH_ANG (ends before the front-row pocket).
WIN_W = 20.0                     # centred on the pocket (the LEDs are at -6.0 / +6.0 / +5.4 from the radio centre)
WIN_Z = 2.0                      # window sill above the pocket floor (LED centres 4.0 / 20.0)
TRENCH_ANG = 50.0
# No side notch: the single-board radio's switch knob / wheel start ~36 mm above the floor and the Feather's are higher
# still, all above the 25 mm pocket (checked by check_dock_fit.py).
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
TOP_Z = FLOOR_Z + POCKET_DEPTH   # 37.3 flat top = overall dock height
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
    """radio footprint (x0, y0, x1, y1) in the dock frame; front face at y0 (row 0 = front row)"""
    x0 = SIDE + c*PITCH_X + (STAGGER if r == 0 else 0.0); y0 = FRONT + r*PITCH_Y
    return x0, y0, x0 + RL, y0 + RT
def usb_xy(c, r):
    x0, y0, x1, y1 = radio_box(c, r); return (x0 + USB_FROM_END, y0 + USB_FROM_FRONT)
def k(x, y):  return (round(x - PCB_X0, 4), round(PCB_Y1 - y, 4))     # dock -> KiCad
def d(kx, ky): return (kx + PCB_X0, PCB_Y1 - ky)                       # KiCad -> dock
SLOTS = [(c, r) for r in range(ROWS) for c in range(COLS)]   # slot n = index+1: 1-3 front row L->R, 4-6 back row L->R
POCKET_OUT = CLR_GUIDE + POCKET_WALL                  # pocket tube outer face beyond the radio footprint
if __name__ == "__main__":
    print("outer %.2f x %.2f x %.2f (pocket depth %.2f)" % (OUT_W, OUT_D, TOP_Z, POCKET_DEPTH), "pcb %.2f x %.2f" % (PCB_W, PCB_H), "insertion %.2f" % INSERTION)
    for r in MOUTHS: print(r, "insertion %.2f" % insertion(r))
    for n, (c, r) in enumerate(SLOTS, 1): print(n, usb_xy(c, r), k(*usb_xy(c, r)))
