# ⚙️ Практичний парсер версій та аналізатор можливостей польотного контролера

Під час розробки наземних станцій керування, бортового програмного забезпечення для комп'ютерів-компаньйонів (англ. *companion computer*) або шлюзів телеметрії (MAVLink-to-ROS) однією з перших задач після встановлення зв'язку є визначення реальних можливостей підключеного апарата. Якщо станція почне транслювати шляхові точки у цілочисельному форматі `MISSION_ITEM_INT` чи запитувати файли журналів через MAVLink FTP до того, як переконається у їхній підтримці бортом, канал зв'язку зазнає збою.

Нижче наведено повну інженерну реалізацію модуля узгодження можливостей (англ. *Capability Negotiator*) мовами C та C++. Модуль автоматично ініціює запит `MAV_CMD_REQUEST_MESSAGE`, відстежує стан очікування з тайм-аутом, розбирає структуру `AUTOPILOT_VERSION (#148)`, розпаковує семантичні версії прошивки (SemVer), форматує апаратний ідентифікатор чіпа (UID2) та формує конфігураційну матрицю підсистем для адаптації протоколу.

---

### Архітектура кінцевого автомата узгодження

Процес узгодження будується як кінцевий автомат (англ. *Finite State Machine*, FSM) із чотирма основними станами:

```
[ IDLE ] ──(Отримано HEARTBEAT)──> [ REQUESTING ] ──(Відправлено запит)──> [ WAITING_RESPONSE ]
                                                                                   │
                      ┌────────────────────────────────────────────────────────────┴───────────────────────────┐
                      ▼ (Отримано AUTOPILOT_VERSION)                                                           ▼ (Тайм-аут 1000 мс, спроби > 3)
              [ NEGOTIATED ]                                                                           [ FALLBACK_DEGRADED ]
(Активація MISSION_INT, FTP, MAVLink2)                                                 (Активація MISSION_FLOAT, PARAM_FLOAT, MAVLink1)
```

1. **IDLE (Очікування):** Модуль перебуває у стані спокою, доки на лінку не з'явиться перший пакет `HEARTBEAT` від невідомого раніше ідентифікатора системи (`sysid`).
2. **REQUESTING (Формування запиту):** Модуль створює повідомлення `COMMAND_LONG` із командою `MAV_CMD_REQUEST_MESSAGE` (`#512`), передаючи `param1 = 148.0f` (`AUTOPILOT_VERSION`).
3. **WAITING_RESPONSE (Очікування відповіді):** Модуль запускає таймер на 1000 мс. Якщо відповідь не надходить протягом інтервалу, лічильник спроб нарощується, і запит надсилається повторно (до трьох спроб).
4. **NEGOTIATED (Успішне узгодження):** Отримано `AUTOPILOT_VERSION`. Виконується парсинг бітової маски, розпакування SemVer та активація розширених протоколів.
5. **FALLBACK_DEGRADED (Аварійна деградація):** Після трьох невдалих спроб модуль фіксує відсутність відповіді (характерно для застарілих або спрощених мікро-прошивок) і перемикає клієнтський стек у консервативний базовий режим: float-координати місій, класичні float-параметри та кадрування MAVLink v1.

---

### Інтеграція з потоковим розбірником MAVLink

У реальних вбудованих додатках модуль узгодження безпосередньо взаємодіє з потоковим розбірником (англ. *stream parser*), який вичитує байти з послідовного порту UART або UDP-сокета через кільцевий буфер.

Коли черговий байт надходить у функцію `mavlink_parse_char(chan, byte, &msg, &status)`, парсер перевіряє стартовий маркер (`0xFD` або `0xFE`), довжину корисного навантаження та контрольну суму `CRC_EXTRA`. Щойно повний кадр зібрано, диспетчер повідомлень викликає обробник автомата узгодження:

* Якщо отримано `HEARTBEAT (msg.msgid == 0)`, автомат перевіряє поле `sysid`. Якщо для цієї системи процедура узгодження ще не проводилася або була скинута, запускається метод `neg_start(&negotiator, current_time_ms)`.
* Якщо отримано `AUTOPILOT_VERSION (msg.msgid == 148)`, викликається функція декодування `mavlink_msg_autopilot_version_decode(&msg, &payload)` і передається у метод `neg_handle_version_msg`.

Ця схема гарантує повну ізоляцію логіки мережевого рівня від прикладного рівня керування польотом.

---

### Розподіл каналів MAVLink та протокол PROTOCOL_VERSION (#300)

У складних апаратних архітектурах польотний контролер обслуговує декілька фізичних інтерфейсів одночасно через логічні канали C-бібліотеки MAVLink (`MAVLINK_COMM_0` .. `MAVLINK_COMM_3`):
* `MAVLINK_COMM_0` — пряме USB-з'єднання з високою швидкістю та нульовою втратою пакетів;
* `MAVLINK_COMM_1` — радіомодем дальнього зв'язку (433/915 МГц, 57600 бод) з високою затримкою;
* `MAVLINK_COMM_2` — швидкісний порт комп'ютера-компаньйона (UART 921600 бод або Ethernet).

Важливо розрізняти два споріднених повідомлення узгодження:
1. `AUTOPILOT_VERSION (#148)` — описує **функціональні можливості автопілота** (місії, параметри, автономні контури, калібрування сенсорів, ревізію плати та UID чіпа).
2. `PROTOCOL_VERSION (#300)` — описує **характеристики самого протоколу передачі даних** (поточну версію `version = 200`, мінімальну підтримувану `min_version = 100`, максимальну `max_version = 200` та хеші схем XML `spec_version_hash` і `library_version_hash`).

Повнофункціональна станція керування виконує паралельний запит обох повідомлень: `PROTOCOL_VERSION` визначає правила перемикання парсерів на рівні байтів, а `AUTOPILOT_VERSION` конфігурує прикладні модулі користувацького інтерфейсу.

---

### Еволюційне розширення: COMPONENT_INFORMATION (#395) та метадані

У найновіших версіях екосистеми MAVLink поверх `AUTOPILOT_VERSION` розгорнуто протокол метаданих компонентів (повідомлення `COMPONENT_INFORMATION`, `#395`).

Якщо `AUTOPILOT_VERSION` відповідає на питання, *які базові протоколи підтримує ядро*, то `COMPONENT_INFORMATION` надає станції посилання (URI) та контрольну суму CRC32 на завантажувані JSON-файли метаданих. Ці файли містять:
* Повний опис усіх конфігураційних параметрів прошивки (включно з мінімальними, максимальними значеннями та переліком одиниць вимірювання SI);
* Опис доступних команд польоту та їхніх числових аргументів;
* Топологію приводів, моторів та сервоприводів (Actuator Configuration v2).

Наземна станція використовує тандем: спочатку через `AUTOPILOT_VERSION` вмикається швидкісний канал MAVLink FTP, а потім через FTP за лічені мілісекунди завантажуються скомпільовані стиснені JSON-метадані `COMPONENT_INFORMATION`.

---

### Динамічне налаштування потоків телеметрії для ROS / Companion Computer

Після успішного отримання маски `capabilities` комп'ютер-компаньйон (наприклад, вузол MAVROS або шлюз micro-XRCE-DDS) використовує інформацію про версію для вибору методу конфігурації потоків телеметрії:

1. **Сучасний метод (MAVLink 2.0 / SemVer >= v1.10):** Для кожного необхідного повідомлення (наприклад, `ATTITUDE`, `LOCAL_POSITION_NED`, `ODOMETRY`) бортовий комп'ютер надсилає індивідуальну команду `MAV_CMD_SET_MESSAGE_INTERVAL (#511)`. Ця команда приймає номер повідомлення та бажаний інтервал у мікросекундах (наприклад, `20000` мкс для частоти 50 Гц). Цей підхід забезпечує точне дозування пропускної здатності без перевантаження шини UART.
2. **Застарілий метод (Legacy Fallback):** Якщо прапорець `MAVLINK2` скинутий, а прошивка має версію нижче 1.10, комп'ютер переходить на групове керування потоками через повідомлення `REQUEST_DATA_STREAM (#66)`. Замість індивідуальних повідомлень активуються цілі групи потоків (`MAV_DATA_STREAM_EXTRA1`, `MAV_DATA_STREAM_POSITION`) на фіксованих частотах, хоча це створює надлишковий трафік.

---

### Керування підсистемами наземної станції на основі бітової маски

Отримання маски `capabilities` безпосередньо впливає на логіку ініціалізації внутрішніх компонентів програмного стека станції керування:

#### Підсистема 1: Протокол завантаження місій (Mission Engine)
Якщо прапорець `MAV_PROTOCOL_CAPABILITY_MISSION_INT` активний, рушій місій транслює шляхові точки у вигляді цілочисельних повідомлень `MISSION_ITEM_INT`. Це забезпечує сантиметрову точність координат та захищає від похибок округлення на екваторіальних широтах. Якщо прапорець скинутий, але встановлено `MAV_PROTOCOL_CAPABILITY_MISSION_FLOAT`, рушій активує застарілий формат `MISSION_ITEM`, автоматично конвертуючи координати у float32 з виведенням попередження оператору про знижену точність навігації.

#### Підсистема 2: Синхронізація параметрів (Parameter Manager)
Якщо встановлено біт `MAV_PROTOCOL_CAPABILITY_FTP`, менеджер параметрів ініціює завантаження кешованого файлу конфігурації через високошвидкісний протокол MAVLink FTP (повідомлення `FILE_TRANSFER_PROTOCOL`). Замість відправки сотень окремих запитів `PARAM_REQUEST_READ` станція отримує повний стиснений бінарний список параметрів за декілька пакетних транзакцій (заощаджуючи до 90% часу підключення). Якщо прапорець FTP скинутий, станція переходить до послідовного опитування через `PARAM_REQUEST_LIST`.

#### Підсистема 3: Автономні контури керування (Offboard Controller)
Наявність бітів `MAV_PROTOCOL_CAPABILITY_SET_POSITION_TARGET_LOCAL_NED` та `MAV_PROTOCOL_CAPABILITY_SET_ATTITUDE_TARGET` дає змогу зовнішнім модулям комп'ютерного зору (на базі ROS2 або OpenCV) транслювати локальні вектори швидкості та просторові кватерніони. Якщо автопілот не підтримує локальні цілі, станція блокує перехід у режим Offboard, захищаючи апарат від некерованого дрейфу.

#### Підсистема 4: Кадрування каналу зв'язку (Framing Layer)
Біт `MAV_PROTOCOL_CAPABILITY_MAVLINK2` служить сигналом для мережевого рівня: радіолінк перемикається зі стартового байта `0xFE` (v1) на `0xFD` (v2). Це вмикає підтримку 24-бітних ідентифікаторів повідомлень, нульового стискання пакетів та криптографічного підпису для запобігання атакам підміни телеметрії.

#### Підсистема 5: Обмін картами рельєфу (Terrain Protocol)
Прапорець `MAV_PROTOCOL_CAPABILITY_TERRAIN` активує сервер рельєфу на наземній станції. Якщо автопілот виконує політ із відстеженням рельєфу місцевості (англ. *terrain following*), він періодично надсилає запити `TERRAIN_REQUEST`, вказуючи координати сітки. Станція вичитує матрицю висот SRTM із локального накопичувача та відповідає пакетами `TERRAIN_DATA`. Якщо прапорець скинуто, GCS не витрачає обчислювальні ресурси на фонове обслуговування карт висот.

#### Підсистема 6: Статистика нальоту та ресурс батарей (Flight Information)
Якщо виявлено біт `MAV_PROTOCOL_CAPABILITY_FLIGHT_INFORMATION`, станція автоматично планує періодичний запит повідомлення `FLIGHT_INFORMATION (#264)`. Це дозволяє фіксувати час перебування у зведеному стані (англ. *arm time*), загальний час нальоту двигунів (англ. *total flight time*) та унікальний ідентифікатор польотного рейсу для ведення електронного журналу технічного обслуговування безпілотника.

---

### Матриця підтримки можливостей сучасними польотними контролерами

Нижче наведено порівняльну таблицю конфігурацій, які повертають різні покоління апаратних плат та прошивок:

| Платформа та прошивка | Маска capabilities (Hex) | Ключові активні можливості | Режим роботи GCS |
| :--- | :--- | :--- | :--- |
| **Pixhawk 6X (PX4 v1.14)** | `0x000000000000B0F7` | MISSION_INT, PARAM_UNION, FTP, MAVLink2, LocalNED, FlightInfo, CompassCal | Повний швидкісний режим (FTP-параметри, MAVLink v2) |
| **Cube Orange+ (ArduPilot 4.5)** | `0x000000000000B2F7` | MISSION_INT, PARAM_UNION, FTP, MAVLink2, Terrain, Fence, Rally, CompassCal | Повний функціонал із картами рельєфу та геозонами |
| **Matek H743 (iNav 7.1)** | `0x0000000000001005` | MISSION_INT, MAVLink2, базові команди | Базовий режим місій без розширеного FTP |
| **Застарілий APM 2.8 (ArduCopter 3.2)** | `0x0000000000000003` | MISSION_FLOAT, PARAM_FLOAT | Консервативний режим сумісності (float-координати, MAVLink v1) |

---

### Алгоритм розпакування полів

Розбір отриманого пакету складається з кількох послідовних кроків:

* **Розпакування SemVer:** 32-бітне число зсувається вправо на 24, 16 та 8 бітів для виділення полів Major, Minor та Patch. Молодший байт порівнюється з переліком `FIRMWARE_VERSION_TYPE` для встановлення суфікса (`-dev`, `-alpha`, `-beta`, `-rc`, `""` для стабільного релізу).
* **Форматування Git SHA:** Перші 8 байтів масиву `flight_custom_version` конвертуються у шістнадцятковий рядок (наприклад, `01a4f8c3`).
* **Форматування UID2:** Перший байт `uid2[0]` інтерпретується як довжина даних. Решта байтів форматуються у шістнадцяткове представлення з роздільниками-дефісами для відображення у графічному інтерфейсі станції.
* **Оцінка прапорців можливостей:** Бітова маска перевіряється набором побітових операцій `AND` із константами `MAV_PROTOCOL_CAPABILITY_*`.

---

### Покроковий розбір реального двійкового пакету

Для наочності розглянемо реальний приклад розбору шістнадцяткового згустку корисного навантаження `AUTOPILOT_VERSION`, отриманого від польотного контролера Pixhawk 6X із прошивкою PX4 v1.14.0-rc2:

```
[Байти 0..7]   Capabilities:  0x00000000000030E5 (MISSION_INT | PARAM_UNION | FTP | POS_NED | ATT_TARGET | MAVLINK2 | FENCE)
[Байти 8..15]  Legacy UID:    0x001B002434385112
[Байти 16..19] Flight SW:     0x010E00C0 -> Major=1, Minor=14, Patch=0, Type=192 (RC)
[Байти 20..23] Middleware SW: 0x010E00C0
[Байти 24..27] OS SW:         0x0A0200FF -> NuttX v10.2.0 Official Release
[Байти 28..31] Board Version: 0x00000006 -> FMUv6X
[Байти 32..39] Git Custom:    61 8f 4c d2 00 00 00 00 -> Commit SHA 618f4cd2
[Байти 56..57] Vendor ID:     0x26AC (Dronecode / 3DR)
[Байти 58..59] Product ID:    0x0011 (Pixhawk 6X)
[Байти 60..77] UID2:          10 00 32 00 12 51 38 34 34 24 00 1B ... (128-бітний UUID чіпа STM32H7)
```

Розбір маски `0x30E5`:
* `0x0001` (MISSION_FLOAT): підтримується
* `0x0004` (MISSION_INT): підтримується (GCS обирає int32 місії)
* `0x0020` (FTP): підтримується (GCS завантажує параметри через FTP)
* `0x0040` (SET_ATTITUDE_TARGET): підтримується (Offboard орієнтація активна)
* `0x0080` (SET_POSITION_TARGET_LOCAL_NED): підтримується (Offboard швидкість активна)
* `0x1000` (MAVLINK2): підтримується (лінк перемикається на MAVLink v2)
* `0x2000` (MISSION_FENCE): підтримується (увімкнено інтерфейс геозон)

---

### Робоча реалізація на мовах C та C++

У прикладі нижче реалізовано повний цикл: створення запиту, оновлення таймера, обробку вхідного пакету та налаштування конфігурації.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define MAV_CMD_REQUEST_MESSAGE 512
#define MSG_ID_AUTOPILOT_VERSION 148

#define CAP_MISSION_FLOAT  (1ULL << 0)
#define CAP_PARAM_FLOAT    (1ULL << 1)
#define CAP_MISSION_INT    (1ULL << 2)
#define CAP_COMMAND_INT    (1ULL << 3)
#define CAP_PARAM_UNION    (1ULL << 4)
#define CAP_FTP            (1ULL << 5)
#define CAP_SET_ATT_TARGET (1ULL << 6)
#define CAP_SET_POS_NED    (1ULL << 7)
#define CAP_TERRAIN        (1ULL << 9)
#define CAP_COMPASS_CAL    (1ULL << 11)
#define CAP_MAVLINK2       (1ULL << 12)
#define CAP_FLIGHT_INFO    (1ULL << 15)

typedef enum {
    NEG_STATE_IDLE,
    NEG_STATE_REQUESTING,
    NEG_STATE_WAITING,
    NEG_STATE_NEGOTIATED,
    NEG_STATE_FALLBACK
} neg_state_t;

typedef struct {
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
    uint8_t release_type;
    char    version_str[32];
    char    git_hash_str[17];
    char    uid2_str[48];
    bool    supports_mission_int;
    bool    supports_ftp;
    bool    supports_param_union;
    bool    supports_mavlink2;
    bool    supports_offboard_ned;
    bool    supports_terrain;
    bool    supports_flight_info;
} vehicle_caps_t;

typedef struct {
    neg_state_t    state;
    uint8_t        target_sysid;
    uint8_t        target_compid;
    uint32_t       last_request_time_ms;
    uint8_t        retry_count;
    vehicle_caps_t caps;
} capability_negotiator_t;

// Ініціалізація автомата
void neg_init(capability_negotiator_t* neg, uint8_t sysid, uint8_t compid) {
    neg->state = NEG_STATE_IDLE;
    neg->target_sysid = sysid;
    neg->target_compid = compid;
    neg->last_request_time_ms = 0;
    neg->retry_count = 0;
    memset(&neg->caps, 0, sizeof(vehicle_caps_t));
}

// Запуск процедури після отримання HEARTBEAT
void neg_start(capability_negotiator_t* neg, uint32_t now_ms) {
    neg->state = NEG_STATE_REQUESTING;
    neg->retry_count = 0;
    neg->last_request_time_ms = now_ms;
}

// Періодичний крок оновлення (тайм-аути та повторні спроби)
void neg_update(capability_negotiator_t* neg, uint32_t now_ms) {
    if (neg->state == NEG_STATE_REQUESTING) {
        // Симуляція відправки COMMAND_LONG (MAV_CMD_REQUEST_MESSAGE, param1=148)
        printf("[C-Negotiator] Надсилання MAV_CMD_REQUEST_MESSAGE(#512) для AUTOPILOT_VERSION (спроба %d)\n",
               neg->retry_count + 1);
        neg->last_request_time_ms = now_ms;
        neg->state = NEG_STATE_WAITING;
    } else if (neg->state == NEG_STATE_WAITING) {
        if (now_ms - neg->last_request_time_ms > 1000) { // 1 секунда тайм-аут
            neg->retry_count++;
            if (neg->retry_count >= 3) {
                printf("[C-Negotiator] Тайм-аут відповіді вичерпано. Перехід у FALLBACK_DEGRADED.\n");
                neg->state = NEG_STATE_FALLBACK;
                // Налаштування базової консервативної сумісності
                neg->caps.supports_mission_int = false;
                neg->caps.supports_ftp = false;
                neg->caps.supports_mavlink2 = false;
                neg->caps.supports_terrain = false;
                neg->caps.supports_flight_info = false;
            } else {
                neg->state = NEG_STATE_REQUESTING;
            }
        }
    }
}

// Обробка отриманого пакета AUTOPILOT_VERSION
void neg_handle_version_msg(capability_negotiator_t* neg,
                            uint64_t capabilities,
                            uint32_t flight_sw_version,
                            const uint8_t flight_custom_version[8],
                            const uint8_t uid2[18]) {
    if (neg->state != NEG_STATE_WAITING && neg->state != NEG_STATE_REQUESTING) {
        return;
    }

    vehicle_caps_t* c = &neg->caps;

    // 1. Розпакування SemVer
    c->major        = (uint8_t)((flight_sw_version >> 24) & 0xFF);
    c->minor        = (uint8_t)((flight_sw_version >> 16) & 0xFF);
    c->patch        = (uint8_t)((flight_sw_version >> 8)  & 0xFF);
    c->release_type = (uint8_t)(flight_sw_version & 0xFF);

    const char* type_suffix = "";
    if (c->release_type == 0)        type_suffix = "-dev";
    else if (c->release_type == 64)  type_suffix = "-alpha";
    else if (c->release_type == 128) type_suffix = "-beta";
    else if (c->release_type == 192) type_suffix = "-rc";

    snprintf(c->version_str, sizeof(c->version_str), "v%u.%u.%u%s",
             c->major, c->minor, c->patch, type_suffix);

    // 2. Форматування Git хешу
    for (int i = 0; i < 8; ++i) {
        snprintf(&c->git_hash_str[i * 2], 3, "%02x", flight_custom_version[i]);
    }

    // 3. Форматування UID2
    int offset = 0;
    for (int i = 0; i < 18 && offset < (int)sizeof(c->uid2_str) - 3; ++i) {
        offset += snprintf(&c->uid2_str[offset], sizeof(c->uid2_str) - offset,
                           (i == 0) ? "%02X" : "-%02X", uid2[i]);
    }

    // 4. Оцінка бітової маски
    c->supports_mission_int   = (capabilities & CAP_MISSION_INT) != 0;
    c->supports_ftp           = (capabilities & CAP_FTP) != 0;
    c->supports_param_union   = (capabilities & CAP_PARAM_UNION) != 0;
    c->supports_mavlink2      = (capabilities & CAP_MAVLINK2) != 0;
    c->supports_offboard_ned  = (capabilities & CAP_SET_POS_NED) != 0;
    c->supports_terrain       = (capabilities & CAP_TERRAIN) != 0;
    c->supports_flight_info   = (capabilities & CAP_FLIGHT_INFO) != 0;

    neg->state = NEG_STATE_NEGOTIATED;

    printf("[C-Negotiator] Узгодження успішне!\n");
    printf("  Прошивка: %s (Git SHA: %s)\n", c->version_str, c->git_hash_str);
    printf("  UID2: %s\n", c->uid2_str);
    printf("  Підтримка: MISSION_INT=%d, FTP=%d, MAVLink2=%d, Terrain=%d, FlightInfo=%d\n",
           c->supports_mission_int, c->supports_ftp,
           c->supports_mavlink2, c->supports_terrain, c->supports_flight_info);
}
```
```cpp
#include <cstdint>
#include <string>
#include <string_view>
#include <array>
#include <format>
#include <chrono>
#include <iostream>
#include <span>
#include <optional>

enum class ReleaseType : uint8_t {
    Dev      = 0,
    Alpha    = 64,
    Beta     = 128,
    Rc       = 192,
    Official = 255
};

enum class NegotiatorState {
    Idle,
    Requesting,
    WaitingResponse,
    Negotiated,
    FallbackDegraded
};

struct VehicleCapabilities {
    uint8_t major{0};
    uint8_t minor{0};
    uint8_t patch{0};
    ReleaseType release_type{ReleaseType::Dev};
    std::string version_string;
    std::string git_hash;
    std::string uid2_formatted;

    bool supports_mission_int{false};
    bool supports_ftp{false};
    bool supports_param_union{false};
    bool supports_mavlink2{false};
    bool supports_offboard_ned{false};
    bool supports_compass_calibration{false};
    bool supports_terrain{false};
    bool supports_flight_info{false};
};

class CapabilityNegotiator {
public:
    static constexpr uint64_t CAP_MISSION_INT = (1ULL << 2);
    static constexpr uint64_t CAP_PARAM_UNION = (1ULL << 4);
    static constexpr uint64_t CAP_FTP         = (1ULL << 5);
    static constexpr uint64_t CAP_SET_POS_NED = (1ULL << 7);
    static constexpr uint64_t CAP_TERRAIN     = (1ULL << 9);
    static constexpr uint64_t CAP_COMPASS_CAL = (1ULL << 11);
    static constexpr uint64_t CAP_MAVLINK2    = (1ULL << 12);
    static constexpr uint64_t CAP_FLIGHT_INFO = (1ULL << 15);

    CapabilityNegotiator(uint8_t sysid, uint8_t compid)
        : target_sysid_(sysid), target_compid_(compid) {}

    void on_heartbeat_detected(std::chrono::steady_clock::time_point now) {
        if (state_ == NegotiatorState::Idle) {
            state_ = NegotiatorState::Requesting;
            retry_count_ = 0;
            last_request_time_ = now;
        }
    }

    void update(std::chrono::steady_clock::time_point now) {
        using namespace std::chrono_literals;

        if (state_ == NegotiatorState::Requesting) {
            std::cout << std::format("[CPP-Negotiator] Відправка MAV_CMD_REQUEST_MESSAGE(148) до sysid={} compid={} (спроба {})\n",
                                     target_sysid_, target_compid_, retry_count_ + 1);
            last_request_time_ = now;
            state_ = NegotiatorState::WaitingResponse;
        } else if (state_ == NegotiatorState::WaitingResponse) {
            if (now - last_request_time_ > 1000ms) {
                retry_count_++;
                if (retry_count_ >= 3) {
                    std::cout << "[CPP-Negotiator] Досягнуто ліміт спроб. Перехід у FallbackDegraded.\n";
                    state_ = NegotiatorState::FallbackDegraded;
                    caps_ = VehicleCapabilities{}; // Базові нульові можливості
                } else {
                    state_ = NegotiatorState::Requesting;
                }
            }
        }
    }

    void handle_autopilot_version(uint64_t capabilities,
                                  uint32_t flight_sw_version,
                                  std::span<const uint8_t, 8> custom_version,
                                  std::span<const uint8_t, 18> uid2_bytes) {
        if (state_ != NegotiatorState::WaitingResponse && state_ != NegotiatorState::Requesting) {
            return;
        }

        VehicleCapabilities c;
        c.major = static_cast<uint8_t>((flight_sw_version >> 24) & 0xFF);
        c.minor = static_cast<uint8_t>((flight_sw_version >> 16) & 0xFF);
        c.patch = static_cast<uint8_t>((flight_sw_version >> 8) & 0xFF);
        c.release_type = static_cast<ReleaseType>(flight_sw_version & 0xFF);

        std::string_view suffix;
        switch (c.release_type) {
            case ReleaseType::Dev:      suffix = "-dev"; break;
            case ReleaseType::Alpha:    suffix = "-alpha"; break;
            case ReleaseType::Beta:     suffix = "-beta"; break;
            case ReleaseType::Rc:       suffix = "-rc"; break;
            case ReleaseType::Official: suffix = ""; break;
        }
        c.version_string = std::format("v{}.{}.{}{}", c.major, c.minor, c.patch, suffix);

        // Форматування Git SHA
        for (uint8_t b : custom_version) {
            c.git_hash += std::format("{:02x}", b);
        }

        // Форматування UID2
        for (size_t i = 0; i < uid2_bytes.size(); ++i) {
            c.uid2_formatted += std::format("{:02X}", uid2_bytes[i]);
            if (i + 1 < uid2_bytes.size()) c.uid2_formatted += '-';
        }

        // Бітова маска
        c.supports_mission_int        = (capabilities & CAP_MISSION_INT) != 0;
        c.supports_ftp                = (capabilities & CAP_FTP) != 0;
        c.supports_param_union        = (capabilities & CAP_PARAM_UNION) != 0;
        c.supports_mavlink2           = (capabilities & CAP_MAVLINK2) != 0;
        c.supports_offboard_ned       = (capabilities & CAP_SET_POS_NED) != 0;
        c.supports_compass_calibration = (capabilities & CAP_COMPASS_CAL) != 0;
        c.supports_terrain            = (capabilities & CAP_TERRAIN) != 0;
        c.supports_flight_info        = (capabilities & CAP_FLIGHT_INFO) != 0;

        caps_ = std::move(c);
        state_ = NegotiatorState::Negotiated;

        std::cout << std::format("[CPP-Negotiator] Узгодження успішне!\n"
                                 "  Версія: {} (Git: {})\n"
                                 "  UID2: {}\n"
                                 "  MISSION_INT: {}, FTP: {}, MAVLink2: {}, Terrain: {}, FlightInfo: {}\n",
                                 caps_->version_string, caps_->git_hash,
                                 caps_->uid2_formatted, caps_->supports_mission_int,
                                 caps_->supports_ftp, caps_->supports_mavlink2,
                                 caps_->supports_terrain, caps_->supports_flight_info);
    }

    [[nodiscard]] NegotiatorState state() const noexcept { return state_; }
    [[nodiscard]] const std::optional<VehicleCapabilities>& capabilities() const noexcept { return caps_; }

private:
    NegotiatorState state_{NegotiatorState::Idle};
    uint8_t target_sysid_{1};
    uint8_t target_compid_{1};
    uint8_t retry_count_{0};
    std::chrono::steady_clock::time_point last_request_time_{};
    std::optional<VehicleCapabilities> caps_{std::nullopt};
};
```
:::

---

### Детермінізм пам'яті та нульові динамічні виділення

У вбудованих системах керування реального часу (RTOS, наприклад NuttX, FreeRTOS або ChibiOS) критично важливо уникати динамічного виділення пам'яті (`malloc`/`new`) у циклі обробки пакетів телеметрії. Динамічний розподіл пам'яті призводить до фрагментації купи та недетермінованих затримок планувальника задач.

У наведеній реалізації мовою C структура `capability_negotiator_t` має фіксований розмір пам'яті (усі рядкові буфери виділені статично як масиви символів `char[32]`, `char[48]`). Це дає змогу розміщувати екземпляр автомата безпосередньо у статичній секції BSS або у стеку задач прийому телеметрії без ризику вичерпання системної пам'яті.

У версії C++ клас `CapabilityNegotiator` використовує `std::span` для нульового копіювання байтових зрізів сирого пакету та обгортку `std::optional` для безпечного доступу до результатів узгодження без застосування сирих вказівників.

---

### Робота в багатоапаратних мережах (Swarm / Multi-Vehicle Routing)

Коли на спільній радіочастоті працює група або рій дронів, кожен апарат має свій унікальний номер системи `sysid` (від `1` до `254`), але всі вони транслюють пакети `HEARTBEAT` у спільний радіоефір.

Для коректної роботи в такій мережі наземна станція повинна дотримуватися таких правил:

1. **Індивідуальні екземпляри автомата:** Станція створює асоціативний масив автоматів узгодження (наприклад, `std::unordered_map<uint8_t, CapabilityNegotiator>`), де ключем є номер системи `sysid`. Кожен дрон проходить власне незалежне рукостискання.
2. **Адресний запит замість широкомовного:** Команда `MAV_CMD_REQUEST_MESSAGE` надсилається з полем `target_system = sysid` та `param7 = 1.0f` (адресна відповідь). Це запобігає ситуації, коли широкомовний запит змушує всі десять дронів у рої одночасно надіслати 78-байтні пакети `AUTOPILOT_VERSION`, викликаючи колапс та колізію радіоканалу (англ. *channel packet collision*).
3. **Ізоляція конфігураційних баз:** Отриманий `uid2` прив'язується до конкретного `sysid` у таблиці маршрутизації станції. Якщо під час польоту зв'язок із дроном переривається, а потім з'являється новий дрон з тим самим `sysid` (наприклад, при випадковому дублюванні налаштувань перед стартом), станція виявляє невідповідність `uid2` і негайно сигналізує оператору про конфлікт адрес на лінії зв'язку.

---

### Відмовостійкість, динамічне перепідключення та перезавантаження

У реальних польотних умовах наземна станція повинна коректно реагувати на нештатні події в каналі зв'язку:

1. **Гаряче перезавантаження автопілота (Reboot in-flight / on-ground):** Якщо автопілот перезавантажується після калібрування сенсорів чи оновлення параметрів, лічильник послідовності пакетів `SEQ` скидається в `0`, а в пакеті `HEARTBEAT` тимчасово виставляється стан `MAV_STATE_BOOT`. Отримавши сигнал перезавантаження, автомат узгодження переходить зі стану `NEGOTIATED` назад у `IDLE` та повторює повний цикл опитування `AUTOPILOT_VERSION`. Це гарантує, що якщо користувач змінив конфігурацію прошивки під час перезавантаження (наприклад, увімкнув MAVLink FTP або вимкнув геозони), станція негайно оновить внутрішні прапорці.
2. **Фільтрація компонентів за Component ID:** Запит версії повинен надсилатися виключно основному польотному контролеру (`MAV_COMP_ID_AUTOPILOT1` = `1`). Якщо на спільній радіолінії присутні інші розумні пристрої (підвіс камери `MAV_COMP_ID_GIMBAL`, бортовий комп'ютер `MAV_COMP_ID_ONBOARD_COMPUTER`), вони генерують власні пакети `HEARTBEAT`. Автомат узгодження створює окремі ізольовані екземпляри стану для кожної пари `(sysid, compid)`, запобігаючи спотворенню характеристик автопілота даними від периферійних модулів.
3. **Евристика для спрощених пристроїв:** Якщо пристрій не відповідає на `MAV_CMD_REQUEST_MESSAGE` протягом 3 спроб, станція не обриває з'єднання, а переходить у режим `FALLBACK_DEGRADED`. У цьому режимі вимикаються всі експериментальні розширення, що дозволяє оператору отримувати базову телеметрію положення навіть від саморобних мінімалістичних трекерів або старих радіомаяків.
4. **Багатопоточність та захист критичних секцій:** У багатопотокових архітектурах станцій (де приймання пакетів із COM-порту виконується у фоновому потоці введення-виведення, а оновлення інтерфейсу — в основному графічному циклі UI) звернення до структури `VehicleCapabilities` має бути захищене м'ютексом або реалізоване через атомарне копіювання розумного вказівника (`std::shared_ptr` із `std::atomic_store`), щоб уникнути стану гонитви (англ. *race condition*) під час оновлення прапорців посеред відмальовки карти.

---

### Тестування модуля в середовищі програмної симуляції (SITL)

Для верифікації роботи модуля узгодження перед польотними випробуваннями використовується симулятор Software-in-the-Loop (SITL) на базі PX4 або ArduPilot:

1. **Запуск емулятора:** Польотний стек запускається у середовищі Linux командою `make px4_sitl none_iris` або `sim_vehicle.py -v ArduCopter`. Автопілот створює віртуальний UDP-сервер на порту `14550`.
2. **Перевірка стандартного рукостискання:** Наш модуль підключається до UDP-сокету, надсилає `MAV_CMD_REQUEST_MESSAGE(#512)` і виводить у консоль розпаковані поля: версію прошивки (наприклад `v1.14.0-dev`), назву операційної системи NuttX або Linux, та повну маску `capabilities`.
3. **Тестування відмови (Chaos Testing):** За допомогою проксі-скрипта (наприклад `mavproxy.py` із фільтром втрати пакетів) симулюється 100% втрата повідомлень з `ID 148`. Спостерігається перехід автомата у стан `FALLBACK_DEGRADED` рівно через 3000 мс після трьох спроб, підтверджуючи стабільність логіки аварійної деградації без падіння програми.
4. **Імітація застарілого контролера:** У тестовому скрипті на Python (через бібліотеку pymavlink) емулюється автовідповідач, який повертає маску `capabilities = 0x0003` (`MISSION_FLOAT | PARAM_FLOAT`). Перевіряється, що модуль узгодження успішно перемикається у стан `NEGOTIATED`, але блокує виклики FTP та цілочисельних місій, надійно захищаючи систему від несумісних транзакцій.
