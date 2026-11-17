"""Write docs/EQUATIONS.md, the model's equations in plain English, from tools/recipe_data.py (single source)."""
import html, pathlib, re, runpy

ROOT = pathlib.Path(__file__).resolve().parent.parent
R = runpy.run_path(str(ROOT / "tools" / "recipe_data.py"))

def clean(s):
    return html.unescape(s).replace("|", "\\|").strip()

BLOCKS = {"A": "A. Energy: shared by both parties", "B": "B. The school's ledger",
          "C": "C. The leasing company's (RESCO's) ledger", "D": "D. Uncertainty and sensitivity"}
out = ["# The model in plain English",
       "",
       "Every equation in the model, what it means in words, where it comes from in the literature, and why it is there. "
       "Equation numbers (E1 to E18) are this project's own; each one records the paper and equation it is built on. "
       "This file is generated from `tools/recipe_data.py` by `tools/make_equations_md.py`, so the words and the code share one source.",
       ""]
block = None
for e in R["EQ"]:
    if e["block"] != block:
        block = e["block"]; out += [f"## {BLOCKS[block]}", ""]
    out += [f"### {e['id']}. {clean(e['name'])}", "", f"> {clean(e['f']).replace(chr(92)+'|', '|')}", "",
            f"**In words.** {clean(e['words'])}", "", f"**Source.** {clean(e['src'])}", "",
            f"**Why it is here.** {clean(e['why'])}", "", f"**Where it sits.** {clean(e['where'])}", ""]
out += ["## Variables", "",
        "Status shows how far each input has got: VERIFIED (read in the primary source), PARTIAL, LITERATURE (taken from a study), "
        "TO GET or TO VERIFY (still open), CHOICE or SCENARIO (set by design), OUTPUT (solved for).", "",
        "| Symbol | Meaning | Units | Used in | Current value (Delhi) | Data source | Status | How it varies in the Monte Carlo |",
        "|---|---|---|---|---|---|---|---|"]
for v in R["VAR"]:
    sym, meaning, units, eq, value, source, status, basis, layer2, why = v
    out.append("| " + " | ".join(clean(x) for x in (sym, meaning, units, eq, value, source, status, layer2)) + " |")
(ROOT / "docs" / "EQUATIONS.md").write_text("\n".join(out) + "\n")
print("wrote docs/EQUATIONS.md")
