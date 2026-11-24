// OpenALD Feather RP2040 enclosure, 2026-11-24 unified envelope (still v1.0).
// Outside 32.9 W x 89.75 L x 34.83 T, plan corner r 5, edge r 2: same length, thickness and dock port as the MI03 and
// the single-board radio (USB-C on the LEFT long side, centred 30.3 mm from the top outer end and 7.55 mm below the
// front face, mouth 1.0 mm inside the side face), so it uses the same charging-dock pocket (radios dock lying on that side).
// Parts:  top    = front shell (front face, jack / charge port / wheel / switch / LED openings, clamp posts)
//         bottom = back shell (floor with the holder pocket and the Feather groove, Feather USB-C opening in the top end)
//         deck   = plate between them: carries the FM module, the thumbwheel cradle and the charge-port breakout
// All dimensions come from case_params.scad (scripts/gen_case_params.py <- scripts/layout.py).
// Frame: X across (0 = centre, -X = dock side), Y = 0 at the inner jack-end wall, Z = 0 at the back face.
include <case_params.scad>

part = "assembly";   // top | bottom | deck | print | assembly | closed | top_raw | bottom_raw | deck_raw | section | g_<ghost>
sec_y = 57.45;       // section plane for part="section"

lip_h = 1.4;  lip_t = 0.9;  fit = 0.15;
snap_len = 8;  snap_bump = 0.3;
snap_ys_l = [12, 75];   // left (dock) wall: clear of the charge-port channel
snap_ys_r = [12, 55];   // right wall: clear of the wheel notch and the switch groove
deck_clr = 0.2;         // deck edge to the inner walls
ledge_w = 1.0;
post_d = 3.0;
asm_fit = 0.2;
$fn = 40;

IN_Y0 = 0;  IN_Y1 = IN_L;
module rrect(x0,y0,x1,y1,r,h) { hull() for (x=[x0+r,x1-r]) for (y=[y0+r,y1-r]) translate([x,y,0]) cylinder(r=r,h=h); }
module rr2d(w,h,r) { r2=min(r,w/2,h/2); hull() for (sx=[-1,1]) for (sy=[-1,1]) translate([sx*(w/2-r2),sy*(h/2-r2)]) circle(r=r2); }
module rounded_shell(z0,z1) {
  hull() for (x=[IN_X0-WALL+OUT_R, IN_X1+WALL-OUT_R]) for (y=[IN_Y0-WALL+OUT_R, IN_Y1+WALL-OUT_R])
    for (z=[z0+EDGE_R, z1-EDGE_R]) translate([x,y,z]) rotate_extrude($fn=48) translate([OUT_R-EDGE_R,0]) circle(r=EDGE_R,$fn=24);
}
module cavity(z0,z1) { translate([0,0,z0]) rrect(IN_X0,IN_Y0,IN_X1,IN_Y1,IN_R,z1-z0); }
module lip_outline(o,h) { rrect(IN_X0-o,IN_Y0-o,IN_X1+o,IN_Y1+o,IN_R+o,h); }
function box(b) = b;   // [x0,x1,y0,y1,z0,z1]
module bx(b) { translate([b[0],b[2],b[4]]) cube([b[1]-b[0],b[3]-b[2],b[5]-b[4]]); }

echo(str("Feather case outer: ", W_OUT, " W x ", IN_L+2*WALL, " L x ", T, " T; split Z ", Z_SPLIT, " (front shell ", T-Z_SPLIT, ", back shell ", Z_SPLIT, ")"));
echo(str("Dock USB-C centre ", IN_L+WALL-DOCK_USB_Y, " mm from the top outer end, ", T-DOCK_USB_Z, " below the front face, mouth ", DOCK_USB_MOUTH_X-(IN_X0-WALL), " inside the side face"));

// ---------------- derived positions ----------------
brk_x0 = DOCK_USB_MOUTH_X + 0.5;               // breakout PCB edge (the receptacle overhangs it by 0.5)
brk_z1 = DOCK_USB_Z - USB_H/2;                 // PCB top (receptacle sits on it)
brk_b  = [brk_x0, brk_x0+BRK_D, DOCK_USB_Y-BRK_W/2, DOCK_USB_Y+BRK_W/2, brk_z1-BRK_T, brk_z1];
usb_b  = [DOCK_USB_MOUTH_X, DOCK_USB_MOUTH_X+USB_LEN, DOCK_USB_Y-USB_W/2, DOCK_USB_Y+USB_W/2, brk_z1, brk_z1+USB_H];
fm_b   = fm_box;
jack_b = [FM_CX-FM_JACK_D/2, FM_CX+FM_JACK_D/2, fm_b[2]-FM_JACK_OUT, fm_b[2]-FM_JACK_OUT+FM_JACK_L, fm_b[5], fm_b[5]+FM_JACK_D];
hdr_b  = [FM_CX-fm_hdr[0]/2, FM_CX+fm_hdr[0]/2, fm_hdr[3]-fm_hdr[1]/2, fm_hdr[3]+fm_hdr[1]/2, fm_b[4]-fm_hdr[2], fm_b[4]];
wx = wheel_xy[0]; wy = wheel_xy[1];
wbody_b = [wx-wheel_body[2], wx+wheel_body[1], wy-wheel_body[0]/2, wy+wheel_body[0]/2, WHEEL_SEAT_Z, WHEEL_SEAT_Z+wheel_z0];
sw_plate_x1 = IN_X1 + WALL - SW_SKIN;          // plate outer face (against the skin)
sw_plate_b = [sw_plate_x1-sw_plate[2], sw_plate_x1, SW_Y-sw_plate[0]/2, SW_Y+sw_plate[0]/2, SW_Z-sw_plate[1]/2, SW_Z+sw_plate[1]/2];
sw_body_b  = [sw_plate_b[0]-sw_body[2], sw_plate_b[0], SW_Y-sw_body[0]/2, SW_Y+sw_body[0]/2, SW_Z-sw_body[1]/2, SW_Z+sw_body[1]/2];
sw_lug_b   = [sw_body_b[0]-SW_LUG_L, sw_body_b[0], SW_Y-SW_LUG_P-0.5, SW_Y+SW_LUG_P+0.5, SW_Z-0.4, SW_Z+0.4];
sw_knob_b  = [sw_plate_x1, sw_plate_x1+SW_L, SW_Y-sw_act[0]/2, SW_Y+sw_act[0]/2, SW_Z-sw_act[1]/2, SW_Z+sw_act[1]/2];  // centre position
fb = feather_board;

// ---------------- ghosts (fit check + previews) ----------------
module g_holder() { bx(holder_box); }
module g_feather() { bx(fb); for (p=feather_parts) bx(p); }
module g_fm() { bx(fm_b); translate([FM_CX, jack_b[2], fm_b[5]+FM_JACK_D/2]) rotate([-90,0,0]) cylinder(d=FM_JACK_D, h=FM_JACK_L); bx(hdr_b); }
module g_breakout() { bx(brk_b); bx(usb_b); bx([usb_b[1], brk_b[1]-2.0, brk_b[2], brk_b[3], brk_z1, brk_z1+1.0]); }   // ASSUMED: top-side parts <= 1.0 tall, none in the last 2 mm
module g_wheel() { bx(wbody_b); translate([wx,wy,WHEEL_SEAT_Z+wheel_z0]) cylinder(r=WHEEL_R, h=wheel_z1-wheel_z0); }
module g_switch(shift=0) { bx(sw_plate_b); bx(sw_body_b); bx(sw_lug_b); translate([0,shift,0]) bx(sw_knob_b); }
module g_leds() { for (p=led3) translate([p[0],p[1],T-FRONT_T-1.0-LED3_ABOVE_FLANGE+FRONT_T+0.6]) { cylinder(d=3.0,h=LED3_ABOVE_FLANGE); translate([0,0,-1.0]) cylinder(d=3.8,h=1.0); } }
module ghosts() { color("black") g_holder(); color("darkgreen") g_feather(); color("royalblue") g_fm(); color("purple") g_breakout(); color("dimgray") g_wheel(); color("silver") g_switch(); color("red") g_leds(); }

// ---------------- openings ----------------
module jack_cuts() {
  translate([FM_CX, IN_Y0+0.01, FM_JACK_AXIS_Z]) rotate([90,0,0]) { cylinder(d=FM_JACK_HOLE_D, h=WALL+1); translate([0,0,WALL-0.8]) cylinder(d1=FM_JACK_HOLE_D, d2=FM_JACK_HOLE_D+1.8, h=0.81); }
}
module dock_usb_cuts() {   // same geometry as the MI03 / single-board cases
  translate([IN_X0-WALL-1, DOCK_USB_Y, DOCK_USB_Z]) rotate([0,90,0]) rotate([0,0,90]) linear_extrude(1+(DOCK_USB_MOUTH_X-USB_RECESS_GAP)-(IN_X0-WALL)) rr2d(USB_RECESS[0], USB_RECESS[1], USB_RECESS[2]);
  translate([IN_X0-WALL-1, DOCK_USB_Y, DOCK_USB_Z]) rotate([0,90,0]) rotate([0,0,90]) linear_extrude(WALL+1.5) rr2d(USB_W+0.5, USB_H+0.5, 1.4);
  // drop-in channel: the receptacle sits 1.0 into the wall, so the wall is open from the split up to it
  translate([DOCK_USB_MOUTH_X-0.15, DOCK_USB_Y-(USB_W+0.5)/2, Z_SPLIT-1]) cube([IN_X0+0.01-(DOCK_USB_MOUTH_X-0.15), USB_W+0.5, DOCK_USB_Z+(USB_H+0.5)/2-(Z_SPLIT-1)]);
  // ... and for the breakout PCB edge (it sits 0.5 behind the mouth, so 0.5 into the wall)
  translate([brk_x0-0.15, brk_b[2]-0.2, Z_SPLIT-1]) cube([IN_X0+0.01-(brk_x0-0.15), BRK_W+0.4, brk_z1+0.1-(Z_SPLIT-1)]);
}
// no back-shell lip where the charge-port breakout and the switch plate reach into the wall
module lip_gaps() {
  translate([IN_X0-lip_t-1, brk_b[2]-0.5, Z_SPLIT-1]) cube([lip_t+1.01, BRK_W+1.0, lip_h+2]);
  translate([IN_X1-0.01, SW_Y-sw_plate[0]/2-0.5, Z_SPLIT-1]) cube([lip_t+1, sw_plate[0]+1.0, lip_h+2]);
}
module feather_usb_cuts() {   // programming port through the top end wall (Feather receptacle long axis along Z)
  fu = feather_usb;
  translate([fu[0], IN_Y1-1, fu[2]]) rotate([-90,0,0]) linear_extrude(WALL+2) rr2d(USB_H+0.5, USB_W+0.5, 1.4);
  translate([fu[0], fu[1]+USB_RECESS_GAP, fu[2]]) rotate([-90,0,0]) linear_extrude(WALL+2) rr2d(USB_RECESS[1], USB_RECESS[0], USB_RECESS[2]);
}
function wheel_ch() = sqrt(pow(WHEEL_R,2)-pow(IN_X1-wx,2));
module wheel_cuts() {
  ch = wheel_ch(); wz = WHEEL_SEAT_Z+(wheel_z0+wheel_z1)/2;
  translate([IN_X1+WALL-1.0, wy-ch-2.5, wz-3.0]) cube([2, 2*ch+5, 6.0]);           // pocket: wall thinned to 1.0
  translate([IN_X1-1, wy-ch-0.6, wz-(wheel_z1-wheel_z0+1.0)/2]) cube([WALL+2, 2*ch+1.2, wheel_z1-wheel_z0+1.0]);
}
module wheel_notch() { ch = wheel_ch(); wz = WHEEL_SEAT_Z+(wheel_z0+wheel_z1)/2; translate([IN_X1-0.5, wy-ch-0.6, Z_SPLIT-1]) cube([WALL+2, 2*ch+1.2, wz-Z_SPLIT+1]); }
module wheel_tab() { ch = wheel_ch(); intersection() { rounded_shell(0,T); translate([IN_X1, wy-ch-0.6+asm_fit, Z_SPLIT-0.01]) cube([WALL+1, 2*ch+1.2-2*asm_fit, WHEEL_SEAT_Z+wheel_z0-0.5-Z_SPLIT+0.01]); } }
sw_slot = [sw_act[0]+SW_TRAVEL+0.4, sw_act[1]+0.4];
module switch_cuts() {
  translate([IN_X1-1, SW_Y-sw_slot[0]/2, SW_Z-sw_slot[1]/2]) cube([WALL+2, sw_slot[0], sw_slot[1]]);                 // knob slot
  translate([sw_plate_x1-SW_GROOVE, SW_Y-sw_plate[0]/2-0.2, Z_SPLIT-1]) cube([SW_GROOVE, sw_plate[0]+0.4, sw_plate_b[5]+0.2-(Z_SPLIT-1)]);   // plate groove, open to the split
  translate([IN_X1-1, SW_Y-sw_body[0]/2-0.3, Z_SPLIT-1]) cube([sw_plate_x1-SW_GROOVE-IN_X1+1.01, sw_body[0]+0.6, sw_body_b[5]+0.3-(Z_SPLIT-1)]); // body window
}
module switch_ribs() {   // inner side of the plate groove beside the body (the wall alone leaves only 0.1 mm there)
  for (s=[-1,1]) translate([sw_plate_x1-SW_GROOVE-SW_RIB, s>0 ? SW_Y+sw_body[0]/2+0.3 : SW_Y-sw_plate[0]/2-0.2, Z_SPLIT+0.6])
    cube([SW_RIB+0.01, sw_plate[0]/2+0.2-sw_body[0]/2-0.3, sw_plate_b[5]+0.2-Z_SPLIT-0.6]);
}
module switch_labels() {
  for (L=[["ON",1],["OFF",-1]]) translate([IN_X1+WALL-0.4, SW_Y+L[1]*(sw_slot[0]/2+0.8), SW_Z])
    rotate([90,0,90]) linear_extrude(1) text(L[0], size=1.8, font="DejaVu Sans:style=Bold", halign=L[1]>0?"left":"right", valign="center");
}
module led_cuts() { for (p=led3) translate([p[0],p[1],Z_CEIL-2.01]) { cylinder(d=3.1, h=FRONT_T+3); cylinder(d=4.0, h=2.0); } }
module led_tubes() { for (p=led3) translate([p[0],p[1],Z_CEIL-2.0]) cylinder(d=5.6, h=2.01); }
// clamp posts from the ceiling: FM corners (around the holes), breakout PCB, deck
fm_post_h = Z_CEIL - fm_b[5];
module posts() {
  for (h=fm_holes) translate([h[0],h[1],fm_b[5]]) difference() { cylinder(d=6.0, h=fm_post_h+0.01); translate([0,0,-1]) cylinder(d=3.4, h=fm_post_h+2); }
  translate([brk_b[1]-1.0, brk_b[3]-1.5, brk_z1]) cylinder(d=2.0, h=Z_CEIL-brk_z1+0.01);
  translate([brk_b[1]-1.0, brk_b[2]+1.5, brk_z1]) cylinder(d=2.0, h=Z_CEIL-brk_z1+0.01);
  for (p=deck_posts) translate([p[0],p[1],DECK_Z1]) cylinder(d=post_d, h=Z_CEIL-DECK_Z1+0.01);
}
deck_posts = [[-8.0, 33.0], [0.0, 84.0], [-12.5, 84.0], [6.0, 30.0], [1.0, 52.0]];

// ---------------- FRONT SHELL ----------------
module top_half() {
  difference() {
    union() {
      difference() { intersection() { rounded_shell(0,T); translate([-50,-50,Z_SPLIT]) cube([100,200,T]); } cavity(Z_SPLIT-1, Z_CEIL); }
      posts(); led_tubes(); switch_ribs();
    }
    translate([0,0,Z_SPLIT-0.01]) difference() { lip_outline(lip_t+fit, lip_h+0.3); translate([0,0,-1]) lip_outline(-0.01, lip_h+3); }
    for (y=snap_ys_l) translate([IN_X0-lip_t-fit-snap_bump-0.1+0.01, y-(snap_len+0.6)/2, Z_SPLIT+lip_h/2-0.5]) cube([snap_bump+0.1, snap_len+0.6, 1.0]);
    for (y=snap_ys_r) translate([IN_X1+lip_t+fit-0.01, y-(snap_len+0.6)/2, Z_SPLIT+lip_h/2-0.5]) cube([snap_bump+0.1, snap_len+0.6, 1.0]);
    jack_cuts(); dock_usb_cuts(); wheel_cuts(); wheel_notch(); switch_cuts(); switch_labels(); led_cuts();
  }
}
// ---------------- BACK SHELL ----------------
module bottom_half() {
  difference() {
    union() {
      difference() { intersection() { rounded_shell(0,T); translate([-50,-50,-1]) cube([100,200,Z_SPLIT+1]); } cavity(FLOOR_T, Z_SPLIT+1); }
      translate([0,0,Z_SPLIT-0.01]) difference() { lip_outline(lip_t, lip_h+0.01); translate([0,0,-1]) lip_outline(0, lip_h+3); translate([0,0,-Z_SPLIT+0.01]) lip_gaps(); }
      for (y=snap_ys_l) translate([IN_X0-lip_t+0.01, y, Z_SPLIT+lip_h/2]) mirror([1,0,0]) snap_bump_shape();
      for (y=snap_ys_r) translate([IN_X1+lip_t-0.01, y, Z_SPLIT+lip_h/2]) snap_bump_shape();
      wheel_tab();
      // deck ledges (45-degree undersides) where neither the holder nor the Feather is: jack end wall, both long walls
      // up to the holder / Feather. Elsewhere the deck lies 0.6 mm over the cell and the front-shell posts clamp it.
      intersection() { cavity(FLOOR_T, Z_SPLIT); union() {
        ledge([IN_X1-ledge_w, IN_X1+0.01], [IN_Y0, holder_box[2]-0.3]);
        ledge([IN_X0-0.01, IN_X0+ledge_w], [IN_Y0, fb[2]-1.0]);
        ledge([IN_X0, IN_X1], [IN_Y0-0.01, IN_Y0+ledge_w]);
      } }
      // Feather locating ribs on the left wall (bottom edge strip of the Feather, below its parts)
      for (y=[fb[2]+8, (fb[2]+fb[3])/2, fb[3]-8]) translate([IN_X0-0.01, y-1.0, FLOOR_T-0.01]) cube([fb[0]-IN_X0-0.1+0.01, 2.0, 2.0]);
    }
    // holder pocket, Feather groove
    translate([holder_box[0]-0.2, holder_box[2]-0.2, holder_box[4]]) cube([holder_box[1]-holder_box[0]+0.4, holder_box[3]-holder_box[2]+0.4, 5]);
    translate([fb[0]-0.15, fb[2]-0.3, fb[4]]) cube([fb[1]-fb[0]+0.3, fb[3]-fb[2]+0.6, 5]);
    feather_usb_cuts();
    translate([-3, IN_Y1+WALL-0.8, Z_SPLIT-0.8]) cube([6, 2, 0.81]);   // pry notch, top end
  }
}
module snap_bump_shape() { hull() { translate([0,-snap_len/2,-0.5]) cube([0.01, snap_len, 1.0]); translate([snap_bump,-snap_len/2+0.3,-0.25]) cube([0.01, snap_len-0.6, 0.5]); } }
module ledge(xr, yr) {
  zt = DECK_Z0 - 0.05;
  hull() { translate([xr[0], yr[0], zt-0.01]) cube([xr[1]-xr[0], yr[1]-yr[0], 0.01]);
           translate([(xr[0]<IN_X0+0.1) ? xr[0] : (xr[1]>IN_X1-0.1 ? xr[1]-0.02 : xr[0]), (yr[0]<IN_Y0+0.1) ? yr[0] : (yr[1]>IN_Y1-0.1 ? yr[1]-0.02 : yr[0]), zt-ledge_w-0.5])
             cube([(xr[0]<IN_X0+0.1 || xr[1]>IN_X1-0.1) ? 0.02 : xr[1]-xr[0], (yr[0]<IN_Y0+0.1 || yr[1]>IN_Y1-0.1) ? 0.02 : yr[1]-yr[0], ledge_w+0.5]); }
}
// ---------------- DECK ----------------
module deck() {
  difference() {
    union() {
      translate([0,0,DECK_Z0]) rrect(IN_X0+deck_clr, IN_Y0+deck_clr, IN_X1-deck_clr, IN_Y1-deck_clr, IN_R-deck_clr, DECK_T);
      for (h=fm_holes) translate([h[0],h[1],DECK_Z1-0.01]) cylinder(d=7.0, h=FM_STANDOFF+0.01);       // FM standoffs
      // wheel cradle: walls on the -Y, +Y and terminal (-X) side are low corner blocks; dial side open to the wall
      for (s=[-1,1]) translate([wbody_b[0]+1.0, s>0 ? wbody_b[3]+0.15 : wbody_b[2]-1.15, DECK_Z1-0.01]) cube([wbody_b[1]-wbody_b[0]-1.0, 1.0, 1.5]);
      // breakout PCB support block (over the holder, beside the Feather slot)
      translate([fb[1]+0.4, brk_b[2], DECK_Z1-0.01]) cube([brk_b[1]-fb[1]-0.4, BRK_W, brk_b[4]-DECK_Z1+0.01]);
    }
    // the Feather's top edge (and its parts) reach 0.75 above the deck underside: the deck stops short of it
    translate([IN_X0-1, fb[2]-0.4, DECK_Z0-1]) cube([fb[1]+0.2-IN_X0+1, IN_Y1-fb[2]+2, DECK_T+2]);
    translate([hdr_b[0]-1.0, IN_Y0, DECK_Z0-1]) cube([hdr_b[1]-hdr_b[0]+2.0, hdr_b[3]+1.0, DECK_T+FM_STANDOFF+2]);         // FM header window
    for (h=fm_holes) translate([h[0],h[1],DECK_Z0-1]) cylinder(d=3.3, h=DECK_T+FM_STANDOFF+2);
    for (s=[-1,1]) translate([wx-4.5, wy+s*3, DECK_Z0-1]) cylinder(d=1.8, h=DECK_T+2);                                    // wheel locating bosses
    translate([wbody_b[0]-3.0, wy-4.0, DECK_Z0-1]) cube([2.5, 8.0, DECK_T+2]);                                            // wheel wires
    translate([sw_lug_b[0]-1.0, SW_Y-4.5, DECK_Z0-1]) cube([3.0, 9.0, DECK_T+2]);                                         // switch wires
  }
}

if (part=="top") translate([0,0,T]) rotate([180,0,0]) top_half();
else if (part=="bottom") bottom_half();
else if (part=="deck") translate([0,0,-DECK_Z0]) deck();
else if (part=="top_raw") top_half();
else if (part=="bottom_raw") bottom_half();
else if (part=="deck_raw") deck();
else if (part=="g_holder") g_holder();
else if (part=="g_feather") g_feather();
else if (part=="g_fm") g_fm();
else if (part=="g_breakout") g_breakout();
else if (part=="g_brk_usb") bx(usb_b);
else if (part=="g_brk_pcb") bx(brk_b);
else if (part=="g_wheel") g_wheel();
else if (part=="g_switch") g_switch();
else if (part=="g_switch_on") g_switch(SW_TRAVEL/2);
else if (part=="g_switch_off") g_switch(-SW_TRAVEL/2);
else if (part=="g_leds") g_leds();
else if (part=="print") { bottom_half(); translate([W_OUT+10,IN_L,T]) rotate([180,0,0]) top_half(); translate([2*W_OUT+20,0,-DECK_Z0]) deck(); }
else if (part=="closed") { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("orange") deck(); ghosts(); }
else if (part=="section") intersection() { union() { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("orange") deck(); ghosts(); } translate([-50, sec_y, -10]) cube([100, 0.6, 60]); }
else { color("lightgray") bottom_half(); color("orange") translate([0,0,8]) deck(); color("lightsteelblue",0.6) translate([0,0,22]) top_half(); ghosts(); }
