#!/usr/bin/env python3
"""Side section (to scale, through the plug centreline across the radio width) of one dock pocket with each radio
variant docked: PCB, fixed vertical plug, floor pad, riser shim, radio bottom wall and USB-C receptacle mouth.
All values from geom.py. Usage: plot_insertion.py out.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom as G
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/dock_plug_insertion_per_radio.png"
cases = [("Single-board radio\n(standard pad)", "single_board", 0.0), ("Feather radio\n(standard pad + %.2f shim)" % G.RISER["feather"], "feather", G.RISER["feather"]),
         ("Feather radio WITHOUT shim\n(not allowed: plug bottoms out)", "feather", 0.0)]
fig, axs = plt.subplots(1, 3, figsize=(15, 7), sharey=True)
for ax, (title, r, rise) in zip(axs, cases):
    m = G.MOUTHS[r]; rb = G.FLOOR_Z + rise; mouth = rb + m; ins = G.PLUG_TOP - mouth
    ax.add_patch(Rectangle((-14, G.PCB_Z0), 28, G.PCB_T, color="darkgreen"))
    ax.add_patch(Rectangle((-14, G.PCB_Z1), 28 - 0, G.PAD_T, color="dimgray")); ax.add_patch(Rectangle((-4.6, G.PCB_Z1), 9.2, G.PAD_T + 0.01, color="white"))
    if rise > 0:
        ax.add_patch(Rectangle((-14, G.FLOOR_Z), 28, rise, color="gold")); ax.add_patch(Rectangle((-4.6, G.FLOOR_Z), 9.2, rise, color="white"))
    # radio bottom wall (opening 9.44 wide) and the receptacle (8.40 cavity) from the mouth up
    if r == "feather":
        ax.add_patch(Rectangle((-14, rb + 1.5), 14 - 4.72, m - 1.5, color="orange")); ax.add_patch(Rectangle((4.72, rb + 1.5), 14 - 4.72, m - 1.5, color="orange"))
        ax.add_patch(Rectangle((-14, rb), 14 - 6.5, 1.5, color="orange")); ax.add_patch(Rectangle((6.5, rb), 14 - 6.5, 1.5, color="orange"))
    else:
        ax.add_patch(Rectangle((-14, rb), 14 - 4.72, m, color="orange")); ax.add_patch(Rectangle((4.72, rb), 14 - 4.72, m, color="orange"))
    ax.add_patch(Rectangle((-5.4, mouth), 1.0, 7.35, color="slategray")); ax.add_patch(Rectangle((4.4, mouth), 1.0, 7.35, color="slategray"))
    seat_lo, seat_hi = mouth + G.SEAT_NOM - G.SEAT_TOL, mouth + G.SEAT_NOM + G.SEAT_TOL
    ax.axhspan(seat_lo, seat_hi, xmin=0.3, xmax=0.7, color="red", alpha=0.18)
    ax.add_patch(Rectangle((-4.125, G.PCB_Z1), 8.25, G.PLUG_H, color="silver", ec="k", lw=0.6))
    ax.annotate("", (8, mouth), (8, G.PLUG_TOP), arrowprops=dict(arrowstyle="<->"))
    ax.text(8.4, (mouth + G.PLUG_TOP) / 2, "%.2f" % ins, va="center", fontsize=12, weight="bold")
    ax.axhline(mouth, color="k", lw=0.5, ls=":"); ax.text(-13.8, mouth + 0.15, "receptacle mouth (%.2f in)" % m, fontsize=8)
    bad = ins > G.SEAT_NOM + G.SEAT_TOL
    ax.set_title(title + ("\ninsertion %.2f > %.2f: radio rests on the plug" % (ins, seat_hi - mouth) if bad else "\ninsertion %.2f, radio rests on the pad" % ins),
                 fontsize=10, color="firebrick" if bad else "k")
    ax.set_xlim(-14, 14); ax.set_ylim(G.PCB_Z0 - 0.5, 24); ax.set_aspect("equal"); ax.set_xlabel("mm (across the radio width)")
axs[0].set_ylabel("Z above the dock bottom, mm")
fig.suptitle("OpenALD Dock v1.0: plug insertion per radio (plug %.2f tall from HX drawing; red band = USB-C full seat %.2f +/- %.2f past the mouth)"
             % (G.PLUG_H, G.SEAT_NOM, G.SEAT_TOL), fontsize=11)
fig.tight_layout(); fig.savefig(out, dpi=110)
