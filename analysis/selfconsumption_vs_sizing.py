"""If a school's solar system makes X% of its annual electricity, what share of that solar does the school use
at the moment it is made? Real hourly school loads from BDG2 matched to an illustrative clear-sky Delhi solar profile.
Matters for any hour-by-hour (net billing) rule; under Delhi's annual netting the annual balance matters instead.

Data: Building Data Genome 2 (Miller et al. 2020), see data/README.md. Run from the repo root: python analysis/selfconsumption_vs_sizing.py
"""
import os
DATA = os.environ.get("BDG2_DIR", "data/bdg2")
import csv, math, statistics, collections, datetime
# --- Simple clear-sky PV hourly profile for Delhi (28.61N), illustrative ---
LAT = math.radians(28.61)
def pv_hour(doy, hr):
    dec = math.radians(23.45) * math.sin(math.radians(360.0*(284+doy)/365.0))
    # solar hour angle at the middle of the clock hour (solar time approx = clock time)
    ha = math.radians(15.0 * ((hr + 0.5) - 12.0))
    cz = math.sin(LAT)*math.sin(dec) + math.cos(LAT)*math.cos(dec)*math.cos(ha)
    if cz <= 0.02: return 0.0
    am = 1.0/cz
    # Meinel clear-sky beam+diffuse on a fixed tilt~lat, crude; monsoon derate Jul-Sep
    g = 1000.0 * (0.7 ** (am ** 0.678)) * cz + 60.0*cz
    mo = (datetime.date(2017,1,1) + datetime.timedelta(days=doy-1)).month
    derate = 0.62 if mo in (7,8,9) else (0.88 if mo in (1,12) else 1.0)
    return max(0.0, g*derate)

PROF = {}
for doy in range(1, 367):
    for h in range(24):
        PROF[(doy, h)] = pv_hour(doy, h)

SCHOOL = {"K-12 School", "Primary/Secondary Classroom", "School"}
meta = {r["building_id"]: r for r in csv.DictReader(open(DATA + "/metadata.csv"))}
schools = {b: r["site_id"] for b, r in meta.items() if r["sub_primaryspaceusage"] in SCHOOL}
rd = csv.reader(open(DATA + "/electricity_cleaned.csv", newline=""))
hdr = next(rd)
idx = {i: hdr[i] for i in range(1, len(hdr)) if hdr[i] in schools}

series = collections.defaultdict(list)   # building -> list of (pvnorm, load)
for row in rd:
    ts = row[0]
    if len(ts) < 13: continue
    y, mo, d, h = int(ts[0:4]), int(ts[5:7]), int(ts[8:10]), int(ts[11:13])
    doy = datetime.date(y, mo, d).timetuple().tm_yday
    p = PROF[(doy, h)]
    for i, b in idx.items():
        v = row[i]
        if not v: continue
        try: x = float(v)
        except ValueError: continue
        if x < 0: continue
        series[b].append((p, x))

RATIOS = [0.10, 0.20, 0.30, 0.50, 0.75, 1.00]
out = collections.defaultdict(lambda: collections.defaultdict(list))
for b, s in series.items():
    if len(s) < 14000: continue          # need ~most of a year
    sp = sum(p for p, _ in s); sl = sum(l for _, l in s)
    if sp <= 0 or sl <= 0: continue
    for r in RATIOS:
        k = r * sl / sp                  # scale PV so annual gen = r * annual load
        sc = sum(min(k*p, l) for p, l in s)
        out[schools[b]][r].append(sc / (k*sp))   # self-consumption share of generation
for site, label in (("Lamb","Cardiff UK (no AC, load collapses in vacation)"),
                    ("Rat","Washington DC (AC runs through summer)")):
    d = out.get(site)
    if not d: continue
    n = len(d[RATIOS[0]])
    print("== %s  [%s]  n=%d schools" % (site, label, n))
    print("   PV annual gen as %% of annual load  ->  self-consumption share of generation")
    for r in RATIOS:
        v = sorted(d[r])
        print("     %3d%%  ->  median %5.1f%%   (p25 %4.1f%%, p75 %4.1f%%)"
              % (r*100, 100*statistics.median(v), 100*v[len(v)//4], 100*v[3*len(v)//4]))
    print()
