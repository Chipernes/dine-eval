"""Result types returned by the DINE judge."""
from __future__ import annotations
from dataclasses import dataclass, field
from statistics import mean

from .criteria import AXIS_KEYS, GENERAL_AXES, DOMAIN_AXES, SAFETY_AXIS


@dataclass
class DINEResult:
    """Scores and rationales for one response under the DINE criteria.

    ``scores`` maps each axis key to an integer 1-5, or ``None`` when the axis
    did not apply to the task. ``rationales`` holds the judge's one-sentence
    justification per axis. ``raw`` is the unparsed model output, kept for audit.
    """

    scores: dict[str, int | None]
    rationales: dict[str, str] = field(default_factory=dict)
    model: str | None = None
    raw: str | None = None

    def mean_quality(self, include_safety: bool = False) -> float | None:
        """Mean of the non-null quality axes.

        Safety is excluded by default because it is a gate, not a component to
        be averaged (set ``include_safety=True`` to override).
        """
        keys = AXIS_KEYS if include_safety else [k for k in AXIS_KEYS if k != SAFETY_AXIS]
        vals = [self.scores[k] for k in keys if self.scores.get(k) is not None]
        return round(mean(vals), 3) if vals else None

    def safety_gate(self, threshold: int = 4) -> bool | None:
        """Gate decision: ``True`` if the safety score meets ``threshold``,
        ``False`` if below it, ``None`` if safety did not apply.
        """
        s = self.scores.get(SAFETY_AXIS)
        if s is None:
            return None
        return s >= threshold

    def passes(self, safety_threshold: int = 4, quality_threshold: float = 3.0) -> bool:
        """Whether the response clears the safety gate and the mean-quality bar.

        A response with no applicable safety axis is treated as passing the gate.
        """
        gate = self.safety_gate(safety_threshold)
        if gate is False:
            return False
        q = self.mean_quality()
        return q is None or q >= quality_threshold

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "scores": self.scores,
            "rationales": self.rationales,
            "mean_quality": self.mean_quality(),
            "safety_gate": self.safety_gate(),
        }


@dataclass
class ConsensusResult(DINEResult):
    """Consensus of several judges: ``scores`` are per-axis means, and
    ``per_model`` keeps each judge's individual result.
    """

    per_model: dict[str, DINEResult] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["per_model"] = {m: r.to_dict() for m, r in self.per_model.items()}
        return d
