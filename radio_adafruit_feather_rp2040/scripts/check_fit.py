#!/usr/bin/env python3
"""Fit check for the Feather case (2026-11-24 unified envelope).
Exports every ghost part (holder, Feather board + parts, FM module + jack + header, charge-port breakout, thumbwheel,
power switch in both knob positions, 3 mm LEDs) from the SCAD and reports overlap volumes against the three printed
parts and against each other, plus the front-shell assembly path (lowered straight onto the back shell with
everything in place) and the shared dock interface numbers.
Usage: check_fit.py top_raw.stl bottom_raw.stl deck_raw.stl"""
import sys,os,subprocess,itertools,trimesh,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import layout as L
CASE=os.path.join(os.path.dirname(HERE),"case"); S=os.path.join(CASE,"openald_feather_case.scad")
G=["holder","feather","fm","breakout","wheel","switch_on","switch_off","leds"]
SW=["brk_usb","brk_pcb"]   # sweep-only pieces
procs=[subprocess.Popen(["openscad","-D",f'part="g_{g}"',"-o",f"/tmp/fg_{g}.stl",S],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) for g in G+SW]
for p in procs: p.wait()
ghost={g:trimesh.load(f"/tmp/fg_{g}.stl") for g in G}
sweep={g:trimesh.load(f"/tmp/fg_{g}.stl") for g in SW}
prt={n:trimesh.load(f) for n,f in zip(("front","back","deck"),sys.argv[1:4])}
bad=0
def vol(a,b):
    try: return trimesh.boolean.intersection([a,b],engine="manifold").volume
    except Exception as e: return -1
print("== printed parts: watertight / volume")
for n,m in prt.items(): print(f"  {n:6s} watertight={m.is_watertight} bodies={len(m.split(only_watertight=False))} volume={m.volume:.0f} mm3 bounds={np.round(m.bounds,2).tolist()}")
print("== ghost vs printed parts (mm3, > 0.01 = interference)")
for g,m in ghost.items():
    for n,c in prt.items():
        v=vol(m,c)
        if v>0.01 or v<0: bad+=1; print(f"  {g:10s} x {n:5s}: {v:.3f}  <-- INTERFERENCE")
    print(f"  {g:10s} clear of all printed parts" if all(vol(m,c)<=0.01 for c in prt.values()) else "")
print("== ghost vs ghost")
for a,b in itertools.combinations(G,2):
    if {a,b}=={"switch_on","switch_off"}: continue
    v=vol(ghost[a],ghost[b])
    if v>0.01: bad+=1; print(f"  {a} x {b}: {v:.3f}  <-- INTERFERENCE")
print("  (all pairs checked)")
print("== printed parts vs each other")
for a,b in itertools.combinations(prt,2):
    v=vol(prt[a],prt[b]); print(f"  {a} x {b}: {v:.3f}"); bad+= v>0.01
# assembly path: the front shell is lowered (-Z) onto the back shell with the deck, FM, breakout, wheel in place.
# Anything reaching past an inner wall face above the split, swept up to the top, must not meet the front shell.
print("== assembly path (front shell lowered straight down)")
fr=prt["front"]
for g in ("brk_usb","brk_pcb","wheel","fm"):
    v=0; O=[]
    for m in (sweep.get(g) or ghost[g]).split(only_watertight=False):      # sweep each solid on its own (a hull over several would bridge walls)
        pts=np.vstack([m.vertices,m.sample(20000)])
        o=pts[((pts[:,0]<L.IN_X0)|(pts[:,0]>L.IN_X1)|(pts[:,1]<0)|(pts[:,1]>L.IN_L))&(pts[:,2]>L.Z_SPLIT)]
        if len(o)<4: continue
        d=o.copy(); d[:,2]=L.Z_SPLIT-0.5; O.append(o)
        v+=vol(trimesh.convex.convex_hull(np.vstack([o,d])),fr)
    if not O: print(f"  {g}: stays inside the inner walls"); continue
    o=np.vstack(O); lo,hi=o.min(0),o.max(0)
    msg=f"  {g}: reaches past the inner wall (x {lo[0]:.2f}..{hi[0]:.2f} y {lo[1]:.2f}..{hi[1]:.2f} z {lo[2]:.2f}..{hi[2]:.2f}); swept volume x front shell {v:.3f}"
    print(msg+("  <-- BLOCKED" if v>0.01 else ": OK")); bad+= v>0.01
print("== dock interface (must match the MI03 / single-board cases)")
b=prt["front"].bounds; bb=prt["back"].bounds
lo=np.minimum(b[0],bb[0]); hi=np.maximum(b[1],bb[1])
print(f"  outer W {hi[0]-lo[0]:.2f}  L {hi[1]-lo[1]:.2f}  T {hi[2]-lo[2]:.2f}")
print(f"  USB-C centre {hi[1]-L.DOCK_USB_Y:.2f} from the top outer end, {hi[2]-L.DOCK_USB_Z:.2f} below the front face, mouth {L.DOCK_USB_MOUTH_X-lo[0]:.2f} inside the side face")
ok=abs(hi[1]-lo[1]-89.75)<0.05 and abs(hi[2]-lo[2]-34.83)<0.05 and abs(hi[1]-L.DOCK_USB_Y-30.3)<0.05 and abs(hi[2]-L.DOCK_USB_Z-7.55)<0.05
print("  dock interface:", "MATCH" if ok else "MISMATCH"); bad+= not ok
print("INTERFERENCES:",bad)
