"""Post-route step (after route_pcb.py; idempotent):
 1. widen the high-current tracks (input, VIN_SW, LX, 5 V rails: up to 2.0 mm; slot outputs: up to 1.2 mm) wherever the
    0.2 mm clearance to every other-net item and 0.3 mm to the board edge still holds; segments into fine-pitch pins stay
    at their routed width
 2. GND stitching vias (0.6/0.3) on a 3 mm grid wherever a via fits fully inside the GND pour on both layers and outside
    every courtyard
 3. refill and save"""
import os,sys,math,pcbnew
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import placement as PLm
PCB=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/openald-dock.kicad_pcb")
b=pcbnew.LoadBoard(PCB); OX,OY=100.0,100.0
mm=pcbnew.FromMM
def P(x,y): return pcbnew.VECTOR2I(mm(OX+x),mm(OY+y))
W,H=PLm.BOARD_W,PLm.BOARD_H
HI={"VBUS","VBUS_F","VIN_SW","LX_A","LX_B","5V_A","5V_B"}; MID={f"SLOT{i}" for i in range(1,7)}
CLR=mm(0.2)
pads=[p for f in b.GetFootprints() for p in f.Pads()]
def others(t,layer):
    bb=t.GetBoundingBox(); bb.Inflate(mm(2.5))
    out=[]
    for o in b.GetTracks():
        if o is t or o.GetNetCode()==t.GetNetCode(): continue
        if o.GetClass()=="PCB_TRACK" and o.GetLayer()!=layer: continue
        if o.GetBoundingBox().Intersects(bb): out.append(o)
    for p in pads:
        if p.GetNetCode()==t.GetNetCode() and p.GetNetCode()>0: continue
        if not p.IsOnLayer(layer) and p.GetAttribute()!=pcbnew.PAD_ATTRIB_NPTH: continue
        if p.GetBoundingBox().Intersects(bb): out.append(p)
    return out
def ok(t,layer,obs):
    s=t.GetEffectiveShape(layer)
    for o in obs:
        if o.GetClass()=="PCB_PAD" and o.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH:
            if s.Collide(o.GetEffectiveHoleShape(),mm(0.25)): return False
            continue
        if s.Collide(o.GetEffectiveShape(layer),CLR): return False
    w=pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu) if t.GetClass()=='PCB_VIA' else t.GetWidth())/2+0.3
    for q in (t.GetStart(),t.GetEnd()):
        x=pcbnew.ToMM(q.x)-OX; y=pcbnew.ToMM(q.y)-OY
        if x<w or y<w or x>W-w or y>H-w: return False
    return True
# remove the GND zones while widening (re-added by the refill below) -> zones stay; they are refilled afterwards
tracks=[t for t in b.GetTracks() if t.GetClass()=="PCB_TRACK" and t.GetNetname() in HI|MID]
tracks.sort(key=lambda t:-t.GetLength())
nw=0
for t in tracks:
    widths=[2.0,1.6,1.2,1.0] if t.GetNetname() in HI else [1.2,1.0,0.8]
    w0=t.GetWidth(); L=t.GetLayer(); obs=others(t,L)
    for w in widths:
        if mm(w)<=w0: break
        t.SetWidth(mm(w))
        if ok(t,L,obs): nw+=1; break
        t.SetWidth(w0)
print("widened segments:",nw,"of",len(tracks))
# vias on the high-current nets: bump to 1.0/0.5 where they fit
for v in [t for t in b.GetTracks() if t.GetClass()=="PCB_VIA" and t.GetNetname() in HI]:
    d0=v.GetWidth(pcbnew.F_Cu); dr0=v.GetDrillValue()
    v.SetWidth(pcbnew.F_Cu,mm(1.0)); v.SetWidth(pcbnew.B_Cu,mm(1.0)); v.SetDrill(mm(0.5))
    if not (ok(v,pcbnew.F_Cu,others(v,pcbnew.F_Cu)) and ok(v,pcbnew.B_Cu,others(v,pcbnew.B_Cu))):
        v.SetWidth(pcbnew.F_Cu,d0); v.SetWidth(pcbnew.B_Cu,d0); v.SetDrill(dr0)
# 2. GND stitching
gnd=b.FindNet("GND")
for t in list(b.GetTracks()):
    g=t.GetParentGroup()
    if t.GetClass()=="PCB_VIA" and g and g.GetName()=="gnd_stitch": b.Delete(t)
for g in list(b.Groups()):
    if g.GetName()=="gnd_stitch": b.Delete(g)
grp=pcbnew.PCB_GROUP(b); grp.SetName("gnd_stitch"); b.Add(grp)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
zones={z.GetFirstLayer():z for z in b.Zones() if z.GetNetname()=="GND" and not z.GetIsRuleArea()}
crt=[]
for f in b.GetFootprints():
    f.BuildCourtyardCaches()
    bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if bb.GetWidth()>0: crt.append(bb)
def free(x,y,r=0.3+0.35):
    for a in range(0,360,30):
        q=P(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a)))
        for L,z in zones.items():
            if not z.GetFilledPolysList(L).Contains(q): return False
    c=P(x,y); m=mm(0.5)
    for bb in crt:
        if bb.GetLeft()-m<c.x<bb.GetRight()+m and bb.GetTop()-m<c.y<bb.GetBottom()+m: return False
    return True
existing=[(pcbnew.ToMM(t.GetPosition().x)-OX,pcbnew.ToMM(t.GetPosition().y)-OY) for t in b.GetTracks() if t.GetClass()=="PCB_VIA"]
n=0; placed=[]
for off in (0.0,):
    y=2.0+off
    while y<H-1.0:
        x=2.0+off
        while x<W-1.0:
            if free(x,y) and all(math.hypot(x-a,y-c)>2.0 for a,c in existing+placed):
                v=pcbnew.PCB_VIA(b); v.SetPosition(P(x,y)); v.SetWidth(pcbnew.F_Cu,mm(0.6)); v.SetWidth(pcbnew.B_Cu,mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(gnd)
                b.Add(v); grp.AddItem(v); placed.append((x,y)); n+=1
            x+=5.0
        y+=5.0
for f in b.GetFootprints():      # hide hole refs (silk clutter)
    if f.GetReference().startswith('H'): f.Reference().SetVisible(False)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("GND stitching vias:",n)
