"""Tests for MemberManager — based on test-plan.md section 2."""

import pytest
from chore_board.member import Member


class TestMemberManagerAdd:
    """2.1 Add Participant"""

    def test_add_ha_user_as_member(self, member_manager):
        member_manager.add_member("user-josh")
        result = member_manager.get_member("user-josh")
        assert result is not None
        assert result.user_id == "user-josh"

    def test_add_ha_user_with_external_account(self, member_manager):
        member_manager.add_member("user-josh", external_account="josh.todoist")
        result = member_manager.get_member("user-josh")
        assert result.external_account == "josh.todoist"

    def test_add_duplicate_member_raises(self, member_manager):
        member_manager.add_member("user-josh")
        with pytest.raises((ValueError, KeyError)):
            member_manager.add_member("user-josh")

    def test_member_exists(self, member_manager):
        member_manager.add_member("user-josh")
        assert member_manager.member_exists("user-josh") is True
        assert member_manager.member_exists("user-unknown") is False


class TestMemberManagerRemove:
    """2.2 Remove Participant"""

    def test_remove_member(self, member_manager):
        member_manager.add_member("user-josh")
        member_manager.remove_member("user-josh")
        assert member_manager.get_member("user-josh") is None

    def test_remove_member_with_no_chore_history(self, member_manager):
        member_manager.add_member("user-josh")
        member_manager.remove_member("user-josh")
        assert member_manager.get_member("user-josh") is None

    def test_remove_nonexistent_raises(self, member_manager):
        with pytest.raises((KeyError, ValueError)):
            member_manager.remove_member("nonexistent")


class TestMemberManagerLinkExternal:
    """2.3 Link External Account"""

    def test_link_external_account(self, member_manager):
        member_manager.add_member("user-josh")
        member_manager.link_external_account("user-josh", "josh.todoist")
        result = member_manager.get_member("user-josh")
        assert result.external_account == "josh.todoist"

    def test_update_existing_external_account(self, member_manager):
        member_manager.add_member("user-josh", external_account="old")
        member_manager.link_external_account("user-josh", "new")
        result = member_manager.get_member("user-josh")
        assert result.external_account == "new"

    def test_remove_external_account(self, member_manager):
        member_manager.add_member("user-josh", external_account="josh.todoist")
        member_manager.link_external_account("user-josh", None)
        result = member_manager.get_member("user-josh")
        assert result.external_account is None

    def test_link_empty_string_stored_as_none(self, member_manager):
        member_manager.add_member("user-josh")
        member_manager.link_external_account("user-josh", "")
        result = member_manager.get_member("user-josh")
        assert result.external_account is None


class TestMemberManagerLookup:
    """2.4 Participant Lookup"""

    def test_lookup_by_user_id(self, member_manager):
        member_manager.add_member("user-josh")
        result = member_manager.get_member("user-josh")
        assert result is not None
        assert result.user_id == "user-josh"

    def test_lookup_nonexistent_returns_none(self, member_manager):
        result = member_manager.get_member("nonexistent")
        assert result is None

    def test_get_all_member_ids(self, member_manager):
        member_manager.add_member("user-josh")
        member_manager.add_member("user-amy")
        ids = member_manager.get_all_member_ids()
        assert "user-josh" in ids
        assert "user-amy" in ids
        assert len(ids) == 2
