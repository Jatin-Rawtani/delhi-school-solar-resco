# The model in plain English

Every equation in the model, what it means in words, where it comes from in the literature, and why it is there. Equation numbers (E1 to E18) are this project's own; each one records the paper and equation it is built on. This file is generated from `tools/recipe_data.py` by `tools/make_equations_md.py`, so the words and the code share one source.

## A. Energy: shared by both parties

### E1. Annual solar generation

> E<sub>t</sub> = P × Y × (1 − d)<sup>t−1</sup>

**In words.** What the system makes in year t: its size times how many units each kWp makes in a year, reduced a little every year as the panels age.

**Source.** Rarasati, Firdaus & Ifrad (2026), Eq. 1 (same form with capacity factor); Narula & Reddy (2015), Eq. 2; physical basis in Sommerfeldt & Madani (2017a), Eq. 2

**Why it is here.** Every rupee on both sides of the deal is priced per unit generated, so this is the first link in the chain.

**Where it sits.** Layer 1, both ledgers. Y and d are drawn from distributions in Layer 2.

### E2. School's annual electricity use

> L<sub>t</sub> = L<sub>0</sub>  (from 24 months of bills; optional sub-model: L = β<sub>0</sub> + β<sub>1</sub>·CDD + β<sub>2</sub>·school days + ε)

**In words.** How many units the school uses in a year. Read directly from its bills. If we want to explain or project it, a small regression on cooling degree days and school days does that.

**Source.** load shape and calendar from Rashid, Singh & Singh (2019) I-BLEND; bill-validation step from Baruah et al. (2025), Fig. 9

**Why it is here.** Under Delhi's annual netting, the size of the system relative to this number decides how many units earn the full tariff and how many fall to APPC.

**Where it sits.** Layer 1 input; Layer 2 distribution (from the regression's prediction interval or the spread in the bills).

### E3. Delhi annual net-metering balance

> O<sub>t</sub> = min(E<sub>t</sub>, L<sub>t</sub>),   S<sub>t</sub> = max(E<sub>t</sub> − L<sub>t</sub>, 0),   G<sub>t</sub> = max(L<sub>t</sub> − E<sub>t</sub>, 0)

**In words.** Solar units are banked against the school's use, unit for unit, over the year to 31 March. O is the part that offsets bought units, S is the year-end surplus (paid at APPC), G is what the school still buys.

**Source.** DERC (Net Metering for Renewable Energy) Regulations 2014, Reg. 9, and Delhi Solar Policy 2023, Appendix II; energy balance as in Haffaf et al. (2020), Eq. 11, and rolling credit as in Ordóñez et al. (2022), Eq. 4

**Why it is here.** This is the Delhi rule that decides what happens to the power a day school cannot use.

**Where it sits.** Layer 1. Time-of-day netting for kVAh-billed consumers is applied within the year where needed.

## B. The school's ledger

### E4. Avoided tariff over time

> P<sub>r,t</sub> = c<sub>e</sub> × (1 + FPPAS) × (1 + ED) × (1 + g)<sup>t−1</sup>

**In words.** What one unit from the grid costs the school in year t: the energy charge, plus the fuel surcharge, plus electricity duty, growing at rate g each year.

**Source.** Retail price built from its components as in Sommerfeldt & Madani (2017b), Eq. 7; growth treated as an uncertain input as in Khan et al. (2026), Table 3 (EPER, Uniform 5–9%/yr)

**Why it is here.** In Khan et al. (2026, Table 8) tariff growth alone explained 47% of the variance in NPV (first-order index 0.474), the largest of five inputs. It is likely to matter most here too.

**Where it sits.** Layer 1, school side; g is a Layer 2 distribution built from the DERC tariff history.

### E5. School's yearly saving under the RESCO PPA

> ΔC<sub>t</sub> = P<sub>r,t</sub>·O<sub>t</sub> + c<sub>s</sub>·APPC·S<sub>t</sub> − PPA<sub>t</sub>·E<sub>t</sub>,   PPA<sub>t</sub> = PPA<sub>1</sub>(1 + e)<sup>t−1</sup>

**In words.** The bill the school no longer pays, plus the year-end credit if the contract gives it to the school, minus what it pays the RESCO for every unit generated.

**Source.** Benefit structure from Sommerfeldt & Madani (2017a), Eq. 5, split between the two parties; customer saving as in Metawe & Brent (2026), Eq. 4; who keeps the export credit is a contract term (Lazo, Haddad & Watts 2025, p. 6)

**Why it is here.** This is the school's side of the deal, year by year.

**Where it sits.** Layer 1. c<sub>s</sub> = 1 or 0 is run as two scenarios.

### E6. School's net present value of the PPA

> NPV<sub>s</sub> = Σ<sub>t=1</sub><sup>T</sup> ΔC<sub>t</sub> / (1 + d<sub>s</sub>)<sup>t</sup>

**In words.** All the yearly savings added up in today's money. The school puts in no capital, so there is no year-0 term.

**Source.** Sommerfeldt & Madani (2017a), Table 2 (NPV); Sommerfeldt & Madani (2017b), Eq. 3

**Why it is here.** Answers ‘does the school save money?’, the first half of the feasibility question.

**Where it sits.** Layer 1; d<sub>s</sub> is the school's own discount rate (Sommerfeldt & Madani 2017a, p. 1387).

### E7. Ceiling: the highest PPA price the school can accept

> PPA<sub>max</sub> solves NPV<sub>s</sub>(PPA<sub>1</sub>) = 0

**In words.** The first-year PPA price at which the school's savings over the contract are exactly zero. Any price below this saves the school money.

**Source.** Two-sided feasible band from Metawe & Brent (2026); break-even pricing method as in Halimatussadiah et al. (2023)

**Why it is here.** The top of the feasible band.

**Where it sits.** Layer 1 output; a distribution in Layer 2.

### E8. The school's other option: buy the system (CAPEX)

> NPV<sub>buy</sub> = −C + Σ<sub>t</sub> [P<sub>r,t</sub>O<sub>t</sub> + APPC·S<sub>t</sub> − OM<sub>t</sub>] / (1 + d<sub>s</sub>)<sup>t</sup>;   NAL = NPV<sub>PPA</sub> − NPV<sub>buy</sub>

**In words.** If the school paid for the system itself, this is what it would gain. The difference tells us whether leasing beats buying for this school. For a school that pays no tax, the textbook lease-versus-buy formula reduces to this comparison.

**Source.** Lease valuation of Franks & Hodges (1978): V<sub>0</sub> formula p. 662; the case of a lessee that cannot use tax shields, p. 664; Ibrik & Hashaika (2019), Eq. 5; Sommerfeldt & Madani (2017a), Eqs. 4–5

**Why it is here.** The project compares two ways for a school to pay for solar: buy it or lease it.

**Where it sits.** Layer 1, school side; reported alongside the PPA result.

## C. The leasing company's (RESCO's) ledger

### E9. RESCO revenue

> R<sub>t</sub> = PPA<sub>t</sub>·E<sub>t</sub> + (1 − c<sub>s</sub>)·APPC·S<sub>t</sub>

**In words.** The company is paid for every unit generated, plus the year-end credit if the contract gives it to the company.

**Source.** Narula & Reddy (2015), Eq. 3; Metawe & Brent (2026), Eq. 2 (inflows)

**Why it is here.** The company's side starts from the same units as the school's.

**Where it sits.** Layer 1, RESCO side.

### E10. Operating costs and inverter replacement

> OM<sub>t</sub> = om·C·(1 + g<sub>om</sub>)<sup>t−1</sup> + 1[t = t<sub>inv</sub>]·C<sub>inv</sub>

**In words.** Yearly upkeep as a share of the system cost, rising each year, plus one inverter replacement in the year it falls due.

**Source.** Sommerfeldt & Madani (2017b), §5 and Table 3 (0.25% of cost rising 1%/yr; inverter replaced once, year 15); Pereira et al. (2014), Eq. 3 (replacement, with compound rather than simple inflation); O&M distribution from Khan et al. (2026), Table 3

**Why it is here.** Delhi dust adds cleaning cost (Al-Otaibi et al. 2015; Sharma, Goel & Lenka 2023).

**Where it sits.** Layer 1, RESCO side; om is a Layer 2 distribution.

### E11. Income tax

> Tax<sub>t</sub> = τ × max(R<sub>t</sub> − OM<sub>t</sub> − Dep<sub>t</sub> − Int<sub>t</sub>, 0)

**In words.** Corporate tax on profit after operating costs, depreciation and loan interest.

**Source.** Narula & Reddy (2015), Eqs. 6–7; Rarasati, Firdaus & Ifrad (2026), Eq. 5 (which leaves interest out); tax shield treatment as in Martínez-Ruiz et al. (2025), Eq. 5

**Why it is here.** Depreciation and interest change what the company keeps; Sommerfeldt & Madani (2017a, p. 1384) warn that leaving taxes out can change the answer.

**Where it sits.** Layer 1, RESCO side.

### E12. Cash available for debt, and the bank's limit

> CFADS<sub>t</sub> = R<sub>t</sub> − OM<sub>t</sub> − Tax<sub>t</sub>;   DS<sub>t</sub> ≤ CFADS<sub>t</sub> / DSCR<sub>min</sub>;   DS = D<sub>0</sub>·i(1+i)<sup>n</sup>/((1+i)<sup>n</sup>−1)

**In words.** The cash that can go to the bank each year, the largest loan payment the bank allows, and the yearly payment on a loan of D<sub>0</sub> at rate i over n years.

**Source.** Rarasati, Firdaus & Ifrad (2026), Eqs. 4 and 7; Jena et al. (2016, CPI), DSCR definition; loan annuity as in Narula & Reddy (2015), Eq. 5 and Heck, Smith & Hittinger (2016), Eq. 2

**Why it is here.** Indian RESCOs borrow most of their capital, and CIF/PwC (2018, p. 33) call the limited availability of financing one of the biggest challenges for Indian rooftop solar.

**Where it sits.** Layer 1, RESCO side.

### E13. Equity cash flow, NPV and IRR

> FCFE<sub>t</sub> = CFADS<sub>t</sub> − DS<sub>t</sub>;   NPV<sub>e</sub> = −(C − D<sub>0</sub>) + Σ FCFE<sub>t</sub>/(1 + k<sub>e</sub>)<sup>t</sup>;   IRR<sub>e</sub>: NPV<sub>e</sub> = 0

**In words.** What is left for the company's owners each year after paying the bank, its value today at the return they require, and the return it actually earns.

**Source.** Jena et al. (2016, CPI), equity IRR definition; Narula & Reddy (2015), Eqs. 8–10; k<sub>e</sub> by CAPM as in Rarasati et al. (2026), Eq. 3 and Sommerfeldt & Madani (2017a), Eq. 6

**Why it is here.** Answers ‘is it viable for the company leasing it?’ CPI reports Indian rooftop equity returns of 14.1% against a 15% hurdle.

**Where it sits.** Layer 1, RESCO side.

### E14. Floor: the lowest PPA price the RESCO can accept

> PPA<sub>min</sub> = max{ PPA<sub>1</sub>: NPV<sub>e</sub> = 0 ;  PPA<sub>1</sub>: min<sub>t</sub> CFADS<sub>t</sub>/DS<sub>t</sub> = DSCR<sub>min</sub> }

**In words.** The lowest first-year price at which the company both earns its required equity return and keeps the bank's coverage ratio. Whichever test bites first sets the floor.

**Source.** Levelised revenue requirement of Bolinger (2009) (every investor return and every debt-coverage constraint met); break-even price as in Halimatussadiah et al. (2023)

**Why it is here.** The bottom of the feasible band. A placeholder dry run showed the bank's ratio, not equity, can be the binding test.

**Where it sits.** Layer 1 output; a distribution in Layer 2.

### E15. The feasible band

> Band = [PPA<sub>min</sub>, PPA<sub>max</sub>];   feasible if PPA<sub>min</sub> ≤ PPA<sub>max</sub>;   width W = PPA<sub>max</sub> − PPA<sub>min</sub>

**In words.** If the company's floor is below the school's ceiling, there is a price both can accept, and the deal is feasible for both. If not, no price works.

**Source.** Metawe & Brent (2026), feasible PPA price band

**Why it is here.** This is the direct answer to the research question, in one number per run.

**Where it sits.** Layer 1 headline; its probability is the Layer 2 headline.

## D. Uncertainty and sensitivity

### E16. Monte Carlo: the probability that a feasible band exists

> For n = 1…N: draw X<sup>(n)</sup>, compute W<sup>(n)</sup>;   P(feasible) = (1/N)·Σ<sub>n</sub> 1[W<sup>(n)</sup> ≥ 0];   report P10, P50, P90;   precision: mean ± 1.96·S/√N

**In words.** Run E1–E15 thousands of times, each time drawing the uncertain inputs from their distributions, and count how often a price exists that works for both. Report the spread, not one number, and show enough runs were done.

**Source.** Probability of profitability from Sommerfeldt & Madani (2017b), §8.1; pairwise probability as in Heck, Smith & Hittinger (2016), Table 10; distributions as in Khan et al. (2026), Table 3, and Sommerfeldt & Madani (2017b), Table 6; convergence interval from Khan et al. (2026), Eq. 8

**Why it is here.** A decision under uncertainty needs probability distributions, not single numbers.

**Where it sits.** Layer 2. N = 10,000 (Heck et al. 2016, p. 25).

### E17. Sensitivity: which inputs drive the answer

> Step 1: one-at-a-time ranges (tornado).   Step 2: S<sub>i</sub> = V[E(Y|X<sub>i</sub>)] / V(Y),   S<sub>Ti</sub> = E[V(Y|X<sub>−i</sub>)] / V(Y)

**In words.** First vary each input from low to high on its own to see which ones matter. Then measure what share of the spread in the result each input causes, alone (S<sub>i</sub>) and with its interactions (S<sub>Ti</sub>).

**Source.** Two-step order from Sommerfeldt & Madani (2017b), §6 and Table 5; indices from Syal & MacDonald (2020), Eqs. 1–2 and Khan et al. (2026), Eq. 16; computed with SALib as in Qutaina (2026)

**Why it is here.** Sommerfeldt & Madani (2017a, p. 1389) say Monte Carlo cannot stand alone; sensitivity analysis finds the critical factors.

**Where it sits.** Layer 3.

### E18. Policy scenario: net billing

> ΔC<sub>t</sub><sup>NB</sup> = Σ<sub>h</sub> [P<sub>r</sub>·min(e<sub>h</sub>, l<sub>h</sub>) + APPC·max(e<sub>h</sub> − l<sub>h</sub>, 0)] − PPA<sub>t</sub>·E<sub>t</sub>

**In words.** If Delhi moved from banking units to paying exports at APPC hour by hour, only solar used at the moment it is made would save the full tariff. This needs an hourly load and generation profile.

**Source.** Ordóñez et al. (2022), Eqs. 5–6; the Uttar Pradesh case in Boruah & Chandel (2024), where exports are paid at APPC (₹4.89 vs a ₹8.86 tariff)

**Why it is here.** Sommerfeldt & Madani (2017a, p. 1387) put the net-metering fine print (settlement period, roll-over, limits) on the analyst; a 25-year contract outlives any one regulation.

**Where it sits.** Scenario run of Layers 1–3; hourly shapes from PVGIS and I-BLEND.

## Variables

Status shows how far each input has got: VERIFIED (read in the primary source), PARTIAL, LITERATURE (taken from a study), TO GET or TO VERIFY (still open), CHOICE or SCENARIO (set by design), OUTPUT (solved for).

| Symbol | Meaning | Units | Used in | Current value (Delhi) | Data source | Status | How it varies in the Monte Carlo |
|---|---|---|---|---|---|---|---|
| P | System size | kWp | E1 | 50 kWp candidate | Design choice (system-size memo, 2026); to be checked against the school's annual use | CHOICE | Fixed per run; test 25–100 kWp |
| Y | Specific yield | kWh/kWp/yr | E1 | ~1,450 central; 1,618 PVGIS upper bound | PVGIS-ERA5, 28.61°N 77.21°E, 2005–2020: 1,618 kWh/kWp (re.jrc.ec.europa.eu/pvg_tools); NASA POWER GHI 4.89 kWh/m²/day (power.larc.nasa.gov) | PULLED 29 Oct | Triangular or normal below the simulated value; year-to-year CV 1.6% (PVGIS) to 4.4% (Sommerfeldt & Madani 2017b) |
| d | Degradation rate | %/yr | E1 | 0.8% mean | Jordan & Kurtz, via Khan et al. 2026 Table 3 and Park & Kim 2017 | LITERATURE | Gamma(2, 0.004) |
| L | School annual use | kWh/yr | E2, E3 | from bills | The school's 24 months of bills; fallback I-BLEND Lecture building (doi:10.6084/m9.figshare.c.3893581) | TO GET | From regression prediction interval or bill spread |
| c<sub>e</sub> | Energy charge, non-domestic | ₹/kVAh | E4 | ₹6.00–8.50 | DERC tariff schedule; no comprehensive order since Sept 2021, so the FY2021–22 schedule still applies (derc.gov.in/tarriff-orders) | PARTIAL | Fixed at the school's actual category |
| FPPAS | Fuel and power purchase surcharge | % | E4 | 12.21–17.94% (May 2026) | DERC order of 10 July 2026 | VERIFIED | Uniform over recent months |
| ED | Electricity duty | % | E4 | ~5% | Delhi electricity duty on the bill; 5% assumed in the model, not yet read in the Act or on a bill | UNVERIFIED | Fixed |
| g | Tariff growth | %/yr | E4 | to build | DERC tariff orders 2014–15 to 2021–22 plus FPPAS history; optional trend regression (Rozon et al. 2023 method) | TO BUILD | Uniform or from regression residuals |
| APPC | Price paid for year-end surplus | ₹/kWh | E3, E5, E9 | ₹5.16–6.26 by DISCOM (FY2021–22) | Delhi Solar Policy 2023, Appendix II; update from latest DERC order | STALE | Fixed per DISCOM |
| c<sub>s</sub> | Who keeps the export credit | 0/1 | E5, E9 | contract term | PPA drafting choice | SCENARIO | Both values run |
| PPA<sub>1</sub>, e | First-year PPA price, escalator | ₹/kWh, %/yr | E5, E9 | output; e = 0% or 3% | Reported Delhi govt-school RESCO tariff ₹3.13 (2019, press report only) | OUTPUT | Solved for, not drawn |
| d<sub>s</sub> | School's discount rate | %/yr | E6, E8 | ~7–9% | School's opportunity cost: bank deposit or borrowing rates (RBI, data.rbi.org.in) | TO GET | Distribution |
| T | Contract and analysis life | years | all | 25 | Delhi Solar Policy 2023 | VERIFIED | Fixed |
| C | Installed cost | ₹/kWp | E8, E10–E13 | ₹32–48k: Delhi installer quote ₹32–36k, MNRE benchmark ₹48k | Two written EPC quotes; MNRE benchmark document (mnre.gov.in), not yet read | UNRESOLVED | Log-normal or normal |
| om, g<sub>om</sub> | O&M share and growth | % of C, %/yr | E10 | 0.5–1.5% + cleaning | EPC/AMC quotes; soiling from Sharma et al. 2023 and Al-Otaibi et al. 2015 | TO GET | Triangular |
| t<sub>inv</sub>, C<sub>inv</sub> | Inverter replacement year and cost | yr, ₹/kW | E10 | ~year 12–15 | Inverter warranty and quotes | TO GET | Discrete or triangular |
| τ | Corporate tax rate | % | E11 | 25.17% (new regime) | Income Tax Act s.115BAA (incometaxindia.gov.in) | TO VERIFY | Fixed |
| Dep | Tax depreciation on solar | % WDV | E11 | 40% WDV | Income-tax Rules, Appendix I | TO VERIFY | Fixed |
| D<sub>0</sub>/C, i, n | Debt share, interest, tenor | %, %/yr, yr | E12 | 70%, 10.5–14%, 7–10 yr | Jena et al. 2016 (CPI) debt cost 10.5–14%; 70:30 debt-equity norm of IREDA, SBI, PNB (CIF/PwC 2018, p. 54); lender term sheets | PARTIAL | Interest rate as a distribution |
| DSCR<sub>min</sub> | Lender's minimum coverage | – | E12, E14 | 1.1–1.3 | CPI covenant 1.1; Rarasati et al. 2026 use 1.25 | LITERATURE | Scenario |
| k<sub>e</sub> | Required equity return | %/yr | E13, E14 | ~15% | CPI 2016 hurdle 15%; CAPM with RBI 10-yr G-sec (data.rbi.org.in) | PARTIAL | Gamma (as Sommerfeldt & Madani 2017b) |
| N | Monte Carlo runs | – | E16 | 10,000 | — | CHOICE | — |
| CDD | Cooling degree days (regression only) | °C-days | E2 | monthly | NASA POWER daily temperature for Delhi (power.larc.nasa.gov) | AVAILABLE | — |
