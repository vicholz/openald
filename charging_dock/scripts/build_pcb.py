"""Phase 1: build the placed, net-assigned dock board from the schematic netlist."""
import pcbnew,sys,os,math,uuid
import xml.etree.ElementTree as ET
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import design,placement as PLm
PRJ=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/")
OX,OY=100.0,100.0
FPLIB="/usr/share/kicad/footprints/"
def mm(v): return pcbnew.FromMM(v)
def P(x,y): return pcbnew.VECTOR2I(mm(x+OX),mm(y+OY))
os.system(f"kicad-cli sch export netlist --format kicadxml -o /tmp/openald-dock.net.xml {PRJ}openald-dock.kicad_sch >/dev/null")
t=ET.parse("/tmp/openald-dock.net.xml")
pinnet={}
for n in t.find("nets"):
    nm=n.get("name").lstrip("/")
    for nd in n.findall("node"): pinnet[(nd.get("ref"),nd.get("pin"))]=nm
board=pcbnew.BOARD()
board.GetDesignSettings().SetCopperLayerCount(2)
board.GetDesignSettings().SetAuxOrigin(pcbnew.VECTOR2I(mm(OX),mm(OY+PLm.BOARD_H)))   # drill/place origin = board bottom-left (front-left)
nets={}
def net(name):
    if name not in nets:
        ni=pcbnew.NETINFO_ITEM(board,name); board.Add(ni); nets[name]=ni
    return nets[name]
W,H,R=PLm.BOARD_W,PLm.BOARD_H,PLm.CORNER_R
def seg(a,b):
    s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
def arc(start,mid,end):
    s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*start),P(*mid),P(*end)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
k=R*(1-math.cos(math.pi/4))
seg((R,0),(W-R,0)); seg((W,R),(W,H-R)); seg((W-R,H),(R,H)); seg((0,H-R),(0,R))
arc((W-R,0),(W-k,k),(W,R)); arc((W,H-R),(W-k,H-k),(W-R,H)); arc((R,H),(k,H-k),(0,H-R)); arc((0,R),(k,k),(R,0))
def load(fpid):
    lib,name=fpid.split(":")
    path=PRJ+"openald.pretty" if lib=="openald" else FPLIB+lib+".pretty"
    f=pcbnew.FootprintLoad(path,name); f.SetFPID(pcbnew.LIB_ID(lib,name)); return f
for p in design.P:
    ref=p["ref"]; f=load(p["fp"])
    f.SetReference(ref); f.SetValue(p["val"])
    f.SetPath(pcbnew.KIID_PATH("/"+str(uuid.uuid5(uuid.NAMESPACE_DNS,"sym-"+ref))))
    if p.get("lcsc"):
        f.SetField("LCSC",p["lcsc"]); fld=f.GetFieldByName("LCSC"); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
    f.SetField("MPN",p.get("mpn","")); f.GetFieldByName("MPN").SetVisible(False); f.GetFieldByName("MPN").SetLayer(pcbnew.F_Fab)
    rt=f.Reference(); rt.SetTextSize(pcbnew.VECTOR2I(mm(0.8),mm(0.8))); rt.SetTextThickness(mm(0.12))
    if ref=="J1":
        m=pcbnew.FP_3DMODEL(); m.m_Filename="${KIPRJMOD}/openald.3dshapes/USB_C_HRO_31-M-12.wrl"; f.Models().clear(); f.Models().append(m)
    if p.get("nobom"): f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    if p.get("boardonly"): f.SetBoardOnly(True)
    board.Add(f)
    x,y,rot=PLm.PL[ref]; f.SetOrientationDegrees(rot); f.SetPosition(P(x,y))
    for pad in f.Pads():
        num=pad.GetNumber()
        if not num: continue
        n=pinnet.get((ref,num))
        if n: pad.SetNet(net(n))
def silk(txt,x,y,sz=0.9,ang=0,layer=pcbnew.F_SilkS):
    t=pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x,y)); t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(sz),mm(sz))); t.SetTextThickness(mm(max(0.15,sz*0.15))); t.SetTextAngleDegrees(ang)
    if layer==pcbnew.B_SilkS: t.SetMirrored(True)
    board.Add(t)
for (txt,x,y,sz) in PLm.SILK: silk(txt,x,y,sz)
for n,(px,py) in PLm.PLUG.items(): silk(f"SLOT {n}",px,py+(-4.2 if py>60 else 4.2),1.2)
# pocket footprints on the fab layer (where the printed floor pads sit: no parts allowed)
for (x0,y0,x1,y1) in PLm.KEEPOUT:
    for a,b in (((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))):
        s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*b)); s.SetLayer(pcbnew.User_2); s.SetWidth(mm(0.15)); board.Add(s)
pcbnew.SaveBoard(PRJ+"openald-dock.kicad_pcb",board)
print("saved; footprints:",len(board.GetFootprints()),"nets:",len(nets))
# placement sanity: courtyards vs pocket keep-outs and vs each other
bad=0; crt={}
for f in board.GetFootprints():
    r=f.GetReference()
    if r.startswith("H"): continue
    bb=f.GetCourtyard(pcbnew.F_CrtYd).BBox()
    x0,y0,x1,y1=[pcbnew.ToMM(v) for v in (bb.GetLeft()-mm(OX),bb.GetTop()-mm(OY),bb.GetRight()-mm(OX),bb.GetBottom()-mm(OY))]
    crt[r]=(x0,y0,x1,y1)
    if r.startswith("J"): continue      # plugs belong in the pockets; J1 pads reach 0.9 mm under the slot-5 pad rim (relieved in the case)
    for (a0,b0,a1,b1) in PLm.KEEPOUT:
        if x0<a1 and x1>a0 and y0<b1 and y1>b0: print("IN POCKET:",r,(round(x0,2),round(y0,2),round(x1,2),round(y1,2))); bad+=1
    if x0<0.3 or y0<0 or x1>W-0.3 or y1>H: print("EDGE:",r)
print("pocket keep-out violations:",bad)
