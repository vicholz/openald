"""OpenALD print colour palette (t124u, Victor: "make all 3 cases and their parts different colors so it is easy to
tell the parts apart"). One hue family per case so the families are distinguishable too:
  single board = blues, Feather = greens, MI03 = oranges / reds, dock = purples.
These hex values are repeated as C_* constants in each .scad file (previews) and used by tools/make_3mf.py (coloured
3MF plates); make_3mf.py checks that every .scad still carries its palette. Change them here AND in the .scad."""
PALETTE = {
    "single_board": {   # radio_single_board/case/openald_case.scad
        "case_top":      ("#2E6FD8", "blue",        "front shell"),
        "case_bottom":   ("#9CC3F5", "light blue",  "back cover"),
        "holder_spacer": ("#0B2E6B", "navy",        "holder spacer"),
    },
    "feather": {        # radio_adafruit_feather_rp2040/case/openald_feather_case.scad
        "case_top":      ("#2FA84F", "green",       "front shell"),
        "case_bottom":   ("#A8E0A0", "light green", "back shell"),
        "deck":          ("#0F5A2A", "dark green",  "deck (inner plate)"),
    },
    "mi03": {           # mi03_case/mi03_case.scad
        "mi03_front_shell":                ("#E8731A", "orange",       "front shell"),
        "mi03_back_shell":                 ("#F7C08A", "peach",        "back shell"),
        "mi03_battery_frame_front_mount":  ("#8C3B0C", "brown",        "battery frame (front mount)"),
        "mi03_battery_frame_back_mount":   ("#8C3B0C", "brown",        "battery frame (back mount; print one of the two)"),
        "mi03_button_plunger":             ("#D62828", "red",          "button plunger"),
        "mi03_switch_carrier":             ("#E5B80B", "mustard",      "switch carrier"),
        "mi03_switch_knob":                ("#7A0F2E", "maroon",       "switch knob"),
    },
    "dock": {           # charging_dock/case/openald_dock.scad
        "dock_top_shell":      ("#7B4FB8", "purple",      "top shell"),
        "dock_base":           ("#C9B6E8", "lavender",    "base"),
        "dock_floor_pads_x6":  ("#3B2360", "dark purple", "floor pads (x6)"),
    },
}
