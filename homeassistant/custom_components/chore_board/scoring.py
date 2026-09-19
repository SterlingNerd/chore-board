"""LLM-based scoring for ad-hoc tasks.

OpenAI-compatible API. Configurable base_url, api_key, model.
Falls back to DEFAULT_POINTS on failure.
"""

from __future__ import annotations

import logging
from typing import Any

from .const import DEFAULT_LLM_MODEL

_LOGGER = logging.getLogger(__name__)

# Scoring scale
MIN_POINTS = 1
MAX_POINTS = 50
DEFAULT_POINTS = 10

SCORING_PROMPT = """You are scoring household tasks for a gamified chore system.

Rate this task on effort/impact from {min} to {max} points.
Consider: time required, difficulty, how much the household benefits.

Respond with ONLY a number, nothing else."""


class LLMConfig:
    """LLM scoring configuration."""

    def __init__(
        self,
        base_url: str = "",
        api_key: str = "",
        model: str = DEFAULT_LLM_MODEL,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMConfig":
        return cls(
            base_url=data.get("llm_base_url", ""),
            api_key=data.get("llm_api_key", ""),
            model=data.get("llm_model", DEFAULT_LLM_MODEL),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "llm_base_url": self.base_url,
            "llm_api_key": self.api_key,
            "llm_model": self.model,
        }


async def ai_score_task(task_description: str, config: LLMConfig | None = None) -> int:
    """Score a task via OpenAI-compatible LLM. Returns points."""
    if config is None:
        config = LLMConfig()

    try:
        import openai
    except ImportError:
        _LOGGER.warning("openai package not installed, using default points")
        return DEFAULT_POINTS

    client_kwargs: dict[str, Any] = {"model": config.model}
    if config.api_key:
        client_kwargs["api_key"] = config.api_key
    if config.base_url:
        client_kwargs["base_url"] = config.base_url

    try:
        client = openai.OpenAI(**client_kwargs)
        response = await client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": SCORING_PROMPT.format(min=MIN_POINTS, max=MAX_POINTS)},
                {"role": "user", "content": task_description},
            ],
            max_tokens=10,
        )
        raw = response.choices[0].message.content.strip()
        points = int(raw)
        return max(MIN_POINTS, min(MAX_POINTS, points))
    except Exception:
        _LOGGER.warning("LLM scoring failed, using default %d points", DEFAULT_POINTS)
        return DEFAULT_POINTS
