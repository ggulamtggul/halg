"""Base class for ThinQ Web emulated entities."""

from collections.abc import Callable, Coroutine
import logging
from typing import Any

from homeassistant.core import callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import ThinQWebAPIException
from .const import COMPANY, DEVICE_UNIT_TO_HA, DOMAIN
from .coordinator import DeviceDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class ThinQEntity(CoordinatorEntity[DeviceDataUpdateCoordinator]):
    """The base implementation of all lg thinq emulated entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DeviceDataUpdateCoordinator,
        entity_description: EntityDescription,
        property_id: str,
        postfix_id: str | None = None,
    ) -> None:
        """Initialize an entity."""
        super().__init__(coordinator)

        self.entity_description = entity_description
        self.property_id = property_id

        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, coordinator.unique_id)},
            manufacturer=COMPANY,
            model=f"{coordinator.model_name} ({coordinator.device_type})",
            name=coordinator.device_name,
        )
        self._attr_unique_id = (
            f"{coordinator.unique_id}_{self.property_id}"
            if postfix_id is None
            else f"{coordinator.unique_id}_{self.property_id}_{postfix_id}"
        )

    @property
    def data(self) -> Any:
        """Return the value for this property from the coordinator data."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.property_id)

    def _update_status(self) -> None:
        """Update status itself."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_status()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Call when entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

    async def async_call_api(
        self,
        target: Coroutine[Any, Any, Any],
        on_fail_method: Callable[[], None] | None = None,
    ) -> None:
        """Call the given api and handle exception."""
        try:
            await target
        except ThinQWebAPIException as exc:
            if on_fail_method:
                on_fail_method()
            raise ServiceValidationError(exc.message) from exc
        except ValueError as exc:
            if on_fail_method:
                on_fail_method()
            raise ServiceValidationError(exc) from exc
