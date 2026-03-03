import logging

from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_ID

from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)
from .titon.TitonFanSpeed import TitonFanSpeed

_LOGGER = logging.getLogger(__name__)

# Define the 5 speed options
SPEED_OPTIONS = ["Speed 0", "Speed 1", "Speed 2", "Speed 3", "Speed 4"]


async def async_setup_entry(hass, config_entry, async_add_entities):
    unique_id = config_entry.data[CONF_ID]
    client = hass.data[DOMAIN][unique_id][WEB_BOILER_SYSTEM]

    fan_manager = TitonFanSpeed(client)

    async_add_entities(
        [
            TitonHRVSpeedSelector(fan_manager),
        ],
        True,
    )

    if not client.is_connected:
        await client.connect()

    await fan_manager.perform()


class TitonHRVSpeedSelector(SelectEntity):
    def __init__(self, fan_manager):
        """Initialize the fan speed selector."""
        super().__init__()

        self.fan_manager = fan_manager

        def update_callback():
            self.async_write_ha_state()
            _LOGGER.debug("update_callback called")

        self.fan_manager.update_callbacks.append(update_callback)

    @property
    def name(self):
        return "Titon Aura-t Wifi HRV Speed"

    @property
    def options(self) -> list[str]:
        """Return the list of available options."""
        return SPEED_OPTIONS

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.fan_manager.value is not None:
            return SPEED_OPTIONS[self.fan_manager.value]
        return None

    @property
    def available(self):
        """Return True if the device is available."""
        return self.fan_manager.value is not None

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return "titon_speed_selector"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        speed = SPEED_OPTIONS.index(option)
        await self.fan_manager.set_to(speed)

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
