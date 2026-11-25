# OpenALD Dock v1.0 — 6-slot USB-C charging dock

A charging dock for six OpenALD radios (**2 columns × 3 rows**). It is designed only for the **single-board and Feather
radios**, which share one case envelope (89.75 L × 34.83 T, USB-C on the left long side, 30.3 mm from the top end,
7.55 mm behind the front face, mouth 1.0 mm inside), so every pocket takes either of them. **The MI03 radio is not dock-compatible** (Victor, 2026-11-24: "The mi03 version doesn't need to work with the dock."); the dock is designed and checked only for the single-board and Feather radios. A radio **lies on its
USB-C side**, front face toward you, top end to the left, and drops onto a vertical USB-C plug in a shallow pocket.
**One USB-C PD input at the rear centre** powers all six slots.

> **Status: design only, nothing here is hardware-validated.** ERC/DRC are clean and the CAD fit check passes for both
> radios, but no board has been built, no charger tested, no part printed, and the plug height and insertion
> have not been measured on a real part. Treat the first build as a prototype.

The exact interface is in **[DOCK_INTERFACE.md](DOCK_INTERFACE.md)**.

**2026-11-24 redesign (still v1.0):** the old dock held the radios standing USB-C-down in 50.8 mm deep pockets
(191.8 × 111.7 × 62.5 mm). With the USB-C now on the long side, the radios lie down instead: the pockets are
89.75 × 34.83 footprints (+0.35 mm per side), the back and end walls ("fins") stand 14 mm above the pocket floor and
the front wall only 6 mm, so the front face — level bar, charge LEDs — stays in view. The dock is wider and deeper but
**much lower (26.3 mm)**. Widths differ (single board 30.5, Feather 32.9);
width is just the radio's height above the floor here, so all use the same pockets. Same electronics and schematic; the PCB was re-laid out and re-routed for the new
plug positions.

## Key numbers
| | |
|---|---|
| Outer size | **216.9 × 174.79 × 26.3 mm** (W × D × H; deck 18.3) |
| Spacing | **25.4 mm (1.0 in)** between radios, in both X and Y; margins 6 sides/front, 13.5 back |
| Pocket | 89.75 × 34.83 + 0.35/side; floor Z 12.3; back/end fins 14 above the floor, front wall 6; 1.5 mm lead-in chamfer |
| Plug | HX TYPE C-M 16P vertical, top Z 19.3 → **6.0 mm past the radio's receptacle mouth** (all three radios; full seat 6.20 ± 0.20) |
| Floor pads | 4.6 mm (`PAD_T`), one per slot |
| PCB | **211.1 × 169.0 mm**, 2-layer, 1.6 mm, all SMT parts on top (was 186.0 × 105.9) |
| Minimum charger | **USB-C PD, 45 W: must offer 20 V ≥ 2.25 A or 15 V ≥ 3 A** |
| Per-slot limit | ~1.45 A (1.09–1.81 A, SY6280 ±25 %), 5.10 V |
| Print bed | the top shell and base are 216.9 × 174.8 mm: **needs a ≥ 220 × 180 bed** (fits 220 × 220 with ~1.5 mm to spare; not a 180 × 180 / A1 mini) |
| Filament | top shell ~105 g + base ~101 g + 6 pads (PLA estimate) |

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
Status LED (light pipe in the deck between the centre pockets): green = 5 V up; red = input present but no usable PD
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

## Checks (2026-11-24)
* **ERC:** 0 errors, 0 warnings.
* **DRC:** 0 errors, **0 unconnected**. 69 silkscreen-only warnings (silk_edge_clearance, silk_over_copper, silk_overlap; cosmetic).
* **JLC placement:** `jlc_cpl_fit.py --check` → *correction table: OK*. Overlays in `previews/cpl_overlay_*.png`.
* **Case fit** (`scripts/check_dock_fit.py` → `case/dock_fit_report.txt`): **INTERFERENCES: 0**. It exports the real
  STLs of both radio cases (single board, Feather), puts each in every one of the six pockets
  in the docked pose and checks it against the shell, base, pads and plug; then the PCB and its 80 part boxes against
  every case part, and the case parts against each other. Smallest plug-to-case gap: single board 0.32 mm,
  Feather 0.32. Closest PCB part to the shell: D2, 0.19 mm. All printed STLs are watertight single bodies
  (`dock_floor_pads_x6.stl` is six bodies on purpose).
* Previews: `previews/dock_assembly.png`, `dock_assembly_rear.png`, `dock_exploded.png`, `dock_front_view_slot1.png`,
  `dock_print_layout.png`, `dock_plug_insertion_per_radio.png` (both radios on their plugs), PCB renders.

## Printing (no supports)
* **Top shell:** print it **upright, skirt on the bed**, as exported. The deck between walls bridges ≤ ~21 mm; the
  fins, bosses, light pipe and housings grow straight up. Vents and the rear USB-C opening bridge short spans.
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
4. Dock a radio **on its USB-C side, front face toward you, top end to the left**, and press it down onto the plug.

## Open risks and judgment calls
* **Plug height and insertion are not measured.** The HX drawing gives 11.60 (used here, 6.0 mm insertion) but also a
  12.50 overall. Measure a soldered plug from the PCB top; if it is taller, make `PAD_T` thicker by the difference in
  `scripts/geom.py` and rebuild.
* **Receptacle depth:** the real seat depth of the radios' receptacles isn't on their drawings; 6.20 ± 0.20 is the
  USB-C spec value. All three radios have the mouth 1.0 mm inside the side face.
* **Lying radios load the plug sideways** if pushed or knocked: the 0.35 mm guide and the 14 mm back/end fins take
  that, not the plug, but a radio pulled out at an angle will lever the plug. Lift straight up.
* **Old radios** (43 × 92 × 33.4 single board, 45.5 × 92 × 33.4 Feather, USB-C on the end) **do not fit** this dock.
* **Hand-soldered plugs:** fine pitch, must be perpendicular; ~0.5 mm misalignment tolerance.
* **Plug supply:** only 782 in stock at LCSC when checked. Buy spares early.
* **12 V fallback:** 12 V-only chargers are deliberately not supported.
* **Autorouted power layout:** Freerouting plus scripted widening of high-current tracks and GND pours on both
  layers. Review the buck hot loops in `previews/pcb_*.png` before ordering.
* **Heat:** six radios charging lying down in open-front pockets, no fan; deck and skirt are vented. Watch radio
  temperature on the first full charge.
* **While docked:** the radio's switch and wheel point up and are reachable; the single board's level bar and TP4056
  charge LEDs face you above the 6 mm front wall. The Feather's NeoPixel faces its own case wall (hidden).
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
