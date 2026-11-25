# -*- coding: utf-8 -*-
"""world-atlas TopoJSON → 한반도 해안선(단순화) ../data/korea.json
사용법: python3 geo.py path/to/countries-10m.json"""
import json, sys, os
topo = json.load(open(sys.argv[1]))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for a in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
def arc(i):
    return arcs[i] if i >= 0 else arcs[~i][::-1]
def ring(r):
    pts = []
    for i in r:
        a = arc(i); pts += a if not pts else a[1:]
    return pts
def dp(pts, eps):
    if len(pts) < 3: return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dmax, idx = 0, 0
    L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5 or 1e-12
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        d = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]
def area(p):
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2
out = {}
for g in topo["objects"]["countries"]["geometries"]:
    if g.get("id") not in ("410", "408"): continue
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    rings = []
    for poly in polys:
        r = ring(poly[0])
        if area(r) < 0.0008: continue
        eps = 0.004 if g["id"] == "410" else 0.01
        h = len(r) // 2
        s = dp(r[:h + 1], eps)[:-1] + dp(r[h:], eps)
        if len(s) >= 4:
            rings.append([[round(x, 3), round(y, 3)] for x, y in s])
    out["south" if g["id"] == "410" else "north"] = rings
here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, "..", "data", "korea.json"), "w"), separators=(",", ":"))
print({k: (len(v), sum(len(r) for r in v)) for k, v in out.items()})
