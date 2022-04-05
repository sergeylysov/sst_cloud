from __future__ import annotations
from typing import Any, Callable, Tuple
from homeassistant.helpers.entity import Entity
from .const import DOMAIN
from . import sst
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)
import logging
_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass, config_entry, async_add_entities):
    sst1 = hass.data[DOMAIN][config_entry.entry_id]


    new_devices = []
    for module in sst1.devices:
        new_devices.append(MainModule(module))
        for leakSensor in module.leakSensors:

            new_devices.append(LeakSensorAlert(leakSensor,module))
        for wSensor in module.wirelessLeakSensors:
            new_devices.append(WirelessLeakSensorAlert(wSensor,module))
            new_devices.append(WirelessLeakSensorLost(wSensor,module))
            new_devices.append(WirelessLeakSensorBatteryDischarge(wSensor,module))
        new_devices.append(SecondGroupModuleAlert(module))
        new_devices.append(FirstGroupModuleAlert(module))
        if new_devices:
            async_add_entities(new_devices)


class WirelessLeakSensorAlert(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, wirelessLeakSensor: sst.WirelessLeakSensor, module: sst.LeakModule):
        self._sensor = wirelessLeakSensor
        self._module = module
        # Уникальный идентификатор
        self._attr_unique_id = f"{self._sensor.get_wireless_leak_serial_number}_WireLessLeakSensorAlert"
        # Отображаемое имя
        self._attr_name = f"LeakSensor {self._sensor.get_wireless_leak_sensor_name}"
        # Текущее значение
        self._is_on = self._sensor.get_wireless_leak_sensor_alert_status


    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._module.get_device_id)}}


    @property
    def icon(self):
        return "mdi:water-alert"

    @property
    def is_on(self):
        self._is_on = self._sensor.get_wireless_leak_sensor_alert_status
        return self._is_on
    @property
    def state(self) -> Literal["on", "off"] | None:
        """Return the state of the binary sensor."""
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"


class LeakSensorAlert(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, leakSensor: sst.LeakSensor, module: sst.LeakModule):
        self._sensor = leakSensor
        self._module = module
        # Уникальный идентификатор
        self._attr_unique_id = f"{self._sensor.get_leak_sensor_name}_leakSensorAlert"
        # Отображаемое имя
        self._attr_name = f"LeakSensor {self._sensor.get_leak_sensor_name}"
        # Текущее значение
        self._is_on = self._sensor.get_leak_sensor_alarm_status
        if self._sensor.get_leak_sensor_alarm_status == "yes":
            self._is_on = True
        else:
            self._is_on = False
    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN,  self._module.get_device_id)}}

    @property
    def icon(self):
        return "mdi:water-alert"

    @property
    def is_on(self):
        if self._sensor.get_leak_sensor_alarm_status == "yes":
            self._is_on = True
        else:
            self._is_on = False
        return self._is_on

    @property
    def state(self) -> Literal["on", "off"] | None:
        """Return the state of the binary sensor."""
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"

class WirelessLeakSensorLost(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, wirelessLeakSensor: sst.WirelessLeakSensor, module: sst.LeakModule):
        self._sensor = wirelessLeakSensor
        self._module = module
        # Уникальный идентификатор
        self._attr_unique_id = f"{self._sensor.get_wireless_leak_serial_number}_WirelesleakSensorLost"
        # Отображаемое имя
        self._attr_name = f"WirelessLeakSensor Lost {self._sensor.get_wireless_leak_sensor_name}"
        # Текущее значение
        self._is_on = self._sensor.get_wireless_leak_sensor_lost_status

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._module.get_device_id)}}

    @property
    def icon(self):
        return "mdi:lan-disconnect"

    @property
    def is_on(self):
        self._is_on = self._sensor.get_wireless_leak_sensor_lost_status
        return self._is_on
    @property
    def state(self) -> Literal["on", "off"] | None:
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"


class WirelessLeakSensorBatteryDischarge(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, wirelessLeakSensor: sst.WirelessLeakSensor, module: sst.LeakModule):
        self._sensor = wirelessLeakSensor
        self._module = module
        # Уникальный идентификатор
        self._attr_unique_id = f"{self._sensor.get_wireless_leak_serial_number}_WirelesleakSensorBatteryDischarge"
        # Отображаемое имя
        self._attr_name = f"WirelessLeakSensor battery discharge {self._sensor.get_wireless_leak_sensor_name}"
        # Текущее значение
        self._is_on = self._sensor.get_wireless_leak_sensor_battery_discharge

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._module.get_device_id)}}

    @property
    def icon(self):
        return "mdi:battery-remove"

    @property
    def is_on(self):
        self._is_on = self._sensor.get_wireless_leak_sensor_battery_discharge
        return self._is_on

    @property
    def state(self) -> Literal["on", "off"] | None:
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"


class FirstGroupModuleAlert(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, module: sst.LeakModule):

        self._module = module
        # Уникальный идентификатор
        self._attr_unique_id = f"first_group_alarm_module_alert"
        # Отображаемое имя
        self._attr_name = f"Alert module first_group_alarm"
        # Текущее значение
        if self._module.first_group_alarm == "yes":
            self._is_on = True
        else:
            self._is_on = False

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._module.get_device_id)}}

    @property
    def icon(self):
        return "mdi:alert"

    @property
    def is_on(self):
        if self._module.first_group_alarm == "yes":
            self._is_on = True
        else:
            self._is_on = False
        return self._is_on
    @property
    def state(self) -> Literal["on", "off"] | None:
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"


class SecondGroupModuleAlert(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, module: sst.LeakModule):

        self._module = module
        # Уникальный идентификатор
        self._attr_unique_id = f"second_group_alarm_module_alert"
        # Отображаемое имя
        self._attr_name = f"Alert module second_group_alarm"
        # Текущее значение
        if self._module.second_group_alarm == "yes":
            self._is_on = True
        else:
            self._is_on = False

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self._module.get_device_id)}}

    @property
    def icon(self):
        return "mdi:alert"

    @property
    def is_on(self):
        if self._module.second_group_alarm == "yes":
            self._is_on = True
        else:
            self._is_on = False
        return self._is_on
    @property
    def state(self) -> Literal["on", "off"] | None:
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"

class MainModule(Entity):

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, module: sst.LeakModule):

        self._module = module
        #self.is_on = False
        if (self._module.second_group_alarm == "true") | (self._module.first_group_alarm == "true"):
            self._is_on = True
        else:
            self._is_on = False
        # Уникальный идентификатор
        self._attr_unique_id = f"{self._module.get_device_id}_main_module"
        # Отображаемое имя
        self._attr_name = f"Neptun {self._module.get_device_name}"


    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._module.get_device_id)},
            "name": self._module.get_device_name,
            "sw_version": "none",
            "model": "Neptun Smart",
            "manufacturer": "SST",
        }

    @property
    def icon(self):
        return "mdi:water-pump"

    @property
    def is_on(self) -> bool:
        return self._is_on

    #@final
    @property
    def state(self) -> Literal["on", "off"] | None:
        if (is_on := self.is_on) is None:
            return None
        return "on" if is_on else "off"

    def update(self) -> None:
        self._module.update()
