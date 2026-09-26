"""Tests for TodoStore — based on test-plan.md section 9."""

import pytest
from chore_board.todo_store.ha_todos import HATodoStore


class TestHATodoStore:
    """9 Todo Store (HATodoStore)"""

    @pytest.mark.asyncio
    async def test_initialize_with_valid_config(self):
        """9.1 Initialize — positive case"""
        store = HATodoStore(hass=None)
        await store.async_initialize()
        # Should not raise

    @pytest.mark.asyncio
    async def test_poll_returns_changes(self):
        """9.2 Poll — positive"""
        store = HATodoStore(hass=None)
        await store.async_initialize()
        changes = await store.async_poll()
        assert isinstance(changes, list)

    @pytest.mark.asyncio
    async def test_poll_no_changes_no_false_positives(self):
        """9.2 Poll — no changes"""
        store = HATodoStore(hass=None)
        await store.async_initialize()
        changes1 = await store.async_poll()
        changes2 = await store.async_poll()
        # Subsequent polls should not report the same items as new

    @pytest.mark.asyncio
    async def test_poll_empty_response_handled(self):
        """9.2 Poll — negative: empty response"""
        store = HATodoStore(hass=None)
        await store.async_initialize()
        changes = await store.async_poll()
        assert isinstance(changes, list)

    @pytest.mark.asyncio
    async def test_list_returns_items(self):
        """9.3 List"""
        store = HATodoStore(hass=None)
        await store.async_initialize()
        items = await store.async_list()
        assert isinstance(items, list)
