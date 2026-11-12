# OpenALD Dock v1.0 — radio ↔ pocket interface (for every radio variant)

Status: **design values used by the dock CAD** (written 2026-11-11). Nothing here is hardware-validated yet.
All dimensions in mm. Any OpenALD radio variant (single-board, Feather RP2040, ...) fits the dock if its
**bottom 52 mm** (50.8 mm pocket depth + 1.2 mm margin) matches this envelope and connector position.

## 1. Orientation in the dock
* Radio stands **vertically, USB-C end down**, inserted 50.8 mm (2.00 in) into its pocket.
* **Front face** = the radio's top half (LED/silkscreen side, the face with the level-bar windows) faces the user.
* Thumbwheel side (single-board radio: right side when looking at the front face) is on the user's right.
* **Single-board radio level bar** (updated 2026-11-11, still v1.0): 3 windows (2.4 × 1.4) on the **centreline of the front
  face** (21.50 from either side face), window centres **77.8 / 80.6 / 83.4 above the case bottom face** = **27.0 / 29.8 / 32.6
  above the rim** (D1 lowest level … D6 full; ~24–30 above the bottom of the 3.0 lead-in chamfer). Nothing in the dock
  covers the front face above the rim. Previous position: 5 mm right of the centreline, 23.3–29.3 above the rim.

## 2. Outer envelope (bottom 52 mm of the case)
| Item | Value |
|---|---|
| Cross-section (width × depth) | **43.00 × 33.41** (width = across the front face, depth = case thickness) |
| Long-edge radius (the 4 edges running along the case length) | **2.0** |
| Bottom end face | flat, **32.0 × 29.41** contact rectangle (centred); the end is rounded into the sides with plan-corner radius **5.5** (in the width direction) and edge radius **2.0** (in the depth direction) |
| Depth split (single-board case) | front (top) half 9.80 above the PCB-bottom plane, back (bottom) half 23.61 below it |
| Nothing may protrude beyond the envelope within the bottom 52 mm, except the power-switch knob in the relief slot of §4 |

## 3. USB-C receptacle (HRO TYPE-C-31-M-12 or any std. USB-C receptacle)
| Item | Value |
|---|---|
| Receptacle mouth (front face of the receptacle shell) | **2.50 inside the case bottom face** (2.0 wall + 0.5 PCB-edge clearance, connector flush with the PCB edge) |
| Centreline, width direction | **centred**: 21.50 from either side face |
| Centreline, depth direction | **6.57 behind the front face** (= 26.84 in front of the back face) |
| Connector long axis | parallel to the case width |
| Case opening, outer | 12.8 × 7.4 pocket, corner r 3.0, **1.5 deep** (filleted), centred on the USB centreline |
| Case opening, through the remaining 0.5 wall | 9.44 × 3.76, corner r 1.4 |

The dock plug (HX TYPE C-M 16P V-SMT, LCSC C55200592, shell 8.25 × 2.40) enters through these openings.
Design insertion: plug shell tip reaches **6.0 past the receptacle mouth** with the radio resting on the
pocket floor (USB-C nominal full mate ≈ 6.6; a normal cable in this case also stops ~1 mm short).

## 4. Pocket (dock side)
| Item | Value |
|---|---|
| Depth (rim to floor) | **50.8** |
| Clearance, bottom guide zone (floor to 12 mm up) | **0.35 per side** (43.70 × 34.11, corner r 2.35) — centres the radio on the plug |
| Clearance above the guide zone | **0.60 per side** (44.20 × 34.61, corner r 2.6) |
| Lead-in at the rim | 45° chamfer, 3.0 deep |
| Switch-knob relief slot | single-board radio: SK-12E12 knob sticks out 2.8 from the right side, 22.5–28.5 above the case bottom (knob travel included), 5.05–7.55 behind the front face. The dock keeps a **4.5 wide (depth dir.) × 3.5 deep slot in the right pocket wall from the rim down to 20 mm above the floor**, centred 6.30 behind the radio's front face. A variant may use it or leave it empty |
| Floor | flat; hole for the plug 9.2 × 3.4 (r 1.0) centred on the §3 USB centreline |

## 5. Dock build values (OpenALD Dock v1.0, from scripts/geom.py)
| Item | Value |
|---|---|
| Radio floor (pad top) | Z 11.70 above the dock bottom; PCB top Z 8.60; floor pad 3.10 thick |
| Plug top | Z 20.20 (HX drawing: 11.60 above the PCB) -> **6.0 mm insertion** past the receptacle mouth |
| If the plug measures taller (the drawing also shows a 12.50 overall) | it seats ~0.9 mm deeper (6.9 > 6.6 full mate): the radio then rests on the plug instead of the pad; if that matters, print the pads thicker (`PAD_T` in geom.py) |
| Layout | 2 rows x 3, 25.4 mm (1.0 in) gap between radios in X and Y; outer 191.8 x 111.72 x 62.5 mm |
