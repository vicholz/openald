"""Generate custom footprints + simple VRML 3D models for parts not in the KiCad library."""
import math,uuid,os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/openald.pretty")
M3D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/openald.3dshapes")
def U(): return str(uuid.uuid4())
def line(x1,y1,x2,y2,layer,w=0.12):
    return f'  (fp_line (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (layer "{layer}") (uuid "{U()}"))\n'
def rect(x1,y1,x2,y2,layer,w=0.12):
    return line(x1,y1,x2,y1,layer,w)+line(x2,y1,x2,y2,layer,w)+line(x2,y2,x1,y2,layer,w)+line(x1,y2,x1,y1,layer,w)
def circle(cx,cy,r,layer,w=0.12):
    return f'  (fp_circle (center {cx:.3f} {cy:.3f}) (end {cx+r:.3f} {cy:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{U()}"))\n'
def text(kind,val,x,y,layer,hide=False):
    h=" (hide yes)" if hide else ""
    return f'  (property "{kind}" "{val}" (at {x:.3f} {y:.3f} 0) (layer "{layer}"){h} (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))\n'
def smd(num,x,y,w,h,rot=0,shape="roundrect"):
    rr=' (roundrect_rratio 0.15)' if shape=="roundrect" else ''
    return f'  (pad "{num}" smd {shape} (at {x:.3f} {y:.3f} {rot}) (size {w} {h}) (layers "F.Cu" "F.Paste" "F.Mask"){rr} (uuid "{U()}"))\n'
def tht(num,x,y,d,drill,shape="circle"):
    return f'  (pad "{num}" thru_hole {shape} (at {x:.3f} {y:.3f}) (size {d} {d}) (drill {drill}) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'
def npth(x,y,d):
    return f'  (pad "" np_thru_hole circle (at {x:.3f} {y:.3f}) (size {d} {d}) (drill {d}) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'
def model(name,off=(0,0,0),rot=(0,0,0)):
    return f'  (model "${{KIPRJMOD}}/openald.3dshapes/{name}.wrl" (offset (xyz {off[0]} {off[1]} {off[2]})) (scale (xyz 1 1 1)) (rotate (xyz {rot[0]} {rot[1]} {rot[2]})))\n'
def fp(name,descr,body,attr="smd",ref_y=-7,val_y=7):
    s=f'(footprint "{name}" (version 20240108) (generator "openald_gen") (layer "F.Cu")\n  (descr "{descr}")\n'
    s+=text("Reference","REF**",0,ref_y,"F.SilkS")+text("Value",name,0,val_y,"F.Fab")
    s+=f'  (attr {attr})\n'+body+')\n'
    open(os.path.join(OUT,name+".kicad_mod"),"w").write(s)

os.makedirs(OUT,exist_ok=True); os.makedirs(M3D,exist_ok=True)
def slot(num,x,y,cw,cl,dw,dl):
    return f'  (pad "{num}" thru_hole oval (at {x:.3f} {y:.3f}) (size {cw} {cl}) (drill oval {dw} {dl}) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'
# ---------- HX TYPE C-M 16P V-SMT vertical USB-C plug (LCSC C55200592), land pattern per the HX drawing (2020-08-24) ----------
# Component side view: top row (y-) A12 A9 A8 A7 A6 A5 A4 A1 left->right, bottom row (y+) B1 B4 B5 B6 B7 B8 B9 B12.
# Pads 0.35 x 1.20 on 0.80 pitch, rows 2.28 apart (3.48 overall); shell legs in 2 plated slots 1.20 x 2.10 copper,
# 0.80 x 1.70 drill, 7.96 apart.  Drawing is for a 0.8 mm board; on 1.6 mm the legs do not protrude (solder from the top).
b=""
xs=[-2.8,-2.0,-1.2,-0.4,0.4,1.2,2.0,2.8]
for n,x in zip(("A12","A9","A8","A7","A6","A5","A4","A1"),xs): b+=smd(n,x,-1.14,0.35,1.2,shape="rect")
for n,x in zip(("B1","B4","B5","B6","B7","B8","B9","B12"),xs): b+=smd(n,x,1.14,0.35,1.2,shape="rect")
b+=slot("S1",-3.98,0,1.2,2.1,0.8,1.7)+slot("S1",3.98,0,1.2,2.1,0.8,1.7)
b+=rect(-4.125,-1.2,4.125,1.2,"F.Fab",0.1)
b+=rect(-4.9,-2.1,4.9,2.1,"F.CrtYd",0.05)
b+=line(-3.4,-1.9,-4.7,-1.9,"F.SilkS")+line(3.4,-1.9,4.7,-1.9,"F.SilkS")+line(-3.4,1.9,-4.7,1.9,"F.SilkS")+line(3.4,1.9,4.7,1.9,"F.SilkS")
b+=f'  (fp_text user "A1" (at 3.4 -2.8 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.15))))\n'
b+=model("USB_C_Plug_HX_16P_V")
fp("USB_C_Plug_HX_TYPE-C-M-16P_Vertical","HX TYPE C-M 16P V-SMT vertical USB-C plug, 11.6 mm tall, shell 8.25x2.40, land pattern per HX drawing (t=0.8 board)",b,ref_y=-3.2,val_y=3.2)
# ---------- Sunlord MWSA0604S 7.0 x 6.6 x 3.8 mm power inductor ----------
b=smd("1",-3.0,0,2.4,3.2)+smd("2",3.0,0,2.4,3.2)
b+=rect(-3.5,-3.3,3.5,3.3,"F.Fab",0.1)+rect(-4.45,-3.6,4.45,3.6,"F.CrtYd",0.05)
b+=line(-1.6,-3.45,1.6,-3.45,"F.SilkS")+line(-1.6,3.45,1.6,3.45,"F.SilkS")
b+=model("L_MWSA0604S")
fp("L_Sunlord_MWSA0604S","Sunlord MWSA0604S molded power inductor 7.0x6.6x3.8 mm (pads 2.4x3.2 at 6.0 mm)",b,ref_y=-4.4,val_y=4.4)
# ---------- VRML models (units: 1 = 2.54 mm in KiCad wrl); meshes only (KiCad ignores VRML primitives) ----------
def _shape(pts,faces,col):
    p=", ".join("%.4f %.4f %.4f"%(x/2.54,y/2.54,z/2.54) for x,y,z in pts)
    f=", ".join(" ".join(str(i) for i in fc)+" -1" for fc in faces)
    return ("Shape { appearance Appearance { material Material { diffuseColor %g %g %g } } "
            "geometry IndexedFaceSet { coord Coordinate { point [ %s ] } coordIndex [ %s ] } }\n")%(col[0],col[1],col[2],p,f)
def box(c,d,col):
    x,y,z=c; a,b,h=d[0]/2,d[1]/2,d[2]/2
    P=[(x+sx*a,y+sy*b,z+sz*h) for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)]
    F=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return _shape(P,F,col)
def cyl(c,r,h,axis,col,n=24):
    x,y,z=c; P=[]
    for end in (-h/2,h/2):
        for i in range(n):
            a=2*math.pi*i/n; u,v=r*math.cos(a),r*math.sin(a)
            P.append((x+u,y+v,z+end) if axis=="z" else (x+u,y+end,z+v) if axis=="y" else (x+end,y+u,z+v))
    F=[tuple(range(n))[::-1],tuple(range(n,2*n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    return _shape(P,F,col)
def wrl(name,shapes):
    open(os.path.join(M3D,name+".wrl"),"w").write("#VRML V2.0 utf8\n"+"".join(shapes))
wrl("USB_C_Plug_HX_16P_V",[box((0,0,0.9),(7.96,3.48,1.8),(0.1,0.1,0.1)),box((0,0,1.8+4.9),(8.25,2.40,9.8),(0.8,0.8,0.82))])
wrl("L_MWSA0604S",[box((0,0,1.9),(7.0,6.6,3.8),(0.25,0.25,0.25))])
wrl("USB_C_HRO_31-M-12",[box((0,0,1.63),(8.94,7.3,3.26),(0.8,0.8,0.82))])
print("footprints:",sorted(os.listdir(OUT)))
