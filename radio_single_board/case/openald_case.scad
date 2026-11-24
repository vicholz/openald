// OpenALD single-board enclosure, 2026-11-24 unified envelope (still v1.0).
// Same outside as the MI03 case: 27.5 W x 89.75 L x 34.83 T, plan corner r 5, edge r 2, USB-C on the LEFT long side
// 30.3 mm from the top outer end, centre 7.55 mm below the front face, mouth 1.0 mm inside the side face, so all
// three OpenALD radios share one charging-dock pocket (they dock lying on that side).
// Two halves split at the PCB bottom face:
//   top    = front shell: front face, all side openings, LED tunnels, 2 bosses the board+holder screw into
//   bottom = back cover: snaps on (lip + 4 bumps); nothing is screwed to it, so the cell is swapped by popping it off
//   spacer = 0.8 mm plate between the PCB and the BH-18650-PC holder (clears the through-hole tails under it)
// All component positions come from case_params.scad (scripts/gen_case_params.py, from the KiCad board).
// Frame: X = PCB x (0 = USB-C / dock edge), Y = 0 at the jack end, Y = pcb_h at the top end, Z = 0 at the PCB bottom.
//
//   openscad -D 'part="top"'    -o case_top.stl    openald_case.scad
//   openscad -D 'part="bottom"' -o case_bottom.stl openald_case.scad
//   openscad -D 'part="spacer"' -o holder_spacer.stl openald_case.scad
include <case_params.scad>

part = "assembly";  // top | bottom | spacer | print | assembly | closed | cutaway | top_raw | bottom_raw | spacer_raw | tunnels_raw

// ---------------- shared envelope (keep identical to mi03_case.scad / feather case / dock) ----------------
env_T          = 34.83;  // outside thickness, front face to back face
usb_from_front = 7.55;   // USB-C centre below the front face
usb_mouth_in   = 1.0;    // USB-C mouth inside the side face
wall      = 2.0;
edge_r    = 2.0;    // rounding of the front/back edges
clr       = 0.5;    // PCB edge to inner wall (all four sides)
front_t   = 1.6;    // front face
floor_t   = 1.4;    // back face
// ---------------- tunables ----------------
lip_h = 1.4;  lip_t = 0.9;  fit = 0.15;      // back-cover lip into the front-shell rebate (stays under the USB-C shell at Z 1.6)
snap_ys = [14, 72];  snap_len = 8;  snap_bump = 0.3;
boss_r   = 2.0;    // front-shell bosses at the holder's two floor holes
pilot_d  = 1.7;    // M2 self-tapping
spacer_t = 0.8;    // holder spacer
spacer_clr = 0.2;
holder_shift = spacer_t;   // the holder sits this far below the PCB
// LED light tunnels (level bar + TP4056 charge LEDs): one sealed tunnel per 0603 LED
led_window = "open";  // "open" = filleted through-hole | "skin" = closed thin skin on the outer face
skin_t     = 0.4;
tun_in     = [2.0, 3.2]; // tunnel bore (x, y): the LEDs are rotated 90 degrees
tun_wall   = 0.7;
tun_gap    = 0.2;     // air between the tunnel walls and the PCB surface
bar_win    = [1.4, 2.4, 0.5];  // level-bar window (x, y), corner radius: three across = a bar that is vertical when docked
chg_win_d  = 1.6;
win_fillet = 0.4;
wheel_pocket_d = 1.0; wheel_pocket_h = 6.0;
usb_recess = [13.0, 7.6]; usb_recess_r = 3.0;   // OpenALD cable-plug recess (Y x Z) on the side face
usb_recess_gap = 0.55;                          // recess floor this far outside the receptacle mouth (MI03 value)
asm_fit   = 0.2;
label_depth = 0.4;  label_size = 1.8;
$fn = 48;

// ---------------- derived ----------------
in_x0 = -clr;  in_x1 = pcb_w + clr;
in_y0 = -clr;  in_y1 = pcb_h + clr;
in_r  = pcb_r + clr;   // 3.0
out_r = in_r + wall;   // 5.0 (MI03)
usb_zc = pcb_t + usb_h/2;
Ht = usb_zc + usb_from_front;   // front outer face
Hb = env_T - Ht;                // back outer face is at Z = -Hb
top_in = Ht - front_t;          // ceiling
bot_in = Hb - floor_t;          // floor top at Z = -bot_in
holder_low = -(holder_shift + holder_h);
assert(top_in >= pcb_t + top_tallest + 0.5, "ceiling too low for the tallest top part");
assert(-bot_in <= holder_low - 0.3, "back face too close to the holder");
assert(abs((in_x0-wall) - usb_mouth_x + usb_mouth_in) < 0.01, "USB-C mouth must be 1.0 inside the side face");
echo(str("Case outer: ", in_x1-in_x0+2*wall, " W x ", in_y1-in_y0+2*wall, " L x ", Ht+Hb, " T mm"));
echo(str("Front face Z ", Ht, ", ceiling ", top_in, ", floor top ", -bot_in, ", back face ", -Hb, ", holder low ", holder_low, " (air ", holder_low+bot_in, ")"));
echo(str("USB-C centre ", (in_y1+wall)-usb_y, " mm from the top outer end, ", Ht-usb_zc, " below the front face"));
echo(str("Switch knob protrudes ", sw_tip_x-(in_x1+wall), " mm beyond the right side; wheel ", wheel_xy[0]+wheel_r-(in_x1+wall)));

module rrect(x0,y0,x1,y1,r,h) { hull() for (x=[x0+r,x1-r]) for (y=[y0+r,y1-r]) translate([x,y,0]) cylinder(r=r,h=h); }
module rounded_shell(z0,z1) {
  hull() for (x=[in_x0-wall+out_r, in_x1+wall-out_r]) for (y=[in_y0-wall+out_r, in_y1+wall-out_r])
    for (z=[z0+edge_r, z1-edge_r]) translate([x,y,z]) rotate_extrude($fn=48) translate([out_r-edge_r,0]) circle(r=edge_r,$fn=24);
}
module cavity(z0=-bot_in, z1=top_in) { translate([0,0,z0]) rrect(in_x0,in_y0,in_x1,in_y1,in_r,z1-z0); }
module rr2d(w,h,r) { r2=min(r,w/2,h/2); hull() for (sx=[-1,1]) for (sy=[-1,1]) translate([sx*(w/2-r2),sy*(h/2-r2)]) circle(r=r2); }
// opening along local +Z; wall from z=0 (inside) to z=depth (outer surface); quarter-round outer fillet fr
module filleted_hole(w,h,cr,depth,fr,in_fr=0,n=10,z_in=-1) {
  translate([0,0,z_in]) linear_extrude(depth+1-z_in) rr2d(w,h,cr);
  if (fr>0) for (i=[0:n-1]) hull() for (k=[i,i+1]) {
    u=fr*k/n; e=fr-sqrt(max(fr*fr-u*u,0));
    translate([0,0,depth-fr+u]) linear_extrude(0.01) rr2d(w+2*e,h+2*e,cr+e);
  }
  if (fr>0) translate([0,0,depth-0.005]) linear_extrude(1) rr2d(w+2*fr,h+2*fr,cr+fr);
  if (in_fr>0) for (i=[0:n-1]) hull() for (k=[i,i+1]) {
    u=in_fr*k/n; e=in_fr-sqrt(max(in_fr*in_fr-u*u,0));
    translate([0,0,in_fr-u]) linear_extrude(0.01) rr2d(w+2*e,h+2*e,cr+e);
  }
}
module filleted_pocket(w,h,cr,depth,n=10) { translate([0,0,-depth]) filleted_hole(w-2*depth,h-2*depth,max(cr-depth,0.3),depth,depth,0,n,z_in=0); }

// ---------------- openings, used on both halves ----------------
function wheel_ch() = sqrt(pow(wheel_r,2)-pow(in_x1-wheel_xy[0],2));
sw_slot_l = abs(sw_on_y-sw_off_y)+sw_act_w+0.7;
module cutouts() {
  // 3.5 mm jack (jack end): 6.8 mm hole for the plug overmold, outer chamfer
  translate([jack_xy[0], in_y0+0.1, pcb_t+jack_axis_h]) rotate([90,0,0]) { cylinder(d=6.8,h=wall+1); translate([0,0,wall-0.8]) cylinder(d1=6.8,d2=8.6,h=0.9); }
  // thumbwheel (right side): pocket that thins the wall to 1 mm, slot through its floor
  ch = wheel_ch(); wz = pcb_t+(wheel_z0+wheel_z1)/2;
  translate([in_x1+wall, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90]) filleted_pocket(2*ch+5.0, wheel_pocket_h, 2.6, wheel_pocket_d);
  translate([in_x1, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90]) filleted_hole(2*ch+1.2, wheel_z1-wheel_z0+1.0, 1.0, wall-wheel_pocket_d, 0.5, 0.3);
  // power switch (right side)
  translate([in_x1, (sw_on_y+sw_off_y)/2, pcb_t+(sw_act_z0+sw_act_z1)/2]) rotate([0,90,0]) rotate([0,0,90])
    filleted_hole(sw_slot_l, sw_act_z1-sw_act_z0+0.7, 0.9, wall, 0.8, 0.3);
  // USB-C (left side = dock face): MI03 geometry: cable-plug recess 13.0 x 7.6 r 3 stopping 0.55 outside the mouth,
  // receptacle clearance through the rest of the wall
  translate([in_x0-wall-1, usb_y, usb_zc]) rotate([0,90,0]) rotate([0,0,90]) linear_extrude(1+(usb_mouth_x-usb_recess_gap)-(in_x0-wall)) rr2d(usb_recess[0], usb_recess[1], usb_recess_r);
  translate([in_x0+0.5, usb_y, usb_zc]) rotate([0,-90,0]) rotate([0,0,90]) filleted_hole(usb_w+0.5, usb_h+0.5, 1.4, wall+0.5, 0, 0);
}
module asm_notches() {   // top half: the wheel dial, switch knob and USB-C shell reach into/through the walls, so the
                         // wall below each is open down to the split; the bottom half fills it back up (asm_tabs)
  ch = wheel_ch(); wz = pcb_t+(wheel_z0+wheel_z1)/2;
  translate([in_x1-0.5, wheel_xy[1]-ch-0.6, -1]) cube([wall+2, 2*ch+1.2, 1+wz]);
  translate([in_x1-0.5, (sw_on_y+sw_off_y)/2-sw_slot_l/2, -1]) cube([wall+2, sw_slot_l, 1+pcb_t+(sw_act_z0+sw_act_z1)/2]);
  translate([usb_mouth_x-0.15, usb_y-(usb_w+0.5)/2, -1]) cube([in_x0+0.01-(usb_mouth_x-0.15), usb_w+0.5, 1+usb_zc]);
}
module asm_tabs() {      // bottom half: wheel and switch notches filled to 0.5 under the dial / knob (USB: the lip does it)
  ch = wheel_ch();
  intersection() { rounded_shell(-Hb,Ht); union() {
    translate([in_x1, wheel_xy[1]-ch-0.6+asm_fit, -0.01]) cube([wall+1, 2*ch+1.2-2*asm_fit, pcb_t+wheel_z0-0.5+0.01]);
    translate([in_x1, (sw_on_y+sw_off_y)/2-sw_slot_l/2+asm_fit, -0.01]) cube([wall+1, sw_slot_l-2*asm_fit, pcb_t+sw_act_z0-0.5+0.01]);
  } }
}
module switch_labels() {   // engraved ON / OFF next to the switch slot (right side)
  sl = sw_slot_l/2+0.8+0.6;  sgn = sw_on_y>sw_off_y ? 1 : -1;
  for (L=[["ON",sgn],["OFF",-sgn]])
    translate([in_x1+wall-label_depth, (sw_on_y+sw_off_y)/2 + L[1]*sl, pcb_t+(sw_act_z0+sw_act_z1)/2])
      rotate([90,0,90]) linear_extrude(label_depth+1) text(L[0], size=label_size, font="DejaVu Sans:style=Bold", halign=L[1]>0?"left":"right", valign="center");
}
// ---------------- LED light tunnels ----------------
module tunnel_walls(pts, bore=tun_in, w=tun_wall) {
  z0 = pcb_t + tun_gap;
  difference() {
    hull() for (p=pts) translate([p[0],p[1],z0]) linear_extrude(top_in-z0+0.01) rr2d(bore[0]+2*w, bore[1]+2*w, 0.6);
    for (p=pts) translate([p[0],p[1],z0-1]) linear_extrude(top_in-z0+1.02) rr2d(bore[0], bore[1], 0.3);
  }
}
module led_window(p,w,h,cr) {
  if (led_window=="skin") translate([p[0],p[1],top_in-0.01]) linear_extrude(front_t-skin_t+0.01) rr2d(w,h,cr);
  else translate([p[0],p[1],top_in]) filleted_hole(w,h,cr,front_t,win_fillet);
}
module led_tunnels() { tunnel_walls(bar_leds); tunnel_walls(chg_leds); }
module led_windows() { for (p=bar_leds) led_window(p,bar_win[0],bar_win[1],bar_win[2]); for (p=chg_leds) led_window(p,chg_win_d,chg_win_d,chg_win_d/2); }
module lip_outline(o,h) { rrect(in_x0-o,in_y0-o,in_x1+o,in_y1+o,in_r+o,h); }
// no lip/rebate along the straight part of the jack-end wall (the lip would show at the bottom of the 6.8 plug hole)
module jack_end_no_lip() { translate([in_x0+in_r, in_y0-wall-1, -1]) cube([in_x1-in_x0-2*in_r, wall+1, lip_h+3]); }

// ---------------- FRONT SHELL (Z 0 .. Ht) ----------------
module top_half() {
  difference() {
    union() {
      difference() { intersection() { rounded_shell(-Hb,Ht); translate([-50,-50,0]) cube([200,200,Ht+1]); } cavity(); }
      led_tunnels();
      for (s=screws) translate([s[0],s[1],pcb_t]) cylinder(r=boss_r, h=top_in-pcb_t+0.01);
    }
    translate([0,0,-0.01]) difference() { lip_outline(lip_t+fit, lip_h+0.3); translate([0,0,-1]) lip_outline(-0.01, lip_h+3); jack_end_no_lip(); }
    for (sx=[-1,1]) for (y=snap_ys) translate([sx>0 ? in_x1+lip_t+fit-0.01 : in_x0-lip_t-fit-snap_bump-0.1+0.01, y-(snap_len+0.6)/2, lip_h/2-0.5]) cube([snap_bump+0.1, snap_len+0.6, 1.0]);
    for (s=screws) translate([s[0],s[1],pcb_t-0.01]) cylinder(d=pilot_d, h=top_in-pcb_t-0.4);
    cutouts(); asm_notches(); led_windows(); switch_labels();
  }
}
// ---------------- BACK COVER (Z -Hb .. 0, lip to +lip_h) ----------------
module bottom_half() {
  difference() {
    union() {
      difference() { intersection() { rounded_shell(-Hb,Ht); translate([-50,-50,-Hb-1]) cube([200,200,Hb+1]); } cavity(-bot_in, 1); }
      translate([0,0,-0.01]) difference() { lip_outline(lip_t, lip_h+0.01); translate([0,0,-1]) lip_outline(0, lip_h+3); jack_end_no_lip(); }
      for (sx=[-1,1]) for (y=snap_ys) translate([sx*(sx>0 ? in_x1+lip_t-0.01 : -(in_x0-lip_t+0.01)), y, lip_h/2]) mirror([sx>0 ? 0 : 1,0,0])
        hull() { translate([0,-snap_len/2,-0.5]) cube([0.01, snap_len, 1.0]); translate([snap_bump,-snap_len/2+0.3,-0.25]) cube([0.01, snap_len-0.6, 0.5]); }
      asm_tabs();
    }
    cutouts();
    translate([pcb_w/2-3, in_y1+wall-0.8, -0.8]) cube([6, 2, 0.81]);   // pry notch at the top end
  }
}
// ---------------- holder spacer (Z -spacer_t .. 0) ----------------
module spacer() {
  difference() {
    translate([0,0,-spacer_t]) rrect(holder_box[0]+spacer_clr, holder_box[2]+spacer_clr, holder_box[1]-spacer_clr, holder_box[3]-spacer_clr, 1.0, spacer_t);
    for (s=screws) translate([s[0],s[1],-5]) cylinder(d=2.6, h=10);
    for (p=holder_pins) translate([p[0],p[1],-5]) cylinder(d=2.2, h=10);
    for (t=tails) translate([t[0],t[1],-5]) cylinder(d=t[2], h=10);
  }
}
module holder_ghost() {
  color("black",0.6) difference() {
    translate([holder_box[0],holder_box[2],holder_low]) cube([holder_box[1]-holder_box[0],holder_box[3]-holder_box[2],holder_h]);
    translate([(holder_box[0]+holder_box[1])/2, holder_box[2]+4, holder_low+holder_h-18.6/2]) rotate([-90,0,0]) cylinder(d=18.6, h=holder_box[3]-holder_box[2]-8);
  }
}
module pcb_ghost() {
  color("green",0.6) rrect(0,0,pcb_w,pcb_h,pcb_r,pcb_t);
  holder_ghost();
  color("dimgray") translate([wheel_xy[0],wheel_xy[1],pcb_t+wheel_z0]) cylinder(r=wheel_r,h=wheel_z1-wheel_z0);
}

if (part=="top")         translate([0,0,Ht]) rotate([180,0,0]) top_half();   // front face on the bed
else if (part=="bottom") translate([0,0,Hb]) bottom_half();                  // back face on the bed
else if (part=="spacer") translate([0,0,spacer_t]) spacer();
else if (part=="tunnels_raw") led_tunnels();
else if (part=="top_raw") top_half();
else if (part=="bottom_raw") bottom_half();
else if (part=="spacer_raw") spacer();
else if (part=="closed") {   // needs /tmp/pcb_assembly.stl from check_case_fit.py
  color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("white") import("/tmp/pcb_assembly.stl"); color("orange") spacer();
}
else if (part=="cutaway") {
  K=[bar_leds[1][0],-20,-40];
  color("lightgray")      intersection() { bottom_half(); translate(K) cube([100,200,80]); }
  color("lightsteelblue") intersection() { top_half();    translate(K) cube([100,200,80]); }
  color("white") import("/tmp/pcb_assembly_cut.stl");
}
else if (part=="print")  { translate([0,0,Hb]) bottom_half(); translate([pcb_w+12,pcb_h,Ht]) rotate([180,0,0]) top_half(); translate([2*pcb_w+24,0,spacer_t]) spacer(); }
else { color("lightgray") bottom_half(); color("lightblue",0.55) translate([0,0,14]) top_half(); color("orange") translate([0,0,-3]) spacer(); pcb_ghost(); }
