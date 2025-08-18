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
    publish_telemetry(client, "test", "OK", "WARN")
    client.publish.assert_called_once_with(
        "test/telemetry",
        json.dumps({"faults": "OK", "warnings": "WARN"}),
        retain=False,
    )


@pytest.mark.asyncio
async def test_poll_once_reads_registers_and_decodes():
    client = AsyncMock()

    async def fake_read(name: str):
        if name == "Equipment fault code":
            return 1 << 2  # Battery overvoltage
        if name == "Obtain the warning code after shield processing":
            return 1 << 0  # Mains supply zero-crossing loss
        return 0

    client.read_register.side_effect = fake_read
    fault_state, warning_state = await poll_once(client)

    assert "Battery overvoltage" in fault_state
    assert "Mains supply zero-crossing loss" in warning_state
    client.read_register.assert_any_call("Equipment fault code")
    client.read_register.assert_any_call(
        "Obtain the warning code after shield processing"
    )
