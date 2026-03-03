import logging
import asyncio

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_ID

from .const import DOMAIN, TITON_CLIENT
from .titon.TitonGeneralInfo import TitonGeneralInfo

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    unique_id = config_entry.data[CONF_ID]
    client = hass.data[DOMAIN][unique_id][TITON_CLIENT]

    info = TitonGeneralInfo(client)

    sensors = [
        TitonFilterSensor(info),
        TitonSummerSensor(info),
        TitonFrostSensor(info),
    ]

    async_add_entities(sensors, True)

    if not client.is_connected:
        await client.connect()

    await info.perform()

    async def schedule_job():
        while True:
            await asyncio.sleep(10)
            if not client.is_connected:
                await client.connect()
            try:
                await info.perform()
                for s in sensors:
                    s.async_write_ha_state()
            except Exception:
                _LOGGER.exception("Error updating TitonGeneralInfo")

    loop = asyncio.get_event_loop()
    loop.create_task(schedule_job())


class TitonFilterSensor(BinarySensorEntity):
    def __init__(self, info):
        super().__init__()
        self.info = info

    @property
    def name(self):
        return "Titon Filter Change"

    @property
    def is_on(self):
        return bool(self.info.filter_flag)

    @property
    def available(self):
        return self.info.filter_flag is not None

    @property
    def unique_id(self) -> str:
        return "titon_filter_change"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "unique_device_id")},
            "name": "Titon HRV Unit",
            "manufacturer": "Titon",
        }


class TitonSummerSensor(BinarySensorEntity):
    def __init__(self, info):
        super().__init__()
        self.info = info

    @property
    def name(self):
        return "Titon Summer Boost"

    @property
    def is_on(self):
        return bool(self.info.summer_flag)

    @property
    def available(self):
        return self.info.summer_flag is not None

    @property
    def unique_id(self) -> str:
        return "titon_summer_boost"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "unique_device_id")},
            "name": "Titon HRV Unit",
            "manufacturer": "Titon",
        }


class TitonFrostSensor(BinarySensorEntity):
    def __init__(self, info):
        super().__init__()
        self.info = info

    @property
    def name(self):
        return "Titon Frost Protection"

    @property
    def is_on(self):
        return bool(self.info.frost_flag)

    @property
    def available(self):
        return self.info.frost_flag is not None

    @property
    def unique_id(self) -> str:
        return "titon_frost_protection"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "unique_device_id")},
            "name": "Titon HRV Unit",
            "manufacturer": "Titon",
        }
