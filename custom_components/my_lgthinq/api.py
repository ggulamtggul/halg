"""LG ThinQ Web Dashboard API Client.

This client emulates the web app behavior of https://my.lgthinq.com/
to authenticate with LG Account and interact with the ThinQ Web backend API.
"""

import logging
from typing import Any
import aiohttp

_LOGGER = logging.getLogger(__name__)

# Emulated host endpoints for ThinQ Web portal
LG_ACCOUNT_URL = "https://kr.m.lgaccount.com/login"
THINQ_WEB_API_HOST = "https://kic-service.lgthinq.com:46030"


class ThinQWebAPIException(Exception):
    """Exception class for ThinQ Web API."""

    def __init__(self, message: str, code: str = "unknown_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ThinQWebAPI:
    """API Client that mimics the browser session of ThinQ Web portal."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        refresh_token: str | None = None,
        country_code: str = "KR",
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.country_code = country_code
        self._simulated_states: dict[str, dict[str, Any]] = {}

    async def async_login(self) -> bool:
        """Bypass login and verify access token validity."""
        _LOGGER.debug("Bypassing login, using direct access token verification")
        if not self.access_token:
            raise ThinQWebAPIException("Access token is missing", "invalid_credentials")
        return True

    async def async_refresh_token(self) -> bool:
        """Attempt to refresh the access token using the refresh token."""
        if not self.refresh_token:
            _LOGGER.debug("No refresh token available to refresh session")
            return False
        
        url = f"{THINQ_WEB_API_HOST}/v1/service/auth/token/refresh"
        payload = {"refresh_token": self.refresh_token}
        _LOGGER.debug("Attempting to refresh Access Token using Refresh Token")
        
        try:
            async with self._session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    res_json = await response.json()
                    new_access = res_json.get("access_token") or res_json.get("accessToken")
                    new_refresh = res_json.get("refresh_token") or res_json.get("refreshToken")
                    if new_access:
                        self.access_token = new_access
                        _LOGGER.info("Access token successfully refreshed")
                    if new_refresh:
                        self.refresh_token = new_refresh
                    return True
                else:
                    text = await response.text()
                    _LOGGER.warning("Token refresh API rejected request: %s", text)
        except Exception as err:
            _LOGGER.error("Network error during token refresh: %s", err)
        return False

    def _get_headers(self) -> dict[str, str]:
        """Get standard headers with authorization."""
        if not self.access_token:
            raise ThinQWebAPIException("Client is not authenticated", "unauthorized")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-ThinQ-Country-Code": self.country_code,
        }

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Retrieve the list of registered appliances."""
        if not self.access_token:
            await self.async_login()
            
        # If mock token is explicitly provided (for testing/dev), return mock device
        if self.access_token == "mock-token":
            return [
                {
                    "deviceId": "mock-robot-vacuum-id",
                    "alias": "로봇청소기",
                    "deviceType": "ROBOT_CLEANER",
                    "modelName": "B-95AW.CKOR",
                }
            ]
            
        url = f"{THINQ_WEB_API_HOST}/v1/service/devices"
        _LOGGER.debug("Fetching device list from: %s", url)
        
        try:
            async with self._session.get(url, headers=self._get_headers(), timeout=10) as response:
                if response.status == 401:
                    # Token expired, try refreshing
                    if await self.async_refresh_token():
                        async with self._session.get(url, headers=self._get_headers(), timeout=10) as retry_resp:
                            if retry_resp.status != 200:
                                text = await retry_resp.text()
                                raise ThinQWebAPIException(f"Session expired and could not refresh: {text}", "session_expired")
                            return await retry_resp.json()
                    else:
                        raise ThinQWebAPIException("Session expired and token refresh failed", "session_expired")
                        
                if response.status != 200:
                    text = await response.text()
                    raise ThinQWebAPIException(f"Failed to fetch devices: Status {response.status}, Response: {text}", "api_error")
                    
                return await response.json()
                
        except aiohttp.ClientError as err:
            raise ThinQWebAPIException(f"Connection failed to fetch devices: {err}", "connection_error") from err

    async def async_get_device_status(self, device_id: str) -> dict[str, Any]:
        """Fetch status detail of a specific device."""
        if not self.access_token:
            await self.async_login()
            
        # Handle mock/simulation explicitly
        if self.access_token == "mock-token":
            if device_id not in self._simulated_states:
                self._simulated_states[device_id] = {
                    "runState": "sleep",
                    "battery": 95,
                    "robotCleanerJobMode": "cleaning",
                    "cleaningMode": "suction_mop",
                    "suctionStrength": "strong",
                    "waterSupply": "medium",
                    "carpetMode": "smart_carpet",
                    "volume": "medium",
                    "aiObstacleAvoidance": "on",
                    "autoResume": "on",
                    "childLock": "off",
                    "autoEmptyDustbin": "on",
                    "autoMopWash": "on",
                    "autoMopDry": "on",
                    "dndMode": "off",
                    "mainBrushLife": 85,
                    "sideBrushLife": 90,
                    "filterLife": 75,
                    "mopLife": 95,
                    "dustBagLife": 40,
                    "modelName": "B-95AW.CKOR",
                    "serialNumber": "408SSCS09715",
                }
            return self._simulated_states[device_id]

        url = f"{THINQ_WEB_API_HOST}/v1/service/devices/{device_id}/status"
        _LOGGER.debug("Fetching status for device %s", device_id)
        
        try:
            async with self._session.get(url, headers=self._get_headers(), timeout=10) as response:
                if response.status == 401:
                    if await self.async_refresh_token():
                        async with self._session.get(url, headers=self._get_headers(), timeout=10) as retry_resp:
                            if retry_resp.status != 200:
                                text = await retry_resp.text()
                                raise ThinQWebAPIException(f"Session expired: {text}", "session_expired")
                            return await retry_resp.json()
                    else:
                        raise ThinQWebAPIException("Session expired and refresh failed", "session_expired")
                        
                if response.status != 200:
                    text = await response.text()
                    raise ThinQWebAPIException(f"Failed to fetch status: Status {response.status}, Response: {text}", "api_error")
                    
                return await response.json()
                
        except aiohttp.ClientError as err:
            raise ThinQWebAPIException(f"Connection failed to fetch status: {err}", "connection_error") from err

    async def async_set_device_control(
        self, device_id: str, command: str, value: str
    ) -> bool:
        """Send a control command to the device."""
        if not self.access_token:
            await self.async_login()

        # Handle mock/simulation explicitly
        if self.access_token == "mock-token":
            if device_id in self._simulated_states:
                self._simulated_states[device_id][command] = value
            else:
                self._simulated_states[device_id] = {command: value}
            _LOGGER.info("Mock control command success: %s -> %s", command, value)
            return True
            
        url = f"{THINQ_WEB_API_HOST}/v1/service/devices/{device_id}/control"
        payload = {
            "command": command,
            "value": value,
        }
        _LOGGER.debug("Sending control to %s: %s -> %s", device_id, command, value)
        
        try:
            async with self._session.post(
                url, json=payload, headers=self._get_headers(), timeout=10
            ) as response:
                if response.status == 401:
                    if await self.async_refresh_token():
                        async with self._session.post(
                            url, json=payload, headers=self._get_headers(), timeout=10
                        ) as retry_resp:
                            return retry_resp.status == 200
                    return False
                        
                if response.status != 200:
                    text = await response.text()
                    _LOGGER.warning("Control command failed with status %s: %s", response.status, text)
                    return False
                    
                return True
                
        except aiohttp.ClientError as err:
            raise ThinQWebAPIException(f"Connection failed to control device: {err}", "connection_error") from err
