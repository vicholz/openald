# OpenALD Dock v1.0 — radio ↔ pocket interface (for every radio variant)

Status: **design values used by the dock CAD** (rewritten t116u, 2026-11-24, for the bottom-end USB-C; still v1.0).
Nothing here is hardware-validated yet. All dimensions in mm. The dockable radios are the OpenALD **single-board** and
**Feather RP2040** radios; a future variant fits the dock if its **end footprint, edge radius and USB-C position** match
this file. The radio's length does not matter (it is the height above the pocket floor).

**The MI03 radio is not dock-compatible** (Victor, 2026-11-24: "The mi03 version doesn't need to work with the dock.");
it keeps its side USB-C and is not checked against or supported by the dock.

## 1. Orientation in the dock
* The radio **stands upright on its bottom end** (the end with the USB-C), **front face toward the user**.
* The pocket walls are **50.8** (2 in) high on the back and both sides; the front wall is open above a **2.5** lip
  except for **5** wide returns at the two front corners, so the front face (single-board level bar / charge LEDs,
  Feather CHG LED and NeoPixel) stays visible.
* The right side wall is cut away **8** deep from the front above **30** over the floor, for the single-board radio's
  switch knob (2.8 proud) and wheel (0.35 proud) on its right side. Anything else on the sides must stay above 50.8 or
  within the 0.35 clearance.

## 2. End footprint
| Item | Value |
|---|---|
| Width (left side to right side) | **31.9** |
| Thickness (front face to back face) | **33.86** |
| Length (bottom end to top end) | any: single-board **89.75**, Feather **98.71** |
| Edge radius (the edges between the front/back faces and the sides) | **2.0** (pocket corner radius 2.0 + clearance) |
| Nothing may protrude from the bottom end face or the back face; side features see section 1 |

## 3. USB-C receptacle (any standard USB-C receptacle; HRO TYPE-C-31-M-12 on the single board, the Feather's own on the Feather)
| Item | Value |
|---|---|
| Centre across the width | **centred** (15.95 from either side) |
| Centre through the thickness | **6.62 behind the front face** |
| Receptacle mouth | **1.0 inside the bottom end face** |
| Connector long axis | across the width (parallel to the front face) |
| Case opening, outer | cable-plug recess **13.0 × 7.6, corner r 3.0**; its floor stops **0.55 outside the mouth** (0.45 deep), then a ~9.4 × 3.8 opening to the receptacle (same on both radios) |

The dock plug (HX TYPE C-M 16P V-SMT, LCSC C55200592, shell 8.25 × 2.40) enters through these openings.
Design insertion: plug shell tip reaches **6.0 past the receptacle mouth** with the radio resting on the pocket floor.

**USB-C mating depth (USB Type-C spec R2.x, §3.2, notes on Fig. 3-1):** the receptacle's effective shell length is
**6.20 ± 0.20**, i.e. a fully seated plug travels 6.0–6.4 past the receptacle mouth and then bottoms out (the plug shell
is 6.65 ± 0.10 long). **Design target 6.0** = the low end of the seat window: the contacts are fully engaged, and the
radio's weight stays on the printed pad, never on the plug.

| Radio | Mouth inside the bottom face | Insertion on the 4.60 pad |
|---|---|---|
| Single-board (J1 on the bottom edge since t116u) | **1.00** | **6.00** |
| Feather RP2040 (the Feather's own USB-C since t116u) | **1.00** | **6.00** |

A future variant must keep the mouth at 1.00 (± ~0.2) or the pad thickness has to change for it.

## 4. Pocket (dock side)
| Item | Value |
|---|---|
| Footprint | end footprint + **0.35 per side**: 32.6 × 34.56, corner r 2.35 |
| Walls | back + both sides **50.8** above the floor (1.5 × 45° lead-in at the top); front: 2.5 lip (1.0 × 45° lead-in) with 5 wide corner returns up to 50.8; right-side notch 8 × (50.8 − 30) at the front |
| Floor | flat printed pad (4.60 thick); hole for the plug 9.2 × 3.4 (r 1.0), long axis across the pocket |
| Plug position in the pocket | centred across the width, 6.62 behind its front edge (radio footprint frame) |

## 5. Dock build values (OpenALD Dock v1.0, from scripts/geom.py)
| Item | Value |
|---|---|
| Z stack | base 2.0 + standoffs 4.1 -> PCB Z 6.10..7.70; floor pad **4.60** thick (`PAD_T`) |
| Radio floor (pad top) | Z **12.30** above the dock bottom; deck Z 14.80; pocket walls Z 63.10 |
| Plug top | Z 19.30 (HX drawing: 11.60 above the PCB) = 7.00 above the floor -> **6.0 mm insertion** past the 1.00 receptacle mouth |
| If the plug measures taller (the drawing also shows a 12.50 overall) | every radio seats deeper by the difference (12.50: 6.90, past the 6.40 maximum seat, so the radio rests on the plug). Fix: pads thicker by the difference (`PAD_T` += measured − 11.60) and `STANDOFF` thinner by the same amount (shorter screws) |
| Layout | **3 columns × 2 rows**, 25.4 mm (1.0 in) gap between radios in X and Y, **aligned grid** (t120u; back row directly behind the front row); outer **158.5 × 112.62 × 63.1** mm (fits a 220 × 180 bed; was 216.9 × 174.79 × 26.3 with the side-lying pockets) |
