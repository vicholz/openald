#!/usr/bin/env python3
"""OpenALD Dock v1.0 fit check (trimesh + manifold booleans), dock frame.
Inputs: STLs of shell_raw, base_raw, pads_raw, radios (bottom 52 mm envelope of a docked radio, USB-C cavity open) and
plugs from case/openald_dock.scad, plus every PCB part as a box (courtyard shrunk 0.25 mm, height from HEIGHTS)."""
import sys, os, math, trimesh, numpy as np, pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as G, design
T = "/tmp/dock_%s.stl"
case = {n: trimesh.load(T % n) for n in ("shell_raw", "base_raw", "pads_raw")}
radios = trimesh.load(T % "radios"); plugs = trimesh.load(T % "plugs")
def inter(a, b):
    try: return trimesh.boolean.intersection([a, b], engine="manifold").volume
    except Exception as e: return float("nan")
HEIGHTS = [("CP_Elec_8x10", 10.5), ("CP_Elec_6.3x7.7", 7.9), ("MWSA0604S", 3.8), ("SOIC", 1.75), ("SOT-23", 1.25), ("DFN", 0.8),
           ("D_SMB", 2.45), ("Fuse_1206", 0.9), ("1206", 1.8), ("0805", 1.35), ("0603", 0.9), ("HRO_TYPE-C", 3.26)]
b = pcbnew.LoadBoard(os.path.join(os.path.dirname(__file__), "../kicad/openald-dock.kicad_pcb"))
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
        jx = G.d(93.0, 0)[0]
        m = trimesh.creation.box(extents=[8.94, 7.75, 3.26]); m.apply_translation([jx, G.PCB_Y1 - 7.3/2 + 0.45, G.PCB_Z1 + 1.63])
        p = trimesh.creation.box(extents=[7.4, 1.5, 0.15]); p.apply_translation([jx, G.PCB_Y1 - 7.7, G.PCB_Z1 + 0.075])
        m = trimesh.boolean.union([m, p], engine="manifold")
    comps[r] = m
pcb = trimesh.creation.box(extents=[G.PCB_W, G.PCB_H, G.PCB_T - 0.02]); pcb.apply_translation([(G.PCB_X0 + G.PCB_X1) / 2, (G.PCB_Y0 + G.PCB_Y1) / 2, G.PCB_Z0 + G.PCB_T / 2])
import placement as PL
_holes = []
for (hx, hy), dia in [(h, 3.2) for h in PL.HOLES] + [(g, 2.2) for g in PL.PEGS]:
    X, Y = G.d(hx, hy); c = trimesh.creation.cylinder(radius=dia / 2, height=10); c.apply_translation([X, Y, G.PCB_Z0]); _holes.append(c)
pcb = trimesh.boolean.difference([pcb] + _holes, engine="manifold")     # PCB with its screw and peg holes
bad = 0; out = []
def rep(name, v):
    global bad
    flag = not (v < 0.01); bad += flag
    out.append(f"{'FAIL' if flag else 'ok  '} {name:42s} {v:9.3f} mm^3")
for n, c in case.items():
    rep(f"radios x {n}", inter(radios, c)); rep(f"plugs x {n}", inter(plugs, c)); rep(f"PCB x {n}", inter(pcb, c))
rep("plugs x radios (plug inside USB-C cavity)", inter(plugs, radios))
rep("shell x pads", inter(case["shell_raw"], case["pads_raw"])); rep("shell x base", inter(case["shell_raw"], case["base_raw"]))
rep("pads x base", inter(case["pads_raw"], case["base_raw"]))

from scipy.spatial import cKDTree
_sh = case['shell_raw']; _tree = cKDTree(np.vstack([_sh.sample(400000), _sh.vertices]))
worst = (1e9, None)
for r, m in sorted(comps.items()):
    for n, c in case.items():
        v = inter(m, c)
        if not v < 0.01: bad += 1; out.append(f"FAIL {r} x {n}: {v:.3f} mm^3")
    d = float(_tree.query(np.vstack([m.vertices, m.sample(2000)]))[0].min())
    if d < worst[0]: worst = (d, r)
out.append(f"closest PCB part to the top shell: {worst[1]} at {worst[0]:.2f} mm (part boxes)")
out.append(f"insertion past the receptacle mouth: {G.INSERTION:.2f} mm (plug top Z {G.PLUG_TOP:.2f}, radio floor Z {G.FLOOR_Z:.2f})")
for r, m in G.MOUTHS.items():
    out.append(f"  {r:12s} receptacle mouth {m:.2f} inside the bottom face -> insertion {G.insertion(r):.2f} mm")
out.append(f"  USB-C full seat (spec effective receptacle shell) {G.SEAT_NOM:.2f} +/- {G.SEAT_TOL:.2f}; design target {G.TARGET_INSERTION:.2f}")
out.append(f"Z stack: base {G.BASE_T:.1f}, standoff {G.STANDOFF:.1f}, PCB {G.PCB_Z0:.2f}..{G.PCB_Z1:.2f}, pad {G.PAD_T:.2f} -> floor {G.FLOOR_Z:.2f}, plug top {G.PLUG_TOP:.2f}, deck {G.TOP_Z:.2f}")
out.append(f"radio-to-guide clearance {G.CLR_GUIDE:.2f}/side for {G.GUIDE_H:.0f} mm, {G.CLR_UPPER:.2f}/side above; pocket depth {G.POCKET_DEPTH:.1f}")
out.append(f"outer size {G.OUT_W:.1f} x {G.OUT_D:.2f} x {G.TOP_Z:.1f} mm; radio gap {G.GAP:.1f} mm")
out.append(f"INTERFERENCES: {bad}")
print("\n".join(out))
