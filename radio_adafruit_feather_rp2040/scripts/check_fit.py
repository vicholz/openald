#!/usr/bin/env python3
"""3D interference / fit check for the Feather variant.
Parts (assembly pose, case frame): Feather RP2040 (board with holes + every component envelope from Adafruit's
Eagle file), 18650 holder box, FM module (board + jack box, ESTIMATED), SIQ-02FVS3 wheel (Mitsumi-datasheet WRL model)
plus its dial swept over the push travel and a solder/wire keepout at its terminals, SS-12F16 switch (datasheet
boxes) with the knob swept over its travel, lug keepout, optional 3 mm LEDs.
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
def usb_shell(p):   # USB-C receptacle (CUI CUSB31): the shell is a stadium (fully rounded ends, r = h/2), not a box
    from shapely.geometry import box as sbox
    r=(p[5]-p[4])/2-0.01; prof=sbox(p[0]+r,p[4]+r,p[1]-r,p[5]-r).buffer(r,resolution=16)
    m=trimesh.creation.extrude_polygon(prof,p[3]-p[2])   # profile in (x,z), extruded along local z -> map to Y
    m.apply_transform(np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)); m.apply_translation([0,p[3],0]); return m
for i,p in enumerate(fparts):
    is_usb = abs((p[1]-p[0])-8.94)<0.05 and abs(p[5]-4.86)<0.05
    parts.setdefault("Feather parts",[]).append(usb_shell(p) if is_usb else box(*p))
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
# SS-12F16 switch, screwless, left wall: plate pressed to the outer skin (n = SW_SKIN from the outer face), body inward,
# knob outward through the slot, swept over its full travel. The fit model uses a 0.45 plate (the crush bumps' free gap);
# 0.5-0.6 plates squeeze the 0.25 bumps by 0.05-0.15 (reported below, intended).
X0OU=L.IN_X0U-L.WALL
pw,pz,_pt=L.SW_PLATE; pt=L.SW_GROOVE-L.SW_CRUSH; bl,bz,bd=L.SW_BODY; px0=X0OU+L.SW_SKIN; px1=px0+pt
sw=[box(px0,px1,L.SW_Y-pw/2,L.SW_Y+pw/2,L.SW_Z-pz/2,L.SW_Z+pz/2),
    box(px1,px1+bd,L.SW_Y-bl/2,L.SW_Y+bl/2,L.SW_Z-bz/2,L.SW_Z+bz/2)]
sw+=[box(px1+bd,px1+bd+L.SW_LUG_L,L.SW_Y+k*L.SW_LUG_P-0.8,L.SW_Y+k*L.SW_LUG_P+0.8,L.SW_Z-0.25,L.SW_Z+0.25) for k in (-1,0,1)]
parts[f"SS-12F16-G0{int(L.SW_L*10)} switch"]=sw
ax,az=L.SW_ACT
parts["switch knob, full travel"]=[box(px0-L.SW_L,px0,L.SW_Y-L.SW_TRAVEL/2-ax/2,L.SW_Y+L.SW_TRAVEL/2+ax/2,L.SW_Z-az/2,L.SW_Z+az/2)]
parts["switch lug solder/wire keepout"]=[box(px1+bd+0.01,px1+bd+L.SW_LUG_L+1.5,L.SW_Y-L.SW_LUG_P-1.2,L.SW_Y+L.SW_LUG_P+1.2,L.SW_Z-1.2,L.SW_Z+1.2)]
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
# part-to-part (expected overlaps: the dial sweep contains the dial)
def ok_pair(a,b):
    p={a,b}
    if any(n.startswith("wheel dial") for n in p) and any(n.startswith("SIQ") for n in p): return True
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
# switch drop-in path: the switch goes into the bottom half from above (plate in the groove, knob down the channel)
def up(m,z1=3.0):
    lo,hi=m.bounds; return box(lo[0],hi[0],lo[1],hi[1],lo[2],z1)
v=sum(trimesh.boolean.intersection([up(m),cases["case bottom"]],engine="manifold").volume for m in parts[f"SS-12F16-G0{int(L.SW_L*10)} switch"])
# the knob is checked at the travel position where it sits while dropping: centred in the channel (any position fits)
kn=box(px0-L.SW_L,px0,L.SW_Y-ax/2,L.SW_Y+ax/2,L.SW_Z-az/2,L.SW_Z+az/2); v+=trimesh.boolean.intersection([up(kn),cases["case bottom"]],engine="manifold").volume
if v>0.01: bad+=1; print(f"  INTERFERENCE switch drop-in path (bottom half): {v:.3f} mm^3")
else: print("  switch drops straight into its groove from above (no screws): OK")
# switch retention: what closes it in once the frame and the top half are on
fr=cases["frame"]; top=cases["case top"]
cap=trimesh.boolean.intersection([fr,box(px0-0.1,px1+bd,L.SW_Y-pw/2,L.SW_Y+pw/2,L.SW_Z+pz/2,L.SW_Z+pz/2+1.5)],engine="manifold")
print(f"  switch cap: frame tab over the plate/body from Z {cap.bounds[0][2]:.2f} (plate/body top {L.SW_Z+pz/2:.2f}) -> {cap.bounds[0][2]-(L.SW_Z+pz/2):.2f} mm vertical play")
for t in (0.4,0.5,0.6): print(f"    plate {t:.1f}: {'free in groove, play %.2f' % (pt-t) if t<=pt else 'crush bumps squeezed %.2f' % (t-pt)}")
# frame: vertical insertion into the bottom half (tabs into the parting-line notches), and the clamp
tabs=[]
for (sd,pos,w) in json.loads(re.search(r"frame_tabs\s*=\s*(\[.*?\]);",open(os.path.join(ROOT,"case","case_params.scad")).read(),re.S).group(1)):
    tabs.append((sd,pos,w))
v=0
for (sd,pos,w) in tabs:
    if sd==0:   xi=L.IN_X0U if pos>54.3 else L.IN_X0; m=box(xi-0.85,xi+0.85,pos-w/2,pos+w/2,L.DECK_Z0,L.DECK_Z1)
    elif sd==1: xi=L.IN_X1U if pos>54.3 else L.IN_X1; m=box(xi-0.85,xi+0.85,pos-w/2,pos+w/2,L.DECK_Z0,L.DECK_Z1)
    else:       m=box(pos-w/2,pos+w/2,L.Y_IN1-0.85,L.Y_IN1+0.85,L.DECK_Z0,L.DECK_Z1)
    v+=trimesh.boolean.intersection([up(m,6),cases["case bottom"]],engine="manifold").volume
    under=trimesh.boolean.intersection([box(m.bounds[0][0],m.bounds[1][0],m.bounds[0][1],m.bounds[1][1],L.DECK_Z1-0.05,L.DECK_Z1+0.3),top],engine="manifold")
    print(f"    tab {'LRT'[sd]}{pos:g} w{w:g}: top-half plug over it: {'yes' if under.volume>0.01 else 'NO'}")
if v>0.01: bad+=1; print(f"  INTERFERENCE frame tab insertion path: {v:.3f} mm^3")
else: print(f"  frame drops in from above; {len(tabs)} tabs sit on the notch floors (Z {L.DECK_Z0}) under top-half plugs (Z {L.DECK_Z1}): clamped")
# top half below the parting line (must be only the switch-channel tongue, which closes over the knob, not through it)
lowt=trimesh.boolean.intersection([top,box(-60,100,-60,150,-30,-0.02)],engine="manifold")
if lowt.volume>0.01: print(f"  top half below Z 0: {lowt.volume:.2f} mm^3 at x {lowt.bounds[0][0]:.2f}..{lowt.bounds[1][0]:.2f} y {lowt.bounds[0][1]:.2f}..{lowt.bounds[1][1]:.2f} z {lowt.bounds[0][2]:.2f}..{lowt.bounds[1][2]:.2f} (knob top {L.SW_Z+az/2:.2f})")
def down(m):   # swept volume of a part moved down 30 mm (= the space top-half material must pass through to get under it)
    h=m if m.is_watertight else m.convex_hull; h2=h.copy(); h2.apply_translation([0,0,-30])
    return trimesh.util.concatenate([h,h2]).convex_hull   # (convex: conservative)
v=0
for k in parts:
    if k.startswith("3 mm LED") or k.startswith("Feather"): continue   # LEDs live in the top half; Feather is checked by its clamp posts
    vk=sum(trimesh.boolean.intersection([down(m),top],engine="manifold").volume for m in parts[k])
    if vk>0.01: print(f"    lowering path through {k}: {vk:.3f} mm^3")
    v+=vk
if v>0.01: bad+=1; print(f"  INTERFERENCE top-half lowering path through a part: {v:.3f} mm^3")
else: print("  top half lowers straight down without passing through any part: OK")
# battery holder vs frame: the holder cannot lift the frame
H=L.HOLDER; hf=trimesh.boolean.intersection([fr,box(H["x0"],H["x1"],H["y0"],H["y1"],-30,5)],engine="manifold")
print(f"  holder top Z {H['z1']:.2f} (in a {L.HOLDER_POCKET} floor pocket), frame underside over it Z {hf.bounds[0][2]:.2f} -> gap {hf.bounds[0][2]-H['z1']:.2f} mm")
# protrusions
OUT_X=L.IN_X1U+L.WALL
print(f"  wheel: dial edge X {WX+R:.2f}, outer face X {OUT_X:.2f} -> protrudes {WX+R-OUT_X:.2f} mm past the case side, "
      f"{WX+R-(OUT_X-1.0):.2f} mm past the 1 mm-deep thumb pocket floor; body front {WX+3.85:.2f} vs inner wall {L.IN_X1U:.2f}")
print(f"  switch (left side): knob tip X {px0-L.SW_L:.2f} -> protrudes {X0OU-(px0-L.SW_L):.2f} mm past the case side (SW_L={L.SW_L:g}; "
      f"G4 {4-L.SW_SKIN:.2f} / G5 {5-L.SW_SKIN:.2f} / G6 {6-L.SW_SKIN:.2f}); skin in front of the plate {L.SW_SKIN:.2f} mm")
# USB-C: receptacle mouth vs the case bottom (dock) face and the cable-plug recess floor
uf=json.load(open(os.path.join(ROOT,"ref","feather_rp2040_mech.json")))["usb"]["face_y"]
YO=L.Y_IN0-L.WALL; RF=YO+1.5
print(f"  USB-C: receptacle mouth Y {uf:.2f}: {uf-YO:.2f} mm inside the outer (dock) face Y {YO:.2f}, {uf-RF:.2f} mm behind the "
      f"cable-plug recess floor Y {RF:.2f} (single board: 2.50 / 1.00); dock plug insertion {6.0-uf:.2f} mm on the standard pad (USB-C full seat 6.20 +/- 0.20 -> use the dock's {-uf:.2f} mm Feather riser shim: 6.00, like the single board)")
# switch backing: material behind the plate ears / body and under it (bottom half)
bh=cases["case bottom"]
ear=sum(trimesh.boolean.intersection([box(px1+0.3,px1+2.3,L.SW_Y+sg*7.0-0.5,L.SW_Y+sg*7.0+0.5,L.SW_Z-pz/2,L.SW_Z+pz/2),bh],engine="manifold").volume for sg in (-1,1))
bk=trimesh.boolean.intersection([box(px1+bd+0.1,px1+bd+3,L.SW_Y-5.4,L.SW_Y+5.4,L.SW_Z-pz/2,L.SW_Z+pz/2),bh],engine="manifold")
sh=trimesh.boolean.intersection([box(px1,px1+bd,L.SW_Y-5,L.SW_Y+5,L.FLOOR_Z,L.SW_Z-pz/2-0.05),bh],engine="manifold")
print(f"  switch backing: solid behind the ears {ear:.1f}/{2*2*1*pz:.1f} mm^3 sampled; back wall from X {bk.bounds[0][0]:.2f} (body back {px1+bd:.2f}, "
      f"{bk.bounds[0][0]-(px1+bd):.2f} gap; {bk.bounds[0][0]-(px0+0.6+bd):.2f} with a 0.6 plate) to X {bk.bounds[1][0]:.2f}; shelf under the body {sh.volume/((bd)*10*(L.SW_Z-pz/2-0.05-L.FLOOR_Z))*100:.0f}% solid down to the floor")
print("RESULT:", "PASS (0 interferences)" if bad==0 else f"FAIL ({bad} interferences)")
allm=[m for ms in parts.values() for m in ms]; trimesh.util.concatenate(allm).export("/tmp/feather_assembly.stl")
