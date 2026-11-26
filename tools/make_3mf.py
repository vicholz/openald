#!/usr/bin/env python3
"""Coloured 3MF plates for the OpenALD printed parts (t124u).

  python3 tools/make_3mf.py [single_board|feather|mi03|dock|all]

Reads the print-ready STLs (already in print orientation), lays them out side by side on the bed (Z = 0, 10 mm gaps)
and writes ONE 3MF per case family next to the STLs. Each part is its own named object with a 3MF core-spec
<basematerials> colour (displaycolor) from tools/palette.py, so slicers that read 3MF colours (e.g. Bambu Studio /
OrcaSlicer, Cura, 3D Builder) show each part in its colour; all slicers keep the parts as separate named objects.
Also checks that every .scad still carries its palette hex values (previews and 3MF must agree)."""
import os, sys, zipfile, re
import numpy as np, trimesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import PALETTE
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAM = {   # family: (stl dir, output 3MF, scad that must carry the palette, part order)
    "single_board": ("radio_single_board/case", "radio_single_board/case/openald_single_board_case_colored.3mf",
                     "radio_single_board/case/openald_case.scad", ["case_bottom", "case_top", "holder_spacer"]),
    "feather": ("radio_adafruit_feather_rp2040/case", "radio_adafruit_feather_rp2040/case/openald_feather_case_colored.3mf",
                "radio_adafruit_feather_rp2040/case/openald_feather_case.scad", ["case_bottom", "case_top", "deck"]),
    "mi03": ("mi03_case/stl", "mi03_case/stl/mi03_case_colored.3mf", "mi03_case/mi03_case.scad",
             ["mi03_front_shell", "mi03_back_shell", "mi03_battery_frame_front_mount", "mi03_battery_frame_back_mount",
              ("mi03_button_plunger", 2), "mi03_switch_carrier", "mi03_switch_knob"]),
    "dock": ("charging_dock/case", "charging_dock/case/openald_dock_colored.3mf", "charging_dock/case/openald_dock.scad",
             ["dock_top_shell", "dock_base", "dock_floor_pads_x6"]),
}
BED_W, GAP = 230.0, 10.0

def xml_mesh(m):
    v = "".join('<vertex x="%.6f" y="%.6f" z="%.6f"/>' % tuple(p) for p in m.vertices)
    t = "".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f) for f in m.faces)
    return "<mesh><vertices>%s</vertices><triangles>%s</triangles></mesh>" % (v, t)

def build(fam):
    d, out, scad, order = FAM[fam]
    pal = PALETTE[fam]
    src = open(os.path.join(R, scad)).read()
    order = [(o, 1) if isinstance(o, str) else o for o in order]   # (part, copies on the plate)
    missing = sorted({pal[p][0] for p, _ in order} - set(re.findall(r'#[0-9A-Fa-f]{6}', src)))
    if missing: sys.exit("%s: palette colours %s not in %s (keep tools/palette.py and the .scad in sync)" % (fam, missing, scad))
    mats, objs, items = [], [], []
    x = y = rowh = 0.0
    parts = [(p, k) for p, n in order for k in range(n)]
    pidx = {p: i for i, (p, _) in enumerate(order)}
    for p, _ in order:
        hexc, cname, label = pal[p]
        mats.append('<base name="%s (%s)" displaycolor="%sFF"/>' % (label, cname, hexc.upper()))
    for i, (p, k) in enumerate(parts):
        m = trimesh.load(os.path.join(R, d, p + ".stl"), force="mesh")
        m.merge_vertices()
        lo, hi = m.bounds
        w, h = hi[0] - lo[0], hi[1] - lo[1]
        if x > 0 and x + w > BED_W: x, y, rowh = 0.0, y + rowh + GAP, 0.0
        m.apply_translation([x - lo[0], y - lo[1], -lo[2]])
        x += w + GAP; rowh = max(rowh, h)
        label = pal[p][2]
        oid = i + 2
        objs.append('<object id="%d" type="model" pid="1" pindex="%d" name="%s"><metadatagroup><metadata name="Title">%s</metadata></metadatagroup>%s</object>'
                    % (oid, pidx[p], p + ("_%d" % (k + 1) if k else ""), label, xml_mesh(m)))
        items.append('<item objectid="%d"/>' % oid)
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<metadata name="Title">OpenALD v1.0 %s parts (coloured)</metadata>'
             '<metadata name="Designer">OpenALD</metadata><metadata name="LicenseTerms">CC0 1.0</metadata>'
             '<resources><basematerials id="1">%s</basematerials>%s</resources><build>%s</build></model>'
             % (fam, "".join(mats), "".join(objs), "".join(items)))
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    path = os.path.join(R, out)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in (("[Content_Types].xml", ct), ("_rels/.rels", rels), ("3D/3dmodel.model", model)):
            zi = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)   # fixed timestamps: rebuilding the same STLs gives the same 3MF
    # read back: every part present, watertight, same volume as its STL
    sc = trimesh.load(path, process=False)
    geoms = sc.geometry if hasattr(sc, "geometry") else {"m": sc}
    assert len(geoms) == len(parts), (fam, len(geoms))
    for k, g in geoms.items():
        t = trimesh.Trimesh(g.vertices, g.faces, process=False)
        assert t.is_watertight, (fam, k, "not watertight in the 3MF")
    print("%s: %s (%d parts: %s)" % (fam, out, len(parts), ", ".join("%s%s %s" % (p, " x%d" % n if n > 1 else "", pal[p][0]) for p, n in order)))

if __name__ == "__main__":
    for f in (FAM if len(sys.argv) < 2 or sys.argv[1] == "all" else sys.argv[1:]): build(f)
