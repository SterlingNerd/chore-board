"""Tests for AttributionManager — based on test-plan.md section 4."""

import pytest
from chore_board.attribution import AttributionState, PendingAttribution


class TestAttributionManagerLifecycle:
    """4.1 Pending Attribution Lifecycle"""

    def test_create_pending(self, attribution_manager):
        aid = attribution_manager.create_pending("task-1", "Dishes done")
        assert aid is not None
        entry = attribution_manager.get_attribution(aid)
        assert entry.task_uid == "task-1"
        assert entry.state == AttributionState.PENDING

    def test_resolve_pending(self, attribution_manager):
        aid = attribution_manager.create_pending("task-1", "Dishes done")
        attribution_manager.resolve(aid, "user-josh")
        entry = attribution_manager.get_attribution(aid)
        assert entry.state == AttributionState.ATTRIBUTED
        assert entry.attributed_to == "user-josh"

    def test_dismiss_pending(self, attribution_manager):
        aid = attribution_manager.create_pending("task-1", "Dishes done")
        attribution_manager.dismiss(aid)
        entry = attribution_manager.get_attribution(aid)
        assert entry.state == AttributionState.DISMISSED

    def test_acknowledge_nonexistent_raises(self, attribution_manager):
        with pytest.raises((KeyError, ValueError)):
            attribution_manager.resolve("nonexistent", "user-josh")

    def test_multiple_pending_independent(self, attribution_manager):
        aid1 = attribution_manager.create_pending("task-1", "Dishes")
        aid2 = attribution_manager.create_pending("task-2", "Mop")
        attribution_manager.resolve(aid1, "user-josh")
        entry2 = attribution_manager.get_attribution(aid2)
        assert entry2.state == AttributionState.PENDING


class TestAttributionManagerQueries:
    def test_get_pending(self, attribution_manager):
        attribution_manager.create_pending("task-1", "Dishes")
        attribution_manager.create_pending("task-2", "Mop")
        pending = attribution_manager.get_pending()
        assert len(pending) == 2

    def test_has_pending(self, attribution_manager):
        attribution_manager.create_pending("task-1", "Dishes")
        assert attribution_manager.has_pending("task-1") is True
        assert attribution_manager.has_pending("task-nonexistent") is False

    def test_cleanup_removes_entry(self, attribution_manager):
        aid = attribution_manager.create_pending("task-1", "Dishes")
        attribution_manager.dismiss(aid)
        attribution_manager.cleanup(aid)
        assert len(attribution_manager.get_pending()) == 0

    def test_cleanup_attributed_entry(self, attribution_manager):
        aid = attribution_manager.create_pending("task-1", "Dishes")
        attribution_manager.resolve(aid, "user-josh")
        attribution_manager.cleanup(aid)
        assert len(attribution_manager.get_pending()) == 0
