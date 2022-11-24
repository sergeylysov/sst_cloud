from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.climate.const import (
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from .const import DOMAIN
from . import sst
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    sst1 = hass.data[DOMAIN][config_entry.entry_id]
    new_devices = []
    for module in sst1.devices:
        if module.get_device_type == 3:
            new_devices.append(Thermostat_equation(module))
        if module.get_device_type == 6:
            new_devices.append(Thermostat_equation(module))
    async_add_entities(new_devices)


class Thermostat_equation(ClimateEntity):
    def __init__(self, module: sst.ThermostatEquation):
        self._module = module
        self._attr_unique_id = f"{self._module.get_device_id}_Thermostat_equation"
        self._attr_name = self._module.get_device_name
        self._attr_hvac_modes = [HVAC_MODE_HEAT,HVAC_MODE_OFF]
        #self._attr_hvac_mode = HVAC_MODE_HEAT

    def set_temperature(self, **kwargs):
        self._module.setTemperature(kwargs.get("temperature", self.target_temperature))

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return 1.0

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""

        if self._module.get_status == "on":
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            self._module.switchOff()
        if hvac_mode == HVAC_MODE_HEAT:
            self._module.switchOn()
            return


    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        features = SUPPORT_TARGET_TEMPERATURE
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