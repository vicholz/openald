"""JLCPCB outputs for the controls board: gerbers+drill zip, JLC BOM, CPL (with JLC_CORR), centroid, .pos,
human BOM with live LCSC prices/stock (JLCPCB parts API). Paths are relative to this folder."""
import os,sys,csv,subprocess,zipfile,glob,re,json,shutil,collections,urllib.request,math
from datetime import datetime
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import design
ROOT=os.path.dirname(HERE)+"/"; NAME="openald-feather-controls"
PCB=ROOT+"kicad/"+NAME+".kicad_pcb"; FAB=ROOT+"fab/"; GB=FAB+"gerbers/"
# JLC CPL corrections per (LCSC, KiCad footprint): (dx, dy, drot) in the footprint frame (mm, Y up; drot CCW).
# Same parts and footprints as the OpenALD single board, where scripts/jlc_cpl_fit.py fitted the EasyEDA footprints
# onto the KiCad pads; re-verify here with `python3 jlc_cpl_fit.py --check`.  0603 R/C/LEDs need no correction.
JLC_CORR={
 ("C136720","SW_Slide_SPDT_Angled_HRO_SK-12E12-G5"): (-0.076, 0.000, 270),  # SW1 (only if JLC THT-assembles it)
 ("C2925423","Mitsumi_SIQ-02FVS3"):                  ( 0.000,-2.436,   0),  # SW2 EasyEDA origin = pad bbox centre, not wheel axis
}
def run(c): subprocess.run(c,shell=True,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def natkey(r): return (re.sub(r"\d","",r),int(re.sub(r"\D","",r) or 0))
def apply_corr(lcsc,fp,x,y,rot):
    dx,dy,dr=JLC_CORR.get((lcsc,fp),(0,0,0)); a=math.radians(rot)
    return x+dx*math.cos(a)-dy*math.sin(a), y+dx*math.sin(a)+dy*math.cos(a), (rot+dr)%360
def jlc(code):
    if os.environ.get("OPENALD_OFFLINE"): return None   # offline: reuse fab/lcsc_lookup.json
    try:
        req=urllib.request.Request("https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
            data=json.dumps({"keyword":code,"currentPage":1,"pageSize":5}).encode(),headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
        for c in json.load(urllib.request.urlopen(req,timeout=60))["data"]["componentPageInfo"]["list"] or []:
            if c.get("componentCode")==code: return c
    except Exception as e: print("price lookup failed",code,e)
def price_of(pr,q):
    for b in pr:
        if b["startNumber"]<=q and (b["endNumber"]==-1 or q<=b["endNumber"]): return b["productPrice"]
    return pr[0]["productPrice"] if pr else None
def main():
    shutil.rmtree(GB,ignore_errors=True); os.makedirs(GB)
    run(f'kicad-cli pcb export gerbers -o {GB} -l F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin {PCB}')
    run(f'kicad-cli pcb export drill -o {GB} --format excellon --excellon-units mm --excellon-zeros-format decimal --excellon-oval-format alternate --excellon-separate-th --generate-map --map-format gerberx2 --drill-origin plot {PCB}')
    zp=FAB+NAME+"-gerbers-jlcpcb.zip"
    with zipfile.ZipFile(zp,"w",zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(GB+"*")): z.write(f,os.path.basename(f))
    print("gerber zip:",os.path.relpath(zp,ROOT),len(glob.glob(GB+"*")),"files")
    pos_csv="/tmp/fctl_pos.csv"
    run(f'kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp --use-drill-file-origin -o {pos_csv} {PCB}')
    parts=design.PARTS
    asm=[p for p in design.P if p.get("lcsc") and not p.get("hand")]; aset={p["ref"] for p in asm}
    rows=[];crows=[];prows=[]
    for r in csv.DictReader(open(pos_csv)):
        ref=r["Ref"]; x=float(r["PosX"]); y=float(r["PosY"]); rot=float(r["Rot"])
        if ref in aset:
            fp=parts[ref]["fp"].split(":")[1]; x,y,rot=apply_corr(parts[ref]["lcsc"],fp,x,y,rot)
            side="Top" if r["Side"]=="top" else "Bottom"
            rows.append([ref,"%.4fmm"%x,"%.4fmm"%y,side,"%g"%rot]); crows.append([ref,parts[ref]["val"],fp,"%.4f"%x,"%.4f"%y,"%g"%rot,side])
        prows.append((ref,r["Val"],r["Package"],x,y,rot%360,r["Side"]))
    for L_ in (rows,crows,prows): L_.sort(key=lambda a:natkey(a[0]))
    with open(FAB+NAME+"-CPL-jlcpcb.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Designator","Mid X","Mid Y","Layer","Rotation"]); w.writerows(rows)
    with open(FAB+NAME+"-centroid.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Designator","Comment","Footprint","Mid X","Mid Y","Rotation","Layer"]); w.writerows(crows)
    with open(FAB+NAME+".pos","w") as f:
        f.write("### Footprint positions - created on %s (JLC_CORR applied to JLC-assembled refs; SW1 = KiCad origin) ###\n"%datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z"))
        f.write("## Unit = mm, Angle = deg.\n## Side : All\n# Ref     Val                     Package                                       PosX       PosY       Rot  Side\n")
        for ref,val,pkg,x,y,rot,side in prows: f.write("%-9s %-23s %-44s %9.4f %9.4f %8.4f  %s\n"%(ref,val.replace(" ","_"),pkg.replace(" ","_"),x,y,rot,side))
        f.write("## End\n")
    groups=collections.OrderedDict(); _g=collections.OrderedDict()
    for p in asm: _g.setdefault((p["fp"].split(":")[1],p["lcsc"]),[]).append(p)
    for (fpn,l),ps in _g.items(): groups[(" / ".join(dict.fromkeys(p["val"] for p in ps)),fpn,l)]=[p["ref"] for p in ps]
    with open(FAB+NAME+"-BOM-jlcpcb.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Comment","Designator","Footprint","LCSC Part #"])
        for (v,fp,l),refs in groups.items(): w.writerow([v,",".join(sorted(refs,key=natkey)),fp,l])
    print("CPL rows:",len(rows),"JLC BOM lines:",len(groups))
    info={}
    for code in sorted({p["lcsc"] for p in design.P if p.get("lcsc")}):
        c=jlc(code)
        if c:
            pr=c.get("componentPrices") or []
            info[code]=dict(model=c.get("componentModelEn"),pkg=c.get("componentSpecificationEn"),stock=c.get("stockCount"),
                lib="Basic" if c.get("componentLibraryType")=="base" else ("Preferred ext." if c.get("preferredComponentFlag") else "Extended"),
                p1=price_of(pr,1),p10=price_of(pr,10),p50=price_of(pr,50))
    info["_fetched"]=datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    if os.environ.get("OPENALD_OFFLINE") and os.path.exists(FAB+"lcsc_lookup.json"):
        info=json.load(open(FAB+"lcsc_lookup.json"))   # offline: last saved live prices/stock
    else:
        json.dump(info,open(FAB+"lcsc_lookup.json","w"),indent=1)
    tot=0; hand=0
    with open(FAB+NAME+"-BOM-human.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Designator(s)","Qty/board","Value / description","Manufacturer part","LCSC #","JLC library","LCSC stock (live)","Unit price USD (qty 10)","Assembly","Link"])
        for (v,fp,l),refs in groups.items():
            p=parts[refs[0]]; i=info.get(l,{}); u=i.get("p10"); tot+=(u or 0)*len(refs)
            w.writerow([",".join(sorted(refs,key=natkey)),len(refs),v+" ("+fp+")",p.get("mpn",""),l,i.get("lib","?"),i.get("stock","?"),u,"JLCPCB SMT",f"https://www.lcsc.com/product-detail/{l}.html"])
        for p in design.P:
            if p.get("hand") and p.get("lcsc"):
                i=info.get(p["lcsc"],{}); hand+=i.get("p10") or 0
                w.writerow([p["ref"],1,p["val"],p.get("mpn",""),p["lcsc"],i.get("lib","?"),i.get("stock","?"),i.get("p10"),"Hand solder (THT) - or add to JLC THT assembly with JLC_CORR above",f"https://www.lcsc.com/product-detail/{p['lcsc']}.html"])
        w.writerow(["J1",1,"9 wire pads to the Feather (no part)","","","","","","Wires soldered by hand",""])
    ext=sorted({l for (v,fp,l) in groups if info.get(l,{}).get("lib")!="Basic"})
    fee=[l for l in ext if info.get(l,{}).get("lib")=="Extended"]
    s=dict(jlc_parts_cost_per_board_qty10=round(tot,3),hand_solder_lcsc_parts=round(hand,3),extended=ext,fee_bearing_extended=fee,
           extended_setup_fee_estimate_usd=3*len(fee),prices_fetched=info["_fetched"])
    json.dump(s,open(FAB+"cost_summary.json","w"),indent=1); print(json.dumps(s))
if __name__=="__main__": main()
