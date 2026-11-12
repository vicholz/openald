"""OpenALD Feather RP2040 v1.0 - single source of truth for the mechanical layout.
Everything is in the CASE frame (same frame as the single-board radio's case so the dock interface can be compared
directly):  X across the case (case centre X = 19.0), Y = 0 at the USB-C receptacle face (+Y toward the top end),
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
# Feather: from scripts/feather_data.py (Adafruit Eagle file)
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
# controls board (KiCad), in case frame; Z 0..1.6 like the single-board PCB
CB_Z0, CB_T = 0.0, 1.6
CB_OUTLINE = [(26.05,54.9),(39.25,54.9),(39.25,86.0),(38.25,87.0),(26.05,87.0)]   # polygon, CCW
WHEEL = (IN_X1U-4.9, 62.5)   # SIQ-02FVS3 wheel centre (same 4.9 mm in from the inner wall as the single board)
SWITCH_PIN_X = IN_X1U-3.0    # SK-12E12 pin line (single board: 35.5 = inner wall 38.5 - 3.0)
SWITCH_Y = 76.7              # centre pin
LEDS = [("D1",28.2,72.9,"red","CHG"),("D2",28.2,75.9,"green","FULL")]
PAD_X, PAD_Y0, PAD_P = 31.6, 71.35, 1.8
PADS = ["ENCA","ENCB","ENCSW","EN","GND","VBUS","STAT","VBAT","BSNS"]   # pad 1 at PAD_Y0, +PAD_P each
PASSIVES = {"R3":(28.2,78.6),"R4":(28.2,80.3),"R1":(28.2,82.2),"R2":(28.2,83.9),"C1":(28.2,85.6)}
PASSIVE_ROT = {"R1":180}   # VBAT pad toward the wire pads
CB_HOLES = [(27.4,70.1),(37.3,85.6)]   # NPTH 2.1 mm for printed locating pegs
CB_HOLE_D = 2.1
# case screws (M2, from the back into heat-set inserts in the top half)
SCREWS = [(1.8,1.8),(36.2,1.8),(0.0,51.8),(38.0,51.8)]
