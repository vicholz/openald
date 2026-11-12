#!/bin/bash
# Build the per-subproject zip packages (the GitHub Release assets) from the committed tree (HEAD).
# Output: dist/openald-v1.0-package.zip, dist/openald-dock-v1.0-package.zip, dist/openald-feather-rp2040-v1.0-package.zip
set -e
cd "$(dirname "$0")/.."; mkdir -p dist; V=${VERSION:-v1.0}
pkg() { git archive --format=zip --prefix="$2/" --add-file=LICENSE -o "dist/$3" "HEAD:$1"; echo "dist/$3"; }
pkg radio_single_board            "openald-$V"              "openald-$V-package.zip"
pkg charging_dock                 "openald-dock-$V"         "openald-dock-$V-package.zip"
pkg radio_adafruit_feather_rp2040 "openald-feather-rp2040-$V" "openald-feather-rp2040-$V-package.zip"
