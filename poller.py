"""Poll VEVOR EML3500 registers and publish decoded statuses."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Optional

import paho.mqtt.client as mqtt

from modbus_client import ModbusRTUOverTCPClient
from fault_decoder import decode_faults, decode_warnings


async def poll_once(client: ModbusRTUOverTCPClient) -> tuple[str, str]:
    fault_val = await client.read_register("Equipment fault code")
    warn_val = await client.read_register(
        "Obtain the warning code after shield processing"
    )
    faults = decode_faults(int(fault_val))
    warnings = decode_warnings(int(warn_val))
    fault_state = ", ".join(faults) if faults else "OK"
    warning_state = ", ".join(warnings) if warnings else "OK"
    return fault_state, warning_state


def publish_discovery(
    client: mqtt.Client, prefix: str = "vevor_eml3500"
) -> None:
    """Publish Home Assistant MQTT discovery config."""
    sensors = {
        "faults": "Faults",
        "warnings": "Warnings",
    }
    for key, name in sensors.items():
        topic = f"homeassistant/sensor/{prefix}_{key}/config"
        payload = json.dumps(
            {
                "name": f"VEVOR {name}",
                "state_topic": f"{prefix}/{key}",
                "unique_id": f"{prefix}_{key}",
            }
        )
        client.publish(topic, payload, retain=True)


async def main(args: argparse.Namespace) -> None:
    modbus = ModbusRTUOverTCPClient(
        host=args.bridge_host,
        port=args.bridge_port,
        poll_interval=args.poll_interval,
    )

    mqtt_client: Optional[mqtt.Client] = None
    if args.mqtt_host:
        mqtt_client = mqtt.Client()
        if args.mqtt_username:
            mqtt_client.username_pw_set(
                args.mqtt_username, args.mqtt_password or ""
            )
        mqtt_client.connect(args.mqtt_host, args.mqtt_port)
        publish_discovery(mqtt_client)

    try:
        while True:
            fault_state, warning_state = await poll_once(modbus)
            if mqtt_client:
                mqtt_client.publish(
                    "vevor_eml3500/faults", fault_state, retain=True
                )
                mqtt_client.publish(
                    "vevor_eml3500/warnings", warning_state, retain=True
                )
                mqtt_client.loop(0.1)
            await asyncio.sleep(args.poll_interval)
    finally:
        await modbus.close()
        if mqtt_client:
            mqtt_client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VEVOR EML3500 poller")
    parser.add_argument("--bridge-host", required=True)
    parser.add_argument("--bridge-port", type=int, default=23)
    parser.add_argument("--poll-interval", type=int, default=60)
    parser.add_argument("--mqtt-host", default="")
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--mqtt-username", default="")
    parser.add_argument("--mqtt-password", default="")
    asyncio.run(main(parser.parse_args()))
