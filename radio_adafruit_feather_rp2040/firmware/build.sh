#!/bin/bash
# Compile (and optionally upload) the OpenALD Feather RP2040 v1.0 firmware with arduino-cli.
#   ./build.sh            compile only (output in ./build)
#   ./build.sh /dev/ttyACM0   compile and upload over USB (or copy build/*.uf2 to the RPI-RP2 drive after a RESET double-tap)
# First run installs the Earle Philhower RP2040 core and the Adafruit NeoPixel library.
set -e
cd "$(dirname "$0")"
URL=https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json
FQBN=rp2040:rp2040:adafruit_feather
arduino-cli core list | grep -q '^rp2040:rp2040' || { arduino-cli core update-index --additional-urls $URL; arduino-cli core install rp2040:rp2040 --additional-urls $URL; }
arduino-cli lib list | grep -q 'Adafruit NeoPixel' || arduino-cli lib install "Adafruit NeoPixel"
arduino-cli compile --fqbn $FQBN --warnings all --output-dir build openald_feather
[ -n "${1:-}" ] && arduino-cli upload --fqbn $FQBN -p "$1" --input-dir build openald_feather
ls -l build/*.uf2
