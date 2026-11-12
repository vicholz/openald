#!/usr/bin/env python3
"""Fit each JLC-placed part's EasyEDA/LCSC footprint (the one JLC's placement preview and 3D model use) onto the
KiCad footprint's pads on the routed board, and derive the CPL position/rotation JLC needs.

  - EasyEDA footprints are fetched from https://easyeda.com/api/products/<LCSC>/components (cached in
    tools/easyeda/<LCSC>.json).  Source: JLCEDA/EasyEDA official library (https://easyeda.com, https://lceda.cn).
  - JLC places the EasyEDA footprint origin (its 'head' x/y, the pad-bounding-box centre for LCSC footprints)
    at CPL Mid X/Mid Y and rotates it CCW by CPL Rotation (viewed from the top, Y up).
  - For every rotation 0/90/180/270 the EasyEDA pads are matched geometrically to the KiCad pads (centre within
    0.35 mm); ties (pin-symmetric parts) are broken by pin-number/name agreement, then by the 3D-model offset.
Writes fab/jlc_cpl_fit.json (used by make_fab.py) and, with --plots, previews/cpl_overlay_<REF>.png."""
import json, math, os, sys, subprocess, itertools
import numpy as np, pcbnew
sys.path.insert(0, os.path.dirname(__file__))
import design, placement as PLm
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get("EASYEDA_CACHE", os.path.join(ROOT, "..", "tools", "easyeda")); os.makedirs(CACHE, exist_ok=True)
PCB = os.path.join(ROOT, "kicad", "openald.kicad_pcb")
U = 0.254                                # EasyEDA unit = 10 mil
TOL = 0.6                                # pad-centre match tolerance (libraries differ in land length, e.g. ESOP-8)
# pin-symmetric mechanical parts: the 3D-model side (knob) outranks pin numbering (SPDT pins 1/3 are interchangeable)
MODEL_FIRST = {"SW1"}
OX, OY = 100.0, 100.0 + PLm.BOARD_H      # CPL origin = board bottom-left (aux/drill origin), Y up
# KiCad pad name -> EasyEDA pad name, where the libraries name the same physical pin differently
NAME_MAP = {"J1": {"A1": "A1B12", "B12": "A1B12", "A12": "B1A12", "B1": "B1A12", "A4": "A4B9", "B9": "A4B9",
                   "A9": "B4A9", "B4": "B4A9", "S1": ""},
            "J2": {"S": "1", "T": "2", "R1": "3", "R2": "4"},   # EasyEDA PJ-320D-4A numbers its 4 pads 1-4 (geometry decides)
            "SW3": {"MP": ""}}
# 2-terminal polarized parts: compare by function (cathode/anode), because LCSC LED footprints differ in which pad
# is numbered 1 (e.g. KT-0603R C2286: pad 1 = anode; KT-0603G C12624: pad 1 = cathode). KiCad LED/D: pad 1 = K.
POLAR = {"K": "K", "-": "K", "A": "A", "+": "A"}

def easyeda(lcsc):
    p = os.path.join(CACHE, lcsc + ".json")
    if not os.path.exists(p):
        subprocess.run(["curl", "-s", "-A", "curl/8.0", "--compressed", "-o", p,
                        f"https://easyeda.com/api/products/{lcsc}/components?version=6.4.19.5"], check=True)
    r = json.load(open(p))["result"]; pd = r["packageDetail"]["dataStr"]; title = r["packageDetail"]["title"]
    hx, hy = float(pd["head"]["x"]), float(pd["head"]["y"])
    pads = []; model = None; silk = []
    names = {}
    for sh in r["dataStr"]["shape"]:
        if sh.startswith("P~"):
            q = sh.split("^^"); names[q[0].split("~")[3]] = q[3].split("~")[4]
    for s in pd["shape"]:
        f = s.split("~")
        if f[0] == "PAD":
            x, y, w, h, rot = float(f[2]), float(f[3]), float(f[4]), float(f[5]), float(f[11] or 0)
            if rot % 180 == 90: w, h = h, w
            pads.append(dict(n=f[8], fn=names.get(f[8], ""), x=(x-hx)*U, y=-(y-hy)*U, w=w*U, h=h*U, tht=f[6] == "11"))
        elif f[0] == "HOLE":
            pads.append(dict(n="", fn="", x=(float(f[1])-hx)*U, y=-(float(f[2])-hy)*U, w=2*float(f[3])*U, h=2*float(f[3])*U, tht=True))
        elif f[0] == "SVGNODE":
            a = json.loads(s.split("~", 1)[1])["attrs"]
            if a.get("c_etype") == "outline3D":
                ox_, oy_ = map(float, a["c_origin"].split(",")); model = ((ox_-hx)*U, -(oy_-hy)*U)
        elif f[0] == "TRACK" and f[2] == "3":
            v = list(map(float, f[4].split())); silk.append([((v[i]-hx)*U, -(v[i+1]-hy)*U) for i in range(0, len(v), 2)])
    return dict(title=title, pads=pads, model=model, silk=silk, names=names)

def kicad_pads(f):
    out = []
    for p in f.Pads():
        x = pcbnew.ToMM(p.GetPosition().x) - OX; y = OY - pcbnew.ToMM(p.GetPosition().y)
        bb = p.GetBoundingBox()
        out.append(dict(n=p.GetNumber(), x=x, y=y, w=pcbnew.ToMM(bb.GetWidth()), h=pcbnew.ToMM(bb.GetHeight()),
                        tht=p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD))
    return out

def rot(px, py, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a)); return c*px - s*py, s*px + c*py

def fit(ref, f, ez):
    K = kicad_pads(f); KP = np.array([[k["x"], k["y"]] for k in K])
    nm = NAME_MAP.get(ref, {})
    polar = ref.startswith("D")
    org = np.array([pcbnew.ToMM(f.GetPosition().x) - OX, OY - pcbnew.ToMM(f.GetPosition().y)])
    xs = []; ys = []
    for it in f.GraphicalItems():
        if it.GetLayer() == pcbnew.F_CrtYd:
            bb = it.GetBoundingBox(); xs += [bb.GetLeft(), bb.GetRight()]; ys += [bb.GetTop(), bb.GetBottom()]
    ccen = np.array([pcbnew.ToMM((min(xs)+max(xs))/2) - OX, OY - pcbnew.ToMM((min(ys)+max(ys))/2)]) if xs else None
    best = None
    for a in (0, 90, 180, 270):
        E = np.array([rot(e["x"], e["y"], a) for e in ez["pads"]])
        cands = [KP[i] - E[j] for i in range(len(K)) for j in range(len(E)) if K[i]["tht"] == ez["pads"][j]["tht"]]
        for t in cands:
            d = np.linalg.norm((E + t)[:, None, :] - KP[None, :, :], axis=2)
            m = d.min(axis=1) < TOL
            if m.sum() < max(2, 0.6*len(E)): continue
            # translation: from the drilled features (holes / THT pads) when there are >= 2, else from all pads
            J = [j for j in range(len(E)) if m[j] and ez["pads"][j]["tht"]]
            if len(J) < 2: J = [j for j in range(len(E)) if m[j]]
            t2 = t + np.mean([KP[d[j].argmin()] - (E[j]+t) for j in J], axis=0)
            d2 = np.linalg.norm((E + t2)[:, None, :] - KP[None, :, :], axis=2)
            m2 = d2.min(axis=1) < TOL; rms = math.sqrt(np.mean(d2.min(axis=1)[m2]**2))
            agree = 0; total = 0
            for j in range(len(E)):
                en = ez["pads"][j]["n"]
                if not m2[j] or not en: continue
                kn = K[d2[j].argmin()]["n"]; kn2 = nm.get(kn, kn)
                if polar:
                    total += 1; agree += (("K" if kn == "1" else "A") == POLAR.get(ez["pads"][j]["fn"], "?")); continue
                if kn2: total += 1; agree += (kn2 == en)
            # 3D model side: EasyEDA model centre offset vs KiCad courtyard centre offset (knob / mouth side)
            mag = 0
            if ez["model"] and np.hypot(*ez["model"]) > 0.5 and ccen is not None:
                mv = np.array(rot(ez["model"][0], ez["model"][1], a)) + t2 - org
                cv = ccen - org
                if np.hypot(*cv) > 0.5: mag = 1 if np.dot(mv, cv) > 0 else -1
            score = (int(m2.sum()), mag, agree, -round(rms, 3)) if ref in MODEL_FIRST else (int(m2.sum()), agree, mag, -round(rms, 3))
            if best is None or score > best["score"]:
                best = dict(score=score, a=a, t=t2, rms=rms, matched=int(m2.sum()), n=len(E), agree=agree, total=total, model=mag)
    return best

def main(plots):
    b = pcbnew.LoadBoard(PCB)
    res = {}
    for p in design.P:
        if not p.get("lcsc") or p.get("dnp") or p.get("hand"): continue
        f = b.FindFootprintByReference(p["ref"]); ez = easyeda(p["lcsc"])
        r = fit(p["ref"], f, ez)
        kx = pcbnew.ToMM(f.GetPosition().x) - OX; ky = OY - pcbnew.ToMM(f.GetPosition().y); ka = f.GetOrientationDegrees()
        if r is None: print(p["ref"], "NO FIT", ez["title"]); continue
        # pin-symmetric tie-break: both 180-degree solutions match all pads -> pick the one whose 3D model sits on
        # the same side of the origin as the KiCad courtyard centre (knob / jack mouth side)
        out = dict(ref=p["ref"], lcsc=p["lcsc"], easyeda_fp=ez["title"], x=round(float(r["t"][0]), 4), y=round(float(r["t"][1]), 4),
                   rot=r["a"] % 360, rms=round(r["rms"], 3), matched=f'{r["matched"]}/{r["n"]}', pins_agree=f'{r["agree"]}/{r["total"]}', model_side=r['model'],
                   kicad_x=round(kx, 4), kicad_y=round(ky, 4), kicad_rot=ka % 360)
        out["dx"] = round(out["x"] - kx, 3); out["dy"] = round(out["y"] - ky, 3); out["drot"] = (out["rot"] - ka) % 360
        res[p["ref"]] = out; res[p["ref"]]["_ez"] = ez
    return b, res

if __name__ == "__main__" and len(sys.argv) == 1:
    b, res = main(False)
    for r, o in res.items():
        print(f'{r:5s} {o["easyeda_fp"][:38]:38s} kicad ({o["kicad_x"]:7.3f},{o["kicad_y"]:7.3f}) {o["kicad_rot"]:5.0f} -> JLC ({o["x"]:7.3f},{o["y"]:7.3f}) {o["rot"]:4.0f}'
              f'  d=({o["dx"]:+.3f},{o["dy"]:+.3f}) drot={o["drot"]:3.0f}  pads {o["matched"]} rms {o["rms"]:.3f} pins {o["pins_agree"]}')

# ---------------------------------------------------------------- verification / overlay plots
def table_from_make_fab():
    import ast
    src = open(os.path.join(os.path.dirname(__file__), "make_fab.py")).read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "JLC_CORR":
            return ast.literal_eval(node.value)
    return {}

def local_corr(o):
    a = math.radians(o["kicad_rot"])
    return (round(math.cos(a)*o["dx"] + math.sin(a)*o["dy"], 3), round(-math.sin(a)*o["dx"] + math.cos(a)*o["dy"], 3), o["drot"] % 360)

def check(res):
    tab = table_from_make_fab(); bad = 0
    for r, o in res.items():
        fp = design.PARTS[r]["fp"].split(":")[1]; want = local_corr(o); have = tab.get((o["lcsc"], fp), (0, 0, 0))
        if abs(want[0]-have[0]) > 0.02 or abs(want[1]-have[1]) > 0.02 or (want[2]-have[2]) % 360:
            bad += 1; print("MISMATCH", r, o["lcsc"], fp, "fit", want, "table", have)
    print("correction table:", "OK" if not bad else f"{bad} mismatches")
    return bad

def read_cpl(path, yshift=0.0):
    import csv
    return {r["Designator"]: (float(r["Mid X"][:-2]), float(r["Mid Y"][:-2]) + yshift, float(r["Rotation"])) for r in csv.DictReader(open(path))}

def plot(b, o, cpl, before=None, outdir=None):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon
    ref = o["ref"]; f = b.FindFootprintByReference(ref); ez = o["_ez"]
    fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=130)
    for p in f.Pads():      # KiCad copper (real pad outlines)
        poly = p.GetEffectivePolygon(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
        for i in range(poly.OutlineCount()):
            ol = poly.Outline(i); pts = [(pcbnew.ToMM(ol.CPoint(k).x) - OX, OY - pcbnew.ToMM(ol.CPoint(k).y)) for k in range(ol.PointCount())]
            ax.add_patch(Polygon(pts, closed=True, fc="#4caf50", ec="#1b5e20", alpha=0.55, lw=0.8))
        if p.GetDrillSize().x > 0:
            c = p.GetPosition(); ax.add_patch(matplotlib.patches.Ellipse((pcbnew.ToMM(c.x)-OX, OY-pcbnew.ToMM(c.y)),
                pcbnew.ToMM(p.GetDrillSize().x), pcbnew.ToMM(p.GetDrillSize().y), fc="white", ec="#1b5e20", lw=0.6))
        c = p.GetPosition()
        if p.GetNumber(): ax.text(pcbnew.ToMM(c.x)-OX, OY-pcbnew.ToMM(c.y), p.GetNumber(), color="#1b5e20", fontsize=6, ha="center", va="center")
    def draw_ez(x0, y0, a, col, ls, lab, labels=True):
        for e in ez["pads"]:
            w, h = (e["w"], e["h"]) if a % 180 == 0 else (e["h"], e["w"])
            cx, cy = rot(e["x"], e["y"], a); cx += x0; cy += y0
            if e["n"] == "":   # NPTH hole
                ax.add_patch(matplotlib.patches.Circle((cx, cy), e["w"]/2, fc="none", ec=col, ls=ls, lw=1.2))
            else:
                ax.add_patch(Rectangle((cx-w/2, cy-h/2), w, h, fc="none", ec=col, ls=ls, lw=1.2))
                if labels: ax.text(cx, cy - min(w, h)*0.75 if True else cy, e["n"] + (f'({e["fn"]})' if ref.startswith("D") and e["fn"] else ""), color=col, fontsize=5.5, ha="center", va="top")
        for tr in ez["silk"]:
            P = [rot(x, y, a) for x, y in tr]; ax.plot([x0+p[0] for p in P], [y0+p[1] for p in P], color=col, lw=0.7, ls=ls, alpha=0.8)
        if ez["model"]:
            mx, my = rot(*ez["model"], a); ax.plot(x0+mx, y0+my, marker="*", color=col, ms=8)
        ax.plot(x0, y0, marker="x", color=col, ms=9, mew=1.6, label=lab)
    if before and ref in before and before[ref] != cpl[ref]:
        bx, by, ba = before[ref]; draw_ez(bx, by, ba, "#ff9800", ":", f"rev3 CPL ({bx:.2f}, {by:.2f}, {ba:g} deg)", labels=False)
    x, y, a = cpl[ref]; draw_ez(x, y, a, "#d32f2f", "--", f"fixed CPL ({x:.2f}, {y:.2f}, {a:g} deg)")
    kx, ky = pcbnew.ToMM(f.GetPosition().x)-OX, OY-pcbnew.ToMM(f.GetPosition().y)
    ax.plot(kx, ky, marker="+", color="#1565c0", ms=12, mew=1.6, label=f"KiCad origin ({kx:.2f}, {ky:.2f}, {f.GetOrientationDegrees()%360:g} deg)")
    ax.set_aspect("equal"); ax.autoscale_view(); ax.margins(0.12); ax.grid(alpha=0.25)
    ax.set_title(f'{ref} {o["lcsc"]}  {ez["title"]}\ngreen = KiCad pads on the board, red dashed = EasyEDA/JLC footprint at the CPL\n'
                 f'(* = EasyEDA 3D-model origin; source: JLCEDA/EasyEDA official library)', fontsize=7)
    ax.set_xlabel("board X (mm, from bottom-left)"); ax.set_ylabel("board Y (mm, up)"); ax.legend(fontsize=6, loc="best")
    p = os.path.join(outdir, f"cpl_overlay_{ref}.png"); fig.tight_layout(); fig.savefig(p); plt.close(fig); return p

def verify_cpl(b, res, cpl):
    """Independent check of the written CPL: place each EasyEDA footprint at its CPL row, measure pad agreement."""
    worst = 0; out = {}
    for r, o in res.items():
        if r not in cpl: continue
        x, y, a = cpl[r]; K = np.array([[k["x"], k["y"]] for k in kicad_pads(b.FindFootprintByReference(r))])
        E = np.array([np.array(rot(e["x"], e["y"], a)) + (x, y) for e in o["_ez"]["pads"]])
        d = np.linalg.norm(E[:, None, :] - K[None, :, :], axis=2).min(axis=1)
        out[r] = (int((d < TOL).sum()), len(E), round(float(d.max()), 3)); worst = max(worst, d.max())
    return out, worst

if __name__ == "__main__" and len(sys.argv) > 1:
    b, res = main(False)
    if "--check" in sys.argv: sys.exit(1 if check(res) else 0)
    if "--plots" in sys.argv:
        cpl = read_cpl(os.path.join(ROOT, "fab", "openald-CPL-jlcpcb.csv"))
        before = read_cpl(sys.argv[sys.argv.index("--before")+1], 2.0) if "--before" in sys.argv else None   # rev-3 CPL used origin y=185
        v, worst = verify_cpl(b, res, cpl)
        for r, (m, n, dm) in v.items(): print(f"CPL check {r:5s} pads matched {m}/{n}, worst pad-centre offset {dm:.3f} mm")
        print(f"worst pad-centre offset over all parts: {worst:.3f} mm")
        refs = [r for r in sys.argv[sys.argv.index("--plots")+1].split(",")] if len(sys.argv) > sys.argv.index("--plots")+1 and not sys.argv[sys.argv.index("--plots")+1].startswith("--") else list(res)
        for r in refs: print("wrote", plot(b, res[r], cpl, before, os.path.join(ROOT, "previews")))
    json.dump({r: {k: v for k, v in o.items() if k != "_ez"} for r, o in res.items()}, open(os.path.join(ROOT, "fab", "jlc_cpl_fit.json"), "w"), indent=1)
