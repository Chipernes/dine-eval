"""Apply DINE as an LLM-as-a-judge.

    from dine_eval import DINEJudge, OpenAICompatibleClient

    judge = DINEJudge(OpenAICompatibleClient(model="gpt-6", api_key="..."))
    result = judge.evaluate(
        response="A classic pasta with guanciale, egg yolk and pecorino.",
        task="Describe this dish for the menu.",
        context="spaghetti, guanciale, egg yolk, pecorino, black pepper",
    )
    print(result.scores, result.safety_gate())
"""
from __future__ import annotations
import json
import re

from .client import Client, OpenAICompatibleClient
from .criteria import AXIS_KEYS
from .prompts import DINE_PROMPT
from .types import DINEResult, ConsensusResult


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply, tolerating code fences
    and leading/trailing prose.
    """
    if text is None:
        raise ValueError("empty model reply")
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    # fall back to the outermost {...}
    start, depth = t.find("{"), 0
    if start == -1:
        raise ValueError(f"no JSON object in reply: {text[:200]!r}")
    for i in range(start, len(t)):
        depth += (t[i] == "{") - (t[i] == "}")
        if depth == 0:
            return json.loads(t[start : i + 1])
    raise ValueError(f"unbalanced JSON in reply: {text[:200]!r}")


def _coerce_score(v) -> int | None:
    if v is None:
        return None
    try:
        iv = int(round(float(v)))
    except (TypeError, ValueError):
        return None
    return min(5, max(1, iv))


class DINEJudge:
    """A single judge model applying the six DINE criteria."""

    def __init__(self, client: Client, prompt: str = DINE_PROMPT):
        self.client = client
        self.prompt = prompt
        self.model = getattr(client, "model", None)

    def build_prompt(self, response: str, task: str = "", context: str = "") -> str:
        return self.prompt.format(task=task or "(none)", context=context or "(none)", response=response)

    def evaluate(self, response: str, task: str = "", context: str = "") -> DINEResult:
        raw = self.client.complete(self.build_prompt(response, task, context))
        data = _extract_json(raw)
        scores: dict[str, int | None] = {}
        rationales: dict[str, str] = {}
        for ax in AXIS_KEYS:
            cell = data.get(ax) or {}
            if not isinstance(cell, dict):
                cell = {"score": cell}
            scores[ax] = _coerce_score(cell.get("score"))
            rationales[ax] = str(cell.get("rationale", "")).strip()
        return DINEResult(scores=scores, rationales=rationales, model=self.model, raw=raw)


class DINEConsensus:
    """A panel of judges; the consensus score per axis is the mean of the judges
    that returned a score for that axis.
    """

    def __init__(self, judges: list[DINEJudge]):
        if not judges:
            raise ValueError("DINEConsensus needs at least one judge")
        self.judges = judges

    def evaluate(self, response: str, task: str = "", context: str = "") -> ConsensusResult:
        results = [j.evaluate(response, task, context) for j in self.judges]
        # Key per_model uniquely so judges that share a model name are both kept.
        per_model: dict[str, DINEResult] = {}
        for r in results:
            name = r.model or "judge"
            key, i = name, 2
            while key in per_model:
                key, i = f"{name}#{i}", i + 1
            per_model[key] = r
        # The consensus averages over every judge, not over the de-duplicated names.
        mean_scores: dict[str, float | None] = {}
        for ax in AXIS_KEYS:
            vals = [r.scores[ax] for r in results if r.scores.get(ax) is not None]
            mean_scores[ax] = round(sum(vals) / len(vals), 3) if vals else None
        return ConsensusResult(scores=mean_scores, model="consensus", per_model=per_model)
