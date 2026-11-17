"""The two-sided price band for a leased (RESCO) rooftop solar system at a Delhi school, equations E1 to E15.

For a given first-year PPA price, model() returns the school's NPV, the RESCO's equity NPV and the lowest debt
coverage ratio. The script then solves for:
  - the CEILING: the highest price at which the school still saves money (school NPV = 0)
  - the FLOOR:   the lowest price at which the company earns its equity return AND meets the bank's coverage ratio
If floor <= ceiling there is a price both sides can accept. Every equation is explained in docs/EQUATIONS.md.

INPUTS ARE PLACEHOLDERS. This run shows the chain computes end to end; it is not a result. Each input is being
replaced with a verified source (status column in docs/EQUATIONS.md), and the Monte Carlo layer (E16) and
sensitivity layer (E17) are built on top of this function.
Run: python model/resco_price_band.py
"""
import numpy as np
from scipy.optimize import brentq

def model(PPA1, x, school_keeps_export=True):
    T = x["T"]; t = np.arange(1, T + 1)
    E = x["P"] * x["Y"] * (1 - x["d"]) ** (t - 1)                       # E1 generation
    L = np.full(T, x["L"])                                                 # E2 school use
    O = np.minimum(E, L); S = np.maximum(E - L, 0)                         # E3 annual netting
    Pr = x["Pr0"] * (1 + x["g"]) ** (t - 1)                                # E4 avoided tariff
    ppa = PPA1 * (1 + x["e"]) ** (t - 1)
    cs = 1.0 if school_keeps_export else 0.0
    sav = Pr * O + cs * x["APPC"] * S - ppa * E                            # E5 school saving
    npv_s = np.sum(sav / (1 + x["ds"]) ** t)                               # E6 school NPV
    # RESCO
    I = x["P"] * x["capex"]
    R = ppa * E + (1 - cs) * x["APPC"] * S                                 # E9 revenue
    OM = x["om"] * I * (1 + x["gom"]) ** (t - 1); OM[x["inv_yr"] - 1] += x["inv"] * x["P"]   # E10
    D0 = x["debt"] * I; A = D0 * x["id"] / (1 - (1 + x["id"]) ** -x["nd"])  # E12 loan annuity (CRF)
    bal = D0; interest = np.zeros(T); DS = np.zeros(T)
    for k in range(T):
        if k < x["nd"]:
            interest[k] = bal * x["id"]; DS[k] = A; bal -= (A - interest[k])
    wdv = I; dep = np.zeros(T)
    for k in range(T):
        dep[k] = wdv * x["dep"]; wdv -= dep[k]
    tax = np.maximum(x["tau"] * (R - OM - dep - interest), 0)              # E11 tax (no loss carry-forward: conservative)
    CFADS = R - OM - tax                                                   # E12
    fcfe = CFADS - DS                                                      # E13
    npv_e = -(I - D0) + np.sum(fcfe / (1 + x["ke"]) ** t)
    dscr_min = np.min(CFADS[: x["nd"]] / DS[: x["nd"]])
    return npv_s, npv_e, dscr_min

x = dict(T=25, P=50, Y=1450, d=0.007, L=70000, Pr0=8.5 * 1.18 * 1.05, g=0.02, APPC=5.5,
         e=0.0, ds=0.08, capex=42000, om=0.01, gom=0.03, inv_yr=12, inv=5000,
         debt=0.7, id=0.105, nd=10, dep=0.40, tau=0.2517, ke=0.15)
for keep in (True, False):
    ceil = brentq(lambda p: model(p, x, keep)[0], 0.1, 50)                # E7 ceiling
    floor = brentq(lambda p: model(p, x, keep)[1], 0.1, 50)               # E14 floor
    print(f"school keeps export={keep}: floor (RESCO break-even) = Rs {floor:.2f}/kWh, "
          f"ceiling (school break-even) = Rs {ceil:.2f}/kWh, band width = {ceil-floor:.2f}, "
          f"min DSCR at floor = {model(floor, x, keep)[2]:.2f}")
x2 = dict(x, L=25000)
ceil = brentq(lambda p: model(p, x2, True)[0], 0.1, 50); floor = brentq(lambda p: model(p, x2, True)[1], 0.1, 50)
print(f"small school (25 MWh/yr), school keeps export: floor {floor:.2f}, ceiling {ceil:.2f}, width {ceil-floor:.2f}")

# E14 corrected: the floor must meet BOTH the equity hurdle and the lender's minimum DSCR (Bolinger 2009; Rarasati et al. 2026 Eq. 7)
def floor_price(x, keep=True, dscr_req=1.2):
    p_eq = brentq(lambda p: model(p, x, keep)[1], 0.1, 50)
    p_ds = brentq(lambda p: model(p, x, keep)[2] - dscr_req, 0.1, 50)
    return max(p_eq, p_ds), p_eq, p_ds
for L in (70000, 25000):
    xx = dict(x, L=L)
    f, pe, pd = floor_price(xx)
    c = brentq(lambda p: model(p, xx, True)[0], 0.1, 50)
    print(f"L={L/1000:.0f} MWh: floor = {f:.2f} (equity {pe:.2f}, DSCR 1.2 {pd:.2f}), ceiling = {c:.2f}, width = {c-f:.2f}")
