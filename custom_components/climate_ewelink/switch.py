from .ac_entity import AirConditionerEntity, AC_SWITCHES
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.const import (
    STATE_ON,
    STATE_OFF,
)

from .const import (
    STATES_MANAGER,
    CLIMATE_DEVICES
)

from typing import Any

import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass, config_entry, async_add_entities):
    devices = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for deviceid, device in hass.data[config_entry.entry_id][CLIMATE_DEVICES].items():
        for state_key, config in AC_SWITCHES.items():
            if config["type"] == "switch":
                dev = ACSwitch(states_manager, deviceid, state_key, device.status)
                devices.append(dev)
    async_add_entities(devices)


class ACSwitch(AirConditionerEntity, ToggleEntity):
    @property
    def is_on(self) -> bool:
        return self._state == STATE_ON

    def turn_on(self, **kwargs: Any):
        value = STATE_ON
        if "value_exchange" in AC_SWITCHES[self._state_key] and \
                value in AC_SWITCHES[self._state_key]["value_exchange"]["set"]:
            value = AC_SWITCHES[self._state_key]["value_exchange"]["set"][value]
        self._state_manager.send_payload(self._device_id, {"power": "on", self._state_key: value})

    def turn_off(self, **kwargs: Any):
        value = STATE_OFF
        if "value_exchange" in AC_SWITCHES[self._state_key] and \
                value in AC_SWITCHES[self._state_key]["value_exchange"]["set"]:
            value = AC_SWITCHES[self._state_key]["value_exchange"]["set"][value]
        self._state_manager.send_payload(self._device_id, {self._state_key: value})

    def _update_state(self, status):
        if "online" in status:
            self._is_online = status["online"]
            return True
        return AirConditionerEntity._update_state(self, status)
