"""Sensors for Chore Board: per-member scores and leaderboard."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ChoreBoardCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ChoreBoardCoordinator = hass.data["coordinator"]

    sensors = []
    for member_id, member in coordinator.members.items():
        sensors.append(ScoreSensor(coordinator, member_id, member.name))

    async_add_entities(sensors)


class ScoreSensor(SensorEntity):
    """Sensor showing a member's total points."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator: ChoreBoardCoordinator, member_id: str, name: str) -> None:
        self._coordinator = coordinator
        self._member_id = member_id
        self._member_name = name
        self._attr_unique_id = f"{member_id}_score"
        self._attr_native_unit_of_measurement = "pts"
        self._attr_should_poll = False

    @property
    def native_value(self) -> int | None:
        return self._coordinator.data.scores.get(self._member_id) if self._coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        history = [h for h in self._coordinator.data.task_history if h.get("member_id") == self._member_id]
        return {
            "member_id": self._member_id,
            "name": self._member_name,
            "recent_activity": history[-5:] if history else [],
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
