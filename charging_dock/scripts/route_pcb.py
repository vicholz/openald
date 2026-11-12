"""Phase 2: autoroute with Freerouting (Specctra DSN/SES), add GND pours on both layers, fill, save."""
import pcbnew,os,sys,subprocess,math
sys.path.insert(0,os.path.dirname(__file__))
import placement as PLm
PRJ=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/"); PCB=PRJ+"openald-dock.kicad_pcb"
OX,OY=100.0,100.0
def mm(v): return pcbnew.FromMM(v)
board=pcbnew.LoadBoard(PCB)
gnd=board.FindNet("GND")
# GND thermal vias inside the exposed pads (SY8205FCC x2, HUSB238), placed before routing so the router avoids them
def _epvias(ref,offs,drill=0.3,dia=0.6):
    f=board.FindFootprintByReference(ref); c=f.GetPosition()
    for dx,dy in offs:
        v=pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I(c.x+mm(dx),c.y+mm(dy))); v.SetDrill(mm(drill)); v.SetWidth(pcbnew.F_Cu,mm(dia)); v.SetWidth(pcbnew.B_Cu,mm(dia)); v.SetNet(gnd); v.SetLocked(True); board.Add(v)
for u in ("U2","U3"): _epvias(u,[(-0.55,-0.9),(0.55,-0.9),(-0.55,0.0),(0.55,0.0),(-0.55,0.9),(0.55,0.9)])
_epvias("U1",[(0,-0.6),(0,0.6)])
u1=board.FindFootprintByReference("U2")
# temporary keep-out strips along the board edge so the autorouter honours the 0.3 mm copper-to-edge rule
W0,H0=PLm.BOARD_W,PLm.BOARD_H; KO=0.45; kos=[]
for (x0,y0,x1,y1) in ((0,0,W0,KO),(0,H0-KO,W0,H0),(0,0,KO,H0),(W0-KO,0,W0,H0)):
    z=pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowCopperPour(False) if hasattr(z,"SetDoNotAllowCopperPour") else None
    ls=pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
    ol=z.Outline(); ol.NewOutline()
    for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)): ol.Append(mm(x+OX),mm(y+OY))
    board.Add(z); kos.append(z)
# ---- input pre-route (locked): J1 VBUS pairs tied on B.Cu and run to F1; CC1/CC2 as nested U-shapes on F.Cu into
# U1 (HUSB238, pins facing the board interior); fused VBUS_F under J1 on B.Cu to C2/U1 VIN. Board mm, top-left origin.
PRE = {   # net: list of (layer, width, polyline); vias
 "VBUS":   dict(seg=[("F",0.4,[(90.55,8.2),(90.3,9.2)]), ("F",0.4,[(95.45,8.2),(95.6,9.2)]), ("F",0.8,[(83.9,4.4),(83.9,6.2)]),
                     ("B",0.8,[(95.6,9.2),(90.3,9.2),(87.0,9.2),(83.9,6.2)])], vias=[(90.3,9.2),(95.6,9.2),(83.9,6.2)]),
 "CC1":    dict(seg=[("F",0.2,[(94.25,7.9),(94.25,10.2),(102.9,10.2),(102.9,5.55)])], vias=[]),
 "CC2":    dict(seg=[("F",0.2,[(91.25,7.9),(91.25,10.9),(103.4,10.9),(103.4,5.55)])], vias=[]),
 "VBUS_F": dict(seg=[("F",0.8,[(86.7,4.4),(86.7,2.6)]), ("F",0.6,[(98.6,7.0),(99.6,6.175)]), ("F",0.3,[(99.6,6.175),(100.6,6.7),(101.4,6.7),(101.4,5.55)]),
                     ("B",0.8,[(86.7,2.6),(87.7,4.5),(98.6,4.5),(98.6,7.0)])], vias=[(86.7,2.6),(98.6,7.0)]),
}
def _pt(x,y): return pcbnew.VECTOR2I(mm(x+OX),mm(y+OY))
for nn,spec in PRE.items():
    nt=board.FindNet(nn)
    for lay,w,poly in spec["seg"]:
        for a,b2 in zip(poly,poly[1:]):
            t=pcbnew.PCB_TRACK(board); t.SetStart(_pt(*a)); t.SetEnd(_pt(*b2)); t.SetLayer(pcbnew.F_Cu if lay=="F" else pcbnew.B_Cu)
            t.SetNet(nt); t.SetLocked(True); t.SetWidth(mm(w)); board.Add(t)
    for (x,y) in spec["vias"]:
        v=pcbnew.PCB_VIA(board); v.SetPosition(_pt(x,y)); v.SetDrill(mm(0.4)); v.SetWidth(pcbnew.F_Cu,mm(0.8)); v.SetWidth(pcbnew.B_Cu,mm(0.8)); v.SetNet(nt); v.SetLocked(True); board.Add(v)
dsn="/tmp/dock.dsn"; ses="/tmp/dock.ses"
if os.path.exists(ses): os.remove(ses)
pcbnew.ExportSpecctraDSN(board,dsn)
passes=sys.argv[1] if len(sys.argv)>1 else "40"
cmd=[os.environ.get("JAVA","java"),"-Djava.awt.headless=true","-jar",os.environ.get("FREEROUTING",os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"..","tools","freerouting.jar")),"-de",dsn,"-do",ses,"-mp",passes,"--gui.enabled=false"]
print(" ".join(cmd),flush=True); r=subprocess.run(cmd,capture_output=True,text=True,timeout=1500)
open("/tmp/freerouting_dock.log","w").write(r.stdout+r.stderr)
print("\n".join([l for l in (r.stdout+r.stderr).splitlines()][-12:]))
ok=pcbnew.ImportSpecctraSES(board,ses); print("SES import:",ok)
for z in kos: board.Remove(z)
# remove vias that Freerouting left connected on one layer only (KiCad flags them as via_dangling)
def _touch(v,layer):
    p=v.GetPosition(); rad=v.GetWidth(pcbnew.F_Cu)/2
    for t in board.GetTracks():
        if t.GetClass()=="PCB_TRACK" and t.GetLayer()==layer and t.GetNetCode()==v.GetNetCode() and t.HitTest(p,int(rad)): return True
    for f in board.GetFootprints():
        for pd in f.Pads():
            if pd.GetNetCode()==v.GetNetCode() and pd.IsOnLayer(layer) and pd.HitTest(p): return True
    return False
_dang=[v for v in board.GetTracks() if v.GetClass()=="PCB_VIA" and v.GetNetname()!="GND" and not v.IsLocked() and not (_touch(v,pcbnew.F_Cu) and _touch(v,pcbnew.B_Cu))]
for v in _dang: board.Remove(v)
print("removed dangling vias:",len(_dang))
_nst=0
while True:      # dead-end stubs (KiCad connectivity); GND is skipped because it connects through the pours filled below
    board.BuildConnectivity(); cn=board.GetConnectivity()
    st=[t for t in board.GetTracks() if t.GetClass()=="PCB_TRACK" and t.GetNetname()!="GND" and not t.IsLocked() and cn.TestTrackEndpointDangling(t,False)]
    if not st: break
    for t in st: board.Remove(t)
    _nst+=len(st)
print("removed dangling track stubs:",_nst)

ep=u1.GetPosition()
for t in board.GetTracks():
    if t.GetClass()!="PCB_VIA": continue
    p=t.GetPosition()
    w=pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))
    t.SetDrill(mm(0.5 if w>=0.95 else 0.4 if w>=0.75 else 0.3))   # SES import assigns the netclass drill; restore the routed padstack drill
for t in board.GetTracks():                 # Freerouting pin neck-down can drop below the 0.15 mm board minimum
    if t.GetClass()=="PCB_TRACK" and t.GetWidth()<mm(0.15): t.SetWidth(mm(0.15))
W,H=PLm.BOARD_W,PLm.BOARD_H
def zone(layer):
    z=pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(gnd)
    ol=z.Outline(); ol.NewOutline()
    for (x,y) in ((0,0),(W,0),(W,H),(0,H)): ol.Append(mm(x+OX),mm(y+OY))
    z.SetLocalClearance(mm(0.25)); z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetAssignedPriority(0); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    board.Add(z); return z
zone(pcbnew.F_Cu); zone(pcbnew.B_Cu)
for fpx in board.GetFootprints():          # THT GND pins: solid zone connection (avoids starved thermals on tiny islands)
    for pad in fpx.Pads():
        if pad.GetNetname()=="GND" and pad.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        if pad.GetNetname()=="GND" and fpx.GetReference() in ("U1","U2","U3"): pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)   # MCU GND pin: tracks crowd its thermal spokes
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB,board)
print("tracks:",len([t for t in board.GetTracks() if t.GetClass()=="PCB_TRACK"]),"vias:",len([t for t in board.GetTracks() if t.GetClass()=="PCB_VIA"]))
