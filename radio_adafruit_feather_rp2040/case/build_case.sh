#!/bin/bash
# Regenerate case parameters, export print-ready STLs, run the fit check and render previews.
# 2026-11-24 unified envelope (32.9 x 89.75 x 34.83 mm, dock port shared with the MI03 and single-board radios).
# Needs: openscad (2021.01+), python3 with trimesh + manifold3d + numpy. The charging-dock insertion check for all three
# radios lives in charging_dock/scripts/check_dock_fit.py.
set -e
cd "$(dirname "$0")"
python3 ../scripts/feather_data.py >/dev/null
python3 ../scripts/gen_case_params.py >/dev/null
S=openald_feather_case.scad
mkdir -p ../previews
openscad -D 'part="top"'    -o case_top.stl    $S 2>/dev/null &
openscad -D 'part="bottom"' -o case_bottom.stl $S 2>/dev/null &
openscad -D 'part="deck"'   -o deck.stl        $S 2>/dev/null &
openscad -D 'part="top_raw"'    -o /tmp/f_top.stl    $S 2>/dev/null &
openscad -D 'part="bottom_raw"' -o /tmp/f_bottom.stl $S 2>/dev/null &
openscad -D 'part="deck_raw"'   -o /tmp/f_deck.stl   $S 2>/dev/null &
wait
python3 ../scripts/check_fit.py /tmp/f_top.stl /tmp/f_bottom.stl /tmp/f_deck.stl 2>/dev/null > case_fit_report.txt
P="--imgsize=1200,900 --colorscheme=Tomorrow --projection=p"
O="--imgsize=1200,900 --colorscheme=Tomorrow --projection=o"
R=../previews
openscad $P --camera=0,44,17,60,0,35,260   -D 'part="assembly"' -o $R/case_exploded.png $S 2>/dev/null &
openscad $P --camera=0,44,17,55,0,40,200   -D 'part="closed"'   -o $R/case_closed.png $S 2>/dev/null &
openscad $P --camera=0,44,17,120,0,220,200 -D 'part="closed"'   -o $R/case_closed_back.png $S 2>/dev/null &
openscad $P --render --camera=40,44,10,45,0,200,260 -D 'part="print"' -o $R/case_print_layout.png $S 2>/dev/null &
wait
openscad $P --camera=-16,57,27,80,0,270,60 -D 'part="closed"' -o $R/closeup_dock_usb_c.png $S 2>/dev/null &
openscad $P --camera=0,0,24,80,0,0,75      -D 'part="closed"' -o $R/closeup_jack_end_fm.png $S 2>/dev/null &
openscad $P --camera=0,88,12,80,0,180,70   -D 'part="closed"' -o $R/closeup_top_end_feather_usb.png $S 2>/dev/null &
openscad $P --camera=16,45,24,70,0,80,75   -D 'part="closed"' -o $R/closeup_wheel_switch.png $S 2>/dev/null &
openscad $P --camera=0,44,34,0,0,0,120     -D 'part="closed"' -o $R/front_face.png $S 2>/dev/null &
openscad $O --camera=0,14,17,90,0,0,70     -D 'part="section"' -D 'sec_y=14' -o $R/section_fm_y14.png $S 2>/dev/null &
openscad $O --camera=0,57,17,90,0,0,70     -D 'part="section"' -D 'sec_y=57.45' -o $R/section_dock_usb_y57.png $S 2>/dev/null &
openscad $O --camera=0,70,17,90,0,0,70     -D 'part="section"' -D 'sec_y=70' -o $R/section_switch_y70.png $S 2>/dev/null &
wait
echo done
