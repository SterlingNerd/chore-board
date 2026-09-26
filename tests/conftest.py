"""Shared fixtures for chore-board tests."""

import pytest
from chore_board.chore import Chore, ChoreManager
from chore_board.member import MemberManager
from chore_board.scoring import ScoringEngine, FALLBACK_POINTS
from chore_board.attribution import AttributionManager


@pytest.fixture
def chore_manager():
    return ChoreManager()


@pytest.fixture
def member_manager():
    return MemberManager()


@pytest.fixture
def scoring_engine(member_manager):
    return ScoringEngine(member_manager)


@pytest.fixture
def attribution_manager():
    return AttributionManager()


@pytest.fixture
def sample_chore():
    return Chore(id="chore-1", title="Dishes", points=10)


@pytest.fixture
def sample_member(member_manager):
    # Return the same member_manager used by scoring_engine
    return member_manager
