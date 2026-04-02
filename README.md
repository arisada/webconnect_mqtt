# Porsche Webconnect MQTT Bridge

Async Python bridge that connects to a Webconnect-compatible wallbox via WebSocket and publishes all available metrics to MQTT using Home Assistant MQTT Discovery.

The implementation is intentionally generic. While developed against a Porsche-branded wallbox, the Webconnect backend appears to be shared across multiple VW-group vehicles and chargers.

---

## Features

* Async WebSocket client
* Automatic Home Assistant MQTT Discovery
* Lightweight Docker deployment

No filtering, deduplication, or rate limiting is implemented intentionally — Home Assistant handles that layer better.

---

## Architecture

```
Wallbox (WebSocket/TCP-IP)
        ↓
Python bridge (asyncio + aiomqtt)
        ↓
MQTT Broker
        ↓
Home Assistant (MQTT Discovery)
```

Each metric is:

* Published to a state topic
* Registered via MQTT discovery
* Associated with a single logical device
* Exposed with unit metadata

---

## Requirements

* Python 3.11+
* MQTT broker (e.g. Mosquitto)
* Home Assistant with MQTT integration enabled

---

## Configuration

The bridge uses a `config.json` file.

Example:

```json
{
  "charger": {
    "host": "porsche-charger.lan",
    "password": "your-user-password"
  },
  "mqtt": {
    "host": "homeassistant.lan",
    "port": 1883,
    "username": "homeassistant",
    "password": "password",
    "base_topic": "porsche_charger"
  }
}

```

Set the host names accordingly. If more than one device is used, base_topic should be changed.
The metrics are fetched from WebSocket without authentication, but authentication is required to perform Current Limit changes.

## Running Without Docker

```bash
pip install -r requirements.txt
python porsche_web_mqtt.py
```

---

## Docker Deployment

### Build

```bash
docker build -t webconnect-mqtt-bridge .
```

### Run

```bash
docker run -d \
  --name webconnect-mqtt-bridge \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  webconnect-mqtt-bridge
```

---

## Docker Compose Example

A docker-compose file is available.

---

## Home Assistant Integration

1. Enable the MQTT integration.
2. Ensure discovery is enabled.
3. Start the bridge.
4. A new device will appear automatically under **Devices & Services → MQTT**.

If entities do not appear:

* Check bridge logs first. It should connect to both WebSocket and MQTT broker.
* Verify discovery topics are published. A good start is to listen on `homeassistant/sensor/id from the logs/config`

---

## Limitations and future improvement

* Does not auto-discover charger IP.
* Too many useless and debug metrics are exported.
* Integrate it into Home Assistant without MQTT.
* Currently TLS certificates error are silently ignored and should not be used on untrusted networks.

---

## License

Copyright (c) 2026 Aris Adamantiadis
BSD 2-clause
