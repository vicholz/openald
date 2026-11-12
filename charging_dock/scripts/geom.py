"""OpenALD Dock v1.0 - single source of truth for the dock geometry (mm).
Dock frame: X right, Y toward the back, Z up; origin = front-left-bottom corner of the case.
KiCad board frame: kx = X - PCB_X0, ky = PCB_Y1 - Y (Y down, origin = board top-left = rear-left)."""
# ---- radio envelope (see ../DOCK_INTERFACE.md) ----
RW, RD = 43.00, 33.41            # radio width x depth (case thickness)
USB_FROM_FRONT = 6.57            # USB-C centreline behind the radio front face
MOUTH_UP = 2.50                  # receptacle mouth above the radio bottom face
# ---- layout ----
COLS, ROWS = 3, 2
GAP = 25.4                       # 1.0 in between radios (X and Y)
SIDE, FRONT, BACK = 6.0, 6.0, 13.5
PITCH_X, PITCH_Y = RW + GAP, RD + GAP
OUT_W = 2*SIDE + COLS*RW + (COLS-1)*GAP          # 191.8
OUT_D = FRONT + BACK + ROWS*RD + (ROWS-1)*GAP     # 111.72
WALL = 2.0                       # outer skirt wall
# ---- pockets ----
POCKET_DEPTH = 50.8
CLR_GUIDE, GUIDE_H = 0.35, 12.0
CLR_UPPER = 0.60
POCKET_WALL = 2.0
CHAMFER = 3.0
# ---- Z stack ----
BASE_T = 2.0                     # base tray floor
STANDOFF = 5.0
PCB_T = 1.6
PCB_Z0 = BASE_T + STANDOFF       # 7.0 PCB bottom
PCB_Z1 = PCB_Z0 + PCB_T          # 8.6 PCB top
PAD_T = 3.1                      # floor pad thickness
FLOOR_Z = PCB_Z1 + PAD_T         # 11.7 radio rests here
PLUG_H = 11.6                    # HX TYPE C-M 16P plug height above the PCB (drawing 11.60; see README risk)
PLUG_TOP = PCB_Z1 + PLUG_H       # 20.2
TOP_Z = FLOOR_Z + POCKET_DEPTH   # 62.5 deck top
INSERTION = PLUG_TOP - (FLOOR_Z + MOUTH_UP)       # 6.0 past the receptacle mouth
# ---- PCB ----
PCB_X0, PCB_Y0 = WALL + 0.9, WALL + 0.9           # 2.9 (0.9 gap to the skirt inner face)
PCB_X1, PCB_Y1 = OUT_W - PCB_X0, OUT_D - PCB_Y0
PCB_W, PCB_H = PCB_X1 - PCB_X0, PCB_Y1 - PCB_Y0
def radio_box(c, r):
    """radio footprint (x0, y0, x1, y1) in the dock frame; front face at y0"""
    x0 = SIDE + c*PITCH_X; y0 = FRONT + r*PITCH_Y
    return x0, y0, x0 + RW, y0 + RD
def usb_xy(c, r):
    x0, y0, x1, y1 = radio_box(c, r); return (x0 + RW/2, y0 + USB_FROM_FRONT)
def k(x, y):  return (round(x - PCB_X0, 4), round(PCB_Y1 - y, 4))     # dock -> KiCad
def d(kx, ky): return (kx + PCB_X0, PCB_Y1 - ky)                       # KiCad -> dock
SLOTS = [(c, r) for r in (0, 1) for c in range(3)]   # slot n = index+1: 1-3 front row L->R, 4-6 back row L->R
POCKET_OUT = CLR_UPPER + POCKET_WALL                  # pocket tube outer face beyond the radio footprint
if __name__ == "__main__":
    print("outer %.2f x %.2f x %.2f" % (OUT_W, OUT_D, TOP_Z), "pcb %.2f x %.2f" % (PCB_W, PCB_H), "insertion %.2f" % INSERTION)
    for n, (c, r) in enumerate(SLOTS, 1): print(n, usb_xy(c, r), k(*usb_xy(c, r)))
