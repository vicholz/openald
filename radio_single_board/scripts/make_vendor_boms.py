#!/usr/bin/env python3
"""Fill the PCBWay (.xlsx) and NextPCB (.xls) BOM templates from the human BOM.

Quantities are per board. The PCBWay title records a 5-board order (xxPCS);
NextPCB has no order-qty field. Spare parts are not added to quantities.
Off-board items (cell, screws, inserts) are omitted. U4, BT1 and J3 are
included and marked DNS (PCBWay) / DNP (NextPCB) so an assembler will not
fit them. Manufacturers are taken only from project data; unknown ones
are left blank.
"""
from __future__ import annotations

import csv
import json
import sys
from copy import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAB = ROOT / "fab"
TMPL = Path(__file__).resolve().parent / "templates"
HUMAN = FAB / "openald-BOM-human.csv"
LOOKUP = FAB / "lcsc_lookup.json"
OUT_PCBWAY = FAB / "openald-BOM-pcbway.xlsx"
OUT_NEXTPCB = FAB / "openald-BOM-nextpcb.xls"
BOARDS = 5

# Manufacturer names attested in design.py / README / the "Manufacturer part" field.
# Do not invent brands for resistor/capacitor series that the project never names.
MFG_FROM_MPN_PREFIX = (
    ("HRO ", "HRO"),
    ("AOS ", "AOS"),
    ("Panasonic ", "Panasonic"),
    ("ST ", "ST"),
    ("WCH ", "WCH"),
    ("Mitsumi ", "Mitsumi"),
    ("MPD ", "MPD"),
)
MFG_FROM_MPN_PAREN = {
    "DW01A (PUOLOP)": ("PUOLOP", "DW01A"),
    "FS8205A (TECH PUBLIC)": ("TECH PUBLIC", "FS8205A"),
}
MFG_FROM_EXACT_MPN = {
    "ATMEGA328PB-AU": "Microchip",
    "XC6206P332MR-G": "Torex",
    "TP4056-42-ESOP8": "TOPPOWER",
}

SKIP_DESIGNATORS = {"—", "-", ""}


def split_mfg_mpn(raw: str) -> tuple[str, str]:
    raw = (raw or "").strip()
    if raw in MFG_FROM_MPN_PAREN:
        return MFG_FROM_MPN_PAREN[raw]
    if raw in MFG_FROM_EXACT_MPN:
        return MFG_FROM_EXACT_MPN[raw], raw
    for prefix, mfg in MFG_FROM_MPN_PREFIX:
        if raw.startswith(prefix):
            return mfg, raw[len(prefix) :].strip()
    return "", raw


def short_package(lookup_pkg: str, designator: str) -> str:
    if lookup_pkg:
        return lookup_pkg
    first = designator.split(",")[0]
    if first == "U4":
        return "11x11mm castellated"
    if first == "BT1":
        return "THT, 2 pins 72.9mm"
    if first == "J3":
        return "2x3 2.54mm pads"
    return ""


def pcbway_type(assembly: str, designator: str) -> str:
    # Template Type values: SMD, DNS, thru-hole. DNS takes priority.
    a = (assembly or "").lower()
    first = designator.split(",")[0]
    if first in {"U4", "BT1", "J3"} or "dnp" in a or a.startswith("hand"):
        return "DNS"
    if "tht" in a or "through-hole" in a or "through hole" in a:
        return "thru-hole"
    return "SMD"


def nextpcb_proc(assembly: str, designator: str) -> str:
    a = (assembly or "").lower()
    first = designator.split(",")[0]
    if first in {"U4", "BT1", "J3"} or "dnp" in a or a.startswith("hand"):
        return "DNP"
    return ""


def notes_for(row: dict) -> str:
    bits = []
    if row["lcsc"]:
        bits.append(f"LCSC {row['lcsc']}")
    if row["type"] in {"DNS", "DNP"} or row["proc"] == "DNP":
        if row["designator"] == "U4":
            bits.append(
                "Hand-solder castellated FM module after assembly; not placed by the assembler."
            )
        elif row["designator"] == "BT1":
            bits.append(
                "Hand-solder THT 18650 holder on the bottom side after assembly. "
                "Fit the + (flat contact) on the square pad at the USB-C end."
            )
        elif row["designator"] == "J3":
            bits.append(
                "Do not fit a header (the case will not close over it). "
                "2x3 ISP pogo pads only, for a one-time bootloader burn."
            )
        else:
            bits.append("Do not populate.")
    if row["designator"] == "SW1":
        bits.append(
            "Through-hole right-angle slide switch, knob off the right edge. "
            "Can be hand-soldered (5 joints) instead of assembled."
        )
    if row["designator"] == "U3":
        bits.append(
            "If out of stock, ATmega328P-AU (LCSC C14877) is a same-footprint drop-in."
        )
    return " ".join(bits)


def load_rows() -> list[dict]:
    lookup = json.loads(LOOKUP.read_text()) if LOOKUP.exists() else {}
    rows = []
    with HUMAN.open(newline="") as f:
        for rec in csv.DictReader(f):
            des = (rec.get("Designator(s)") or "").strip()
            if des in SKIP_DESIGNATORS:
                continue
            assembly = rec.get("Assembly") or ""
            mpn_raw = rec.get("Manufacturer part") or ""
            mfg, mpn = split_mfg_mpn(mpn_raw)
            lcsc = (rec.get("LCSC #") or "").strip()
            if lcsc in {"—", "-"}:
                lcsc = ""
            pkg = lookup.get(lcsc, {}).get("pkg") or ""
            desc = (rec.get("Value / description") or "").strip()
            qty = rec.get("Qty/board") or "1"
            try:
                qty_n = int(float(qty))
            except ValueError:
                qty_n = qty
            row = {
                "designator": des,
                "qty": qty_n,
                "mfg": mfg,
                "mpn": mpn,
                "desc": desc,
                "pkg": short_package(pkg, des),
                "lcsc": lcsc,
                "assembly": assembly,
                "type": pcbway_type(assembly, des),
                "proc": nextpcb_proc(assembly, des),
            }
            row["notes"] = notes_for(row)
            rows.append(row)
    return rows


def apply_style(dest, src):
    dest.font = copy(src.font)
    dest.border = copy(src.border)
    dest.fill = copy(src.fill)
    dest.number_format = src.number_format
    dest.alignment = copy(src.alignment)
    dest.protection = copy(src.protection)


def fill_pcbway(rows: list[dict]) -> None:
    from openpyxl import load_workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.worksheet.hyperlink import Hyperlink

    # Load a second copy only to snapshot data-row styles before we clear them.
    src = TMPL / "pcbway-BOM-template.xlsx"
    style_wb = load_workbook(src)
    style_ws = style_wb["Sheet1"]
    style_cells = [style_ws.cell(7, c) for c in range(1, 10)]

    wb = load_workbook(src)
    ws = wb["Sheet1"]

    footer_specs = []
    for r in (24, 26):
        cell = ws.cell(r, 1)
        footer_specs.append(
            {
                "value": cell.value,
                "font": copy(cell.font),
                "alignment": copy(cell.alignment),
                "fill": copy(cell.fill),
                "border": copy(cell.border),
                "number_format": cell.number_format,
                "hyperlink": cell.hyperlink.target if cell.hyperlink else None,
                "height": ws.row_dimensions[r].height,
            }
        )

    for rng in list(ws.merged_cells.ranges):
        s = str(rng)
        if s in {"A2:B3", "D2:F4"}:
            continue
        ws.unmerge_cells(s)

    ws["D2"] = f"OpenALD v1.0  {BOARDS}PCS BOM"

    # Clear sample data and old footers (rows 7-26).
    for r in range(7, 27):
        for c in range(1, 10):
            cell = ws.cell(r, c)
            cell.value = None
            cell.hyperlink = None

    first = 7
    for i, row in enumerate(rows):
        r = first + i
        values = [
            i + 1,
            row["designator"],
            row["qty"],
            row["mfg"] or None,
            row["mpn"],
            row["desc"],
            row["pkg"],
            row["type"],
            row["notes"] or None,
        ]
        for c, val in enumerate(values, 1):
            dest = ws.cell(r, c, val)
            apply_style(dest, style_cells[c - 1])
            # Package column in the template sometimes uses text format.
            if c == 7:
                dest.number_format = "@"
            # Wrap long designator lists, descriptions and notes.
            if c in (2, 6, 7, 9):
                al = copy(dest.alignment)
                al.wrap_text = True
                dest.alignment = al
        # Type column: use 11 pt when the template did for DNS, otherwise leave as copied (10 pt SMD).
        # Copied from the SMD sample row; values are what matter.

    last_data = first + len(rows) - 1
    # Two blank rows, then the two instruction footers with a blank row between, as in the template.
    f1 = last_data + 3
    f2 = last_data + 5
    for dest_row, spec in ((f1, footer_specs[0]), (f2, footer_specs[1])):
        ws.merge_cells(start_row=dest_row, start_column=1, end_row=dest_row, end_column=9)
        cell = ws.cell(dest_row, 1)
        cell.value = spec["value"]
        cell.font = spec["font"]
        cell.alignment = spec["alignment"]
        cell.fill = spec["fill"]
        cell.border = spec["border"]
        cell.number_format = spec["number_format"]
        if spec["hyperlink"]:
            cell.hyperlink = spec["hyperlink"]
        if spec["height"] is not None:
            ws.row_dimensions[dest_row].height = spec["height"]

    # Pillow must be installed so openpyxl keeps the PCBWay logo.
    if not ws._images:
        raise RuntimeError("PCBWay logo was not loaded; install Pillow and retry")
    wb.save(OUT_PCBWAY)
    style_wb.close()
    wb.close()


def _xlwt_font_from_xlrd(rb, font):
    import xlwt

    f = xlwt.Font()
    f.name = font.name
    f.height = font.height
    f.bold = bool(font.bold)
    f.italic = bool(font.italic)
    f.underline = font.underline_type
    # colour_index 32767 means "system default"; leave xlwt default in that case.
    if font.colour_index not in (32767, None):
        f.colour_index = font.colour_index
    return f


def _xlwt_style_from_xf(rb, xf_index):
    """Rebuild an xlwt XFStyle that matches a template XF as closely as we can."""
    import xlwt

    xf = rb.xf_list[xf_index]
    style = xlwt.XFStyle()
    style.font = _xlwt_font_from_xlrd(rb, rb.font_list[xf.font_index])

    al = xlwt.Alignment()
    # xlrd hor_align: 0 general, 1 left, 2 center, 3 right, ...
    al.horz = xf.alignment.hor_align
    # xlrd vert_align: 0 top, 1 centre, 2 bottom
    al.vert = xf.alignment.vert_align
    al.wrap = 1 if xf.alignment.text_wrapped else 0
    style.alignment = al

    b = xlwt.Borders()
    brd = xf.border
    b.left = brd.left_line_style
    b.right = brd.right_line_style
    b.top = brd.top_line_style
    b.bottom = brd.bottom_line_style
    b.left_colour = brd.left_colour_index
    b.right_colour = brd.right_colour_index
    b.top_colour = brd.top_colour_index
    b.bottom_colour = brd.bottom_colour_index
    style.borders = b

    pat = xlwt.Pattern()
    bg = xf.background
    # fill_pattern 0 = no fill, 1 = solid
    if bg.fill_pattern:
        pat.pattern = bg.fill_pattern
        pat.pattern_fore_colour = bg.pattern_colour_index
        pat.pattern_back_colour = bg.background_colour_index
    style.pattern = pat

    # number format
    if xf.format_key in rb.format_map:
        fmt = rb.format_map[xf.format_key].format_str
        if fmt and fmt not in ("General", "GENERAL"):
            style.num_format_str = fmt
    return style


def fill_nextpcb(rows: list[dict]) -> None:
    import xlrd
    from xlutils.copy import copy as xl_copy

    src = str(TMPL / "nextpcb-BOM-template.xls")
    rb = xlrd.open_workbook(src, formatting_info=True)
    rs = rb.sheet_by_index(0)
    # Snapshot XF styles from the first example data row (row 3, index 2)
    # and from the DNP / C example rows for Procurement Type if needed.
    data_styles = [_xlwt_style_from_xf(rb, rs.cell(2, c).xf_index) for c in range(8)]
    # Qty is a number, centered (col 1). Procurement Type uses the same family.

    wb = xl_copy(rb)
    ws = wb.get_sheet(0)
    ws.name = "BOM"

    # Leave rows 0-1 (headers + "Required"/instructions) untouched.
    # Overwrite example rows starting at row 2, and extend as needed.
    for i, row in enumerate(rows):
        r = 2 + i
        values = [
            row["designator"],
            row["qty"],
            row["mpn"],
            row["mfg"] or "",
            row["pkg"],
            row["desc"],
            row["proc"],
            row["notes"],
        ]
        for c, val in enumerate(values):
            # Keep empty optional fields as empty strings (clears leftover example values).
            style = data_styles[c]
            if c in (0, 4, 5, 7):
                import xlwt
                style = xlwt.XFStyle()
                # shallow-copy the rebuilt style and turn wrap on
                style.font = data_styles[c].font
                style.alignment = xlwt.Alignment()
                style.alignment.horz = data_styles[c].alignment.horz
                style.alignment.vert = data_styles[c].alignment.vert
                style.alignment.wrap = 1
                style.borders = data_styles[c].borders
                style.pattern = data_styles[c].pattern
                style.num_format_str = data_styles[c].num_format_str
            ws.write(r, c, val, style)

    # If we had fewer rows than the template examples, clear the leftovers.
    # (We have more, so this is just a safeguard.)
    for r in range(2 + len(rows), rs.nrows):
        for c in range(8):
            ws.write(r, c, "", data_styles[c])

    wb.save(str(OUT_NEXTPCB))


def main() -> int:
    rows = load_rows()
    if not rows:
        print("No BOM rows loaded from", HUMAN, file=sys.stderr)
        return 1
    fill_pcbway(rows)
    fill_nextpcb(rows)
    print(f"Wrote {OUT_PCBWAY}  ({len(rows)} part rows, per-board qty, title {BOARDS}PCS)")
    print(f"Wrote {OUT_NEXTPCB} ({len(rows)} part rows, per-board qty)")
    dnp = [r["designator"] for r in rows if r["proc"] == "DNP"]
    blank_mfg = [r["designator"] for r in rows if not r["mfg"]]
    print("DNP/DNS:", ", ".join(dnp))
    print("Manufacturer left blank:", ", ".join(blank_mfg) if blank_mfg else "(none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
