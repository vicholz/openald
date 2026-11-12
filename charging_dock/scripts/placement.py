"""OpenALD Dock v1.0 board placement (KiCad board frame: origin = rear-left corner, X right, Y toward the FRONT, mm).
Parts live only in the free channels between the pocket footprints (the 3.1 mm floor pads sit on the PCB inside each
pocket footprint): X-channels kx 48.7-68.9 and 117.1-137.3, Y-channel ky 46.61-66.81, rear strip ky 0-8.0."""
import geom as G
BOARD_W, BOARD_H, CORNER_R = G.PCB_W, G.PCB_H, 2.0
PLUG = {n: G.k(*G.usb_xy(c, r)) for n, (c, r) in enumerate(G.SLOTS, 1)}
# pocket component keep-outs (tube outer footprint + 0.3), KiCad frame (x0, y0, x1, y1)
KEEPOUT = []
for (c, r) in G.SLOTS:
    x0, y0, x1, y1 = G.radio_box(c, r); m = G.POCKET_OUT + 0.3
    a = G.k(x0 - m, y1 + m); b = G.k(x1 + m, y0 - m); KEEPOUT.append((a[0], a[1], b[0], b[1]))
PEGS = []
for (c, r) in G.SLOTS:
    x0, y0, x1, y1 = G.radio_box(c, r)
    PEGS += [G.k(x0 + 6, y1 - 6), G.k(x1 - 6, y1 - 6)]
HOLES = [(58.8, 101.0), (127.2, 101.0), (55.0, 4.0), (131.0, 4.0), (4.0, 56.71), (182.0, 56.71)]
LEDPIPE = (93.0, 56.71)          # light-pipe axis (status LEDs D2/D3)
PL = {f"H{i+1}": (x, y, 0) for i, (x, y) in enumerate(HOLES)}
PL.update({f"H{i+7}": (x, y, 0) for i, (x, y) in enumerate(PEGS)})
# ---- input chain, rear strip (USB-C at the rear centre, mouth to the rear edge)
PL.update({"J1": (93.0, 3.65, 180), "U1": (102.4, 4.0, 90), "C2": (99.6, 5.4, 90), "R1": (106.1, 2.45, 0),
           "F1": (85.3, 4.4, 0), "D1": (78.8, 4.4, 180), "C1": (73.7, 4.4, 90),
           "Q1": (65.0, 4.4, 180), "R2": (70.6, 2.1, 0), "C3": (70.6, 3.9, 0), "R3": (70.6, 5.7, 0),
           "C4": (58.8, 15.2, 90)})
# ---- buck A (X-channel left), buck B = same layout shifted by one column pitch (X-channel right)
BUCK = {"U": (61.0, 30.0, 0), "L": (53.5, 30.5, 90), "C1": (66.6, 28.4, 90), "C2": (66.6, 23.6, 90), "C3": (59.0, 26.3, 0),
        "C4": (66.6, 32.4, 90), "C5": (57.0, 36.6, 90), "R3": (58.6, 36.6, 90), "R4": (60.2, 36.6, 90), "C10": (61.8, 36.6, 90),
        "R1": (63.4, 36.6, 90), "R2": (65.0, 36.6, 90), "C6": (50.8, 39.4, 90), "C7": (53.0, 39.4, 90), "C8": (55.2, 39.4, 90),
        "C9": (61.4, 42.2, 0)}
for s, (u, l, cb, rb, dx) in {"A": ("U2", "L1", 10, 10, 0.0), "B": ("U3", "L2", 30, 30, G.PITCH_X)}.items():
    for key, (x, y, a) in BUCK.items():
        ref = u if key == "U" else l if key == "L" else ("C%d" % (cb + int(key[1:])) if key[0] == "C" else "R%d" % (rb + int(key[1:])))
        PL[ref] = (round(x + dx, 3), y, a)
# ---- slot switches in the Y-channel, one cluster per slot next to its column
for n, (px, py) in PLUG.items():
    PL[f"J{1+n}"] = (px, py, 0)
    y = 62.0 if py > 60 else 51.4              # front-row slots: lower half of the Y-channel; back row: upper half
    x = px
    PL[f"U{3+n}"] = (x, y, 0); PL[f"C{50+n}"] = (x - 3.0, y, 90); PL[f"C{60+n}"] = (x + 3.2, y, 90)
    dy = 2.6 if py > 60 else -2.6
    PL[f"R{50+n}"] = (x, y + dy, 0); PL[f"R{60+n}"] = (x + 3.2, y + dy, 0)
# ---- status LEDs under the light pipe (between the centre pockets)
PL.update({"D2": (92.2, 56.71, 90), "D3": (93.8, 56.71, 90), "R4": (88.6, 55.9, 90), "R6": (87.0, 55.9, 90),
           "R5": (97.6, 56.71, 90), "Q2": (101.0, 56.71, 0)})
SILK = [("OpenALD Dock v1.0", 72.0, 56.71, 1.5), ("IN: USB-C PD >= 45 W (20V 2.25A or 15V 3A)", 140.0, 56.71, 0.8)]
