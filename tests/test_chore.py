"""Tests for ChoreManager — based on test-plan.md section 1."""

import pytest
from chore_board.chore import Chore


class TestChoreManagerCreate:
    """1.1 Create Chore"""

    def test_create_valid_chore(self, chore_manager):
        chore = Chore(id="chore-1", title="Dishes", points=10)
        chore_manager.add_chore(chore)
        result = chore_manager.get_chore("chore-1")
        assert result.id == "chore-1"
        assert result.title == "Dishes"
        assert result.points == 10

    def test_create_chore_with_zero_points(self, chore_manager):
        chore = Chore(id="chore-2", title="Breathe", points=0)
        chore_manager.add_chore(chore)
        result = chore_manager.get_chore("chore-2")
        assert result.points == 0

    def test_create_chore_with_high_points(self, chore_manager):
        chore = Chore(id="chore-3", title="Rearrange furniture", points=100)
        chore_manager.add_chore(chore)
        result = chore_manager.get_chore("chore-3")
        assert result.points == 100

    def test_create_chore_with_assignee(self, chore_manager):
        chore = Chore(id="chore-4", title="Mow lawn", points=15, assigned_to="user-josh")
        chore_manager.add_chore(chore)
        result = chore_manager.get_chore("chore-4")
        assert result.assigned_to == "user-josh"

    def test_create_chore_with_missing_title_raises(self, chore_manager):
        with pytest.raises((ValueError, TypeError)):
            chore_manager.add_chore(Chore(id="chore-5", title="", points=5))

    def test_create_chore_with_empty_title_raises(self, chore_manager):
        with pytest.raises((ValueError, TypeError)):
            chore_manager.add_chore(Chore(id="chore-6", title="   ", points=5))

    def test_create_chore_with_negative_points_raises(self, chore_manager):
        with pytest.raises((ValueError, TypeError)):
            chore_manager.add_chore(Chore(id="chore-7", title="Walk dog", points=-1))

    def test_create_chore_with_non_integer_points_raises(self, chore_manager):
        with pytest.raises((ValueError, TypeError)):
            chore_manager.add_chore(Chore(id="chore-8", title="Sweep", points=3.5))


class TestChoreManagerUpdate:
    """1.2 Update Chore"""

    def test_update_points(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        chore_manager.update_chore("chore-1", points=15)
        result = chore_manager.get_chore("chore-1")
        assert result.points == 15

    def test_update_title(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        chore_manager.update_chore("chore-1", title="Wash Dishes")
        result = chore_manager.get_chore("chore-1")
        assert result.title == "Wash Dishes"

    def test_update_assignee(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        chore_manager.update_chore("chore-1", assigned_to="user-josh")
        result = chore_manager.get_chore("chore-1")
        assert result.assigned_to == "user-josh"

    def test_update_nonexistent_chore_raises(self, chore_manager):
        with pytest.raises((KeyError, ValueError)):
            chore_manager.update_chore("nonexistent", points=5)

    def test_update_chore_with_negative_points_raises(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        with pytest.raises((ValueError, TypeError)):
            chore_manager.update_chore("chore-1", points=-5)


class TestChoreManagerToggleActive:
    """1.3 Toggle Chore Active/Inactive"""

    def test_deactivate_chore(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        chore_manager.toggle_active("chore-1")
        result = chore_manager.get_chore("chore-1")
        assert result.active is False

    def test_reactivate_chore(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        chore_manager.toggle_active("chore-1")
        chore_manager.toggle_active("chore-1")
        result = chore_manager.get_chore("chore-1")
        assert result.active is True

    def test_toggle_nonexistent_raises(self, chore_manager):
        with pytest.raises((KeyError, ValueError)):
            chore_manager.toggle_active("nonexistent")


class TestChoreManagerDelete:
    """1.4 Delete Chore"""

    def test_delete_chore(self, chore_manager):
        chore_manager.add_chore(Chore(id="chore-1", title="Dishes", points=10))
        chore_manager.delete_chore("chore-1")
        with pytest.raises((KeyError, ValueError)):
            chore_manager.get_chore("chore-1")

    def test_delete_nonexistent_raises(self, chore_manager):
        with pytest.raises((KeyError, ValueError)):
            chore_manager.delete_chore("nonexistent")


class TestChoreManagerListQuery:
    """1.5 List/Query Chores"""

    def test_list_all_chores(self, chore_manager):
        chore_manager.add_chore(Chore(id="c1", title="Dishes", points=10))
        chore_manager.add_chore(Chore(id="c2", title="Mop", points=5))
        result = chore_manager.list_chores()
        assert len(result) == 2

    def test_list_active_only(self, chore_manager):
        chore_manager.add_chore(Chore(id="c1", title="Dishes", points=10))
        chore_manager.add_chore(Chore(id="c2", title="Mop", points=5))
        chore_manager.toggle_active("c2")
        result = chore_manager.list_chores(active_only=True)
        assert len(result) == 1
        assert result[0].id == "c1"

    def test_list_by_assignee(self, chore_manager):
        chore_manager.add_chore(Chore(id="c1", title="Dishes", points=10, assigned_to="user-josh"))
        chore_manager.add_chore(Chore(id="c2", title="Mop", points=5, assigned_to="user-amy"))
        result = chore_manager.list_chores_by_assignee("user-josh")
        assert len(result) == 1
        assert result[0].id == "c1"

    def test_no_chores_returns_empty_list(self, chore_manager):
        result = chore_manager.list_chores()
        assert result == []
        assert isinstance(result, list)

    def test_list_active_chores_helper(self, chore_manager):
        chore_manager.add_chore(Chore(id="c1", title="Dishes", points=10))
        chore_manager.add_chore(Chore(id="c2", title="Mop", points=5))
        chore_manager.toggle_active("c2")
        result = chore_manager.list_active_chores()
        assert len(result) == 1
