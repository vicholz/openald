#!/bin/bash
# Full regeneration: footprints -> symbols -> schematic -> ERC -> board -> route -> DRC
set -e
cd "$(dirname "$0")"
python3 make_footprints.py >/dev/null
python3 make_symbols.py >/dev/null
python3 gen_sch.py
(cd ../kicad && kicad-cli sch erc --severity-all --format report -o ../fab/erc_report.txt openald.kicad_sch >/dev/null; tail -1 ../fab/erc_report.txt)
python3 build_pcb.py | head -1
python3 fix_pro.py
python3 route_pcb.py ${1:-60} 2>&1 | grep -E "SES import|tracks|dangling"
python3 stitch_gnd.py 2>&1 | grep -v SetWidth
(cd ../kicad && kicad-cli pcb drc --severity-all --schematic-parity --format report -o ../fab/drc_report.txt openald.kicad_pcb >/dev/null; grep -E "^\*\* Found" ../fab/drc_report.txt; grep -E "^\[" ../fab/drc_report.txt | sed 's/:.*//' | sort | uniq -c)
