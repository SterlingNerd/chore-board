"""Tests for WebSocket module — based on test-plan.md section 11.4."""

import pytest
from chore_board.websocket import async_register_websocket


class TestWebSocket:
    """11.4 WebSocket"""

    @pytest.mark.asyncio
    async def test_register_websocket_handlers(self):
        """Should not raise"""
        await async_register_websocket(hass=None)
