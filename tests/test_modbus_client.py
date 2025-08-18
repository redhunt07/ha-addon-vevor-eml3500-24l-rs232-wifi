
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from modbus_client import load_register_definitions, DEFAULT_REGISTER_CSV


def test_load_registers():
    path = DEFAULT_REGISTER_CSV
    registers = load_register_definitions(path)
    reg = registers["Mains voltage effective value"]
    assert reg.address == 202
    assert reg.count == 1
    assert reg.data_format == "Int"
    assert reg.scale == 0.1
