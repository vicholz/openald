import json,os
F=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"kicad","openald-feather-controls.kicad_pro")
d=json.load(open(F))
r=d["board"]["design_settings"]["rules"]
r.update({"min_copper_edge_clearance":0.3,"min_clearance":0.15,"min_track_width":0.15,"min_via_diameter":0.5,"min_via_annular_width":0.1,
          "min_through_hole_diameter":0.3,"min_hole_clearance":0.25,"min_hole_to_hole":0.25,"min_text_height":0.6})
ns=d["net_settings"]; base=dict(ns["classes"][0])
base.update({"name":"Default","track_width":0.25,"clearance":0.2,"via_diameter":0.6,"via_drill":0.3})
pw=dict(base); pw.update({"name":"Power","track_width":0.4,"clearance":0.2,"via_diameter":0.7,"via_drill":0.35,"priority":0})
ns["classes"]=[base,pw]
ns["netclass_patterns"]=[{"netclass":"Power","pattern":n} for n in ["GND","VBUS","VBAT","EN"]]
json.dump(d,open(F,"w"),indent=2); print("pro updated")
