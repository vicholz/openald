// MI03 FM Pocket Radio (PCB silk "MLA-M3(2291) V4.1 20240627") + 18650 enclosure.
// Adapted from the OpenALD single-board case (radio_single_board/case/openald_case.scad):
// same 2.0 mm walls, rounded shell, alignment lip/rebate, M2 heat-set inserts, filleted-opening style,
// USB-C plug recess, and the same MPD BH-18650-PC holder (here mounted in the back shell, wired to VBAT).
//
// Frame (front view = looking at the LCD/buttons, top end of the board up):
//   X = 0 on the board centre line, +X = power-switch side (front-view right), -X = USB-C side.
//   Y = pcb_l - d, where d = "distance from the top" exactly as Victor measured it (top end at Y = 80).
//   Z = 0 at the PCB BACK face (switch/USB/jack side); +Z towards the front (LCD/buttons).
//
// Parts:  openscad -D 'part="front"' -o front_shell.stl mi03_case.scad   (also: back, plunger, switch_cap, print)
// Every measurement Victor gave is a named parameter below; "ASSUMED" marks values he did not give.

part = "assembly";  // front | back | plunger | switch_cap | print | assembly | exploded | closed | section_buttons
                    // section_switch | front_raw | back_raw | plungers_raw | cap_raw | ghost_* (fit-check poses)
cap_shift = 0;      // switch cap / actuator offset along Y for travel checks (-sw_travel/2 .. +sw_travel/2)

// ================= Victor's measurements (mm, d = from the top end) =================
pcb_t = 1.0;
pcb_l = 80;
pcb_sections = [[0,20,21],[20,39,22],[39,62.5,22.5],[62.5,80,21]];  // [d0, d1, width]
pcb_end_r_top = 6;      // ASSUMED rounding of the top end ("semicircular-ish" in the photo; only used for the ghost)
pcb_end_r_bot = 4;      // ASSUMED rounding of the bottom corners
// mounting holes [x, d, diameter, use]   use: "screw_back" (screw from the PCB back into the front shell),
// "screw_thru" (screw from the front face into an insert in the back shell), "pin" (locating pin), "none"
hole_bot_in   = 2.1;    // ASSUMED: "1 mm from left and right" read as hole EDGE 1 mm from the board edge (2.2 mm hole)
holes = [[0, 3.75, 3.2, "screw_back"],
         [0, 28,   2.25, "none"],        // set "pin" for a 1.9 mm locating pin (off: LED pads/wires sit near here)
         [-(21/2-hole_bot_in), 73, 2.2, "screw_thru"],
         [ (21/2-hole_bot_in), 73, 2.2, "screw_thru"]];
// front (top) side
lcd_d0 = 6.75;  lcd_glass_d1 = 21.75;  lcd_bl_d1 = 26.25;
lcd_w  = 21 - 1;        // "1 mm narrower than the board"
lcd_glass_t = 1.78;  lcd_bl_t = 1.4;
lcd_stacked = true;     // ASSUMED: glass sits ON the backlight plate (glass top = pcb + 1.4 + 1.78). false = both on the PCB
btn_d      = [37.25, 45, 54, 62, 70.75];   // S1, S3, S2, S4, S5 (top to bottom)
btn_press  = [true, true, false, false, false];  // top two = through-case plungers, rest = pin holes
btn_body_h = 1.0;  btn_cap_h = 0.5;  btn_cap_d = 2.0;
btn_body_w = 4.0;       // ASSUMED square body footprint (only for the ghost / clearance)
// back (bottom) side, heights are "with the board" as measured
jack_total_h = 6.25;  jack_body_out = 1.0;  jack_barrel_out = 2.25;
jack_barrel_d = 5.0;    // ASSUMED (body is only 5.25 mm tall, so a 6 mm barrel can't be centred on it)
jack_body_w = 6.0;  jack_body_len = 12;   // ASSUMED body footprint
usb_d = 27;  usb_out = 1.75;  usb_total_h = 4.1;
usb_w = 8.94;  usb_h = 3.26;  usb_len = 7.35;   // ASSUMED standard USB-C receptacle shell
sw_d  = 27;  sw_body_w = 9;  sw_total_h = 4.8;
sw_head = [1.5, 1.5];   // switch head (Y x Z)
sw_head_out = 1.5;      // ASSUMED: head sticks out 1.5 mm past the board edge
sw_body_depth = 3.5;    // ASSUMED body depth into the board
sw_travel = 2.0;        // ASSUMED total actuator travel (Victor's estimate 1.5-2)
back_misc_h = 1.8;      // ASSUMED: everything else on the back (SOIC, passives) is <= 1.8 mm tall
// 18650 holder: MPD BH-18650-PC, as used on OpenALD (KiCad 3D model 77.7 x 20.9; datasheet holes 10.68 mm from the - end, 55.61 apart)
holder_l = 77.7;  holder_w = 20.9;
holder_env_h = 19.6;    // ASSUMED base -> top of an inserted cell (18.6 mm cell + ~1 mm floor)
holder_side_h = 12.0;   // ASSUMED side-wall height (ghost only)
holder_end_t = 4.0;     // ASSUMED end-wall (contact) thickness, full height
holder_pin_in = 2.4;    // PC pins 72.9 mm apart, centred
holder_hole_d = 3.2;  holder_hole_from_neg = 10.68;  holder_hole_pitch = 55.61;
cell_d = 18.6;

// ================= case tunables (OpenALD values where they exist) =================
wall    = 2.0;     // side wall (OpenALD)
front_t = 1.6;     // front face (OpenALD floor_t)
floor_t = 2.0;     // back floor (0.4 thicker than OpenALD: wire grooves + pin pockets)
clr     = 0.5;     // PCB edge to inner wall (OpenALD)
end_clr_top = 1.3; // top end: room for the closing snap tab
jack_clr = 0.3;    // jack body face to inner wall -> barrel ends flush with the outer face
top_clear = 0.3;   // air above the LCD glass
bat_clear = 0.5;   // air between the lowest back part (jack) and the cell
edge_r  = 2.0;     // rounding of the front/back edges (OpenALD)
plan_r_in = 3.0;   // plan-view inner corner radius
lip_h = 1.2;  lip_t = 0.9;  fit = 0.15;   // alignment lip (OpenALD)
// fasteners (OpenALD: M2 + heat-set inserts)
screw_d = 2.4;  insert_d = 3.2;  insert_l = 4.0;  insert_hole_l = 4.5;
csk_d = 4.2;           // M2 countersunk head (3.8) + clearance
pilot_d = 1.7;         // M2 self-tapping into the front shell (top hole)
boss_r_back = 2.6;  boss_r_front = 2.2;
pin_d = 1.9;  pin_l = 0.8;
// buttons
plunger_stem_d = 3.1;  plunger_hole_d = 3.5;  plunger_flange_d = 5.6;
plunger_gap = 0.15;     // plunger bottom to switch cap (rest)
plunger_proud = 0.8;    // stem above the front face
pinhole_d = 1.0;        // Victor's 1 mm pin
pinhole_clr = 0.2;      // printed holes come out small: 1.2 mm modelled
tube_od = 3.0;  tube_gap = 0.35;   // guide tube ends this far above the button cap
funnel_d = 2.4;         // lead-in cone on the front face
// switch cap
cap_flange = [6.0, 3.6];   // Y x Z, inside the wall
cap_flange_t = 1.7;        // X
cap_stem   = [3.0, 2.4];   // Y x Z, through the wall slot
cap_knob   = [7.0, 5.0, 2.25];  // Y x Z x protrusion
cap_socket_clr = 0.1;      // per side on the 1.5 x 1.5 head (tight; scale if loose)
slot_clr = 0.2;
// LCD window
lcd_border = 0.8;  bezel = 0.8;
// edge ledges supporting the PCB back between the buttons (d ranges)
ledge_d = [[33, 62]];  ledge_w = 1.1;  ledge_h = 1.2;
// wires
wire_side = -1;   // -1 = USB-C side, +1 = switch side
groove_w = 1.4;  groove_dp = 1.0;
$fn = 40;

// ================= derived =================
function Y(d) = pcb_l - d;
pcb_wmax = max([for (s=pcb_sections) s[2]]);
function pcb_halfw(d) = max([for (s=pcb_sections) if (d>=s[0]-1e-6 && d<=s[1]+1e-6) s[2]/2]);
z_pcb_top  = pcb_t;
z_glass    = pcb_t + (lcd_stacked ? lcd_bl_t + lcd_glass_t : max(lcd_bl_t, lcd_glass_t));
z_btn_top  = pcb_t + btn_body_h + btn_cap_h;
z_ceiling  = z_glass + top_clear;
Zf         = z_ceiling + front_t;          // front outer face
jack_h     = jack_total_h - pcb_t;  usb_hb = usb_total_h - pcb_t;  sw_h = sw_total_h - pcb_t;
jack_axis_z = -jack_h/2;
sw_head_z  = -sw_h/2;                      // ASSUMED head centred on the body height
z_cell_top = -(max(jack_h, sw_h, usb_hb) + bat_clear);
z_floor_in = z_cell_top - holder_env_h;
Zb         = z_floor_in - floor_t;          // back outer face (negative)
in_x1 = pcb_wmax/2 + clr;  in_x0 = -in_x1;
in_y1 = Y(-end_clr_top);                    // top end
in_y0 = Y(pcb_l + jack_body_out + jack_clr);// bottom end (jack)
out_r = plan_r_in + wall;
holder_y1 = in_y1 - 0.5;                   // + end at the top end wall
holder_y0 = holder_y1 - holder_l;
wire_ch_bot_y = Y(73) + boss_r_back + 1.5;  // above the bottom insert boss
sw_x   = pcb_halfw(sw_d);                   // switch body face (board edge)
sw_tip = sw_x + sw_head_out;
usb_tip = -pcb_halfw(usb_d) - usb_out;
echo(str("MI03 case outer: ", in_x1-in_x0+2*wall, " W x ", in_y1-in_y0+2*wall, " L x ", Zf-Zb, " T mm (knob adds ", cap_knob[2]+0.2, " mm on the switch side)"));
echo(str("Z stack: back face ", Zb, ", floor top ", z_floor_in, ", cell top ", z_cell_top, ", PCB 0..", pcb_t, ", LCD glass top ", z_glass, ", ceiling ", z_ceiling, ", front face ", Zf));
echo(str("Holder Y ", holder_y0, "..", holder_y1, " (cavity ", in_y0, "..", in_y1, ")"));
echo(str("Switch tip x ", sw_tip, ", USB tip x ", usb_tip, ", inner wall ", in_x1));

// ================= helpers (from openald_case.scad) =================
module rrect(x0,y0,x1,y1,r,h) { hull() for (x=[x0+r,x1-r]) for (y=[y0+r,y1-r]) translate([x,y,0]) cylinder(r=r,h=h); }
module rounded_shell(z0,z1) {
  hull() for (x=[in_x0-wall+out_r, in_x1+wall-out_r]) for (y=[in_y0-wall+out_r, in_y1+wall-out_r])
    for (z=[z0+edge_r, z1-edge_r]) translate([x,y,z]) rotate_extrude($fn=40) translate([out_r-edge_r,0]) circle(r=edge_r,$fn=20);
}
module cavity(z0,z1) { translate([0,0,z0]) rrect(in_x0,in_y0,in_x1,in_y1,plan_r_in,z1-z0); }
module rr2d(w,h,r) { r2=min(r,w/2,h/2); hull() for (sx=[-1,1]) for (sy=[-1,1]) translate([sx*(w/2-r2),sy*(h/2-r2)]) circle(r=r2); }
// opening along local +Z; wall from z=0 (inside) to z=depth (outside); 45-degree outer chamfer ch
module chamfered_hole(w,h,cr,depth,ch) {
  translate([0,0,-1]) linear_extrude(depth+2) rr2d(w,h,cr);
  if (ch>0) translate([0,0,depth-ch]) hull() { linear_extrude(0.01) rr2d(w,h,cr); translate([0,0,ch+0.5]) linear_extrude(0.01) rr2d(w+2*ch+1,h+2*ch+1,cr+ch+0.5); }
}

// ================= ghost parts (fit check + previews) =================
module pcb_outline2d() {
  intersection() {
    union() for (s=pcb_sections) translate([-s[2]/2, Y(s[1])]) square([s[2], s[1]-s[0]]);
    hull() {
      for (sx=[-1,1]) translate([sx*(pcb_wmax/2-pcb_end_r_top), Y(pcb_end_r_top)]) circle(r=pcb_end_r_top);
      for (sx=[-1,1]) translate([sx*(pcb_wmax/2-pcb_end_r_bot), Y(pcb_l-pcb_end_r_bot)]) circle(r=pcb_end_r_bot);
    }
  }
}
module ghost_pcb() {
  difference() { linear_extrude(pcb_t) pcb_outline2d(); for (h=holes) translate([h[0],Y(h[1]),-1]) cylinder(d=h[2],h=3); }
}
module ghost_front_parts() {
  // LCD: backlight plate (full length), glass (to lcd_glass_d1)
  translate([-lcd_w/2, Y(lcd_bl_d1), pcb_t]) cube([lcd_w, lcd_bl_d1-lcd_d0, lcd_bl_t]);
  translate([-lcd_w/2, Y(lcd_glass_d1), lcd_stacked ? pcb_t+lcd_bl_t : pcb_t]) cube([lcd_w, lcd_glass_d1-lcd_d0, lcd_glass_t]);
  for (d=btn_d) translate([0,Y(d),0]) {
    translate([-btn_body_w/2,-btn_body_w/2,pcb_t]) cube([btn_body_w,btn_body_w,btn_body_h]);
    translate([0,0,pcb_t+btn_body_h]) cylinder(d=btn_cap_d,h=btn_cap_h);
  }
}
module ghost_back_parts(shift=0) {
  // jack: square body to 1 mm past the end, barrel 2.25 mm further
  translate([-jack_body_w/2, Y(pcb_l+jack_body_out), -jack_h]) cube([jack_body_w, jack_body_len, jack_h]);
  translate([0, Y(pcb_l+jack_body_out)+0.01, jack_axis_z]) rotate([90,0,0]) cylinder(d=jack_barrel_d, h=jack_barrel_out);
  // USB-C receptacle (edge-mounted, -X side), shell from -usb_hb up to usb_h
  translate([usb_tip, Y(usb_d)-usb_w/2, -usb_hb]) cube([usb_len, usb_w, usb_h]);
  // slide switch (+X side): body under the board edge, head sticking out
  translate([sw_x-sw_body_depth, Y(sw_d)-sw_body_w/2, -sw_h]) cube([sw_body_depth, sw_body_w, sw_h]);
  translate([sw_x-0.01, Y(sw_d)+shift-sw_head[0]/2, sw_head_z-sw_head[1]/2]) cube([sw_head_out+0.01, sw_head[0], sw_head[1]]);
}
module ghost_holder() {
  translate([0,0,z_floor_in]) {
    difference() {   // base/sides + full-height end walls
      union() {
        translate([-holder_w/2, holder_y0, 0]) cube([holder_w, holder_l, holder_side_h]);
        for (y=[holder_y0, holder_y1-holder_end_t]) translate([-holder_w/2, y, 0]) cube([holder_w, holder_end_t, holder_env_h]);
      }
      translate([0, holder_y0+4, holder_env_h-cell_d/2]) rotate([-90,0,0]) cylinder(d=cell_d, h=holder_l-8);
    }
    translate([0, holder_y0+2.5, holder_env_h-cell_d/2]) rotate([-90,0,0]) cylinder(d=cell_d, h=holder_l-5);  // cell
    for (y=[holder_y0+holder_pin_in, holder_y1-holder_pin_in]) translate([0,y,-1.0]) cylinder(d=1.2,h=1.01,$fn=12); // trimmed pins (1 mm)
  }
}
module screws() {   // hardware ghosts, for the fit check
  for (h=holes) translate([h[0],Y(h[1]),0]) {
    if (h[3]=="screw_thru") { translate([0,0,-3.92]) cylinder(d=2.0,h=Zf+3.92-1.0); translate([0,0,Zf-1.0]) cylinder(d1=2.0,d2=3.8,h=0.99); }
    if (h[3]=="screw_back") { translate([0,0,1.0]) cylinder(d=2.0,h=3.0); translate([0,0,-1.3]) cylinder(d=3.8,h=1.3); }
  }
}

// ================= openings shared by both shells =================
module side_openings() {
  // USB-C: shell clearance through the wall + plug recess on the outside (OpenALD 13.0 x 7.6 recess, r 3)
  zc = -usb_hb + usb_h/2;
  translate([in_x0+0.5, Y(usb_d), zc]) rotate([0,-90,0]) chamfered_hole(usb_h+0.5, usb_w+0.5, 0.4, wall+1, 0);
  translate([in_x0-wall-1, Y(usb_d), zc]) rotate([0,90,0]) linear_extrude(1 + usb_tip-(in_x0-wall)) rr2d(7.6, 13.0, 3.0);
  // headphone jack barrel: through hole + 45-degree outer chamfer for the plug
  translate([0, in_y0+0.01, jack_axis_z]) rotate([90,0,0]) chamfered_hole(jack_barrel_d+0.4, jack_barrel_d+0.4, 99, wall, 0.7);
}
// switch slot (stem) + wall pocket (flange), open at Z=0 so the cap drops in before the front closes
module switch_cuts() {
  yc = Y(sw_d);
  sl = cap_stem[0] + sw_travel + 2*slot_clr;
  fl = cap_flange[0] + sw_travel + 2*slot_clr;
  translate([in_x1-1, yc-sl/2, sw_head_z-cap_stem[1]/2-slot_clr]) cube([wall+2, sl, -(sw_head_z-cap_stem[1]/2-slot_clr)+0.01]);
  translate([in_x1-1, yc-fl/2, sw_head_z-cap_flange[1]/2-slot_clr]) cube([1+ (sw_x+0.15+cap_flange_t+slot_clr) - in_x1, fl, -(sw_head_z-cap_flange[1]/2-slot_clr)+0.01]);
}

// ================= FRONT SHELL (z = 0 .. Zf) =================
module front_shell() {
  difference() {
    union() {
      difference() {
        intersection() { rounded_shell(Zb, Zf); translate([-50,-50,0]) cube([100,200,Zf+1]); }
        cavity(-1, z_ceiling);
      }
      // PCB bosses (ceiling -> PCB top)
      for (h=holes) translate([h[0],Y(h[1]),0]) {
        if (h[3]=="screw_back") translate([0,0,z_pcb_top]) cylinder(r=boss_r_front+0.3, h=z_ceiling-z_pcb_top+0.01);
        if (h[3]=="screw_thru") intersection() {
          translate([-h[0],-Y(h[1]),z_pcb_top]) cavity(0, z_ceiling-z_pcb_top+0.01);
          hull() { translate([0,0,z_pcb_top]) cylinder(r=boss_r_front, h=z_ceiling-z_pcb_top+0.01);
                   translate([sign(h[0])*(in_x1-h[0]*sign(h[0])), 0, z_pcb_top]) translate([-1,-boss_r_front,0]) cube([2,2*boss_r_front,z_ceiling-z_pcb_top+0.01]); }
        }
        if (h[3]=="pin") { translate([0,0,z_pcb_top]) cylinder(r=1.8, h=z_ceiling-z_pcb_top+0.01); translate([0,0,z_pcb_top-pin_l]) cylinder(d=pin_d, h=pin_l+0.01); }
      }
      // pin guide tubes (ceiling -> just above the button cap)
      for (i=[0:len(btn_d)-1]) if (!btn_press[i]) translate([0,Y(btn_d[i]),z_btn_top+tube_gap]) cylinder(d=tube_od, h=z_ceiling-z_btn_top-tube_gap+0.01);
      // closing snap tab at the top end (hangs into the back shell, bump clicks into its end wall)
      translate([-3, in_y1-0.9, -3.0]) {
        cube([6, 0.9, z_ceiling+3.0]);
        translate([0,0.9,0.4]) hull() { cube([6,0.01,1.4]); translate([0,0,0.3]) cube([6,0.45,0.8]); }
      }
    }
    // rebate for the back-shell lip
    translate([0,0,-0.01]) difference() {
      rrect(in_x0-lip_t-fit,in_y0-lip_t-fit,in_x1+lip_t+fit,in_y1+lip_t+fit,plan_r_in+lip_t+fit,lip_h+0.3);
      translate([0,0,-1]) rrect(in_x0+0.01,in_y0+0.01,in_x1-0.01,in_y1-0.01,plan_r_in,lip_h+3);
      switch_keeper_zone();   // no rebate beside the switch: the front wall closes the top of the switch pocket
    }
    // LCD window with 45-degree bezel
    translate([0, Y((lcd_d0+lcd_glass_d1)/2), z_ceiling]) chamfered_hole(lcd_w-2*lcd_border, lcd_glass_d1-lcd_d0-2*lcd_border, 0.6, front_t, bezel);
    // plunger holes / pin holes with funnels
    for (i=[0:len(btn_d)-1]) translate([0,Y(btn_d[i]),0]) {
      if (btn_press[i]) translate([0,0,z_ceiling]) chamfered_hole(plunger_hole_d, plunger_hole_d, 99, front_t, 0.4);
      else { translate([0,0,z_btn_top]) cylinder(d=pinhole_d+pinhole_clr, h=Zf); translate([0,0,Zf-(funnel_d-pinhole_d-pinhole_clr)/2]) cylinder(d1=pinhole_d+pinhole_clr, d2=funnel_d, h=(funnel_d-pinhole_d-pinhole_clr)/2+0.01); translate([0,0,Zf]) cylinder(d=funnel_d,h=1); }
    }
    // screw holes
    for (h=holes) translate([h[0],Y(h[1]),0]) {
      if (h[3]=="screw_back") translate([0,0,z_pcb_top-0.01]) cylinder(d=pilot_d, h=z_ceiling-z_pcb_top-0.3);
      if (h[3]=="screw_thru") { translate([0,0,-1]) cylinder(d=screw_d, h=Zf+2); translate([0,0,Zf-(csk_d-screw_d)/2]) cylinder(d1=screw_d, d2=csk_d, h=(csk_d-screw_d)/2+0.01); translate([0,0,Zf]) cylinder(d=csk_d,h=1); }
    }
    side_openings();
  }
}
module switch_keeper_zone() {
  translate([in_x1-0.5, Y(sw_d)-(cap_flange[0]+sw_travel)/2-2, -1]) cube([lip_t+fit+1, cap_flange[0]+sw_travel+4, lip_h+3]);
}

// ================= BACK SHELL (z = Zb .. 0, lip to +lip_h) =================
module back_shell() {
  difference() {
    union() {
      difference() {
        intersection() { rounded_shell(Zb, Zf); translate([-50,-50,Zb-1]) cube([100,200,-Zb+1]); }
        cavity(z_floor_in, 1);
      }
      // alignment lip (removed beside the switch pocket)
      difference() {
        rrect(in_x0-lip_t,in_y0-lip_t,in_x1+lip_t,in_y1+lip_t,plan_r_in+lip_t,lip_h);
        translate([0,0,-1]) rrect(in_x0,in_y0,in_x1,in_y1,plan_r_in,lip_h+2);
        switch_keeper_zone();
      }
      // insert bosses for the through screws: hang from the side wall, 45-degree underside (prints without support)
      for (h=holes) if (h[3]=="screw_thru") translate([h[0],Y(h[1]),0]) intersection() {
        translate([-h[0],-Y(h[1]),0]) cavity(z_floor_in, 0);
        s = sign(h[0]); reach = in_x1 - abs(h[0]);
        union() {
          hull() {   // boss + flat bridge to the wall
            translate([0,0,-jack_h]) cylinder(r=boss_r_back, h=jack_h);
            translate([s*(reach+0.5)-0.5, -boss_r_back, -jack_h]) cube([1, 2*boss_r_back, jack_h]);
          }
          // 45-degree support wedge under it, only where the holder's end wall is not (y > end wall + 0.4)
          intersection() {
            hull() {
              translate([0,0,-jack_h]) cylinder(r=boss_r_back, h=jack_h);
              translate([s*(reach+0.5)-0.5, -boss_r_back, -jack_h-reach-boss_r_back]) cube([1, 2*boss_r_back, jack_h+reach+boss_r_back]);
            }
            translate([-20, holder_y0+holder_end_t+0.4-Y(h[1]), -40]) cube([40, 40, 40]);
          }
        }
      }
      // PCB edge ledges between the buttons (stop the board flexing when S1/S3 are pressed)
      for (r=ledge_d) for (s=[-1,1]) intersection() {
        cavity(z_floor_in, 0);
        hull() {
          translate([s>0 ? in_x1-ledge_w-clr+0.5 : in_x0-0.01, Y(r[1]), -ledge_h]) cube([ledge_w+clr-0.5+0.01, r[1]-r[0], ledge_h]);
          translate([s>0 ? in_x1-0.01 : in_x0-0.01, Y(r[1]), -ledge_h-ledge_w-clr]) cube([0.02, r[1]-r[0], ledge_h+ledge_w+clr]);
        }
      }
      // holder locating rails along the long sides (middle part only, wire grooves stay free at the ends)
      for (s=[-1,1]) translate([s>0 ? holder_w/2+0.2 : -holder_w/2-0.2-0.8, holder_y0+12, z_floor_in-0.01]) cube([0.8, holder_l-24, 1.5]);
      // locating pegs for the holder's two 3.2 mm holes (- end at the jack end)
      for (y=[holder_y0+holder_hole_from_neg, holder_y0+holder_hole_from_neg+holder_hole_pitch]) translate([0,y,z_floor_in-0.01]) cylinder(d1=holder_hole_d-0.3, d2=holder_hole_d-0.6, h=1.5);
    }
    // inserts
    for (h=holes) if (h[3]=="screw_thru") translate([h[0],Y(h[1]),-insert_hole_l]) cylinder(d=insert_d, h=insert_hole_l+lip_h+1);
    // trimmed holder pins: pockets + wire grooves to the wire-side wall, then up the wall to the PCB zone
    // channel Y positions: top wire straight up at its pin, bottom wire runs along the wall past the insert boss first
    wx0 = wire_side>0 ? in_x1-0.6 : in_x0-groove_dp;      // floor groove hugging the wall
    for (pc=[[holder_y1-holder_pin_in, holder_y1-holder_pin_in], [holder_y0+holder_pin_in, wire_ch_bot_y]]) {
      y=pc[0]; yc=pc[1];
      translate([-1.5, y-1.5, z_floor_in-groove_dp]) cube([3,3,groove_dp+0.01]);
      translate([wire_side>0 ? 0 : in_x0-groove_dp, y-groove_w/2, z_floor_in-groove_dp]) cube([in_x1+groove_dp, groove_w, groove_dp+0.01]);
      translate([wx0, min(y,yc)-groove_w/2, z_floor_in-groove_dp]) cube([groove_dp+0.6, abs(yc-y)+groove_w, groove_dp+0.01]);
      translate([wire_side>0 ? in_x1-0.01 : in_x0-groove_dp, yc-groove_w/2, z_floor_in-groove_dp]) cube([groove_dp+0.01, groove_w, -z_floor_in+groove_dp+lip_h+1]);
    }
    // recess for the snap-tab bump (top end wall)
    translate([-3.3, in_y1-0.01, -3.0+0.2]) cube([6.6, 0.6, 1.8]);
    side_openings();
    switch_cuts();
  }
}

// ================= loose parts =================
module plunger() {   // assembly pose: bottom on the button cap
  z0 = z_btn_top + plunger_gap;
  translate([0,0,z0]) {
    cylinder(d=plunger_flange_d, h=z_ceiling-top_clear-z0);
    cylinder(d=plunger_stem_d, h=Zf+plunger_proud-z0-0.6);
    translate([0,0,Zf+plunger_proud-z0-0.6]) cylinder(d1=plunger_stem_d, d2=plunger_stem_d-1.2, h=0.6);
  }
}
module switch_cap(shift=0) {   // assembly pose
  yc = Y(sw_d) + shift;  zc = sw_head_z;
  x0 = sw_x + 0.15;   // flange inner face
  difference() {
    union() {
      translate([x0, yc-cap_flange[0]/2, zc-cap_flange[1]/2]) cube([cap_flange_t, cap_flange[0], cap_flange[1]]);
      translate([x0+cap_flange_t-0.01, yc-cap_stem[0]/2, zc-cap_stem[1]/2]) cube([in_x1+wall-(x0+cap_flange_t)+0.2+0.02, cap_stem[0], cap_stem[1]]);
      translate([in_x1+wall+0.2, yc, zc]) rotate([0,90,0]) linear_extrude(cap_knob[2]-0.6) rr2d(cap_knob[1], cap_knob[0], 1.2);
      translate([in_x1+wall+0.2+cap_knob[2]-0.6, yc, zc]) rotate([0,90,0]) hull() { linear_extrude(0.01) rr2d(cap_knob[1], cap_knob[0], 1.2); translate([0,0,0.59]) linear_extrude(0.01) rr2d(cap_knob[1]-1.2, cap_knob[0]-1.2, 0.6); }
    }
    // socket for the 1.5 x 1.5 head
    translate([x0-0.01, yc-sw_head[0]/2-cap_socket_clr, zc-sw_head[1]/2-cap_socket_clr]) cube([sw_tip-x0+0.2, sw_head[0]+2*cap_socket_clr, sw_head[1]+2*cap_socket_clr]);
    // grip grooves across the knob face
    for (k=[-2:2]) translate([in_x1+wall+0.2+cap_knob[2]-0.35, yc+k*1.2-0.3, zc-cap_knob[1]/2-1]) cube([1, 0.6, cap_knob[1]+2]);
  }
}

// ================= output =================
module ghosts(shift=0) { color("green") ghost_pcb(); color("black") ghost_front_parts(); color("silver") ghost_back_parts(shift); color("royalblue") ghost_holder(); color("gold") screws(); }
plunger_ys = [for (i=[0:len(btn_d)-1]) if (btn_press[i]) Y(btn_d[i])];

if (part=="front")       translate([0,0,Zf]) rotate([180,0,0]) front_shell();     // front face on the bed
else if (part=="back")   translate([0,0,-Zb]) back_shell();                       // floor on the bed
else if (part=="plunger") translate([0,0,-(z_btn_top+plunger_gap)]) plunger();   // flange on the bed
else if (part=="switch_cap") rotate([0,90,0]) translate([-(in_x1+wall+0.2+cap_knob[2]),-Y(sw_d),-sw_head_z]) switch_cap(); // knob face on the bed
else if (part=="print") {
  translate([0,0,-Zb]) back_shell();
  translate([in_x1-in_x0+2*wall+6, 0, Zf]) rotate([180,0,0]) translate([0,-in_y1-in_y0,0]) front_shell();
  for (k=[0,1]) translate([-24, 20+k*9, -(z_btn_top+plunger_gap)]) plunger();
  translate([-24, 50, 0]) rotate([0,90,0]) translate([-(in_x1+wall+0.2+cap_knob[2]),-Y(sw_d),-sw_head_z]) switch_cap();
}
else if (part=="front_raw") front_shell();
else if (part=="back_raw")  back_shell();
else if (part=="plungers_raw") for (y=plunger_ys) translate([0,y,0]) plunger();
else if (part=="cap_raw") switch_cap(cap_shift);
else if (part=="ghost_pcb") ghost_pcb();
else if (part=="ghost_front") ghost_front_parts();
else if (part=="ghost_back") ghost_back_parts(cap_shift);
else if (part=="ghost_holder") ghost_holder();
else if (part=="ghost_screws") screws();
else if (part=="closed") {
  color("lightsteelblue") front_shell(); color("lightgray") back_shell();
  color("orange") for (y=plunger_ys) translate([0,y,0]) plunger(); color("tomato") switch_cap();
}
else if (part=="exploded") {
  color("lightgray") back_shell(); ghosts();
  color("tomato") translate([6,0,0]) switch_cap();
  color("orange") for (y=plunger_ys) translate([0,y,14]) plunger();
  color("lightsteelblue",0.85) translate([0,0,24]) front_shell();
}
else if (part=="section_buttons") {   // cut at X = 0 (through all five buttons, the jack and the cell)
  intersection() { union() { color("lightsteelblue") front_shell(); color("lightgray") back_shell(); color("orange") for (y=plunger_ys) translate([0,y,0]) plunger(); ghosts(); } translate([0,-50,-50]) cube([100,200,100]); }
}
else if (part=="section_switch") {    // cut at Y = switch centre (through the switch, its cap and the USB-C)
  intersection() { union() { color("lightsteelblue") front_shell(); color("lightgray") back_shell(); color("tomato") switch_cap(); ghosts(); } translate([-50,Y(sw_d)-100,-50]) cube([100,100,100]); }
}
else { color("lightsteelblue") front_shell(); color("lightgray") back_shell(); color("orange") for (y=plunger_ys) translate([0,y,0]) plunger(); color("tomato") switch_cap(); ghosts(); }
