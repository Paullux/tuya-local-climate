# Tuya Local Climate

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/Paullux/tuya-local-climate)](https://github.com/Paullux/tuya-local-climate/releases)
[![License](https://img.shields.io/github/license/Paullux/tuya-local-climate)](LICENSE.md)

![Logo](https://raw.githubusercontent.com/Paullux/tuya-local-climate/main/logo.png)

A Home Assistant custom integration for controlling Tuya-based air conditioners **locally**, over your LAN, using [tinytuya](https://github.com/jasonacox/tinytuya). No Tuya/Smart Life cloud account is required at runtime — only the device's local key, which you extract once.

Built from a working setup for a Costway portable A/C, generalized so it works with any Tuya climate device that exposes similar datapoints (DPS). The DPS mapping is fully configurable from the UI, so other device models can be supported without touching the code.

## Features

- Native Home Assistant `climate` entity: `off` / `cool` / `heat` / `dry` / `auto`, fan speed (`low` / `medium` / `high`), swing (`on` / `off`), target and current temperature
- `switch` entities for Sleep mode and Swing (in addition to swing being controllable from the climate entity)
- 100% local polling via `tinytuya` (default: every 30 seconds) — no cloud dependency
- Configurable via the UI (`config_flow`) — IP, device ID, local key, protocol version, and DPS mapping
- DPS mapping can be changed later from the integration's **Options**

## Requirements

- Home Assistant 2024.2 or newer
- Python 3.11+
- Your device's local key (see below)

## Installation

### HACS (recommended)

1. In HACS, go to **Integrations** → menu (⋮) → **Custom repositories**.
2. Add `https://github.com/Paullux/tuya-local-climate` with category **Integration**.
3. Search for "Tuya Local Climate" in HACS and install it.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/tuya_local_climate` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.

## Getting your device ID and local key

You need three pieces of information for each device:

- **IP address** — assign a static/reserved IP on your router so it doesn't change.
- **Device ID**
- **Local key**

The reliable way to get these is the [tinytuya wizard](https://github.com/jasonacox/tinytuya#setup-wizard-getting-local-keys). It requires a **free** Tuya IoT developer account, but only as a one-time step to read the keys — the account is not needed afterwards and Home Assistant never talks to the cloud.

### Step 1 — Create a Tuya IoT Cloud project

1. Go to [https://iot.tuya.com](https://iot.tuya.com) and sign up / log in (a normal email account is fine).
2. Go to **Cloud → Development → Create Cloud Project**.
   - Any name, any industry (e.g. "Smart Home").
   - Data Center: pick the region matching your Smart Life / Tuya Smart app account (e.g. "Central Europe", "Western America"...). If unsure, check the app's account settings — it lists your region.
3. When prompted to select APIs/services to subscribe to, add at least: **IoT Core**, **Authorization**, and **Smart Home Scene Linkage**. These have a free trial tier which is enough for this use case.
4. Once created, open the project and note the **Access ID/Client ID** and **Access Secret/Client Secret** shown on the project's **Overview** tab — you'll need them for the wizard.

### Step 2 — Link your app account to the project

Devices only become visible to the API once your Smart Life/Tuya Smart app account is linked to the cloud project:

1. In your project, go to the **Devices** tab → **Link Tuya App Account** (sometimes under **Link App Account** or a similar name depending on the console version).
2. Click **Add App Account**, then scan the QR code with the **Smart Life** or **Tuya Smart** app (the same app you use to control the device) — usually via the app's scan feature or a "Scan QR code" option under your profile.
3. Once linked, your registered devices should appear in the **Devices** tab.

### Step 3 — Run the tinytuya wizard

```bash
pip install tinytuya
python -m tinytuya wizard
```

- Paste the **Access ID** and **Access Secret** from Step 1 when asked.
- Choose your region/data center (matches what you picked when creating the project — e.g. `eu`, `us`, `cn`, `in`).
- When asked for your Tuya app account details, you can normally just press Enter/skip — the linked app account from Step 2 is enough for the wizard to pull devices.

The wizard prints and saves a `devices.json` file listing every linked device's `id` (device ID), `key` (local key), and often its `ip` and `name`. Find your climate device in that list.

### Step 4 — Confirm the local IP

If the wizard didn't report a working IP (or your device's IP changes), run a local network scan to find it and double-check the key still works:

```bash
python -m tinytuya scan
```

This broadcasts on your LAN and lists responding Tuya devices with their IP, device ID, and protocol version. Use this IP in the integration setup, and set a DHCP reservation for it on your router so it doesn't change later.

### Common pitfalls

- **"Invalid client_id" / auth errors in the wizard**: double-check you copied the Access ID/Secret without extra spaces, and picked the correct data center/region.
- **No devices listed after linking**: the app account link can take a minute to sync — reopen the **Devices** tab in the Tuya IoT console, or unlink and re-link the app account.
- **Local key stops working**: the local key changes if you remove and re-add the device in the Smart Life/Tuya Smart app, or reset it to factory settings. Re-run the wizard to get the new key.
- **Device not responding locally despite a correct key**: try the other protocol versions (`3.1`–`3.5`) in this integration's setup — older/cheaper Tuya modules often use `3.3` instead of `3.5`.

## Configuration

Configuration is done entirely from the UI:

1. **Settings → Devices & Services → Add Integration → Tuya Local Climate**.
2. Enter a name, the device's IP address, device ID, local key, and protocol version (default `3.5`; try `3.3` or `3.4` if `3.5` doesn't connect).
3. On the next screen, confirm or adjust the DPS mapping (defaults match common Tuya A/C units — see table below).

To change the DPS mapping later, open the integration entry and click **Configure**.

## DPS mapping

These are the default datapoint IDs, based on a Costway portable air conditioner. Many Tuya A/C units share this layout, but check your device's actual datapoints (e.g. via the tinytuya wizard or `Device.status()`) if entities don't behave as expected.

| DPS | Type | Purpose | Values |
|-----|------|---------|--------|
| `1`   | bool | Power on/off | `true` / `false` |
| `2`   | int  | Target temperature (°C) | e.g. `21` |
| `3`   | int  | Current temperature (°C, read-only) | e.g. `24` |
| `4`   | str  | Mode | `Cool`, `Heat`, `Dry`, `Auto` |
| `5`   | str  | Fan speed | `Low`, `Mid`, `High` |
| `15`  | str  | Swing | `ON`, `OFF` |
| `101` | bool | Sleep mode | `true` / `false` |

## Example: raw tinytuya reference

This is the equivalent raw control this integration wraps, for reference/debugging:

```python
import tinytuya

d = tinytuya.Device(DEVICE_ID, IP, LOCAL_KEY, version=3.5)

d.set_value(4, "Cool")   # mode: Cool / Heat / Dry / Auto
d.set_value(1, True)     # power on
d.set_value(2, 21)       # target temperature
d.set_value(5, "Low")    # fan speed: Low / Mid / High
d.set_value(15, "ON")    # swing
d.set_value(101, True)   # sleep mode

status = d.status()
# {'dps': {'1': True, '2': 21, '3': 24, '4': 'Cool', '5': 'High', '15': 'ON', '101': False}}
```

## Troubleshooting

- **Cannot connect during setup**: double-check the IP, device ID and local key; try a different protocol version (`3.1`–`3.5`).
- **Entities show wrong/no values**: your device's DPS layout differs from the defaults — inspect `Device.status()` output and update the mapping in the integration's Options.
- **State lags behind the physical remote**: this integration polls every 30 seconds; changes made with a physical remote will appear on the next poll.

## Contributing

Issues and pull requests are welcome, especially DPS mappings for other Tuya climate device models.

## License

[MIT](LICENSE.md)
