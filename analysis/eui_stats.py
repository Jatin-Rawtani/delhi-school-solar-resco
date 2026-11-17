"""How much electricity do schools use per square metre? Energy-use intensity (EUI) and floor area for the
education buildings in the Building Data Genome 2 dataset, all education versus K-12 schools only.

Data: Building Data Genome 2 (Miller et al. 2020), see data/README.md. Run from the repo root: python analysis/eui_stats.py
"""
import os
DATA = os.environ.get("BDG2_DIR", "data/bdg2")
import csv, collections, statistics
rows = list(csv.DictReader(open(DATA + "/metadata.csv")))
SCHOOL = {"K-12 School", "Primary/Secondary Classroom", "School"}
def num(s):
    try: return float(s)
    except Exception: return None
for label, sel in [("ALL Education", lambda r: r["primaryspaceusage"]=="Education"),
                   ("K-12/school only", lambda r: r["sub_primaryspaceusage"] in SCHOOL)]:
    g = [r for r in rows if sel(r)]
    eui = sorted(x for x in (num(r["eui"]) for r in g) if x)
    sq  = sorted(x for x in (num(r["sqm"]) for r in g) if x)
    print("== %s: n=%d, with electricity meter=%d" % (label, len(g), sum(1 for r in g if r["electricity"]=="Yes")))
    if eui:
        print("   EUI kWh/m2/yr n=%d: min %.0f | p25 %.0f | median %.0f | p75 %.0f | max %.0f | mean %.0f"
              % (len(eui), eui[0], eui[len(eui)//4], statistics.median(eui), eui[3*len(eui)//4], eui[-1], statistics.mean(eui)))
    if sq:
        print("   floor area m2: median %.0f | p25 %.0f | p75 %.0f" % (statistics.median(sq), sq[len(sq)//4], sq[3*len(sq)//4]))
    print("   sites:", dict(collections.Counter(r["site_id"] for r in g)))
