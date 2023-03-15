from __future__ import annotations
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from .import sst
from homeassistant.components.number import PLATFORM_SCHEMA, NumberEntity
from homeassistant.const import *
from homeassistant.exceptions import PlatformNotReady
import logging
_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass, config_entry, async_add_entities):
    sst1 = hass.data[DOMAIN][config_entry.entry_id]
    new_devices = []
    for module in sst1.devices:
        if module.get_device_type == 6:
            new_devices.append(BrightSet(module,hass))
    if new_devices:
         async_add_entities(new_devices)

class BrightSet(NumberEntity):
    def __init__(self, module,hass):
        self._hass = hass
        self._module = module
        self._attr_unique_id = f"{self._module.get_device_id}_bright"
        self._attr_name = f"bright"
        self._attr_min_value = 0
        self._attr_max_value = 9
        self._attr_step = 1.0

    async def async_set_native_value(self, value: float):
       await self._hass.async_add_executor_job(self._module.set_bright,value)

    @property
    def native_step(self):
         return self._attr_step
    @property
    def native_max_value(self):
        return self._attr_max_value

    @property
    def native_min_value(self):
        return self._attr_min_value
    @property
    def native_value(self):
        return self._module.get_bright

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._module.get_device_id)}}