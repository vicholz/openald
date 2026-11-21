#!/bin/bash
# Export the MI03 case STLs, the fit-check poses and the previews.  Run from anywhere.
set -e
cd "$(dirname "$0")/.."
S=mi03_case.scad
O="openscad"
$O -D 'part="front"'      -o stl/mi03_front_shell.stl $S 2>/dev/null &
$O -D 'part="back"'       -o stl/mi03_back_shell.stl  $S 2>/dev/null &
$O -D 'part="plunger"'    -o stl/mi03_button_plunger.stl $S 2>/dev/null &
$O -D 'part="switch_cap"' -o stl/mi03_switch_cap.stl  $S 2>/dev/null &
$O -D 'part="battery_frame"' -o stl/mi03_battery_frame.stl $S 2>/dev/null &
mkdir -p /tmp/mi03fit
for p in front_raw back_raw frame_raw plungers_raw ghost_pcb ghost_front ghost_holder ghost_screws; do
  $O -D "part=\"$p\"" -o /tmp/mi03fit/$p.stl $S 2>/dev/null &
done
$O -D 'part="front_raw"' -D 'lcd_press="none"' -o /tmp/mi03fit/front_raw_nopress.stl $S 2>/dev/null &
for sh in -1 0 1; do
  $O -D 'part="cap_raw"' -D "cap_shift=$sh" -o /tmp/mi03fit/cap_$sh.stl $S 2>/dev/null &
  $O -D 'part="ghost_back"' -D "cap_shift=$sh" -o /tmp/mi03fit/ghost_back_$sh.stl $S 2>/dev/null &
done
wait
python3 scripts/check_fit.py > fit_report.txt
cat fit_report.txt
# previews
P="--imgsize=1200,900 --colorscheme=Tomorrow --projection=p"
R=previews
$O $P --camera=0,40,0,55,0,25,190   -D 'part="closed"'   -o $R/front_iso.png $S 2>/dev/null &
$O $P --camera=0,40,-10,235,0,30,230 -D 'part="closed"' -o $R/back_iso.png $S 2>/dev/null &
$O $P --camera=0,40,5,60,0,35,230   -D 'part="exploded"' -o $R/exploded.png $S 2>/dev/null &
$O $P --camera=55,40,8,13,53,-2 -D 'part="closed"'   -o $R/closeup_switch_cap.png $S 2>/dev/null &
$O $P --camera=-55,60,8,-13,53,-2 -D 'part="closed"'  -o $R/closeup_usb_c.png $S 2>/dev/null &
$O $P --camera=15,-45,5,0,-3,-8 -D 'part="closed"'   -o $R/closeup_jack_end.png $S 2>/dev/null &
$O $P --render --camera=0,40,-12,35,0,20,180 -D 'part="back_raw"' -o $R/back_shell_inside.png $S 2>/dev/null &
$O $P --render --camera=10,40,10,45,0,30,200 -D 'part="print"' -o $R/print_layout.png $S 2>/dev/null &
wait
python3 scripts/sections.py
