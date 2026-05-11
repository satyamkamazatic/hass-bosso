"""Polling-based data coordinator for Bosso devices."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BossoApiClient, BossoApiError, BossoAuthError
from .const import (
    DOMAIN,
    EFFECT_ID_SOLID,
    EFFECT_NAME_SOLID,
    PRESET_NONE_LABEL,
    SCAN_INTERVAL_SECONDS,
)
from .presets import build_preset_apply_payload, calc_led_count

_LOGGER = logging.getLogger(__name__)


class BossoCoordinator(DataUpdateCoordinator[dict[int, dict[str, Any]]]):
    """Fetches device list periodically; entities read state from this dict.

    Also caches the effects catalog (loaded once on setup) so the light
    entity can map effect names <-> IDs.
    """

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: BossoApiClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.api = api
        self.entry = entry

        # Effects cache: name -> id and id -> name mappings
        # Always includes "Solid" (id 0) as the default no-effect option.
        self.effect_name_to_id: dict[str, int] = {EFFECT_NAME_SOLID: EFFECT_ID_SOLID}
        self.effect_id_to_name: dict[int, str] = {EFFECT_ID_SOLID: EFFECT_NAME_SOLID}

        # Preset name->id maps. Loaded once on setup so the dropdown has
        # options. The actual preset *details* are fetched fresh every
        # time a preset is applied (per user requirement).
        self.predefined_preset_name_to_id: dict[str, int] = {}
        self.predefined_preset_id_to_name: dict[int, str] = {}
        self.user_preset_name_to_id: dict[str, int] = {}
        self.user_preset_id_to_name: dict[int, str] = {}

        # Optimistic in-memory state: remember the last preset applied
        # via this integration so the select dropdown can display the
        # name even if the backend's `current_preset` field doesn't
        # update reliably after apply-to-home.
        # Maps device_id -> preset_id.
        self._last_applied_preset: dict[int, int] = {}

    async def async_load_effects(self) -> None:
        """Load the effects catalog once at integration startup.

        Failure to load effects is non-fatal — we just won't expose effects
        on the lights, but everything else still works.
        """
        try:
            effects = await self.api.async_list_effects()
        except BossoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except BossoApiError as err:
            _LOGGER.warning(
                "Could not load Bosso effects (%s) — continuing without effects", err
            )
            return

        for effect in effects:
            effect_id = effect.get("id")
            effect_name = effect.get("name")
            if effect_id is None or not effect_name:
                continue
            # Skip "Solid" duplicates from backend (we already added id 0)
            if effect_id == EFFECT_ID_SOLID:
                continue
            self.effect_name_to_id[effect_name] = effect_id
            self.effect_id_to_name[effect_id] = effect_name

        _LOGGER.info("Loaded %d Bosso effects", len(self.effect_name_to_id))

    @property
    def effect_list(self) -> list[str]:
        """Return effect names in a stable order (Solid first)."""
        names = [EFFECT_NAME_SOLID]
        for name in sorted(self.effect_name_to_id):
            if name != EFFECT_NAME_SOLID:
                names.append(name)
        return names

    async def async_load_presets(self) -> None:
        """Load both preset catalogs (predefined + user-defined) at startup.

        Called once during setup. The dropdown options come from this cache.
        Failures are logged and non-fatal — the dropdowns just appear empty.
        """
        try:
            predefined = await self.api.async_list_presets(predefined=True)
            for preset in predefined:
                preset_id = preset.get("id")
                name = preset.get("n")
                if preset_id is None or not name:
                    continue
                # Resolve duplicate names by appending the id
                key = name
                if key in self.predefined_preset_name_to_id:
                    key = f"{name} ({preset_id})"
                self.predefined_preset_name_to_id[key] = preset_id
                self.predefined_preset_id_to_name[preset_id] = key
            _LOGGER.info(
                "Loaded %d predefined Bosso presets",
                len(self.predefined_preset_name_to_id),
            )
        except BossoApiError as err:
            _LOGGER.warning("Could not load predefined presets: %s", err)

        try:
            user = await self.api.async_list_presets(predefined=False)
            for preset in user:
                preset_id = preset.get("id")
                name = preset.get("n")
                if preset_id is None or not name:
                    continue
                key = name
                if key in self.user_preset_name_to_id:
                    key = f"{name} ({preset_id})"
                self.user_preset_name_to_id[key] = preset_id
                self.user_preset_id_to_name[preset_id] = key
            _LOGGER.info(
                "Loaded %d user-defined Bosso presets",
                len(self.user_preset_name_to_id),
            )
        except BossoApiError as err:
            _LOGGER.warning("Could not load user presets: %s", err)

    @property
    def predefined_preset_options(self) -> list[str]:
        """Return predefined preset names sorted, with 'None' first."""
        return [PRESET_NONE_LABEL] + sorted(self.predefined_preset_name_to_id)

    @property
    def user_preset_options(self) -> list[str]:
        """Return user preset names sorted, with 'None' first."""
        return [PRESET_NONE_LABEL] + sorted(self.user_preset_name_to_id)

    async def async_apply_preset(
        self, device_id: int, preset_id: int
    ) -> None:
        """Full flow: fetch preset details + device config, then apply.

        Per the requirement, this fetches fresh data every time:
          1. GET /preset/{id}/  -> preset details
          2. If preset has 'i' array: GET /controller/device/{id}/config/
             -> sum LED counts -> resize i array
          3. POST /controller/apply-to-home/ with the constructed payload
        """
        try:
            preset_data = await self.api.async_get_preset(preset_id)
        except BossoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err

        led_count = 0
        # Only fetch device config if the preset actually has an i array.
        # Saves an API call for presets that don't need it.
        if isinstance(preset_data.get("i"), list) and preset_data["i"]:
            try:
                device_config = await self.api.async_get_device_config(device_id)
                led_count = calc_led_count(device_config)
                _LOGGER.debug(
                    "Device %d total LED count: %d", device_id, led_count
                )
            except BossoAuthError as err:
                raise ConfigEntryAuthFailed(str(err)) from err
            except BossoApiError as err:
                _LOGGER.warning(
                    "Could not fetch device config for %d: %s — proceeding "
                    "with led_count=0 (i array won't be resized)",
                    device_id,
                    err,
                )

        payload = build_preset_apply_payload(device_id, preset_data, led_count)
        _LOGGER.debug(
            "Applying preset %d to device %d: payload=%s",
            preset_id,
            device_id,
            payload,
        )

        try:
            await self.api.async_apply_to_home(payload)
        except BossoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err

        # Remember which preset was applied so the select dropdown can
        # keep showing it. Cleared automatically when user does anything
        # else (brightness, color, effect) that overrides the preset.
        self._last_applied_preset[device_id] = preset_id

        # Refresh state so the UI reflects the new preset
        await self.async_request_refresh()

    async def _async_update_data(self) -> dict[int, dict[str, Any]]:
        """Fetch the device list and return as {device_id: device}."""
        try:
            devices = await self.api.async_list_devices()
        except BossoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except BossoApiError as err:
            raise UpdateFailed(f"Bosso API error: {err}") from err

        # Defensive: skip any device entries missing an 'id' field
        # (shouldn't happen, but a malformed API response shouldn't kill
        # the whole integration).
        result: dict[int, dict[str, Any]] = {}
        for device in devices:
            device_id = device.get("id")
            if device_id is None:
                _LOGGER.warning(
                    "Skipping device with missing 'id' field: %s",
                    {k: device.get(k) for k in ("name", "mac", "ip_address")},
                )
                continue
            result[device_id] = device
        return result

    async def async_send_state(
        self, device_id: int, state: dict[str, Any]
    ) -> None:
        """PATCH state for a device, then refresh data."""
        try:
            await self.api.async_set_device_state(device_id, state)
        except BossoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err

        # Any explicit on/off or brightness change overrides the active
        # preset, so forget our remembered preset for this device.
        self._last_applied_preset.pop(device_id, None)

        # Optimistic local update for snappy UI feedback
        if self.data and device_id in self.data:
            current = self.data[device_id].get("state", {})
            current.update(state)
            self.data[device_id]["state"] = current
            self.async_set_updated_data(self.data)

        # Real refresh to get authoritative state from cloud
        await self.async_request_refresh()

    async def async_apply_to_home(self, payload: dict[str, Any]) -> None:
        """POST apply-to-home for color/CCT/effects.

        Note: this is the *direct* color/effect path used by the light
        entity. Preset application uses async_apply_preset() which goes
        through a different flow.
        """
        try:
            await self.api.async_apply_to_home(payload)
        except BossoAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err

        # Color/effect changes override any active preset.
        device_id = payload.get("device", {}).get("device")
        if device_id is not None:
            self._last_applied_preset.pop(device_id, None)

        await self.async_request_refresh()

    def get_last_applied_preset(self, device_id: int) -> int | None:
        """Return the preset id last applied to this device, or None."""
        return self._last_applied_preset.get(device_id)
