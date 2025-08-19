# ha-addon-vevor-eml3500-24l-rs232-wifi

Home Assistant add-on to communicate with and monitor the VEVOR EML3500-24L inverter via an RS232-to-WiFi bridge. Provides Modbus RTU over TCP polling, live telemetry (power, voltage, current, SOC), fault/status codes, and safe write commands. Includes auto-discovery, configurable update intervals, and robust reconnect/retry logic. MQTT export log.

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store**.
2. Use the menu in the top-right to add the repository URL for this add-on.
3. Locate **VEVOR EML3500-24L RS232 Wi-Fi bridge** and click **Install**.
4. Configure the options described below and start the add-on.
5. Check the add-on logs to confirm successful connection to the bridge and MQTT broker.

## Configuration

| Option | Description | Default |
| ------ | ----------- | ------- |
| `bridge_host` | IP address of the RS232-to-WiFi bridge | `192.168.1.50` |
| `bridge_port` | TCP port exposed by the bridge | `23` |
| `poll_interval` | Time between Modbus polls in seconds | `60` |
| `mqtt.host` | MQTT broker IP or hostname | `192.168.1.2` |
| `mqtt.port` | MQTT broker port | `1883` |
| `mqtt.username` | MQTT username (optional) | `""` |
| `mqtt.password` | MQTT password (optional) | `""` |

### Example add-on configuration

```yaml
bridge_host: 192.168.1.50
bridge_port: 23
poll_interval: 60
mqtt:
  host: 192.168.1.2
  port: 1883
  username: homeassistant
  password: secret
```

### Example Home Assistant `configuration.yaml`

If MQTT discovery is disabled or you want to manually define sensors:

```yaml
mqtt:
  sensor:
    - name: "VEVOR Faults"
      state_topic: "vevor_eml3500/faults"
    - name: "VEVOR Warnings"
      state_topic: "vevor_eml3500/warnings"
```

## MQTT topics

| Topic | Payload |
| ----- | ------- |
| `vevor_eml3500/faults` | Current inverter fault state (retained) |
| `vevor_eml3500/warnings` | Current inverter warning state (retained) |
| `vevor_eml3500/working_mode` | Current working mode |
| `vevor_eml3500/mains_voltage` | Mains voltage (V) |
| `vevor_eml3500/mains_frequency` | Mains frequency (Hz) |
| `vevor_eml3500/mains_power` | Average mains power (W) |
| `vevor_eml3500/inverter_voltage` | Inverter output voltage (V) |
| `vevor_eml3500/inverter_current` | Inverter output current (A) |
| `vevor_eml3500/inverter_frequency` | Inverter output frequency (Hz) |
| `vevor_eml3500/inverter_power` | Inverter output power (W) |
| `vevor_eml3500/inverter_charging_power` | Inverter charging power (W) |
| `vevor_eml3500/output_voltage` | Output voltage (V) |
| `vevor_eml3500/output_current` | Output current (A) |
| `vevor_eml3500/output_frequency` | Output frequency (Hz) |
| `vevor_eml3500/output_active_power` | Output active power (W) |
| `vevor_eml3500/output_apparent_power` | Output apparent power (VA) |
| `vevor_eml3500/battery_voltage` | Battery voltage (V) |
| `vevor_eml3500/battery_current` | Battery current (A) |
| `vevor_eml3500/battery_power` | Battery power (W) |
| `vevor_eml3500/battery_current_filter_average` | Battery current filter average (A) |
| `vevor_eml3500/battery_soc` | Battery state of charge (%) |
| `vevor_eml3500/pv_voltage` | PV input voltage (V) |
| `vevor_eml3500/pv_current` | PV input current (A) |
| `vevor_eml3500/pv_power` | PV input power (W) |
| `vevor_eml3500/pv_charging_power` | PV charging power (W) |
| `vevor_eml3500/inverter_charging_current` | Inverter charging current (A) |
| `vevor_eml3500/pv_charging_current` | PV charging current (A) |
| `vevor_eml3500/power_flow_status` | Power flow status |
| `vevor_eml3500/load_percent` | Load percentage (%) |
| `vevor_eml3500/dcdc_temperature` | DCDC temperature (°C) |
| `vevor_eml3500/inverter_temperature` | Inverter temperature (°C) |
| `vevor_eml3500/telemetry` | JSON payload containing all fields |
| `homeassistant/sensor/vevor_eml3500_<slug>/config` | MQTT discovery for each sensor |

### Telemetry payload example

```json
{
  "faults": "OK",
  "warnings": "OK",
  "working_mode": "Mains mode",
  "mains_voltage": 230.0,
  "mains_frequency": 50.0,
  "mains_power": 1000.0,
  "inverter_voltage": 230.0,
  "inverter_current": 5.0,
  "inverter_frequency": 50.0,
  "inverter_power": 1200.0,
  "inverter_charging_power": 500.0,
  "output_voltage": 230.0,
  "output_current": 5.0,
  "output_frequency": 50.0,
  "output_active_power": 1000.0,
  "output_apparent_power": 1100.0,
  "battery_voltage": 48.0,
  "battery_current": -10.0,
  "battery_power": -480.0,
  "battery_current_filter_average": -9.5,
  "battery_soc": 80,
  "pv_voltage": 150.0,
  "pv_current": 4.0,
  "pv_power": 600.0,
  "pv_charging_power": 400.0,
  "inverter_charging_current": 10.0,
  "pv_charging_current": 6.0,
  "power_flow_status": "PV connected, Mains connected, Battery charging, Load powered",
  "load_percent": 30,
  "dcdc_temperature": 35.0,
  "inverter_temperature": 40.0,
  "battery_discharge_soc_limit": 20,
  "device_name": "VEVOR",
  "output_mode": "single machine",
  "output_priority": "Main-PV-Battery (UTI)",
  "input_voltage_range": "APL",
  "buzzer_mode": "mute",
  "lcd_backlight": 1,
  "lcd_return_home": 0,
  "energy_saving_mode_switch": 0,
  "overload_auto_restart": 1,
  "over_temperature_auto_restart": 1,
  "overload_bypass_enable": 0,
  "battery_eq_mode_enable": 0,
  "warning_mask": "OK",
  "dry_contact": 0,
  "output_voltage_setting": 230,
  "output_frequency_setting": 50,
  "battery_type": "AGM",
  "battery_overvoltage_protection": 63.0,
  "max_charge_voltage": 58.4,
  "floating_charge_voltage": 54.0,
  "mains_discharge_recovery_point": 52.0,
  "mains_low_voltage_protection_point": 48.0,
  "off_grid_low_voltage_protection_point": 46.0,
  "cv_to_float_wait_time": 120,
  "battery_charging_priority": "mains first",
  "max_charge_current": 60,
  "max_mains_charging_current": 30,
  "eq_charging_voltage": 58.8,
  "battery_eq_time": 30,
  "eq_timeout": 180,
  "eq_interval": 30,
  "automatic_mains_output_enable": 1,
  "mains_discharge_soc_protection_value": 30,
  "mains_discharge_soc_recovery_value": 40,
  "max_discharge_current_protection": 80,
  "boot_mode": "local or remote",
  "remote_switch": "remote power-on",
  "fault_info_query_index": 0
}
```

## Register map

The complete register table is available in [docs/registers.md](docs/registers.md).

## Writable entities

For each register, the poller publishes the latest value to `{prefix}/{slug}`. The default prefix is `vevor_eml3500`, so the mains voltage is exposed on `vevor_eml3500/mains_voltage`.

Writable registers are updated by publishing to `{prefix}/set` with a JSON payload mapping slugs to the desired values. Available command slugs are:

| Slug | Description | Example payload |
| ---- | ----------- | --------------- |
| `warnings` | Clear warning code | `{"warnings": 0}` |
| `battery_discharge_soc_limit` | Set battery discharge SOC limit | `{"battery_discharge_soc_limit": 20}` |
| `device_name` | Set device name | `{"device_name": "MyDevice"}` |
| `output_mode` | Set output mode | `{"output_mode": "parallel"}` |
| `output_priority` | Set output priority | `{"output_priority": "PV-mains-battery (SOL)"}` |
| `input_voltage_range` | Set input voltage range | `{"input_voltage_range": "UPS"}` |
| `buzzer_mode` | Set buzzer mode | `{"buzzer_mode": "mute"}` |
| `lcd_backlight` | Set LCD backlight | `{"lcd_backlight": 1}` |
| `lcd_return_home` | LCD automatically returns to home | `{"lcd_return_home": 1}` |
| `energy_saving_mode_switch` | Toggle energy saving mode | `{"energy_saving_mode_switch": 1}` |
| `overload_auto_restart` | Toggle overload auto restart | `{"overload_auto_restart": 1}` |
| `over_temperature_auto_restart` | Toggle over-temperature auto restart | `{"over_temperature_auto_restart": 1}` |
| `overload_bypass_enable` | Enable overload bypass | `{"overload_bypass_enable": 1}` |
| `battery_eq_mode_enable` | Enable battery EQ mode | `{"battery_eq_mode_enable": 1}` |
| `warning_mask` | Set warning mask bits | `{"warning_mask": 0}` |
| `dry_contact` | Control dry contact | `{"dry_contact": 1}` |
| `output_voltage_setting` | Output voltage setting | `{"output_voltage_setting": 230}` |
| `output_frequency_setting` | Output frequency setting | `{"output_frequency_setting": 50}` |
| `battery_type` | Set battery type | `{"battery_type": "AGM"}` |
| `battery_overvoltage_protection` | Battery overvoltage protection | `{"battery_overvoltage_protection": 63}` |
| `max_charge_voltage` | Maximum charge voltage | `{"max_charge_voltage": 58.4}` |
| `floating_charge_voltage` | Floating charge voltage | `{"floating_charge_voltage": 54}` |
| `mains_discharge_recovery_point` | Mains discharge recovery point | `{"mains_discharge_recovery_point": 52}` |
| `mains_low_voltage_protection_point` | Mains low voltage protection | `{"mains_low_voltage_protection_point": 48}` |
| `off_grid_low_voltage_protection_point` | Off-grid low voltage protection | `{"off_grid_low_voltage_protection_point": 46}` |
| `cv_to_float_wait_time` | CV to float wait time (min) | `{"cv_to_float_wait_time": 120}` |
| `battery_charging_priority` | Battery charging priority | `{"battery_charging_priority": "mains first"}` |
| `max_charge_current` | Maximum charge current | `{"max_charge_current": 60}` |
| `max_mains_charging_current` | Max mains charging current | `{"max_mains_charging_current": 30}` |
| `eq_charging_voltage` | Equalization charging voltage | `{"eq_charging_voltage": 58.8}` |
| `battery_eq_time` | Battery EQ time (min) | `{"battery_eq_time": 30}` |
| `eq_timeout` | EQ timeout (min) | `{"eq_timeout": 180}` |
| `eq_interval` | EQ interval (days) | `{"eq_interval": 30}` |
| `automatic_mains_output_enable` | Automatic mains output enable | `{"automatic_mains_output_enable": 1}` |
| `mains_discharge_soc_protection_value` | Mains discharge SOC protection (%) | `{"mains_discharge_soc_protection_value": 30}` |
| `mains_discharge_soc_recovery_value` | Mains discharge SOC recovery (%) | `{"mains_discharge_soc_recovery_value": 40}` |
| `max_discharge_current_protection` | Max discharge current protection | `{"max_discharge_current_protection": 80}` |
| `boot_mode` | Boot mode | `{"boot_mode": "remote only"}` |
| `remote_switch` | Remote switch | `{"remote_switch": "remote power-on"}` |
| `fault_info_query_index` | Fault info query index | `{"fault_info_query_index": 0}` |

## Script example

The following Home Assistant script publishes a command to the inverter via MQTT:

```yaml
script:
  vevor_clear_warnings:
    alias: Clear VEVOR warnings
    sequence:
      - service: mqtt.publish
        data:
          topic: vevor_eml3500/set
          payload: '{"warnings": 0}'
```

## Dashboard YAML

A full dashboard example is available in [docs/dashboard_example.yaml](docs/dashboard_example.yaml).

```yaml
views:
  - title: VEVOR Inverter
    cards:
      - type: entities
        entities:
          - sensor.vevor_working_mode
          - sensor.vevor_mains_voltage
          - sensor.vevor_mains_frequency
          - sensor.vevor_mains_power
          - sensor.vevor_inverter_voltage
          - sensor.vevor_inverter_current
          - sensor.vevor_inverter_frequency
          - sensor.vevor_inverter_power
          - sensor.vevor_inverter_charging_power
          - sensor.vevor_output_voltage
          - sensor.vevor_output_current
          - sensor.vevor_output_frequency
          - sensor.vevor_output_active_power
          - sensor.vevor_output_apparent_power
          - sensor.vevor_battery_voltage
          - sensor.vevor_battery_current
          - sensor.vevor_battery_power
          - sensor.vevor_battery_current_filter_average
          - sensor.vevor_battery_soc
          - sensor.vevor_pv_voltage
          - sensor.vevor_pv_current
          - sensor.vevor_pv_power
          - sensor.vevor_pv_charging_power
          - sensor.vevor_inverter_charging_current
          - sensor.vevor_pv_charging_current
          - sensor.vevor_power_flow_status
          - sensor.vevor_load_percent
          - sensor.vevor_dcdc_temperature
          - sensor.vevor_inverter_temperature
          - sensor.vevor_faults
          - sensor.vevor_warnings
      - type: gauge
        entity: sensor.vevor_battery_soc
        min: 0
        max: 100
        name: Battery SOC
      - type: entities
        title: Controls
        entities:
          - entity: number.vevor_warnings
            name: Clear Warnings
          - entity: number.vevor_battery_discharge_soc_limit
            name: Battery SOC Limit
          - entity: select.vevor_output_mode
            name: Output Mode
          - entity: number.vevor_output_voltage_setting
            name: Output Voltage
          - entity: number.vevor_max_charge_current
            name: Max Charge Current
          - entity: select.vevor_battery_type
            name: Battery Type
          - entity: select.vevor_remote_switch
            name: Remote Switch
```

When MQTT discovery is enabled, control entities such as `number` and `select` are created automatically; no manual configuration in `configuration.yaml` is required.

## Entities

When discovery is enabled, the following entities are created in Home Assistant:

- `sensor.vevor_faults` – reports the most recent fault or `OK`.
- `sensor.vevor_warnings` – reports the most recent warning or `OK`.
- `sensor.vevor_working_mode` – current working mode.
- `sensor.vevor_mains_voltage` – mains voltage.
- `sensor.vevor_mains_frequency` – mains frequency.
- `sensor.vevor_mains_power` – average mains power.
- `sensor.vevor_inverter_voltage` – inverter output voltage.
- `sensor.vevor_inverter_current` – inverter output current.
- `sensor.vevor_inverter_frequency` – inverter output frequency.
- `sensor.vevor_inverter_power` – inverter output power.
- `sensor.vevor_inverter_charging_power` – inverter charging power.
- `sensor.vevor_output_voltage` – output voltage.
- `sensor.vevor_output_current` – output current.
- `sensor.vevor_output_frequency` – output frequency.
- `sensor.vevor_output_active_power` – output active power.
- `sensor.vevor_output_apparent_power` – output apparent power.
- `sensor.vevor_battery_voltage` – battery voltage.
- `sensor.vevor_battery_current` – battery current.
- `sensor.vevor_battery_power` – battery power.
- `sensor.vevor_battery_current_filter_average` – battery current filter average.
- `sensor.vevor_battery_soc` – battery state of charge.
- `sensor.vevor_pv_voltage` – PV input voltage.
- `sensor.vevor_pv_current` – PV input current.
- `sensor.vevor_pv_power` – PV input power.
- `sensor.vevor_pv_charging_power` – PV charging power.
- `sensor.vevor_inverter_charging_current` – inverter charging current.
- `sensor.vevor_pv_charging_current` – PV charging current.
- `sensor.vevor_power_flow_status` – decoded power flow status.
- `sensor.vevor_load_percent` – load percentage.
- `sensor.vevor_dcdc_temperature` – DCDC temperature.
- `sensor.vevor_inverter_temperature` – inverter temperature.

## Energy dashboard

The add-on exposes several power sensors that can feed Home Assistant's Energy dashboard:

- `sensor.vevor_mains_power` – power imported from the grid
- `sensor.vevor_pv_power` – photovoltaic (PV) production
- `sensor.vevor_output_active_power` – load consumption
- `sensor.vevor_battery_power` – battery charge (negative) / discharge (positive)

Convert these to cumulative energy sensors using the Riemann sum integration platform:

```yaml
sensor:
  - platform: integration
    source: sensor.vevor_pv_power
    name: vevor_pv_energy
    unit_prefix: k
    round: 2

  - platform: integration
    source: sensor.vevor_mains_power
    name: vevor_grid_energy
    unit_prefix: k
    round: 2

  - platform: integration
    source: sensor.vevor_output_active_power
    name: vevor_load_energy
    unit_prefix: k
    round: 2

  - platform: integration
    source: sensor.vevor_battery_power
    name: vevor_battery_energy
    unit_prefix: k
    round: 2
```

To link these sensors in the Energy dashboard:

1. In Home Assistant, open **Settings → Dashboards → Energy**.
2. Under **Electricity grid**, select `sensor.vevor_grid_energy` for consumption (and return if applicable).
3. Under **Solar production**, choose `sensor.vevor_pv_energy`.
4. Under **Home batteries**, pick `sensor.vevor_battery_energy`.
5. Under **Individual devices**, add `sensor.vevor_load_energy` to track load usage.
6. Save the dashboard and allow data to accumulate.

## RS232-to-WiFi bridge troubleshooting

- **Network reachability**: Verify the bridge responds on its IP and port using tools such as `telnet` or `nc`.
- **Serial wiring**: Confirm RX/TX/GND are correctly connected and that the bridge baud rate matches the inverter.
- **Power cycle**: Restart the bridge and inverter if communication stalls.
- **MQTT connection**: Ensure the broker address and credentials are correct.
- **Add-on logs**: Review the log output for connection errors or malformed Modbus responses.
