"""Scoring, LLM config, and point awards."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class LLMConfig:
    base_url: str
    api_key: str
    model: str


@dataclass
class ScoreEntry:
    timestamp: str  # ISO format
    chore_title: str
    points: int
    participant_id: str


class ScoringEngine:
    """Award points and manage score history."""

    def __init__(self, member_manager: object) -> None:
        self._member_manager = member_manager
        self._scores: dict[str, int] = {}
        self._history: list[ScoreEntry] = []

    def award_points(
        self,
        participant_id: str,
        chore_title: str,
        points: int,
        timestamp: Optional[str] = None,
    ) -> int:
        """Award points to a participant. Returns new total score."""
        if not self._member_manager.member_exists(participant_id):
            raise KeyError(f"Participant '{participant_id}' not found")
        if not isinstance(points, int) or isinstance(points, bool):
            raise ValueError("Points must be an integer")
        if points < 0:
            raise ValueError("Points cannot be negative")

        self._scores[participant_id] = self._scores.get(participant_id, 0) + points
        entry = ScoreEntry(
            timestamp=timestamp or datetime.now(timezone.utc).isoformat(),
            chore_title=chore_title,
            points=points,
            participant_id=participant_id,
        )
        self._history.append(entry)
        return self._scores[participant_id]

    def get_score(self, participant_id: str) -> int:
        """Get total score for a participant."""
        return self._scores.get(participant_id, 0)

    def get_history(self, participant_id: Optional[str] = None) -> list[ScoreEntry]:
        """Get score history, optionally filtered by participant."""
        if participant_id:
            return [e for e in self._history if e.participant_id == participant_id]
        return list(self._history)

    def get_recent_history(
        self, participant_id: str, limit: int = 10
    ) -> list[ScoreEntry]:
        """Get the N most recent history entries for a participant."""
        participant_history = [
            e for e in self._history if e.participant_id == participant_id
        ]
        return participant_history[-limit:]

    def ai_score_task(
        self, description: str, llm_config: Optional[LLMConfig] = None
    ) -> int:
        """Use LLM to score a task description. Returns points (default 10 on failure)."""
        if not llm_config:
            return FALLBACK_POINTS
        try:
            import openai
            client = openai.OpenAI(base_url=llm_config.base_url, api_key=llm_config.api_key)
            response = client.chat.completions.create(
                model=llm_config.model,
                messages=[
                    {"role": "system", "content": "You are a chore point scorer. Respond with only an integer number of points."},
                    {"role": "user", "content": f"Score this chore in points: {description}"},
                ],
                max_tokens=10,
            )
            text = response.choices[0].message.content.strip()
            result = int(text)
            if result < 0:
                return FALLBACK_POINTS
            return result
        except Exception:
            return FALLBACK_POINTS


FALLBACK_POINTS = 10
