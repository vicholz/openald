# OpenALD — handoff / resume document

This file lets anyone (person or AI) pick the project up cold. It records **what exists, why it is the way it is, what
must not change, what is still open, and exactly how to rebuild and re-check everything**. The per-subproject READMEs
hold the full detail (the single-board README keeps every pre-release revision note and design review); this file is the
map and the decision log.

* Owner: Victor (GitHub `vicholz`). Designed 2026-11-09 … 2026-11-11 (America/Los_Angeles) with an AI assistant.
* Version: **v1.0** for every part. **Keep v1.0 even when changing the design** (owner's instruction).
* Status: **designed and CAD/datasheet-checked only. Nothing has been built, powered, programmed or measured.** Never
  describe any of it as hardware-validated until a real board has passed the checklist in §8.
* License: **released into the public domain under CC0 1.0** (see §11).

---

## 1. What OpenALD is
A pocket FM radio for headphones (the headphone cable is the antenna), one 18650 cell, USB-C charging and USB-C
programming, a thumbwheel for volume/tuning, a slide power switch, a battery-check button and a 3-LED battery-level bar,
in a 3D-printed case. Plus a 6-slot charging dock and an off-the-shelf (Feather RP2040) variant.

| Subproject | Main files | One-line status |
|---|---|---|
| `radio_single_board/` | `kicad/openald.kicad_{sch,pcb,pro}`, `case/openald_case.scad`, `fab/` | v1.0 design complete; ERC 0 err (2 accepted warnings), DRC 0 err/58 silk-only, CPL check OK, case fit 0 interferences |
| `charging_dock/` | `kicad/openald-dock.*`, `case/openald_dock.scad`, `scripts/geom.py` | v1.0 design complete; ERC 0/0, DRC 0 err/75 silk-only, CPL check OK, dock fit 0 interferences |
| `radio_adafruit_feather_rp2040/` | `kicad/openald-feather-controls.*`, `case/openald_feather_case.scad`, `scripts/layout.py` | v1.0 design complete; ERC 0/0, DRC 0, CPL check OK, fit PASS; FM-module geometry is estimated |

## 2. Hard constraints (from Victor — do not violate)
1. **Never change the single-board radio case thickness** (33.4 mm). Case outer size stays **43 × 92 × 33.4 mm**.
2. **USB-C stays centred** on the bottom edge (board x = 19.0 mm of 38).
3. **Keep the positions** of the power switch, headphone jack, thumbwheel, battery holder and battery-check button.
   (The level-bar LEDs were allowed to move for the dock; they did, once — see §3.)
4. **Version stays v1.0** even when the design changes (record changes in the history instead).
5. **Don't claim hardware validation.** Everything is datasheet/CAD-checked only.
6. Dock: 6 radios, 2 rows × 3, **~1 in (25.4 mm) between radios**, radios stand USB-C-down **2 in (50.8 mm)** deep,
   **one USB-C input at the rear centre** powers all six, footprint as compact as possible, level LEDs visible while docked.
7. Feather variant must keep the **same base (dock) footprint** as the single-board radio; it may be bigger above the dock line.
8. Dock files live in their own folder, separate from the radio.

## 3. Design history (chronological)
Dates are 2026, America/Los_Angeles. "rev" names are the pre-release names; the silkscreen now reads **OpenALD v1.0**.

| Stage | What happened / why |
|---|---|
| **Original spec** | Pocket FM radio: **ATtiny84A** MCU + **RDA5807M** (RRD-102 module), one 18650 cell, TP4056 USB-C charging with DW01A + FS8205A protection, XC6206 3.3 V LDO, Mitsumi SIQ-02FVS3 thumbwheel encoder with push (volume/tune), slide power switch sticking out of the case, battery-check button, a 5 mm RGB status LED, headphone cable as antenna, 3D-printed case. Note: the attached spec file itself could not be opened by the build tools; the design follows the written summary of the spec — **compare against Victor's original spec if it turns up.** |
| rev 1.0 → **1.1** | USB-C **centred** on the bottom edge (board grew 2 mm to **38 × 87 mm**, holder moved 3.55 mm toward the jack end); RGB LED moved to the top face, flush; bigger C&K OS102011 slide switch; smooth filleted recesses for USB plug and wheel. |
| **rev 2** | Flat-top 5 mm RGB LED (TJ-L5FP, C20613341) on a printed spacer; switch changed to **HRO SK-12E12-G5** (C136720; knob 3.5 × 2.5 mm, sticks out 2.8 mm, slide toward jack = ON). Switch body height raised the lid 0.6 mm → **case 43 × 92 × 33.4 mm** (frozen from here on). |
| **rev 3** | RGB LED replaced by a **3-LED battery-level bar** (KT-0603G green 0603, C12624, 1k each ≈ 0.85 mA) — originally a horizontal row above the USB-C; button-triggered level display; CHRG_SENSE (TP4056 nCHRG via Schottky D7) so firmware can show charging; light tunnels in the case. |
| **rev 3.1** | **JLC pick-and-place fix**: JLC places parts using the *EasyEDA/LCSC* footprint origin/rotation, which differs from KiCad's for several parts (J1 +1.41 mm Y, J2 rot +90 / −0.8 mm, SW1 rot −90, SW3 −2.44 mm X, U2 DW01A +270 not +180, U5 +0.03). Added `scripts/jlc_cpl_fit.py` (downloads EasyEDA footprints, fits pads at 0/90/180/270, writes `fab/jlc_cpl_fit.json` and overlay PNGs) and the `JLC_CORR` table in `make_fab.py`. `--check` re-derives and fails on disagreement. Drill/place origin moved to the true board corner. |
| **rev 4** | **USB programming**: ATtiny84A → **ATmega328PB-AU** (C132230, TQFP-32, internal 8 MHz, MiniCore/Optiboot) + **CH340K** USB-serial (C968586, VBUS-powered only) + USBLC6-2SC6 ESD + DTR auto-reset; MCU gets its own XC6206 (U6) fed by a Schottky-OR of switched VSYS / VBUS / button, so you can upload with the power switch off and the radio/battery untouched. Hardware I2C; ISP on J3 pogo pads. **PE0 tied to GND, PE1 to +3V3** so the **ATmega328P-AU (C14877) drops in** (those pins are GND/VCC on the 328P). Battery life with the switch off unchanged (CH340K/MCU have no battery path). |
| **rev 4.1** | Review fixes: battery ADC divider **47k/12k + 100 nF** (was 100k/33k), button sense divider **4.7k/10k**, docs. |
| **rev 4.2** | **Battery reverse-polarity protection**: P-FET **Q2 AO3401A** (C15127) in the cell + path, with gate driver **Q3 AO3400A** (C20917) + R23/R24 (1M); reversed cell is harmless; adds ~4.2 µA standby; drop ≤ 62 mV at 730 mA. Two full datasheet reviews. Low-battery firmware cutoff raised from 3.10 V to **3.25 V** (MCU rail ≈ 0.26 V below the cell; BOD can trip 2.5–2.9 V). |
| **rev 4.3** | **Charge current 730 mA (R3 = 1.5k) → ~900 mA (R3 = 1.2k, C22765, Basic)** using I = 1100/R_PROG (≈ 917 mA; datasheet table 1.2k = 900 mA). 1.3k rejected (Extended part, 846 mA). Charge time ~3.7–4 h for 3000 mAh. Needs a ≥ 1 A charger (USB 2.0 laptop port is 500 mA; for that use R3 = 2.4k C22940 ≈ 460 mA). **Thermal note:** TP4056 dissipates ~1.7–2.0 W at start of CC; inside the closed case it will likely hit thermal regulation (~140–145 °C) and throttle — slower, not damaging; unmeasured. Independent review: no hardware errors. |
| Vendor BOMs | Filled PCBWay (.xlsx) and NextPCB (.xls) official templates (38 lines, 74 placements/board, U4/BT1/J3 DNP). `scripts/make_vendor_boms.py`. |
| Minimal set | `fab/minimal/`: JLC places only J1, U1, U3, U7 (≈ $36 for 5 boards, estimate); LCSC hand-solder list with spares. |
| **OpenALS** | Project renamed "OpenALS" and reset to **v1.0** (folders, files, silkscreen, docs). Circuit unchanged. |
| **OpenALD** | Renamed to **OpenALD** ("a device, not a system"). Same v1.0. |
| Dock + LED move | For the dock the **level bar moved to a vertical column near the jack end**: D1/D5/D6 at x = 24.0, y = 15.4/12.4/9.4 mm (KiCad coords from top-left; D1 lowest, D6 nearest the jack, 3 mm pitch) ≈ 20 mm above the dock rim. Re-routed; nothing else moved; case thickness unchanged. TP4056 LEDs D3/D4 stay beside the USB-C (hidden when docked → firmware shows charging on the bar). **OpenALD Dock v1.0** designed in `charging_dock/`. |
| Feather variant | `radio_adafruit_feather_rp2040/` designed (see §5). |
| Repo | This GitHub repo created 2026-11-11; scripts made path-independent (no `/workspace` paths); `tools/` added; CC0 chosen. |

## 4. Single-board radio (radio_single_board) — key design facts
**Blocks:** USB-C (HRO TYPE-C-31-M-12, C165948; 5.1k CC pull-downs = default USB power) → TP4056 (C16581, PROG R3 1.2k)
→ DW01A (C351410) + FS8205A (C2830320) protection → Q2/Q3 reverse-polarity → MPD BH-18650-PC holder (bottom side).
SW1 SK-12E12-G5 switches VBAT → VSYS. U5 XC6206 → +3V3R (radio + I2C pull-ups). U6 XC6206 → +3V3 (MCU only) from
VMCU = D8 (VSYS) ∪ D9 (VBUS) ∪ D10 (button). RRD-102 module (U4, hand-soldered); audio through 100 µF caps + 600 Ω
ferrites; headphone ground via FB3 = antenna, coupled with 1 nF. Exact LCSC numbers for every part:
`fab/openald-BOM-human.csv`.

**Pin map (ATmega328PB TQFP-32, MiniCore names):** D3/PD3 ENC_B · D4/PD4 ENC_SW · pin 3 PE0 = GND and pin 6 PE1 = +3V3
(leave as inputs, no pull-up) · D5/PD5 LVL1 (D1, lowest) · D6/PD6 LVL2 (D5) · D9/PB1 LVL3 (D6, top) · PB3/4/5 ISP only ·
AREF 100 nF (use internal 1.1 V) · **A0/PC0 BAT_ADC** · **A1/PC1 BTN_SENSE** (high = pressed) · **A2/PC2 CHRG_SENSE**
(pull-up on, low = charging) · A4/A5 SDA/SCL (1k series, 4.7k pull-ups to +3V3R) · PC6 RESET (10k, DTR via 100 nF) ·
PD0/PD1 UART to CH340K (1k on TX) · D2/PD2 ENC_A. Spare: PB0, PB2, PB6, PB7, PC3, PD7, ADC6/7. Full table: radio README.

**Formulas**
* Battery: `V_sys = ADC/1023 × 1.1 × 59/12` (47k/12k divider, internal 1.1 V ref). 4.2 V → ~0.85 V at the pin (ADC ≈ 795).
  The 1.1 V reference is only 1.0–1.2 V: **calibrate once per board**.
* Button sense: 4.7k/10k divider; read as digital high or ADC1 threshold ≈ 1.3 V.
* Charge current: `I = 1100 V / R_PROG` → 1.2k ≈ 917 mA.
* LED current: ~0.85 mA typ through 1k from 3.3 V (KT-0603G Vf ≈ 2.4 V at 1 mA).
* Battery life (paper estimate): radio on ≈ 20–25 mA → ~130 h on a 3000 mAh cell; off ≈ 7–9 µA standby.

**Firmware requirements (no firmware exists yet)** — full spec in the radio README "Firmware spec":
* **Thumbwheel (SIQ-02FVS3):** A/B/S are switches to common C (GND). Use internal pull-ups; there is no RC or ESD.
  15 detents, one quadrature cycle (4 Gray-code transitions) per detent; count one step per detent, not per edge.
  1 ms state-table poll debounces. On the single board, PD2/PD3 are INT0/INT1 but at rest A or B may already be
  low, so wake from Power-down with pin-change (PCINT18/19/20), not INT0/INT1 low-level. Example code is in
  `radio_single_board/README.md` (MiniCore) and `radio_adafruit_feather_rp2040/docs/firmware_notes.md` (Arduino-Pico).
  Behaviour: turn = volume, push-and-turn = tune, long press = seek. Paper-verified only; not hardware-tested.
* Level bar off by default; show on SW2 press (+3 s). Levels: ≥ 3.90 V ●●● · 3.60–3.90 ●●○ · 3.40–3.60 ●○○ ·
  3.30–3.40 LED1 slow blink · < 3.30 LED1 fast blink. Sample ADC with LEDs off, 16-sample average, 50 mV hysteresis.
* **Low-battery cutoff 3.25 V**: mute/power down the RDA5807M and sleep the MCU (DW01A at ~2.5 V is the backstop).
* **Don't call `Wire.begin()` while the radio rail is off** (AVR pull-ups would back-feed ~80 µA/line into the
  unpowered RDA5807M); start Wire only when V_sys > 3 V, `Wire.end()` + SDA/SCL as inputs before power-off.
* **V_sys < 2.5 V with BTN_SENSE low = USB-only power** (switch off, MCU on VBUS): cell voltage unknown; keep radio off.
* Button-powered (switch off, SW2 held): add ~0.1–0.15 V for D2's drop (calibrate).
* While charging the reading is ~0.15 V high: estimate = V − 0.15 V; show "filling" blink.
* **Show charging on the level bar** — D3/D4 (TP4056 LEDs) are hidden inside the dock pocket.
* Keep `Serial` closed in normal use (UART back-feed into unpowered CH340K). BOD 2.7 V. Internal 8 MHz. RDA5807M I2C 0x10/0x11.
* Programming: burn bootloader once over J3 (3.3 V ISP, never 5 V), then upload over USB-C (CH340, MiniCore ATmega328 /
  variant 328PB, internal 8 MHz, 38400 baud safest).

## 5. Feather RP2040 variant — key facts and risks
* Parts: Adafruit Feather RP2040 (#4884), RDA5807M breakout with built-in 3.5 mm jack (~27 × 27 mm, 4-pin I2C: VCC,
  GND, SDA, SCL; runs 3.3–5 V, ~20 mA; use 3.3 V — not 5 V tolerant; drives 32 Ω headphones; headphone cable antenna),
  MPD BH-18650-PC holder + protected 18650 (Feather has no reverse-polarity protection), JST PH lead (#261), STEMMA QT
  cable (#4210), small JLC controls board (SIQ-02FVS3 wheel, SK-12E12 switch on Feather EN, 220k/220k battery divider,
  red/green charge-mirror LEDs driven from VBUS + the MCP73831 STAT pin via a fine wire to Feather R2).
* Case: bottom 52.8 mm identical to the single-board case (43 × 33.4 mm), tapers to 45.5 mm wide above; 92 mm long.
  Feather sits where the old PCB was so its USB-C lines up with the dock plug (no adapter). Older Feathers (rev B and
  before, 2.48 mm USB overhang): `python3 scripts/feather_data.py --usb-overhang 2.48` then `case/build_case.sh`.
* ~$32/radio in parts (estimate, excl. JLC/shipping/FM module).
* **Risks/TODO:** FM-module hole/jack positions are **estimates** (photo could not be measured) — measure and edit
  `scripts/layout.py` (table in its README) before printing; charging is only **200 mA (≈ 18–20 h)**; off-state drain
  ~0.4 mA via the Feather EN pull-up (~9 %/month; swap that resistor to 100k → ~50 µA total); battery change means
  lifting the frame; top end held by the lip only; STAT tap is a fine-wire joint; holder-to-deck margin 0.1 mm relies on
  the datasheet height 21.31 mm; wheel has no RC debounce.

## 6. Charging dock — key facts and risks
* **Power:** rear USB-C (HRO TYPE-C-31-M-12) → **HUSB238** PD sink (C7471904; requests the highest PDO ≤ 20 V with
  ≥ 2.25 A) → 4 A fuse + SMBJ22A TVS → AO4407A P-FET input switch → **2 × SY8205FCC** bucks (C111875, 5.10 V, slots
  1/2/4 and 3/5/6) → **SY6280AAC per slot** (C55136, ~1.45 A limit, 1.09–1.81 A) → vertical plug VBUS; 22k Rp on CC.
* **Charger requirement: USB-C PD ≥ 45 W offering 20 V ≥ 2.25 A or 15 V ≥ 3 A.** Bucks enable at ~11.2–13.1 V, so
  5 V/9 V never start them (red LED, dock off). **12 V-only chargers are unsupported.** Worst case 6 × ~0.95 A × 5.1 V ≈ 29 W.
* Mechanics: 191.8 × 111.7 × 62.5 mm, 25.4 mm gaps, 50.8 mm pockets, 0.35 mm/side guide zone (bottom 12 mm), 3 mm
  lead-in chamfer, switch-knob relief slot, vents, light pipe for the status LED; prints without supports but needs a
  ≥ 192 × 112 mm bed. Geometry source of truth: `charging_dock/scripts/geom.py`. Interface: `DOCK_INTERFACE.md`.
* **Risks/TODO:** vertical plug **C55200592 only 782 in stock** (buy spares; hand-soldered, 0.8 mm pitch, must be
  perpendicular); **plug height**: drawing says 11.6 mm (used) and 12.5 mm overall — measure; if taller, reprint thicker
  floor pads (`PAD_T`); power stage was **autorouted** then widened — review buck hot loops before ordering; no fan —
  check temperatures; HUSB238 negotiation, buck stability, SY6280 limits all untested. Est. $90–110 for 2 assembled
  boards + 1 printed case (estimate).
* **Using a non-JLC assembler:** CPL files carry JLC/EasyEDA corrections (`JLC_CORR`). For PCBWay/NextPCB etc., export a
  plain KiCad position file (`kicad-cli pcb export pos --format csv --units mm --use-drill-file-origin`) or ask
  the parent design to add a "generic" CPL output; do **not** reuse the JLC CPL.

## 7. Regeneration and checks
Tool versions used: KiCad **9.0.2** (Debian `kicad 9.0.2+dfsg-1`), OpenSCAD **2021.01**, Python **3.13.5**, packages in
`requirements.txt`, Freerouting (build 2026-10-05) on OpenJDK 25 (re-routing only). Stock KiCad 3D models are needed
for the case fit checks: `tools/fetch_kicad3d.sh && export KICAD9_3DMODEL_DIR=$PWD/tools/kicad3d` (or install
`kicad-packages3d`). Without them the radio fit check silently checks only the project's own models — a complete `case/case_fit_report.txt` has 82 part lines starting with `BT1` (the 18650 holder).

**Quick check (non-destructive):** `tools/check_all.sh` → expected:
```
radio_single_board  ERC 0 errors / 2 warnings   (pin_to_pin U3 pin 3 PE0–GND and pin 6 PE1–+3V3: intentional 328P drop-in)
                    DRC 58 = 8 silk_edge_clearance + 22 silk_over_copper + 28 silk_overlap; 0 unconnected; 0 parity
charging_dock       ERC 0/0; DRC 75 = 2 silk_edge_clearance + 39 silk_over_copper + 34 silk_overlap; 0 unconnected; 0 parity
feather_controls    ERC 0/0; DRC 0; 0 unconnected; 0 parity
each                jlc_cpl_fit.py --check -> "correction table: OK"
ALL CHECKS PASSED
```
**Case fit:** `tools/check_all.sh --case` (or each `build_case.sh`) → `INTERFERENCES: 0` (radio: closest to tunnel
walls FB2 0.40 mm; dock: outer 191.8 × 111.72 × 62.5); feather `RESULT: PASS (0 interferences)`. Takes ~3 min (radio),
longer for the dock; rewrites STLs/previews (diffs are mesh-ordering/timestamp noise).

**Per subproject** (run from the subproject folder):
| Step | radio_single_board | charging_dock | radio_adafruit_feather_rp2040 |
|---|---|---|---|
| Full PCB regen (re-routes! needs Freerouting) | `scripts/run_all_pcb.sh [passes]` | `scripts/run_all_pcb.sh [passes]` | `./make_all.sh` (everything) |
| Fab outputs | `cd scripts && python3 make_fab.py` and `python3 make_fab.py --minimal` | `cd scripts && python3 make_fab.py` | `cd scripts && python3 make_fab.py` |
| JLC CPL check | `cd scripts && python3 jlc_cpl_fit.py --check` (`--plots` for overlays) | same | same |
| Vendor BOMs | `cd scripts && python3 make_vendor_boms.py` | – | – |
| Case + fit + renders | `scripts/build_case.sh` | `scripts/build_case.sh` | `case/build_case.sh` |
| Previews | `python3 scripts/render_pcb_previews.py` | same | (in make_all/build_case) |

Notes: `make_fab.py` queries JLC's public parts API for live stock/price (slow, network); set **`OPENALD_OFFLINE=1`**
to reuse `fab/lcsc_lookup.json`. With fixed inputs, fab outputs regenerate byte-identical except timestamps (verified on a
fresh clone). Re-routing with Freerouting is **not deterministic** — after `run_all_pcb.sh` re-run DRC, `jlc_cpl_fit.py
--check`, `make_fab.py`, `build_case.sh` and re-inspect the layout. Scratch files go to `/tmp`. `FREEROUTING`, `JAVA`,
`EASYEDA_CACHE`, `KICAD9_3DMODEL_DIR`, `REF_CASE_DIR` (feather dock check) are the env overrides.
`tools/make_packages.sh` builds the release zips into `dist/`.

## 8. Hardware bring-up test checklist
Build **one** board of each kind first. Single-board radio:
1. Before fitting anything: meter-check the holder polarity (+ flat contact on the square pad at the USB-C end).
2. **Reverse cell** for ~1 s, **without and with USB**: VBAT (TP4056 pin 5) stays ≈ 0 V vs the holder − pad, nothing warms.
3. **Q2 drop while charging** < 60 mV (holder + pad → TP4056 BAT); standby current ≈ 7–9 µA (switch off, no USB).
4. Power switch direction (toward jack = ON); radio rail +3V3R stays 0 V with switch off and USB in.
5. CH340K enumerates; burn bootloader over J3 at 3.3 V; **USB upload works, including while charging** and with the switch off.
6. **Audio L/R**: confirm the headphone tip is the left channel / module pin 2 = R, pin 3 = L **before fitting U4 on
   all boards** (a swap can be fixed in firmware). Check FM reception with the headphone-cable antenna.
7. **ADC calibration**: measure the cell with a meter vs BAT_ADC; calibrate the 1.1 V reference, the D2 drop
   (button-powered) and the 0.15 V charging offset. Confirm CHRG_SENSE reads high with USB unplugged.
8. **Charge current ≈ 900 mA and temperatures**: TP4056 and cell temperature in the closed case on a full charge
   from ~3.0 V; note throttling and total charge time. Use a ≥ 1 A charger.
9. Level-bar visibility through the windows, light bleed between tunnels; wheel, button plunger and switch knob feel.
10. Case: print one, test-fit jack plug overmold (≤ 6.8 mm), inserts, screws.

Dock: 11. With a ≥ 45 W PD charger: green LED, 5.0–5.2 V on each slot VBUS; 5 V-only charger → red only, no slot voltage.
12. **Measure the plug height** (11.6 vs 12.5 mm) and insertion depth; adjust `PAD_T`. 13. Insert/remove a radio
repeatedly; check alignment tolerance (~0.5 mm). 14. **Thermal**: six radios charging at once — check radio, buck and
plug temperatures; per-slot current limit trips at ~1.1–1.8 A.

Feather variant: 15. **Measure the FM module** (outline, thickness, holes, jack position/height, bottom pin length,
tallest part) and update `scripts/layout.py` before printing. 16. Verify the 0.1 mm holder-to-deck gap with a real
cell. 17. STAT mirror LEDs behaviour; off-state drain; 200 mA charge time.

## 9. Open decisions / TODOs
* Write firmware (single board: MiniCore/Arduino per §4; Feather: Arduino-Pico or CircuitPython per its firmware_notes).
* Build and run §8; record measured values back into the READMEs (keep v1.0, add history notes).
* Dock: review autorouted power layout; decide plug sourcing (buy spares now); maybe a light pipe / angle for back-row bars.
* Optional: generic (non-JLC) placement output for other assemblers.
* Optional radio tweaks noted in reviews: RESET clamp Schottky if uploads are flaky; R3 2.4k for laptop USB charging;
  LED colour alternatives (KT-0603R C2286 basic).
* Possible separate project: smaller off-the-shelf builds (XIAO ESP32-C3 etc., §10). Victor chose to stay with v1.0 for now.
* Repo is private; Victor may make it public.

## 10. Research summaries (estimates, dated 2026-11-10/11; re-check before relying on them)
**Assembly vendors (5 boards, shipped to California):** JLCPCB Economic is the cheapest that could be priced with
confidence: ~$130–165 for 5 fully assembled radios incl. ~35 % tariff, excl. radio module/holder/cell. NextPCB has free
first-order assembly but a 50 mm minimum board width (ours is 38 mm) and stock gaps; PCBWay offers $29 first-order
assembly but higher parts prices and tariffs (37.5–47.5 %). Seeed, PCBgogo, ALLPCB, Elecrow are quote-only; US houses
(MacroFab) run several hundred dollars. DIY: bare boards + stencil from JLC (~$5) + LCSC parts ≈ $60–110; CH340K and
TP4056 have exposed pads (hot air/hotplate). Minimal JLC assembly (4 hard parts) ≈ $36 + shipping. Frameless stencil
recommended for hand work. Where to buy: JLCPCB + LCSC (combined shipping); PCBWay/NextPCB; OSH Park (US boards);
OSH Stencils; DigiKey/Mouser as backup (DW01A, FS8205A, HRO connectors need substitutes); RRD-102 from AliExpress/Amazon;
cells from a reputable seller.

**Off-the-shelf alternatives:** no breakout exists for the Mitsumi thumbwheel, so a small custom controls board is
always needed. Candidates: Seeed XIAO ESP32-C3 (~$5, 380 mA charge, ~75–120 h, best fit for the current case — the
recommended pick), XIAO nRF52840 ($9.99, ~130 h but 50–100 mA charge), LilyGO T-Energy S3 (~$15, built-in 18650,
bigger case, sold out), Adafruit Feather RP2040 ($11.95, 200 mA charge; used for the variant here). Avoid cheap
"18650 battery shield V3" boards. Victor's FM breakout (RDA5807M, jack, I2C) is assumed to be the same chip as the
single board, identified from size/labels/photo (chip markings not read).

**Stock caveats:** ATmega328PB-AU C132230 had only ~735 at LCSC (2026-11-10) → drop-in **ATmega328P-AU C14877**
(same footprint and CPL). Dock plug **C55200592: 782**. Re-check all stock before ordering.

## 11. License and third-party files
OpenALD (hardware designs, KiCad projects, generated fab files, OpenSCAD, scripts, docs) is **released into the public
domain under CC0 1.0 Universal** — see `LICENSE`. Third-party material keeps its own license:
* `radio_adafruit_feather_rp2040/ref/Adafruit Feather RP2040.brd` — Adafruit's Eagle board
  (github.com/adafruit/Adafruit-Feather-RP2040-PCB), **CC BY-SA** (attribution: Adafruit Industries).
  `ref/feather_rp2040_mech.json` is mechanical data parsed from it (treat as derived from the CC BY-SA file).
* `tools/easyeda/*.json` — cached footprint data from the JLCEDA/EasyEDA/LCSC public component library; subject to EasyEDA's terms.
* `radio_single_board/scripts/templates/` and the filled `fab/openald-BOM-pcbway.xlsx` / `openald-BOM-nextpcb.xls` — based on PCBWay's and NextPCB's BOM templates.
* Stock KiCad library footprints/symbols embedded in the boards and the STEP models fetched by `tools/fetch_kicad3d.sh`
  (not stored here) — KiCad libraries, CC-BY-SA 4.0 with the KiCad library exception.
* All `*.pretty`, `*.kicad_sym` and `*.3dshapes/*.wrl` files in this repo are generated by this project's scripts from
  datasheet dimensions (including `ref/single_board/` copies), so they are CC0. Vendor datasheets are **not** included.

## 12. Directory map
```
README.md / HANDOFF.md / LICENSE (CC0) / requirements.txt / .gitignore
tools/  check_all.sh  fetch_kicad3d.sh  make_packages.sh  easyeda/ (EasyEDA footprint cache)
radio_single_board/
  README.md                full design notes, ordering, programming, pin map, firmware spec, all revision notes/reviews
  kicad/                   openald.kicad_{pro,sch,pcb,prl}, openald.kicad_sym, openald.pretty/, openald.3dshapes/, lib tables
  fab/                     gerbers/, openald-gerbers-jlcpcb.zip, BOM/CPL (JLC), centroid, .pos, human BOM, PCBWay/NextPCB BOMs,
                           minimal/ (4-part JLC set + LCSC hand-solder list + cost), erc/drc reports, jlc_cpl_fit.json, lcsc_lookup.json
  case/                    openald_case.scad, case_params.scad (generated), STLs, nut_variant/, case_fit_report.txt
  previews/ docs/ (schematic PDF) scripts/ (design.py = netlist/BOM source, placement.py, generators, templates/)
charging_dock/
  README.md DOCK_INTERFACE.md kicad/ fab/ case/ (STLs, floor_pads/, dock_fit_report.txt) previews/ docs/
  scripts/                 geom.py = geometry source of truth, design.py, generators, plugsearch.py/jlcq.py (part search helpers)
radio_adafruit_feather_rp2040/
  README.md make_all.sh kicad/ fab/ case/ (stl/, reports) previews/ docs/ (pin map, firmware notes, BOM, wiring) ref/
  scripts/                 layout.py = mechanical source of truth, feather_data.py parses ref/*.brd
```
Generated (not hand-edited) files: `.kicad_sch`, `.kicad_pcb`, footprints/symbols/3D models, `case_params.scad`,
`dock_params.scad`, everything in `fab/`, `previews/` and STLs. Edit `design.py` / `placement.py` / `geom.py` /
`layout.py` / the `.scad` sources and regenerate.

## 13. Release packages
GitHub Release **v1.0** carries one zip per subproject (built with `tools/make_packages.sh` from the tagged commit).
Zips and `dist/` are git-ignored.
