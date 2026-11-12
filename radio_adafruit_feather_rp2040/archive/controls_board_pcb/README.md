# Retired: Feather controls board (PCB)

**Not used by the current OpenALD Feather RP2040 v1.0 design. Kept for reference only; not maintained.**

Until 2026-11-11 the Feather variant had a small JLC-assembled controls PCB carrying the SIQ-02FVS3 thumbwheel, an
SK-12E12 slide switch on the Feather EN pin, a 220k/220k battery divider and two charge-mirror LEDs. At Victor's request
it was replaced by direct mounting: an SS-12F16 switch screwed into the case wall and the wheel glued into a printed
cradle, all hand-wired to the Feather (see `../../README.md`).

Contents: `kicad/` (schematic, routed PCB, libraries), `fab/` (Gerbers, JLC BOM/CPL, ERC/DRC reports as of the
retirement: ERC 0/0, DRC 0), `scripts/` (the generators plus a snapshot of the `layout.py` and `feather_data.py` they
were written against). The generators import `layout` from this folder and write into `../kicad` / `../fab`
relative to `scripts/`; they were not re-run after the move and may need path fixes if you revive them.
The case/frame for this board is in git history (commit before "Feather: direct-mount SS-12F16 switch and glued wheel").
