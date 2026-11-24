# OpenALD Dock v1.0 — radio ↔ pocket interface (for every radio variant)

Status: **design values used by the dock CAD** (rewritten 2026-11-24 for the unified envelope; still v1.0). Nothing here
is hardware-validated yet. All dimensions in mm. Any OpenALD radio (MI03 18650 case, single-board, Feather RP2040, ...)
fits the dock if its **outside footprint, edge radius and USB-C position** match this file. The width of the radio does
not matter (it is the height above the pocket floor when docked).

## 1. Orientation in the dock
* The radio **lies on its USB-C long side** in a shallow tray (until 2026-11-24 radios stood USB-C-end down 50.8 deep).
* **Front face** (LCD / LEDs / buttons) faces the user; the **top end is on the left**, the jack end on the right.
* The pocket's back wall and both end walls are **14** high; the front wall is only **6** high, so the whole front face
  (MI03 LCD, single-board level bar, Feather LED windows) stays visible. Everything on the radio's top long side
  (power-switch knob, thumbwheel) points up and is free.

## 2. Outer envelope
| Item | Value |
|---|---|
| Length (top end to jack end) | **89.75** |
| Thickness (front face to back face) | **34.83** |
| Width (USB-C side to the opposite side) | any: MI03 **27.5**, single-board **27.5**, Feather **32.9** |
| Edge radius (the edges between the front/back faces and the sides/ends) | **2.0** (pocket corner radius 2.0 + clearance) |
| Plan-corner radius (in the width × length plane) | 5.0 (only rounds the radio's ends near the floor; not used by the pocket) |
| Nothing may protrude from the USB-C side face, the back face or the two end faces; the front face may carry features up to ~1 proud **more than 6 above the USB-C side face** (MI03 plungers sit 13.75 up) |

## 3. USB-C receptacle (any standard USB-C receptacle; MI03 stock, HRO TYPE-C-31-M-12, USB-C breakout on the Feather)
| Item | Value |
|---|---|
| Centre along the length | **30.3 from the top outer end** |
| Centre through the thickness | **7.55 behind the front face** |
| Receptacle mouth | **1.0 inside the USB-C side face** (all three radios) |
| Connector long axis | along the radio length |
| Case opening, outer | cable-plug recess **13.0 × 7.6, corner r 3.0**; its floor stops **0.55 outside the mouth** (0.45 deep), then a ~9.4 × 3.8 opening to the receptacle (MI03 geometry, copied by the other two cases) |

The dock plug (HX TYPE C-M 16P V-SMT, LCSC C55200592, shell 8.25 × 2.40) enters through these openings.
Design insertion: plug shell tip reaches **6.0 past the receptacle mouth** with the radio resting on the pocket floor.

**USB-C mating depth (USB Type-C spec R2.x, §3.2, notes on Fig. 3-1):** the receptacle's effective shell length is
**6.20 ± 0.20**, i.e. a fully seated plug travels 6.0–6.4 past the receptacle mouth and then bottoms out (the plug shell
is 6.65 ± 0.10 long). **Design target 6.0** = the low end of the seat window: the contacts are fully engaged, and the
radio's weight stays on the printed pad, never on the plug.

| Radio | Mouth inside the side face | Insertion on the 4.60 pad |
|---|---|---|
| MI03 (stock board, 18650 case) | **1.00** | **6.00** |
| Single-board (J1 on the long edge since 2026-11-24) | **1.00** | **6.00** |
| Feather RP2040 (USB-C breakout, since 2026-11-24) | **1.00** | **6.00** |

A future variant must keep the mouth at 1.00 (± ~0.2) or the pad thickness has to change for it.

## 4. Pocket (dock side)
| Item | Value |
|---|---|
| Footprint | radio footprint + **0.35 per side**: 90.45 × 35.53, corner r 2.35 |
| Walls | back + both ends **14** above the floor (1.5 × 45° lead-in at the top); front **6** (deck height, 1.0 × 45° lead-in) |
| Floor | flat printed pad (4.60 thick); hole for the plug 9.2 × 3.4 (r 1.0), long axis along the pocket |
| Plug position in the pocket | 30.3 from the pocket's left end, 7.55 behind its front edge (radio footprint frame) |

## 5. Dock build values (OpenALD Dock v1.0, from scripts/geom.py)
| Item | Value |
|---|---|
| Z stack | base 2.0 + standoffs 4.1 -> PCB Z 6.10..7.70; floor pad **4.60** thick (`PAD_T`, was 4.00) |
| Radio floor (pad top) | Z **12.30** above the dock bottom; deck Z 18.30; fins (pocket back/end walls) Z 26.30 |
| Plug top | Z 19.30 (HX drawing: 11.60 above the PCB) = 7.00 above the floor -> **6.0 mm insertion** past the 1.00 receptacle mouth |
| If the plug measures taller (the drawing also shows a 12.50 overall) | every radio seats deeper by the difference (12.50: 6.90, past the 6.40 maximum seat, so the radio rests on the plug). Fix: pads thicker by the difference (`PAD_T` += measured − 11.60) and `STANDOFF` thinner by the same amount (shorter screws) |
| Layout | **2 columns × 3 rows**, 25.4 mm (1.0 in) gap between radios in X and Y; outer **216.9 × 174.79 × 26.3** mm (was 191.8 × 111.72 × 62.5) |
