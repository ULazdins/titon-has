"""Config flow for the Titon Aura-T integration."""

from collections import OrderedDict
import logging

import voluptuous as vol

from titon import TitonClient

from homeassistant import config_entries
from homeassistant.const import CONF_ID

_LOGGER = logging.getLogger(__name__)

# pylint: disable=missing-function-docstring
# pylint: disable=broad-except


class TitonIntegrationConfigFlowHandler(
    config_entries.ConfigFlow, domain="titon_integration"
):
    """Handle a config flow for the Titon Aura-T integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_PUSH

    @staticmethod
    def async_get_options_flow(config_entry):
        return TitonOptionsFlow(config_entry)

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        errors = {}

        fields = OrderedDict()
        fields[
            vol.Required(CONF_ID, description={"suggested_value": "AA-BB-CC-11-22-33"})
        ] = str

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(fields), errors=errors
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step.

        Validate that the supplied MAC address corresponds to a reachable device.
        """
        errors = {}
        if user_input is None:
            return await self._show_setup_form()

        mac = user_input[CONF_ID]

        # try to contact the device using the TitonClient
        client = TitonClient(mac)
        try:
            # attempt connection with short timeout
            await client.connect()
        except Exception:
            errors[CONF_ID] = "cannot_connect"
        else:
            # disconnect since we just wanted to validate
            client.disconnect()

        if errors:
            return await self._show_setup_form(errors=errors)

        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"Titon {mac}",
            data={CONF_ID: mac},
        )


class TitonOptionsFlow(config_entries.OptionsFlow):
    """Allow the configured MAC address to be changed after setup."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            mac = user_input[CONF_ID]
            client = TitonClient(mac)
            try:
                await client.connect()
            except Exception:
                errors[CONF_ID] = "cannot_connect"
            else:
                client.disconnect()
            if not errors:
                data = {**self.config_entry.data, CONF_ID: mac}
                await self.hass.config_entries.async_update_entry(
                    self.config_entry, data=data
                )
                # also update unique_id attribute
                self.config_entry.unique_id = mac
                return self.async_create_entry(title="", data={})
        schema = vol.Schema(
            {vol.Required(CONF_ID, default=self.config_entry.data.get(CONF_ID)): str}
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
