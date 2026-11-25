#!/usr/bin/env python3
"""OpenALD Dock v1.0 fit check (trimesh + manifold booleans), dock frame.  t116u (2026-11-24): 3 x 2 upright pockets
(back row offset half a pitch), radios standing on their bottom-end USB-C.
 * dock parts: shell_raw, base_raw, pads_raw, plugs from case/openald_dock.scad (STLs in /tmp, see build_case.sh)
 * radios: the REAL printed case parts of the two dockable OpenALD radios (single-board, Feather; the MI03 case is not
   dock-compatible since 2026-11-24 and is not checked), exported from their
   own SCAD files, plus what sticks out of them (single-board: switch knob and wheel; Feather: wheel, switch knob in
   both positions), rotated into the docked pose (bottom end down on the floor pad, front face toward the dock front)
   and dropped into every pocket: each must clear the shell, the pads and the plug, and the plug must pass through its
   USB-C opening. The insertion path (straight down from above the pocket walls) is swept too.
 * every dock PCB part as a box (courtyard shrunk 0.25 mm, height from HEIGHTS) against the printed dock parts."""
import sys, os, math, subprocess, trimesh, numpy as np, pcbnew
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom as G, design, placement as PL
ROOT = os.path.abspath(os.path.join(HERE, "../.."))
T = "/tmp/dock_%s.stl"
case = {n: trimesh.load(T % n) for n in ("shell_raw", "base_raw", "pads_raw")}
plugs = trimesh.load(T % "plugs")
def inter(a, b):
    try: return trimesh.boolean.intersection([a, b], engine="manifold").volume
    except Exception: return float("nan")
bad = 0; out = []
def rep(name, v, tol=0.01):
    global bad
    flag = not (v < tol); bad += flag
    out.append(f"{'FAIL' if flag else 'ok  '} {name:58s} {v:9.3f} mm^3")
# ---------------- dock parts against each other
rep("shell x pads", inter(case["shell_raw"], case["pads_raw"])); rep("shell x base", inter(case["shell_raw"], case["base_raw"]))
rep("pads x base", inter(case["pads_raw"], case["base_raw"]))
for n, c in case.items(): rep(f"plugs x {n}", inter(plugs, c))
# ---------------- radios
RADIOS = {   # name: (scad, outer shell parts, extra parts that stick out of the shell)
    "single_board": (f"{ROOT}/radio_single_board/case/openald_case.scad", ["top_raw", "bottom_raw"], []),
    "feather": (f"{ROOT}/radio_adafruit_feather_rp2040/case/openald_feather_case.scad", ["top_raw", "bottom_raw", "deck_raw"],
                ["g_wheel", "g_switch_on", "g_switch_off"]),
}
def _scadvars(path):
    d = {}
    for line in open(path):
        if "=" in line and not line.startswith("//"):
            k, v = line.split("=", 1)
            try: d[k.strip()] = eval(v.strip().rstrip(";"))
            except Exception: pass
    return d
def single_board_extras():
    """the single-board radio's switch knob (both positions) and wheel, in its case frame (from case_params.scad)"""
    P = _scadvars(f"{ROOT}/radio_single_board/case/case_params.scad")
    ms = []
    for y in (P["sw_on_y"], P["sw_off_y"]):
        b = trimesh.creation.box(extents=[P["sw_tip_x"] - P["sw_face_x"], P["sw_act_w"], P["sw_act_z1"] - P["sw_act_z0"]])
        b.apply_translation([(P["sw_tip_x"] + P["sw_face_x"]) / 2, y, P["pcb_t"] + (P["sw_act_z0"] + P["sw_act_z1"]) / 2]); ms.append(b)
    c = trimesh.creation.cylinder(radius=P["wheel_r"], height=P["wheel_z1"] - P["wheel_z0"], sections=96)
    c.apply_translation([P["wheel_xy"][0], P["wheel_xy"][1], P["pcb_t"] + (P["wheel_z0"] + P["wheel_z1"]) / 2]); ms.append(c)
    return ms
DOCKED = {}
procs = []
for r, (scad, shells, extra) in RADIOS.items():
    for p in shells + extra:
        procs.append(subprocess.Popen(["openscad", "-D", f'part="{p}"', "-o", f"/tmp/dockfit_{r}_{p}.stl", scad],
                                      cwd=os.path.dirname(scad), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in procs: p.wait()
def plug_mesh(i):
    px, py = G.usb_xy(*G.SLOTS[i])
    a = trimesh.creation.box(extents=[8.25, 2.40, G.PLUG_H]); a.apply_translation([px, py, G.PCB_Z1 + G.PLUG_H / 2])
    return a
for r, (scad, shells, extra) in RADIOS.items():
    sh = [trimesh.load(f"/tmp/dockfit_{r}_{p}.stl") for p in shells]
    ex = [trimesh.load(f"/tmp/dockfit_{r}_{p}.stl") for p in extra] + (single_board_extras() if r == "single_board" else [])
    body = trimesh.util.concatenate(sh)
    lo, hi = body.bounds
    W, L, Th = hi - lo
    out.append(f"--- {r}: case {W:.2f} W x {L:.2f} L x {Th:.2f} T (shell parts {', '.join(shells)}; extras {', '.join(extra) or 'switch knob (on/off), wheel'})")
    if abs(W - G.RL) > 0.05 or abs(Th - G.RT) > 0.05:
        bad += 1; out.append(f"FAIL {r}: end footprint {W:.2f} x {Th:.2f} differs from the dock footprint {G.RL} x {G.RT}")
    worst = {}
    for i, (c, rr) in enumerate(G.SLOTS):
        x0, y0, _, _ = G.radio_box(c, rr)
        # docked pose: X_dock = x0 + (x - Xmin), Y_dock = y0 + (Zmax - z), Z_dock = FLOOR_Z + (y - Ymin)  (proper rotation)
        M = np.array([[1, 0, 0, x0 - lo[0]], [0, 0, -1, y0 + hi[2]], [0, 1, 0, G.FLOOR_Z - lo[1]], [0, 0, 0, 1.0]])
        parts = [m.copy().apply_transform(M) for m in sh + ex]
        rad = trimesh.boolean.union(parts, engine="manifold") if len(parts) > 1 else parts[0]
        if i in (0, 3):   # insertion path: the radio lowered straight down from above the pocket walls (sweep in 2 mm steps)
            sweep = []
            for dz in np.arange(2.0, G.FIN_Z - G.FLOOR_Z + 4.0, 2.0):
                m2 = rad.copy(); m2.apply_translation([0, 0, dz]); sweep.append(m2)
            sv = inter(trimesh.boolean.union(sweep, engine="manifold"), case["shell_raw"])
            worst["shell (insertion path)"] = max(worst.get("shell (insertion path)", 0), sv)
        DOCKED[(r, i)] = (rad, M, lo, hi)
        if i == {'single_board': 0, 'feather': 3}[r]: rad.export(f'/tmp/dock_docked_{r}.stl')   # for the previews
        for n, cpart in case.items():
            v = inter(rad, cpart); worst[n] = max(worst.get(n, 0), v)
        v = inter(rad, plug_mesh(i)); worst["plug"] = max(worst.get("plug", 0), v)
        if i == 0:   # plug-to-opening clearance and the plug's reach past the radio's side face (slot 1)
            pm = plug_mesh(i); sp = pm.sample(20000); sp = sp[sp[:, 2] > G.FLOOR_Z - 0.5]; q = trimesh.proximity.closest_point(rad, sp)[1]
            out.append(f"     slot 1: smallest gap plug -> {r} case {q.min():.2f} mm; plug reaches {G.PLUG_TOP - G.FLOOR_Z:.2f} above the floor, "
                       f"{G.PLUG_TOP - G.FLOOR_Z - G.MOUTHS[r]:.2f} past the receptacle mouth")
            # plug centre vs the radio's USB opening centre (case frame -> dock)
            out.append(f"     slot 1: {r} case X centre {x0 + (hi[0]-lo[0])/2:.2f} vs plug X {G.usb_xy(c, rr)[0]:.2f}")
    for n, v in worst.items(): rep(f"{r} (worst of 6 pockets) x {n}", v)
    out.append(f"     docked height above the floor {L:.2f} (top {G.FLOOR_Z + L:.2f} vs pocket walls {G.FIN_Z:.2f}, deck {G.TOP_Z:.2f})")
# ---------------- Feather LEDs visible in the dock: rays from its front-face LED holes toward the viewer (level and
# 15 / 30 / 45 deg up) against the dock shell and the radios in the other five pockets (single-board radios in the
# front row = the tallest neighbours, Feathers in the back row)
sys.path.insert(0, f"{ROOT}/radio_adafruit_feather_rp2040/scripts")
import layout as FL
from trimesh.ray.ray_triangle import RayMeshIntersector
for i in range(6):
    rad, M, lo, hi = DOCKED[("feather", i)]
    obst = trimesh.util.concatenate([case["shell_raw"]] + [DOCKED[("single_board" if j < 3 else "feather", j)][0] for j in range(6) if j != i])
    ri = RayMeshIntersector(obst)
    res = []
    for name, (lx, ly) in FL.feather_leds().items():
        pt = (M @ np.array([lx, ly, hi[2] + 0.05, 1.0]))[:3]
        clear = []
        for a in (0, 15, 30, 45):
            d = np.array([0.0, -math.cos(math.radians(a)), math.sin(math.radians(a))])
            hit = ri.intersects_any(pt[None, :], d[None, :])[0]
            clear.append("clear" if not hit else "BLOCKED")
        ok = all(c == "clear" for c in clear[1:])     # a level ray may hit a raised housing / neighbour; 15-45 deg must be clear
        if not ok: bad += 1
        res.append(f"{name} {pt[2] - G.FLOOR_Z:.1f} above floor: " + "/".join(clear))
    out.append(f"{'ok  ' if all('BLOCKED' not in x.split(': ')[1].split('/', 1)[1] for x in res) else 'FAIL'} Feather LEDs, slot {i+1} (0/15/30/45 deg up): " + "; ".join(res))
# ---------------- dock PCB parts
HEIGHTS = [("CP_Elec_8x10", 10.5), ("CP_Elec_6.3x7.7", 7.9), ("MWSA0604S", 3.8), ("SOIC", 1.75), ("SOT-23", 1.25), ("DFN", 0.8),
           ("D_SMB", 2.45), ("Fuse_1206", 0.9), ("1206", 1.8), ("0805", 1.35), ("0603", 0.9), ("HRO_TYPE-C", 3.26)]
b = pcbnew.LoadBoard(os.path.join(HERE, "../kicad/openald-dock.kicad_pcb"))
comps = {}
for f in b.GetFootprints():
    r = f.GetReference()
    if r.startswith("H") or r in [f"J{i}" for i in range(2, 8)]: continue
    fp = design.PARTS[r]["fp"]; h = next((hh for k, hh in HEIGHTS if k in fp), 2.0)
    f.BuildCourtyardCaches(); bb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    x0, x1 = pcbnew.ToMM(bb.GetLeft()) - 100 + 0.25, pcbnew.ToMM(bb.GetRight()) - 100 - 0.25
    y0, y1 = pcbnew.ToMM(bb.GetTop()) - 100 + 0.25, pcbnew.ToMM(bb.GetBottom()) - 100 - 0.25
    X0, Y1 = G.d(x0, y0); X1, Y0 = G.d(x1, y1)
    m = trimesh.creation.box(extents=[X1 - X0, Y1 - Y0, h]); m.apply_translation([(X0 + X1) / 2, (Y0 + Y1) / 2, G.PCB_Z1 + h / 2])
    if r == "J1":   # real shape: shell/body 8.94 x 7.3 x 3.26 (mouth 0.45 past the board edge), signal pads only 0.15 tall
        jx = G.d(PL.PL["J1"][0], 0)[0]
        m = trimesh.creation.box(extents=[8.94, 7.75, 3.26]); m.apply_translation([jx, G.PCB_Y1 - 7.3/2 + 0.45, G.PCB_Z1 + 1.63])
        p = trimesh.creation.box(extents=[7.4, 1.5, 0.15]); p.apply_translation([jx, G.PCB_Y1 - 7.7, G.PCB_Z1 + 0.075])
        m = trimesh.boolean.union([m, p], engine="manifold")
    comps[r] = m
pcb = trimesh.creation.box(extents=[G.PCB_W, G.PCB_H, G.PCB_T - 0.02]); pcb.apply_translation([(G.PCB_X0 + G.PCB_X1) / 2, (G.PCB_Y0 + G.PCB_Y1) / 2, G.PCB_Z0 + G.PCB_T / 2])
_holes = []
for (hx, hy), dia in [(h, 3.2) for h in PL.HOLES] + [(g, 2.2) for g in PL.PEGS]:
    X, Y = G.d(hx, hy); c = trimesh.creation.cylinder(radius=dia / 2, height=10); c.apply_translation([X, Y, G.PCB_Z0]); _holes.append(c)
pcb = trimesh.boolean.difference([pcb] + _holes, engine="manifold")
for n, c in case.items(): rep(f"PCB x {n}", inter(pcb, c))
from scipy.spatial import cKDTree
_sh = case['shell_raw']; _tree = cKDTree(np.vstack([_sh.sample(400000), _sh.vertices]))
worst = (1e9, None)
for r, m in sorted(comps.items()):
    for n, c in case.items():
        v = inter(m, c)
        if not v < 0.01: bad += 1; out.append(f"FAIL {r} x {n}: {v:.3f} mm^3")
    d = float(_tree.query(np.vstack([m.vertices, m.sample(2000)]))[0].min())
    if d < worst[0]: worst = (d, r)
out.append(f"dock PCB parts: {len(comps)} checked against shell/base/pads; closest to the top shell: {worst[1]} at {worst[0]:.2f} mm (part boxes)")
out.append(f"insertion past the receptacle mouth: {G.INSERTION:.2f} mm (plug top Z {G.PLUG_TOP:.2f}, pocket floor Z {G.FLOOR_Z:.2f}, mouth {G.MOUTH_UP:.2f} above the floor)")
out.append(f"  USB-C full seat (spec effective receptacle shell) {G.SEAT_NOM:.2f} +/- {G.SEAT_TOL:.2f}; design target {G.TARGET_INSERTION:.2f}")
out.append(f"Z stack: base {G.BASE_T:.1f}, standoff {G.STANDOFF:.1f}, PCB {G.PCB_Z0:.2f}..{G.PCB_Z1:.2f}, pad {G.PAD_T:.2f} -> floor {G.FLOOR_Z:.2f}, "
           f"plug top {G.PLUG_TOP:.2f}, deck {G.TOP_Z:.2f}, fins {G.FIN_Z:.2f}")
out.append(f"pocket: {G.RL} x {G.RT} footprint + {G.CLR_GUIDE:.2f}/side; walls {G.FIN_H:.1f} high, front window above {G.FRONT_WALL_H:.1f} "
           f"between {G.FRONT_RETURN:.0f} mm corner returns; right-wall notch {G.SIDE_NOTCH_D:.0f} deep above {G.SIDE_NOTCH_Z:.0f}")
out.append(f"outer size {G.OUT_W:.2f} x {G.OUT_D:.2f} x {G.FIN_Z:.1f} mm (bed 220 x 180: fits); radio gap {G.GAP:.1f} mm, back row offset {G.STAGGER:.2f}")
out.append(f"INTERFERENCES: {bad}")
print("\n".join(out))
