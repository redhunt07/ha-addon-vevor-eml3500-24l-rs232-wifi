import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from vevor_eml3500_rs232_wifi.modbus_client import (
    DEFAULT_REGISTER_CSV,
    load_register_definitions,
)


def test_load_registers():
    path = DEFAULT_REGISTER_CSV
    registers = load_register_definitions(path)
    reg = registers["Mains voltage effective value"]
    assert reg.address == 202
    assert reg.count == 1
    assert reg.data_format == "Int"
    assert reg.scale == 0.1
