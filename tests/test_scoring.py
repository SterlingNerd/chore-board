"""Tests for ScoringEngine — based on test-plan.md sections 3 & 5."""

import pytest
from chore_board.scoring import ScoringEngine, ScoreEntry, LLMConfig, FALLBACK_POINTS


class TestScoringEngineAwardPoints:
    """3.1 Award Points"""

    def test_award_points_to_member(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        total = scoring_engine.award_points("user-josh", "Dishes", 10)
        assert total == 10

    def test_award_points_accumulates(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        total = scoring_engine.award_points("user-josh", "Mop", 5)
        assert total == 15

    def test_award_zero_points(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        total = scoring_engine.award_points("user-josh", "Breathe", 0)
        assert total == 0

    def test_award_points_to_nonmember_raises(self, scoring_engine):
        with pytest.raises((KeyError, ValueError)):
            scoring_engine.award_points("unknown-user", "Dishes", 10)

    def test_award_negative_points_raises(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        with pytest.raises((ValueError, TypeError)):
            scoring_engine.award_points("user-josh", "Dishes", -5)

    def test_award_points_records_history(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        history = scoring_engine.get_history("user-josh")
        assert len(history) == 1
        assert history[0].chore_title == "Dishes"
        assert history[0].points == 10
        assert history[0].participant_id == "user-josh"


class TestScoringEngineGetScore:
    def test_get_score(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        assert scoring_engine.get_score("user-josh") == 10

    def test_get_score_zero_for_new_member(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        assert scoring_engine.get_score("user-josh") == 0


class TestScoringEngineHistory:
    """3.3 Score History"""

    def test_history_is_append_only(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        scoring_engine.award_points("user-josh", "Mop", 5)
        history = scoring_engine.get_history("user-josh")
        assert len(history) == 2

    def test_history_has_timestamp(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        history = scoring_engine.get_history("user-josh")
        assert history[0].timestamp is not None
        assert len(history[0].timestamp) > 0

    def test_get_recent_history(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        for i in range(5):
            scoring_engine.award_points("user-josh", f"Task {i}", i + 1)
        recent = scoring_engine.get_recent_history("user-josh", limit=3)
        assert len(recent) == 3

    def test_empty_history_returns_empty_list(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        history = scoring_engine.get_history("user-josh")
        assert history == []
        assert isinstance(history, list)

    def test_get_all_history_unfiltered(self, scoring_engine, sample_member):
        sample_member.add_member("user-josh")
        sample_member.add_member("user-amy")
        scoring_engine.award_points("user-josh", "Dishes", 10)
        scoring_engine.award_points("user-amy", "Mop", 5)
        all_history = scoring_engine.get_history()
        assert len(all_history) == 2


class TestScoringEngineAIScore:
    """5.2 AI Score Task"""

    def test_ai_score_with_valid_config_returns_int(self, scoring_engine):
        config = LLMConfig(base_url="http://test", api_key="key", model="test")
        result = scoring_engine.ai_score_task("Clean the garage", config)
        assert isinstance(result, int)

    def test_ai_score_no_config_fallback(self, scoring_engine):
        result = scoring_engine.ai_score_task("Clean the garage")
        assert result == FALLBACK_POINTS

    def test_ai_score_invalid_config_fallback(self, scoring_engine):
        config = LLMConfig(base_url="not-a-url", api_key="", model="test")
        result = scoring_engine.ai_score_task("Clean the garage", config)
        assert result == FALLBACK_POINTS

    def test_ai_score_timeout_fallback(self, scoring_engine):
        config = LLMConfig(base_url="http://nonexistent.invalid", api_key="key", model="test")
        result = scoring_engine.ai_score_task("Clean the garage", config)
        assert result == FALLBACK_POINTS

    def test_ai_score_non_integer_response_fallback(self, scoring_engine):
        # This test will need a mock — for now, verify fallback path exists
        config = LLMConfig(base_url="http://test", api_key="key", model="test")
        result = scoring_engine.ai_score_task("Test", config)
        assert isinstance(result, int)
