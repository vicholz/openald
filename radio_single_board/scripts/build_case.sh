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
# t116u: Y = 0 is the bottom (USB-C / dock) end, Y = pcb_h the top (jack) end; X 0 .. pcb_w (left .. right edge)
read W H SWY WHY BARX BARY JX <<< $(python3 -c "
import re;t=open('case_params.scad').read();g=lambda k:re.search(k+r' = ([^;]+);',t).group(1)
import json;W=float(g('pcb_w'));H=float(g('pcb_h'));so=float(g('sw_on_y'));sf=float(g('sw_off_y'));wh=json.loads(g('wheel_xy'));bl=json.loads(g('bar_leds'));jx=json.loads(g('jack_xy'))
print(W,H,(so+sf)/2,wh[1],bl[1][0],bl[1][1],jx[0])")
C=$(python3 -c "print($W/2)")
openscad $P --camera=$C,42,-5,60,0,35,200  -D 'part="assembly"' -o $R/case_assembly_exploded.png $S 2>/dev/null &
openscad $P --camera=$C,42,-5,70,0,235,200 -D 'part="assembly"' -o $R/case_assembly_back.png $S 2>/dev/null &
openscad $P --render --camera=$(python3 -c "print(1.5*$W+12)"),42,10,45,0,200,220 -D 'part="print"' -o $R/case_print_layout.png $S 2>/dev/null &
openscad $P --camera=$C,42,-5,55,0,50,175 -D 'part="closed"' -o $R/case_closed.png $S 2>/dev/null &
wait
# close-ups of the openings (closed case with the assembled PCB inside)
openscad $P --camera=$(python3 -c "print($W+3)"),$SWY,4,85,0,90,40   -D 'part="closed"' -o $R/closeup_power_switch.png $S 2>/dev/null &
openscad $P --camera=$(python3 -c "print($W+3)"),$WHY,4,80,0,90,55   -D 'part="closed"' -o $R/closeup_thumbwheel.png $S 2>/dev/null &
openscad $P --camera=$C,-3,3,80,0,0,50  -D 'part="closed"' -o $R/closeup_usb_c.png $S 2>/dev/null &
openscad $P --camera=$(python3 -c "print($BARX-2)"),$BARY,9,0,0,0,40     -D 'part="closed"' -o $R/closeup_led_bar.png $S 2>/dev/null &
python3 -c "
import trimesh,re
x=float(re.search(r'bar_leds = \[\[[-\d.]+, [-\d.]+\], \[([-\d.]+),',open('case_params.scad').read()).group(1))
m=trimesh.load('/tmp/pcb_assembly.stl'); m.update_faces(m.triangles_center[:,0]>=x); m.remove_unreferenced_vertices(); m.export('/tmp/pcb_assembly_cut.stl')"
openscad $P --camera=$BARX,$BARY,3,80,0,270,60 -D 'part="cutaway"' -o $R/cutaway_led_tunnels.png $S 2>/dev/null &
openscad $P --camera=$JX,$(python3 -c "print($H+3)"),4,80,0,180,55   -D 'part="closed"' -o $R/closeup_jack_end.png $S 2>/dev/null &
wait
rm -f $R/closeup_front_usb_leds.png
tail -4 case_fit_report.txt
