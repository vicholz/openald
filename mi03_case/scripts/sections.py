#!/usr/bin/env python3
"""Cross-section previews from the assembly-pose meshes in /tmp/mi03fit (built by build.sh)."""
import trimesh, matplotlib, numpy as np
import shapely.geometry as sg
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
F='/tmp/mi03fit/'
def parts(m='front'):
    return [('front_raw','#9db7d6','front shell'),('back_raw','#c8c8c8','back shell'),(f'frame_raw_{m}','mediumseagreen',f'battery frame ({m} mount)'),
            ('plungers_raw','orange','plungers'),('carrier_0','tomato','switch carrier'),('knob_0','#ff9f80','switch knob'),
            ('ghost_pcb','darkgreen','PCB'),('ghost_front','black','LCD / buttons'),('ghost_back_0','#7a7a7a','jack / USB-C / switch'),
            ('ghost_holder','royalblue','18650 + holder'),('ghost_board_screws','gold','board screws (M2)'),(f'frame_screws_{m}','darkgoldenrod',f'frame screws ({m})')]
_cache={}
def draw(ax, origin, normal, to2d, m='front'):
    for n,c,lab in parts(m):
        if n not in _cache: _cache[n]=trimesh.load(F+n+'.stl')
        s=_cache[n].section(plane_origin=origin, plane_normal=normal)
        if s is None: continue
        # even-odd combine the loops so holes (openings) show as holes
        geo=None
        for poly in s.discrete:
            g=sg.Polygon(to2d(poly)).buffer(0)
            geo=g if geo is None else geo.symmetric_difference(g)
        first=True
        for pg in getattr(geo,'geoms',[geo]):
            if pg.is_empty or pg.geom_type!='Polygon': continue
            verts=[]; codes=[]
            for ring in [pg.exterior]+list(pg.interiors):
                xy=np.asarray(ring.coords); verts+=list(xy); codes+=[Path.MOVETO]+[Path.LINETO]*(len(xy)-2)+[Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts,codes), fc=c, ec='k', lw=0.3, alpha=0.9, label=lab if first else None)); first=False
    ax.set_aspect('equal'); ax.autoscale_view(); ax.grid(alpha=0.3)
def split_line(ax, horiz=True):
    (ax.axhline if horiz else ax.axvline)(-8.15, color='r', lw=0.6, ls='--', label='front/back split z=-8.15')
def save(fig,ax,name,title):
    h,l=ax.get_legend_handles_labels(); ax.legend(h,l,fontsize=7,loc='upper left',bbox_to_anchor=(1.0,1.0))
    ax.set_title(title,fontsize=9); fig.tight_layout(); fig.savefig('previews/'+name,dpi=170); plt.close(fig)
YZ=lambda p:p[:,[1,2]]; XZ=lambda p:p[:,[0,2]]
# lengthwise at X=0
fig,ax=plt.subplots(figsize=(13,5.5)); draw(ax,[0,0,0],[1,0,0],YZ); split_line(ax)
ax.set_xlabel('Y (mm)  [top end of board at Y=80, jack end left]'); ax.set_ylabel('Z (mm)  [PCB back face = 0]')
save(fig,ax,'section_buttons_x0.png','Section X=0: S5..S1, LCD, jack (barrel inside the end wall), 18650; split below the frame')
fig,ax=plt.subplots(figsize=(11,4.5)); draw(ax,[0,0,0],[1,0,0],YZ); ax.set_xlim(2,50); ax.set_ylim(-8,8)
save(fig,ax,'section_buttons_zoom.png','Section X=0, zoom: plungers S1/S3 (right), pin guide tubes S2/S4/S5')
# switch / USB-C (Y = 53)
fig,ax=plt.subplots(figsize=(8,8)); draw(ax,[0,53,0],[0,1,0],XZ); split_line(ax)
ax.set_xlabel('X (mm)  [+X = switch side, -X = USB-C side]'); ax.set_ylabel('Z (mm)')
save(fig,ax,'section_switch_usb.png','Section Y=53: switch carrier+knob (right) and USB-C (left) both in the FRONT shell')
fig,ax=plt.subplots(figsize=(10,6)); draw(ax,[0,53,0],[0,1,0],XZ); split_line(ax); ax.set_xlim(-16,18); ax.set_ylim(-10,6)
save(fig,ax,'section_switch_usb_zoom.png','Section Y=53 zoom: closed switch slot + pocket and drop-in channel (right); USB-C opening, recess, drop-in channel (left)')
fig,ax=plt.subplots(figsize=(10,6)); draw(ax,[13.0,0,0],[1,0,0],YZ); split_line(ax); ax.set_xlim(44,62); ax.set_ylim(-10,6)
save(fig,ax,'section_switch_wall_x13.png','Section X=13 (inside the switch-side wall): closed slot around the stem, pocket, head channel below')
# jack end
fig,ax=plt.subplots(figsize=(11,6)); draw(ax,[0,0,0],[1,0,0],YZ); split_line(ax); ax.set_xlim(-8,14); ax.set_ylim(-12,7)
save(fig,ax,'section_jack_end.png','Section X=0 at the jack end: barrel 1.2 inside the end wall, 6.8 mm plug hole + 7.8 counterbore, all in the front shell')
fig,ax=plt.subplots(figsize=(9,7)); draw(ax,[0,-5.5,0],[0,1,0],XZ); split_line(ax)
save(fig,ax,'section_jack_end_wall.png','Section Y=-5.5 (through the end wall): plug hole entirely above the split')
# frame options
for m, x in [("front", 5.3), ("back", 9.0)]:
    fig,ax=plt.subplots(figsize=(11,6)); draw(ax,[x,0,0],[1,0,0],YZ,m); split_line(ax); ax.set_xlim(-8,14); ax.set_ylim(-29.5,7)
    save(fig,ax,f'section_frame_{m}_mount.png',f'Section X={x}: frame_mount="{m}": ' + ('M2x5 CSK from under the plate into the front-shell boss (frame joins the front + board unit)' if m=='front' else 'M2x8 CSK from above into the back-shell column; front boss bears on the plate'))
    fig,ax=plt.subplots(figsize=(9,7)); draw(ax,[0,-2.05 if m=="front" else 0.3,0],[0,1,0],XZ,m); split_line(ax); ax.set_ylim(-29.5,7)
    save(fig,ax,f'section_frame_{m}_mount_across.png',f'Section through the frame screw line, frame_mount="{m}"')
# S1, plan, LCD, frame mid-length
fig,ax=plt.subplots(figsize=(8,8)); draw(ax,[0,80-37.25,0],[0,1,0],XZ); split_line(ax)
save(fig,ax,'section_S1.png','Section through S1: plunger; PCB edge ribs on the battery frame support the board')
fig,ax=plt.subplots(figsize=(6,13)); draw(ax,[0,0,-3],[0,0,1],lambda p:p[:,[0,1]])
save(fig,ax,'section_plan_z-3.png','Plan section Z=-3 (under the PCB, front shell walls)')
fig,ax=plt.subplots(figsize=(6,13)); draw(ax,[0,0,-7.0],[0,0,1],lambda p:p[:,[0,1]])
save(fig,ax,'section_plan_z-7.png','Plan section Z=-7 (battery frame, back-shell lip in the front rebate, snap bumps)')
fig,ax=plt.subplots(figsize=(10,5)); draw(ax,[0,80-14.25+3.5,0],[0,1,0],XZ); ax.set_xlim(-14.5,14.5); ax.set_ylim(-1,7)
save(fig,ax,'section_lcd_across.png','Section across the LCD: frame walls, ribs on the glass border, window')
fig,ax=plt.subplots(figsize=(12,5)); draw(ax,[0,0,0],[1,0,0],YZ); ax.set_xlim(50,82); ax.set_ylim(-1,7)
save(fig,ax,'section_lcd_lengthwise.png','Section X=0 through the LCD: top wall, ribs on the top/bottom glass border')
fig,ax=plt.subplots(figsize=(8,9)); draw(ax,[0,40,0],[0,1,0],XZ); split_line(ax)
save(fig,ax,'section_frame_holder_across.png','Section Y=40: PCB on the frame ribs, frame on the back-shell side ledges, lip + snap, holder, cell')
fig,ax=plt.subplots(figsize=(11,6)); draw(ax,[0,62,0],[0,1,0],XZ); split_line(ax); ax.set_xlim(-15,15); ax.set_ylim(-11,3)
save(fig,ax,'section_snap_y62.png','Section Y=62: snap bump on the back-shell lip in the front-shell rebate groove')
# USB-C opening shape: plane through the 0.4 mm skin between the plug recess and the drop-in channel (X = -13.1)
fig,ax=plt.subplots(figsize=(8,5)); draw(ax,[-13.1,0,0],[1,0,0],YZ); ax.set_xlim(44,62); ax.set_ylim(-9,6)
save(fig,ax,'section_usb_opening_x-13.1.png','Section X=-13.1 (wall skin): stadium USB-C opening 9.44 x 3.76, end radius 1.88, around the receptacle')
