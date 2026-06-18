"""Tests for LG ThinQ Custom vacuum platform (Web API Emulated)."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from homeassistant.components.vacuum import VacuumActivity

from custom_components.my_lgthinq.vacuum import (
    ROBOT_STATUS_TO_HA,
    State,
)


def test_robot_status_mapping():
    """Test status mapping from ThinQ Web values to Home Assistant activities."""
    assert ROBOT_STATUS_TO_HA["charging"] == VacuumActivity.DOCKED
    assert ROBOT_STATUS_TO_HA["working"] == VacuumActivity.CLEANING
    assert ROBOT_STATUS_TO_HA["pause"] == VacuumActivity.PAUSED
    assert ROBOT_STATUS_TO_HA["homing"] == VacuumActivity.RETURNING
    assert ROBOT_STATUS_TO_HA["error"] == VacuumActivity.ERROR


@pytest.mark.asyncio
async def test_vacuum_entity_start():
    """Test vacuum entity start command using emulated Web API."""
    coordinator = MagicMock()
    coordinator.device_name = "Test Web Cleaner"
    coordinator.device_id = "test-device-id-123"
    coordinator.async_request_refresh = AsyncMock()
    
    # Emulate Web API client
    coordinator.api = MagicMock()
    coordinator.api.async_set_device_control = AsyncMock()

    description = MagicMock()
    property_id = "runState"

    with patch("custom_components.my_lgthinq.vacuum.ThinQStateVacuumEntity.async_call_api") as mock_call_api:
        from custom_components.my_lgthinq.vacuum import ThinQStateVacuumEntity
        entity = ThinQStateVacuumEntity(coordinator, description, property_id)
        
        # Emulate coordinator data
        mock_data = {
            "runState": State.SLEEP,
            "battery": 95
        }
        entity.coordinator.data = mock_data
        
        # Trigger state update
        entity._update_status()
        
        # Perform start
        await entity.async_start()
        
        # Verify call parameters: device_id, command_key, command_value
        coordinator.api.async_set_device_control.assert_called_with(
            coordinator.device_id, "runState", State.WAKE_UP
        )
