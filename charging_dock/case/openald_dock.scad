// OpenALD Dock v1.0 - 6-slot charging dock case.
// t122u (2026-11-24): pockets 35.9 wide (wider Feather case; the single-board case has a 35.9 dock collar) -> 170.5 wide.
// t121u (2026-11-24): FLAT dock. A closed box 158.5 x 112.62 x 37.3 with six pockets RECESSED 25 mm into its flat top,
// aligned 3 x 2 grid; radios STAND UPRIGHT on their bottom-end USB-C (front face toward you). (t116u/t120u had 50.8 mm
// pocket walls on a low deck.) The dockable OpenALD radios (single-board, Feather; NOT the MI03) share the 35.9 x 33.86
// end footprint and the USB-C position (centred across the width, 6.62 behind the front face, mouth 1.0 inside the
// bottom end face). Each pocket's front wall has a 20 mm sight window down to 2 mm above the floor so the Feather's
// CHG / red / NeoPixel LEDs stay visible: front row straight out through the dock front, back row through a sloped
// trench in the top between the rows.
// Dock frame: X right, Y toward the back, Z up, origin = front-left-bottom corner. All mm.
// Parts: part="base" | "shell" (print upside down, flat top on the bed) | "pad" (6x, one per pocket; pad_index 0-5) | "pads" (all 6)
//        "assembly" | "exploded" | "print" | "section" | raw parts for the fit check: shell_raw, base_raw, pads_raw, radios, plugs
// t124u part colours (dock = purples; same hex in tools/palette.py and the coloured 3MF)
C_SHELL = "#7B4FB8";    // top shell                    purple
C_BASE  = "#C9B6E8";    // base                         lavender
C_PADS  = "#3B2360";    // floor pads                   dark purple
C_RADIO_SB = "#2E6FD8"; // docked single-board radio (its front-shell blue)
C_RADIO_FE = "#2FA84F"; // docked Feather radio (its front-shell green)
include <dock_params.scad>
part = "assembly";
pad_index = 0;
$fn = 48;
SHELL_R = 4.0;           // outer plan corner radius
DECK_T = 2.0;
SKIRT_GAP = 0.3;         // skirt bottom clears the base plate (the PCB clamp between bosses and standoffs carries the load)
BOSS_D = 8.0; INSERT_D = 4.0; INSERT_L = 6.5;       // M3 heat-set insert (OD ~4.6, L 4-5.7)
STANDOFF_D = 8.0; SCREW_D = 3.4; HEAD_D = 6.2; HEAD_L = 3.0;
PAD_OFF = 2.4;           // floor pad = radio footprint + 2.4 (pocket wall overlaps it -> pad held down)
TUBE_GAP = 0.2;          // pocket wall bottom above the pad top
PIPE_ID = 4.0; PIPE_OD = 7.0; PIPE_Z0 = PCB_Z1 + 1.0;
HOUSING_T = 1.2; HOUSING_CLR = 0.5;
PLUG_HOLE = [9.2, 3.4]; PLUG_BORE = [10.6, 5.0, 1.8];
PW = CLR_GUIDE + POCKET_WALL;
module rrect(x0, y0, w, d, r, h) { translate([x0, y0, 0]) linear_extrude(h) offset(r = r) offset(delta = -r) square([w, d]); }
module rbox_c(cx, cy, w, d, r, h) { rrect(cx - w/2, cy - d/2, w, d, r, h); }
// radio footprint grown by o (corner radius = radio edge radius + o)
module rfoot(i, o, h) { rrect(radios[i][0] - o, radios[i][1] - o, RL + 2*o, RT + 2*o, EDGE_R + o, h); }
// ---------------------------------------------------------------- top shell (t121u: flat box, recessed pockets)
TR_RUN = (TOP_Z - FLOOR_Z - WIN_Z) / tan(TRENCH_ANG);   // back-row trench: horizontal run of its sloped floor
WIN_WALL = 1.6;          // window / trench side walls and floor
SOLID_Z0 = FLOOR_Z + TUBE_GAP;                          // window blocks and trench walls stay above the floor pads
module pocket_cavity(i) {
    translate([0, 0, FLOOR_Z - 0.01]) rfoot(i, CLR_GUIDE, TOP_Z - FLOOR_Z + 1);
    // lead-in chamfer on the pocket rim
    hull() { translate([0, 0, TOP_Z - CHAMFER]) rfoot(i, CLR_GUIDE, 0.01); translate([0, 0, TOP_Z]) rfoot(i, CLR_GUIDE + CHAMFER, 0.01);
             translate([0, 0, TOP_Z + 1]) rfoot(i, CLR_GUIDE + CHAMFER, 0.01); }
}
// sight window in the pocket's front wall (YZ profile extruded along X, width w centred on the pocket)
module xext(cx, w, pts) { translate([cx - w/2, 0, 0]) rotate([90, 0, 90]) linear_extrude(w) polygon(pts); }
module win_solid(i) {    // material around the window / trench (inside the hollow shell)
    cx = radios[i][0] + RL/2; yf = radios[i][1] - CLR_GUIDE;
    if (i < 3) xext(cx, WIN_W + 2*WIN_WALL, [[WALL - 0.01, SOLID_Z0], [yf + 0.01, SOLID_Z0], [yf + 0.01, TOP_Z - 0.01], [WALL - 0.01, TOP_Z - 0.01]]);
    else intersection() {
        xext(cx, WIN_W + 2*WIN_WALL, [[yf + 0.01, SOLID_Z0], [yf + 0.01, TOP_Z - 0.01],
                                      [yf - TR_RUN - 3.5, TOP_Z - 0.01], [yf - TR_RUN - 3.5, TOP_Z - 2.0], [yf, FLOOR_Z + WIN_Z - 2.6]]);
        translate([0, 0, SOLID_Z0]) cube([OUT_W, OUT_D, 100]);
    }
}
module win_cut(i) {
    cx = radios[i][0] + RL/2; yf = radios[i][1] - CLR_GUIDE; zs = FLOOR_Z + WIN_Z;
    if (i < 3) xext(cx, WIN_W, [[-1, zs], [yf + 1, zs], [yf + 1, TOP_Z + 1], [-1, TOP_Z + 1]]);
    else xext(cx, WIN_W, [[yf + 1, zs], [yf + 1, TOP_Z + 1], [yf - TR_RUN - 1/tan(TRENCH_ANG), TOP_Z + 1], [yf, zs]]);
}
module shell_raw() {
    difference() {
        union() {
            // skirt + flat top
            difference() {
                translate([0, 0, BASE_T + SKIRT_GAP]) rrect(0, 0, OUT_W, OUT_D, SHELL_R, TOP_Z - BASE_T - SKIRT_GAP);
                translate([0, 0, BASE_T]) rrect(WALL, WALL, OUT_W - 2*WALL, OUT_D - 2*WALL, SHELL_R - WALL, TOP_Z - BASE_T - DECK_T);
            }
            // pocket walls from just above the pad up to the top
            for (i = [0:5]) translate([0, 0, FLOOR_Z + TUBE_GAP]) rfoot(i, PW, TOP_Z - FLOOR_Z - TUBE_GAP);
            for (i = [0:5]) win_solid(i);
            // screw bosses (clamp the PCB onto the base standoffs)
            for (h = holes) translate([h[0], h[1], PCB_Z1]) cylinder(d = BOSS_D, h = TOP_Z - PCB_Z1 - 0.5);
            // status-LED light pipe
            translate([led_pipe[0], led_pipe[1], PIPE_Z0]) cylinder(d = PIPE_OD, h = TOP_Z - PIPE_Z0 - 0.5);
        }
        for (i = [0:5]) { pocket_cavity(i); win_cut(i); }
        for (h = holes) translate([h[0], h[1], PCB_Z1 - 0.01]) cylinder(d = INSERT_D, h = INSERT_L);
        translate([led_pipe[0], led_pipe[1], PIPE_Z0 - 1]) cylinder(d = PIPE_ID, h = 50);
        // clearance around the tallest PCB parts (the room under the top is 27 mm; no raised housings needed any more)
        for (t = tall) translate([0, 0, PCB_Z1 - 1]) rbox_c(t[0], t[1], t[2] + 2*HOUSING_CLR, t[3] + 2*HOUSING_CLR, 1.0, t[4] + HOUSING_CLR + 1);
        // rear USB-C input opening (fits any USB-C cable overmold up to 12.4 x 6.5)
        translate([usb_in[0], OUT_D + 0.1, usb_in_z]) rotate([90, 0, 0]) translate([-6.5, -3.8, 0]) linear_extrude(WALL + 1) offset(r = 3) offset(delta = -3) square([13, 7.6]);
        // top vents over the two buck converters (front-row gaps)
        for (b = bucks) for (dx = [-6, -2, 2, 6])
            translate([b[0] + dx - 1.0, b[1] - 3, TOP_Z - DECK_T - 1]) cube([2.0, 12, DECK_T + 2]);
        // side skirt vents (low, near the PCB), clear of the Y-channel screws
        for (y = [20:8:44]) for (x = [-1, OUT_W - WALL - 1]) translate([x, y, BASE_T + 3]) cube([WALL + 2, 3, 7]);
        for (y = [60:8:100]) for (x = [-1, OUT_W - WALL - 1]) translate([x, y, BASE_T + 3]) cube([WALL + 2, 3, 7]);
        // engraved labels on the top: title in the rear strip, slot numbers behind each pocket
        translate([(radios[3][0] + radios[4][0] + RL) / 2, OUT_D - WALL - 6.6, TOP_Z - 0.6])
            linear_extrude(1) text("OpenALD Dock v1.0", size = 3.4, font = "Liberation Sans:style=Bold", halign = "center");
        translate([(radios[4][0] + radios[5][0] + RL) / 2, OUT_D - WALL - 6.6, TOP_Z - 0.6])
            linear_extrude(1) text("USB-C PD 45 W+", size = 3.4, font = "Liberation Sans:style=Bold", halign = "center");
        for (i = [0:5]) translate([radios[i][0] + RL/2 + (i < 3 ? 13 : 0), radios[i][1] + RT + PW + 1.5, TOP_Z - 0.6])
            linear_extrude(1) text(str(i + 1), size = 4.0, font = "Liberation Sans:style=Bold", halign = "center");
    }
}
// ---------------------------------------------------------------- base tray
module base_raw() {
    difference() {
        union() {
            rrect(0, 0, OUT_W, OUT_D, SHELL_R, BASE_T);
            // locating rim inside the skirt
            difference() {
                rrect(WALL + 0.25, WALL + 0.25, OUT_W - 2*WALL - 0.5, OUT_D - 2*WALL - 0.5, SHELL_R - WALL, BASE_T + 3);
                translate([0, 0, -1]) rrect(WALL + 1.75, WALL + 1.75, OUT_W - 2*WALL - 3.5, OUT_D - 2*WALL - 3.5, 1, BASE_T + 5);
            }
            for (h = holes) translate([h[0], h[1], 0]) cylinder(d = STANDOFF_D, h = PCB_Z0);
            // plug support pillars (insertion force 5-20 N per slot) + pillars under the floor-pad pegs
            for (p = plugs) rbox_c(p[0], p[1], 12, 6, 1, PCB_Z0);
            for (g = pegs) translate([g[0], g[1], 0]) cylinder(d = 6, h = PCB_Z0);
        }
        for (h = holes) { translate([h[0], h[1], -1]) cylinder(d = SCREW_D, h = PCB_Z0 + 2);
                          translate([h[0], h[1], -1]) cylinder(d = HEAD_D, h = HEAD_L + 1); }
        // vents under the buck converters
        for (b = bucks) for (dx = [-6, -2, 2, 6]) translate([b[0] + dx - 1.0, b[1] - 8, -1]) cube([2.0, 16, BASE_T + 2]);
        // rubber-foot recesses (10 mm bumpers)
        for (x = [12, OUT_W - 12]) for (y = [10, OUT_D - 10]) translate([x, y, -0.01]) cylinder(d = 10.5, h = 1.0);
    }
}
// ---------------------------------------------------------------- floor pads (one per pocket)
module pad_raw(i) {
    p = plugs[i];
    difference() {
        union() {
            translate([0, 0, PCB_Z1]) rfoot(i, PAD_OFF, PAD_T);
            for (g = [pegs[2*i], pegs[2*i + 1]]) translate([g[0], g[1], PCB_Z1 - 1.4]) cylinder(d = 2.0, h = 1.5);
        }
        translate([0, 0, PCB_Z1 - 1]) rbox_c(p[0], p[1], PLUG_HOLE[0], PLUG_HOLE[1], 1.0, PAD_T + 2);
        translate([0, 0, PCB_Z1 - 1]) rbox_c(p[0], p[1], PLUG_BORE[0], PLUG_BORE[1], 1.0, PLUG_BORE[2] + 1);
        // finger notch to lift the pad out (front edge, under the sight window)
        translate([radios[i][0] + RL/2, radios[i][1] - PAD_OFF, PCB_Z1 + PAD_T]) scale([1, 0.6, 1]) sphere(d = 8);
    }
}
// ---------------------------------------------------------------- fit-check / preview helpers
// generic docked radio (preview only; the fit check uses the real case STLs of all three radios):
// width w, 13.0 x 7.6 r3 cable-plug recess 0.45 deep, 9.4 x 3.8 opening to the receptacle mouth (MOUTH_UP), receptacle cavity
module radio_env(i, w = 89.75) {
    p = plugs[i];
    difference() {
        translate([0, 0, FLOOR_Z]) rfoot(i, 0, w);
        translate([0, 0, FLOOR_Z - 1]) rbox_c(p[0], p[1], 13.0, 7.6, 3.0, 0.45 + 1);
        translate([0, 0, FLOOR_Z - 1]) rbox_c(p[0], p[1], 9.4, 3.8, 1.4, MOUTH_UP + 1);
        translate([0, 0, FLOOR_Z]) rbox_c(p[0], p[1], 8.40, 2.60, 1.25, MOUTH_UP + 7.0);
    }
}
module plug(i) { p = plugs[i];
    translate([0, 0, PCB_Z1]) rbox_c(p[0], p[1], 7.96, 3.48, 0.3, 1.8);
    translate([0, 0, PCB_Z1]) rbox_c(p[0], p[1], 8.25, 2.40, 1.15, PLUG_H); }
module pcb() { color("darkgreen") translate([PCB_X0, PCB_Y0, PCB_Z0]) cube([PCB_X1 - PCB_X0, PCB_Y1 - PCB_Y0, PCB_T]); }
if (part == "shell")  translate([0, OUT_D, TOP_Z]) rotate([180, 0, 0]) shell_raw();   // print upside down, flat top on the bed (only bridges: 20 mm window sills)
if (part == "base")   base_raw();
if (part == "pad")    translate([0, 0, PCB_Z1 + PAD_T]) rotate([180, 0, 0]) pad_raw(pad_index);   // print top-down
if (part == "pads")   for (i = [0:5]) translate([(i % 3) * 45 - radios[i][0], floor(i / 3) * 45 + radios[i][1] + RT + PAD_OFF, PCB_Z1 + PAD_T]) rotate([180, 0, 0]) pad_raw(i);
if (part == "shell_raw") shell_raw();
if (part == "base_raw")  base_raw();
if (part == "pads_raw")  for (i = [0:5]) pad_raw(i);
if (part == "radios")    for (i = [0:5]) radio_env(i);
if (part == "plugs")     for (i = [0:5]) plug(i);
// previews use the STLs exported by build_case.sh / check_dock_fit.py (OpenCSG cannot preview the full CSG tree)
module assembly_parts() {
    color(C_BASE) import("/tmp/dock_base_raw.stl"); pcb();
    color("silver") import("/tmp/dock_plugs.stl");
    color(C_PADS) import("/tmp/dock_pads_raw.stl");
    color(C_SHELL) import("/tmp/dock_shell_raw.stl");
    color(C_RADIO_SB) import("/tmp/dock_docked_single_board.stl");  // slot 1 (front row, left)
    color(C_RADIO_FE) import("/tmp/dock_docked_feather.stl");         // slot 4 (back row, left)
}
if (part == "assembly") assembly_parts();
if (part == "section") intersection() { assembly_parts(); translate([-1, -1, -1]) cube([plugs[0][0], OUT_D + 2, 200]); }   // render with --render
if (part == "exploded") {
    color(C_BASE) import("/tmp/dock_base_raw.stl"); pcb();
    color("silver") import("/tmp/dock_plugs.stl");
    color(C_PADS) translate([0, 0, 15]) import("/tmp/dock_pads_raw.stl");
    color(C_SHELL) translate([0, 0, 30]) import("/tmp/dock_shell_raw.stl");
}
if (part == "print") {   // t124u: coloured preview from the exported STLs (build_case.sh renders it without --render)
    color(C_SHELL) translate([0, OUT_D, TOP_Z]) rotate([180, 0, 0]) import("/tmp/dock_shell_raw.stl");
    color(C_BASE) translate([0, OUT_D + 15, 0]) import("/tmp/dock_base_raw.stl");
    color(C_PADS) translate([OUT_W + 15, 0, 0]) import("dock_floor_pads_x6.stl");
}
