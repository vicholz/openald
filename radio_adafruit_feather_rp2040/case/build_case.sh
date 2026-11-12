#!/bin/bash
# Regenerate case parameters, export print-ready STLs, run the fit + dock checks, render previews.
# Needs: openscad (2021.01+), python3 with trimesh + manifold3d + shapely, KiCad 9 python (pcbnew).
# The dock check compares against the single-board case: set REF_CASE_DIR to its case/ folder (default ../../radio_single_board/case).
set -e
cd "$(dirname "$0")"
python3 ../scripts/feather_data.py >/dev/null
python3 ../scripts/gen_case_params.py >/dev/null
S=openald_feather_case.scad
mkdir -p stl ../previews
openscad -D 'part="top"'    -o stl/case_top.stl    $S 2>/dev/null &
openscad -D 'part="bottom"' -o stl/case_bottom.stl $S 2>/dev/null &
openscad -D 'part="frame"'  -o stl/frame.stl       $S 2>/dev/null &
openscad -D 'part="top_raw"'    -o /tmp/f_top.stl    $S 2>/dev/null &
openscad -D 'part="bottom_raw"' -o /tmp/f_bottom.stl $S 2>/dev/null &
openscad -D 'part="frame_raw"'  -o /tmp/f_frame.stl  $S 2>/dev/null &
wait
python3 ../scripts/check_fit.py /tmp/f_top.stl /tmp/f_bottom.stl /tmp/f_frame.stl 2>/dev/null > case_fit_report.txt
REF=${REF_CASE_DIR:-../../radio_single_board/case}
if [ -f "$REF/openals_case.scad" ] || [ -f "$REF/openald_case.scad" ]; then
  RS=$(ls $REF/open*_case.scad | head -1)
  (cd $REF && openscad -D 'part="top_raw"' -o /tmp/ref_top.stl $(basename $RS) 2>/dev/null & cd $REF && openscad -D 'part="bottom_raw"' -o /tmp/ref_bot.stl $(basename $RS) 2>/dev/null; wait)
fi
[ -f /tmp/ref_top.stl ] && python3 ../scripts/check_dock.py /tmp/f_top.stl /tmp/f_bottom.stl /tmp/ref_top.stl /tmp/ref_bot.stl 2>/dev/null > dock_check_report.txt
P="--imgsize=1200,900 --colorscheme=Tomorrow --projection=p"
R=../previews
openscad $P --camera=19,43,5,60,0,35,230   -D 'part="assembly"' -o $R/case_exploded.png $S 2>/dev/null &
openscad $P --camera=19,43,0,55,0,40,175   -D 'part="closed"'   -o $R/case_closed.png $S 2>/dev/null &
openscad $P --camera=19,43,0,60,0,220,175  -D 'part="closed"'   -o $R/case_closed_back.png $S 2>/dev/null &
openscad $P --render --camera=75,43,10,45,0,200,260 -D 'part="print"' -o $R/case_print_layout.png $S 2>/dev/null &
wait
openscad $P --camera=19,-2,4,80,0,0,50    -D 'part="closed"' -o $R/closeup_usb_end.png $S 2>/dev/null &
openscad $P --camera=19,20,9,10,0,0,70    -D 'part="closed"' -o $R/closeup_top_led_windows.png $S 2>/dev/null &
openscad $P --camera=42,70,4,85,0,90,55   -D 'part="closed"' -o $R/closeup_wheel_switch.png $S 2>/dev/null &
openscad $P --camera=12,90,4,80,0,180,55  -D 'part="closed"' -o $R/closeup_jack_end.png $S 2>/dev/null &
openscad $P --camera=19,43,0,0,0,0,200   -D 'part="frame"' -o $R/frame_top_view.png $S 2>/dev/null &
openscad $P --camera=19,30,-7,90,0,0,95   -D 'part="section"' -D 'sec_y=30' -o $R/section_y30.png $S 2>/dev/null &
openscad $P --camera=19,70,-7,90,0,0,95   -D 'part="section"' -D 'sec_y=70' -o $R/section_y70.png $S 2>/dev/null &
wait
echo done
