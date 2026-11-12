"""Phase 2: autoroute with Freerouting (Specctra DSN/SES), add GND pours on both layers, fill, save."""
import pcbnew,os,sys,subprocess,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import layout as L
from build_pcb import K,mm,PRJ,NAME
PCB=PRJ+NAME+".kicad_pcb"
JAVA=os.environ.get("JAVA","java"); FR=os.environ.get("FREEROUTING",os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"..","tools","freerouting.jar"))
board=pcbnew.LoadBoard(PCB); gnd=board.FindNet("GND")
pts=L.CB_OUTLINE; KO=0.4; kos=[]
for a,b in zip(pts,pts[1:]+pts[:1]):          # keep-out strip along each edge (router honours copper-to-edge rule)
    dx,dy=b[0]-a[0],b[1]-a[1]; l=math.hypot(dx,dy); nx,ny=-dy/l*KO,dx/l*KO
    z=pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    ls=pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
    ol=z.Outline(); ol.NewOutline()
    for (x,y) in ((a[0]-nx,a[1]-ny),(b[0]-nx,b[1]-ny),(b[0]+nx,b[1]+ny),(a[0]+nx,a[1]+ny)):
        p=K(x,y); ol.Append(p.x,p.y)
    board.Add(z); kos.append(z)
dsn="/tmp/fctl.dsn"; ses="/tmp/fctl.ses"
if os.path.exists(ses): os.remove(ses)
pcbnew.ExportSpecctraDSN(board,dsn)
passes=sys.argv[1] if len(sys.argv)>1 else "30"
r=subprocess.run([JAVA,"-Djava.awt.headless=true","-jar",FR,"-de",dsn,"-do",ses,"-mp",passes,"--gui.enabled=false"],capture_output=True,text=True,timeout=1200)
open("/tmp/fctl_freerouting.log","w").write(r.stdout+r.stderr)
print("SES import:",pcbnew.ImportSpecctraSES(board,ses))
for z in kos: board.Remove(z)
_nst=0
while True:
    board.BuildConnectivity(); cn=board.GetConnectivity()
    st=[t for t in board.GetTracks() if t.GetClass()=="PCB_TRACK" and t.GetNetname()!="GND" and cn.TestTrackEndpointDangling(t,False)]
    if not st: break
    for t in st: board.Remove(t)
    _nst+=len(st)
print("removed dangling stubs:",_nst)
for t in board.GetTracks():
    if t.GetClass()=="PCB_VIA": t.SetDrill(mm(0.3))
    elif t.GetWidth()<mm(0.15): t.SetWidth(mm(0.15))
def zone(layer):
    z=pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(gnd)
    ol=z.Outline(); ol.NewOutline()
    for (x,y) in pts: p=K(x,y); ol.Append(p.x,p.y)
    z.SetLocalClearance(mm(0.25)); z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL); z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS); board.Add(z)
zone(pcbnew.F_Cu); zone(pcbnew.B_Cu)
for f in board.GetFootprints():
    for pad in f.Pads():
        if pad.GetNetname()=="GND" and pad.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(PCB,board)
print("tracks:",len([t for t in board.GetTracks() if t.GetClass()=="PCB_TRACK"]),"vias:",len([t for t in board.GetTracks() if t.GetClass()=="PCB_VIA"]))
