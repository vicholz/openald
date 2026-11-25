#!/bin/bash
# Regenerate dock_params.scad from the PCB layout, export print STLs, run the fit check (all three radios), render previews.
# t121u (2026-11-24): flat dock, 6 pockets recessed 25 mm (aligned 3 x 2 grid), radios standing on their bottom-end USB-C. Needs openscad, python3 trimesh+manifold3d+scipy,
# KiCad 9 pcbnew (part boxes) and matplotlib. The radio cases are exported from their own SCAD files by the fit check.
set -e
cd "$(dirname "$0")"
python3 gen_dock_params.py >/dev/null
cd ../case
S=openald_dock.scad
rm -f floor_pads/*.stl
openscad -D 'part="shell"' -o dock_top_shell.stl $S 2>/dev/null &
openscad -D 'part="base"'  -o dock_base.stl $S 2>/dev/null &
openscad -D 'part="pads"'  -o dock_floor_pads_x6.stl $S 2>/dev/null &
for p in shell_raw base_raw pads_raw radios plugs; do openscad -D "part=\"$p\"" -o /tmp/dock_$p.stl $S 2>/dev/null & done
wait
for i in 0 1 2 3 4 5; do openscad -D 'part="pad"' -D "pad_index=$i" -o floor_pads/dock_floor_pad_slot$((i+1)).stl $S 2>/dev/null & done
wait
python3 ../scripts/check_dock_fit.py 2>/dev/null | grep -v "memory leak" > dock_fit_report.txt
P="--imgsize=1400,1000 --colorscheme=Tomorrow --projection=p"
R=../previews
rm -f $R/dock_*.png
O="--imgsize=1400,1000 --colorscheme=Tomorrow --projection=o"
openscad $P --camera=85,56,40,55,0,20,550  -D 'part="assembly"' -o $R/dock_assembly.png $S 2>/dev/null &
openscad $P --camera=85,56,40,60,0,200,550 -D 'part="assembly"' -o $R/dock_assembly_rear.png $S 2>/dev/null &
openscad $P --camera=85,56,40,55,0,20,590  -D 'part="exploded"' -o $R/dock_exploded.png $S 2>/dev/null &
openscad $P --camera=54,40,55,75,0,0,320   -D 'part="assembly"' -o $R/dock_front_view.png $S 2>/dev/null &
openscad $O --camera=85,56,30,0,0,0,330    -D 'part="assembly"' -o $R/dock_top_view.png $S 2>/dev/null &
openscad $P --render --camera=160,110,0,50,0,20,640 -D 'part="print"' -o $R/dock_print_layout.png $S 2>/dev/null &
python3 ../scripts/plot_insertion.py $R/dock_plug_insertion_per_radio.png &
wait
tail -1 dock_fit_report.txt
