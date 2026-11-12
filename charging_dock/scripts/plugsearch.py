import jlcq, json, subprocess
seen={}
for kw in ["Type-C Male Vertical","type-c male surface mount vertical","USB Type-C plug SMD vertical","Type-C 24P male","Type-C 16P male","TYPE-C male 180","Type-C plug","USB-C male","typec male board","Type-C Male Plug Through Hole vertical","Male Type-C Plugin"]:
    for page in (1,2,3):
        try:
            import urllib.request
            req=urllib.request.Request("https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
              data=json.dumps({"keyword":kw,"currentPage":page,"pageSize":50}).encode(),headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
            L=json.load(urllib.request.urlopen(req,timeout=60))["data"]["componentPageInfo"]["list"] or []
        except Exception as e: print(e); L=[]
        for c in L:
            d=(c.get("describe") or "")
            if "Male" in d and (c.get("stockCount") or 0)>=30: seen[c["componentCode"]]=c
for k,c in seen.items():
    print(k, c.get("componentModelEn")[:32], c.get("stockCount"), (c.get("componentPrices") or [{}])[0].get("productPrice"), c.get("describe")[:120])
