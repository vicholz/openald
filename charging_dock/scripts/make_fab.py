"""OpenALD Dock v1.0 - JLCPCB outputs: gerbers+drill zip, JLC BOM, CPL, centroid, .pos, human BOM (live LCSC stock/prices),
cost estimate.  python3 scripts/make_fab.py"""
import os,sys,csv,subprocess,zipfile,glob,re,json,shutil,collections,urllib.request,math
from datetime import datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import design
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/"; PCB=ROOT+"kicad/openald-dock.kicad_pcb"; FAB=ROOT+"fab/"
GB=FAB+"gerbers/"
# JLC CPL corrections, per (LCSC part, KiCad footprint): (dx, dy, drot) in the KiCad footprint's own frame (mm, Y up,
# before the footprint's board rotation; drot in degrees CCW).  Derived by scripts/jlc_cpl_fit.py, which fits each
# EasyEDA/LCSC footprint (easyeda.com/api/products/<LCSC>/components) onto the KiCad pads of the routed board;
# `python3 jlc_cpl_fit.py --check` re-verifies this table.  Parts not listed need no correction (checked the same way).
JLC_CORR={
 ("C165948","USB_C_Receptacle_HRO_TYPE-C-31-M-12"):            ( 0.000, 1.414,   0),  # J1  EasyEDA origin 1.41 mm toward the pads
 ("C7471904","DFN-10-1EP_3x3mm_P0.5mm_EP1.55x2.48mm"):         ( 0.000, 0.000, 270),  # U1  HUSB238
 ("C16072", "SOIC-8_3.9x4.9mm_P1.27mm"):                       ( 0.000, 0.000, 270),  # Q1  AO4407A
 ("C111875","SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm"):        ( 0.000, 0.000, 270),  # U2/U3 SY8205FCC
 ("C55136", "SOT-23-5"):                                       ( 0.003, 0.000, 270),  # U4-U9 SY6280AAC
 ("C20917", "SOT-23"):                                         ( 0.021, 0.000, 180),  # Q2  AO3400A
}

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
    zp=FAB+"openald-dock-gerbers-jlcpcb.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(GB+"*")): z.write(f,os.path.basename(f))
    print("gerber zip:",zp,[os.path.basename(f) for f in sorted(glob.glob(GB+"*"))])
    pos_csv=export_pos_csv()
    assembled=assembled_parts(); aset={p["ref"] for p in assembled}
    rows,crows,prows,groups=write_jlc_set(
        aset, pos_csv,
        FAB+"openald-dock-BOM-jlcpcb.csv",
        FAB+"openald-dock-CPL-jlcpcb.csv",
        FAB+"openald-dock-centroid.csv",
        FAB+"openald-dock.pos",
        pos_also=tuple(f"J{i}" for i in range(2,8)),
        pos_match_note="fab/openald-dock-centroid.csv and fab/openald-dock-CPL-jlcpcb.csv",
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
    HAND={ # parts not assembled by JLCPCB (no EasyEDA footprint -> JLC cannot verify placement), with where to buy
     **{f"J{i}":("HX TYPE C-M 16P V-SMT vertical USB-C plug (slot %d) - hand solder, see README"%(i-1),None,"https://www.lcsc.com/product-detail/C55200592.html") for i in range(2,8)}}
    EXTRA=[("—","6","M3 x 10 mm screws, socket or pan head (from below, heads in 3 mm counterbores; 4.1 mm standoffs)","~$0.05","https://www.amazon.com/s?k=M3+x+12mm+socket+head+screws"),
           ("—","6","M3 brass heat-set inserts, OD 4.0-4.6 mm x L 4-5.7 mm","~$0.06","https://www.amazon.com/s?k=M3+heat+set+inserts"),
           ("—","4","10 mm round rubber bumper feet (optional)","~$0.05","https://www.amazon.com/s?k=10mm+rubber+bumper+feet"),
           ("—","1","USB-C PD charger, 45 W or more (must offer 20 V >= 2.25 A or 15 V >= 3 A) + USB-C cable","~$15-25","https://www.amazon.com/s?k=45W+USB+C+PD+charger")]
    tot1=0
    with open(FAB+"openald-dock-BOM-human.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["Designator(s)","Qty/board","Value / description","Manufacturer part","LCSC #","JLC library","LCSC stock (live)","Unit price USD (qty 10)","Assembly","Link"])
        for (v,fp,l),refs in groups.items():
            p=parts[refs[0]]; i=info.get(l,{})
            u=i.get("p10"); tot1+= (u or 0)*len(refs)
            how="JLCPCB SMT"
            w.writerow([",".join(sorted(refs,key=natkey)),len(refs),v+" ("+fp+")",p.get("mpn",""),l,i.get("lib","?"),i.get("stock","?"),u,how,f"https://www.lcsc.com/product-detail/{l}.html"])
        for ref,(d,pr,link) in HAND.items():
            l=parts[ref].get("lcsc",""); i=info.get(l,{})
            if pr is None: pr=i.get("p10")
            w.writerow([ref,1,d,parts[ref].get("mpn",""),l,i.get("lib","—") if l else "—",i.get("stock","—") if l else "—",pr,"Hand solder",link])
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


if __name__=="__main__":
    main()
