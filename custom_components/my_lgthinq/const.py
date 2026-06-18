"""Constants for LG ThinQ Custom Integration."""

from datetime import timedelta
from typing import Final

from homeassistant.const import Platform, UnitOfTemperature

# Config flow
DOMAIN = "my_lgthinq"
COMPANY = "LGE"
DEFAULT_COUNTRY: Final = "KR"
THINQ_DEFAULT_NAME: Final = "LG ThinQ Custom"
THINQ_PAT_URL: Final = "https://connect-pat.lgthinq.com"
CLIENT_PREFIX: Final = "home-assistant-custom"
CONF_CONNECT_CLIENT_ID: Final = "connect_client_id"

# Platforms
PLATFORMS = [
    Platform.VACUUM,
    Platform.SENSOR,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
]

# MQTT
MQTT_SUBSCRIPTION_INTERVAL: Final = timedelta(days=1)

# MQTT: Message types
DEVICE_PUSH_MESSAGE: Final = "DEVICE_PUSH"
DEVICE_STATUS_MESSAGE: Final = "DEVICE_STATUS"

# Unit conversion map
DEVICE_UNIT_TO_HA: dict[str, str] = {
    "F": UnitOfTemperature.FAHRENHEIT,
    "C": UnitOfTemperature.CELSIUS,
}
REVERSE_DEVICE_UNIT_TO_HA = {v: k for k, v in DEVICE_UNIT_TO_HA.items()}
