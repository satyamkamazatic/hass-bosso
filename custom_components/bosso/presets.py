"""Pure helper functions for building preset payloads.

These are kept separate from the rest of the integration so they can be
unit-tested without spinning up Home Assistant. No HA imports here.
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def calc_led_count(device_config: dict[str, Any]) -> int:
    """Sum the per-channel LED counts. None values count as 0.

    Example device_config:
        {"data_1_led_count": 300, "data_2_led_count": null, ...}
    """
    total = 0
    for key in (
        "data_1_led_count",
        "data_2_led_count",
        "data_3_led_count",
        "data_4_led_count",
    ):
        value = device_config.get(key)
        if value:
            total += value
    return total


def has_valid_i_array(i_array: Any) -> bool:
    """Return True if `i_array` is a non-empty list."""
    return isinstance(i_array, list) and len(i_array) > 0


def resize_i_array(i_array: list[Any], led_count: int) -> list[Any]:
    """Resize the preset's i array to match the device's LED count.

    Mirrors the JavaScript logic from the Bosso web client:
    - If led_count == len(i_array): return as-is
    - If led_count < len(i_array): truncate to led_count
    - If led_count > len(i_array): tile/repeat the i array to fill the
      device, plus the leftover slice for the remainder.

    Args:
        i_array: the preset's i pattern (per-LED data)
        led_count: total LED count for the target device

    Returns:
        A new list of length `led_count` (or the original if led_count <= 0).
    """
    if led_count <= 0:
        # Defensive: don't try to resize if we don't know the LED count
        return list(i_array)

    original_length = len(i_array)
    if original_length == 0:
        return []

    if led_count == original_length:
        return list(i_array)

    if led_count < original_length:
        return list(i_array[:led_count])

    # led_count > original_length: tile the array
    # Mirrors the JS:
    #   diff = led_count - original_length
    #   times = floor(diff / original_length)
    #   remainder = diff % original_length
    #   extended = concat(iArray, times) + iArray.slice(0, remainder)
    #   result = iArray + extended
    diff = led_count - original_length
    times = diff // original_length
    remainder = diff % original_length

    extended: list[Any] = []
    for _ in range(times):
        extended.extend(i_array)
    extended.extend(i_array[:remainder])

    return list(i_array) + extended


def build_preset_apply_payload(
    device_id: int,
    preset_data: dict[str, Any],
    led_count: int,
) -> dict[str, Any]:
    """Build the apply-to-home payload for a preset.

    Two cases (matching the JS reference logic):

    Case 1 - preset has a valid `i` array:
        Resize the i array to match the device's LED count, then send a
        minimal payload that just contains the i pattern.

    Case 2 - preset has no valid `i` array:
        Send the full preset state (color, fx, palette, etc.).

    Args:
        device_id: The Bosso device id to target.
        preset_data: Full preset dict from GET /preset/{id}/.
        led_count: Total LED count for the device (only used for Case 1).

    Returns:
        A dict ready to POST to /controller/apply-to-home/.
    """
    i_array = preset_data.get("i")

    if has_valid_i_array(i_array):
        # ---- Case 1: i-based payload --------------------------------
        resized = resize_i_array(i_array, led_count)
        _LOGGER.debug(
            "Preset i-array resized: original=%d, target=%d, final=%d",
            len(i_array),
            led_count,
            len(resized),
        )
        return {
            "device": {"device": device_id, "i": resized},
            "is_cct_enabled": True,
            "cct": preset_data.get("cct", 127),
            "fx": None,
        }

    # ---- Case 2: full preset payload --------------------------------
    return {
        "device": {"device": device_id, "i": []},
        "fx": preset_data.get("fx"),
        "sx": preset_data.get("sx"),
        "ix": preset_data.get("ix"),
        "pal": preset_data.get("pal"),
        "col": preset_data.get("col"),
        "rev": preset_data.get("rev"),
        "mi": preset_data.get("mi"),
        "is_cct_enabled": True,
        "cct": preset_data.get("cct", 127),
    }
