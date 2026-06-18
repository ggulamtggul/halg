"""Support for sensor entities via ThinQ Web API emulation."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ThinqConfigEntry
from .entity import ThinQEntity

_LOGGER = logging.getLogger(__name__)

# List of sensors to create for each robot cleaner
SENSORS_DESC = [
    SensorEntityDescription(
        key="battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="runState",
        device_class=SensorDeviceClass.ENUM,
        translation_key="current_state",
    ),
    SensorEntityDescription(
        key="robotCleanerJobMode",
        device_class=SensorDeviceClass.ENUM,
        translation_key="current_job_mode",
    ),
    SensorEntityDescription(
        key="mainBrushLife",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="main_brush_life",
    ),
    SensorEntityDescription(
        key="sideBrushLife",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="side_brush_life",
    ),
    SensorEntityDescription(
        key="filterLife",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="filter_life",
    ),
    SensorEntityDescription(
        key="mopLife",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="mop_life",
    ),
    SensorEntityDescription(
        key="dustBagLife",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="dust_bag_life",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ThinqConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up entry for sensor platform."""
    entities: list[ThinQSensorEntity] = []
    for coordinator in entry.runtime_data.coordinators.values():
        for description in SENSORS_DESC:
            # We create a sensor for each key in coordinator data if it exists or default
            entities.append(ThinQSensorEntity(coordinator, description, description.key))

    if entities:
        async_add_entities(entities)


class ThinQSensorEntity(ThinQEntity, SensorEntity):
    """Represent an emulated ThinQ sensor."""

    def _update_status(self) -> None:
        """Update status native value."""
        super()._update_status()

        if self.coordinator.data is None:
            self._attr_native_value = None
            return

        self._attr_native_value = self.coordinator.data.get(self.property_id)
        _LOGGER.debug(
            "[%s] sensor update status for %s: %s",
            self.coordinator.device_name,
            self.property_id,
            self.native_value,
        )
