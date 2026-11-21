#!/usr/bin/env python3
"""Cross-section previews from the assembly-pose meshes in /tmp/mi03fit (built by build.sh)."""
import trimesh, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
F='/tmp/mi03fit/'
parts=[('front_raw','#9db7d6','front shell'),('back_raw','#c8c8c8','back shell'),('frame_raw','mediumseagreen','battery frame'),('plungers_raw','orange','plungers'),
       ('cap_0','tomato','switch cap'),('ghost_pcb','darkgreen','PCB'),('ghost_front','black','LCD / buttons'),
       ('ghost_back_0','#7a7a7a','jack / USB-C / switch'),('ghost_holder','royalblue','18650 + holder'),('ghost_screws','gold','screws')]
def draw(ax, origin, normal, to2d):
    for n,c,lab in parts:
        m=trimesh.load(F+n+'.stl'); s=m.section(plane_origin=origin, plane_normal=normal)
        if s is None: continue
        first=True
        for poly in s.discrete:
            p=to2d(poly)
            ax.add_patch(PathPatch(Path(p), fc=c, ec='k', lw=0.3, alpha=0.9, label=lab if first else None)); first=False
    ax.set_aspect('equal'); ax.autoscale_view(); ax.grid(alpha=0.3)
def save(fig,ax,name,title):
    h,l=ax.get_legend_handles_labels(); ax.legend(h,l,fontsize=7,loc='upper left',bbox_to_anchor=(1.0,1.0))
    ax.set_title(title,fontsize=9); fig.tight_layout(); fig.savefig('previews/'+name,dpi=170); plt.close(fig)
# 1: lengthwise at X=0 (all five buttons, jack, top screw, cell)
fig,ax=plt.subplots(figsize=(13,5.5)); draw(ax,[0,0,0],[1,0,0],lambda p:p[:,[1,2]])
ax.set_xlabel('Y (mm)  [top end of board at Y=80, jack end left]'); ax.set_ylabel('Z (mm)  [PCB back face = 0]')
save(fig,ax,'section_buttons_x0.png','Section X=0: S5..S1 (pin tubes / plungers), LCD, jack, 18650')
# zoom of the button area
fig,ax=plt.subplots(figsize=(11,4.5)); draw(ax,[0,0,0],[1,0,0],lambda p:p[:,[1,2]]); ax.set_xlim(2,50); ax.set_ylim(-8,8)
save(fig,ax,'section_buttons_zoom.png','Section X=0, zoom: plungers S1/S3 (right), pin guide tubes S2/S4/S5, jack (left)')
# 2: across at the switch / USB-C (Y = 80-27 = 53)
fig,ax=plt.subplots(figsize=(8,8)); draw(ax,[0,53,0],[0,1,0],lambda p:p[:,[0,2]])
ax.set_xlabel('X (mm)  [+X = switch side, -X = USB-C side, front view]'); ax.set_ylabel('Z (mm)')
save(fig,ax,'section_switch_usb.png','Section Y=53 (27 mm from the top): switch cap (right), USB-C (left), 18650')
fig,ax=plt.subplots(figsize=(10,6)); draw(ax,[0,53,0],[0,1,0],lambda p:p[:,[0,2]]); ax.set_xlim(-16,18); ax.set_ylim(-8,8)
save(fig,ax,'section_switch_usb_zoom.png','Section Y=53 zoom: switch cap in its wall slot, USB-C opening + plug recess')
# 3: across S1 (Y = 42.75) plunger
fig,ax=plt.subplots(figsize=(8,8)); draw(ax,[0,80-37.25,0],[0,1,0],lambda p:p[:,[0,2]])
save(fig,ax,'section_S1.png','Section through S1 (37.25 mm from the top): plunger, PCB edge ledges, cell')
# 4: plan section just under the PCB (Z=-3)
fig,ax=plt.subplots(figsize=(6,13)); draw(ax,[0,0,-3],[0,0,1],lambda p:p[:,[0,1]])
save(fig,ax,'section_plan_z-3.png','Plan section Z=-3 (back side, under the PCB)')
# 5: across the LCD (through the top/bottom ribs' line is along X; cut at Y through side ribs) + lengthwise at the side ribs' X
fig,ax=plt.subplots(figsize=(10,5)); draw(ax,[0,80-14.25+3.5,0],[0,1,0],lambda p:p[:,[0,2]]); ax.set_xlim(-14.5,14.5); ax.set_ylim(-1,7)
save(fig,ax,'section_lcd_across.png','Section across the LCD (Y through the side press ribs): frame walls, ribs on the glass border, window')
fig,ax=plt.subplots(figsize=(12,5)); draw(ax,[0,0,0],[1,0,0],lambda p:p[:,[1,2]]); ax.set_xlim(50,82); ax.set_ylim(-1,7)
save(fig,ax,'section_lcd_lengthwise.png','Section X=0 through the LCD: top wall, ribs on the top/bottom glass border, glass-edge wall above the backlight')
# 6: battery frame + holder: across at mid-length, and lengthwise through the bottom-hole insert column
fig,ax=plt.subplots(figsize=(8,9)); draw(ax,[0,40,0],[0,1,0],lambda p:p[:,[0,2]])
save(fig,ax,'section_frame_holder_across.png','Section Y=40: PCB, battery frame on its side ledges, holder glued under it, cell, floor')
fig,ax=plt.subplots(figsize=(13,6)); draw(ax,[-8.4,0,0],[1,0,0],lambda p:p[:,[1,2]])
save(fig,ax,'section_frame_holder_lengthwise.png','Section X=-8.4 (bottom-left mounting hole): screw -> PCB -> frame insert column, frame, holder, end ledge')
fig,ax=plt.subplots(figsize=(11,6)); draw(ax,[-8.4,0,0],[1,0,0],lambda p:p[:,[1,2]]); ax.set_xlim(-4,20); ax.set_ylim(-12,7)
save(fig,ax,'section_frame_holder_zoom.png','Section X=-8.4 zoom: front boss, PCB, insert column on the frame, jack-end ledge and snap tab')
