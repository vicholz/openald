# OpenALD — handoff / resume document

This file lets anyone (person or AI) pick the project up cold. It records **what exists, why it is the way it is, what
must not change, what is still open, and exactly how to rebuild and re-check everything**. The per-subproject READMEs
hold the full detail (the single-board README keeps every pre-release revision note and design review); this file is the
map and the decision log.

* Owner: Victor (GitHub `vicholz`). Designed 2026-11-09 … 2026-11-24 (America/Los_Angeles) with an AI assistant.
* Version: **v1.0** for every part. **Keep v1.0 even when changing the design** (owner's instruction).
* Status: **designed and CAD/datasheet-checked only. Nothing has been built, powered, programmed or measured.** Never
  describe any of it as hardware-validated until a real board has passed the checklist in §8.
* License: **released into the public domain under CC0 1.0** (see §11).

---

## 1. What OpenALD is
A pocket FM radio for headphones (the headphone cable is the antenna), one 18650 cell, USB-C charging and USB-C
programming, a thumbwheel for volume/tuning (its press is the battery check), a slide power switch and a 3-LED battery-level bar,
in a 3D-printed case. Plus a 6-slot charging dock, an off-the-shelf (Feather RP2040) variant and an 18650 case for the
stock MI03 radio. **Since t116u (2026-11-24) the single-board and Feather radios share one dock interface:** a
35.9 W × 33.86 T end footprint (t122u; was 31.9; edges r 2) with the **USB-C in the bottom end face, centred across the width,
6.62 mm behind the front face, mouth 1.0 mm inside the face**. They stand upright in the dock's pockets; lengths differ
(single board 89.75, Feather 98.71). **The MI03 keeps its side USB-C and is not dock-compatible** (Victor, 2026-11-24).

| Subproject | Main files | One-line status |
|---|---|---|
| `radio_single_board/` | `kicad/openald.kicad_{sch,pcb,pro}`, `case/openald_case.scad`, `fab/` | v1.0; t116u: **26.9 × 84.75 mm 2-layer** PCB, J1 centred on the bottom edge; case 31.9 × 89.75 × 33.86 body + t122u 35.9-wide dock collar on the lowest 27 mm; ERC 0 err (2 accepted warnings), DRC 0 err / 0 unconnected / 82 silk-only, CPL check OK, case fit 0 interferences |
| `charging_dock/` | `kicad/openald-dock.*`, `case/openald_dock.scad`, `scripts/geom.py` | v1.0; t116u: radios stand upright on their bottom-end USB-C; t120u: aligned 3 × 2 grid; t121u: flat top, pockets recessed 25 mm; t122u: 35.9-wide pockets, **170.5 × 112.62 × 37.3 mm** (fits 220 × 180), PCB 164.70 × 106.82 2-layer; ERC 0/0, DRC 0 err/72 silk-only, CPL check OK, dock fit 0 interferences (both radios, all six pockets, insertion sweep, Feather-LED line of sight: front row clear, back row only from ~75° up); 4.6 mm pads, 6.0 mm insertion |
| `radio_adafruit_feather_rp2040/` | `case/openald_feather_case.scad`, `scripts/layout.py` (no PCB: direct-mount wheel + switch) | v1.0; t116u/t122u: case **35.9** × 98.71 × 33.86, Feather flat (centring pegs) at the bottom end, **its own USB-C is the dock port**, CHG / red / NeoPixel LEDs through front-face holes, wheel right between Feather and FM module, switch left (heat-staked, t122u), FM module flipped; fit 0 interferences, dock interface MATCH; FM header/jack details assumed |
| `mi03_case/` | `mi03_case.scad`, `stl/` | CAD only; side USB-C; **not dock-compatible**; t123u: stadium USB-C opening 9.44 × 3.76 r 1.88 |

## 2. Hard constraints (from Victor — do not violate)
1. **Dock interface (t116u, 2026-11-24):** Victor: "All boards except for the MI03 should have the USB-C connector in
   the same location at the bottom so they can be placed into the charging station for charging." Single-board and
   Feather radios: USB-C in the **bottom end face, centred across the width, 6.62 behind the front face, mouth 1.0
   inside**, end footprint 35.9 × 33.86 (t122u, was 31.9). Do not change it without asking. (Supersedes the 2026-11-24 side-USB
   envelope 89.75 × 34.83 / 30.3 / 7.55 and the older frozen 33.4 mm thickness.) **Keep the single board 2-layer**
   (t115u/t116u); slightly larger is acceptable. **Feather: its on-board LEDs must be visible through case holes**;
   the battery display stays on the NeoPixel.
2. **MI03:** keeps its side USB-C; not dock-compatible (Victor: "The mi03 version doesn't need to work with the doc").
3. **Keep the positions** of the power switch, headphone jack, thumbwheel and battery holder *(superseded 2026-11-24:
   Victor overrode the old frozen positions and board size for the unified envelope; the parts kept their roles and
   sides — jack at the bottom end, wheel and switch on the right, holder under the board)*. (The battery-check button
   was on this list until Victor asked to remove it on 2026-11-11; the wheel press does its job now — see §3.)
   (The level-bar LEDs were allowed to move: once for the dock, then centred and raised on 2026-11-11 — see §3.)
4. **Version stays v1.0** even when the design changes (record changes in the history instead).
5. **Don't claim hardware validation.** Everything is datasheet/CAD-checked only.
6. Dock: 6 radios, **~1 in (25.4 mm) between radios**, **one USB-C PD input at the rear** powers all six,
   footprint as compact as possible (fits a 220 × 180 bed), radios **stand USB-C-end down** (t116u; the side-lying variant is superseded), aligned 3 × 2 grid (t120u),
   **flat dock with pockets recessed 2–4 cm** (t121u, Victor: "Remove the tall guides … recessed square holes that are
   2-4cm deep"; 25 mm used); front-row faces / LEDs visible while docked (sight windows), back row only from above.
7. Both dockable radios share `charging_dock/DOCK_INTERFACE.md`; length may differ (Feather 98.71).
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
| Vendor BOMs | Filled PCBWay (.xlsx) and NextPCB (.xls) official templates (38 lines, 74 placements/board, U4/BT1/J3 DNP; 37 lines / 75 placements after the 2026-11-11 wheel-press update). `scripts/make_vendor_boms.py`. |
| Minimal set | `fab/minimal/`: JLC places only J1, U1, U3, U7 (≈ $36 for 5 boards, estimate); LCSC hand-solder list with spares. |
| **OpenALS** | Project renamed "OpenALS" and reset to **v1.0** (folders, files, silkscreen, docs). Circuit unchanged. |
| **OpenALD** | Renamed to **OpenALD** ("a device, not a system"). Same v1.0. |
| Dock + LED move | For the dock the **level bar moved to a vertical column near the jack end**: D1/D5/D6 at x = 24.0, y = 15.4/12.4/9.4 mm (KiCad coords from top-left; D1 lowest, D6 nearest the jack, 3 mm pitch) ≈ 20 mm above the dock rim. Re-routed; nothing else moved; case thickness unchanged. TP4056 LEDs D3/D4 stay beside the USB-C (hidden when docked → firmware shows charging on the bar). **OpenALD Dock v1.0** designed in `charging_dock/`. |
| Feather variant | `radio_adafruit_feather_rp2040/` designed (see §5). |
| **Feather: direct-mount controls** (2026-11-11, still v1.0) | Victor: "add a case frame … where I can mount a SS-12F16 1P2T G4/G6 switch directly into the case, and glue the wheel into. I will solder wires from the wheel and the switch to the feather." The **controls PCB is retired** (moved to `radio_adafruit_feather_rp2040/archive/controls_board_pcb/`). **SS-12F16** SPDT panel switch: plate in a 0.6 mm pocket on the inside of the right wall (bottom half, centre Y 75, Z −5), 2 × M2 × 3 screws from outside into its tapped ears, knob slot 6.6 × 3.6, `SW_L` = 4 (G4, 2.6 mm proud; G6 = 4.6 mm). **SIQ-02FVS3** bought loose and glued into a frame cradle (1.6 mm platform, boss holes, side walls with tab notches; a tenon on the bottom-half post under it takes the push); dial moved 0.6 mm outward → **0.95 mm proud of the side / 1.95 mm above the thumb-pocket floor** (was 0.35 / 1.35). Top-half wheel slot now runs to the split with a bottom-half tab under the dial (the old Feather case could not be closed over the protruding dial — the new check found 30 mm³ of top half in that path). Divider and charge-mirror LEDs become optional hand-wired parts (inline resistors; two 3 mm LEDs in top-half sockets). Same GPIOs (A D24, B D25, push D4, C GND, switch common EN). Backup: `/workspace/openald-feather-pre-directmount-backup` on the build box (not in git). |
| **Feather: screwless switch + clamped frame** (2026-11-11, still v1.0) | Victor: "Can the switch have enough of a cut out to not require screws? Can the frame also be sandwiched between the top and bottom case parts so it does not move up and down in case the battery holder is not exactly the same?" **Switch moved to the LEFT wall** (bottom half, Y 72, Z −4; the right wall has no room above the wheel tab for a top-open groove) and is **screwless**: 1.2 mm outer skin + 0.7 mm groove (open to the top) + 0.8 mm ribs behind the ears with 0.25 mm crush bumps (plates 0.4–0.6), body in an 11.3 mm window between the ribs (takes the knob force in Y), knob drops down a channel in the skin; the frame's long left tab covers it (0.15 mm play) and a top-half tongue fills the channel. M2 holes/screws removed from CAD, BOM, docs. G4 now 2.8 mm proud (G6 4.8). **Frame clamped by the halves:** six deck tabs (L25, L72, R25, R42, R79, T33) sit in parting-line notches in the bottom half (floor Z −1) under top-half plugs (Z 0; `clamp_crush` to add squeeze); holder in a 0.2 mm floor pocket + 0.4 mm deck relief → **holder-to-deck gap 0.7 mm** (was 0.1), thin tape / glue dots instead of foam. New checks: switch drop-in path, frame-tab insertion path, top-half lowering path vs all parts, plug over each tab, holder gap. Backup: `/workspace/openald-feather-pre-screwless-backup` (not in git). |
| **Feather: test-print fixes** (2026-11-12, still v1.0) | Victor printed 52983f3: "The switch pocket doesn't have enough support behind and under it and can easily be pushed in." / "The feather board needs to be moved down 0.8-1mm because the USB connector is too recessed and the cable connection barely holds on. The fillet around the connector should also be a bit larger diameter." **Switch backing:** the thin ribs became a solid block from the case floor to the deck (Z −22.4..−1.0) fused to the left wall: side blocks behind the ears (X −1.85..5.2, 2 mm past the groove ends), a 2 mm back wall 0.30 mm behind the body (0.15 with a 0.6 plate), a solid shelf under the body, an 8.8 mm lug/wire slot open to the top; drop-in and screwless retention kept. **USB:** Feather moved 0.9 mm toward the USB face (`FEATHER_DY`; pegs, posts, LED windows/tunnels, RESET, shell-leg reliefs follow) → receptacle mouth **1.60 mm inside the bottom face, 0.10 mm behind the recess floor** (was 2.50 / 1.00); recess now straight-walled 13.0 × 7.6 r3, 1.5 deep + r1.0 face fillet (mouth 15.0 × 9.6; was a 12.8 × 7.4 → 9.8 × 4.4 bowl). Dock outer envelope unchanged (0.1788 mm²); every single-board opening still open; **dock plug insertion now 6.9 mm** (≈0.3 past full mate: radio may rest on the plug — dock `PAD_T` +0.3–0.4 or `FEATHER_DY=-0.6` if needed). Single-board radio has the same 2.5 mm / bowl USB geometry (not changed). Backup: `/workspace/openald-feather-pre-usbfix-backup`. |
| **Dock: per-radio plug depth / Feather riser shim** (2026-11-12, still v1.0; superseded by the next row) | Victor chose "make the dock pad thicker so the plug depth matches" for the Feather after 1452af8. Checked against the USB Type-C spec: full seat = receptacle effective shell **6.20 ± 0.20** past the mouth (the old "full mate ≈ 6.6" was the plug shell length 6.65). Single-board radio (mouth 2.50): 6.00 on the 3.10 pad (fine). Feather (mouth 1.60): 6.90 on the same pad = 0.5 past the 6.40 maximum seat, so it would stand on the plug. **One pad thickness can't serve both**: a pad thick enough for the Feather (≥ 3.60, i.e. 6.40) leaves the single board at ≤ 5.50, and matching the Feather to 6.00 (4.00) leaves it at 5.10. So `PAD_T` stays **3.10** (outer size 191.8 × 111.72 × 62.5 and the 50.8 pocket unchanged) and Feather pockets get a loose **0.90 mm riser shim** on the pad (radio footprint + 0.10/side, plug hole; `case/riser_shims/`): **both radios 6.00**, both resting on printed parts. `geom.py` now has `MOUTHS`, `TARGET_INSERTION`, `RISER` (computed: 0.00 / 0.90; grows with `PLUG_H` — 12.50 would give 0.90 / 1.80 and export a single-board shim), `insertion()`. Fit check covers shims and a Feather envelope on its shim (0 interferences). New preview `previews/dock_plug_insertion_per_radio.png` (`scripts/plot_insertion.py`). No radio design changed. Backup: `/workspace/openald_backup_charging_dock_20261112_161434`. |
| **Single board: USB-C to 1.60 mm + assembly notches; dock pad 4.0, shims removed** (2026-11-12, still v1.0) | Victor: "Update the USB on the single board to match." **J1 moved 0.9 mm toward the board edge** (placement.py 83.35 → 84.25; KiCad y 184.25; CPL Y 5.064 → 4.164, only J1 changed): shell overhangs the edge 0.9 mm, mouth **1.60** inside the bottom face, 0.10 behind the new straight **13.0 × 7.6 × 1.5 recess** (r 3.0, 1.0 rim), same as the Feather. Chosen over moving the whole PCB (would thin the 2.0 mm USB-end wall to 1.1 under a 1.5 recess and shift the jack, LEDs, switch and wheel relative to the case/dock). USB pre-route in `route_pcb.py` shifted 0.9; full Freerouting re-route (`run_all_pcb.sh 100`, best of 3: 909 tracks / 184 vias / 2.20 m vs 915 / 200 / 2.19 m). ERC 0/2 warn, DRC 0 err / 0 unconnected / 62 silk; fab + minimal + vendor BOMs regenerated, cost unchanged. **Assembly path:** a new check in `check_case_fit.py` (parts reaching past an inner wall, swept down to the split, vs the top half) showed the old top half could **not** be lowered over the wheel (29.8 mm³) or the switch knob (18.6 mm³); fixed with top-half notches down to the split and bottom-half tabs up to 0.5 mm below dial/knob (`asm_notches()`, `asm_tabs()`, `asm_fit` 0.2). Same check on the Feather found a 0.05 mm³ scrape at the USB receptacle → `usb_notch()` in the Feather top half (`case_top.stl` changed). Dock: riser shims removed, **`PAD_T` 3.10 → 4.00, `STANDOFF` 5.0 → 4.1** (floor Z 11.70, outer size, deck and 50.8 pocket unchanged), insertion **6.00 / 6.00**; screws now **M3 × 10** (M3 × 12 would bottom out). `check_dock.py` blocking area eroded 0.02 mm (facet noise). Backup: `/workspace/openald_backup_20261112_165151`. |
| **Feather: flat frame over the cell, firmware, wiring diagram** (2026-11-12, still v1.0) | Victor: "update the frame to not have a cutout/recess for the 18650 cell. Just add a minor outline for where it should sit. The recess is so small the printer doesn't generate supports and it gets stringy and is not smooth." Then: a 0.4 mm deep recessed (engraved) outline, no raised rib, ~0.8–1.0 mm line. "Also add feather code and wiring schematic/diagram". **Frame:** the 0.4 mm deck-underside relief over the holder is gone (`DECK_RELIEF = 0`); the underside is flat with an engraved holder-footprint outline **0.9 mm wide × 0.4 mm deep** (inner edge 0.1 mm outside the holder; `CELL_MARK_W/D`) and a 4 mm engraved "+" at the + end. Prints deck-down: 0.9 mm bridge, no supports. **Holder-to-deck gap 0.7 → 0.3 mm.** Only `frame.stl` changed (top/bottom geometry identical). Fit check PASS (0 interferences). **Firmware:** `firmware/openald_feather/` (Arduino, arduino-pico 6.3.2 + Adafruit NeoPixel), compiles (`firmware/build.sh`, prebuilt .uf2); turn = volume, short press = battery colour on the NeoPixel 3 s, hold 0.5 s = seek, push+turn = tune, flash-saved freq/volume, 3.25 V cut-off; not run on hardware. Fixed the firmware_notes example (D4 is GPIO 6, not 4). **Wiring:** `docs/wiring_diagram.svg/.png` redrawn (every wire, resistor/LED/cap symbols, splices), new KiCad schematic `docs/wiring_schematic/` (ERC 0/0, PDF), firmware pin table in `docs/pin_map.md`. Backup: `/workspace/openald-feather-pre-frameoutline-backup` (not in git). |
| **Feather firmware: NeoPixel only for the battery level** (2026-11-12, still v1.0) | Victor: "Update the code to show the battery level using the RGB led on the feather when it is first turned on for 5 seconds then turn off to save battery." Power-on display 5 s (`POWER_ON_SHOW_MS`), short press still 3 s (`PRESS_SHOW_MS`); removed the seek (blue), no-radio (magenta) and low-battery 10 s flash indicators, so the pixel is cleared at all other times (serial log only). No NeoPixel power switch exists on the Feather RP2040 (VDD on +3V3 per the Eagle file; GPIO 20 = MISO, left alone). Recompiled, `.uf2` updated; not run on hardware. |
| **Feather firmware: 97.3 MHz first-boot station** (2026-11-14, still v1.0) | Victor: "can you update the firmware to set the fm frequency to 97.3 on initial boot?" `DEFAULT_FREQ_10K` 9910 → **9730** (channel 103 on the 100 kHz grid; the 200 kHz tune step only applies to wheel turns, so 97.3 isn't rounded and turning from it goes 97.5 / 97.1 …). Settings magic `0x0A1D1000` → `0x0A1D1001` so a station saved by an earlier build (the EEPROM flash sector survives a .uf2 copy) is ignored once; later boots restore the saved station as before. Single board: no firmware exists, nothing to change. Recompiled, `.uf2` updated; not run on hardware. |
| Repo | This GitHub repo created 2026-11-11; scripts made path-independent (no `/workspace` paths); `tools/` added; CC0 chosen. |
| **Unified envelope: single board + Feather match the MI03; dock re-laid out** (2026-11-24, still v1.0) | Victor: "Try to make the original single board and feather versions the same width as the and usb-c connectors in the same position as the MI03 version. Resize any and all … as small as possible and consistent shape so they can all use the charging dock … Also update on the feather version fm module size: it is 27.25mm x 27.25mm with 3.8mm mounting holes …" **Shared envelope** 89.75 L × 34.83 T, r 5 / r 2, USB-C on the left long side 30.3 / 7.55 / 1.0 (MI03 values), 13.0 × 7.6 r 3 recess. **Single board:** PCB 38 × 87 2-layer → 22.5 × 84.75, 4-layer (In1 GND plane; 2-layer left GND islands — **superseded by the next row: 25.5 mm, 2-layer**), J1 on the left long edge, level bar across the board near the top, BH-18650-PC kept and screwed through its floor holes into the front shell, snap-on back cover, 0.8 mm holder spacer, no corner holes/inserts; case 43 × 92 × 33.4 → **27.5 × 89.75 × 34.83 (thicker by 1.43 — flagged)**; full re-route (934 tracks, 151 vias), ERC 0/2, DRC 0 err / 0 unconnected, CPL OK, fit 0. **Feather:** 45.5 × 92 × 33.4 → **32.9 × 89.75 × 34.83** (wider for the 27.25 mm FM module); Feather on edge beside the holder, FM module on a deck at the jack end (0.4 mm standoffs, clamped by four front-shell posts, optional M3), jack through a 6.8 mm end-wall hole, USB-C breakout as the dock port (VBUS → Feather USB via a Schottky), front shell / deck / back shell with snaps; NeoPixel now hidden. **Dock:** radios lie on the USB-C side; 191.8 × 111.7 × 62.5 → **216.9 × 174.79 × 26.3**, PCB 186.0 × 105.9 → 211.1 × 169.0, `PAD_T` 4.6, fins 14 / front wall 6, new `check_dock_fit.py` checks the real STLs of all three radios in all six pockets (0 interferences, insertion 6.0). Old `check_dock.py`, Feather `case/stl/` and the single-board `nut_variant/` removed. |
| **Single board back to 2 layers, 3 mm wider** (2026-11-24, still v1.0) | Victor: "Make the single board and all the cases slightly bigger if it helps to keep the board 2 layers." Board widened (length kept) and re-routed on 2 layers with GND routed as copper plus F/B pours; 24.5 and 25.0 mm left 3 unconnected (24.5 tried twice), **25.5 × 84.75 routed completely** → DRC 0 errors / 0 unconnected / 87 silk-only, ERC 0/2, CPL OK. `placement.py` stretches the 22.5 mm layout (`BOARD_W`, env `OPENALD_BOARD_W`): J1 fixed on the left edge, SW1/SW3 move with the right edge, holder and screw points centred, the rest scaled. `gnd_fanout.py` and the In1/In2 handling removed; gerbers back to F/B; 5-pc PCB estimate back to $2. Case **27.5 → 30.5 wide**, length/thickness/USB-C position unchanged, fit 0 interferences. **Dock unchanged:** the pockets are length × thickness (89.75 × 34.83 + 0.35/side) and width is only the height above the floor, so per-radio widths need no pocket change; dock fit re-run with the 30.5 case (0 interferences, plug gap 0.32, insertion 6.0). MI03 case unchanged (its board fixes it; it already defines the shared length/thickness/USB-C position). |
| **MI03 dropped from the dock** (2026-11-24, still v1.0) | Victor: "The mi03 version doesn't need to work with the dock." `check_dock_fit.py`, `geom.py` (`MOUTHS`/`WIDTHS`), `plot_insertion.py`, the dock previews and docs now cover only the single-board and Feather radios; the MI03 README says it is not dock-compatible. Dock geometry, outer size (216.9 × 174.79 × 26.3) and PCB unchanged: both remaining radios use the same 89.75 × 34.83 footprint and USB-C position, so the MI03 imposed nothing extra. Dock fit 0 interferences. |
| **t116u: USB-C on the bottom end, upright dock again** (2026-11-24, still v1.0) | Victor: "All boards except for the MI03 should have the USB-C connector in the same location at the bottom so they can be placed into the charging station for charging. Update the design of the single board if needed and board placement of the other cases as needed. Try to keep the single board 2 layer, and try to keep the feather position where its onboard LEDs can be seen through case holes." (+ "The mi03 version doesn't need to work with the doc".) **Shared dock interface:** 31.9 × 33.86 end footprint, USB-C in the bottom end face, centred, 6.62 behind the front face, mouth 1.0 inside. **Single board:** 26.9 × 84.75, 2-layer, J1 centred on the bottom edge, full re-place + re-route (983 segments, 146 vias), ERC 0/2, DRC 0 err / 0 unconnected / 82 silk, CPL OK, fab regenerated; case 31.9 × 89.75 × 33.86, fit 0. **Feather:** lies flat components-up at the bottom end, its own USB-C = dock port (breakout and Schottky removed, charging via its MCP73831 at 200 mA), CHG / red / NeoPixel LEDs and RESET under light tunnels to front-face holes (ray check clear), wheel on the right between Feather and FM module, switch on the left, FM module at the top end; battery to the BAT/GND pads, FM to 3V3/GND/SDA/SCL pads (no JST/QT plugs: no room); case 31.9 × 98.71 × 33.86, fit 0, wiring diagram + schematic (ERC 0/0), BOM, pin map, README updated. **Dock:** upright pockets 50.8 deep with a front window (2.5 lip, 5 mm corner returns) and a right-wall notch for the single board's knob/wheel; 3 + 3, back row offset 28.65 so back-row radios show through front-row gaps; 187.15 × 112.62 × 63.1 (fits 220 × 180); PCB 181.35 × 106.82 re-placed (slot switches in the Y-channel, bucks in the front-row gaps, LEDs/C4 front-left, input chain rear behind the slot 5/6 gap) and re-routed, ERC 0/0, DRC 0 err / 72 silk, CPL OK; `check_dock_fit.py` now also sweeps the insertion path, adds the radios' protruding knobs/wheels and ray-tests the Feather LEDs (clear at 15–45° upward in all slots). |
| **t120u: dock slots in an aligned grid** (2026-11-24, still v1.0) | Victor: "Yes extra length is ok. One change for the dock, make the slots so they are in a grid and not offset." Feather length 98.71 approved. **Dock:** 3 × 2 aligned grid (STAGGER 0), 158.5 × 112.62 × 63.1 (fits 220 × 180; was 187.15 wide); PCB 152.70 × 106.82 re-placed (LEDs, light pipe, C4 and a screw in back-row gap 4–5; title + screw in gap 5–6; bucks still in the front-row gaps; input chain behind gap 5–6) and re-routed (826 tracks, 76 vias): ERC 0/0, DRC 0 err / 0 unconnected / 72 silk, CPL OK. Fit check 0 interferences, both radios, all six pockets. **Feather LEDs:** slots 1–3 clear at 0–75°; slots 4–6 blocked 0–60°, visible from ~75° up (front-row radios in the way). Not fixed (not asked); options: a stepped back row (≈ 35 mm raise for a 45° view) or a deeper row gap (≈ +35 mm). |
| **t121u: flat dock, recessed pockets** (2026-11-24, still v1.0) | Victor: "Remove the tall guides on the dock. The dock should be flat with recessed square holes that are 2-4cm deep to act as a guide." **Dock:** 50.8 mm pocket walls, front lips, corner returns and the side notch removed; closed flat-topped box **158.5 × 112.62 × 37.3** (was 63.1 tall; fits 220 × 180) with six pockets recessed **25 mm** (POCKET_DEPTH; 0.35 clearance, 1.5 rim chamfer) in the same aligned grid. Feather LEDs (4 / 20 mm up) are below the top, so each pocket has a 20 mm front sight window from 2 mm above the floor: front row out through the dock front, back row into a closed trench in the top (floor 50°). Raised housings dropped (27 mm room under the top); title and slot numbers re-placed; shell prints upside down. PCB, pads, plug height unchanged (ERC 0/0, DRC 0 err / 72 silk, CPL OK). Fit check 0 interferences (both radios, all six pockets, insertion sweep); Feather LEDs: slots 1–3 clear 0–75°, slots 4–6 blocked by the front-row radios to 60°, visible from ~75° (dock alone: 60° CHG/red, 15° NeoPixel). |
| **t122u: Feather case fit fixes** (2026-11-24, still v1.0) | Victor: 2 mm more room beside the Feather for the battery plug, pins through the Feather holes, an insertable switch with backing, the FM module flipped / 1.5 mm up on shorter pegged standoffs, a smaller headphone hole. **Feather case 35.9 × 98.71 × 33.86** (was 31.9 wide; Feather centred, 4.5 mm to each wall). Deck pegs Ø2.2 in the 2.5 holes, 1.0 mm proud of the Feather top (front posts Ø4.0 with sockets). **Switch: heat-stake option** — the plate slides sideways from inside into a 0.8 mm wall pocket onto 2 × Ø1.4 studs (15 mm pitch through its M2 holes, 1.5 mm to melt); deck ribs stop 0.4 mm behind both plate ends; knob slot unchanged (2.8 mm proud). **FM module flipped**, flat side 1.5 mm under the ceiling on Ø5.5 standoffs with Ø3.4 pegs (0.6 into the Ø3.8 holes), Ø6 deck posts with pegs below, +1.5 mm toward the top (Y 67.96–95.21; case length unchanged, jack nose into the end wall), jack under the board through a deck notch; header/jack pins cut to ≤ 1.2 mm on the flat side (wiring unchanged; diagram note). **Jack hole Ø6.95** (6.35 + 0.3/side; was 6.8 + Ø8.6 chamfer), axis Z 25.99, spanning the shell split (front U-notch + back tab). Fit 0 interferences, new switch-insertion sweep and rib check OK, LEDs clear, dock interface MATCH. **Dock:** both radios keep one end footprint: pockets **35.9** wide, single-board case gets a 35.9 dock collar over its lowest 27 mm (body still 31.9; knob/wheel above it). Dock **170.5 × 112.62 × 37.3** (25.4 gaps kept), PCB **164.70 × 106.82** re-placed / re-routed: ERC 0/0, DRC 0 err / 0 unconnected / 72 silk, CPL OK; dock fit 0 interferences, LED visibility unchanged. |
| **t124u: part colours** (2026-11-25, still v1.0) | Victor: "if possible make all 3 cases and their parts different colors so it is easy to tell the parts apart". One hue family per case: single board blues, Feather greens, MI03 oranges / reds, dock purples; each part its own shade (`tools/palette.py`, repeated as `C_*` constants in each `.scad`). All assembly / exploded / print-layout / section previews use them (print layouts now rendered in preview mode so the colours show). New `tools/make_3mf.py` writes one **coloured 3MF plate** per case next to the STLs (3MF core `basematerials` display colours, one named object per part; checked with lib3mf: 0 warnings, manifold) and is run by each case build script; it fails if a `.scad` loses its palette. Legends in each README. No geometry change. |
| **t123u: MI03 rounded USB-C opening** (2026-11-25, still v1.0) | Victor: "MI03 case: make the cut out for the usb-c connector have rounded corners (same shape as usb-c connector)". The MI03 USB-C opening is now a stadium 9.44 × 3.76 mm with end radius 1.88 (half its height); same 0.25 mm/side clearance and position; drop-in channel uses the same profile; stand-in receptacle made stadium-shaped. MI03 fit check PASS, all 7 STLs watertight / single body. New previews `closeup_usb_c_opening.png`, `section_usb_opening_x-13.1.png`. Not printed. |
| **Wheel press = battery check; bar centred** (2026-11-11, still v1.0) | Victor: remove the separate battery-check button and use the wheel press; centre the level bar and move it up for the dock. **SW2 EVQ-P7A01P (C79167) removed** (footprint, 3D model, case hole, printed plunger). The wheel's push switch S now drives the gate of new **P-FET Q4 AO3401A (C15127)** with **R25 1M (C22935)** pull-up to VBAT; Q4 replaces SW2 between VBAT and VBTN, so D2/D10/R6/R7 work as before (switch off: hold the wheel in → MCU powered → bar shows level). S left PD4 (it now sits at VBAT); the press is read as **BTN_SENSE high on PC1** (wake PCINT9); PD4 spare. Mapping: short press = battery check 3 s, hold = seek, push-and-turn = tune. **Bar: D6/D5/D1 at x = 19.0 (centreline), y = 6.1/8.9/14.0**, windows evenly spaced at y = 6.1/8.9/11.7 (D1 tunnel slanted, it has to skip the holder peg hole at (19, 11.34)); window centres 32.6/29.8/27.0 mm above the dock rim. FB1/FB2 moved to (24.0, 10.4/12.4). Re-routed. −$0.10/board parts, one fewer extended-part fee. Backup of the pre-change folder: `/workspace/openald-pre-button-removal-backup` on the build box (not in git; the previous commit 9509ac4 has it too). |

## 4. Single-board radio (radio_single_board) — key design facts
**t116u (current):** 26.9 × 84.75 mm 2-layer board, J1 centred on the bottom edge (shell 1.5 mm past it), case 31.9 × 89.75 × 33.86 (front shell 9.85 / back cover 24.01), USB-C 6.62 behind the front face, mouth 1.0 inside the bottom face; level bar + charge LEDs at the top end; wheel and switch on the right edge (knob 2.8 / wheel 0.35 proud). Older size/position notes below are history.
**Blocks:** USB-C (HRO TYPE-C-31-M-12, C165948; 5.1k CC pull-downs = default USB power) → TP4056 (C16581, PROG R3 1.2k)
→ DW01A (C351410) + FS8205A (C2830320) protection → Q2/Q3 reverse-polarity → MPD BH-18650-PC holder (bottom side).
SW1 SK-12E12-G5 switches VBAT → VSYS. U5 XC6206 → +3V3R (radio + I2C pull-ups). U6 XC6206 → +3V3 (MCU only) from
VMCU = D8 (VSYS) ∪ D9 (VBUS) ∪ D10 (VBTN = wheel press via Q4). RRD-102 module (U4, hand-soldered); audio through 100 µF caps + 600 Ω
ferrites; headphone ground via FB3 = antenna, coupled with 1 nF. Exact LCSC numbers for every part:
`fab/openald-BOM-human.csv`.

**Pin map (ATmega328PB TQFP-32, MiniCore names):** D3/PD3 ENC_B · D4/PD4 spare (was ENC_SW) · pin 3 PE0 = GND and pin 6 PE1 = +3V3
(leave as inputs, no pull-up) · D5/PD5 LVL1 (D1, lowest) · D6/PD6 LVL2 (D5) · D9/PB1 LVL3 (D6, top) · PB3/4/5 ISP only ·
AREF 100 nF (use internal 1.1 V) · **A0/PC0 BAT_ADC** · **A1/PC1 BTN_SENSE** (wheel press via Q4; high = pressed; `INPUT`, no pull-up) · **A2/PC2 CHRG_SENSE**
(pull-up on, low = charging) · A4/A5 SDA/SCL (1k series, 4.7k pull-ups to +3V3R) · PC6 RESET (10k, DTR via 100 nF) ·
PD0/PD1 UART to CH340K (1k on TX) · D2/PD2 ENC_A. Spare: PB0, PB2, PB6, PB7, PC3, PD4, PD7, ADC6/7. Full table: radio README.

**Formulas**
* Battery: `V_sys = ADC/1023 × 1.1 × 59/12` (47k/12k divider, internal 1.1 V ref). 4.2 V → ~0.85 V at the pin (ADC ≈ 795).
  The 1.1 V reference is only 1.0–1.2 V: **calibrate once per board**.
* Wheel-press sense (BTN_SENSE): 4.7k/10k divider from VBTN; read as digital high or ADC1 threshold ≈ 1.3 V.
* Charge current: `I = 1100 V / R_PROG` → 1.2k ≈ 917 mA.
* LED current: ~0.85 mA typ through 1k from 3.3 V (KT-0603G Vf ≈ 2.4 V at 1 mA).
* Battery life (paper estimate): radio on ≈ 20–25 mA → ~130 h on a 3000 mAh cell; off ≈ 7–9 µA standby.

**Firmware requirements** (single board: no firmware yet; Feather: `radio_adafruit_feather_rp2040/firmware/openald_feather`, compiles, untested) — full spec in the radio README "Firmware spec":
* **Thumbwheel (SIQ-02FVS3):** A/B/S are switches to common C (GND). A/B: internal pull-ups; no RC or ESD. S drives Q4's gate (R25 1M to VBAT) and is read as BTN_SENSE (PC1, high = pressed).
  15 detents, one quadrature cycle (4 Gray-code transitions) per detent; count one step per detent, not per edge.
  1 ms state-table poll debounces. On the single board, PD2/PD3 are INT0/INT1 but at rest A or B may already be
  low, so wake from Power-down with pin-change (PCINT18/19 for the turn, PCINT9 on PC1 for the press), not INT0/INT1 low-level. Example code is in
  `radio_single_board/README.md` (MiniCore) and `radio_adafruit_feather_rp2040/docs/firmware_notes.md` (Arduino-Pico).
  Behaviour: turn = volume, **short press = battery check (bar 3 s)**, push-and-turn = tune, hold ≥ 0.5 s = seek; switch
  off: holding the wheel in powers the MCU and shows the level while held. Paper-verified only; not hardware-tested.
* Level bar off by default; show on a short wheel press (3 s). Levels: ≥ 3.90 V ●●● · 3.60–3.90 ●●○ · 3.40–3.60 ●○○ ·
  3.30–3.40 LED1 slow blink · < 3.30 LED1 fast blink. Sample ADC with LEDs off, 16-sample average, 50 mV hysteresis.
* **Low-battery cutoff 3.25 V**: mute/power down the RDA5807M and sleep the MCU (DW01A at ~2.5 V is the backstop).
* **Don't call `Wire.begin()` while the radio rail is off** (AVR pull-ups would back-feed ~80 µA/line into the
  unpowered RDA5807M); start Wire only when V_sys > 3 V, `Wire.end()` + SDA/SCL as inputs before power-off.
* **V_sys < 2.5 V with BTN_SENSE low = USB-only power** (switch off, MCU on VBUS): cell voltage unknown; keep radio off.
* Wheel-powered (switch off, wheel held in): add ~0.1–0.15 V for D2's drop (calibrate).
* While charging the reading is ~0.15 V high: estimate = V − 0.15 V; show "filling" blink.
* **Show charging on the level bar** — D3/D4 (TP4056 LEDs) are hidden inside the dock pocket.
* Keep `Serial` closed in normal use (UART back-feed into unpowered CH340K). BOD 2.7 V. Internal 8 MHz. RDA5807M I2C 0x10/0x11.
* Programming: burn bootloader once over J3 (3.3 V ISP, never 5 V), then upload over USB-C (CH340, MiniCore ATmega328 /
  variant 328PB, internal 8 MHz, 38400 baud safest).

## 5. Feather RP2040 variant — key facts and risks
* Parts: Adafruit Feather RP2040 (#4884), RDA5807M breakout with built-in 3.5 mm jack (~27 × 27 mm, 4-pin I2C: VCC,
  GND, SDA, SCL; runs 3.3–5 V, ~20 mA; use 3.3 V — not 5 V tolerant; drives 32 Ω headphones; headphone cable antenna),
  MPD BH-18650-PC holder + protected 18650 (Feather has no reverse-polarity protection), JST PH lead (#261), STEMMA QT
  cable (#4210). **No PCB:** Mitsumi SIQ-02FVS3 wheel (LCSC C2925423, loose) glued into a printed frame cradle and an
  SS-12F16 SPDT panel slide switch (G4 default, `SW_L` in `layout.py`) pressed into a screwless groove in the left case
  wall (solid backing block floor-to-deck behind/under it; frame tab + top-half tongue close it in), both hand-wired
  to the Feather (A D24, B D25, push D4, C GND; switch common EN, OFF-end lug GND). Optional hand-wired 220k/220k divider
  on A0 and two 3 mm charge LEDs (VBUS/STAT, top-half sockets, visible while docked). Old controls PCB: `archive/`.
* **t122u (current) changes:** 35.9 wide (4.5 mm Feather edge to wall each side: room for the JST battery plug);
  deck pegs Ø2.2 stick 1.0 mm through the Feather holes (posts Ø4.0 with sockets); **switch heat-staked**: plate in a
  0.8 mm pocket on 2 × Ø1.4 studs (15 mm pitch, through the M2 holes), deck backing ribs 0.4 behind both plate ends;
  **FM module flipped** (flat side to the front, 1.5 mm under the ceiling on Ø5.5 standoffs with Ø3.4 pegs, Ø6 deck
  posts with pegs below), moved 1.5 mm toward the top end, jack under the board through a deck notch, **jack hole
  Ø6.95** spanning the shell split (front U-notch + back-shell tab); header/jack pins cut to ≤ 1.2 mm on the flat side.
* **Case (t116u):** 31.9 × 98.71 × 33.86 mm (t122u: 35.9 wide). Back shell: holder flat on the floor, centred, + toward the USB
  end (PC pins trimmed and wired; joints in floor relief holes). Deck over the holder carries the **Feather flat,
  components up, at the bottom end** (its own USB-C = dock / charge / programming port, mouth 1.0 inside the bottom
  face), the wheel cradle on the right between the Feather and the FM module, and the 27.25 mm FM module at the top end
  (jack through the top end wall). Front shell: light tunnels to front-face holes over the Feather's CHG, red LED and
  NeoPixel, RESET pin tube, the switch in a left-wall groove, clamp posts, snaps. Battery to the BAT / GND pads and FM
  to the 3V3 / GND / SDA / SCL pads (JST and STEMMA QT plugs don't fit). No breakout, Schottky or 3 mm LEDs any more.
  The bullets below are history:
* (2026-11-24, superseded) 32.9 × 89.75 × 34.83 side-USB case with a USB-C breakout and the Feather on its edge.
* Old case: bottom 52.8 mm identical to the single-board case (43 × 33.4 mm), tapers to 45.5 mm wide above; 92 mm long.
  Feather sits where the old PCB was, 0.9 mm nearer the USB face (receptacle mouth 1.6 mm inside the bottom face, cable-plug
  recess 13.0 × 7.6 × 1.5), so its USB-C lines up with the dock plug (no adapter; insertion 6.0 mm on the dock's 4.0 mm pads, same as the single board). Older Feathers (rev B and
  before, 2.48 mm USB overhang): `python3 scripts/feather_data.py --usb-overhang 2.48` then `case/build_case.sh`.
* ~$32/radio in priced parts (estimate, excl. screws/wire/passives/shipping/FM module); no JLC order any more.
* **Risks/TODO:** FM-module hole/jack positions are **estimates** (photo could not be measured) — measure and edit
  `scripts/layout.py` (table in its README) before printing; charging is only **200 mA (≈ 18–20 h)**; off-state drain
  ~0.4 mA via the Feather EN pull-up (~9 %/month; swap that resistor to 100k → ~50 µA total); battery change means
  lifting the frame; top end held by the lip only; STAT tap is a fine-wire joint; frame is clamped at the parting line by
  six tabs (zero nominal clearance) and clears the holder by 0.3 mm (flat deck since 2026-11-12; `DECK_RELIEF=0.4` restores 0.7); wheel has no RC debounce; wheel push travel (1.0 mm
  assumed) and glue strength untested; screwless switch grip (groove/crush bumps/1.2 mm skin) depends on print
  tolerance (backing made solid after test print 1, not reprinted); dock plug may bottom out ~0.3 mm in the receptacle; SS-12F16 clone dimensions vary and the OFF lug must be found with a meter.

## 6. Charging dock — key facts and risks
* **Power:** rear USB-C (HRO TYPE-C-31-M-12) → **HUSB238** PD sink (C7471904; requests the highest PDO ≤ 20 V with
  ≥ 2.25 A) → 4 A fuse + SMBJ22A TVS → AO4407A P-FET input switch → **2 × SY8205FCC** bucks (C111875, 5.10 V, slots
  1/2/4 and 3/5/6) → **SY6280AAC per slot** (C55136, ~1.45 A limit, 1.09–1.81 A) → vertical plug VBUS; 22k Rp on CC.
* **Charger requirement: USB-C PD ≥ 45 W offering 20 V ≥ 2.25 A or 15 V ≥ 3 A.** Bucks enable at ~11.2–13.1 V, so
  5 V/9 V never start them (red LED, dock off). **12 V-only chargers are unsupported.** Worst case 6 × ~0.95 A × 5.1 V ≈ 29 W.
* Mechanics (t121u, t122u width): **170.5 × 112.62 × 37.3 mm** flat-topped box (fits a 220 × 180 bed), radios **stand upright on
  the bottom-end USB-C**, aligned 3 × 2 grid (back row directly behind the front row), 25.4 mm gaps,
  pockets 35.9 × 33.86 + 0.35/side **recessed 25 mm** (1.5 mm rim chamfer), 20 mm sight window in each pocket's front
  wall from 2 mm above the floor (front row: out through the dock front; back row: closed trench, floor at 50°), no
  side notch, floor Z 12.3, top 37.3, pads 4.6, insertion 6.0; shell prints upside down. PCB 164.70 × 106.82: slot switches in the Y-channel between the rows, bucks in the
  front-row gaps, status LEDs + light pipe + C4 in the back-row gap 4–5, title + screw in gap 5–6, input chain in the rear strip behind the slot 5/6 gap;
  no raised housings any more (27 mm under the top). (Was 158.5 × 112.62 × 37.3 with 31.9 pockets (t121u), 158.5 × 112.62 × 63.1 with 50.8 mm walls (t120u), 187.15 × 112.62 staggered (t116u), 216.9 × 174.79 × 26.3 side-lying, before that 191.8 × 111.7 × 62.5 upright.)
  Geometry source of truth: `charging_dock/scripts/geom.py`. Interface: `DOCK_INTERFACE.md`.
* **Risks/TODO:** vertical plug **C55200592 only 782 in stock** (buy spares; hand-soldered, 0.8 mm pitch, must be
  perpendicular); **plug height**: drawing says 11.6 mm (used) and 12.5 mm overall — measure; if taller, set `PLUG_H` and
  make `PAD_T` thicker and `STANDOFF` thinner by the difference (single-board radios built before 2026-11-12 with J1 flush only get 5.1 mm); **M3 × 10 screws** (not × 12); power stage was **autorouted** then widened — review buck hot loops before ordering; no fan —
  check temperatures; HUSB238 negotiation, buck stability, SY6280 limits all untested. Est. $90–110 for 2 assembled
  boards + 1 printed case (estimate).
* **Using a non-JLC assembler:** CPL files carry JLC/EasyEDA corrections (`JLC_CORR`). For PCBWay/NextPCB etc., export a
  plain KiCad position file (`kicad-cli pcb export pos --format csv --units mm --use-drill-file-origin`) or ask
  the parent design to add a "generic" CPL output; do **not** reuse the JLC CPL.

## 7. Regeneration and checks
Tool versions used: KiCad **9.0.2** (Debian `kicad 9.0.2+dfsg-1`), OpenSCAD **2021.01**, Python **3.13.5**, packages in
`requirements.txt`, Freerouting (build 2026-10-05) on OpenJDK 25 (re-routing only). Stock KiCad 3D models are needed
for the case fit checks: `tools/fetch_kicad3d.sh && export KICAD9_3DMODEL_DIR=$PWD/tools/kicad3d` (or install
`kicad-packages3d`). Without them the radio fit check silently checks only the project's own models — a complete `case/case_fit_report.txt` has 82 part lines starting with `BT1` (then 3 `ASSEMBLY` lines) (the 18650 holder).

**Quick check (non-destructive):** `tools/check_all.sh` → expected:
```
radio_single_board  ERC 0 errors / 2 warnings   (pin_to_pin U3 pin 3 PE0–GND and pin 6 PE1–+3V3: intentional 328P drop-in)
                    DRC 82 = 9 silk_edge_clearance + 35 silk_over_copper + 38 silk_overlap; 0 unconnected; 0 parity
charging_dock       ERC 0/0; DRC 72 = 2 silk_edge_clearance + 39 silk_over_copper + 31 silk_overlap; 0 unconnected; 0 parity
each                jlc_cpl_fit.py --check -> "correction table: OK"
ALL CHECKS PASSED
```
**Case fit:** `tools/check_all.sh --case` (or each `build_case.sh`) → `INTERFERENCES: 0` (radio: closest to tunnel
walls Q1 0.25 mm; dock (t122u): outer 170.5 × 112.62 × 37.3, flat, pockets 35.9 × 33.86, pockets recessed 25, aligned grid, single-board and Feather radios upright in all six
pockets incl. knobs/wheels and the insertion sweep, plug gaps 0.32 / 0.32, Feather LEDs clear in front-row slots 1–3, back-row slots 4–6 visible only from ~75° up (reported as info); the MI03
is not checked: not dock-compatible); feather `INTERFERENCES: 0` (t122u adds the switch insertion sweep and the staked switch vs the deck ribs), LED/RESET line of sight clear and
`dock interface: MATCH` (no PCB checks: the Feather variant has no PCB). Takes ~3 min (radio),
longer for the dock; rewrites STLs/previews (diffs are mesh-ordering/timestamp noise).

**Per subproject** (run from the subproject folder):
| Step | radio_single_board | charging_dock | radio_adafruit_feather_rp2040 |
|---|---|---|---|
| Full PCB regen (re-routes! needs Freerouting) | `scripts/run_all_pcb.sh [passes]` | `scripts/run_all_pcb.sh [passes]` | no PCB; `./make_all.sh` rebuilds wiring + schematic + case; `firmware/build.sh` compiles the firmware |
| Fab outputs | `cd scripts && python3 make_fab.py` and `python3 make_fab.py --minimal` | `cd scripts && python3 make_fab.py` | – |
| JLC CPL check | `cd scripts && python3 jlc_cpl_fit.py --check` (`--plots` for overlays) | same | – |
| Vendor BOMs | `cd scripts && python3 make_vendor_boms.py` | – | – |
| Case + fit + renders | `scripts/build_case.sh` | `scripts/build_case.sh` | `case/build_case.sh` |
| Previews | `python3 scripts/render_pcb_previews.py` | same | (in make_all/build_case) |

Notes: `make_fab.py` queries JLC's public parts API for live stock/price (slow, network); set **`OPENALD_OFFLINE=1`**
to reuse `fab/lcsc_lookup.json`. With fixed inputs, fab outputs regenerate byte-identical except timestamps (verified on a
fresh clone). Re-routing with Freerouting is **not deterministic** — after `run_all_pcb.sh` re-run DRC, `jlc_cpl_fit.py
--check`, `make_fab.py`, `build_case.sh` and re-inspect the layout. Scratch files go to `/tmp`. `FREEROUTING`, `JAVA`,
`EASYEDA_CACHE`, `KICAD9_3DMODEL_DIR` are the env overrides (`REF_CASE_DIR` is gone with the old Feather dock check).
Freerouting needs **Java 21+** (the 2026-10 build is class-file 69 = Java 25 on this box: `JAVA=/usr/lib/jvm/java-25-openjdk-amd64/bin/java`).
The single board's route is: `build_pcb.py` → `route_pcb.py` (Freerouting on 2 layers, GND routed too; F/B GND pours)
→ `stitch_gnd.py` → DRC. Freerouting is not deterministic: on a narrower `OPENALD_BOARD_W` it may leave unconnected nets;
re-run (or widen) until DRC shows 0 unconnected.
Freerouting is not in git: `route_pcb.py` defaults to `<repo>/tools/freerouting.jar`; on the original build box it is
`/workspace/tools/freerouting.jar`, so run `FREEROUTING=/path/to/freerouting.jar scripts/run_all_pcb.sh` (without it the
SES import fails and DRC reports ~113 unconnected pads).
`tools/make_packages.sh` builds the release zips into `dist/`.

**Part colours / 3MF (t124u):** palette in `tools/palette.py` (must match the `C_*` constants in the four `.scad`
files); `python3 tools/make_3mf.py all` rebuilds the coloured 3MF plates from the STLs (the build scripts call it).

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
   (wheel-powered) and the 0.15 V charging offset. Confirm CHRG_SENSE reads high with USB unplugged.
8. **Charge current ≈ 900 mA and temperatures**: TP4056 and cell temperature in the closed case on a full charge
   from ~3.0 V; note throttling and total charge time. Use a ≥ 1 A charger.
9. Level-bar visibility through the windows (D1's slanted tunnel may look dimmer), light bleed between tunnels; wheel
   turn/press feel and switch knob. **Wheel press with the switch off powers the MCU (Q4) and shows the bar; with it on,
   BTN_SENSE goes high on a press and low within a few ms of release; standby current unchanged (≈ 7–9 µA).**
10. Case: print one, test-fit jack plug overmold (≤ 6.8 mm), inserts, screws; check the top half drops over the wheel, switch knob and USB-C (notches/tabs, 2026-11-12) and that a USB-C cable plug seats fully.

Dock: 11. With a ≥ 45 W PD charger: green LED, 5.0–5.2 V on each slot VBUS; 5 V-only charger → red only, no slot voltage.
12. **Measure the plug height** (11.6 vs 12.5 mm, from the PCB top) and insertion depth for both radios (both
should be 6.0); set `PLUG_H` if different and adjust `PAD_T`/`STANDOFF`. 13. Insert/remove a radio
repeatedly; check alignment tolerance (~0.5 mm). 14. **Thermal**: six radios charging at once — check radio, buck and
plug temperatures; per-slot current limit trips at ~1.1–1.8 A.

Feather variant: 15. **Measure the FM module** (outline, thickness, holes, jack position/height, bottom pin length,
tallest part) and update `scripts/layout.py` before printing. 16. Verify the 0.3 mm holder-to-deck gap with a real
cell (and tape) and that the frame tabs clamp without rattle (`clamp_crush`). 17. Optional 3 mm charge LEDs behaviour; off-state drain; 200 mA charge time. 18. **Print and fit the direct-mount
controls:** switch press-fit in its groove (0.4–0.6 plates), knob travel/feel, OFF lug with a meter; wheel in the cradle (boss holes,
side walls), push travel and click with the case closed, glue joint after many pushes, top half closing over the dial.

## 9. Open decisions / TODOs
* Write firmware for the single board (MiniCore/Arduino per §4). Feather: flash and test `firmware/openald_feather` (written 2026-11-12, compile-checked only).
* Build and run §8; record measured values back into the READMEs (keep v1.0, add history notes).
* Dock: review autorouted power layout; decide plug sourcing (buy spares now); back-row visibility in the aligned grid (see t120u/t121u item).
* Optional: generic (non-JLC) placement output for other assemblers.
* Optional radio tweaks noted in reviews: RESET clamp Schottky if uploads are flaky; R3 2.4k for laptop USB charging;
  LED colour alternatives (KT-0603R C2286 basic).
* Possible separate project: smaller off-the-shelf builds (XIAO ESP32-C3 etc., §10). Victor chose to stay with v1.0 for now.
* Repo is private; Victor may make it public.
* t116u open items: measure the FM module header/jack and edit `layout.py`; check the Feather LED tunnels light up
  usefully (brightness, bleed); print one radio of each kind + one dock pocket to test the upright fit, plug insertion and plug side load; Feather length 98.71 mm approved by Victor (t120u).
* t120u/t121u open item: back-row (slots 4–6) Feather LEDs are hidden behind the front-row radios in the aligned grid
  (visible only from ~75° up; with the front pocket empty, from 60° (CHG/red) and 15° (NeoPixel) through the trench).
  The flat t121u dock did not change this: the blocker is the front radio, not the walls. Decide whether that is fine
  or add a stepped back row (≈ 60 mm higher for ~45°) or a deeper row gap; not built.
* t121u: print-test one pocket for the 25 mm guide feel and the window sill; check the shell prints cleanly upside down.
* t122u (Feather fit fixes) — **assumed, verify on real parts:** FM jack barrel Ø6.35 and 1.0 mm past the board; FM
  jack-side components ≤ 5.5 mm; nothing inside the Ø6 deck posts / Ø5.5 standoffs around the module holes; header and
  jack pins cut to ≤ 1.2 mm on the flat side; SS-12F16 plate holes 15 mm apart (M2); melted stud heads ≤ 1.0 mm tall,
  ≤ 3.4 mm across; the JST plug fits the 4.5 mm side gap; printed hole sizes (Ø6.95 jack, Ø2.2/Ø3.4 pegs, Ø1.4 studs).
  Single-board dock collar (35.9 over the lowest 27 mm) is new; check its look and the snap flex at Y 14 (thicker wall).

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
  case/                    openald_case.scad, case_params.scad (generated), case_top/case_bottom/holder_spacer STLs, case_fit_report.txt
  previews/ docs/ (schematic PDF) scripts/ (design.py = netlist/BOM source, placement.py, generators, templates/)
charging_dock/
  README.md DOCK_INTERFACE.md kicad/ fab/ case/ (STLs, floor_pads/, dock_fit_report.txt) previews/ docs/
  scripts/                 geom.py = geometry source of truth, design.py, generators, plugsearch.py/jlcq.py (part search helpers)
mi03_case/
  README.md mi03_case.scad stl/ previews/ scripts/ fit_report.txt   (MI03 radio case = envelope reference; not dock-compatible)
radio_adafruit_feather_rp2040/
  README.md make_all.sh case/ (STLs: case_top, case_bottom, deck; build_case.sh, fit report) previews/ docs/ (pin map, firmware notes, BOM, wiring diagram, wiring_schematic/) ref/ (+ models/)
  firmware/                openald_feather/ Arduino sketch (arduino-pico), build.sh, prebuilt .uf2
  scripts/                 layout.py = mechanical source of truth, feather_data.py parses ref/*.brd, check_fit.py
  archive/controls_board_pcb/  retired controls PCB (KiCad, fab, generators) - not used
```
Generated (not hand-edited) files: `.kicad_sch`, `.kicad_pcb`, footprints/symbols/3D models, `case_params.scad`,
`dock_params.scad`, everything in `fab/`, `previews/` and STLs. Edit `design.py` / `placement.py` / `geom.py` /
`layout.py` / the `.scad` sources and regenerate.

## 13. Release packages
GitHub Release **v1.0** carries one zip per subproject (built with `tools/make_packages.sh` from the tagged commit).
Zips and `dist/` are git-ignored.
