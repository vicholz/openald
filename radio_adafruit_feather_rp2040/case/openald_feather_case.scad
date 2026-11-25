// OpenALD Feather RP2040 enclosure, t116u (2026-11-24) bottom-end USB-C (still v1.0).
// Outside 31.9 W x 98.71 L x 33.86 T, plan corner r 5, edge r 2. The Feather lies flat at the bottom end and its own
// USB-C is the dock / charging port: centred across the bottom end face, 6.62 mm below the front face, mouth 1.0 mm
// inside the face -- the same spot, width and thickness as the single-board radio, so both stand upright in the same
// charging-dock pocket. The Feather's CHG LED, red LED and NeoPixel show through the front face (light tunnels).
// Parts:  top    = front shell (front face, LED tunnels, RESET pin hole, jack / wheel / switch / USB-C openings, clamp posts)
//         bottom = back shell (floor with the holder pocket, ledges for the deck, snap lip)
//         deck   = plate between them: carries the Feather (pegs + standoffs), the thumbwheel cradle and the FM module
// All dimensions come from case_params.scad (scripts/gen_case_params.py <- scripts/layout.py).
// Frame: X across (0 = centre, +X = right / wheel side), Y = 0 at the inner face of the bottom (USB-C) end wall,
// Z = 0 at the back face.
include <case_params.scad>

part = "assembly";   // top | bottom | deck | print | assembly | closed | top_raw | bottom_raw | deck_raw | section | g_<ghost>
sec_y = 2.0;         // section plane for part="section"
sec_x = 0.0;         // section plane for part="xsection"

lip_h = 1.4;  lip_t = 0.9;  fit = 0.15;
snap_len = 8;  snap_bump = 0.3;
snap_ys = [16, 84];     // both long walls: clear of the wheel notch (right) and the switch groove (left)
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
module bx(b) { translate([b[0],b[2],b[4]]) cube([b[1]-b[0],b[3]-b[2],b[5]-b[4]]); }

echo(str("Feather case outer: ", W_OUT, " W x ", IN_L+2*WALL, " L x ", T, " T; split Z ", Z_SPLIT, " (front shell ", T-Z_SPLIT, ", back shell ", Z_SPLIT, ")"));
echo(str("Dock USB-C centre X ", DOCK_USB_X, " (centred), ", T-DOCK_USB_Z, " below the front face, mouth ", DOCK_USB_MOUTH_Y-(IN_Y0-WALL), " inside the bottom end face"));

// ---------------- derived positions ----------------
fm_b   = fm_box;
// t122u: the FM module is FLIPPED (flat side toward the front face, jack hanging below the board)
jack_b = [FM_CX-FM_JACK_D/2, FM_CX+FM_JACK_D/2, fm_b[3]+FM_JACK_OUT-FM_JACK_L, fm_b[3]+FM_JACK_OUT, fm_b[4]-FM_JACK_D, fm_b[4]];
hdr_b  = [FM_CX-fm_hdr[0]/2, FM_CX+fm_hdr[0]/2, fm_hdr[3]-fm_hdr[1]/2, fm_hdr[3]+fm_hdr[1]/2, fm_b[5], fm_b[5]+fm_hdr[2]];   // header stubs (cut back)
wx = wheel_xy[0]; wy = wheel_xy[1];
wbody_b = [wx-wheel_body[2], wx+wheel_body[1], wy-wheel_body[0]/2, wy+wheel_body[0]/2, WHEEL_SEAT_Z, WHEEL_SEAT_Z+wheel_z0];
// power switch: built for the RIGHT wall at SW_Y, then mirrored onto the left wall (sw_side)
sw_plate_x1 = IN_X1 + WALL - SW_SKIN;          // plate outer face (against the skin)
sw_plate_b = [sw_plate_x1-sw_plate[2], sw_plate_x1, SW_Y-sw_plate[0]/2, SW_Y+sw_plate[0]/2, SW_Z-sw_plate[1]/2, SW_Z+sw_plate[1]/2];
sw_body_b  = [sw_plate_b[0]-sw_body[2], sw_plate_b[0], SW_Y-sw_body[0]/2, SW_Y+sw_body[0]/2, SW_Z-sw_body[1]/2, SW_Z+sw_body[1]/2];
sw_lug_b   = [sw_body_b[0]-SW_LUG_L, sw_body_b[0], SW_Y-SW_LUG_P-0.5, SW_Y+SW_LUG_P+0.5, SW_Z-0.4, SW_Z+0.4];
sw_knob_b  = [sw_plate_x1, sw_plate_x1+SW_L, SW_Y-sw_act[0]/2, SW_Y+sw_act[0]/2, SW_Z-sw_act[1]/2, SW_Z+sw_act[1]/2];  // centre position
module sw_side() { mirror([1,0,0]) children(); }
fb = feather_board;
fu = feather_usb;     // [x, mouth y, z]

// ---------------- ghosts (fit check + previews) ----------------
module g_holder() { bx(holder_box); }
module g_feather() {
  difference() { bx(fb); for (h=f_holes) translate([h[0],h[1],fb[4]-1]) cylinder(d=2.5, h=fb[5]-fb[4]+2); }
  for (i=[0:len(feather_parts)-2]) let(q=feather_parts[i]) bx([q[0],q[1],max(q[2],0),q[3],q[4],q[5]]);   // inside the cavity (the receptacle's own outline -> stadium below)
  u=feather_parts[len(feather_parts)-1]; r=(u[5]-u[4])/2;    // USB-C receptacle: stadium (rounded ends), like the real shell
  hull() for (x=[u[0]+r, u[1]-r]) translate([x, u[2], u[4]+r]) rotate([-90,0,0]) cylinder(r=r, h=u[3]-u[2]);
}
module g_fm() { difference() { bx(fm_b); for (h=fm_holes) translate([h[0],h[1],fm_b[4]-1]) cylinder(d=FM_HOLE_D, h=FM_T+2); }
               translate([FM_CX, jack_b[2], FM_JACK_AXIS_Z]) rotate([-90,0,0]) cylinder(d=FM_JACK_D, h=FM_JACK_L); bx(hdr_b); }
module g_wheel() { bx(wbody_b); translate([wx,wy,WHEEL_SEAT_Z+wheel_z0]) cylinder(r=WHEEL_R, h=wheel_z1-wheel_z0); }
module g_switch(shift=0) { sw_side() { difference() { bx(sw_plate_b); for (s=[-1,1]) translate([sw_plate_b[0]-1, SW_Y+s*SW_HOLE_P/2, SW_Z]) rotate([0,90,0]) cylinder(d=1.57, h=3, $fn=20); }
  bx(sw_body_b); bx(sw_lug_b); translate([0,shift,0]) bx(sw_knob_b); } }
module ghosts() { color("black") g_holder(); color("darkgreen") g_feather(); color("royalblue") g_fm(); color("dimgray") g_wheel(); color("silver") g_switch(); }

// ---------------- openings ----------------
module jack_cuts() {   // top end wall: barrel + 0.3 per side (t122u), 0.3 mm edge break
  translate([FM_CX, IN_Y1-0.01, FM_JACK_AXIS_Z]) rotate([-90,0,0]) { cylinder(d=FM_JACK_HOLE_D, h=WALL+1); translate([0,0,WALL-0.3]) cylinder(d1=FM_JACK_HOLE_D, d2=FM_JACK_HOLE_D+0.6, h=0.31); }
}
// front shell: the jack axis is below... the barrel sits in the end wall, so the wall under its axis is open down to
// the split (the back shell's jack_tab fills it), and the board edge (0.5 into the wall) gets a relief open to the split
module jack_notch() {
  translate([FM_CX-FM_JACK_HOLE_D/2, IN_Y1-0.01, Z_SPLIT-1]) cube([FM_JACK_HOLE_D, WALL+1, FM_JACK_AXIS_Z-(Z_SPLIT-1)]);
  translate([fm_b[0]-0.4, IN_Y1-0.01, Z_SPLIT-1]) cube([fm_b[1]-fm_b[0]+0.8, fm_b[3]-IN_Y1+0.3+0.01, fm_b[5]+0.3-(Z_SPLIT-1)]);
}
module jack_tab() { intersection() { rounded_shell(0,T);
  translate([FM_CX-FM_JACK_HOLE_D/2+asm_fit, IN_Y1, Z_SPLIT-0.01]) cube([FM_JACK_HOLE_D-2*asm_fit, WALL+1, FM_JACK_AXIS_Z-Z_SPLIT+0.01]); } }
usb_open = [USB_W+0.5, USB_H+0.5];
module dock_usb_cuts() {   // bottom end wall: same geometry as the single-board case
  translate([DOCK_USB_X, IN_Y0-WALL-1, DOCK_USB_Z]) rotate([-90,0,0]) linear_extrude(1+(DOCK_USB_MOUTH_Y-USB_RECESS_GAP)-(IN_Y0-WALL)) rr2d(USB_RECESS[0], USB_RECESS[1], USB_RECESS[2]);
  translate([DOCK_USB_X, IN_Y0-WALL-1, DOCK_USB_Z]) rotate([-90,0,0]) linear_extrude(WALL+1.5) rr2d(usb_open[0], usb_open[1], 1.4);
}
// front shell: the receptacle reaches 1.0 into the end wall, so the wall below it is open down to the split ...
module usb_notch() { translate([DOCK_USB_X-usb_open[0]/2, DOCK_USB_MOUTH_Y-0.15, Z_SPLIT-1]) cube([usb_open[0], IN_Y0+0.01-(DOCK_USB_MOUTH_Y-0.15), DOCK_USB_Z-(Z_SPLIT-1)]); }
// ... and the back shell fills it back up to just under the receptacle
module usb_tab() { translate([DOCK_USB_X-usb_open[0]/2+asm_fit, DOCK_USB_MOUTH_Y-0.15+asm_fit, Z_SPLIT-0.01]) cube([usb_open[0]-2*asm_fit, IN_Y0-(DOCK_USB_MOUTH_Y-0.15+asm_fit), F_Z1-0.1-Z_SPLIT+0.01]); }
module lip_gaps() {   // no lip beside the switch plate (left wall) or under the FM jack (top end wall)
  sw_side() translate([IN_X1-0.01, SW_Y-sw_plate[0]/2-0.5, Z_SPLIT-1]) cube([lip_t+1, sw_plate[0]+1.0, lip_h+2]);
  translate([FM_CX-FM_JACK_HOLE_D/2-0.6, IN_Y1-0.01, Z_SPLIT-1]) cube([FM_JACK_HOLE_D+1.2, lip_t+1, lip_h+2]);
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
// t122u: plate in a 0.8 mm pocket in the inner wall face (put in from inside), held by two heat-stake studs through its
// M2 holes; nothing slides along a groove any more
sw_pocket = [sw_plate[0]+0.4, sw_plate[1]+0.4];
module switch_cuts() { sw_side() {
  translate([IN_X1-1, SW_Y-sw_slot[0]/2, SW_Z-sw_slot[1]/2]) cube([WALL+2, sw_slot[0], sw_slot[1]]);                 // knob slot
  translate([IN_X1-1, SW_Y-sw_pocket[0]/2, SW_Z-sw_pocket[1]/2]) cube([sw_plate_x1-IN_X1+1, sw_pocket[0], sw_pocket[1]]);   // plate pocket
} }
module switch_studs() { sw_side() for (s=[-1,1])
  translate([sw_plate_x1+0.01, SW_Y+s*SW_HOLE_P/2, SW_Z]) rotate([0,-90,0]) cylinder(d=SW_STUD_D, h=sw_plate[2]+SW_STUD_OUT+0.01, $fn=20);
}
// deck: backing ribs behind both plate ends (outside the body), stopping 0.1 short of the wall face; a slot open to the
// top clears each melted stud head (<= 1.0 tall, <= 3.6 across) as the front shell comes down
module switch_backing() { sw_side() difference() {
  for (s=[-1,1]) translate([IN_X1-0.1-SW_BACK_RIB, s>0 ? SW_Y+sw_body[0]/2+0.4 : SW_Y-sw_plate[0]/2-0.2, DECK_Z1-0.01])
    cube([SW_BACK_RIB, sw_plate[0]/2+0.2-sw_body[0]/2-0.4, sw_plate_b[5]-DECK_Z1+0.01]);
  for (s=[-1,1]) translate([IN_X1-0.1-1.2, SW_Y+s*SW_HOLE_P/2-1.8, SW_Z-1.8]) cube([1.3, 3.6, 10]);
} }
module switch_labels() {   // engraved on the LEFT face; ON toward the top end
  for (L=[["ON",1],["OFF",-1]]) translate([IN_X0-WALL+0.4, SW_Y+L[1]*(sw_slot[0]/2+0.8), SW_Z])
    rotate([90,0,-90]) linear_extrude(1) text(L[0], size=1.8, font="DejaVu Sans:style=Bold", halign=L[1]>0?"right":"left", valign="center");
}
// Feather LEDs: one light tunnel per LED from the ceiling down to just above the part, open through the front face
module led_tubes() {
  for (l=f_leds) translate([l[0],l[1],F_Z1+l[4]]) cylinder(d=l[2]+2*l[3], h=Z_CEIL-(F_Z1+l[4])+0.01);
  translate([f_reset[0],f_reset[1],F_Z1+f_reset[4]]) cylinder(d=f_reset[2]+2*f_reset[3], h=Z_CEIL-(F_Z1+f_reset[4])+0.01);
}
module led_cuts() {
  for (l=f_leds) translate([l[0],l[1],F_Z1+l[4]-1]) { cylinder(d=l[2], h=T); translate([0,0,T-0.4-(F_Z1+l[4]-1)]) cylinder(d1=l[2], d2=l[2]+1.0, h=0.41); }
  translate([f_reset[0],f_reset[1],F_Z1+f_reset[4]-1]) cylinder(d=f_reset[2], h=T);    // RESET pin hole (paper clip)
}
// clamp posts from the ceiling: FM standoffs (short, with centring pegs), Feather holes (socket for the deck peg tip), deck
fm_post_h = Z_CEIL - fm_b[5];   // = FM_GAP_FRONT
deck_posts = [[2.0, 54.5], [2.0, 62.5]];   // t122u: x -3 -> +2, clear of the switch lugs while the switch is put in sideways
module posts() {
  for (h=fm_holes) translate([h[0],h[1],fm_b[5]]) { cylinder(d=5.5, h=fm_post_h+0.01);
    translate([0,0,-FM_PEG_IN]) { cylinder(d=FM_PEG_D, h=FM_PEG_IN+0.01); translate([0,0,-0.01]) cylinder(d1=FM_PEG_D-0.6, d2=FM_PEG_D, h=0.3); } }
  for (h=f_holes) translate([h[0],h[1],F_Z1+0.05]) difference() { cylinder(d=F_POST_D, h=Z_CEIL-F_Z1-0.05+0.01); translate([0,0,-1]) cylinder(d=F_POST_SOCKET[0], h=F_POST_SOCKET[1]+1); }
  for (p=deck_posts) translate([p[0],p[1],DECK_Z1]) cylinder(d=post_d, h=Z_CEIL-DECK_Z1+0.01);
}

// ---------------- FRONT SHELL ----------------
module top_half() { union() { switch_studs();   // studs added after the plate pocket is cut
  difference() {
    union() {
      difference() { intersection() { rounded_shell(0,T); translate([-50,-50,Z_SPLIT]) cube([100,200,T]); } cavity(Z_SPLIT-1, Z_CEIL); }
      posts(); led_tubes();
    }
    translate([0,0,Z_SPLIT-0.01]) difference() { lip_outline(lip_t+fit, lip_h+0.3); translate([0,0,-1]) lip_outline(-0.01, lip_h+3); }
    for (y=snap_ys) translate([IN_X0-lip_t-fit-snap_bump-0.1+0.01, y-(snap_len+0.6)/2, Z_SPLIT+lip_h/2-0.5]) cube([snap_bump+0.1, snap_len+0.6, 1.0]);
    for (y=snap_ys) translate([IN_X1+lip_t+fit-0.01, y-(snap_len+0.6)/2, Z_SPLIT+lip_h/2-0.5]) cube([snap_bump+0.1, snap_len+0.6, 1.0]);
    jack_cuts(); jack_notch(); dock_usb_cuts(); usb_notch(); wheel_cuts(); wheel_notch(); switch_cuts(); switch_labels(); led_cuts();
  }
} }
// ---------------- BACK SHELL ----------------
module ledge(x0,x1,y0,y1,dx,dy) {   // deck support strip under the deck, 45-degree underside toward (dx,dy)
  zt = DECK_Z0 - 0.05;
  hull() { translate([x0,y0,zt-0.01]) cube([x1-x0,y1-y0,0.01]);
           translate([dx>0 ? x0 : (dx<0 ? x1-0.02 : x0), dy>0 ? y0 : (dy<0 ? y1-0.02 : y0), zt-ledge_w-0.5])
             cube([dx!=0 ? 0.02 : x1-x0, dy!=0 ? 0.02 : y1-y0, ledge_w+0.5]); }
}
module bottom_half() {
  difference() {
    union() {
      difference() { intersection() { rounded_shell(0,T); translate([-50,-50,-1]) cube([100,200,Z_SPLIT+1]); } cavity(FLOOR_T, Z_SPLIT+1); }
      translate([0,0,Z_SPLIT-0.01]) difference() { lip_outline(lip_t, lip_h+0.01); translate([0,0,-1]) lip_outline(0, lip_h+3); translate([0,0,-Z_SPLIT+0.01]) lip_gaps(); }
      for (y=snap_ys) translate([IN_X0-lip_t+0.01, y, Z_SPLIT+lip_h/2]) mirror([1,0,0]) snap_bump_shape();
      for (y=snap_ys) translate([IN_X1+lip_t-0.01, y, Z_SPLIT+lip_h/2]) snap_bump_shape();
      wheel_tab(); usb_tab(); jack_tab();
      // deck ledges along all four walls (the holder is centred with 3.5 mm wire channels beside it)
      intersection() { cavity(FLOOR_T, Z_SPLIT); union() {
        ledge(IN_X0-0.01, IN_X0+ledge_w, IN_Y0, IN_Y1, -1, 0);
        ledge(IN_X1-ledge_w, IN_X1+0.01, IN_Y0, IN_Y1, 1, 0);
        ledge(IN_X0, IN_X1, IN_Y0-0.01, IN_Y0+ledge_w, 0, -1);
        difference() { ledge(IN_X0, IN_X1, IN_Y1-ledge_w, IN_Y1+0.01, 0, 1); translate([FM_CX-FM_JACK_D/2-0.6, IN_Y1-5, 0]) cube([FM_JACK_D+1.2, 10, 50]); }
      } }
    }
    // holder pocket + relief holes for its two PC pins (trimmed, wires soldered on, joints sit in the holes)
    translate([holder_box[0]-0.2, holder_box[2]-0.2, holder_box[4]]) cube([holder_box[1]-holder_box[0]+0.4, holder_box[3]-holder_box[2]+0.4, 5]);
    for (p=holder_pins) translate([p[0],p[1],-1]) cylinder(d=3.5, h=FLOOR_T+2);
    dock_usb_cuts(); jack_cuts();
    translate([IN_X1+WALL-0.8, 30-3, Z_SPLIT-0.8]) cube([2, 6, 0.81]);   // pry notch, right side
  }
}
module snap_bump_shape() { hull() { translate([0,-snap_len/2,-0.5]) cube([0.01, snap_len, 1.0]); translate([snap_bump,-snap_len/2+0.3,-0.25]) cube([0.01, snap_len-0.6, 0.5]); } }
// ---------------- DECK ----------------
wire_slots = [[IN_X0+ledge_w+0.1, -F_W_HALF()-0.2, 12.0, 22.0],     // left: holder + lead -> BAT, switch / divider
              [IN_X0+ledge_w+0.1, -F_W_HALF()-0.2, 39.0, 47.0],     // left: FM SDA / SCL (from under the deck) -> SDA / SCL
              [F_W_HALF()+0.2, IN_X1-ledge_w-0.1, 7.0, 17.0]];      // right: holder - lead, FM 3V3 / GND -> 3V3 / GND
function F_W_HALF() = (fb[1]-fb[0])/2;
module deck() {
  difference() {
    union() {
      translate([0,0,DECK_Z0]) rrect(IN_X0+deck_clr, IN_Y0+deck_clr, IN_X1-deck_clr, IN_Y1-deck_clr, IN_R-deck_clr, DECK_T);
      // FM support posts up to the (flipped) module's component side, with short centring pegs into its holes
      for (h=fm_holes) translate([h[0],h[1],DECK_Z1-0.01]) { cylinder(d=6.0, h=fm_b[4]-0.05-DECK_Z1+0.01);
        translate([0,0,fm_b[4]-DECK_Z1-0.06]) { cylinder(d=FM_PEG_D, h=FM_PEG_IN+0.06-0.3); translate([0,0,FM_PEG_IN+0.06-0.31]) cylinder(d1=FM_PEG_D, d2=FM_PEG_D-0.6, h=0.3); } }
      // Feather standoffs + pegs through its holes, sticking out F_PEG_OUT above its top face (centring)
      for (h=f_holes) translate([h[0],h[1],DECK_Z1-0.01]) { cylinder(d=4.4, h=F_STANDOFF+0.01); cylinder(d=F_PEG_D, h=F_Z1+F_PEG_OUT-0.3-DECK_Z1+0.01);
        translate([0,0,F_Z1+F_PEG_OUT-0.3-DECK_Z1]) cylinder(d1=F_PEG_D, d2=F_PEG_D-0.6, h=0.3); }
      switch_backing();
      // wheel cradle: low blocks on the -Y and +Y sides of the body; dial side open to the wall
      for (s=[-1,1]) translate([wbody_b[0]+1.0, s>0 ? wbody_b[3]+0.15 : wbody_b[2]-1.15, DECK_Z1-0.01]) cube([wbody_b[1]-wbody_b[0]-1.0, 1.0, 1.5]);
    }
    translate([jack_b[0]-0.4, jack_b[2]-0.5, DECK_Z0-1]) cube([jack_b[1]-jack_b[0]+0.8, IN_Y1-jack_b[2]+2, DECK_T+2]);   // notch: the jack dips through the deck
    for (s=[-1,1]) translate([wx-4.5, wy+s*3, DECK_Z0-1]) cylinder(d=1.8, h=DECK_T+2);                                    // wheel locating bosses
    for (w=wire_slots) translate([w[0], w[2], DECK_Z0-1]) cube([w[1]-w[0], w[3]-w[2], DECK_T+2]);                         // wire slots
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
else if (part=="g_wheel") g_wheel();
else if (part=="g_switch") g_switch();
else if (part=="g_switch_on") g_switch(SW_TRAVEL/2);
else if (part=="g_switch_off") g_switch(-SW_TRAVEL/2);
else if (part=="print") { bottom_half(); translate([W_OUT+10,IN_L,T]) rotate([180,0,0]) top_half(); translate([2*W_OUT+20,0,-DECK_Z0]) deck(); }
else if (part=="closed") { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("orange") deck(); ghosts(); }
else if (part=="section") intersection() { union() { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("orange") deck(); ghosts(); } translate([-50, sec_y, -10]) cube([100, 0.6, 60]); }
else if (part=="xsection") intersection() { union() { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("orange") deck(); ghosts(); } translate([sec_x, -10, -10]) cube([0.6, 120, 60]); }
else { color("lightgray") bottom_half(); color("orange") translate([0,0,8]) deck(); color("lightsteelblue",0.6) translate([0,0,22]) top_half(); ghosts(); }
