#!/bin/bash
# Fetch only the stock KiCad 9 STEP models that the three OpenALD boards reference (~4 MB) instead of
# installing the whole kicad-packages3d package (~350 MB deb). The 3D fit checks need them.
# Usage: tools/fetch_kicad3d.sh [DEST]   (default DEST=tools/kicad3d, git-ignored)
#        export KICAD9_3DMODEL_DIR=$PWD/tools/kicad3d
# (.wrl references are fetched together with their .step, which kicad-cli --subst-models uses; it needs both.)
# Models are from https://gitlab.com/kicad/libraries/kicad-packages3D (tag 9.0.2), CC-BY-SA 4.0 with the KiCad
# libraries exception; they are not redistributed in this repo.
set -e
R="$(cd "$(dirname "$0")/.." && pwd)"; DEST=${1:-$R/tools/kicad3d}
grep -ho '\${KICAD9_3DMODEL_DIR}/[^"]*' "$R"/*/kicad/*.kicad_pcb | sed 's/.*}\///' | sed 's/^\(.*\)\.wrl$/\1.wrl\n\1.step/' | sort -u | while read -r m; do
  [ -s "$DEST/$m" ] && continue
  mkdir -p "$(dirname "$DEST/$m")"
  curl -sfL --max-time 120 "https://gitlab.com/kicad/libraries/kicad-packages3D/-/raw/9.0.2/$m" -o "$DEST/$m" || echo "failed: $m"
done
echo "export KICAD9_3DMODEL_DIR=$DEST"
