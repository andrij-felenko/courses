# 📋 Бінарний контракт телеметрії та розподіл даних

Цей документ визначає повну специфікацію бінарного інтерфейсу передачі даних між автономним сенсорним вузлом, польовим шлюзом, брокером повідомлень та аналітичним сховищем. Жорсткий контракт усуває невизначеність щодо порядку байтів, вирівнювання структур у пам'яті, квантування вимірювань та механізмів дедуплікації в умовах ненадійного радіозв'язку.

## Чому бінарний формат: ціна текстових протоколів у радіоефірі

У бездротових мережах із низькою пропускною здатністю (LPWAN: LoRaWAN, NB-IoT) кожен переданий байт безпосередньо конвертується у міліампер-години заряду батареї та час зайнятості радіоефіру (Time-on-Air). Використання текстових форматів самоописуваних даних (JSON, XML) на ділянці «вузол — шлюз» є неприпустимим через надлишковість синтаксису: назви ключів, лапки, коми та форматування чисел у ASCII збільшують обсяг корисного навантаження у 5–10 разів.

Порівняємо передачу трьох фізичних величин (температура, вологість, напруга батареї) разом із метаданими ідентифікатора та часу:
- Еквівалентний JSON-рядок займає близько 130–160 байтів. При швидкості передачі LoRa на коефіцієнті розширення SF10 (Data Rate 980 біт/с) час передачі такого пакета становить понад 1400 мс, споживаючи близько 40 мА·с заряду.
- Оптимізований упакований бінарний кадр фіксованої довжини займає рівно 24 байти. Час його передачі скорочується до 320 мс, а витрати енергії зменшуються у 4.5 рази.

Крім того, мікроконтролери початкового рівня на базі ядер ARM Cortex-M0+ часто не мають апаратного блоку обчислень із плаваючою комою (FPU). Програмна емуляція операцій `float` і форматування рядків `sprintf` вимагають тисяч тактів процесора та збільшують розмір коду прошивки. Використання цілих чисел із фіксованою комою (fixed-point arithmetic) дозволяє виконувати всі операції в цілочисельних регістрах за одиниці мікросекунд.

---

## Специфікація польового кадру (Uplink: Node → Gateway)

Кадр має фіксовану довжину **24 байти**. Всі багатобайтові цілі числа передаються в порядку **Little-Endian** (найменш значущий байт розташовується за молодшою адресою пам'яті). Це відповідає нативному порядку байтів більшості сучасних мікроконтролерів (ARM Cortex-M, RISC-V, ESP32) і виключає необхідність побайтового розвертання на стороні передавача.

### Побайтна структура кадру

| Зсув (байти) | Поле | Тип | Опис, одиниці вимірювання та діапазон |
|---|---|---|---|
| `0x00..0x01` | `magic` | `uint16_t` | Фіксована преамбула протоколу (`0xA55A`). Використовується для швидкого відсікання випадкового сміття в ефірі |
| `0x02` | `version` | `uint8_t` | Версія бінарної схеми (`0x01`). Дозволяє шлюзу підтримувати парк пристроїв різних поколінь |
| `0x03` | `flags` | `uint8_t` | Бітова маска апаратного стану вузла, тривог та режимів вивантаження |
| `0x04..0x07` | `node_id` | `uint32_t` | Унікальний 32-бітний числовий ідентифікатор пристрою (або молодші 4 байти апаратного DevEUI) |
| `0x08..0x0B` | `seq_num` | `uint32_t` | Монотонно зростаючий лічильник кадрів. Використовується для дедуплікації та розрахунку втрат пакетів |
| `0x0C..0x0F` | `timestamp` | `uint32_t` | Час вимірювання на бортовому годиннику RTC (Unix Epoch у секундах, UTC) |
| `0x10..0x11` | `temperature` | `int16_t` | Температура у сотих долях градуса Цельсія: діапазон від -327.68 °C до +327.67 °C, крок 0.01 °C |
| `0x12..0x13` | `humidity` | `uint16_t` | Відносна вологість у сотих долях відсотка: діапазон від 0.00% до 100.00% (`0..10000`), крок 0.01% |
| `0x14..0x15` | `battery_mv` | `uint16_t` | Напруга живлення батареї у мілівольтах: діапазон від 0 до 65535 мВ (для 3.6 В батареї значення `3600`) |
| `0x16..0x17` | `crc16` | `uint16_t` | Контрольна сума CRC16-CCITT (поліном `0x1021`, початкове значення `0xFFFF`) за байтами `0x00..0x15` |

### Призначення бітових прапорців стану (`flags`)

Поле прапорців агрегує технічний стан вузла без необхідності введення додаткових байтів у кадр:
- **Bit 0 (`0x01`) — `FLAG_LOW_BATTERY`**: Встановлюється, якщо напруга батареї під час передачі впала нижче 3.0 В (попередження про наближення кінця ресурсу хімічного джерела Li-SOCl2).
- **Bit 1 (`0x02`) — `FLAG_SENSOR_FAULT`**: Встановлюється при відмові інтерфейсу давача (таймаут I2C, обрив аналогової лінії або значення поза фізичними межами). При цьому поля вимірювань заповнюються сигнальним значенням `0x7FFF`.
- **Bit 2 (`0x04`) — `FLAG_TAMPER`**: Фіксує спрацювання датчика розкриття корпусу (геркон або тамперна кнопка) для захисту від фізичного втручання.
- **Bit 3 (`0x08`) — `FLAG_STORED_OFFLINE`**: Індикатор походження кадру. Якщо прапорець встановлений, кадр піднято з локального кільцевого Flash-буфера після відновлення зв'язку, а не згенеровано щойно.
- **Bit 4..7**: Зарезервовано під майбутні розширення (повинні передаватися як `0`).

---

## Вирівнювання структури та пакування в пам'яті

При оголошенні структур мовами C та C++ компілятор за замовчуванням вирівнює поля за межами слів (4 байти на 32-бітних архітектурах). Це може призвести до додавання невидимих байтів заповнення (padding bytes) між полями `version`, `flags` та `node_id`, що спотворить передачу даних через радіоканал.

Для запобігання цьому застосовується атрибут упакованої структури:
- У мові C: `__attribute__((packed))` або директива `#pragma pack(push, 1)`.
- У мові C++: безпечне побайтове читання через `std::span` та явні зсуви або десеріалізація без порушення правил суворого псевдонімування (Strict Aliasing Rule). Пряме приведення вказівників типу `(telemetry_frame_raw_t*)buf` на архітектурах ARM Cortex-M0 може викликати апаратний виняток `UsageFault` при непарному вирівнюванні адреси в буфері.

---

## Контроль цілісності: чому CRC16-CCITT, а не звичайна сума

У зашумленому радіоканалі прості суми (наприклад, XOR або сума за модулем 256) пропускають значну частину помилок: перестановка двох байтів місцями або симетрична зміна двох бітів дає абсолютно однакову контрольну суму.

Алгоритм **CRC16-CCITT** із генераторним поліномом `x¹⁶ + x¹² + x⁵ + 1` (`0x1021`) математично гарантує:
1. 100% виявлення всіх одиничних, подвійних і непарних бітових помилок у межах кадру довжиною до 2048 бітів.
2. 100% виявлення пакетних помилок (burst errors) довжиною до 16 бітів (що типово для імпульсних завад в ефірі).
3. 99.997% ймовірність виявлення будь-яких довільних спотворень більшої довжини.

Це забезпечує надійне відсікання пошкоджених пакетів на рівні апаратного драйвера шлюзу ще до того, як вони навантажать шину чи будуть передані в хмару.

---

## Контракт обміну через брокер (Gateway → Broker)

Шлюз приймає радіокадр, перевіряє контрольну суму, доповнює пакет метриками радіоефіру та публікує його у брокер MQTT.

### Ієрархія та простір тем MQTT

Топіки структуруються за принципом «служба / версія / локація / вузол / тип повідомлення»:
```
telemetry/v1/{site_id}/{node_id}/state
```
- `telemetry` — функціональний домен системи.
- `v1` — версія протоколу обміну.
- `{site_id}` — ідентифікатор географічної локації або підприємства (наприклад, `field-alpha-04`).
- `{node_id}` — десятковий або шістнадцятковий номер вузла (наприклад, `node-1048577`).
- `state` — тип повідомлення (телеметрія стану).

### Формат JSON-повідомлення у брокері

```json
{
  "version": 1,
  "node_id": 1048577,
  "seq": 4821,
  "ts": 1724745600,
  "metrics": {
    "temperature_c": 21.45,
    "humidity_pct": 65.20,
    "battery_v": 3.615
  },
  "status": {
    "low_battery": false,
    "sensor_fault": false,
    "tamper": false,
    "offline_sync": false
  },
  "radio": {
    "rssi_dbm": -84,
    "snr_db": 9.5,
    "gateway_id": "gw-agro-sector-04"
  }
}
```

---

## Контракт зворотного керування (Downlink: Service → Gateway → Node)

Для налаштування параметрів вузла (зміна періоду опитування, перезавантаження, оновлення порогів алерту) служба формує команду зворотного зв'язку.

### Структура кадру команди (Downlink Frame, 8 байтів)

| Зсув | Поле | Тип | Опис |
|---|---|---|---|
| `0x00..0x01` | `cmd_magic` | `uint16_t` | Сигнатура команди (`0x55AA`) |
| `0x02` | `cmd_id` | `uint8_t` | Тип команди (1 — зміна періоду, 2 — калібрування, 3 — скидання) |
| `0x03` | `nonce` | `uint8_t` | Одноразовий номер для захисту від повторних атак (Replay Attack) |
| `0x04..0x05` | `param_val` | `uint16_t` | Значення параметра (наприклад, новий період сну в секундах) |
| `0x06..0x07` | `crc16` | `uint16_t` | Контрольна сума CRC16 кадру команди |

Оскільки автономний вузол більшу частину часу спить, команда не може бути доставлена миттєво. Вона буферизується на сервері або шлюзі і відправляється в ефір строго під час короткого вікна прийому (RX window) відразу після чергового виходу вузла на зв'язок.

---

## Політика лічильника кадрів та дедуплікація

Поле `seq_num` є 32-бітним беззнаковим числом. При інтервалі відправки 1 раз на 10 хвилин лічильник переповниться лише через `2³² · 10 хв ≈ 81700 років`, тому переповненням лічильника в рамках життєвого циклу пристрою можна знехтувати.

Серверна служба реалізує алгоритм ковзного вікна (Sliding Window):
- Зберігається останній підтверджений номер `last_seq` для кожного `node_id`.
- Якщо надходить пакет із `seq_num <= last_seq`, перевіряється прапорець `FLAG_STORED_OFFLINE`. Якщо прапорець встановлений, пакет приймається як історичний архів. Якщо ні — пакет вважається дублікатом від повторної спроби передачі й ігнорується.
- Втрати пакетів оцінюються як розриви між послідовними значеннями `seq_num`.

---

## Програмний парсер бінарного кадру

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEMETRY_MAGIC 0xA55A
#define TELEMETRY_VERSION 1
#define TELEMETRY_FRAME_SIZE 24

typedef struct __attribute__((packed)) {
    uint16_t magic;
    uint8_t version;
    uint8_t flags;
    uint32_t node_id;
    uint32_t seq_num;
    uint32_t timestamp;
    int16_t temperature;
    uint16_t humidity;
    uint16_t battery_mv;
    uint16_t crc16;
} telemetry_frame_raw_t;

typedef struct {
    uint32_t node_id;
    uint32_t seq_num;
    uint32_t timestamp;
    float temperature_c;
    float humidity_pct;
    float battery_v;
    bool low_battery;
    bool sensor_fault;
    bool tamper;
    bool offline_sync;
} telemetry_parsed_t;

static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; ++j) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

bool telemetry_parse(const uint8_t *buf, size_t len, telemetry_parsed_t *out) {
    if (!buf || len < TELEMETRY_FRAME_SIZE || !out) {
        return false;
    }

    const telemetry_frame_raw_t *raw = (const telemetry_frame_raw_t *)buf;

    if (raw->magic != TELEMETRY_MAGIC || raw->version != TELEMETRY_VERSION) {
        return false;
    }

    uint16_t expected_crc = crc16_ccitt(buf, TELEMETRY_FRAME_SIZE - 2);
    if (raw->crc16 != expected_crc) {
        return false;
    }

    out->node_id = raw->node_id;
    out->seq_num = raw->seq_num;
    out->timestamp = raw->timestamp;
    out->temperature_c = (float)raw->temperature / 100.0f;
    out->humidity_pct = (float)raw->humidity / 100.0f;
    out->battery_v = (float)raw->battery_mv / 1000.0f;

    out->low_battery = (raw->flags & (1 << 0)) != 0;
    out->sensor_fault = (raw->flags & (1 << 1)) != 0;
    out->tamper = (raw->flags & (1 << 2)) != 0;
    out->offline_sync = (raw->flags & (1 << 3)) != 0;

    return true;
}
```
```cpp
#include <cstdint>
#include <span>
#include <expected>
#include <bit>

namespace iot::telemetry {

constexpr uint16_t MAGIC = 0xA55A;
constexpr uint8_t VERSION = 1;
constexpr size_t FRAME_SIZE = 24;

enum class ParseError {
    InvalidSize,
    InvalidMagic,
    UnsupportedVersion,
    ChecksumMismatch
};

struct Frame {
    uint32_t nodeId{0};
    uint32_t seqNum{0};
    uint32_t timestamp{0};
    float temperatureC{0.0f};
    float humidityPct{0.0f};
    float batteryV{0.0f};
    bool lowBattery{false};
    bool sensorFault{false};
    bool tamper{false};
    bool offlineSync{false};
};

[[nodiscard]] constexpr uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (int i = 0; i < 8; ++i) {
            if (crc & 0x8000) {
                crc = static_cast<uint16_t>((crc << 1) ^ 0x1021);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

[[nodiscard]] inline std::expected<Frame, ParseError> parse(std::span<const uint8_t> buffer) noexcept {
    if (buffer.size() < FRAME_SIZE) {
        return std::unexpected(ParseError::InvalidSize);
    }

    const auto readU16 = [](const uint8_t* p) -> uint16_t {
        return static_cast<uint16_t>(p[0] | (p[1] << 8));
    };

    const auto readI16 = [](const uint8_t* p) -> int16_t {
        return static_cast<int16_t>(p[0] | (p[1] << 8));
    };

    const auto readU32 = [](const uint8_t* p) -> uint32_t {
        return static_cast<uint32_t>(p[0] | (p[1] << 8) | (p[2] << 16) | (p[3] << 24));
    };

    const uint16_t magic = readU16(&buffer[0]);
    if (magic != MAGIC) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    const uint8_t version = buffer[2];
    if (version != VERSION) {
        return std::unexpected(ParseError::UnsupportedVersion);
    }

    const uint16_t expectedCrc = calculateCrc16(buffer.subspan(0, FRAME_SIZE - 2));
    const uint16_t actualCrc = readU16(&buffer[22]);
    if (expectedCrc != actualCrc) {
        return std::unexpected(ParseError::ChecksumMismatch);
    }

    Frame frame;
    const uint8_t flags = buffer[3];
    frame.nodeId = readU32(&buffer[4]);
    frame.seqNum = readU32(&buffer[8]);
    frame.timestamp = readU32(&buffer[12]);
    frame.temperatureC = static_cast<float>(readI16(&buffer[16])) / 100.0f;
    frame.humidityPct = static_cast<float>(readU16(&buffer[18])) / 100.0f;
    frame.batteryV = static_cast<float>(readU16(&buffer[20])) / 1000.0f;

    frame.lowBattery = (flags & (1 << 0)) != 0;
    frame.sensorFault = (flags & (1 << 1)) != 0;
    frame.tamper = (flags & (1 << 2)) != 0;
    frame.offlineSync = (flags & (1 << 3)) != 0;

    return frame;
}

} // namespace iot::telemetry
```
:::

---

## Схема реляційного сховища (TimescaleDB / PostgreSQL)

Після обробки та валідації службою дані записуються в базу даних часових рядів із партиціонуванням за часом:

```sql
-- Таблиця часових рядів телеметрії
CREATE TABLE telemetry_readings (
    measured_at TIMESTAMPTZ NOT NULL,
    node_id INTEGER NOT NULL,
    seq_num BIGINT NOT NULL,
    temperature_c REAL,
    humidity_pct REAL,
    battery_v REAL,
    flags SMALLINT NOT NULL DEFAULT 0,
    rssi_dbm SMALLINT,
    gateway_id VARCHAR(32),
    PRIMARY KEY (node_id, measured_at)
);

-- Перетворення у гіпертаблицю TimescaleDB з інтервалом партиції 7 днів
SELECT create_hypertable('telemetry_readings', 'measured_at', chunk_time_interval => INTERVAL '7 days');

-- Увімкнення політики компресії старих чанків для економії 90% дискового простору
ALTER TABLE telemetry_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'node_id',
    timescaledb.compress_orderby = 'measured_at DESC'
);

SELECT add_compression_policy('telemetry_readings', INTERVAL '30 days');
```
