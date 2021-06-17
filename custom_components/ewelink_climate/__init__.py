import logging

from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    MIDEA_DEVICES,
    STATES_MANAGER
)

from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME
)

from .ewelinkcloud import EWeLinkCloud
from .statemanager import StateManager

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup(hass: HomeAssistant, hass_config: dict):
    hass.data.setdefault(DOMAIN, {})

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry):

    config = config_entry.data

    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    session = async_create_clientsession(hass)
    ewelink_cloud = EWeLinkCloud(session)

    await ewelink_cloud.login(username, password)
    devices = await ewelink_cloud.get_devices()
    if len(devices) > 0:
        ws_url = await ewelink_cloud.get_ws_url()
        token = ewelink_cloud.get_token()
        apikey = ewelink_cloud.get_apikey()
        state_manager = StateManager(hass, ws_url, devices, token, apikey)
        hass.data[config_entry.entry_id] = {}
        hass.data[config_entry.entry_id][MIDEA_DEVICES] = devices
        hass.data[config_entry.entry_id][STATES_MANAGER] = state_manager
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(
            config_entry, "climate"))
        state_manager.start_keep_alive()
        return True
    return False



