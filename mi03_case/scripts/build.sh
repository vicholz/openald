#!/bin/bash
# Export the MI03 case STLs, the fit-check poses and the previews.  Run from anywhere.
set -e
cd "$(dirname "$0")/.."
S=mi03_case.scad
O="openscad"
mkdir -p /tmp/mi03fit
$O -D 'part="front"'      -o stl/mi03_front_shell.stl $S 2>/dev/null &
$O -D 'part="back"'       -o stl/mi03_back_shell.stl  $S 2>/dev/null &
$O -D 'part="plunger"'    -o stl/mi03_button_plunger.stl $S 2>/dev/null &
$O -D 'part="switch_carrier"' -o stl/mi03_switch_carrier.stl $S 2>/dev/null &
$O -D 'part="switch_knob"'    -o stl/mi03_switch_knob.stl    $S 2>/dev/null &
for m in front back; do
  $O -D 'part="battery_frame"' -D "frame_mount=\"$m\"" -o stl/mi03_battery_frame_${m}_mount.stl $S 2>/dev/null &
  $O -D 'part="frame_raw"' -D "frame_mount=\"$m\"" -o /tmp/mi03fit/frame_raw_$m.stl $S 2>/dev/null &
  $O -D 'part="ghost_frame_screws"' -D "frame_mount=\"$m\"" -o /tmp/mi03fit/frame_screws_$m.stl $S 2>/dev/null &
done
for p in front_raw back_raw plungers_raw ghost_pcb ghost_front ghost_holder ghost_board_screws board_unit; do
  $O -D "part=\"$p\"" -o /tmp/mi03fit/$p.stl $S 2>/dev/null &
done
$O -D 'part="front_raw"' -D 'lcd_press="none"' -o /tmp/mi03fit/front_raw_nopress.stl $S 2>/dev/null &
for sh in -1 0 1; do
  $O -D 'part="carrier_raw"' -D "cap_shift=$sh" -o /tmp/mi03fit/carrier_$sh.stl $S 2>/dev/null &
  $O -D 'part="knob_raw"'    -D "cap_shift=$sh" -o /tmp/mi03fit/knob_$sh.stl $S 2>/dev/null &
  $O -D 'part="ghost_back"'  -D "cap_shift=$sh" -o /tmp/mi03fit/ghost_back_$sh.stl $S 2>/dev/null &
done
wait
python3 scripts/check_fit.py > fit_report.txt
cat fit_report.txt
# previews
P="--imgsize=1200,900 --colorscheme=Tomorrow --projection=p"
R=previews
$O $P --camera=0,40,0,55,0,25,195   -D 'part="closed"'   -o $R/front_iso.png $S 2>/dev/null &
$O $P --camera=0,40,-10,235,0,30,235 -D 'part="closed"' -o $R/back_iso.png $S 2>/dev/null &
$O $P --camera=0,40,0,60,0,35,260   -D 'part="exploded"' -o $R/exploded.png $S 2>/dev/null &
$O $P --camera=0,40,0,60,0,35,260   -D 'part="exploded"' -D 'frame_mount="back"' -o $R/exploded_frame_back_mount.png $S 2>/dev/null &
$O $P --camera=55,40,8,13,53,-2 -D 'part="closed"'   -o $R/closeup_switch_cap.png $S 2>/dev/null &
$O $P --camera=-55,60,8,-13,53,-2 -D 'part="closed"'  -o $R/closeup_usb_c.png $S 2>/dev/null &
$O $P --camera=-38,46,3,-13.75,53,-1.47 -D 'part="usb_view"' -o $R/closeup_usb_c_opening.png $S 2>/dev/null &
$O $P --camera=30,-75,10,0,-4,-4 -D 'part="closed"'   -o $R/closeup_jack_end.png $S 2>/dev/null &
$O $P --render --camera=0,40,-14,35,0,20,185 -D 'part="back_raw"' -o $R/back_shell_inside.png $S 2>/dev/null &
$O $P --render --camera=0,40,4,215,0,25,175 -D 'part="front_raw"' -o $R/front_shell_inside.png $S 2>/dev/null &
$O $P --render --camera=10,40,10,45,0,30,200 -D 'part="print"' -o $R/print_layout.png $S 2>/dev/null &
wait
python3 scripts/sections.py
