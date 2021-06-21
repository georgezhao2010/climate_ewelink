import threading
import time
import websocket
import json
import logging

from .const import APPID

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class StateManager(threading.Thread):
    def __init__(self, hass, url, devices, token, apikey):
        threading.Thread.__init__(self)
        self._ws = None
        self._wst = None
        self._hass = hass
        self._url = url
        self._devices = devices
        self._token = token
        self._apikey = apikey
        self._run = False
        self._last_ts = 0
        self._device_updates = {}

    def on_open(self):
        _LOGGER.debug("Websocket on_open")
        ts = time.time()
        payload = {
            'action': 'userOnline',
            'at': self._token,
            'apikey': self._apikey,
            'userAgent': 'app',
            'appid': APPID,
            'nonce': str(int(ts / 100)),
            'ts': int(ts),
            'version': 8,
            'sequence': str(int(ts * 1000))
        }
        self.send_json(payload)

    def on_message(self, message):
        data = json.loads(message)
        if data:
            if "deviceid" in data and "params" in data:
                update = self._device_updates[data["deviceid"]]
                if update:
                    update(data["params"])
            elif "config" in data:
                for deviceid, device in self._devices.items():
                    self.send_payload(deviceid, {"_query": 1})

    def on_close(self):
        _LOGGER.warning("Websocket closed, reconnect now")
        self.run()
        pass

    def send_json(self, jsondata):
        self._ws.send(json.dumps(jsondata))

    def send_payload(self, deviceid, data):
        while time.time() - self._last_ts < 0.1:
            time.sleep(0.1)
        self._last_ts = time.time()
        sequence = str(int(self._last_ts * 1000))
        device_status =  self._devices[deviceid].get_status()
        payload = {
            'action': 'query',
            'apikey': device_status['apikey'],
            'selfApikey': self._apikey,
            'deviceid': deviceid,
            'params': [],
            'userAgent': 'app',
            'sequence': sequence,
            'ts': 0
        } if '_query' in data else {
            'action': 'update',
            'apikey': device_status['apikey'],
            'selfApikey': self._apikey,
            'deviceid': deviceid,
            'userAgent': 'app',
            'sequence': sequence,
            'ts': 0,
            'params': data
        }
        self.send_json(payload)

    def run(self):
        self._ws = websocket.WebSocketApp(self._url,
                                          on_open=self.on_open, on_message=self.on_message,
                                          on_close=self.on_close)
        self._ws.keep_running = True
        self._wst = threading.Thread(target = self._ws.run_forever(ping_interval=145, ping_timeout=5))
        self._wst.daemon = True
        self._wst.start()

    def start_keep_alive(self):
        self._run = True
        threading.Thread.start(self)

    def set_update(self, deviceid, update):
        self._device_updates[deviceid] = update

