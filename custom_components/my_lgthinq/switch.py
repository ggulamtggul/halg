"""Support for switch entities via ThinQ Web API emulation."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ThinqConfigEntry
from .entity import ThinQEntity

_LOGGER = logging.getLogger(__name__)

SWITCH_DESC = [
    SwitchEntityDescription(
        key="aiObstacleAvoidance",
        name="AI Obstacle Avoidance",
        translation_key="ai_obstacle_avoidance",
    ),
    SwitchEntityDescription(
        key="autoResume",
        name="Auto Resume",
        translation_key="auto_resume",
    ),
    SwitchEntityDescription(
        key="childLock",
        name="Child Lock",
        translation_key="child_lock",
    ),
    SwitchEntityDescription(
        key="autoEmptyDustbin",
        name="Auto Empty Dustbin",
        translation_key="auto_empty_dustbin",
    ),
    SwitchEntityDescription(
        key="autoMopWash",
        name="Auto Mop Wash",
        translation_key="auto_mop_wash",
    ),
    SwitchEntityDescription(
        key="autoMopDry",
        name="Auto Mop Dry",
        translation_key="auto_mop_dry",
    ),
    SwitchEntityDescription(
        key="dndMode",
        name="Do Not Disturb Mode",
        translation_key="dnd_mode",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ThinqConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up entry for switch platform."""
    entities: list[ThinQSwitchEntity] = []
    for coordinator in entry.runtime_data.coordinators.values():
        for description in SWITCH_DESC:
            entities.append(ThinQSwitchEntity(coordinator, description, description.key))

    if entities:
        async_add_entities(entities)


class ThinQSwitchEntity(ThinQEntity, SwitchEntity):
    """Represent an emulated ThinQ switch entity."""

    def __init__(
        self,
        coordinator: Any,
        description: SwitchEntityDescription,
        property_id: str,
    ) -> None:
        """Initialize switch entity."""
        super().__init__(coordinator, description, property_id)
        self._attr_is_on = False

    def _update_status(self) -> None:
        """Update status native value."""
        super()._update_status()

        if self.coordinator.data is None:
            self._attr_is_on = False
            return

        value = self.coordinator.data.get(self.property_id, "off")
        self._attr_is_on = value == "on"
        _LOGGER.debug(
            "[%s] switch update status for %s: %s",
            self.coordinator.device_name,
            self.property_id,
            self.is_on,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug(
            "[%s] switch turn_on for %s",
            self.coordinator.device_name,
            self.property_id,
        )
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, self.property_id, "on"
            )
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug(
            "[%s] switch turn_off for %s",
            self.coordinator.device_name,
            self.property_id,
        )
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, self.property_id, "off"
            )
        )
        await self.coordinator.async_request_refresh()
