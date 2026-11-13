"""OpenALD Feather RP2040 v1.0 - single source of truth for the mechanical layout.
Everything is in the CASE frame (same frame as the single-board radio's case so the dock interface can be compared
directly):  X across the case (case centre X = 19.0), Y = 0 at the single-board USB-C receptacle face (the Feather's is at FEATHER_DY = -0.9) (+Y toward the top end),
Z = 0 at the Feather bottom face (= the single-board PCB bottom face).  Outer bottom (dock) face is at Y = -2.5."""
# ---------------- dock interface (copied from the single-board case: case_params.scad + openald_case.scad) -------
WALL=2.0; CLR=0.5; PCB_W=38.0; PCB_R=3.0; EDGE_R=2.0
IN_X0, IN_X1 = -CLR, PCB_W+CLR                 # -0.5 .. 38.5   (outer -2.5 .. 40.5 = 43.0 wide)
IN_R = PCB_R+CLR                               # 3.5 inner plan radius at the USB end
OUT_R = IN_R+WALL                              # 5.5 outer plan radius at the USB end
Y_IN0 = -CLR                                   # inner wall at the USB end
Y_OUT0 = Y_IN0-WALL                            # -2.5 = dock (bottom) face
TOP_IN, TOP_T = 8.2, 1.6                       # ceiling (inside) / top skin  -> outer top face Z = 9.8
BOT_OUT = -23.61                               # outer back face Z (single board: holder 21.31 + 0.7 + 1.6 floor)
USB_X, USB_Z, USB_W, USB_H = 19.0, 1.6+3.26/2, 8.94, 3.26
DOCK_DEPTH = 50.8                              # 2 in pocket
DOCK_LINE_Y = Y_OUT0+DOCK_DEPTH                # 48.3: above this the case may differ
# ---------------- this variant ----------------
FLOOR_T = 1.2                                  # thinner floor inside (outside unchanged): holder needs the room
FLOOR_Z = BOT_OUT+FLOOR_T                      # -22.41 interior floor
J0, J1 = 50.3, 54.3                            # taper from the dock cross-section to the wider upper body
WIDEN = 1.25                                   # each side above J1  -> upper body 45.5 wide
IN_X0U, IN_X1U = IN_X0-WIDEN, IN_X1+WIDEN      # -1.75 .. 39.75
Y_IN1 = 87.5; Y_OUT1 = Y_IN1+WALL              # top end: outer 89.5 -> overall length 92.0 (single board: 92.0)
TOP_OUT_R = 3.0; TOP_IN_R = TOP_OUT_R-WALL     # smaller plan radius at the (free) top end
# 18650 holder MPD BH-18650-PC (77.7 x 20.9 x 21.31, PC pins 72.9 apart), base on the floor, cell opening up
HOLDER = dict(x0=19.0-20.9/2, x1=19.0+20.9/2, y0=3.0, y1=3.0+77.7, z0=FLOOR_Z, z1=FLOOR_Z+21.31)
HOLDER_PINS = [(19.0, 3.0+2.4, "+"), (19.0, 3.0+2.4+72.9, "-")]   # + end at the USB end
# Feather: from scripts/feather_data.py (Adafruit Eagle file).
# FEATHER_DY: the Feather (and its USB-C receptacle face) sits 0.9 mm closer to the USB/bottom face than the single
# board's receptacle (Y 0): mouth 1.6 mm inside the bottom face, 0.1 mm behind the plug-overmold recess floor (Y -1.0),
# so a cable plug seats fully (test print 52983f3: the cable barely held). Y = 0 is still the single board's mouth.
FEATHER_DY = -0.9
# frame (deck) under the Feather / boards
DECK_Z0, DECK_Z1 = -1.0, 0.0
# FM module (26.9 x 26.9, from the photo / listing; MEASURE YOURS) - components up, jack toward +Y (top end)
FM = dict(x0=IN_X0U+0.5, y1=Y_IN1-0.5, w=26.9, h=26.9, z0=0.6, t=1.6)
FM["x1"]=FM["x0"]+FM["w"]; FM["y0"]=FM["y1"]-FM["h"]
FM_HOLE_INSET = 2.5          # ESTIMATE: corner hole centres 2.5 mm in from each edge (photo not measurable)
FM_HOLE_D = 2.2              # ESTIMATE
FM_JACK_X = FM["x0"]+FM["w"]/2   # ESTIMATE: jack axis X (centre of the board edge)
FM_JACK_AXIS_H = 2.5         # jack axis above the FM board top (PJ-313 / PJ-320 class, 5 mm body)
FM_JACK_BODY_H = 5.0
FM_JACK_HOLE_D = 6.8
# ---------------- direct-mount controls (no PCB; v1.0 "direct-mount" revision, 2026-11-11) ----------------
# Thumbwheel: Mitsumi SIQ-02FVS3 bought loose, glued into a printed cradle on the frame, wires soldered to its 4 tabs.
# Datasheet: https://datasheet.lcsc.com/datasheet/pdf/7bff72617d5a3503f5ed21ab02a77dea.pdf?productCode=C2925423
#   body 10.3 (across) x 11.1 (3.85 toward the dial side + 7.25 toward the terminals), dial D14.5 x 2 thick on top,
#   overall height 4.0 (dial Z 2..4 above the seat), 2 locating bosses D1.55 at 4.5 toward the terminals, 6 apart,
#   terminals A / S(push) / C(common) / B along the rear edge, slide (push) operating force 3-6 N.
WHEEL = (IN_X1U-4.3, 62.5)   # dial centre: 4.3 mm in from the inner wall (was 4.9 on the PCB version) -> 0.6 mm more protrusion
WHEEL_R = 7.25               # dial radius
WHEEL_SEAT_Z = 1.6           # encoder body bottom (cradle top) = old PCB top, so the dial height (Z 3.6..5.6) is unchanged
WHEEL_DIAL_Z = (2.0, 4.0)    # dial above the seat
WHEEL_PUSH = 1.0             # assumed push travel (datasheet gives none); everything behind the dial clears >= 1.5 mm
# Power switch: SS-12F16 SPDT (1P2T) panel slide switch, SCREWLESS: its plate drops into a groove inside the LEFT wall
# of the bottom half (ears trapped between the outer skin and printed ribs), the frame tab above it and a top-half
# tongue in the knob channel close it in. (The right wall has no room: the wheel slot occupies it.)
# Datasheets: G-Switch SS-12F16-GXXX https://xonstorage.z8.web.core.windows.net/pdf/gswitch_ss12f16g050_apr22_xonlink.pdf
#             Light Country SS12F16 (SS-001B) https://yibeiic-shop.oss-cn-hangzhou.aliyuncs.com/media/collection/ss12d02-9bziHfGW-yoDg9ny3q.pdf
#   mounting plate 19.5-19.7 x 5.6-5.7 x 0.4-0.5 (cheap copies up to 0.6), 2x M2 holes 15 apart (not used), body 11 x
#   ~5.7 x 5 deep below the plate, 3 solder lugs 3 mm pitch, 3 mm long, knob 3 x 3, travel 3 mm,
#   knob height L above the plate: G040/"G4" = 4.0, G050 = 5.0, G060/"G6" = 6.0.
SW_L = 4.0                   # knob height above the plate (G4 default; 6.0 for G6, 5.0 for LCSC's G050)
SW_Y, SW_Z = 72.0, -4.0      # switch centre on the LEFT wall (bottom half, above the dock line, under the FM module)
SW_PLATE = (19.7, 5.7, 0.5)  # length (Y) x width (Z) x thickness used for the fit model
SW_BODY = (11.0, 5.7, 5.0)   # length (Y) x width (Z) x depth (into the case)
SW_LUG_L, SW_LUG_P = 3.0, 3.0
SW_ACT = (3.0, 3.0)          # knob Y x Z
SW_TRAVEL = 3.0
SW_SKIN = 1.2                # outer skin in front of the plate -> G4 knob 2.8 mm proud (same as the original radio)
SW_GROOVE = 0.7              # plate groove width (fits 0.4-0.6 plates; crush ribs take up the slack)
SW_RIB = 0.8                 # printed ribs behind the plate ears
SW_CRUSH = 0.25              # crush bumps on the side blocks (effective groove 0.45)
SW_PLATE_MAX = 0.6           # thickest plate allowed for (sets the back-wall position)
SW_BACK = 2.0                # solid back wall behind the switch body (lug slot open to the top)
SW_SIDE_EXT = 2.0            # side blocks run 2 mm past the groove ends
# Optional dock-visible charge LEDs: two 3 mm THT LEDs pushed into sockets in the top half, wired with inline resistors.
LED3 = [("red","CHG",30.0,74.0),("green","FULL",30.0,78.5)]
LED3_ABOVE_FLANGE = 4.6      # 3 mm LED length from the flange top to the dome tip (measure yours; typical 4.3-4.8)
# frame clamp tabs: the deck's tabs sit in notches at the parting line (bottom half below, top-half plugs above)
# (side, position along that wall, width); "L"/"R" = left/right wall at Y, "T" = top end wall at X
FRAME_TABS = [("L",25.0,6.0),("L",SW_Y,20.4),("R",25.0,6.0),("R",42.0,6.0),("R",79.0,6.0),("T",33.0,6.0)]
# battery-holder seat: floor pocket under the holder; the deck underside over it is FLAT (2026-11-12 print feedback:
# the old 0.4 mm underside relief was too shallow for supports and printed stringy) -> holder-to-deck gap 0.1 + 0.2 = 0.3 mm
HOLDER_POCKET = 0.2          # floor pocket depth under the holder
DECK_RELIEF = 0.0            # was 0.4 (underside relief over the holder); removed, kept as a knob
# engraved locating outline of the holder footprint on the deck underside (bed face): a 0.9 mm groove bridges cleanly
CELL_MARK_D = 0.4            # groove depth into the 1.0 mm deck
CELL_MARK_W = 0.9            # groove width; inner edge 0.1 mm outside the holder footprint
# case screws (M2, from the back into heat-set inserts in the top half)
SCREWS = [(1.8,1.8),(36.2,1.8),(0.0,51.8),(38.0,51.8)]
# the holder sits in its floor pocket
HOLDER["z0"] -= HOLDER_POCKET; HOLDER["z1"] -= HOLDER_POCKET
