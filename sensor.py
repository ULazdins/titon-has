import logging
import asyncio

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_ID

from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)
from .titon.TitonFanSpeed import TitonFanSpeed

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    unique_id = config_entry.data[CONF_ID]
    client = hass.data[DOMAIN][unique_id][WEB_BOILER_SYSTEM]

    fan_manager = TitonFanSpeed(client)

    async_add_entities([YourIntegrationSensor(fan_manager)], True)

    if not client.is_connected:
        await client.connect()

    await fan_manager.perform()

    async def schedule_job():
        while True:
            await asyncio.sleep(5)
            if not client.is_connected:
                await client.connect()

            await fan_manager.perform()

    loop = asyncio.get_event_loop()
    loop.create_task(schedule_job())


class YourIntegrationSensor(SensorEntity):
    def __init__(self, fan_manager):
        """Initialize the binary sensor."""
        super().__init__()
        self.fan_manager = fan_manager

        def update_callback():
            self.async_write_ha_state()
            _LOGGER.warning(f"update_callback called")

        self.fan_manager.update_callbacks.append(update_callback)

    @property
    def name(self):
        return "Minimal Sensor"

    @property
    def state(self):
        _LOGGER.info(
            "Read sensor value: %d",
            self.fan_manager.value,
        )
        return self.fan_manager.value

    @property
    def available(self):
        """Return True if the device is available."""
        return self.fan_manager.value is not None
