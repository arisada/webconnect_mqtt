#!/usr/bin/env python3

# Copyright 2026 Aris Adamantiadis <aris@badcode.be>
# BSD 2-Clause License

import asyncio
import websockets
import traceback
from websockets.datastructures import Headers
import ssl
import json
import uuid
import getopt
import sys
import aiohttp
from aiomqtt import Client as MQTTClient, MqttError

CONFIG_FILE = "config.json"

# ==========================================================
# METRIC REGISTRY
# ==========================================================

METRICS = {

# -------------------------
# iCAN – Active Power
# -------------------------
"de.bebro.iCAN.activePowerL1.value": {
    "unit": "W",
    "device_class": "power",
    "state_class": "measurement",
},
"de.bebro.iCAN.activePowerL2.value": {
    "unit": "W",
    "device_class": "power",
    "state_class": "measurement",
},
"de.bebro.iCAN.activePowerL3.value": {
    "unit": "W",
    "device_class": "power",
    "state_class": "measurement",
},

# -------------------------
# SelfTest – EMMC
# -------------------------
"de.bebro.SelfTest.EMMC.EMMC.identifier": {},
"de.bebro.SelfTest.EMMC.EMMC.PersistencyFreeSpaceError": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.EMMC.EMMC.PersistencyFreeSpaceWarning": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.EMMC.EMMC.PersistencyMountStatusError": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.EMMC.EMMC.SystemFreeSpaceError": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.EMMC.EMMC.SystemFreeSpaceWarning": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.EMMC.EMMC.SystemMountStatusError": {"entity_category": "diagnostic"},

# -------------------------
# SelfTest – RAM
# -------------------------
"de.bebro.SelfTest.RAM.RAM.error": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.RAM.RAM.sensorType": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.RAM.RAM.warning": {"entity_category": "diagnostic"},

# -------------------------
# SelfTest – Temperature
# -------------------------
"de.bebro.SelfTest.Temperature.Temp_CPU.error": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_CPU.sensorType": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_CPU.warning": {"entity_category": "diagnostic"},

"de.bebro.SelfTest.Temperature.Temp_LCD.error": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_LCD.sensorType": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_LCD.warning": {"entity_category": "diagnostic"},

"de.bebro.SelfTest.Temperature.Temp_LED1.error": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_LED1.sensorType": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_LED1.warning": {"entity_category": "diagnostic"},

"de.bebro.SelfTest.Temperature.Temp_LED2.error": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_LED2.sensorType": {"entity_category": "diagnostic"},
"de.bebro.SelfTest.Temperature.Temp_LED2.warning": {"entity_category": "diagnostic"},

# -------------------------
# Cumulative Charging Data
# -------------------------
"de.bebro.WebServer.cumulativeChargingData.totalEnergy": {
    "unit": "kWh",
    "device_class": "energy",
    "state_class": "total_increasing",
},
"de.bebro.WebServer.cumulativeChargingData.totalTime": {
    "device_class": "duration",
    "state_class": "measurement",
},

# -------------------------
# Current Session
# -------------------------
"de.bebro.WebServer.swaggerCurrentSession.account": {},
"de.bebro.WebServer.swaggerCurrentSession.chargingRate": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.chargingType": {},
"de.bebro.WebServer.swaggerCurrentSession.clockSrc": {},
"de.bebro.WebServer.swaggerCurrentSession.costs": {"unit": "€", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.currency": {},
"de.bebro.WebServer.swaggerCurrentSession.departTime": {},
"de.bebro.WebServer.swaggerCurrentSession.duration": {"unit": "s", "device_class": "duration", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.endOfChargeTime": {},
"de.bebro.WebServer.swaggerCurrentSession.endSoc": {"unit": "%", "device_class": "battery", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.endTime": {"device_class": "timestamp"},
"de.bebro.WebServer.swaggerCurrentSession.energySumKwh": {
    "unit": "kWh",
    "device_class": "energy",
    "state_class": "total_increasing",
},
"de.bebro.WebServer.swaggerCurrentSession.evChargingRatekW": {
    "unit": "kW",
    "device_class": "power",
    "state_class": "measurement",
},
"de.bebro.WebServer.swaggerCurrentSession.evTargetSoc": {"unit": "%", "device_class": "battery", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.evVasAvailability": {},
"de.bebro.WebServer.swaggerCurrentSession.pcid": {},
"de.bebro.WebServer.swaggerCurrentSession.powerRange": {"unit": "km", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.profileChargingState": {},
"de.bebro.WebServer.swaggerCurrentSession.remainingChargingTime": {"unit": "s", "device_class": "duration", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.selfEnergy": {"unit": "kWh", "device_class": "energy", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.sessionId": {},
"de.bebro.WebServer.swaggerCurrentSession.soc": {"unit": "%", "device_class": "battery", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.solarEnergyShare": {"unit": "%", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.startSoc": {"unit": "%", "device_class": "battery", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.startTime": {"device_class": "timestamp"},
"de.bebro.WebServer.swaggerCurrentSession.timerChargingState": {},
"de.bebro.WebServer.swaggerCurrentSession.totalRange": {"unit": "km", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurrentSession.vehicleBrand": {},
"de.bebro.WebServer.swaggerCurrentSession.vehicleModel": {},
"de.bebro.WebServer.swaggerCurrentSession.whitelist": {},

# -------------------------
# Swagger Curve
# -------------------------
"de.bebro.WebServer.swaggerCurve.availableSelfGeneratedPower": {
    "unit": "kW",
    "device_class": "power",
    "state_class": "measurement",
},
"de.bebro.WebServer.swaggerCurve.currentEnergyCost": {"unit": "€", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerL1": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerL2": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerL3": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerLimitL1": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerLimitL2": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerLimitL3": {"unit": "kW", "device_class": "power", "state_class": "measurement"},
"de.bebro.WebServer.swaggerCurve.powerLimitReasonL1": {},
"de.bebro.WebServer.swaggerCurve.powerLimitReasonL2": {},
"de.bebro.WebServer.swaggerCurve.powerLimitReasonL3": {},
"de.bebro.WebServer.swaggerCurve.sessionId": {},
"de.bebro.WebServer.swaggerCurve.startTime": {"device_class": "timestamp"},
"de.bebro.WebServer.swaggerCurve.timestamp": {"device_class": "timestamp"},
}


VERBOSE = False

def parse_args():
    global VERBOSE
    opts, _ = getopt.getopt(sys.argv[1:], "v", ["verbose"])
    for opt, _ in opts:
        if opt in ("-v", "--verbose"):
            VERBOSE = True

def vprint(msg):
    if VERBOSE:
        print(msg)

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def convert_properties(obj):
    json_interfaces = ("de.bebro.WebServer", "de.bebro.iCAN")
    rc = {}
    if "interface" in obj and "args" in obj:
        intf = obj["interface"]
        args = obj["args"]
        path = obj["path"].lstrip('/')
        for k, v in args.items():
            try:
                if intf in json_interfaces:
                    rc[k] = json.loads(v)
                else:
                    rc[k] = v
            except TypeError as e:
                print("TypeError:", e)
                print(f"{intf}.{path}.{k} value: {v}")
        if path:
            rc = {path: rc}
        rc = {intf: rc}
    else:
        print("Don't know what to do with obj")
        print(obj)
    return flatten_dict(rc)

class WebConnect:
    ssl_context = ssl.create_default_context()

    def __init__(self, hostname):
        self._hostname = hostname
        self._ws = None

    async def async_connect(self):
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        headers = Headers({"Origin": f"https://{self._hostname}"})
        vprint("Connecting to charger...")
        self._ws = await websockets.connect(
            f"wss://{self._hostname}/ws",
            ssl=self.ssl_context,
            additional_headers=headers,
        )
        print(f"Connected to charger at {self._hostname}")

    async def async_recv(self):
        data = await self._ws.recv()
        obj = json.loads(data)
        return convert_properties(obj)

    async def async_close(self):
        if self._ws:
            await self._ws.close()

class WebConnectClient:

    def __init__(self, config: dict):
        self.host = config["charger"]["host"]
        self.password = config["charger"]["password"]

        self._session: Optional[aiohttp.ClientSession] = None
        self._token: Optional[str] = None
        self._token_expiry: Optional[int] = None

        self._refresh_task = None
        self._deepsleep_task = None

        self.current_limit = None

    async def start(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)

        self._session = aiohttp.ClientSession(connector=connector)
        await self.login()
        self._refresh_task = asyncio.create_task(self._refresh_loop())

    async def stop(self):
        if self._refresh_task:
            self._refresh_task.cancel()
        if self._deepsleep_task:
            self._deepsleep_task.cancel()
        if self._session:
            await self._session.close()
    def _auth_headers(self):
        return {
            "Authorization": f"Bearer {self._token}"
        }
    async def login(self):
        url = f"https://{self.host}/jwt/login"

        data = {
            "user": "user",
            "pass": self.password
        }

        async with self._session.post(
            url,
            data=data,
            headers={"Accept": "application/json", "Referer":f"https://{self.host}/"}
        ) as resp:

            if resp.status != 200:
                raise RuntimeError(f"Login failed: {resp.status}")

            payload = await resp.json()
            self._token = payload["token"]
            vprint("Web interface logged in")

    async def refresh(self):
        url = f"https://{self.host}/jwt/refresh"

        async with self._session.get(
            url,
            headers={**self._auth_headers(), "Referer":f"https://{self.host}/"}
        ) as resp:

            if resp.status != 200:
                # fallback to full login
                await self.login()
                return

            payload = await resp.json()
            self._token = payload["token"]
            vprint("Web interface successful refresh")
    
    async def _refresh_loop(self):
        while True:
            await asyncio.sleep(30)
            await self.refresh()
    
    async def setHMICurrentLimit(self, value: int) -> bool:
        url = (
            f"https://{self.host}/v1/api/SCC/properties/"
            f"propHMICurrentLimit?value={value}"
        )

        async with self._session.put(
            url,
            headers={**self._auth_headers(), "Referer":f"https://{self.host}/"}
        ) as resp:

            if resp.status != 200:
                vprint(f"Error setting setHMICurrentLimit({value}): {resp.status}")
                return False

            text = await resp.text()

            if "OK" in text:
                self.current_limit = value
                vprint(f"Web interface successful setHMICurrentLimit({value})")
                return True
            print(f"Web interface setHMICurrentLimit({value}):{text}")
            return False

class MQTTPublisher:

    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.username = config["username"]
        self.password = config["password"]
        self.base_topic = config["base_topic"]

        self.device_id = "porsche_ev_charger"
        self.availability_topic = f"{self.base_topic}/status"

    async def connect(self):
        self.client = MQTTClient(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        #await self.client.connect()

    async def disconnect(self):
        async with self.client:
            await self.publish(self.availability_topic, "offline", retain=True)
            #await self.client.disconnect()

    async def publish(self, topic, payload, retain=False):
        if VERBOSE:
            print(f"[MQTT] {topic} → {payload}")
        await self.client.publish(topic, payload, retain=retain)

    async def publish_metrics(self, metrics):
        for key, value in metrics.items():
            if key in METRICS:
                key = key.replace(".", "_")
                topic = f"{self.base_topic}/{key}"
                await self.publish(topic, str(value))
            else:
                print(f"Metric {key} ignored: {value}")

    async def publish_discovery(self):
        for key, cfg in METRICS.items():
            key = key.replace(".", "_")
            unique_id = f"{self.device_id}_{key}"

            payload = {
                "name": key,
                "state_topic": f"{self.base_topic}/{key}",
                "unique_id": unique_id,
                "availability_topic": self.availability_topic,
                "device": {
                    "identifiers": [self.device_id],
                    "name": "Porsche EV Charger",
                    "manufacturer": "Porsche",
                    "model": "EV Charger"
                }
            }

            for field in ("unit", "device_class", "state_class", "entity_category"):
                if field in cfg:
                    if field == "unit":
                        payload["unit_of_measurement"] = cfg[field]
                    else:
                        payload[field] = cfg[field]

            topic = f"homeassistant/sensor/{unique_id}/config"
            await self.publish(topic, json.dumps(payload), retain=True)

async def websocket_loop(charger_host, mqtt_pub):
    connect_failed_once = False
    while True:
        wc = WebConnect(charger_host)
        try:
            await wc.async_connect()
            print("Websocket connected.")
            connect_failed_once = False
            await mqtt_pub.client.publish(mqtt_pub.availability_topic, "online", retain=True)
            await mqtt_pub.publish_discovery()
            print("starting websocket loop...")
            while True:
                metrics = await wc.async_recv()
                await mqtt_pub.publish_metrics(metrics)
        except Exception as e:
            print(f"Websocket error: {e}")
            print(traceback.format_exc())
            await asyncio.sleep(5)
        except OSError as e:
            if not connect_failed_once:
                connect_failed_once = True
                print(f"Connection error: {e}")
            await asyncio.sleep(5)
        finally:
            await wc.async_close()
    await mqtt_pub.client.publish(mqtt_pub.availability_topic, "offline", retain=True)

async def mqtt_loop(config):
    mqtt_pub = MQTTPublisher(config["mqtt"])
    while True:
        try:
            await mqtt_pub.connect()
            async with mqtt_pub.client:
                await websocket_loop(config["charger"]["host"], mqtt_pub)
        except MqttError as e:
            print(f"MQTT error: {e}")
            await asyncio.sleep(5)
        except asyncio.exceptions.CancelledError:
            print("Stopped from keyboard")
            await mqtt_pub.disconnect()
            break
        finally:
            try:
                await mqtt_pub.disconnect()
            except:
                pass

async def main():
    parse_args()
    config = load_config()
    await mqtt_loop(config)

if __name__ == "__main__":
    asyncio.run(main())
