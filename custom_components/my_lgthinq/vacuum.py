"""Support for vacuum entities via ThinQ Web API emulation."""

from enum import StrEnum
import logging
from typing import Any

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    StateVacuumEntityDescription,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ThinqConfigEntry
from .entity import ThinQEntity

_LOGGER = logging.getLogger(__name__)


class State(StrEnum):
    """State of device commands."""

    HOMING = "homing"
    PAUSE = "pause"
    RESUME = "resume"
    SLEEP = "sleep"
    START = "start"
    WAKE_UP = "wake_up"


# Map ThinQ Web status report values to Home Assistant activities
ROBOT_STATUS_TO_HA = {
    "charging": VacuumActivity.DOCKED,
    "diagnosis": VacuumActivity.IDLE,
    "homing": VacuumActivity.RETURNING,
    "initializing": VacuumActivity.IDLE,
    "macrosector": VacuumActivity.IDLE,
    "monitoring_detecting": VacuumActivity.IDLE,
    "monitoring_moving": VacuumActivity.IDLE,
    "monitoring_positioning": VacuumActivity.IDLE,
    "pause": VacuumActivity.PAUSED,
    "reservation": VacuumActivity.IDLE,
    "setdate": VacuumActivity.IDLE,
    "sleep": VacuumActivity.IDLE,
    "standby": VacuumActivity.IDLE,
    "working": VacuumActivity.CLEANING,
    "station": VacuumActivity.CLEANING,
    "station_dry": VacuumActivity.CLEANING,
    "clean_learning": VacuumActivity.CLEANING,
    "station_mop": VacuumActivity.CLEANING,
    "water_removal": VacuumActivity.CLEANING,
    "water_injection": VacuumActivity.CLEANING,
    "clean_select": VacuumActivity.CLEANING,
    "clean_select_gozone": VacuumActivity.CLEANING,
    "error": VacuumActivity.ERROR,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ThinqConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up an entry for vacuum platform."""
    entities: list[ThinQStateVacuumEntity] = []
    for coordinator in entry.runtime_data.coordinators.values():
        description = StateVacuumEntityDescription(
            key="vacuum_control",
            name=None,
        )
        entities.append(ThinQStateVacuumEntity(coordinator, description, "runState"))

    if entities:
        async_add_entities(entities)


class ThinQStateVacuumEntity(ThinQEntity, StateVacuumEntity):
    """Represent an emulated ThinQ robot cleaner."""

    _attr_supported_features = (
        VacuumEntityFeature.STATE
        | VacuumEntityFeature.BATTERY
        | VacuumEntityFeature.START
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.RETURN_HOME
    )

    def _update_status(self) -> None:
        """Update the entity status based on coordinator data."""
        super()._update_status()
        
        if self.coordinator.data is None:
            return

        # Fetch status fields
        current_state = self.coordinator.data.get("runState", "sleep")
        battery_level = self.coordinator.data.get("battery", 0)

        # Update HA state
        self._attr_activity = ROBOT_STATUS_TO_HA.get(current_state, VacuumActivity.IDLE)
        self._attr_battery_level = battery_level

        _LOGGER.debug(
            "[%s] update status: %s -> %s (battery_level=%s)",
            self.coordinator.device_name,
            current_state,
            self.state,
            self.battery_level,
        )

    async def async_start(self, **kwargs) -> None:
        """Start or resume the cleaning task."""
        current_state = self.coordinator.data.get("runState", "sleep") if self.coordinator.data else "sleep"
        
        if current_state == State.SLEEP:
            value = State.WAKE_UP
        elif self._attr_activity == VacuumActivity.PAUSED:
            value = State.RESUME
        else:
            value = State.START

        _LOGGER.debug("[%s] async_start: command state %s", self.coordinator.device_name, value)
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, "runState", value
            )
        )
        await self.coordinator.async_request_refresh()

    async def async_pause(self, **kwargs) -> None:
        """Pause the cleaning task."""
        _LOGGER.debug("[%s] async_pause", self.coordinator.device_name)
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, "runState", State.PAUSE
            )
        )
        await self.coordinator.async_request_refresh()

    async def async_return_to_base(self, **kwargs: Any) -> None:
        """Send the robot back to dock."""
        _LOGGER.debug("[%s] async_return_to_base", self.coordinator.device_name)
        await self.async_call_api(
            self.coordinator.api.async_set_device_control(
                self.coordinator.device_id, "runState", State.HOMING
            )
        )
        await self.coordinator.async_request_refresh()
