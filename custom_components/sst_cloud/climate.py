from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature
)
from .const import DOMAIN
from . import sst
import logging
import time

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    sst1 = hass.data[DOMAIN][config_entry.entry_id]
    new_devices = []
    for module in sst1.devices:
        if module.get_device_type == 1:
            new_devices.append(Thermostat_equation(module,hass))
        if module.get_device_type == 3:
            new_devices.append(Thermostat_equation(module,hass))
        if module.get_device_type == 6:
            new_devices.append(Thermostat_equation(module,hass))
    async_add_entities(new_devices)


class Thermostat_equation(ClimateEntity):
    def __init__(self, module: sst.ThermostatEquation,hass: HomeAssistant):

        self._module = module
        self._hass1:HomeAssistant = hass
        self._attr_unique_id = f"{self._module.get_device_id}_Thermostat_equation"
        self._attr_name = self._module.get_device_name
       # self._attr_hvac_modes = [HVAC_MODE_HEAT,HVAC_MODE_AUTO,HVAC_MODE_OFF]
        self._attr_hvac_modes = [HVACMode.AUTO,HVACMode.HEAT,HVACMode.OFF]

    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get("temperature", self.target_temperature)
        self.target_temp = temp
        await self._hass1.async_add_executor_job(
            self.set_temperature,temp)
    def set_temperature(self, temp):
        self._module.setTemperature(temp)
    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return 1.0

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""

        if self._module.get_status == "on":
            if self._module.get_mode == "manual":
                return HVACMode.HEAT
            if self._module.get_mode == "chart":
                return HVACMode.AUTO
        return HVACMode.OFF

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        _LOGGER.warning(f"set_hvac_mode {hvac_mode}")
        if hvac_mode == HVACMode.OFF:
            _LOGGER.warning("switch off")
            self._module.switchOff()
        if hvac_mode == HVACMode.HEAT:
            if self._module.get_status == "off":
               self._module.switchOn()
               time.sleep(5)
               _LOGGER.warning(f"switchOn {hvac_mode}")
            self._module.switchToManual()
        if hvac_mode == HVACMode.AUTO:
            if self._module.get_status == "off":
               self._module.switchOn()
               time.sleep(5)
            self._module.switchToChart()






    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        features = ClimateEntityFeature.TARGET_TEMPERATURE
        return features

    def update(self) -> None:
        self._module.update()

    @property
    def temperature_unit(self) -> str:
        return TEMP_CELSIUS

    @property
    def current_temperature(self) -> float:
        return self._module.get_current_floor_temperature

    @property
    def target_temperature(self) -> float:
        return self._module.get_target_floor_temperature

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._module.get_device_id)},
            "name": self._module.get_device_name,
            "sw_version": "none",
            "model": "Thermostat Equation",
            "manufacturer": "SST",
        }

