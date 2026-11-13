#!/bin/bash
# Regenerate dock_params.scad from the PCB layout, export print STLs, run the fit check, render previews.
set -e
cd "$(dirname "$0")"
python3 gen_dock_params.py >/dev/null
cd ../case
S=openald_dock.scad
openscad -D 'part="shell"' -o dock_top_shell.stl $S 2>/dev/null &
openscad -D 'part="base"'  -o dock_base.stl $S 2>/dev/null &
openscad -D 'part="pads"'  -o dock_floor_pads_x6.stl $S 2>/dev/null &
for p in shell_raw base_raw pads_raw radios plugs shims_raw radios_feather; do openscad -D "part=\"$p\"" -o /tmp/dock_$p.stl $S 2>/dev/null & done
wait
for i in 0 1 2 3 4 5; do openscad -D 'part="pad"' -D "pad_index=$i" -o floor_pads/dock_floor_pad_slot$((i+1)).stl $S 2>/dev/null & done
# riser shims (geom.py RISER): Feather always; single board only if a taller PLUG_H gives it a riser too
mkdir -p riser_shims
openscad -D 'part="shims"' -o riser_shims/dock_riser_shims_feather_x6.stl $S 2>/dev/null &
for i in 0 1 2 3 4 5; do openscad -D 'part="shim"' -D "shim_index=$i" -o riser_shims/dock_riser_shim_feather_slot$((i+1)).stl $S 2>/dev/null & done
SB=$(cd ../scripts && python3 -c 'import geom as G; print(G.RISER["single_board"])')
rm -f riser_shims/dock_riser_shims_single_board_x6.stl
if python3 -c "import sys; sys.exit(0 if $SB > 0 else 1)"; then
  openscad -D 'part="shims"' -D "shim_t=$SB" -o riser_shims/dock_riser_shims_single_board_x6.stl $S 2>/dev/null &
fi
wait
python3 ../scripts/check_dock_fit.py 2>/dev/null > dock_fit_report.txt
P="--imgsize=1400,1000 --colorscheme=Tomorrow --projection=p"
R=../previews
openscad $P --camera=96,56,30,55,0,25,420  -D 'part="assembly"' -o $R/dock_assembly.png $S 2>/dev/null &
openscad $P --camera=96,56,30,60,0,205,420 -D 'part="assembly"' -o $R/dock_assembly_rear.png $S 2>/dev/null &
openscad $P --camera=96,56,40,60,0,25,480  -D 'part="exploded"' -o $R/dock_exploded.png $S 2>/dev/null &
openscad $P --render --camera=95,56,32,90,0,90,260 -D 'part="section"' -o $R/dock_section_centre_column.png $S 2>/dev/null &
openscad $P --render --camera=150,80,0,40,0,20,520 -D 'part="print"' -o $R/dock_print_layout.png $S 2>/dev/null &
python3 ../scripts/plot_insertion.py $R/dock_plug_insertion_per_radio.png &
wait
tail -1 dock_fit_report.txt
