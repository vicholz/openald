#!/usr/bin/env python3
"""MI03 case checks: watertight/extents of every printable STL, and pairwise interference volumes
between the case parts, loose parts and the ghost PCB/components/18650 holder (assembly pose)."""
import trimesh, itertools, os
F = '/tmp/mi03fit'
def L(n): return trimesh.load(os.path.join(F, n + '.stl'))
bad = 0
print("== Printable STLs ==")
for n in ['mi03_front_shell', 'mi03_back_shell', 'mi03_battery_frame', 'mi03_button_plunger', 'mi03_switch_cap']:
    m = trimesh.load(f'stl/{n}.stl')
    e = m.extents
    nb = len(m.split(only_watertight=False))
    if not m.is_watertight or nb != 1: bad += 1
    print(f"{n:22s} watertight={m.is_watertight} bodies={nb} volume={m.volume:8.1f} mm3  extents {e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f}  min z {m.bounds[0][2]:.2f}")
def vol(a, b):
    try:
        r = trimesh.boolean.intersection([a, b], engine='manifold')
        return 0.0 if r is None or r.is_empty else abs(r.volume)
    except Exception as ex:
        return f"ERR {ex}"
case = {'front_shell': L('front_raw'), 'back_shell': L('back_raw'), 'battery_frame': L('frame_raw')}
ghost = {'pcb': L('ghost_pcb'), 'lcd+buttons': L('ghost_front'), 'jack/usb/switch': L('ghost_back_0'),
         '18650+holder': L('ghost_holder')}
loose = {'plungers': L('plungers_raw'), 'switch_cap': L('cap_0')}
print("\n== Interference (mm3, assembly pose; 0 = clear) ==")
EXPECTED = {frozenset(['pcb','jack/usb/switch']): 'USB-C shell top (z +0.16) sits in the board-edge notch (mid-mount): modelling artefact',
            frozenset(['front_shell','lcd+buttons']): 'LCD press ribs reach lcd_preload below the glass top on purpose (see the LCD frame section below)',
            }
def chk(na, a, nb, b, expect0=True):
    global bad
    v = vol(a, b)
    note = EXPECTED.get(frozenset([na, nb]))
    flag = '' if (isinstance(v, float) and v < 1e-3) or not expect0 else ('  (expected: ' + note + ')' if note else '  <-- CHECK')
    if note and flag: expect0 = False
    if flag and expect0: bad += 1
    print(f"{na:18s} x {nb:18s} {v if isinstance(v,str) else round(v,4)}{flag}")
chk('front_shell', case['front_shell'], 'back_shell', case['back_shell'])
chk('front_shell', case['front_shell'], 'battery_frame', case['battery_frame'])
chk('back_shell', case['back_shell'], 'battery_frame', case['battery_frame'])
for cn, c in case.items():
    for gn, g in list(ghost.items()) + list(loose.items()):
        chk(cn, c, gn, g)
for a, b in itertools.combinations(list(ghost.items()) + list(loose.items()), 2):
    if {a[0], b[0]} == {'switch_cap', 'jack/usb/switch'}: continue
    chk(a[0], a[1], b[0], b[1])
print("\n== LCD frame ==")
chk('front (no ribs)', L('front_raw_nopress'), 'lcd+buttons', ghost['lcd+buttons'])
chk('front (no ribs)', L('front_raw_nopress'), 'pcb', ghost['pcb'])
r = trimesh.boolean.intersection([case['front_shell'], ghost['lcd+buttons']], engine='manifold')
if r is None or r.is_empty: print("press ribs: NOT touching the glass  <-- CHECK"); bad += 1
else:
    b = r.bounds
    print(f"press ribs x glass: {abs(r.volume):.3f} mm3 in {len(r.split(only_watertight=False))} contact(s); engagement depth {b[1][2]-b[0][2]:.3f} mm (glass top z {b[1][2]:.2f}), all within the glass border: X {b[0][0]:.2f}..{b[1][0]:.2f}, Y {b[0][1]:.2f}..{b[1][1]:.2f}")
print("\n== Switch cap travel (cap + actuator shifted together) ==")
for s in ['-1', '0', '1']:
    cap = L('cap_' + s); gb = L('ghost_back_' + s)
    for cn, c in case.items(): chk(f'cap shift {s}', cap, cn, c)
    chk(f'cap shift {s}', cap, 'switch/usb/jack', gb)
print("\n== Hardware ghosts (screws) ==")
sc = L('ghost_screws')
for cn, c in list(case.items()) + list(ghost.items()):
    v = vol(sc, c)
    print(f"screws x {cn:18s} {round(v,3) if isinstance(v,float) else v}   (expected >0 only for the self-tapping top screw biting its 1.7 mm pilot)" if cn=='front_shell' else f"screws x {cn:18s} {round(v,3) if isinstance(v,float) else v}")
print("\n== Battery frame ==")
fr = L('frame_raw'); hb = L('ghost_holder'); import numpy as np
b = fr.bounds; print(f"frame plate underside (glue face) at z {b[0][2]:.2f}, plate 1.6 mm thick; trimmed holder pins reach z {hb.bounds[1][2]:.2f}, inside the plate slots")
# glue area = downward faces of the frame at the plate bottom, inside the holder footprint
hx = hb.bounds; tri = fr.triangles; n = fr.face_normals; cz = fr.triangles_center
sel = (n[:,2] < -0.99) & (abs(cz[:,2]-b[0][2]) < 1e-3)
sub = fr.submesh([np.where(sel)[0]], append=True)
import shapely.geometry as sg, shapely.ops as so
polys = [sg.Polygon(t[:, :2]) for t in sub.triangles]
face = so.unary_union(polys)
foot = sg.box(hx[0][0], hx[0][1], hx[1][0], hx[1][1])
print(f"glue area (frame underside inside the holder's {hx[1][0]-hx[0][0]:.1f} x {hx[1][1]-hx[0][1]:.1f} mm footprint): {face.intersection(foot).area:.0f} mm2 of {foot.area:.0f} mm2")
print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} unexpected interferences)")
