"""Support for button entities via ThinQ Web API emulation."""

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ThinqConfigEntry
from .entity import ThinQEntity

_LOGGER = logging.getLogger(__name__)

BUTTON_DESC = [
    ButtonEntityDescription(
        key="emptyDustbin",
        name="Empty Dustbin",
        translation_key="empty_dustbin",
    ),
    ButtonEntityDescription(
        key="mopWash",
        name="Mop Wash",
        translation_key="mop_wash",
    ),
    ButtonEntityDescription(
        key="mopDry",
        name="Mop Dry",
        translation_key="mop_dry",
    ),
    ButtonEntityDescription(
        key="residualWaterRemoval",
        name="Residual Water Removal",
        translation_key="residual_water_removal",
    ),
    ButtonEntityDescription(
        key="findVacuum",
        name="Find Vacuum",
        translation_key="find_vacuum",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ThinqConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up entry for button platform."""
    entities: list[ThinQButtonEntity] = []
    for coordinator in entry.runtime_data.coordinators.values():
        for description in BUTTON_DESC:
            entities.append(ThinQButtonEntity(coordinator, description, description.key))

    if entities:
        async_add_entities(entities)


class ThinQButtonEntity(ThinQEntity, ButtonEntity):
    """Represent an emulated ThinQ button entity."""

    async def async_press(self) -> None:
        """Press the button."""
        _LOGGER.debug(
            "[%s] button pressed for %s",
            self.coordinator.device_name,
            self.property_id,
        )
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, self.property_id, "start"
            )
        )
        await self.coordinator.async_request_refresh()
