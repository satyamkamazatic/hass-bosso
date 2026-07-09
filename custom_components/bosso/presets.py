# """Pure helper functions for building preset payloads.

# These are kept separate from the rest of the integration so they can be
# unit-tested without spinning up Home Assistant. No HA imports here.
# """
# from __future__ import annotations

# import logging
# from typing import Any

# _LOGGER = logging.getLogger(__name__)


# def calc_led_count(device_config: dict[str, Any]) -> int:
#     """Sum the per-channel LED counts. None values count as 0.

#     Example device_config:
#         {"data_1_led_count": 300, "data_2_led_count": null, ...}
#     """
#     total = 0
#     for key in (
#         "data_1_led_count",
#         "data_2_led_count",
#         "data_3_led_count",
#         "data_4_led_count",
#     ):
#         value = device_config.get(key)
#         if value:
#             total += value
#     return total


# def has_valid_i_array(i_array: Any) -> bool:
#     """Return True if `i_array` is a non-empty list."""
#     return isinstance(i_array, list) and len(i_array) > 0


# def resize_i_array(i_array: list[Any], led_count: int) -> list[Any]:
#     """Resize the preset's i array to match the device's LED count.

#     Mirrors the JavaScript logic from the Bosso web client:
#     - If led_count == len(i_array): return as-is
#     - If led_count < len(i_array): truncate to led_count
#     - If led_count > len(i_array): tile/repeat the i array to fill the
#       device, plus the leftover slice for the remainder.

#     Args:
#         i_array: the preset's i pattern (per-LED data)
#         led_count: total LED count for the target device

#     Returns:
#         A new list of length `led_count` (or the original if led_count <= 0).
#     """
#     if led_count <= 0:
#         # Defensive: don't try to resize if we don't know the LED count
#         return list(i_array)

#     original_length = len(i_array)
#     if original_length == 0:
#         return []

#     if led_count == original_length:
#         return list(i_array)

#     if led_count < original_length:
#         return list(i_array[:led_count])

#     # led_count > original_length: tile the array
#     # Mirrors the JS:
#     #   diff = led_count - original_length
#     #   times = floor(diff / original_length)
#     #   remainder = diff % original_length
#     #   extended = concat(iArray, times) + iArray.slice(0, remainder)
#     #   result = iArray + extended
#     diff = led_count - original_length
#     times = diff // original_length
#     remainder = diff % original_length

#     extended: list[Any] = []
#     for _ in range(times):
#         extended.extend(i_array)
#     extended.extend(i_array[:remainder])

#     return list(i_array) + extended


# def build_preset_apply_payload(
#     device_id: int,
#     preset_data: dict[str, Any],
#     led_count: int,
# ) -> dict[str, Any]:
#     """Build the apply-to-home payload for a preset.

#     Two cases (matching the JS reference logic):

#     Case 1 - preset has a valid `i` array:
#         Resize the i array to match the device's LED count, then send a
#         minimal payload that just contains the i pattern.

#     Case 2 - preset has no valid `i` array:
#         Send the full preset state (color, fx, palette, etc.).

#     Args:
#         device_id: The Bosso device id to target.
#         preset_data: Full preset dict from GET /preset/{id}/.
#         led_count: Total LED count for the device (only used for Case 1).

#     Returns:
#         A dict ready to POST to /controller/apply-to-home/.
#     """
#     i_array = preset_data.get("i")

#     if has_valid_i_array(i_array):
#         # ---- Case 1: i-based payload --------------------------------
#         resized = resize_i_array(i_array, led_count)
#         _LOGGER.debug(
#             "Preset i-array resized: original=%d, target=%d, final=%d",
#             len(i_array),
#             led_count,
#             len(resized),
#         )
#         return {
#             "device": {"device": device_id, "i": resized},
#             "is_cct_enabled": True,
#             "cct": preset_data.get("cct", 127),
#             "fx": None,
#         }

#     # ---- Case 2: full preset payload --------------------------------
#     return {
#         "device": {"device": device_id, "i": []},
#         "fx": preset_data.get("fx"),
#         "sx": preset_data.get("sx"),
#         "ix": preset_data.get("ix"),
#         "pal": preset_data.get("pal"),
#         "col": preset_data.get("col"),
#         "rev": preset_data.get("rev"),
#         "mi": preset_data.get("mi"),
#         "is_cct_enabled": True,
#         "cct": preset_data.get("cct", 127),
#     }


"""Pure helper functions for building preset payloads.

These are kept separate from the rest of the integration so they can be
unit-tested without spinning up Home Assistant. No HA imports here.
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def calc_led_count(device_config: dict[str, Any]) -> int:
    """Sum the per-channel LED counts. None values count as 0."""
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
    """Resize an i array to match a target LED count (tile/truncate)."""
    if led_count <= 0:
        return list(i_array)

    original_length = len(i_array)
    if original_length == 0:
        return []

    if led_count == original_length:
        return list(i_array)

    if led_count < original_length:
        return list(i_array[:led_count])

    diff = led_count - original_length
    times = diff // original_length
    remainder = diff % original_length

    extended: list[Any] = []
    for _ in range(times):
        extended.extend(i_array)
    extended.extend(i_array[:remainder])

    return list(i_array) + extended


def get_device_i_array(preset_data: dict[str, Any]) -> Any:
    """Extract the device-level i array, correctly nested under 'device'."""
    device = preset_data.get("device") or {}
    return device.get("i")


def get_zones_i_array(preset_data: dict[str, Any]) -> list[Any]:
    """Concatenate the i arrays from all zones, in list order.

    Zones with no/invalid `i` are skipped. Returns an empty list if no
    zone has a valid `i` array.
    """
    zones = preset_data.get("zones") or []
    combined: list[Any] = []
    for zone in zones:
        zone_i = zone.get("i")
        if has_valid_i_array(zone_i):
            combined.extend(zone_i)
    return combined


def build_preset_apply_payload(
    device_id: int,
    preset_data: dict[str, Any],
    led_count: int,
) -> dict[str, Any]:
    """Build the apply-to-home payload for a preset.

    Three cases, all resized against the device's total `led_count`
    (there's no per-zone target length here - everything is flattened
    into a single `device.i` array):

    Case 1 - preset has a valid device-level `i` array (`device.i`):
        Resize it to the device's LED count, send a minimal i-based payload.

    Case 2 - device.i is empty/missing, but one or more `zones[].i` are
        valid:
        Concatenate all zones' i arrays (in order) into a single source
        array, then resize *that* to the device's LED count and send it
        as `device.i` - same shape as Case 1, just a different source.

    Case 3 - neither device.i nor any zone.i is valid:
        Send the full preset state (color, fx, palette, etc.), same as
        before.

    Args:
        device_id: The Bosso device id to target.
        preset_data: Full preset dict from GET /preset/{id}/.
        led_count: Total LED count for the device.

    Returns:
        A dict ready to POST to /controller/apply-to-home/.
    """
    device_i_array = get_device_i_array(preset_data)

    # ---- Case 1: device-level i array --------------------------------
    source_i_array = device_i_array if has_valid_i_array(device_i_array) else None
    source_label = "device"

    # ---- Case 2: zone-level i arrays (concatenated) --------------------
    if source_i_array is None:
        zones_i_array = get_zones_i_array(preset_data)
        if has_valid_i_array(zones_i_array):
            source_i_array = zones_i_array
            source_label = "zones (concatenated)"

    if source_i_array is not None:
        resized = resize_i_array(source_i_array, led_count)
        _LOGGER.debug(
            "%s i-array resized: original=%d, target=%d, final=%d",
            source_label,
            len(source_i_array),
            led_count,
            len(resized),
        )
        return {
            "device": {"device": device_id, "i": resized},
            "is_cct_enabled": True,
            "cct": preset_data.get("cct", 127),
            "fx": None,
        }

    # ---- Case 3: full preset payload --------------------------------
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


