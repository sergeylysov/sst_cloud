import requests
import json

import logging
from homeassistant.core import HomeAssistant

SST_CLOUD_API_URL = "https://api.sst-cloud.com/"
_LOGGER = logging.getLogger(__name__)

class SST:

    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self.devices = []


    def pull_data(self):
        response = requests.post(SST_CLOUD_API_URL + "auth/login/",
                                 json={"username": self._username, "password": self._password, "email": self._username},
                                 headers={'Content-Type': 'application/json'})
        self.key = json.loads(response.text)["key"]
        response = requests.get(SST_CLOUD_API_URL + "houses", headers={"Authorization": "Token " + self.key})
        houses = json.loads(response.text)
        for house in houses:  # перебираем все дома
            response = requests.get(SST_CLOUD_API_URL +
                                    "houses/" + str(house["id"]) + "/devices",
                                    headers={"Authorization": "Token " + self.key})
            devices = json.loads(response.text)
            # Перебираем все устройства в доме
            for device in devices:
                response = requests.get(SST_CLOUD_API_URL +
                                        "houses/" + str(house["id"]) + "/devices/" + str(device["id"]),
                                        headers={"Authorization": "Token " + self.key})
                json_device = json.loads(response.text)
                if json_device["type"] == 7:
                    self.devices.append(LeakModule(json_device, self))
                if json_device["type"] == 2:
                    self.devices.append(NeptunProwWiFi(json_device, self))
#Neptun ProW+ WiFi
class NeptunProwWiFi:
    def __init__(self, moduleDescription: json, sst: SST):
        self._sst = sst
        config = json.loads(moduleDescription["parsed_configuration"])
        self._access_status = config["access_status"]  # Main device "available" is true
        self._device_name = moduleDescription["name"]
        self._house_id = moduleDescription["house"]
        self._type = moduleDescription["type"] #2
        self._id = moduleDescription["id"]
        self._valves_state = config["settings"]["valve_settings"]
        self.alert_status = config["settings"]["status"]["alert"]
        self._dry_flag = config["settings"]["dry_flag"]
        self.counters = []
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/counters",
                                headers={"Authorization": "Token " + self._sst.key})
        countersJson = json.loads(response.text)
        for counterDesc in countersJson:
            self.counters.append(Counter(counterDesc["id"], counterDesc["name"], counterDesc["value"]))
        self.leakSensors = []
        # Перебрать статус всех проводных датчиков протечки
        for leakSensorDesc in config["lines_status"]:
            self.leakSensors.append(
                LeakSensor(leakSensorDesc, config["lines_status"][leakSensorDesc]))
        self.wirelessLeakSensors = []
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/wireless_sensors",
                                headers={"Authorization": "Token " + self._sst.key})
        wirelessSensors = json.loads(response.text)
        # Перебираем все беспроводные датчики
        for wirelessSensorDesc in wirelessSensors:
            self.wirelessLeakSensors.append(WirelessLeakSensor443(wirelessSensorDesc))

    def close_valve(self):
            requests.post(SST_CLOUD_API_URL +
                           "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/valve_settings/",
                           json={"valve_settings":"closed"},
                           headers={"Authorization": "Token " + self._sst.key})
            self._valves_state = "closed"

    def open_valve(self):
            requests.post(SST_CLOUD_API_URL +
                           "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/valve_settings/",
                           json={"valve_settings":"opened"},
                           headers={"Authorization": "Token " + self._sst.key})
            self._valves_state = "opened"
    def set_on_washing_floors_mode(self):
        requests.post(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/dry_flag/",
                       json={"dry_flag":"on"},
                       headers={"Authorization": "Token " + self._sst.key})
        self._dry_flag = "on"
    def set_off_washing_floors_mode(self):
        requests.post(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/dry_flag/",
                       json={"dry_flag": "off"},
                       headers={"Authorization": "Token " + self._sst.key})
        self._dry_flag = "off"


    @property
    def get_avalible_status(self) -> bool:
            if self._access_status == "available":
                return "true"
            else:
                return "false"

    @property
    def get_device_id(self) -> str:
            return self._id

    @property
    def get_device_name(self) -> str:
            return self._device_name

    @property
    def get_device_type(self) -> int:
            return self._type

    @property
    def get_valves_state(self) -> str:
            # opened or closed
            return self._valves_state
    @property
    def get_washing_floors_mode(self)-> str:
        return self._dry_flag

    def update(self) -> None:
            # Обновляем парметры модуля
            response = requests.get(SST_CLOUD_API_URL +
                                    "houses/" + str(self._house_id) + "/devices/" + str(self._id),
                                    headers={"Authorization": "Token " + self._sst.key})
            json_device = json.loads(response.text)
            config = json.loads(json_device["parsed_configuration"])
            self._access_status = config["access_status"]  # Main device "available" is true
            self._device_name = json_device["name"]
            self._house_id = json_device["house"]
            self._type = json_device["type"]
            self._id = json_device["id"]
            self._valves_state = config["settings"]["valve_settings"]
            self.alert_status = config["settings"]["status"]["alert"]

            # Обновляем статус счетчиков
            response = requests.get(SST_CLOUD_API_URL +
                                    "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/counters",
                                    headers={"Authorization": "Token " + self._sst.key})
            countersJson = json.loads(response.text)
            for counter in self.counters:
                counter.update(countersJson)

            # Обновляем статус датчиков
            for leakSensor in self.leakSensors:
                leakSensor.update(config["lines_status"])
            # Обновляем статус беспроводных датчиков
            response = requests.get(SST_CLOUD_API_URL +
                                    "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/wireless_sensors",
                                    headers={"Authorization": "Token " + self._sst.key})
            # print(response.text)
            wirelessSensorsJson = json.loads(response.text)
            for wirelessSensor in self.wirelessLeakSensors:
                wirelessSensor.update(wirelessSensorsJson)

#Neptun Smart
class LeakModule:
    def __init__(self, moduleDescription: json, sst: SST):
        self._sst = sst
        config = json.loads(moduleDescription["parsed_configuration"])
        self._access_status = config["access_status"]  # Main device "available" is true
        self._device_id = config["device_id"]
        self._device_name = moduleDescription["name"]
        self._house_id = moduleDescription["house"]
        self._type = moduleDescription["type"] #7
        self._id = moduleDescription["id"]
        self._first_group_valves_state = config["module_settings"]["module_config"]["first_group_valves_state"]
        self._second_group_valves_state = config["module_settings"]["module_config"]["second_group_valves_state"]
        self.first_group_alarm = config["module_settings"]["module_status"]["first_group_alarm"]
        self.second_group_alarm = config["module_settings"]["module_status"]["second_group_alarm"]
        self._washing_floors_mode = config["module_settings"]["module_status"]["washing_floors_mode"]
        self.counters = []
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/counters",
                                headers={"Authorization": "Token " + self._sst.key})
        countersJson = json.loads(response.text)
        for counterDesc in countersJson:
            self.counters.append(Counter(counterDesc["id"], counterDesc["name"], counterDesc["value"]))

        self.leakSensors = []
        # Перебрать статус всех проводных датчиков протечки
        for leakSensorDesc in config["module_settings"]["wire_lines_status"]:
            self.leakSensors.append(
                LeakSensor(leakSensorDesc, config["module_settings"]["wire_lines_status"][leakSensorDesc]))
        self.wirelessLeakSensors = []
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/wireless_sensors",
                                headers={"Authorization": "Token " + self._sst.key})
        wirelessSensors = json.loads(response.text)
        # Перебираем все беспроводные датчики
        for wirelessSensorDesc in wirelessSensors:
            self.wirelessLeakSensors.append(WirelessLeakSensor(wirelessSensorDesc))

    def close_valve_first_group(self):
        requests.patch(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/module_settings/",
                       json={"module_config": {"first_group_valves_state": "closed"}},
                       headers={"Authorization": "Token " + self._sst.key})
        self._first_group_valves_state = "closed"

    def open_valve_first_group(self):
        requests.patch(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/module_settings/",
                       json={"module_config": {"first_group_valves_state": "opened"}},
                       headers={"Authorization": "Token " + self._sst.key})
        self._first_group_valves_state = "opened"

    def close_valve_second_group(self):
        requests.patch(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/module_settings/",
                       json={"module_config": {"second_group_valves_state": "closed"}},
                       headers={"Authorization": "Token " + self._sst.key})
        self._second_group_valves_state = "closed"

    def open_valve_second_group(self):
        requests.patch(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/module_settings/",
                       json={"module_config": {"second_group_valves_state": "opened"}},
                       headers={"Authorization": "Token " + self._sst.key})
        self._second_group_valves_state = "opened"

    def set_on_washing_floors_mode(self):
        requests.patch(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/module_settings/",
                       json={"washing_floors_mode":"on"},
                       headers={"Authorization": "Token " + self._sst.key})
        self._washing_floors_mode = "on"
    def set_off_washing_floors_mode(self):
        requests.patch(SST_CLOUD_API_URL +
                       "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/module_settings/",
                       json={"washing_floors_mode": "off"},
                       headers={"Authorization": "Token " + self._sst.key})
        self._washing_floors_mode = "off"


    @property
    def get_avalible_status(self) -> bool:
        if self._access_status == "available":
            return "true"
        else:
            return "false"

    @property
    def get_device_id(self) -> str:
        return self._id

    @property
    def get_device_name(self) -> str:
        return self._device_name

    @property
    def get_device_type(self) -> int:
        return self._type

    @property
    def get_first_group_valves_state(self) -> str:
        # opened or closed
        return self._first_group_valves_state

    @property
    def get_second_group_valves_state(self) -> str:
        # opened or closed
        return self._second_group_valves_state

    @property
    def get_washing_floors_mode(self)-> str:
        return self._washing_floors_mode

    def update(self) -> None:
        # Обновляем парметры модуля
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id),
                                headers={"Authorization": "Token " + self._sst.key})
        json_device = json.loads(response.text)
        config = json.loads(json_device["parsed_configuration"])
        self._access_status = config["access_status"]  # Main device "available" is true
        self._device_id = config["device_id"]
        self._device_name = json_device["name"]
        self._house_id = json_device["house"]
        self._type = json_device["type"]
        self._id = json_device["id"]
        self._first_group_valves_state = config["module_settings"]["module_config"]["first_group_valves_state"]
        self._second_group_valves_state = config["module_settings"]["module_config"]["second_group_valves_state"]
        self.first_group_alarm = config["module_settings"]["module_status"]["first_group_alarm"]
        self.second_group_alarm = config["module_settings"]["module_status"]["second_group_alarm"]
        self._washing_floors_mode = config["module_settings"]["module_status"]["washing_floors_mode"]
        # Обновляем статус счетчиков
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/counters",
                                headers={"Authorization": "Token " + self._sst.key})
        countersJson = json.loads(response.text)
        for counter in self.counters:
            counter.update(countersJson)

        # Обновляем статус датчиков
        for leakSensor in self.leakSensors:
            leakSensor.update(config["module_settings"]["wire_lines_status"])
        # Обновляем статус беспроводных датчиков
        response = requests.get(SST_CLOUD_API_URL +
                                "houses/" + str(self._house_id) + "/devices/" + str(self._id) + "/wireless_sensors",
                                headers={"Authorization": "Token " + self._sst.key})
        # print(response.text)
        wirelessSensorsJson = json.loads(response.text)
        for wirelessSensor in self.wirelessLeakSensors:
            wirelessSensor.update(wirelessSensorsJson)


class Counter:
    def __init__(self, id: int, name: str, value: int):
        self._id = id
        self.name = name
        self._value = value

    @property
    def counter_id(self) -> int:
        return self._id

    @property
    def counter_name(self) -> str:
        return self.name

    @property
    def counter_value(self) -> int:
        return self._value

    def update(self, countersJson: json) -> None:
        for counterJson in countersJson:
            if self._id == counterJson["id"]:
               self._value = counterJson["value"]


class LeakSensor:
    def __init__(self, name: str, status: str):
        self._name = name
        self._alarm = status

    #  print("name = "+self._name+" alarm = "+self._alarm)
    @property
    def get_leak_sensor_name(self) -> str:
        return self._name

    @property
    def get_leak_sensor_alarm_status(self) -> bool:
        return self._alarm

    def update(self, LeakSensorsDesc: json):
        self._alarm = LeakSensorsDesc[self._name]
    #  print("sensor "+ self._name +" status updated")


class WirelessLeakSensor:
    def __init__(self, wirelessLeakSensorDescription):
        self._type = 868
        self._name = wirelessLeakSensorDescription["name"]
        self._battery_level = wirelessLeakSensorDescription["battery"]
        self._alert = wirelessLeakSensorDescription["attention"]
        self._lost = wirelessLeakSensorDescription["sensor_lost"] #!
        self._battery_discharge = wirelessLeakSensorDescription["battery_discharge"] #!
        self._serial = wirelessLeakSensorDescription["serial_number"] #!


    @property
    def get_wireless_leak_serial_number(self) -> str:
        return self._serial

    @property
    def get_wireless_leak_sensor_name(self) -> str:
        return self._name

    @property
    def get_wireless_leak_sensor_battery_level(self) -> int:
        return self._battery_level

    @property
    def get_wireless_leak_sensor_alert_status(self) -> bool:
        return self._alert

    @property
    def get_wireless_leak_sensor_lost_status(self) -> bool:
        return self._lost

    @property
    def get_wireless_leak_sensor_battery_discharge(self) -> bool:
        return self._battery_discharge

    @property
    def get_type(self) -> int:
        return self._type

    def update(self, wireless_sensor_description: str):
        for sensor_desc in wireless_sensor_description:
            if sensor_desc["name"] == self._name:
                self._battery_level = sensor_desc["battery"]
                self._alert = sensor_desc["attention"]
                self._lost = sensor_desc["sensor_lost"]
                self._battery_discharge = sensor_desc["battery_discharge"]


class WirelessLeakSensor443:
    def __init__(self, wirelessLeakSensorDescription):
        self._name = wirelessLeakSensorDescription["name"]
        self._battery_level = wirelessLeakSensorDescription["battery"]
        self._alert = wirelessLeakSensorDescription["attention"]
        self._line = wirelessLeakSensorDescription["line"]
        self._type = 443


    @property
    def get_type(self) -> int:
        return self._type

    @property
    def get_line(self) -> int:
        return self._line

    @property
    def get_wireless_leak_sensor_name(self) -> str:
        return self._name

    @property
    def get_wireless_leak_sensor_battery_level(self) -> int:
        return self._battery_level

    @property
    def get_wireless_leak_sensor_alert_status(self) -> bool:
        return self._alert

    @property
    def get_wireless_leak_serial_number(self) -> str:
        return self._name + "line" + str(self._line)

    def update(self, wireless_sensor_description: str):
        for sensor_desc in wireless_sensor_description:
            if sensor_desc["name"] == self._name:
                self._battery_level = sensor_desc["battery"]
                self._alert = sensor_desc["attention"]
