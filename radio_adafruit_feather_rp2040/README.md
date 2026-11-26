# OpenALD Feather RP2040 v1.0

This is a variant of the OpenALD pocket FM radio built around an **Adafruit Feather RP2040**. It has:
* an FM module (Victor's module: **27.25 × 27.25 mm, 1.6 mm board, Ø3.8 mm holes in the corners on a 20 mm square,
  a 4-pin 90° through-board header and a standard 6.35 × 14 mm headphone jack, both centred on the bottom edge, the
  jack 1 mm past the board**),
* an 18650 cell in an MPD BH-18650-PC holder (the same holder as the single-board radio),
* a **Mitsumi SIQ-02FVS3 thumbwheel** (volume/tune + push) glued into a printed cradle on the deck,
* an **SS-12F16 slide switch** (SPDT, "G4" 4 mm knob by default) dropped onto two heat-stake studs in the case wall
  (t122u; melt the stud tips with a soldering iron), no screws,
* hand-soldered wires to the Feather's header pads. **There is no custom PCB** in this variant.

**t116u (2026-11-24, still v1.0): bottom-end USB-C, dock-compatible with the single-board radio.** The Feather lies
flat at the bottom end and **its own USB-C is the charge / dock / programming port**, in the bottom end face,
**centred across the width, 6.62 mm behind the front face, mouth 1.0 mm inside the face** — the same spot as the
single-board radio, so both stand in the same charging-dock pocket (35.9 × 33.86 end footprint since t122u, see
`../charging_dock/DOCK_INTERFACE.md`). The USB-C breakout, the Schottky diode and the optional 3 mm charge LEDs are
gone; the Feather's own **CHG LED, red LED and NeoPixel shine through holes in the front face**. The MI03 radio keeps
its side USB-C and does not dock.

> **Status: design only. Nothing here has been printed, built or tested.**
> - FM module: outline, holes, jack and header from Victor's description; the header pin length/side, the jack
>   barrel diameter at the end wall and the module pin order are **assumed** (see "Measure and edit").
> - Feather part heights are datasheet estimates; board outline, holes, LEDs, buttons, pads and connectors come from
>   Adafruit's own Eagle file. Wheel and switch geometry come from their datasheets, not from measured parts.

**t122u (2026-11-24, still v1.0): Victor's fit fixes.**
* **Wider:** 35.9 mm outside (was 31.9), 4.5 mm from each Feather edge to the inner wall, so there is room for the
  battery plug on the JST side, with the same gap on the other side. The Feather stays centred. The dock pockets are now
  35.9 wide too. The single-board case keeps its 31.9 body and gets a 35.9-wide dock collar on its bottom 27 mm.
* **Feather centring pins:** the deck pegs are Ø2.2 (in the 2.5 mm holes) and stick **1.0 mm out of the Feather's top
  face**. The front-shell hold-down posts (Ø4.0) have a 2.7 × 1.3 socket for the peg tips.
* **Switch: heat-stake studs.** The switch plate drops from inside into a 0.8 mm pocket in the left wall. Two **Ø1.4
  studs** (15 mm apart, 1.5 mm longer than the plate is thick) go through the plate's two M2 holes. Melt the stud tips
  into heads (≤ 1.0 mm tall, ≤ 3.4 mm across). The plate goes in sideways from the cavity, so nothing has to slide past
  a wall lip. **Backing ribs** on the deck stop 0.4 mm behind the plate at both ends, so the switch can't be pushed
  into the case. The knob slot, the knob (2.8 mm proud) and the ON/OFF labels are unchanged.
* **FM module flipped**, with the flat side (where the header and jack pins come through) toward the front face. It
  sits **1.5 mm further toward the top end** (Y 67.96 – 95.21). The front-shell standoffs are 1.5 mm, Ø5.5, with
  **Ø3.4 pegs** that go 0.6 mm into the Ø3.8 holes. The deck has Ø6 support posts under the module's corners with the
  same pegs from below. The jack now hangs below the board and dips through a notch in the deck. **Cut the 4-pin header
  pins and the jack's solder tails to ≤ 1.2 mm on the flat side.** The wires are soldered there before you close the
  case. Seen from the flat side the header pin order is mirrored, so wire by the pin labels, not by position (the connections in the wiring diagram are unchanged).
* **Headphone hole Ø6.95** (the 6.35 barrel + 0.3 mm per side; was 6.8 with a Ø8.6 outer chamfer, now a 0.3 mm edge
  break). The jack axis is 25.99 above the back face. The hole straddles the shell split: a U-notch in the front shell
  plus a tab on the back shell.
* Close-ups: `previews/closeup_switch_inside.png`, `closeup_fm_module_pegs.png`, `closeup_feather_pins.png`,
  `section_jack_x0.png`.

![exploded](previews/case_exploded.png)

## Part colours (t124u)
Victor: "make all 3 cases and their parts different colors so it is easy to tell the parts apart". Each case family has
its own hue (single board **blues**, Feather **greens**, MI03 **oranges / reds**, dock **purples**); this one uses
**greens**. The same colours are used in every preview and in the coloured 3MF plate **`case/openald_feather_case_colored.3mf`** (all printed parts laid
out on one plate, each a separate named object with its colour; source `../tools/palette.py`, rebuilt by
`../tools/make_3mf.py`). Colours are only for telling the parts apart; print in any filament.

| Part (STL) | What | Colour | Hex |
|---|---|---|---|
| `case/case_top.stl` | front shell | green | `#2FA84F` |
| `case/case_bottom.stl` | back shell | light green | `#A8E0A0` |
| `case/deck.stl` | deck (inner plate) | dark green | `#0F5A2A` |

## Folder contents
| Path | What |
|---|---|
| `case/` | OpenSCAD source (`openald_feather_case.scad`), generated `case_params.scad` / `feather_params.scad`, print-ready **`case_top.stl`** (front shell), **`case_bottom.stl`** (back shell), **`deck.stl`** (inner plate), `case_fit_report.txt`, `build_case.sh` |
| `previews/` | `case_exploded.png`, `case_closed.png`, `case_closed_back.png`, `case_print_layout.png`, `front_face.png`, close-ups (`closeup_dock_usb_c.png`, `closeup_feather_leds.png`, `closeup_jack_end_fm.png`, `closeup_wheel.png`, `closeup_switch.png`, t122u `closeup_switch_inside.png`, `closeup_fm_module_pegs.png`, `closeup_feather_pins.png`) and sections (`section_jack_x0.png`, (`section_feather_y2.png`, `section_wheel_y58.png`, `section_fm_y80.png`) |
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
| Outside | **35.90 W × 98.71 L × 33.86 T**, edges r 2 (t122u; was 31.90 wide, and 32.9 × 89.75 × 34.83 with the side USB-C) |
| Walls / floor / front | 2.0 / 1.4 / 1.6 |
| Parts | **back shell** (Z 0 – 23.61 + lip), **deck** (Z 22.61 – 23.61, separate plate), **front shell** (Z 23.61 – 33.86) |
| Dock USB-C (the Feather's own) | **centred across the width, 6.62 behind the front face, mouth 1.00 inside the bottom end face** — identical to the single-board radio (fit report: "dock interface: MATCH") |
| Visible LEDs | CHG (charging) at X 6.0, red at X −6.0 (both Y 2.0), NeoPixel at X 5.4 Y 18.0; RESET pin-hole at X 5.0 Y 12.0 |

**Back shell (Z 0 – 23.6):** the **18650 holder** lies on the floor, centred (X ±10.45, Y 2.5 – 80.2, in a 0.5 mm
floor pocket), **+ toward the USB end**. Its PC pins are trimmed and wired; the joints sit in Ø3.5 floor relief holes.
Ledges on all four walls carry the deck.

**Deck (Z 22.61 – 23.61):** rests on the ledges 0.4 mm over the holder; front-shell posts clamp it. It carries:
* the **Feather** at the bottom end (Y 0.2 – 51.0), components up, on four 0.4 mm standoffs with Ø2.2 pegs through its
  holes (1.0 mm proud of its top face); its USB-C reaches the bottom end wall (mouth 1.0 inside the face, centre Z 27.24). A back-shell tab fills the
  wall under the receptacle.
* the **thumbwheel cradle** on the right wall between the Feather and the FM module (dial centre Y 58.7), dial
  **0.95 mm proud** of the right face.
* the **FM module** (t122u: flipped, flat side to the front) at the top end, centred (X ±13.625, Y 67.96 – 95.21,
  board Z 29.16 – 30.76), on four Ø6 deck posts with Ø3.4 pegs. The jack hangs below the board toward the top end wall
  (**Ø6.95 plug hole**, axis Z 25.99) through a deck notch. Four front-shell standoffs (Ø5.5 × 1.5 with Ø3.4 pegs)
  hold the flat side. The header and jack pins on the flat side must be cut to ≤ 1.2 mm.
* wire slots: left Y 12 – 22 and 39 – 47, right Y 7 – 17; the wires run in the side channels under the deck.

**Front shell (Z 23.61 – 33.86):** light tunnels from the Feather's CHG, red and NeoPixel LEDs to holes in the front
face, a pin tube over RESET, Feather hold-down posts (with sockets for the peg tips), FM standoffs, the **SS-12F16
switch** heat-staked on two studs in a pocket inside the **left** wall at Y 56 (G4 knob 2.8 mm proud, ON toward the
top end; engraved labels; deck ribs behind the plate ends), and
the snap lip (bumps at Y 16 and 84 on both sides).

**Docked:** the radio stands on its bottom end in a 25 mm deep pocket in the flat dock top (35.9 × 33.86 + 0.35 per
side), front face toward you. A 20 mm window in the pocket's front wall shows the CHG LED (≈ 4 mm above the pocket
floor) and the NeoPixel (≈ 20 mm); the switch (≈ 58 mm) and the wheel (from ≈ 53 mm) are above the pocket. Plug insertion
6.0 mm past the receptacle mouth (same as the single-board radio).

## Print and assemble
1. Print `case/case_bottom.stl` (back face down), `case/case_top.stl` (front face down) and `case/deck.stl` (as
   exported: flat underside down, posts and pegs up). PLA or PETG, 0.2 mm layers, ≥ 3 perimeters (thin studs and
   pegs); the USB-C opening bridges ≤ 9 mm.
2. Back shell: trim the holder's PC pins, solder the battery leads (+ red, − black) and glue/tape the holder into its
   floor pocket (+ end toward the USB end). Run the leads up the side channels.
3. Wire the Feather per `docs/pin_map.md` (wheel, switch, divider, FM header, battery to the BAT / GND pads, or a
   battery lead into the JST socket; since t122u there is 4.5 mm beside the Feather for the plug). Leave the STEMMA QT
   socket empty.
4. FM module: cut the header pins and jack tails to ≤ 1.2 mm on the flat side, solder the 4 wires there, and set the
   module **flat side up** on the deck posts (jack toward the top end, down through the deck notch).
5. Deck: glue the wheel into the cradle, set the Feather on its pegs (USB-C to the bottom end), lay the deck onto its
   ledges.
6. Switch: solder its wires, then from inside the front shell slide the plate sideways into the wall pocket onto the
   two studs (knob out through the slot). Melt each stud tip into a head with a soldering iron (≤ 1.0 mm tall).
7. Lower the front shell straight onto the back shell until the four snaps click. The posts clamp the deck, the
   Feather and the FM module; the deck ribs sit behind the switch plate.

## Measure and edit (all in `scripts/layout.py`, then `case/build_case.sh`)
* FM module: `FM_S`, `FM_HOLE_PITCH`, `FM_JACK_D/L/OUT`, `FM_JACK_HOLE_D` (= barrel + 0.6), header stubs `FM_HDR`,
  `FM_GAP_FRONT` (front standoff height), `FM_PEG_D`, `FM_SHIFT`.
* Switch: `SW_HOLE_P` (hole pitch), `SW_STUD_D`, `SW_STUD_OUT`, `SW_BACK_RIB`. Feather pegs: `F_PEG_D`, `F_PEG_OUT`.
* Feather: run `python3 scripts/feather_data.py --usb-overhang <mm>` for older boards (the dock USB-C position
  follows the Feather's receptacle; the fit check asserts it still matches the dock).
* LED tunnels: `LED_TUN`, `RESET_TUBE`.

## Checks (`case/build_case.sh` → `case/case_fit_report.txt`)
* All three printed parts watertight, one body each; **0 interferences** between them and the ghost parts (holder,
  Feather + parts, FM module + jack + header, wheel, switch in both positions); assembly path (front shell lowered
  straight down past the Feather's USB-C, the wheel and the FM module) clear. t122u: switch plate slid sideways onto
  the studs clear of the front shell; the staked switch (with 1.0 mm heads) clear of the deck ribs as the shells close.
* **LED / RESET line of sight:** straight rays from the CHG, red, NeoPixel and RESET positions out through the front
  face: all clear.
* Dock interface: 35.90 W × 33.86 T, USB-C centred, 6.62 / 1.00 → **MATCH**. Dock insertion and LED visibility in
  the dock are checked with the real STLs in `../charging_dock/case/dock_fit_report.txt`.

## Known risks and limits
* Nothing has been printed or built. Fit is CAD-only, from datasheet dimensions and Victor's FM-module description.
* **Longer than the single-board radio** (98.71 vs 89.75 mm): the wheel sits between the Feather and the FM module
  because the FM module's component heights are unknown. Same thickness and dock pocket; 4 mm wider body (the
  single-board case has a dock collar to match).
* The light tunnels assume the Feather's LED positions from Adafruit's Eagle file; LED brightness through 1.6 mm
  tunnels is untested.
* FM module (t122u, all **assumed**, please measure): jack barrel Ø6.35 and 1.0 mm past the board edge; components on
  the jack side ≤ 5.5 mm tall; nothing within the Ø6 deck posts / Ø5.5 front standoffs around the holes; header and
  jack pins cut to ≤ 1.2 mm on the flat side. Hole sizes are CAD sizes; check them on a printed part (holes print small).
* Switch (assumed from the SS-12F16 drawing): M2 plate holes 15 mm apart. The Ø1.4 studs are thin; print the front
  shell with ≥ 3 perimeters and melt them gently.
* JST battery plug: 4.5 mm between the Feather edge and the wall on that side; check that your plug and its wires fit.
* Charging is slow: 200 mA (the Feather's charger), about 18 h for 3500 mAh. Off-state drain about 0.4 mA through the
  Feather's EN pull-up.
* Battery wires on the BAT / GND pads instead of the JST plug: get the polarity right, there is no keyed connector.
* The wheel has no RC debounce or ESD diode; the firmware debounces it.
* Battery change: open the snaps, lift the deck (with the Feather, the wheel and the FM module, all wired) out
  together. Not tool-free.

Licence: case and scripts are released into the public domain under CC0 1.0, like the rest of OpenALD (see `../LICENSE`). The Adafruit Feather RP2040 Eagle file in `ref/` (and the mechanical data parsed from it) is CC BY-SA (Adafruit).
