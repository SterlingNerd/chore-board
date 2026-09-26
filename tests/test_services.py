"""Tests for service handlers — based on test-plan.md section 6."""

import pytest
from types import SimpleNamespace


class TestAssignChoreHandler:
    """6.1 chore_board.assign_chore"""

    @pytest.mark.asyncio
    async def test_assign_chore_valid_data(self, chore_manager, member_manager, scoring_engine, attribution_manager):
        """Positive: assign chore with valid data"""
        from chore_board.services.chore_handlers import async_assign_chore

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "chore_manager": chore_manager,
                    "member_manager": member_manager,
                    "scoring_engine": scoring_engine,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"chore_id": "c1", "title": "Dishes", "points": 10})
        await async_assign_chore(mock_hass, mock_call)
        assert chore_manager.get_chore("c1").title == "Dishes"

    @pytest.mark.asyncio
    async def test_assign_chore_missing_fields_raises(self, chore_manager, member_manager, scoring_engine, attribution_manager):
        """Negative: missing required fields"""
        from chore_board.services.chore_handlers import async_assign_chore

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "chore_manager": chore_manager,
                    "member_manager": member_manager,
                    "scoring_engine": scoring_engine,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={})
        with pytest.raises(ValueError):
            await async_assign_chore(mock_hass, mock_call)


class TestAwardPointsHandler:
    """6.2 chore_board.award_points"""

    @pytest.mark.asyncio
    async def test_award_points_valid(self, scoring_engine, member_manager, attribution_manager):
        member_manager.add_member("user-josh")
        from chore_board.services.scoring_handlers import async_award_points

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "scoring_engine": scoring_engine,
                    "member_manager": member_manager,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"participant_id": "user-josh", "chore_title": "Dishes", "points": 10})
        await async_award_points(mock_hass, mock_call)
        assert scoring_engine.get_score("user-josh") == 10

    @pytest.mark.asyncio
    async def test_award_points_invalid_participant_raises(self, scoring_engine, member_manager, attribution_manager):
        from chore_board.services.scoring_handlers import async_award_points

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "scoring_engine": scoring_engine,
                    "member_manager": member_manager,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"participant_id": "unknown", "chore_title": "Dishes", "points": 10})
        with pytest.raises(KeyError):
            await async_award_points(mock_hass, mock_call)


class TestAdjustChorePointsHandler:
    """6.3 chore_board.adjust_chore_points"""

    @pytest.mark.asyncio
    async def test_adjust_points_up(self, chore_manager):
        from chore_board.chore import Chore
        chore_manager.add_chore(Chore(id="c1", title="Dishes", points=10))
        from chore_board.services.chore_handlers import async_adjust_chore_points

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(data={"chore_manager": chore_manager})
        )
        mock_call = SimpleNamespace(data={"chore_id": "c1", "points": 15})
        await async_adjust_chore_points(mock_hass, mock_call)
        assert chore_manager.get_chore("c1").points == 15

    @pytest.mark.asyncio
    async def test_adjust_points_for_nonexistent_raises(self, chore_manager):
        from chore_board.services.chore_handlers import async_adjust_chore_points

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(data={"chore_manager": chore_manager})
        )
        mock_call = SimpleNamespace(data={"chore_id": "nonexistent", "points": 15})
        with pytest.raises(KeyError):
            await async_adjust_chore_points(mock_hass, mock_call)


class TestLogTaskHandler:
    """6.4 chore_board.log_task"""

    @pytest.mark.asyncio
    async def test_log_task_with_description_and_points(self, scoring_engine, member_manager, attribution_manager):
        member_manager.add_member("user-josh")
        from chore_board.services.scoring_handlers import async_log_task

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "scoring_engine": scoring_engine,
                    "member_manager": member_manager,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"description": "Cleaned garage", "points": 20, "participant_id": "user-josh"})
        await async_log_task(mock_hass, mock_call)
        assert scoring_engine.get_score("user-josh") == 20

    @pytest.mark.asyncio
    async def test_log_task_missing_description_raises(self, scoring_engine, member_manager, attribution_manager):
        from chore_board.services.scoring_handlers import async_log_task

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "scoring_engine": scoring_engine,
                    "member_manager": member_manager,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"points": 10, "participant_id": "user-josh"})
        with pytest.raises(ValueError):
            await async_log_task(mock_hass, mock_call)


class TestAiScoreHandler:
    """6.5 chore_board.ai_score"""

    @pytest.mark.asyncio
    async def test_ai_score_with_llm(self, scoring_engine, member_manager, attribution_manager):
        from chore_board.services.scoring_handlers import async_ai_score

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "scoring_engine": scoring_engine,
                    "member_manager": member_manager,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"description": "Clean the garage"})
        result = await async_ai_score(mock_hass, mock_call)
        assert "points" in result
        assert isinstance(result["points"], int)

    @pytest.mark.asyncio
    async def test_ai_score_no_config_fallback(self, scoring_engine, member_manager, attribution_manager):
        from chore_board.services.scoring_handlers import async_ai_score

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(
                data={
                    "scoring_engine": scoring_engine,
                    "member_manager": member_manager,
                    "attribution_manager": attribution_manager,
                }
            )
        )
        mock_call = SimpleNamespace(data={"description": "Clean the garage"})
        result = await async_ai_score(mock_hass, mock_call)
        assert result["points"] == 10  # FALLBACK_POINTS


class TestAcknowledgeHandler:
    """6.6 chore_board.acknowledge"""

    @pytest.mark.asyncio
    async def test_acknowledge_pending(self, attribution_manager):
        from chore_board.services.scoring_handlers import async_acknowledge

        aid = attribution_manager.create_pending("task-1", "Dishes")
        mock_hass = SimpleNamespace(
            services=SimpleNamespace(data={"attribution_manager": attribution_manager})
        )
        mock_call = SimpleNamespace(data={"attribution_id": aid})
        await async_acknowledge(mock_hass, mock_call)
        entry = attribution_manager.get_attribution(aid)
        assert entry.state.value == "dismissed"

    @pytest.mark.asyncio
    async def test_acknowledge_nonexistent_raises(self, attribution_manager):
        from chore_board.services.scoring_handlers import async_acknowledge

        mock_hass = SimpleNamespace(
            services=SimpleNamespace(data={"attribution_manager": attribution_manager})
        )
        mock_call = SimpleNamespace(data={"attribution_id": "nonexistent"})
        with pytest.raises(KeyError):
            await async_acknowledge(mock_hass, mock_call)
