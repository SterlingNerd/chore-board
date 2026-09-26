"""Service handlers for scoring-related services."""

from __future__ import annotations


async def async_award_points(hass: object, service_call: object) -> None:
    """Handle chore_board.award_points service."""
    data = service_call.data if service_call else {}
    participant_id = data.get("participant_id")
    chore_title = data.get("chore_title")
    points = data.get("points", 10)

    if not participant_id:
        raise ValueError("participant_id is required")
    if not chore_title:
        raise ValueError("chore_title is required")

    scoring = hass.services.data["scoring_engine"]
    scoring.award_points(participant_id, chore_title, points)


async def async_log_task(hass: object, service_call: object) -> None:
    """Handle chore_board.log_task service."""
    data = service_call.data if service_call else {}
    description = data.get("description")
    points = data.get("points", 10)
    participant_id = data.get("participant_id")

    if not description:
        raise ValueError("description is required")
    if not participant_id:
        raise ValueError("participant_id is required")

    scoring = hass.services.data["scoring_engine"]
    scoring.award_points(participant_id, description, points)


async def async_ai_score(hass: object, service_call: object) -> None:
    """Handle chore_board.ai_score service."""
    data = service_call.data if service_call else {}
    description = data.get("description")

    if not description:
        raise ValueError("description is required")

    scoring = hass.services.data["scoring_engine"]
    llm_config = hass.services.data.get("llm_config")
    points = scoring.ai_score_task(description, llm_config)

    return {"points": points}


async def async_acknowledge(hass: object, service_call: object) -> None:
    """Handle chore_board.acknowledge service."""
    data = service_call.data if service_call else {}
    attribution_id = data.get("attribution_id")

    if not attribution_id:
        raise ValueError("attribution_id is required")

    attribution = hass.services.data["attribution_manager"]
    attribution.dismiss(attribution_id)
