#!/usr/bin/env python3
"""Write MPN / Manufacturer / LCSC fields (and optionally the DNP flag) into silkscreen_pcb.kicad_sch
from fabrication/part_fields.csv.

    python fabrication/apply_part_fields.py            # dry run: report what would change
    python fabrication/apply_part_fields.py --write    # apply (KiCad must be closed)

- MPN / Manufacturer name the genuine "prime" part (what a hand-builder orders from DigiKey/Mouser).
- LCSC is the JLCPCB/LCSC code actually used for assembly; the Fabrication Toolkit reads this field.
- Only those three fields and the DNP flag are touched. Value, Footprint, Datasheet and any vendor
  fields (MF, MP, MANUFACTURER, ...) are left alone. Re-running is safe: unchanged parts are skipped.
- Pure Python, no KiCad needed. Refuses to run while KiCad has the schematic open (lock file), because
  KiCad would overwrite the edit on its next save. After --write: open the schematic, then
  "Update PCB from Schematic" with "Update footprint fields" ticked so the footprints get the fields too.
"""
import argparse, csv, io, re, shutil, sys
from pathlib import Path

FIELDS = ("MPN", "Manufacturer", "LCSC")
HERE = Path(__file__).resolve().parent


def match_paren(s, i):
    """s[i] == '(' -> index just past the matching ')', honouring quoted strings."""
    depth, n, q = 0, len(s), False
    while i < n:
        c = s[i]
        if q:
            if c == "\\":
                i += 1
            elif c == '"':
                q = False
        elif c == '"':
            q = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced parentheses")


def children(s, start, end):
    """Yield (name, a, b) for each direct child list of the list spanning [start, end)."""
    i = start + 1
    while i < end - 1:
        c = s[i]
        if c == '"':
            i += 1
            while s[i] != '"':
                if s[i] == "\\":
                    i += 1
                i += 1
        elif c == "(":
            j = match_paren(s, i)
            yield re.match(r"\(\s*([^\s()\"]+)", s[i:i + 80]).group(1), i, j
            i = j
            continue
        i += 1


def esc(v):
    return v.replace("\\", "\\\\").replace('"', '\\"')


def unesc(v):
    return re.sub(r"\\(.)", r"\1", v)


PROP_RE = re.compile(r'\(property\s+"((?:[^"\\]|\\.)*)"\s+"((?:[^"\\]|\\.)*)"')


def load_map(path):
    m, order = {}, []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            for ref in (r.strip() for r in row["Refs"].split(",")):
                if not ref:
                    continue
                if ref in m:
                    sys.exit(f"{path.name}: {ref} listed twice")
                m[ref] = {"Value": row.get("Value", "").strip(), "MPN": row["MPN"].strip(), "Manufacturer": row["Manufacturer"].strip(),
                          "LCSC": row["LCSC"].strip(), "DNP": row.get("DNP", "").strip().lower()}
                order.append(ref)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sch", type=Path, default=HERE.parent / "silkscreen_pcb.kicad_sch")
    ap.add_argument("--csv", type=Path, default=HERE / "part_fields.csv")
    ap.add_argument("--write", action="store_true", help="modify the schematic (default is a dry run)")
    ap.add_argument("--force", action="store_true", help="ignore KiCad's lock file")
    a = ap.parse_args()

    parts = load_map(a.csv)
    s = io.open(a.sch, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    lock = a.sch.with_name("~" + a.sch.name + ".lck")
    if a.write and lock.exists() and not a.force:
        sys.exit(f"{lock.name} exists - the schematic is open in KiCad. Close it first (KiCad would overwrite this edit on save).")

    edits, seen, log, warn = [], set(), [], []          # edits: (start, end, replacement)
    added = updated = same = dnp_changed = 0
    for name, sa, sb in children(s, 0, match_paren(s, 0)):
        if name != "symbol":
            continue
        props, last_prop_end, indent = {}, None, "\t\t"
        for n2, c, d in children(s, sa, sb):
            if n2 == "property":
                m = PROP_RE.match(s, c)                  # positions are absolute (pattern.match with pos)
                props[unesc(m.group(1))] = (unesc(m.group(2)), m.start(2), m.end(2))
                last_prop_end = d
                indent = s[s.rfind("\n", 0, c) + 1:c]
        ref = props.get("Reference", ("",))[0]
        if not ref or ref.startswith("#"):
            continue
        head = s[sa:sa + 700]
        in_bom = re.search(r"\(in_bom\s+(yes|no)\)", head).group(1)
        dnp_m = re.search(r"\(dnp\s+(yes|no)\)", head)
        if ref not in parts:
            if in_bom == "yes" and not re.match(r"(H|TP[12]$)", ref):
                warn.append(f"{ref}: in the schematic but not in {a.csv.name}")
            continue
        seen.add(ref)
        want = parts[ref]
        if want["Value"] and want["Value"] != props["Value"][0]:
            warn.append(f"{ref}: schematic Value '{props['Value'][0]}' != CSV Value '{want['Value']}' - is the CSV row still right for this part?")
        fitted = not (dnp_m and dnp_m.group(1) == "yes") and want["DNP"] != "yes"
        if fitted and want["MPN"] and not want["LCSC"]:
            warn.append(f"{ref}: fitted with an MPN but no LCSC - the Fabrication Toolkit would export the MPN as the JLC part number")
        at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)", head)
        new_blocks = ""
        for f in FIELDS:
            if f in props:
                old, va, vb = props[f]
                if old == want[f]:
                    same += 1
                else:
                    edits.append((va, vb, esc(want[f]))); updated += 1; log.append(f"{ref}: {f} '{old}' -> '{want[f]}'")
            else:
                i1, i2, i3, i4 = indent, indent + "\t", indent + "\t\t", indent + "\t\t\t"
                new_blocks += (f'{nl}{i1}(property "{f}" "{esc(want[f])}"{nl}{i2}(at {at.group(1)} {at.group(2)} 0){nl}{i2}(effects{nl}{i3}(font{nl}{i4}(size 1.27 1.27){nl}{i3}){nl}'
                               f'{i3}(hide yes){nl}{i2}){nl}{i1})')
                added += 1
        if new_blocks:
            edits.append((last_prop_end, last_prop_end, new_blocks)); log.append(f"{ref}: + " + ", ".join(f"{f}={want[f] or '-'}" for f in FIELDS if f not in props))
        if want["DNP"] in ("yes", "no") and dnp_m and dnp_m.group(1) != want["DNP"]:
            edits.append((sa + dnp_m.start(1), sa + dnp_m.end(1), want["DNP"])); dnp_changed += 1; log.append(f"{ref}: dnp {dnp_m.group(1)} -> {want['DNP']}")

    for ref in parts:
        if ref not in seen:
            warn.append(f"{ref}: in {a.csv.name} but not in the schematic")
    for line in log:
        print(" ", line)
    print(f"\n{len(seen)} parts matched: {added} fields to add, {updated} to update, {same} already correct, {dnp_changed} DNP flag change(s)")
    for w in warn:
        print("  WARNING:", w)
    if not a.write:
        print("\ndry run - nothing written. Re-run with --write (KiCad closed) to apply.")
        return
    if not edits:
        print("nothing to do.")
        return
    out = s
    for start, end, rep in sorted(edits, key=lambda e: (e[0], e[1]), reverse=True):
        out = out[:start] + rep + out[end:]
    match_paren(out, 0)                                   # sanity: still balanced
    bak = a.sch.with_name(a.sch.name + ".pre-fields.bak")
    shutil.copy2(a.sch, bak)
    io.open(a.sch, "w", encoding="utf-8", newline="").write(out)
    print(f"\nwrote {a.sch.name} (backup: {bak.name}). Next: open it in KiCad, then Update PCB from Schematic with 'Update footprint fields' ticked.")


if __name__ == "__main__":
    main()
