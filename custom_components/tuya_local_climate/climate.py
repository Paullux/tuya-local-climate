"""Climate platform for Tuya Local Climate."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    SWING_OFF,
    SWING_ON,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    CONF_DP_FAN_SPEED,
    CONF_DP_MODE,
    CONF_DP_POWER,
    CONF_DP_SWING,
    CONF_DP_TEMP_CURRENT,
    CONF_DP_TEMP_SET,
    DEFAULT_DPS,
    DOMAIN,
    DPS_MODE_TO_HVAC_MODE,
    DPS_SPEED_TO_FAN_MODE,
    FAN_MODE_TO_DPS_SPEED,
    HVAC_MODE_TO_DPS_MODE,
    SWING_DPS_OFF,
    SWING_DPS_ON,
)
from .coordinator import TuyaLocalClimateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the climate entity from a config entry."""
    coordinator: TuyaLocalClimateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TuyaLocalClimateEntity(coordinator, entry)])


class TuyaLocalClimateEntity(CoordinatorEntity[TuyaLocalClimateCoordinator], ClimateEntity):
    """Representation of a Tuya local climate device."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL,
        HVACMode.HEAT,
        HVACMode.DRY,
        HVACMode.AUTO,
    ]
    _attr_fan_modes = [FAN_LOW, FAN_MEDIUM, FAN_HIGH]
    _attr_swing_modes = [SWING_ON, SWING_OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_target_temperature_step = 1

    def __init__(self, coordinator: TuyaLocalClimateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._dps = {**DEFAULT_DPS, **entry.options}
        self._attr_unique_id = entry.data[CONF_DEVICE_ID]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])},
            name=entry.title,
            manufacturer="Tuya",
            model="Local Climate",
        )

    @property
    def current_temperature(self) -> float | None:
        value = self.coordinator.data.get(self._dps[CONF_DP_TEMP_CURRENT])
        return float(value) if value is not None else None

    @property
    def target_temperature(self) -> float | None:
        value = self.coordinator.data.get(self._dps[CONF_DP_TEMP_SET])
        return float(value) if value is not None else None

    @property
    def hvac_mode(self) -> HVACMode:
        if not self.coordinator.data.get(self._dps[CONF_DP_POWER]):
            return HVACMode.OFF
        mode = self.coordinator.data.get(self._dps[CONF_DP_MODE])
        return HVACMode(DPS_MODE_TO_HVAC_MODE.get(mode, "cool"))

    @property
    def fan_mode(self) -> str | None:
        speed = self.coordinator.data.get(self._dps[CONF_DP_FAN_SPEED])
        return DPS_SPEED_TO_FAN_MODE.get(speed)

    @property
    def swing_mode(self) -> str | None:
        swing = self.coordinator.data.get(self._dps[CONF_DP_SWING])
        return SWING_ON if swing == SWING_DPS_ON else SWING_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self.coordinator.async_set_dp(self._dps[CONF_DP_TEMP_SET], int(temperature))

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_dp(self._dps[CONF_DP_POWER], False)
            return
        dps_mode = HVAC_MODE_TO_DPS_MODE[hvac_mode]
        if self.hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_dps(
                {self._dps[CONF_DP_POWER]: True, self._dps[CONF_DP_MODE]: dps_mode}
            )
        else:
            await self.coordinator.async_set_dp(self._dps[CONF_DP_MODE], dps_mode)

    async def async_turn_on(self) -> None:
        await self.coordinator.async_set_dp(self._dps[CONF_DP_POWER], True)

    async def async_turn_off(self) -> None:
        await self.coordinator.async_set_dp(self._dps[CONF_DP_POWER], False)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await self.coordinator.async_set_dp(
            self._dps[CONF_DP_FAN_SPEED], FAN_MODE_TO_DPS_SPEED[fan_mode]
        )

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        value = SWING_DPS_ON if swing_mode == SWING_ON else SWING_DPS_OFF
        await self.coordinator.async_set_dp(self._dps[CONF_DP_SWING], value)
