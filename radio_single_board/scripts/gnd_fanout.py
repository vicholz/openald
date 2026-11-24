"""2026-11-24 post-route step (run after route_pcb.py, before stitch_gnd.py; idempotent).
GND is not given to the autorouter on the 22.5 mm board (route_pcb.py); it is carried by the two pours. Every top-side
GND pad gets a short stub + via into the bottom pour, placed where it clears all other-net copper, so no GND pad is
left on an isolated top-pour island."""
import os,sys,math,pcbnew
sys.path.insert(0,os.path.dirname(__file__)); import placement as PLm
PCB=os.path.join(os.path.dirname(__file__),"../kicad/openald.kicad_pcb")
b=pcbnew.LoadBoard(PCB); OX,OY=100.0,100.0
mm=pcbnew.FromMM; gnd=b.FindNet("GND")
for g in list(b.Groups()):
    if g.GetName()=="gnd_fanout":
        for it in list(g.GetItems()): b.Delete(it)
        b.Delete(g)
grp=pcbnew.PCB_GROUP(b); grp.SetName("gnd_fanout"); b.Add(grp)
VIA_R, CLR, TW = 0.3, 0.22, 0.3
others=[t for t in b.GetTracks() if t.GetNetCode()!=gnd.GetNetCode()]
opads=[p for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode()!=gnd.GetNetCode()]
holes=[p for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH,pcbnew.PAD_ATTRIB_PTH)]
def clear(x,y,r,layers,skip=None):
    q=pcbnew.VECTOR2I(mm(x),mm(y)); a=mm(r+CLR)
    if not (OX+r+0.3<x<OX+PLm.BOARD_W-r-0.3 and OY+r+0.3<y<OY+PLm.BOARD_H-r-0.3): return False
    for t in others:
        if t.GetClass()=="PCB_VIA" or t.GetLayer() in layers:
            if t.HitTest(q,a): return False
    for p in opads:
        if any(p.IsOnLayer(L) for L in layers) and p.HitTest(q,a): return False
    for p in holes:
        if p is not skip and p.HitTest(q,mm(r+0.25)): return False
    return True
def seg_clear(x0,y0,x1,y1,skip):
    n=max(2,int(math.hypot(x1-x0,y1-y0)/0.1))
    for i in range(n+1):
        x=x0+(x1-x0)*i/n; y=y0+(y1-y0)*i/n
        if not clear(x,y,TW/2,[pcbnew.F_Cu],skip): return False
    return True
mine=[]
def far_from_mine(x,y): return all(math.hypot(x-a,y-c)>VIA_R*2+0.25 for a,c in mine)
n=0; miss=[]
for f in b.GetFootprints():
    if f.IsFlipped(): continue
    for p in f.Pads():
        if p.GetNetCode()!=gnd.GetNetCode() or p.GetAttribute()!=pcbnew.PAD_ATTRIB_SMD or not p.IsOnLayer(pcbnew.F_Cu): continue
        cx,cy=pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)
        bb=p.GetBoundingBox(); hw=max(pcbnew.ToMM(bb.GetWidth()),pcbnew.ToMM(bb.GetHeight()))/2
        done=False
        for d in [hw+0.45+k*0.2 for k in range(8)]:
            for a in range(0,360,15):
                x=cx+d*math.cos(math.radians(a)); y=cy+d*math.sin(math.radians(a))
                if not far_from_mine(x,y): continue
                if not clear(x,y,VIA_R,[pcbnew.F_Cu,pcbnew.B_Cu]): continue
                # stub from the pad edge region to the via
                if not seg_clear(cx,cy,x,y,None): continue
                v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(mm(x),mm(y))); v.SetWidth(pcbnew.F_Cu,mm(2*VIA_R)); v.SetDrill(mm(0.3)); v.SetNet(gnd); b.Add(v); grp.AddItem(v)
                t=pcbnew.PCB_TRACK(b); t.SetStart(p.GetPosition()); t.SetEnd(v.GetPosition()); t.SetWidth(mm(TW)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t); grp.AddItem(t)
                mine.append((x,y)); n+=1; done=True; break
            if done: break
        if not done: miss.append(f"{f.GetReference()}-{p.GetNumber()}")
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(PCB,b)
print("GND fan-out vias:",n,"| pads without a fan-out (rely on the top pour):",", ".join(miss) or "none")
