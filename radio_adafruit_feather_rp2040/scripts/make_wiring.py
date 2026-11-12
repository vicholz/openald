#!/usr/bin/env python3
"""Draw docs/wiring_diagram.svg (+ .png): Feather RP2040 <-> FM module <-> controls board <-> 18650 holder."""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import layout as L
ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,"docs","wiring_diagram")
W,H=1560,1010
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Arial, sans-serif">',
   f'<rect width="{W}" height="{H}" fill="white"/>',
   '<text x="30" y="42" font-size="26" font-weight="bold">OpenALD Feather RP2040 v1.0 - wiring</text>',
   '<text x="30" y="70" font-size="15" fill="#555">All wires are hand-soldered. Not hardware-validated. Wire colours are suggestions. FM module pin order: check the silkscreen on yours.</text>']
def box(x,y,w,h,title,sub,fill):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="#333" stroke-width="2"/>')
    o.append(f'<text x="{x+w/2}" y="{y+28}" font-size="19" font-weight="bold" text-anchor="middle">{title}</text>')
    for i,s in enumerate(sub): o.append(f'<text x="{x+w/2}" y="{y+50+i*18}" font-size="13" fill="#333" text-anchor="middle">{s}</text>')
def pin(x,y,label,side):   # side: 'r' pin on right edge, 'l' on left edge
    o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#d4a017" stroke="#333"/>')
    if side=="r": o.append(f'<text x="{x-12}" y="{y+5}" font-size="14" text-anchor="end">{label}</text>')
    else: o.append(f'<text x="{x+12}" y="{y+5}" font-size="14">{label}</text>')
def wire(pts,col,label=None,lx=None,ly=None,dash=False):
    d="M"+" L".join(f"{x},{y}" for x,y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round" {"stroke-dasharray=\'10,6\'" if dash else ""}/>')
    if label: o.append(f'<text x="{lx}" y="{ly}" font-size="12" fill="#222">{label}</text>')
# Feather
FX,FY,FW,FH=520,160,330,600
box(FX,FY,FW,FH,"Adafruit Feather RP2040",["(#4884, mounted components-up,","USB-C at the dock end)"],"#e8f4ea")
fl={"VBAT":215,"EN":255,"USB (VBUS)":295,"STAT tap: R2 pad (STAT side)":335,"JST PH battery +":420,"JST PH battery -":460}
fr={"GND":215,"A0 (GP26)":255,"D24 (GP24)":295,"D25 (GP25)":335,"D4 (GP6)":375,"STEMMA QT 3V3":470,"STEMMA QT GND":510,"STEMMA QT SDA (GP2)":550,"STEMMA QT SCL (GP3)":590}
for k,y in fl.items(): pin(FX,FY+y,k,"l")
for k,y in fr.items(): pin(FX+FW,FY+y,k,"r")
o.append(f'<text x="{FX+FW/2}" y="{FY+92}" font-size="13" text-anchor="middle" fill="#333">On-board: MCP73831 charger 200 mA, CHG LED (amber),</text>')
o.append(f'<text x="{FX+FW/2}" y="{FY+110}" font-size="13" text-anchor="middle" fill="#333">red LED D13, NeoPixel - all seen through top windows.</text>')
o.append(f'<text x="{FX+FW/2}" y="{FY+128}" font-size="13" text-anchor="middle" fill="#333">EN low = 3.3 V regulator off (radio off).</text>')
# Controls board (right)
CX,CY,CW,CH=1110,190,380,520
box(CX,CY,CW,CH,"Controls board (KiCad, JLC)",["SIQ-02FVS3 wheel + push, SK-12E12 switch,","220k/220k divider, CHG/FULL mirror LEDs"],"#e6eefb")
cy={}
for i,n in enumerate(L.PADS):
    y=CY+120+i*40; cy[n]=y; pin(CX,y,f"J1.{i+1} {n}","l")
# Battery holder (left bottom)
BX,BY,BW,BH=60,460,300,170
box(BX,BY,BW,BH,"18650 holder MPD BH-18650-PC",["protected button-top cell","+ pin at the USB end, - at the jack end"],"#f6eee0")
pin(BX+BW,BY+90,"+ (red)","r"); pin(BX+BW,BY+130,"- (black)","r")
# FM module (left top)
MX,MY,MW,MH=60,190,300,200
box(MX,MY,MW,MH,"RDA5807M FM module",["26.9 x 26.9, 3.5 mm jack on board","I2C 0x10 / 0x11, 3.3 V"],"#eef")
mp={"VCC":280,"GND":310,"SDA":340,"SCL":370}
# route FM via STEMMA QT cable: FM pins on the right edge of the FM box
for k,y in mp.items(): pin(MX+MW,y,k,"r")
# wires: battery
wire([(BX+BW,BY+90),(470,BY+90),(470,FY+420),(FX,FY+420)],"#d22","JST PH cable (#261) red",372,BY+82)
wire([(BX+BW,BY+130),(490,BY+130),(490,FY+460),(FX,FY+460)],"#111","black",372,BY+150)
# FM via QT cable: from Feather right side QT pins around the bottom to FM? draw: QT pins right side -> down -> left under -> up to FM
qt=[("STEMMA QT 3V3","VCC","#d22"),("STEMMA QT GND","GND","#111"),("STEMMA QT SDA (GP2)","SDA","#27c"),("STEMMA QT SCL (GP3)","SCL","#cc0")]
for i,(f,m,col) in enumerate(qt):
    y1=FY+fr[f]; xr=FX+FW+30+i*14; yb=FY+FH+40+i*14; xl=400+i*14
    wire([(FX+FW,y1),(xr,y1),(xr,yb),(xl,yb),(xl,mp[m]),(MX+MW,mp[m])],col)
o.append(f'<text x="{FX+FW/2}" y="{FY+FH+120}" font-size="13" text-anchor="middle">STEMMA QT cable (Adafruit #4210, one end cut and soldered to the FM module): red 3V3, black GND, blue SDA, yellow SCL</text>')
# controls wires
ct=[("ENCA","D24 (GP24)","r","#7a3"),("ENCB","D25 (GP25)","r","#3a7"),("ENCSW","D4 (GP6)","r","#a73"),("GND","GND","r","#111"),
    ("BSNS","A0 (GP26)","r","#888"),("EN","EN","l","#f80"),("VBUS","USB (VBUS)","l","#d22"),("STAT","STAT tap: R2 pad (STAT side)","l","#a0a"),("VBAT","VBAT","l","#c55")]
for i,(c,f,side,col) in enumerate(ct):
    yc=cy[c]
    if side=="r":
        y1=FY+fr[f]; xm=FX+FW+110+i*16
        wire([(FX+FW,y1),(xm,y1),(xm,yc),(CX,yc)],col)
    else:
        y1=FY+fl[f]; xl=FX-24-(i-5)*12; yt=FY-24-(i-5)*14; xm=CX-30-(i-5)*14
        wire([(FX,y1),(xl,y1),(xl,yt),(xm,yt),(xm,yc),(CX,yc)],col,dash=(c=="STAT"))
o.append(f'<text x="{CX-10}" y="{CY+CH+30}" font-size="13">J1: 9 THT pads, 1.8 mm pitch; wires come up through the frame slot.</text>')
o.append(f'<text x="{CX-10}" y="{CY+CH+50}" font-size="13">SW1 common = EN; knob toward the USB end = EN to GND = OFF.</text>')
o.append(f'<text x="{CX-10}" y="{CY+CH+70}" font-size="13">STAT (dashed) is a fine wire to the STAT end of Feather R2 (10k,</text>')
o.append(f'<text x="{CX-10}" y="{CY+CH+88}" font-size="13">CHG LED resistor). Optional: skip it and fit no D1/D2.</text>')
o.append("</svg>")
open(OUT+".svg","w").write("\n".join(o))
import cairosvg; cairosvg.svg2png(url=OUT+".svg",write_to=OUT+".png",output_width=W)
print("wrote",os.path.relpath(OUT+".svg",ROOT),os.path.relpath(OUT+".png",ROOT))
