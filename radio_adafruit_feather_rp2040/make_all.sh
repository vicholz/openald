#!/bin/bash
# Rebuild everything for OpenALD Feather RP2040 v1.0 (run from this folder).
# Direct-mount version: no PCB. Needs OpenSCAD 2021.01+, kicad-cli 9 (wiring schematic ERC/PDF), python3: trimesh manifold3d shapely numpy cairosvg.
# Firmware is built separately: firmware/build.sh (arduino-cli).
# (The retired controls-board PCB and its generators are kept, unmaintained, in archive/controls_board_pcb/.)
set -e
cd "$(dirname "$0")/scripts"
python3 feather_data.py            # Feather mechanics from Adafruit's Eagle board (ref/)
python3 make_wiring.py
python3 make_schematic.py
(cd ../docs/wiring_schematic && kicad-cli sch erc --severity-all --exit-code-violations -o /tmp/openald-feather-wiring-erc.txt openald-feather-wiring.kicad_sch >/dev/null \
  && kicad-cli sch export pdf -o openald-feather-wiring.pdf openald-feather-wiring.kicad_sch >/dev/null && echo "wiring schematic: ERC clean, PDF exported")
../case/build_case.sh
