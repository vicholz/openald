#!/bin/bash
# Rebuild everything for OpenALD Feather RP2040 v1.0 (run from this folder).
# Direct-mount version: no PCB. Needs OpenSCAD 2021.01+, python3: trimesh manifold3d shapely numpy cairosvg.
# (The retired controls-board PCB and its generators are kept, unmaintained, in archive/controls_board_pcb/.)
set -e
cd "$(dirname "$0")/scripts"
python3 feather_data.py            # Feather mechanics from Adafruit's Eagle board (ref/)
python3 make_wiring.py
../case/build_case.sh
