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
| Receptacle mouth (front face of the receptacle shell) | **1.60 inside the case bottom face** on every radio since 2026-11-12 (single board: J1 sticks 0.9 past its PCB edge; Feather: board moved 0.9). It is 0.10 behind the cable-plug recess floor, and the shell reaches 0.4 into the 0.5 end wall through the opening below. Until 2026-11-12: 2.50 (connector flush with the PCB edge) |
| Centreline, width direction | **centred**: 21.50 from either side face |
| Centreline, depth direction | **6.57 behind the front face** (= 26.84 in front of the back face) |
| Connector long axis | parallel to the case width |
| Case opening, outer | straight-walled cable-plug recess **13.0 × 7.6, corner r 3.0, 1.5 deep** (floor 1.5 inside the bottom face), r 1.0 fillet at the face (mouth 15.0 × 9.6), centred on the USB centreline (was a 12.8 × 7.4 → 9.8 × 4.4 filleted bowl) |
| Case opening, through the remaining 0.5 wall | 9.44 × 3.76, corner r 1.4; in the top half it continues at full width down to the case split so the top half can be lowered past the receptacle |

The dock plug (HX TYPE C-M 16P V-SMT, LCSC C55200592, shell 8.25 × 2.40) enters through these openings.
Design insertion: plug shell tip reaches **6.0 past the receptacle mouth** with the radio resting on the
pocket floor.

**USB-C mating depth (USB Type-C spec R2.x, §3.2, notes on Fig. 3-1):** the receptacle's effective shell length is
**6.20 ± 0.20**, i.e. a fully seated plug travels 6.0–6.4 past the receptacle mouth and then bottoms out (the plug
shell is 6.65 ± 0.10 long, so its base stands ~0.45 outside the mouth). Earlier versions of this file said "full mate
≈ 6.6"; that was the plug shell length, not the insertion. **Design target 6.0** = the low end of the seat window: the
contacts are fully engaged, and the radio's weight stays on the printed pad, never on the plug.

**Receptacle mouth depth per variant** (distance inside the radio's bottom face; the dock plug is fixed, so this sets
the insertion):

| Radio | Mouth inside the bottom face | Insertion on the 4.00 pad |
|---|---|---|
| Single-board (HRO TYPE-C-31-M-12, J1 0.9 past the board edge since 2026-11-12) | **1.60** | **6.00** |
| Feather RP2040 (CUI CUSB31, since commit 1452af8) | **1.60** | **6.00** |

History: on 2026-11-12 the Feather alone had the 1.60 mouth and the dock briefly used a 0.90 riser shim for Feather
pockets (commit 0ba4451). The single board was then changed to match, the shims were removed and the pad went from 3.10
to 4.00 (standoffs 5.0 → 4.1, so the outer size and the 50.8 pocket stay). A future variant must keep the mouth at 1.60
(± ~0.2) or the pad thickness has to change for it.

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
| Z stack | base 2.0 + standoffs **4.1** (was 5.0) -> PCB Z 6.10..7.70; floor pad **4.00** thick (`PAD_T`, was 3.10) |
| Radio floor (pad top) | Z 11.70 above the dock bottom (unchanged), so the pocket stays 50.8 deep and the deck stays at Z 62.5 |
| Plug top | Z 19.30 (HX drawing: 11.60 above the PCB) = 7.60 above the radio bottom face -> **6.0 mm insertion** past the 1.60 receptacle mouth on both radios |
| If the plug measures taller (the drawing also shows a 12.50 overall) | every radio seats deeper by the difference (12.50: 6.90, past the 6.40 maximum seat, so the radio stands on the plug). Fix: pads thicker by the difference (`PAD_T` += measured − 11.60) and `STANDOFF` thinner by the same amount to keep the outer size and pocket depth (needs shorter screws) (the pads are clamped under the pocket tubes, so a thicker pad alone does not fit) |
| Layout | 2 rows x 3, 25.4 mm (1.0 in) gap between radios in X and Y; outer 191.8 x 111.72 x 62.5 mm |
