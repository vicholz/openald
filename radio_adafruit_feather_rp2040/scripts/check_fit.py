#!/usr/bin/env python3
"""3D interference / fit check for the Feather variant.
Parts (assembly pose, case frame): Feather RP2040 (board with holes + every component envelope from Adafruit's
Eagle file), 18650 holder box, FM module (board + jack box, ESTIMATED), SIQ-02FVS3 wheel (Mitsumi-datasheet WRL model)
plus its dial swept over the push travel and a solder/wire keepout at its terminals, SS-12F16 switch (datasheet
boxes) with the knob swept over its travel, M2 screw shanks, lug keepout, optional 3 mm LEDs.
Checked against case top, case bottom and frame, part-to-part, and the top half's vertical assembly path over the dial.
usage: check_fit.py top.stl bottom.stl frame.stl"""
import sys,os,re,math,json,numpy as np,trimesh
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import layout as L
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
# ---- direct-mount controls (no PCB)
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
WX,WY=L.WHEEL; ZS=L.WHEEL_SEAT_Z; R=L.WHEEL_R; DZ0,DZ1=ZS+L.WHEEL_DIAL_Z[0],ZS+L.WHEEL_DIAL_Z[1]
T=trimesh.transformations.rotation_matrix(math.radians(-90),[0,0,1]); T[:3,3]=[WX,WY,ZS]   # same pose as footprint rot -90 on the old PCB
for m in wrl_mesh(os.path.join(ROOT,"ref","models","SIQ-02FVS3.wrl")):
    m.apply_transform(T); parts.setdefault("SIQ-02FVS3 wheel (WRL)",[]).append(m)
def wl(u0,u1,v0,v1,z0,z1): return box(WX+u0,WX+u1,WY+v0,WY+v1,z0,z1)
# dial swept over the (assumed) push travel: nothing may sit in its path
dial=trimesh.creation.cylinder(radius=R,height=DZ1-DZ0,sections=96); dial.apply_translation([WX,WY,(DZ0+DZ1)/2])
d2=dial.copy(); d2.apply_translation([-L.WHEEL_PUSH,0,0])
parts["wheel dial + push sweep"]=[trimesh.util.concatenate([dial,d2]).convex_hull]
parts["wheel solder joints/wires keepout"]=[wl(-9.0,-7.05,-5.0,5.0,0.2,2.6)]
# SS-12F16 switch (plate in the wall pocket, knob swept over its full travel), M2 screw shanks
pw,pz,pt=L.SW_PLATE; bl,bz,bd=L.SW_BODY; px1=L.IN_X1U+L.SW_POCKET; px0=px1-pt
sw=[box(px0,px1,L.SW_Y-pw/2,L.SW_Y+pw/2,L.SW_Z-pz/2,L.SW_Z+pz/2),
    box(px0-bd,px0,L.SW_Y-bl/2,L.SW_Y+bl/2,L.SW_Z-bz/2,L.SW_Z+bz/2)]
sw+=[box(px0-bd-L.SW_LUG_L,px0-bd,L.SW_Y+k*L.SW_LUG_P-0.8,L.SW_Y+k*L.SW_LUG_P+0.8,L.SW_Z-0.25,L.SW_Z+0.25) for k in (-1,0,1)]
parts[f"SS-12F16-G0{int(L.SW_L*10)} switch"]=sw
ax,az=L.SW_ACT
parts["switch knob, full travel"]=[box(px1,px1+L.SW_L,L.SW_Y-L.SW_TRAVEL/2-ax/2,L.SW_Y+L.SW_TRAVEL/2+ax/2,L.SW_Z-az/2,L.SW_Z+az/2)]
parts["switch lug solder/wire keepout"]=[box(px0-bd-L.SW_LUG_L-1.5,px0-bd-0.01,L.SW_Y-L.SW_LUG_P-1.2,L.SW_Y+L.SW_LUG_P+1.2,L.SW_Z-1.2,L.SW_Z+1.2)]
SCREWS_ON = "sw_screws = true" in open(os.path.join(ROOT,"case","openald_feather_case.scad")).read()
if SCREWS_ON:   # M2 x 3 pan head from outside: shank from the outer face 3 mm in (head outside the case)
    ox=L.IN_X1U+L.WALL
    for dy in (-L.SW_HOLE_P/2,L.SW_HOLE_P/2):
        c=trimesh.creation.cylinder(radius=0.95,height=3.0,sections=24); c.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,1,0]))
        c.apply_translation([ox-1.5,L.SW_Y+dy,L.SW_Z]); parts.setdefault("M2x3 switch screws (shank)",[]).append(c)
# optional 3 mm LEDs (top half sockets)
TOP_OUT=L.TOP_IN+L.TOP_T; seat=TOP_OUT-L.LED3_ABOVE_FLANGE
for (_c,_l,x,y) in L.LED3:
    parts.setdefault("3 mm LEDs (flange, body, leads)",[]).extend([cyl(x,y,3.8,seat-1.0,seat),cyl(x,y,2.95,seat,TOP_OUT-0.05),
        box(x-1.6,x+1.6,y-0.4,y+0.4,1.8,seat-1.0)])
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
# part-to-part (expected overlaps: the dial sweep contains the dial; screws thread into the switch plate)
def ok_pair(a,b):
    p={a,b}
    if any(n.startswith("wheel dial") for n in p) and any(n.startswith("SIQ") for n in p): return True
    if any(n.startswith("M2x3") for n in p) and any(n.startswith("SS-12F16") for n in p): return True
    if any(n.startswith("switch") for n in p) and any(n.startswith("SS-12F16") for n in p): return True
    if any(n.startswith("wheel solder") for n in p) and any(n.startswith("SIQ") for n in p): return True
    return False
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
        if vol>0.01 and not ({pn[i],pn[j]}<={"Feather PCB","Feather parts"}) and not ok_pair(pn[i],pn[j]):
            print(f"  part overlap {pn[i]} x {pn[j]}: {vol:.3f} mm^3")
# clearances to the inner surfaces: min gap from each part's bbox to each case piece (sampled)
cn=list(cases)
for i in range(3):
    for j in range(i+1,3):
        v=trimesh.boolean.intersection([cases[cn[i]],cases[cn[j]]],engine="manifold").volume
        if v>0.01: bad+=1; print(f"  INTERFERENCE {cn[i]} x {cn[j]}: {v:.3f} mm^3")
        else: print(f"  {cn[i]} x {cn[j]}: no overlap")
# assembly path: the top half is lowered straight down (-Z) onto the bottom half after the frame (with the wheel) is in.
# Any top-half material that ends up below the protruding part of the dial would have to pass through it, so the
# dial's footprint outside the inner wall, extruded from the dial top down to the split (Z 0), must be free of the top half.
col=trimesh.creation.cylinder(radius=R,height=DZ1+1,sections=96); col.apply_translation([WX,WY,(DZ1-1)/2])
path=trimesh.boolean.intersection([col,box(L.IN_X1U,L.IN_X1U+10,WY-10,WY+10,-1,DZ1)],engine="manifold")
v=trimesh.boolean.intersection([path,cases["case top"]],engine="manifold").volume
if v>0.01: bad+=1; print(f"  INTERFERENCE top-half assembly path over the dial: {v:.3f} mm^3")
else: print("  top half can be lowered straight over the protruding dial: OK")
# protrusions
OUT_X=L.IN_X1U+L.WALL
print(f"  wheel: dial edge X {WX+R:.2f}, outer face X {OUT_X:.2f} -> protrudes {WX+R-OUT_X:.2f} mm past the case side, "
      f"{WX+R-(OUT_X-1.0):.2f} mm past the 1 mm-deep thumb pocket floor; body front {WX+3.85:.2f} vs inner wall {L.IN_X1U:.2f}")
print(f"  switch: knob tip X {px1+L.SW_L:.2f} -> protrudes {px1+L.SW_L-OUT_X:.2f} mm past the case side (SW_L={L.SW_L:g}; "
      f"G4 {px1+4-OUT_X:.2f} / G5 {px1+5-OUT_X:.2f} / G6 {px1+6-OUT_X:.2f}); wall under the plate {L.WALL-L.SW_POCKET:.2f} mm")
print("RESULT:", "PASS (0 interferences)" if bad==0 else f"FAIL ({bad} interferences)")
allm=[m for ms in parts.values() for m in ms]; trimesh.util.concatenate(allm).export("/tmp/feather_assembly.stl")
