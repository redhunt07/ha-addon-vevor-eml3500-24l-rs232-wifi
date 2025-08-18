"""Decode working mode and power flow status registers."""

from __future__ import annotations

from typing import Dict, List, Tuple


WORKING_MODES = {
    0: "Power on mode",
    1: "Standby mode",
    2: "Mains mode",
    3: "Off-grid mode",
    4: "Bypass mode",
    5: "Charging mode",
    6: "Failure mode",
}


def decode_working_mode(value: int) -> str:
    """Return human readable working mode."""
    return WORKING_MODES.get(value, f"Unknown ({value})")


def decode_power_flow(value: int) -> List[str]:
    """Decode bitfield from power flow status register."""
    statuses: List[str] = []
    pv = value & 0b11
    if pv == 1:
        statuses.append("PV connected")
    mains = (value >> 2) & 0b11
    if mains == 1:
        statuses.append("Mains connected")
    battery = (value >> 4) & 0b11
    if battery == 1:
        statuses.append("Battery charging")
    elif battery == 2:
        statuses.append("Battery discharging")
    load = (value >> 6) & 0b11
    if load == 1:
        statuses.append("Load powered")
    if value & (1 << 8):
        statuses.append("Mains charging")
    if value & (1 << 9):
        statuses.append("PV charging")
    if value & (1 << 10):
        statuses.append("Battery icon off")
    if value & (1 << 11):
        statuses.append("PV icon off")
    if value & (1 << 12):
        statuses.append("Mains icon off")
    if value & (1 << 13):
        statuses.append("Load icon off")
    return statuses


def _enum_codec(mapping: Dict[int, str]) -> Tuple[callable, callable]:
    """Return paired decoder and encoder for an enum mapping."""

    def decode(value: int) -> str:
        return mapping.get(int(value), f"Unknown ({value})")

    def encode(value: int | str) -> int:
        if isinstance(value, str):
            val = value.lower()
            for key, name in mapping.items():
                if name.lower() == val:
                    return key
            raise ValueError(f"Invalid enum value: {value}")
        return int(value)

    return decode, encode


decode_output_mode, encode_output_mode = _enum_codec(
    {
        0: "single machine",
        1: "parallel",
        2: "three-phase combination-P1",
        3: "three-phase combination-P2",
        4: "three-phase combination-P3",
    }
)

decode_output_priority, encode_output_priority = _enum_codec(
    {
        0: "Main-PV-Battery (UTI)",
        1: "PV-mains-battery (SOL)",
        2: "PV-battery-mains (SBU)",
        3: "PV-Mains-Battery (SUB)",
    }
)

decode_input_voltage_range, encode_input_voltage_range = _enum_codec(
    {0: "APL", 1: "UPS"}
)

decode_buzzer_mode, encode_buzzer_mode = _enum_codec(
    {
        0: "mute",
        1: "source change or warning",
        2: "warning or fault",
        3: "fault only",
    }
)

decode_battery_type, encode_battery_type = _enum_codec(
    {
        0: "AGM",
        1: "FLD",
        2: "USER",
        3: "Li1",
        4: "Li2",
        5: "Li3",
        6: "Li4",
    }
)

decode_battery_charging_priority, encode_battery_charging_priority = _enum_codec(
    {
        0: "mains first",
        1: "PV priority",
        2: "PV equals mains",
        3: "PV only",
    }
)

decode_boot_mode, encode_boot_mode = _enum_codec(
    {0: "local or remote", 1: "local only", 2: "remote only"}
)

decode_remote_switch, encode_remote_switch = _enum_codec(
    {0: "remote shutdown", 1: "remote power-on"}
)


