import threading
import time
import websocket
import json
import logging

from .const import APPID
from .ewelinkcloud import EWeLinkCloud

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class WebsocketNotOnlineException(Exception):
    pass


class StateManager(threading.Thread):
    def __init__(self, ewelink_cloud: EWeLinkCloud):
        threading.Thread.__init__(self)
        self._ws = None
        self._url = None
        self._devices = {}
        self._ewelink_cloud = ewelink_cloud
        self._token = None
        self._apikey = None
        self._last_ts = 0
        self._device_updates = {}

    def update_device(self, deviceid, params):
        if deviceid in self._device_updates:
            updates = self._device_updates[deviceid]
            if updates:
                for update_state in updates:
                    update_state(params)

    def on_open(self):
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
            if "error" in data:
                if data["error"] == 0:
                    if "config" in data:
                        for deviceid, device in self._devices.items():
                            self.send_query(deviceid)
                    elif "deviceid" in data and "params" in data:
                        self.update_device(data["deviceid"], data["params"])
                else:
                    if "deviceid" in data and "reason" in data:
                        _LOGGER.warning(f"Command failed, deviceid:{data['deviceid']}, "
                                        f"error code: {data['error']}, reason: {data['reason']}")
            elif "action" in data and data["action"] == "update" or data["action"] == "sysmsg" \
                    and "deviceid" in data and "params" in data:
                self.update_device(data["deviceid"], data["params"])

    def send_json(self, jsondata):
        message = json.dumps(jsondata)
        self._ws.send(message)

    def send_query(self, deviceid):
        self.send_payload(deviceid, {"_query": 1})

    def send_payload(self, deviceid, data):
        while time.time() - self._last_ts < 0.1:
            time.sleep(0.1)
        self._last_ts = time.time()
        sequence = str(int(self._last_ts * 1000))
        if deviceid in self._devices:
            device_status =  self._devices[deviceid].status
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
        while True:
            while self._url is None:
                if self._ewelink_cloud.login():
                    self._url = self._ewelink_cloud.get_ws_url()
                    self._devices = self._ewelink_cloud.get_devices()
                    self._token = self._ewelink_cloud.token
                    self._apikey = self._ewelink_cloud.apikey
                else:
                    _LOGGER.debug("could not login to eWeLink Cloud, retry after 30 seconds")
                    time.sleep(30)

            self._ws = websocket.WebSocketApp(self._url,
                                              on_open=self.on_open, on_message=self.on_message)
            self._ws.keep_running = True
            threading.Thread(target = self._ws.run_forever(ping_interval=145, ping_timeout=5))
            _LOGGER.debug("websocket disconnected, retrying")
            self._ws.close()
            self._ws = None
            self._url = None

    def start_keep_alive(self):
        threading.Thread.start(self)

    def add_update(self, deviceid, update):
        if deviceid not in self._device_updates:
            self._device_updates[deviceid] = []
        self._device_updates[deviceid].append(update)

