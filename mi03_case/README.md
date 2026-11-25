# MI03 FM Pocket Radio + 18650 case (adapted from the OpenALD single-board case)

For the stock MI03 board (silk "MLA-M3(2291) V4.1 20240627"), with its 300 mAh LiPo swapped for an 18650 in an
MPD BH-18650-PC holder (the same holder OpenALD uses). **CAD only: nothing has been printed, assembled or tested.**
This folder is separate from the OpenALD v1.0 design: none of the OpenALD files were changed.

**t116u (2026-11-24): the OpenALD single-board and Feather radios moved their USB-C to the bottom end** (31.9 × 33.86 end footprint, centred USB-C) and no longer share this case's envelope; the MI03 keeps its side USB-C and is **not dock-compatible**. Earlier on 2026-11-24 this case was the reference envelope for the OpenALD single-board and Feather radios (same
89.75 × 34.83 length and thickness, widths 30.5 single board / 32.9 Feather vs 27.5 here, same USB-C position: 30.3 mm from the top outer end, 7.55 mm behind the front face,
mouth 1.0 mm inside the left face, 13.0 × 7.6 r 3 recess). The MI03 files themselves were not changed. **The MI03 is not dock-compatible** (Victor, 2026-11-24: "The mi03 version doesn't need to work with the dock."): the
charging dock is designed and checked only for the OpenALD single-board and Feather radios. Charge the MI03 with a
USB-C cable.

## Files
* `mi03_case.scad`: the parametric source. Every measurement Victor gave is a named parameter at the top, and
  every guess is marked `ASSUMED`. `frame_mount = "front" | "back"` picks the battery-frame mounting option.
* `stl/mi03_front_shell.stl`: front face with the LCD window, plungers/pin holes, **and (since 2026-11-22) the
  USB-C opening, the power-switch slot and the headphone-jack opening**. The board screws straight into it.
* `stl/mi03_back_shell.stl`: snap-on back cover with the battery-frame ledges and the two option-"back" screw columns.
* `stl/mi03_battery_frame_front_mount.stl` / `stl/mi03_battery_frame_back_mount.stl`: the flat plate between the
  PCB and the 18650 (holder glued to its underside). Print **one**, for the option you want; they differ only in
  where the two countersunk holes are and which face they are countersunk on.
* `stl/mi03_button_plunger.stl`: print 2.
* `stl/mi03_switch_carrier.stl` + `stl/mi03_switch_knob.stl`: the switch cap, now two pieces (print 1 of each).
* `scripts/build.sh` rebuilds the STLs, runs the fit check and renders the previews. `scripts/check_fit.py` runs the
  watertight and single-body checks, the interference checks for both frame options, the drop-in sweeps and the
  glue-area measurement. `scripts/sections.py` draws the cross-sections.
* `fit_report.txt` is the latest check output. `previews/*.png` are the pictures.

## What changed on 2026-11-22 (front shell + board = one unit)
* **Split moved down.** The front/back split is now at **z = −8.15**, 1 mm below the battery frame (it was at the
  PCB back face, z = 0). The front shell is 14.23 mm deep, the back shell 20.6 mm. USB-C, switch and jack are
  therefore entirely inside the front shell's walls.
* **Board screws into the front shell.** All three used holes (top centre and both bottom corners) now take an
  M2 × 4 self-tapping screw from the back of the board into a front-shell boss (1.7 mm pilots). The old front-face
  countersinks, the heat-set inserts and the M2 × 10 screws are gone. Front shell + board is one rigid unit.
* **Straight drop-in.** The board goes into the front shell straight along its axis:
  * the USB-C receptacle sticks 1 mm into the wall, so the wall has a 9.4 mm wide drop-in channel from the split up
    to it (1.1 mm of wall left outside; the plug recess stops 0.55 mm outside the receptacle to keep a 0.4 mm skin);
  * the switch head goes down a 4.1 mm wide channel into the cap carrier;
  * the jack barrel now ends **inside** the case (1.2 mm from the inner end wall) instead of poking through it.
    The end wall has a 6.8 mm plug hole with a 7.8 mm × 1.0 mm counterbore and 45° chamfer outside, so a plug
    reaches 2.2 mm in to the barrel face.
* **Case is 3.15 mm longer**: 89.75 mm (was 86.6). 2.25 mm is the jack barrel moving inside; the other 0.9 mm
  (barrel-to-wall gap 1.2 mm instead of the old 0.3) makes room for the option-"front" frame screws between the
  board's bottom end and the plate edge. Width (27.5 mm) and thickness (34.83 mm) are unchanged.
* **Back shell is a snap-on cover.** A 1.8 mm tall, 0.9 mm lip goes into a rebate in the front shell, with 4 snap
  bumps (0.3 mm, 8 mm long, 45° flanks) on the long sides at 18 and 62 mm from the top, and a pry notch at the top
  end. There is no lip along the straight part of the jack end so that wall stays a full 2 mm under the plug hole.
  The old snap tabs and the switch keeper zone are gone.
* **PCB edge supports** (between S1/S3, 33–62 mm from the top) are now tapered ribs on the battery frame, reaching
  0.05 mm under the board edge, instead of ledges in the back shell.
* **Switch cap is two pieces** (see below), because the wall slot is now closed all round.

## Size and Z stack
Z = 0 at the PCB back face.

| Z (mm) | What |
|---|---|
| +6.08 | Front face (front wall 1.6 mm, as in OpenALD) |
| +4.48 | Inside of the front face (0.3 mm above the LCD glass) |
| +4.18 | LCD glass top: board top + 1.4 mm backlight + 1.78 mm glass, **assumed stacked** |
| +2.50 | Button cap tops (1 mm body + 0.5 mm cap) |
| 0 to +1.0 | PCB |
| −2.0 | Bottom of the option-"front" frame bosses (clear of back-side parts ≤ 1.8 mm) |
| −5.25 | Bottom of the jack, the deepest part on the back (switch −3.8, USB-C −3.1) |
| −5.55 | Top of the battery frame (0.3 mm air gap under the jack) |
| −7.15 | Underside of the frame = glue face = holder base (holder mounted **base up**) |
| **−8.15** | **Front/back split** (back-shell lip up to −6.35) |
| −26.75 | Lowest point of the cell (holder plus cell assumed 19.6 mm) |
| −27.15 | Top of the floor (0.4 mm clearance) |
| −28.75 | Back face (1.6 mm floor, as in OpenALD) |

**Outside size: 27.5 mm wide × 89.75 mm long × 34.83 mm thick.** The switch knob sticks out another 2.45 mm on one
side.

## Battery-frame mounting options
Both options use the same front shell, back shell, holder gluing and wiring; only the frame STL differs.

| | `frame_mount = "front"` (default) | `frame_mount = "back"` |
|---|---|---|
| Screws | 2 × **M2 × 5** 90° countersunk self-tapping | 2 × **M2 × 8** 90° countersunk self-tapping |
| Where | X = ±5.3, 2.05 mm past the board's bottom end (Y = −2.05), beside the jack | X = ±9.0, Y = +0.3 (jack-end corners) |
| Direction | from **under** the plate, up into front-shell bosses (r 1.9, 1.6 mm pilots, z −5.55..−2.0, merged into the end wall with a 45° top) | from **above** the plate, down into back-shell columns (r 1.9, floor to z −7.25, merged into the end wall, 1.6 mm pilots 7 mm deep) |
| Result | frame + holder + cell join the front + board unit; the back shell is just a cover | frame + holder + cell live in the back shell; front + board unit snaps on over them |
| Cell swap | unclip the back shell: the cell is right there (the holder opens toward the floor) | unclip, lift off the front unit, undo the 2 screws, lift the frame + holder out, swap, reverse |

In both options the plate also rests on the back-shell ledges (0.1 mm below it: both long sides and across the jack
end), and the front shell's top-end post (0.05 mm above the plate) and the two front bosses bear on it when the case
is closed, so neither end can rattle. The front bosses sit outside the board footprint, so they do not block the
board dropping in.

## How it goes together
1. **Battery frame and holder.** Trim the holder's two PC pins to **1.4 mm or less** and solder 26–28 AWG silicone
   wires to them. Glue the holder **base up** to the flat underside of the battery frame, with its − (spring) end
   toward the jack end.
   * The pins sit in the frame's 3.0 × 3.6 mm slots, and the holder's two 3.2 mm holes line up with matching holes
     in the frame. A 3 mm drill bit or pin through each pair keeps the holder aligned while the glue sets.
   * Optionally, add 2-56 or M2.5 screws through those holes with nuts on the frame top.
   * The jack-end wire runs in a 1.4 × 0.9 mm groove on the frame top, sideways out from under the jack. Both wires
     then run over the frame to the stock VBAT pads.
   * Check the polarity at the VBAT pads with a meter before you put a cell in.
2. **Switch carrier into the front shell.** Lay the front shell face down and put the **carrier** in from inside:
   stem outward through the wall slot, flange into the pocket, where it rests on the pocket floor. Slide it to the
   same position as the board's switch. (The knob goes on later.)
3. **Plungers.** Drop the two plungers into their holes, flange side in.
4. **Board.** Lower the board (LCD, buttons, everything soldered, battery wires attached) straight down into the
   front shell. The USB-C and the switch head slide down their wall channels; the switch head drops into the
   carrier's socket, which is open toward the board. Fix it with **3 × M2 × 4 self-tapping pan-head screws** from
   the back of the board into the front-shell bosses (top hole and both bottom corners).
5. **Knob.** Press the switch knob onto the stem from outside (tight fit, add a drop of CA glue).
6. **Battery frame.**
   * Option `"front"`: put the frame (holder glued on, wires soldered) onto the front unit, ribs toward the board,
     and drive 2 × M2 × 5 countersunk self-tapping screws from the holder side of the plate into the two bosses at
     the jack end. Insert the cell.
   * Option `"back"`: put the frame into the back shell and drive 2 × M2 × 8 countersunk screws from the top of the
     plate into the two columns. Insert the cell (from the open side of the holder, before the frame goes in).
7. **Close.** Press the back shell onto the front unit until the four snaps click. To open, use the pry notch at the
   top end.

## Controls and openings
* **S1 and S3** (37.25 and 45 mm from the top) use through-case plungers. The 3.1 mm stem passes through a 3.5 mm
  hole and stands 0.8 mm proud. The 5.6 mm flange inside keeps the plunger from falling out. At rest the plunger
  sits 0.15 mm above the button cap and has 0.3 mm of play below the ceiling.
* **S2, S4 and S5** (54, 62 and 70.75 mm) use pin holes. They are modelled at 1.2 mm so a printed hole comes out
  near 1 mm (`pinhole_clr`). Each has a 2.4 mm lead-in cone on the outside and a 3.0 mm guide tube that ends 0.35 mm
  above the button cap.
* **Power switch (two-piece cap).** The slot no longer opens onto the split, so a one-piece cap could not be fitted.
  * **Carrier:** 6 × 3.6 × 1.7 mm flange in a closed wall pocket (z −3.9..+0.1), and a 3 × 2.4 mm stem through a
    closed 5.4 × 2.8 mm slot. Its socket fits the 1.5 × 1.5 head with 0.1 mm per side and is open toward the board
    (and toward the inside), so the head drops in when the board goes in.
  * **Knob:** the same ribbed 7 × 5 mm knob as before, sticking out 2.45 mm, with a 1.5 mm deep socket that is
    0.05 mm per side over the stem: press fit plus a drop of CA glue.
  * Travel ±1.0 mm (`sw_travel` = 2.0); the check confirms carrier and knob move freely at −1, 0 and +1 mm.
* **USB-C.** Same 9.4 × 3.8 mm opening and 13 × 7.6 mm OpenALD-style plug recess as before, now entirely in the
  front shell. The recess is 0.45 mm shallower (it stops 0.55 mm outside the receptacle face) so the drop-in channel
  behind it keeps a skin.
* **Headphone jack.** 6.8 mm plug hole + 7.8 mm × 1.0 mm counterbore (45° chamfer) in the end wall; the 5 mm barrel
  ends 1.2 mm inside the wall. The plug's overmold has to fit a 6.8 mm hole for the first 1.0 mm and the plug
  reaches 2.2 mm in to the barrel face (see the assumptions).
* **LCD window.** It is 18.4 × 12.2 mm (2026-11-21), with a 0.8 mm 45° bezel.
  * The top edge now covers **2.0 mm** of the glass (`lcd_top_cover`), so the window starts 8.75 mm from the board
    top. That hides the zebra strip.
  * The other three edges cover 0.8 mm (`lcd_border`), so the window ends 20.95 mm from the top and is 18.4 mm wide.

## LCD retaining frame (added 2026-11-20, top cover and zebra-edge ribs 2026-11-21)
The display is a bare LCD glass connected to the board only by a rubber (zebra) strip, so the front shell now holds
it in place:
* **Frame walls** (`lcd_frame_t` = 0.8 mm) hang from the inside of the front face around the glass and the backlight
  plate, with `lcd_frame_clr` = **0.2 mm** clearance per side. They stop `lcd_frame_gap` = 0.3 mm above the board.
  * Side walls run the full length of the glass and backlight; there is also a wall above the glass top edge.
  * At the glass's lower edge, a short wall locates the glass but stops 0.2 mm above the backlight plate, which
    continues under it.
  * Past the backlight's lower end there are only 3 mm corner stubs (`lcd_bl_stub`). The middle is left open for the
    LED pads and wires.
* **Light pressure.** By default (`lcd_press = "ribs"`) there are **12 short crush ribs** on the glass border outside
  the viewing window. None of them touch the backlight extension.
  * **5 ribs, each 3.0 mm long, along the top (zebra-strip) edge** (2026-11-21). They are centred 7.75 mm from the
    board top, in the middle of the 2 mm covered strip, at X = −8, −4, 0, 4 and 8 mm (`lcd_ribs_x_top`,
    `lcd_rib_len_top`). Together they press 15 mm of the 20 mm wide strip edge evenly.
  * 3 ribs, each 3.5 mm long, along the bottom edge.
  * 2 ribs, each 3.5 mm long, on each side.
  * Each rib tapers from 0.6 mm wide at the face (`lcd_rib_w`) to a 0.25 mm tip (`lcd_rib_tip`).
  * The tips reach **`lcd_preload` = 0.15 mm below the nominal glass top**. The narrow tips crush or flex slightly
    the first time the case closes, and the 1.6 mm front face bows a little. Together they give a light, even
    pressure instead of a hard stop.
  * `lcd_press = "lip"` uses one continuous thin lip around the border instead (more even pressure, but stiffer).
    `"none"` leaves only the frame.
* All of these are parameters, and the ribs follow the LCD height (`lcd_glass_t`, `lcd_bl_t`, `lcd_stacked`)
  automatically.
* **Z stack recheck.** The zebra strip agrees with `lcd_stacked = true`: the strip spans the gap between the glass and
  the board along one edge, beside the 1.4 mm backlight, and the glass rests on the backlight. Glass top is then
  1.0 + 1.4 + 1.78 = **4.18 mm** above the board's back face (3.18 mm above its front), unchanged. The LCD frame doesn't change
  the case thickness.
* **Tuning on the first print:**
  * **Missing or faint segments, or segments that come and go when you squeeze the case**, mean the zebra strip isn't
    pressed enough. Raise `lcd_preload` to 0.25–0.3, or put a 0.2–0.5 mm foam or tape shim on the ribs over the strip
    edge.
  * **Rainbow or dark blotches on the glass, or a case that won't close flat**, mean too much pressure. Lower
    `lcd_preload` to 0.05–0.1, or shave the rib tips.
  * **Never force it closed.** The glass is thin.
  * If the glass slides around, reduce `lcd_frame_clr` to 0.1. If it binds, increase it to 0.3.

## Hardware
* Board: **3 × M2 × 4 self-tapping pan-head screws** (top hole and both bottom corners, from the board back into the
  front shell; 1.7 mm pilots).
* Battery frame, option `"front"`: **2 × M2 × 5 90° countersunk self-tapping** (plate underside into front-shell
  bosses; 1.6 mm pilots).
* Battery frame, option `"back"`: **2 × M2 × 8 90° countersunk self-tapping** (plate top into back-shell columns;
  1.6 mm pilots).
* Back shell: no screws (4 snaps).
* No heat-set inserts any more.
* MPD BH-18650-PC holder and an 18650 cell (see the battery notes below).
* About 2 × 120 mm of 26–28 AWG silicone wire.
* Glue for the holder on the frame: medium CA or a thin layer of 2-part epoxy. Lightly sand both faces first. Hot
  glue also works, but it is softer. PETG is harder to glue than PLA.
* A drop of CA for the switch knob.
* Optional: 2 × 2-56 or M2.5 screws and nuts through the holder's 3.2 mm holes.

## Printing
* **Front shell:** front face down. Bosses, tubes, the top-end post and the frame bosses grow upward (the frame
  bosses have 45° tops into the end wall). The switch pocket and USB/switch channels are small bridges (≤ 1.3 mm).
* **Back shell:** floor down. The frame ledges have 45° undersides; the snap bumps have 45° flanks.
* **Battery frame:** flat glue face down, ribs up. Option "front" has its countersinks on the bed side (fine for a
  45° cone). Use 4 or more perimeters and 30% or more infill so the plate is stiff.
* **Plungers:** flange down. **Switch carrier:** flange inner face down (stem up). **Switch knob:** knob face down.
* PETG or PLA with 0.2 mm layers. No supports are expected.

## Fit check (`fit_report.txt`)
All seven STLs are watertight and each is a single body. Everything was checked in the assembled position, for
**both** frame options: front shell, back shell, battery frame, plungers, switch carrier and knob, the PCB outline,
LCD and buttons, jack, USB-C, switch, the inverted 18650 holder with its cell, board screws and frame screws.
**Result: PASS, no unexpected interferences.**
* **Drop-in sweep:** the board with LCD, buttons, jack, USB-C and switch was moved straight along Z from 14 mm out
  to 0.3 mm from home in 0.25 mm steps: it touches neither the front shell nor the switch carrier anywhere.
* **Option "front" frame sweep:** the frame moved straight in from 12 mm away clears the front shell, the board unit
  and the carrier.
* Frame screws only touch their own pilots (front bosses for "front", back columns for "back").
* With the press ribs turned off, the LCD frame clears the LCD, the backlight and the PCB completely. With them on,
  the 12 ribs touch the glass 0.150 mm deep, all within the glass border.
* **Glue area:** 1586 mm² of flat contact between the frame and the holder base, out of 1624 mm².

Expected overlaps: the LCD rib preload, the USB-C shell's top 0.16 mm in the board-edge notch (the stand-in PCB has
no notch), and the self-tapping screws cutting into their pilots. These are checks against stand-in models built
from the measurements, not against the real parts.

## Assumptions: please measure these
1. **LCD height.** I assumed the glass sits on top of the backlight (total 3.18 mm above the board), which agrees with
   the zebra-strip construction. Measure the glass top above the board with the strip compressed as it normally
   sits; if it isn't 3.18 mm, adjust `lcd_glass_t`/`lcd_bl_t`.
   * Victor confirmed the zebra strip is on the glass's **top** edge, which is now covered by 2 mm.
   * The other three borders are assumed to be at least 0.8 mm wide outside the viewing area (`lcd_border`).
2. **Switch head.** I assumed it sits halfway down the 3.8 mm body (1.9 mm below the board), sticks out 1.5 mm past
   the board edge, and travels about 2 mm in total. Please check the head height, how far it sticks out, and the
   travel.
3. **Jack plug.** The plug now has to reach 2.2 mm into the case (6.8 mm hole for the first 1.0 mm). Slim plugs
   are fine; a fat overmold (over about 6.6 mm) may stop short and not click in. Bigger hole: `jack_plug_d`,
   deeper counterbore: `jack_cbore`. **Jack barrel.** I used **5.0 mm** across, not 6 mm: the jack body is only 5.25 mm tall, so a 6 mm barrel
   couldn't be centred on it. The barrel axis is at the middle of the body (2.6 mm below the board). Please measure
   the barrel diameter.
4. **USB-C.** I assumed a standard 8.94 × 3.26 mm shell, 7.35 mm deep, with its underside 3.1 mm below the board, so
   it is a mid-mount part sitting in a notch in the board edge. Please check the shell size and the height of its
   centre.
5. **Mounting holes.**
   * The bottom-corner holes moved down 1 mm on 2026-11-21: **6 mm up from the bottom end** (`hole_bot_d` = 74 mm
     from the top). I read "1 mm from the left and right" as the hole edge, giving centres 2.1 mm in, with a 2.2 mm
     hole.
   * The front bosses and board screws follow `hole_bot_d`.
   * The 2.25 mm hole at 28 mm is assumed centred and is **not used**, because the LED pads and wires sit near it.
     `holes[1] = "pin"` turns on a locating pin there.
6. **Back side.** Apart from the switch, USB-C and jack, I assumed nothing on the back is taller than 1.8 mm. The
   PCB edge support ribs on the battery frame (33–62 mm from the top, X 10.1–10.9 at the tip, widening to 9.3 at the
   plate) must land on bare board, and the three board-screw heads (about 3.8 mm across, 1.3 mm tall) now sit on the
   **back** of the board at the top hole and both bottom-corner holes. Please check those areas, including where the
   crystal sits. The option-"front" frame bosses (X ±3.4–7.2, below z −2.0) are just past the board's bottom end
   and must clear anything that overhangs it.
7. **Front side.** The front bosses at the top hole and the bottom corners, and the plunger flanges, must miss the
   crystal and the LED wires.
8. **Board outline.** The ends are modelled as rounded (6 mm radius at the top, 4 mm at the bottom). The case is
   rectangular, so this mostly matters at the bottom end: the option-"front" frame bosses stop 0.15 mm short of the
   board's bottom edge (straight edge assumed for |X| up to 6.5 mm).
9. **Battery holder.** The BH-18650-PC size comes from its KiCad model (77.7 × 20.9 mm).
   * I assumed the cell reaches 19.6 mm from the holder base, and that the holes are 10.68 mm from the − end and
     55.61 mm apart (MPD drawing).
   * **New:** I assumed the holder base is flat enough to glue to. If it has ribs or a recess, the glue area is
     smaller; a thicker epoxy layer or the optional screws make up for it.
   * The pins must be trimmed to 1.4 mm or less, or they will poke above the frame into the 0.3 mm gap under the
     jack.
   **Check that your cell fits:** protected 18650s are often 69–70 mm long and may not fit this holder.

## Battery and charging notes
* An 18650 is the same Li-ion chemistry (3.7 V nominal, 4.2 V full) as the stock 502035 LiPo, so the stock charger's
  voltage is right.
* The stock charger is sized for a 300 mAh pouch, probably about 100–300 mA. A 2500–3500 mAh cell will take roughly
  **10–30 hours** to charge from empty, and the charger IC may run warm for that whole time.
* The stock pouch has its own protection board, which the 18650 does not replace. Use a protected cell if it fits, or
  check whether the MI03 board protects the battery itself.
* Keep the cell's polarity exactly as the stock leads had it. A reversed 18650 can damage the board.
