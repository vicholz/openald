"""Project symbol library: SIQ-02FVS3 thumbwheel encoder (same symbol as the single-board radio)."""
import os
OUT=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"kicad","openald_fctl.kicad_sym")
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
W,H=10.16,10.16; L=-W/2-2.54; R=W/2+2.54
lib+=sym("SIQ-02FVS3","SW","SIQ-02FVS3","openald_fctl:Mitsumi_SIQ-02FVS3","https://datasheet.lcsc.com/datasheet/pdf/7bff72617d5a3503f5ed21ab02a77dea.pdf",W,H,[
    pin("passive","A","A",L,2.54,0), pin("passive","B","B",L,-2.54,0), pin("passive","S","S",R,2.54,180), pin("passive","C","C",R,-2.54,180)],
    "Thumbwheel rotary encoder (A/B to common C) with push switch S (to C)")
lib+=")\n"
open(OUT,"w").write(lib); print("ok")
