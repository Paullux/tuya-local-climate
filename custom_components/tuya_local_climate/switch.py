"""Switch platform for Tuya Local Climate (sleep mode and swing)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    CONF_DP_SLEEP,
    CONF_DP_SWING,
    DEFAULT_DPS,
    DOMAIN,
    SWING_DPS_OFF,
    SWING_DPS_ON,
)
from .coordinator import TuyaLocalClimateCoordinator

SLEEP_DESCRIPTION = SwitchEntityDescription(
    key="sleep",
    translation_key="sleep",
    name="Sleep Mode",
    icon="mdi:power-sleep",
)
SWING_DESCRIPTION = SwitchEntityDescription(
    key="swing",
    translation_key="swing",
    name="Swing",
    icon="mdi:arrow-oscillating",
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sleep and swing switches from a config entry."""
    coordinator: TuyaLocalClimateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TuyaLocalSleepSwitch(coordinator, entry),
            TuyaLocalSwingSwitch(coordinator, entry),
        ]
    )


class TuyaLocalSwitchBase(CoordinatorEntity[TuyaLocalClimateCoordinator], SwitchEntity):
    """Base switch entity backed by a single Tuya datapoint."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TuyaLocalClimateCoordinator,
        entry: ConfigEntry,
        description: SwitchEntityDescription,
        dp_key: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._dps = {**DEFAULT_DPS, **entry.options}
        self._dp = self._dps[dp_key]
        self._attr_unique_id = f"{entry.data[CONF_DEVICE_ID]}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
        )


class TuyaLocalSleepSwitch(TuyaLocalSwitchBase):
    """Switch controlling sleep mode."""

    def __init__(self, coordinator: TuyaLocalClimateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, SLEEP_DESCRIPTION, CONF_DP_SLEEP)

    @property
    def is_on(self) -> bool | None:
        return bool(self.coordinator.data.get(self._dp))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(self._dp, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(self._dp, False)


class TuyaLocalSwingSwitch(TuyaLocalSwitchBase):
    """Switch controlling swing (mirrors the climate entity's swing mode)."""

    def __init__(self, coordinator: TuyaLocalClimateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, SWING_DESCRIPTION, CONF_DP_SWING)

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._dp) == SWING_DPS_ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(self._dp, SWING_DPS_ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_dp(self._dp, SWING_DPS_OFF)
