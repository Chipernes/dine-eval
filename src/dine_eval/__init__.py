"""dine-eval: a domain-adapted, interpretable evaluation method (DINE) for
restaurant AI-assistant responses, applied as an LLM-as-a-judge.

DINE = Domain-adapted INterpretable Evaluation.

Quick start:

    from dine_eval import DINEJudge, OpenAICompatibleClient

    judge = DINEJudge(OpenAICompatibleClient(model="gpt-6", api_key="sk-..."))
    result = judge.evaluate(
        response="...",
        task="Answer the guest's question.",
        context="dish ingredients / menu facts",
    )
    result.scores          # {'accuracy': 5, 'relevance': 5, 'safety': 4, ...}
    result.safety_gate()   # True / False / None
    result.passes()        # safety gate AND mean-quality threshold
"""
from .criteria import AXES, AXIS_KEYS, GENERAL_AXES, DOMAIN_AXES, TASK_AXES, Axis
from .prompts import DINE_PROMPT, BASELINE_SINGLE_PROMPT, BASELINE_GENERAL_PROMPT, ALLERGEN_SAFETY_PROMPT
from .client import Client, OpenAICompatibleClient, CallableClient
from .judge import DINEJudge, DINEConsensus
from .types import DINEResult, ConsensusResult

__version__ = "0.1.0"
__all__ = [
    "AXES", "AXIS_KEYS", "GENERAL_AXES", "DOMAIN_AXES", "TASK_AXES", "Axis",
    "DINE_PROMPT", "BASELINE_SINGLE_PROMPT", "BASELINE_GENERAL_PROMPT", "ALLERGEN_SAFETY_PROMPT",
    "Client", "OpenAICompatibleClient", "CallableClient",
    "DINEJudge", "DINEConsensus", "DINEResult", "ConsensusResult",
    "__version__",
]
