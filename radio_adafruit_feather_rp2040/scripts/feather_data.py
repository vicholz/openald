#!/usr/bin/env python3
"""Extract the Adafruit Feather RP2040 mechanical data from Adafruit's own Eagle board file
(github.com/adafruit/Adafruit-Feather-RP2040-PCB, "Adafruit Feather RP2040.brd", the current revision with the
right-angle BOOT button, CC BY-SA) and write
  ref/feather_rp2040_mech.json   every part's footprint box, LEDs, buttons, header pads, holes (Feather + case frame)
  case/feather_params.scad       the same, for the OpenSCAD case
Feather frame: Eagle mm, origin = board lower-left, X along the 50.8 mm length (USB-C at X=0), Y across (22.86 mm).
Case frame:   X across the case (Feather centred on X=19), Y = 0 at the USB-C receptacle face, +Y toward the
              top end, Z = 0 at the Feather bottom face (Feather mounted components-up).
Part heights are NOT in the Eagle file; they are estimates from the part datasheets (see HEIGHT below)."""
import xml.etree.ElementTree as ET, json, math, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
BRD=os.path.join(ROOT,"ref","Adafruit Feather RP2040.brd")
# USB-C (X6, CUI CUSB31-CFM2AX-01-X) package outline runs to local y=-5.08 (the receptacle face);
# rotated R270 at X=3.8735 -> face at X=-1.2065, i.e. 1.21 mm beyond the board edge (current rev).
# Rev B and older boards: X6 at X=2.6035 -> 2.48 mm overhang (see README "Feather revisions").
FEATHER_T=1.6
HEIGHT={  # mm above the Feather top surface (datasheet / typical values; measure your board)
 "0805-NO":1.25,"CHIPLED_0603_NOOUTLINE":0.6,"0603-NO":0.55,"BTN_KMR2_4.6X2.8":1.9,"SOT23-5":1.2,"JSTPH2_BATT":5.5,
 "LED3535":1.0,"USON8_4X4":0.6,"SOD-123":1.2,"SOT23-R":1.2,"USB_C_CUSB31-CFM2AX-01-X":3.26,"QFN56_7MM_REDUCEDEPAD":0.9,
 "JST_SH4":2.95,"2X05_1.27MM_BOX_NOCREAM":0.0,"CRYSTAL_2.5X2":0.8,"SOD-323_MINI":1.0,"SPST_TACTILE_RA_2*4*3.5MM":2.5,
 "1X16_ROUND":0.0,"1X12_ROUND":0.0}
def rot(x,y,r,mirror=False):
    if mirror: x=-x
    a=math.radians(r); return x*math.cos(a)-y*math.sin(a), x*math.sin(a)+y*math.cos(a)
def parse_rot(s):
    s=s or "R0"; m="M" in s; return float(s.replace("M","").replace("R","") or 0), m
def main(ovh=None):
    r=ET.parse(BRD).getroot(); b=r.find(".//board")
    pk={}
    for lib in b.find("libraries"):
        ps=lib.find("packages")
        if ps is None: continue
        for p in ps: pk[(lib.get("name"),p.get("name"))]=p
    els={e.get("name"):e for e in b.find("elements")}
    x6=els["X6"]; OVH=5.08-float(x6.get("x")) if ovh is None else ovh
    def to_case(fx,fy): return (round(19.0-(fy-11.43),3), round(fx+OVH,3))
    parts=[]
    for name,e in els.items():
        P=pk[(e.get("library"),e.get("package"))]; R,M=parse_rot(e.get("rot"))
        if M: continue                                   # bottom-side items (test pads, logo): nothing tall
        xs=[];ys=[]
        for c in P:
            if c.tag=="smd":
                cx,cy,dx,dy=(float(c.get(k)) for k in ("x","y","dx","dy")); pr=float((c.get("rot") or "R0").replace("R",""))
                for sx in (-1,1):
                    for sy in (-1,1):
                        px,py=rot(sx*dx/2,sy*dy/2,pr); xs.append(cx+px); ys.append(cy+py)
            elif c.tag=="wire" and c.get("layer") in ("21","51"):
                xs+=[float(c.get("x1")),float(c.get("x2"))]; ys+=[float(c.get("y1")),float(c.get("y2"))]
        if not xs or e.get("package") not in HEIGHT: continue
        h=HEIGHT[e.get("package")]
        if h<=0: continue
        corners=[rot(x,y,R) for x in (min(xs),max(xs)) for y in (min(ys),max(ys))]
        ex,ey=float(e.get("x")),float(e.get("y"))
        cc=[to_case(ex+u,ey+v) for u,v in corners]
        X=[c[0] for c in cc]; Y=[c[1] for c in cc]
        parts.append(dict(ref=name,pkg=e.get("package"),value=e.get("value"),x0=min(X),x1=max(X),y0=min(Y),y1=max(Y),
                          z0=FEATHER_T,z1=round(FEATHER_T+h,2),at=to_case(ex,ey)))
    # holes: 2.5 mm plated pair at the USB end (elements), 2.54 mm NPTH pair at the far end (plain holes)
    holes=[to_case(float(els[n].get("x")),float(els[n].get("y"))) for n in ("U$32","U$31")]
    holes+=[to_case(float(h.get("x")),float(h.get("y"))) for h in b.find("plain") if h.tag=="hole"]
    holes=sorted(holes,key=lambda p:(p[1],p[0]))
    pads={}
    sig={}
    for s in b.find("signals"):
        for c in s.findall("contactref"):
            sig[(c.get("element"),c.get("pad"))]=s.get("name")
    for hdr,n,x0,step,y in (("JP1",16,25.4+19.05,-2.54,1.27),("JP3",12,30.48-13.97,2.54,21.6535)):
        for i in range(1,n+1):
            pads[f"{hdr}.{i}"]=dict(net=sig.get((hdr,str(i))),case=to_case(x0+step*(i-1),y))
    # STAT tap: R2 pad 2 (net N$3 = MCP73831 STAT), 0603 pads at +-0.75 mm
    r2=els["R2"]; stat=to_case(float(r2.get("x"))+0.8,float(r2.get("y")))
    led=lambda n: to_case(float(els[n].get("x")),float(els[n].get("y")))
    out=dict(source="Adafruit Feather RP2040.brd (github.com/adafruit/Adafruit-Feather-RP2040-PCB), CC BY-SA 3.0",
             board_w=50.8,board_h=22.86,board_t=FEATHER_T,usb_overhang=round(OVH,4),
             board_case=dict(x0=round(19-11.43,3),x1=round(19+11.43,3),y0=round(OVH,3),y1=round(OVH+50.8,3)),
             holes=holes,hole_d=[2.5,2.5,2.54,2.54],
             leds=dict(CHG=led("CHG"),RED_D13=led("L"),NEOPIXEL=led("LED1")),
             buttons=dict(RESET=led("SW1"),BOOT_RA=led("SW3")),jst_bat=led("X1"),stemma_qt=led("CONN1"),
             usb=dict(center_x=19.0,center_z=round(FEATHER_T+3.26/2,3),w=8.94,h=3.26,face_y=0.0,len=7.35),
             stat_tap_R2_pad2=stat,pads=pads,parts=parts)
    os.makedirs(os.path.join(ROOT,"ref"),exist_ok=True)
    json.dump(out,open(os.path.join(ROOT,"ref","feather_rp2040_mech.json"),"w"),indent=1)
    L=["// AUTO-GENERATED by scripts/feather_data.py from Adafruit's Feather RP2040 Eagle board -- do not edit",
       f"feather_t = {FEATHER_T};", f"feather_box = [{out['board_case']['x0']}, {out['board_case']['x1']}, {out['board_case']['y0']}, {out['board_case']['y1']}];",
       f"feather_holes = {json.dumps([list(h) for h in holes])};",
       f"f_led_chg = {list(out['leds']['CHG'])};", f"f_led_red = {list(out['leds']['RED_D13'])};", f"f_led_neo = {list(out['leds']['NEOPIXEL'])};",
       f"f_btn_reset = {list(out['buttons']['RESET'])};", f"f_btn_boot = {list(out['buttons']['BOOT_RA'])};",
       f"f_jst = {list(out['jst_bat'])};", f"f_qt = {list(out['stemma_qt'])};",
       "// component envelopes [x0,x1,y0,y1,z0,z1] (case frame)",
       "f_parts = ["+",\n  ".join(f"[{p['x0']},{p['x1']},{p['y0']},{p['y1']},{p['z0']},{p['z1']}]" for p in parts)+"];"]
    open(os.path.join(ROOT,"case","feather_params.scad"),"w").write("\n".join(L)+"\n")
    return out
if __name__=="__main__":
    # older Feather RP2040 boards (rev B and before): USB-C 2.48 mm past the edge -> --usb-overhang 2.48
    o=main(float(sys.argv[sys.argv.index("--usb-overhang")+1]) if "--usb-overhang" in sys.argv else None)
    print("USB overhang",o["usb_overhang"],"board",o["board_case"],"holes",o["holes"])
    print("LEDs",o["leds"],"buttons",o["buttons"],"JST",o["jst_bat"],"QT",o["stemma_qt"],"STAT tap",o["stat_tap_R2_pad2"])
    for k in ("JP1.12","JP1.13","JP1.14","JP1.8","JP1.7","JP1.1","JP3.1","JP3.2","JP3.3","JP3.11","JP3.12"): print(k,o["pads"][k])
    for p in o["parts"]:
        if p["z1"]>3: print(p["ref"],p["pkg"],p["x0"],p["x1"],p["y0"],p["y1"],p["z1"])
