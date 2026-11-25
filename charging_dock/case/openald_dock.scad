// OpenALD Dock v1.0 - 6-slot charging dock case.
// t116u (2026-11-24): 3 columns x 2 rows, radios STAND UPRIGHT on their bottom-end USB-C (front face toward you) in
// 50.8 mm deep pockets; the back row is offset by half a pitch so each back-row radio shows between two front-row
// radios. The dockable OpenALD radios (single-board, Feather; NOT the MI03) share the 31.9 x 33.86 end footprint and
// the USB-C position (centred across the width, 6.62 behind the front face, mouth 1.0 inside the bottom end face).
// The pocket front wall is open above the deck except for 5 mm corner returns, so the front faces (and the Feather's
// CHG / NeoPixel LEDs) stay visible.
// Dock frame: X right, Y toward the back, Z up, origin = front-left-bottom corner. All mm.
// Parts: part="base" | "shell" (print upright, skirt down) | "pad" (6x, one per pocket; pad_index 0-5) | "pads" (all 6)
//        "assembly" | "exploded" | "print" | "section" | raw parts for the fit check: shell_raw, base_raw, pads_raw, radios, plugs
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
// ---------------------------------------------------------------- top shell
module pocket_cavity(i) {
    x0 = radios[i][0]; y0 = radios[i][1];
    translate([0, 0, FLOOR_Z - 0.01]) rfoot(i, CLR_GUIDE, FIN_Z - FLOOR_Z + 1);
    // lead-in chamfer on the fin tops (back and end walls)
    hull() { translate([0, 0, FIN_Z - CHAMFER]) rfoot(i, CLR_GUIDE, 0.01); translate([0, 0, FIN_Z]) rfoot(i, CLR_GUIDE + CHAMFER, 0.01);
             translate([0, 0, FIN_Z + 1]) rfoot(i, CLR_GUIDE + CHAMFER, 0.01); }
    // lead-in chamfer on the low front wall (in the front window only)
    intersection() {
        hull() { translate([0, 0, TOP_Z - 1.0]) rfoot(i, CLR_GUIDE, 0.01); translate([0, 0, TOP_Z]) rfoot(i, CLR_GUIDE + 1.0, 0.01);
                 translate([0, 0, TOP_Z + 0.5]) rfoot(i, CLR_GUIDE + 1.0, 0.01); }
        translate([x0 + FRONT_RETURN + 1, y0 - PW - 1, 0]) cube([RL - 2*FRONT_RETURN - 2, PW + 1 + 3, 100]);
    }
}
module fins(i) {      // pocket walls above the deck: back, both sides and 5 mm front corner returns
    x0 = radios[i][0]; y0 = radios[i][1];
    difference() {
        translate([0, 0, TOP_Z - 0.01]) rfoot(i, PW, FIN_Z - TOP_Z + 0.01);
        // front window
        translate([x0 + FRONT_RETURN, y0 - PW - 1, TOP_Z]) cube([RL - 2*FRONT_RETURN, PW + 1 + EDGE_R, FIN_Z]);
        // right-wall notch for the single-board radio's switch knob and wheel (open at the top and the front)
        translate([x0 + RL - 1, y0 - PW - 1, FLOOR_Z + SIDE_NOTCH_Z]) cube([PW + 2, PW + 1 + SIDE_NOTCH_D, FIN_Z]);
    }
}
module shell_raw() {
    difference() {
        union() {
            // skirt + deck
            difference() {
                translate([0, 0, BASE_T + SKIRT_GAP]) rrect(0, 0, OUT_W, OUT_D, SHELL_R, TOP_Z - BASE_T - SKIRT_GAP);
                translate([0, 0, BASE_T]) rrect(WALL, WALL, OUT_W - 2*WALL, OUT_D - 2*WALL, SHELL_R - WALL, TOP_Z - BASE_T - DECK_T);
            }
            // pocket walls from just above the pad to the deck, and the fins above it
            for (i = [0:5]) { translate([0, 0, FLOOR_Z + TUBE_GAP]) rfoot(i, PW, TOP_Z - FLOOR_Z - TUBE_GAP); fins(i); }
            // screw bosses (clamp the PCB onto the base standoffs)
            for (h = holes) translate([h[0], h[1], PCB_Z1]) cylinder(d = BOSS_D, h = TOP_Z - PCB_Z1 - 0.5);
            // status-LED light pipe
            translate([led_pipe[0], led_pipe[1], PIPE_Z0]) cylinder(d = PIPE_OD, h = TOP_Z - PIPE_Z0 - 0.5);
            // raised housings over parts taller than the room under the deck
            for (t = tall) translate([0, 0, TOP_Z - DECK_T]) rbox_c(t[0], t[1], t[2] + 2*(HOUSING_CLR + HOUSING_T), t[3] + 2*(HOUSING_CLR + HOUSING_T), 1.5,
                                                                   PCB_Z1 + t[4] + HOUSING_CLR + HOUSING_T - (TOP_Z - DECK_T));
        }
        for (i = [0:5]) pocket_cavity(i);
        for (h = holes) translate([h[0], h[1], PCB_Z1 - 0.01]) cylinder(d = INSERT_D, h = INSERT_L);
        translate([led_pipe[0], led_pipe[1], PIPE_Z0 - 1]) cylinder(d = PIPE_ID, h = 50);
        for (t = tall) translate([0, 0, PCB_Z1 - 1]) rbox_c(t[0], t[1], t[2] + 2*HOUSING_CLR, t[3] + 2*HOUSING_CLR, 1.0, t[4] + HOUSING_CLR + 1);
        // rear USB-C input opening (fits any USB-C cable overmold up to 12.4 x 6.5)
        translate([usb_in[0], OUT_D + 0.1, usb_in_z]) rotate([90, 0, 0]) translate([-6.5, -3.8, 0]) linear_extrude(WALL + 1) offset(r = 3) offset(delta = -3) square([13, 7.6]);
        // deck vents over the two buck converters (front-row gaps; clear of the 470 uF housings in front of them)
        for (b = bucks) for (dx = [-6, -2, 2, 6])
            translate([b[0] + dx - 1.0, b[1] - 3, TOP_Z - DECK_T - 1]) cube([2.0, 12, DECK_T + 2]);
        // side skirt vents (low, near the PCB), clear of the Y-channel screws
        for (y = [20:8:44]) for (x = [-1, OUT_W - WALL - 1]) translate([x, y, BASE_T + 3]) cube([WALL + 2, 3, 7]);
        for (y = [60:8:100]) for (x = [-1, OUT_W - WALL - 1]) translate([x, y, BASE_T + 3]) cube([WALL + 2, 3, 7]);
        // engraved labels on the deck (Y-channel between the rows)
        translate([radios[3][0] + RL + PW + 4, ychan_y + 1.2, TOP_Z - 0.6])
            linear_extrude(1) text("OpenALD Dock v1.0", size = 4.2, font = "Liberation Sans:style=Bold", halign = "left");
        translate([radios[3][0] + RL + PW + 4, ychan_y - 6.2, TOP_Z - 0.6])
            linear_extrude(1) text("USB-C PD 45 W+", size = 4.2, font = "Liberation Sans:style=Bold", halign = "left");
        for (i = [0:5]) translate([radios[i][0] + RL + PW + 3.0, radios[i][1] + 2.0, TOP_Z - 0.6])
            linear_extrude(1) text(str(i + 1), size = 4.0, font = "Liberation Sans:style=Bold", halign = "left");
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
        // finger notch to lift the pad out (front edge, under the low front wall)
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
if (part == "shell")  translate([0, 0, -BASE_T - SKIRT_GAP]) shell_raw();     // print upright, skirt on the bed (deck bridges <= ~30 mm between walls / bosses)
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
    color("gainsboro") import("/tmp/dock_base_raw.stl"); pcb();
    color("silver") import("/tmp/dock_plugs.stl");
    color("dimgray") import("/tmp/dock_pads_raw.stl");
    color("lightsteelblue") import("/tmp/dock_shell_raw.stl");
    color("salmon") import("/tmp/dock_docked_single_board.stl");  // slot 1 (front row, left)
    color("gold") import("/tmp/dock_docked_feather.stl");         // slot 4 (back row, left)
}
if (part == "assembly") assembly_parts();
if (part == "section") intersection() { assembly_parts(); translate([-1, -1, -1]) cube([plugs[0][0], OUT_D + 2, 200]); }   // render with --render
if (part == "exploded") {
    color("gainsboro") import("/tmp/dock_base_raw.stl"); pcb();
    color("silver") import("/tmp/dock_plugs.stl");
    color("dimgray") translate([0, 0, 15]) import("/tmp/dock_pads_raw.stl");
    color("lightsteelblue") translate([0, 0, 35]) import("/tmp/dock_shell_raw.stl");
}
if (part == "print") {
    translate([0, 0, -BASE_T - SKIRT_GAP]) shell_raw();
    translate([0, OUT_D + 15, 0]) base_raw();
    for (i = [0:5]) translate([OUT_W + 15 + (i % 3) * 45 - radios[i][0], floor(i / 3) * 45 + radios[i][1] + RT + PAD_OFF, PCB_Z1 + PAD_T]) rotate([180, 0, 0]) pad_raw(i);
}
