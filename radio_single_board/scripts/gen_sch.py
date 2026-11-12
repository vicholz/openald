"""Generate the KiCad schematic (openald.kicad_sch) from design.py.
Every pin gets a short wire stub and a net label, so connectivity is explicit and ERC-checkable."""
import os,uuid,math,copy
from sexp import dump,Sym,find,find1
import symlib,design
PRJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/kicad/"
EXTRA={"openald":PRJ+"openald.kicad_sym"}
ROOT=str(uuid.uuid5(uuid.NAMESPACE_DNS,"openald-root"))
def U(seed=None): return str(uuid.uuid5(uuid.NAMESPACE_DNS,seed)) if seed else str(uuid.uuid4())
S=Sym
G=2.54
def snap(v): return round(v/1.27)*1.27
GROUPS=[("usb","USB-C input (power + USB 2.0 data, CC 5.1k pull-downs)",(15,25,135)),
        ("chg","TP4056 Li-ion charger (~900 mA) + charge LEDs",(15,105,135)),
        ("bat","18650 + reverse-polarity FETs (Q2/Q3) + DW01A / FS8205A protection",(155,25,125)),
        ("pwr","Power switch, wheel-press power FET (Q4), radio 3.3 V LDO (+3V3R), battery ADC",(155,105,125)),
        ("mcu","ATmega328PB MCU (internal 8 MHz) + AVR ISP pogo pads",(15,185,150)),
        ("ui","Battery level bar (3x LED) + thumbwheel encoder",(170,185,120)),
        ("fm","RRD-102 (RDA5807M) FM module, headphone out, headphone-ground antenna",(295,25,115)),
        ("ser","USB serial: CH340K (VBUS only) + ESD + auto-reset; MCU-only 3.3 V rail",(295,112,115)),
        ("flags","Power flags (ERC)",(170,262,120))]
lib_syms={}
items=[]
def label_w(t): return len(t)*1.0+3.5
def place_symbol(p,X,Y):
    lid=p["lib"]
    if lid not in lib_syms:
        s=symlib.get_symbol(lid,EXTRA); s=copy.deepcopy(s); s[1]=lid
        # drop lib-level property ids not needed
        lib_syms[lid]=s
    sym=lib_syms[lid]
    pins=symlib.pins(sym)
    props={pr[1]:pr for pr in find(sym,"property")}
    ref=p["ref"]
    e=[S("symbol"),[S("lib_id"),lid],[S("at"),X,Y,0],[S("unit"),1],[S("exclude_from_sim"),S("no")],
       [S("in_bom"),S("no") if p.get("nobom") else S("yes")],[S("on_board"),S("yes")],[S("dnp"),S("yes") if p.get("dnp") else S("no")],
       [S("uuid"),U("sym-"+ref)]]
    ys=[pp["y"] for pp in pins] or [0]
    top=Y-max(ys)-3; bot=Y-min(ys)+3
    def prop(k,v,x,y,hide=False,just=None):
        eff=[S("effects"),[S("font"),[S("size"),1.27,1.27]]]
        if just: eff.append([S("justify"),S(just)])
        if hide: eff.append([S("hide"),S("yes")])
        return [S("property"),k,v,[S("at"),x,y,0],eff]
    e.append(prop("Reference",ref,X,top-1.27))
    e.append(prop("Value",p["val"],X,bot+1.27))
    e.append(prop("Footprint",p["fp"],X,Y,True))
    e.append(prop("Datasheet",props["Datasheet"][2] if "Datasheet" in props else "~",X,Y,True))
    e.append(prop("LCSC",p.get("lcsc",""),X,Y,True))
    e.append(prop("MPN",p.get("mpn",""),X,Y,True))
    for pp in pins: e.append([S("pin"),pp["num"],[S("uuid"),U("pin-"+ref+"-"+pp["num"])]])
    e.append([S("instances"),[S("project"),"openald",[S("path"),"/"+ROOT,[S("reference"),ref],[S("unit"),1]]]])
    items.append(e)
    # stubs + labels
    for pp in pins:
        tx=X+pp["x"]; ty=Y-pp["y"]
        a=math.radians(pp["ang"])
        dx=-round(math.cos(a)); dy=round(math.sin(a))
        net=p["pins"].get(pp["num"],"__missing__")
        if net=="__missing__": raise SystemExit(f"{ref} pin {pp['num']} not in design")
        if net is None:
            items.append([S("no_connect"),[S("at"),tx,ty],[S("uuid"),U("nc-"+ref+pp["num"])]])
            continue
        ex=tx+dx*G; ey=ty+dy*G
        items.append([S("wire"),[S("pts"),[S("xy"),tx,ty],[S("xy"),ex,ey]],[S("stroke"),[S("width"),0],[S("type"),S("default")]],[S("uuid"),U("w-"+ref+pp["num"])]])
        ang={(1,0):0,(-1,0):180,(0,-1):90,(0,1):270}[(dx,dy)]
        just={0:"left",180:"right",90:"left",270:"right"}[ang]
        items.append([S("global_label"),net,[S("shape"),S("passive")],[S("at"),ex,ey,ang],[S("fields_autoplaced"),S("yes")],
                      [S("effects"),[S("font"),[S("size"),1.27,1.27]],[S("justify"),S(just)]],[S("uuid"),U("l-"+ref+pp["num"])],
                      [S("property"),"Intersheetrefs","${INTERSHEET_REFS}",[S("at"),ex,ey,0],[S("effects"),[S("font"),[S("size"),1.27,1.27]],[S("hide"),S("yes")]]]])
def extents(p):
    lid=p["lib"]; s=symlib.get_symbol(lid,EXTRA); pins=symlib.pins(s)
    L=R=T=B=0
    for pp in pins:
        a=math.radians(pp["ang"]); dx=-round(math.cos(a)); dy=round(math.sin(a))
        net=p["pins"].get(pp["num"]) or ""
        ex=pp["x"]+dx*(G+label_w(net)); ey=-pp["y"]+dy*(G+label_w(net))
        L=min(L,ex,pp["x"]-3);R=max(R,ex,pp["x"]+3);T=min(T,ey,-pp["y"]-4);B=max(B,ey,-pp["y"]+4)
    return L,R,T-2.5,B+2.5
# power flags
flags=[dict(ref=f"#FLG0{i+1}",lib="power:PWR_FLAG",val="PWR_FLAG",fp="",lcsc="",mpn="",pins={"1":n},grp="flags",nobom=True)
       for i,n in enumerate(["GND","VBUS","VSYS","DW_VCC","BATN","FM_VDD","VMCU"])]
allp=[q for q in design.P if q["grp"]!="mech"]+flags
for g,title,(gx,gy,gw) in GROUPS:
    items.append([S("text"),title,[S("exclude_from_sim"),S("no")],[S("at"),gx,gy-6,0],[S("effects"),[S("font"),[S("size"),2,2],[S("bold"),S("yes")]],[S("justify"),S("left")]],[S("uuid"),U("t-"+g)]])
    x=gx; y=gy; rowh=0; x0=gx
    for i,p in enumerate([q for q in allp if q["grp"]==g]):
        L,R,T,B=extents(p)
        w=R-L; h=B-T
        if x+w>gx+gw and x>x0:
            x=x0; y+=rowh+3; rowh=0
        X=snap(x-L); Y=snap(y-T)
        place_symbol(p,X,Y)
        x+=w+4
        if i==0 and h>60: x0=x      # a tall first symbol (the MCU) gets its own column; the rest wrap beside it
        else: rowh=max(rowh,h)
sch=[S("kicad_sch"),[S("version"),20231120],[S("generator"),"eeschema"],[S("generator_version"),"8.0"],[S("uuid"),ROOT],[S("paper"),"A3"],
     [S("title_block"),[S("title"),"OpenALD v1.0 - ATmega328PB + CH340K + RDA5807M, 18650, USB-C"],[S("date"),"2026-11-11"],[S("rev"),"1.0"],
      [S("comment"),1,"Generated from scripts/design.py - every pin is labelled with its net name"],
      [S("comment"),2,"ATmega328PB TQFP-32 (DS40001906): pin 3 PE0=GND, pin 6 PE1=+3V3 (328P-AU fits too)"]],
     [S("lib_symbols")]+list(lib_syms.values())]+items+[[S("sheet_instances"),[S("path"),"/",[S("page"),"1"]]]]
open(PRJ+"openald.kicad_sch","w").write(dump(sch)+"\n")
print("symbols:",len([i for i in items if i[0]=="symbol"]),"labels:",len([i for i in items if i[0]=="global_label"]))
