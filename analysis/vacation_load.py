"""How far does a school's electricity use drop in the summer break and at weekends?
Monthly and weekday/weekend load shape for BDG2 schools in Washington DC (with air conditioning) and Cardiff, UK.

Data: Building Data Genome 2 (Miller et al. 2020), see data/README.md. Run from the repo root: python analysis/vacation_load.py
"""
import os
DATA = os.environ.get("BDG2_DIR", "data/bdg2")
import csv, statistics, collections
SCHOOL = {"K-12 School", "Primary/Secondary Classroom", "School"}
meta = {r["building_id"]: r for r in csv.DictReader(open(DATA + "/metadata.csv"))}
schools = {b: r["site_id"] for b, r in meta.items() if r["sub_primaryspaceusage"] in SCHOOL}
import datetime
rd = csv.reader(open(DATA + "/electricity_cleaned.csv", newline=""))
hdr = next(rd)
idx = {i: hdr[i] for i in range(1, len(hdr)) if hdr[i] in schools}
mon = collections.defaultdict(lambda: [0.0, 0])
wk  = collections.defaultdict(lambda: [0.0, 0])   # (b, is_weekend)
for row in rd:
    ts = row[0]
    if len(ts) < 16: continue
    y, mo, d = int(ts[0:4]), int(ts[5:7]), int(ts[8:10])
    we = datetime.date(y, mo, d).weekday() >= 5
    for i, b in idx.items():
        v = row[i]
        if not v: continue
        try: x = float(v)
        except ValueError: continue
        a = mon[(b, mo)]; a[0] += x; a[1] += 1
        c = wk[(b, we)];  c[0] += x; c[1] += 1
mm = collections.defaultdict(dict)
for (b, mo), (s, n) in mon.items():
    if n >= 300: mm[b][mo] = s/n
TERM = [1,2,3,4,5,9,10,11,12]
SUM = {"Rat": [6,7,8], "Lamb": [7,8]}   # US summer break Jun-Aug; UK Jul-Aug
res = collections.defaultdict(list)
shape = collections.defaultdict(lambda: collections.defaultdict(list))
for b, d in mm.items():
    if not all(m in d for m in range(1,13)): continue
    site = schools[b]
    base = statistics.mean(d[m] for m in TERM)
    if base <= 0: continue
    br = SUM.get(site)
    if br: res[site].append(statistics.mean(d[m] for m in br)/base)
    for m in range(1,13): shape[site][m].append(d[m]/base)
for site, v in sorted(res.items(), key=lambda x: -len(x[1])):
    v = sorted(v)
    print("%-6s summer-break/term  n=%-4d p10 %.2f | p25 %.2f | median %.2f | p75 %.2f | mean %.2f"
          % (site, len(v), v[int(.1*len(v))], v[len(v)//4], statistics.median(v), v[3*len(v)//4], statistics.mean(v)))
print()
for site in ("Rat", "Lamb"):
    print("%s monthly shape (term mean = 1.00)  [%s]" % (site, "Washington DC" if site=="Rat" else "Cardiff UK"))
    for m in range(1,13):
        x = statistics.mean(shape[site][m])
        print("   %2d  %.2f  %s" % (m, x, "#"*int(x*40)))
    print()
# weekday vs weekend
print("Weekend / weekday mean load")
agg = collections.defaultdict(list)
for b in idx.values():
    a, c = wk.get((b, False)), wk.get((b, True))
    if not a or not c or a[1] < 1000 or c[1] < 400: continue
    wd, we = a[0]/a[1], c[0]/c[1]
    if wd > 0: agg[schools[b]].append(we/wd)
for site, v in sorted(agg.items(), key=lambda x: -len(x[1])):
    v = sorted(v)
    print("  %-6s n=%-4d p25 %.2f | median %.2f | p75 %.2f | mean %.2f" % (site, len(v), v[len(v)//4], statistics.median(v), v[3*len(v)//4], statistics.mean(v)))
