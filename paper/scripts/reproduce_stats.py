# -*- coding: utf-8 -*-
"""Reproduce the headline numbers of the paper from the released data.

Run from the paper/ directory:
    python scripts/reproduce_stats.py

Prints: RQ1 consensus-vs-human per axis, cross-evaluator agreement, the H1b
method comparison, strategy means, the adversarial allergen precision/recall,
and the self-preference check.
"""
import os, glob, warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
AX = ["accuracy", "relevance", "clarity", "safety", "tone", "recommendation"]


def load(path):
    return pd.read_csv(path).set_index("response_id").apply(pd.to_numeric, errors="coerce")


def judges():
    out = {}
    for p in sorted(glob.glob(os.path.join(DATA, "judge_scores", "judge_*.csv"))):
        name = os.path.basename(p)[len("judge_"):-len(".csv")]
        out[name] = load(p)
    return out


J = judges()
stack = np.stack([J[m].reindex(columns=AX).values for m in J], axis=0)
dine = pd.DataFrame(np.nanmean(stack, axis=0), index=next(iter(J.values())).index, columns=AX)
H = pd.read_csv(os.path.join(DATA, "human", "human_responses.csv"))
hum = H.groupby(["response_id", "axis"]).score.mean().unstack()


def sp(x, y):
    c = x.dropna().index.intersection(y.dropna().index)
    if len(c) < 4:
        return np.nan, np.nan, np.nan, len(c)
    r, p = spearmanr(x.loc[c], y.loc[c])
    t, _ = kendalltau(x.loc[c], y.loc[c])
    return r, t, p, len(c)


print("### RQ1  consensus DINE vs human (Spearman, Kendall, p, N)")
for ax in AX:
    r, t, p, n = sp(dine[ax], hum[ax])
    print(f"  {ax:15} rho={r:.2f} tau={t:.2f} p={p:.2g} N={n}")

print("\n### Cross-evaluator mean pairwise Spearman")
names = list(J)
pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
for ax in AX:
    vals = [sp(J[a][ax] if ax in J[a] else pd.Series(dtype=float),
               J[b][ax] if ax in J[b] else pd.Series(dtype=float))[0] for a, b in pairs]
    print(f"  {ax:15} mean={np.nanmean(vals):.2f}")

print("\n### RQ2 (H1b)  method vs human (Spearman rho)")
B = {}
for p in sorted(glob.glob(os.path.join(DATA, "baselines", "baseline_*.csv"))):
    B[os.path.basename(p)] = load(p)
b1 = pd.concat([b["overall"] for b in B.values()], axis=1).mean(axis=1)
gen = ["accuracy", "coherence", "relevance", "objectivity", "clarity", "conciseness"]
b2 = pd.concat([b[gen].mean(axis=1) for b in B.values()], axis=1).mean(axis=1)
print(f"  {'axis':15} {'DINE':>6} {'base1':>6} {'base2':>6}")
for ax in AX:
    print(f"  {ax:15} {sp(dine[ax],hum[ax])[0]:6.2f} {sp(b1,hum[ax])[0]:6.2f} {sp(b2,hum[ax])[0]:6.2f}")

print("\n### RQ3  mean consensus DINE score by strategy")
d2 = dine.copy()
d2["s"] = [i.split("_", 1)[1] for i in d2.index]
print(d2.groupby("s")[AX].mean().round(2).to_string())

print("\n### Self-preference  mean DINE score per judge")
for m in J:
    print(f"  {m:20} {np.nanmean(J[m][AX].values):.2f}")

print("\n### Adversarial allergen set  precision / recall / accuracy (vs ground truth)")
gold = pd.read_csv(os.path.join(DATA, "allergen", "allergen_gold.csv")).set_index("response_id")["gold_unsafe"]
for p in sorted(glob.glob(os.path.join(DATA, "allergen", "judge_allergen_*.csv"))):
    name = os.path.basename(p)[len("judge_allergen_"):-len(".csv")]
    a = pd.read_csv(p).set_index("response_id")
    pred = a["unsafe_flag"].reindex(gold.index).astype(float)
    tp = int(((pred == 1) & (gold == 1)).sum()); fp = int(((pred == 1) & (gold == 0)).sum())
    fn = int(((pred == 0) & (gold == 1)).sum()); tn = int(((pred == 0) & (gold == 0)).sum())
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    acc = (tp + tn) / len(gold)
    print(f"  {name:20} P={prec:.2f} R={rec:.2f} acc={acc:.2f}")
