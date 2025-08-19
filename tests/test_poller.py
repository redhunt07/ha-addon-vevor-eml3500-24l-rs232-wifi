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


def test_publish_discovery_select_and_number():
    client = MagicMock(spec=mqtt.Client)
    publish_discovery(client, prefix="test")
    calls = {args[0]: json.loads(args[1]) for args, _ in client.publish.call_args_list}
    select_payload = calls["homeassistant/select/test_output_priority/config"]
    assert select_payload["command_topic"] == "test/output_priority/set"
    assert "PV-mains-battery (SOL)" in select_payload["options"]
    number_payload = calls["homeassistant/number/test_max_charge_voltage/config"]
    assert number_payload["command_topic"] == "test/max_charge_voltage/set"
    assert all(k in number_payload for k in ("min", "max", "step"))


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
@pytest.mark.parametrize(
    "payload,register,expected",
    [
        ({"warnings": 0}, "Obtain the warning code after shield processing", 0.0),
        ({"output_mode": "parallel"}, "Output mode", 1.0),
        ({"device_name": "MyDevice"}, "Device name", "MyDevice"),
    ],
)
async def test_handle_command_writes_register(payload, register, expected):
    modbus = AsyncMock()
    await handle_command(modbus, json.dumps(payload))
    modbus.write_register.assert_awaited_once_with(register, expected)


@pytest.mark.asyncio
async def test_handle_command_validates_input():
    modbus = AsyncMock()
    await handle_command(modbus, json.dumps({"unknown": 1, "warnings": "bad"}))
    modbus.write_register.assert_not_called()


@pytest.mark.asyncio
async def test_handle_command_individual_topic():
    modbus = AsyncMock()
    await handle_command(modbus, "parallel", slug="output_mode")
    modbus.write_register.assert_awaited_once_with("Output mode", 1.0)
