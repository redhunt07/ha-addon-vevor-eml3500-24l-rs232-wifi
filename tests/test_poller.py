import sys
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call
import importlib
import logging

import paho.mqtt.client as mqtt
import pytest

# Ensure pymodbus provides FramerType during tests
framer_module = importlib.import_module("pymodbus.framer")
if not hasattr(framer_module, "FramerType"):
    class FramerType:
        RTU = framer_module.ModbusRtuFramer

    framer_module.FramerType = FramerType

sys.path.append(str(Path(__file__).resolve().parents[1]))

import vevor_eml3500_24l_rs232_wifi.poller as poller  # noqa: E402
from vevor_eml3500_24l_rs232_wifi.poller import (  # noqa: E402
    poll_once,
    publish_discovery,
    publish_telemetry,
    handle_command,
    load_energy_state,
    save_energy_state,
    update_energy_state,
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


def test_publish_discovery_includes_energy_sensors():
    client = MagicMock(spec=mqtt.Client)
    publish_discovery(client, prefix="test")
    calls = {args[0]: json.loads(args[1]) for args, _ in client.publish.call_args_list}
    for slug in (
        "grid_import_energy",
        "pv_energy",
        "battery_charge_energy",
    ):
        payload = calls[f"homeassistant/sensor/test_{slug}/config"]
        assert payload["unit_of_measurement"] == "kWh"
        assert payload["device_class"] == "energy"
        assert payload["state_class"] == "total_increasing"


def test_publish_discovery_includes_last_update_sensor():
    client = MagicMock(spec=mqtt.Client)
    publish_discovery(client, prefix="test")
    calls = {args[0]: json.loads(args[1]) for args, _ in client.publish.call_args_list}
    payload = calls["homeassistant/sensor/test_last_update/config"]
    assert payload["device_class"] == "timestamp"


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
    data, last_update = await poll_once(client)

    assert isinstance(last_update, str)
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
async def test_poll_once_logs_and_continues_on_error(caplog):
    client = AsyncMock()

    async def fake_read(register: str):
        if register == "Working mode":
            raise RuntimeError("boom")
        return 1

    client.read_register.side_effect = fake_read

    with caplog.at_level(logging.WARNING):
        data, _ = await poll_once(client)

    assert data["working_mode"] is None
    assert data["mains_voltage"] == 1
    assert "Working mode" in caplog.text
    assert "stale" in caplog.text



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


@pytest.mark.asyncio
async def test_handle_command_publishes_state():
    modbus = AsyncMock()
    mqtt_client = MagicMock(spec=mqtt.Client)

    async def fake_read(register: str):
        mapping = {
            "Output mode": 1,
            "Output priority": 2,
            "Maximum charge voltage [B]": 57.0,
        }
        return mapping[register]

    modbus.read_register.side_effect = fake_read

    payload = json.dumps(
        {
            "output_mode": "parallel",
            "output_priority": "PV-battery-mains (SBU)",
            "max_charge_voltage": 57,
        }
    )
    await handle_command(
        modbus,
        payload,
        mqtt_client=mqtt_client,
        prefix="test",
    )
    modbus.write_register.assert_has_awaits(
        [
            call("Output mode", 1.0),
            call("Output priority", 2.0),
            call("Maximum charge voltage [B]", 57.0),
        ]
    )
    mqtt_client.publish.assert_has_calls(
        [
            call("test/output_mode", "parallel", retain=True),
            call(
                "test/output_priority",
                "PV-battery-mains (SBU)",
                retain=True,
            ),
            call("test/max_charge_voltage", "57.0", retain=True),
        ]
    )


@pytest.mark.asyncio
async def test_poll_once_reads_numeric_and_enum_registers():
    client = AsyncMock()

    async def fake_read(name: str):
        mapping = {
            "Maximum charge voltage [B]": 56.0,
            "Output priority": 1,
        }
        return mapping.get(name, 0)

    client.read_register.side_effect = fake_read
    data, _ = await poll_once(client)

    assert data["max_charge_voltage"] == 56.0
    assert data["output_priority"] == "PV-mains-battery (SOL)"
    client.read_register.assert_any_call("Maximum charge voltage [B]")
    client.read_register.assert_any_call("Output priority")


@pytest.mark.asyncio
async def test_handle_command_writes_enum_and_publishes():
    modbus = AsyncMock()
    mqtt_client = MagicMock(spec=mqtt.Client)
    modbus.read_register.return_value = 2
    await handle_command(
        modbus,
        "PV-battery-mains (SBU)",
        slug="output_priority",
        mqtt_client=mqtt_client,
        prefix="test",
    )
    modbus.write_register.assert_awaited_once_with("Output priority", 2.0)
    mqtt_client.publish.assert_called_once_with(
        "test/output_priority", "PV-battery-mains (SBU)", retain=True
    )


@pytest.mark.asyncio
async def test_handle_command_writes_numeric_and_publishes():
    modbus = AsyncMock()
    mqtt_client = MagicMock(spec=mqtt.Client)
    modbus.read_register.return_value = 57.0
    await handle_command(
        modbus,
        json.dumps({"max_charge_voltage": 57}),
        mqtt_client=mqtt_client,
        prefix="test",
    )
    modbus.write_register.assert_awaited_once_with(
        "Maximum charge voltage [B]", 57.0
    )
    mqtt_client.publish.assert_called_once_with(
        "test/max_charge_voltage", "57.0", retain=True
    )


def test_energy_state_persistence(tmp_path, monkeypatch):
    temp = tmp_path / "energy_state.json"
    monkeypatch.setattr(poller, "ENERGY_STATE_FILE", temp)
    state = load_energy_state()
    data = {"mains_power": 1000.0, "pv_power": 500.0, "battery_power": -200.0}
    update_energy_state(data, state, 60)
    save_energy_state(state)
    reloaded = load_energy_state()
    assert reloaded["grid_import_energy"] == pytest.approx(1 / 60, rel=1e-3)
    assert reloaded["pv_energy"] == pytest.approx(0.5 / 60, rel=1e-3)
    assert reloaded["battery_charge_energy"] == pytest.approx(0.2 / 60, rel=1e-3)


def test_energy_state_multiple_poll_cycles(tmp_path, monkeypatch):
    temp = tmp_path / "energy_state.json"
    monkeypatch.setattr(poller, "ENERGY_STATE_FILE", temp)

    # First polling cycle
    state = load_energy_state()
    data1 = {"mains_power": 1000.0, "pv_power": 500.0, "battery_power": -200.0}
    update_energy_state(data1, state, 60)
    save_energy_state(state)

    # Second cycle loads previous state and accumulates more energy
    state = load_energy_state()
    data2 = {"mains_power": 500.0, "pv_power": 250.0, "battery_power": -100.0}
    update_energy_state(data2, state, 60)
    save_energy_state(state)

    reloaded = load_energy_state()
    assert reloaded["grid_import_energy"] == pytest.approx(1.5 / 60, rel=1e-3)
    assert reloaded["pv_energy"] == pytest.approx(0.75 / 60, rel=1e-3)
    assert reloaded["battery_charge_energy"] == pytest.approx(0.3 / 60, rel=1e-3)


def test_update_energy_state_handles_none_and_invalid_values():
    state = {slug: 1.0 for slug in poller.ENERGY_SENSORS}
    initial = state.copy()
    data = {"mains_power": None, "pv_power": "invalid", "battery_power": None}

    update_energy_state(data, state, 60)

    for slug, value in state.items():
        assert value == pytest.approx(initial[slug])
