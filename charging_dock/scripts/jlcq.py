import json,urllib.request,sys
def q(kw,n=15):
    req=urllib.request.Request("https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
        data=json.dumps({"keyword":kw,"currentPage":1,"pageSize":n}).encode(),headers={"Content-Type":"application/json","User-Agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req,timeout=60))["data"]["componentPageInfo"]["list"] or []
if __name__=="__main__":
    for kw in sys.argv[1:]:
        print("==",kw)
        for c in q(kw):
            pr=c.get("componentPrices") or [{}]
            print(f'{c["componentCode"]:10s} {c.get("componentModelEn","")[:30]:30s} {c.get("componentSpecificationEn","")[:22]:22s} stk={c.get("stockCount")} {"B" if c.get("componentLibraryType")=="base" else ("P" if c.get("preferredComponentFlag") else "E")} ${pr[0].get("productPrice")} | {(c.get("describe") or "")[:90]}')
