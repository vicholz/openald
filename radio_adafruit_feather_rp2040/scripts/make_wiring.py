#!/usr/bin/env python3
"""Draw docs/wiring_diagram.svg (+ .png) for the direct-mount Feather RP2040 variant (no controls PCB):
Feather RP2040 <-> SIQ-02FVS3 wheel, SS-12F16 switch, FM module, 18650 holder, optional divider and 3 mm charge LEDs."""
import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import layout as L
ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,"docs","wiring_diagram")
W,H=1640,1120
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Arial, sans-serif">',
   f'<rect width="{W}" height="{H}" fill="white"/>',
   '<text x="30" y="42" font-size="26" font-weight="bold">OpenALD Feather RP2040 v1.0 - wiring (direct-mount wheel and switch, no controls board)</text>',
   '<text x="30" y="70" font-size="15" fill="#555">All wires are hand-soldered (28-30 AWG silicone). Not hardware-validated. Colours are suggestions. Dashed = optional. FM module pin order: check your silkscreen.</text>']
def box(x,y,w,h,title,sub,fill,dash=False):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="#333" stroke-width="2" {"stroke-dasharray=\'8,5\'" if dash else ""}/>')
    o.append(f'<text x="{x+w/2}" y="{y+28}" font-size="19" font-weight="bold" text-anchor="middle">{title}</text>')
    for i,s in enumerate(sub): o.append(f'<text x="{x+w/2}" y="{y+50+i*18}" font-size="13" fill="#333" text-anchor="middle">{s}</text>')
def pin(x,y,label,side):
    o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#d4a017" stroke="#333"/>')
    if side=="r": o.append(f'<text x="{x-12}" y="{y+5}" font-size="14" text-anchor="end">{label}</text>')
    else: o.append(f'<text x="{x+12}" y="{y+5}" font-size="14">{label}</text>')
def wire(pts,col,label=None,lx=None,ly=None,dash=False):
    d="M"+" L".join(f"{x},{y}" for x,y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round" {"stroke-dasharray=\'10,6\'" if dash else ""}/>')
    if label: o.append(f'<text x="{lx}" y="{ly}" font-size="12" fill="#222">{label}</text>')
def txt(x,y,s,size=13,anchor="start",col="#222"): o.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}">{s}</text>')
# Feather
FX,FY,FW,FH=520,150,330,640
box(FX,FY,FW,FH,"Adafruit Feather RP2040",["(#4884, components up,","USB-C at the dock end)"],"#e8f4ea")
fl={"BAT (VBAT)":215,"EN":255,"USB (VBUS)":295,"STAT tap: R2 pad (STAT side)":335,"JST PH battery +":440,"JST PH battery -":480}
fr={"GND (only one pin)":215,"A0 (GP26)":255,"D24 (GP24)":295,"D25 (GP25)":335,"D4 (GP6)":375,"STEMMA QT 3V3":480,"STEMMA QT GND":520,"STEMMA QT SDA (GP2)":560,"STEMMA QT SCL (GP3)":600}
for k,y in fl.items(): pin(FX,FY+y,k,"l")
for k,y in fr.items(): pin(FX+FW,FY+y,k,"r")
txt(FX+FW/2,FY+92,"MCP73831 charger 200 mA, CHG LED, red D13, NeoPixel",13,"middle","#333")
txt(FX+FW/2,FY+110,"(seen through top windows when undocked).",13,"middle","#333")
txt(FX+FW/2,FY+128,"EN low = 3.3 V regulator off (radio off).",13,"middle","#333")
# battery / FM (left)
BX,BY,BW,BH=60,500,300,170
box(BX,BY,BW,BH,"18650 holder (BH-18650-PC)",["protected button-top cell","+ pin at the USB end, - at the jack end"],"#f6eee0")
pin(BX+BW,BY+90,"+ (red)","r"); pin(BX+BW,BY+130,"- (black)","r")
wire([(BX+BW,BY+90),(470,BY+90),(470,FY+440),(FX,FY+440)],"#d22","JST PH cable (#261) red",372,BY+82)
wire([(BX+BW,BY+130),(490,BY+130),(490,FY+480),(FX,FY+480)],"#111","black",372,BY+150)
MX,MY,MW,MH=60,180,300,200
box(MX,MY,MW,MH,"RDA5807M FM module",["26.9 x 26.9, 3.5 mm jack on board","I2C 0x10 / 0x11, 3.3 V"],"#eef")
mp={"VCC":270,"GND":300,"SDA":330,"SCL":360}
for k,y in mp.items(): pin(MX+MW,y,k,"r")
qt=[("STEMMA QT 3V3","VCC","#d22"),("STEMMA QT GND","GND","#111"),("STEMMA QT SDA (GP2)","SDA","#27c"),("STEMMA QT SCL (GP3)","SCL","#cc0")]
for i,(f,m,col) in enumerate(qt):
    y1=FY+fr[f]; xr=FX+FW+30+i*14; yb=FY+FH+30+i*14; xl=400+i*14
    wire([(FX+FW,y1),(xr,y1),(xr,yb),(xl,yb),(xl,mp[m]),(MX+MW,mp[m])],col)
txt(FX+FW/2,FY+FH+110,"STEMMA QT cable (#4210, one end cut, soldered to the FM module): red 3V3, black GND, blue SDA, yellow SCL",13,"middle")
# GND splice
GX,GY=1000,150
o.append(f'<rect x="{GX-8}" y="{GY+40}" width="16" height="330" fill="#444" rx="6"/>'); txt(GX,GY+30,"GND splice (heat-shrink, in the right channel)",13,"middle")
wire([(FX+FW,FY+fr["GND (only one pin)"]),(GX,FY+fr["GND (only one pin)"])],"#111")
# wheel (right top)
WX_,WY_,WW,WH=1180,110,400,220
box(WX_,WY_,WW,WH,"Mitsumi SIQ-02FVS3 thumbwheel",["glued in the frame cradle; 4 tabs on the inner edge","order along +Y (USB end -> top end): B, C, S, A"],"#e6eefb")
wp={"A":190,"B":220,"S (push)":250,"C (common)":280}
for k,y in wp.items(): pin(WX_,y,k,"l")
for i,(sig,fp,col) in enumerate([("A","D24 (GP24)","#7a3"),("B","D25 (GP25)","#3a7"),("S (push)","D4 (GP6)","#a73")]):
    xm=FX+FW+120+i*16; wire([(FX+FW,FY+fr[fp]),(xm,FY+fr[fp]),(xm,wp[sig]),(WX_,wp[sig])],col)
wire([(GX,wp["C (common)"]),(WX_,wp["C (common)"])],"#111")
# switch (right middle)
SX,SY,SW,SH=1180,370,400,200
box(SX,SY,SW,SH,"SS-12F16 slide switch (SPDT)",["in a groove in the LEFT wall, no screws","knob toward the USB end = OFF"],"#e6eefb")
sp={"lug at the OFF end (USB side)":450,"middle lug (common)":490,"lug at the ON end: unused":530}
for k,y in sp.items(): pin(SX,y,k,"l")
wire([(GX,sp["lug at the OFF end (USB side)"]),(SX,sp["lug at the OFF end (USB side)"])],"#111")
yt=FY-30; xl=FX-40
wire([(FX,FY+fl["EN"]),(xl,FY+fl["EN"]),(xl,yt),(1100,yt),(1100,sp["middle lug (common)"]),(SX,sp["middle lug (common)"])],"#f80")
txt(SX,SY+SH+22,"Check with a meter before soldering: with the knob at the OFF end,",13)
txt(SX,SY+SH+40,"the OFF-end lug must connect to the middle lug.",13)
txt(SX,SY-14,"OFF lug GND: splice to battery (-) lead (same net)",12)
# optional divider + LEDs
DX,DY,DW,DH=1180,640,400,170
box(DX,DY,DW,DH,"Battery divider (inline, heat-shrink)",["BAT - 220k - A0 - 220k - GND, 100 nF A0 to GND","needed for the battery gauge (Feather has none)"],"#f3f3f3")
dp={"top (BAT)":720,"middle (A0)":750,"bottom (GND)":780}
for k,y in dp.items(): pin(DX,y,k,"l")
wire([(FX,FY+fl["BAT (VBAT)"]),(FX-60,FY+fl["BAT (VBAT)"]),(FX-60,FY+FH+70),(1080,FY+FH+70),(1080,dp["top (BAT)"]),(DX,dp["top (BAT)"])],"#c55")
wire([(FX+FW,FY+fr["A0 (GP26)"]),(FX+FW+80,FY+fr["A0 (GP26)"]),(FX+FW+80,dp["middle (A0)"]),(DX,dp["middle (A0)"])],"#888")
wire([(GX,FY+370),(GX,dp["bottom (GND)"]),(DX,dp["bottom (GND)"])],"#111")
LX,LY,LW,LH=1180,860,400,230
box(LX,LY,LW,LH,"Optional dock-visible charge LEDs",["two 3 mm THT LEDs in the top-half sockets","VBUS - 1.5k - red(A>K) - STAT - 1.5k - green(A>K) - GND"],"#fff6f6",dash=True)
lp={"VBUS (via 1.5k to red anode)":960,"STAT (red K, 1.5k to green A)":1000,"GND (green cathode)":1040}
for k,y in lp.items(): pin(LX,y,k,"l")
wire([(FX,FY+fl["USB (VBUS)"]),(FX-80,FY+fl["USB (VBUS)"]),(FX-80,lp["VBUS (via 1.5k to red anode)"]),(LX,lp["VBUS (via 1.5k to red anode)"])],"#d22",dash=True)
wire([(FX,FY+fl["STAT tap: R2 pad (STAT side)"]),(FX-100,FY+fl["STAT tap: R2 pad (STAT side)"]),(FX-100,lp["STAT (red K, 1.5k to green A)"]),(LX,lp["STAT (red K, 1.5k to green A)"])],"#a0a",dash=True)
wire([(GX,dp["bottom (GND)"]),(GX,lp["GND (green cathode)"]),(LX,lp["GND (green cathode)"])],"#111",dash=True)
txt(30,H-20,"STAT tap = 32-36 AWG enamel wire to the STAT end of Feather R2 (10k in series with the CHG LED), case position (25.92, 7.77). Skip it and the two LEDs if you don't need dock-visible charge status.",13)
o.append("</svg>")
open(OUT+".svg","w").write("\n".join(o))
import cairosvg; cairosvg.svg2png(url=OUT+".svg",write_to=OUT+".png",output_width=W)
print("wrote",os.path.relpath(OUT+".svg",ROOT),os.path.relpath(OUT+".png",ROOT))
