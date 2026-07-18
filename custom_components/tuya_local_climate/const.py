"""Constants for the Tuya Local Climate integration."""
from homeassistant.components.climate import FAN_HIGH, FAN_LOW, FAN_MEDIUM

DOMAIN = "tuya_local_climate"
PLATFORMS = ["climate", "switch"]

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL_VERSION = "protocol_version"

CONF_DP_POWER = "dp_power"
CONF_DP_TEMP_SET = "dp_temp_set"
CONF_DP_TEMP_CURRENT = "dp_temp_current"
CONF_DP_MODE = "dp_mode"
CONF_DP_FAN_SPEED = "dp_fan_speed"
CONF_DP_SWING = "dp_swing"
CONF_DP_SLEEP = "dp_sleep"

DEFAULT_NAME = "Tuya Local Climate"
DEFAULT_PROTOCOL_VERSION = "3.5"
PROTOCOL_VERSIONS = ["3.1", "3.2", "3.3", "3.4", "3.5"]

DEFAULT_DPS = {
    CONF_DP_POWER: "1",
    CONF_DP_TEMP_SET: "2",
    CONF_DP_TEMP_CURRENT: "3",
    CONF_DP_MODE: "4",
    CONF_DP_FAN_SPEED: "5",
    CONF_DP_SWING: "15",
    CONF_DP_SLEEP: "101",
}

DEFAULT_SCAN_INTERVAL = 30

MODE_COOL = "Cool"
MODE_HEAT = "Heat"
MODE_DRY = "Dry"
MODE_AUTO = "Auto"

HVAC_MODE_TO_DPS_MODE = {
    "cool": MODE_COOL,
    "heat": MODE_HEAT,
    "dry": MODE_DRY,
    "auto": MODE_AUTO,
}
DPS_MODE_TO_HVAC_MODE = {v: k for k, v in HVAC_MODE_TO_DPS_MODE.items()}

FAN_SPEED_LOW = "Low"
FAN_SPEED_MID = "Mid"
FAN_SPEED_HIGH = "High"

FAN_MODE_TO_DPS_SPEED = {
    FAN_LOW: FAN_SPEED_LOW,
    FAN_MEDIUM: FAN_SPEED_MID,
    FAN_HIGH: FAN_SPEED_HIGH,
}
DPS_SPEED_TO_FAN_MODE = {v: k for k, v in FAN_MODE_TO_DPS_SPEED.items()}

SWING_DPS_ON = "ON"
SWING_DPS_OFF = "OFF"
