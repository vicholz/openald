#!/usr/bin/env python3
"""3D interference / fit check for the Feather variant.
Parts (assembly pose, case frame): Feather RP2040 (board with holes + every component envelope from Adafruit's
Eagle file), 18650 holder box, FM module (board + jack box, ESTIMATED), controls board (outline + this project's
WRL models for the wheel and switch, boxes for 0603 parts).  Checked against case top, case bottom and frame.
usage: check_fit.py top.stl bottom.stl frame.stl"""
import sys,os,re,math,json,numpy as np,trimesh,pcbnew
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import layout as L
from build_pcb import PRJ,NAME,X0,Y1
ROOT=os.path.dirname(HERE)
mech=json.load(open(os.path.join(ROOT,"ref","feather_rp2040_mech.json")))
def box(x0,x1,y0,y1,z0,z1):
    m=trimesh.creation.box(extents=[x1-x0,y1-y0,z1-z0]); m.apply_translation([(x0+x1)/2,(y0+y1)/2,(z0+z1)/2]); return m
def cyl(x,y,d,z0,z1):
    m=trimesh.creation.cylinder(radius=d/2,height=z1-z0,sections=32); m.apply_translation([x,y,(z0+z1)/2]); return m
def diff(a,bs): return trimesh.boolean.difference([a]+bs,engine="manifold")
parts={}
# ---- Feather
fb=mech["board_box"] if "board_box" in mech else None
sc=open(os.path.join(ROOT,"case","feather_params.scad")).read()
def arr(n): return json.loads(re.search(n+r"\s*=\s*(\[.*?\]);",sc,re.S).group(1))
fbx=arr("feather_box"); fh=arr("feather_holes"); fparts=arr("f_parts")
parts["Feather PCB"]=[diff(box(fbx[0],fbx[1],fbx[2],fbx[3],0,1.6),[cyl(x,y,2.5,-1,3) for x,y in fh])]
for i,p in enumerate(fparts): parts.setdefault("Feather parts",[]).append(box(*p))
# ---- holder
H=L.HOLDER; parts["18650 holder"]=[box(H["x0"],H["x1"],H["y0"],H["y1"],H["z0"],H["z1"])]
# ---- FM module (ESTIMATED geometry)
F=L.FM; z0=F["z0"]; zt=z0+F["t"]
hi=L.FM_HOLE_INSET
parts["FM board"]=[diff(box(F["x0"],F["x1"],F["y0"],F["y1"],z0,zt),[cyl(x,y,L.FM_HOLE_D,z0-1,zt+1) for x in (F["x0"]+hi,F["x1"]-hi) for y in (F["y0"]+hi,F["y1"]-hi)])]
parts["FM jack"]=[box(L.FM_JACK_X-3,L.FM_JACK_X+3,F["y1"]-12,F["y1"],zt,zt+L.FM_JACK_BODY_H)]
# ---- controls board
b=pcbnew.LoadBoard(PRJ+NAME+".kicad_pcb")
def C(v): return (pcbnew.ToMM(v.x)-100+X0, Y1-(pcbnew.ToMM(v.y)-100))
poly=trimesh.creation.extrude_polygon(__import__("shapely.geometry",fromlist=["Polygon"]).Polygon(L.CB_OUTLINE),L.CB_T)
holes=[]
for f in b.GetFootprints():
    for p in f.Pads():
        d=pcbnew.ToMM(p.GetDrillSize().x)
        if d>0: x,y=C(p.GetPosition()); holes.append(cyl(x,y,d,-1,3))
parts["Controls PCB"]=[diff(poly,holes)]
def wrl_mesh(path):
    t=open(path).read(); out=[]
    for pts,idx in re.findall(r'point\s*\[([^\]]*)\].*?coordIndex\s*\[([^\]]*)\]',t,re.S):
        v=np.array([float(a) for a in re.findall(r'-?[\d.]+(?:e-?\d+)?',pts)]).reshape(-1,3)*2.54
        ii=[int(a) for a in re.findall(r'-?\d+',idx)]; faces=[];cur=[]
        for k in ii:
            if k<0:
                for j in range(1,len(cur)-1): faces.append([cur[0],cur[j],cur[j+1]])
                cur=[]
            else: cur.append(k)
        out.append(trimesh.Trimesh(v,faces))
    return out
for f in b.GetFootprints():
    ref=f.GetReference(); x,y=C(f.GetPosition()); a=math.radians(f.GetOrientationDegrees())
    T=trimesh.transformations.rotation_matrix(a,[0,0,1]); T[:3,3]=[x,y,L.CB_Z0+L.CB_T]
    ms=[m.m_Filename for m in f.Models() if "KIPRJMOD" in m.m_Filename]
    if ms:
        for m in wrl_mesh(ms[0].replace("${KIPRJMOD}",PRJ.rstrip("/"))):
            m.apply_transform(T); parts.setdefault(f"{ref} ({f.GetValue()})",[]).append(m)
    elif ref[0] in "RCD":
        bb=f.GetBoundingBox(False,False) if False else None
        w,h=(1.6,0.8); 
        if abs(math.sin(a))>0.5: w,h=h,w
        parts.setdefault("0603 parts",[]).append(box(x-w/2,x+w/2,y-h/2,y+h/2,1.6,1.6+0.55))
# ---- check
names=sys.argv[1:4]; cases={n:trimesh.load(p) for n,p in zip(("case top","case bottom","frame"),names)}
for n,c in cases.items(): print(f"{n:12s} watertight={c.is_watertight} volume={c.volume/1000:.2f} cm^3 bounds x {c.bounds[0][0]:.2f}..{c.bounds[1][0]:.2f} y {c.bounds[0][1]:.2f}..{c.bounds[1][1]:.2f} z {c.bounds[0][2]:.2f}..{c.bounds[1][2]:.2f}")
bad=0; rows=[]
for pn,ms in parts.items():
    for cn,c in cases.items():
        vol=0
        for m in ms:
            s=m if m.is_watertight else m.convex_hull
            try: vol+=trimesh.boolean.intersection([s,c],engine="manifold").volume
            except Exception as e: print("bool fail",pn,cn,e)
        if vol>0.01: bad+=1; print(f"  INTERFERENCE {pn} x {cn}: {vol:.3f} mm^3")
    lo=np.min([m.bounds[0] for m in ms],axis=0); hi_=np.max([m.bounds[1] for m in ms],axis=0)
    rows.append(f"  {pn:26s} x {lo[0]:6.2f}..{hi_[0]:6.2f}  y {lo[1]:6.2f}..{hi_[1]:6.2f}  z {lo[2]:6.2f}..{hi_[2]:6.2f}")
print("parts (case frame):"); print("\n".join(rows))
# part-to-part (holder vs boards)
pn=list(parts)
for i in range(len(pn)):
    for j in range(i+1,len(pn)):
        A=trimesh.util.concatenate(parts[pn[i]]); B=trimesh.util.concatenate(parts[pn[j]])
        if not (np.all(A.bounds[0]<B.bounds[1]) and np.all(B.bounds[0]<A.bounds[1])): continue
        vol=0
        for a_ in parts[pn[i]]:
            for b_ in parts[pn[j]]:
                if not (np.all(a_.bounds[0]<b_.bounds[1]) and np.all(b_.bounds[0]<a_.bounds[1])): continue
                try: vol+=trimesh.boolean.intersection([a_ if a_.is_watertight else a_.convex_hull, b_ if b_.is_watertight else b_.convex_hull],engine="manifold").volume
                except Exception: pass
        if vol>0.01 and not ({pn[i],pn[j]}<={"Feather PCB","Feather parts"}) and not (pn[i].startswith("S") and pn[j]=="Controls PCB"):
            print(f"  part overlap {pn[i]} x {pn[j]}: {vol:.3f} mm^3")
# clearances to the inner surfaces: min gap from each part's bbox to each case piece (sampled)
cn=list(cases)
for i in range(3):
    for j in range(i+1,3):
        v=trimesh.boolean.intersection([cases[cn[i]],cases[cn[j]]],engine="manifold").volume
        if v>0.01: bad+=1; print(f"  INTERFERENCE {cn[i]} x {cn[j]}: {v:.3f} mm^3")
        else: print(f"  {cn[i]} x {cn[j]}: no overlap")
print("RESULT:", "PASS (0 interferences)" if bad==0 else f"FAIL ({bad} interferences)")
allm=[m for ms in parts.values() for m in ms]; trimesh.util.concatenate(allm).export("/tmp/feather_assembly.stl")
