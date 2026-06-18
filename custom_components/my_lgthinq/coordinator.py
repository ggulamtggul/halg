"""DataUpdateCoordinator for the LG ThinQ Web emulated device."""

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from . import ThinqConfigEntry

from .api import ThinQWebAPI, ThinQWebAPIException
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DeviceDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """LG ThinQ Web emulated Device's Data Update Coordinator."""

    config_entry: "ThinqConfigEntry"

    def __init__(
        self,
        hass,
        config_entry: "ThinqConfigEntry",
        api: ThinQWebAPI,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize data coordinator."""
        # Poll state every 60 seconds
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN}_{device_info['deviceId']}",
            update_interval=timedelta(seconds=60),
        )

        self.api = api
        self.device_id = device_info["deviceId"]
        self.device_name = device_info.get("alias", "LG Robot Cleaner")
        self.model_name = device_info.get("modelName", "Robot Cleaner")
        self.device_type = device_info.get("deviceType", "ROBOT_CLEANER")
        self.unique_id = self.device_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Request to the server to update the status."""
        try:
            _LOGGER.debug("Polling status for ThinQ Web device: %s", self.device_id)
            return await self.api.async_get_device_status(self.device_id)
        except ThinQWebAPIException as e:
            raise UpdateFailed(f"Error communicating with ThinQ Web API: {e}") from e
