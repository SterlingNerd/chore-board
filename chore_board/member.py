"""HA user → participant management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Member:
    """A participant, backed by an HA user."""
    user_id: str
    external_account: Optional[str] = None


class MemberManager:
    """Manage participants (HA users)."""

    def __init__(self) -> None:
        self._members: dict[str, Member] = {}

    def add_member(self, user_id: str, external_account: Optional[str] = None) -> None:
        """Add a participant."""
        if user_id in self._members:
            raise ValueError(f"Member '{user_id}' already exists")
        self._members[user_id] = Member(user_id=user_id, external_account=external_account)

    def remove_member(self, user_id: str) -> None:
        """Remove a participant."""
        if user_id not in self._members:
            raise KeyError(f"Member '{user_id}' not found")
        del self._members[user_id]

    def link_external_account(self, user_id: str, account: Optional[str]) -> None:
        """Link or unlink an external account."""
        member = self._get_or_raise(user_id)
        member.external_account = account if account and account.strip() else None

    def get_member(self, user_id: str) -> Optional[Member]:
        """Look up a participant. Returns None if not found."""
        return self._members.get(user_id)

    def get_all_member_ids(self) -> list[str]:
        """Return all participant user IDs."""
        return list(self._members.keys())

    def member_exists(self, user_id: str) -> bool:
        """Check if a participant exists."""
        return user_id in self._members

    def _get_or_raise(self, user_id: str) -> Member:
        if user_id not in self._members:
            raise KeyError(f"Member '{user_id}' not found")
        return self._members[user_id]
