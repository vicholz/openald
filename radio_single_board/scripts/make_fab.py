"""JLCPCB outputs: gerbers+drill zip, BOM (JLC format), CPL, human-readable BOM with prices/links.

Default: regenerate the full fab set (gerbers, BOM, CPL, centroid, .pos, human BOM).
  python3 scripts/make_fab.py --minimal
      writes only fab/minimal/ (hotplate-part assembly set + LCSC hand-solder order list).
      Does not touch gerbers or the full BOM/CPL/centroid/.pos.
"""
import os,sys,csv,subprocess,zipfile,glob,re,json,shutil,collections,urllib.request,math
from datetime import datetime
sys.path.insert(0,os.path.dirname(__file__))
import design
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/"; PCB=ROOT+"kicad/openald.kicad_pcb"; FAB=ROOT+"fab/"
GB=FAB+"gerbers/"

# JLC CPL corrections, per (LCSC part, KiCad footprint): (dx, dy, drot) in the KiCad footprint's own frame
# (mm, Y up, before the footprint's board rotation; drot in degrees CCW).  JLC places the LCSC/EasyEDA footprint
# origin at Mid X/Y and rotates it by Rotation, so CPL = KiCad position + R(kicad_rot)*(dx,dy), rotation + drot.
# Derived by scripts/jlc_cpl_fit.py, which fits each EasyEDA footprint (easyeda.com/api/products/<LCSC>/components,
# JLCEDA/EasyEDA official library) onto the KiCad pads; `python3 jlc_cpl_fit.py --check` re-verifies this table.
# Parts not listed (0603/0805/1206 R, C, L, LEDs, SOD-123 diodes; EVQ-P7A until SW2 was removed) need no correction (checked the same way).
JLC_CORR={
 ("C95562", "Jack_3.5mm_KoreanHropartsElec_PJ-320D-4A_Horizontal"): ( 0.800, 0.000,  90),  # J2  EasyEDA origin = pad bbox centre, mouth along -Y
 ("C136720","SW_Slide_SPDT_Angled_HRO_SK-12E12-G5"):                 (-0.076, 0.000, 270),  # SW1 EasyEDA pins along Y, knob +X
 ("C165948","USB_C_Receptacle_HRO_TYPE-C-31-M-12"):                  ( 0.000, 1.414,   0),  # J1  EasyEDA origin 1.41 mm toward the pads
 ("C2925423","Mitsumi_SIQ-02FVS3"):                                  ( 0.000,-2.436,   0),  # SW3 EasyEDA origin = pad bbox centre, not wheel axis
 ("C351410","SOT-23-6"):                                             ( 0.000, 0.000, 270),  # U2  DW01A, EasyEDA pin 1 bottom-left
 ("C2830320","SOT-23-6"):                                            ( 0.000, 0.000, 180),  # Q1  FS8205A, EasyEDA pin 1 bottom-right
 ("C5446",  "SOT-23-3"):                                             ( 0.032, 0.000, 180),  # U5  XC6206
 ("C16581", "SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm"):            ( 0.000, 0.000, 270),  # U1  TP4056 ESOP-8
 # rev 4 parts (fitted the same way; overlays in previews/cpl_overlay_U3/U6/U7/U8.png)
 ("C132230","TQFP-32_7x7mm_P0.8mm"):                                 ( 0.000, 0.000, 270),  # U3  ATmega328PB-AU, EasyEDA pin 1 bottom-left
 ("C14877", "TQFP-32_7x7mm_P0.8mm"):                                 ( 0.000, 0.000, 270),  # U3 alt. ATmega328P-AU (same EasyEDA TQFP-32 land)
 ("C968586","SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm"):               ( 0.000, 0.000, 270),  # U7  CH340K ESSOP-10, EasyEDA pin 1 bottom-left
 ("C7519",  "SOT-23-6"):                                             ( 0.000, 0.000, 270),  # U8  USBLC6-2SC6, EasyEDA pin 1 bottom-left
 # rev 4.2 reverse-polarity FETs (overlays in previews/cpl_overlay_Q2.png, cpl_overlay_Q3.png)
 ("C15127", "SOT-23"):                                               ( 0.071, 0.000, 180),  # Q2/Q4 AO3401A, EasyEDA origin = pad bbox centre (pins 1/2 right)
 ("C20917", "SOT-23"):                                               ( 0.021, 0.000, 180),  # Q3  AO3400A, same, slightly different land length
}

# Parts that really need factory reflow / a hotplate: exposed-pad SO packages, 0.8 mm-pitch TQFP, and the mid-mount USB-C.
# SOT-23 / SOT-23-6 (U2 DW01A, Q1 FS8205A, U8 USBLC6, Q2/Q3/Q4, U5/U6) are left off: all pins are on the sides, no
# bottom-only pad, and they are routine with an iron or a hot-air station. This project's FS8205A is SOT-23-6, not TSSOP-8.
MINIMAL_REFS = ("J1", "U1", "U3", "U7")

def run(c):
    subprocess.run(c,shell=True,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def natkey(r):
    return (re.sub(r"\d","",r),int(re.sub(r"\D","",r) or 0))

def apply_corr(lcsc, fp, x, y, rot):
    dx,dy,dr=JLC_CORR.get((lcsc,fp),(0,0,0))
    a=math.radians(rot)
    x+=dx*math.cos(a)-dy*math.sin(a)
    y+=dx*math.sin(a)+dy*math.cos(a)
    rot=(rot+dr)%360
    return x,y,rot

def export_pos_csv(path="/tmp/pos.csv"):
    run(f'kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp --use-drill-file-origin -o {path} {PCB}')
    return path

def assembled_parts():
    return [p for p in design.P if p.get("lcsc") and not p.get("dnp") and not p.get("hand")]

def write_jlc_set(aset, pos_csv, bom_path, cpl_path, centroid_path, pos_path, pos_also=(), pos_match_note=""):
    """Write JLC BOM + CPL + centroid + KiCad .pos for the designators in aset. JLC_CORR is applied to assembled refs."""
    parts=design.PARTS
    # CPL
    rows=[]
    for r in csv.DictReader(open(pos_csv)):
        ref=r["Ref"]
        if ref not in aset: continue
        fp=parts[ref]["fp"].split(":")[1]; rot=float(r["Rot"]); x=float(r["PosX"]); y=float(r["PosY"])
        x,y,rot=apply_corr(parts[ref]["lcsc"],fp,x,y,rot)
        rows.append([ref,"%.4fmm"%x,"%.4fmm"%y,"Top" if r["Side"]=="top" else "Bottom","%g"%rot])
    rows.sort(key=lambda x:(re.sub(r"\d","",x[0]),int(re.sub(r"\D","",x[0]) or 0)))
    os.makedirs(os.path.dirname(cpl_path) or ".", exist_ok=True)
    with open(cpl_path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["Designator","Mid X","Mid Y","Layer","Rotation"]); w.writerows(rows)
    # centroid
    crows=[]
    for r in csv.DictReader(open(pos_csv)):
        ref=r["Ref"]
        if ref not in aset: continue
        fp=parts[ref]["fp"].split(":")[1]; rot=float(r["Rot"]); x=float(r["PosX"]); y=float(r["PosY"])
        x,y,rot=apply_corr(parts[ref]["lcsc"],fp,x,y,rot)
        crows.append([ref,parts[ref]["val"],fp,"%.4f"%x,"%.4f"%y,"%g"%rot,"Top" if r["Side"]=="top" else "Bottom"])
    crows.sort(key=lambda x:(re.sub(r"\d","",x[0]),int(re.sub(r"\D","",x[0]) or 0)))
    with open(centroid_path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["Designator","Comment","Footprint","Mid X","Mid Y","Rotation","Layer"]); w.writerows(crows)
    # KiCad ASCII .pos
    prows=[]
    also=set(pos_also)
    for r in csv.DictReader(open(pos_csv)):
        ref=r["Ref"]
        if ref not in aset and ref not in also: continue
        rot=float(r["Rot"]); x=float(r["PosX"]); y=float(r["PosY"])
        if ref in aset:
            fp=parts[ref]["fp"].split(":")[1]
            x,y,rot=apply_corr(parts[ref]["lcsc"],fp,x,y,rot)
        else:
            rot=rot%360
        prows.append((ref,r["Val"],r["Package"],x,y,rot,r["Side"]))
    prows.sort(key=lambda x:(re.sub(r"\d","",x[0]),int(re.sub(r"\D","",x[0]) or 0)))
    with open(pos_path,"w") as f:
        f.write("### Footprint positions - created on %s ###\n"%datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"))
        f.write("### Unit = mm, Angle = deg. Positions match %s\n"%pos_match_note)
        f.write("## Unit = mm, Angle = deg.\n")
        f.write("## Side : All\n")
        f.write("# Ref     Val                     Package                                                   PosX       PosY       Rot  Side\n")
        for ref,val,pkg,x,y,rot,side in prows:
            f.write("%-9s %-23s %-56s %9.4f %9.4f %8.4f  %s\n"%(ref,val.replace(" ","_"),pkg.replace(" ","_"),x,y,rot,side))
        f.write("## End\n")
    # JLC BOM, one line per LCSC part, in design.P order
    groups=collections.OrderedDict()
    _g=collections.OrderedDict()
    assembled=[p for p in design.P if p["ref"] in aset]
    for p in assembled: _g.setdefault((p["fp"].split(":")[1],p["lcsc"]),[]).append(p)
    for (fpn,l),ps in _g.items():
        v=" / ".join(dict.fromkeys(p["val"] for p in ps)); groups[(v,fpn,l)]=[p["ref"] for p in ps]
    with open(bom_path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["Comment","Designator","Footprint","LCSC Part #"])
        for (v,fp,l),refs in groups.items(): w.writerow([v,",".join(sorted(refs,key=natkey)),fp,l])
    return rows, crows, prows, groups

def jlc(code):
    if os.environ.get("OPENALD_OFFLINE"): return None   # offline: reuse fab/lcsc_lookup.json
    try:
        req=urllib.request.Request("https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
            data=json.dumps({"keyword":code,"currentPage":1,"pageSize":5}).encode(),headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
        L=json.load(urllib.request.urlopen(req,timeout=60))["data"]["componentPageInfo"]["list"] or []
        for c in L:
            if c.get("componentCode")==code: return c
    except Exception as e: print("price lookup failed",code,e)
    return None

def price_of(pr, q):
    for b in pr:
        if b["startNumber"]<=q and (b["endNumber"]==-1 or q<=b["endNumber"]): return b["productPrice"]
    return pr[0]["productPrice"] if pr else None

def load_lookup():
    path=FAB+"lcsc_lookup.json"
    if os.path.exists(path):
        return json.load(open(path))
    return {}

# ---- full fab (default) -------------------------------------------------
def main():
    shutil.rmtree(GB,ignore_errors=True); os.makedirs(GB)
    run(f'kicad-cli pcb export gerbers -o {GB} -l F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin {PCB}')
    run(f'kicad-cli pcb export drill -o {GB} --format excellon --excellon-units mm --excellon-zeros-format decimal --excellon-oval-format alternate --excellon-separate-th --generate-map --map-format gerberx2 --drill-origin plot {PCB}')
    zp=FAB+"openald-gerbers-jlcpcb.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(GB+"*")): z.write(f,os.path.basename(f))
    print("gerber zip:",zp,[os.path.basename(f) for f in sorted(glob.glob(GB+"*"))])
    pos_csv=export_pos_csv()
    assembled=assembled_parts(); aset={p["ref"] for p in assembled}
    rows,crows,prows,groups=write_jlc_set(
        aset, pos_csv,
        FAB+"openald-BOM-jlcpcb.csv",
        FAB+"openald-CPL-jlcpcb.csv",
        FAB+"openald-centroid.csv",
        FAB+"openald.pos",
        pos_also=("BT1","U4"),
        pos_match_note="fab/openald-centroid.csv and fab/openald-CPL-jlcpcb.csv",
    )
    print("CPL rows:",len(rows))
    print("centroid rows:",len(crows))
    print("pos rows:",len(prows))
    print("JLC BOM lines:",len(groups))
    # ---- prices / stock (live JLCPCB parts API) for the human BOM
    info={}
    for code in sorted({p["lcsc"] for p in design.P if p.get("lcsc")}):
        c=jlc(code)
        if c:
            pr=c.get("componentPrices") or []
            info[code]=dict(model=c.get("componentModelEn"),pkg=c.get("componentSpecificationEn"),stock=c.get("stockCount"),
                            lib="Basic" if c.get("componentLibraryType")=="base" else ("Preferred ext." if c.get("preferredComponentFlag") else "Extended"),
                            p1=price_of(pr,1),p10=price_of(pr,10),p50=price_of(pr,50))
    if os.environ.get("OPENALD_OFFLINE") and os.path.exists(FAB+"lcsc_lookup.json"):
        info=json.load(open(FAB+"lcsc_lookup.json"))   # offline: last saved live prices/stock
    else:
        json.dump(info,open(FAB+"lcsc_lookup.json","w"),indent=1)
    parts=design.PARTS
    HAND={ # parts not assembled by JLCPCB, with where to buy
     "U4":("RRD-102V2.0 RDA5807M FM module (11x11mm castellated)","~$1-2 ea (often sold in 5-10 packs)","https://www.amazon.com/s?k=RDA5807M+RRD-102+FM+module"),
     "BT1":("MPD BH-18650-PC 18650 PCB holder (THT, 2 pins 72.9mm)","~$3","https://www.digikey.com/en/products/result?keywords=BH-18650-PC"),
     "J3":("2x3 2.54mm AVR-ISP pogo pads (ATmega328PB MISO/SCK/MOSI/RESET, 3.3 V) - bootloader burn only; do not leave a header fitted","~$0.10 (or a 2x3 pogo clip)","https://www.digikey.com/en/products/result?keywords=2x3%20pin%20header%202.54mm"),
    }
    EXTRA=[("—","1","18650 Li-ion cell (flat or button top; protected cells up to ~69mm fit the MPD holder)","~$5","https://www.amazon.com/s?k=18650+battery"),
           ("—","4","M2 x 12 mm screws, pan or socket head (M2 x 16 if using the hex-nut case option)","~$0.05","https://www.amazon.com/s?k=M2+x+12mm+socket+head+screws"),
           ("—","4","M2 brass heat-set inserts, OD 3.2-3.5 mm x L 3-4 mm (or M2 hex nuts)","~$0.05","https://www.amazon.com/s?k=M2+heat+set+inserts")]
    tot1=0
    with open(FAB+"openald-BOM-human.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["Designator(s)","Qty/board","Value / description","Manufacturer part","LCSC #","JLC library","LCSC stock (live)","Unit price USD (qty 10)","Assembly","Link"])
        for (v,fp,l),refs in groups.items():
            p=parts[refs[0]]; i=info.get(l,{})
            u=i.get("p10"); tot1+= (u or 0)*len(refs)
            how="JLCPCB THT (Standard PCBA) - or delete the BOM line and hand-solder" if p.get("tht") else "JLCPCB SMT"
            w.writerow([",".join(sorted(refs,key=natkey)),len(refs),v+" ("+fp+")",p.get("mpn",""),l,i.get("lib","?"),i.get("stock","?"),u,how,f"https://www.lcsc.com/product-detail/{l}.html"])
        for ref,(d,pr,link) in HAND.items():
            l=parts[ref].get("lcsc",""); i=info.get(l,{})
            if pr is None: pr=i.get("p10")
            w.writerow([ref,1,d,parts[ref].get("mpn",""),l,i.get("lib","—") if l else "—",i.get("stock","—") if l else "—",pr,"Hand solder" if ref!="J3" else "DNP",link])
        for e in EXTRA: w.writerow([e[0],e[1],e[2],"","","","",e[3],"Off-board",e[4]])
    print("JLC-assembled parts cost per board (qty-10 pricing): $%.2f"%tot1)
    ext=sorted({l for (v,fp,l) in groups if info.get(l,{}).get("lib")!="Basic"})
    print("extended part types:",len(ext),ext)
    # JLC waives the extended-part (feeder) fee for "Preferred extended" parts, so only plain Extended parts cost ~$3 each
    fee=sorted(l for l in ext if info.get(l,{}).get("lib")=="Extended")
    print("fee-bearing extended part types:",len(fee),fee)
    hand_cost=sum((info.get(parts[r].get("lcsc",""),{}).get("p10") or 0) for r in HAND)
    print("hand-solder LCSC parts: $%.2f"%hand_cost)
    json.dump(dict(parts_cost=tot1,extended=ext,hand_solder_lcsc_parts=hand_cost,fee_bearing_extended=fee,extended_setup_fee_estimate=3*len(fee)),open(FAB+"cost_summary.json","w"),indent=1)

# ---- minimal (hotplate) set ---------------------------------------------
def _spare_qty(fp, n_per_board, refs, lcsc, unit_price):
    """Sensible spares for 5 boards. 0603/small passives get more; unique ICs/mechanicals get one. Labelled in the CSV."""
    fl=(fp or "").lower()
    # 0603 resistors, caps, beads
    if "0603" in fl or "1608" in fl:
        if "led" in fl:
            return 3, "LED: +3 spares (easy to lose or overheat)"
        return 10, "0603 passive: +10 spares (cheap, easy to lose)"
    if "0805" in fl or "2012" in fl or "1206" in fl or "3216" in fl:
        return 2, "0805/1206 cap: +2 spares"
    if "sod-123" in fl:
        return 3, "SOD-123 diode: +3 spares"
    if "sot-23" in fl:
        return 1, "SOT-23 / SOT-23-3 / SOT-23-6: +1 spare (hot air can lift them)"
    # Mechanical / unique: one spare, call out if the part is pricey
    note="+1 spare"
    if unit_price and unit_price >= 1.0:
        note="+1 optional spare (part is about $%.2f each; skip if you want to save)"%unit_price
    return 1, note

def write_handsolder_order(groups_full, info, out_path, boards=5):
    parts=design.PARTS
    # Remaining LCSC parts: in the full JLC BOM (assembled) but not in the minimal set, plus none of the hand-only module/holder.
    rows=[]
    for (v,fp,l),refs in groups_full.items():
        if any(r in MINIMAL_REFS for r in refs):
            continue
        p=parts[refs[0]]; i=info.get(l,{})
        n=len(refs)
        unit=i.get("p10") or i.get("p1")
        sp, policy=_spare_qty(fp, n, refs, l, unit)
        order=n*boards+sp
        rows.append({
            "LCSC #": l,
            "Order qty": order,
            "Qty per board": n,
            "Qty for 5 boards": n*boards,
            "Spares": sp,
            "Spare policy": policy,
            "Designator(s)": ",".join(sorted(refs,key=natkey)),
            "Value / description": v,
            "Manufacturer part": p.get("mpn",""),
            "Package / footprint": fp,
            "JLC library": i.get("lib",""),
            "Unit price USD (qty 10)": unit if unit is not None else "",
            "Link": f"https://www.lcsc.com/product-detail/{l}.html",
        })
    cols=["LCSC #","Order qty","Qty per board","Qty for 5 boards","Spares","Spare policy",
          "Designator(s)","Value / description","Manufacturer part","Package / footprint",
          "JLC library","Unit price USD (qty 10)","Link"]
    with open(out_path,"w",newline="") as f:
        w=csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return rows

def write_minimal_cost(groups_min, info, out_path, boards=5):
    # Published Economic PCBA fees (JLCPCB PCB Assembly Cost page; same $3.07 feeder figure used in this README).
    SETUP=8.18; STENCIL=1.53; FEEDER=3.07; SMT_JOINT=0.0016; CONFIRM=0.45
    PCB_5PCS=2.00  # earlier project estimate for 5 pcs, 38x87 mm, 2-layer 1.6 mm; not a live quote
    # Joints: count SMT pads on the four parts (from the board).
    joints_per_board=13+32+12+16  # U1 13, U3 32, U7 12, J1 16 SMT (J1 also has 6 mid-mount mechanical pads)
    fee_parts=[]; pref=[]; basic=[]
    parts_cost=0.0
    lines=[]
    for (v,fp,l),refs in groups_min.items():
        i=info.get(l,{})
        lib=i.get("lib","?")
        # For 5 pcs, use the qty-1 break if the qty-10 break starts at 10.
        unit=i.get("p1") if i.get("p1") is not None else i.get("p10")
        # Prefer the bracket that actually covers qty=5: if p10 exists and p1 exists, p1 applies below 10.
        n=len(refs)*boards
        cost=(unit or 0)*n
        parts_cost+=cost
        if lib=="Extended": fee_parts.append(l)
        elif lib=="Preferred ext.": pref.append(l)
        else: basic.append(l)
        lines.append("  %s  %s  %s  x%d  $%.4f ea  $%.2f  [%s]"%( ",".join(refs), l, v, n, unit or 0, cost, lib))
    feeder=FEEDER*len(fee_parts)
    smt=SMT_JOINT*joints_per_board*boards
    sub=PCB_5PCS+SETUP+STENCIL+feeder+smt+CONFIRM+parts_cost
    text=[]
    text.append("OpenALD v1.0 — estimated JLC cost for 5 boards, MINIMAL (hotplate) assembly")
    text.append("ESTIMATE ONLY. Fees from JLCPCB's published Economic PCBA table (setup $8.18, stencil $1.53,")
    text.append("extended feeder $3.07 / type, SMT $0.0016 / joint, confirm-placement $0.45). PCB $2 is the")
    text.append("earlier project estimate for 5 pcs of this 38x87 mm 2-layer 1.6 mm board, not a live quote.")
    text.append("Shipping, tax and any US tariff are NOT included. Prices drift.")
    text.append("")
    text.append("Parts JLC places: J1 USB-C (C165948), U1 TP4056 (C16581, Preferred ext.), U3 ATmega328PB-AU")
    text.append("(C132230), U7 CH340K (C968586).")
    text.append("")
    text.append("Parts:")
    text.extend(lines)
    text.append("  Parts subtotal (5 boards, qty-1 unit prices): $%.2f"%parts_cost)
    text.append("")
    text.append("Fees (Economic PCBA, one order):")
    text.append("  PCB, 5 pcs (estimate)                         $%.2f"%PCB_5PCS)
    text.append("  Setup                                         $%.2f"%SETUP)
    text.append("  Stencil (kept by JLC, not shipped)            $%.2f"%STENCIL)
    text.append("  Extended feeder loading  %d x $%.2f           $%.2f"%(len(fee_parts), FEEDER, feeder))
    text.append("    fee-bearing: %s"%(", ".join(fee_parts) if fee_parts else "(none)"))
    text.append("    no fee (Preferred ext.): %s"%(", ".join(pref) if pref else "(none)"))
    text.append("  SMT assembly  %d joints x 5 x $%.4f          $%.2f"%(joints_per_board, SMT_JOINT, smt))
    text.append("  Confirm parts placement                       $%.2f"%CONFIRM)
    text.append("  ------------------------------------------------")
    text.append("  Estimated order total, before ship/tariff     $%.2f"%sub)
    text.append("")
    text.append("Notes: J1 is mid-mount and has 6 extra mechanical pads; JLC may quote some of those as manual")
    text.append("joints (~$0.0164 each). That would add at most a couple of dollars. This is not a live cart quote.")
    open(out_path,"w").write("\n".join(text)+"\n")
    return sub, parts_cost, fee_parts

def main_minimal():
    out=FAB+"minimal/"; os.makedirs(out, exist_ok=True)
    pos_csv=export_pos_csv("/tmp/pos_minimal.csv")
    aset=set(MINIMAL_REFS)
    rows,crows,prows,groups=write_jlc_set(
        aset, pos_csv,
        out+"openald-BOM-jlcpcb-minimal.csv",
        out+"openald-CPL-jlcpcb-minimal.csv",
        out+"openald-centroid-minimal.csv",
        out+"openald-minimal.pos",
        pos_also=(),
        pos_match_note="fab/minimal/openald-centroid-minimal.csv and fab/minimal/openald-CPL-jlcpcb-minimal.csv",
    )
    print("minimal CPL rows:",len(rows), [r[0] for r in rows])
    print("minimal centroid rows:",len(crows))
    print("minimal pos rows:",len(prows))
    print("minimal JLC BOM lines:",len(groups))
    # Full assembled groups, for the hand-solder LCSC list (no live re-fetch; use cached lookup).
    full_assembled=assembled_parts()
    full_g=collections.OrderedDict()
    for p in full_assembled:
        full_g.setdefault((p["fp"].split(":")[1],p["lcsc"]),[]).append(p)
    groups_full=collections.OrderedDict()
    for (fpn,l),ps in full_g.items():
        v=" / ".join(dict.fromkeys(p["val"] for p in ps))
        groups_full[(v,fpn,l)]=[p["ref"] for p in ps]
    info=load_lookup()
    hs=write_handsolder_order(groups_full, info, out+"openald-LCSC-order-handsolder.csv")
    print("hand-solder LCSC lines:",len(hs))
    tot, pc, fee=write_minimal_cost(groups, info, out+"cost_estimate.txt")
    print("estimated 5-board total (no ship/tariff): $%.2f"%tot)
    print("fee-bearing extended:", fee)

if __name__=="__main__":
    if "--minimal" in sys.argv:
        main_minimal()
    else:
        main()
