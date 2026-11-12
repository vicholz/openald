"""Phase 1: build the placed, net-assigned controls board from the schematic netlist (positions from layout.py)."""
import pcbnew,sys,os,math,uuid
import xml.etree.ElementTree as ET
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import design, layout as L
ROOT=os.path.dirname(HERE); PRJ=os.path.join(ROOT,"kicad")+"/"; NAME="openald-feather-controls"
OX,OY=100.0,100.0
XS=[p[0] for p in L.CB_OUTLINE]; YS=[p[1] for p in L.CB_OUTLINE]
X0,Y1=min(XS),max(YS); BOARD_H=Y1-min(YS)
def mm(v): return pcbnew.FromMM(v)
def K(x,y): return pcbnew.VECTOR2I(mm(x-X0+OX),mm(Y1-y+OY))     # case frame -> KiCad
FPLIB="/usr/share/kicad/footprints/"
PL={"SW2":(L.WHEEL[0],L.WHEEL[1],-90), "SW1":(L.SWITCH_PIN_X,L.SWITCH_Y,90), "J1":(L.PAD_X,L.PAD_Y0,180)}
for ref,x,y,_c,_l in L.LEDS: PL[ref]=(x,y,0)
for ref,(x,y) in L.PASSIVES.items(): PL[ref]=(x,y,L.PASSIVE_ROT.get(ref,0))
for i,(x,y) in enumerate(L.CB_HOLES): PL[f"H{i+1}"]=(x,y,0)
def main():
    net_xml="/tmp/"+NAME+".net.xml"
    os.system(f"kicad-cli sch export netlist --format kicadxml -o {net_xml} {PRJ}{NAME}.kicad_sch >/dev/null")
    t=ET.parse(net_xml); pinnet={}
    for n in t.find("nets"):
        nm=n.get("name").lstrip("/")
        for nd in n.findall("node"): pinnet[(nd.get("ref"),nd.get("pin"))]=nm
    board=pcbnew.BOARD(); ds=board.GetDesignSettings(); ds.SetCopperLayerCount(2)
    ds.SetAuxOrigin(pcbnew.VECTOR2I(mm(OX),mm(OY+BOARD_H)))      # drill/place origin = board bottom-left
    nets={}
    def net(name):
        if name not in nets:
            ni=pcbnew.NETINFO_ITEM(board,name); board.Add(ni); nets[name]=ni
        return nets[name]
    pts=L.CB_OUTLINE
    for a,b in zip(pts,pts[1:]+pts[:1]):
        s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(K(*a)); s.SetEnd(K(*b)); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); board.Add(s)
    for p in design.P:
        ref=p["ref"]; lib,name=p["fp"].split(":")
        path=PRJ+"openald_fctl.pretty" if lib=="openald_fctl" else FPLIB+lib+".pretty"
        f=pcbnew.FootprintLoad(path,name); f.SetFPID(pcbnew.LIB_ID(lib,name))
        f.SetReference(ref); f.SetValue(p["val"])
        if not p.get("boardonly"): f.SetPath(pcbnew.KIID_PATH("/"+str(uuid.uuid5(uuid.NAMESPACE_DNS,"sym-"+ref))))
        else: f.SetBoardOnly(True); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
        if p.get("lcsc"):
            f.SetField("LCSC",p["lcsc"]); fl=f.GetFieldByName("LCSC"); fl.SetVisible(False); fl.SetLayer(pcbnew.F_Fab)
        rt=f.Reference(); rt.SetTextSize(pcbnew.VECTOR2I(mm(0.7),mm(0.7))); rt.SetTextThickness(mm(0.12)); rt.SetLayer(pcbnew.F_Fab)
        x,y,rot=PL[ref]; board.Add(f); f.SetOrientationDegrees(rot); f.SetPosition(K(x,y))
        for pad in f.Pads():
            n=pinnet.get((ref,pad.GetNumber()))
            if n: pad.SetNet(net(n))
    def silk(txt,x,y,sz=0.8,ang=0,layer=pcbnew.F_SilkS):
        t=pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(K(x,y)); t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(sz),mm(sz))); t.SetTextThickness(mm(0.13)); t.SetTextAngleDegrees(ang)
        if layer==pcbnew.B_SilkS: t.SetMirrored(True)
        board.Add(t)
    # pad names beside the wire pads (bottom side, readable from below where the wires enter) + top
    for i,n in enumerate(L.PADS):
        silk(n,L.PAD_X+2.6,L.PAD_Y0+i*L.PAD_P,0.6,0,pcbnew.B_SilkS)
    silk("OpenALD",32.5,59.0,0.9,90,pcbnew.B_SilkS); silk("Feather ctl v1.0",34.4,62.5,0.8,90,pcbnew.B_SilkS)
    tb=board.GetTitleBlock(); tb.SetTitle("OpenALD Feather RP2040 v1.0 - controls board"); tb.SetRevision("1.0")
    tb.SetDate("2026-11-11"); tb.SetComment(0,"Thumbwheel + power switch + battery divider + charge-mirror LEDs; wired to an Adafruit Feather RP2040")
    tb.SetComment(1,"Not hardware-validated")
    pcbnew.SaveBoard(PRJ+NAME+".kicad_pcb",board)
    print("saved; footprints:",len(board.GetFootprints()),"nets:",len(nets))
    return board
if __name__=="__main__": main()
