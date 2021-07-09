import logging
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, CONF_COUNTRY, ACCOUNTS
from .ewelinkcloud import EWeLinkCloud
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

_LOGGER = logging.getLogger(__name__)

COUNTRIES = {
    'cn': "China",
    'oc': "Outside China"
}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None, error=None):

        if user_input is not None:
            if DOMAIN in self.hass.data and ACCOUNTS in self.hass.data[DOMAIN] \
                    and user_input[CONF_USERNAME] in self.hass.data[DOMAIN][ACCOUNTS]:
                return await self.async_step_user(error="account_exist")
            cloud = EWeLinkCloud(user_input[CONF_COUNTRY], user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            if await self.hass.async_add_executor_job(cloud.login):
                return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)
            else:
                return await self.async_step_user(error="cant_login")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_COUNTRY, default=['cn']): vol.In(COUNTRIES)
            }),
            errors={"base": error} if error else None
        )
