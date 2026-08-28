# 📋 Специфікація повідомлень і структур даних первинного рукостискання MAVLink

Цей довідник містить вичерпний опис бінарного формату кадру, полів корисного навантаження, сигнатур пакування, структур даних та числових переліків констант, що визначають протокольну взаємодію між наземною станцією керування (GCS) та бортовим автопілотом на етапі первинного рукостискання за стандартом MAVLink v2.

---

### 1. Загальні правила серіалізації, кадрування та вирівнювання MAVLink v2

Протокол MAVLink v2 є бінарним пакетним протоколом із фіксованим заголовком і змінною довжиною корисного навантаження. Загальна структура кадру в каналі зв'язку має такий вигляд:

```
+-----+-----+----------+----------+-----+--------+--------+--------+------------------+---------+-------------------+
| STX | LEN | INC_FLAGS| CMP_FLAGS| SEQ | SYS_ID | COMP_ID| MSG_ID |     PAYLOAD      | CHECKSUM| SIGNATURE (opt)   |
| 1B  | 1B  | 1B       | 1B       | 1B  | 1B     | 1B     | 3B     |    0..255 B      | 2B (CRC)| 13B               |
+-----+-----+----------+----------+-----+--------+--------+--------+------------------+---------+-------------------+
```

#### Поля заголовка кадру

* **`STX` (Magic Byte)**: маркер початку пакета. Для MAVLink v2 завжди дорівнює `0xFD` (у застарілому v1 використовувався `0xFE`).
* **`LEN` (Payload Length)**: довжина корисного навантаження в байтах (від 0 до 255).
* **`INC_FLAGS` (Incompatibility Flags)**: прапорці несумісності. Якщо приймач не підтримує встановлені тут біти (наприклад, біт `0x01` — наявність криптографічного підпису кадру), пакет повинен бути відкинутий.
* **`CMP_FLAGS` (Compatibility Flags)**: прапорці сумісності. Вказують на розширення, які старі приймачі можуть безпечно ігнорувати.
* **`SEQ` (Sequence Counter)**: циклічний лічильник пакетів відправника від 0 до 255. Дозволяє виявляти втрати пакетів у каналі зв'язку.
* **`SYS_ID` (System ID)**: системний ідентифікатор апарата-відправника (1..254). Значення 255 традиційно зарезервовано за наземною станцією.
* **`COMP_ID` (Component ID)**: ідентифікатор конкретного бортового модуля (1 = автопілот, 154 = підвіс камери, 191 = бортовий комп'ютер).
* **`MSG_ID` (Message ID)**: 24-бітний числовий код типу повідомлення (на відміну від 8-бітного в MAVLink v1).
* **`PAYLOAD`**: серіалізоване тіло повідомлення.
* **`CHECKSUM` (CRC16-MCRF4XX)**: 16-бітна циклічна контрольна сума, що розраховується за алгоритмом X.25 для заголовка та навантаження, із додаванням завершального байта `CRC-EXTRA`.
* **`SIGNATURE` (необов'язково)**: 13 байтів аутентифікації (ID ключа, часова мітка та 48-бітний хеш SHA-256).

#### Вирівнювання пам'яті та механізм зрізання нулів (Zero-Truncation)

У кожному повідомленні MAVLink v2 поля корисного навантаження впорядковуються генератором коду строго за спаданням розміру типів: 64-бітні поля (`uint64_t`, `int64_t`, `double`), потім 32-бітні (`uint32_t`, `int32_t`, `float`), 16-бітні (`uint16_t`, `int16_t`) і наприкінці 8-бітні (`uint8_t`, `int8_t`, `char`). Це усуває внутрішнє вирівнювання (Memory Alignment Padding) на 32-бітних і 64-бітних архітектурах мікроконтролерів і гарантує байтову ідентичність кадру в ефірі незалежно від компілятора.

Для заощадження пропускної здатності радіоканалу в MAVLink v2 реалізовано механізм **Zero-Truncation**: якщо наприкінці корисного навантаження стоять нульові байти, генератор відтинає їх перед відправкою, зменшуючи поле `LEN`. Приймач автоматично доповнює буфер нулями до повного розміру структури перед розпакуванням.

#### Механізм CRC-EXTRA

Для захисту від неузгодженості діалектів MAVLink обчислює додатковий байт контрольної суми — **CRC-EXTRA**. Він розраховується від імені повідомлення та типів його полів у файлі визначення XML. Якщо станція та автопілот збігаються за номером повідомлення `msgid`, але мають різний набір полів або різні типи даних, байт CRC-EXTRA не зійдеться, і приймач безпечно відкине пакет як несумісний, захищаючи пам'ять від пошкодження.

---

### 2. Ідентифікація та контроль присутності: повідомлення HEARTBEAT (#0, CRC-EXTRA: 50)

Повідомлення `HEARTBEAT` транслюється всіма активними вузлами бездротової мережі з фіксованою частотою 1 Гц для оголошення адреси, типу платформи, стану готовності та версії протоколу.

:::tabs
```c
// Структура кадру HEARTBEAT у мові C (заголовок mavlink_msg_heartbeat.h)
typedef struct __mavlink_heartbeat_t {
    uint32_t custom_mode;     // Специфічний числовий код польотного режиму прошивки
    uint8_t  type;            // Тип платформи (enum MAV_TYPE)
    uint8_t  autopilot;       // Тип польотного стеку (enum MAV_AUTOPILOT)
    uint8_t  base_mode;       // Бітова маска базових станів (enum MAV_MODE_FLAG)
    uint8_t  system_status;   // Загальний стан готовності ядра (enum MAV_STATE)
    uint8_t  mavlink_version; // Версія протоколу відправника (3 для MAVLink v2)
} mavlink_heartbeat_t;
```
```cpp
// Ідіоматична обгортка структури HEARTBEAT у C++20
struct MavlinkHeartbeat {
    uint32_t custom_mode{0};
    uint8_t  type{0};
    uint8_t  autopilot{0};
    uint8_t  base_mode{0};
    uint8_t  system_status{0};
    uint8_t  mavlink_version{3};

    [[nodiscard]] constexpr bool isArmed() const noexcept {
        return (base_mode & 0x80) != 0; // MAV_MODE_FLAG_SAFETY_ARMED
    }

    [[nodiscard]] constexpr bool isAuto() const noexcept {
        return (base_mode & 0x04) != 0; // MAV_MODE_FLAG_AUTO_ENABLED
    }

    [[nodiscard]] constexpr bool isGuided() const noexcept {
        return (base_mode & 0x08) != 0; // MAV_MODE_FLAG_GUIDED_ENABLED
    }
};
```
:::

#### Таблиця полів повідомлення HEARTBEAT

| Поле | Тип | Діапазон | Опис призначення |
| :--- | :--- | :--- | :--- |
| `custom_mode` | `uint32_t` | `0 .. 0xFFFFFFFF` | Код польотного режиму. В ArduPilot транслюється як ціле число (0=STABILIZE, 3=AUTO, 4=GUIDED, 5=LOITER, 6=RTL). У PX4 кодується 32-бітною маскою `(main_mode << 16) \| (sub_mode << 24)`. |
| `type` | `uint8_t` | `enum MAV_TYPE` | Фізичний тип апарата: 1=FIXED_WING, 2=QUADROTOR, 3=COAXIAL, 4=HELICOPTER, 10=GROUND_ROVER, 12=SUBMARINE, 27=VTOL_TAILSITTER. Визначає графічну модель у GCS. |
| `autopilot` | `uint8_t` | `enum MAV_AUTOPILOT` | Тип польотного стеку: 3=ARDUPILOTMEGA, 12=PX4, 0=GENERIC. Визначає семантику команд та таблицю параметрів. |
| `base_mode` | `uint8_t` | `enum MAV_MODE_FLAG` | Бітова маска стандартних прапорців стану ядра керування. |
| `system_status` | `uint8_t` | `enum MAV_STATE` | Стан живлення й готовності: 0=UNINIT, 1=BOOT, 2=CALIBRATING, 3=STANDBY, 4=ACTIVE, 5=CRITICAL, 6=EMERGENCY, 7=POWEROFF. |
| `mavlink_version`| `uint8_t` | `3` | Версія протоколу передавача (константа 3 для MAVLink v2, 2 для v1). |

#### Типи апаратів (`MAV_TYPE`)

| Код | Константа | Опис |
| :--- | :--- | :--- |
| 0 | `MAV_TYPE_GENERIC` | Універсальний невідомий пристрій |
| 1 | `MAV_TYPE_FIXED_WING` | Літак класичної схеми (планер, дельтаплан) |
| 2 | `MAV_TYPE_QUADROTOR` | Квадрокоптер (4 мотори) |
| 3 | `MAV_TYPE_COAXIAL` | Співвісний гелікоптер або мультикоптер |
| 4 | `MAV_TYPE_HELICOPTER` | Класичний гелікоптер з автоматом перекосу |
| 10 | `MAV_TYPE_GROUND_ROVER` | Наземний колісний або гусеничний робот |
| 11 | `MAV_TYPE_SURFACE_BOAT` | Наводний катер |
| 12 | `MAV_TYPE_SUBMARINE` | Підводний апарат (ROV/AUV) |
| 13 | `MAV_TYPE_HEXAROTOR` | Гексакоптер (6 моторів) |
| 14 | `MAV_TYPE_OCTOROTOR` | Октокоптер (8 моторів) |
| 20 | `MAV_TYPE_VTOL_TILTROTOR`| VTOL із поворотними двигунами |
| 27 | `MAV_TYPE_VTOL_TAILSITTER`| VTOL, що злітає вертикально на хвості |

#### Типи автопілотів (`MAV_AUTOPILOT`)

| Код | Константа | Польотний стек |
| :--- | :--- | :--- |
| 0 | `MAV_AUTOPILOT_GENERIC` | Загальний автопілот без специфічного діалекту |
| 3 | `MAV_AUTOPILOT_ARDUPILOTMEGA` | ArduPilot (ArduCopter, ArduPlane, ArduRover, ArduSub) |
| 12 | `MAV_AUTOPILOT_PX4` | PX4 Autopilot (Dronecode стек) |
| 13 | `MAV_AUTOPILOT_SMACCMPILOT` | SMACCMPilot експериментальний верифікований стек |
| 14 | `MAV_AUTOPILOT_AUTOQUAD` | AutoQuad професійний контролер |

#### Бітова маска `base_mode` (`MAV_MODE_FLAG`)

| Біт | Прапорець | Значення | Опис поведінки апарата |
| :--- | :--- | :--- | :--- |
| 7 | `MAV_MODE_FLAG_SAFETY_ARMED` | `128` (`0x80`) | **1** — мотори під напругою, апарат зброєний (ARMED); **0** — мотори знеструмлені (DISARMED). |
| 6 | `MAV_MODE_FLAG_MANUAL_INPUT_ENABLED` | `64` (`0x40`) | Керування з пульту RC або джойстика GCS активне. |
| 5 | `MAV_MODE_FLAG_HIL_ENABLED` | `32` (`0x20`) | Апарат працює в режимі симуляції Hardware-in-the-Loop. |
| 4 | `MAV_MODE_FLAG_STABILIZED_ENABLED` | `16` (`0x10`) | Алгоритми стабілізації кутових швидкостей та орієнтації активні. |
| 3 | `MAV_MODE_FLAG_GUIDED_ENABLED` | `8` (`0x08`) | Борт приймає прямі цільові точки (Setpoints) від GCS або супутнього комп'ютера. |
| 2 | `MAV_MODE_FLAG_AUTO_ENABLED` | `4` (`0x04`) | Автопілот виконує завантажену автономну польотну місію (Waypoints). |
| 1 | `MAV_MODE_FLAG_TEST_ENABLED` | `2` (`0x02`) | Режим заводського або лабораторного тестування. |
| 0 | `MAV_MODE_FLAG_CUSTOM_MODE_ENABLED`| `1` (`0x01`) | **1** — поле `custom_mode` є валідним і має пріоритет над базовими прапорцями. |

---

### 3. Протокол завантаження параметрів (Parameter Protocol)

Протокол параметрів синхронізує таблицю налаштувань автопілота з локальною базою даних наземної станції. Усі параметри ідентифікуються 16-байтним рядком ASCII та передаються у форматі 32-бітного значення.

#### 3.1. Повідомлення `PARAM_REQUEST_LIST` (#21, CRC-EXTRA: 159)

Надсилається наземною станцією для ініціалізації масового вивантаження всієї таблиці конфігурації.

:::tabs
```c
typedef struct __mavlink_param_request_list_t {
    uint8_t target_system;    // SysID цільового апарата (зазвичай 1)
    uint8_t target_component; // CompID цільового компонента (зазвичай 1: MAV_COMP_ID_AUTOPILOT1)
} mavlink_param_request_list_t;
```
```cpp
struct MavlinkParamRequestList {
    uint8_t target_system{1};
    uint8_t target_component{1};
};
```
:::

#### 3.2. Повідомлення `PARAM_REQUEST_READ` (#20, CRC-EXTRA: 214)

Використовується для точкового дозапиту окремого параметра, втраченого під час передачі через радіозавади. Якщо поле `param_index >= 0`, пошук виконується за індексом; якщо `param_index = -1`, пошук виконується за рядком `param_id`.

:::tabs
```c
typedef struct __mavlink_param_request_read_t {
    int16_t param_index;      // Індекс параметра (0 .. param_count-1). Якщо >= 0, запит за індексом.
    uint8_t target_system;    // SysID автопілота
    uint8_t target_component; // CompID автопілота
    char    param_id[16];     // Назва параметра (ASCII-рядок, нуль-термінований або доповнений нулями)
} mavlink_param_request_read_t;
```
```cpp
struct MavlinkParamRequestRead {
    int16_t param_index{-1};
    uint8_t target_system{1};
    uint8_t target_component{1};
    char    param_id[16]{0};
};
```
:::

#### 3.3. Повідомлення `PARAM_VALUE` (#22, CRC-EXTRA: 220)

Транслюється автопілотом у відповідь на запити списку або окремого параметра.

:::tabs
```c
typedef struct __mavlink_param_value_t {
    float    param_value;     // Значення параметра (IEEE 754 float32)
    uint16_t param_count;     // Загальна кількість параметрів у пам'яті автопілота (N)
    uint16_t param_index;     // Порядковий індекс поточного параметра (0 .. N-1)
    char     param_id[16];    // Текстовий ідентифікатор параметра (наприклад, "WPNAV_SPEED\0")
    uint8_t  param_type;      // Тип даних (enum MAV_PARAM_TYPE)
} mavlink_param_value_t;
```
```cpp
struct MavlinkParamValue {
    float    param_value{0.0f};
    uint16_t param_count{0};
    uint16_t param_index{0};
    char     param_id[16]{0};
    uint8_t  param_type{0};
};
```
:::

#### Типи даних параметрів (`MAV_PARAM_TYPE`)

Усі типи даних передаються всередині 4-байтового поля `param_value`. Для цілих чисел значення запаковується за допомогою побітового копіювання (`std::memcpy` або бітовий каст), щоб запобігти спотворенню 32-бітних цілих чисел при неявному перетворенні на `float`.

| Код | Константа | Розмір | Спосіб розпакування |
| :--- | :--- | :--- | :--- |
| 1 | `MAV_PARAM_TYPE_UINT8` | 1 байт | Пряме читання молодшого байта `(uint8_t)param_value` |
| 2 | `MAV_PARAM_TYPE_INT8` | 1 байт | Читання знакового байта `(int8_t)param_value` |
| 3 | `MAV_PARAM_TYPE_UINT16` | 2 байти | Побітове читання молодших 16 бітів |
| 4 | `MAV_PARAM_TYPE_INT16` | 2 байти | Побітове читання знакових 16 бітів |
| 5 | `MAV_PARAM_TYPE_UINT32` | 4 байти | `uint32_t val; std::memcpy(&val, &pv.param_value, 4);` |
| 6 | `MAV_PARAM_TYPE_INT32` | 4 байти | `int32_t val; std::memcpy(&val, &pv.param_value, 4);` |
| 9 | `MAV_PARAM_TYPE_REAL32` | 4 байти | Пряме використання значення `param_value` як `float` |

---

### 4. Налаштування потоків телеметрії: `MAV_CMD_SET_MESSAGE_INTERVAL` (#511)

Налаштування індивідуальних частот відправки повідомлень виконується через універсальне командне повідомлення `COMMAND_LONG` (`#76`, CRC-EXTRA: 152).

:::tabs
```c
typedef struct __mavlink_command_long_t {
    float    param1;          // Target Message ID (наприклад, 30 для ATTITUDE)
    float    param2;          // Інтервал у мікросекундах (1 000 000 / частота в Гц). -1 = вимкнути, 0 = дефолт
    float    param3;          // Резерв (0.0f)
    float    param4;          // Резерв (0.0f)
    float    param5;          // Резерв (0.0f)
    float    param6;          // Резерв (0.0f)
    float    param7;          // Response Target (0 = транслювати на поточний порт)
    uint16_t command;         // MAV_CMD_SET_MESSAGE_INTERVAL (511)
    uint8_t  target_system;    // SysID автопілота
    uint8_t  target_component; // CompID автопілота
    uint8_t  confirmation;     // Номер спроби (0 при першому надсиланні, 1..N при повторах)
} mavlink_command_long_t;
```
```cpp
struct MavlinkCommandLong {
    float    param1{0.0f};
    float    param2{0.0f};
    float    param3{0.0f};
    float    param4{0.0f};
    float    param5{0.0f};
    float    param6{0.0f};
    float    param7{0.0f};
    uint16_t command{0};
    uint8_t  target_system{1};
    uint8_t  target_component{1};
    uint8_t  confirmation{0};
};
```
:::

#### Підтвердження виконання команд: `COMMAND_ACK` (#77, CRC-EXTRA: 143)

Автопілот відповідає на кожну команду `COMMAND_LONG` кадром `COMMAND_ACK`.

:::tabs
```c
typedef struct __mavlink_command_ack_t {
    uint16_t command;        // Код команди, що підтверджується (511)
    uint8_t  result;         // Результат виконання (enum MAV_RESULT)
    uint8_t  progress;       // Прогрес виконання 0..100 (MAVLink v2 extension)
    int32_t  result_param2;  // Додатковий числовий код помилки прошивки
    uint8_t  target_system;   // SysID станції
    uint8_t  target_component;// CompID станції
} mavlink_command_ack_t;
```
```cpp
struct MavlinkCommandAck {
    uint16_t command{0};
    uint8_t  result{0};
    uint8_t  progress{0};
    int32_t  result_param2{0};
    uint8_t  target_system{0};
    uint8_t  target_component{0};
};
```
:::

#### Коди результатів виконання команд (`MAV_RESULT`)

| Код | Константа | Значення | Дія станції |
| :--- | :--- | :--- | :--- |
| 0 | `MAV_RESULT_ACCEPTED` | Команду прийнято й успішно виконано | Перехід до наступного потоку |
| 1 | `MAV_RESULT_TEMPORARILY_REJECTED` | Тимчасова відмова (борт зайнятий) | Повторити запит через 200–500 мс |
| 2 | `MAV_RESULT_DENIED` | Відхилено (неприпустима дія в поточному стані) | Зафіксувати попередження в журналі |
| 3 | `MAV_RESULT_UNSUPPORTED` | Команда не підтримується прошивкою | Перемкнутися на застарілий `REQUEST_DATA_STREAM` |
| 4 | `MAV_RESULT_FAILED` | Помилка виконання на борту | Повторити запит до 3 разів |
| 5 | `MAV_RESULT_IN_PROGRESS` | Виконується тривала операція | Очікувати наступний ACK з `progress=100` |

---

### 5. Транзакційний протокол місій (Mission Protocol)

Протокол місії забезпечує покрокову вичитку навігаційного плану з обов'язковим квитуванням кожної точки.

#### 5.1. Повідомлення `MISSION_REQUEST_LIST` (#43, CRC-EXTRA: 132)

:::tabs
```c
typedef struct __mavlink_mission_request_list_t {
    uint8_t target_system;    // SysID автопілота
    uint8_t target_component; // CompID автопілота
    uint8_t mission_type;     // Тип місії: 0=MAV_MISSION_TYPE_MISSION, 1=FENCE, 2=RALLY
} mavlink_mission_request_list_t;
```
```cpp
struct MavlinkMissionRequestList {
    uint8_t target_system{1};
    uint8_t target_component{1};
    uint8_t mission_type{0};
};
```
:::

#### 5.2. Повідомлення `MISSION_COUNT` (#44, CRC-EXTRA: 221)

:::tabs
```c
typedef struct __mavlink_mission_count_t {
    uint16_t count;           // Кількість шляхових точок у плані (N)
    uint8_t  target_system;    // SysID станції
    uint8_t  target_component; // CompID станції
    uint8_t  mission_type;     // 0 = MAV_MISSION_TYPE_MISSION
} mavlink_mission_count_t;
```
```cpp
struct MavlinkMissionCount {
    uint16_t count{0};
    uint8_t  target_system{0};
    uint8_t  target_component{0};
    uint8_t  mission_type{0};
};
```
:::

#### 5.3. Повідомлення `MISSION_REQUEST_INT` (#51, CRC-EXTRA: 196)

:::tabs
```c
typedef struct __mavlink_mission_request_int_t {
    uint16_t seq;             // Номер елемента (0 .. count-1)
    uint8_t  target_system;    // SysID автопілота
    uint8_t  target_component; // CompID автопілота
    uint8_t  mission_type;     // 0 = MAV_MISSION_TYPE_MISSION
} mavlink_mission_request_int_t;
```
```cpp
struct MavlinkMissionRequestInt {
    uint16_t seq{0};
    uint8_t  target_system{1};
    uint8_t  target_component{1};
    uint8_t  mission_type{0};
};
```
:::

#### 5.4. Повідомлення `MISSION_ITEM_INT` (#73, CRC-EXTRA: 38)

:::tabs
```c
typedef struct __mavlink_mission_item_int_t {
    float   param1;           // Параметр 1 команди (наприклад, час зависання у секундах)
    float   param2;           // Параметр 2 (радіус прийняття точки в метрах)
    float   param3;           // Параметр 3 (радіус проходження по спіралі або 0)
    float   param4;           // Параметр 4 (бажаний курс / Yaw у градусах)
    int32_t x;                // Широта (Latitude) * 1e7 (наприклад, 504501000 = 50.4501000° N)
    int32_t y;                // Довгота (Longitude) * 1e7 (наприклад, 305234000 = 30.5234000° E)
    float   z;                // Висота в метрах (AMSL або відносна над точкою зльоту)
    uint16_t seq;             // Порядковий номер точки (0 .. N-1)
    uint16_t command;         // MAV_CMD (16=NAV_WAYPOINT, 20=NAV_RETURN_TO_LAUNCH, 21=NAV_LAND, 22=NAV_TAKEOFF)
    uint8_t target_system;    // SysID станції
    uint8_t target_component; // CompID станції
    uint8_t frame;            // Система координат (MAV_FRAME: 0=GLOBAL, 3=GLOBAL_RELATIVE_ALT, 6=GLOBAL_TERRAIN_ALT)
    uint8_t current;          // 1 = поточна активна точка навігації, 0 = неактивна
    uint8_t autocontinue;     // 1 = автоматично переходити до наступної точки після досягнення
    uint8_t mission_type;     // 0 = MAV_MISSION_TYPE_MISSION
} mavlink_mission_item_int_t;
```
```cpp
struct MavlinkMissionItemInt {
    float   param1{0.0f};
    float   param2{0.0f};
    float   param3{0.0f};
    float   param4{0.0f};
    int32_t x{0};
    int32_t y{0};
    float   z{0.0f};
    uint16_t seq{0};
    uint16_t command{0};
    uint8_t target_system{0};
    uint8_t target_component{0};
    uint8_t frame{0};
    uint8_t current{0};
    uint8_t autocontinue{1};
    uint8_t mission_type{0};
};
```
:::

#### 5.5. Повідомлення `MISSION_ACK` (#47, CRC-EXTRA: 153)

:::tabs
```c
typedef struct __mavlink_mission_ack_t {
    uint8_t target_system;    // SysID автопілота
    uint8_t target_component; // CompID автопілота
    uint8_t type;             // Результат транзакції (enum MAV_MISSION_RESULT)
    uint8_t mission_type;     // 0 = MAV_MISSION_TYPE_MISSION
} mavlink_mission_ack_t;
```
```cpp
struct MavlinkMissionAck {
    uint8_t target_system{1};
    uint8_t target_component{1};
    uint8_t type{0};
    uint8_t mission_type{0};
};
```
:::

#### Коди підтвердження транзакції місії (`MAV_MISSION_RESULT`)

| Код | Константа | Опис |
| :--- | :--- | :--- |
| 0 | `MAV_MISSION_ACCEPTED` | **Успіх**: план перевірено й зафіксовано в пам'яті автопілота |
| 1 | `MAV_MISSION_ERROR` | Загальна невизначена помилка передачі |
| 2 | `MAV_MISSION_UNSUPPORTED_FRAME` | Непідтримувана система координат (`frame`) |
| 3 | `MAV_MISSION_UNSUPPORTED` | Непідтримувана навігаційна команда (`command`) |
| 4 | `MAV_MISSION_NO_SPACE` | Недостатньо пам'яті Flash/EEPROM для збереження точок |
| 5 | `MAV_MISSION_INVALID` | Помилка валідації параметрів точки |
| 6 | `MAV_MISSION_INVALID_PARAM1` .. `7` | Неприпустиме значення конкретного аргументу `paramN` |
| 13 | `MAV_MISSION_INVALID_SEQUENCE` | Порушено порядок індексів `seq` (виявлено пропуск або дубль) |
| 14 | `MAV_MISSION_DENIED` | Відхилено через активні блокування безпеки |
| 15 | `MAV_MISSION_OPERATION_CANCELLED`| Транзакцію скасовано за таймаутом |

---

### 6. Часові параметри та пороги таймаутів рукостискання

Під час виконання конвеєра рукостискання наземна станція повинна дотримуватися таких часових інтервалів:

* **`HEARTBEAT_TIMEOUT` (3500 мс)**: інтервал очікування чергового серцебиття від автопілота. Перевищення переводить станцію в аварійний стан `LINK_LOST`.
* **`PARAM_REQUEST_TIMEOUT` (1200 мс)**: час очікування відповіді на `PARAM_REQUEST_LIST`. Після цього запускається процедура аналізу бітової маски та точкового дозапиту.
* **`PARAM_READ_TIMEOUT` (800 мс)**: інтервал очікування відповіді на `PARAM_REQUEST_READ`. Якщо відповідь не надійшла, запит повторюється.
* **`STREAM_CMD_ACK_TIMEOUT` (600 мс)**: час очікування кадру `COMMAND_ACK` на команду `MAV_CMD_SET_MESSAGE_INTERVAL`. При відсутності відповіді лічильник `confirmation` збільшується на одиницю.
* **`MISSION_REQ_TIMEOUT` (1500 мс)**: максимальний час очікування чергової точки `MISSION_ITEM_INT` після надсилання `MISSION_REQUEST_INT`.
* **`MAX_RETRY_COUNT` (5 спроб)**: ліміт повторних спроб для будь-якої транзакції перед переведенням автомата в стан помилки `HandshakeState::Failed`.
