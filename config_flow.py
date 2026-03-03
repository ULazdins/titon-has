"""Config flow for Centrometal boiler integration."""
from collections import OrderedDict
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ID

_LOGGER = logging.getLogger(__name__)

# pylint: disable=missing-function-docstring
# pylint: disable=broad-except


class CentrometalBoilerConfigFlowHandler(
    config_entries.ConfigFlow, domain="minimal_integration"
):
    """Handle a config flow for Centrometal boiler."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        errors = {}

        fields = OrderedDict()
        fields[vol.Required("CONF_DEVICE_ID")] = str

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(fields), errors=errors
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return await self._show_setup_form()

        unique_id = user_input["CONF_DEVICE_ID"]

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Test thing",
            data={CONF_ID: unique_id},
        )
