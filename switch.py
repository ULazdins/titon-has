import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_ID

from typing import Any
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

    async_add_entities(
        [
            TitonHRVSpeedSwitch(fan_manager, 0),
            TitonHRVSpeedSwitch(fan_manager, 1),
            TitonHRVSpeedSwitch(fan_manager, 2),
            TitonHRVSpeedSwitch(fan_manager, 3),
            TitonHRVSpeedSwitch(fan_manager, 4),
        ],
        True,
    )

    if not client.is_connected:
        await client.connect()

    await fan_manager.perform()


class TitonHRVSpeedSwitch(SwitchEntity):
    def __init__(self, fan_manager, speed):
        """Initialize the fan."""
        super().__init__()

        self.fan_manager = fan_manager
        self.speed = speed

        def update_callback():
            self.async_write_ha_state()
            _LOGGER.warning(f"update_callback called")

        self.fan_manager.update_callbacks.append(update_callback)

    @property
    def name(self):
        return f"Titon Aura-t Wifi HRV controller (Speed {self.speed})"

    @property
    def is_on(self):
        """Return true if it is on."""
        return self.fan_manager.value == self.speed

    @property
    def available(self):
        """Return True if the device is available."""
        return self.fan_manager.value is not None

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"safsdfdsfsd{self.speed}"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the fan."""

        await self.fan_manager.set_to(self.speed)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        pass

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
