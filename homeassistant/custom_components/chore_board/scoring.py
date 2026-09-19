"""LLM-based scoring for ad-hoc tasks."""

from __future__ import annotations

import logging

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


async def ai_score_task(task_description: str, model: str = DEFAULT_LLM_MODEL, api_key: str | None = None) -> int:
    """Score a task via LLM. Returns points between MIN_POINTS and MAX_POINTS."""
    try:
        import openai
    except ImportError:
        _LOGGER.warning("openai package not installed, using default points")
        return DEFAULT_POINTS

    client_kwargs: dict[str, str] = {"model": model}
    if api_key:
        client_kwargs["api_key"] = api_key

    try:
        client = openai.OpenAI(**client_kwargs)
        response = await client.chat.completions.create(
            model=model,
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
