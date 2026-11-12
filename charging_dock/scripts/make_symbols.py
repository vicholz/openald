"""Dock project symbol library (openald.kicad_sym): HUSB238, AO4407A, SY8205FCC, SY6280AAC, 16-pin USB-C plug."""
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/openald.kicad_sym")
def pin(typ,name,num,x,y,ang,length=2.54,hide=False):
    h=" hide" if hide else ""
    return f'      (pin {typ} line (at {x} {y} {ang}) (length {length}){h} (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))\n'
def prop(k,v,x,y,hide=False):
    h=" (hide yes)" if hide else ""
    return f'    (property "{k}" "{v}" (at {x} {y} 0) (effects (font (size 1.27 1.27)){h}))\n'
def sym(name,ref,val,fp,ds,w,h,pins,desc):
    s=f'  (symbol "{name}" (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
    s+=prop("Reference",ref,0,h/2+1.27)+prop("Value",val,0,-h/2-1.27)+prop("Footprint",fp,0,-h/2-3.81,True)+prop("Datasheet",ds,0,0,True)+prop("Description",desc,0,0,True)
    s+=f'    (symbol "{name}_0_1"\n      (rectangle (start {-w/2} {h/2}) (end {w/2} {-h/2}) (stroke (width 0.254) (type default)) (fill (type background)))\n    )\n'
    s+=f'    (symbol "{name}_1_1"\n'+"".join(pins)+'    )\n  )\n'
    return s
lib='(kicad_symbol_lib (version 20231120) (generator "openald_gen") (generator_version "9.0")\n'
W,H=15.24,15.24; L=-W/2-2.54; R=W/2+2.54
lib+=sym("HUSB238","U","HUSB238","Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.55x2.48mm","https://www.lcsc.com/datasheet/C7471904.pdf",W,H,[
    pin("power_in","VIN","1",0,H/2+2.54,270),
    pin("power_in","GND","11",0,-H/2-2.54,90),
    pin("bidirectional","CC1","4",L,5.08,0), pin("bidirectional","CC2","5",L,2.54,0),
    pin("bidirectional","D+","2",L,-2.54,0), pin("bidirectional","D-","3",L,-5.08,0),
    pin("open_collector","GATE","10",R,5.08,180), pin("passive","ISET","9",R,2.54,180), pin("passive","VSET","8",R,0,180),
    pin("bidirectional","SDA","6",R,-2.54,180), pin("input","SCL","7",R,-5.08,180)],
    "USB PD sink controller, up to 20 V / 5 A, resistor-set voltage/current, open-drain GATE for an external P-FET")
W,H=10.16,10.16; L=-W/2-2.54; R=W/2+2.54
lib+=sym("AO4407A","Q","AO4407A","Package_SO:SOIC-8_3.9x4.9mm_P1.27mm","https://www.lcsc.com/datasheet/C16072.pdf",W,H,[
    pin("passive","S","1",L,2.54,0), pin("passive","S","2",L,2.54,0,hide=True), pin("passive","S","3",L,2.54,0,hide=True),
    pin("input","G","4",0,-H/2-2.54,90),
    pin("passive","D","5",R,2.54,180), pin("passive","D","6",R,2.54,180,hide=True), pin("passive","D","7",R,2.54,180,hide=True), pin("passive","D","8",R,2.54,180,hide=True)],
    "P-channel MOSFET -30 V -12 A, SOIC-8")
W,H=15.24,12.7; L=-W/2-2.54; R=W/2+2.54
lib+=sym("SY8205FCC","U","SY8205FCC","Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm","https://www.lcsc.com/datasheet/C111875.pdf",W,H,[
    pin("power_in","IN","7",L,5.08,0), pin("passive","IN","8",L,5.08,0,hide=True),
    pin("input","EN","3",L,0,0), pin("passive","SS","4",L,-5.08,0),
    pin("passive","BS","1",R,5.08,180), pin("power_out","LX","2",R,2.54,180), pin("input","FB","5",R,-2.54,180), pin("power_out","VCC","6",R,-5.08,180),
    pin("power_in","GND","9",0,-H/2-2.54,90)],
    "Synchronous buck 4.5-30 V in, 5 A, 500 kHz, Vref 0.6 V (SOIC-8 with exposed pad = GND)")
W,H=10.16,7.62; L=-W/2-2.54; R=W/2+2.54
lib+=sym("SY6280AAC","U","SY6280AAC","Package_TO_SOT_SMD:SOT-23-5","https://www.lcsc.com/datasheet/C55136.pdf",W,H,[
    pin("power_in","IN","5",L,2.54,0), pin("input","EN","4",L,-2.54,0),
    pin("power_out","OUT","1",R,2.54,180), pin("passive","ISET","3",R,-2.54,180),
    pin("power_in","GND","2",0,-H/2-2.54,90)],
    "Current-limited power distribution switch 2.4-5.5 V, Ilim = 6800/Rset (A, ohm)")
W,H=12.7,22.86; L=-W/2-2.54; R=W/2+2.54
pl=[pin("passive","VBUS",n,R,8.89,180,hide=(n!="A4")) for n in ("A4","A9","B4","B9")]
pl+=[pin("passive","GND",n,0,-H/2-2.54,90,hide=(n!="A1")) for n in ("A1","A12","B1","B12")]
pl+=[pin("passive","SHIELD","S1",-5.08,-H/2-2.54,90)]
for nm,n,y in (("CC","A5",6.35),("VCONN","B5",3.81),("D+","A6",1.27),("D-","A7",-1.27),("D+","B6",-3.81),("D-","B7",-6.35),("SBU1","A8",-8.89)):
    pl.append(pin("bidirectional",nm,n,R,y,180))
pl.append(pin("bidirectional","SBU2","B8",L,-8.89,0))
lib+=sym("USB_C_Plug_16P","J","USB_C_Plug_16P","openald:USB_C_Plug_HX_TYPE-C-M-16P_Vertical","https://www.lcsc.com/datasheet/C55200592.pdf",W,H,pl,
    "USB Type-C plug, 16 contacts (vertical PCB mount)")
lib+=")\n"
open(OUT,"w").write(lib); print("ok")
