"""Poll VEVOR EML3500 registers and publish decoded statuses."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import paho.mqtt.client as mqtt

from .modbus_client import ModbusRTUOverTCPClient
from .fault_decoder import decode_faults, decode_warnings
from .status_decoder import (
    decode_working_mode,
    decode_power_flow,
    decode_output_mode,
    encode_output_mode,
    decode_output_priority,
    encode_output_priority,
    decode_input_voltage_range,
    encode_input_voltage_range,
    decode_buzzer_mode,
    encode_buzzer_mode,
    decode_battery_type,
    encode_battery_type,
    decode_battery_charging_priority,
    encode_battery_charging_priority,
    decode_boot_mode,
    encode_boot_mode,
    decode_remote_switch,
    encode_remote_switch,
)


logger = logging.getLogger(__name__)


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
    "working_mode": {
        "register": "Working mode",
        "name": "Working Mode",
        "decoder": decode_working_mode,
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
    "inverter_frequency": {
        "register": "Inverter frequency",
        "name": "Inverter Frequency",
        "unit": "Hz",
    },
    "inverter_power": {
        "register": "Inverter power average",
        "name": "Inverter Power",
        "unit": "W",
        "device_class": "power",
    },
    "inverter_charging_power": {
        "register": "Inverter charging power",
        "name": "Inverter Charging Power",
        "unit": "W",
        "device_class": "power",
    },
    "output_voltage": {
        "register": "Effective value of output voltage",
        "name": "Output Voltage",
        "unit": "V",
        "device_class": "voltage",
    },
    "output_current": {
        "register": "Effective value of output current",
        "name": "Output Current",
        "unit": "A",
        "device_class": "current",
    },
    "output_frequency": {
        "register": "Output frequency",
        "name": "Output Frequency",
        "unit": "Hz",
    },
    "output_active_power": {
        "register": "Output active power",
        "name": "Output Active Power",
        "unit": "W",
        "device_class": "power",
    },
    "output_apparent_power": {
        "register": "Output apparent power",
        "name": "Output Apparent Power",
        "unit": "VA",
        "device_class": "power",
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
    "battery_current_filter_average": {
        "register": "Battery current filter average",
        "name": "Battery Current Filter Average",
        "unit": "A",
        "device_class": "current",
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
    "pv_charging_power": {
        "register": "Average PV charging power",
        "name": "PV Charging Power",
        "unit": "W",
        "device_class": "power",
    },
    "inverter_charging_current": {
        "register": "Average value of inverter charging current",
        "name": "Inverter Charging Current",
        "unit": "A",
        "device_class": "current",
    },
    "pv_charging_current": {
        "register": "Average PV charging current",
        "name": "PV Charging Current",
        "unit": "A",
        "device_class": "current",
    },
    "power_flow_status": {
        "register": "Power flow status",
        "name": "Power Flow Status",
        "decoder": decode_power_flow,
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
    "device_name": {
        "register": "Device name",
        "name": "Device Name",
        "writable": True,
    },
    "output_mode": {
        "register": "Output mode",
        "name": "Output Mode",
        "decoder": decode_output_mode,
        "encoder": encode_output_mode,
        "writable": True,
    },
    "output_priority": {
        "register": "Output priority",
        "name": "Output Priority",
        "decoder": decode_output_priority,
        "encoder": encode_output_priority,
        "writable": True,
    },
    "input_voltage_range": {
        "register": "Input voltage range",
        "name": "Input Voltage Range",
        "decoder": decode_input_voltage_range,
        "encoder": encode_input_voltage_range,
        "writable": True,
    },
    "buzzer_mode": {
        "register": "Buzzer mode",
        "name": "Buzzer Mode",
        "decoder": decode_buzzer_mode,
        "encoder": encode_buzzer_mode,
        "writable": True,
    },
    "lcd_backlight": {
        "register": "LCD backlight",
        "name": "LCD Backlight",
        "writable": True,
    },
    "lcd_return_home": {
        "register": "LCD automatically returns to the home page",
        "name": "LCD Return Home",
        "writable": True,
    },
    "energy_saving_mode_switch": {
        "register": "Energy saving mode switch",
        "name": "Energy Saving Mode Switch",
        "writable": True,
    },
    "overload_auto_restart": {
        "register": "Overload automatic restart",
        "name": "Overload Automatic Restart",
        "writable": True,
    },
    "over_temperature_auto_restart": {
        "register": "Over-temperature automatic restart",
        "name": "Over-temperature Automatic Restart",
        "writable": True,
    },
    "overload_bypass_enable": {
        "register": "Overload Bypass Enable",
        "name": "Overload Bypass Enable",
        "writable": True,
    },
    "battery_eq_mode_enable": {
        "register": "Battery Eq Mode Enable",
        "name": "Battery Eq Mode Enable",
        "writable": True,
    },
    "warning_mask": {
        "register": "Warning Mask [I]",
        "name": "Warning Mask",
        "decoder": decode_warnings,
        "writable": True,
    },
    "dry_contact": {
        "register": "Dry contact",
        "name": "Dry Contact",
        "writable": True,
    },
    "output_voltage_setting": {
        "register": "Output voltage",
        "name": "Output Voltage Setting",
        "unit": "V",
        "writable": True,
    },
    "output_frequency_setting": {
        "register": "Output frequency",
        "name": "Output Frequency Setting",
        "unit": "Hz",
        "writable": True,
    },
    "battery_type": {
        "register": "Battery type",
        "name": "Battery Type",
        "decoder": decode_battery_type,
        "encoder": encode_battery_type,
        "writable": True,
    },
    "battery_overvoltage_protection": {
        "register": "Battery overvoltage protection point [A]",
        "name": "Battery Overvoltage Protection",
        "unit": "V",
        "writable": True,
    },
    "max_charge_voltage": {
        "register": "Maximum charge voltage [B]",
        "name": "Maximum Charge Voltage",
        "unit": "V",
        "writable": True,
    },
    "floating_charge_voltage": {
        "register": "Floating charge voltage | [C]",
        "name": "Floating Charge Voltage",
        "unit": "V",
        "writable": True,
    },
    "mains_discharge_recovery_point": {
        "register": "Mains mode battery discharge recovery point [D]",
        "name": "Mains Discharge Recovery Point",
        "unit": "V",
        "writable": True,
    },
    "mains_low_voltage_protection_point": {
        "register": "Battery low voltage protection point in mains mode [E]",
        "name": "Mains Low Voltage Protection Point",
        "unit": "V",
        "writable": True,
    },
    "off_grid_low_voltage_protection_point": {
        "register": "Off-grid mode battery low voltage protection point [F]",
        "name": "Off-grid Low Voltage Protection Point",
        "unit": "V",
        "writable": True,
    },
    "cv_to_float_wait_time": {
        "register": "Waiting time from constant voltage to floating charge",
        "name": "CV to Float Wait Time",
        "unit": "min",
        "writable": True,
    },
    "battery_charging_priority": {
        "register": "Battery charging priority",
        "name": "Battery Charging Priority",
        "decoder": decode_battery_charging_priority,
        "encoder": encode_battery_charging_priority,
        "writable": True,
    },
    "max_charge_current": {
        "register": "Maximum charge current [G]",
        "name": "Maximum Charge Current",
        "unit": "A",
        "writable": True,
    },
    "max_mains_charging_current": {
        "register": "Maximum mains charging current [H]",
        "name": "Maximum Mains Charging Current",
        "unit": "A",
        "writable": True,
    },
    "eq_charging_voltage": {
        "register": "The charging voltage of Eq",
        "name": "Eq Charging Voltage",
        "unit": "V",
        "writable": True,
    },
    "battery_eq_time": {
        "register": "bat_eq_time",
        "name": "Battery Eq Time",
        "unit": "min",
        "writable": True,
    },
    "eq_timeout": {
        "register": "Eq timed out",
        "name": "Eq Timeout",
        "unit": "min",
        "writable": True,
    },
    "eq_interval": {
        "register": "Two-time Eq charge interval",
        "name": "Eq Interval",
        "unit": "day",
        "writable": True,
    },
    "automatic_mains_output_enable": {
        "register": "Automatic Mains Output Enable",
        "name": "Automatic Mains Output Enable",
        "writable": True,
    },
    "mains_discharge_soc_protection_value": {
        "register": "Mains mode battery discharge SOC protection value [K]",
        "name": "Mains Discharge SOC Protection Value",
        "unit": "%",
        "writable": True,
    },
    "mains_discharge_soc_recovery_value": {
        "register": "Mains mode battery discharge SOC recovery value",
        "name": "Mains Discharge SOC Recovery Value",
        "unit": "%",
        "writable": True,
    },
    "max_discharge_current_protection": {
        "register": "Maximum discharge current protection",
        "name": "Maximum Discharge Current Protection",
        "unit": "A",
        "writable": True,
    },
    "boot_mode": {
        "register": "Boot mode",
        "name": "Boot Mode",
        "decoder": decode_boot_mode,
        "encoder": encode_boot_mode,
        "writable": True,
    },
    "remote_switch": {
        "register": "Remote switch",
        "name": "Remote Switch",
        "decoder": decode_remote_switch,
        "encoder": encode_remote_switch,
        "writable": True,
    },
    "fault_info_query_index": {
        "register": "Fault Information Query Index",
        "name": "Fault Information Query Index",
        "writable": True,
    },
}

WRITABLE_REGISTERS = {
    slug: info["register"]
    for slug, info in REGISTER_MAP.items()
    if info.get("writable")
}

ENERGY_SENSORS = {
    "grid_import_energy": {
        "name": "Grid Import Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "grid_export_energy": {
        "name": "Grid Export Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "pv_energy": {
        "name": "PV Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "battery_charge_energy": {
        "name": "Battery Charge Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "battery_discharge_energy": {
        "name": "Battery Discharge Energy",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
}

ALL_SENSORS = {**REGISTER_MAP, **ENERGY_SENSORS}

ENERGY_STATE_FILE = Path("energy_state.json")


def load_energy_state() -> Dict[str, float]:
    """Load persistent energy values from disk."""
    if ENERGY_STATE_FILE.exists():
        try:
            with ENERGY_STATE_FILE.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            return {slug: float(data.get(slug, 0.0)) for slug in ENERGY_SENSORS}
        except (OSError, json.JSONDecodeError):
            pass
    return {slug: 0.0 for slug in ENERGY_SENSORS}


def save_energy_state(state: Dict[str, float]) -> None:
    """Persist energy values to disk."""
    try:
        with ENERGY_STATE_FILE.open("w", encoding="utf-8") as fp:
            json.dump(state, fp)
    except OSError:
        pass


def update_energy_state(
    data: Dict[str, Any], state: Dict[str, float], interval: float
) -> None:
    """Integrate power readings over interval to update energies."""
    hours = interval / 3600.0

    mains_power = float(data.get("mains_power", 0.0))
    if mains_power > 0:
        state["grid_import_energy"] += mains_power / 1000.0 * hours
    elif mains_power < 0:
        state["grid_export_energy"] += -mains_power / 1000.0 * hours

    pv_power = float(data.get("pv_power", 0.0))
    if pv_power > 0:
        state["pv_energy"] += pv_power / 1000.0 * hours

    battery_power = float(data.get("battery_power", 0.0))
    if battery_power > 0:
        state["battery_discharge_energy"] += battery_power / 1000.0 * hours
    elif battery_power < 0:
        state["battery_charge_energy"] += -battery_power / 1000.0 * hours


async def poll_once(client: ModbusRTUOverTCPClient) -> Dict[str, Any]:
    """Read all relevant registers and return slug-value mapping."""

    results: Dict[str, Any] = {}
    for slug, info in REGISTER_MAP.items():
        register_name = info["register"]
        try:
            raw_value = await client.read_register(register_name)
            decoder = info.get("decoder")
            if decoder:
                decoded = decoder(int(raw_value))
                if isinstance(decoded, list):
                    value = ", ".join(decoded) if decoded else "OK"
                else:
                    value = decoded
            else:
                value = raw_value
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to read register %s: %s; data is stale", register_name, exc
            )
            value = None
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
    for slug, info in ALL_SENSORS.items():
        writable = info.get("writable")
        base: Dict[str, Any] = {
            "name": f"VEVOR {info['name']}",
            "state_topic": f"{prefix}/{slug}",
            "unique_id": f"{prefix}_{slug}",
            "device": device_info,
        }
        if writable:
            command_topic = f"{prefix}/{slug}/set"
            if info.get("encoder") and info.get("decoder"):
                decoder = info["decoder"]
                options: list[str] = []
                if getattr(decoder, "__closure__", None):
                    mapping = decoder.__closure__[0].cell_contents
                    if isinstance(mapping, dict):
                        options = list(mapping.values())
                payload = {
                    **base,
                    "command_topic": command_topic,
                    "options": options,
                }
                topic = f"homeassistant/select/{prefix}_{slug}/config"
            else:
                payload = {
                    **base,
                    "command_topic": command_topic,
                    "min": info.get("min", 0),
                    "max": info.get("max", 1000),
                    "step": info.get("step", 1),
                }
                if unit := info.get("unit"):
                    payload["unit_of_measurement"] = unit
                    payload["state_class"] = "measurement"
                if device_class := info.get("device_class"):
                    payload["device_class"] = device_class
                topic = f"homeassistant/number/{prefix}_{slug}/config"
        else:
            payload = base.copy()
            if unit := info.get("unit"):
                payload["unit_of_measurement"] = unit
            state_class = info.get("state_class")
            if state_class:
                payload["state_class"] = state_class
            elif unit:
                payload["state_class"] = "measurement"
            if device_class := info.get("device_class"):
                payload["device_class"] = device_class
            topic = f"homeassistant/sensor/{prefix}_{slug}/config"
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
    modbus: ModbusRTUOverTCPClient,
    payload: str,
    slug: str | None = None,
    mqtt_client: mqtt.Client | None = None,
    prefix: str = "vevor_eml3500",
) -> None:
    """Handle MQTT command payload to write registers and republish state."""
    if slug is not None:
        data = {slug: payload}
    else:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return
        if not isinstance(data, dict):
            return
    for key, value in data.items():
        if key not in WRITABLE_REGISTERS:
            continue
        info = REGISTER_MAP[key]
        encoder = info.get("encoder")
        if encoder:
            try:
                value = encoder(value)
            except Exception:
                continue
        elif isinstance(value, str) and key != "device_name":
            continue
        if not isinstance(value, (int, float, str)):
            continue
        try:
            await modbus.write_register(
                info["register"], value if isinstance(value, str) else float(value)
            )
        except Exception:
            continue

        if mqtt_client:
            try:
                new_value = await modbus.read_register(info["register"])
            except Exception:
                continue
            decoder = info.get("decoder")
            if decoder:
                decoded = decoder(int(new_value))
                if isinstance(decoded, list):
                    new_value = ", ".join(decoded) if decoded else "OK"
                else:
                    new_value = decoded
            mqtt_client.publish(
                f"{prefix}/{key}", str(new_value), retain=True
            )


async def main(args: argparse.Namespace) -> None:
    modbus = ModbusRTUOverTCPClient(
        host=args.bridge_host,
        port=args.bridge_port,
        poll_interval=args.poll_interval,
    )

    mqtt_client: Optional[mqtt.Client] = None
    prefix = "vevor_eml3500"
    energy_state = load_energy_state()
    if args.mqtt_host:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if args.mqtt_username:
            mqtt_client.username_pw_set(
                args.mqtt_username, args.mqtt_password or ""
            )
        try:
            mqtt_client.connect(
                args.mqtt_host, args.mqtt_port, keepalive=args.mqtt_keepalive
            )
            mqtt_client.loop_start()
        except OSError as err:  # pragma: no cover - network error
            print(f"MQTT connect failed: {err}")
            mqtt_client = None
        else:
            data = await poll_once(modbus)
            all_data = {**data, **energy_state}
            publish_discovery(mqtt_client, prefix)
            for slug, value in all_data.items():
                mqtt_client.publish(f"{prefix}/{slug}", str(value), retain=True)
            publish_telemetry(mqtt_client, prefix, all_data)
            mqtt_client.subscribe(f"{prefix}/set")
            mqtt_client.subscribe(f"{prefix}/+/set")

            def on_message(
                client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
            ) -> None:
                topic = msg.topic
                payload = msg.payload.decode()
                if topic == f"{prefix}/set":
                    asyncio.create_task(
                        handle_command(
                            modbus, payload, mqtt_client=client, prefix=prefix
                        )
                    )
                else:
                    slug = topic.split("/")[-2]
                    asyncio.create_task(
                        handle_command(modbus, payload, slug, client, prefix)
                    )

            mqtt_client.on_message = on_message

    try:
        while True:
            data = await poll_once(modbus)
            update_energy_state(data, energy_state, args.poll_interval)
            all_data = {**data, **energy_state}
            if mqtt_client:
                try:
                    for slug, value in all_data.items():
                        mqtt_client.publish(
                            f"{prefix}/{slug}", str(value), retain=True
                        )
                    publish_telemetry(mqtt_client, prefix, all_data)
                except OSError as err:  # pragma: no cover - network error
                    print(f"MQTT publish failed: {err}")
                    mqtt_client.loop_stop()
                    mqtt_client = None
            elif args.mqtt_host:
                try:
                    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                    if args.mqtt_username:
                        mqtt_client.username_pw_set(
                            args.mqtt_username, args.mqtt_password or ""
                        )
                    mqtt_client.connect(
                        args.mqtt_host, args.mqtt_port, keepalive=args.mqtt_keepalive
                    )
                    mqtt_client.loop_start()
                except OSError as err:  # pragma: no cover - network error
                    print(f"MQTT reconnect failed: {err}")
                    mqtt_client = None
                else:
                    publish_discovery(mqtt_client, prefix)
                    for slug, value in all_data.items():
                        mqtt_client.publish(
                            f"{prefix}/{slug}", str(value), retain=True
                        )
                    publish_telemetry(mqtt_client, prefix, all_data)
                    mqtt_client.subscribe(f"{prefix}/set")
                    mqtt_client.subscribe(f"{prefix}/+/set")
                    mqtt_client.on_message = (
                        lambda c, u, m: asyncio.create_task(
                            handle_command(
                                modbus,
                                m.payload.decode(),
                                None
                                if m.topic == f"{prefix}/set"
                                else m.topic.split("/")[-2],
                                c,
                                prefix,
                            )
                        )
                    )
            save_energy_state(energy_state)
            await asyncio.sleep(args.poll_interval)
    finally:
        await modbus.close()
        if mqtt_client:
            mqtt_client.loop_stop()
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
    parser.add_argument("--mqtt-keepalive", type=int, default=60)
    asyncio.run(main(parser.parse_args()))
