# OpenALD Feather RP2040 v1.0

This is a variant of the OpenALD pocket FM radio built around an **Adafruit Feather RP2040**. It has:
* an RDA5807M FM module with its own 3.5 mm jack,
* an 18650 cell in an MPD BH-18650-PC holder (the same holder as the single-board radio),
* a small custom **controls board** with the thumbwheel (volume/tune + push), the power switch, a battery divider and two charge-mirror LEDs,
* a thin 3D-printed **internal frame** that locates everything.

The bottom 2 in of the case is a copy of the single-board radio's case, so it fits the same **OpenALD charging dock**.

> **Status: design only. Nothing here has been built or tested on hardware.**
> - The FM-module mounting-hole and jack positions are **estimates**. The module photo could not be measured. See "Measure and edit" below.
> - Feather part heights are datasheet estimates. Board outline, holes, LEDs, buttons, pads and connectors come from Adafruit's own Eagle file.

![exploded](previews/case_exploded.png)

## Folder contents
| Path | What |
|---|---|
| `kicad/` | Controls board: schematic, PCB (routed, GND pours), project libraries (`openald_fctl`) |
| `fab/` | Gerber + drill zip, JLC BOM/CPL (with JLC_CORR rotation/offset corrections), centroid, .pos, human BOM with live LCSC prices, ERC/DRC reports |
| `case/` | OpenSCAD source (`openald_feather_case.scad`) and generated parameters. `stl/` holds `case_top.stl`, `case_bottom.stl` and `frame.stl` in print orientation, plus fit and dock reports |
| `previews/` | Renders: exploded, closed, back, print layout, close-ups, sections |
| `docs/` | `wiring_diagram.svg/.png`, `pin_map.md`, `firmware_notes.md`, `BOM.md/.csv` |
| `scripts/` | Generators. `layout.py` is the single source of truth for the mechanical layout |
| `ref/` | Adafruit Feather RP2040 Eagle board (CC BY-SA, from github.com/adafruit/Adafruit-Feather-RP2040-PCB) and the parsed mechanical data |
| `make_all.sh` | Rebuilds everything: footprints → schematic → ERC → PCB → route → DRC → fab → wiring → case STLs → checks → renders |

## Size and the dock interface
| | Width × thickness | Y range (from the bottom face) |
|---|---|---|
| **Dock section** (identical to the single-board case) | **43.00 × 33.41 mm**, R5.5 plan corners, R2 edges | 0 – 52.8 mm |
| Taper (+1.25 mm per side) | 43.0 → 45.5 | 52.8 – 56.8 mm |
| **Upper body** | **45.50 × 33.41 mm**, R3 plan corners at the top end | 56.8 – 92.0 mm |
| **Overall** | 45.5 × 33.41 × **92.0 mm**, the same length as the single board | |

`case/dock_check_report.txt` compares section by section with the single-board case STLs over the bottom 52 mm. `DOCK_INTERFACE.md` asks for 50.8 mm pocket plus 1.2 mm margin. The worst outer-envelope difference is **0.18 mm²** per section, which is tessellation noise. The USB-C end wall, including the plug pocket and opening, matches to within 0.03 mm². The widening starts 0.8 mm above the 52 mm limit, 2 mm above the pocket rim.

**USB-C alignment** works by placing the Feather directly; there is no adapter or extension.
* The Feather is centred at X = 19.0 with its bottom face on the Z = 0 plane, the same plane as the single-board PCB bottom. It sits on the printed deck, which rests on posts above the battery holder.
* Its USB-C receptacle (CUI CUSB31, 3.26 mm tall) therefore lands with its centre at Z = 3.23 and X = 19.0, the same as the single board. In dock terms that is 6.57 mm behind the front face and 26.84 mm in front of the back face, centred across the width.
* The current Feather revision has the receptacle 1.21 mm past its board edge. Putting the board edge 1.21 mm from the inner wall puts the receptacle mouth **2.50 mm inside the bottom face**, the same as the single board.
* Four frame pegs locate the Feather in its mounting holes, and four top-half posts clamp it. **Older Feathers (rev B and before) have 2.48 mm overhang**: run `python3 scripts/feather_data.py --usb-overhang 2.48`, then `case/build_case.sh`.

## LEDs: what you can see
| LED | Where | Visible when |
|---|---|---|
| Feather **CHG** (amber, MCP73831 STAT) | Ø1.6 window in the top, near the USB end, with its own light tunnel | undocked (USB cable) |
| Feather **red D13** | window near the USB end | undocked |
| Feather **NeoPixel** | window about 21 mm above the bottom face | undocked |
| Controls-board **red "CHG"** mirror | window at the upper right, 75 mm from the bottom | **always, including while docked** |
| Controls-board **green "FULL"** | window just above it | **always, including while docked** |

The Feather's own LEDs sit inside the dock pocket, so the two mirror LEDs repeat the charger state above the dock line. They are driven in hardware from VBUS and the charger's STAT pin through a fine wire to the STAT end of the Feather's R2. That means they work with the power switch OFF. If you'd rather not solder that wire, leave D1/D2 and the STAT wire out; the Feather windows still work when undocked. A RESET pin-hole (paper clip) sits above the Feather's RESET button.

## Inside the case (front face up, USB-C end down)
* **Bottom half, back:** the 18650 holder lies flat on the floor with the cell opening up and + at the USB end. Its PC pins are bent flat into floor grooves and soldered to wires just past each end of the holder. Corner fences locate the holder; double-sided tape holds it. Eight posts beside the holder carry the deck.
* **Frame:** a 1 mm deck over the holder, with:
  * pegs for the Feather and controls-board holes,
  * a 0.6 mm ledge and corner stops for the FM module,
  * slots for the wires (battery leads up beside the JST, Feather header wires down to the right-side channel, and back up under the controls-board pads),
  * reliefs for the USB shell legs and the switch and wheel pins.
* **On the deck:**
  * the Feather at the USB end (Y 1.2 – 52.0),
  * the FM module at the top left with its jack out through the top end wall,
  * the controls board on the right, with the wheel and switch knob through the right wall, both above the dock line.
* **Wires:** battery to the Feather JST in the left channel. Feather to controls board in the right channel. Feather STEMMA QT to the FM module over the deck.
* Four M2 × 12 screws go in from the back into heat-set inserts in the top half: two at the USB end and two at the taper. A perimeter lip seals the joint. **There are no screws at the top end**, because there is no room; the lip and the FM/controls hold-downs keep it closed.

## Assembly (outline)
1. Order the controls board from `fab/`: gerbers zip, `*-BOM-jlcpcb.csv` and `*-CPL-jlcpcb.csv`. Hand-solder SW1 (SK-12E12, LCSC C136720).
2. Print `case/stl/case_bottom.stl` (floor down), `case_top.stl` (face down) and `frame.stl` (deck down). Use PLA or PETG with 0.2 mm layers. Supports are needed only for the USB/jack/switch openings if your printer can't bridge them. Fit 4 M2 heat-set inserts into the top half.
3. Battery: bend the holder pins flat toward the holder ends and solder the cut JST PH lead (#261): red to + at the USB end, black to −. Check the polarity against the Feather's "+" mark. Tape the holder into the fences. Run the leads up the left channel.
4. Solder 9 wires to the Feather per `docs/pin_map.md`, and the STAT fine wire if used. Solder the cut STEMMA QT cable to the FM module: red 3V3, black GND, blue SDA, yellow SCL.
5. Lay the frame on the posts. Press the Feather onto its pegs, feed the controls wires down the right slot and up into J1 from below, and solder. Fit the controls board and the FM module.
6. Fit the cell, close the case and fit the screws.

## Measure and edit (do this before printing)
All are in `scripts/layout.py`. Then run `case/build_case.sh`.
| Parameter | Current value | Measure on your FM module |
|---|---|---|
| `FM["w"], FM["h"]` | 26.9 × 26.9 | board outline |
| `FM["t"]`, `FM["z0"]` | 1.6, 0.6 (ledge height) | thickness, and the bottom-side pin protrusion: must be ≤ 1.7 mm |
| `FM_HOLE_INSET`, `FM_HOLE_D` | 2.5, 2.2 (**estimate**) | corner-hole centre to the board edges, hole Ø. These only position the top hold-down posts; set `fm_posts=false` in the .scad to drop them. |
| `FM_JACK_X` | board-edge centre (**estimate**) | jack axis X; the case X = FM left edge (−1.25) + offset |
| `FM_JACK_AXIS_H`, `FM_JACK_BODY_H` | 2.5, 5.0 | jack axis height above the board top, body height |
| component height on the FM top | assumed ≤ 5.5 mm (ceiling at Z 8.2) | tallest part |
| holder height | 21.31 (datasheet) | with the cell fitted, must stay below the deck (0.1 mm margin) |

## Checks (as generated)
* ERC on the controls board: **0 errors, 0 warnings** (`fab/erc_report.txt`).
* DRC: **0 violations, 0 unconnected, 0 schematic-parity issues** (`fab/drc_report.txt`).
* JLC CPL: corrections refit from the EasyEDA footprints: `scripts/jlc_cpl_fit.py --check` → OK.
* 3D fit (`case/case_fit_report.txt`): no overlap between any part and the top, bottom or frame, and none between the three printed parts. Parts checked: Feather board and every component envelope from the Eagle file, holder, FM board and jack, controls board, wheel and switch models, 0603 parts.
* Dock interface (`case/dock_check_report.txt`): see above.

## Known risks and limits
* FM-module geometry is estimated: hole positions, jack position, bottom-side pin length, I2C pull-ups.
* The 0.1 mm gap between the holder top and the deck relies on the datasheet height of 21.31 mm.
* The STAT tap is a fine-wire solder joint on a Feather 0603 resistor pad.
* Off-state drain is about 0.4 mA through the Feather's EN pull-up. Charging is slow: 200 mA, about 18 h for 3500 mAh.
* The wheel has no RC debounce or ESD diode. Debounce in firmware (quadrature state table, one step per detent); see `docs/firmware_notes.md` for the decode notes and an Arduino-Pico example. The SIQ-02FVS3 locating bosses are assumed not to protrude more than 1.1 mm below the 1.6 mm controls board.
* The battery is changed by lifting the frame stack. Not tool-free.
* The top end is held only by the lip, with no screws.

Licence: case, board and scripts are released into the public domain under CC0 1.0, like the rest of OpenALD (see `../LICENSE`). The Adafruit Feather RP2040 Eagle file in `ref/` (and the mechanical data parsed from it) is CC BY-SA (Adafruit).
