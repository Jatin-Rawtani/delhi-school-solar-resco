# Leasing rooftop solar to a Delhi school

**Is zero-upfront solar leasing financially feasible for a private day school in Delhi, and for the company that leases it?**

Under a RESCO (renewable energy service company) lease, a company pays for a solar system, puts it on the school's roof, owns it and maintains it. The school pays nothing upfront and buys the electricity the panels make at an agreed price per unit under a long contract (a power purchase agreement, or PPA). The deal only happens if one price works for both sides:

- the **school** has to save money compared with buying from the grid, and
- the **company** has to earn its required return *and* pass the bank's debt-coverage test.

This repository solves for that two-sided price band, the school's **ceiling** and the company's **floor**, under Delhi's annual net-metering rule. It treats every input as uncertain, because a 25-year contract outlives any single tariff or regulation.

This is the working model for my M.S. capstone in Climate Science and Policy at Bard College's Center for Environmental Policy (due May 2027). It is a work in progress and is published as it is built.

## Written in English first

Every equation is written out in plain English before it is written in code. [docs/EQUATIONS.md](docs/EQUATIONS.md) gives, for each of the 18 equations, the formula, what it means in words, the paper and equation it comes from, why it is in the model, and where it sits. It also has a table of every input with its data source and how far it has been verified. The document is generated from the same source file the code uses (`tools/recipe_data.py`), so the explanation and the model cannot drift apart. [docs/LITERATURE.md](docs/LITERATURE.md) maps the five bodies of research the model draws on, and lists 98 references.

## The model

| Layer | What it does | Equations |
|---|---|---|
| 1. Two ledgers | Solar output, the school's use, Delhi's annual netting, the school's savings and NPV, the company's revenue, costs, tax, loan and equity return | E1–E15 |
| 2. Monte Carlo | Draw every uncertain input from a distribution, 10,000 times, and report the probability that a feasible price band exists | E16 |
| 3. Sensitivity | Find which inputs drive the answer: one at a time first, then variance-based (Sobol) indices | E17 |
| Policy scenario | Hour-by-hour net billing instead of annual netting | E18 |

`model/resco_price_band.py` runs Layer 1 end to end and solves for both ends of the band. **Its inputs are placeholders**, so the output shows that the chain works and is not a result:

```
L=70 MWh: floor = 6.00 (equity 5.06, DSCR 1.2 6.00), ceiling = 12.38, width = 6.38
L=25 MWh: floor = 6.00 (equity 5.06, DSCR 1.2 6.00), ceiling = 8.06, width = 2.05
```

Even with placeholders, the dry run already showed something worth checking with real data. The **bank's coverage ratio, not the owners' return, sets the company's floor**, and a smaller school's ceiling falls fast because more of its solar is surplus credited at the lower APPC rate.

## What real school data says

Delhi school meter data is not public, so the scripts in `analysis/` use 194 real schools from the Building Data Genome 2 dataset (hourly meters in Washington DC and Cardiff, UK) to bound the load inputs:

| Question | Finding | Script |
|---|---|---|
| How much do schools use per m²? | Education buildings: median 167 kWh/m²/yr (p25 102, p75 333; n = 60 with floor area and EUI) | `eui_stats.py` |
| How deep is the summer-break dip? | Cardiff (no air conditioning): break load is a median **0.60** of term load. Washington DC (air conditioning): **1.19**, higher in summer | `vacation_load.py` |
| If solar makes as much as the school uses in a year, how much is used as it is made? | Only about **47%** at both sites. The rest is exported, which is why the surplus rule matters so much | `selfconsumption_vs_sizing.py` |

Delhi's day schools close in the hottest months and run air conditioning in the rest, so the real profile sits somewhere between these two cases. The bills of the school being studied will settle it.

## Run it

```bash
pip install -r requirements.txt
python model/resco_price_band.py               # Layer 1 dry run, placeholder inputs
python tools/make_equations_md.py              # rebuild docs/EQUATIONS.md from tools/recipe_data.py
python analysis/eui_stats.py                   # needs BDG2, see data/README.md
python analysis/vacation_load.py
python analysis/selfconsumption_vs_sizing.py
```

Saved outputs from each script sit next to it (`*_output.txt`).

## Status

- Done: equation chain and plain-English specification; literature map; dry run; school-load bounds from BDG2.
- In progress: replacing placeholder inputs with verified Delhi values (tariff schedule, APPC, tax and depreciation rates, installer quotes, the school's own bills); building Layers 2 and 3.

## How this was built

I set the research question, chose the method and wrote the model's logic in plain English, with sources, step by step. The code and the generated documents were written with an AI coding assistant (Claude Code) working from that specification, then checked by rerunning the model and tracing every equation back to its paper. I think this is where analytical work is going: the thinking, the assumptions and the checking stay human and readable, and the code follows from them.

Code: MIT licence. Author: Jatin Rawtani.
