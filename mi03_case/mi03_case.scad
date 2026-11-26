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
// Parts:  openscad -D 'part="front"' -o front_shell.stl mi03_case.scad
//         (also: back, battery_frame [-D frame_mount="front"|"back"], plunger, switch_carrier, switch_knob, print)
//
// 2026-11-22 layout: the USB-C opening, the switch slot/pocket and the jack opening are entirely in the FRONT shell.
// The board screws straight into the front shell (3 x M2 self-tapping from the board back), so front + board is one
// rigid unit.  The front/back split moved down to 1 mm below the battery frame (z_split); the back shell is a snap-on
// cover with a lip.  The battery frame screws either into the front shell over the board (frame_mount="front") or
// into columns in the back shell (frame_mount="back").
// Every measurement Victor gave is a named parameter below; "ASSUMED" marks values he did not give.

part = "assembly";  // front | back | battery_frame | plunger | switch_carrier | switch_knob | print | assembly | exploded | closed
                    // front_raw | back_raw | frame_raw | plungers_raw | cap_raw | ghost_* | board_unit (fit-check poses)
frame_mount = "front"; // "front" = frame screws over the board into front-shell bosses | "back" = into back-shell columns
cap_shift = 0;      // switch cap / actuator offset along Y for travel checks (-sw_travel/2 .. +sw_travel/2)

// ================= Victor's measurements (mm, d = from the top end) =================
pcb_t = 1.0;
pcb_l = 80;
pcb_sections = [[0,20,21],[20,39,22],[39,62.5,22.5],[62.5,80,21]];  // [d0, d1, width]
pcb_end_r_top = 6;      // ASSUMED rounding of the top end ("semicircular-ish" in the photo; only used for the ghost)
pcb_end_r_bot = 4;      // ASSUMED rounding of the bottom corners
// mounting holes [x, d, diameter, use]   use: "screw_back" (screw from the PCB back into the front shell),
// "screw_thru" (screw from the front face into an insert in the back shell), "pin" (locating pin), "none"
hole_bot_d    = 74;     // 2026-11-21: moved down 1 mm (was 73): 6 mm from the bottom end
hole_bot_in   = 2.1;    // ASSUMED: "1 mm from left and right" read as hole EDGE 1 mm from the board edge (2.2 mm hole)
holes = [[0, 3.75, 3.2, "screw_back"],
         [0, 28,   2.25, "none"],        // set "pin" for a 1.9 mm locating pin (off: LED pads/wires sit near here)
         [-(21/2-hole_bot_in), hole_bot_d, 2.2, "screw_back"],   // 2026-11-22: all board screws go from the
         [ (21/2-hole_bot_in), hole_bot_d, 2.2, "screw_back"]];  // board back into front-shell bosses
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
floor_t = 1.6;     // back floor (OpenALD)
clr     = 0.5;     // PCB edge to inner wall (OpenALD)
end_clr_top = 1.3; // top end: room for the closing snap tab
jack_tip_clr = 1.2; // 2026-11-22: jack barrel tip to the inner end wall (barrel now fully inside so the board drops in;
                   // 1.2 rather than 0.2 so the option-"front" frame screws fit between the board end and the plate edge)
jack_plug_d = 6.8;  // ASSUMED: hole in the end wall for the plug overmold
jack_cbore = [7.8, 1.0];  // outside counterbore around the plug hole: plug reaches 1.2 + 2.0 - 1.0 = 2.2 mm in to the barrel face
top_clear = 0.3;   // air above the LCD glass
// battery frame (2026-11-21): a flat plate between the PCB and the 18650; the holder is glued BASE-UP to its underside
frame_gap  = 0.3;  // air between the lowest back part (jack, 5.25 mm) and the frame top
frame_t    = 1.6;  // plate thickness (flat glue face underneath)
frame_clr  = 0.2;  // plate edge to the inner wall
frame_ledge_w = 1.0;   // back-shell ledges the plate rests on (sides + jack end)
frame_ledge_gap = 0.1; // ledge top sits this far below the plate (the screws set the plate height)
cell_floor_clr = 0.4;  // cell (open side of the inverted holder) to the floor
holder_pin_trim = 1.4; // trim the holder pins to this so they stay inside the 1.6 mm plate slots
pin_slot = [3.0, 3.6]; // through-slots in the plate for the trimmed pins (X x Y)
edge_r  = 2.0;     // rounding of the front/back edges (OpenALD)
plan_r_in = 3.0;   // plan-view inner corner radius
lip_h = 1.8;  lip_t = 0.9;  fit = 0.15;   // back-shell lip into the front-shell rebate (taller: it carries the snaps)
split_below_frame = 1.0;  // front/back split this far below the battery frame underside
snap_ys = [18, 62];  snap_len = 8;  snap_bump = 0.3;   // snap bumps on the lip, both long sides
// battery-frame fasteners (M2 x 90-degree countersunk self-tapping, e.g. DIN 7982 / ISO 7050 2.2 or M2 "PT" style)
frame_pilot_d = 1.6;  frame_csk_d = 4.0;  frame_boss_r = 1.9;
frame_screw_front = [5.3, -2.05];   // option "front": [+-X, Y] of the front-shell bosses (beside the jack body, +-3)
frame_screw_back  = [9.0, 0.3];    // option "back":  [+-X, Y] of the back-shell columns (in the end corners)
frame_screw_len   = [5, 8];        // M2 countersunk length: option "front", option "back"
frame_boss_top = -2.0;             // front bosses stop 2 mm below the PCB back face (clear of back-side parts <= 1.8 mm)
frame_rib = [10.1, 10.9];           // PCB edge support ribs on the frame (X range, both sides), d = ledge_d
usb_open_clr = 0.25;                // USB-C opening clearance per side around the receptacle shell
usb_recess_gap = 0.55;              // plug recess stops this far outside the USB-C tip (keeps a skin over the drop-in channel)
knob_fit = 0.05;                    // per side, knob socket on the carrier stem (press fit + a drop of CA glue)
knob_socket_l = 1.5;
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
lcd_top_cover = 2.0;   // 2026-11-21: the case covers the top 2 mm of the glass (zebra strip edge)
// LCD retaining frame (the glass is held to the PCB only by a zebra/elastomer strip, so the case holds it)
lcd_frame       = true;
lcd_frame_clr   = 0.2;    // lateral clearance per side around the glass and the backlight plate
lcd_frame_t     = 0.8;    // frame wall thickness
lcd_frame_gap   = 0.3;    // frame walls stop this far above the PCB top
lcd_bl_stub     = 3.0;    // the wall past the backlight's lower end is only corner stubs this long (LED pads/wires in the middle)
lcd_press       = "ribs"; // "ribs" = short crush ribs on the glass border | "lip" = continuous thin lip | "none"
lcd_preload     = 0.15;   // how far the rib/lip tips reach BELOW the nominal glass top (interference)
lcd_rib_w       = 0.6;    // rib/lip width at the ceiling (tapers to lcd_rib_tip at the tip)
lcd_rib_tip     = 0.25;
lcd_rib_len     = 3.5;    // rib length (ribs mode)
lcd_ribs_x      = [-6, 0, 6];     // rib centres along the bottom glass edge (X)
lcd_ribs_x_top  = [-8, -4, 0, 4, 8]; // rib centres along the top (zebra) edge, under the 2 mm cover
lcd_rib_len_top = 3.0;
lcd_ribs_y      = [-3.5, 3.5];    // rib centres along the side edges (offset from the glass centre, Y)
// edge ledges supporting the PCB back between the buttons (d ranges)
ledge_d = [[33, 62]];  // (2026-11-22: now ribs on the battery frame, see frame_rib)
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
z_frame_top = -(max(jack_h, sw_h, usb_hb) + frame_gap);
z_frame_bot = z_frame_top - frame_t;        // = holder base (glue face)
z_cell_low  = z_frame_bot - holder_env_h;   // lowest point of the cell in the inverted holder
z_floor_in = z_cell_low - cell_floor_clr;
Zb         = z_floor_in - floor_t;          // back outer face (negative)
in_x1 = pcb_wmax/2 + clr;  in_x0 = -in_x1;
in_y1 = Y(-end_clr_top);                    // top end
in_y0 = Y(pcb_l + jack_body_out + jack_barrel_out + jack_tip_clr);// bottom end (jack barrel inside)
z_split = z_frame_bot - split_below_frame;  // front shell: z_split .. Zf, back shell: Zb .. z_split (+ lip)
out_r = plan_r_in + wall;
holder_y1 = in_y1 - 0.7;                   // + end at the top end wall (clears the 3 mm inner corner radius)
holder_y0 = holder_y1 - holder_l;
sw_x   = pcb_halfw(sw_d);                   // switch body face (board edge)
sw_tip = sw_x + sw_head_out;
usb_tip = -pcb_halfw(usb_d) - usb_out;
echo(str("MI03 case outer: ", in_x1-in_x0+2*wall, " W x ", in_y1-in_y0+2*wall, " L x ", Zf-Zb, " T mm (knob adds ", cap_knob[2]+0.2, " mm on the switch side); split at z ", z_split, " (front shell ", Zf-z_split, ", back shell ", z_split-Zb, ")"));
echo(str("Z stack: back face ", Zb, ", floor top ", z_floor_in, ", cell low ", z_cell_low, ", frame ", z_frame_bot, "..", z_frame_top, ", PCB 0..", pcb_t, ", LCD glass top ", z_glass, ", ceiling ", z_ceiling, ", front face ", Zf));
echo(str("LCD: glass top ", z_glass, ", ceiling ", z_ceiling, ", press ", lcd_press, " tips at z ", z_glass-lcd_preload, " (preload ", lcd_preload, " mm), frame clearance ", lcd_frame_clr, "/side"));
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
  // stadium-section shell (ends radius usb_h/2), like a real USB-C receptacle
  translate([usb_tip, Y(usb_d), -usb_hb+usb_h/2]) rotate([0,90,0]) linear_extrude(usb_len) rr2d(usb_h, usb_w, usb_h/2);
  // slide switch (+X side): body under the board edge, head sticking out
  translate([sw_x-sw_body_depth, Y(sw_d)-sw_body_w/2, -sw_h]) cube([sw_body_depth, sw_body_w, sw_h]);
  translate([sw_x-0.01, Y(sw_d)+shift-sw_head[0]/2, sw_head_z-sw_head[1]/2]) cube([sw_head_out+0.01, sw_head[0], sw_head[1]]);
}
module ghost_holder() {   // inverted: base glued under the frame, cell opening toward the floor
  translate([0,0,z_frame_bot]) mirror([0,0,1]) {
    difference() {   // base/sides + full-height end walls
      union() {
        translate([-holder_w/2, holder_y0, 0]) cube([holder_w, holder_l, holder_side_h]);
        for (y=[holder_y0, holder_y1-holder_end_t]) translate([-holder_w/2, y, 0]) cube([holder_w, holder_end_t, holder_env_h]);
      }
      translate([0, holder_y0+4, holder_env_h-cell_d/2]) rotate([-90,0,0]) cylinder(d=cell_d, h=holder_l-8);
    }
    translate([0, holder_y0+2.5, holder_env_h-cell_d/2]) rotate([-90,0,0]) cylinder(d=cell_d, h=holder_l-5);  // cell
    for (y=[holder_y0+holder_pin_in, holder_y1-holder_pin_in]) translate([0,y,-holder_pin_trim]) cylinder(d=1.2,h=holder_pin_trim+0.01,$fn=12); // trimmed pins (into the plate slots)
  }
}
module board_screws() { for (h=holes) if (h[3]=="screw_back") translate([h[0],Y(h[1]),0]) { translate([0,0,1.0]) cylinder(d=2.0,h=3.0); translate([0,0,-1.3]) cylinder(d=3.8,h=1.3); } }
module frame_screws(m=frame_mount) {   // M2 countersunk: head 3.8 / 0.9 deep
  if (m=="front") for (sx=[-1,1]) translate([sx*frame_screw_front[0], frame_screw_front[1], z_frame_bot]) {   // from under the plate up
    cylinder(d1=3.8, d2=2.0, h=0.9); translate([0,0,0.89]) cylinder(d=2.0, h=frame_screw_len[0]-0.89); }
  if (m=="back") for (sx=[-1,1]) translate([sx*frame_screw_back[0], frame_screw_back[1], z_frame_top]) {    // from above down
    translate([0,0,-0.9]) cylinder(d1=2.0, d2=3.8, h=0.9); translate([0,0,-frame_screw_len[1]]) cylinder(d=2.0, h=frame_screw_len[1]-0.89); }
}
module screws() { board_screws(); frame_screws(); }

// ================= openings (all in the FRONT shell) =================
module usb_cuts() {
  zc = -usb_hb + usb_h/2;  yc = Y(usb_d);
  // shell clearance through the wall: stadium (USB-C receptacle shape), ends radius = half the opening height
  // (2026-11-25; was a rectangle with 0.4 mm corners).  usb_open_clr = 0.25 per side, unchanged.
  translate([in_x0+0.5, yc, zc]) rotate([0,-90,0]) chamfered_hole(usb_h+2*usb_open_clr, usb_w+2*usb_open_clr, (usb_h+2*usb_open_clr)/2, wall+1, 0);
  // plug recess on the outside (OpenALD 13.0 x 7.6, r 3); stops usb_recess_gap outside the receptacle tip
  translate([in_x0-wall-1, yc, zc]) rotate([0,90,0]) linear_extrude(1 + (usb_tip-usb_recess_gap)-(in_x0-wall)) rr2d(7.6, 13.0, 3.0);
  // drop-in channel: the receptacle sticks 1 mm into the wall, so the wall is relieved from the split up to it
  // (stadium profile swept straight down to the split, so its top also follows the rounded opening)
  translate([usb_tip-0.15, yc, 0]) rotate([0,90,0]) linear_extrude(in_x0+0.01-(usb_tip-0.15))
    hull() for (z=[zc, z_split-1+(usb_h+2*usb_open_clr)/2]) translate([-z,0]) rr2d(usb_h+2*usb_open_clr, usb_w+2*usb_open_clr, (usb_h+2*usb_open_clr)/2);
}
module jack_cuts() {   // plug hole + outside counterbore with a 45-degree chamfer (barrel ends jack_tip_clr inside the wall)
  translate([0, in_y0+0.01, jack_axis_z]) rotate([90,0,0]) cylinder(d=jack_plug_d, h=wall+1);
  translate([0, in_y0-wall+jack_cbore[1], jack_axis_z]) rotate([90,0,0]) cylinder(d=jack_cbore[0], h=jack_cbore[1]+1);
  translate([0, in_y0-wall+0.4, jack_axis_z]) rotate([90,0,0]) cylinder(d1=jack_cbore[0], d2=jack_cbore[0]+2*1.4, h=1.4);
}
// no lip/rebate along the straight part of the jack end wall (the front wall keeps its full 2 mm there, below the plug hole)
module jack_end_no_lip() { translate([-(in_x1-plan_r_in), in_y0-wall-1, z_split-1]) cube([2*(in_x1-plan_r_in), wall+1, lip_h+3]); }
// closed stem slot + flange pocket in the side wall, and a channel below the pocket so the switch head drops in
module switch_cuts() {
  yc = Y(sw_d);
  sl = cap_stem[0] + sw_travel + 2*slot_clr;
  fl = cap_flange[0] + sw_travel + 2*slot_clr;
  hw = sw_head[0] + sw_travel + 0.6;
  zp0 = sw_head_z - cap_flange[1]/2 - slot_clr;
  translate([in_x1-1, yc-sl/2, sw_head_z-cap_stem[1]/2-slot_clr]) cube([wall+2, sl, cap_stem[1]+2*slot_clr]);
  translate([in_x1-1, yc-fl/2, zp0]) cube([1+(sw_x+0.15+cap_flange_t+slot_clr)-in_x1, fl, cap_flange[1]+2*slot_clr]);
  translate([in_x1-1, yc-hw/2, z_split-1]) cube([1+sw_tip+0.15-in_x1, hw, zp0-(z_split-1)+0.01]);
}
module lip_outline(o, h) { rrect(in_x0-o, in_y0-o, in_x1+o, in_y1+o, plan_r_in+o, h); }

// ================= FRONT SHELL (z = z_split .. Zf) =================
module frame_front_boss(sx) {   // option "front" battery-frame boss, merged into the jack end wall (45-degree top)
  x = sx*frame_screw_front[0];  y = frame_screw_front[1];  r = frame_boss_r;
  hull() {
    translate([x, y, z_frame_top]) cylinder(r=r, h=frame_boss_top-z_frame_top);
    translate([x-r, in_y0-0.5, z_frame_top]) cube([2*r, 0.5, frame_boss_top-z_frame_top+(y+r-in_y0)]);
  }
}
module front_shell() {
  difference() {
    union() {
      difference() {
        intersection() { rounded_shell(Zb, Zf); translate([-50,-50,z_split]) cube([100,200,Zf-z_split+1]); }
        cavity(z_split-1, z_ceiling);
      }
      // PCB bosses (ceiling -> PCB top); the board screws into all of them from its back
      for (h=holes) translate([h[0],Y(h[1]),0]) {
        if (h[3]=="screw_back" && abs(h[0])<1) translate([0,0,z_pcb_top]) cylinder(r=boss_r_front+0.3, h=z_ceiling-z_pcb_top+0.01);
        if (h[3]=="screw_back" && abs(h[0])>=1) intersection() {
          translate([-h[0],-Y(h[1]),z_pcb_top]) cavity(0, z_ceiling-z_pcb_top+0.01);
          hull() { translate([0,0,z_pcb_top]) cylinder(r=boss_r_front, h=z_ceiling-z_pcb_top+0.01);
                   translate([sign(h[0])*(in_x1-h[0]*sign(h[0])), 0, z_pcb_top]) translate([-1,-boss_r_front,0]) cube([2,2*boss_r_front,z_ceiling-z_pcb_top+0.01]); }
        }
        if (h[3]=="pin") { translate([0,0,z_pcb_top]) cylinder(r=1.8, h=z_ceiling-z_pcb_top+0.01); translate([0,0,z_pcb_top-pin_l]) cylinder(d=pin_d, h=pin_l+0.01); }
      }
      if (lcd_frame) lcd_frame_walls();
      if (lcd_press!="none") lcd_press_features();
      for (i=[0:len(btn_d)-1]) if (!btn_press[i]) translate([0,Y(btn_d[i]),z_btn_top+tube_gap]) cylinder(d=tube_od, h=z_ceiling-z_btn_top-tube_gap+0.01);
      // post at the top end: holds the battery frame's top end (both options)
      translate([-3, in_y1-0.9, z_frame_top+0.05]) cube([6, 0.91, z_ceiling-z_frame_top-0.05+0.01]);
      // battery-frame bosses in the jack end (screwed in option "front", they just bear on the plate in option "back")
      for (sx=[-1,1]) frame_front_boss(sx);
    }
    // rebate for the back-shell lip + snap grooves
    translate([0,0,z_split-0.01]) difference() { lip_outline(lip_t+fit, lip_h+0.3+0.01); translate([0,0,-1]) lip_outline(-0.01, lip_h+3); translate([0,0,-z_split+0.01]) jack_end_no_lip(); }
    for (sx=[-1,1]) for (y=snap_ys) translate([sx>0 ? in_x1+lip_t+fit-0.01 : in_x0-lip_t-fit-snap_bump-0.1+0.01, Y(y)-(snap_len+0.6)/2, z_split+lip_h/2-0.5]) cube([snap_bump+0.1, snap_len+0.6, 1.0]);
    // LCD window with 45-degree bezel
    translate([0, Y((lcd_d0+lcd_top_cover+lcd_glass_d1-lcd_border)/2), z_ceiling]) chamfered_hole(lcd_w-2*lcd_border, lcd_glass_d1-lcd_border-(lcd_d0+lcd_top_cover), 0.6, front_t, bezel);
    for (i=[0:len(btn_d)-1]) translate([0,Y(btn_d[i]),0]) {
      if (btn_press[i]) translate([0,0,z_ceiling]) chamfered_hole(plunger_hole_d, plunger_hole_d, 99, front_t, 0.4);
      else { translate([0,0,z_btn_top]) cylinder(d=pinhole_d+pinhole_clr, h=Zf); translate([0,0,Zf-(funnel_d-pinhole_d-pinhole_clr)/2]) cylinder(d1=pinhole_d+pinhole_clr, d2=funnel_d, h=(funnel_d-pinhole_d-pinhole_clr)/2+0.01); translate([0,0,Zf]) cylinder(d=funnel_d,h=1); }
    }
    // board screw pilots (M2 self-tapping)
    for (h=holes) if (h[3]=="screw_back") translate([h[0],Y(h[1]),z_pcb_top-0.01]) cylinder(d=pilot_d, h=z_ceiling-z_pcb_top-0.3);
    // battery-frame screw pilots
    for (sx=[-1,1]) translate([sx*frame_screw_front[0], frame_screw_front[1], z_frame_top-0.01]) cylinder(d=frame_pilot_d, h=frame_boss_top-z_frame_top-0.2);
    usb_cuts(); jack_cuts(); switch_cuts();
  }
}
// ---------- LCD retaining frame (part of the front shell) ----------
// Walls locate the glass + backlight laterally; ribs/lip press the glass border (outside the viewing window).
module lcd_frame_walls() {
  c = lcd_frame_clr; t = lcd_frame_t; zb = z_pcb_top + lcd_frame_gap;
  x1 = lcd_w/2 + c;
  yg_top = Y(lcd_d0) + c;          // above the glass top edge
  yg_bot = Y(lcd_glass_d1) - c;    // glass lower edge
  yb_bot = Y(lcd_bl_d1) - c;       // backlight lower edge
  glass_z0 = lcd_stacked ? pcb_t + lcd_bl_t : pcb_t;
  h = z_ceiling - zb + 0.01;
  // side walls (full length of glass + backlight)
  for (sx=[-1,1]) translate([sx>0 ? x1 : -x1-t, yb_bot-t, zb]) cube([t, yg_top+t-(yb_bot-t), h]);
  // top wall (above the glass top edge)
  translate([-x1-t, yg_top, zb]) cube([2*x1+2*t, t, h]);
  // short wall at the glass lower edge: only down to 0.2 above the backlight (it continues under the glass)
  if (lcd_stacked) translate([-x1, yg_bot-t, glass_z0+0.2]) cube([2*x1, t, z_ceiling-glass_z0-0.2+0.01]);
  // corner stubs past the backlight's lower end
  for (sx=[-1,1]) translate([sx>0 ? x1-lcd_bl_stub : -x1-t, yb_bot-t, zb]) cube([lcd_bl_stub+t, t, h]);
}
module rib_x(len) {   // rib running along X, tip down, centred on the origin, base on z = 0
  hull() { translate([-len/2,-lcd_rib_w/2,-0.01]) cube([len,lcd_rib_w,0.01]); translate([-len/2,-lcd_rib_tip/2,-rib_h]) cube([len,lcd_rib_tip,0.01]); }
}
rib_h = z_ceiling - z_glass + lcd_preload;   // ceiling to (glass top - preload)
module lcd_press_features() {
  b = lcd_border/2;   // centre of the border strip between the glass edge and the window
  yt = Y(lcd_d0 + lcd_top_cover/2);  yb = Y(lcd_glass_d1) + b;  yc = (Y(lcd_d0)+Y(lcd_glass_d1))/2;  xs = lcd_w/2 - b;
  wlen_x = lcd_w - lcd_border;  wlen_y = lcd_glass_d1 - lcd_d0 - lcd_border;
  translate([0,0,z_ceiling]) {
    if (lcd_press=="ribs") {
      for (x=lcd_ribs_x_top) translate([x,yt,0]) rib_x(lcd_rib_len_top);   // zebra edge
      for (x=lcd_ribs_x) translate([x,yb,0]) rib_x(lcd_rib_len);
      for (y=lcd_ribs_y) for (sx=[-1,1]) translate([sx*xs,yc+y,0]) rotate([0,0,90]) rib_x(lcd_rib_len);
    }
    if (lcd_press=="lip") {
      for (y=[yt,yb]) translate([0,y,0]) rib_x(wlen_x+lcd_rib_w);
      for (sx=[-1,1]) translate([sx*xs,yc,0]) rotate([0,0,90]) rib_x(wlen_y+lcd_rib_w);
    }
  }
}
// ================= BACK SHELL (z = Zb .. z_split, lip to z_split + lip_h) =================
// A plain snap-on cover: lip with 4 snap bumps, ledges + 2 columns for the battery frame (same part for both options).
module back_shell() {
  zt = z_frame_bot - frame_ledge_gap;
  difference() {
    union() {
      difference() {
        intersection() { rounded_shell(Zb, Zf); translate([-50,-50,Zb-1]) cube([100,200,z_split-Zb+1]); }
        cavity(z_floor_in, z_split+1);
      }
      translate([0,0,z_split-0.01]) difference() { lip_outline(lip_t, lip_h+0.01); translate([0,0,-1]) lip_outline(0, lip_h+3); translate([0,0,-z_split+0.01]) jack_end_no_lip(); }
      // snap bumps (45-degree flanks) on the lip, both long sides
      for (sx=[-1,1]) for (y=snap_ys) translate([sx*(in_x1+lip_t-0.01), Y(y), z_split+lip_h/2]) mirror([sx>0 ? 0 : 1,0,0])
        hull() { translate([0,-snap_len/2,-0.65]) cube([0.01, snap_len, 1.3]); translate([snap_bump,-snap_len/2+0.3,-0.35]) cube([0.01, snap_len-0.6, 0.7]); }
      // ledges the battery frame rests on: both long sides + the jack end (45-degree undersides, no supports)
      intersection() {
        cavity(z_floor_in, z_split+5);
        union() {
          for (sx=[-1,1]) hull() {
            translate([sx>0 ? in_x1-frame_ledge_w : in_x0-0.01, in_y0, zt-0.01]) cube([frame_ledge_w+0.01, in_y1-in_y0, 0.01]);
            translate([sx>0 ? in_x1-0.01 : in_x0-0.01, in_y0, zt-frame_ledge_w-0.5]) cube([0.02, in_y1-in_y0, frame_ledge_w+0.5]);
          }
          hull() {
            translate([in_x0, in_y0-0.01, zt-0.01]) cube([in_x1-in_x0, holder_y0-0.4-in_y0+0.01, 0.01]);
            translate([in_x0, in_y0-0.01, zt-(holder_y0-0.4-in_y0)-0.5]) cube([in_x1-in_x0, 0.02, holder_y0-0.4-in_y0+0.5]);
          }
        }
      }
      // option "back" screw columns (floor -> ledge height, merged into the end wall)
      for (sx=[-1,1]) intersection() {
        cavity(z_floor_in-1, zt+1);
        hull() {
          translate([sx*frame_screw_back[0], frame_screw_back[1], z_floor_in-0.01]) cylinder(r=frame_boss_r, h=zt-z_floor_in+0.01);
          translate([sx*frame_screw_back[0]-frame_boss_r, in_y0-0.5, z_floor_in-0.01]) cube([2*frame_boss_r, 0.5, zt-z_floor_in+0.01]);
        }
      }
    }
    for (sx=[-1,1]) translate([sx*frame_screw_back[0], frame_screw_back[1], zt-7]) cylinder(d=frame_pilot_d, h=7.01);
    // pry notch on the seam at the top end
    translate([-3, in_y1+wall-0.8, z_split-0.8]) cube([6, 2, 0.81]);
  }
}

// ================= BATTERY FRAME (loose part, assembly pose) =================
// Flat plate between the PCB and the 18650; the BH-18650-PC holder is glued base-up to its flat underside.
// m="front": 2 x M2x5 countersunk self-tapping from UNDER the plate up into the front-shell bosses (frame joins the
//            front + board unit).  m="back": 2 x M2x8 countersunk from ABOVE into the back-shell columns.
// In both cases the plate also sits on the back-shell ledges and the front-shell top post / bosses bear on it when closed.
module battery_frame(m=frame_mount) {
  x1 = in_x1 - frame_clr;  y0 = in_y0 + frame_clr;  y1 = in_y1 - frame_clr;
  difference() {
    union() {
      translate([0,0,z_frame_bot]) rrect(-x1, y0, x1, y1, plan_r_in-frame_clr, frame_t);
      // PCB edge support ribs between the buttons (replace the old back-shell ledges), tapered for stiffness
      for (r=ledge_d) for (sx=[-1,1]) mirror([sx>0 ? 0 : 1,0,0]) hull() {
        translate([frame_rib[0]-0.8, Y(r[1]), z_frame_top-0.01]) cube([frame_rib[1]-frame_rib[0]+0.8, r[1]-r[0], 0.01]);
        translate([frame_rib[0], Y(r[1]), -0.06]) cube([frame_rib[1]-frame_rib[0], r[1]-r[0], 0.01]);
      }
    }
    if (m=="front") for (sx=[-1,1]) translate([sx*frame_screw_front[0], frame_screw_front[1], z_frame_bot]) {
      translate([0,0,-1]) cylinder(d=screw_d, h=frame_t+2);
      translate([0,0,-0.01]) cylinder(d1=frame_csk_d, d2=screw_d, h=(frame_csk_d-screw_d)/2+0.01);
    }
    if (m=="back") for (sx=[-1,1]) translate([sx*frame_screw_back[0], frame_screw_back[1], z_frame_top]) {
      translate([0,0,-frame_t-1]) cylinder(d=screw_d, h=frame_t+2);
      translate([0,0,-(frame_csk_d-screw_d)/2]) cylinder(d1=screw_d, d2=frame_csk_d, h=(frame_csk_d-screw_d)/2+0.01);
    }
    for (y=[holder_y0+holder_pin_in, holder_y1-holder_pin_in]) translate([-pin_slot[0]/2, y-pin_slot[1]/2, z_frame_bot-1]) cube([pin_slot[0], pin_slot[1], frame_t+2]);
    translate([wire_side>0 ? 0 : -(jack_body_w/2+2), holder_y0+holder_pin_in-groove_w/2, z_frame_top-0.9]) cube([jack_body_w/2+2, groove_w, 1]);
    for (y=[holder_y0+holder_hole_from_neg, holder_y0+holder_hole_from_neg+holder_hole_pitch]) translate([0,y,z_frame_bot-1]) cylinder(d=holder_hole_d, h=frame_t+2);
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
}// Switch cap, now TWO pieces because the wall slot is closed (it no longer opens onto the split):
//  carrier = flange (inside the wall pocket) + stem (through the slot); pushed out through the slot from inside before
//            the board goes in.  Its head socket is open toward -Z, so the switch head drops into it with the board.
//  knob    = pressed onto the stem end outside (tight socket, knob_fit per side) + a drop of CA glue.
module switch_carrier(shift=0) {
  yc = Y(sw_d) + shift;  zc = sw_head_z;  x0 = sw_x + 0.15;
  xs1 = in_x1 + wall + 0.2 + knob_socket_l;
  difference() {
    union() {
      translate([x0, yc-cap_flange[0]/2, zc-cap_flange[1]/2]) cube([cap_flange_t, cap_flange[0], cap_flange[1]]);
      translate([x0+cap_flange_t-0.01, yc-cap_stem[0]/2, zc-cap_stem[1]/2]) cube([xs1-(x0+cap_flange_t)+0.01, cap_stem[0], cap_stem[1]]);
    }
    translate([x0-0.01, yc-sw_head[0]/2-cap_socket_clr, zc-cap_flange[1]/2-1]) cube([sw_tip-x0+0.2+0.01, sw_head[0]+2*cap_socket_clr, cap_flange[1]/2+1+sw_head[1]/2+cap_socket_clr]);
  }
}
module switch_knob(shift=0) {
  yc = Y(sw_d) + shift;  zc = sw_head_z;  xk = in_x1 + wall + 0.2;
  difference() {
    union() {
      translate([xk, yc, zc]) rotate([0,90,0]) linear_extrude(cap_knob[2]-0.6) rr2d(cap_knob[1], cap_knob[0], 1.2);
      translate([xk+cap_knob[2]-0.6, yc, zc]) rotate([0,90,0]) hull() { linear_extrude(0.01) rr2d(cap_knob[1], cap_knob[0], 1.2); translate([0,0,0.59]) linear_extrude(0.01) rr2d(cap_knob[1]-1.2, cap_knob[0]-1.2, 0.6); }
    }
    translate([xk-0.01, yc-cap_stem[0]/2-knob_fit, zc-cap_stem[1]/2-knob_fit]) cube([knob_socket_l+0.01, cap_stem[0]+2*knob_fit, cap_stem[1]+2*knob_fit]);
    for (k=[-2:2]) translate([xk+cap_knob[2]-0.35, yc+k*1.2-0.3, zc-cap_knob[1]/2-1]) cube([1, 0.6, cap_knob[1]+2]);
  }
}
module switch_cap(shift=0) { switch_carrier(shift); switch_knob(shift); }

// ================= output =================
// t124u part colours (MI03 = oranges / reds; same hex in tools/palette.py and the coloured 3MF)
C_FRONT   = "#E8731A";  // front shell            orange
C_BACK    = "#F7C08A";  // back shell             peach
C_FRAME   = "#8C3B0C";  // battery frame          brown
C_PLUNGER = "#D62828";  // button plungers        red
C_CARRIER = "#E5B80B";  // switch carrier         mustard
C_KNOB    = "#7A0F2E";  // switch knob            maroon
C_SCREWS  = "#4A4A4A";  // ghost: screws (not printed)
module ghosts(shift=0) { color("green") ghost_pcb(); color("black") ghost_front_parts(); color("silver") ghost_back_parts(shift); color("dimgray") ghost_holder(); color(C_SCREWS) screws(); }
plunger_ys = [for (i=[0:len(btn_d)-1]) if (btn_press[i]) Y(btn_d[i])];
module carrier_print() rotate([0,-90,0]) translate([-(sw_x+0.15),-Y(sw_d),-sw_head_z]) switch_carrier();       // flange inner face on the bed
module knob_print() rotate([0,90,0]) translate([-(in_x1+wall+0.2+cap_knob[2]),-Y(sw_d),-sw_head_z]) switch_knob(); // knob face on the bed

if (part=="front")       translate([0,0,Zf]) rotate([180,0,0]) front_shell();     // front face on the bed
else if (part=="back")   translate([0,0,-Zb]) back_shell();                       // floor on the bed
else if (part=="battery_frame") translate([0,0,-z_frame_bot]) battery_frame();   // flat (glue) face on the bed, ribs up
else if (part=="frame_raw") battery_frame();
else if (part=="plunger") translate([0,0,-(z_btn_top+plunger_gap)]) plunger();   // flange on the bed
else if (part=="switch_carrier") carrier_print();
else if (part=="switch_knob") knob_print();
else if (part=="print") {
  color(C_BACK) translate([0,0,-Zb]) back_shell();
  color(C_FRONT) translate([in_x1-in_x0+2*wall+6, 0, Zf]) rotate([180,0,0]) translate([0,-in_y1-in_y0,0]) front_shell();
  for (k=[0,1]) color(C_PLUNGER) translate([-24, 20+k*9, -(z_btn_top+plunger_gap)]) plunger();
  color(C_FRAME) translate([-2*(in_x1-in_x0)-14, 0, -z_frame_bot]) battery_frame();
  color(C_CARRIER) translate([-24, 45, 0]) carrier_print();
  color(C_KNOB) translate([-24, 56, 0]) knob_print();
}
else if (part=="front_raw") front_shell();
else if (part=="back_raw")  back_shell();
else if (part=="plungers_raw") for (y=plunger_ys) translate([0,y,0]) plunger();
else if (part=="carrier_raw") switch_carrier(cap_shift);
else if (part=="knob_raw") switch_knob(cap_shift);
else if (part=="ghost_pcb") ghost_pcb();
else if (part=="ghost_front") ghost_front_parts();
else if (part=="ghost_back") ghost_back_parts(cap_shift);
else if (part=="ghost_holder") ghost_holder();
else if (part=="ghost_screws") screws();
else if (part=="ghost_board_screws") board_screws();
else if (part=="ghost_frame_screws") frame_screws();
else if (part=="board_unit") { ghost_pcb(); ghost_front_parts(); ghost_back_parts(0); }
else if (part=="usb_view") { color(C_FRONT) front_shell(); color("silver") ghost_back_parts(0); color("green") ghost_pcb(); }
else if (part=="closed") {
  color(C_FRONT) front_shell(); color(C_BACK) back_shell(); color(C_FRAME) battery_frame();
  color(C_PLUNGER) for (y=plunger_ys) translate([0,y,0]) plunger(); color(C_CARRIER) switch_carrier(); color(C_KNOB) switch_knob();
}
else if (part=="exploded") {   // front unit (front + board [+ frame in option "front"]) above, back cover below
  color(C_BACK) translate([0,0,-34]) back_shell();
  translate([0,0,frame_mount=="front" ? -10 : -24]) { color(C_FRAME) battery_frame(); color("dimgray") ghost_holder(); color(C_SCREWS) frame_screws(); }
  color("green") ghost_pcb(); color("black") ghost_front_parts(); color("silver") ghost_back_parts(0); color(C_SCREWS) board_screws();
  color(C_KNOB) translate([6,0,0]) switch_knob(); color(C_CARRIER) switch_carrier();
  color(C_PLUNGER) for (y=plunger_ys) translate([0,y,14]) plunger();
  color(C_FRONT,0.85) translate([0,0,22]) front_shell();
}
else { color(C_FRONT) front_shell(); color(C_BACK) back_shell(); color(C_FRAME) battery_frame(); color(C_PLUNGER) for (y=plunger_ys) translate([0,y,0]) plunger(); color(C_CARRIER) switch_carrier(); color(C_KNOB) switch_knob(); ghosts(); }
