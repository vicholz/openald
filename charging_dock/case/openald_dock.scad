// OpenALD Dock v1.0 - 6-slot charging dock case (2 rows x 3, radios stand USB-C down, 2.00 in deep pockets)
// Dock frame: X right, Y toward the back, Z up, origin = front-left-bottom corner. All mm.
// Parts: part="base" | "shell" (print deck-down) | "pad" (6x, one per pocket; pad_index 0-5) | "pads" (all 6)
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
PAD_OFF = 2.4;           // floor pad = radio footprint + 2.4 (tube wall overlaps it -> pad held down)
TUBE_GAP = 0.2;          // tube bottom above the pad top
PIPE_ID = 4.0; PIPE_OD = 7.0; PIPE_Z0 = PCB_Z1 + 1.0;
KNOB_W = 4.5; KNOB_D = 3.5; KNOB_Y = 6.30; KNOB_Z = 20.0;   // switch-knob relief slot (right wall)
PLUG_HOLE = [9.2, 3.4]; PLUG_BORE = [10.6, 5.0, 1.8];
module rrect(x0, y0, w, d, r, h) { translate([x0, y0, 0]) linear_extrude(h) offset(r = r) offset(delta = -r) square([w, d]); }
module rbox_c(cx, cy, w, d, r, h) { rrect(cx - w/2, cy - d/2, w, d, r, h); }
// radio footprint grown by o (corner radius 2 + o)
module rfoot(i, o, h) { rrect(radios[i][0] - o, radios[i][1] - o, RW + 2*o, RD + 2*o, 2.0 + o, h); }
// ---------------------------------------------------------------- top shell
module pocket_cavity(i) {
    z0 = FLOOR_Z - 0.01;
    translate([0, 0, z0]) rfoot(i, CLR_GUIDE, GUIDE_H + 0.01);                                       // guide zone
    hull() { translate([0, 0, FLOOR_Z + GUIDE_H]) rfoot(i, CLR_GUIDE, 0.01);
             translate([0, 0, FLOOR_Z + GUIDE_H + (CLR_UPPER - CLR_GUIDE)]) rfoot(i, CLR_UPPER, 0.01); }  // 45 deg step
    translate([0, 0, FLOOR_Z + GUIDE_H]) rfoot(i, CLR_UPPER, TOP_Z - FLOOR_Z - GUIDE_H + 1);
    hull() { translate([0, 0, TOP_Z - CHAMFER]) rfoot(i, CLR_UPPER, 0.01);
             translate([0, 0, TOP_Z]) rfoot(i, CLR_UPPER + CHAMFER, 0.01);
             translate([0, 0, TOP_Z + 1]) rfoot(i, CLR_UPPER + CHAMFER, 0.01); }                       // lead-in
    // switch-knob relief: right wall, from the rim down to 20 mm above the floor
    translate([radios[i][0] + RW + CLR_UPPER - 0.5, radios[i][1] + KNOB_Y - KNOB_W/2, FLOOR_Z + KNOB_Z]) cube([KNOB_D + 0.5, KNOB_W, TOP_Z]);
    // wall vents: vertical slots 2 x 30 at 14-44 mm above the floor, left/right/back walls
    for (y = [14, 20, 26]) for (x = [radios[i][0] - 4, radios[i][0] + RW + 0.2])
        translate([x, radios[i][1] + y - 1, FLOOR_Z + 14]) cube([3.8, 2, 30]);
    for (x = [9, 16, 27, 34]) translate([radios[i][0] + x - 1, radios[i][1] + RD + 0.2, FLOOR_Z + 14]) cube([2, 3.8, 30]);
}
module shell_raw() {
    difference() {
        union() {
            // skirt
            difference() {
                translate([0, 0, BASE_T + SKIRT_GAP]) rrect(0, 0, OUT_W, OUT_D, SHELL_R, TOP_Z - BASE_T - SKIRT_GAP);
                translate([0, 0, BASE_T]) rrect(WALL, WALL, OUT_W - 2*WALL, OUT_D - 2*WALL, SHELL_R - WALL, TOP_Z - BASE_T - DECK_T);
            }
            // pocket tubes
            for (i = [0:5]) translate([0, 0, FLOOR_Z + TUBE_GAP]) rfoot(i, CLR_UPPER + POCKET_WALL, TOP_Z - FLOOR_Z - TUBE_GAP);
            // screw bosses (clamp the PCB onto the base standoffs)
            for (h = holes) translate([h[0], h[1], PCB_Z1]) cylinder(d = BOSS_D, h = TOP_Z - PCB_Z1 - 0.5);
            // status-LED light pipe
            translate([led_pipe[0], led_pipe[1], PIPE_Z0]) cylinder(d = PIPE_OD, h = TOP_Z - PIPE_Z0 - 0.5);
        }
        for (i = [0:5]) pocket_cavity(i);
        for (h = holes) translate([h[0], h[1], PCB_Z1 - 0.01]) cylinder(d = INSERT_D, h = INSERT_L);
        translate([led_pipe[0], led_pipe[1], PIPE_Z0 - 1]) cylinder(d = PIPE_ID, h = TOP_Z);
        // rear USB-C input opening (fits any USB-C cable overmold up to 12.4 x 6.5)
        translate([usb_in[0], OUT_D + 0.1, usb_in_z]) rotate([90, 0, 0]) translate([-6.5, -3.8, 0]) linear_extrude(WALL + 1) offset(r = 3) offset(delta = -3) square([13, 7.6]);
        // deck vents over the channels between the pockets
        for (cx = [radios[0][0] + RW + GAP/2, radios[1][0] + RW + GAP/2]) for (dx = [-6, -2, 2, 6])
            for (yr = [[16, 38], [72, 94]]) translate([cx + dx - 1.0, yr[0], TOP_Z - DECK_T - 1]) cube([2.0, yr[1] - yr[0], DECK_T + 2]);
        for (x0 = [14, 150]) for (dy = [-4, 0, 4]) translate([x0, radios[0][1] + RD + GAP/2 + dy - 1, TOP_Z - DECK_T - 1]) cube([28, 2, DECK_T + 2]);
        // side skirt vents (low, near the PCB)
        for (y = [20:8:92]) for (x = [-1, OUT_W - WALL - 1]) translate([x, y, BASE_T + 3]) cube([WALL + 2, 3, 9]);
        // engraved label on the deck (Y-channel, left)
        translate([radios[1][0] - GAP/2 - 30, radios[0][1] + RD + GAP/2 - 2.5, TOP_Z - 0.6])
            linear_extrude(1) text("OpenALD Dock v1.0", size = 4.2, font = "Liberation Sans:style=Bold", halign = "left");
        translate([radios[1][0] + RW + GAP/2 + 8, radios[0][1] + RD + GAP/2 - 2.5, TOP_Z - 0.6])
            linear_extrude(1) text("USB-C PD 45 W+", size = 4.2, font = "Liberation Sans:style=Bold", halign = "left");
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
            for (p = plugs) translate([0, 0, 0]) rbox_c(p[0], p[1], 12, 6, 1, PCB_Z0);
            for (g = pegs) translate([g[0], g[1], 0]) cylinder(d = 6, h = PCB_Z0);
        }
        for (h = holes) { translate([h[0], h[1], -1]) cylinder(d = SCREW_D, h = PCB_Z0 + 2);
                          translate([h[0], h[1], -1]) cylinder(d = HEAD_D, h = HEAD_L + 1); }
        // vents under the X- and Y-channels (buck converters, slot switches)
        for (cx = [radios[0][0] + RW + GAP/2, radios[1][0] + RW + GAP/2]) for (dx = [-6, -2, 2, 6])
            for (yr = [[16, 40], [64, 96]]) translate([cx + dx - 1.0, yr[0], -1]) cube([2.0, yr[1] - yr[0], BASE_T + 2]);
        for (x0 = [16, 70, 116, 150]) for (dy = [-4, 0, 4]) translate([x0, radios[0][1] + RD + GAP/2 + dy - 1, -1]) cube([26, 2, BASE_T + 2]);
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
        // slot 5 (back centre): relief over the rear USB-C receptacle's signal pads under the pad's back rim
        if (i == 4) translate([usb_in[0] - 4.0, OUT_D - 15, PCB_Z1 - 1]) cube([8.0, 15, 1.6]);
        // finger notch to lift the pad out (front edge)
        translate([radios[i][0] + RW/2, radios[i][1] - PAD_OFF, PCB_Z1 + PAD_T]) scale([1, 0.6, 1]) sphere(d = 8);
    }
}
// ---------------------------------------------------------------- fit-check / preview helpers
module radio_env(i) {        // bottom 52 mm of any OpenALD radio (see DOCK_INTERFACE.md), USB-C cavity open
    p = plugs[i];
    difference() {
        translate([0, 0, FLOOR_Z]) rfoot(i, 0, 52);
        translate([0, 0, FLOOR_Z - 1]) rbox_c(p[0], p[1], 9.44, 3.76, 1.4, MOUTH_UP + 1);
        translate([0, 0, FLOOR_Z]) rbox_c(p[0], p[1], 8.40, 2.60, 1.25, MOUTH_UP + 7.0);
    }
}
module plug(i) { p = plugs[i];
    translate([0, 0, PCB_Z1]) rbox_c(p[0], p[1], 7.96, 3.48, 0.3, 1.8);
    translate([0, 0, PCB_Z1]) rbox_c(p[0], p[1], 8.25, 2.40, 1.15, PLUG_H); }
module pcb() { color("darkgreen") translate([PCB_X0, PCB_Y0, PCB_Z0]) cube([PCB_X1 - PCB_X0, PCB_Y1 - PCB_Y0, PCB_T]); }
if (part == "shell")  translate([0, OUT_D, TOP_Z]) rotate([180, 0, 0]) shell_raw();     // print deck-down
if (part == "base")   base_raw();
if (part == "pad")    translate([0, 0, PCB_Z1 + PAD_T]) rotate([180, 0, 0]) pad_raw(pad_index);   // print top-down
if (part == "pads")   for (i = [0:5]) translate([(i % 3) * 52 - radios[i][0], floor(i / 3) * 42 + radios[i][1] + RD + PAD_OFF, PCB_Z1 + PAD_T]) rotate([180, 0, 0]) pad_raw(i);   // top face down (rotation, not mirror)
if (part == "shell_raw") shell_raw();
if (part == "base_raw")  base_raw();
if (part == "pads_raw")  for (i = [0:5]) pad_raw(i);
if (part == "radios")    for (i = [0:5]) radio_env(i);
if (part == "plugs")     for (i = [0:5]) plug(i);
if (part == "assembly" || part == "section") {
    intersection() {
        union() {
            color("gainsboro") base_raw(); pcb();
            color("silver") for (i = [0:5]) plug(i);
            color("dimgray") for (i = [0:5]) pad_raw(i);
            color("lightsteelblue", 0.9) shell_raw();
            color("orange", 0.85) for (i = [0, 1, 4]) radio_env(i);
        }
        if (part == "section") translate([-1, -1, -1]) cube([plugs[1][0] + 1, OUT_D + 2, 200]);
        else cube([1000, 1000, 1000]);
    }
}
if (part == "exploded") {
    color("gainsboro") base_raw(); pcb();
    color("silver") for (i = [0:5]) plug(i);
    color("dimgray") translate([0, 0, 25]) for (i = [0:5]) pad_raw(i);
    color("lightsteelblue") translate([0, 0, 70]) shell_raw();
}
if (part == "print") {
    translate([0, OUT_D, TOP_Z]) rotate([180, 0, 0]) shell_raw();
    translate([0, OUT_D + 15, 0]) base_raw();
    for (i = [0:5]) translate([OUT_W + 15 + (i % 2) * 52 - radios[i][0], floor(i / 2) * 42 + radios[i][1] + RD + PAD_OFF, PCB_Z1 + PAD_T]) rotate([180, 0, 0]) pad_raw(i);
}
