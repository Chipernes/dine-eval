# DINE human questionnaire

The 27 participants rated the same 60 responses the judge models scored, shown one at a
time in **randomised order** and **blind** (no indication of the prompting strategy or the
model that produced them). Delivered as a Google Form; the builder script is
`scripts/make_form_script.py`, and the anonymised long-format ratings are in
`data/human/human_responses.csv`.

## Consent and background (asked once)

- **Informed consent** (required): "I understand the purpose of the study and agree to take part anonymously."
- **Age**: under 20 / 20–29 / 30–39 / 40+
- **Dining-out frequency**: rarely / a few times a month / weekly or more often
- **Professional hospitality experience**: yes / no

## Per-response rating

For every response the participant saw the guest-facing **input** and the **response to
rate**, then scored it from **1 (worst) to 5 (best)** on the axes that apply to the task,
using the behavioural anchors of Table 2 in the paper. Only applicable axes were shown:

| Task | Axes shown |
|---|---|
| T1 — menu-item description | accuracy, relevance, clarity, hospitality tone |
| T2 — guest question answering | all six (accuracy, relevance, clarity, allergen safety, tone, recommendation) |
| T3 — procurement note | accuracy, relevance, clarity, recommendation appropriateness |

Item wording:

- **Accuracy** — the facts are correct and nothing is invented.
- **Relevance** — the response answers what was actually asked.
- **Clarity and conciseness** — the response is clear and free of padding.
- **Allergen and dietary safety** — allergens and dietary constraints are handled correctly and cautiously.
- **Hospitality tone** — the response is warm, polite and welcoming.
- **Recommendation appropriateness** — any suggestion is helpful and not pushy.

Each answer is one integer per applicable axis per response, reshaped into the long format
`rater_id, response_id, task, axis, score`.
