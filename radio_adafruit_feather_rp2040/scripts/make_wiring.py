#!/usr/bin/env python3
"""Draw docs/wiring_diagram.svg (+ .png) for the direct-mount Feather RP2040 variant (no controls PCB):
every hand-soldered wire between the Feather RP2040, the SIQ-02FVS3 wheel, the SS-12F16 switch, the 18650 holder,
the RDA5807M module and the battery divider (t116u: no breakout, no Schottky, no extra LEDs). Pin numbers match firmware/openald_feather."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
ROOT=os.path.dirname(HERE); OUT=os.path.join(ROOT,"docs","wiring_diagram")
W,H=1800,1320
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

txt(30,42,"OpenALD Feather RP2040 v1.0 — wiring diagram (t116u: Feather's own USB-C is the bottom-end dock port)",26,bold=True)
txt(30,70,"Every line is a hand-soldered wire (28–30 AWG silicone unless noted). Wire colours are suggestions. No breakout, no Schottky, no JST or STEMMA QT plugs "
          "(no room at the walls). Designed from datasheets only — NOT built or tested on hardware.",14,col="#555")

# ---------------- Feather ----------------
FX0,FX1,FY0,FY1=700,1000,140,940
box(FX0,FY0,FX1-FX0,FY1-FY0,"Adafruit Feather RP2040",["#4884, components up, flat at the bottom end,","its USB-C = the dock port (case bottom face)"],"#e8f4ea")
L={"SDA":310,"SCL":350,"EN":503,"BAT":750}
R={"3V3":230,"D24":310,"D25":350,"D4":390,"GND":450,"A0":600}
pin(FX0,L["SDA"],"SDA = GP2","in_l","JP3.12 (left header)")
pin(FX0,L["SCL"],"SCL = GP3","in_l","JP3.11")
pin(FX0,L["EN"],"EN","in_l","JP3.2")
pin(FX0,L["BAT"],"BAT (VBAT)","in_l","JP3.1")
pin(FX1,R["3V3"],"3V3","in_r","JP1.14 (right header)")
pin(FX1,R["D24"],"D24 = GP24","in_r","JP1.8")
pin(FX1,R["D25"],"D25 = GP25","in_r","JP1.7")
pin(FX1,R["D4"],"D4 = GP6","in_r","JP1.1 (NOT GPIO 4)")
pin(FX1,R["GND"],"GND","in_r","JP1.13, the only GND pin")
pin(FX1,R["A0"],"A0 = GP26 / ADC0","in_r","JP1.12")
for i,t in enumerate(["on board, seen through the front-face holes:","CHG LED (amber, MCP73831 charger 200 mA),",
                      "red LED GP13, NeoPixel GP16 (battery level).","EN low = 3.3 V regulator off.","JST PH socket: leave EMPTY (BAT pad used)."]):
    txt((FX0+FX1)/2,820+i*17,t,12,"middle","#444")

# ---------------- rails under the Feather ----------------
VR,GR=975,1000          # VBAT rail, GND rail (drawn under the Feather; physically: wires in the side channels)
GBX=1745
o.append(f'<rect x="{GBX-7}" y="330" width="14" height="{GR-330+7}" rx="6" fill="#444"/>')
txt(1790,303,"GND splice",13,"end",bold=True); txt(1790,320,"(heat-shrink)",11,"end","#444")
line([(FX1,R["GND"]),(GBX,R["GND"])],"#111"); txt(1080,R["GND"]-10,"GND (one wire to the Feather's GND pad)",12.5,col="#444")

# ---------------- FM module ----------------
MX0,MX1=70,380
box(MX0,140,MX1-MX0,250,"RDA5807M FM module",["27.25 × 27.25 mm, flipped: flat side to the front face","I2C 0x10 / 0x11, 3.3 V","headphone cable = antenna"],"#eef0ff")
FMV,FMG=230,270
pin(MX1,FMV,"VCC","in_r"); pin(MX1,FMG,"GND","in_r")
for k,lab,col in [("SDA","SDA","#27c"),("SCL","SCL","#d8b800")]:
    pin(MX1,L[k],lab,"in_r"); line([(MX1,L[k]),(FX0,L[k])],col)
line([(MX1,FMV),(560,FMV),(560,115),(1040,115),(1040,R["3V3"]),(FX1,R["3V3"])],"#d22")
txt(800,108,"VCC wire over the Feather to its 3V3 pad",12.5,"middle","#444")
GLX=620; line([(MX1,FMG),(GLX,FMG)],"#111")
txt((MX1+FX0)/2+20,L["SCL"]+22,"4 wires from the FM header (pins cut back on the flat side)",12,"middle","#444")
txt(MX0+10,376,"No I2C found? add 4.7k SDA→3V3, SCL→3V3",11.5,col="#a40")

# ---------------- switch ----------------
SX0,SX1,SY0,SY1=70,380,410,590
box(SX0,SY0,SX1-SX0,SY1-SY0,"SS-12F16 slide switch",["left-wall groove, no screws","knob toward the USB end = OFF"],"#e6eefb")
OFFY=545
px=110; line([(px,L["EN"]),(SX1,L["EN"])],"#111",3); dot(px,L["EN"],"#111")
line([(px,L["EN"]),(175,OFFY-6)],"#111",3)
o.append(f'<circle cx="180" cy="{OFFY}" r="4.5" fill="white" stroke="#111" stroke-width="2"/>'); line([(185,OFFY),(SX1,OFFY)],"#111",3)
o.append(f'<circle cx="180" cy="{OFFY+28}" r="4.5" fill="white" stroke="#111" stroke-width="2"/>'); txt(192,OFFY+32,"ON-end lug: not connected",11,col="#666")
txt(90,OFFY+8,"shown OFF",10.5,col="#666")
pin(SX1,L["EN"],"middle lug (common)","above_r"); pin(SX1,OFFY,"OFF-end lug","above_r")
line([(SX1,L["EN"]),(FX0,L["EN"])],"#f80")
txt((SX1+FX0)/2,L["EN"]-12,"EN wire (left channel → deck slot)",12.5,"middle","#444")
line([(SX1,OFFY),(GLX,OFFY)],"#111")

# ---------------- battery ----------------
BX0,BX1,BY0,BY1=70,380,610,790
BM=700
box(BX0,BY0,BX1-BX0,BY1-BY0,"18650 holder BH-18650-PC",["protected button-top cell, under the deck","+ at the USB end, − at the jack end"],"#f6eee0")
bx=120; line([(bx,BM),(BX1,BM)],"#111",3); line([(bx,BM),(bx,718)],"#111",3)
line([(bx-11,718),(bx+11,718)],"#111",7); line([(bx-22,730),(bx+22,730)],"#111",4)
line([(bx,730),(bx,L["BAT"]),(BX1,L["BAT"])],"#d22",3)
txt(bx+20,714,"−",16,bold=True); txt(bx+30,748,"+",16,bold=True)
pin(BX1,L["BAT"],"+","in_r"); pin(BX1,BM,"−","in_r")
line([(BX1,L["BAT"]),(FX0,L["BAT"])],"#d22"); txt(540,L["BAT"]-10,"red: holder + pin → BAT pad",12.5,"middle","#444")
line([(BX1,BM),(GLX,BM)],"#111"); txt(470,BM-10,"black: holder − pin",12.5,"middle","#444")
txt(72,808,"holder PC pins trimmed, wires soldered on (joints in the floor relief holes)",11.5,col="#666")
# left GND splice: FM GND + switch OFF lug + battery − -> GND rail -> right splice
line([(GLX,FMG),(GLX,GR),(GBX,GR)],"#111"); dot(GLX,OFFY); dot(GLX,BM)
txt(GLX-8,GR-8,"GND: FM, switch OFF lug and battery − joined in the left channel, one wire to the right splice",11.5,"end","#444")
# VBAT rail for the divider
line([(FX0-40,L["BAT"]),(FX0-40,VR),(1180,VR)],"#c33"); dot(FX0-40,L["BAT"],"#c33")
txt(1175,VR-8,"VBAT to the divider (2nd wire on the BAT pad)",11.5,"end","#444")

# ---------------- wheel ----------------
WX0,WX1=1400,1690
box(WX0,140,WX1-WX0,250,"Mitsumi SIQ-02FVS3 wheel",["right wall, between the Feather and the FM","tab order USB end → top: B, C, S, A","S closes to C when pushed"],"#e6eefb")
for k,lab,col in [("D24","A","#3a3"),("D25","B","#1a8a7a"),("D4","S (push)","#b06a1a")]:
    pin(WX0,R[k],lab,"in_l"); line([(FX1,R[k]),(WX0,R[k])],col)
pin(WX1,350,"C (common)","in_r"); line([(WX1,350),(GBX,350)],"#111")
txt(1200,R["D24"]-12,"internal pull-ups, no RC filter",12.5,"middle","#444")

# ---------------- battery divider ----------------
rect(1080,500,630,180,"#f5f5f5",rx=8,stroke="#888"); txt(1095,520,"Battery divider — inline in heat-shrink (needed for the battery gauge)",13,bold=True)
NX=1330; DY=560
RX=1180; line([(RX,VR),(RX,DY)],"#c33"); resistor(RX,NX,DY,"R1","220k","#c33")
resistor(NX,GBX,DY,"R2","220k"); dot(NX,DY)
line([(NX,DY),(NX,R["A0"])],"#777"); dot(NX,R["A0"],"#777")
line([(FX1,R["A0"]),(NX,R["A0"])],"#777"); cap(NX,GBX,R["A0"],"C1","100 nF")
txt(1095,665,"A0 = VBAT / 2   (≈ 9.5 µA always, also when switched off)",12,col="#444")

# ---------------- LEDs ----------------
rect(1080,720,630,130,"#f4fff4",rx=8,stroke="#5a5"); txt(1095,742,"Status LEDs — nothing to wire",13,bold=True)
for i,t in enumerate(["The Feather's own CHG LED (charging, amber), red LED (GP13) and NeoPixel (GP16, battery",
                      "level) sit under light tunnels to holes in the front face, so charging is visible in the dock.",
                      "The battery display stays on the NeoPixel (not moved to the front)."]):
    txt(1095,766+i*20,t,12,col="#444")

# ---------------- notes ----------------
ny=1050
txt(30,ny,"Notes",18,bold=True)
notes=["Polarity: holder + pin (USB end) → BAT pad, − pin → GND. Check with a meter before inserting the cell; the JST socket stays empty.",
 "Switch: before soldering, check with a meter which outer lug connects to the middle lug with the knob at the OFF (USB-end) position; that lug goes to GND.",
 "Wheel: check the A / B / S / C tab markings on your part's datasheet drawing. If A and B are swapped, the wheel just counts the other way (swap PIN_ENC_A / PIN_ENC_B).",
 "Use the silkscreen names: D4 is RP2040 GPIO 6 on this board. The firmware uses GPIO numbers 24, 25, 6, 26 (A0), 2/3 (I2C), 16 (NeoPixel).",
 "With the switch OFF (EN low) the 3.3 V rail is off: Feather, FM module and NeoPixel are unpowered. Charging still works (MCP73831 runs from VBUS).",
 "No wheel-push battery check with the switch OFF (the single board can; the Feather cannot). The firmware flashes the level at power-on and on a short press.",
 "Wire lengths ~120 mm per lead; wires run in the side channels under the deck and come up through the deck slots, as in the README.",
 "Part numbers, prices and sources: docs/BOM.md. Pin table: docs/pin_map.md. KiCad schematic: docs/wiring_schematic/ (ERC-checked)."]
for i,n in enumerate(notes): txt(40,ny+30+i*26,"• "+n,14)
o.append("</svg>")
open(OUT+".svg","w").write("\n".join(o))
import cairosvg; cairosvg.svg2png(url=OUT+".svg",write_to=OUT+".png",output_width=W)
print("wrote",os.path.relpath(OUT+".svg",ROOT),os.path.relpath(OUT+".png",ROOT))
