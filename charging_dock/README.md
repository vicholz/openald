# OpenALD Dock v1.0 — 6-slot USB-C charging dock

A charging dock for six OpenALD radios (**3 columns × 2 rows, aligned grid**). It is designed
only for the **single-board and Feather radios**, which share one end footprint (31.9 W × 33.86 T) and one USB-C
position (**bottom end face, centred across the width, 6.62 mm behind the front face, mouth 1.0 mm inside**), so every
pocket takes either of them. **The MI03 radio is not dock-compatible** (Victor, 2026-11-24: "The mi03 version doesn't
need to work with the dock."); it keeps its side USB-C. A radio **stands upright on its bottom end**, front face toward
you, and drops onto a vertical USB-C plug in a pocket **recessed 25 mm into the flat top** of the dock. **One USB-C PD input at the rear** powers all six
slots.

> **Status: design only, nothing here is hardware-validated.** ERC/DRC are clean and the CAD fit check passes for both
> radios, but no board has been built, no charger tested, no part printed, and the plug height and insertion
> have not been measured on a real part. Treat the first build as a prototype.

The exact interface is in **[DOCK_INTERFACE.md](DOCK_INTERFACE.md)**.

**t116u redesign (2026-11-24, still v1.0):** both dockable radios now have their USB-C on the **bottom end**, so the
radios stand upright again (the earlier 2026-11-24 version had them lying on a side-mounted USB-C in 216.9 × 174.79 ×
26.3 mm). Pockets are 31.9 × 33.86 (+0.35 mm per side) with **50.8 mm walls** on the back and both sides; the front
wall is open above a 2.5 mm lip except for 5 mm corner returns, so the front faces (single-board level bar and charge
LEDs, Feather CHG LED and NeoPixel) stay visible. The right pocket wall has a notch at the front
above 30 mm for the single-board radio's switch knob and wheel. Same electronics and schematic; the PCB was re-placed
and re-routed for the new plug positions.

**t120u (2026-11-24, still v1.0):** Victor: "make the slots so they are in a grid and not offset." The back row now
stands directly behind the front row (aligned 3 × 2 grid), which shrinks the dock to **158.5 × 112.62 × 63.1 mm**
(PCB 152.70 × 106.82, re-placed and re-routed). Trade-off: front faces of back-row radios are hidden behind the
front-row radios unless you look down from steeply above (see *Feather LEDs in the dock* below).

**t121u (2026-11-24, still v1.0): flat dock.** Victor: "Remove the tall guides on the dock. The dock should be flat
with recessed square holes that are 2-4cm deep to act as a guide." The 50.8 mm pocket walls, front lips and corner
returns are gone: the dock is a closed **158.5 × 112.62 × 37.3 mm** box with six pockets **25 mm deep** in its flat
top (same aligned grid, same PCB, pads and plug height). The Feather's LEDs (4 and 20 mm above the floor) would sit
below the top, so each pocket's front wall has a **20 mm sight window** down to 2 mm above the floor: front row
straight out through the dock's front face, back row into a closed trench in the top whose floor rises at 50° toward
the front row. No side notch: both radios' switch knobs and wheels sit above 25 mm.

## Key numbers
| | |
|---|---|
| Outer size | **158.5 × 112.62 × 37.3 mm** (W × D × H; flat top) — **fits a 220 × 180 bed** |
| Layout | 3 × 2 aligned grid, **25.4 mm (1.0 in)** between radios in X and Y; margins 6 sides/front, 13.5 back |
| Pocket | 31.9 × 33.86 + 0.35/side, **recessed 25.0 mm** (floor Z 12.3, top Z 37.3, 1.5 mm lead-in chamfer); 20 mm sight window in the front wall from 2 mm above the floor (back row: sloped trench, 50°); no side notch |
| Plug | HX TYPE C-M 16P vertical, top Z 19.3 → **6.0 mm past the radio's receptacle mouth** (both radios; full seat 6.20 ± 0.20) |
| Floor pads | 4.6 mm (`PAD_T`), one per slot |
| PCB | **152.70 × 106.82 mm**, 2-layer, 1.6 mm, all SMT parts on top |
| Minimum charger | **USB-C PD, 45 W: must offer 20 V ≥ 2.25 A or 15 V ≥ 3 A** |
| Per-slot limit | ~1.45 A (1.09–1.81 A, SY6280 ±25 %), 5.10 V |
| Filament | solid volumes: top shell 104.5 cm³, base 47.5 cm³, 6 pads 37.4 cm³ (~235 g PLA if solid, less with infill) |
| Docked radios | single-board 89.75 mm tall, Feather 98.71 mm tall above the pocket floor (tops at Z 102 / 111) |

## Power architecture
```
USB-C IN (J1, HRO TYPE-C-31-M-12, CC1/CC2 -> HUSB238)
  -> F1 4 A fuse (0466004.NRHF) -> D1 SMBJ22A TVS -> C1 10 uF 50 V
  -> Q1 AO4407A P-FET input switch (gate: R2 100k / R3 47k / C3 4.7 nF soft turn-on, driven by HUSB238 GATE; opens on OVP)
  -> VIN_SW, C4 100 uF 35 V
     -> U2 SY8205FCC buck A (4.7 uH MWSA0604S, 3x22 uF + 470 uF, 75k/10k -> 5.10 V) -> slots 1, 2, 4
     -> U3 SY8205FCC buck B (same)                                                   -> slots 3, 5, 6
        each slot: SY6280AAC current-limited switch (Rset 4.7k -> ~1.45 A) + 10 uF -> vertical plug VBUS,
        22k Rp on CC ("default USB power" to the radio's 5.1k Rd), plug GND + shell to GND
Status LED (light pipe in the top, in the back-row gap between slots 4 and 5): green = 5 V up; red = input present but no usable PD
```
* **HUSB238** (VSET open = request up to 20 V, ISET 13.7k = 2.25 A) picks the highest PDO ≤ 20 V that offers ≥ 2.25 A,
  otherwise it steps down. D+/D− are left open (PD only).
* **Buck enable threshold:** EN divider 100k/12k from VIN_SW. The bucks turn on at 11.2–13.1 V (typ. 12.1 V). **5 V and
  9 V never enable them** (non-PD or 5 V-only chargers are safe: the dock stays off with the red LED lit). 15 V and
  20 V always enable them. **12 V-only chargers are not supported** (they may or may not start).
* Worst-case load is 6 × ~0.95 A × 5.1 V ≈ 29 W. At 20 V/2.25 A (45 W) there is about 35 % headroom after converter
  losses. Each buck is rated 5 A and carries ≤ 3 radios.

| Part | LCSC | Stock (2026-11-11 PST) | Unit |
|---|---|---|---|
| HUSB238_002DD PD sink | C7471904 | 17,771 | $0.47 |
| SY8205FCC buck ×2 | C111875 | 10,557 | $0.34 |
| SY6280AAC slot switch ×6 | C55136 | 97,877 | $0.09 |
| AO4407A input P-FET | C16072 | 19,166 | $0.33 |
| MWSA0604S-4R7MT 4.7 µH 7 A ×2 | C408457 | 8,136 | $0.17 |
| 0466004.NRHF 4 A fuse | C187596 | 14,764 | $0.08 |
| SMBJ22A TVS | C151920 | 7,664 | $0.07 |
| 100 µF 35 V / 470 µF 10 V electrolytic | C2895269 / C2858856 | 5,149 / 138,705 | $0.12 / $0.05 |
| HRO TYPE-C-31-M-12 input receptacle | C165948 | 281,637 | $0.19 |
| HX TYPE C-M 16P V-SMT vertical plug ×6 (hand solder) | C55200592 | **782** | $0.54 |

The full list is in `fab/openald-dock-BOM-human.csv` (live stock and price); `fab/cost_estimate.txt` has the cost estimate.

## Files
| Path | What |
|---|---|
| `kicad/openald-dock.kicad_{pro,sch,pcb}` | KiCad 9 project (schematic and board are generated by the scripts) |
| `fab/openald-dock-gerbers-jlcpcb.zip` | Gerbers + drill (JLCPCB) |
| `fab/openald-dock-BOM-jlcpcb.csv`, `fab/openald-dock-CPL-jlcpcb.csv` | JLC assembly BOM + CPL (JLC_CORR rotation/offset corrections applied) |
| `fab/openald-dock-centroid.csv`, `fab/openald-dock.pos` | Centroid / KiCad position files |
| `fab/openald-dock-BOM-human.csv`, `fab/cost_estimate.txt`, `fab/lcsc_lookup.json` | Human BOM with live stock and prices, cost estimate |
| `fab/erc_report.txt`, `fab/drc_report.txt`, `fab/jlc_cpl_fit.json` | Check reports |
| `case/openald_dock.scad`, `case/dock_params.scad` | OpenSCAD case (parameters generated from the PCB layout) |
| `case/dock_top_shell.stl`, `case/dock_base.stl`, `case/dock_floor_pads_x6.stl`, `case/floor_pads/*.stl` | Print-ready STLs (already in print orientation) |
| `case/dock_fit_report.txt` | Fit-check result (all three radio cases, real STLs, every slot) |
| `docs/openald-dock-schematic.pdf`, `previews/*.png` | Schematic PDF, PCB/case renders, CPL overlay plots |
| `scripts/` | Generators: `run_all_pcb.sh` (symbols → schematic → ERC → board → route → post-route → DRC), `make_fab.py`, `jlc_cpl_fit.py`, `build_case.sh`, `check_dock_fit.py`, `render_pcb_previews.py`; `geom.py` is the single source of the geometry |

## Checks (t116u, 2026-11-24)
* **ERC:** 0 errors, 0 warnings.
* **DRC:** 0 errors, **0 unconnected**. 72 silkscreen-only warnings (2 silk_edge_clearance, 39 silk_over_copper, 31 silk_overlap; cosmetic).
* **JLC placement:** `jlc_cpl_fit.py --check` → *correction table: OK*. Overlays in `previews/cpl_overlay_*.png`.
* **Case fit** (`scripts/check_dock_fit.py` → `case/dock_fit_report.txt`): **INTERFERENCES: 0**. It exports the real
  STLs of both radio cases (single board, Feather) plus what sticks out of them (single-board switch knob in both
  positions and wheel; Feather wheel and switch knob), stands each in every one of the six pockets and checks it
  against the shell, base, pads and plug; **sweeps the insertion path** (radio lowered straight down from above the
  top); checks the PCB and its 80 part boxes against every case part; and the case parts against each other.
  Smallest plug-to-case gap 0.32 mm (both radios); plug centred on the radio's USB opening. Closest PCB part to the
  shell: D2, 0.19 mm (part boxes). All printed STLs are watertight single bodies
  (`dock_floor_pads_x6.stl` is six bodies on purpose).
* **Feather LEDs in the dock** (rays at 0/15/30/45/60/75° upward from the CHG (≈ 4 mm above the floor), red (≈ 4 mm)
  and NeoPixel (≈ 20 mm) holes through the sight windows, tested against the shell and radios in the other five
  pockets). The single-board radio's level bar and charge LEDs sit ~77–82 mm up, well above the top.
  * **Front row, slots 1–3: clear at every angle (0–75°)**, including level, through the front windows.
  * **Back row, slots 4–6 with radios in the front row: blocked 0–60°, visible from about 75° up.** Removing the
    walls did not change this: the blocker is the front-row radio itself (64–74 mm above the top, 25.4 mm in
    front), which needs about 74° to look over. **With the front pocket empty**, the dock alone lets you see the
    CHG / red LEDs from 60° and the NeoPixel from 15°. Reported as `info`, not failures. Fix if needed (not built):
    a stepped back row (back pockets ≈ 60 mm higher for a ~45° view) or a much deeper gap between rows.
* Previews: `previews/dock_assembly.png`, `dock_assembly_rear.png`, `dock_exploded.png`, `dock_top_view.png`
  (aligned grid), `dock_front_view.png`, `dock_print_layout.png`, `dock_plug_insertion_per_radio.png`
  (both radios on their plugs), PCB renders.

## Printing (no supports)
* **Top shell:** print it **upside down, flat top on the bed**, as exported. Pocket walls, bosses, light pipe and the
  window blocks grow straight up; the back-row trench floors overhang at 40° from vertical; the only bridges are the
  20 mm front-window sills and the short vents / rear USB-C opening.
* **Base:** print it flat, as exported.
* **Floor pads (6):** print them as exported (one STL per slot in `floor_pads/`, or all six in `dock_floor_pads_x6.stl`).
* PETG or PLA, 0.2 mm layers, 3 walls. Try one radio in one pocket before printing all six pads. If the fit is tight,
  the guide clearance is `CLR_GUIDE` in `scripts/geom.py`.

## Assembly
1. **Order the PCB** with JLC SMT assembly (gerber zip + BOM + CPL). The six vertical plugs J2–J7 are **not** in the JLC
   BOM (LCSC has no EasyEDA footprint for C55200592). Buy 6 (+1 spare) and hand-solder them: 16 fine-pitch (0.8 mm)
   SMD pads plus 2 plated shell slots; use flux, a fine tip or hot air, and keep each plug **vertical** (a printed
   floor pad slipped over it works as a jig).
2. **Test before docking a radio:** with a ≥ 45 W PD charger, green lights and red stays off; each slot reads
   5.0–5.2 V on VBUS. A 5 V-only charger gives red only, no slot voltage.
3. Press 6 M3 heat-set inserts into the shell bosses. Lay the PCB on the base standoffs, drop the six floor pads in
   (pegs into the PCB holes), lower the shell over everything and fit 6 × **M3 × 10** screws from below.
4. Stand a radio in a pocket **USB-C end down, front face toward you**, and press it down onto the plug.

## Open risks and judgment calls
* **Plug height and insertion are not measured.** The HX drawing gives 11.60 (used here, 6.0 mm insertion) but also a
  12.50 overall. Measure a soldered plug from the PCB top; if it is taller, make `PAD_T` thicker by the difference in
  `scripts/geom.py` and rebuild.
* **Receptacle depth:** the real seat depth of the radios' receptacles isn't on their drawings; 6.20 ± 0.20 is the
  USB-C spec value. Both radios have the mouth 1.0 mm inside the bottom end face.
* **Tall radios on a plug:** the 25 mm deep pocket (0.35 mm clearance, ≤ ~1.6° tilt) takes side loads, not the plug;
  the radio guides for 18 mm before the plug tip reaches its opening, and its top stands 65–74 mm above the dock.
  Lift straight up.
* **Older radios** (side USB-C, 89.75 × 34.83, or the original end-USB 43 × 92 boards) **do not fit** this dock.
* **Hand-soldered plugs:** fine pitch, must be perpendicular; ~0.5 mm misalignment tolerance.
* **Plug supply:** only 782 in stock at LCSC when checked. Buy spares early.
* **12 V fallback:** 12 V-only chargers are deliberately not supported.
* **Autorouted power layout:** Freerouting plus scripted widening of high-current tracks and GND pours on both
  layers. Review the buck hot loops in `previews/pcb_*.png` before ordering.
* **Heat:** six radios charging upright in recessed pockets, no fan; the top and skirt are vented over the bucks. Watch
  radio temperature on the first full charge.
* **While docked:** the single-board level bar and charge LEDs are well above the top; the Feather CHG / red LEDs and
  NeoPixel show through the 20 mm sight windows (back row only from steeply above, see above). Both radios' switches
  and wheels sit above the 25 mm pockets.
* **Not validated:** HUSB238 negotiation, buck stability, SY6280 limits, thermals and plug mating are all untested.

## History
* v1.0 (2026-11-11): first design (radios standing USB-down, 191.8 × 111.7 × 62.5 mm). The project was renamed from
  OpenALS to OpenALD before release, so the dock was born as "OpenALD Dock v1.0".
* 2026-11-12: floor pads 3.1 → 4.0, standoffs 5.0 → 4.1 for 6.0 mm insertion.
* 2026-11-24 (still v1.0): unified radio envelope; radios lie on the USB-C side; 2 × 3 layout, 216.9 × 174.79 ×
  26.3 mm, PCB 211.1 × 169.0, pads 4.6; fit-checked with all three radios.
* 2026-11-24 (still v1.0): single-board radio widened to 30.5 (2-layer board), re-checked. MI03 support dropped
  (Victor: "The mi03 version doesn't need to work with the dock."): fit check, previews and the insertion plot cover
  the single-board and Feather radios only. Pocket geometry, outer size and PCB unchanged (both radios share the same
  89.75 × 34.83 footprint, so dropping the MI03 frees nothing).
* t116u (2026-11-24, still v1.0): USB-C moved to the **bottom end** of both dockable radios (centred, 6.62 behind the
  front face). Radios stand upright again: 3 + 3 staggered pockets, 50.8 mm walls with a front window, 187.15 ×
  112.62 × 63.1 mm (fits 220 × 180), PCB 181.35 × 106.82 re-placed and re-routed (DRC 0, ERC 0, CPL OK). Fit check
  adds the insertion sweep, the radios' protruding knobs/wheels and a Feather-LED line-of-sight test.
* t120u (2026-11-24, still v1.0): aligned 3 × 2 grid (Victor: "make the slots so they are in a grid and not offset").
  158.5 × 112.62 × 63.1 mm (fits 220 × 180), PCB 152.70 × 106.82 re-placed (LEDs, light pipe and C4 in the back-row
  gap 4–5; title and a screw in gap 5–6) and re-routed: ERC 0/0, DRC 0 err / 0 unconnected / 72 silk, CPL OK. Fit
  check 0 interferences, both radios, all six pockets; back-row Feather LEDs visible only from ~75° up (front row clear).
* t121u (2026-11-24, still v1.0): flat dock (Victor: "Remove the tall guides on the dock. The dock should be flat with
  recessed square holes that are 2-4cm deep"). 158.5 × 112.62 × **37.3** mm (was 63.1 tall), pockets recessed 25 mm,
  20 mm sight windows (front) / sloped trenches (back) for the Feather LEDs, no side notch, raised housings dropped
  (27 mm room under the top), shell printed upside down. PCB, pads and plug height unchanged (DRC/ERC/CPL as t120u).
  Fit check 0 interferences, both radios, all six pockets, insertion sweep.
