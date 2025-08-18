import sys
import json
from pathlib import Path
from unittest.mock import MagicMock

import paho.mqtt.client as mqtt

sys.path.append(str(Path(__file__).resolve().parents[1]))

from poller import publish_discovery, publish_telemetry  # noqa: E402


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
