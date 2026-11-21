#!/usr/bin/env python3
"""MI03 case checks: watertight/extents of every printable STL, and pairwise interference volumes
between the case parts, loose parts and the ghost PCB/components/18650 holder (assembly pose)."""
import trimesh, itertools, os
F = '/tmp/mi03fit'
def L(n): return trimesh.load(os.path.join(F, n + '.stl'))
print("== Printable STLs ==")
for n in ['mi03_front_shell', 'mi03_back_shell', 'mi03_button_plunger', 'mi03_switch_cap']:
    m = trimesh.load(f'stl/{n}.stl')
    e = m.extents
    print(f"{n:22s} watertight={m.is_watertight} volume={m.volume:8.1f} mm3  extents {e[0]:.2f} x {e[1]:.2f} x {e[2]:.2f}  min z {m.bounds[0][2]:.2f}")
def vol(a, b):
    try:
        r = trimesh.boolean.intersection([a, b], engine='manifold')
        return 0.0 if r is None or r.is_empty else abs(r.volume)
    except Exception as ex:
        return f"ERR {ex}"
case = {'front_shell': L('front_raw'), 'back_shell': L('back_raw')}
ghost = {'pcb': L('ghost_pcb'), 'lcd+buttons': L('ghost_front'), 'jack/usb/switch': L('ghost_back_0'),
         '18650+holder': L('ghost_holder')}
loose = {'plungers': L('plungers_raw'), 'switch_cap': L('cap_0')}
print("\n== Interference (mm3, assembly pose; 0 = clear) ==")
bad = 0
EXPECTED = {frozenset(['pcb','jack/usb/switch']): 'USB-C shell top (z +0.16) sits in the board-edge notch (mid-mount): modelling artefact',
            frozenset(['back_shell','18650+holder']): 'holder locating pegs in the holder\'s 3.2 mm holes + trimmed pins in their floor pockets (ghost holder has no holes)'}
def chk(na, a, nb, b, expect0=True):
    global bad
    v = vol(a, b)
    note = EXPECTED.get(frozenset([na, nb]))
    flag = '' if (isinstance(v, float) and v < 1e-3) or not expect0 else ('  (expected: ' + note + ')' if note else '  <-- CHECK')
    if note and flag: expect0 = False
    if flag and expect0: bad += 1
    print(f"{na:18s} x {nb:18s} {v if isinstance(v,str) else round(v,4)}{flag}")
chk('front_shell', case['front_shell'], 'back_shell', case['back_shell'])
for cn, c in case.items():
    for gn, g in list(ghost.items()) + list(loose.items()):
        chk(cn, c, gn, g)
for a, b in itertools.combinations(list(ghost.items()) + list(loose.items()), 2):
    if {a[0], b[0]} == {'switch_cap', 'jack/usb/switch'}: continue
    chk(a[0], a[1], b[0], b[1])
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
print(f"\nRESULT: {'PASS' if bad == 0 else 'FAIL'} ({bad} unexpected interferences)")
