# ⚙️ Бінарний пакер телеметрії: бітові поля, фіксована кома та CRC16

Цей проєкт реалізує нуль-алокаційний серіалізатор і десеріалізатор польових телеметричних кадрів, який стискає розлогий набір сенсорних вимірювань (мітка часу, температура, напруга, вологість, стан 8 дискретних прапорців) у фіксовані 13 байтів із контрольною сумою CRC16-CCITT замість 120–150 байтів у форматі JSON.

## Задача компактного пакування в автономних системах

Польовий автономний контролер збирає комплекс фізичних параметрів щосекунди або раз на кілька хвилин:
1. Абсолютний час вимірювання (32-бітний лічильник секунд Unix Timestamp).
2. Температуру навколишнього середовища (діапазон від −40.00 °C до +85.00 °C, апаратна роздільна здатність сенсора 0.01 °C).
3. Напругу живлення батареї (діапазон від 0.00 В до 5.00 В, роздільна здатність вимірювання АЦП 1 мВ).
4. Відносну вологість повітря (діапазон від 0.0 % до 100.0 %, крок 0.5 %).
5. Вісім дискретних сигналів (тривога зламу, тампер, статус клапана, прапорець заклинювання, стан радіозв'язку, індикатор переповнення тощо).

У типовому форматі JSON такий пакет виглядає так:
```json
{"ts":1724673600,"temp":23.45,"batt":3.612,"hum":58.5,"flags":{"tamper":0,"alarm":0,"valve":1,"rf_ok":1}}
```

Довжина цього рядка складає 110 байтів без пробілів і переносу рядків. Якщо передавати це модемом NB-IoT або радіомодулем LoRaWAN, кожна передача забирає додатковий час у радіоефірі, розряджає батарею та збільшує рахунок стільникового оператора.

## Архітектура та структура бінарного кадру

Ми оптимізуємо структуру до 13 байтів без використання динамічної пам'яті (купа не використовується взагалі):
- Байт 0: Магічний байт і версія (`0x5A` у старшому ніблі та 4-бітний номер версії `0x01` у молодшому ніблі).
- Байти 1–4: 32-бітне ціле число `uint32_t` Unix Timestamp у мережевому порядку байтів (Big-Endian).
- Байти 5–6: Температура `int16_t` як `T × 100` (значення −4000..+8500 займає 2 байти зі знаком).
- Байти 7–8: Напруга `uint16_t` у мілівольтах (0..5000 мВ, 2 байти без знаку).
- Байт 9: Вологість `uint8_t` як `H × 2` (значення 0..200 для 0.0..100.0% з кроком 0.5%).
- Байт 10: Бітова маска прапорців стану `uint8_t` (8 незалежних бітів, кожен біт відповідає за один стан).
- Байти 11–12: Контрольна сума CRC16-CCITT (поліном 0x1021, початкове значення 0xFFFF) поверх байтів 0..10.

Загальний розмір корисного кадру: рівно 13 байтів (разом із заголовком і CRC16).

## Квантування та арифметика з фіксованою комою

При перетворенні чисел з плаваючою комою у цілочисельний формат із фіксованою комою наївне множення та відтинання дробової частини через приведення типу `(int16_t)(temp * 100.0f)` породжує похибки квантування через особливості двійкового представлення IEEE-754. Наприклад, число `23.45` у форматі `float` представляється як `23.44999885...`. Звичайне відтинання дасть `2344` замість `2345`.

Щоб уникнути зміщення значень, застосовується симетричне округлення до найближчого цілого:

:::tabs
```c
int16_t temp_fixed = (temp_celsius >= 0.0f) 
    ? (int16_t)(temp_celsius * 100.0f + 0.5f) 
    : (int16_t)(temp_celsius * 100.0f - 0.5f);
```
```cpp
#include <cmath>
#include <cstdint>

int16_t temp_fixed = static_cast<int16_t>(std::lround(temp_celsius * 100.0));
```
:::

Також перед серіалізацією слід обов'язково перевіряти діапазони фізичних величин (clamp validation). Якщо датчик вийшов з ладу і повертає нереалістичне значення, наприклад `+999.0 °C`, спроба записати це в `int16_t` призведе до переповнення типу, якщо множити на 100 без обмеження.

## Реалізація пакера на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEM_FRAME_MAGIC   0x50
#define TELEM_FRAME_VERSION 0x01
#define TELEM_FRAME_SIZE    13

typedef struct {
    uint32_t timestamp;
    int16_t  temp_centi_deg;  /* Температура * 100 (напр. 2345 = 23.45 °C) */
    uint16_t batt_millivolts; /* Напруга в мВ (напр. 3612 = 3.612 В) */
    uint8_t  hum_half_pct;    /* Вологість * 2 (напр. 117 = 58.5 %) */
    uint8_t  flags;           /* 8 дискретних бітів стану */
} TelemetryData;

/* Обчислення CRC16-CCITT (поліном 0x1021, init 0xFFFF) без таблиці в RAM */
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/* Серіалізація структури у фіксований буфер (Big-Endian) */
bool telemetry_pack(const TelemetryData *src, uint8_t *dst_buf, size_t buf_len) {
    if (!src || !dst_buf || buf_len < TELEM_FRAME_SIZE) {
        return false;
    }

    dst_buf[0] = (TELEM_FRAME_MAGIC & 0xF0) | (TELEM_FRAME_VERSION & 0x0F);

    /* Час uint32_t у Big-Endian через побайтовий зсув */
    dst_buf[1] = (uint8_t)((src->timestamp >> 24) & 0xFF);
    dst_buf[2] = (uint8_t)((src->timestamp >> 16) & 0xFF);
    dst_buf[3] = (uint8_t)((src->timestamp >> 8) & 0xFF);
    dst_buf[4] = (uint8_t)(src->timestamp & 0xFF);

    /* Температура int16_t у Big-Endian */
    uint16_t raw_temp = (uint16_t)src->temp_centi_deg;
    dst_buf[5] = (uint8_t)((raw_temp >> 8) & 0xFF);
    dst_buf[6] = (uint8_t)(raw_temp & 0xFF);

    /* Напруга uint16_t у Big-Endian */
    dst_buf[7] = (uint8_t)((src->batt_millivolts >> 8) & 0xFF);
    dst_buf[8] = (uint8_t)(src->batt_millivolts & 0xFF);

    /* Вологість та бітові прапорці */
    dst_buf[9]  = src->hum_half_pct;
    dst_buf[10] = src->flags;

    /* Обчислення та запис CRC16 поверх перших 11 байтів */
    uint16_t crc = crc16_ccitt(dst_buf, 11);
    dst_buf[11] = (uint8_t)((crc >> 8) & 0xFF);
    dst_buf[12] = (uint8_t)(crc & 0xFF);

    return true;
}

/* Десеріалізація з перевіркою версії та контрольної суми */
bool telemetry_unpack(const uint8_t *src_buf, size_t buf_len, TelemetryData *dst) {
    if (!src_buf || !dst || buf_len < TELEM_FRAME_SIZE) {
        return false;
    }

    uint8_t magic_ver = src_buf[0];
    if ((magic_ver & 0xF0) != (TELEM_FRAME_MAGIC & 0xF0)) {
        return false;
    }
    if ((magic_ver & 0x0F) != TELEM_FRAME_VERSION) {
        return false;
    }

    /* Перевірка цілісності CRC16 */
    uint16_t expected_crc = ((uint16_t)src_buf[11] << 8) | src_buf[12];
    uint16_t actual_crc = crc16_ccitt(src_buf, 11);
    if (expected_crc != actual_crc) {
        return false;
    }

    /* Розпакування полів із мережевого порядку байтів */
    dst->timestamp = ((uint32_t)src_buf[1] << 24) |
                     ((uint32_t)src_buf[2] << 16) |
                     ((uint32_t)src_buf[3] << 8)  |
                     (uint32_t)src_buf[4];

    dst->temp_centi_deg  = (int16_t)(((uint16_t)src_buf[5] << 8) | src_buf[6]);
    dst->batt_millivolts = ((uint16_t)src_buf[7] << 8) | src_buf[8];
    dst->hum_half_pct    = src_buf[9];
    dst->flags           = src_buf[10];

    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <cmath>

namespace telemetry {

inline constexpr uint8_t FrameMagic   = 0x50;
inline constexpr uint8_t FrameVersion = 0x01;
inline constexpr size_t  FrameSize    = 13;

enum class UnpackError {
    BufferTooSmall,
    InvalidMagic,
    UnsupportedVersion,
    CrcMismatch
};

struct TelemetryData {
    uint32_t timestamp{0};
    int16_t  temp_centi_deg{0};
    uint16_t batt_millivolts{0};
    uint8_t  hum_half_pct{0};
    uint8_t  flags{0};

    [[nodiscard]] double temperature_celsius() const noexcept {
        return static_cast<double>(temp_centi_deg) / 100.0;
    }

    [[nodiscard]] double battery_volts() const noexcept {
        return static_cast<double>(batt_millivolts) / 1000.0;
    }

    [[nodiscard]] double humidity_pct() const noexcept {
        return static_cast<double>(hum_half_pct) * 0.5;
    }

    static TelemetryData from_physical(uint32_t ts, double temp, double batt_v, double hum, uint8_t fl) noexcept {
        TelemetryData d{};
        d.timestamp = ts;
        d.temp_centi_deg = static_cast<int16_t>(std::lround(temp * 100.0));
        d.batt_millivolts = static_cast<uint16_t>(std::lround(batt_v * 1000.0));
        d.hum_half_pct = static_cast<uint8_t>(std::clamp(std::lround(hum * 2.0), 0L, 200L));
        d.flags = fl;
        return d;
    }
};

class FramePacker {
public:
    static constexpr uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (const uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    static bool pack(const TelemetryData& src, std::span<uint8_t> dst) noexcept {
        if (dst.size() < FrameSize) {
            return false;
        }

        dst[0] = (FrameMagic & 0xF0) | (FrameVersion & 0x0F);

        dst[1] = static_cast<uint8_t>((src.timestamp >> 24) & 0xFF);
        dst[2] = static_cast<uint8_t>((src.timestamp >> 16) & 0xFF);
        dst[3] = static_cast<uint8_t>((src.timestamp >> 8) & 0xFF);
        dst[4] = static_cast<uint8_t>(src.timestamp & 0xFF);

        const auto raw_temp = static_cast<uint16_t>(src.temp_centi_deg);
        dst[5] = static_cast<uint8_t>((raw_temp >> 8) & 0xFF);
        dst[6] = static_cast<uint8_t>(raw_temp & 0xFF);

        dst[7] = static_cast<uint8_t>((src.batt_millivolts >> 8) & 0xFF);
        dst[8] = static_cast<uint8_t>(src.batt_millivolts & 0xFF);

        dst[9]  = src.hum_half_pct;
        dst[10] = src.flags;

        const uint16_t crc = calculate_crc16(dst.subspan(0, 11));
        dst[11] = static_cast<uint8_t>((crc >> 8) & 0xFF);
        dst[12] = static_cast<uint8_t>(crc & 0xFF);

        return true;
    }

    [[nodiscard]] static std::expected<TelemetryData, UnpackError> unpack(
        std::span<const uint8_t> src) noexcept {
        if (src.size() < FrameSize) {
            return std::unexpected(UnpackError::BufferTooSmall);
        }

        const uint8_t header = src[0];
        if ((header & 0xF0) != (FrameMagic & 0xF0)) {
            return std::unexpected(UnpackError::InvalidMagic);
        }
        if ((header & 0x0F) != FrameVersion) {
            return std::unexpected(UnpackError::UnsupportedVersion);
        }

        const uint16_t expected_crc = (static_cast<uint16_t>(src[11]) << 8) | src[12];
        const uint16_t actual_crc = calculate_crc16(src.subspan(0, 11));
        if (expected_crc != actual_crc) {
            return std::unexpected(UnpackError::CrcMismatch);
        }

        TelemetryData result{};
        result.timestamp = (static_cast<uint32_t>(src[1]) << 24) |
                           (static_cast<uint32_t>(src[2]) << 16) |
                           (static_cast<uint32_t>(src[3]) << 8)  |
                           static_cast<uint32_t>(src[4]);

        result.temp_centi_deg  = static_cast<int16_t>((static_cast<uint16_t>(src[5]) << 8) | src[6]);
        result.batt_millivolts = (static_cast<uint16_t>(src[7]) << 8) | src[8];
        result.hum_half_pct    = src[9];
        result.flags           = src[10];

        return result;
    }
};

} // namespace telemetry
```
:::

## Потоковий розбір у кільцевому буфері UART

При прийомі бінарного кадру через послідовний порт UART утилітою або шлюзом байти надходять неперервним потоком без маркерів меж пакетів. Для надійного виділення кадру без копіювання в проміжний масив використовується автомат станів ковзного вікна:

1. Алгоритм сканує вхідний кільцевий буфер у пошуках байта з преамбулою `0x50` (`(byte & 0xF0) == 0x50`).
2. При виявленні преамбули перевіряється, чи є в буфері щонайменше 13 доступних байтів.
3. Обчислюється CRC16 над першими 11 байтами. Якщо сума збігається з двома останніми байтами, кадр вважається валідним і передається на обробку, а покажчик буфера зміщується на 13 байтів.
4. Якщо CRC16 не зійшлася, преамбула вважається помилковим збігом у випадкових даних, покажчик зміщується лише на 1 байт уперед, і пошук преамбули продовжується.

Такий підхід повністю захищає пристрій від спотворення даних під час перешкод у радіоефірі та не потребує додаткових символів кадрування типу COBS або HDLC.

## Підводні камені апаратної реалізації

### 1. Небезпека копіювання структур через `memcpy`

Початківці часто намагаються упакувати кадр прямим викликом `memcpy(buffer, &struct, sizeof(struct))`. Це призводить до трьох фатальних проблем:
- **Вирівнювання пам'яті (Alignment Padding)**: За стандартами C ABI компілятор додає порожні байти вирівнювання між полями різного розміру. Наприклад, поле `uint32_t` після `uint8_t` на 32-бітному ARM автоматично зміщується на 3 байти вперед, роздуваючи розмір кадру з 13 до 16–20 байтів і заповнюючи порожнечі сміттям зі стека.
- **Апаратні аномалії невирівняного доступу (Unaligned Access)**: На ядрах ARM Cortex-M0 і Cortex-M0+ пряме розіменування покажчика `*(uint32_t*)&buffer[1]` призводить до апаратного виключення `HardFault`, оскільки ядро фізично не підтримує читання 32-бітних слів за непарними адресами. Побайтовий зсув `(src[1] << 24) | (src[2] << 16)...` компілюється в безпечні побайтові інструкції `LDRB` і гарантовано працює на будь-якому ядрі без помилок шини.
- **Порядок байтів (Endianness)**: Більшість мікроконтролерів Cortex-M є Little-Endian (молодший байт за молодшою адресою), тоді як мережеві протоколи вимагають Big-Endian. Прямий `memcpy` порушує порядок байтів при читанні на сервері з іншою архітектурою.

### 2. Вибір алгоритму CRC: таблиця проти ітерацій

Для автономних мікроконтролерів із жорстким обмеженням пам'яті (наприклад, STM32L0 з 8 КБ Flash або 2 КБ RAM) попередньо розрахована таблиця CRC16 на 256 елементів (512 байтів) займає надто велику частку простору програм. Порозрядний ітераційний алгоритм виконує рівно 8 ітерацій на байт і для 11-байтового кадру потребує лише 88 тактів процесора (менше 2 мікросекунд на частоті 48 МГц), що повністю нівелює потребу у використанні пам'яті для таблиць.
