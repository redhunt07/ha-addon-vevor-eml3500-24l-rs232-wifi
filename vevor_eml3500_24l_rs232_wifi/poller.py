"""Poll VEVOR EML3500 registers and publish decoded statuses."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Optional, Dict, Any

import paho.mqtt.client as mqtt

from .modbus_client import ModbusRTUOverTCPClient
from .fault_decoder import decode_faults, decode_warnings


REGISTER_MAP = {
    "faults": {
        "register": "Equipment fault code",
        "name": "Faults",
        "decoder": decode_faults,
    },
    "warnings": {
        "register": "Obtain the warning code after shield processing",
        "name": "Warnings",
        "decoder": decode_warnings,
        "writable": True,
    },
    "mains_voltage": {
        "register": "Mains voltage effective value",
        "name": "Mains Voltage",
        "unit": "V",
    },
    "mains_frequency": {
        "register": "Mains frequency",
        "name": "Mains Frequency",
        "unit": "Hz",
    },
    "mains_power": {
        "register": "Average mains power",
        "name": "Mains Power",
        "unit": "W",
    },
    "inverter_voltage": {
        "register": "Effective value of inverter voltage",
        "name": "Inverter Voltage",
        "unit": "V",
    },
    "inverter_current": {
        "register": "Effective value of inverter current",
        "name": "Inverter Current",
        "unit": "A",
    },
    "battery_voltage": {
        "register": "Average battery voltage",
        "name": "Battery Voltage",
        "unit": "V",
        "device_class": "voltage",
    },
    "battery_current": {
        "register": "Average battery current",
        "name": "Battery Current",
        "unit": "A",
        "device_class": "current",
    },
    "battery_power": {
        "register": "Average battery power",
        "name": "Battery Power",
        "unit": "W",
        "device_class": "power",
    },
    "battery_soc": {
        "register": "Battery percentage",
        "name": "Battery SOC",
        "unit": "%",
        "device_class": "battery",
    },
    "pv_voltage": {
        "register": "Average PV voltage",
        "name": "PV Voltage",
        "unit": "V",
        "device_class": "voltage",
    },
    "pv_current": {
        "register": "Average PV current",
        "name": "PV Current",
        "unit": "A",
        "device_class": "current",
    },
    "pv_power": {
        "register": "Average PV power",
        "name": "PV Power",
        "unit": "W",
        "device_class": "power",
    },
    "load_percent": {
        "register": "Percent of load",
        "name": "Load Percent",
        "unit": "%",
    },
    "dcdc_temperature": {
        "register": "DCDC temperature",
        "name": "DCDC Temperature",
        "unit": "°C",
        "device_class": "temperature",
    },
    "inverter_temperature": {
        "register": "Inverter temperature",
        "name": "Inverter Temperature",
        "unit": "°C",
        "device_class": "temperature",
    },
    "battery_discharge_soc_limit": {
        "register": "Battery discharge SOC protection value in off-grid mode",
        "name": "Battery Discharge SOC Limit",
        "unit": "%",
        "writable": True,
    },
}

WRITABLE_REGISTERS = {
    slug: info["register"]
    for slug, info in REGISTER_MAP.items()
    if info.get("writable")
}


async def poll_once(client: ModbusRTUOverTCPClient) -> Dict[str, Any]:
    """Read all relevant registers and return slug-value mapping."""

    results: Dict[str, Any] = {}
    for slug, info in REGISTER_MAP.items():
        value = await client.read_register(info["register"])
        decoder = info.get("decoder")
        if decoder:
            decoded = decoder(int(value))
            value = ", ".join(decoded) if decoded else "OK"
        results[slug] = value
    return results


def publish_discovery(
    client: mqtt.Client, prefix: str = "vevor_eml3500"
) -> None:
    """Publish Home Assistant MQTT discovery config with device metadata."""
    device_info = {
        "identifiers": [prefix],
        "manufacturer": "VEVOR",
        "model": "EML3500-24L",
        "name": "VEVOR EML3500-24L",
    }
    for slug, info in REGISTER_MAP.items():
        topic = f"homeassistant/sensor/{prefix}_{slug}/config"
        payload: Dict[str, Any] = {
            "name": f"VEVOR {info['name']}",
            "state_topic": f"{prefix}/{slug}",
            "unique_id": f"{prefix}_{slug}",
            "device": device_info,
        }
        if unit := info.get("unit"):
            payload["unit_of_measurement"] = unit
            payload["state_class"] = "measurement"
        if device_class := info.get("device_class"):
            payload["device_class"] = device_class
        client.publish(topic, json.dumps(payload), retain=True)


def publish_telemetry(
    client: mqtt.Client,
    prefix: str,
    data: Dict[str, Any],
) -> None:
    """Publish telemetry JSON for each poll cycle."""
    payload = json.dumps(data)
    client.publish(f"{prefix}/telemetry", payload, retain=False)


async def handle_command(
    modbus: ModbusRTUOverTCPClient, payload: str
) -> None:
    """Handle MQTT command payload to write registers."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return
    if not isinstance(data, dict):
        return
    for slug, value in data.items():
        if slug not in WRITABLE_REGISTERS:
            continue
        if not isinstance(value, (int, float)):
            continue
        try:
            await modbus.write_register(WRITABLE_REGISTERS[slug], float(value))
        except Exception:
            continue


async def main(args: argparse.Namespace) -> None:
    modbus = ModbusRTUOverTCPClient(
        host=args.bridge_host,
        port=args.bridge_port,
        poll_interval=args.poll_interval,
    )

    mqtt_client: Optional[mqtt.Client] = None
    prefix = "vevor_eml3500"
    if args.mqtt_host:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if args.mqtt_username:
            mqtt_client.username_pw_set(
                args.mqtt_username, args.mqtt_password or ""
            )
        try:
            mqtt_client.connect(args.mqtt_host, args.mqtt_port)
        except OSError as err:  # pragma: no cover - network error
            print(f"MQTT connect failed: {err}")
            mqtt_client = None
        else:
            publish_discovery(mqtt_client, prefix)
            mqtt_client.subscribe(f"{prefix}/set")

            def on_message(
                client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
            ) -> None:
                asyncio.create_task(handle_command(modbus, msg.payload.decode()))

            mqtt_client.on_message = on_message

    try:
        while True:
            data = await poll_once(modbus)
            if mqtt_client:
                try:
                    for slug, value in data.items():
                        mqtt_client.publish(
                            f"{prefix}/{slug}", str(value), retain=True
                        )
                    publish_telemetry(mqtt_client, prefix, data)
                    mqtt_client.loop(0.1)
                except OSError as err:  # pragma: no cover - network error
                    print(f"MQTT publish failed: {err}")
                    mqtt_client = None
            elif args.mqtt_host:
                try:
                    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                    if args.mqtt_username:
                        mqtt_client.username_pw_set(
                            args.mqtt_username, args.mqtt_password or ""
                        )
                    mqtt_client.connect(args.mqtt_host, args.mqtt_port)
                except OSError as err:  # pragma: no cover - network error
                    print(f"MQTT reconnect failed: {err}")
                    mqtt_client = None
                else:
                    publish_discovery(mqtt_client, prefix)
                    mqtt_client.subscribe(f"{prefix}/set")
                    mqtt_client.on_message = (
                        lambda c, u, m: asyncio.create_task(
                            handle_command(modbus, m.payload.decode())
                        )
                    )
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
