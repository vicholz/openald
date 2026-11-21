# MI03 FM Pocket Radio + 18650 case (adapted from the OpenALD single-board case)

For the stock MI03 board (silk "MLA-M3(2291) V4.1 20240627"), with its 300 mAh LiPo swapped for an 18650 in an
MPD BH-18650-PC holder (the same holder OpenALD uses). **CAD only: nothing has been printed, assembled or tested.**
This folder is separate from the OpenALD v1.0 design: none of the OpenALD files were changed.

## Files
* `mi03_case.scad`: the parametric source. Every measurement Victor gave is a named parameter at the top, and
  every guess is marked `ASSUMED`.
* `stl/mi03_front_shell.stl`: front face with the LCD window, 2 plunger holes and 3 pin holes with guide tubes.
* `stl/mi03_back_shell.stl`: battery tub with the USB-C, jack and switch openings.
* `stl/mi03_button_plunger.stl`: print 2.
* `stl/mi03_switch_cap.stl`: print 1.
* `scripts/build.sh` rebuilds the STLs, runs the fit check and renders the previews. `scripts/check_fit.py` runs the
  watertight check and the interference check. `scripts/sections.py` draws the cross-sections.
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
| -5.75 | Top of the 18650 (0.5 mm air gap) |
| -25.35 | Holder base / top of the floor (holder plus cell assumed 19.6 mm tall) |
| -27.35 | Back face (2.0 mm floor) |

**Outside size: 27.5 mm wide × 86.6 mm long × 33.4 mm thick.** The switch knob sticks out another 2.45 mm on one side.
The case is 2 mm wider than the widest part of the board (22.5 mm), with 0.5 mm clearance and 2 mm walls.

## How it goes together
1. **Battery.** Trim the holder's two PC pins to about 1 mm and solder 26–28 AWG silicone wires to them. Set the
   holder on the floor with its − (spring) end toward the jack. Its two 3.2 mm holes drop over the floor pegs, and
   side rails keep it straight; add double-sided tape if you like. The pins sit in floor pockets. The wires run in
   floor grooves to the USB-C-side wall, then up wall grooves into the 5 mm space under the PCB, and on to the stock
   VBAT pads. The − wire first runs along the wall past the bottom screw boss. Check the polarity at the VBAT pads
   with a meter before you put a cell in.
2. **Switch cap.** Drop the cap into its slot from above, with the inner plate in the wall pocket and the knob outside.
3. **PCB.** Lay the PCB in the tub so the switch head goes into the cap's 1.7 mm square socket. The board edge sits
   on two ledges between 33 and 62 mm from the top, which stop it flexing when S1 and S3 are pressed.
4. **Front shell.** Drop the two plungers into the front shell, flange side in. Fix the PCB's top hole to the
   front-shell boss with an M2 × 4 self-tapping screw from the back of the PCB. The front shell's tab at the top end
   clicks into the back shell's end wall. The front wall closes the top of the switch slot, so the cap can't come out.
5. **Screws.** Fit 2 × M2 × 10 countersunk screws from the front face through the two bottom-corner holes into M2
   heat-set inserts in the back shell (OD 3.2, L 4.0, the same kind as OpenALD).

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
* **LCD window.** It is 18.4 × 13.4 mm: the glass area minus a 0.8 mm border, with a 0.8 mm 45° bezel.

## Hardware
* 2 × M2 × 10 countersunk machine screws.
* 2 × M2 heat-set inserts, OD 3.2 mm, 4 mm long (holes 3.2 × 4.5 mm).
* 1 × M2 × 4 self-tapping screw (PCB top hole into the front shell; 1.7 mm pilot).
* MPD BH-18650-PC holder and an 18650 cell (see the battery notes below).
* About 2 × 120 mm of 26–28 AWG silicone wire.
* Optional double-sided foam tape under the holder.

## Printing
* **Front shell:** front face down. The bosses, tubes and snap tab grow upward, and the bezel and countersinks are
  45° chamfers on the bed side.
* **Back shell:** floor down. The insert bosses hang off the side walls with a 45° wedge underneath. Near the jack
  end, the holder's end wall leaves room for only a partial wedge, so about 3 mm of each boss's underside is a short
  overhang. It should bridge, but if it sags, use a support blocker there.
* **Plungers:** flange down.
* **Switch cap:** knob face down.
* PETG or PLA with 0.2 mm layers. No supports are expected apart from the note above.

## Fit check (`fit_report.txt`)
All four STLs are watertight. The parts were checked against each other in the assembled position: front shell,
back shell, plungers, switch cap, the PCB outline, LCD and buttons, jack, USB-C, switch, the 18650 in its holder,
and the screws. **No unexpected interferences.** Three overlaps are expected:
* The holder pegs sit in the holder's holes, which the stand-in model of the holder doesn't have.
* The USB-C shell's top 0.16 mm sits in the board-edge notch (the stand-in PCB has no notch).
* The self-tapping screw cuts into its pilot hole.

These are checks against stand-in models built from the measurements, not against the real parts.

## Assumptions: please measure these
1. **LCD height.** I assumed the glass sits on top of the backlight (total 3.18 mm above the board). If the glass
   sits directly on the board, set `lcd_stacked=false` and the case gets about 1.4 mm thinner.
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
   * The bottom-corner holes: I read "1 mm from the left and right" as the hole edge, giving centres 2.1 mm in and
     7 mm up, with a 2.2 mm hole.
   * The 2.25 mm hole at 28 mm is assumed centred and is **not used**, because the LED pads and wires sit near it.
     `holes[1] = "pin"` turns on a locating pin there.
6. **Back side.** Apart from the switch, USB-C and jack, I assumed nothing on the back is taller than 1.8 mm. The
   insert bosses (bottom corners) and the PCB edge ledges (33–62 mm from the top, 0.6 mm under the edge) must land on
   bare board. Please check that area, including where the crystal sits.
7. **Front side.** The front bosses at the top hole and the bottom corners, and the plunger flanges, must miss the
   crystal and the LED wires.
8. **Board outline.** The ends are modelled as rounded (6 mm radius at the top, 4 mm at the bottom). The case is
   rectangular, so this only matters for the snap tab at the top end, which has 0.1 mm of clearance.
9. **Battery holder.** The BH-18650-PC size comes from its KiCad model (77.7 × 20.9 mm). I assumed the cell top is
   19.6 mm above the holder base, and that the peg holes are 10.68 mm from the − end and 55.61 mm apart (MPD drawing).
   **Check that your cell fits:** protected 18650s are often 69–70 mm long and may not fit this holder.

## Battery and charging notes
* An 18650 is the same Li-ion chemistry (3.7 V nominal, 4.2 V full) as the stock 502035 LiPo, so the stock charger's
  voltage is right.
* The stock charger is sized for a 300 mAh pouch, probably about 100–300 mA. A 2500–3500 mAh cell will take roughly
  **10–30 hours** to charge from empty, and the charger IC may run warm for that whole time.
* The stock pouch has its own protection board, which the 18650 does not replace. Use a protected cell if it fits, or
  check whether the MI03 board protects the battery itself.
* Keep the cell's polarity exactly as the stock leads had it. A reversed 18650 can damage the board.
