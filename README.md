# ha-addon-vevor-eml3500-24l-rs232-wifi

Home Assistant add-on to communicate with and monitor the VEVOR EML3500-24L inverter via an RS232-to-WiFi bridge. Provides Modbus RTU over TCP polling, live telemetry (power, voltage, current, SOC), fault/status codes, and safe write commands. Includes auto-discovery, configurable update intervals, and robust reconnect/retry logic. MQTT export log.

## Novità 0.1.15

- Aggiornata la versione dell'add-on e documentate le dipendenze Python (`pymodbus`, `paho-mqtt`) necessarie per eseguire i test end-to-end del polling MQTT/Modbus.
- Pubblicazione degli aggiornamenti con un'unica entità per ogni comando: l'oggetto scoperto in Home Assistant mostra sia il valore attuale sia il controllo (evitando duplicati `sensor`/`number`).
- Descrizioni e attributi in italiano visibili da Home Assistant per tutti i sensori/controlli.
- Contatori energetici estesi per distinguere quanta energia proviene da rete, FV o batteria e dove viene indirizzata (utenze o batteria), con versioni giornaliere che si azzerano a mezzanotte.

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
| `mqtt.keepalive` | MQTT keepalive interval in seconds | `60` |
| `mqtt.username` | MQTT username (optional) | `""` |
| `mqtt.password` | MQTT password (optional) | `""` |

The `mqtt.keepalive` option controls how often the client pings the broker to keep the connection alive.

### Example add-on configuration

```yaml
bridge_host: 192.168.1.50
bridge_port: 23
poll_interval: 60
mqtt:
  host: 192.168.1.2
  port: 1883
  keepalive: 60
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

## Lovelace energy flow card example

If you use [`custom:energy-flow-card-plus`](https://github.com/flixlix/energy-flow-card-plus), you can start from the example in [docs/energy_flow_card_plus.yaml](docs/energy_flow_card_plus.yaml). It references the directional grid/battery sensors (import/export and charge/discharge) added in version 0.1.12 so the card and the Home Assistant energy dashboard both display positive-only values.

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

When discovery is enabled, entities are created with Italian names/descriptions and writable items appear as a single object that shows the current value and lets you send a command (no more duplicate `sensor` + `number`).

**Stato e telemetria di base**

- `sensor.vevor_faults`, `sensor.vevor_warnings`, `sensor.vevor_working_mode`.
- Rete/inverter/carico: tensione, frequenza, corrente e potenza (`sensor.vevor_mains_voltage`, `sensor.vevor_inverter_power`, `sensor.vevor_output_active_power`, ecc.).
- Batteria: `sensor.vevor_battery_voltage`, `sensor.vevor_battery_current`, `sensor.vevor_battery_power`, `sensor.vevor_battery_soc`, temperature interne.
- Fotovoltaico: `sensor.vevor_pv_voltage`, `sensor.vevor_pv_current`, `sensor.vevor_pv_power`, correnti/potenze di carica.

**Flussi di potenza direzionali**

- `sensor.vevor_grid_import_power`, `sensor.vevor_grid_export_power`.
- `sensor.vevor_battery_charge_power`, `sensor.vevor_battery_discharge_power`.
- `sensor.vevor_load_power`, `sensor.vevor_pv_to_battery_power`, `sensor.vevor_pv_to_load_power`.
- `sensor.vevor_grid_to_battery_power`, `sensor.vevor_grid_to_load_power`, `sensor.vevor_battery_to_load_power`.

**Contatori energetici (kWh)**

- Rete: `sensor.vevor_grid_import_energy`, `sensor.vevor_grid_export_energy`.
- Fotovoltaico: `sensor.vevor_pv_energy`, `sensor.vevor_pv_to_battery_energy`, `sensor.vevor_pv_to_load_energy`.
- Batteria: `sensor.vevor_battery_charge_energy`, `sensor.vevor_battery_discharge_energy`, `sensor.vevor_grid_to_battery_energy`.
- Utenze: `sensor.vevor_load_energy`, `sensor.vevor_load_from_grid_energy`, `sensor.vevor_load_from_pv_energy`, `sensor.vevor_load_from_battery_energy`, `sensor.vevor_load_from_offgrid_energy`.
- Ogni contatore ha il corrispettivo giornaliero (`*_today`) che si azzera automaticamente alle 00:00.

**Controlli (scrivibili)**

- I comandi vengono pubblicati come `number`, `select` o `switch` con la descrizione in italiano nel pannello Home Assistant; lo stato letto via Modbus resta visibile nella stessa entità.

## Energy dashboard

The add-on now publishes long-term energy counters alongside the instantaneous power sensors così puoi sapere, su base giornaliera (00:00 → 00:00), quanta energia proviene da rete/FV/batteria e dove viene consumata.

Use the following sensors as inputs to Home Assistant's Energy dashboard:

- Rete: `sensor.vevor_grid_import_energy` / `sensor.vevor_grid_export_energy`.
- Fotovoltaico: `sensor.vevor_pv_energy` più i flussi `sensor.vevor_pv_to_load_energy` e `sensor.vevor_pv_to_battery_energy`.
- Batteria: `sensor.vevor_battery_charge_energy`, `sensor.vevor_battery_discharge_energy`, `sensor.vevor_grid_to_battery_energy`.
- Carico: `sensor.vevor_load_energy` con la ripartizione `sensor.vevor_load_from_grid_energy`, `sensor.vevor_load_from_pv_energy`, `sensor.vevor_load_from_battery_energy`, `sensor.vevor_load_from_offgrid_energy`.

For convenience, every sensor has a daily-resetting companion (`*_today`) that restarts at midnight and can be charted directly nei dashboard.

To link the lifetime sensors in the Energy dashboard:

1. In Home Assistant, open **Settings → Dashboards → Energy**.
2. Under **Electricity grid**, select `sensor.vevor_grid_import_energy` for consumption and `sensor.vevor_grid_export_energy` for return (if applicable).
3. Under **Solar production**, choose `sensor.vevor_pv_energy`.
4. Under **Home batteries**, pick `sensor.vevor_battery_charge_energy` for charging and `sensor.vevor_battery_discharge_energy` for discharging.
5. Add any of the other flows above to custom dashboards/cards (e.g. energy-flow-card-plus) to visualise come la rete, il FV e la batteria alimentano le utenze nel corso delle 24 ore.

## Sviluppo e test

- Installa le dipendenze di sviluppo con `pip install -r requirements-dev.txt` per includere `pymodbus`, `paho-mqtt` e `pytest`.
- I test saltano automaticamente se le librerie opzionali non sono disponibili, ma per verificare l'intero ciclo di polling MQTT/Modbus è consigliato installarle.
- Esegui `python -m pytest` dalla root del repository per validare i decoder Modbus e la generazione dei payload MQTT/Home Assistant.

## RS232-to-WiFi bridge troubleshooting

- **Network reachability**: Verify the bridge responds on its IP and port using tools such as `telnet` or `nc`.
- **Serial wiring**: Confirm RX/TX/GND are correctly connected and that the bridge baud rate matches the inverter.
- **Power cycle**: Restart the bridge and inverter if communication stalls.
- **MQTT connection**: Ensure the broker address and credentials are correct.
- **Add-on logs**: Review the log output for connection errors or malformed Modbus responses.
