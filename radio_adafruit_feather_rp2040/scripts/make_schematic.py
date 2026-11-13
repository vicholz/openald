#!/usr/bin/env python3
"""Generate docs/wiring_schematic/openald-feather-wiring.kicad_sch: a KiCad 9 schematic of the hand-wired Feather RP2040
variant (same nets as docs/wiring_diagram.svg and firmware/openald_feather). Every pin gets a short wire stub and a
net label, as in the single-board generator, so the connectivity is explicit and ERC-checkable.
Run ERC:  kicad-cli sch erc --severity-all docs/wiring_schematic/openald-feather-wiring.kicad_sch"""
import os,sys,uuid,math,copy,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from sexp import dump,Sym as S,find,parse
import symlib
ROOT=os.path.dirname(HERE); D=os.path.join(ROOT,"docs","wiring_schematic"); os.makedirs(D,exist_ok=True)
NAME="openald-feather-wiring"; LIBN="openald_feather"
G=2.54
def U(seed): return str(uuid.uuid5(uuid.NAMESPACE_DNS,"openald-feather-"+seed))
RUUID=U("root")

# ---------------- project symbol library ----------------
def lpin(name,num,x,y,ang): return f'      (pin passive line (at {x} {y} {ang}) (length 2.54) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))\n'
def lprop(k,v,x,y,hide=False): return f'    (property "{k}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27)){" (hide yes)" if hide else ""}))\n'
def lsym(name,ref,val,ds,w,h,pins,desc):
    s=f'  (symbol "{name}" (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
    s+=lprop("Reference",ref,0,h/2+1.27)+lprop("Value",val,0,-h/2-1.27)+lprop("Footprint","",0,-h/2-3.81,True)+lprop("Datasheet",ds,0,0,True)+lprop("Description",desc,0,0,True)
    s+=f'    (symbol "{name}_0_1"\n      (rectangle (start {-w/2} {h/2}) (end {w/2} {-h/2}) (stroke (width 0.254) (type default)) (fill (type background)))\n    )\n'
    s+=f'    (symbol "{name}_1_1"\n'+"".join(pins)+'    )\n  )\n'
    return s
FL=[("QT_3V3","QT3V3"),("QT_GND","QTGND"),("QT_SDA/GP2","QTSDA"),("QT_SCL/GP3","QTSCL"),
    ("EN/JP3.2","EN"),("JST_BAT+","JST+"),("JST_BAT-","JST-")]
FR=[("D24/GP24/JP1.8","D24"),("D25/GP25/JP1.7","D25"),("D4/GP6/JP1.1","D4"),("GND/JP1.13","GND"),
    ("BAT/JP3.1","BAT"),("A0/GP26/JP1.12","A0"),("USB/VBUS/JP3.3","USB"),("STAT/R2_tap","STAT")]
FW,FH=60.96,45.72
fp=[lpin(n,k,-FW/2-2.54,FH/2-5.08*(i+1),0) for i,(n,k) in enumerate(FL)]+[lpin(n,k,FW/2+2.54,FH/2-5.08*(i+1),180) for i,(n,k) in enumerate(FR)]
lib='(kicad_symbol_lib (version 20231120) (generator "openald_gen") (generator_version "9.0")\n'
lib+=lsym("Feather_RP2040_wired","U","Adafruit Feather RP2040 (#4884)","https://learn.adafruit.com/adafruit-feather-rp2040-pico",FW,FH,fp,
          "Adafruit Feather RP2040: only the pins/pads used by OpenALD Feather v1.0 (JST+ = BAT and JST- = GND on the board)")
MW,MH=15.24,15.24
lib+=lsym("RDA5807M_module","U","RDA5807M FM module (3.5 mm jack on board)","",MW,MH,
          [lpin(n,n,-MW/2-2.54,MH/2-3.81*(i+1),0) for i,n in enumerate(["VCC","GND","SDA","SCL"])],"26.9 x 26.9 mm RDA5807M module, I2C 0x10/0x11")
EW,EH=10.16,10.16
lib+=lsym("SIQ-02FVS3","SW","Mitsumi SIQ-02FVS3","https://datasheet.lcsc.com/datasheet/pdf/7bff72617d5a3503f5ed21ab02a77dea.pdf",EW,EH,
          [lpin("A","A",-EW/2-2.54,2.54,0),lpin("B","B",-EW/2-2.54,-2.54,0),lpin("S","S",EW/2+2.54,2.54,180),lpin("C","C",EW/2+2.54,-2.54,180)],
          "Thumbwheel encoder (A/B to common C) with push switch S (to C)")
lib+=")\n"
open(os.path.join(D,LIBN+".kicad_sym"),"w").write(lib)
open(os.path.join(D,"sym-lib-table"),"w").write(f'(sym_lib_table\n  (version 7)\n  (lib (name "{LIBN}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIBN}.kicad_sym")(options "")(descr "OpenALD Feather wiring symbols"))\n)\n')
EXTRA={LIBN:os.path.join(D,LIBN+".kicad_sym")}

# ---------------- parts (ref, lib, value, pins->nets, X, Y) ----------------
P=[dict(ref="U1",lib=f"{LIBN}:Feather_RP2040_wired",val="Adafruit Feather RP2040",X=165.1,Y=111.76,
        pins={"QT3V3":"+3V3","QTGND":"GND","QTSDA":"SDA","QTSCL":"SCL","EN":"EN","JST+":"VBAT","JST-":"GND",
              "D24":"ENC_A","D25":"ENC_B","D4":"ENC_SW","GND":"GND","BAT":"VBAT","A0":"VBAT_SENSE","USB":"VBUS","STAT":"STAT"}),
   dict(ref="U2",lib=f"{LIBN}:RDA5807M_module",val="RDA5807M FM module",X=78.74,Y=68.58,pins={"VCC":"+3V3","GND":"GND","SDA":"SDA","SCL":"SCL"}),
   dict(ref="BT1",lib="Device:Battery_Cell",val="18650 in BH-18650-PC",X=73.66,Y=114.3,pins={"1":"VBAT","2":"GND"}),
   dict(ref="SW1",lib="Switch:SW_SPDT",val="SS-12F16 (A = OFF-end lug)",X=73.66,Y=152.4,pins={"2":"EN","1":"GND","3":None}),
   dict(ref="SW2",lib=f"{LIBN}:SIQ-02FVS3",val="SIQ-02FVS3 wheel",X=264.16,Y=68.58,pins={"A":"ENC_A","B":"ENC_B","S":"ENC_SW","C":"GND"}),
   dict(ref="R1",lib="Device:R",val="220k",X=246.38,Y=114.3,pins={"1":"VBAT","2":"VBAT_SENSE"}),
   dict(ref="R2",lib="Device:R",val="220k",X=271.78,Y=114.3,pins={"1":"VBAT_SENSE","2":"GND"}),
   dict(ref="C1",lib="Device:C",val="100nF",X=297.18,Y=114.3,pins={"1":"VBAT_SENSE","2":"GND"}),
   dict(ref="R3",lib="Device:R",val="1.5k (optional)",X=233.68,Y=162.56,pins={"1":"VBUS","2":"LED_R_A"}),
   dict(ref="D1",lib="Device:LED",val="red 3 mm CHG (optional)",X=264.16,Y=162.56,pins={"2":"LED_R_A","1":"STAT"}),
   dict(ref="R4",lib="Device:R",val="1.5k (optional)",X=294.64,Y=162.56,pins={"1":"STAT","2":"LED_G_A"}),
   dict(ref="D2",lib="Device:LED",val="green 3 mm FULL (optional)",X=325.12,Y=162.56,pins={"2":"LED_G_A","1":"GND"})]
lib_syms={}; items=[]
def eff(hide=False,just=None,size=1.27):
    e=[S("effects"),[S("font"),[S("size"),size,size]]]
    if just: e.append([S("justify"),S(just)])
    if hide: e.append([S("hide"),S("yes")])
    return e
for p in P:
    lid=p["lib"]
    if lid not in lib_syms:
        s=copy.deepcopy(symlib.get_symbol(lid,EXTRA)); s[1]=lid; lib_syms[lid]=s
    pins=symlib.pins(lib_syms[lid]); X,Y,ref=p["X"],p["Y"],p["ref"]
    ys=[pp["y"] for pp in pins]; top=Y-max(ys)-3; bot=Y-min(ys)+3
    e=[S("symbol"),[S("lib_id"),lid],[S("at"),X,Y,0],[S("unit"),1],[S("exclude_from_sim"),S("no")],[S("in_bom"),S("yes")],
       [S("on_board"),S("yes")],[S("dnp"),S("no")],[S("uuid"),U("sym-"+ref)],
       *([[S("property"),"Reference",ref,[S("at"),X+2.54,Y-1.27,0],eff(just="left")],[S("property"),"Value",p["val"],[S("at"),X+2.54,Y+1.27,0],eff(just="left")]]
         if lid in ("Device:R","Device:C","Device:Battery_Cell") else
         [[S("property"),"Reference",ref,[S("at"),X,top-1.27,0],eff()],[S("property"),"Value",p["val"],[S("at"),X,bot+1.27,0],eff()]]),
       [S("property"),"Footprint","",[S("at"),X,Y,0],eff(True)],[S("property"),"Datasheet","~",[S("at"),X,Y,0],eff(True)]]
    for pp in pins: e.append([S("pin"),pp["num"],[S("uuid"),U("pin-"+ref+"-"+pp["num"])]])
    e.append([S("instances"),[S("project"),NAME,[S("path"),"/"+RUUID,[S("reference"),ref],[S("unit"),1]]]])
    items.append(e)
    for pp in pins:
        tx=X+pp["x"]; ty=Y-pp["y"]; a=math.radians(pp["ang"]); dx=-round(math.cos(a)); dy=round(math.sin(a))
        if pp["num"] not in p["pins"]: raise SystemExit(f"{ref} pin {pp['num']} not assigned")
        net=p["pins"][pp["num"]]
        if net is None: items.append([S("no_connect"),[S("at"),tx,ty],[S("uuid"),U("nc-"+ref+pp["num"])]]); continue
        ex=tx+dx*G; ey=ty+dy*G
        items.append([S("wire"),[S("pts"),[S("xy"),tx,ty],[S("xy"),ex,ey]],[S("stroke"),[S("width"),0],[S("type"),S("default")]],[S("uuid"),U("w-"+ref+pp["num"])]])
        ang={(1,0):0,(-1,0):180,(0,-1):90,(0,1):270}[(dx,dy)]
        items.append([S("global_label"),net,[S("shape"),S("passive")],[S("at"),ex,ey,ang],[S("fields_autoplaced"),S("yes")],
                      eff(just={0:"left",180:"right",90:"left",270:"right"}[ang]),[S("uuid"),U("l-"+ref+pp["num"])],
                      [S("property"),"Intersheetrefs","${INTERSHEET_REFS}",[S("at"),ex,ey,0],eff(True)]])
notes=["OpenALD Feather RP2040 v1.0: every net below is a hand-soldered wire (no PCB). NOT built or tested on hardware.",
       "GND: Feather JP1.13 is the only GND pin -> heat-shrunk splice to SW2 C, R2, C1, D2 K. SW1 OFF lug -> splice on the battery black lead (JST- = GND).",
       "SW1: knob at the USB end = OFF: common (EN) connects to the OFF-end lug (GND) -> 3.3 V regulator off. Check which lug with a meter.",
       "U1 JST+ and BAT are the same node on the Feather (VBAT); 3V3 (STEMMA QT) is switched by EN.",
       "R3/D1/R4/D2 optional: STAT low (charging) -> red, STAT high (full) -> green, no USB -> both off. STAT = fine wire to the STAT end of Feather R2.",
       "Firmware: firmware/openald_feather (GP24 ENC_A, GP25 ENC_B, GP6 ENC_SW, GP26 VBAT_SENSE = VBAT/2, I2C1 GP2/GP3, NeoPixel GP16)."]
for i,n in enumerate(notes):
    items.append([S("text"),n,[S("exclude_from_sim"),S("no")],[S("at"),25.4,210+i*6,0],eff(just="left",size=1.8),[S("uuid"),U(f"note{i}")]])
items.append([S("text"),"OpenALD Feather RP2040 v1.0 - hand-wiring schematic",[S("exclude_from_sim"),S("no")],[S("at"),25.4,30,0],
              [S("effects"),[S("font"),[S("size"),3,3],[S("bold"),S("yes")]],[S("justify"),S("left")]],[S("uuid"),U("title")]])
sch=[S("kicad_sch"),[S("version"),20231120],[S("generator"),"eeschema"],[S("generator_version"),"9.0"],[S("uuid"),RUUID],[S("paper"),"A3"],
     [S("title_block"),[S("title"),"OpenALD Feather RP2040 v1.0 - wiring"],[S("date"),"2026-11-12"],[S("rev"),"1.0"],
      [S("comment"),1,"Generated by scripts/make_schematic.py - same nets as docs/wiring_diagram.svg"],[S("comment"),2,"Not hardware-validated"]],
     [S("lib_symbols")]+list(lib_syms.values())]+items+[[S("sheet_instances"),[S("path"),"/",[S("page"),"1"]]]]
open(os.path.join(D,NAME+".kicad_sch"),"w").write(dump(sch)+"\n")
pro=os.path.join(D,NAME+".kicad_pro")
if not os.path.exists(pro): json.dump({"meta":{"filename":NAME+".kicad_pro","version":1},"schematic":{},"sheets":[[RUUID,"Root"]]},open(pro,"w"),indent=2)
print("wrote",os.path.relpath(os.path.join(D,NAME+".kicad_sch"),ROOT),"symbols:",len(P))
