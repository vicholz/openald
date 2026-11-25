# OpenALD Feather RP2040 v1.0

This is a variant of the OpenALD pocket FM radio built around an **Adafruit Feather RP2040**. It has:
* an FM module (Victor's module: **27.25 × 27.25 mm, 1.6 mm board, Ø3.8 mm holes in the corners on a 20 mm square,
  a 4-pin 90° through-board header and a standard 6.35 × 14 mm headphone jack, both centred on the bottom edge, the
  jack 1 mm past the board**),
* an 18650 cell in an MPD BH-18650-PC holder (the same holder as the single-board radio),
* a **Mitsumi SIQ-02FVS3 thumbwheel** (volume/tune + push) glued into a printed cradle on the deck,
* an **SS-12F16 slide switch** (SPDT, "G4" 4 mm knob by default) pressed into a groove in the case wall, no screws,
* hand-soldered wires to the Feather's header pads. **There is no custom PCB** in this variant.

**t116u (2026-11-24, still v1.0): bottom-end USB-C, dock-compatible with the single-board radio.** The Feather lies
flat at the bottom end and **its own USB-C is the charge / dock / programming port**, in the bottom end face,
**centred across the width, 6.62 mm behind the front face, mouth 1.0 mm inside the face** — the same spot as the
single-board radio, so both stand in the same charging-dock pocket (31.9 × 33.86 end footprint, see
`../charging_dock/DOCK_INTERFACE.md`). The USB-C breakout, the Schottky diode and the optional 3 mm charge LEDs are
gone; the Feather's own **CHG LED, red LED and NeoPixel shine through holes in the front face**. The MI03 radio keeps
its side USB-C and does not dock.

> **Status: design only. Nothing here has been printed, built or tested.**
> - FM module: outline, holes, jack and header from Victor's description; the header pin length/side, the jack
>   barrel diameter at the end wall and the module pin order are **assumed** (see "Measure and edit").
> - Feather part heights are datasheet estimates; board outline, holes, LEDs, buttons, pads and connectors come from
>   Adafruit's own Eagle file. Wheel and switch geometry come from their datasheets, not from measured parts.

![exploded](previews/case_exploded.png)

## Folder contents
| Path | What |
|---|---|
| `case/` | OpenSCAD source (`openald_feather_case.scad`), generated `case_params.scad` / `feather_params.scad`, print-ready **`case_top.stl`** (front shell), **`case_bottom.stl`** (back shell), **`deck.stl`** (inner plate), `case_fit_report.txt`, `build_case.sh` |
| `previews/` | `case_exploded.png`, `case_closed.png`, `case_closed_back.png`, `case_print_layout.png`, `front_face.png`, close-ups (`closeup_dock_usb_c.png`, `closeup_feather_leds.png`, `closeup_jack_end_fm.png`, `closeup_wheel.png`, `closeup_switch.png`) and sections (`section_feather_y2.png`, `section_wheel_y58.png`, `section_fm_y80.png`) |
| `docs/` | `wiring_diagram.svg/.png`, `wiring_schematic/` (KiCad 9 schematic + PDF), `pin_map.md`, `firmware_notes.md`, `BOM.md/.csv` |
| `firmware/` | **Arduino firmware** `openald_feather/` (arduino-pico core), `build.sh` (arduino-cli), prebuilt `openald_feather_v1.0.uf2`. Compiles; **not tested on hardware** |
| `scripts/` | `layout.py` (single source of truth for the mechanical layout), `feather_data.py`, `gen_case_params.py`, `check_fit.py`, `make_wiring.py`, `make_schematic.py` (+ `sexp.py`, `symlib.py`) |
| `ref/` | Adafruit Feather RP2040 Eagle board (CC BY-SA), the parsed mechanical data, and `models/SIQ-02FVS3.wrl` |
| `archive/controls_board_pcb/` | The **retired** controls PCB from before the direct-mount change. Not used, not maintained |
| `make_all.sh` | Rebuilds everything: Feather data → wiring diagram + schematic (ERC) → case params → STLs → fit check → renders |

The charging-dock check (this radio and the single-board radio in all six pockets) is
`../charging_dock/scripts/check_dock_fit.py`, run by the dock's `build_case.sh`.

## Firmware and wiring (added 2026-11-12)
* **Wiring:** [`docs/wiring_diagram.png`](docs/wiring_diagram.png) (and `.svg`) shows every hand-soldered wire; [`docs/wiring_schematic/openald-feather-wiring.pdf`](docs/wiring_schematic/openald-feather-wiring.pdf) is the same circuit as a KiCad 9 schematic (ERC 0 errors / 0 warnings); the pin table is in [`docs/pin_map.md`](docs/pin_map.md).
* **Firmware:** [`firmware/openald_feather/`](firmware/openald_feather/) is an Arduino sketch for Earle Philhower's arduino-pico core (board "Adafruit Feather RP2040") plus the Adafruit NeoPixel library. `firmware/build.sh` compiles it with arduino-cli; `firmware/openald_feather_v1.0.uf2` is a prebuilt image (double-tap RESET through the pin-hole, copy the .uf2 to the RPI-RP2 drive). **It compiles; it has not been run on hardware.**
* **Wheel:** turn = volume (0 mutes, 1–15), short press = battery level on the NeoPixel for 3 s, hold ≥ 0.5 s without turning = seek up, push and turn = tune (200 kHz per detent by default). The last frequency and volume are saved to flash 5 s after the last change; the first boot after flashing starts at **97.3 MHz** (the settings format was bumped on 2026-11-14 so a station saved by an older build is ignored once). At power-on the battery level is shown for **5 s**, then the NeoPixel turns off.
* **Battery level colours** (NeoPixel, 50 mV hysteresis, same thresholds as the single board's 3-LED bar): green ≥ 3.90 V, yellow 3.60–3.90, orange 3.40–3.60, red slow blink 3.30–3.40, red fast blink < 3.30. Below 3.25 V the radio is powered down (it restarts above 3.45 V). The NeoPixel is **off at all other times** (no seek, error or low-battery blinks) to save battery. Its power can't be cut: on the Feather RP2040 the WS2812B's VDD is wired straight to 3.3 V and there is no NeoPixel power pin (GPIO 20 is MISO on this board), so a dark pixel still draws its idle current (~1 mA typ., datasheet value, not measured) while the switch is ON. Seek and "FM module not found" are reported only on the USB serial log.
* **Differences from the single board:** no wheel-press battery check with the switch OFF (EN holds the Feather's regulator off, so nothing can run); the level is a NeoPixel colour, not a 3-LED bar (visible through the front face, also in the dock); the firmware cannot see the charge state (only the Feather's CHG LED shows it).

## Size, layout and the dock interface (t116u)
Case frame: X across (0 = centre, +X = right = wheel side), Y along (0 = inside of the bottom / USB-C end wall, top
(jack) end at +Y), Z from the back face (0) to the front face (33.86).

| | Value |
|---|---|
| Outside | **31.90 W × 98.71 L × 33.86 T**, edges r 2 (was 32.9 × 89.75 × 34.83 with the side USB-C) |
| Walls / floor / front | 2.0 / 1.4 / 1.6 |
| Parts | **back shell** (Z 0 – 23.61 + lip), **deck** (Z 22.61 – 23.61, separate plate), **front shell** (Z 23.61 – 33.86) |
| Dock USB-C (the Feather's own) | **centred across the width, 6.62 behind the front face, mouth 1.00 inside the bottom end face** — identical to the single-board radio (fit report: "dock interface: MATCH") |
| Visible LEDs | CHG (charging) at X 6.0, red at X −6.0 (both Y 2.0), NeoPixel at X 5.4 Y 18.0; RESET pin-hole at X 5.0 Y 12.0 |

**Back shell (Z 0 – 23.6):** the **18650 holder** lies on the floor, centred (X ±10.45, Y 2.5 – 80.2, in a 0.5 mm
floor pocket), **+ toward the USB end**. Its PC pins are trimmed and wired; the joints sit in Ø3.5 floor relief holes.
Ledges on all four walls carry the deck.

**Deck (Z 22.61 – 23.61):** rests on the ledges 0.4 mm over the holder; front-shell posts clamp it. It carries:
* the **Feather** at the bottom end (Y 0.2 – 51.0), components up, on four 0.4 mm standoffs with pegs through its
  holes; its USB-C reaches the bottom end wall (mouth 1.0 inside the face, centre Z 27.24). A back-shell tab fills the
  wall under the receptacle.
* the **thumbwheel cradle** on the right wall between the Feather and the FM module (dial centre Y 58.7), dial
  **0.95 mm proud** of the right face.
* the **FM module** at the top end, centred (X ±13.625, Y 66.46 – 93.71), on four 0.4 mm standoffs at its holes, jack
  toward the top end wall (**6.8 mm plug hole** on the jack axis, Z 28.78). Its 4-pin header points **down** through a
  window in the deck (pins assumed 8.5 mm long below the board). Four front-shell posts (Ø6) clamp its corners;
  optionally M3 × 8 screws with nuts.
* wire slots: left Y 12 – 22 and 39 – 47, right Y 7 – 17; the wires run in the side channels under the deck.

**Front shell (Z 23.61 – 33.86):** light tunnels from the Feather's CHG, red and NeoPixel LEDs to holes in the front
face, a pin tube over RESET, Feather hold-down posts, FM clamp posts, the **SS-12F16 switch** in a groove inside the
**left** wall at Y 56 (above the Feather's edge, G4 knob 2.8 mm proud, ON toward the top end; engraved labels), and
the snap lip (bumps at Y 16 and 84 on both sides).

**Docked:** the radio stands on its bottom end in a dock pocket, front face toward you. The pocket walls are 50.8 mm
high with a front window above a 2.5 mm lip, so the CHG LED (≈ 4 mm above the pocket floor) and the NeoPixel
(≈ 20 mm) are visible; the switch (≈ 58 mm) and the wheel (from ≈ 53 mm) are above the pocket walls. Plug insertion
6.0 mm past the receptacle mouth (same as the single-board radio).

## Print and assemble
1. Print `case/case_bottom.stl` (back face down), `case/case_top.stl` (front face down) and `case/deck.stl` (flat,
   top face down). PLA or PETG, 0.2 mm layers; the FM plug hole and the USB-C opening bridge ≤ 9 mm.
2. Back shell: trim the holder's PC pins, solder the battery leads (+ red, − black) and glue/tape the holder into its
   floor pocket (+ end toward the USB end). Run the leads up the side channels.
3. Wire the Feather per `docs/pin_map.md` (wheel, switch, divider, FM header, battery to the BAT / GND pads). Leave
   the JST and STEMMA QT sockets empty.
4. Deck: glue the wheel into the cradle, put the FM module on its standoffs (header pins down through the window,
   wires soldered underneath), set the Feather on its pegs (USB-C to the bottom end), lay the deck onto its ledges.
5. Front shell: press the switch plate into the left-wall groove from inside, then lower the front shell straight
   onto the back shell until the four snaps click. The posts clamp the deck, the Feather and the FM module.

## Measure and edit (all in `scripts/layout.py`, then `case/build_case.sh`)
* FM module: `FM_S`, `FM_HOLE_PITCH`, `FM_JACK_D/L/OUT`, header `FM_HDR` (pin side and length), standoff height.
* Feather: run `python3 scripts/feather_data.py --usb-overhang <mm>` for older boards (the dock USB-C position
  follows the Feather's receptacle; the fit check asserts it still matches the dock).
* LED tunnels: `LED_TUN`, `RESET_TUBE`.

## Checks (`case/build_case.sh` → `case/case_fit_report.txt`)
* All three printed parts watertight, one body each; **0 interferences** between them and the ghost parts (holder,
  Feather + parts, FM module + jack + header, wheel, switch in both positions); assembly path (front shell lowered
  straight down past the Feather's USB-C, the wheel and the FM module) clear.
* **LED / RESET line of sight:** straight rays from the CHG, red, NeoPixel and RESET positions out through the front
  face: all clear.
* Dock interface: 31.90 W × 33.86 T, USB-C centred, 6.62 / 1.00 → **MATCH**. Dock insertion and LED visibility in
  the dock are checked with the real STLs in `../charging_dock/case/dock_fit_report.txt`.

## Known risks and limits
* Nothing has been printed or built. Fit is CAD-only, from datasheet dimensions and Victor's FM-module description.
* **Longer than the single-board radio** (98.71 vs 89.75 mm): the wheel sits between the Feather and the FM module
  because the FM module's component heights are unknown. Same width, thickness and dock pocket.
* The light tunnels assume the Feather's LED positions from Adafruit's Eagle file; LED brightness through 1.6 mm
  tunnels is untested.
* FM module header: assumed straight pins pointing down; if yours is a right-angle header with pins lying along the
  board, bend or replace it so the pins go down through the deck window.
* Charging is slow: 200 mA (the Feather's charger), about 18 h for 3500 mAh. Off-state drain about 0.4 mA through the
  Feather's EN pull-up.
* Battery wires on the BAT / GND pads instead of the JST plug: get the polarity right, there is no keyed connector.
* The wheel has no RC debounce or ESD diode; the firmware debounces it.
* Battery change: open the snaps, lift the deck (with the Feather, the wheel and the FM module, all wired) out
  together. Not tool-free.

Licence: case and scripts are released into the public domain under CC0 1.0, like the rest of OpenALD (see `../LICENSE`). The Adafruit Feather RP2040 Eagle file in `ref/` (and the mechanical data parsed from it) is CC BY-SA (Adafruit).
