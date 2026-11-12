"""Generate the KiCad schematic (openald.kicad_sch) from design.py.
Every pin gets a short wire stub and a net label, so connectivity is explicit and ERC-checkable."""
import uuid,math,copy
from sexp import dump,Sym,find,find1
import symlib,design
import os
PRJ=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/")
EXTRA={"openald":PRJ+"openald.kicad_sym"}
ROOT=str(uuid.uuid5(uuid.NAMESPACE_DNS,"openald-dock-root"))
def U(seed=None): return str(uuid.uuid5(uuid.NAMESPACE_DNS,seed)) if seed else str(uuid.uuid4())
S=Sym
G=2.54
def snap(v): return round(v/1.27)*1.27
GROUPS=[("in","USB-C PD input: fuse, TVS, HUSB238 PD sink (20 V / 2.25 A request), AO4407A input switch",(15,25,190)),
        ("buckA","Buck A: SY8205FCC 5.10 V / 5 A -> slots 1, 2, 4 (EN >= ~12 V)",(15,110,190)),
        ("buckB","Buck B: SY8205FCC 5.10 V / 5 A -> slots 3, 5, 6 (EN >= ~12 V)",(215,25,190)),
        ("led","Status LED: green = 5 V up, red = input present but no usable PD",(215,110,190)),
        ("slot1","Slot 1",(15,190,125)),("slot2","Slot 2",(145,190,125)),("slot3","Slot 3",(275,190,125)),
        ("slot4","Slot 4",(15,245,125)),("slot5","Slot 5",(145,245,125)),("slot6","Slot 6",(275,245,125)),
        ("flags","Power flags (ERC)",(215,160,190))]
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
    e.append([S("instances"),[S("project"),"openald-dock",[S("path"),"/"+ROOT,[S("reference"),ref],[S("unit"),1]]]])
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
       for i,n in enumerate(["GND","VBUS","VBUS_F","VIN_SW","5V_A","5V_B"])]
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
sch=[S("kicad_sch"),[S("version"),20231120],[S("generator"),"eeschema"],[S("generator_version"),"8.0"],[S("uuid"),ROOT],[S("paper"),"A2"],
     [S("title_block"),[S("title"),"OpenALD Dock v1.0 - 6-slot USB-C charging dock (PD 20 V in, 2x 5.1 V buck, per-slot 1.45 A limit)"],[S("date"),"2026-11-11"],[S("rev"),"1.0"],
      [S("comment"),1,"Generated from scripts/design.py - every pin is labelled with its net name"],
      [S("comment"),2,"Minimum charger: USB-C PD 45 W (20 V >= 2.25 A or 15 V >= 3 A). Not hardware-validated."]],
     [S("lib_symbols")]+list(lib_syms.values())]+items+[[S("sheet_instances"),[S("path"),"/",[S("page"),"1"]]]]
open(PRJ+"openald-dock.kicad_sch","w").write(dump(sch)+"\n")
print("symbols:",len([i for i in items if i[0]=="symbol"]),"labels:",len([i for i in items if i[0]=="global_label"]))
