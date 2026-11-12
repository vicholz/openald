"""rev 4.1/4.2 post-route step (run after route_pcb.py; idempotent):
 - sync footprint Value/LCSC/MPN fields from design.py (lets value-only fixes be applied without re-routing)
 - add GND stitching vias (0.6/0.3 mm) on a 2.5 mm grid wherever a via fits fully inside the filled GND pour on
   BOTH layers, outside every top-side courtyard (no vias under ICs, the module, connectors or switches)
 - add an extra thermal via in the centre of the TP4056 exposed pad (was 2 vias)
Then refills the zones and saves."""
import os,sys,math,pcbnew
sys.path.insert(0,os.path.dirname(__file__)); import design, placement as PLm
PCB=os.path.join(os.path.dirname(__file__),"../kicad/openald.kicad_pcb")
b=pcbnew.LoadBoard(PCB); OX,OY=100.0,100.0      # board top-left corner in KiCad coords
def P(x,y): return pcbnew.VECTOR2I(pcbnew.FromMM(OX+x),pcbnew.FromMM(OY+y))
# 1. field sync
for p in design.P:
    f=b.FindFootprintByReference(p["ref"])
    if not f: continue
    if f.GetValue()!=p["val"]: print("value",p["ref"],f.GetValue(),"->",p["val"]); f.SetValue(p["val"])
    for k,v in (("LCSC",p.get("lcsc","")),("MPN",p.get("mpn",""))):
        fld=f.GetFieldByName(k)
        if fld and v and fld.GetText()!=v: fld.SetText(v)
gnd=b.FindNet("GND")
# 2. remove earlier stitching vias (tagged by exact size 0.6/0.3 on a 2.5 mm grid is fragile) -> use a group
for t in list(b.GetTracks()):
    g=t.GetParentGroup()
    if t.GetClass()=="PCB_VIA" and g and g.GetName()=="gnd_stitch": b.Delete(t)
for g in list(b.Groups()):
    if g.GetName()=="gnd_stitch": b.Delete(g)
grp=pcbnew.PCB_GROUP(b); grp.SetName("gnd_stitch"); b.Add(grp)
def via(x,y):
    v=pcbnew.PCB_VIA(b); v.SetPosition(P(x,y))
    try: v.SetWidth(pcbnew.F_Cu,pcbnew.FromMM(0.6))
    except TypeError: v.SetWidth(pcbnew.FromMM(0.6))
    v.SetDrill(pcbnew.FromMM(0.3)); v.SetNet(gnd); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu)
    b.Add(v); grp.AddItem(v); return v
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
zones={z.GetFirstLayer():z for z in list(b.Zones()) if z.GetNetname()=="GND"}
crt=[]
for f in b.GetFootprints():
    if f.GetSide()!=pcbnew.F_Cu or f.GetReference().startswith("H"): continue
    bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if bb.GetWidth()>0: crt.append(bb)
# rev 4.2: keep stitching vias off the cell-polarity silkscreen marks (silk over a via would be clipped by the mask opening)
MARKBOX=[(mx-0.45*len(t)*sz-0.6, mx+0.45*len(t)*sz+0.6, my-0.6*sz-0.6, my+0.6*sz+0.6) for (t,mx,my,sz,_l) in PLm.POL_MARKS]
def free(x,y,r=0.3+0.35):          # via radius + 0.35 mm margin (> 0.25 mm zone clearance)
    for (a0,a1,b0,b1) in MARKBOX:
        if a0<x<a1 and b0<y<b1: return False
    for a in range(0,360,30):
        q=P(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a)))
        for L,z in zones.items():
            if not z.GetFilledPolysList(L).Contains(q): return False
    c=P(x,y)
    for bb in crt:
        m=pcbnew.FromMM(0.5)
        if bb.GetLeft()-m<c.x<bb.GetRight()+m and bb.GetTop()-m<c.y<bb.GetBottom()+m: return False
    return True
n=0; placed=[]
existing=[(pcbnew.ToMM(t.GetPosition().x)-OX,pcbnew.ToMM(t.GetPosition().y)-OY) for t in b.GetTracks() if t.GetClass()=="PCB_VIA"]
y=1.5
while y<86.0:
    x=1.5
    while x<37.0:
        if free(x,y) and all(math.hypot(x-a,y-c)>1.6 for a,c in existing+placed):
            via(x,y); placed.append((x,y)); n+=1
        x+=2.5
    y+=2.5
# 2b. rev 4.2: second pass on a grid offset by half a pitch, to fill pour areas the first grid missed (the long
#     Q2/Q3 gate traces split some pour regions); same keep-outs and 1.6 mm minimum via spacing
y=2.75
while y<86.0:
    x=2.75
    while x<37.0:
        if free(x,y) and all(math.hypot(x-a,y-c)>1.6 for a,c in existing+placed):
            via(x,y); placed.append((x,y)); n+=1
        x+=2.5
    y+=2.5
# 3. TP4056 EP centre thermal via (EP is GND, full zone connection)
u1=b.FindFootprintByReference("U1"); ep=[p for p in u1.Pads() if p.GetNumber()=="9"][0]
ex,ey=pcbnew.ToMM(ep.GetPosition().x)-OX,pcbnew.ToMM(ep.GetPosition().y)-OY
def _clear_of_tracks(x,y,r=0.3+0.2):
    c=P(x,y)
    return not any(t.GetClass()=="PCB_TRACK" and t.GetNetname()!="GND" and t.HitTest(c,pcbnew.FromMM(r)+t.GetWidth()//2) for t in b.GetTracks())
if all(math.hypot(ex-a,ey-c)>0.5 for a,c in existing) and _clear_of_tracks(ex,ey): via(ex,ey); n+=1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("GND stitching/thermal vias added:",n)
