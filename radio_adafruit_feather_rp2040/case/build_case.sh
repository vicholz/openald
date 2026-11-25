#!/bin/bash
# Regenerate case parameters, export print-ready STLs, run the fit check and render previews.
# t122u: 35.9 x 98.71 x 33.86 mm (t116u was 31.9 wide), bottom-end USB-C = the Feather's own, same dock pocket as the single-board radio.
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
openscad $P --camera=0,48,17,60,0,35,280   -D 'part="assembly"' -o $R/case_exploded.png $S 2>/dev/null &
openscad $P --camera=0,48,17,55,0,40,210   -D 'part="closed"'   -o $R/case_closed.png $S 2>/dev/null &
openscad $P --camera=0,48,17,120,0,220,210 -D 'part="closed"'   -o $R/case_closed_back.png $S 2>/dev/null &
openscad $P --render --camera=40,48,10,45,0,200,280 -D 'part="print"' -o $R/case_print_layout.png $S 2>/dev/null &
wait
# close-ups (frame: X right/wheel side, Y = 0 at the bottom-end inner wall (USB-C), Z = 0 at the back face)
openscad $P --camera=0,-2,24,80,0,0,75       -D 'part="closed"' -o $R/closeup_dock_usb_c.png $S 2>/dev/null &
openscad $P --camera=0,96,24,80,0,180,75     -D 'part="closed"' -o $R/closeup_jack_end_fm.png $S 2>/dev/null &
openscad $P --camera=0,12,34,20,0,0,70       -D 'part="closed"' -o $R/closeup_feather_leds.png $S 2>/dev/null &
openscad $P --camera=16,58,24,75,0,90,75     -D 'part="closed"' -o $R/closeup_wheel.png $S 2>/dev/null &
openscad $P --camera=-16,56,24,75,0,270,75   -D 'part="closed"' -o $R/closeup_switch.png $S 2>/dev/null &
openscad $P --camera=0,48,34,0,0,90,190      -D 'part="closed"' -o $R/front_face.png $S 2>/dev/null &
openscad $O --camera=0,2,17,90,0,0,70        -D 'part="section"' -D 'sec_y=2' -o $R/section_feather_y2.png $S 2>/dev/null &
openscad $O --camera=0,58,17,90,0,0,70       -D 'part="section"' -D 'sec_y=58.7' -o $R/section_wheel_y58.png $S 2>/dev/null &
openscad $O --camera=0,80,17,90,0,0,70       -D 'part="section"' -D 'sec_y=80' -o $R/section_fm_y80.png $S 2>/dev/null &
wait
# t122u close-ups: switch from inside (studs, pocket, backing ribs), FM module pegs/standoffs (section through its
# right-hand holes), Feather centring pegs (section through its left-hand holes), jack in the end wall (section x = 0)
openscad $P --camera=-14,56,27,140,0,90,80  -D 'part="switch_detail"' -o $R/closeup_switch_inside.png $S 2>/dev/null &
openscad $P --camera=10,82,27,65,0,60,95     -D 'part="xsection"' -D 'sec_x=10' -o $R/closeup_fm_module_pegs.png $S 2>/dev/null &
openscad $P --camera=-8.9,26,27,65,0,60,95   -D 'part="xsection"' -D 'sec_x=-8.89' -o $R/closeup_feather_pins.png $S 2>/dev/null &
openscad $P --camera=0,88,26,75,0,80,70      -D 'part="xsection"' -D 'sec_x=0' -o $R/section_jack_x0.png $S 2>/dev/null &
wait
echo done
