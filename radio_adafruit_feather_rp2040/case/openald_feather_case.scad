// OpenALD Feather RP2040 v1.0 - enclosure (top half, bottom half) + internal frame.
// Case frame: X across (centre 19), Y = 0 at the USB-C receptacle face (+Y toward the jack end), Z = 0 at the
// Feather's bottom face.  The lowest 2 in (Y -2.5 .. 48.3) is the same solid as the OpenALD single-board case
// (43.0 x 33.41 section, R5.5 plan corners, R2 edges, same USB-C opening and plug-body recess) so it fits the dock.
// Above that the body tapers out by 1.25 mm per side (Y 50.3 .. 54.3) to 45.5 mm wide.
// All positions come from case_params.scad (generated from scripts/layout.py + the KiCad controls board).
include <case_params.scad>

part = "assembly";  // top | bottom | frame | assembly | print | closed | top_raw | bottom_raw | frame_raw | section

// ---------------- printing / fit settings (edit) ----------------
lip_h = 1.2; lip_t = 0.9; fit = 0.15;              // alignment lip on the bottom half, rebate in the top
screw_d = 2.4; head_d = 4.5; screw_l = 12;         // M2 x 12 from the back into heat-set inserts in the top half
insert_d = 3.2; insert_l = 4.5;
tun_wall = 0.6; tun_gap = 0.2;                     // LED light tunnels (walls stop 0.2 above the board)
win_d = 1.6; win_fillet = 0.4;                     // LED windows in the top skin
reset_d = 1.4;                                     // pin-hole over the Feather RESET button
deck_clr = 0.35;                                   // frame deck to the inner walls
fm_ledge = 1.5;                                    // FM board rests on a 1.5 mm ledge (z 0 .. fm z0)
fm_posts = true;                                   // top-half posts on the (ESTIMATED) FM corner holes
usb_pocket_d = 1.5; label_depth = 0.4; label_size = 1.8;
wheel_pocket_d = 1.0; wheel_pocket_h = 6.0;
$fn = 40;

TOP_OUT = TOP_IN + TOP_T;                          // 9.8
X0O = IN_X0-WALL; X1O = IN_X1+WALL;                // -2.5 .. 40.5 (dock section)
X0OU = IN_X0U-WALL; X1OU = IN_X1U+WALL;            // -3.75 .. 41.75 (upper body)
echo(str("Dock section: ", X1O-X0O, " x ", TOP_OUT-BOT_OUT, " mm (Y ", Y_OUT0, " .. ", J0, ")"));
echo(str("Upper body:   ", X1OU-X0OU, " x ", TOP_OUT-BOT_OUT, " mm (Y ", J1, " .. ", Y_OUT1, "); length ", Y_OUT1-Y_OUT0));

// ---------------- 2D helpers ----------------
module rr2d(w,h,r) { r2=min(r,w/2,h/2); hull() for (sx=[-1,1]) for (sy=[-1,1]) translate([sx*(w/2-r2),sy*(h/2-r2)]) circle(r=r2); }
module slab2d(y,x0,x1) { translate([x0,y-0.005]) square([x1-x0,0.01]); }
module in2d_raw() {                                  // interior plan outline
  hull() { for (x=[IN_X0+IN_R, IN_X1-IN_R]) translate([x,Y_IN0+IN_R]) circle(r=IN_R,$fn=64); slab2d(J0,IN_X0,IN_X1); }
  hull() { slab2d(J0,IN_X0,IN_X1); slab2d(J1,IN_X0U,IN_X1U); }
  hull() { slab2d(J1,IN_X0U,IN_X1U); for (x=[IN_X0U+TOP_IN_R, IN_X1U-TOP_IN_R]) translate([x,Y_IN1-TOP_IN_R]) circle(r=TOP_IN_R,$fn=32); }
}
module in2d(d=0) { if (d==0) in2d_raw(); else offset(r=d) in2d_raw(); }
// X at the inner wall for a given Y (both sides) - used to fillet bosses into the wall
function in_x0_at(y) = y<=J0 ? IN_X0 : (y>=J1 ? IN_X0U : IN_X0+(IN_X0U-IN_X0)*(y-J0)/(J1-J0));
function in_x1_at(y) = y<=J0 ? IN_X1 : (y>=J1 ? IN_X1U : IN_X1+(IN_X1U-IN_X1)*(y-J0)/(J1-J0));

// ---------------- outer shell (union of hulls; dock section is an exact copy of the single-board case) -------------
module torus_at(x,y,z,R) { translate([x,y,z]) rotate_extrude($fn=48) intersection() {   // clipped at the axis when R < 2*EDGE_R
    translate([R-EDGE_R,0]) circle(r=EDGE_R,$fn=24); translate([0,-EDGE_R-1]) square([R+1,2*EDGE_R+2]); } }
module xsec(y,x0,x1) {    // XZ section (rounded rectangle, R = EDGE_R) as a 0.01 mm slab at Y
  translate([0,y+0.005,0]) rotate([90,0,0]) linear_extrude(0.01)
    hull() for (x=[x0+EDGE_R,x1-EDGE_R]) for (z=[BOT_OUT+EDGE_R,TOP_OUT-EDGE_R]) translate([x,z]) circle(r=EDGE_R,$fn=24);
}
module shell() {
  hull() { for (x=[X0O+OUT_R, X1O-OUT_R]) for (z=[BOT_OUT+EDGE_R, TOP_OUT-EDGE_R]) torus_at(x,Y_OUT0+OUT_R,z,OUT_R); xsec(J0,X0O,X1O); }
  hull() { xsec(J0,X0O,X1O); xsec(J1,X0OU,X1OU); }
  hull() { xsec(J1,X0OU,X1OU); for (x=[X0OU+TOP_OUT_R, X1OU-TOP_OUT_R]) for (z=[BOT_OUT+EDGE_R, TOP_OUT-EDGE_R]) torus_at(x,Y_OUT1-TOP_OUT_R,z,TOP_OUT_R); }
}
module cavity() { translate([0,0,FLOOR_Z]) linear_extrude(TOP_IN-FLOOR_Z) in2d(); }

// ---------------- fillet helpers (same as the single-board case) ----------------
module filleted_hole(w,h,cr,depth,fr,in_fr=0,n=10,z_in=-1) {
  translate([0,0,z_in]) linear_extrude(depth+1-z_in) rr2d(w,h,cr);
  if (fr>0) for (i=[0:n-1]) hull() for (k=[i,i+1]) { u=fr*k/n; e=fr-sqrt(max(fr*fr-u*u,0));
    translate([0,0,depth-fr+u]) linear_extrude(0.01) rr2d(w+2*e,h+2*e,cr+e); }
  if (fr>0) translate([0,0,depth-0.005]) linear_extrude(1) rr2d(w+2*fr,h+2*fr,cr+fr);
  if (in_fr>0) for (i=[0:n-1]) hull() for (k=[i,i+1]) { u=in_fr*k/n; e=in_fr-sqrt(max(in_fr*in_fr-u*u,0));
    translate([0,0,in_fr-u]) linear_extrude(0.01) rr2d(w+2*e,h+2*e,cr+e); }
}
module filleted_pocket(w,h,cr,depth,n=10) { translate([0,0,-depth]) filleted_hole(w-2*depth,h-2*depth,max(cr-depth,0.3),depth,depth,0,n,z_in=0); }

// ---------------- openings ----------------
module cutouts() {
  zc = CB_Z0 + CB_T;   // controls-board top = Feather top = 1.6
  // USB-C (bottom face) - identical to the single-board case: plug-body pocket + filleted receptacle opening
  translate([USB_X, Y_IN0-WALL, USB_Z]) rotate([90,0,0]) filleted_pocket(12.8, 7.4, 3.0, usb_pocket_d);
  translate([USB_X, Y_IN0, USB_Z]) rotate([90,0,0]) filleted_hole(USB_W+0.5, USB_H+0.5, 1.4, WALL-usb_pocket_d, 0.4, 0.3);
  // 3.5 mm jack on the FM module (top end wall); position is an ESTIMATE from the module photo - edit layout.py
  translate([FM_JACK_X, Y_IN1-0.1, fm_box[4]+fm_box[5]+FM_JACK_AXIS_H]) rotate([-90,0,0]) {
    cylinder(d=FM_JACK_HOLE_D,h=WALL+1); translate([0,0,WALL-0.8]) cylinder(d1=FM_JACK_HOLE_D,d2=FM_JACK_HOLE_D+1.8,h=0.9); }
  // thumbwheel (right side): pocket thins the wall to 1 mm, slot through its floor
  ch = sqrt(pow(wheel_r,2)-pow(IN_X1U-wheel_xy[0],2));
  wz = zc+(wheel_z0+wheel_z1)/2;
  translate([IN_X1U+WALL, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90]) filleted_pocket(2*ch+5.0, wheel_pocket_h, 2.6, wheel_pocket_d);
  translate([IN_X1U, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90]) filleted_hole(2*ch+1.2, wheel_z1-wheel_z0+1.0, 1.0, WALL-wheel_pocket_d, 0.5, 0.3);
  // power switch (right side)
  translate([IN_X1U, sw_y, zc+(sw_act_z0+sw_act_z1)/2]) rotate([0,90,0]) rotate([0,0,90])
    filleted_hole(abs(sw_on_y-sw_off_y)+sw_act_w+0.7, sw_act_z1-sw_act_z0+0.7, 0.9, WALL, 0.8, 0.3);
}
module switch_labels() {   // engraved under the two ends of the switch slot (right side, top half)
  for (L=[["ON",sw_on_y+0.6],["OFF",sw_off_y-0.6]])
    translate([IN_X1U+WALL-label_depth, L[1], 1.9]) rotate([90,0,90]) linear_extrude(label_depth+1)
      text(L[0], size=1.5, font="DejaVu Sans:style=Bold", halign="center", valign="center");
}

// ---------------- LEDs: tunnels + windows ----------------
// [x, y, bore_x, bore_y, board_top_z]; Feather CHG (amber, MCP73831), Feather red D13, Feather NeoPixel,
// controls-board red CHG + green FULL mirrors (above the dock line, visible while docked)
leds = [[f_led_chg[0],f_led_chg[1],2.0,1.4], [f_led_red[0],f_led_red[1],1.4,2.0], [f_led_neo[0],f_led_neo[1],2.6,2.6],
        [cb_leds[0][0],cb_leds[0][1],2.6,1.8], [cb_leds[1][0],cb_leds[1][1],2.6,1.8]];
usb_env = f_parts[21];
module part_keepout() {   // Feather components + 0.25 (tunnel walls must not land on parts)
  for (p=f_parts) translate([p[0]-0.25,p[2]-0.25,p[4]-0.01]) cube([p[1]-p[0]+0.5,p[3]-p[2]+0.5,p[5]-p[4]+0.26]);
}
module led_tunnels() {
  z0 = 1.6 + tun_gap;
  difference() {
    for (p=leds) translate([p[0],p[1],z0]) linear_extrude(TOP_IN-z0+0.01) rr2d(p[2]+2*tun_wall, p[3]+2*tun_wall, 0.5);
    for (p=leds) translate([p[0],p[1],z0-1]) linear_extrude(TOP_IN-z0+1) rr2d(p[2], p[3], 0.3);
    part_keepout();
  }
}
module led_windows() { for (p=leds) translate([p[0],p[1],TOP_IN]) filleted_hole(win_d,win_d,win_d/2,TOP_T,win_fillet); }

// ---------------- screws ----------------
function side_cube(s) = s[1]<10 ? [s[0]<19?IN_X0-1:IN_X1-1, Y_IN0-1] : [s[0]<19?in_x0_at(s[1])-1.5:in_x1_at(s[1])-0.5, s[1]-1];
insert_top = insert_l;            // insert hole z 0 .. 4.5
head_seat = insert_top - 0.5 - screw_l;   // screw tip 0.5 short of the insert-hole bottom
module boss(s,r,z0,z1) { intersection() {
  translate([0,0,z0]) linear_extrude(z1-z0) in2d(0.01);
  hull() { translate([s[0],s[1],z0]) cylinder(r=r,h=z1-z0); c=side_cube(s); translate([c[0],c[1],z0]) cube([2,2,z1-z0]); } } }

// ---------------- top half ----------------
module top_half() {
  difference() {
    union() {
      difference() { intersection() { shell(); translate([-50,-50,0]) cube([200,200,TOP_OUT+1]); } cavity(); }
      led_tunnels();
      for (s=screws) boss(s,2.6,0,TOP_IN+0.01);
      // Feather clamp posts on its 4 mounting holes (press on the board top around the hole)
      for (h=feather_holes) translate([h[0],h[1],1.6+0.05]) cylinder(d=3.4,h=TOP_IN-1.65+0.01);
      // RESET pin-hole guide tube (paper clip), stops 0.5 above the button
      translate([f_btn_reset[0],f_btn_reset[1],4.0]) cylinder(d=reset_d+1.6,h=TOP_IN-4.0+0.01);
      // controls-board hold-downs on the two peg holes
      for (h=cb_holes) translate([h[0],h[1],CB_Z0+CB_T+0.05]) cylinder(d=3.2,h=TOP_IN-CB_T-0.05+0.01);
      // FM module hold-downs (corner holes - ESTIMATED positions)
      if (fm_posts) for (x=[fm_box[0]+FM_HOLE_INSET, fm_box[1]-FM_HOLE_INSET]) for (y=[fm_box[2]+FM_HOLE_INSET, fm_box[3]-FM_HOLE_INSET])
        translate([x,y,fm_box[4]+fm_box[5]+0.05]) cylinder(d=3.6,h=TOP_IN-fm_box[4]-fm_box[5]-0.05+0.01);
    }
    translate([0,0,-0.01]) difference() { linear_extrude(lip_h+0.3) in2d(lip_t+fit); translate([0,0,-1]) linear_extrude(lip_h+3) in2d(-0.01); }
    for (s=screws) translate([s[0],s[1],-0.01]) cylinder(d=insert_d,h=insert_top+0.01);
    for (h=cb_holes) translate([h[0],h[1],CB_T-0.1]) cylinder(d=CB_HOLE_D+0.2,h=1.2);      // peg-tip relief
    for (h=feather_holes) translate([h[0],h[1],1.5]) cylinder(d=2.3,h=1.2);
    translate([f_btn_reset[0],f_btn_reset[1],3.9]) cylinder(d=reset_d,h=TOP_IN);
    translate([f_btn_reset[0],f_btn_reset[1],TOP_OUT-0.4]) cylinder(d1=reset_d,d2=reset_d+0.9,h=0.45);
    cutouts(); led_windows(); switch_labels();
  }
}

// ---------------- bottom half ----------------
module bottom_half() {
  difference() {
    union() {
      difference() { intersection() { shell(); translate([-50,-50,BOT_OUT-1]) cube([200,200,-BOT_OUT+1]); } cavity(); }
      difference() { linear_extrude(lip_h) in2d(lip_t); translate([0,0,-1]) linear_extrude(lip_h+2) in2d(); }
      for (s=screws) boss(s,3.2,FLOOR_Z-0.01,0);
      // holder corner fences (1.0 wide, 2.0 tall, 0.3 clearance)
      hb=holder_box;
      for (cx=[0,1]) for (cy=[0,1]) {
        x = cx==0 ? hb[0]-0.3-1.0 : hb[1]+0.3; y = cy==0 ? hb[2]-0.3-1.0 : hb[3]+0.3;
        translate([x, cy==0?y:y-4+1.0, FLOOR_Z-0.01]) cube([1.0,5.0,2.0]);
        translate([cx==0?x:x-4+1.0, y, FLOOR_Z-0.01]) cube([5.0,1.0,2.0]);
      }
      // deck supports: posts from the floor to the frame deck, in the side channels beside the holder
      for (l=legs) translate([l[0]-leg_w[0]/2,l[1]-leg_w[1]/2,FLOOR_Z-0.01]) cube([leg_w[0],leg_w[1],DECK_Z0-0.05-FLOOR_Z+0.01]);
    }
    for (s=screws) { translate([s[0],s[1],head_seat-0.01]) cylinder(d=screw_d,h=-head_seat+1);
                     translate([s[0],s[1],BOT_OUT-1]) cylinder(d=head_d,h=head_seat-BOT_OUT+1); }
    // grooves for the holder's PC pins, bent flat under the holder toward its ends (wire soldered past the end)
    for (i=[0,1]) { p=holder_pins[i]; y0 = i==0 ? holder_box[2]-1.8 : p[1]-0.8; y1 = i==0 ? p[1]+0.8 : holder_box[3]+1.8;
      translate([p[0]-1.0, y0, FLOOR_Z-0.6]) cube([2.0, y1-y0, 0.61]); }
    cutouts();
  }
}

// deck-support posts (bottom half) and the internal frame (print 1x, deck down)
legs = [[7.0,7.0],[7.0,40],[-0.5,72],[7.0,85.8], [36.6,8.0],[36.6,40],[36.6,62.5],[36.6,85.2]];
leg_w = [1.3, 3.0];
module frame() {
  difference() {
    union() {
      translate([0,0,DECK_Z0]) linear_extrude(DECK_Z1-DECK_Z0) in2d(-deck_clr);
      // FM ledge ring (board rests at fm z0) and corner locators
      difference() {
        translate([fm_box[0],fm_box[2],0]) cube([fm_box[1]-fm_box[0],fm_box[3]-fm_box[2],fm_box[4]]);
        translate([fm_box[0]+fm_ledge,fm_box[2]+fm_ledge,-1]) cube([fm_box[1]-fm_box[0]-2*fm_ledge,fm_box[3]-fm_box[2]-2*fm_ledge,5]);
      }
      lz = fm_box[4]+fm_box[5]+0.8;
      // (the controls-board edge, 0.4 mm away, locates the FM board's +X side; the case walls locate -X and +Y)
      translate([fm_box[1]-4.5,fm_box[2]-1.0,0]) cube([4.5,0.8,lz]);           // -Y edge, right end
      translate([fm_box[0]+0.5,fm_box[2]-1.0,0]) cube([4,0.8,lz]);              // y0 edge near the left wall
      // Feather locating pegs (in its 2.5 mm holes) and controls-board pegs (2.1 mm holes)
      for (h=feather_holes) translate([h[0],h[1],-0.01]) cylinder(d=2.2,h=1.4);
      for (h=cb_holes) translate([h[0],h[1],-0.01]) cylinder(d=CB_HOLE_D-0.2,h=1.4);
    }
    for (s=screws) hull() { translate([s[0],s[1],-5]) cylinder(r=3.2+0.4,h=10); c=side_cube(s); translate([c[0]-0.5,c[1]-0.5,-5]) cube([3,3,10]); }
    translate([0.0,8.0,-5]) cube([6.2,9.0,10]);                  // battery wires up to the JST (left channel)
    translate([31.2,12.0,-5]) cube([3.8,36.0,10]);              // Feather JP1/JP3 wires down to the right channel
    translate([pad_col[0]-1.2,pad_col[1]-1.2,-5]) cube([2.4,pad_col[2]-pad_col[1]+2.4,10]);   // wires up to the pad column
    for (p=cb_tht) translate([p[0],p[1],-5]) cylinder(d=p[2],h=10);
    for (x=[14.68,23.32]) for (y=[2.60,6.78]) translate([x,y,-5]) cylinder(d=1.8,h=10);      // Feather USB-C shell legs
    translate([fm_box[0]+fm_ledge,fm_box[2]+fm_ledge,-5]) cube([fm_box[1]-fm_box[0]-2*fm_ledge,fm_box[3]-fm_box[2]-2*fm_ledge,10]);  // under the FM board
  }
}

// ---------------- ghosts ----------------
module ghosts() {
  color("#1b6",0.9) translate([feather_box[0],feather_box[2],0]) cube([feather_box[1]-feather_box[0],feather_box[3]-feather_box[2],1.6]);
  color("#333") for (p=f_parts) translate([p[0],p[2],p[4]]) cube([p[1]-p[0],p[3]-p[2],p[5]-p[4]]);
  color("#222",0.8) translate([holder_box[0],holder_box[2],holder_box[4]]) cube([holder_box[1]-holder_box[0],holder_box[3]-holder_box[2],holder_box[5]-holder_box[4]]);
  color("#36c",0.9) translate([fm_box[0],fm_box[2],fm_box[4]]) cube([fm_box[1]-fm_box[0],fm_box[3]-fm_box[2],fm_box[5]]);
  color("#888") translate([FM_JACK_X-3,fm_box[3]-12,fm_box[4]+fm_box[5]]) cube([6,12,FM_JACK_BODY_H]);
  color("#2a5",0.9) linear_extrude(CB_T) polygon(cb_outline);
  color("#555") translate([wheel_xy[0],wheel_xy[1],CB_T+wheel_z0]) cylinder(r=wheel_r,h=wheel_z1-wheel_z0);
  color("#eee") translate([sw_pin_x-2,sw_y-4.3,CB_T]) cube([sw_face_x-sw_pin_x+2,8.6,4.5]);
  color("#eee") translate([sw_face_x,(sw_on_y)-sw_act_w/2,CB_T+sw_act_z0]) cube([sw_tip_x-sw_face_x,sw_act_w,sw_act_z1-sw_act_z0]);
}

if (part=="top")         translate([0,0,TOP_OUT]) rotate([180,0,0]) top_half();
else if (part=="bottom") translate([0,0,-BOT_OUT]) bottom_half();
else if (part=="frame")  translate([0,0,-DECK_Z0]) frame();     // deck on the bed, pegs and ledges up
else if (part=="top_raw") top_half();
else if (part=="bottom_raw") bottom_half();
else if (part=="frame_raw") frame();
else if (part=="print") { translate([0,0,-BOT_OUT]) bottom_half(); translate([55,87,TOP_OUT]) rotate([180,0,0]) top_half();
                          translate([105,0,-DECK_Z0]) frame(); }
else if (part=="closed") { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("tan") frame(); ghosts(); }
else if (part=="section") {   // closed case cut at Y = sec_y, looking from the USB-C end
  color("lightgray") clipc() bottom_half(); color("lightsteelblue") clipc() top_half(); color("tan") clipc() frame(); clipc() ghosts(); }
else { color("lightgray") bottom_half(); color("tan") translate([0,0,14]) frame(); ghosts_up(); color("lightsteelblue",0.6) translate([0,0,30]) top_half(); }
module clipc() { intersection() { children(); translate([-20,sec_y,-40]) cube([100,100,80]); } }
module ghosts_up() { translate([0,0,14]) ghosts(); }
sec_y = 30;
