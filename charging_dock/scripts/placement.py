"""OpenALD Dock v1.0 board placement (KiCad board frame: origin = rear-left corner, X right, Y toward the FRONT, mm).
t120u layout (aligned 3 x 2 grid, radios standing upright): parts live only outside the pocket footprints (the floor
pads sit on the PCB inside each pocket footprint):
  Y-channel (between the rows)      full width          -> the six slot switch clusters (front-row slots in its front
                                                           half, back-row slots in its back half), one at each plug's X
  front-row gaps (between radios)   20 mm wide          -> buck A (gap 1-2), buck B (gap 2-3)
  back-row gap 4-5                  20 mm wide          -> status LEDs (light pipe) + input bulk cap C4
  back-row gap 5-6                  20 mm wide          -> M3 clamp screw, silkscreen title
  rear strip                        ky 0-8.25           -> USB-C PD input chain (J1 behind the back-row gap 5-6)"""
import geom as G
BOARD_W, BOARD_H, CORNER_R = G.PCB_W, G.PCB_H, 2.0
PLUG = {n: G.k(*G.usb_xy(c, r)) for n, (c, r) in enumerate(G.SLOTS, 1)}
# pocket component keep-outs (pocket wall outer footprint + 0.3), KiCad frame (x0, y0, x1, y1)
KEEPOUT = []
for (c, r) in G.SLOTS:
    x0, y0, x1, y1 = G.radio_box(c, r); m = G.POCKET_OUT + 0.3
    a = G.k(x0 - m, y1 + m); b = G.k(x1 + m, y0 - m); KEEPOUT.append((a[0], a[1], b[0], b[1]))
PEGS = []
for (c, r) in G.SLOTS:
    x0, y0, x1, y1 = G.radio_box(c, r)
    PEGS += [G.k(x0 + 6, y1 - 6), G.k(x1 - 6, y1 - 6)]
_f = [G.radio_box(c, 0) for c in range(G.COLS)]          # front row boxes (dock frame)
_b = [G.radio_box(c, 1) for c in range(G.COLS)]          # back row boxes
XC = round(G.OUT_W / 2 - G.PCB_X0, 3)                    # board centre line
XG1 = round((_f[0][2] + _f[1][0]) / 2 - G.PCB_X0, 3)     # column gap 1-2 / 4-5 centre (aligned grid)
XG2 = round((_f[1][2] + _f[2][0]) / 2 - G.PCB_X0, 3)     # column gap 2-3 / 5-6 centre
YF = round(G.PCB_Y1 - (_f[0][1] + _f[0][3]) / 2, 3)      # front-row centre (ky)
YB = round(G.PCB_Y1 - (_b[0][1] + _b[0][3]) / 2, 3)      # back-row centre (ky)
YC1 = round(G.PCB_Y1 - (_f[0][3] + _b[0][1]) / 2, 3)     # Y-channel centre (ky)
# M3 clamp screws: both ends of the Y-channel, two in the rear strip, two in the back-row gaps
HOLES = [(3.6, YC1), (BOARD_W - 3.6, YC1), (17.1, 3.9), (BOARD_W - 17.1, 3.9), (XG1, YB + 13.5), (XG2, YB)]
LEDPIPE = (round(XG1 - 1.2, 3), YB - 10.0)   # light-pipe axis (status LEDs D2/D3), back-row gap 4-5
PL = {f"H{i+1}": (round(x, 3), round(y, 3), 0) for i, (x, y) in enumerate(HOLES)}
PL.update({f"H{i+7}": (x, y, 0) for i, (x, y) in enumerate(PEGS)})
# ---- input chain, rear strip (USB-C at the rear centre, mouth to the rear edge); same relative layout as before
# input chain: J1 in the rear strip behind the gap between back-row slots 5 and 6 (straight behind a pocket its 7.3 mm
# deep body would run under that pocket's floor pad)
XIN = round((_b[1][2] + _b[2][0]) / 2 - G.PCB_X0, 3)
_dx = XIN - 93.0
PL.update({k: (round(x + _dx, 3), y, a) for k, (x, y, a) in {
    "J1": (93.0, 3.65, 180), "U1": (102.4, 4.0, 90), "C2": (99.6, 5.4, 90), "R1": (106.1, 2.45, 0),
    "F1": (85.3, 4.4, 0), "D1": (78.8, 4.4, 180), "C1": (73.7, 4.4, 90),
    "Q1": (65.0, 4.4, 180), "R2": (70.6, 2.1, 0), "C3": (70.6, 3.9, 0), "R3": (70.6, 5.7, 0)}.items()})
PL["C4"] = (XG1, YB + 2.0, 90)   # 100 uF bulk (8 x 10 can) in the back-row gap 4-5; under a raised housing
# ---- buck A (front-row gap 1-2) and buck B (front-row gap 2-3): the old block, translated
BUCK = {"U": (61.0, 30.0, 0), "L": (53.5, 30.5, 90), "C1": (66.6, 28.4, 90), "C2": (66.6, 23.6, 90), "C3": (59.0, 26.3, 0),
        "C4": (66.6, 32.4, 90), "C5": (57.0, 36.6, 90), "R3": (58.6, 36.6, 90), "R4": (60.2, 36.6, 90), "C10": (61.8, 36.6, 90),
        "R1": (63.4, 36.6, 90), "R2": (65.0, 36.6, 90), "C6": (50.8, 39.4, 90), "C7": (53.0, 39.4, 90), "C8": (55.2, 39.4, 90),
        "C9": (61.4, 42.2, 0)}
for s, (u, l, cb, rb, kx_c, ky_c) in {"A": ("U2", "L1", 10, 10, XG1, YF), "B": ("U3", "L2", 30, 30, XG2, YF)}.items():
    _bx = kx_c - 58.7; _by = ky_c - 32.9
    for key, (x, y, a) in BUCK.items():
        ref = u if key == "U" else l if key == "L" else ("C%d" % (cb + int(key[1:])) if key[0] == "C" else "R%d" % (rb + int(key[1:])))
        PL[ref] = (round(x + _bx, 3), round(y + _by, 3), a)
# ---- slot switches in the Y-channel, one cluster per slot at its plug's X
#   front row (slots 1-3): front half of the Y-channel (R/C toward the front); back row (4-6): back half
YCH1 = (YC1 - 10.05, YC1 + 10.05)
for n, (px, py) in PLUG.items():
    PL[f"J{1+n}"] = (px, py, 0)
    row = (n - 1) // G.COLS
    if row == 0:   y, dy = YCH1[1] - 4.4, 2.6
    else:          y, dy = YCH1[0] + 4.4, -2.6
    x = px
    PL[f"U{3+n}"] = (x, round(y, 3), 0); PL[f"C{50+n}"] = (x - 3.0, round(y, 3), 90); PL[f"C{60+n}"] = (x + 3.2, round(y, 3), 90)
    PL[f"R{50+n}"] = (x, round(y + dy, 3), 0); PL[f"R{60+n}"] = (x + 3.2, round(y + dy, 3), 0)
# ---- status LEDs under the light pipe (old block, translated)
_lx, _ly = LEDPIPE[0] - 93.0, LEDPIPE[1] - 56.71
PL.update({k: (round(x + _lx, 3), round(y + _ly, 3), a) for k, (x, y, a) in {
    "D2": (92.2, 56.71, 90), "D3": (93.8, 56.71, 90), "R4": (88.6, 55.9, 90), "R6": (87.0, 55.9, 90),
    "R5": (97.6, 56.71, 90), "Q2": (101.0, 56.71, 0)}.items()})
SILK = [("OpenALD Dock v1.0", XG2, YB + 10.0, 1.0), ("IN: USB-C PD >= 45 W (20V 2.25A or 15V 3A)", 40.0, 6.3, 0.8)]
# parts taller than the room under the deck (TOP_Z - DECK_T - PCB_Z1 = 5.1 mm) get a raised housing in the shell
TALL = ["C4", "C19", "C39"]
