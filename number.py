import logging

from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_ID

from .titon.TitonKitchenTimer import TitonKitchenTimer
from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)
from .titon.TitonHumidity import TitonHumidity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    unique_id = config_entry.data[CONF_ID]
    client = hass.data[DOMAIN][unique_id][WEB_BOILER_SYSTEM]

    kitchen_manager = TitonKitchenTimer(client)
    humidity_manager = TitonHumidity(client)

    async_add_entities(
        [
            FanSpeed("Kitchen timer", kitchen_manager),
            HumidityNumber("Humidity threshold", humidity_manager),
        ],
        True,
    )

    if not client.is_connected:
        await client.connect()

    await kitchen_manager.perform()


class FanSpeed(NumberEntity):
    entity_description: {"min_value": 0, "max_value": 100, "step": 1}

    def __init__(self, title, kitchen_manager):
        """Initialize the fan."""
        super().__init__()

        self.title = title
        self.kitchen_manager = kitchen_manager

        def update_callback():
            self.async_write_ha_state()
            _LOGGER.debug("update_callback called")

        self.kitchen_manager.update_callbacks.append(update_callback)

    @property
    def name(self):
        return self.title

    @property
    def available(self):
        """Return True if the device is available."""
        return self.kitchen_manager.value is not None

    @property
    def state(self):
        return self.kitchen_manager.value

    async def async_set_native_value(self, value):
        """Update the current value."""

        await self.kitchen_manager.set_to(value)

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"titon_fan_{self.name}"

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "unique_device_id")
            },
            "name": "Titon HRV Unit",
            "manufacturer": "Titon",
        }


class HumidityNumber(NumberEntity):
    entity_description: {"min_value": 0, "max_value": 100, "step": 1}

    def __init__(self, title, humidity_manager):
        super().__init__()
        self.title = title
        self.humidity_manager = humidity_manager

        def update_callback():
            self.async_write_ha_state()

        # TitonHumidity has no update_callbacks by default; we'll trust callers to
        # call perform() on setup. If you want continuous polling, add a loop.

    @property
    def name(self):
        return self.title

    @property
    def available(self):
        return True

    @property
    def state(self):
        return getattr(self, "_value", None)

    async def async_set_native_value(self, value):
        success = await self.humidity_manager.set_to(int(value))
        if success:
            self._value = int(value)

    async def async_update(self):
        try:
            if not self.humidity_manager.client.is_connected:
                await self.humidity_manager.client.connect()
            v = await self.humidity_manager.perform()
            self._value = v
        except Exception:
            pass

    @property
    def unique_id(self) -> str:
        return f"titon_humidity_{self.title}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "unique_device_id")},
            "name": "Titon HRV Unit",
            "manufacturer": "Titon",
        }
