"""Tests for ScoreSensor — based on test-plan.md section 3.2."""

import pytest
from chore_board.sensor import ScoreSensor


class TestScoreSensor:
    """3.2 Score Sensors"""

    def test_sensor_returns_correct_score(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        sensor = ScoreSensor("user-josh", scoring_engine)
        assert sensor.score == 10

    def test_sensor_updates_after_points_awarded(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        sensor = ScoreSensor("user-josh", scoring_engine)
        assert sensor.score == 0
        scoring_engine.award_points("user-josh", "Dishes", 10)
        assert sensor.score == 10

    def test_sensor_zero_score(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        sensor = ScoreSensor("user-josh", scoring_engine)
        assert sensor.score == 0

    def test_sensor_has_history_attributes(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        sensor = ScoreSensor("user-josh", scoring_engine)
        attrs = sensor.get_attributes()
        assert "score" in attrs
        assert "history" in attrs
        assert attrs["score"] == 10

    def test_sensor_history_contains_activity(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        scoring_engine.award_points("user-josh", "Mop", 5)
        sensor = ScoreSensor("user-josh", scoring_engine)
        history = sensor.history
        assert len(history) == 2

    def test_sensor_no_crash_no_members(self, scoring_engine):
        sensor = ScoreSensor("unknown-user", scoring_engine)
        assert sensor.score == 0
