#!/bin/bash
# Regenerate case parameters from the PCB, export STLs, run the fit check and render previews.
set -e
cd "$(dirname "$0")/.."
python3 scripts/gen_case_params.py >/dev/null
cd case
S=openald_case.scad
rm -rf nut_variant   # 2026-11-24: no corner screws any more (board + holder screw into the front shell)
openscad -D 'part="top"'    -o case_top.stl      $S 2>/dev/null &
openscad -D 'part="bottom"' -o case_bottom.stl   $S 2>/dev/null &
openscad -D 'part="spacer"' -o holder_spacer.stl $S 2>/dev/null &
openscad -D 'part="top_raw"'    -o /tmp/top_raw.stl $S 2>/dev/null &
openscad -D 'part="bottom_raw"' -o /tmp/bot_raw.stl $S 2>/dev/null &
openscad -D 'part="spacer_raw"' -o /tmp/spacer_raw.stl $S 2>/dev/null &
openscad -D 'part="tunnels_raw"' -o /tmp/tunnels_raw.stl $S 2>/dev/null &
wait
python3 ../scripts/check_case_fit.py /tmp/top_raw.stl /tmp/bot_raw.stl /tmp/tunnels_raw.stl /tmp/spacer_raw.stl 2>/dev/null > case_fit_report.txt
P="--imgsize=1200,900 --colorscheme=Tomorrow --projection=p"
R=../previews
openscad $P --camera=11,42,-5,60,0,35,200  -D 'part="assembly"' -o $R/case_assembly_exploded.png $S 2>/dev/null &
openscad $P --camera=11,42,-5,70,0,235,200 -D 'part="assembly"' -o $R/case_assembly_back.png $S 2>/dev/null &
openscad $P --render --camera=40,42,10,45,0,200,220 -D 'part="print"' -o $R/case_print_layout.png $S 2>/dev/null &
openscad $P --camera=11,42,-5,55,0,50,175 -D 'part="closed"' -o $R/case_closed.png $S 2>/dev/null &
wait
# close-ups of the openings (closed case with the assembled PCB inside)
openscad $P --camera=25,44,4,85,0,90,40   -D 'part="closed"' -o $R/closeup_power_switch.png $S 2>/dev/null &
openscad $P --camera=25,58,4,80,0,90,55   -D 'part="closed"' -o $R/closeup_thumbwheel.png $S 2>/dev/null &
openscad $P --camera=-3,57,3,80,0,270,50  -D 'part="closed"' -o $R/closeup_usb_c.png $S 2>/dev/null &
openscad $P --camera=16,80,9,0,0,0,40     -D 'part="closed"' -o $R/closeup_led_bar.png $S 2>/dev/null &
python3 -c "
import trimesh,re
x=float(re.search(r'bar_leds = \[\[[-\d.]+, [-\d.]+\], \[([-\d.]+),',open('case_params.scad').read()).group(1))
m=trimesh.load('/tmp/pcb_assembly.stl'); m.update_faces(m.triangles_center[:,0]>=x); m.remove_unreferenced_vertices(); m.export('/tmp/pcb_assembly_cut.stl')"
openscad $P --camera=22,78,3,80,0,270,60 -D 'part="cutaway"' -o $R/cutaway_led_tunnels.png $S 2>/dev/null &
openscad $P --camera=11,-4,4,80,0,0,55   -D 'part="closed"' -o $R/closeup_jack_end.png $S 2>/dev/null &
wait
rm -f $R/closeup_front_usb_leds.png
tail -4 case_fit_report.txt
