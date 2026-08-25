# 📋 Інтерфейс та структура повідомлення HIGH_LATENCY2

Специфікація протоколу великої затримки MAVLink визначає структуру бінарного корисного навантаження повідомлення `HIGH_LATENCY2` (`MSG ID 235`, контрольний байт сумісності `CRC_EXTRA = 179`), алгоритми квантування та масштабування числових полів, маски бітових прапорців діагностики відмов та параметри транзакції керування `MAV_CMD_CONTROL_HIGH_LATENCY` (`#2600`).

### 1. Двійковий формат корисного навантаження HIGH_LATENCY2 (65 байтів)

Усі багатобайтові поля в корисних даних MAVLink зберігаються у форматі Little-Endian (молодший байт розташовано за меншою адресою пам'яті). Поля в структурі впорядковано за спаданням розміру типів даних для уникнення апаратного вирівнювання (padding bytes) на 32- та 64-бітних процесорах ARM Cortex-M та Cortex-A.

| Зсув (B) | Поле | Тип даних | Одиниці вимірювання | Масштабний коефіцієнт | Діапазон значень | Фізичний опис |
|---|---|---|---|---|---|---|
| 0 .. 3 | `timestamp` | `uint32_t` | мілісекунди (мс) | 1 | 0 .. 4 294 967 295 | Час від старту автопілота (або UTC) |
| 4 .. 7 | `latitude` | `int32_t` | градуси × 10⁷ | 1e-7 | -90.0 .. +90.0° | Глобальна широта GPS (WGS-84) |
| 8 .. 11 | `longitude` | `int32_t` | градуси × 10⁷ | 1e-7 | -180.0 .. +180.0° | Глобальна довгота GPS (WGS-84) |
| 12 .. 13 | `custom_mode` | `uint16_t` | перелік | 1 | 0 .. 65535 | Специфічний польотний режим автопілота |
| 14 .. 15 | `altitude` | `int16_t` | метри (м) | 1 | -32768 .. +32767 м | Абсолютна висота над рівнем моря (AMSL) |
| 16 .. 17 | `target_altitude` | `int16_t` | метри (м) | 1 | -32768 .. +32767 м | Цільова задана висота польоту |
| 18 .. 19 | `target_distance` | `uint16_t` | декаметри (дам) | 10 м | 0 .. 655 350 м | Відстань до поточної точки місії |
| 20 .. 21 | `wp_num` | `uint16_t` | номер | 1 | 0 .. 65535 | Індекс активної маршрутної точки |
| 22 .. 23 | `failure_flags` | `uint16_t` | бітова маска | 1 | `HL_FAILURE_FLAG` | Маска відмов сенсорів і підсистем |
| 24 .. 25 | `current_battery` | `int16_t` | 0.1 Ампера (dA) | 100 мА | -3276.8 .. +3276.7 А | Струм споживання від батареї (-1 = невідомо) |
| 26 | `type` | `uint8_t` | enum | 1 | `MAV_TYPE` | Тип літального апарата (літак, коптер тощо) |
| 27 | `autopilot` | `uint8_t` | enum | 1 | `MAV_AUTOPILOT` | Тип польотного стеку (PX4, ArduPilot) |
| 28 | `heading` | `uint8_t` | градуси / 2 | 2° | 0 .. 358° (значення 0..179) | Поточний курс польоту (Yaw/Heading) |
| 29 | `target_heading` | `uint8_t` | градуси / 2 | 2° | 0 .. 358° (значення 0..179) | Цільовий навігаційний курс |
| 30 | `throttle` | `uint8_t` | відсотки (%) | 1% | 0 .. 100% | Рівень газу двигунів (тяга) |
| 31 | `airspeed` | `uint8_t` | м/с × 5 | 0.2 м/с | 0.0 .. 51.0 м/с | Поточна приладова швидкість (IAS) |
| 32 | `airspeed_sp` | `uint8_t` | м/с × 5 | 0.2 м/с | 0.0 .. 51.0 м/с | Задана приладова швидкість (Setpoint) |
| 33 | `groundspeed` | `uint8_t` | м/с × 5 | 0.2 м/с | 0.0 .. 51.0 м/с | Шляхова швидкість відносно землі (GPS) |
| 34 | `windspeed` | `uint8_t` | м/с × 5 | 0.2 м/с | 0.0 .. 51.0 м/с | Оцінка швидкості зустрічного/бокового вітру |
| 35 | `wind_heading` | `uint8_t` | градуси / 2 | 2° | 0 .. 358° | Напрямок, звідки дме вітер |
| 36 | `eph` | `uint8_t` | 0.1 метра (дм) | 0.1 м | 0.0 .. 25.5 м | Горизонтальна похибка GPS (HDOP/EPH) |
| 37 | `epv` | `uint8_t` | 0.1 метра (дм) | 0.1 м | 0.0 .. 25.5 м | Вертикальна похибка GPS (VDOP/EPV) |
| 38 | `temperature_air`| `int8_t` | градуси Цельсія | 1 °C | -128 .. +127 °C | Температура забортного повітря (OAT) |
| 39 | `climb_rate` | `int8_t` | 0.1 м/с (дм/с) | 0.1 м/с | -12.8 .. +12.7 м/с | Вертикальна швидкість (варіометр) |
| 40 | `battery` | `int8_t` | відсотки (%) | 1% | 0 .. 100% (-1 = N/A) | Залишок заряду акумуляторної батареї |
| 41 | `custom0` | `int8_t` | значення | 1 | -128 .. +127 | Поле користувача 0 (наприклад, кадр камери) |
| 42 | `custom1` | `int8_t` | значення | 1 | -128 .. +127 | Поле користувача 1 (статус корисного навантаження) |
| 43 | `custom2` | `int8_t` | значення | 1 | -128 .. +127 | Поле користувача 2 (резерв / діагностика) |
| 44 | `temperature` | `int8_t` | градуси Цельсія | 1 °C | -128 .. +127 °C | Внутрішня температура плати автопілота |
| 45 | `failsafe` | `uint8_t` | бітова маска | 1 | 0 .. 255 | Статус системних захистів від відмов |
| 46 .. 64 | `(extensions)` | `uint8_t[19]` | байти | 1 | — | Резервні поля розширення MAVLink v2 |

### 2. Детальний аналіз функціональних груп полів

Кожне поле структури `HIGH_LATENCY2` спроєктоване таким чином, щоб задовольнити вимоги навігаційної безпеки польоту за мінімальної ентропії даних.

#### А. Координати глобального позиціонування (latitude та longitude)
У стандартному представленні чисел з плаваючою комою одинарної точності IEEE 754 (`float`) мантиса займає 23 біти (еквівалент 7 десяткових знаків). Якщо передавати географічну координату числом `float`, на широті 50° похибка представлення досягає 1.5–2.5 метра, що неприпустимо для точної навігації.
Для усунення цієї похибки в протоколі High Latency координати передаються як 32-бітні знакові цілі числа `int32_t` у масштабі `1e-7` градусів:
* Довжина екватора становить 40 075 000 метрів.
* Дискретність сітки `1e-7` градуса дорівнює:
  ```
  Δx = (40 075 000 м) / (360 · 10⁷) ≈ 0.0111 м = 1.11 см
  ```
Це забезпечує повну сантиметрову точність вимірювання сучасних супутникових приймачів GNSS без жодного округлення чи деградації точності.

#### Б. Барометрична та геометрична висота (altitude та target_altitude)
Поле `altitude` кодується 16-бітним цілим числом `int16_t` в одиницях 1 метр над середнім рівнем моря (AMSL).
Вибір шкали AMSL (а не відносної висоти над точкою старту AGL) обумовлений вимогами аеронавігації: диспетчерські служби та системи запобігання зіткненням у повітрі (ACAS/TCAS) оперують виключно абсолютними висотами тиску.
Діапазон від -32 768 до +32 767 метрів з надлишком покриває всі можливі польотні профілі:
* Від польотів над западинами нижче рівня океану (Мертве море, -430 м);
* До стратосферних висотних безпілотників на сонячних батареях (висоти 20–25 км).
Цільова висота `target_altitude` передається у тій самій шкалі, що дозволяє наземній станції порівнювати фактичний профіль з ешелоном польотного завдання.

#### В. Польотний режим автопілота (custom_mode)
Поле `custom_mode` займає 2 байти (`uint16_t`) і відображає специфічний внутрішній стан польотного стеку:
* **Для автопілотів PX4:** старший байт кодує основний режим (`PX4_CUSTOM_MAIN_MODE`: Manual, Altitude, Position, Auto, Offboard), а молодший байт — підрежим (`PX4_CUSTOM_SUB_MODE_AUTO`: Ready, Takeoff, Loiter, Mission, RTL, Land, Follow Target).
* **Для автопілотів ArduPilot:** значення є числовим номером режиму з переліку `PLANE_MODE` (Manual, Circle, Stabilize, Auto, RTL, Loiter, Guided) або `COPTER_MODE`.
Наземна станція інтерпретує значення поля `custom_mode` з урахуванням байта `autopilot`, що дозволяє коректно відображати назву активного режиму для будь-якого польотного контролера.

#### Г. Комплекс швидкостей та оцінка вітрового дрейфу
Для літаків далекого радіуса дії контроль швидкостей є критичним фактором запобігання аеродинамічному звалюванню (stall):
* `airspeed` — приладова повітряна швидкість, виміряна трубкою Піто. Вона визначає підйомну силу крила. Якщо `airspeed` наближається до мінімальної швидкості звалювання (Vs), оператор бачить загрозу зриву потоку.
* `groundspeed` — шляхова швидкість за GPS.
* `windspeed` та `wind_heading` — розрахунковий вектор вітру, що оцінюється навігаційним фільтром EKF як різниця між вектором повітряної швидкості та вектором шляхової швидкості.
Якщо дрон летить за сильного попутного вітру, шляхова швидкість може складати 35 м/с за приладової швидкості 18 м/с. Наявність усіх чотирьох параметрів дозволяє оператору оцінити запас палива або акумулятора для повернення проти зустрічного вітру.

#### Д. Відстань до цілі та індекс точки маршруту (target_distance та wp_num)
Поле `target_distance` кодується в декаметрах (дам, 1 дам = 10 м). Значення `245` відповідає 2450 метрам. Максимальне число `65535` дозволяє передавати відстань до 655.35 кілометрів, що охоплює найдовші автономні перельоти.
Поле `wp_num` показує номер поточної поворотної точки місії (Waypoint Index), за якою автопілот веде навігацію.

#### Е. Енергетика та тепловий режим
Поле `current_battery` передає струм споживання в десятих долях Ампера (0.1 А або 100 мА). Це дозволяє наземній станції контролювати споживану потужність двигунів та розраховувати залишковий час польоту за формулою:
```
t_remaining_hours = (Battery_Capacity_Ah · battery_pct / 100.0) / (current_battery · 0.1)
```
Поля `temperature` (температура процесора автопілота) та `temperature_air` (температура зовнішнього повітря) виконують функцію запобігання відмовам:
* Різке зростання внутрішньої температури свідчить про перегрів регуляторів живлення BEC або процесора в закритому фюзеляжі.
* Падіння температури зовнішнього повітря нижче 0 °C у поєднанні з високою вологістю сигналізує оператору про ризик обмерзання крила та трубки Піто.

#### Ж. Взаємодія з оптимізацією Zero-Trimming у MAVLink v2
Протокол MAVLink версії 2 підтримує апаратне відтинання нульових байтів у кінці корисного навантаження (Zero-Trimming). Поля структури `HIGH_LATENCY2` навмисно спроєктовані так, що діагностичні прапорці та користувацькі байти `custom0..2`, `temperature`, `failsafe` розташовані в самому хвості структури (байти 41..45).
Якщо під час спокійного крейсерського польоту безпілотника відмови відсутні (`failure_flags == 0`), прапорці захисту не активні (`failsafe == 0`), а додаткові поля користувача дорівнюють нулю, передавач MAVLink 2 автоматично зменшує значення довжини кадру `LEN` з 65 до 40 байтів.
Це дозволяє скоротити фізичний розмір кадру на дроті з 77 байтів до 52 байтів, заощаджуючи додаткові 32% супутникового трафіку в штатних режимах польоту.

### 3. Математичні формули квантування та декодування полів

Для перетворення фізичних дійсних чисел у компактні цілочисельні байти на борту апарата та їх зворотного відновлення на станції керування використовуються такі співвідношення:

#### 1. Навігаційні кути курсу (Heading):
Повний коловий сектор 0..360° упаковується в 1 байт (`uint8_t`) шляхом ділення на 2:
```
Кодування:   heading_byte = (uint8_t)(round(heading_deg / 2.0f)) % 180;
Декодування: heading_deg  = (float)heading_byte * 2.0f;
```
Квантування дає фіксовану роздільну здатність `2.0°` при максимальній похибці округлення `±1.0°`.

#### 2. Швидкості польоту (Airspeed, Groundspeed, Windspeed):
Швидкість у діапазоні 0..51.0 м/с масштабується з коефіцієнтом 5:
```
Кодування:   speed_byte = (uint8_t)fminf(fmaxf(roundf(speed_mps * 5.0f), 0.0f), 255.0f);
Декодування: speed_mps  = (float)speed_byte / 5.0f;
```
Роздільна здатність становить `0.2 м/с` (0.72 км/год).

#### 3. Вертикальна швидкість підйому/спуску (Climb Rate):
Швидкість набору висоти в діапазоні -12.8 .. +12.7 м/с масштабується у дециметри за секунду (фактор 10):
```
Кодування:   climb_byte = (int8_t)fminf(fmaxf(roundf(climb_mps * 10.0f), -128.0f), 127.0f);
Декодування: climb_mps  = (float)climb_byte / 10.0f;
```
Роздільна здатність: `0.1 м/с`.

#### 4. Відстань до точки місії (Target Distance):
Відстань у метрах ділиться на 10 (переведення в декаметри, dam), що забезпечує радіус охоплення до 655.35 км:
```
Кодування:   dist_u16 = (uint16_t)fminf(roundf(dist_meters / 10.0f), 65535.0f);
Декодування: dist_m   = (float)dist_u16 * 10.0f;
```
Роздільна здатність: `10 метрів`.

#### 5. Струм батареї (Current Battery):
Струм у діапазоні від -3276.8 А до +3276.7 А кодується в десятих долях Ампера (100 мА):
```
Кодування:   current_i16 = (int16_t)roundf(current_amps * 10.0f);
Декодування: current_amps = (float)current_i16 / 10.0f;
```

### 4. Бітова маска діагностики відмов HL_FAILURE_FLAG (uint16_t)

Поле `failure_flags` є 16-бітною маскою, у якій кожен окремий біт сигналізує про критичну відмову конкретної бортової апаратної або програмної підсистеми.

:::tabs
```c
typedef enum HL_FAILURE_FLAG {
    HL_FAILURE_FLAG_GPS                   = 1,     // Біт 0: Втрата фіксації GPS або вихід похибки за межі
    HL_FAILURE_FLAG_DIFFERENTIAL_PRESSURE = 2,     // Біт 1: Відмова датчика повітряної швидкості (трубка Піто)
    HL_FAILURE_FLAG_ABSOLUTE_PRESSURE     = 4,     // Біт 2: Відмова барометра (абсолютний тиск)
    HL_FAILURE_FLAG_3D_ACCEL              = 8,     // Біт 3: Збій або розкалібрування акселерометра IMU
    HL_FAILURE_FLAG_3D_GYRO               = 16,    // Біт 4: Збій гіроскопа IMU (дрейф кутової швидкості)
    HL_FAILURE_FLAG_3D_MAG                = 32,    // Біт 5: Магнітна аномалія або відмова компаса
    HL_FAILURE_FLAG_TERRAIN               = 64,    // Біт 6: Недоступні дані висоти рельєфу (Terrain DB)
    HL_FAILURE_FLAG_BATTERY               = 128,   // Біт 7: Критичний рівень розряду батареї або перегрів
    HL_FAILURE_FLAG_RC_RECEIVER           = 256,   // Біт 8: Втрата сигналу апаратури радіокерування (RC)
    HL_FAILURE_FLAG_OFFBOARD              = 512,   // Біт 9: Втрата зв'язку з супутнім бортовим комп'ютером
    HL_FAILURE_FLAG_ENGINE                = 1024,  // Біт 10: Зупинка двигуна, відмова ESC або збій палива
    HL_FAILURE_FLAG_GEOFENCE              = 2048,  // Біт 11: Порушення кордону геозони (Geofence Breach)
    HL_FAILURE_FLAG_ESTIMATOR             = 4096,  // Біт 12: Розбіжність або деградація навігаційного фільтра EKF
    HL_FAILURE_FLAG_MISSION               = 8192   // Біт 13: Некоректне польотне завдання або недосяжна точка
} HL_FAILURE_FLAG;
```
```cpp
enum class HlFailureFlag : uint16_t {
    Gps                  = 1,     // Біт 0: Втрата фіксації GPS або деградація точності
    DifferentialPressure = 2,     // Біт 1: Відмова датчика повітряної швидкості (трубка Піто)
    AbsolutePressure     = 4,     // Біт 2: Відмова барометра
    Accel3D              = 8,     // Біт 3: Збій акселерометра IMU
    Gyro3D               = 16,    // Біт 4: Збій гіроскопа IMU
    Mag3D                = 32,    // Біт 5: Відмова магнітометра / компаса
    Terrain              = 64,    // Біт 6: Відсутність даних висоти рельєфу
    Battery              = 128,   // Біт 7: Критичний розряд батареї або перегрів
    RcReceiver           = 256,   // Біт 8: Втрата сигналу апаратури радіокерування
    Offboard             = 512,   // Біт 9: Втрата зв'язку з супутнім бортовим комп'ютером
    Engine               = 1024,  // Біт 10: Відмова силової установки або регулятора ESC
    Geofence             = 2048,  // Біт 11: Порушення меж дозволеної геозони
    Estimator            = 4096,  // Біт 12: Розбіжність навігаційного фільтра EKF
    Mission              = 8192   // Біт 13: Помилка польотного завдання
};

constexpr HlFailureFlag operator|(HlFailureFlag a, HlFailureFlag b) noexcept {
    return static_cast<HlFailureFlag>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

constexpr bool operator&(HlFailureFlag a, HlFailureFlag b) noexcept {
    return (static_cast<uint16_t>(a) & static_cast<uint16_t>(b)) != 0;
}
```
:::

Фізичні умови спрацьовування прапорців у польотному стеку:
* `HL_FAILURE_FLAG_GPS`: спрацьовує, якщо кількість видимих супутників менше 6, горизонтальна похибка `eph > 3.0 м` або втрачено фіксацію 3D Fix протягом більше ніж 2.0 секунд.
* `HL_FAILURE_FLAG_DIFFERENTIAL_PRESSURE`: встановлюється, якщо тиск датчика швидкості дорівнює нулю під час польоту зі швидкістю понад 15 м/с за GPS (забивання трубки Піто льодом або комахами).
* `HL_FAILURE_FLAG_ESTIMATOR`: сигналізує про перевищення інноваційних нев'язок фільтра EKF (EKF Innovation Test Ratio > 1.0), що означає розбіжність між показами інерційних датчиків та GPS.
* `HL_FAILURE_FLAG_BATTERY`: піднімається при падінні залишкового заряду нижче критичного порогу (наприклад, менше 20%) або при напрузі окремої банки літієвого акумулятора нижче 3.5 В.
* `HL_FAILURE_FLAG_GEOFENCE`: активується при перетині максимального радіуса відльоту від бази або виході за верхню межу ешелону.
* `HL_FAILURE_FLAG_ENGINE`: фіксує зупинку двигуна внутрішнього згоряння (оберти RPM = 0) або перевантаження по струму безколекторного мотора (ESC Overcurrent Alert).

### 5. Команда керування MAV_CMD_CONTROL_HIGH_LATENCY (#2600)

Команда `MAV_CMD_CONTROL_HIGH_LATENCY` надсилається всередині стандартного пакета `COMMAND_LONG` (`#76`) або `COMMAND_INT` (`#75`) і містить такі параметри:

* **Параметр 1 (`Enable/Disable`):**
  * `0.0f` — **Вимкнути High Latency**: відновити стандартні високочастотні потоки телеметрії (завершення супутникового режиму).
  * `1.0f` — **Увімкнути High Latency**: зупинити високочастотні потоки MAVLink та розпочати циклічну трансляцію `HIGH_LATENCY2`.
* **Параметр 2..7:** Зарезервовано для майбутніх розширень (передається значення `0.0f` або `NaN`).

Автопілот підтверджує отримання команди відповіддю `COMMAND_ACK` із результатом `MAV_RESULT_ACCEPTED`. Якщо команда надійшла некоректно або автопілот заблокований у режимі аварійної посадки, повертається `MAV_RESULT_DENIED` або `MAV_RESULT_TEMPORARILY_REJECTED`.

### 6. Побайтний розбір реального кадру HIGH_LATENCY2 у двійковому дампі

Розглянемо практичний бінарний дамп 77-байтового кадру MAVLink v2, перехопленого на послідовному інтерфейсі UART модема Iridium 9603 під час польоту літака над акваторією Чорного моря (координати Одеси: 46.482526° N, 30.723309° E, висота 450 м, курс 124°, швидкість 22.4 м/с, батарея 78%):

```
Побайтний дамп кадру MAVLink v2 (77 байтів):
0x00..09: FD 41 00 00 1A 01 01 EB 00 00 
0x0A..19: 80 F0 36 00 5E 46 B5 1B FD C2 50 12 03 00 C2 01 
0x1A..29: F4 01 F5 00 0E 00 00 00 B9 00 01 03 3E 41 41 70 
0x2A..39: 6E 7C 00 00 00 00 0E 0C 4E 00 00 00 2A 00 00 00 
0x3A..49: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
0x4A..4C: 00 8F C4
```

Детальна побайтова інтерпретація полів кадру:
* `0x00`: `0xFD` — стартовий магічний байт протоколу MAVLink v2 (STX).
* `0x01`: `0x41` (65 десяткове) — довжина корисного навантаження (`LEN = 65 байтів`).
* `0x02`: `0x00` — прапорці несумісності `incompat_flags` (біт 0x01 відсутній — кадр без підпису).
* `0x03`: `0x00` — прапорці сумісності `compat_flags`.
* `0x04`: `0x1A` (26 десяткове) — лічильник послідовності пакета `seq`.
* `0x05`: `0x01` — системний ідентифікатор безпілотника (`sysid = 1`).
* `0x06`: `0x01` — ідентифікатор компонента автопілота (`compid = 1`, `MAV_COMP_ID_AUTOPILOT1`).
* `0x07..09`: `0xEB 0x00 0x00` — 24-бітний числовий ідентифікатор типу повідомлення (`MSG ID 235` = `0x0000EB`, `HIGH_LATENCY2`).
* `0x0A..0D`: `0x80 0xF0 0x36 0x00` — системний час `timestamp = 3 600 000 мс` (1 година польоту від увімкнення живлення).
* `0x0E..11`: `0x5E 0x46 0xB5 0x1B` — широта `latitude = 464 825 246` (`46.4825246° N`).
* `0x12..15`: `0xFD 0xC2 0x50 0x12` — довгота `longitude = 307 233 021` (`30.7233021° E`).
* `0x16..17`: `0x03 0x00` — режим `custom_mode = 3` (`AUTO.MISSION` у польотному стеку PX4).
* `0x18..19`: `0xC2 0x01` — висота `altitude = 450 метрів` AMSL.
* `0x1A..1B`: `0xF4 0x01` — цільова висота `target_altitude = 500 метрів`.
* `0x1C..1D`: `0xF5 0x00` — відстань до точки `target_distance = 245` (2450 метрів).
* `0x1E..1F`: `0x0E 0x00` — номер активної поворотної точки маршруту `wp_num = 14`.
* `0x20..21`: `0x00 0x00` — маска відмов `failure_flags = 0` (усі бортові підсистеми працюють штатно).
* `0x22..23`: `0xB9 0x00` — струм батареї `current_battery = 185` (18.5 Ампера).
* `0x24`: `0x01` — тип літального апарата `type = 1` (`MAV_TYPE_FIXED_WING`).
* `0x25`: `0x03` — тип польотного стеку `autopilot = 3` (`MAV_AUTOPILOT_PX4`).
* `0x26`: `0x3E` — курс `heading = 62` (істинний курс `62 · 2 = 124°`).
* `0x27`: `0x41` — цільовий курс `target_heading = 65` (курс на точку `65 · 2 = 130°`).
* `0x28`: `0x41` — рівень газу `throttle = 65%`.
* `0x29`: `0x70` — приладова повітряна швидкість `airspeed = 112` (`112 / 5 = 22.4 м/с` = 80.6 км/год).
* `0x2A`: `0x6E` — задана швидкість `airspeed_sp = 110` (`22.0 м/с`).
* `0x2B`: `0x7C` — шляхова швидкість за GPS `groundspeed = 124` (`24.8 м/с`).
* `0x30`: `0x0E` — температура забортного повітря `temperature_air = 14 °C`.
* `0x31`: `0x0C` — вертикальна швидкість варіометра `climb_rate = 12` (`+1.2 м/с`).
* `0x32`: `0x4E` — залишковий заряд батареї `battery = 78%`.
* `0x36`: `0x2A` — внутрішня температура автопілота `temperature = 42 °C`.
* `0x4B..4C`: `0x8F 0xC4` — 16-бітна контрольна сума кадру CRC-16/MCRF4XX з урахуванням константи `CRC_EXTRA = 179`.

### 7. Конфігурація маршрутизації в mavlink-router та MAVProxy

У складних бортових комплексах на базі комп'ютерів Linux (Raspberry Pi CM4, Nvidia Jetson) маршрутизація пакетів MAVLink між польотним контролером, супутниковим модемом та відеосистемами покладається на сервіс `mavlink-routerd`.

Конфігураційний файл `/etc/mavlink-router/main.conf` налаштовує вибіркове пропускання високочастотного та супутникового трафіку:

```ini
[General]
ReportTelemetry = false
MavlinkDialect = common

# Основне підключення до польотного контролера Pixhawk (UART)
[UartEndpoint fcu]
Device = /dev/ttyS1
Baud = 115200

# Радіомодем прямої видимості (RF 915 МГц)
[UartEndpoint rf_los]
Device = /dev/ttyUSB0
Baud = 57600

# Супутниковий міст Iridium SBD (режим High Latency)
[UartEndpoint sat_sbd]
Device = /dev/ttyUSB1
Baud = 19200
# Фільтрація: блокувати всі повідомлення, окрім HIGH_LATENCY2 та відповідей на команди
AllowMsgId = 0, 76, 77, 235, 2600
```

Завдяки директиві `AllowMsgId` маршрутизатор апаратно відсікає високочастотні пакети `ATTITUDE` та `GLOBAL_POSITION_INT` від потрапляння у вузький порт супутникового модема, забезпечуючи нульове навантаження черг модема у змішаних режимах польоту.

### 8. Криптографічний підпис на супутникових лініях

Якщо місія вимагає захисту від несанкціонованого перехоплення команд керування зловмисником, супутниковий канал може бути захищений механізмом [криптографічного підпису MAVLink v2](root:sys-dron/mavlink-v2-signing).

При активації підпису:
* У заголовку встановлюється біт `incompat_flags = 0x01` (`MAVLINK_IFLAG_SIGNED`);
* До 77 байтів стандартного кадру додається 13-байтовий трейлер підпису (1 байт `link_id`, 6 байтів монотонного часу `timestamp` та 6 байтів гешу SHA-256);
* Загальний фізичний розмір кадру становить **90 байтів**.

Оскільки 90 байтів повністю вкладаються в максимальний ліміт вихідного буфера модема Iridium 9603 SBD (340 байтів), протокол `HIGH_LATENCY2` зберігає повну сумісність із захищеними лініями зв'язку без додаткової фрагментації пакетів.

### 9. Правила валідації та обробки потоку на наземній станції (GCS)

При розробці парсерів наземних станцій (QGroundControl, Mission Planner) для протоколу великої затримки необхідно дотримуватися спеціальних правил обробки:

1. **Спеціальні значення відсутності даних (Sentinel Values):**
   * Якщо датчик струму не встановлено на борту, поле `current_battery` передає значення `-1` (`0xFFFF` у двійковому вигляді), що інтерпретується як «дані струму недоступні».
   * Якщо автопілот не підтримує вимірювання залишкового відсотка акумулятора, поле `battery` містить `-1` (`0xFF`).
   * Якщо бортовий фільтр вітру ще не зійшовся (наприклад, у перші 60 секунд польоту після зльоту), поля `windspeed` та `wind_heading` передають `0`.
2. **Обробка лічильника послідовності пакетів (Sequence Counter `seq`):**
   * При перемиканні між основним радіоканалом прямої видимості та супутниковим мостом лічильник `seq` не скидається в нуль, а продовжує інкрементуватися. Парсер GCS не повинен трактувати різкий стрибок номера `seq` (спричинений відкиданням високочастотних повідомлень) як втрату пакетів на супутниковій лінії.
3. **Фільтрація та апроксимація курсу та швидкостей:**
   * Оскільки курс `heading` квантується з кроком 2°, на мапі GCS застосовується плавна інтерполяція візуального маркера літака між сусідніми кадрами з урахуванням останньої відомої кутової швидкості.

### 10. Декларації структур та функцій кодування мовами C та C++

:::tabs
```c
#ifndef MAVLINK_HIGH_LATENCY2_H
#define MAVLINK_HIGH_LATENCY2_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAVLINK_MSG_ID_HIGH_LATENCY2 235
#define MAVLINK_MSG_ID_HIGH_LATENCY2_LEN 65
#define MAVLINK_MSG_ID_HIGH_LATENCY2_CRC 179

#pragma pack(push, 1)
typedef struct __mavlink_high_latency2_t {
    uint32_t timestamp;        // Час від старту (мс)
    int32_t  latitude;         // Широта (degE7)
    int32_t  longitude;        // Довгота (degE7)
    uint16_t custom_mode;      // Польотний режим
    int16_t  altitude;         // Висота AMSL (м)
    int16_t  target_altitude;  // Цільова висота (м)
    uint16_t target_distance;  // Відстань до цілі (декаметри, ×10 м)
    uint16_t wp_num;           // Номер точки маршруту
    uint16_t failure_flags;    // Маска відмов (HL_FAILURE_FLAG)
    int16_t  current_battery;  // Струм (0.1 А)
    uint8_t  type;             // MAV_TYPE
    uint8_t  autopilot;        // MAV_AUTOPILOT
    uint8_t  heading;          // Курс (deg / 2)
    uint8_t  target_heading;   // Цільовий курс (deg / 2)
    uint8_t  throttle;         // Газ (0..100%)
    uint8_t  airspeed;         // Приладова швидкість (м/с × 5)
    uint8_t  airspeed_sp;      // Задана швидкість (м/с × 5)
    uint8_t  groundspeed;      // Шляхова швидкість (м/с × 5)
    uint8_t  windspeed;        // Швидкість вітру (м/с × 5)
    uint8_t  wind_heading;     // Напрямок вітру (deg / 2)
    uint8_t  eph;              // Горизонтальна похибка GPS (0.1 м)
    uint8_t  epv;              // Вертикальна похибка GPS (0.1 м)
    int8_t   temperature_air;  // Температура повітря (°C)
    int8_t   climb_rate;       // Вертикальна швидкість (0.1 м/с)
    int8_t   battery;          // Залишок батареї (%)
    int8_t   custom0;          // Поле користувача 0
    int8_t   custom1;          // Поле користувача 1
    int8_t   custom2;          // Поле користувача 2
    int8_t   temperature;      // Температура автопілота (°C)
    uint8_t  failsafe;         // Прапорці захисту failsafe
} mavlink_high_latency2_t;
#pragma pack(pop)

static inline void mavlink_high_latency2_pack_fields(
    mavlink_high_latency2_t *msg,
    uint32_t time_boot_ms,
    double lat, double lon,
    float alt_amsl_m, float target_alt_m,
    float heading_deg, float target_heading_deg,
    float target_dist_m, uint16_t wp_idx,
    float airspeed_mps, float groundspeed_mps,
    float climb_rate_mps, int8_t battery_pct,
    float current_amps, uint16_t fail_flags
) {
    msg->timestamp = time_boot_ms;
    msg->latitude = (int32_t)round(lat * 1e7);
    msg->longitude = (int32_t)round(lon * 1e7);
    msg->altitude = (int16_t)round(alt_amsl_m);
    msg->target_altitude = (int16_t)round(target_alt_m);
    msg->heading = (uint8_t)(round(heading_deg / 2.0f)) % 180;
    msg->target_heading = (uint8_t)(round(target_heading_deg / 2.0f)) % 180;
    msg->target_distance = (uint16_t)fminf(roundf(target_dist_m / 10.0f), 65535.0f);
    msg->wp_num = wp_idx;
    msg->airspeed = (uint8_t)fminf(roundf(airspeed_mps * 5.0f), 255.0f);
    msg->groundspeed = (uint8_t)fminf(roundf(groundspeed_mps * 5.0f), 255.0f);
    msg->climb_rate = (int8_t)fminf(fmaxf(roundf(climb_rate_mps * 10.0f), -128.0f), 127.0f);
    msg->battery = battery_pct;
    msg->current_battery = (int16_t)round(current_amps * 10.0f);
    msg->failure_flags = fail_flags;
}

#endif // MAVLINK_HIGH_LATENCY2_H
```
```cpp
#pragma once

#include <cstdint>
#include <array>
#include <optional>
#include <span>
#include <cmath>
#include <algorithm>

namespace mavlink {

struct HighLatency2 {
    uint32_t timestamp_ms{0};
    double   latitude_deg{0.0};
    double   longitude_deg{0.0};
    uint16_t custom_mode{0};
    int16_t  altitude_m{0};
    int16_t  target_altitude_m{0};
    float    target_distance_m{0.0f};
    uint16_t waypoint_index{0};
    HlFailureFlag failure_flags{static_cast<HlFailureFlag>(0)};
    float    battery_current_a{0.0f};
    uint8_t  system_type{0};
    uint8_t  autopilot_type{0};
    float    heading_deg{0.0f};
    float    target_heading_deg{0.0f};
    uint8_t  throttle_pct{0};
    float    airspeed_mps{0.0f};
    float    airspeed_sp_mps{0.0f};
    float    groundspeed_mps{0.0f};
    float    windspeed_mps{0.0f};
    float    wind_heading_deg{0.0f};
    float    eph_m{0.0f};
    float    epv_m{0.0f};
    int8_t   air_temperature_c{0};
    float    climb_rate_mps{0.0f};
    int8_t   battery_pct{0};
    int8_t   custom0{0};
    int8_t   custom1{0};
    int8_t   custom2{0};
    int8_t   board_temperature_c{0};
    uint8_t  failsafe_flags{0};

    [[nodiscard]] std::array<uint8_t, 65> serialize() const noexcept {
        std::array<uint8_t, 65> buf{};
        auto write_u32 = [&](size_t off, uint32_t v) {
            buf[off] = static_cast<uint8_t>(v);
            buf[off+1] = static_cast<uint8_t>(v >> 8);
            buf[off+2] = static_cast<uint8_t>(v >> 16);
            buf[off+3] = static_cast<uint8_t>(v >> 24);
        };
        auto write_i32 = [&](size_t off, int32_t v) { write_u32(off, static_cast<uint32_t>(v)); };
        auto write_u16 = [&](size_t off, uint16_t v) {
            buf[off] = static_cast<uint8_t>(v);
            buf[off+1] = static_cast<uint8_t>(v >> 8);
        };
        auto write_i16 = [&](size_t off, int16_t v) { write_u16(off, static_cast<uint16_t>(v)); };

        write_u32(0, timestamp_ms);
        write_i32(4, static_cast<int32_t>(std::round(latitude_deg * 1e7)));
        write_i32(8, static_cast<int32_t>(std::round(longitude_deg * 1e7)));
        write_u16(12, custom_mode);
        write_i16(14, altitude_m);
        write_i16(16, target_altitude_m);
        write_u16(18, static_cast<uint16_t>(std::clamp(std::round(target_distance_m / 10.0f), 0.0f, 65535.0f)));
        write_u16(20, waypoint_index);
        write_u16(22, static_cast<uint16_t>(failure_flags));
        write_i16(24, static_cast<int16_t>(std::round(battery_current_a * 10.0f)));

        buf[26] = system_type;
        buf[27] = autopilot_type;
        buf[28] = static_cast<uint8_t>(std::fmod(std::round(heading_deg / 2.0f), 180.0f));
        buf[29] = static_cast<uint8_t>(std::fmod(std::round(target_heading_deg / 2.0f), 180.0f));
        buf[30] = throttle_pct;
        buf[31] = static_cast<uint8_t>(std::clamp(std::round(airspeed_mps * 5.0f), 0.0f, 255.0f));
        buf[32] = static_cast<uint8_t>(std::clamp(std::round(airspeed_sp_mps * 5.0f), 0.0f, 255.0f));
        buf[33] = static_cast<uint8_t>(std::clamp(std::round(groundspeed_mps * 5.0f), 0.0f, 255.0f));
        buf[34] = static_cast<uint8_t>(std::clamp(std::round(windspeed_mps * 5.0f), 0.0f, 255.0f));
        buf[35] = static_cast<uint8_t>(std::fmod(std::round(wind_heading_deg / 2.0f), 180.0f));
        buf[36] = static_cast<uint8_t>(std::clamp(std::round(eph_m * 10.0f), 0.0f, 255.0f));
        buf[37] = static_cast<uint8_t>(std::clamp(std::round(epv_m * 10.0f), 0.0f, 255.0f));
        buf[38] = static_cast<uint8_t>(air_temperature_c);
        buf[39] = static_cast<uint8_t>(static_cast<int8_t>(std::clamp(std::round(climb_rate_mps * 10.0f), -128.0f, 127.0f)));
        buf[40] = static_cast<uint8_t>(battery_pct);
        buf[41] = static_cast<uint8_t>(custom0);
        buf[42] = static_cast<uint8_t>(custom1);
        buf[43] = static_cast<uint8_t>(custom2);
        buf[44] = static_cast<uint8_t>(board_temperature_c);
        buf[45] = failsafe_flags;

        return buf;
    }

    static HighLatency2 deserialize(std::span<const uint8_t, 65> data) noexcept {
        HighLatency2 msg{};
        auto read_u32 = [&](size_t off) -> uint32_t {
            return static_cast<uint32_t>(data[off]) |
                   (static_cast<uint32_t>(data[off+1]) << 8) |
                   (static_cast<uint32_t>(data[off+2]) << 16) |
                   (static_cast<uint32_t>(data[off+3]) << 24);
        };
        auto read_i32 = [&](size_t off) -> int32_t { return static_cast<int32_t>(read_u32(off)); };
        auto read_u16 = [&](size_t off) -> uint16_t {
            return static_cast<uint16_t>(data[off]) | (static_cast<uint16_t>(data[off+1]) << 8);
        };
        auto read_i16 = [&](size_t off) -> int16_t { return static_cast<int16_t>(read_u16(off)); };

        msg.timestamp_ms = read_u32(0);
        msg.latitude_deg = static_cast<double>(read_i32(4)) * 1e-7;
        msg.longitude_deg = static_cast<double>(read_i32(8)) * 1e-7;
        msg.custom_mode = read_u16(12);
        msg.altitude_m = read_i16(14);
        msg.target_altitude_m = read_i16(16);
        msg.target_distance_m = static_cast<float>(read_u16(18)) * 10.0f;
        msg.waypoint_index = read_u16(20);
        msg.failure_flags = static_cast<HlFailureFlag>(read_u16(22));
        msg.battery_current_a = static_cast<float>(read_i16(24)) * 0.1f;

        msg.system_type = data[26];
        msg.autopilot_type = data[27];
        msg.heading_deg = static_cast<float>(data[28]) * 2.0f;
        msg.target_heading_deg = static_cast<float>(data[29]) * 2.0f;
        msg.throttle_pct = data[30];
        msg.airspeed_mps = static_cast<float>(data[31]) / 5.0f;
        msg.airspeed_sp_mps = static_cast<float>(data[32]) / 5.0f;
        msg.groundspeed_mps = static_cast<float>(data[33]) / 5.0f;
        msg.windspeed_mps = static_cast<float>(data[34]) / 5.0f;
        msg.wind_heading_deg = static_cast<float>(data[35]) * 2.0f;
        msg.eph_m = static_cast<float>(data[36]) * 0.1f;
        msg.epv_m = static_cast<float>(data[37]) * 0.1f;
        msg.air_temperature_c = static_cast<int8_t>(data[38]);
        msg.climb_rate_mps = static_cast<float>(static_cast<int8_t>(data[39])) * 0.1f;
        msg.battery_pct = static_cast<int8_t>(data[40]);
        msg.custom0 = static_cast<int8_t>(data[41]);
        msg.custom1 = static_cast<int8_t>(data[42]);
        msg.custom2 = static_cast<int8_t>(data[43]);
        msg.board_temperature_c = static_cast<int8_t>(data[44]);
        msg.failsafe_flags = data[45];

        return msg;
    }
};

} // namespace mavlink
```
:::
