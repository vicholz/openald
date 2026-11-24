"""2026-11-24 post-route repair for the 22.5 mm board (run after route_pcb.py and gnd_fanout.py; idempotent-ish).
Freerouting leaves a few connections open on this narrow board, and GND (left to the pours) can end up on separate pour
islands. This step finds every net that KiCad's own copper splits into more than one piece (raster connectivity on
both layers, zone fills included) and joins the pieces with a simple two-layer grid maze router (0.1 mm grid, 0.2 mm
tracks, 0.6/0.3 mm vias) that keeps the board's clearances to all other-net copper, holes and the board edge.
New items go into the group "maze_fix" (deleted and redone on every run). Zones are refilled at the end."""
import os,sys,math,heapq,pcbnew,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
sys.path.insert(0,os.path.dirname(__file__)); import placement as PLm
PCB=os.path.join(os.path.dirname(__file__),"../kicad/openald.kicad_pcb")
b=pcbnew.LoadBoard(PCB); OX,OY=100.0,100.0; W,H=PLm.BOARD_W,PLm.BOARD_H
R=0.1; NX,NY=int(round(W/R))+1,int(round(H/R))+1
TW=0.2; CLR=0.15; VIA_D,VIA_DRILL=0.6,0.3
LAYERS=[pcbnew.F_Cu,pcbnew.B_Cu]
mm=pcbnew.FromMM; tomm=pcbnew.ToMM
for g in list(b.Groups()):
    if g.GetName()=="maze_fix":
        for it in list(g.GetItems()): b.Delete(it)
        b.Delete(g)
grp=pcbnew.PCB_GROUP(b); grp.SetName("maze_fix"); b.Add(grp)
def fill():
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
def polys_of(ps):
    out=[]
    for i in range(ps.OutlineCount()):
        o=ps.Outline(i); out.append(([(tomm(o.CPoint(j).x)-OX,tomm(o.CPoint(j).y)-OY) for j in range(o.PointCount())],False))
        for k in range(ps.HoleCount(i)):
            h=ps.Hole(i,k); out.append(([(tomm(h.CPoint(j).x)-OX,tomm(h.CPoint(j).y)-OY) for j in range(h.PointCount())],True))
    return out
def raster(polys,img=None):
    img=img or Image.new("1",(NX,NY),0); d=ImageDraw.Draw(img)
    for pts,hole in polys:
        if len(pts)>=3: d.polygon([(x/R,y/R) for x,y in pts],fill=0 if hole else 1)
    return img
def item_polys(it,layer,clr):
    ps=pcbnew.SHAPE_POLY_SET()
    it.TransformShapeToPolygon(ps,layer,mm(clr),mm(0.005),pcbnew.ERROR_OUTSIDE)
    return polys_of(ps)
def hole_polys(p,clr):
    ps=pcbnew.SHAPE_POLY_SET(); p.TransformHoleToPolygon(ps,mm(clr),mm(0.005),pcbnew.ERROR_OUTSIDE); return polys_of(ps)
def items():
    pads=[p for f in b.GetFootprints() for p in f.Pads()]
    return pads,list(b.GetTracks())
def net_copper(net):
    """per-layer raster of the net's copper (incl. zone fills) and the layer links (vias, THT pads)"""
    pads,trk=items(); M=[Image.new("1",(NX,NY),0) for _ in LAYERS]; links=Image.new("1",(NX,NY),0)
    for k,L in enumerate(LAYERS):
        pl=[]
        for p in pads:
            if p.GetNetCode()==net and p.IsOnLayer(L): pl+=item_polys(p,L,0)
        for t in trk:
            if t.GetNetCode()==net and (t.GetClass()=="PCB_VIA" or t.GetLayer()==L): pl+=item_polys(t,L,0)
        for z in b.Zones():
            if z.GetNetCode()==net and not z.GetIsRuleArea() and z.IsOnLayer(L): pl+=polys_of(z.GetFilledPolysList(L))
        raster(pl,M[k])
    ll=[]
    for p in pads:
        if p.GetNetCode()==net and p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: ll+=item_polys(p,pcbnew.F_Cu,0)
    for t in trk:
        if t.GetNetCode()==net and t.GetClass()=="PCB_VIA": ll+=item_polys(t,pcbnew.F_Cu,0)
    raster(ll,links)
    return np.stack([np.array(m,dtype=bool).T for m in M]), np.array(links,dtype=bool).T   # [layer, x, y]
def obstacles(net,infl):
    pads,trk=items(); O=[Image.new("1",(NX,NY),0) for _ in LAYERS]
    for k,L in enumerate(LAYERS):
        pl=[]
        for p in pads:
            if p.GetNetCode()!=net and p.IsOnLayer(L): pl+=item_polys(p,L,infl)
            if p.HasHole() and (p.GetNetCode()!=net or p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH): pl+=hole_polys(p,infl+0.1)
        for t in trk:
            if t.GetNetCode()!=net and (t.GetClass()=="PCB_VIA" or t.GetLayer()==L): pl+=item_polys(t,L,infl)
        # (the GND pours are not obstacles: they are refilled around the new copper)
        raster(pl,O[k])
    A=np.stack([np.array(o,dtype=bool).T for o in O])
    e=int(math.ceil((0.3+infl-CLR)/R))     # copper-to-edge 0.3
    A[:,:e,:]=True; A[:,-e:,:]=True; A[:,:,:e]=True; A[:,:,-e:]=True
    # rounded board corners
    xs=np.arange(NX)*R; ys=np.arange(NY)*R; X,Y=np.meshgrid(xs,ys,indexing="ij"); cr=PLm.CORNER_R; lim=cr-(0.3+infl-CLR)
    for cx,cy in ((cr,cr),(W-cr,cr),(cr,H-cr),(W-cr,H-cr)):
        m=((X-cx)*np.sign(cx-W/2+1e-9)>0)&((Y-cy)*np.sign(cy-H/2+1e-9)>0)&(np.hypot(X-cx,Y-cy)>lim)
        A[:,m]=True
    return A
def route(net,src,dst,blk,vblk):
    """Dijkstra from src cells to dst cells ([2,NX,NY] bool), 8-connected per layer, vias where vblk is free"""
    INF=1e18; dist=np.full((2,NX,NY),INF); prev={}
    pq=[]
    for l,x,y in zip(*np.nonzero(src)):
        dist[l,x,y]=0; pq.append((0.0,int(l),int(x),int(y)))
    heapq.heapify(pq)
    steps=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414),(1,-1,1.414),(-1,1,1.414),(-1,-1,1.414)]
    while pq:
        d,l,x,y=heapq.heappop(pq)
        if d>dist[l,x,y]: continue
        if dst[l,x,y]:
            path=[(l,x,y)]
            while (path[-1]) in prev: path.append(prev[path[-1]])
            return path[::-1]
        for dx,dy,c in steps:
            nx_,ny_=x+dx,y+dy
            if not (0<=nx_<NX and 0<=ny_<NY) or blk[l,nx_,ny_]: continue
            if dx and dy and (blk[l,x+dx,y] or blk[l,x,y+dy]): continue
            nd=d+c+(0.3 if l==1 else 0)
            if nd<dist[l,nx_,ny_]: dist[l,nx_,ny_]=nd; prev[(l,nx_,ny_)]=(l,x,y); heapq.heappush(pq,(nd,l,nx_,ny_))
        if not vblk[x,y]:
            ol=1-l; nd=d+25
            if not blk[ol,x,y] and nd<dist[ol,x,y]: dist[ol,x,y]=nd; prev[(ol,x,y)]=(l,x,y); heapq.heappush(pq,(nd,ol,x,y))
    return None
def emit(net,path):
    P=lambda x,y: pcbnew.VECTOR2I(mm(OX+x*R),mm(OY+y*R))
    # split into per-layer runs, merge collinear steps
    runs=[]; cur=[path[0]]
    for q in path[1:]:
        if q[0]!=cur[-1][0]: runs.append(cur); cur=[q]
        else: cur.append(q)
    runs.append(cur)
    for i,r in enumerate(runs):
        if i>0:
            v=pcbnew.PCB_VIA(b); v.SetPosition(P(r[0][1],r[0][2])); v.SetWidth(pcbnew.F_Cu,mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNetCode(net); b.Add(v); grp.AddItem(v)
        pts=[(r[0][1],r[0][2])]
        for j in range(1,len(r)):
            if j+1<len(r):
                d1=(r[j][1]-r[j-1][1],r[j][2]-r[j-1][2]); d2=(r[j+1][1]-r[j][1],r[j+1][2]-r[j][2])
                if d1==d2: continue
            pts.append((r[j][1],r[j][2]))
        for a,c in zip(pts,pts[1:]):
            t=pcbnew.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*c)); t.SetWidth(mm(TW)); t.SetLayer(LAYERS[r[0][0]]); t.SetNetCode(net); b.Add(t); grp.AddItem(t)
fill()
nets=sorted({p.GetNetCode() for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode()>0})
gnd=b.FindNet("GND").GetNetCode()
total=0; failed=[]
for net in nets:
    name=b.FindNet(net) if False else b.GetNetInfo().GetNetItem(net).GetNetname()
    for it in range(30):
        cu,lk=net_copper(net)
        # components: label each layer, then merge across links
        lab=np.zeros(cu.shape,dtype=np.int32); n=0
        for k in range(2):
            l,c=ndimage.label(cu[k],structure=np.ones((3,3))); lab[k]=np.where(l>0,l+n,0); n+=c
        parent=list(range(n+1))
        def f(a):
            while parent[a]!=a: parent[a]=parent[parent[a]]; a=parent[a]
            return a
        for x,y in zip(*np.nonzero(lk)):
            a,c=lab[0,x,y],lab[1,x,y]
            if a and c: parent[f(a)]=f(c)
        # only components that contain a pad of the net matter (stray zone islands without pads are removed by the filler)
        padcells=[]
        for fp in b.GetFootprints():
            for p in fp.Pads():
                if p.GetNetCode()==net:
                    x=int(round((tomm(p.GetPosition().x)-OX)/R)); y=int(round((tomm(p.GetPosition().y)-OY)/R))
                    for k in range(2):
                        if 0<=x<NX and 0<=y<NY and lab[k,x,y]: padcells.append(f(lab[k,x,y]))
        roots=sorted(set(padcells))
        if len(roots)<=1: break
        # join the smallest piece to the rest
        sizes={r:0 for r in roots}
        R_all=np.vectorize(f)(lab) if n<5000 else None
        for r in roots: sizes[r]=int((R_all==r).sum())
        small=min(roots,key=lambda r:sizes[r])
        src=(R_all==small); dst=np.isin(R_all,[r for r in roots if r!=small])
        blk=obstacles(net,TW/2+CLR+0.02); vb=obstacles(net,VIA_D/2+CLR+0.02); vblk=vb[0]|vb[1]
        blk=blk&~src&~dst|(blk&False)
        path=route(net,src,dst,blk,vblk)
        if not path: failed.append(name); print("NO PATH",name); break
        emit(net,path); total+=1; fill()
        print(f"joined a piece of {name}: {len(path)} cells")
fill()
pcbnew.SaveBoard(PCB,b)
print("maze_fix: connections added:",total,"| failed:",", ".join(failed) or "none")
