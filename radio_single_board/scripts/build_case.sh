#!/bin/bash
# Regenerate case parameters from the PCB, export STLs, run the fit check and render previews.
set -e
cd "$(dirname "$0")/.."
python3 scripts/gen_case_params.py >/dev/null
cd case
S=openald_case.scad
openscad -D 'part="top"'        -o case_top.stl       $S 2>/dev/null &
openscad -D 'part="bottom"'     -o case_bottom.stl    $S 2>/dev/null &
rm -f led_spacer.stl ../previews/closeup_led.png button_plunger.stl    # rev 3: no 5 mm LED / spacer; 2026-11-11: no button SW2 / plunger
mkdir -p nut_variant
openscad -D 'part="top"'    -D 'fastener="nut"' -o nut_variant/case_top_nut.stl    $S 2>/dev/null &
openscad -D 'part="bottom"' -D 'fastener="nut"' -o nut_variant/case_bottom_nut.stl $S 2>/dev/null &
openscad -D 'part="top_raw"'    -o /tmp/top_raw.stl $S 2>/dev/null &
openscad -D 'part="bottom_raw"' -o /tmp/bot_raw.stl $S 2>/dev/null &
openscad -D 'part="tunnels_raw"' -o /tmp/tunnels_raw.stl $S 2>/dev/null &
wait
python3 ../scripts/check_case_fit.py /tmp/top_raw.stl /tmp/bot_raw.stl /tmp/tunnels_raw.stl 2>/dev/null > case_fit_report.txt
P="--imgsize=1200,900 --colorscheme=Tomorrow --projection=p"
R=../previews
openscad $P --camera=19,43,0,60,0,35,195  -D 'part="assembly"' -o $R/case_assembly_exploded.png $S 2>/dev/null &
openscad $P --camera=19,43,0,70,0,235,195 -D 'part="assembly"' -o $R/case_assembly_back.png $S 2>/dev/null &
openscad $P --render --camera=45,43,10,45,0,200,235 -D 'part="print"' -o $R/case_print_layout.png $S 2>/dev/null &
openscad $P --camera=19,43,0,55,0,50,170 -D 'part="closed"' -o $R/case_closed.png $S 2>/dev/null &
wait
# close-ups of the openings (closed case with PCB inside)
openscad $P --camera=41,23,4,85,0,90,40  -D 'part="closed"' -o $R/closeup_power_switch.png $S 2>/dev/null &
openscad $P --camera=41,61,4,80,0,90,55  -D 'part="closed"' -o $R/closeup_thumbwheel.png $S 2>/dev/null &
openscad $P --camera=19,-2,4,80,0,0,45   -D 'part="closed"' -o $R/closeup_usb_c.png $S 2>/dev/null &
openscad $P --camera=19,78,9,0,0,0,45   -D 'part="closed"' -o $R/closeup_led_bar.png $S 2>/dev/null &
openscad $P --camera=19,8,5,62,0,0,62    -D 'part="closed"' -o $R/closeup_front_usb_leds.png $S 2>/dev/null &
python3 -c "
import trimesh,re
x=float(re.search(r'bar_leds = \[\[([-\d.]+),',open('case_params.scad').read()).group(1))
m=trimesh.load('/tmp/pcb_assembly.stl'); m.update_faces(m.triangles_center[:,0]>=x); m.remove_unreferenced_vertices(); m.export('/tmp/pcb_assembly_cut.stl')"
openscad $P --camera=24,74.6,3,80,0,270,70 -D 'part="cutaway"' -o $R/cutaway_led_tunnels.png $S 2>/dev/null &
openscad $P --camera=19,90,4,80,0,180,60 -D 'part="closed"' -o $R/closeup_jack_end.png $S 2>/dev/null &
wait
rm -f $R/case_top_right_side.png $R/case_top_usb_end.png $R/case_top_jack_end.png
tail -4 case_fit_report.txt
