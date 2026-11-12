"""Generate custom footprints + simple VRML 3D models for parts not in the KiCad library."""
import math,uuid,os
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/kicad/openald.pretty"
M3D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/kicad/openald.3dshapes"
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

# ---------- RRD-102V2.0 RDA5807M module (11.0 x 11.0 mm, castellated, 2.0 mm pitch) ----------
b=""
for i in range(5):
    b+=smd(str(i+1), 5.3, 4-2*i, 1.8,1.2)       # right column, pin1 bottom-right (datasheet top view)
    b+=smd(str(i+6),-5.3,-4+2*i, 1.8,1.2)       # left column, pin6 top-left
b+=rect(-5.5,-5.5,5.5,5.5,"F.Fab",0.1)
b+=rect(-6.45,-5.85,6.45,5.85,"F.CrtYd",0.05)
b+=line(-5.6,-5.6,5.6,-5.6,"F.SilkS")+line(-5.6,5.6,5.6,5.6,"F.SilkS")
b+=circle(6.9,4.0,0.25,"F.SilkS",0.3)   # pin-1 dot
b+=f'  (fp_text user "RDA5807M" (at 0 0 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))\n'
b+=model("RRD-102_RDA5807M_Module")
fp("RRD-102_RDA5807M_Module","RRD-102V2.0 FM module (RDA5807M), 11x11mm castellated, 2.0mm pitch. Pin1=GND bottom-right (top view)",b,ref_y=-6.6,val_y=6.6)

# ---------- Mitsumi SIQ-02FVS3 thumb-wheel encoder + push (origin = wheel centre) ----------
b=""
for num,x in (("A",-4.0),("S",-1.475),("C",1.475),("B",4.0)):
    b+=smd(num,x,7.7,1.3,1.2,shape="rect")
for x in (-5.4,5.4):
    for y in (1.3,5.4):
        b+=smd("MP",x,y,1.2,1.3,shape="rect")
b+=smd("MP",-3.25,-3.25,0.85,1.2,rot=45,shape="rect")
b+=smd("MP", 3.25,-3.25,0.85,1.2,rot=-45,shape="rect")
b+=npth(-3.0,4.5,1.6)+npth(3.0,4.5,1.6)
b+=rect(-5.15,-3.85,5.15,7.25,"F.Fab",0.1)+circle(0,0,7.25,"F.Fab",0.1)
b+=rect(-6.25,-4.45,6.25,8.55,"F.CrtYd",0.05)
b+=line(-5.3,7.0,-5.3,6.3,"F.SilkS")+line(5.3,7.0,5.3,6.3,"F.SilkS")
b+=f'  (fp_text user "wheel overhangs board edge" (at 0 -8.3 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.6 0.6) (thickness 0.1))))\n'
b+=model("SIQ-02FVS3")
fp("Mitsumi_SIQ-02FVS3","Mitsumi SIQ-02FVS3 SMD thumbwheel rotary encoder with push (slide) switch, 15 detents, land pattern per datasheet",b,ref_y=0,val_y=9.6)

# ---------- HRO SK-12E12-G5 right-angle slide switch (SPDT) ----------
# Datasheet LT-DR-SK12E12G5-00: body 12.9 x 5.6 x 6.0 (H); knob 3.5 (along travel) x 2.5 thick, 5.0 long from the
# body face, centre 3.5 above the seating plane; travel 2.5; 3 pins 0.7x0.4 at 3.0 pitch in the body centre line;
# 2 frame tabs 0.4 thick at 12.5 mm. Origin = centre pin; knob points to +Y.
b=""
for num,x in (("1",-3.0),("2",0.0),("3",3.0)):
    b+=tht(num,x,0,1.7,1.0,"rect" if num=="1" else "circle")
for x in (-6.25,6.25):
    b+=f'  (pad "" thru_hole oval (at {x:.3f} 0) (size 1.3 2.1) (drill oval 0.7 1.5) (layers "*.Cu" "*.Mask") (uuid "{U()}"))\n'
b+=rect(-6.45,-2.8,6.45,2.8,"F.Fab",0.1)+rect(-3.0,2.8,0.5,7.8,"F.Fab",0.1)
b+=line(-6.55,-2.9,6.55,-2.9,"F.SilkS")+line(-6.55,2.9,-3.2,2.9,"F.SilkS")+line(3.2,2.9,6.55,2.9,"F.SilkS")
_cy=[(-7.2,-3.3),(7.2,-3.3),(7.2,3.3),(3.3,3.3),(3.3,8.3),(-3.3,8.3),(-3.3,3.3),(-7.2,3.3)]
for i in range(len(_cy)): b+=line(*_cy[i],*_cy[(i+1)%len(_cy)],"F.CrtYd",0.05)
b+=model("SW_Slide_HRO_SK-12E12-G5")
fp("SW_Slide_SPDT_Angled_HRO_SK-12E12-G5","HRO SK-12E12-G5 right-angle SPDT slide switch, knob 3.5x2.5x5mm, travel 2.5mm, pins P3.0mm, tabs 12.5mm (datasheet LT-DR-SK12E12G5-00)",b,attr="through_hole",ref_y=-4.0,val_y=9.0)
for old in ("LED_D5.0mm_RGB_CC_XL-A504RGBW.kicad_mod","LED_D5.0mm_RGB_CC_FlatTop_TJ-L5FP.kicad_mod"):   # rev 3: RGB LED replaced by a 3x 0603 level bar
    if os.path.exists(os.path.join(OUT,old)): os.remove(os.path.join(OUT,old))

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
# VRML coords: x right, y = -footprint y, z up
wrl("RRD-102_RDA5807M_Module",[box((0,0,0.4),(11,11,0.8),(0.1,0.55,0.2)),box((0,1,1.3),(5,5,1.0),(0.08,0.08,0.08)),box((0,-3.5,1.2),(6,1.8,0.8),(0.8,0.8,0.8))])
wrl("SIQ-02FVS3",[box((0,-1.7,1.0),(10.3,11.1,2.0),(0.75,0.75,0.78)),cyl((0,0,3.0),7.25,2.0,"z",(0.12,0.12,0.12)),cyl((0,0,3.0),3.5,2.05,"z",(0.3,0.3,0.3))])
wrl("SW_Slide_HRO_SK-12E12-G5",[box((0,0,3.0),(12.9,5.6,6.0),(0.78,0.78,0.8)),        # VRML y = -footprint y
      box((-1.25,-5.3,3.5),(3.5,5.0,2.5),(0.1,0.1,0.1))])                           # knob, shown in pos.1 (OFF)
for old in ("LED_RGB_5mm_XL-A504_on_spacer.wrl","LED_RGB_3mm_bent.wrl","LED_RGB_5mm_FlatTop_on_spacer.wrl","EVQP7A.wrl"):   # EVQP7A: button SW2 removed 2026-11-11
    if os.path.exists(os.path.join(M3D,old)): os.remove(os.path.join(M3D,old))
# generic PJ-320D style jack (mouth toward -x in footprint coords)
wrl("PJ-320D-4A",[box((-0.2,0,2.5),(12.0,6.1,5.0),(0.1,0.1,0.1)),cyl((-7.3,0,2.5),2.5,2.2,"x",(0.1,0.1,0.1))])
wrl("USB_C_HRO_31-M-12",[box((0,0,1.63),(8.94,7.3,3.26),(0.8,0.8,0.82))])
print("footprints written:",os.listdir(OUT))
