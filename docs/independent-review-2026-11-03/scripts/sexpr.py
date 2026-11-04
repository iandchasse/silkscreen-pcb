"""Minimal S-expression reader for KiCad netlist / schematic / board files (read-only)."""
import re

_TOKEN = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)


def parse(text):
    stack = [[]]
    pos = 0
    n = len(text)
    while pos < n:
        m = _TOKEN.match(text, pos)
        if not m:
            if text[pos:].strip() == "":
                break
            raise ValueError("parse error at %d: %r" % (pos, text[pos:pos + 40]))
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            done = stack.pop()
            stack[-1].append(done)
        elif m.group(3) is not None:
            stack[-1].append(m.group(3).replace('\\"', '"').replace("\\\\", "\\"))
        else:
            stack[-1].append(m.group(4))
    return stack[0][0]


def find(node, key):
    """Direct children lists whose head == key."""
    return [c for c in node[1:] if isinstance(c, list) and c and c[0] == key]


def find1(node, key, default=None):
    r = find(node, key)
    return r[0] if r else default


def walk(node, key):
    """All descendant lists whose head == key (depth-first)."""
    out = []
    st = [node]
    while st:
        x = st.pop()
        if isinstance(x, list) and x:
            if x[0] == key:
                out.append(x)
            st.extend(c for c in x[1:] if isinstance(c, list))
    return out
