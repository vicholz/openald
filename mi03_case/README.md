# MI03 FM Pocket Radio + 18650 case (adapted from the OpenALD single-board case)

For the stock MI03 board (silk "MLA-M3(2291) V4.1 20240627"), with its 300 mAh LiPo swapped for an 18650 in an
MPD BH-18650-PC holder (the same holder OpenALD uses). **CAD only: nothing has been printed, assembled or tested.**
This folder is separate from the OpenALD v1.0 design: none of the OpenALD files were changed.

## Files
* `mi03_case.scad`: the parametric source. Every measurement Victor gave is a named parameter at the top, and
  every guess is marked `ASSUMED`.
* `stl/mi03_front_shell.stl`: front face with the LCD window, 2 plunger holes and 3 pin holes with guide tubes.
* `stl/mi03_back_shell.stl`: back tub with the USB-C, jack and switch openings and the ledges for the battery frame.
* `stl/mi03_battery_frame.stl`: flat plate between the PCB and the 18650. The holder is glued to its underside, and
  it carries the two M2 inserts.
* `stl/mi03_button_plunger.stl`: print 2.
* `stl/mi03_switch_cap.stl`: print 1.
* `scripts/build.sh` rebuilds the STLs, runs the fit check and renders the previews. `scripts/check_fit.py` runs the
  watertight and single-body checks, the interference check and the glue-area measurement. `scripts/sections.py` draws the cross-sections.
* `fit_report.txt` is the latest check output. `previews/*.png` are the pictures.

## Size and Z stack
Z = 0 at the PCB back face.

| Z (mm) | What |
|---|---|
| +6.08 | Front face (front wall 1.6 mm, as in OpenALD) |
| +4.48 | Inside of the front face (0.3 mm above the LCD glass) |
| +4.18 | LCD glass top: board top + 1.4 mm backlight + 1.78 mm glass, **assumed stacked** |
| +2.50 | Button cap tops (1 mm body + 0.5 mm cap) |
| 0 to +1.0 | PCB |
| -5.25 | Bottom of the jack, the deepest part on the back (switch -3.8, USB-C -3.1) |
| -5.55 | Top of the battery frame (0.3 mm air gap under the jack) |
| -7.15 | Underside of the frame = glue face = holder base (holder mounted **base up**) |
| -26.75 | Lowest point of the cell (holder plus cell assumed 19.6 mm) |
| -27.15 | Top of the floor (0.4 mm clearance) |
| -28.75 | Back face (1.6 mm floor, as in OpenALD) |

**Outside size: 27.5 mm wide × 86.6 mm long × 34.8 mm thick** (34.83 mm). That is **1.4 mm thicker** than before the
battery frame (33.43 mm). Width and length are unchanged. The switch knob sticks out another 2.45 mm on one side.
The added 1.4 mm is the 1.6 mm frame plus a 0.3 mm air gap above it, offset by the 0.4 mm thinner floor. The floor
no longer needs wire grooves, so it went from 2.0 mm back to OpenALD's 1.6 mm.

## How it goes together
1. **Battery frame and holder.** Trim the holder's two PC pins to **1.4 mm or less** and solder 26–28 AWG silicone
   wires to them. Glue the holder **base up** to the flat underside of the battery frame, with its − (spring) end
   toward the jack end.
   * The pins sit in the frame's 3.0 × 3.6 mm slots, and the holder's two 3.2 mm holes line up with matching holes
     in the frame. A 3 mm drill bit or pin through each pair keeps the holder aligned while the glue sets.
   * Optionally, add 2-56 or M2.5 screws through those holes with nuts on the frame top.
   * The jack-end wire runs in a 1.4 × 0.9 mm groove on the frame top, sideways out from under the jack. Both wires
     then run over the frame to the stock VBAT pads.
   * Check the polarity at the VBAT pads with a meter before you put a cell in. The cell goes in from the open
     (floor) side of the holder.
2. **Into the back shell.** Lower the frame, holder and cell into the back shell. The frame rests on 1.0 mm ledges
   along both long walls and on a ledge across the jack end. It is notched where it passes the PCB edge ledges.
3. **Switch cap.** Drop the cap into its slot from above, with the inner plate in the wall pocket and the knob outside.
4. **PCB.** Lay the PCB in so the switch head goes into the cap's 1.7 mm square socket. The board edge sits on two
   ledges between 33 and 62 mm from the top, which stop it flexing when S1 and S3 are pressed. The frame's two insert
   columns come up under the bottom mounting holes.
5. **Front shell.** Drop the two plungers into the front shell, flange side in. Fix the PCB's top hole to the
   front-shell boss with an M2 × 4 self-tapping screw from the back of the PCB.
   * The front shell has three snap tabs: one at the top end and two beside the jack. They click into the back
     shell's end walls.
   * The top tab reaches down to 0.05 mm above the frame, so it also holds the frame's top end down.
   * The front wall closes the top of the switch slot, so the cap can't come out.
6. **Screws.** Fit 2 × M2 × 10 countersunk screws from the front face, through the two bottom-corner holes, into M2
   heat-set inserts in the battery frame's columns (OD 3.2, L 4.0, the same kind as OpenALD). This clamps the front
   shell, PCB and frame together, so the battery hangs from the PCB stack rather than from the back shell.
   * The frame's ledges sit 0.1 mm below it, so the screws, not the ledges, set its height.
   * To swap the cell, undo the two screws, unclip the back shell, and lift out the front shell, PCB, frame and
     holder as one unit. The cell comes out from below.

## Controls and openings
* **S1 and S3** (37.25 and 45 mm from the top) use through-case plungers. The 3.1 mm stem passes through a 3.5 mm
  hole and stands 0.8 mm proud. The 5.6 mm flange inside keeps the plunger from falling out. At rest the plunger
  sits 0.15 mm above the button cap and has 0.3 mm of play below the ceiling.
* **S2, S4 and S5** (54, 62 and 70.75 mm) use pin holes. They are modelled at 1.2 mm so a printed hole comes out
  near 1 mm (`pinhole_clr`). Each has a 2.4 mm lead-in cone on the outside and a 3.0 mm guide tube that ends 0.35 mm
  above the button cap.
* **Power switch.** The cap's socket fits the 1.5 × 1.5 head with 0.1 mm per side. The inner plate (6 × 3.6 mm)
  rides in a pocket in the wall, and the 3 × 2.4 mm stem goes through a slot. The ribbed outside knob is 7 × 5 mm
  and sticks out 2.45 mm. The slot allows ±1.0 mm of travel (`sw_travel` = 2.0); the check confirms the cap moves
  freely at −1, 0 and +1 mm.
* **USB-C.** The opening is centred on the connector at 27 mm from the top, with a 13 × 7.6 mm plug recess on the
  outside (OpenALD style). The receptacle ends 1.0 mm inside the outer face.
* **Headphone jack.** A 5.4 mm hole fits the barrel, with a 0.7 mm chamfer outside. The barrel ends flush with the
  outer face.
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
* 2 × M2 × 10 countersunk machine screws.
* 2 × M2 heat-set inserts, OD 3.2 mm, 4 mm long (holes 3.2 × 4.5 mm), in the battery frame's columns.
* 1 × M2 × 4 self-tapping screw (PCB top hole into the front shell; 1.7 mm pilot).
* MPD BH-18650-PC holder and an 18650 cell (see the battery notes below).
* About 2 × 120 mm of 26–28 AWG silicone wire.
* Glue for the holder on the frame: medium CA or a thin layer of 2-part epoxy. Lightly sand both faces first. Hot
  glue also works, but it is softer. PETG is harder to glue than PLA.
* Optional: 2 × 2-56 or M2.5 screws and nuts through the holder's 3.2 mm holes.

## Printing
* **Front shell:** front face down. The bosses, tubes and snap tabs grow upward (the top tab is now 11.6 mm tall
  and 0.9 mm thick, so print it slowly or with a brim if your printer wobbles thin features), and the bezel and countersinks are
  45° chamfers on the bed side.
* **Back shell:** floor down. The frame ledges and the PCB edge ledges all have 45° undersides. The earlier
  overhanging insert bosses are gone (the inserts are in the battery frame now).
* **Battery frame:** flat glue face down, columns up. No supports needed. Use 4 or more perimeters and 30% or more
  infill so the plate is stiff.
* **Plungers:** flange down.
* **Switch cap:** knob face down.
* PETG or PLA with 0.2 mm layers. No supports are expected.

## Fit check (`fit_report.txt`)
All five STLs are watertight and each is a single body. The parts were checked against each other in the assembled
position: front shell, back shell, battery frame, plungers, switch cap, the PCB outline, LCD and buttons, jack,
USB-C, switch, the inverted 18650 holder with its cell, and the screws. **No unexpected interferences.**
* The battery frame clears the jack (0.3 mm), the back shell (it sits 0.1 mm above its ledges), the cell and the
  front shell.
* With the press ribs turned off, the LCD frame clears the LCD, the backlight and the PCB completely. With them on,
  the 12 ribs touch the glass 0.150 mm deep, all within the glass border.
* **Glue area:** 1586 mm² of flat contact between the frame and the holder base, out of the holder's
  77.7 × 20.9 mm (1624 mm²) footprint. Only the two pin slots and the two 3.2 mm alignment holes are missing.

Three overlaps are expected:
* The LCD press ribs reach 0.15 mm into the glass on purpose (the preload).
* The USB-C shell's top 0.16 mm sits in the board-edge notch (the stand-in PCB has no notch).
* The self-tapping screw cuts into its pilot hole.

These are checks against stand-in models built from the measurements, not against the real parts.

## Assumptions: please measure these
1. **LCD height.** I assumed the glass sits on top of the backlight (total 3.18 mm above the board), which agrees with
   the zebra-strip construction. Measure the glass top above the board with the strip compressed as it normally
   sits; if it isn't 3.18 mm, adjust `lcd_glass_t`/`lcd_bl_t`.
   * Victor confirmed the zebra strip is on the glass's **top** edge, which is now covered by 2 mm.
   * The other three borders are assumed to be at least 0.8 mm wide outside the viewing area (`lcd_border`).
2. **Switch head.** I assumed it sits halfway down the 3.8 mm body (1.9 mm below the board), sticks out 1.5 mm past
   the board edge, and travels about 2 mm in total. Please check the head height, how far it sticks out, and the
   travel.
3. **Jack barrel.** I used **5.0 mm** across, not 6 mm: the jack body is only 5.25 mm tall, so a 6 mm barrel
   couldn't be centred on it. The barrel axis is at the middle of the body (2.6 mm below the board). Please measure
   the barrel diameter.
4. **USB-C.** I assumed a standard 8.94 × 3.26 mm shell, 7.35 mm deep, with its underside 3.1 mm below the board, so
   it is a mid-mount part sitting in a notch in the board edge. Please check the shell size and the height of its
   centre.
5. **Mounting holes.**
   * The bottom-corner holes moved down 1 mm on 2026-11-21: **6 mm up from the bottom end** (`hole_bot_d` = 74 mm
     from the top). I read "1 mm from the left and right" as the hole edge, giving centres 2.1 mm in, with a 2.2 mm
     hole.
   * The front bosses, frame insert columns and screws all follow `hole_bot_d`.
   * The 2.25 mm hole at 28 mm is assumed centred and is **not used**, because the LED pads and wires sit near it.
     `holes[1] = "pin"` turns on a locating pin there.
6. **Back side.** Apart from the switch, USB-C and jack, I assumed nothing on the back is taller than 1.8 mm. The
   battery frame's insert columns (5.2 mm diameter, bottom corners) and the PCB edge ledges (33–62 mm from the top, 0.6 mm under the edge) must land on
   bare board. Please check that area, including where the crystal sits.
7. **Front side.** The front bosses at the top hole and the bottom corners, and the plunger flanges, must miss the
   crystal and the LED wires.
8. **Board outline.** The ends are modelled as rounded (6 mm radius at the top, 4 mm at the bottom). The case is
   rectangular, so this only matters for the snap tab at the top end, which has 0.1 mm of clearance.
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
