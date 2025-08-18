"""Decode working mode and power flow status registers."""

from __future__ import annotations

from typing import List


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

