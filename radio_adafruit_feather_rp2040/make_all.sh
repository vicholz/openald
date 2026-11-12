#!/bin/bash
# Rebuild everything for OpenALD Feather RP2040 v1.0 (run from this folder).
# Needs KiCad 9 (kicad-cli + pcbnew python), Java 21+ and Freerouting (FREEROUTING=/path/freerouting.jar),
# OpenSCAD 2021.01+, python3: trimesh manifold3d shapely numpy cairosvg.
set -e
cd "$(dirname "$0")/scripts"
python3 feather_data.py            # Feather mechanics from Adafruit's Eagle board (ref/)
python3 make_footprints.py && python3 make_symbols.py
python3 gen_sch.py
kicad-cli sch erc --severity-all --format report -o ../fab/erc_report.txt ../kicad/openald-feather-controls.kicad_sch
python3 build_pcb.py && python3 fix_pro.py && python3 route_pcb.py 40 && python3 fix_pro.py
kicad-cli pcb drc --severity-all --schematic-parity --format report -o ../fab/drc_report.txt ../kicad/openald-feather-controls.kicad_pcb
python3 make_fab.py && python3 jlc_cpl_fit.py --check
python3 make_wiring.py
../case/build_case.sh
