from .const import APPID, APPSECRET, SUPPORTED_CLIMATES
import time
import base64
import hashlib
import hmac
import json
import logging
from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

def update_payload(payload):
    ts = int(time.time());
    payload.update({
        'appid': APPID,
        'nonce': str(ts),  # 8-digit random alphanumeric characters
        'ts': ts,  # 10-digit standard timestamp
        'version': 8
    })
    return payload


class eWeLinkDevice:
    def __init__(self, deviceid, status):
        self._deviceid = deviceid
        self._status = status

    def get_deviceid(self):
        return self._deviceid

    def get_status(self):
        return self._status


class EWeLinkCloud:
    def __init__(self, session: ClientSession):
        self._apikey = None
        self._token = None
        self._session = session

    async def login(self, username: str, password: str):
        payload = {'phoneNumber': username, 'password': password}
        payload = update_payload(payload)
        hex_dig = hmac.new(APPSECRET.encode(),
                           json.dumps(payload).encode(),
                           digestmod=hashlib.sha256).digest()
        auth = "Sign " + base64.b64encode(hex_dig).decode()
        r = await self._session.post('https://cn-api.coolkit.cn:8080/api/user/login', json=payload,
                               headers={'Authorization': auth})
        rejson = await r.json()
        if "at" in rejson and "user" in rejson and "apikey" in rejson["user"]:
            self._apikey = rejson["user"]["apikey"]
            self._token = rejson["at"]
            return True
        return False

    async def get_devices(self):
        payload = {'getTags': 1}
        payload = update_payload(payload)
        auth = "Bearer " + self._token
        r = await self._session.get('https://cn-api.coolkit.cn:8080/api/user/device', params=payload,
                              headers={'Authorization': auth})

        rejson = await r.json()
        devices: eWeLinkDevice[dict] = {}
        for index in range(len(rejson['devicelist'])):
            if rejson['devicelist'][index]['uiid'] in SUPPORTED_CLIMATES:
                devices[rejson['devicelist'][index]['deviceid']] = eWeLinkDevice(rejson['devicelist'][index]['deviceid'],
                                                                                 rejson['devicelist'][index])
            else:
                _LOGGER.debug(f"Unsupported device: {rejson['devicelist'][index]}")
        return devices;

    async def get_ws_url(self):
        payload = {'accept': 'ws'}
        payload = update_payload(payload)
        auth = "Bearer " + self._token
        r = await self._session.get('https://cn-api.coolkit.cn:8080/dispatch/app', params=payload,
                              headers={'Authorization': auth})
        rejson = await r.json()
        return f"wss://{rejson['domain']}:{rejson['port']}/api/ws"

    def get_apikey(self):
        return self._apikey

    def get_token(self):
        return self._token
