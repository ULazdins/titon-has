import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.number import NumberEntity
from typing import Any
from homeassistant.const import CONF_ID
from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    unique_id = config_entry.data[CONF_ID]
    manager = hass.data[DOMAIN][unique_id][WEB_BOILER_SYSTEM]

    async_add_entities(
        [
            TitonHRVSpeedSwitch(manager, 1),
            TitonHRVSpeedSwitch(manager, 2),
            TitonHRVSpeedSwitch(manager, 3),
            TitonHRVSpeedSwitch(manager, 4),
        ],
        True,
    )

    await manager.start()


class TitonHRVSpeedSwitch(SwitchEntity):
    def __init__(self, manager, speed):
        """Initialize the fan."""
        super().__init__()

        self.manager = manager
        self.speed = speed

        def update_callback():
            self.async_write_ha_state()
            _LOGGER.warning(f"update_callback called")

        self.manager.update_callbacks.append(update_callback)

    @property
    def name(self):
        return f"Titon Aura-t Wifi HRV controller (Speed {self.speed})"

    @property
    def is_on(self):
        """Return true if it is on."""
        return self.manager.speed == self.speed

    @property
    def available(self):
        """Return True if the device is available."""
        return self.manager.speed != 0

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"safsdfdsfsd{self.speed}"

    def turn_on(self, **kwargs: Any) -> None:
        """Turn on the fan."""

        self.manager.set_speed(self.speed)

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
