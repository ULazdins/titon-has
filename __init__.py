import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.const import CONF_ID
from homeassistant.const import Platform

from .const import (
    DOMAIN,
    WEB_BOILER_SYSTEM,
)

from .HRVManager import HRVManager

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Titon integration."""

    manager = HRVManager()

    unique_id = entry.data[CONF_ID]
    hass.data[DOMAIN][unique_id] = {}
    hass.data[DOMAIN][unique_id][WEB_BOILER_SYSTEM] = manager

    # Will look into sensor.py for sensor entities. All entities here, even if defined as Switches, will be installed as sensors
    # Docs forget to mention that

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(entry, "sensor")
    # )
    # # Will look into switch.py for switches
    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(entry, "switch")
    # )

    _LOGGER.debug("Titon component setup finished")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_unload(entry, component)
        )
    return True
