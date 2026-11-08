# dine-eval

**DINE (Domain-adapted INterpretable Evaluation)** is a domain-adapted, interpretable
method for evaluating the responses of **restaurant AI-assistants**. It scores a response
on six criteria — three general and three hospitality-specific — each on a 1–5 scale with a
written rationale, and it is applied as an *LLM-as-a-judge*.

DINE is a **measuring instrument**: the same six criteria can be applied by an automated
judge (this package) or by a human rater. In the accompanying paper the LLM application of
DINE is validated against 27 human raters applying the identical criteria.

| Axis | Type | What it measures |
|---|---|---|
| Accuracy | general | Factual grounding; no invented dishes, prices or ingredients |
| Relevance | general | Answers what was actually asked |
| Clarity | general | Clear, well formed, no padding |
| **Allergen & dietary safety** | domain (objective **gate**) | Correct, cautious handling of allergens/diets |
| **Hospitality tone** | domain | Warm, polite, on-brand voice |
| **Recommendation appropriateness** | domain | Helpful suggestions, not pushy |

Safety is **objective** and is treated as a **gate**: it is reported and used separately and is
never averaged with the other axes. One dangerous allergen answer should block a response
regardless of how warm or well written it is.

## Install

```bash
pip install dine-eval
# or, from source:
pip install -e .
```

The core has **no third-party dependencies** (standard library only).

## Quick start

```python
from dine_eval import DINEJudge, OpenAICompatibleClient

judge = DINEJudge(OpenAICompatibleClient(
    model="gpt-6",
    api_key="sk-...",                       # your key
    base_url="https://api.openai.com/v1",   # any OpenAI-compatible endpoint
))

result = judge.evaluate(
    response="Our green curry contains fish sauce, so it is not vegan. "
             "I can ask the kitchen to prepare a vegan version without it.",
    task="A guest asks whether the Thai green curry is vegan.",
    context="green curry paste, coconut milk, fish sauce, vegetables",
)

result.scores          # {'accuracy': 5, 'relevance': 5, 'clarity': 5, 'safety': 5, 'tone': 5, 'recommendation': None}
result.rationales      # one sentence per axis
result.safety_gate()   # True  (safety >= 4)
result.mean_quality()  # mean of the non-safety axes
result.passes()        # True  (clears the safety gate and the quality bar)
result.to_dict()
```

`base_url` makes it work with OpenAI, Azure, Together, Groq, a local vLLM server, or an
Ollama OpenAI-compatible endpoint. If your provider is not OpenAI-compatible, wrap any
`str -> str` function with `CallableClient`:

```python
from dine_eval import DINEJudge, CallableClient
judge = DINEJudge(CallableClient(my_llm_call, model="my-model"))
```

## Consensus of several judges

The paper uses a three-model panel; the consensus score per axis is the mean of the judges.

```python
from dine_eval import DINEJudge, DINEConsensus, OpenAICompatibleClient

panel = DINEConsensus([
    DINEJudge(OpenAICompatibleClient(model="gpt-6", api_key=...)),
    DINEJudge(OpenAICompatibleClient(model="gemini-2.5-flash", api_key=..., base_url=...)),
    DINEJudge(OpenAICompatibleClient(model="claude-opus-5-5", api_key=..., base_url=...)),
])
cons = panel.evaluate(response=..., task=..., context=...)
cons.scores           # per-axis means
cons.per_model        # each judge's full result
```

## Self-checking assistant (safety gate + quality bar)

```python
def serve(candidate, task, context, judge, max_tries=3):
    for _ in range(max_tries):
        r = judge.evaluate(candidate, task=task, context=context)
        if r.passes(safety_threshold=4, quality_threshold=3.5):
            return candidate
        candidate = regenerate(task, context)   # your generator
    return escalate_to_human(task, context)
```

## Reproducing the paper

Everything needed to reproduce the study is in [`paper/`](paper/):

```
paper/
  data/
    judge_scores/      DINE scores, 3 judge models x 60 responses
    baselines/         single-overall and general-axis baseline scores
    allergen/          adversarial set: 3 per-model safety judgements + allergen_gold.csv
    human/             anonymised 27-rater responses (long format) + demographics
    responses/         the 60 generated responses with tasks and contexts
  prompts/             the exact DINE and baseline judge prompts
  scripts/             analysis that produces every table and figure
  figures/             figures 1-6 as used in the paper
  README.md            step-by-step reproduction
```

```bash
cd paper && pip install -r requirements.txt && python scripts/reproduce_stats.py
```

## How the package maps to the paper

- `dine_eval.prompts.DINE_PROMPT` is Appendix A verbatim.
- `dine_eval.criteria.AXES` is Tables 1 and 2.
- `DINEConsensus` is the multi-evaluator consensus metric of Section 5.
- The safety **gate** and `ALLERGEN_SAFETY_PROMPT` are the adversarial-set evaluation.

## License

MIT — see [LICENSE](LICENSE).
