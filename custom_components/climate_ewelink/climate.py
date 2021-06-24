import logging
from homeassistant.components.climate import *
from homeassistant.components.climate.const import *
from homeassistant.const import (
    PRECISION_HALVES,
    TEMP_CELSIUS,
    PRECISION_WHOLE,
    PRECISION_TENTHS,
    ATTR_TEMPERATURE,
    STATE_ON,
    STATE_OFF
)
from .const import (
    DOMAIN,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX,
    STATES_MANAGER,
    CLIMATE_DEVICES,
    MODE_OFFLINE
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass, config_entry, async_add_entities):
    devices = []
    states_manager = hass.data[config_entry.entry_id][STATES_MANAGER]
    for deviceid,device in hass.data[config_entry.entry_id][CLIMATE_DEVICES].items():
        dev = EWeLinkClimate(states_manager, deviceid, device.status)
        devices.append(dev)
    async_add_entities(devices)


class EWeLinkClimate(ClimateEntity):
    def __init__(self, states_manager, deviceid:str, device_status):
        self._is_on = None
        self._device_id = deviceid
        self._unique_id = f"{DOMAIN}.{deviceid}"
        self.entity_id = self._unique_id
        self._states_manager = states_manager
        self._states_manager.add_update(self._device_id, self.update)
        self._attr_precision = PRECISION_TENTHS
        self._attr_fan_mode = None
        self._attr_indoor_temperature = None
        self._attr_target_temperature = None
        self._attr_swing_mode = None
        self._is_online = True

        if "params" in device_status:
            self.update_data(device_status["params"])
        manufacturer = "Unknow"
        model = "Unknow"
        if "extra" in device_status and "extra" in device_status["extra"] and "manufacturer" in device_status["extra"]["extra"]:
            manufacturer = device_status["extra"]["extra"]["manufacturer"]
        if "extra" in device_status and "extra" in device_status["extra"] and "model" in device_status["extra"]["extra"]:
            model = device_status["extra"]["extra"]["model"]
        self._device_info = {
            "manufacturer":  manufacturer,
            "model": model,
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Climate {self._device_id}",
        }

    @property
    def name(self):
        return f"Climate {self._device_id}"

    @property
    def device_info(self):
        return self._device_info

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE

    @property
    def should_poll(self):
        return False

    @property
    def hvac_mode(self) -> str:
        return self._attr_hvac_mode if self._is_on else HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        return [MODE_OFFLINE, HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_AUTO, HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY]

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def fan_mode(self):
        return self._attr_fan_mode

    @property
    def fan_modes(self):
        return [FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_AUTO]

    @property
    def swing_mode(self):
        return self._attr_swing_mode

    @property
    def swing_modes(self):
        return [SWING_OFF, SWING_VERTICAL, SWING_HORIZONTAL, SWING_BOTH]

    @property
    def target_temperature_low(self):
        return TEMPERATURE_MIN

    @property
    def target_temperature_high(self):
        return TEMPERATURE_MAX

    @property
    def target_temperature_step(self):
        return PRECISION_WHOLE

    @property
    def target_temperature(self):
        return self._attr_target_temperature

    @property
    def current_temperature(self):
        return self._attr_indoor_temperature

    @property
    def min_temp(self):
        return TEMPERATURE_MIN

    @property
    def max_temp(self):
        return TEMPERATURE_MAX

    @property
    def state(self) -> str:
        if self._is_online is False:
            return MODE_OFFLINE
        elif self._is_on:
            return self.hvac_mode
        else:
            return HVAC_MODE_OFF

    def update_data(self, data: dict = None):
        try:
            if "online" in data:
                _LOGGER.debug("Climate is offline")
                self._is_online = data["online"]
            if "power" in data:  # 0 - off, 1 - onW
                self._is_on = (data['power'] == "on")
            if "mode" in data:  # 0 - heat, 1 - cool, 15 - off
                if data['mode'] == "fan":
                    self._attr_hvac_mode = HVAC_MODE_FAN_ONLY
                else:
                    self._attr_hvac_mode = data['mode']
            if 'wind_speed' in data:  # 0 - low, 3 - auto, 15 - off
                self._attr_fan_speed = data['wind_speed']
                if self._attr_fan_speed > 100:
                    self._attr_fan_mode = FAN_AUTO
                elif self._attr_fan_speed > 70:
                    self._attr_fan_mode = FAN_HIGH
                elif self._attr_fan_speed > 30:
                    self._attr_fan_mode = FAN_MEDIUM
                else:
                    self._attr_fan_mode = FAN_LOW
            if "temperature" in data:
                self._attr_target_temperature = data["temperature"]
            if "indoor_temperature" in data:
                self._attr_indoor_temperature = data["indoor_temperature"]

        except:
            pass

    def update(self, data: dict = None):
        self.update_data(data)
        self.schedule_update_ha_state()

    def set_temperature(self, **kwargs) -> None:
        if self.state != MODE_OFFLINE:
            temperature = int(kwargs[ATTR_TEMPERATURE])
            self._states_manager.send_payload(self._device_id, {"temperature": temperature})

    def set_fan_mode(self, fan_mode: str) -> None:
        if self.state != MODE_OFFLINE:
            wind_speed = 102
            if fan_mode == FAN_LOW:
                wind_speed = 29
            elif fan_mode == FAN_MEDIUM:
                wind_speed = 69
            elif fan_mode == FAN_HIGH:
                wind_speed = 99
            self._states_manager.send_payload(self._device_id, {"power": "on","wind_speed": wind_speed})

    def set_hvac_mode(self, hvac_mode: str) -> None:
        if self.state != MODE_OFFLINE:
            mode = hvac_mode
            mode_key = "mode"
            if hvac_mode == HVAC_MODE_OFF:
                mode_key = "power"
            elif hvac_mode == HVAC_MODE_FAN_ONLY:
                mode = "fan"
            self._states_manager.send_payload(self._device_id, {"power": "on", mode_key: mode})

    def set_swing_mode(self, swing_mode: str) -> None:
        if self.state != MODE_OFFLINE:
            data = {"wind_swing_lr": "off", "wind_swing_ud": "off"}
            if swing_mode == SWING_BOTH:
                data = {"wind_swing_lr": "on", "wind_swing_ud": "on"}
            elif swing_mode == SWING_VERTICAL:
                data = {"wind_swing_lr": "off", "wind_swing_ud": "on"}
            elif swing_mode == SWING_HORIZONTAL:
                data = {"wind_swing_lr": "on", "wind_swing_ud": "off"}
            self._states_manager.send_payload(self._device_id, data)

    def turn_on(self):
        if self.state != MODE_OFFLINE:
            self._states_manager.send_payload(self._device_id, {"power": "on"})

    def turn_off(self):
        if self.state != MODE_OFFLINE:
            self._states_manager.send_payload(self._device_id, {"power": "off"})