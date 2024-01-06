import logging
from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_ID
from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    async_add_entities([FanSpeed()], True)


class FanSpeed(NumberEntity):
    def __init__(self):
        """Initialize the fan."""
        super().__init__()

        self.vvv = 12

    entity_description: {"min_value": 0, "max_value": 100, "step": 1}

    @property
    def name(self):
        return f"Test number"

    @property
    def state(self):
        return self.vvv

    def set_native_value(self, value):
        """Update the current value."""

        self.vvv = value
