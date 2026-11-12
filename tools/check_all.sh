#!/bin/bash
# Non-destructive design checks for all three OpenALD subprojects (KiCad 9 kicad-cli + pcbnew python).
# Reports go to $OUT (default /tmp/openald-checks); nothing in the repo is modified.
#   tools/check_all.sh          ERC + DRC + JLC CPL fit check for every board
#   tools/check_all.sh --case   also rebuild the cases and run the 3D fit checks (slow: ~3-10 min each;
#                               this DOES rewrite the STLs/previews/fit reports in the working tree)
# Expected results (v1.0, 2026-11-11):
#   radio_single_board  ERC 0 errors / 2 warnings (accepted PE0/PE1 pin_to_pin), DRC 58 silk-only, 0 unconnected, 0 parity
#   charging_dock       ERC 0 / 0, DRC 75 silk-only, 0 unconnected, 0 parity
#   radio_adafruit_feather_rp2040  ERC 0 / 0, DRC 0 / 0 unconnected / 0 parity
#   every board         jlc_cpl_fit.py --check -> "correction table: OK"
#   --case              INTERFERENCES: 0 in each fit report
set -u
R="$(cd "$(dirname "$0")/.." && pwd)"; OUT=${OUT:-/tmp/openald-checks}; mkdir -p "$OUT"; fail=0
chk() { # name dir sch pcb
  local n=$1 d=$R/$2 sch=$3 pcb=$4
  echo "== $n"
  kicad-cli sch erc --severity-all --format report -o "$OUT/$n-erc.txt" "$d/kicad/$sch" >/dev/null 2>&1
  echo "  ERC: $(grep -E 'ERC messages' "$OUT/$n-erc.txt" | sed 's/^ *//')"
  grep -q "Errors 0 " "$OUT/$n-erc.txt" || { echo "  ERC FAIL"; fail=1; }
  kicad-cli pcb drc --severity-all --schematic-parity --format report -o "$OUT/$n-drc.txt" "$d/kicad/$pcb" >/dev/null 2>&1
  echo "  DRC: $(grep -E '^\*\* Found' "$OUT/$n-drc.txt" | tr '\n' ' ')"
  local nonsilk; nonsilk=$(grep -E '^\[' "$OUT/$n-drc.txt" | sed 's/:.*//' | grep -v '\[silk_' | wc -l)
  grep -E '^\[' "$OUT/$n-drc.txt" | sed 's/:.*//' | sort | uniq -c | sed 's/^/       /'
  grep -q "Found 0 unconnected pads" "$OUT/$n-drc.txt" && [ "$nonsilk" = 0 ] || { echo "  DRC FAIL (non-silk violations or unconnected pads)"; fail=1; }
  (cd "$d/scripts" && python3 jlc_cpl_fit.py --check 2>&1 | tail -1 | sed 's/^/  JLC CPL: /')
  (cd "$d/scripts" && python3 jlc_cpl_fit.py --check 2>&1 | grep -q "correction table: OK") || { echo "  JLC CPL FAIL"; fail=1; }
}
chk radio_single_board radio_single_board openald.kicad_sch openald.kicad_pcb
chk charging_dock charging_dock openald-dock.kicad_sch openald-dock.kicad_pcb
chk feather_controls radio_adafruit_feather_rp2040 openald-feather-controls.kicad_sch openald-feather-controls.kicad_pcb
if [ "${1:-}" = "--case" ]; then
  [ -d "${KICAD9_3DMODEL_DIR:-/usr/share/kicad/3dmodels}/Capacitor_SMD.3dshapes" ] || echo "WARNING: KiCad 3D models not found (install kicad-packages3d or set KICAD9_3DMODEL_DIR); the radio fit check will only cover the project's own models"
  echo "== case fit: radio_single_board"; bash "$R/radio_single_board/scripts/build_case.sh" >/dev/null 2>&1; tail -1 "$R/radio_single_board/case/case_fit_report.txt"
  echo "== case fit: charging_dock";      bash "$R/charging_dock/scripts/build_case.sh" >/dev/null 2>&1; tail -1 "$R/charging_dock/case/dock_fit_report.txt"
  echo "== case fit: feather";            bash "$R/radio_adafruit_feather_rp2040/case/build_case.sh" >/dev/null 2>&1; tail -1 "$R/radio_adafruit_feather_rp2040/case/case_fit_report.txt"
  for f in radio_single_board/case/case_fit_report.txt charging_dock/case/dock_fit_report.txt radio_adafruit_feather_rp2040/case/case_fit_report.txt; do
    grep -qE "INTERFERENCES: 0|PASS \(0 interferences\)" "$R/$f" || { echo "  FIT FAIL: $f"; fail=1; }; done
fi
[ $fail = 0 ] && echo "ALL CHECKS PASSED" || { echo "SOME CHECKS FAILED"; exit 1; }
