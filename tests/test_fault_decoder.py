import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from vevor_eml3500_rs232_wifi.fault_decoder import (
    decode_faults,
    decode_warnings,
)


def test_decode_faults():
    # bit3 -> Battery overvoltage
    faults = decode_faults(1 << 2)
    assert "Battery overvoltage" in faults


def test_decode_warnings():
    # bit 0 -> Mains supply zero-crossing loss
    warnings = decode_warnings(1 << 0)
    assert "Mains supply zero-crossing loss" in warnings
