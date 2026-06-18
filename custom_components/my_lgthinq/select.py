"""Support for select entities via ThinQ Web API emulation."""

import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ThinqConfigEntry
from .entity import ThinQEntity

_LOGGER = logging.getLogger(__name__)

SELECT_DESC = [
    SelectEntityDescription(
        key="cleaningMode",
        name="Cleaning Mode",
        options=["suction_mop", "suction_only", "mop_only"],
        translation_key="cleaning_mode",
    ),
    SelectEntityDescription(
        key="carpetMode",
        name="Carpet Mode",
        options=["smart_carpet", "carpet_avoidance"],
        translation_key="carpet_mode",
    ),
    SelectEntityDescription(
        key="volume",
        name="Product Volume",
        options=["loud", "medium", "soft", "mute"],
        translation_key="product_volume",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ThinqConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up entry for select platform."""
    entities: list[ThinQSelectEntity] = []
    for coordinator in entry.runtime_data.coordinators.values():
        for description in SELECT_DESC:
            entities.append(ThinQSelectEntity(coordinator, description, description.key))

    if entities:
        async_add_entities(entities)


class ThinQSelectEntity(ThinQEntity, SelectEntity):
    """Represent an emulated ThinQ select entity."""

    def __init__(
        self,
        coordinator: Any,
        description: SelectEntityDescription,
        property_id: str,
    ) -> None:
        """Initialize select entity."""
        super().__init__(coordinator, description, property_id)
        self._attr_current_option = None
        self._attr_options = description.options

    def _update_status(self) -> None:
        """Update status native value."""
        super()._update_status()

        if self.coordinator.data is None:
            self._attr_current_option = None
            return

        self._attr_current_option = self.coordinator.data.get(self.property_id)
        _LOGGER.debug(
            "[%s] select update status for %s: %s",
            self.coordinator.device_name,
            self.property_id,
            self.current_option,
        )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.debug(
            "[%s] select option for %s: %s",
            self.coordinator.device_name,
            self.property_id,
            option,
        )
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, self.property_id, option
            )
        )
        await self.coordinator.async_request_refresh()
