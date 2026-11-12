import json
import os
F=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../kicad/openald-dock.kicad_pro")
d=json.load(open(F))
r=d["board"]["design_settings"]["rules"]
r.update({"min_copper_edge_clearance":0.3,"min_clearance":0.15,"min_track_width":0.15,"min_via_diameter":0.5,"min_via_annular_width":0.1,
          "min_through_hole_diameter":0.3,"min_hole_clearance":0.25,"min_hole_to_hole":0.25,"min_text_height":0.6})
ns=d["net_settings"]
base=dict(ns["classes"][0])
base.update({"track_width":0.25,"clearance":0.2,"via_diameter":0.6,"via_drill":0.3})
pw=dict(base); pw.update({"name":"Power","track_width":0.6,"clearance":0.2,"via_diameter":0.8,"via_drill":0.4,"priority":1})
hc=dict(base); hc.update({"name":"HiCur","track_width":0.8,"clearance":0.2,"via_diameter":0.8,"via_drill":0.4,"priority":0})
ns["classes"]=[base,pw,hc]
ns["netclass_patterns"]=[{"netclass":"HiCur","pattern":n} for n in ["VBUS","VBUS_F","VIN_SW","LX_A","LX_B","5V_A","5V_B"]]+[{"netclass":"Power","pattern":n} for n in ["GND"]+[f"SLOT{i}" for i in range(1,7)]]
d["board"]["design_settings"].setdefault("defaults",{})
json.dump(d,open(F,"w"),indent=2)
print("pro updated")
