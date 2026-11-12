#!/usr/bin/env python3
"""Re-render the PCB preview PNGs (kicad-cli 3D render) and the schematic PDF/PNG."""
import subprocess, os
from PIL import Image
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); K=f"{ROOT}/kicad"; P=f"{ROOT}/previews"
PCB=f"{K}/openald.kicad_pcb"
def render(out,side,w,h,zoom=1.0,extra=()):
    subprocess.run(["kicad-cli","pcb","render","-o",out,"--side",side,"-w",str(w),"-h",str(h),"--quality","high","--background","opaque","--zoom",str(zoom),*extra,PCB],check=True,capture_output=True)
# board is 38 x 87 mm portrait; at zoom 1 kicad fits the board (with margin) into the frame
render(f"{P}/pcb_top.png","top",1008,728)
render(f"{P}/pcb_bottom.png","bottom",1008,728)
big="/tmp/rr/top_big.png"; render(big,"top",2400,5200,1.0)
bigb="/tmp/rr/bot_big.png"; render(bigb,"bottom",2400,5200,1.0)
def board_box(path):
    im=Image.open(path).convert("RGB"); bg=im.getpixel((2,2)); W,H=im.size
    # board area = rows/cols that differ from the background (includes overhanging parts; fine for crops)
    import numpy as np
    a=np.asarray(im).astype(int); m=(abs(a-np.array(bg)).sum(2)>30)
    ys=np.where(m.any(1))[0]; xs=np.where(m.any(0))[0]; return im,xs.min(),xs.max(),ys.min(),ys.max()
im,x0,x1,y0,y1=board_box(big)
s=(y1-y0)/87.0                                   # px per mm (height is the board outline: no part overhangs top/bottom much)
cx=(x0+x1)/2-19*s                                 # board x=0 in px (board centred; wheel/switch overhang is roughly symmetric to jack? use centre)
def crop(img,bx0,by0,bx1,by1,out,flip=False):
    if flip: bx0,bx1=38-bx1,38-bx0
    img.crop((int(cx+bx0*s),int(y0+by0*s),int(cx+bx1*s),int(y0+by1*s))).save(out)
crop(im,14,3,34,18,f"{P}/pcb_closeup_led_bar.png")
crop(im,14,64,38,87,f"{P}/pcb_closeup_usb_serial.png")
crop(im,0,64,38,87,f"{P}/pcb_closeup_reverse_polarity.png")
imb,bx0,bx1,by0,by1=board_box(bigb); 
crop(imb,0,0,38,20,f"{P}/pcb_closeup_polarity_marks_bottom.png",flip=True)
subprocess.run(["kicad-cli","sch","export","pdf","-o",f"{ROOT}/docs/openald-schematic.pdf",f"{K}/openald.kicad_sch"],check=True,capture_output=True)
subprocess.run(["pdftoppm","-r","110","-png","-singlefile",f"{ROOT}/docs/openald-schematic.pdf",f"{P}/schematic-1"],check=True)
print("rendered")
