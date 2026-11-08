"""Offline tests: a fake client returns canned JSON, so no network/API key is
needed. Run with: pytest
"""
from dine_eval import DINEJudge, DINEConsensus, CallableClient
from dine_eval.judge import _extract_json, _coerce_score


DINE_JSON = """```json
{"accuracy":{"score":5,"rationale":"grounded"},
 "relevance":{"score":4,"rationale":"on point"},
 "clarity":{"score":4,"rationale":"clear"},
 "safety":{"score":2,"rationale":"misleading on allergen"},
 "tone":{"score":5,"rationale":"warm"},
 "recommendation":{"score":null,"rationale":"n/a for this task"}}
```"""


def _judge(payload):
    return DINEJudge(CallableClient(lambda _p: payload, model="fake"))


def test_parse_with_code_fence_and_null():
    r = _judge(DINE_JSON).evaluate(response="x", task="t", context="c")
    assert r.scores["accuracy"] == 5
    assert r.scores["recommendation"] is None
    assert r.rationales["safety"].startswith("misleading")


def test_safety_gate_and_passes():
    r = _judge(DINE_JSON).evaluate(response="x")
    assert r.safety_gate(threshold=4) is False  # safety is 2
    assert r.passes() is False                  # fails gate
    # mean quality excludes safety by default
    assert r.mean_quality() == round((5 + 4 + 4 + 5) / 4, 3)


def test_extract_json_with_prose():
    d = _extract_json('Sure! Here it is: {"overall": {"score": 3}} Hope that helps.')
    assert d["overall"]["score"] == 3


def test_coerce_score_clamps():
    assert _coerce_score(9) == 5
    assert _coerce_score(0) == 1
    assert _coerce_score("4") == 4
    assert _coerce_score(None) is None


def test_consensus_means():
    hi = """{"accuracy":{"score":4},"relevance":{"score":4},"clarity":{"score":4},
             "safety":{"score":5},"tone":{"score":4},"recommendation":{"score":4}}"""
    lo = """{"accuracy":{"score":2},"relevance":{"score":2},"clarity":{"score":2},
             "safety":{"score":3},"tone":{"score":2},"recommendation":{"score":2}}"""
    panel = DINEConsensus([_judge(hi), _judge(lo)])
    c = panel.evaluate(response="x")
    assert c.scores["safety"] == 4.0  # mean of 5 and 3
    assert set(c.per_model) == {"fake", "fake#2"}  # both judges kept despite shared name
