"""DataUpdateCoordinator for Tuya Local Climate."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import tinytuya
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TuyaLocalClimateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls a local Tuya climate device."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        host: str,
        device_id: str,
        local_key: str,
        protocol_version: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.entry = entry
        self.device = tinytuya.Device(
            device_id, host, local_key, version=float(protocol_version)
        )
        # Reconnect fresh on every call instead of keeping a long-lived socket:
        # a persistent socket shared between the poll loop and command calls
        # (each dispatched to a different executor thread) can end up in a
        # broken state after concurrent access, causing spurious "unavailable".
        self.device.set_socketPersistent(False)
        self._device_lock = asyncio.Lock()

    async def _async_update_data(self) -> dict[str, Any]:
        async with self._device_lock:
            result = await self.hass.async_add_executor_job(self.device.status)
        if not result:
            raise UpdateFailed("No response from device")
        if "Error" in result:
            raise UpdateFailed(result.get("Error", "Unknown error"))
        if "dps" not in result:
            raise UpdateFailed(f"Invalid response from device: {result}")
        return result["dps"]

    async def async_set_dp(self, dp: str, value: Any) -> None:
        """Set a single datapoint and refresh state."""
        async with self._device_lock:
            await self.hass.async_add_executor_job(self.device.set_value, int(dp), value)
        if self.data is not None:
            self.data[dp] = value
            self.async_set_updated_data(self.data)

    async def async_set_dps(self, values: dict[str, Any]) -> None:
        """Set multiple datapoints at once and refresh state."""
        payload = {int(dp): value for dp, value in values.items()}
        async with self._device_lock:
            await self.hass.async_add_executor_job(self.device.set_multiple_values, payload)
        if self.data is not None:
            self.data.update(values)
            self.async_set_updated_data(self.data)
