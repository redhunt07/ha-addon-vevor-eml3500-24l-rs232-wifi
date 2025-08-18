# ha-addon-vevor-eml3500-24l-rs232-wifi

Home Assistant add-on to communicate with and monitor the VEVOR EML3500-24L inverter via an RS232-to-WiFi bridge. Provides Modbus RTU over TCP polling, live telemetry (power, voltage, current, SOC), fault/status codes, and safe write commands. Includes auto-discovery, configurable update intervals, and robust reconnect/retry logic. MQTT export log.

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store**.
2. Use the menu in the top-right to add the repository URL for this add-on.
3. Locate **VEVOR EML3500 RS232 Wi-Fi bridge** and click **Install**.
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
| `vevor_eml3500/telemetry` | JSON payload containing `faults` and `warnings` |
| `homeassistant/sensor/vevor_eml3500_faults/config` | MQTT discovery for faults sensor |
| `homeassistant/sensor/vevor_eml3500_warnings/config` | MQTT discovery for warnings sensor |

## Entities

When discovery is enabled, the following entities are created in Home Assistant:

- `sensor.vevor_faults` – reports the most recent fault or `OK`.
- `sensor.vevor_warnings` – reports the most recent warning or `OK`.

## RS232-to-WiFi bridge troubleshooting

- **Network reachability**: Verify the bridge responds on its IP and port using tools such as `telnet` or `nc`.
- **Serial wiring**: Confirm RX/TX/GND are correctly connected and that the bridge baud rate matches the inverter.
- **Power cycle**: Restart the bridge and inverter if communication stalls.
- **MQTT connection**: Ensure the broker address and credentials are correct.
- **Add-on logs**: Review the log output for connection errors or malformed Modbus responses.
