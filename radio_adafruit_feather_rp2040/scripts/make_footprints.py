"""Project footprints: copies the single-board Mitsumi wheel and SK-12E12 footprints/3D meshes and adds the
wire-pad row and the frame peg hole."""
import os,shutil,uuid
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
OUT=os.path.join(ROOT,"kicad","openald_fctl.pretty"); M3D=os.path.join(ROOT,"kicad","openald_fctl.3dshapes")
SRC=os.path.join(ROOT,"ref","single_board")
os.makedirs(OUT,exist_ok=True); os.makedirs(M3D,exist_ok=True)
for f in ("Mitsumi_SIQ-02FVS3.kicad_mod","SW_Slide_SPDT_Angled_HRO_SK-12E12-G5.kicad_mod"):
    t=open(os.path.join(SRC,f)).read().replace("${KIPRJMOD}/openals.3dshapes/","${KIPRJMOD}/openald_fctl.3dshapes/").replace("${KIPRJMOD}/openald.3dshapes/","${KIPRJMOD}/openald_fctl.3dshapes/")
    open(os.path.join(OUT,f),"w").write(t)
for f in ("SIQ-02FVS3.wrl","SW_Slide_HRO_SK-12E12-G5.wrl"): shutil.copy(os.path.join(SRC,f),os.path.join(M3D,f))
def U(): return str(uuid.uuid4())
def fp(name,descr,body,attr="through_hole"):
    s=f'(footprint "{name}" (version 20240108) (generator "openald_gen") (layer "F.Cu")\n  (descr "{descr}")\n  (attr {attr})\n'
    s+=f'  (property "Reference" "REF**" (at 0 -2.2 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
    s+=f'  (property "Value" "{name}" (at 0 2.2 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))\n'
    s+=body+")\n"; open(os.path.join(OUT,name+".kicad_mod"),"w").write(s)
# 9 wire pads, 1.8 mm pitch along +Y (pad 1 at origin), 1.5 mm pads, 0.9 mm holes (26-28 AWG)
b=""
for i in range(9):
    sh="rect" if i==0 else "circle"
    b+=f'  (pad "{i+1}" thru_hole {sh} (at 0 {i*1.8:.3f}) (size 1.5 1.5) (drill 0.9) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'
b+=f'  (fp_rect (start -0.95 -0.95) (end 0.95 {8*1.8+0.95:.3f}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{U()}"))\n'
fp("WirePads_1x09_P1.80mm","9 wire solder pads, 1.8 mm pitch, 0.9 mm holes",b)
b=f'  (pad "" np_thru_hole circle (at 0 0) (size 2.1 2.1) (drill 2.1) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'
b+=f'  (fp_circle (center 0 0) (end 1.1 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd") (uuid "{U()}"))\n'
fp("PegHole_2.1mm","NPTH 2.1 mm for a printed 1.9 mm locating peg",b)
print("footprints:",sorted(os.listdir(OUT)))
