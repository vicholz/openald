#!/usr/bin/env python3
"""MI03 case checks: watertight/single body of every printable STL, pairwise interference volumes in the assembly
pose for BOTH battery-frame options, drop-in sweeps (board into the front shell, frame into the front unit),
switch-cap travel, hardware ghosts and the battery-frame glue area."""
import trimesh, itertools, os, numpy as np
import shapely.geometry as sg, shapely.ops as so
F = '/tmp/mi03fit'
def L(n): return trimesh.load(os.path.join(F, n + '.stl'))
bad = 0
print("== Printable STLs ==")
for n in ['mi03_front_shell', 'mi03_back_shell', 'mi03_battery_frame_front_mount', 'mi03_battery_frame_back_mount',
          'mi03_button_plunger', 'mi03_switch_carrier', 'mi03_switch_knob']:
    m = trimesh.load(f'stl/{n}.stl'); e = m.extents
    nb = len(m.split(only_watertight=False))
    if not m.is_watertight or nb != 1: bad += 1
    print(f"{n:32s} watertight={m.is_watertight} bodies={nb} volume={m.volume:8.1f} mm3  extents {e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f}  min z {m.bounds[0][2]:.2f}")
def vol(a, b):
    try:
        r = trimesh.boolean.intersection([a, b], engine='manifold')
        return 0.0 if r is None or r.is_empty else abs(r.volume)
    except Exception as ex:
        return f"ERR {ex}"
EXPECTED = {frozenset(['pcb','jack/usb/switch']): 'USB-C shell top (z +0.16) sits in the board-edge notch (mid-mount): modelling artefact',
            frozenset(['front_shell','lcd+buttons']): 'LCD press ribs reach lcd_preload below the glass top on purpose (see the LCD frame section below)'}
def chk(na, a, nb, b):
    global bad
    v = vol(a, b); note = EXPECTED.get(frozenset([na, nb]))
    clear = isinstance(v, float) and v < 1e-3
    flag = '' if clear else ('  (expected: ' + note + ')' if note else '  <-- CHECK')
    if not clear and not note: bad += 1
    print(f"{na:22s} x {nb:20s} {v if isinstance(v,str) else round(v,4)}{flag}")
front, back = L('front_raw'), L('back_raw')
ghost = {'pcb': L('ghost_pcb'), 'lcd+buttons': L('ghost_front'), 'jack/usb/switch': L('ghost_back_0'), '18650+holder': L('ghost_holder')}
loose = {'plungers': L('plungers_raw'), 'switch_carrier': L('carrier_0'), 'switch_knob': L('knob_0')}
print("\n== Interference, shells + loose parts (mm3, assembly pose; 0 = clear) ==")
chk('front_shell', front, 'back_shell', back)
for cn, c in [('front_shell', front), ('back_shell', back)]:
    for gn, g in list(ghost.items()) + list(loose.items()): chk(cn, c, gn, g)
for a, b in itertools.combinations(list(ghost.items()) + list(loose.items()), 2):
    chk(a[0], a[1], b[0], b[1])
for m in ['front', 'back']:
    fr = L(f'frame_raw_{m}'); fs = L(f'frame_screws_{m}')
    print(f"\n== Battery frame, option frame_mount=\"{m}\" ==")
    chk(f'frame({m})', fr, 'front_shell', front); chk(f'frame({m})', fr, 'back_shell', back)
    for gn, g in list(ghost.items()) + list(loose.items()): chk(f'frame({m})', fr, gn, g)
    chk(f'frame({m})', fr, 'board screws', L('ghost_board_screws'))
    for n, o in [('frame', fr), ('front_shell', front), ('back_shell', back)] + list(ghost.items()) + list(loose.items()):
        v = vol(fs, o); exp = (m == 'front' and n == 'front_shell') or (m == 'back' and n == 'back_shell')
        ok = (isinstance(v, float) and (v > 0 if exp else v < 1e-3))
        if not ok: bad += 1
        print(f"frame screws({m}) x {n:16s} {round(v,3) if isinstance(v,float) else v}" + ('   (expected >0: self-tapping thread biting its 1.6 mm pilot)' if exp else '') + ('' if ok else '  <-- CHECK'))
    # gaps that matter
    print(f"plate z {fr.bounds[0][2]:.2f}..{fr.bounds[0][2]+1.6:.2f}; frame screws z {fs.bounds[0][2]:.2f}..{fs.bounds[1][2]:.2f}")
    # glue area
    hb = ghost['18650+holder']; hx = hb.bounds; b = fr.bounds; n_ = fr.face_normals; cz = fr.triangles_center
    sel = (n_[:,2] < -0.99) & (abs(cz[:,2]-b[0][2]) < 1e-3)
    sub = fr.submesh([np.where(sel)[0]], append=True)
    face = so.unary_union([sg.Polygon(t[:, :2]) for t in sub.triangles])
    foot = sg.box(hx[0][0], hx[0][1], hx[1][0], hx[1][1])
    print(f"glue area (underside inside the holder's {hx[1][0]-hx[0][0]:.1f} x {hx[1][1]-hx[0][1]:.1f} mm footprint): {face.intersection(foot).area:.0f} mm2 of {foot.area:.0f} mm2")
print("\n== Drop-in sweeps ==")
bu = L('board_unit'); car = L('carrier_0')
worst = 0
for dz in np.arange(0.3, 14.01, 0.25):
    t = bu.copy(); t.apply_translation([0, 0, -dz])
    v1 = vol(t, front); v2 = vol(t, car)
    if not (isinstance(v1, float) and isinstance(v2, float) and v1 < 1e-3 and v2 < 1e-3):
        bad += 1; worst += 1; print(f"board unit {dz:.2f} mm short of home: front {v1}  carrier {v2}  <-- CHECK")
print(f"board (PCB + LCD + buttons + jack/USB-C/switch) moved straight along Z from 14 mm out to 0.3 mm from home: {'clear at every 0.25 mm step' if worst == 0 else 'COLLISIONS'} (last 0.15 mm = LCD rib preload)")
fa = L('frame_raw_front'); unit = trimesh.util.concatenate([front, bu]); worst = 0
for dz in np.arange(0.1, 12.01, 0.25):
    t = fa.copy(); t.apply_translation([0, 0, -dz])
    vs = [vol(t, o) for o in (front, bu, car)]
    if not all(isinstance(v, float) and v < 1e-3 for v in vs): bad += 1; worst += 1; print(f"frame(front) {dz:.2f} short: {vs}  <-- CHECK")
print(f"option \"front\": frame moved along Z into the front + board unit from 12 mm out: {'clear' if worst == 0 else 'COLLISIONS'}")
print("\n== LCD frame ==")
nop = L('front_raw_nopress')
chk('front (no ribs)', nop, 'lcd+buttons', ghost['lcd+buttons']); chk('front (no ribs)', nop, 'pcb', ghost['pcb'])
r = trimesh.boolean.intersection([front, ghost['lcd+buttons']], engine='manifold')
if r is None or r.is_empty: print("press ribs: NOT touching the glass  <-- CHECK"); bad += 1
else:
    b = r.bounds
    print(f"press ribs x glass: {abs(r.volume):.3f} mm3 in {len(r.split(only_watertight=False))} contact(s); engagement depth {b[1][2]-b[0][2]:.3f} mm, X {b[0][0]:.2f}..{b[1][0]:.2f}, Y {b[0][1]:.2f}..{b[1][1]:.2f}")
print("\n== Switch cap travel (carrier + knob + actuator shifted together) ==")
for s in ['-1', '0', '1']:
    c, k, gb = L('carrier_' + s), L('knob_' + s), L('ghost_back_' + s)
    for pn, p in [('carrier', c), ('knob', k)]:
        chk(f'{pn} shift {s}', p, 'front_shell', front); chk(f'{pn} shift {s}', p, 'back_shell', back)
        chk(f'{pn} shift {s}', p, 'switch/usb/jack', gb); chk(f'{pn} shift {s}', p, 'pcb', ghost['pcb'])
    chk(f'carrier shift {s}', c, 'knob', k)
print("\n== Board screws ==")
sc = L('ghost_board_screws')
for n, o in [('front_shell', front), ('back_shell', back)] + list(ghost.items()):
    v = vol(sc, o); print(f"board screws x {n:16s} {round(v,3) if isinstance(v,float) else v}" + ('   (expected >0: self-tapping thread in the 1.7 mm pilots)' if n == 'front_shell' else ''))
    if n not in ('front_shell',) and not (isinstance(v, float) and v < 1e-3): bad += 1
print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} unexpected interferences)")
