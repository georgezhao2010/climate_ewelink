import logging

from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    CLIMATE_DEVICES,
    STATES_MANAGER,
    CONF_COUNTRY
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
    country = config[CONF_COUNTRY]

    ewelink_cloud = EWeLinkCloud(country, username, password)

    if await hass.async_add_executor_job(ewelink_cloud.login):
        devices = await hass.async_add_executor_job(ewelink_cloud.get_devices)
        if len(devices) > 0:
            state_manager = StateManager(ewelink_cloud)
            hass.data[config_entry.entry_id] = {}
            hass.data[config_entry.entry_id][CLIMATE_DEVICES] = devices
            hass.data[config_entry.entry_id][STATES_MANAGER] = state_manager
            hass.async_create_task(hass.config_entries.async_forward_entry_setup(
                config_entry, "climate"))
            state_manager.start_keep_alive()
            return True
    return False