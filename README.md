# SST Cloud Integration


Unofficial SST Cloud integration for Home Assistant


Не официальный плагин для интеграции с облаком SST Cloud


Теперь доступна утсановка из каталога HACS

На текущий момент работает с защитой от протечек. Протестировано на модуле Neptun Smart и ProW+ WiFi. 

А так же с терморегуляторами Equation и EcoSmart 25



# Установка

## Вариант 1 - через HACS
1) Перейти в HACS -> Добавить репозиторий -> в поиске ввести sst Cloud, кликнуть на найденый репозиторий и нажать загрузить.


![изображение](https://user-images.githubusercontent.com/18576858/224535384-4716011b-6037-420b-b320-cdc704e0c933.png)


2) Перезагрузить HA.
3) Настроить интеграцию - Конфигурация -> Устройства и службы -> Добавить интеграцию, в поиске ввести SST, выбрать интеграцию "SST Cloud Integration"


![изображение](https://user-images.githubusercontent.com/18576858/166641784-4cb8b22b-7789-4bc6-942e-467077b82e06.png)

(Если такая интеграция не находится, Ctrl + F5, чтобы обновить кэш браузера)

Ввести логин и пароль.

![изображение](https://user-images.githubusercontent.com/18576858/187661775-a3f47f99-b9bb-427c-bf5b-c85fd4b93172.png)


## Вариант 2 - Вручную
1) Cкопировать каталог sst_cloud из репозитория в папку custom_components на сервере Home Assistant
2)Перезагрузить HA.
3) Настроить интеграцию - Конфигурация -> Устройства и службы -> Добавить интеграцию, в поиске ввести SST, выбрать интеграцию "SST Cloud Integration"


![изображение](https://user-images.githubusercontent.com/18576858/166641784-4cb8b22b-7789-4bc6-942e-467077b82e06.png)

(Если такая интеграция не находится, Ctrl + F5, чтобы обновить кэш браузера)

Ввести логин и пароль.

![изображение](https://user-images.githubusercontent.com/18576858/187661824-b0b3ee11-983a-4e59-bf56-4277e97bb2e0.png)


## Добавление счечиков для контроля потребляния воды в HA
к сожалению HA почему то не видит SensorStateClass.TOTAL видимо поэтому не отображает в энергии.
Есть обходной путь, добавить в configuration.yaml для каждого счетчика:
```
template:
  - sensor:
    - name: "water counter"
    state: "{{ states('sensor.watercounter') }}"
    unit_of_measurement: m³
    device_class: water
    state_class: total_increasing
```
Тогда будет еще одно устройство, которое уже можно добавить в энергию

