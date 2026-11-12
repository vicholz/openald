import os,copy
from sexp import parse,find,find1,Sym
LIBDIR="/usr/share/kicad/symbols/"
_cache={}
def load_lib(path):
    if path not in _cache:
        _cache[path]=parse(open(path).read())
    return _cache[path]
def get_symbol(lib_id, extra_libs={}):
    lib,name=lib_id.split(":")
    path=extra_libs.get(lib, LIBDIR+lib+".kicad_sym")
    L=load_lib(path)
    syms={s[1]:s for s in find(L,"symbol")}
    s=copy.deepcopy(syms[name])
    ext=find1(s,"extends")
    if ext:
        base=copy.deepcopy(syms[ext[1]])
        while find1(base,"extends"):
            base=copy.deepcopy(syms[find1(base,"extends")[1]])
        bname=base[1]
        # props from derived override
        props={p[1]:p for p in find(s,"property")}
        new=[Sym("symbol"),name]
        for item in base[2:]:
            if isinstance(item,list) and item[0]=="property" and item[1] in props:
                new.append(props.pop(item[1]))
            elif isinstance(item,list) and item[0]=="symbol":
                sub=copy.deepcopy(item); sub[1]=sub[1].replace(bname,name,1); new.append(sub)
            else: new.append(item)
        for p in props.values(): new.insert(2,p)
        s=new
    return s
def pins(sym):
    out=[]
    def walk(e,unit):
        for x in e:
            if isinstance(x,list):
                if x[0]=="symbol":
                    parts=x[1].rsplit("_",2); u=int(parts[-2]) if len(parts)>=3 and parts[-2].isdigit() else 0
                    walk(x,u)
                elif x[0]=="pin":
                    at=find1(x,"at"); nm=find1(x,"name"); nu=find1(x,"number"); ln=find1(x,"length")
                    out.append(dict(type=str(x[1]),x=float(at[1]),y=float(at[2]),ang=float(at[3]) if len(at)>3 else 0,name=nm[1],num=nu[1],unit=unit,len=float(ln[1])))
    walk(sym,0)
    return out
if __name__=="__main__":
    import sys
    for lid in sys.argv[1:]:
        s=get_symbol(lid); print("==",lid)
        for p in pins(s): print("  %(num)-4s %(name)-12s %(type)-14s (%(x)g,%(y)g) a%(ang)g u%(unit)d"%p)
        for pr in find(s,"property"): print("   prop",pr[1],"=",pr[2][:80])
