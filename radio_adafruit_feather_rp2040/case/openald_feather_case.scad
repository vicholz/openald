// OpenALD Feather RP2040 v1.0 - enclosure (top half, bottom half) + internal frame.
// Case frame: X across (centre 19), Y = 0 at the single-board USB-C receptacle face (Feather: feather_dy) (+Y toward the jack end), Z = 0 at the
// Feather's bottom face.  The lowest 2 in (Y -2.5 .. 48.3) is the same solid as the OpenALD single-board case
// (43.0 x 33.41 section, R5.5 plan corners, R2 edges, same USB-C opening and plug-body recess) so it fits the dock.
// Above that the body tapers out by 1.25 mm per side (Y 50.3 .. 54.3) to 45.5 mm wide.
// All positions come from case_params.scad (generated from scripts/layout.py).
// Direct-mount controls (no controls PCB, no screws): the SS-12F16 power switch drops into a groove inside the left wall
// of the bottom half and is closed in by the frame tab and a top-half tongue; the SIQ-02FVS3 thumbwheel is glued into a
// cradle on the frame; optional 3 mm charge LEDs push into the top. The frame is clamped at the parting line by tabs
// (bottom-half notches below, top-half plugs above), so its height no longer depends on the battery holder.
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
usb_pocket_d = 1.5; usb_recess = [13.0, 7.6]; usb_recess_r = 3.0; usb_fillet = 1.0;  // cable-plug overmold recess (~12.5 x 7 plugs)
 label_depth = 0.4; label_size = 1.8;
wheel_pocket_d = 1.0; wheel_pocket_h = 6.0;
wheel_tab_fit = 0.15;                              // bottom-half tab under the wheel slot (lets the top half drop over the dial)
cradle_wall = 1.5; cradle_wall_h = 1.6;            // wheel cradle side walls (Z 1.6 .. 3.2, 0.4 under the dial)
peg_hole_d = 1.75;                                 // for the wheel's D1.55 locating bosses
sw_fit = 0.15;                                     // switch groove / body-window / knob-channel clearance
tab_depth = 0.9; tab_fit = 0.15;                   // frame clamp tabs: notch depth into the wall, side clearance
clamp_crush = 0.0;                                 // >0 lowers the top-half plugs into the tabs (mm of squeeze) if the frame rattles
mirror_leds = true;                                // optional dock-visible 3 mm CHG/FULL LEDs in the top half
led3_bore = 3.15; led3_boss_d = 5.4;
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
  zc = WHEEL_SEAT_Z;   // wheel seat (cradle top) = 1.6, the dial is at Z 3.6 .. 5.6
  // USB-C (bottom face): straight-walled cable-plug overmold recess (13.0 x 7.6, r 3.0, 1.5 deep, floor at Y -1.0) with
  // a r 1.0 fillet at the outer face (mouth 15.0 x 9.6). The single board has a 12.8 x 7.4 -> 9.8 x 4.4 filleted bowl;
  // this recess contains it, so the dock plug passes exactly as before. Receptacle opening as the single board.
  translate([USB_X, Y_OUT0, USB_Z]) rotate([90,0,0]) translate([0,0,-usb_pocket_d]) filleted_hole(usb_recess[0], usb_recess[1], usb_recess_r, usb_pocket_d, usb_fillet, 0, 10, z_in=0);
  translate([USB_X, Y_IN0, USB_Z]) rotate([90,0,0]) filleted_hole(USB_W+0.5, USB_H+0.5, 1.4, WALL-usb_pocket_d, 0.4, 0.3);
  // 3.5 mm jack on the FM module (top end wall); position is an ESTIMATE from the module photo - edit layout.py
  translate([FM_JACK_X, Y_IN1-0.1, fm_box[4]+fm_box[5]+FM_JACK_AXIS_H]) rotate([-90,0,0]) {
    cylinder(d=FM_JACK_HOLE_D,h=WALL+1); translate([0,0,WALL-0.8]) cylinder(d1=FM_JACK_HOLE_D,d2=FM_JACK_HOLE_D+1.8,h=0.9); }
  // thumbwheel (right side): pocket thins the wall to 1 mm, slot through its floor
  ch = sqrt(pow(WHEEL_R,2)-pow(IN_X1U-wheel_xy[0],2));
  wz = zc+(wheel_z0+wheel_z1)/2;
  translate([IN_X1U+WALL, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90]) filleted_pocket(2*ch+5.0, wheel_pocket_h, 2.6, wheel_pocket_d);
  translate([IN_X1U, wheel_xy[1], wz]) rotate([0,90,0]) rotate([0,0,90]) filleted_hole(2*ch+1.2, wheel_z1-wheel_z0+1.0, 1.0, WALL-wheel_pocket_d, 0.5, 0.3);
}
function wheel_ch() = sqrt(pow(WHEEL_R,2)-pow(IN_X1U-wheel_xy[0],2));   // half-chord of the dial at the inner wall
module wheel_notch(grow=0) {  // top half: the wheel slot continues down to the split so the top half drops over the dial
  ch = wheel_ch(); wz = WHEEL_SEAT_Z+(wheel_z0+wheel_z1)/2;
  translate([IN_X1U-0.5, wheel_xy[1]-ch-0.6-grow, -1]) cube([WALL+2, 2*ch+1.2+2*grow, 1+wz]);
}
module usb_notch() {   // top half (2026-11-12): the receptacle reaches 0.4 into the end wall (mouth Y -0.9), so the opening
  // continues down to the split at full width; otherwise its lower rounded corners scrape the shell while the top half is lowered
  translate([USB_X-(USB_W+0.5)/2, Y_OUT0-1, -1]) cube([USB_W+0.5, WALL+1.5, 1+USB_Z]);
}
module wheel_tab() {          // bottom half: fills the notch up to just under the slot (dial bottom is 0.65 above it)
  ch = wheel_ch(); top = WHEEL_SEAT_Z+wheel_z0-0.5-wheel_tab_fit;
  intersection() { shell();
    translate([IN_X1U, wheel_xy[1]-ch-0.6+wheel_tab_fit, -0.01]) cube([WALL+1, 2*ch+1.2-2*wheel_tab_fit, top+0.01]); }
}
// ---------------- SS-12F16 switch, screwless, left wall of the bottom half ----------------
// wall-local helper: n = distance inward from the left OUTER face (x = X0OU + n), y, z absolute
module lw(n,y,z) { translate([X0OU+n, y, z]) children(); }
sw_g0 = SW_SKIN; sw_g1 = SW_SKIN+SW_GROOVE;            // groove (plate) between n 1.2 and 1.9
sw_gl = sw_plate[0]+0.4;                               // groove length (19.5-19.7 plates)
sw_gz0 = SW_Z-sw_plate[1]/2-sw_fit;                    // groove bottom
sw_win = sw_body[0]/2+sw_fit;                          // half-length of the body window between the ribs
sw_kh = sw_act[0]+SW_TRAVEL+0.6;                       // knob slot length (Y)
sw_kz = sw_act[1]+0.6;                                 // knob slot height (Z)
module switch_cuts() {   // bottom half only
  difference() {         // plate groove, open to the top so the switch drops in; crush bumps left standing
    lw(sw_g0, SW_Y-sw_gl/2, sw_gz0) cube([SW_GROOVE, sw_gl, -sw_gz0+lip_h+0.5]);
    for (s=[-1,1]) for (k=[0,1]) lw(sw_g1-SW_CRUSH, SW_Y+s*(sw_win+1.2+k*2.2)-0.4, sw_gz0-1) cube([SW_CRUSH+0.1, 0.8, -sw_gz0+1-1.05]);
  }
  lw(sw_g1-0.05, SW_Y-sw_win, sw_gz0) cube([sw_bk0-sw_g1+0.05, 2*sw_win, -sw_gz0+lip_h+0.5]);  // body window between the side blocks
  lw(sw_bk0-0.01, SW_Y-sw_slot_w/2, SW_Z-sw_slot_dz) cube([SW_BACK+0.02, sw_slot_w, -SW_Z+sw_slot_dz+lip_h+0.5]); // lug/wire slot, open to the top
  lw(-0.01, SW_Y-sw_kh/2, SW_Z-sw_kz/2) cube([sw_g0+0.02, sw_kh, -SW_Z+sw_kz/2+lip_h+0.5]); // knob slot + channel up to the split
}
// solid backing (bottom half): two side blocks behind the plate ears, a back wall behind the body and a shelf under it,
// all from the case floor up to the frame deck (Z -1.0) and fused to the left wall, so an inward push on the knob
// (plate ears -> side blocks, body -> back wall) goes straight into the wall and floor
sw_bk0 = SW_SKIN+SW_PLATE_MAX+sw_body[2]+0.15;      // back-wall front face (n 6.95): body back of a 0.6 plate + 0.15
sw_bk1 = sw_bk0+SW_BACK;                               // back-wall rear face (n)
sw_slot_w = 2*SW_LUG_P+1.6+2*0.6;                      // lug slot 8.8 wide (lugs 7.6 + 0.6 each side)
sw_slot_dz = 1.5;                                      // slot floor 1.5 below the lug centre (solder joints)
module switch_backing() {
  sy1 = sw_gl/2+SW_SIDE_EXT;                           // side blocks reach 2 mm past the groove ends
  for (s=[-1,1]) lw(sw_g1-0.01, s>0 ? SW_Y+sw_win : SW_Y-sy1, FLOOR_Z-0.01) cube([sw_bk1-sw_g1+0.01, sy1-sw_win, DECK_Z0-FLOOR_Z+0.01]);
  lw(sw_bk0, SW_Y-sw_win-0.01, FLOOR_Z-0.01) cube([SW_BACK, 2*sw_win+0.02, DECK_Z0-FLOOR_Z+0.01]);      // back wall
  lw(sw_g1-0.01, SW_Y-sw_win-0.01, FLOOR_Z-0.01) cube([sw_bk0-sw_g1+0.02, 2*sw_win+0.02, sw_gz0-FLOOR_Z+0.01]); // shelf (solid to the floor)
}
module switch_tongue() { // top half: fills the knob channel above the slot (closes the slot top, stops the switch rising)
  intersection() { shell(); lw(-0.5, SW_Y-sw_kh/2+sw_fit, SW_Z+sw_kz/2) cube([sw_g0-0.15+0.5, sw_kh-2*sw_fit, -SW_Z-sw_kz/2+0.01]); }
}
module switch_labels() {   // engraved under the knob slot on the left side; knob toward the top end (+Y) = ON
  for (L=[["ON",SW_Y+2.6],["OFF",SW_Y-2.6]])
    lw(label_depth, L[1], SW_Z-sw_kz/2-1.6) rotate([90,0,-90]) linear_extrude(label_depth+1)
      text(L[0], size=1.5, font="DejaVu Sans:style=Bold", halign="center", valign="center");
}
// ---------------- frame clamp tabs (parting line) ----------------
// d = distance inward from the inner wall (negative = into the wall); a tab is [side 0=L 1=R 2=T, position, width]
module tab_box(t, d0, d1, w, z0, z1) {
  if (t[0]==0) { xi=in_x0_at(t[1]); translate([xi+d0, t[1]-w/2, z0]) cube([d1-d0, w, z1-z0]); }
  else if (t[0]==1) { xi=in_x1_at(t[1]); translate([xi-d1, t[1]-w/2, z0]) cube([d1-d0, w, z1-z0]); }
  else translate([t[1]-w/2, Y_IN1-d1, z0]) cube([w, d1-d0, z1-z0]);
}
module tab_notches() { for (t=frame_tabs) tab_box(t, -tab_depth, 0.01, t[2]+2*tab_fit, DECK_Z0, lip_h+0.5); }        // bottom half
module tab_plugs()   { for (t=frame_tabs) tab_box(t, -tab_depth+tab_fit, 0, t[2], DECK_Z1-clamp_crush, lip_h+0.3); } // top half
module frame_tabs_solid() { for (t=frame_tabs) tab_box(t, -tab_depth+0.05, deck_clr+0.5, t[2], DECK_Z0, DECK_Z1); }  // frame
// ---------------- LEDs: tunnels + windows ----------------
// [x, y, bore_x, bore_y]; Feather CHG (amber, MCP73831), Feather red D13, Feather NeoPixel (all inside the dock pocket)
leds = [[f_led_chg[0],f_led_chg[1],2.0,1.4], [f_led_red[0],f_led_red[1],1.4,2.0], [f_led_neo[0],f_led_neo[1],2.6,2.6]];
// optional 3 mm THT CHG/FULL LEDs (above the dock line): pushed in from inside until the flange seats, dome flush with the top
led3_seat = TOP_IN+TOP_T-LED3_ABOVE_FLANGE;
module led3_bosses() { if (mirror_leds) for (p=led3) translate([p[0],p[1],led3_seat]) cylinder(d=led3_boss_d,h=TOP_IN-led3_seat+0.01); }
module led3_bores()  { if (mirror_leds) for (p=led3) { translate([p[0],p[1],led3_seat-0.01]) cylinder(d=led3_bore,h=TOP_T+TOP_IN); 
                         translate([p[0],p[1],TOP_IN+TOP_T-0.4]) cylinder(d1=led3_bore,d2=led3_bore+0.8,h=0.41); } }
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
      led3_bosses();
      // FM module hold-downs (corner holes - ESTIMATED positions)
      if (fm_posts) for (x=[fm_box[0]+FM_HOLE_INSET, fm_box[1]-FM_HOLE_INSET]) for (y=[fm_box[2]+FM_HOLE_INSET, fm_box[3]-FM_HOLE_INSET])
        translate([x,y,fm_box[4]+fm_box[5]+0.05]) cylinder(d=3.6,h=TOP_IN-fm_box[4]-fm_box[5]-0.05+0.01);
    }
    translate([0,0,-0.01]) difference() { linear_extrude(lip_h+0.3) in2d(lip_t+fit); translate([0,0,-1]) linear_extrude(lip_h+3) in2d(-0.01); }
    for (s=screws) translate([s[0],s[1],-0.01]) cylinder(d=insert_d,h=insert_top+0.01);
    for (h=feather_holes) translate([h[0],h[1],1.5]) cylinder(d=2.3,h=1.2);
    translate([f_btn_reset[0],f_btn_reset[1],3.9]) cylinder(d=reset_d,h=TOP_IN);
    translate([f_btn_reset[0],f_btn_reset[1],TOP_OUT-0.4]) cylinder(d1=reset_d,d2=reset_d+0.9,h=0.45);
    cutouts(); wheel_notch(); usb_notch(); led_windows(); led3_bores();
  }
  tab_plugs(); switch_tongue();
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
      // tenon on the leg under the wheel cradle: engages the frame so the wheel push (3-6 N, -X) goes into the case
      translate([tenon_leg[0]-tenon_w[0]/2,tenon_leg[1]-tenon_w[1]/2,DECK_Z0-0.06]) cube([tenon_w[0],tenon_w[1],tenon_h+0.06]);
      wheel_tab();
      switch_backing();
    }
    for (s=screws) { translate([s[0],s[1],head_seat-0.01]) cylinder(d=screw_d,h=-head_seat+1);
                     translate([s[0],s[1],BOT_OUT-1]) cylinder(d=head_d,h=head_seat-BOT_OUT+1); }
    // grooves for the holder's PC pins, bent flat under the holder toward its ends (wire soldered past the end)
    for (i=[0,1]) { p=holder_pins[i]; y0 = i==0 ? holder_box[2]-1.8 : p[1]-0.8; y1 = i==0 ? p[1]+0.8 : holder_box[3]+1.8;
      translate([p[0]-1.0, y0, FLOOR_Z-HOLDER_POCKET-0.6]) cube([2.0, y1-y0, 0.61]); }
    // holder seat: shallow floor pocket (holder height / tape no longer reach the frame: 0.7 mm gap)
    hb=holder_box; translate([hb[0]-0.3, hb[2]-0.3, FLOOR_Z-HOLDER_POCKET]) cube([hb[1]-hb[0]+0.6, hb[3]-hb[2]+0.6, HOLDER_POCKET+0.01]);
    cutouts(); switch_cuts(); switch_labels(); tab_notches();
  }
}

// deck-support posts (bottom half) and the internal frame (print 1x, deck down)
legs = [[7.0,7.0],[7.0,40],[-0.5,58.5],[7.0,85.8], [36.6,8.0],[36.6,40],[36.6,62.5],[36.6,85.2]];
leg_w = [1.3, 3.0];
tenon_leg = [36.6,62.5]; tenon_w = [0.9, 2.4]; tenon_h = 0.7;   // tenon on that leg's top, into a mortise in the deck underside
// wheel-local helper: u along +X (toward the wall) and v along +Y from the dial centre, z absolute
module wl(u,v,z) { translate([wheel_xy[0]+u, wheel_xy[1]+v, z]) children(); }
module wheel_cradle() {      // platform + side walls under the SIQ-02FVS3 body (body: u -7.25..3.85, v -5.15..5.15)
  bw = 5.15+0.15;           // half-width of the body slot
  difference() {
    union() {
      wl(-6.9,-bw-cradle_wall,0) cube([6.9+3.6, 2*(bw+cradle_wall), WHEEL_SEAT_Z]);
      for (s=[-1,1]) wl(-6.9, s>0 ? bw : -bw-cradle_wall, WHEEL_SEAT_Z-0.01) cube([6.9+3.0, cradle_wall, cradle_wall_h+0.01]);
    }
    // locating-boss holes (bosses at u -4.5, v +-3)
    for (s=[-1,1]) wl(-4.5, 3*s, WHEEL_SEAT_Z-1.5) cylinder(d=peg_hole_d, h=2);
    // reliefs under the metal mounting tabs (side tabs at u -1.3 / -5.4 stick out ~0.75 past the body sides; front tabs at u +3.25, v +-3.25)
    for (u=[-1.3,-5.4]) for (s=[-1,1]) wl(u-0.75, s>0 ? 4.6 : -6.3, WHEEL_SEAT_Z-0.4) cube([1.5, 1.7, 1.1]);
    for (s=[-1,1]) wl(3.25, 3.25*s, WHEEL_SEAT_Z-0.4) cylinder(d=1.9, h=1);
    // mortise for the leg tenon (from below)
    translate([tenon_leg[0]-tenon_w[0]/2-0.15, tenon_leg[1]-tenon_w[1]/2-0.15, DECK_Z0-0.01]) cube([tenon_w[0]+0.3, tenon_w[1]+0.3, tenon_h+0.25]);
  }
}
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
      // the case walls locate the FM board's -X and +Y sides; a rail locates +X, two stops locate -Y
      translate([fm_box[1]+0.4,72,0]) cube([0.8,fm_box[3]-1-72,lz]);         // +X edge rail (above the wheel wire bay)
      translate([fm_box[1]-4.5,fm_box[2]-1.0,0]) cube([4.5,0.8,lz]);           // -Y edge, right end
      translate([fm_box[0]+0.5,fm_box[2]-1.0,0]) cube([4,0.8,lz]);              // y0 edge near the left wall
      // Feather locating pegs (in its 2.5 mm holes)
      for (h=feather_holes) translate([h[0],h[1],-0.01]) cylinder(d=2.2,h=1.4);
      wheel_cradle();
      frame_tabs_solid();
    }
    // underside relief over the battery holder (deck 0.6 thick there)
    hb=holder_box; translate([hb[0]-0.5, hb[2]-0.5, DECK_Z0-0.01]) cube([hb[1]-hb[0]+1.0, hb[3]-hb[2]+1.0, DECK_RELIEF+0.01]);
    for (s=screws) hull() { translate([s[0],s[1],-5]) cylinder(r=3.2+0.4,h=10); c=side_cube(s); translate([c[0]-0.5,c[1]-0.5,-5]) cube([3,3,10]); }
    translate([0.0,8.0,-5]) cube([6.2,9.0,10]);                  // battery wires up to the JST (left channel)
    translate([31.2,12.0,-5]) cube([3.8,36.0,10]);              // Feather JP1/JP3 wires down to the right channel
    translate([30.4,69.6,-5]) cube([3.6,10.9,10]);              // wheel / LED wires down to the right channel
    translate([tenon_leg[0]-tenon_w[0]/2-0.15, tenon_leg[1]-tenon_w[1]/2-0.15, DECK_Z0-0.01]) cube([tenon_w[0]+0.3, tenon_w[1]+0.3, tenon_h+0.25]);
    for (x=[14.68,23.32]) for (y=[2.60,6.78]+[feather_dy,feather_dy]) translate([x,y,-5]) cylinder(d=1.8,h=10);      // Feather USB-C shell legs
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
  ghost_wheel();
}
module ghost_wheel() {   // SIQ-02FVS3 (simplified): body, dial, 4 terminals
  color("#777") wl(-7.25,-5.15,WHEEL_SEAT_Z) cube([7.25+3.85,10.3,wheel_z0]);
  color("#333") translate([wheel_xy[0],wheel_xy[1],WHEEL_SEAT_Z+wheel_z0]) cylinder(r=WHEEL_R,h=wheel_z1-wheel_z0,$fn=60);
  color("silver") for (v=[-4,-1.475,1.475,4]) wl(-8.0,v-0.35,WHEEL_SEAT_Z) cube([0.8,0.7,0.3]);
}
module ghost_switch() {  // SS-12F16 (knob at the ON end): plate (pressed to the skin), body, lugs, knob
  color("#bbb") lw(sw_g0, SW_Y-sw_plate[0]/2, SW_Z-sw_plate[1]/2) cube([sw_plate[2], sw_plate[0], sw_plate[1]]);
  color("#222") lw(sw_g0+sw_plate[2], SW_Y-sw_body[0]/2, SW_Z-sw_body[1]/2) cube([sw_body[2], sw_body[0], sw_body[1]]);
  color("silver") for (k=[-1,0,1]) lw(sw_g0+sw_plate[2]+sw_body[2], SW_Y+k*SW_LUG_P-0.8, SW_Z-0.25) cube([SW_LUG_L,1.6,0.5]);
  color("#111") lw(sw_g0-SW_L, SW_Y+SW_TRAVEL/2-sw_act[0]/2, SW_Z-sw_act[1]/2) cube([SW_L, sw_act[0], sw_act[1]]);
}
module ghost_leds() { if (mirror_leds) for (i=[0:len(led3)-1]) { p=led3[i];
  color(i==0?"red":"limegreen") { translate([p[0],p[1],led3_seat-1]) cylinder(d=3.8,h=1); translate([p[0],p[1],led3_seat]) cylinder(d=3,h=LED3_ABOVE_FLANGE-1.5);
                                   translate([p[0],p[1],TOP_IN+TOP_T-1.5]) cylinder(d1=3,d2=2.2,h=1.5); } } }

if (part=="top")         translate([0,0,TOP_OUT]) rotate([180,0,0]) top_half();
else if (part=="bottom") translate([0,0,-BOT_OUT]) bottom_half();
else if (part=="frame")  translate([0,0,-DECK_Z0]) frame();     // deck on the bed, pegs and ledges up
else if (part=="top_raw") top_half();
else if (part=="bottom_raw") bottom_half();
else if (part=="frame_raw") frame();
else if (part=="print") { translate([0,0,-BOT_OUT]) bottom_half(); translate([55,87,TOP_OUT]) rotate([180,0,0]) top_half();
                          translate([105,0,-DECK_Z0]) frame(); }
else if (part=="closed") { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("tan") frame(); ghosts(); ghost_switch(); ghost_leds(); }
else if (part=="section") {   // closed case cut at Y = sec_y, looking from the USB-C end (cut faces keep each part's colour)
  clipc("lightgray") bottom_half(); clipc("lightsteelblue") top_half(); clipc("tan") frame(); clipc("#555") ghosts();
  clipc("#222") ghost_switch(); clipc("red") ghost_leds(); }
else if (part=="inside_left") {   // bottom half + frame + switch, cut at X = 9 (looking at the left wall from inside)
  intersection() { union() { color("lightgray") bottom_half(); color("tan") frame(); ghost_switch(); } translate([-10,52,-40]) cube([19,60,80]); } }
else if (part=="usb_section") {   // closed case cut at X = 19 (USB centreline), looking from +X: receptacle vs the recess
  intersection() { union() { color("lightgray") bottom_half(); color("lightsteelblue") top_half(); color("tan") frame(); ghosts(); }
                   translate([-20,-10,-40]) cube([39,30,80]); } }
else if (part=="switch_backing") {   // bottom half only around the switch (no switch): groove, side blocks, back wall, lug slot
  intersection() { color("lightgray") bottom_half(); translate([-10,55,-30]) cube([22,35,40]); } }
else if (part=="bottom_switch") { color("lightgray") bottom_half(); ghost_switch(); }
else if (part=="inside_right") {   // bottom half + frame + parts, top half removed, cut at X = 30.6, Y > 52 (looking at the right wall from inside)
  intersection() { union() { color("lightgray") bottom_half(); color("tan") frame(); ghosts(); ghost_switch(); } translate([30.6,52,-40]) cube([30,60,80]); } }
else if (part=="cradle") { color("tan") frame(); ghost_wheel(); }
else { color("lightgray") bottom_half(); ghost_switch(); color("tan") translate([0,0,14]) frame(); ghosts_up();
       color("lightsteelblue",0.6) translate([0,0,30]) top_half(); translate([0,0,30]) ghost_leds(); }
module clipc(c="gray") { color(c) intersection() { children(); translate([-20,sec_y,-40]) cube([100,100,80]); } }
module ghosts_up() { translate([0,0,14]) ghosts(); }
sec_y = 30;
