#!/command/with-contenv bashio
# shellcheck shell=bash
set -e

BRIDGE_HOST="$(bashio::config 'bridge_host')"
BRIDGE_PORT="$(bashio::config 'bridge_port')"
POLL_INTERVAL="$(bashio::config 'poll_interval')"
MQTT_HOST="$(bashio::config 'mqtt.host')"
MQTT_PORT="$(bashio::config 'mqtt.port')"
MQTT_USER="$(bashio::config 'mqtt.username')"
MQTT_PASS="$(bashio::config 'mqtt.password')"

bashio::log.info "Starting Vevor EML3500 poller"
exec python3 /app/poller.py \
    --bridge-host "${BRIDGE_HOST}" \
    --bridge-port "${BRIDGE_PORT}" \
    --poll-interval "${POLL_INTERVAL}" \
    --mqtt-host "${MQTT_HOST}" \
    --mqtt-port "${MQTT_PORT}" \
    --mqtt-username "${MQTT_USER}" \
    --mqtt-password "${MQTT_PASS}"
