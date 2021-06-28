from .const import APPID, APPSECRET, SUPPORTED_CLIMATES
import time
import base64
import hashlib
import hmac
import json
import logging
import requests

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


def update_payload(payload):
    ts = int(time.time());
    payload.update({
        'appid': APPID,
        'nonce': str(ts),  # 8-digit random alphanumeric characters
        'ts': ts,  # 10-digit standard timestamp
        'version': 8
    })
    return payload


class EWeLinkDevice:
    def __init__(self, deviceid, status):
        self._device_id = deviceid
        self._status = status

    @property
    def deviceid(self):
        return self._device_id

    @property
    def status(self):
        return self._status


SERVERS = {
    "cn": "cn-api.coolkit.cn:8080",
    "oc": "eu-api.coolkit.cc:8080/"
}


class EWeLinkCloud:
    def __init__(self, country: str, username: str, password: str):
        self._apikey = None
        self._token = None
        self._country = country
        self._username = username
        self._password = password

    def login(self):
        payload = {'phoneNumber': self._username, 'password': self._password}
        payload = update_payload(payload)
        hex_dig = hmac.new(APPSECRET.encode(),
                           json.dumps(payload).encode(),
                           digestmod=hashlib.sha256).digest()
        auth = "Sign " + base64.b64encode(hex_dig).decode()
        r = requests.post(f"https://{SERVERS[self._country]}/api/user/login", json=payload,
                          headers={'Authorization': auth})
        if r.status_code == 200:
            rejson = r.json()
            if "at" in rejson and "user" in rejson and "apikey" in rejson["user"]:
                self._apikey = rejson["user"]["apikey"]
                self._token = rejson["at"]
                return True
        return False

    def get_devices(self):
        payload = {'getTags': 1}
        payload = update_payload(payload)
        auth = "Bearer " + self._token
        devices: EWeLinkDevice[dict] = {}
        r = requests.get(f"https://{SERVERS[self._country]}/api/user/device", params=payload,
                         headers={'Authorization': auth})
        if r.status_code == 200:
            rejson = r.json()

            for index in range(len(rejson['devicelist'])):
                if rejson['devicelist'][index]['uiid'] in SUPPORTED_CLIMATES:
                    devices[rejson['devicelist'][index]['deviceid']] = EWeLinkDevice(
                        rejson['devicelist'][index]['deviceid'],
                        rejson['devicelist'][index])
                else:
                    _LOGGER.debug(f"Unsupported device: {rejson['devicelist'][index]}")
        return devices;

    def get_ws_url(self):
        payload = {'accept': 'ws'}
        payload = update_payload(payload)
        auth = "Bearer " + self._token
        r = requests.get(f"https://{SERVERS[self._country]}/dispatch/app", params=payload,
                         headers={'Authorization': auth})
        if r.status_code == 200:
            rejson = r.json()
            return f"wss://{rejson['domain']}:{rejson['port']}/api/ws"
        return None

    @property
    def apikey(self):
        return self._apikey

    @property
    def token(self):
        return self._token
