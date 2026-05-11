# Bosso Lights for Home Assistant

Control your Bosso smart lights from Home Assistant — turn them on/off, change brightness and color, apply effects, and pick from your saved presets.

## What you get

For each Bosso device in your account, this integration creates three Home Assistant entities:

- **A light entity** — on/off, brightness, RGB color, color temperature, and effects (Solid, Rainbow, etc.)
- **A "Predefined Preset" dropdown** — Bosso's built-in lighting presets
- **A "User Preset" dropdown** — the presets you've saved in the Bosso app

All your changes sync back to the Bosso cloud, so your lights stay in sync across the Bosso mobile app, Google Home, and Home Assistant.

## Setup in 30 seconds

1. Install via HACS
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → + Add Integration**
4. Search for **"Bosso Lights"**
5. Sign in with your Bosso account email and password
6. Your devices appear automatically

## Requirements

- An active Bosso account
- At least one Bosso device set up in your account
- Home Assistant 2024.1 or newer

## Troubleshooting

If the integration doesn't appear after install, restart Home Assistant.
If devices don't show up after login, confirm they appear in your Bosso mobile app first.

For bugs or feature requests, please open an issue on GitHub.
