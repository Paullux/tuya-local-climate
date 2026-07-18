"""Config flow for the Tuya Local Climate integration."""
from __future__ import annotations

import logging
from typing import Any

import tinytuya
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_ID,
    CONF_DP_FAN_SPEED,
    CONF_DP_MODE,
    CONF_DP_POWER,
    CONF_DP_SLEEP,
    CONF_DP_SWING,
    CONF_DP_TEMP_CURRENT,
    CONF_DP_TEMP_SET,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL_VERSION,
    DEFAULT_DPS,
    DEFAULT_NAME,
    DEFAULT_PROTOCOL_VERSION,
    DOMAIN,
    PROTOCOL_VERSIONS,
)

_LOGGER = logging.getLogger(__name__)

DPS_FIELDS = [
    CONF_DP_POWER,
    CONF_DP_TEMP_SET,
    CONF_DP_TEMP_CURRENT,
    CONF_DP_MODE,
    CONF_DP_FAN_SPEED,
    CONF_DP_SWING,
    CONF_DP_SLEEP,
]


async def _validate_connection(
    hass, host: str, device_id: str, local_key: str, protocol_version: str
) -> str | None:
    """Try to connect to the device. Returns an error string or None on success."""

    def _connect() -> dict[str, Any]:
        device = tinytuya.Device(device_id, host, local_key, version=float(protocol_version))
        device.set_socketTimeout(5)
        return device.status()

    try:
        result = await hass.async_add_executor_job(_connect)
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Unexpected error connecting to Tuya device")
        return "unknown"

    if not result or "dps" not in result:
        return "cannot_connect"
    return None


class TuyaLocalClimateConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Local Climate."""

    VERSION = 1

    def __init__(self) -> None:
        self._user_input: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            error = await _validate_connection(
                self.hass,
                user_input[CONF_HOST],
                user_input[CONF_DEVICE_ID],
                user_input[CONF_LOCAL_KEY],
                user_input[CONF_PROTOCOL_VERSION],
            )
            if error is None:
                self._user_input = user_input
                return await self.async_step_dps()
            errors["base"] = error

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_LOCAL_KEY): str,
                vol.Required(
                    CONF_PROTOCOL_VERSION, default=DEFAULT_PROTOCOL_VERSION
                ): vol.In(PROTOCOL_VERSIONS),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_dps(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            data = {**self._user_input}
            await self.async_set_unique_id(data[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()
            title = data.pop(CONF_NAME)
            return self.async_create_entry(title=title, data=data, options=user_input)

        schema = vol.Schema(
            {vol.Required(field, default=DEFAULT_DPS[field]): str for field in DPS_FIELDS}
        )
        return self.async_show_form(step_id="dps", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TuyaLocalClimateOptionsFlow(config_entry)


class TuyaLocalClimateOptionsFlow(OptionsFlow):
    """Handle options (DPS mapping) for an existing entry."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    field, default=current.get(field, DEFAULT_DPS[field])
                ): str
                for field in DPS_FIELDS
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
