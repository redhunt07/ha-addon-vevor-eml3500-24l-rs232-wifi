"""Poll VEVOR EML3500 registers and publish decoded statuses."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

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
        "name": "Allarmi di guasto",
        "description": "Codici di guasto attivi segnalati dall'inverter.",
        "decoder": decode_faults,
        "entity_category": "diagnostic",
    },
    "warnings": {
        "register": "Obtain the warning code after shield processing",
        "name": "Avvisi filtrati",
        "description": "Avvisi attivi considerando la maschera di esclusione.",
        "decoder": decode_warnings,
        "entity_category": "diagnostic",
    },
    "warnings_unmasked": {
        "register": "Obtain the warning code for unmasked processing",
        "name": "Avvisi non filtrati",
        "description": "Avvisi attivi senza applicare la maschera di esclusione.",
        "decoder": decode_warnings,
        "entity_category": "diagnostic",
    },
    "working_mode": {
        "register": "Working mode",
        "name": "Working Mode",
        "entity_category": "diagnostic",
        "decoder": decode_working_mode,
    },
    "mains_voltage": {
        "register": "Mains voltage effective value",
        "name": "Mains Voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "mains_frequency": {
        "register": "Mains frequency",
        "name": "Mains Frequency",
        "unit": "Hz",
        "device_class": "frequency",
        "state_class": "measurement",
    },
    "mains_power": {
        "register": "Average mains power",
        "name": "Mains Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "inverter_voltage": {
        "register": "Effective value of inverter voltage",
        "name": "Inverter Voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "inverter_current": {
        "register": "Effective value of inverter current",
        "name": "Inverter Current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "inverter_frequency": {
        "register": "Inverter frequency",
        "name": "Inverter Frequency",
        "unit": "Hz",
        "device_class": "frequency",
        "state_class": "measurement",
    },
    "inverter_power": {
        "register": "Inverter power average",
        "name": "Inverter Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "inverter_charging_power": {
        "register": "Inverter charging power",
        "name": "Inverter Charging Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "output_voltage": {
        "register": "Effective value of output voltage",
        "name": "Output Voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "output_current": {
        "register": "Effective value of output current",
        "name": "Output Current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "output_frequency": {
        "register": "Output frequency",
        "name": "Output Frequency",
        "unit": "Hz",
        "device_class": "frequency",
        "state_class": "measurement",
    },
    "output_active_power": {
        "register": "Output active power",
        "name": "Output Active Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "output_apparent_power": {
        "register": "Output apparent power",
        "name": "Output Apparent Power",
        "unit": "VA",
        "device_class": "apparent_power",
        "state_class": "measurement",
    },
    "battery_voltage": {
        "register": "Average battery voltage",
        "name": "Battery Voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "battery_current": {
        "register": "Average battery current",
        "name": "Battery Current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "battery_power": {
        "register": "Average battery power",
        "name": "Battery Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "battery_current_filter_average": {
        "register": "Battery current filter average",
        "name": "Battery Current Filter Average",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "battery_soc": {
        "register": "Battery percentage",
        "name": "Battery SOC",
        "unit": "%",
        "device_class": "battery",
        "state_class": "measurement",
    },
    "pv_voltage": {
        "register": "Average PV voltage",
        "name": "PV Voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "pv_current": {
        "register": "Average PV current",
        "name": "PV Current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "pv_power": {
        "register": "Average PV power",
        "name": "PV Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "pv_charging_power": {
        "register": "Average PV charging power",
        "name": "PV Charging Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
    },
    "inverter_charging_current": {
        "register": "Average value of inverter charging current",
        "name": "Inverter Charging Current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "pv_charging_current": {
        "register": "Average PV charging current",
        "name": "PV Charging Current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
    },
    "power_flow_status": {
        "register": "Power flow status",
        "name": "Power Flow Status",
        "decoder": decode_power_flow,
        "entity_category": "diagnostic",
    },
    "load_percent": {
        "register": "Percent of load",
        "name": "Load Percent",
        "unit": "%",
        "state_class": "measurement",
    },
    "rated_power": {
        "register": "Rated power",
        "name": "Rated Power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "entity_category": "diagnostic",
    },
    "rated_cell_count": {
        "register": "Rated number of cells [J]",
        "name": "Rated Cell Count",
        "unit": "pcs",
        "entity_category": "diagnostic",
    },
    "device_type": {
        "register": "Device type",
        "name": "Device Type",
        "entity_category": "diagnostic",
    },
    "device_serial_number": {
        "register": "Device serial number",
        "name": "Device Serial Number",
        "entity_category": "diagnostic",
    },
    "program_version": {
        "register": "Program version",
        "name": "Program Version",
        "entity_category": "diagnostic",
    },
    "dcdc_temperature": {
        "register": "DCDC temperature",
        "name": "DCDC Temperature",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "inverter_temperature": {
        "register": "Inverter temperature",
        "name": "Inverter Temperature",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
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
        "entity_category": "diagnostic",
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
    "force_eq_charge": {
        "register": "Forcing the charge of Eq",
        "name": "Force Eq Charge",
        "writable": True,
        "min": 0,
        "max": 1,
    },
    "exit_fault_lock": {
        "register": "Exits the fail-locked state",
        "name": "Exit Fault Lock",
        "writable": True,
        "min": 0,
        "max": 1,
    },
    "clear_records": {
        "register": "Clear the record",
        "name": "Clear Records",
        "writable": True,
        "min": 0,
        "max": 0xFF,
    },
    "reset_user_parameters": {
        "register": "Reset user parameters",
        "name": "Reset User Parameters",
        "writable": True,
        "min": 0,
        "max": 0xFF,
    },
    "protocol_identifier": {
        "register": "Invalid data",
        "name": "Protocol Identifier",
    },
    "fault_record_storage_info": {
        "register": "Fault record storage information [K]",
        "name": "Fault Record Storage Info",
        "entity_category": "diagnostic",
    },
    "fault_record": {
        "register": "Fault Record [M]",
        "name": "Fault Record",
        "entity_category": "diagnostic",
    },
    "run_log": {
        "register": "Run the log",
        "name": "Run Log",
        "entity_category": "diagnostic",
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
        "name": "Energia prelevata dalla rete",
        "description": "Energia totale assorbita dalla rete elettrica.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "grid_import_energy_today": {
        "name": "Energia prelevata oggi dalla rete",
        "description": "Energia assorbita dalla rete dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "grid_export_energy": {
        "name": "Energia immessa in rete",
        "description": "Energia totale inviata verso la rete elettrica.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "grid_export_energy_today": {
        "name": "Energia immessa oggi in rete",
        "description": "Energia inviata verso la rete dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "pv_energy": {
        "name": "Energia prodotta dai pannelli",
        "description": "Produzione fotovoltaica totale.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "pv_energy_today": {
        "name": "Energia FV prodotta oggi",
        "description": "Produzione fotovoltaica dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "pv_to_battery_energy": {
        "name": "Energia FV verso batteria",
        "description": "Energia solare utilizzata per caricare la batteria.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "pv_to_battery_energy_today": {
        "name": "Energia FV verso batteria oggi",
        "description": "Energia solare in carica batteria dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "pv_to_load_energy": {
        "name": "Energia FV verso utenze",
        "description": "Energia solare usata direttamente dal carico.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "pv_to_load_energy_today": {
        "name": "Energia FV verso utenze oggi",
        "description": "Energia solare diretta alle utenze dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "grid_to_battery_energy": {
        "name": "Energia di rete verso batteria",
        "description": "Energia di rete impiegata per la carica batteria.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "grid_to_battery_energy_today": {
        "name": "Energia di rete verso batteria oggi",
        "description": "Energia di rete in carica batteria dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "battery_charge_energy": {
        "name": "Energia caricata in batteria",
        "description": "Energia totale immessa nella batteria.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "battery_charge_energy_today": {
        "name": "Energia caricata in batteria oggi",
        "description": "Energia immessa in batteria dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "battery_discharge_energy": {
        "name": "Energia prelevata dalla batteria",
        "description": "Energia totale erogata dalla batteria.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "battery_discharge_energy_today": {
        "name": "Energia prelevata dalla batteria oggi",
        "description": "Energia erogata dalla batteria dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "load_energy": {
        "name": "Consumo totale utenze",
        "description": "Energia complessiva assorbita dal carico.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_energy_today": {
        "name": "Consumo utenze oggi",
        "description": "Energia consumata dalle utenze dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "load_from_grid_energy": {
        "name": "Consumo utenze da rete",
        "description": "Quota di consumo coperta dalla rete elettrica.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_from_grid_energy_today": {
        "name": "Consumo utenze da rete oggi",
        "description": "Quota di consumo da rete dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "load_from_pv_energy": {
        "name": "Consumo utenze da fotovoltaico",
        "description": "Quota di consumo coperta direttamente dai pannelli.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_from_pv_energy_today": {
        "name": "Consumo utenze da FV oggi",
        "description": "Quota FV per il carico dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "load_from_battery_energy": {
        "name": "Consumo utenze da batteria",
        "description": "Quota di consumo coperta dalla batteria in scarica.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_from_battery_energy_today": {
        "name": "Consumo utenze da batteria oggi",
        "description": "Scarica batteria usata dal carico dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
    "load_from_offgrid_energy": {
        "name": "Consumo utenze off‑grid",
        "description": "Quota di consumo coperta da fotovoltaico e batteria.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "load_from_offgrid_energy_today": {
        "name": "Consumo utenze off‑grid oggi",
        "description": "Energia fornita a carico da FV+batteria dalle 00:00.",
        "unit": "kWh",
        "device_class": "energy",
        "state_class": "total",
    },
}

DERIVED_SENSORS = {
    "grid_import_power": {
        "name": "Potenza importata da rete",
        "unit": "W",
        "device_class": "power",
        "description": "Potenza assorbita istantanea dalla rete.",
    },
    "grid_export_power": {
        "name": "Potenza immessa in rete",
        "unit": "W",
        "device_class": "power",
        "description": "Potenza inviata istantaneamente verso la rete.",
    },
    "battery_charge_power": {
        "name": "Potenza di carica batteria",
        "unit": "W",
        "device_class": "power",
        "description": "Potenza diretta in carica alla batteria.",
    },
    "battery_discharge_power": {
        "name": "Potenza di scarica batteria",
        "unit": "W",
        "device_class": "power",
        "description": "Potenza fornita dalla batteria in uscita.",
    },
    "load_power": {
        "name": "Potenza assorbita dal carico",
        "unit": "W",
        "device_class": "power",
        "description": "Potenza totale richiesta dalle utenze.",
    },
    "pv_to_battery_power": {
        "name": "Potenza FV verso batteria",
        "unit": "W",
        "device_class": "power",
        "description": "Quota solare impegnata per caricare la batteria.",
    },
    "pv_to_load_power": {
        "name": "Potenza FV verso utenze",
        "unit": "W",
        "device_class": "power",
        "description": "Quota solare che alimenta direttamente il carico.",
    },
    "grid_to_battery_power": {
        "name": "Potenza di rete verso batteria",
        "unit": "W",
        "device_class": "power",
        "description": "Quota di rete che carica la batteria.",
    },
    "grid_to_load_power": {
        "name": "Potenza di rete verso utenze",
        "unit": "W",
        "device_class": "power",
        "description": "Quota di rete che alimenta direttamente il carico.",
    },
    "battery_to_load_power": {
        "name": "Potenza batteria verso utenze",
        "unit": "W",
        "device_class": "power",
        "description": "Quota di scarica batteria che alimenta le utenze.",
    },
}

ENERGY_SENSOR_DAILY_MAP = {
    "grid_import_energy": "grid_import_energy_today",
    "grid_export_energy": "grid_export_energy_today",
    "pv_energy": "pv_energy_today",
    "pv_to_battery_energy": "pv_to_battery_energy_today",
    "pv_to_load_energy": "pv_to_load_energy_today",
    "grid_to_battery_energy": "grid_to_battery_energy_today",
    "battery_charge_energy": "battery_charge_energy_today",
    "battery_discharge_energy": "battery_discharge_energy_today",
    "load_energy": "load_energy_today",
    "load_from_grid_energy": "load_from_grid_energy_today",
    "load_from_pv_energy": "load_from_pv_energy_today",
    "load_from_battery_energy": "load_from_battery_energy_today",
    "load_from_offgrid_energy": "load_from_offgrid_energy_today",
}

ALL_SENSORS = {**REGISTER_MAP, **ENERGY_SENSORS, **DERIVED_SENSORS}

FRIENDLY_NAMES_IT = {
    "working_mode": "Modalità di lavoro",
    "mains_voltage": "Tensione rete",
    "mains_frequency": "Frequenza rete",
    "mains_power": "Potenza rete",
    "inverter_voltage": "Tensione inverter",
    "inverter_current": "Corrente inverter",
    "inverter_frequency": "Frequenza inverter",
    "inverter_power": "Potenza inverter",
    "inverter_charging_power": "Potenza ricarica inverter",
    "output_voltage": "Tensione uscita",
    "output_current": "Corrente uscita",
    "output_frequency": "Frequenza uscita",
    "output_active_power": "Potenza attiva uscita",
    "output_apparent_power": "Potenza apparente uscita",
    "battery_voltage": "Tensione batteria",
    "battery_current": "Corrente batteria",
    "battery_power": "Potenza batteria",
    "battery_current_filter_average": "Corrente batteria filtrata",
    "battery_soc": "SOC batteria",
    "pv_voltage": "Tensione FV",
    "pv_current": "Corrente FV",
    "pv_power": "Potenza FV",
    "pv_charging_power": "Potenza di carica FV",
    "inverter_charging_current": "Corrente di carica inverter",
    "pv_charging_current": "Corrente di carica FV",
    "power_flow_status": "Stato flussi di potenza",
    "load_percent": "Percentuale carico",
    "rated_power": "Potenza nominale",
    "rated_cell_count": "Numero celle nominali",
    "device_type": "Tipo dispositivo",
    "device_serial_number": "Numero di serie",
    "program_version": "Versione firmware",
    "dcdc_temperature": "Temperatura DCDC",
    "inverter_temperature": "Temperatura inverter",
    "battery_discharge_soc_limit": "Limite SOC di scarica",
    "device_name": "Nome dispositivo",
    "output_mode": "Modalità di uscita",
    "output_priority": "Priorità di uscita",
    "input_voltage_range": "Range tensione ingresso",
    "buzzer_mode": "Modalità cicalino",
    "lcd_backlight": "Retroilluminazione LCD",
    "lcd_return_home": "Ritorno automatico LCD",
    "energy_saving_mode_switch": "Risparmio energetico",
    "overload_auto_restart": "Riavvio automatico sovraccarico",
    "over_temperature_auto_restart": "Riavvio automatico sovratemperatura",
    "overload_bypass_enable": "Bypass sovraccarico",
    "battery_eq_mode_enable": "Equalizzazione batteria abilitata",
    "warning_mask": "Maschera avvisi",
    "dry_contact": "Contatto pulito",
    "output_voltage_setting": "Tensione di uscita impostata",
    "output_frequency_setting": "Frequenza di uscita impostata",
    "battery_type": "Tipo batteria",
    "battery_overvoltage_protection": "Protezione sovratensione batteria",
    "max_charge_voltage": "Tensione massima di carica",
    "floating_charge_voltage": "Tensione di mantenimento",
    "mains_discharge_recovery_point": "Recupero scarica in rete",
    "mains_low_voltage_protection_point": "Protezione bassa tensione rete",
    "off_grid_low_voltage_protection_point": "Protezione bassa tensione off‑grid",
    "cv_to_float_wait_time": "Attesa CV → mantenimento",
    "battery_charging_priority": "Priorità carica batteria",
    "max_charge_current": "Corrente massima di carica",
    "max_mains_charging_current": "Corrente massima di carica da rete",
    "eq_charging_voltage": "Tensione carica equalizzazione",
    "battery_eq_time": "Tempo equalizzazione batteria",
    "battery_eq_cycle": "Ciclo equalizzazione batteria",
    "battery_eq_time_on": "Durata equalizzazione",
    "battery_eq_current_limit": "Limite corrente equalizzazione",
    "battery_eq_voltage": "Tensione di equalizzazione",
    "battery_eq_restore_voltage": "Ripristino tensione di equalizzazione",
    "battery_eq_interval": "Intervallo equalizzazione",
    "battery_low_alarm": "Allarme batteria bassa",
    "low_voltage_power_off_point": "Soglia spegnimento bassa tensione",
    "grid_voltage_recovery_point": "Recupero tensione di rete",
    "grid_over_voltage_protection": "Protezione sovratensione rete",
    "grid_under_voltage_protection": "Protezione sottotensione rete",
    "grid_under_voltage_recovery_point": "Recupero sottotensione rete",
    "grid_over_voltage_recovery_point": "Recupero sovratensione rete",
    "backfeed_power_limit": "Limite immissione in rete",
    "remote_switch": "Interruttore remoto",
    "parallel_address": "Indirizzo parallelo",
    "voltage_offset_calibration": "Offset calibrazione tensione",
    "current_offset_calibration": "Offset calibrazione corrente",
    "enable_dry_contact": "Abilita contatto pulito",
    "dry_contact_status": "Stato contatto pulito",
    "fault_record_storage_info": "Archivio registri guasto",
    "fault_record": "Record di guasto",
    "run_log": "Log di esercizio",
    "fault_info_query_index": "Indice interrogazione guasto",
}

ENERGY_STATE_FILE = Path("energy_state.json")


def _safe_float(value: Any) -> float:
    """Convert value to float, returning 0.0 if conversion fails."""

    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_decoded_list(decoded: list[str]) -> str:
    """Convert decoded register list to a state-safe string."""

    if not decoded:
        return "OK"
    text = ", ".join(decoded)
    if len(text) > 250:
        return f"{text[:247]}..."
    return text


def _decode_value(info: Dict[str, Any], raw_value: Any) -> Any:
    """Decode a raw register value using the configured decoder."""

    decoder = info.get("decoder")
    if not decoder:
        return raw_value

    decoder_input = raw_value
    if isinstance(raw_value, list) and len(raw_value) == 2:
        decoder_input = (int(raw_value[0]) << 16) + int(raw_value[1])

    decoded = (
        decoder(int(decoder_input))
        if isinstance(decoder_input, (float, int))
        else decoder(decoder_input)
    )
    if isinstance(decoded, list):
        return _format_decoded_list(decoded)
    return decoded


def _friendly_name(slug: str, info: Dict[str, Any]) -> str:
    """Return the Italian-friendly name for Home Assistant."""

    return FRIENDLY_NAMES_IT.get(slug, info["name"])


def _build_attributes(slug: str, info: Dict[str, Any]) -> Dict[str, Any]:
    """Return MQTT attributes payload with Italian description."""

    descrizione = info.get("description") or _friendly_name(slug, info)
    if info.get("writable"):
        descrizione = f"Comando/configurazione: {descrizione}"
    else:
        descrizione = f"Misura: {descrizione}"

    base = {
        "descrizione": descrizione,
        "accesso": "lettura/scrittura" if info.get("writable") else "solo lettura",
    }
    if register := info.get("register"):
        base["registro_modbus"] = register
    if unit := info.get("unit"):
        base["unita"] = unit
    base["slug"] = slug
    return base


def add_derived_power_values(data: Dict[str, Any]) -> None:
    """Derive directional power sensors for energy dashboards."""

    mains_power = _safe_float(data.get("mains_power", 0.0))
    pv_power = max(_safe_float(data.get("pv_power", 0.0)), 0.0)
    output_power = max(
        _safe_float(data.get("output_active_power", data.get("inverter_power", 0.0))),
        0.0,
    )
    battery_power = _safe_float(data.get("battery_power", 0.0))

    grid_import_power = mains_power if mains_power > 0 else 0.0
    grid_export_power = -mains_power if mains_power < 0 else 0.0
    battery_discharge_power = battery_power if battery_power > 0 else 0.0
    battery_charge_power = -battery_power if battery_power < 0 else 0.0

    pv_to_battery = min(pv_power, battery_charge_power)
    pv_remaining = pv_power - pv_to_battery
    pv_to_load = min(pv_remaining, output_power)

    remaining_charge = max(battery_charge_power - pv_to_battery, 0.0)
    grid_to_battery = min(grid_import_power, remaining_charge)

    remaining_load_after_pv = max(output_power - pv_to_load, 0.0)
    grid_available_for_load = max(grid_import_power - grid_to_battery, 0.0)
    grid_to_load = min(grid_available_for_load, remaining_load_after_pv)

    remaining_load_after_pv_grid = max(remaining_load_after_pv - grid_to_load, 0.0)
    battery_to_load = min(battery_discharge_power, remaining_load_after_pv_grid)

    data["grid_import_power"] = grid_import_power
    data["grid_export_power"] = grid_export_power
    data["battery_discharge_power"] = battery_discharge_power
    data["battery_charge_power"] = battery_charge_power
    data["load_power"] = output_power
    data["pv_to_battery_power"] = pv_to_battery
    data["pv_to_load_power"] = pv_to_load
    data["grid_to_battery_power"] = grid_to_battery
    data["grid_to_load_power"] = grid_to_load
    data["battery_to_load_power"] = battery_to_load


def load_energy_state() -> Dict[str, Any]:
    """Load persistent energy values from disk."""
    state: Dict[str, Any] = {slug: 0.0 for slug in ENERGY_SENSORS}
    state["daily_date"] = datetime.now().date().isoformat()
    if ENERGY_STATE_FILE.exists():
        try:
            with ENERGY_STATE_FILE.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            for slug in ENERGY_SENSORS:
                state[slug] = _safe_float(data.get(slug, state[slug]))
            if isinstance(data.get("daily_date"), str):
                state["daily_date"] = data["daily_date"]
        except (OSError, json.JSONDecodeError):
            pass
    return state


def save_energy_state(state: Dict[str, Any]) -> None:
    """Persist energy values to disk."""
    try:
        with ENERGY_STATE_FILE.open("w", encoding="utf-8") as fp:
            payload = {
                slug: _safe_float(state.get(slug, 0.0))
                for slug in ENERGY_SENSORS
            }
            daily_date = state.get("daily_date")
            if not isinstance(daily_date, str):
                daily_date = datetime.now().date().isoformat()
            payload["daily_date"] = daily_date
            json.dump(payload, fp)
    except OSError:
        pass


def update_energy_state(
    data: Dict[str, Any], state: Dict[str, Any], interval: float
) -> None:
    """Integrate power readings over interval to update energies."""
    hours = interval / 3600.0

    current_date = datetime.now().date().isoformat()
    if state.get("daily_date") != current_date:
        for daily_slug in ENERGY_SENSOR_DAILY_MAP.values():
            state[daily_slug] = 0.0
        state["daily_date"] = current_date

    def _increment(slug: str, amount: float) -> None:
        state[slug] = _safe_float(state.get(slug, 0.0)) + amount

    mains_power = _safe_float(data.get("mains_power", 0.0))
    if mains_power > 0:
        energy = mains_power / 1000.0 * hours
        _increment("grid_import_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["grid_import_energy"], energy)
    elif mains_power < 0:
        energy = -mains_power / 1000.0 * hours
        _increment("grid_export_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["grid_export_energy"], energy)

    pv_power = max(_safe_float(data.get("pv_power", 0.0)), 0.0)
    if pv_power > 0:
        energy = pv_power / 1000.0 * hours
        _increment("pv_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["pv_energy"], energy)

    battery_power = _safe_float(data.get("battery_power", 0.0))
    if battery_power > 0:
        energy = battery_power / 1000.0 * hours
        _increment("battery_discharge_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["battery_discharge_energy"], energy)
    elif battery_power < 0:
        energy = -battery_power / 1000.0 * hours
        _increment("battery_charge_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["battery_charge_energy"], energy)

    pv_to_battery = _safe_float(data.get("pv_to_battery_power", 0.0))
    if pv_to_battery > 0:
        energy = pv_to_battery / 1000.0 * hours
        _increment("pv_to_battery_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["pv_to_battery_energy"], energy)

    grid_to_battery = _safe_float(data.get("grid_to_battery_power", 0.0))
    if grid_to_battery > 0:
        energy = grid_to_battery / 1000.0 * hours
        _increment("grid_to_battery_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["grid_to_battery_energy"], energy)

    pv_to_load = _safe_float(data.get("pv_to_load_power", 0.0))
    if pv_to_load > 0:
        energy = pv_to_load / 1000.0 * hours
        _increment("pv_to_load_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["pv_to_load_energy"], energy)

    grid_to_load = _safe_float(data.get("grid_to_load_power", 0.0))
    if grid_to_load > 0:
        energy = grid_to_load / 1000.0 * hours
        _increment("load_from_grid_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["load_from_grid_energy"], energy)

    battery_to_load = _safe_float(data.get("battery_to_load_power", 0.0))
    if battery_to_load > 0:
        energy = battery_to_load / 1000.0 * hours
        _increment("load_from_battery_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["load_from_battery_energy"], energy)

    if pv_to_load > 0 or battery_to_load > 0:
        offgrid_energy = (pv_to_load + battery_to_load) / 1000.0 * hours
        _increment("load_from_offgrid_energy", offgrid_energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["load_from_offgrid_energy"], offgrid_energy)

    load_power = _safe_float(data.get("load_power", 0.0))
    if load_power > 0:
        energy = load_power / 1000.0 * hours
        _increment("load_energy", energy)
        _increment(ENERGY_SENSOR_DAILY_MAP["load_energy"], energy)

    pv_only_load = pv_to_load / 1000.0 * hours
    if pv_only_load > 0:
        _increment("load_from_pv_energy", pv_only_load)
        _increment(ENERGY_SENSOR_DAILY_MAP["load_from_pv_energy"], pv_only_load)


async def poll_once(client: ModbusRTUOverTCPClient) -> Tuple[Dict[str, Any], str]:
    """Read all relevant registers and return slug-value mapping with timestamp."""

    results: Dict[str, Any] = {}
    for slug, info in REGISTER_MAP.items():
        register_name = info["register"]
        try:
            raw_value = await client.read_register(register_name)
            value = _decode_value(info, raw_value)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to read register %s: %s; data is stale", register_name, exc
            )
            value = None
        results[slug] = value
    add_derived_power_values(results)
    return results, datetime.now(UTC).isoformat().replace("+00:00", "Z")


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
        entity_category = info.get("entity_category")
        if not entity_category and writable:
            entity_category = "config"
        base: Dict[str, Any] = {
            "name": f"VEVOR {_friendly_name(slug, info)}",
            "state_topic": f"{prefix}/{slug}",
            "unique_id": f"{prefix}_{slug}",
            "device": device_info,
            "availability_topic": f"{prefix}/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "json_attributes_topic": f"{prefix}/{slug}/attributes",
        }
        if entity_category:
            base["entity_category"] = entity_category
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
        client.publish(
            f"{prefix}/{slug}/attributes",
            json.dumps(_build_attributes(slug, info)),
            retain=True,
        )
    last_update_payload = {
        "name": "VEVOR Last Update",
        "state_topic": f"{prefix}/last_update",
        "unique_id": f"{prefix}_last_update",
        "device": device_info,
        "device_class": "timestamp",
    }
    client.publish(
        f"homeassistant/sensor/{prefix}_last_update/config",
        json.dumps(last_update_payload),
        retain=True,
    )


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
            logger.warning("Unknown writable register: %s", key)
            if mqtt_client:
                mqtt_client.publish(
                    f"{prefix}/error", f"Unknown writable register: {key}"
                )
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
        except Exception as err:
            logger.error("Write failed for %s: %s", key, err)
            if mqtt_client:
                mqtt_client.publish(
                    f"{prefix}/error", f"Write failed for {key}: {err}"
                )
            continue

        if mqtt_client:
            try:
                new_value = await modbus.read_register(info["register"])
            except Exception:
                continue
            new_value = _decode_value(info, new_value)
            mqtt_client.publish(
                f"{prefix}/{key}", str(new_value), retain=True
            )


async def main(args: argparse.Namespace) -> None:
    modbus = ModbusRTUOverTCPClient(
        host=args.bridge_host,
        port=args.bridge_port,
        poll_interval=args.poll_interval,
    )
    loop = asyncio.get_running_loop()

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
            mqtt_client.publish(
                f"{prefix}/availability", "online", retain=True
            )
        except OSError as err:  # pragma: no cover - network error
            print(f"MQTT connect failed: {err}")
            mqtt_client = None
        else:
            data, last_update = await poll_once(modbus)
            all_data = {**data, **energy_state, "last_update": last_update}
            publish_discovery(mqtt_client, prefix)
            for slug, value in all_data.items():
                payload = "unknown" if value is None else str(value)
                mqtt_client.publish(f"{prefix}/{slug}", payload, retain=True)
            publish_telemetry(mqtt_client, prefix, all_data)
            mqtt_client.subscribe(f"{prefix}/set")
            mqtt_client.subscribe(f"{prefix}/+/set")

            def on_message(
                client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage
            ) -> None:
                topic = msg.topic
                payload = msg.payload.decode()
                if topic == f"{prefix}/set":
                    asyncio.run_coroutine_threadsafe(
                        handle_command(
                            modbus, payload, mqtt_client=client, prefix=prefix
                        ),
                        loop,
                    )
                else:
                    slug = topic.split("/")[-2]
                    asyncio.run_coroutine_threadsafe(
                        handle_command(modbus, payload, slug, client, prefix),
                        loop,
                    )

            mqtt_client.on_message = on_message

    try:
        while True:
            data, last_update = await poll_once(modbus)
            update_energy_state(data, energy_state, args.poll_interval)
            all_data = {**data, **energy_state, "last_update": last_update}
            if mqtt_client:
                try:
                    for slug, value in all_data.items():
                        payload = "unknown" if value is None else str(value)
                        mqtt_client.publish(
                            f"{prefix}/{slug}", payload, retain=True
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
                    mqtt_client.publish(
                        f"{prefix}/availability", "online", retain=True
                    )
                except OSError as err:  # pragma: no cover - network error
                    print(f"MQTT reconnect failed: {err}")
                    mqtt_client = None
                else:
                    publish_discovery(mqtt_client, prefix)
                    for slug, value in all_data.items():
                        payload = "unknown" if value is None else str(value)
                        mqtt_client.publish(
                            f"{prefix}/{slug}", payload, retain=True
                        )
                    publish_telemetry(mqtt_client, prefix, all_data)
                    mqtt_client.subscribe(f"{prefix}/set")
                    mqtt_client.subscribe(f"{prefix}/+/set")
                    mqtt_client.on_message = (
                        lambda c, u, m: asyncio.run_coroutine_threadsafe(
                            handle_command(
                                modbus,
                                m.payload.decode(),
                                None
                                if m.topic == f"{prefix}/set"
                                else m.topic.split("/")[-2],
                                c,
                                prefix,
                            ),
                            loop,
                        )
                    )
            save_energy_state(energy_state)
            await asyncio.sleep(args.poll_interval)
    finally:
        await modbus.close()
        if mqtt_client:
            mqtt_client.publish(
                f"{prefix}/availability", "offline", retain=True
            )
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
