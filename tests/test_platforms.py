"""Tests for LG ThinQ Custom platforms (Web API Emulated)."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from custom_components.my_lgthinq.select import ThinQSelectEntity
from custom_components.my_lgthinq.switch import ThinQSwitchEntity
from custom_components.my_lgthinq.button import ThinQButtonEntity
from custom_components.my_lgthinq.sensor import ThinQSensorEntity


@pytest.mark.asyncio
async def test_select_entity():
    """Test select entity option change."""
    coordinator = MagicMock()
    coordinator.device_name = "Test Vacuum"
    coordinator.device_id = "test-id"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.api = MagicMock()
    coordinator.api.async_set_device_control = AsyncMock()

    description = MagicMock()
    description.key = "cleaningMode"
    description.options = ["suction_mop", "suction_only", "mop_only"]

    entity = ThinQSelectEntity(coordinator, description, "cleaningMode")
    entity.coordinator.data = {"cleaningMode": "suction_mop"}

    entity._update_status()
    assert entity.current_option == "suction_mop"

    await entity.async_select_option("suction_only")
    coordinator.api.async_set_device_control.assert_called_with(
        "test-id", "cleaningMode", "suction_only"
    )


@pytest.mark.asyncio
async def test_switch_entity():
    """Test switch entity turn on/off."""
    coordinator = MagicMock()
    coordinator.device_name = "Test Vacuum"
    coordinator.device_id = "test-id"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.api = MagicMock()
    coordinator.api.async_set_device_control = AsyncMock()

    description = MagicMock()
    description.key = "aiObstacleAvoidance"

    entity = ThinQSwitchEntity(coordinator, description, "aiObstacleAvoidance")
    entity.coordinator.data = {"aiObstacleAvoidance": "off"}

    entity._update_status()
    assert not entity.is_on

    await entity.async_turn_on()
    coordinator.api.async_set_device_control.assert_called_with(
        "test-id", "aiObstacleAvoidance", "on"
    )

    await entity.async_turn_off()
    coordinator.api.async_set_device_control.assert_called_with(
        "test-id", "aiObstacleAvoidance", "off"
    )


@pytest.mark.asyncio
async def test_button_entity():
    """Test button entity press."""
    coordinator = MagicMock()
    coordinator.device_name = "Test Vacuum"
    coordinator.device_id = "test-id"
    coordinator.async_request_refresh = AsyncMock()
    coordinator.api = MagicMock()
    coordinator.api.async_set_device_control = AsyncMock()

    description = MagicMock()
    description.key = "emptyDustbin"

    entity = ThinQButtonEntity(coordinator, description, "emptyDustbin")

    await entity.async_press()
    coordinator.api.async_set_device_control.assert_called_with(
        "test-id", "emptyDustbin", "start"
    )


def test_sensor_consumable_entity():
    """Test consumable life sensor update."""
    coordinator = MagicMock()
    coordinator.device_name = "Test Vacuum"
    coordinator.device_id = "test-id"

    description = MagicMock()
    description.key = "mainBrushLife"

    entity = ThinQSensorEntity(coordinator, description, "mainBrushLife")
    entity.coordinator.data = {"mainBrushLife": 85}

    entity._update_status()
    assert entity.native_value == 85
