# Робота з Thermal Sysfs API

Інтерфейс sysfs надає простий спосіб взаємодії з тепловим каркасом із користувацького простору (userspace).

Усі теплові пристрої лежать у теці `/sys/class/thermal/`.

## Перегляд інформації про зони
Переглянемо список доступних теплових зон:
```bash
$ ls -1 /sys/class/thermal/ | grep thermal_zone
thermal_zone0
thermal_zone1
```

Щоб дізнатись тип першої зони (наприклад, що саме вона вимірює):
```bash
$ cat /sys/class/thermal/thermal_zone0/type
x86_pkg_temp
```

Отримати поточну температуру:
```bash
$ cat /sys/class/thermal/thermal_zone0/temp
45000
```
Значення вказується у міліградусах Цельсія, тобто `45000` = `45°C`.

## Перегляд точок спрацювання (Trip Points)
Для кожної зони можна побачити її точки спрацювання та їх типи:
```bash
$ cat /sys/class/thermal/thermal_zone0/trip_point_0_temp
80000
$ cat /sys/class/thermal/thermal_zone0/trip_point_0_type
passive
```
Тип порогу тут не випадковий. Драйвер пакетного датчика заводить щонайбільше два пороги (`#define MAX_NUMBER_OF_TRIPS 2`) і обидва — пасивними: `trips[i].type = THERMAL_TRIP_PASSIVE` у `drivers/thermal/intel/x86_pkg_temp_thermal.c`. Саму температуру він рахує від межі кристала за зсувом із регістра порогів — `trips[i].temperature = tj_max - thres_reg_value * 1000` — тож `80000` тут означає `Tj_max` 100 °C мінус запрограмований зсув 20 °C, а не якесь власне число драйвера. Поки зсув нульовий, поріг вважається незаданим і ядро тримає в ньому `THERMAL_TEMP_INVALID` (−274000).

Переносити ці числа на іншу платформу не варто: в описі ARM-зони з основної статті 95 °C — це **критичний** поріг, оголошений у дереві пристроїв, і дія за ним зовсім інша (аварійне вимкнення, а не зниження частоти).

Якщо ви маєте права суперкористувача, температуру точок спрацювання можна змінювати, записуючи нові значення у файл `trip_point_X_temp` — але лише там, де драйвер позначив поріг прапорцем `THERMAL_TRIP_FLAG_RW_TEMP`. Пакетний датчик x86 — саме такий випадок: запис у файл доходить до регістра порогів.

## Пристрої охолодження (Cooling Devices)
Пристрої охолодження також представлені в цій теці:
```bash
$ ls -1 /sys/class/thermal/ | grep cooling_device
cooling_device0
cooling_device1
```

Кожен пристрій має поточний стан (`cur_state`) та максимальний стан (`max_state`):
```bash
$ cat /sys/class/thermal/cooling_device0/type
Processor
$ cat /sys/class/thermal/cooling_device0/max_state
10
$ cat /sys/class/thermal/cooling_device0/cur_state
0
```
Значення `0` зазвичай означає відсутність охолодження (наприклад, вентилятор вимкнений або процесор працює на максимальній частоті). Значення `max_state` означає максимальне зусилля охолодження.
