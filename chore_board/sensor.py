"""Per-participant score sensors."""

from __future__ import annotations

from typing import Optional


class ScoreSensor:
    """Represents a score sensor for a single participant."""

    def __init__(self, participant_id: str, scoring_engine: object) -> None:
        self._participant_id = participant_id
        self._scoring_engine = scoring_engine

    @property
    def score(self) -> int:
        """Current score for this participant."""
        return self._scoring_engine.get_score(self._participant_id)

    @property
    def history(self) -> list[dict]:
        """Recent activity history as list of dicts."""
        entries = self._scoring_engine.get_recent_history(self._participant_id, limit=10)
        return [
            {
                "timestamp": e.timestamp,
                "chore_title": e.chore_title,
                "points": e.points,
            }
            for e in entries
        ]

    def get_attributes(self, max_history: int = 10) -> dict:
        """Return sensor attributes for HA."""
        entries = self._scoring_engine.get_recent_history(self._participant_id, limit=max_history)
        return {
            "score": self.score,
            "history": [
                {
                    "timestamp": e.timestamp,
                    "chore_title": e.chore_title,
                    "points": e.points,
                }
                for e in entries
            ],
        }
