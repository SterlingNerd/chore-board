"""Score sensors for each member."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ChoreBoardCoordinator
from .member import Member


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
    _attr_name = None  # show member name as entity name

    def __init__(self, coordinator: ChoreBoardCoordinator, member_id: str, name: str) -> None:
        self._coordinator = coordinator
        self._member_id = member_id
        self._attr_unique_id = f"{member_id}_score"
        self._attr_native_unit_of_measurement = "pts"
        self._attr_should_poll = False

    @property
    def native_value(self) -> int | None:
        return self._coordinator.data.scores.get(self._member_id) if self._coordinator.data else None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
