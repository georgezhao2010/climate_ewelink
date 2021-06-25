from .ac_entity import AirConditionerEntity, AC_ENTITIES
from .const import (
    STATES_MANAGER,
    CLIMATE_DEVICES
)
import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass, config_entry, async_add_entities):
    devices = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for deviceid,device in hass.data[config_entry.entry_id][CLIMATE_DEVICES].items():
        for state_key, config in AC_ENTITIES.items():
            if config["type"] == "sensor":
                dev = AirConditionerEntity(states_manager, deviceid, state_key, device.status)
                devices.append(dev)
    async_add_entities(devices)
