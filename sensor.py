import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_ID
from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    unique_id = config_entry.data[CONF_ID]
    manager = hass.data[DOMAIN][unique_id][WEB_BOILER_SYSTEM]

    async_add_entities([
        YourIntegrationSensor(manager)
    ], True)

class YourIntegrationSensor(SensorEntity):
    def __init__(self, manager):
        """Initialize the binary sensor."""
        super().__init__()
        self.manager = manager

        def update_callback():
            self.async_write_ha_state()
            _LOGGER.warning(f"update_callback called")

        self.manager.update_callbacks.append(update_callback)

    @property
    def name(self):
        return "Minimal Sensor"

    @property
    def state(self):
        _LOGGER.info(
            "Read sensor value: %d",
            self.manager.speed,
        )
        return self.manager.speed
