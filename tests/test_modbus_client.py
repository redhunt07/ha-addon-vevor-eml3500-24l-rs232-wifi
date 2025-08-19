import sys
from pathlib import Path
import importlib

import pytest

# Provide missing FramerType for pymodbus when using newer versions
framer_module = importlib.import_module("pymodbus.framer")
if not hasattr(framer_module, "FramerType"):
    class FramerType:
        RTU = framer_module.ModbusRtuFramer

    framer_module.FramerType = FramerType

sys.path.append(str(Path(__file__).resolve().parents[1]))

from vevor_eml3500_24l_rs232_wifi.modbus_client import (  # noqa: E402
    DEFAULT_REGISTER_CSV,
    RegisterDefinition,
    ModbusRTUOverTCPClient,
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


@pytest.mark.asyncio
async def test_read_register_uses_keyword_count(monkeypatch):
    client = ModbusRTUOverTCPClient("example.com")
    client.registers = {
        "test": RegisterDefinition(
            name="test",
            unit="",
            data_format="UInt",
            address=0,
            count=1,
            access="R",
            remark="",
        )
    }

    async def fake_connect():
        return None

    client.connect = fake_connect

    async def fake_read(address, *, count=1, **kwargs):
        class Resp:
            def __init__(self):
                self.registers = [42] * count

            def isError(self):
                return False

        return Resp()

    client.client.read_holding_registers = fake_read
    value = await client.read_register("test")
    assert value == 42


@pytest.mark.asyncio
async def test_read_register_scales_without_float_error(monkeypatch):
    client = ModbusRTUOverTCPClient("example.com")
    client.registers = {
        "voltage": RegisterDefinition(
            name="voltage",
            unit="",
            data_format="UInt",
            address=0,
            count=1,
            access="R",
            remark="",
            scale=0.1,
        )
    }

    async def fake_connect():
        return None

    client.connect = fake_connect

    async def fake_read(address, *, count=1, **kwargs):
        class Resp:
            def __init__(self):
                self.registers = [249]

            def isError(self):
                return False

        return Resp()

    client.client.read_holding_registers = fake_read
    value = await client.read_register("voltage")
    assert value == 24.9
