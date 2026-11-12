#!/usr/bin/env python3
"""Dock-interface check: compare the outer envelope of this case with the OpenALD single-board case over the
bottom 52 mm (DOCK_INTERFACE.md: 50.8 mm pocket + 1.2 mm margin), section by section, and the USB-C end wall
(including its openings) exactly.  usage: check_dock.py my_top my_bot ref_top ref_bot"""
import sys,numpy as np,trimesh
from shapely.geometry import Polygon,MultiPolygon
from shapely.ops import unary_union
def load(a,b): return [trimesh.load(a),trimesh.load(b)]
mine=load(sys.argv[1],sys.argv[2]); ref=load(sys.argv[3],sys.argv[4])
def section(ms,y):
    """filled XZ cross-section (x, z) of the union of the case halves at plane Y=y"""
    out=[]
    for m in ms:
        s=m.section(plane_origin=[0,y,0],plane_normal=[0,1,0])
        if s is None: continue
        body=Polygon()
        for e in s.discrete:
            if len(e)>=3: body=body.symmetric_difference(Polygon(e[:,[0,2]]).buffer(0))
        out.append(body)
    return unary_union(out).buffer(0.001).buffer(-0.001) if out else Polygon()
def outer(p):
    # the outer shell is convex over the dock zone (hull of the end toroids + constant section), so its envelope is
    # the convex hull of the section; recesses (USB pocket, screw counterbores) are compared separately below
    return p.convex_hull
Y_BOT=-2.5; Y_MARGIN=Y_BOT+52.0
print(f"{'y':>6} {'mm above bottom':>15}  {'width':>6} {'depth':>6}  {'ref w':>6} {'ref d':>6}  outer-envelope XOR area (mm^2)")
worst=0
for y in [-2.45,-2.0,-1.0,-0.6,0.0,0.5,1.0,2.0,3.0,5.0,10,20,30,40,45,48.3,49.0,49.5]:
    a=outer(section(mine,y)); b=outer(section(ref,y))
    x=a.symmetric_difference(b).area; worst=max(worst,x)
    ab=a.bounds; bb=b.bounds
    print(f"{y:6.2f} {y-Y_BOT:15.2f}  {ab[2]-ab[0]:6.2f} {ab[3]-ab[1]:6.2f}  {bb[2]-bb[0]:6.2f} {bb[3]-bb[1]:6.2f}  {x:.4f}")
print(f"worst outer-envelope difference in the bottom 52 mm: {worst:.4f} mm^2")
# end wall with the USB-C openings: full section (solid minus openings) must match
for y in [-2.3,-1.5,-1.2,-0.9,-0.6]:
    a=section(mine,y); b=section(ref,y)
    # compare only the end-wall region (within 6 mm of the USB centre) so interior features don't count
    from shapely.geometry import box
    w=box(19-8,3.23-5,19+8,3.23+5)
    x=a.intersection(w).symmetric_difference(b.intersection(w)).area
    holes=[list(np.round(Polygon(i).bounds,2)) for g in (a.geoms if isinstance(a,MultiPolygon) else [a]) for i in g.interiors if Polygon(i).intersects(w)]
    print(f"USB end wall y={y:5.2f}: XOR area near the USB opening = {x:.4f} mm^2; openings (x0,z0,x1,z1) {holes}")
# whole-length envelope of this case
lo,hi=trimesh.util.concatenate(mine).bounds; print("this case overall: x %.2f..%.2f (%.2f) y %.2f..%.2f (%.2f) z %.2f..%.2f (%.2f)"%(lo[0],hi[0],hi[0]-lo[0],lo[1],hi[1],hi[1]-lo[1],lo[2],hi[2],hi[2]-lo[2]))
lo,hi=trimesh.util.concatenate(ref).bounds; print("single-board case: x %.2f..%.2f (%.2f) y %.2f..%.2f (%.2f) z %.2f..%.2f (%.2f)"%(lo[0],hi[0],hi[0]-lo[0],lo[1],hi[1],hi[1]-lo[1],lo[2],hi[2],hi[2]-lo[2]))
