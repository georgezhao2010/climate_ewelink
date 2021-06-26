from .const import DOMAIN, MODE_OFFLINE
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    TEMP_CELSIUS,
    STATE_ON,
    STATE_OFF,
    DEVICE_CLASS_TEMPERATURE
)

import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

AC_ENTITIES = {
    "climate": {
        "type": "climate",
        "icon": "mdi:air-conditioner"
    },
    "wind_swing_lr": {
        "type": "switch",
        "name": "Swing Horizontal",
        "icon": "mdi:arrow-split-vertical"
    },
    "wind_swing_ud": {
        "type": "switch",
        "name": "Swing Vertical",
        "icon": "mdi:arrow-split-horizontal"
    },
    "eco": {
        "type": "switch",
        "name": "ECO Mode",
        "icon": "mdi:alpha-e-circle"
    },
    "comfort_power_save": {
        "type": "switch",
        "name": "Comfort Mode",
        "icon": "mdi:alpha-c-circle"
    },
    "prevent_straight_wind": {
        "type": "switch",
        "name": "Indirect Wind",
        "icon": "mdi:weather-windy",
        "value_exchange": {
            "get": {
                "1": "off",
                "2": "on"
            },
            "set": {
                "off": "1",
                "on": "2"
            }
        }
    },
    "outdoor_temperature": {
        "type": "sensor",
        "name": "Temperature Outdoor",
        "unit": TEMP_CELSIUS,
        "device_class": DEVICE_CLASS_TEMPERATURE
    }
}


class AirConditionerEntity(Entity):
    def __init__(self, states_manager, deviceid, state_key, device_status):
        self._state_manager = states_manager
        self._device_id = deviceid
        self._state_key = state_key
        self._state_manager.add_update(self._device_id, self.update)
        self._unique_id = f"{DOMAIN}.{deviceid}_{self._state_key}"
        self.entity_id = self._unique_id
        self._state = None
        self._is_online = True
        if "params" in device_status:
            self._update_state(device_status["params"])
        manufacturer = "Unknow"
        model = "Unknow"
        self._device_name = f"Climate {self._device_id}"
        if "brandName" in device_status:
            manufacturer = device_status["brandName"]
        if "productModel" in device_status:
            model = device_status["productModel"]
        if "name" in device_status:
            self._device_name = device_status["name"]
        self._device_info = {
            "manufacturer": manufacturer,
            "model": model,
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name
        }

    def _update_state(self, status):
        if self._state_key in status:
            if "value_exchange" in AC_ENTITIES[self._state_key] \
                    and str(status[self._state_key]) in AC_ENTITIES[self._state_key]["value_exchange"]["get"]:
                value = AC_ENTITIES[self._state_key]["value_exchange"]["get"][str(status[self._state_key])]
            else:
                value = status[self._state_key]
            if value != self._state:
                self._state = value
                return True
        return False

    def update(self, status):
        if self._update_state(status):
            self.schedule_update_ha_state()

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def device_class(self):
        return AC_ENTITIES[self._state_key].get("device_class")

    @property
    def name(self):
        return f"{self._device_name} {AC_ENTITIES[self._state_key].get('name')}" if "name" in AC_ENTITIES[self._state_key] \
                else self._device_name

    @property
    def unit_of_measurement(self):
        return AC_ENTITIES[self._state_key].get("unit")

    @property
    def icon(self):
        return AC_ENTITIES[self._state_key].get("icon")

    @property
    def state(self):
        if self._is_online:
            return self._state
        return MODE_OFFLINE
