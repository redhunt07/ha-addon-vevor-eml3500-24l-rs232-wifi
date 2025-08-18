import sys
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import paho.mqtt.client as mqtt
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from vevor_eml3500_24l_rs232_wifi.poller import (
    poll_once,
    publish_discovery,
    publish_telemetry,
    handle_command,
)


def test_publish_discovery_includes_device_metadata():
    client = MagicMock(spec=mqtt.Client)
    publish_discovery(client, prefix="test")
    topic, payload = client.publish.call_args_list[0][0]
    assert topic == "homeassistant/sensor/test_faults/config"
    data = json.loads(payload)
    assert data["unique_id"] == "test_faults"
    assert data["device"]["manufacturer"] == "VEVOR"
    assert data["device"]["identifiers"] == ["test"]


def test_publish_telemetry_publishes_json():
    client = MagicMock(spec=mqtt.Client)
    data = {"faults": "OK", "warnings": "WARN"}
    publish_telemetry(client, "test", data)
    client.publish.assert_called_once_with(
        "test/telemetry",
        json.dumps(data),
        retain=False,
    )


@pytest.mark.asyncio
async def test_poll_once_reads_registers_and_decodes():
    client = AsyncMock()

    async def fake_read(name: str):
        mapping = {
            "Equipment fault code": 1 << 2,  # Battery overvoltage
            "Obtain the warning code after shield processing": 1 << 0,
            "Working mode": 3,
            "Inverter frequency": 50.0,
            "Inverter power average": 1200.0,
            "Inverter charging power": 500.0,
            "Effective value of output voltage": 230.0,
            "Effective value of output current": 5.0,
            "Output frequency": 50.0,
            "Output active power": 1000.0,
            "Output apparent power": 1100.0,
            "Average battery power": 200.0,
            "Battery current filter average": -2.0,
            "Average PV voltage": 150.0,
            "Average PV current": 4.0,
            "Average PV power": 600.0,
            "Average PV charging power": 400.0,
            "Average value of inverter charging current": 10.0,
            "Average PV charging current": 6.0,
            "Power flow status": 869,
        }
        return mapping.get(name, 0)

    client.read_register.side_effect = fake_read
    data = await poll_once(client)

    assert "Battery overvoltage" in data["faults"]
    assert "Mains supply zero-crossing loss" in data["warnings"]
    assert data["working_mode"] == "Off-grid mode"
    assert data["inverter_frequency"] == 50.0
    assert data["inverter_power"] == 1200.0
    assert data["inverter_charging_power"] == 500.0
    assert data["output_voltage"] == 230.0
    assert data["output_current"] == 5.0
    assert data["output_frequency"] == 50.0
    assert data["output_active_power"] == 1000.0
    assert data["output_apparent_power"] == 1100.0
    assert data["battery_current_filter_average"] == -2.0
    assert data["pv_charging_power"] == 400.0
    assert data["inverter_charging_current"] == 10.0
    assert data["pv_charging_current"] == 6.0
    assert "PV connected" in data["power_flow_status"]
    assert "Mains connected" in data["power_flow_status"]
    assert "Battery discharging" in data["power_flow_status"]
    assert "Mains charging" in data["power_flow_status"]
    assert "PV charging" in data["power_flow_status"]
    client.read_register.assert_any_call("Equipment fault code")
    client.read_register.assert_any_call(
        "Obtain the warning code after shield processing"
    )


@pytest.mark.asyncio
async def test_handle_command_writes_register():
    modbus = AsyncMock()
    await handle_command(
        modbus, json.dumps({"warnings": 0})
    )
    modbus.write_register.assert_awaited_once_with(
        "Obtain the warning code after shield processing", 0.0
    )


@pytest.mark.asyncio
async def test_handle_command_validates_input():
    modbus = AsyncMock()
    await handle_command(modbus, json.dumps({"unknown": 1, "warnings": "bad"}))
    modbus.write_register.assert_not_called()
