import json, csv, collections, sys
S=sys.argv[1]
crawl=json.load(open(S+"/review/crawl.json")); detail=crawl["detail"]; parts=crawl["parts"]
try:
    for c,v in json.load(open(S+"/review/check_codes.json")).items():
        detail.setdefault(c,{}).update({"code":c,"mpn":v["mpn"],"brand":v["brand"],"lib":v["lib"],"preferred":v["pref"],"stock":v["stock"],"pkg":v["pkg"],"tiers":v["tiers"]})
except FileNotFoundError: pass
live=json.load(open(S+"/a3/em/live.json"))["d"]
for c,x in live.items():
    if not x: continue
    detail[c]={"code":c,"mpn":x["componentModelEn"],"brand":x["componentBrandEn"],"lib":x["componentLibraryType"],"preferred":x["preferredComponentFlag"],"stock":x["stockCount"],"pkg":x.get("componentSpecificationEn") or "","tiers":[{"startNumber":t["startNumber"],"endNumber":t["endNumber"],"productPrice":t["productPrice"]} for t in x["componentPrices"]]}
def price_at(t,q):
    for r in t:
        if q>=r["startNumber"] and (r["endNumber"]==-1 or q<=r["endNumber"]): return r["productPrice"]
    return t[-1]["productPrice"]
SMD=("0603","0805","1206","SOT","SOD","SMA","SOIC","ESOP","1008","SMD","DO-214","5X5","3X3")
def att(pkg,q): return int(round(q*1.03))+4 if any(h in (pkg or "").upper() for h in SMD) else q
def cost(bom,b,fee):
    tot=0;ext=0;miss=[]
    for code,per in bom.items():
        d=detail.get(code)
        if not d or not d.get("tiers"): miss.append(code); continue
        q=att(d["pkg"],per*b); tot+=price_at(d["tiers"],q)*q
        if d["lib"]!="base" and not d.get("preferred"): ext+=1
    return (tot+ext*fee)/b, ext, miss
# v4 (current) from production/bom.csv
v4=collections.Counter()
for r in csv.DictReader(open(S.replace("scratchpad","scratchpad")+"/../../../../../../../Documents/PlatformIO/Projects/EPD_Hub_ESP32/de-link_pcb/production/bom.csv" if False else "C:/Users/iandc/Documents/PlatformIO/Projects/EPD_Hub_ESP32/de-link_pcb/production/bom.csv",encoding="utf-8-sig")):
    if r["LCSC Part #"]: v4[r["LCSC Part #"]]+=int(r["Quantity"])
# old v3 per_board -> new v3
v3=collections.Counter({c:p["per_board"] for c,p in parts.items() if p["per_board"]})
def swap(d,o,n):
    k=d.pop(o,0)
    if k: d[n]+=k
swap(v3,"C350879","C206267"); swap(v3,"C22356394","C112307"); swap(v3,"C413592","C88532")
v3["C907858"]-=1; v3["C19077501"]+=1   # CR1 is SMF6.5CA in both builds
k=v3["C28323"]; 
# C9 moves from the C28323 (1u/50V) line to the 4.7u/50V line (v3 uses C98192)
v3["C28323"]-=1; v3["C98192"]+=1
for name,bom in (("v3 brand-conservative (new)",v3),("v4 optimized (new, from production/bom.csv)",v4)):
    for fee in (1.5,3.0):
        row=[]
        for b in (5,10,30,100):
            c,e,m=cost(bom,b,fee); row.append(f"${c:6.2f}")
        print(f"{name:46} fee ${fee:.2f}  ext={e:2d}  "+"  ".join(row), ("MISSING:"+",".join(m)) if m else "")
