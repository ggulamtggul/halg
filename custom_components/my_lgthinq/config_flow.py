"""Config flow for LG ThinQ Custom."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_COUNTRY
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig

from .api import ThinQWebAPI, ThinQWebAPIException
from .const import DEFAULT_COUNTRY, DOMAIN, THINQ_DEFAULT_NAME, THINQ_PAT_URL

SUPPORTED_COUNTRIES = ["KR", "US", "CA", "EU", "AU"]
THINQ_ERRORS = {
    "invalid_credentials": "invalid_credentials",
    "connection_error": "cannot_connect",
    "auth_failed": "auth_failed",
}

_LOGGER = logging.getLogger(__name__)


class ThinQFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ThinQ Web API."""

    VERSION = 1

    def _get_default_country_code(self) -> str:
        """Get the default country code based on config."""
        country = self.hass.config.country
        if country is not None and country in SUPPORTED_COUNTRIES:
            return country

        return DEFAULT_COUNTRY

    async def _validate_and_create_entry(
        self, username: str, password: str, country_code: str
    ) -> ConfigFlowResult:
        """Validate login and create entry."""
        api = ThinQWebAPI(
            session=async_get_clientsession(self.hass),
            username=username,
            password=password,
            country_code=country_code,
        )
        
        # Verify credentials by logging in
        await api.async_login()

        # If verification succeeds, create the config entry.
        return self.async_create_entry(
            title=f"{THINQ_DEFAULT_NAME} ({username})",
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
                CONF_COUNTRY: country_code,
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]
            country_code = user_input[CONF_COUNTRY]

            # Unique ID by email
            await self.async_set_unique_id(username)
            self._abort_if_unique_id_configured()

            try:
                return await self._validate_and_create_entry(username, password, country_code)
            except ThinQWebAPIException as exc:
                errors["base"] = THINQ_ERRORS.get(exc.code, "auth_failed")
                _LOGGER.error("Failed to validate credentials: %s", exc)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                    vol.Required(
                        CONF_COUNTRY, default=self._get_default_country_code()
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=SUPPORTED_COUNTRIES,
                            translation_key="country",
                        )
                    ),
                }
            ),
            description_placeholders={"pat_url": THINQ_PAT_URL},
            errors=errors,
        )
