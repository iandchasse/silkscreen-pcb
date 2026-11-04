"""Dump components and nets from the KiCad s-expression netlist.

Usage: python netlist_dump.py <netlist.net> <out_dir>
Writes components.txt, nets.txt and netlist.json to out_dir.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sexpr import parse, find, find1  # noqa: E402


def main(path, out_dir):
    root = parse(open(path, encoding="utf-8").read())
    comps = {}
    for c in find(find1(root, "components"), "comp"):
        ref = find1(c, "ref")[1]
        val = find1(c, "value")[1]
        fp = find1(c, "footprint")
        fp = fp[1] if fp else ""
        fields = {}
        fs = find1(c, "fields")
        if fs:
            for f in find(fs, "field"):
                name = find1(f, "name")[1]
                fields[name] = f[2] if len(f) > 2 and isinstance(f[2], str) else ""
        props = {}
        for p in find(c, "property"):
            props[find1(p, "name")[1]] = find1(p, "value")[1] if find1(p, "value") else ""
        lib = find1(c, "libsource")
        libpart = ""
        if lib:
            l = find1(lib, "lib")
            pt = find1(lib, "part")
            libpart = (l[1] if l else "") + ":" + (pt[1] if pt else "")
        comps[ref] = dict(value=val, footprint=fp, fields=fields, props=props, lib=libpart)
    nets = {}
    for n in find(find1(root, "nets"), "net"):
        name = find1(n, "name")[1]
        nodes = []
        for nd in find(n, "node"):
            d = {k: find1(nd, k)[1] for k in ("ref", "pin", "pinfunction", "pintype") if find1(nd, k)}
            nodes.append(d)
        nets[name] = nodes
    os.makedirs(out_dir, exist_ok=True)
    json.dump(dict(components=comps, nets=nets), open(os.path.join(out_dir, "netlist.json"), "w"), indent=1)

    def keyref(r):
        import re
        m = re.match(r"([A-Za-z#]+)(\d+)", r)
        return (m.group(1), int(m.group(2))) if m else (r, 0)

    with open(os.path.join(out_dir, "components.txt"), "w", encoding="utf-8") as f:
        for ref in sorted(comps, key=keyref):
            c = comps[ref]
            dnp = "DNP" if ("dnp" in c["props"] or c["fields"].get("DNP")) else ""
            excl = "noBOM" if "exclude_from_bom" in c["props"] else ""
            f.write(f"{ref:6s} {c['value'][:24]:24s} {dnp:3s} {excl:5s} {c['lib'][:40]:40s} {c['footprint'].split(':')[-1][:40]}\n")
    pin_nets = {}
    with open(os.path.join(out_dir, "nets.txt"), "w", encoding="utf-8") as f:
        for name in sorted(nets):
            nodes = nets[name]
            s = ", ".join(f"{d['ref']}.{d['pin']}({d.get('pinfunction','')})" for d in sorted(nodes, key=lambda d: (keyref(d['ref']), d['pin'])))
            f.write(f"{name}: {s}\n")
            for d in nodes:
                pin_nets[(d["ref"], d["pin"])] = name
    with open(os.path.join(out_dir, "pins_by_ref.txt"), "w", encoding="utf-8") as f:
        for ref in sorted(comps, key=keyref):
            pins = sorted([(p, n) for (r, p), n in pin_nets.items() if r == ref], key=lambda x: (len(x[0]), x[0]))
            f.write(f"{ref} [{comps[ref]['value']}]: " + "; ".join(f"{p}={n}" for p, n in pins) + "\n")
    print(len(comps), "components", len(nets), "nets")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
