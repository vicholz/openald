"""OpenALD Dock v1.0 board placement (KiCad board frame: origin = rear-left corner, X right, Y toward the FRONT, mm).
2026-11-24 layout (2 columns x 3 rows, radios lying on their USB-C side): parts live only in the free channels between
the pocket footprints (the floor pads sit on the PCB inside each pocket footprint):
  X-channel (between the columns)  kx 95.5-115.6, full depth  -> buck A (beside row 1), buck B (beside row 2),
                                                                 status LEDs (light pipe), input bulk cap C4
  Y-channel 1 (rows 1/2)           ky 108.3-128.4, full width -> slot switch clusters of rows 1 and 2 (slots 1-4)
  Y-channel 2 (rows 2/3)           ky 48.1-68.2,   full width -> slot switch clusters of row 3 (slots 5-6)
  rear strip                       ky 0-7.95                  -> USB-C PD input chain (J1 at the rear centre)"""
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
XC = round((G.radio_box(0, 0)[2] + G.radio_box(1, 0)[0]) / 2 - G.PCB_X0, 3)          # X-channel centre, kx 105.55
YC1 = round(G.PCB_Y1 - (G.radio_box(0, 0)[3] + G.radio_box(0, 1)[1]) / 2, 3)        # Y-channel 1 centre, ky 118.36
YC2 = round(G.PCB_Y1 - (G.radio_box(0, 1)[3] + G.radio_box(0, 2)[1]) / 2, 3)        # Y-channel 2 centre, ky 58.13
# M3 clamp screws: both ends of both Y-channels (in the 6 mm side margins) + two in the rear strip
HOLES = [(2.6, YC1), (BOARD_W - 2.6, YC1), (2.6, YC2), (BOARD_W - 2.6, YC2), (17.1, 3.9), (BOARD_W - 17.1, 3.9)]
LEDPIPE = (XC, YC1)              # light-pipe axis (status LEDs D2/D3), where the X-channel crosses Y-channel 1
PL = {f"H{i+1}": (round(x, 3), round(y, 3), 0) for i, (x, y) in enumerate(HOLES)}
PL.update({f"H{i+7}": (x, y, 0) for i, (x, y) in enumerate(PEGS)})
# ---- input chain, rear strip (USB-C at the rear centre, mouth to the rear edge); same relative layout as before
_dx = XC - 93.0
PL.update({k: (round(x + _dx, 3), y, a) for k, (x, y, a) in {
    "J1": (93.0, 3.65, 180), "U1": (102.4, 4.0, 90), "C2": (99.6, 5.4, 90), "R1": (106.1, 2.45, 0),
    "F1": (85.3, 4.4, 0), "D1": (78.8, 4.4, 180), "C1": (73.7, 4.4, 90),
    "Q1": (65.0, 4.4, 180), "R2": (70.6, 2.1, 0), "C3": (70.6, 3.9, 0), "R3": (70.6, 5.7, 0)}.items()})
PL["C4"] = (XC, 20.0, 90)        # 100 uF bulk (8 x 10 can) in the X-channel behind row 3; under a raised housing
# ---- buck A (X-channel beside row 1) and buck B (X-channel beside row 2): the old block, translated
BUCK = {"U": (61.0, 30.0, 0), "L": (53.5, 30.5, 90), "C1": (66.6, 28.4, 90), "C2": (66.6, 23.6, 90), "C3": (59.0, 26.3, 0),
        "C4": (66.6, 32.4, 90), "C5": (57.0, 36.6, 90), "R3": (58.6, 36.6, 90), "R4": (60.2, 36.6, 90), "C10": (61.8, 36.6, 90),
        "R1": (63.4, 36.6, 90), "R2": (65.0, 36.6, 90), "C6": (50.8, 39.4, 90), "C7": (53.0, 39.4, 90), "C8": (55.2, 39.4, 90),
        "C9": (61.4, 42.2, 0)}
_bx = XC - 58.7
for s, (u, l, cb, rb, ky_c) in {"A": ("U2", "L1", 10, 10, G.PCB_Y1 - 23.0), "B": ("U3", "L2", 30, 30, G.PCB_Y1 - 84.0)}.items():
    _by = ky_c - 32.9
    for key, (x, y, a) in BUCK.items():
        ref = u if key == "U" else l if key == "L" else ("C%d" % (cb + int(key[1:])) if key[0] == "C" else "R%d" % (rb + int(key[1:])))
        PL[ref] = (round(x + _bx, 3), round(y + _by, 3), a)
# ---- slot switches in the Y-channels, one cluster per slot at its plug's X
#   row 1 (slots 1-2): front half of Y-channel 1 (R/C toward the front); row 2 (3-4): back half of Y-channel 1;
#   row 3 (5-6): back half of Y-channel 2
YCH1 = (YC1 - 10.05, YC1 + 10.05); YCH2 = (YC2 - 10.05, YC2 + 10.05)
for n, (px, py) in PLUG.items():
    PL[f"J{1+n}"] = (px, py, 0)
    row = (n - 1) // 2
    if row == 0:   y, dy = YCH1[1] - 4.4, 2.6
    elif row == 1: y, dy = YCH1[0] + 4.4, -2.6
    else:          y, dy = YCH2[0] + 4.4, -2.6
    x = px
    PL[f"U{3+n}"] = (x, round(y, 3), 0); PL[f"C{50+n}"] = (x - 3.0, round(y, 3), 90); PL[f"C{60+n}"] = (x + 3.2, round(y, 3), 90)
    PL[f"R{50+n}"] = (x, round(y + dy, 3), 0); PL[f"R{60+n}"] = (x + 3.2, round(y + dy, 3), 0)
# ---- status LEDs under the light pipe (old block, translated)
_lx, _ly = LEDPIPE[0] - 93.0, LEDPIPE[1] - 56.71
PL.update({k: (round(x + _lx, 3), round(y + _ly, 3), a) for k, (x, y, a) in {
    "D2": (92.2, 56.71, 90), "D3": (93.8, 56.71, 90), "R4": (88.6, 55.9, 90), "R6": (87.0, 55.9, 90),
    "R5": (97.6, 56.71, 90), "Q2": (101.0, 56.71, 0)}.items()})
SILK = [("OpenALD Dock v1.0", 70.0, YC1, 1.5), ("IN: USB-C PD >= 45 W (20V 2.25A or 15V 3A)", 70.0, YC2 + 2.0, 0.8)]
# parts taller than the room under the deck (TOP_Z - DECK_T - PCB_Z1 = 8.6 mm) get a raised housing in the shell
TALL = ["C4"]
