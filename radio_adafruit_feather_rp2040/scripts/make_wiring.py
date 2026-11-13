#!/usr/bin/env python3
"""Draw docs/wiring_diagram.svg (+ .png) for the direct-mount Feather RP2040 variant (no controls PCB):
every hand-soldered wire between the Feather RP2040, the SIQ-02FVS3 wheel, the SS-12F16 switch, the 18650 holder,
the RDA5807M module, the battery divider and the optional charge LEDs. Pin numbers match firmware/openald_feather."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,"docs","wiring_diagram")
W,H=1800,1270
o=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="DejaVu Sans, Arial, sans-serif">',
   f'<rect width="{W}" height="{H}" fill="white"/>']
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def txt(x,y,s,size=14,anchor="start",col="#222",bold=False,italic=False):
    o.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}"'
             f'{" font-weight=\"bold\"" if bold else ""}{" font-style=\"italic\"" if italic else ""}>{esc(s)}</text>')
def rect(x,y,w,h,fill,dash=False,rx=10,stroke="#333"):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"'
             f'{" stroke-dasharray=\"9,6\"" if dash else ""}/>')
def box(x,y,w,h,title,sub,fill,dash=False):
    rect(x,y,w,h,fill,dash); txt(x+w/2,y+26,title,18,"middle",bold=True)
    for i,s in enumerate(sub): txt(x+w/2,y+46+i*17,s,12.5,"middle","#444")
def line(pts,col="#111",w=4,dash=False):
    d="M"+" L".join(f"{x},{y}" for x,y in pts)
    o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'
             f'{" stroke-dasharray=\"10,7\"" if dash else ""}/>')
def dot(x,y,col="#111"): o.append(f'<circle cx="{x}" cy="{y}" r="6.5" fill="{col}"/>')
def pin(x,y,label,side,sub=None):
    o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#e0b020" stroke="#333" stroke-width="1.5"/>')
    if side=="above_r": txt(x-12,y-9,label,13,"end"); return
    if side=="in_l": txt(x+12,y+5,label,14); sub and txt(x+12,y+21,sub,11,col="#666")
    else:            txt(x-12,y+5,label,14,"end"); sub and txt(x-12,y+21,sub,11,"end","#666")
def resistor(x0,x1,y,name,val,col="#111",dash=False):        # horizontal, IEC box
    xm=(x0+x1)/2
    line([(x0,y),(xm-32,y)],col,4,dash); line([(xm+32,y),(x1,y)],col,4,dash)
    o.append(f'<rect x="{xm-32}" y="{y-11}" width="64" height="22" fill="white" stroke="#111" stroke-width="2.5"/>')
    txt(xm,y-18,f"{name} {val}",13,"middle",bold=True)
def cap(x0,x1,y,name,val):
    xm=(x0+x1)/2; line([(x0,y),(xm-6,y)]); line([(xm+6,y),(x1,y)])
    for dx in (-6,6): line([(xm+dx,y-16),(xm+dx,y+16)],"#111",4)
    txt(xm,y-24,f"{name} {val}",13,"middle",bold=True)
def led(x0,x1,y,name,colname,fill,dash=True):              # horizontal, anode left, cathode right
    xm=(x0+x1)/2; line([(x0,y),(xm-14,y)],"#111",4,dash); line([(xm+14,y),(x1,y)],"#111",4,dash)
    o.append(f'<polygon points="{xm-14},{y-15} {xm-14},{y+15} {xm+14},{y}" fill="{fill}" stroke="#111" stroke-width="2"/>')
    line([(xm+14,y-15),(xm+14,y+15)],"#111",3)
    for k in (0,10): line([(xm-2+k,y-18),(xm+8+k,y-30)],"#111",1.6)
    txt(xm,y+36,f"{name} {colname}",13,"middle",bold=True); txt(xm-24,y-6,"A",10,"middle","#666"); txt(xm+24,y-6,"K",10,"middle","#666")

txt(30,42,"OpenALD Feather RP2040 v1.0 — wiring diagram (direct-mount wheel and switch, no controls board)",26,bold=True)
txt(30,70,"Every line is a hand-soldered wire (28–30 AWG silicone unless noted). Wire colours are suggestions. Dashed = optional. "
          "Designed from datasheets only — NOT built or tested on hardware.",14,col="#555")

# ---------------- Feather ----------------
FX0,FX1,FY0,FY1=700,1000,140,960
box(FX0,FY0,FX1-FX0,FY1-FY0,"Adafruit Feather RP2040",["#4884, components up,","USB-C at the dock end"],"#e8f4ea")
L={"3V3":230,"GND_QT":270,"SDA":310,"SCL":350,"EN":503,"JST-":700,"JST+":750}
R={"D24":230,"D25":270,"D4":310,"GND":430,"BAT":520,"A0":600,"USB":760,"STAT":860}
pin(FX0,L["3V3"],"STEMMA QT 3V3","in_l","red wire of the QT cable")
pin(FX0,L["GND_QT"],"STEMMA QT GND","in_l")
pin(FX0,L["SDA"],"STEMMA QT SDA","in_l","GP2 (Wire, i2c1)")
pin(FX0,L["SCL"],"STEMMA QT SCL","in_l","GP3")
pin(FX0,L["EN"],"EN","in_l","JP3.2 (left header)")
pin(FX0,L["JST+"],"JST PH BAT +","in_l")
pin(FX0,L["JST-"],"JST PH BAT −","in_l")
pin(FX1,R["D24"],"D24 = GP24","in_r","JP1.8")
pin(FX1,R["D25"],"D25 = GP25","in_r","JP1.7")
pin(FX1,R["D4"],"D4 = GP6","in_r","JP1.1 (NOT GPIO 4)")
pin(FX1,R["GND"],"GND","in_r","JP1.13, the only GND pin")
pin(FX1,R["BAT"],"BAT (VBAT)","in_r","JP3.1 (left header)")
pin(FX1,R["A0"],"A0 = GP26 / ADC0","in_r","JP1.12")
pin(FX1,R["USB"],"USB (VBUS, 5 V)","in_r","JP3.3 (left header)")
pin(FX1,R["STAT"],"STAT tap (no pad)","in_r","STAT end of R2, case (25.92, 6.87)")
txt((FX0+FX1)/2,905,"on board: NeoPixel GP16 (battery level), red LED",12,"middle","#444")
txt((FX0+FX1)/2,922,"GP13, CHG LED, MCP73831 charger (200 mA).",12,"middle","#444")
txt((FX0+FX1)/2,939,"EN low = 3.3 V regulator off.",12,"middle","#444")
txt((FX0+FX1)/2,800,"JST+ = BAT, JST− = GND",12,"middle","#444")
txt((FX0+FX1)/2,816,"(joined on the Feather)",12,"middle","#444")

# ---------------- FM module ----------------
MX0,MX1=70,380
box(MX0,140,MX1-MX0,250,"RDA5807M FM module",["26.9 × 26.9 mm, 3.5 mm jack on board","I2C 0x10 / 0x11, 3.3 V","headphone cable = antenna"],"#eef0ff")
for k,lab,col in [("3V3","VCC","#d22"),("GND_QT","GND","#111"),("SDA","SDA","#27c"),("SCL","SCL","#d8b800")]:
    pin(MX1,L[k],lab,"in_r"); line([(MX1,L[k]),(FX0,L[k])],col)
txt((MX1+FX0)/2,L["3V3"]-14,"STEMMA QT cable #4210, one end cut",12.5,"middle","#444")
txt(MX0+10,376,"No I2C found? add 4.7k SDA→3V3, SCL→3V3",11.5,col="#a40")

# ---------------- switch ----------------
SX0,SX1,SY0,SY1=70,380,410,590
box(SX0,SY0,SX1-SX0,SY1-SY0,"SS-12F16 slide switch",["left-wall groove, no screws","knob at the USB end = OFF"],"#e6eefb")
OFFY=545
# symbol (left part of the box): common pole -> EN, throw 1 (OFF end) -> GND, throw 2 (ON end) n.c.
px=110; line([(px,L["EN"]),(SX1,L["EN"])],"#111",3); dot(px,L["EN"],"#111")
line([(px,L["EN"]),(175,OFFY-6)],"#111",3)
o.append(f'<circle cx="180" cy="{OFFY}" r="4.5" fill="white" stroke="#111" stroke-width="2"/>'); line([(185,OFFY),(SX1,OFFY)],"#111",3)
o.append(f'<circle cx="180" cy="{OFFY+28}" r="4.5" fill="white" stroke="#111" stroke-width="2"/>'); txt(192,OFFY+32,"ON-end lug: not connected",11,col="#666")
txt(90,OFFY+8,"shown OFF",10.5,col="#666")
pin(SX1,L["EN"],"middle lug (common)","above_r"); pin(SX1,OFFY,"OFF-end lug","above_r")
line([(SX1,L["EN"]),(FX0,L["EN"])],"#f80")
txt((SX1+FX0)/2,L["EN"]-12,"EN wire (left channel → deck slot)",12.5,"middle","#444")

# ---------------- battery ----------------
BX0,BX1,BY0,BY1=70,380,610,790
box(BX0,BY0,BX1-BX0,BY1-BY0,"18650 holder BH-18650-PC",["protected button-top cell","+ at the USB end, − at the jack end"],"#f6eee0")
bx=120; line([(bx,L["JST-"]),(BX1,L["JST-"])],"#111",3); line([(bx,L["JST-"]),(bx,718)],"#111",3)
line([(bx-11,718),(bx+11,718)],"#111",7); line([(bx-22,730),(bx+22,730)],"#111",4)
line([(bx,730),(bx,L["JST+"]),(BX1,L["JST+"])],"#d22",3)
txt(bx+20,714,"−",16,bold=True); txt(bx+30,748,"+",16,bold=True)
pin(BX1,L["JST+"],"+","in_r"); pin(BX1,L["JST-"],"−","in_r")
line([(BX1,L["JST+"]),(FX0,L["JST+"])],"#d22"); line([(BX1,L["JST-"]),(FX0,L["JST-"])],"#111")
txt(630,L["JST-"]-12,"JST PH #261",12.5,"middle","#444"); txt(470,L["JST+"]+24,"JST PH cable #261 (cut): black −, red +",12.5,"middle","#444")
# OFF lug -> splice on the battery - lead
SPX=560; line([(SX1,OFFY),(SPX,OFFY),(SPX,L["JST-"])],"#111"); dot(SPX,L["JST-"])
txt(SPX-10,L["JST-"]-58,"splice in the left",12,"end","#444"); txt(SPX-10,L["JST-"]-42,"channel (heat-shrink):",12,"end","#444")
txt(SPX-10,L["JST-"]-26,"OFF lug → black lead",12,"end","#444")

# ---------------- GND bus (right channel splice) ----------------
GBX=1745
o.append(f'<rect x="{GBX-7}" y="345" width="14" height="425" rx="6" fill="#444"/>')
txt(1790,318,"GND splice",13,"end",bold=True); txt(1790,335,"(heat-shrink)",11,"end","#444")
line([(FX1,R["GND"]),(GBX,R["GND"])],"#111"); txt(1080,R["GND"]-10,"GND (one wire to the Feather's GND pin)",12.5,col="#444")

# ---------------- wheel ----------------
WX0,WX1=1400,1690
box(WX0,140,WX1-WX0,250,"Mitsumi SIQ-02FVS3 wheel",["glued in the frame cradle","tab order USB end → top: B, C, S, A","S closes to C when pushed"],"#e6eefb")
for k,lab,col in [("D24","A","#3a3"),("D25","B","#1a8a7a"),("D4","S (push)","#b06a1a")]:
    pin(WX0,R[k],lab,"in_l"); line([(FX1,R[k]),(WX0,R[k])],col)
pin(WX1,350,"C (common)","in_r"); line([(WX1,350),(GBX,350)],"#111")
txt(1200,R["D24"]-12,"internal pull-ups, no RC filter",12.5,"middle","#444")

# ---------------- battery divider ----------------
rect(1080,470,630,180,"#f5f5f5",rx=8,stroke="#888"); txt(1095,490,"Battery divider — inline in heat-shrink (needed for the battery gauge)",13,bold=True)
NX=1330
resistor(FX1,NX,R["BAT"],"R1","220k","#c33"); dot(NX,R["BAT"])
resistor(NX,GBX,R["BAT"],"R2","220k")
line([(NX,R["BAT"]),(NX,R["A0"])],"#777"); dot(NX,R["A0"],"#777")
line([(FX1,R["A0"]),(NX,R["A0"])],"#777"); cap(NX,GBX,R["A0"],"C1","100 nF")
txt(1095,640,"A0 = VBAT / 2   (≈ 9.5 µA always, also when switched off)",12,col="#444")

# ---------------- optional charge LEDs ----------------
rect(1080,680,630,220,"#fff6f6",dash=True,rx=8,stroke="#b44"); txt(1095,700,"OPTIONAL dock-visible charge LEDs (3 mm, top-half sockets) — hardware only",13,bold=True)
SN=1440
resistor(FX1,1230,R["USB"],"R3","1.5k","#d22",dash=True); led(1230,SN,R["USB"],"D1","red “CHG”","#f55"); dot(SN,R["USB"],"#a0a")
resistor(SN,1580,R["USB"],"R4","1.5k","#111",dash=True); led(1580,GBX,R["USB"],"D2","green “FULL”","#3c3")
line([(FX1,R["STAT"]),(SN,R["STAT"]),(SN,R["USB"])],"#a0a",4,True)
txt(1100,R["STAT"]-10,"STAT tap: 32–36 AWG enamel / wire-wrap",12.5,col="#444")
txt(1095,885,"Charging: STAT low → red on.  Full: STAT high → green on.  On battery (no USB): both off.",12,col="#444")

# ---------------- notes ----------------
ny=1000
txt(30,ny,"Notes",18,bold=True)
notes=["Polarity: check the + mark next to the Feather's JST PH socket before plugging the battery in. Red = holder + pin (USB end).",
 "Switch: before soldering, check with a meter which outer lug connects to the middle lug with the knob at the OFF (USB) end; that lug goes to GND.",
 "Wheel: check the A / B / S / C tab markings on your part's datasheet drawing. If A and B are swapped, the wheel just counts the other way (swap PIN_ENC_A / PIN_ENC_B).",
 "Use the silkscreen names: D4 is RP2040 GPIO 6 on this board. The firmware uses GPIO numbers 24, 25, 6, 26 (A0), 2/3 (I2C), 16 (NeoPixel).",
 "With the switch OFF (EN low) the 3.3 V rail is off: Feather, FM module and NeoPixel are unpowered. Charging still works (MCP73831 runs from VBUS).",
 "No wheel-push battery check with the switch OFF (the single board can; the Feather cannot). The firmware flashes the level at power-on and on a short press.",
 "Wire lengths ~120 mm per lead; route JP1/JP3 wires down the right channel slot, the battery and EN wires up the left channel, as in the README.",
 "Part numbers, prices and sources: docs/BOM.md. Pin table: docs/pin_map.md. KiCad schematic: docs/wiring_schematic/ (ERC-checked)."]
for i,n in enumerate(notes): txt(40,ny+30+i*26,"• "+n,14)
o.append("</svg>")
open(OUT+".svg","w").write("\n".join(o))
import cairosvg; cairosvg.svg2png(url=OUT+".svg",write_to=OUT+".png",output_width=W)
print("wrote",os.path.relpath(OUT+".svg",ROOT),os.path.relpath(OUT+".png",ROOT))
