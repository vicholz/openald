"""Render dock PCB previews (top/bottom, 3D) and export the schematic PDF + PNG."""
import os, subprocess
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pcb = f"{R}/kicad/openald-dock.kicad_pcb"; sch = f"{R}/kicad/openald-dock.kicad_sch"; P = f"{R}/previews"
def run(*a): subprocess.run(a, check=True, capture_output=True)
run("kicad-cli", "pcb", "render", "--side", "top", "--width", "1600", "--height", "1000", "--background", "opaque", "-o", f"{P}/pcb_top.png", pcb)
run("kicad-cli", "pcb", "render", "--side", "bottom", "--width", "1600", "--height", "1000", "--background", "opaque", "-o", f"{P}/pcb_bottom.png", pcb)
run("kicad-cli", "sch", "export", "pdf", "-o", f"{R}/docs/openald-dock-schematic.pdf", sch)
run("pdftoppm", "-r", "60", "-png", "-singlefile", f"{R}/docs/openald-dock-schematic.pdf", f"{P}/schematic")
# copper layers (for reviewing the autorouted power paths)
for lay, n in (("F.Cu,Edge.Cuts,F.Fab", "pcb_copper_top"), ("B.Cu,Edge.Cuts", "pcb_copper_bottom")):
    run("kicad-cli", "pcb", "export", "pdf", "--layers", lay, "--mode-single", "-o", f"/tmp/{n}.pdf", pcb)
    run("pdftoppm", "-r", "150", "-png", "-singlefile", f"/tmp/{n}.pdf", f"{P}/{n}")
print("ok")
