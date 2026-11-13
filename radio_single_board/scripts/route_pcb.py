"""Phase 2: autoroute with Freerouting (Specctra DSN/SES), add GND pours on both layers, fill, save."""
import pcbnew,os,sys,subprocess,math
sys.path.insert(0,os.path.dirname(__file__))
import placement as PLm
PRJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/kicad/"; PCB=PRJ+"openald.kicad_pcb"
OX,OY=100.0,100.0
def mm(v): return pcbnew.FromMM(v)
board=pcbnew.LoadBoard(PCB)
gnd=board.FindNet("GND")
# GND vias inside the TP4056 exposed pad (heat path to bottom pour), placed before routing
u1=board.FindFootprintByReference("U1"); c=u1.GetPosition()
for dx,dy in ((0,-0.85),(0,0.0),(0,0.85)):   # rev 4.2: centre via placed here too, so the router keeps tracks out from under it
    v=pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I(c.x+mm(dx),c.y+mm(dy))); v.SetDrill(mm(0.3)); v.SetWidth(pcbnew.F_Cu,mm(0.6)); v.SetWidth(pcbnew.B_Cu,mm(0.6)); v.SetNet(gnd); board.Add(v)
# temporary keep-out strips along the board edge so the autorouter honours the 0.3 mm copper-to-edge rule
W0,H0=PLm.BOARD_W,PLm.BOARD_H; KO=0.45; kos=[]
for (x0,y0,x1,y1) in ((0,0,W0,KO),(0,H0-KO,W0,H0),(0,0,KO,H0),(W0-KO,0,W0,H0)):
    z=pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False); z.SetDoNotAllowCopperPour(False) if hasattr(z,"SetDoNotAllowCopperPour") else None
    ls=pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
    ol=z.Outline(); ol.NewOutline()
    for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)): ol.Append(mm(x+OX),mm(y+OY))
    board.Add(z); kos.append(z)
# ---- USB D+/D- pre-route (locked, so Freerouting keeps it): both USB-C orientations tied right at the connector,
# then a short coupled pair on the bottom layer to the CH340K. Coordinates in board mm (top-left origin, Y down).
# 2026-11-12: J1 moved 0.9 mm toward the USB edge (pads now centred at y 80.205): the J1-side fan-out moved with it.
USB_PREROUTE = {
 "USB_DP": dict(top=[[(18.75,79.50),(18.75,79.05),(19.75,79.05),(19.75,79.50)], [(19.25,79.05),(19.25,78.50)],
                     [(27.40,78.00),(27.40,77.20)], [(25.46,79.65),(27.74,79.65)], [(27.40,79.65),(27.40,78.00)]],   # + USBLC6 I/O1 (pins 1-6)
                bot=[[(19.25,78.50),(19.75,78.00),(27.40,78.00)]], vias=[(19.25,78.50),(27.40,78.00)]),
 "USB_DN": dict(top=[[(19.25,80.93),(19.25,81.40),(18.25,81.40),(18.25,80.93)], [(18.75,81.40),(18.75,81.85)],
                     [(28.40,78.80),(28.40,77.20)], [(25.46,81.55),(29.00,81.55)]],                              # + USBLC6 I/O2 (pins 3-4)
                bot=[[(18.75,81.85),(21.80,78.80),(28.40,78.80)], [(28.40,78.80),(29.00,79.40),(29.00,81.55)]],
                vias=[(18.75,81.85),(28.40,78.80),(29.00,81.55)]),
}
def _pt(x,y): return pcbnew.VECTOR2I(mm(x+OX),mm(y+OY))
for nn,spec in USB_PREROUTE.items():
    nt=board.FindNet(nn)
    for layer,key in ((pcbnew.F_Cu,"top"),(pcbnew.B_Cu,"bot")):
        for poly in spec[key]:
            for a,b2 in zip(poly,poly[1:]):
                t=pcbnew.PCB_TRACK(board); t.SetStart(_pt(*a)); t.SetEnd(_pt(*b2)); t.SetWidth(mm(0.2)); t.SetLayer(layer); t.SetNet(nt); t.SetLocked(True); board.Add(t)
    for (x,y) in spec["vias"]:
        v=pcbnew.PCB_VIA(board); v.SetPosition(_pt(x,y)); v.SetDrill(mm(0.3)); v.SetWidth(pcbnew.F_Cu,mm(0.6)); v.SetWidth(pcbnew.B_Cu,mm(0.6)); v.SetNet(nt); v.SetLocked(True); board.Add(v)
dsn="/tmp/fm.dsn"; ses="/tmp/fm.ses"
if os.path.exists(ses): os.remove(ses)
pcbnew.ExportSpecctraDSN(board,dsn)
passes=sys.argv[1] if len(sys.argv)>1 else "40"
cmd=[os.environ.get("JAVA","java"),"-Djava.awt.headless=true","-jar",os.environ.get("FREEROUTING",os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"..","tools","freerouting.jar")),"-de",dsn,"-do",ses,"-mp",passes,"--gui.enabled=false"]
print(" ".join(cmd),flush=True); r=subprocess.run(cmd,capture_output=True,text=True,timeout=1500)
open("/tmp/freerouting.log","w").write(r.stdout+r.stderr)
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
POWER={"GND","VBUS","VBAT","BATN","BAT_P","Q_D","VSYS","+3V3","+3V3R","VMCU"}
ep=u1.GetPosition()
for t in board.GetTracks():
    if t.GetClass()!="PCB_VIA": continue
    p=t.GetPosition()
    w=pcbnew.ToMM(t.GetWidth(pcbnew.F_Cu))
    t.SetDrill(mm(0.4 if w>=0.75 else 0.3))   # SES import assigns the netclass drill; restore the routed padstack drill
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
        if pad.GetNetname()=="GND" and fpx.GetReference() in ("U3","U7","C15","C16"): pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)   # MCU GND pin: tracks crowd its thermal spokes
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB,board)
# KiCad 9 library has no EP2.41x3.3 SOIC-8 3D model: point U1 at the same-body EP2.41x3.81 model (3D view / fit check only)
# KiCad 9.0.2 CH340K footprint points at "...P1mm..." but the shipped model is "...P1.0mm..." (U7)
_t=open(PCB).read(); open(PCB,"w").write(_t.replace("EP2.41x3.3mm.step","EP2.41x3.81mm.step").replace("SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm.step","SSOP-10-1EP_3.9x4.9mm_P1.0mm_EP2.1x3.3mm.step"))
print("tracks:",len([t for t in board.GetTracks() if t.GetClass()=="PCB_TRACK"]),"vias:",len([t for t in board.GetTracks() if t.GetClass()=="PCB_VIA"]))
