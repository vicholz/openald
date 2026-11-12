#!/usr/bin/env python3
"""Interference check: assembled PCB (KiCad STEP models + this project's WRL meshes)
against the two case halves in assembly pose.  Reports overlap volume per part."""
import pcbnew, trimesh, numpy as np, re, math, os, sys, subprocess
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pcb=os.path.join(ROOT,'kicad','openald.kicad_pcb')
import placement as PLm
b=pcbnew.LoadBoard(pcb); H=PLm.BOARD_H
def wrl_mesh(path):
    t=open(path).read(); meshes=[]
    for pts,idx in re.findall(r'point\s*\[([^\]]*)\].*?coordIndex\s*\[([^\]]*)\]',t,re.S):
        v=np.array([float(a) for a in re.findall(r'-?[\d.]+(?:e-?\d+)?',pts)]).reshape(-1,3)*2.54
        ii=[int(a) for a in re.findall(r'-?\d+',idx)]; faces=[];cur=[]
        for k in ii:
            if k<0:
                for j in range(1,len(cur)-1): faces.append([cur[0],cur[j],cur[j+1]])
                cur=[]
            else: cur.append(k)
        meshes.append(trimesh.Trimesh(v,faces))
    return meshes
parts={}
for f in b.GetFootprints():
    for m in f.Models():
        if 'KIPRJMOD' not in m.m_Filename: continue
        p=m.m_Filename.replace('${KIPRJMOD}',os.path.join(ROOT,'kicad'))
        a=math.radians(f.GetOrientationDegrees())
        px=pcbnew.ToMM(f.GetPosition().x)-100; py=H-(pcbnew.ToMM(f.GetPosition().y)-100)
        T=trimesh.transformations.rotation_matrix(a,[0,0,1]); T[:3,3]=[px,py,1.6]
        for mm in wrl_mesh(p):
            mm.apply_transform(T); parts.setdefault(f.GetReference(),[]).append(mm)
# stock STEP-model parts via kicad-cli STL (one per ref, so overlaps are attributable)
stock=sorted(f.GetReference() for f in b.GetFootprints() if len(f.Models()) and not f.GetReference().startswith('H') and not f.IsDNP())   # every fitted part with a 3D model
for r in [s for s in stock if s not in parts]:
    out=f'/tmp/fit_{r}.stl'
    subprocess.run(['kicad-cli','pcb','export','stl','--subst-models','--component-filter',r,'--user-origin',f'100x{100+H:g}mm','-f','-o',out,pcb],capture_output=True)
    if not (os.path.exists(out) and os.path.getsize(out)>200): print('no model for',r); continue
    pcs=trimesh.load(out).split(only_watertight=False)
    # drop the board body (and its holes' walls): pieces lying within z 0..1.6 spanning the board
    if r=='BT1': globals()['BOARD_PIECES']=[p for p in pcs if (p.bounds[0][2]>-0.01 and p.bounds[1][2]<1.61 and (p.bounds[1]-p.bounds[0])[0]>30)]
    keep=[p for p in pcs if not (p.bounds[0][2]>-0.01 and p.bounds[1][2]<1.61 and (p.bounds[1]-p.bounds[0])[0]>30)]
    parts[r]=keep
top=trimesh.load(sys.argv[1]); bot=trimesh.load(sys.argv[2])
bad=0
for r,ms in sorted(parts.items()):
    mesh=trimesh.util.concatenate(ms)
    for name,c in (('top',top),('bottom',bot)):
        
        vol=0
        for sub in ms:
            # exact mesh when it is a closed solid, otherwise its convex hull (conservative)
            try: vol+=trimesh.boolean.intersection([sub if sub.is_watertight else sub.convex_hull,c],engine='manifold').volume
            except Exception as e: pass
        if vol>0.01: bad+=1; print(f"  {r:5s} intersects case_{name}: {vol:.2f} mm^3")
    if mesh is None or len(mesh.vertices)==0: continue
    lo,hi=mesh.bounds; print(f"{r:5s} x {lo[0]:6.2f}..{hi[0]:6.2f}  y {lo[1]:6.2f}..{hi[1]:6.2f}  z {lo[2]:6.2f}..{hi[2]:6.2f}")
# ---- LED light tunnels: walls must clear every component (and are not allowed to touch the board)
if len(sys.argv)>3:
    tun=trimesh.load(sys.argv[3]); tz0=tun.bounds[0][2]
    print(f"TUNNELS: wall bottom z = {tz0:.2f} mm (PCB top 1.60 -> gap {tz0-1.6:.2f} mm)")
    from scipy.spatial import cKDTree
    tree=cKDTree(np.vstack([tun.sample(300000),tun.vertices]))   # dense surface samples (~0.03 mm spacing)
    worst=(99,None)
    for r,ms in sorted(parts.items()):
        mesh=trimesh.util.concatenate(ms)
        vol=sum(trimesh.boolean.intersection([s if s.is_watertight else s.convex_hull,tun],engine='manifold').volume for s in ms)
        if vol>0.001: bad+=1; print(f"  {r:5s} intersects LED tunnel walls: {vol:.3f} mm^3")
        pts=mesh.sample(20000) if len(mesh.faces) else mesh.vertices
        pts=np.vstack([pts,mesh.vertices])
        lo,hi=tun.bounds; m=(pts[:,0]>lo[0]-3)&(pts[:,0]<hi[0]+3)&(pts[:,1]>lo[1]-3)&(pts[:,1]<hi[1]+3)
        if m.sum()==0: continue
        d,_=tree.query(pts[m]); dm=float(d.min())
        if dm<worst[0]: worst=(dm,r)
        if dm<1.0: print(f"  {r:5s} min distance to tunnel walls {dm:.2f} mm")
    print(f"TUNNELS: closest component {worst[1]} at {worst[0]:.2f} mm")
print("INTERFERENCES:",bad)
# assembled-PCB mesh for the case preview renders
allm=[m for ms in parts.values() for m in ms]+globals().get('BOARD_PIECES',[])
trimesh.util.concatenate(allm).export('/tmp/pcb_assembly.stl')
