"""Support for LG ThinQ Connect device via Web Dashboard API emulation."""

import asyncio
from dataclasses import dataclass, field
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_COUNTRY,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ThinQWebAPI, ThinQWebAPIException
from .const import DOMAIN, PLATFORMS
from .coordinator import DeviceDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True)
class ThinqData:
    """A class that holds runtime data."""

    coordinators: dict[str, DeviceDataUpdateCoordinator] = field(default_factory=dict)


type ThinqConfigEntry = ConfigEntry[ThinqData]


async def async_setup_entry(hass: HomeAssistant, entry: ThinqConfigEntry) -> bool:
    """Set up an entry."""
    entry.runtime_data = ThinqData()

    access_token = entry.data[CONF_ACCESS_TOKEN]
    country_code = entry.data[CONF_COUNTRY]

    api = ThinQWebAPI(
        session=async_get_clientsession(hass),
        access_token=access_token,
        country_code=country_code,
    )

    try:
        # Perform login session initiation
        await api.async_login()
    except ThinQWebAPIException as exc:
        raise ConfigEntryNotReady(f"Failed to login: {exc.message}") from exc

    # Setup coordinators and register devices.
    await async_setup_coordinators(hass, entry, api)

    # Set up platforms (vacuum, sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Clean up devices that are no longer in use
    async_cleanup_device_registry(hass, entry)

    return True


async def async_setup_coordinators(
    hass: HomeAssistant,
    entry: ThinqConfigEntry,
    api: ThinQWebAPI,
) -> None:
    """Set up coordinators and register devices."""
    try:
        device_list = await api.async_get_devices()
    except ThinQWebAPIException as exc:
        raise ConfigEntryNotReady(f"Failed to fetch device list: {exc.message}") from exc

    if not device_list:
        _LOGGER.warning("No devices registered on your LG ThinQ account")
        return

    # Filter only vacuum/robot cleaners or similar devices
    supported_devices = [
        dev for dev in device_list
        if dev.get("deviceType") == "ROBOT_CLEANER"
    ]

    if not supported_devices:
        _LOGGER.warning("No LG Robot Cleaners found in your account")
        return

    # Setup coordinator per device.
    coordinators = {}
    for dev in supported_devices:
        coordinator = DeviceDataUpdateCoordinator(hass, entry, api, dev)
        await coordinator.async_refresh()
        coordinators[coordinator.unique_id] = coordinator
        
    entry.runtime_data.coordinators = coordinators


def async_cleanup_device_registry(hass: HomeAssistant, entry: ThinqConfigEntry) -> None:
    """Clean up device registry."""
    new_device_unique_ids = [
        coordinator.unique_id
        for coordinator in entry.runtime_data.coordinators.values()
    ]
    device_registry = dr.async_get(hass)
    existing_entries = dr.async_entries_for_config_entry(
        device_registry, entry.entry_id
    )

    for old_entry in existing_entries:
        old_unique_id = next(iter(old_entry.identifiers))[1]
        if old_unique_id not in new_device_unique_ids:
            device_registry.async_remove_device(old_entry.id)
            _LOGGER.debug("Removed outdated device from registry: %s", old_entry.id)


async def async_unload_entry(hass: HomeAssistant, entry: ThinqConfigEntry) -> bool:
    """Unload the entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
