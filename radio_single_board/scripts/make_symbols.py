"""Project symbol library: RRD-102 module, FS8205A dual NMOS, SIQ-02FVS3 encoder."""
import os
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/kicad/openald.kicad_sym"
def pin(typ,name,num,x,y,ang,length=2.54):
    return f'      (pin {typ} line (at {x} {y} {ang}) (length {length}) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))\n'
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
# RRD-102: left side inputs, right side outputs
W,H=15.24,15.24
L=-W/2-2.54; R=W/2+2.54
lib+=sym("RRD-102","U","RRD-102 (RDA5807M)","openald:RRD-102_RDA5807M_Module","https://aitendo3.sakura.ne.jp/aitendo_data/product_img/audio/radio_module/RDA5807H/RDA5807M.pdf",W,H,[
    pin("power_in","VDD","10",0,H/2+2.54,270),
    pin("power_in","GND","1",0,-H/2-2.54,90),
    pin("bidirectional","SDA","6",L,5.08,0),
    pin("input","SCL","7",L,2.54,0),
    pin("passive","FM_ANT","5",L,-2.54,0),
    pin("no_connect","RCLK","4",L,-5.08,0),
    pin("output","LOUT","3",R,5.08,180),
    pin("output","ROUT","2",R,2.54,180),
    pin("no_connect","GP2","8",R,-2.54,180),
    pin("no_connect","GP3","9",R,-5.08,180)],
    "RRD-102V2.0 FM stereo receiver module, RDA5807M, I2C, 32.768kHz crystal on module")
W,H=12.7,10.16; L=-W/2-2.54; R=W/2+2.54
lib+=sym("FS8205A","Q","FS8205A","Package_TO_SOT_SMD:SOT-23-6","https://datasheet.lcsc.com/datasheet/pdf/c060cb7baa8cc2b2d2a0ed3afa443ef8.pdf",W,H,[
    pin("passive","S1","1",L,2.54,0),
    pin("input","G1","6",L,-2.54,0),
    pin("passive","S2","3",R,2.54,180),
    pin("input","G2","4",R,-2.54,180),
    pin("passive","D12","2",-1.27,H/2+2.54,270),
    pin("passive","D12","5",1.27,H/2+2.54,270)],
    "Dual N-channel MOSFET, common drain, 20V 6A (Li-ion protection)")
W,H=10.16,10.16; L=-W/2-2.54; R=W/2+2.54
lib+=sym("SIQ-02FVS3","SW","SIQ-02FVS3","openald:Mitsumi_SIQ-02FVS3","https://datasheet.lcsc.com/datasheet/pdf/7bff72617d5a3503f5ed21ab02a77dea.pdf",W,H,[
    pin("passive","A","A",L,2.54,0),
    pin("passive","B","B",L,-2.54,0),
    pin("passive","S","S",R,2.54,180),
    pin("passive","C","C",R,-2.54,180)],
    "Thumbwheel rotary encoder (A/B to common C) with push/slide switch S (to C)")
lib+=")\n"
open(OUT,"w").write(lib); print("ok")
