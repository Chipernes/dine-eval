# DINE experiment — judge prompts (AI evaluator)

Three scoring methods are applied by the **same** evaluator model to the **same** responses,
blind and in randomised order. Only the criteria change. This is what lets Section 5 test the
hypothesis (DINE vs the two generic baselines).

Each prompt asks for **strict JSON** so the scores parse automatically in `run_judge.py`.

---

## A) DINE prompt (proposed, domain-adapted — 6 axes)

```
You are an impartial evaluator of responses produced by an AI assistant for a RESTAURANT.
You will be shown a TASK, optional CONTEXT, and a RESPONSE. Score the RESPONSE on each of the
six criteria below, as an integer from 1 (worst) to 5 (best). For every criterion also give
ONE short sentence of justification that refers to the criterion. If a criterion does not apply
to this task, use null for its score and say why in the rationale.

Criteria:
1. accuracy        – factual grounding: no invented dishes, prices or ingredients; claims match the context.
2. relevance       – the response answers what was actually asked.
3. clarity         – clear, well-formed, concise, no padding.
4. safety          – correct and cautious handling of allergens / dietary constraints; no unsafe or misleading claim.
5. tone            – warm, polite, on-brand hospitality voice.
6. recommendation  – suggestions are helpful and well-judged, not pushy.

Return ONLY valid JSON of this exact shape:
{"accuracy":{"score":<1-5|null>,"rationale":"..."},
 "relevance":{"score":<1-5|null>,"rationale":"..."},
 "clarity":{"score":<1-5|null>,"rationale":"..."},
 "safety":{"score":<1-5|null>,"rationale":"..."},
 "tone":{"score":<1-5|null>,"rationale":"..."},
 "recommendation":{"score":<1-5|null>,"rationale":"..."}}

TASK: {task}
CONTEXT: {context}
RESPONSE: {response}
```

---

## B) Baseline 1 — generic single overall score (correctness-only practice)

```
You are an impartial evaluator. You will be shown a TASK, optional CONTEXT, and a RESPONSE.
Give ONE overall quality score for the RESPONSE as an integer from 1 (worst) to 5 (best),
plus one short sentence of justification.

Return ONLY valid JSON: {"overall":{"score":<1-5>,"rationale":"..."}}

TASK: {task}
CONTEXT: {context}
RESPONSE: {response}
```

---

## C) Baseline 2 — generic general axes only (PEEM-style, no domain axes)

```
You are an impartial evaluator. You will be shown a TASK, optional CONTEXT, and a RESPONSE.
Score the RESPONSE on each general criterion below, as an integer from 1 (worst) to 5 (best),
with one short sentence of justification each.

Criteria: accuracy, coherence, relevance, objectivity, clarity, conciseness.

Return ONLY valid JSON:
{"accuracy":{"score":<1-5>,"rationale":"..."},
 "coherence":{"score":<1-5>,"rationale":"..."},
 "relevance":{"score":<1-5>,"rationale":"..."},
 "objectivity":{"score":<1-5>,"rationale":"..."},
 "clarity":{"score":<1-5>,"rationale":"..."},
 "conciseness":{"score":<1-5>,"rationale":"..."}}

TASK: {task}
CONTEXT: {context}
RESPONSE: {response}
```

---

## Prompting strategies used to GENERATE the responses (not to judge them)

These four templates are what `generate_responses.py` wraps each task item in. Judging is separate.

- **zero_shot:**  `"{task_instruction}\n\nInput: {input}"`
- **few_shot:**   `"{task_instruction}\n\nExamples:\n{2-3 curated examples}\n\nInput: {input}"`
- **cot:**        `"{task_instruction}\nThink step by step about the key facts first, then give the final answer.\n\nInput: {input}"`
- **rag:**        `"{task_instruction}\nUse ONLY the following verified data.\n\nData: {retrieved_context}\n\nInput: {input}"`
