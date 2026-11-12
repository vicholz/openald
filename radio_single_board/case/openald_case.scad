// OpenALD enclosure - two halves split at the PCB bottom face, rounded corners.
// All component cutouts come from case_params.scad, generated from the KiCad
// board by scripts/gen_case_params.py.  Frame: X = PCB x, Y = 0 at the USB-C edge,
// Y = pcb_h at the jack/LED/button edge, Z = 0 at PCB bottom face.
//
//   openscad -D 'part="top"'    -o case_top.stl    openald_case.scad
//   openscad -D 'part="bottom"' -o case_bottom.stl openald_case.scad
//   openscad -D 'part="plunger"' -o button_plunger.stl openald_case.scad
include <case_params.scad>

part      = "assembly";  // "top" | "bottom" | "plunger" | "assembly" | "print"
fastener  = "insert";    // "insert" (M2 heat-set insert in top) | "nut" (M2 hex nut pocket on top face)

// ---------------- tunables ----------------
wall      = 2.0;    // side wall
floor_t   = 1.6;    // bottom floor / top ceiling thickness
clr       = 0.5;    // PCB edge to inner wall
edge_r    = 2.0;    // vertical-edge rounding of the outer shell (top and bottom faces)
top_clear = 0.6;    // air above the tallest top-side part
bot_clear = 0.7;    // air below the battery holder
lip_h     = 1.2;    // alignment lip on bottom half
lip_t     = 0.9;
fit       = 0.15;   // lip clearance
// screws: M2 from below, through bottom boss + PCB into top boss
screw_d   = 2.4;    // clearance hole
head_d    = 4.5;    // counterbore for M2 cheese/socket head
screw_l   = fastener=="insert" ? 12 : 16;   // M2x12 into insert, M2x16 into nut (ends flush with top)
insert_d  = 3.2;    // M2 heat-set insert hole (OD 3.2-3.5 inserts: adjust)
insert_l  = 4.5;
nut_af    = 4.3;    // M2 nut across flats + clearance
nut_t     = 1.8;
// LED light tunnels (battery-level bar + TP4056 charge LEDs): one sealed tunnel per 0603 LED
led_window = "open";  // "open" = filleted through-hole (default) | "skin" = closed thin skin on the outer face
skin_t     = 0.4;     // skin thickness for led_window="skin" (2 layers at 0.2 mm; only translucent filament glows through)
tun_in     = [3.2, 2.0]; // tunnel bore (x, y) around each 0603 LED (pads + 0.3 mm)
tun_wall   = 0.8;     // tunnel wall (shared between neighbours)
tun_gap    = 0.2;     // air between the tunnel walls and the PCB surface
bar_win    = [2.4, 1.4, 0.5];  // level-bar window w x h, corner radius (a "bar segment")
chg_win_d  = 1.6;     // charge-LED window diameter
win_fillet = 0.4;     // rounded outer rim of every LED window
wheel_pocket_d = 1.0; // thumbwheel pocket depth (wall left under it = wall - this)
wheel_pocket_h = 6.0; // pocket height (Z)
usb_pocket_d = 1.5;   // USB-C plug-body pocket depth
label_depth  = 0.4;   // engraved ON/OFF text
label_size   = 1.8;
$fn = 48;

// ---------------- derived ----------------
in_x0 = -clr;  in_x1 = pcb_w + clr;
in_y0 = -clr;  in_y1 = pcb_h + clr;
in_r  = pcb_r + clr;
out_r = in_r + wall;                       // plan-view corner radius of the case
top_in  = pcb_t + top_tallest + top_clear; // interior ceiling height (z)
bot_in  = holder_h + bot_clear;            // interior depth below PCB
Ht = top_in + floor_t;                     // top outer z
Hb = bot_in + floor_t;                     // bottom outer z (negative)
// screw head seat height chosen so the screw ends 0.5 short of the insert-hole bottom, or flush with the top face (nut)
bot_boss_h = fastener=="insert" ? screw_l - (pcb_t + insert_l - 0.5) : screw_l - Ht;
echo(str("Case outer size: ", in_x1-in_x0+2*wall, " x ", in_y1-in_y0+2*wall, " x ", Ht+Hb, " mm"));
echo(str("LED tunnels: walls end ", tun_gap, " mm above the PCB; windows ", led_window));
echo(str("Switch knob protrudes ", sw_tip_x-(in_x1+wall), " mm beyond the side wall"));
echo(str("Top half height ", Ht, " mm, bottom half height ", Hb, " mm"));
echo(str("Screws: 4x M2 x ", screw_l, " mm (", fastener, "), head seat ", bot_boss_h, " mm below PCB"));

module rrect(x0,y0,x1,y1,r,h) {           // rounded rectangle prism
  translate([0,0,0]) hull() for (x=[x0+r,x1-r]) for (y=[y0+r,y1-r]) translate([x,y,0]) cylinder(r=r,h=h);
}
module rounded_shell(z0,z1) {             // outer solid with rounded plan corners and rounded top/bottom edges
  hull() for (x=[in_x0-wall+out_r, in_x1+wall-out_r]) for (y=[in_y0-wall+out_r, in_y1+wall-out_r])
    for (z=[z0+edge_r, z1-edge_r]) translate([x,y,z])
      rotate_extrude($fn=48) translate([out_r-edge_r,0]) circle(r=edge_r,$fn=24);
}
module cavity() {
  translate([0,0,-bot_in]) rrect(in_x0,in_y0,in_x1,in_y1,in_r,bot_in+top_in);
}

// ---------------- fillet helpers ----------------
// 2D rounded rectangle centred on the origin (works down to a circle when r = w/2 = h/2)
module rr2d(w,h,r) { r2=min(r,w/2,h/2); hull() for (sx=[-1,1]) for (sy=[-1,1]) translate([sx*(w/2-r2),sy*(h/2-r2)]) circle(r=r2); }
// Opening cutter along local +Z. The wall runs from z=0 (inside) to z=depth (outer surface).
// The opening is a w x h rounded rectangle (corner radius cr) whose outer edge is rounded
// with a quarter-circle fillet of radius fr (tangent to both the hole wall and the outer surface).
module filleted_hole(w,h,cr,depth,fr,in_fr=0,n=10,z_in=-1) {
  translate([0,0,z_in]) linear_extrude(depth+1-z_in) rr2d(w,h,cr);
  if (fr>0) for (i=[0:n-1]) hull() for (k=[i,i+1]) {
    u=fr*k/n; e=fr-sqrt(max(fr*fr-u*u,0));
    translate([0,0,depth-fr+u]) linear_extrude(0.01) rr2d(w+2*e,h+2*e,cr+e);
  }
  if (fr>0) translate([0,0,depth-0.005]) linear_extrude(1) rr2d(w+2*fr,h+2*fr,cr+fr);
  if (in_fr>0) for (i=[0:n-1]) hull() for (k=[i,i+1]) {       // same rounding on the inside edge
    u=in_fr*k/n; e=in_fr-sqrt(max(in_fr*in_fr-u*u,0));
    translate([0,0,in_fr-u]) linear_extrude(0.01) rr2d(w+2*e,h+2*e,cr+e);
  }
}
// Shallow pocket in the outer surface: rounded-rectangle outline, rim rounded with radius = depth,
// so the pocket wall is one smooth quarter-round from the floor to the outer surface.
module filleted_pocket(w,h,cr,depth,n=10) {
  translate([0,0,-depth]) filleted_hole(w-2*depth,h-2*depth,max(cr-depth,0.3),depth,depth,0,n,z_in=0);
}

// --- every opening through the walls, used on both halves ---
module cutouts() {
  zc = pcb_t;   // top surface of PCB
  // 3.5 mm jack (top edge): 6.8 mm hole for the plug overmold (7.0 would be tangent to the ceiling), outer chamfer
  translate([jack_xy[0], in_y1-0.1, zc+jack_axis_h]) rotate([-90,0,0]) {
    cylinder(d=6.8,h=wall+1);
    translate([0,0,wall-0.8]) cylinder(d1=6.8,d2=8.6,h=0.9);
  }
  // battery-check button: plunger hole + inner counterbore for the plunger flange
  translate([btn_xy[0], in_y1-0.1, zc+btn_axis_h]) rotate([-90,0,0]) {
    cylinder(d=2.5,h=wall+1);
    translate([0,0,-1]) cylinder(d=4.4,h=1+1.0+0.1);
  }
  // ---- thumbwheel (right side): smooth pocket that thins the wall to 1 mm, slot through its floor
  ch = sqrt(pow(wheel_r,2)-pow(in_x1-wheel_xy[0],2));  // half-chord where the wheel meets the inner wall
  wz = zc+(wheel_z0+wheel_z1)/2;
  translate([in_x1+wall, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90])
    filleted_pocket(2*ch+5.0, wheel_pocket_h, 2.6, wheel_pocket_d);
  translate([in_x1, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90])
    filleted_hole(2*ch+1.2, wheel_z1-wheel_z0+1.0, 1.0, wall-wheel_pocket_d, 0.5, 0.3);
  // ---- power switch (right side): filleted slot; actuator travel + 0.35 mm clearance all round
  translate([in_x1, (sw_on_y+sw_off_y)/2, zc+(sw_act_z0+sw_act_z1)/2]) rotate([0,90,0]) rotate([0,0,90])
    filleted_hole(abs(sw_on_y-sw_off_y)+sw_act_w+0.7, sw_act_z1-sw_act_z0+0.7, 0.9, wall, 0.8, 0.3);
  // ---- USB-C (bottom edge): smooth pocket for the cable's plug body + filleted connector opening
  translate([usb_xy[0], in_y0-wall, zc+usb_h/2]) rotate([90,0,0]) {
    filleted_pocket(12.8, 7.4, 3.0, usb_pocket_d);
  }
  translate([usb_xy[0], in_y0, zc+usb_h/2]) rotate([90,0,0])
    filleted_hole(usb_w+0.5, usb_h+0.5, 1.4, wall-usb_pocket_d, 0.4, 0.3);
}

// engraved position labels next to the power-switch slot (readable from the right side)
module switch_labels() {
  zc=pcb_t; sl=(abs(sw_on_y-sw_off_y)+sw_act_w+0.7)/2+0.8+0.6;   // half slot + fillet + gap
  sgn = sw_on_y>sw_off_y ? 1 : -1;
  for (L=[["ON",sgn],["OFF",-sgn]])
    translate([in_x1+wall-label_depth, (sw_on_y+sw_off_y)/2 + L[1]*sl, zc+(sw_act_z0+sw_act_z1)/2])
      rotate([90,0,90]) linear_extrude(label_depth+1)
        text(L[0], size=label_size, font="DejaVu Sans:style=Bold", halign=L[1]>0?"left":"right", valign="center");
}

// ---- LED light tunnels: every 0603 LED gets its own walled bore from the ceiling down to tun_gap above the
// PCB, so each window only sees its own LED (no bleed between the bar segments or into the case).
module tunnel_walls(pts) {
  z0 = pcb_t + tun_gap;
  difference() {
    for (p=pts) translate([p[0],p[1],z0]) linear_extrude(top_in-z0+0.01) rr2d(tun_in[0]+2*tun_wall, tun_in[1]+2*tun_wall, 0.6);
    for (p=pts) translate([p[0],p[1],z0-1]) linear_extrude(top_in-z0+1) rr2d(tun_in[0], tun_in[1], 0.3);
  }
}
module led_window(p,w,h,cr) {
  if (led_window=="skin") translate([p[0],p[1],top_in-0.01]) linear_extrude(floor_t-skin_t+0.01) rr2d(w,h,cr);
  else translate([p[0],p[1],top_in]) filleted_hole(w,h,cr,floor_t,win_fillet);
}
module led_tunnels()  { tunnel_walls(bar_leds); tunnel_walls(chg_leds); }
module led_windows()  {
  for (p=bar_leds) led_window(p,bar_win[0],bar_win[1],bar_win[2]);
  for (p=chg_leds) led_window(p,chg_win_d,chg_win_d,chg_win_d/2);
}

module top_half() {
  difference() {
    union() {
      difference() {
        intersection() { rounded_shell(-Hb,Ht); translate([-50,-50,0]) cube([200,200,Ht+1]); }
        cavity();
      }
      led_tunnels();
      // bosses that clamp the PCB from above (filleted into the corner walls)
      for (h=holes) intersection() {
        translate([0,0,pcb_t]) rrect(in_x0,in_y0,in_x1,in_y1,in_r,top_in-pcb_t+0.01);
        hull() {
          translate([h[0],h[1],pcb_t]) cylinder(r=min(2.6,top_boss_room), h=top_in-pcb_t);
          translate([h[0]<pcb_w/2?in_x0-1:in_x1-1, h[1]<pcb_h/2?in_y0-1:in_y1-1, pcb_t]) cube([2,2,top_in-pcb_t]);
        }
      }
    }
    // rebate for the bottom lip
    translate([0,0,-0.01]) difference() {
      rrect(in_x0-lip_t-fit,in_y0-lip_t-fit,in_x1+lip_t+fit,in_y1+lip_t+fit,in_r+lip_t+fit,lip_h+0.3);
      translate([0,0,-1]) rrect(in_x0-0.01,in_y0-0.01,in_x1+0.01,in_y1+0.01,in_r,lip_h+3);
    }
    for (h=holes) translate([h[0],h[1],0]) {
      if (fastener=="insert") translate([0,0,pcb_t-0.01]) cylinder(d=insert_d,h=insert_l);
      else { cylinder(d=screw_d,h=Ht+1); translate([0,0,Ht-nut_t]) cylinder(d=nut_af/cos(30),h=nut_t+1,$fn=6); }
    }
    cutouts();
    led_windows();
    switch_labels();
  }
}

module bottom_half() {
  difference() {
    union() {
      difference() {
        intersection() { rounded_shell(-Hb,Ht); translate([-50,-50,-Hb-1]) cube([200,200,Hb+1]); }
        cavity();
      }
      // alignment lip
      difference() {
        rrect(in_x0-lip_t,in_y0-lip_t,in_x1+lip_t,in_y1+lip_t,in_r+lip_t,lip_h);
        translate([0,0,-1]) rrect(in_x0,in_y0,in_x1,in_y1,in_r,lip_h+2);
      }
      // corner columns: floor to PCB, filleted into the walls
      for (h=holes) intersection() {
        translate([0,0,-bot_in-0.01]) rrect(in_x0,in_y0,in_x1,in_y1,in_r,bot_in+0.01);
        hull() {
          translate([h[0],h[1],-bot_in]) cylinder(r=min(3.2,bot_boss_room), h=bot_in);
          translate([h[0]<pcb_w/2?in_x0-1:in_x1-1, h[1]<pcb_h/2?in_y0-1:in_y1-1, -bot_in]) cube([2,2,bot_in]);
        }
      }
    }
    for (h=holes) translate([h[0],h[1],0]) {
      translate([0,0,-bot_boss_h-0.01]) cylinder(d=screw_d,h=bot_boss_h+1);
      translate([0,0,-Hb-1]) cylinder(d=head_d,h=Hb+1-bot_boss_h);
    }
    cutouts();
  }
}

module plunger() {  // print 1x, flange down; sits inside the counterbore behind the button hole
  cylinder(d=4.0,h=0.8);
  cylinder(d=2.2,h=0.8+1.0+1.0);   // 1.0 through remaining wall + 1.0 proud of the case
}

module pcb_ghost() {
  color("green",0.6) rrect(0,0,pcb_w,pcb_h,pcb_r,pcb_t);
  color("black",0.5) translate([holder_box[0],holder_box[2],-holder_h]) cube([holder_box[1]-holder_box[0],holder_box[3]-holder_box[2],holder_h]);
  color("dimgray") translate([wheel_xy[0],wheel_xy[1],pcb_t+wheel_z0]) cylinder(r=wheel_r,h=wheel_z1-wheel_z0);
}

if (part=="top")         translate([0,0,Ht]) rotate([180,0,0]) top_half();       // ceiling on the bed
else if (part=="bottom") translate([0,0,Hb]) bottom_half();                       // floor on the bed
else if (part=="plunger") plunger();
else if (part=="tunnels_raw") led_tunnels();     // tunnel walls only, assembly pose (fit check)
else if (part=="closed") {   // closed case with the assembled PCB (needs /tmp/pcb_assembly.stl from check_case_fit.py)
  color("lightgray") bottom_half(); color("lightsteelblue") top_half();
  color("white") import("/tmp/pcb_assembly.stl");
}
else if (part=="cutaway") {   // closed case cut lengthwise through the vertical level-bar column (looking from the left side)
  K=[bar_leds[0][0],-20,-40];
  color("lightgray")      intersection() { bottom_half(); translate(K) cube([100,200,80]); }
  color("lightsteelblue") intersection() { top_half();    translate(K) cube([100,200,80]); }
  color("white") import("/tmp/pcb_assembly_cut.stl");   // pre-cut at the same plane by build_case.sh
}
else if (part=="top_raw") top_half();          // assembly pose, for interference checks
else if (part=="bottom_raw") bottom_half();
else if (part=="print")  { translate([0,0,Hb]) bottom_half(); translate([pcb_w+12,pcb_h,Ht]) rotate([180,0,0]) top_half(); }
else { color("lightgray") bottom_half(); color("lightblue",0.55) translate([0,0,12]) top_half(); pcb_ghost(); }
