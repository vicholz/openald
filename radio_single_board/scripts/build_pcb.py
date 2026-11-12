"""Phase 1: build the placed, net-assigned board from the schematic netlist."""
import pcbnew,sys,os,json,math
import xml.etree.ElementTree as ET
sys.path.insert(0,os.path.dirname(__file__))
import design,placement as PLm
PRJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/kicad/"
OX,OY=100.0,100.0
FPLIB="/usr/share/kicad/footprints/"
def mm(v): return pcbnew.FromMM(v)
def P(x,y): return pcbnew.VECTOR2I(mm(x+OX),mm(y+OY))
os.system(f"kicad-cli sch export netlist --format kicadxml -o /tmp/openald.net.xml {PRJ}openald.kicad_sch >/dev/null")
t=ET.parse("/tmp/openald.net.xml")
comps={c.get("ref"):c for c in t.find("components")}
pinnet={}
for n in t.find("nets"):
    nm=n.get("name").lstrip("/")
    if nm.startswith("unconnected-"): nm=nm.replace("/","{slash}")   # KiCad escapes '/' in net names (e.g. XTAL1/PB6)
    for nd in n.findall("node"): pinnet[(nd.get("ref"),nd.get("pin"))]=nm
board=pcbnew.BOARD()
board.GetDesignSettings().SetCopperLayerCount(2)
board.GetDesignSettings().SetAuxOrigin(pcbnew.VECTOR2I(pcbnew.FromMM(100.0),pcbnew.FromMM(100.0+PLm.BOARD_H)))  # drill/place origin = board bottom-left corner
nets={}
def net(name):
    if name not in nets:
        ni=pcbnew.NETINFO_ITEM(board,name); board.Add(ni); nets[name]=ni
    return nets[name]
# outline: rounded rectangle
W,H,R=PLm.BOARD_W,PLm.BOARD_H,PLm.CORNER_R
def seg(a,b):
    s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(*a)); s.SetEnd(P(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
def arc(c,start,mid,end):
    s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*start),P(*mid),P(*end)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
k=R*(1-math.cos(math.pi/4))
seg((R,0),(W-R,0)); seg((W,R),(W,H-R)); seg((W-R,H),(R,H)); seg((0,H-R),(0,R))
arc((W-R,R),(W-R,0),(W-k,k),(W,R)); arc((W-R,H-R),(W,H-R),(W-k,H-k),(W-R,H))
arc((R,H-R),(R,H),(k,H-k),(0,H-R)); arc((R,R),(0,R),(k,k),(R,0))
def load(fpid):
    lib,name=fpid.split(":")
    path=PRJ+"openald.pretty" if lib=="openald" else FPLIB+lib+".pretty"
    f=pcbnew.FootprintLoad(path,name)
    f.SetFPID(pcbnew.LIB_ID(lib,name))
    return f
for p in design.P:
    ref=p["ref"]
    f=load(p["fp"])
    f.SetReference(ref); f.SetValue(p["val"])
    import uuid as _u; tstamp=str(_u.uuid5(_u.NAMESPACE_DNS,"sym-"+ref))
    f.SetPath(pcbnew.KIID_PATH("/"+tstamp))
    if p.get("lcsc"):
        f.SetField("LCSC",p["lcsc"]); fld=f.GetFieldByName("LCSC"); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
    f.SetField("MPN",p.get("mpn","")); f.GetFieldByName("MPN").SetVisible(False); f.GetFieldByName("MPN").SetLayer(pcbnew.F_Fab)
    rt=f.Reference(); rt.SetTextSize(pcbnew.VECTOR2I(mm(0.8),mm(0.8))); rt.SetTextThickness(mm(0.12))
    MODELS={"J2":"PJ-320D-4A","J1":"USB_C_HRO_31-M-12"}
    if ref in MODELS:
        m=pcbnew.FP_3DMODEL(); m.m_Filename="${KIPRJMOD}/openald.3dshapes/"+MODELS[ref]+".wrl"; f.Models().clear(); f.Models().append(m)
    if ref=="BT1":
        m=pcbnew.FP_3DMODEL(); m.m_Filename="${KICAD9_3DMODEL_DIR}/Battery.3dshapes/BatteryHolder_MPD_BH-18650-PC2.wrl"; f.Models().clear(); f.Models().append(m)
    if p.get("dnp"): f.SetDNP(True)
    if p.get("nobom"): f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    if p.get("boardonly"): f.SetBoardOnly(True)
    board.Add(f)
    if ref=="BT1":
        f.Flip(f.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT) if hasattr(pcbnew,"FLIP_DIRECTION_LEFT_RIGHT") else f.Flip(f.GetPosition(),False)
        tx1,ty1=PLm.BT1_PAD1; tx2,ty2=PLm.BT1_PAD2
        best=None
        for ang in (0,90,180,270):
            f.SetOrientationDegrees(ang); f.SetPosition(pcbnew.VECTOR2I(0,0))
            p1=[q for q in f.Pads() if q.GetNumber()=="1"][0].GetPosition(); p2=[q for q in f.Pads() if q.GetNumber()=="2"][0].GetPosition()
            d=(pcbnew.ToMM(p2.x-p1.x),pcbnew.ToMM(p2.y-p1.y))
            if abs(d[0]-(tx2-tx1))<0.01 and abs(d[1]-(ty2-ty1))<0.01: best=(ang,p1); break
        ang,p1=best; f.SetOrientationDegrees(ang)
        f.SetPosition(pcbnew.VECTOR2I(mm(tx1+OX)-p1.x, mm(ty1+OY)-p1.y))
    else:
        x,y,rot=PLm.PL[ref]
        f.SetOrientationDegrees(rot); f.SetPosition(P(x,y))
    for pad in f.Pads():
        num=pad.GetNumber()
        if not num or num=="MP": continue
        n=pinnet.get((ref,num))
        if n and not n.startswith("unconnected-"): pad.SetNet(net(n))
        elif n: pad.SetNet(net(n))
# Q4 sits against the jack-end edge: put its reference below the part instead of clipped by the board edge
_q4=board.FindFootprintByReference("Q4"); _q4.Reference().SetPosition(P(31.9,5.0)) if _q4 else None
# power-switch position labels (SK-12E12: knob toward pin 3 joins 2-3 = VBAT->VSYS = ON)
def silk(txt,x,y,sz=0.9,ang=0):
    t=pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x,y)); t.SetLayer(pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(sz),mm(sz))); t.SetTextThickness(mm(0.15)); t.SetTextAngleDegrees(ang); board.Add(t)
_sw=board.FindFootprintByReference("SW1"); _p={q.GetNumber():q.GetPosition() for q in _sw.Pads() if q.GetNumber()}
_on_up = _p["3"].y < _p["1"].y
_sy=pcbnew.ToMM(_sw.GetPosition().y)-OY; _top=_sy-7.6; _bot=_sy+7.6
silk("ON",33.6,_top if _on_up else _bot); silk("OFF",33.6,_bot if _on_up else _top)
# silkscreen title
tx=pcbnew.PCB_TEXT(board); tx.SetText("OpenALD v1.0"); tx.SetPosition(P(19,61.5)); tx.SetLayer(pcbnew.F_SilkS)
tx.SetTextSize(pcbnew.VECTOR2I(mm(1.0),mm(1.0))); tx.SetTextThickness(mm(0.15)); board.Add(tx)
tb=pcbnew.PCB_TEXT(board); tb.SetText("18650  + end <- USB side"); tb.SetPosition(P(19,40)); tb.SetLayer(pcbnew.B_SilkS)
tb.SetTextSize(pcbnew.VECTOR2I(mm(1.2),mm(1.2))); tb.SetTextThickness(mm(0.18)); tb.SetMirrored(True); tb.SetTextAngleDegrees(90); board.Add(tb)
# rev 4.2: large cell-polarity marks. Bottom (battery side, mirrored): in the free strips left and right of the holder at
# both ends, readable with the holder fitted. Top: next to the holder's + (pin 1) and - (pin 2) solder pads.
# POL_MARKS is also read by stitch_gnd.py, which keeps its stitching vias out of these boxes.
for (txt,x,y,sz,layer) in PLm.POL_MARKS:
    t=pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x,y)); t.SetLayer(pcbnew.B_SilkS if layer=="B" else pcbnew.F_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(mm(sz),mm(sz))); t.SetTextThickness(mm(max(0.15,sz*0.16)))
    if layer=="B": t.SetMirrored(True)
    board.Add(t)
pcbnew.SaveBoard(PRJ+"openald.kicad_pcb",board)
print("saved; footprints:",len(board.GetFootprints()),"nets:",len(nets))
for ref in ("BT1","J2","SW3","SW1","J1","D1","D5","D6","Q4"):
    f=board.FindFootprintByReference(ref)
    print(ref,[(q.GetNumber(),round(pcbnew.ToMM(q.GetPosition().x)-OX,2),round(pcbnew.ToMM(q.GetPosition().y)-OY,2)) for q in f.Pads() if q.GetNumber() not in ("","MP")][:6])
