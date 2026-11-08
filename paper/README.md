# Reproducibility pack

All data, prompts, figures and code behind the paper
*"DINE: A Domain-Adapted Interpretable Evaluation Method for Restaurant AI-Assistants."*

## Layout

```
data/
  judge_scores/      DINE scores (6 axes), one CSV per judge model, 60 responses each
  baselines/         baseline_* : single overall score + PEEM-style general axes per judge
  allergen/          judge_allergen_* : 1-5 safety score + binary unsafe_flag per judge (30 items)
                     allergen_gold.csv : ground-truth unsafe label per item
  human/             human_ratings_readable.csv : most readable - one row per rating with the
                                           verbatim question, the response text rated, and the score
                     human_responses.csv : the same ratings in compact long format (analysis-ready)
                     form_export_raw.csv : the raw anonymised Google Form export (wide: 285 columns,
                                           one per question, cells = the 1-5 scores)
                     demographics_summary.csv, participant_demographics.csv
  responses/         responses.csv : the 60 generated responses with task, strategy, context
prompts/             judge_prompts.md (DINE + baselines)
                     human_questionnaire.md (EN summary), form_questions_uk.md (verbatim, as shown)
figures/             fig1-fig6 as used in the paper
scripts/             reproduce_stats.py (recomputes every number), make_allergen_round.py
```

## Reproduce the headline numbers

```bash
pip install -r requirements.txt
python scripts/reproduce_stats.py
```

This recomputes, from the released CSVs, the RQ1 consensus-vs-human correlations
(tone 0.84, allergen safety 0.79, ...), the cross-evaluator agreement, the H1b method
comparison (Table 7), the per-strategy means (Table 8), the self-preference check, and the
adversarial allergen precision/recall (1.00 / 0.93 for all three judges).

`scripts/make_allergen_round.py` rebuilds the adversarial allergen set
(`allergen_gold.csv` and the judge input package) from the 15 source questions.
Figures 1–6 are provided under `figures/`.

## Notes

- Scores were collected via each model's API at temperature 0.
- `participant_demographics.csv` lists participants in submission order; aggregate counts in
  `demographics_summary.csv` are what the paper reports.
- Column keys use the short axis names: accuracy, relevance, clarity, safety, tone, recommendation.
