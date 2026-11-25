# -*- coding: utf-8 -*-
"""Wikidata 역 좌표(stations_wikidata.json) + lines.py 순서 → ../data/network.json

사용법: python3 build_data.py
"""
import json, math, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from lines import LINES, ALIASES, MANUAL, OVERRIDE, PROVINCE

HERE = os.path.dirname(os.path.abspath(__file__))
REGION_CENTER = {"수도권": (37.55, 126.98), "부산": (35.17, 129.07), "대구": (35.87, 128.60),
                 "광주": (35.15, 126.85), "대전": (36.35, 127.38), "전국": (36.4, 127.8)}

def norm(s):
    s = re.sub(r"\s*\(.*?\)\s*$", "", s.strip())
    if s.endswith("역") and len(s) > 1: s = s[:-1]
    return s.replace(" ", "")

def km(a, b):
    dy = (a[0] - b[0]) * 111.0
    dx = (a[1] - b[1]) * 111.0 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot(dx, dy)

# Wikidata 후보
cand = {}
for row in json.load(open(os.path.join(HERE, "stations_wikidata.json"), encoding="utf-8")):
    cand.setdefault(norm(row["ko"]), []).append((row["lat"], row["lon"]))

def candidates(name):
    if name in OVERRIDE: return [OVERRIDE[name]]
    keys = [norm(a) for a in ALIASES.get(name, [])] + [norm(name)]
    out = []
    for k in keys: out += cand.get(k, [])
    out += [v for k, v in MANUAL.items() if k.split("@")[0] == name]
    return out

stations = []          # {id, n, lat, lon, lines:set, approx}
by_name = {}           # name -> [idx]
MERGE_KM = 2.5

def place(name, pos, approx=False):
    for i in by_name.get(name, []):
        if km((stations[i]["lat"], stations[i]["lon"]), pos) < MERGE_KM:
            return i
    stations.append(dict(n=name, lat=pos[0], lon=pos[1], lines=[], approx=approx))
    by_name.setdefault(name, []).append(len(stations) - 1)
    return len(stations) - 1

def options(name):
    """이미 배치된 같은 이름 역 + Wikidata 후보"""
    opts = [((stations[i]["lat"], stations[i]["lon"]), i) for i in by_name.get(name, [])]
    opts += [(p, None) for p in candidates(name)]
    return opts

report = []
out_lines = []
for L in LINES:
    maxjump = 30 if L["kind"] == "metro" else 90
    paths_idx = []
    for p in L["paths"]:
        names = p.split()
        pos = [None] * len(names)
        ref = [None] * len(names)
        prev = None; prevk = None
        for k, nm in enumerate(names):
            opts = options(nm)
            if not opts:
                continue
            if prev is None:
                # 다음 역 후보와 가장 가까운 조합 / 지역 중심
                nxt = []
                for j in range(k + 1, min(k + 4, len(names))):
                    nxt = [o[0] for o in options(names[j])]
                    if nxt: break
                anchor = REGION_CENTER[L["region"]]
                def score(o):
                    s = km(o[0], anchor) * 0.05
                    if nxt: s += min(km(o[0], q) for q in nxt)
                    return s - (0.5 if o[1] is not None else 0)
                best = min(opts, key=score)
            else:
                best = min(opts, key=lambda o: km(o[0], prev) - (0.3 if o[1] is not None else 0))
                if km(best[0], prev) > maxjump * (k - prevk):
                    report.append(f"[멀리 떨어짐] {L['name']} {names[k-1] if k else ''}→{nm} {km(best[0], prev):.1f}km")
                    continue
            pos[k], ref[k] = best[0], best[1]
            prev = best[0]; prevk = k
        # 좌표 없는 역 보간
        known = [k for k in range(len(names)) if pos[k] is not None]
        if not known:
            report.append(f"[경로 전체 없음] {L['name']}"); continue
        for k in range(len(names)):
            if pos[k] is not None: continue
            a = max([j for j in known if j < k], default=None)
            b = min([j for j in known if j > k], default=None)
            if a is not None and b is not None:
                t = (k - a) / (b - a)
                pos[k] = (pos[a][0] + (pos[b][0] - pos[a][0]) * t, pos[a][1] + (pos[b][1] - pos[a][1]) * t)
            else:
                j = a if a is not None else b
                off = (k - j) * 0.008
                pos[k] = (pos[j][0] + off, pos[j][1] + off)
            report.append(f"[좌표 추정] {L['name']} {names[k]}")
            ref[k] = "approx"
        idx = []
        for k, nm in enumerate(names):
            if isinstance(ref[k], int):
                i = ref[k]
            else:
                i = place(nm, pos[k], approx=(ref[k] == "approx"))
            if L["id"] not in stations[i]["lines"]:
                stations[i]["lines"].append(L["id"])
            idx.append(i)
        paths_idx.append(idx)
    out_lines.append(dict(id=L["id"], name=L["name"], short=L["short"], color=L["color"],
                          kind=L["kind"], region=L["region"], paths=paths_idx))

# id 부여 (같은 이름이 여러 곳이면 지역/노선 표시)
LMAP = {L["id"]: L for L in LINES}
def sub_label(s):
    metro = [LMAP[l] for l in s["lines"] if LMAP[l]["kind"] == "metro"]
    if metro:
        return metro[0]["region"]
    p = (s["lat"], s["lon"])
    return min(PROVINCE, key=lambda r: km(p, PROVINCE[r]))

seen = {}
for s in stations:
    seen.setdefault(s["n"], []).append(s)
for name, group in seen.items():
    for s in group:
        s["sub"] = "" if len(group) == 1 else sub_label(s)
    base = [s["sub"] for s in group]
    for s in group:
        if base.count(s["sub"]) > 1:   # 같은 지역 안 동명 역 → 노선 이름 덧붙임
            s["sub"] = s["sub"] + " " + re.sub(r"\s*\(.*\)", "", LMAP[s["lines"][0]]["name"]).split()[-1]
    for s in group:
        s["id"] = name if len(group) == 1 else f"{name}@{s['sub']}"

net = dict(
    stations=[dict(id=s["id"], n=s["n"], sub=s["sub"], y=round(s["lat"], 5), x=round(s["lon"], 5),
                   l=s["lines"], **({"a": 1} if s["approx"] else {})) for s in stations],
    lines=out_lines,
)
os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
with open(os.path.join(HERE, "..", "data", "network.json"), "w", encoding="utf-8") as f:
    json.dump(net, f, ensure_ascii=False, separators=(",", ":"))
print(f"역 {len(stations)}개, 노선 {len(out_lines)}개")
print("\n".join(report))
