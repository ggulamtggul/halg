import sys
from unittest.mock import MagicMock

# Create mock homeassistant modules to prevent ImportError without installing the whole HA core
class MockModule:
    def __init__(self, name):
        self.__name__ = name
    def __getattr__(self, name):
        # Dynamically return MagicMock or dummy classes
        if name in ("StateVacuumEntity", "VacuumEntity", "SelectEntity", "SwitchEntity", "ButtonEntity", "SensorEntity", "CoordinatorEntity"):
            class DummyEntity:
                def __init__(self, *args, **kwargs):
                    self.coordinator = args[0] if args else MagicMock()
                    self.entity_description = args[1] if len(args) > 1 else MagicMock()
                    self.property_id = args[2] if len(args) > 2 else ""
                    self._attr_native_value = None
                    self._attr_current_option = None
                    self._attr_is_on = False
                    self.hass = MagicMock()
                async def async_call_api(self, target, on_fail_method=None):
                    try:
                        await target
                    except Exception as e:
                        if on_fail_method:
                            on_fail_method()
                        raise e
                def async_write_ha_state(self):
                    pass
                @property
                def native_value(self):
                    return self._attr_native_value
                @property
                def current_option(self):
                    return self._attr_current_option
                @property
                def is_on(self):
                    return self._attr_is_on
                @property
                def state(self):
                    return getattr(self, "_attr_state", "unknown")
                @property
                def battery_level(self):
                    return getattr(self, "_attr_battery_level", None)
                def __class_getitem__(cls, item):
                    return cls
            return DummyEntity
        
        if name == "VacuumActivity":
            class VacuumActivity:
                DOCKED = "docked"
                CLEANING = "cleaning"
                PAUSED = "paused"
                RETURNING = "returning"
                ERROR = "error"
                IDLE = "idle"
            return VacuumActivity
            
        if name == "VacuumEntityFeature":
            class VacuumEntityFeature:
                STATE = 1
                BATTERY = 2
                START = 4
                PAUSE = 8
                RETURN_HOME = 16
            return VacuumEntityFeature

        if name == "SensorDeviceClass":
            class SensorDeviceClass:
                BATTERY = "battery"
                ENUM = "enum"
                MEASUREMENT = "measurement"
            return SensorDeviceClass
            
        if name == "SensorStateClass":
            class SensorStateClass:
                MEASUREMENT = "measurement"
            return SensorStateClass

        if name == "PERCENTAGE":
            return "%"

        if name == "Platform":
            class Platform:
                VACUUM = "vacuum"
                SENSOR = "sensor"
                SELECT = "select"
                SWITCH = "switch"
                BUTTON = "button"
            return Platform

        # Return a generic magic mock for any other attributes
        mock_attr = MagicMock()
        mock_attr.__name__ = f"{self.__name__}.{name}"
        return mock_attr

# Register dummy modules in sys.modules
mock_modules = [
    "homeassistant",
    "homeassistant.const",
    "homeassistant.core",
    "homeassistant.exceptions",
    "homeassistant.helpers",
    "homeassistant.helpers.entity",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.config_entries",
    "homeassistant.util",
    "homeassistant.util.dt",
    "homeassistant.components",
    "homeassistant.components.vacuum",
    "homeassistant.components.select",
    "homeassistant.components.switch",
    "homeassistant.components.button",
    "homeassistant.components.sensor",
]

for mod_name in mock_modules:
    sys.modules[mod_name] = MockModule(mod_name)
