# ⚙️ Адаптивний оптимізатор телеметрії та пакування кадру

Головне джерело неконтрольованих експлуатаційних витрат підключеного пристрою — надсилання сирих даних фіксованої структури за жорстким таймером. Якщо промисловий сенсор вимірює температуру підшипника чи тиск у магістралі кожні 10 секунд і щоразу транслює 150-байтний JSON через стільниковий модем, пристрій оплачує тисячі порожніх сесій зв'язку, де корисний сигнал відрізняється від попереднього лише шумом останнього розряду АЦП.

Оплата стільникового трафіку нараховується не лише за чисті байти, але й за кожне відкриття контексту передачі даних (PDP/PDN context activation) та округлення до кванта сесії (1 чи 10 КБ). Крім того, накладні витрати протоколів безпеки (TLS 1.3 Record Layer, TCP Handshake, MQTT Connect/Ack) перевищують розмір власне корисного вимірювання у десятки разів. Якщо пристрій транслює покази поодинці, компанія сплачує рахунки за повітря та транспортний синтаксис.

Інженерне розв'язання цієї проблеми зосереджене на рівні вбудованої прошивки. Програма поєднує три взаємодоповнюючі рівні оптимізації:
1. **Адаптивна дельта-фільтрація (Deadband & Swing Door Trending)**: сенсор опитується з високою частотою, але точка фіксується у пам'яті лише тоді, коли зміна фізичної величини перевищує поріг чутливості або кут нахилу тренду.
2. **Бінарне пакування зі змінною довжиною (Varint & Bit-packing)**: заміна рядкових ключів JSON та 64-бітних чисел із рухомою комою на цілочисельні дельти з фіксованою комою та бітові маски.
3. **Кільцевий буфер накопичення (Batching Accumulator)**: збереження відфільтрованих точок у локальній пам'яті (RAM / NOR Flash) для пакетної передачі через один спільний TLS/CoAP-сеанс раз на кілька годин або за подією тривоги.

## Принцип роботи адаптивного фільтра Deadband та Swing Door

У стаціонарному режимі фізичні параметри більшості технологічних об'єктів (температура теплоносія, рівень вібрації насоса, тиск у гідравліці) змінюються надзвичайно повільно або коливаються в межах шуму вимірювального тракту. Передавати кожне відхилення на 0.05 °C — це марнотратство ресурсу батареї та грошей компанії.

Алгоритм зони нечутливості (Deadband) порівнює поточне вимірювання з останнім зафіксованим базисним значенням. Якщо абсолютна різниця менша за встановлений поріг `deadband_abs`, поточний вимір відкидається без збереження в буфері. Щоб система не втрачала відчуття часу за тривалої відсутності змін, реалізовано обов'язковий інтервал надсилання життєвого сигналу (Heartbeat `max_interval_sec`): якщо значення залишається незмінним протягом, наприклад, 60 хвилин, алгоритм примусово фіксує поточну точку.

Для процесів із монотонною зміною (плавне нагрівання чи охолодження) звичайний Deadband створює східчасту апроксимацію. У таких випадках застосовується алгоритм поворотних дверей (Swing Door Trending, SDT), який будує лінійний коридор допустимої похибки: нова точка записується лише тоді, коли поточний нахил виходить за межі верхньої та нижньої опорних прямих.

## Архітектура оптимізатора телеметрії

```text
       ┌───────────────┐
       │   Сенсори     │ (опитування кожні 10 с)
       └───────┬───────┘
               │ вимірювання (raw_value, timestamp)
               ▼
┌──────────────────────────────┐
│ Deadband / Slope Компресор   │ ──► Відхилення < ε? ──► [Ігнорувати шум]
└──────────────┬───────────────┘
               │ суттєва точка (Δt, Δv)
               ▼
┌──────────────────────────────┐
│  Бінарний кодер (Bit-Pack)   │ ──► Пакування у 4–6 байтів замість 120 Б JSON
└──────────────┬───────────────┘
               │ стиснений блок
               ▼
┌──────────────────────────────┐
│ Flash Кільцевий буфер        │ ──► Буфер заповнений АБО виник алярм?
└──────────────┬───────────────┘
               │ ТАК (батч із 20–50 точок + 2Б прапорців здоров'я)
               ▼
┌──────────────────────────────┐
│   Мережевий передавач        │ ──► 1 спільний сеанс зв'язку (TLS / CoAP)
└──────────────────────────────┘
```

## Структура бінарного кадру батчу

Замість надсилання об'ємного текстового JSON бінарний кадр формується за жорстким, байт-орієнтованим контрактом:
1. **Заголовок (6 байтів)**:
   - Байт 0: Магічне число `0xAA` (ідентифікатор початку пакета);
   - Байт 1: Версія протоколу `0x01`;
   - Байт 2: Кількість точок у батчі `N` (1..255);
   - Байти 3–4: 16-бітна бітова маска діагностичного стану вузла (Reset Reason, Brownout, Watchdog, Battery Sag, Flash Wear);
   - Байт 5: Зарезервовано під розширення або прапорці пріоритету (Normal / Urgent Alarm).
2. **Базова опорна точка (8 байтів)**:
   - Байти 6–9: Повна 32-бітна мітка часу UNIX Timestamp у секундах;
   - Байти 10–13: Повне 32-бітне цілочисельне значення вимірювання з фіксованою комою.
3. **Масив дельта-точок (по 4 байти на кожну наступну точку)**:
   - 2 байти: `Δt = timestamp[i] - timestamp[0]` (зсув у секундах від базової точки, діапазон до 18.2 годин);
   - 2 байти: `Δv = value[i] - value[0]` (відносне відхилення фізичної величини зі знаком).

Така схема упаковує 32 вимірювання всього у `6 + 8 + 31 × 4 = 138` байтів! Для порівняння: аналогічний набір у JSON-форматі (`{"ts":1714567890,"val":24.58}`) важить понад 1100 байтів.

Нижче наведено повну реалізацію модуля оптимізації та батчингу. Реалізація мовою C розрахована на мікроконтролери з жорсткими обмеженнями пам'яті (C99), а реалізація на C++20 використовує типобезпечні абстракції, семантику переміщення, `std::span` та `std::expected`.

## Реалізація модуля компресії та батчингу

:::tabs
```c
/* telemetry_optimizer.h & telemetry_optimizer.c — Чистий C (C99) */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEMETRY_MAX_BATCH_SAMPLES  32
#define TELEMETRY_PAYLOAD_MAX_BYTES  256

typedef enum {
    TELEM_OK = 0,
    TELEM_DROPPED_NOISE = 1,
    TELEM_BUFFERED = 2,
    TELEM_BATCH_READY = 3,
    TELEM_ERR_OVERFLOW = -1,
    TELEM_ERR_PARAM = -2
} telem_status_t;

/* Структура одного вимірювання */
typedef struct {
    uint32_t timestamp_sec;
    int32_t  value_fixed;   /* Фіксована кома (наприклад, градуси × 100) */
} telem_sample_t;

/* Конфігурація зони нечутливості (Deadband) */
typedef struct {
    int32_t  deadband_abs;      /* Мінімальна абсолютна дельта для запису */
    uint32_t max_interval_sec;  /* Примусовий інтервал запису (Heartbeat) */
} telem_filter_config_t;

/* Стан оптимізатора */
typedef struct {
    telem_filter_config_t cfg;
    telem_sample_t        last_saved_sample;
    bool                  has_baseline;
    
    /* Кільцевий буфер накопичення */
    telem_sample_t        sample_buffer[TELEMETRY_MAX_BATCH_SAMPLES];
    uint16_t              sample_count;
    
    /* Діагностичні прапорці здоров'я вузла */
    uint16_t              system_health_flags;
} telem_optimizer_t;

void telem_init(telem_optimizer_t *opt, const telem_filter_config_t *cfg) {
    if (!opt || !cfg) return;
    memset(opt, 0, sizeof(telem_optimizer_t));
    opt->cfg = *cfg;
    opt->has_baseline = false;
    opt->sample_count = 0;
    opt->system_health_flags = 0;
}

void telem_set_health_flag(telem_optimizer_t *opt, uint16_t flag_mask, bool active) {
    if (!opt) return;
    if (active) {
        opt->system_health_flags |= flag_mask;
    } else {
        opt->system_health_flags &= ~flag_mask;
    }
}

/* Перевірка необхідності збереження вимірювання */
static bool telem_should_save(telem_optimizer_t *opt, const telem_sample_t *s) {
    if (!opt->has_baseline) return true;

    /* Примусовий запис за максимальним тайм-аутом */
    if ((s->timestamp_sec - opt->last_saved_sample.timestamp_sec) >= opt->cfg.max_interval_sec) {
        return true;
    }

    /* Фільтрація Deadband */
    int32_t diff = s->value_fixed - opt->last_saved_sample.value_fixed;
    if (diff < 0) diff = -diff;

    return (diff >= opt->cfg.deadband_abs);
}

/* Запис нового вимірювання в оптимізатор */
telem_status_t telem_push_sample(telem_optimizer_t *opt, uint32_t ts, int32_t val) {
    if (!opt) return TELEM_ERR_PARAM;

    telem_sample_t current = { .timestamp_sec = ts, .value_fixed = val };

    if (!telem_should_save(opt, &current)) {
        return TELEM_DROPPED_NOISE;
    }

    if (opt->sample_count >= TELEMETRY_MAX_BATCH_SAMPLES) {
        return TELEM_ERR_OVERFLOW;
    }

    opt->sample_buffer[opt->sample_count++] = current;
    opt->last_saved_sample = current;
    opt->has_baseline = true;

    if (opt->sample_count >= TELEMETRY_MAX_BATCH_SAMPLES) {
        return TELEM_BATCH_READY;
    }

    return TELEM_BUFFERED;
}

/* Серіалізація батчу у компактний бінарний кадр */
int32_t telem_serialize_batch(telem_optimizer_t *opt, uint8_t *out_buf, uint16_t max_len) {
    if (!opt || !out_buf || opt->sample_count == 0) return TELEM_ERR_PARAM;

    /* Оцінка необхідного розміру: заголовок (6Б) + базова точка (8Б) + дельти (4Б/точка) */
    uint16_t required_len = 6 + 8 + (opt->sample_count - 1) * 4;
    if (max_len < required_len) return TELEM_ERR_OVERFLOW;

    uint16_t ptr = 0;

    /* 1. Заголовок кадру */
    out_buf[ptr++] = 0xAA; /* Magic byte */
    out_buf[ptr++] = 0x01; /* Версія протоколу */
    out_buf[ptr++] = (uint8_t)opt->sample_count;
    
    /* Прапорці здоров'я (2 байти) */
    out_buf[ptr++] = (uint8_t)(opt->system_health_flags & 0xFF);
    out_buf[ptr++] = (uint8_t)((opt->system_health_flags >> 8) & 0xFF);
    out_buf[ptr++] = 0x00; /* Зарезервовано */

    /* 2. Базова точка (повна мітка часу та повне значення) */
    telem_sample_t base = opt->sample_buffer[0];
    memcpy(&out_buf[ptr], &base.timestamp_sec, sizeof(uint32_t));
    ptr += sizeof(uint32_t);
    memcpy(&out_buf[ptr], &base.value_fixed, sizeof(int32_t));
    ptr += sizeof(int32_t);

    /* 3. Дельта-кодовані точки (Δt у секундах uint16_t, Δv у фіксованих одиницях int16_t) */
    for (uint16_t i = 1; i < opt->sample_count; ++i) {
        uint32_t dt = opt->sample_buffer[i].timestamp_sec - base.timestamp_sec;
        int32_t  dv = opt->sample_buffer[i].value_fixed - base.value_fixed;

        uint16_t dt_u16 = (dt > 0xFFFF) ? 0xFFFF : (uint16_t)dt;
        int16_t  dv_i16 = (dv > 32767) ? 32767 : ((dv < -32768) ? -32768 : (int16_t)dv);

        memcpy(&out_buf[ptr], &dt_u16, sizeof(uint16_t));
        ptr += sizeof(uint16_t);
        memcpy(&out_buf[ptr], &dv_i16, sizeof(int16_t));
        ptr += sizeof(int16_t);
    }

    /* Скидання буфера після успішної серіалізації */
    opt->sample_count = 0;
    return (int32_t)ptr;
}
```
```cpp
/* TelemetryOptimizer.hpp — Ідіоматичний C++20 */
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <string_view>
#include <optional>
#include <expected>
#include <algorithm>
#include <bit>

namespace embedded::telemetry {

enum class Status {
    Ok,
    DroppedNoise,
    Buffered,
    BatchReady
};

enum class Error {
    BufferOverflow,
    BufferTooSmall,
    InvalidParameter,
    NoData
};

struct Sample {
    uint32_t timestampSec{0};
    int32_t  valueFixed{0};     // Фіксована кома (наприклад, одиниці × 100)
};

struct FilterConfig {
    int32_t  deadbandAbs{10};    // Мінімальний поріг відхилення
    uint32_t maxIntervalSec{3600}; // Максимальний інтервал Heartbeat
};

template <size_t MaxSamples = 32>
class TelemetryOptimizer {
public:
    explicit constexpr TelemetryOptimizer(FilterConfig cfg) noexcept
        : config_{cfg} {}

    void setHealthFlag(uint16_t flagMask, bool active) noexcept {
        if (active) {
            healthFlags_ |= flagMask;
        } else {
            healthFlags_ &= static_cast<uint16_t>(~flagMask);
        }
    }

    [[nodiscard]] std::expected<Status, Error> pushSample(uint32_t timestamp, int32_t value) noexcept {
        Sample current{timestamp, value};

        if (!shouldSave(current)) {
            return Status::DroppedNoise;
        }

        if (sampleCount_ >= MaxSamples) {
            return std::unexpected(Error::BufferOverflow);
        }

        buffer_[sampleCount_++] = current;
        lastSaved_ = current;
        hasBaseline_ = true;

        if (sampleCount_ >= MaxSamples) {
            return Status::BatchReady;
        }

        return Status::Buffered;
    }

    [[nodiscard]] std::expected<size_t, Error> serializeBatch(std::span<uint8_t> output) noexcept {
        if (sampleCount_ == 0) {
            return std::unexpected(Error::NoData);
        }

        const size_t requiredSize = 6 + sizeof(uint32_t) + sizeof(int32_t) + (sampleCount_ - 1) * 4;
        if (output.size() < requiredSize) {
            return std::unexpected(Error::BufferTooSmall);
        }

        size_t offset = 0;

        // 1. Заголовок
        output[offset++] = 0xAA; // Magic
        output[offset++] = 0x01; // Version
        output[offset++] = static_cast<uint8_t>(sampleCount_);
        output[offset++] = static_cast<uint8_t>(healthFlags_ & 0xFF);
        output[offset++] = static_cast<uint8_t>((healthFlags_ >> 8) & 0xFF);
        output[offset++] = 0x00; // Reserved

        // 2. Базова точка
        const auto& base = buffer_[0];
        writeBytes(output, offset, base.timestampSec);
        writeBytes(output, offset, base.valueFixed);

        // 3. Дельта-точки (uint16_t dt, int16_t dv)
        for (size_t i = 1; i < sampleCount_; ++i) {
            const uint32_t dt = buffer_[i].timestampSec - base.timestampSec;
            const int32_t  dv = buffer_[i].valueFixed - base.valueFixed;

            const auto dtClamped = static_cast<uint16_t>(std::min<uint32_t>(dt, 0xFFFF));
            const auto dvClamped = static_cast<int16_t>(std::clamp<int32_t>(dv, -32768, 32767));

            writeBytes(output, offset, dtClamped);
            writeBytes(output, offset, dvClamped);
        }

        sampleCount_ = 0; // Скидання буфера після успішного пакування
        return offset;
    }

    [[nodiscard]] size_t currentBatchSize() const noexcept { return sampleCount_; }
    [[nodiscard]] bool empty() const noexcept { return sampleCount_ == 0; }

private:
    template <typename T>
    static void writeBytes(std::span<uint8_t> dst, size_t& offset, T value) noexcept {
        auto rawBytes = std::bit_cast<std::array<uint8_t, sizeof(T)>>(value);
        std::copy(rawBytes.begin(), rawBytes.end(), dst.begin() + offset);
        offset += sizeof(T);
    }

    [[nodiscard]] bool shouldSave(const Sample& current) const noexcept {
        if (!hasBaseline_) return true;

        if ((current.timestampSec - lastSaved_.timestampSec) >= config_.maxIntervalSec) {
            return true;
        }

        const int32_t diff = std::abs(current.valueFixed - lastSaved_.valueFixed);
        return diff >= config_.deadbandAbs;
    }

    FilterConfig                 config_;
    Sample                       lastSaved_{};
    bool                         hasBaseline_{false};
    std::array<Sample, MaxSamples> buffer_{};
    size_t                       sampleCount_{0};
    uint16_t                     healthFlags_{0};
};

} // namespace embedded::telemetry
```
:::

## Інженерні пастки та крайові випадки

### 1. Переповнення розрядності дельти при різкому стрибку процесу

Якщо технологічний процес зазнає аварійного або ступеневого стрибка (наприклад, аварійне зростання тиску з 2 до 80 бар за секунду), відносна дельта `dv` вийде за межі діапазону 16-бітного числа зі знаком `int16_t` (`[-32768, 32767]`). 

Операція насичення `std::clamp` чи приведення типів у такій ситуації призведе до фатального викривлення даних на сервері: сервер отримає зрізане значення замість справжнього аварійного стрибка. 

Коректна логіка драйвера передбачає перевірку виходу дельти за діапазон перед записом:
- Якщо `|dv| > 32000`, поточний батч негайно закривається на індексі `i - 1`;
- Модуль ініціює створення нового батчу, де нова екстремальна точка записується як повнорозмірна 32-бітна базова точка;
- Батч позначається прапорцем терміновості (Urgent Alarm) і негайно передається в чергу відправки модема.

### 2. Стрибки годинника реального часу (RTC Clock Skew)

Вбудовані системи регулярно коригують власний час за протоколами NTP, NITZ (із базової станції GSM) або GPS. Якщо локальний годинник мікроконтролера поспішав на 3 хвилини, а синхронізація перевела час назад, віднімання `timestamp[i] - timestamp[0]` дасть від'ємне значення.

Оскільки `Δt` зберігається як беззнакове 16-бітне ціле `uint16_t`, від'ємна дельта перетвориться на гігантське число (наприклад, `0xFFE0 = 65504` секунди). Хмарний бекенд інтерпретує це як вимірювання з майбутнього або викине весь батч через порушення хронології.

**Правило захисту**: якщо `timestamp_sec < last_saved_sample.timestamp_sec`, прошивка фіксує стрибок часу, скидає поточний буфер як окремий сегмент і встановлює прапорець `RTC_SYNC_ADJUST` у заголовку наступного кадру.

### 3. Знос NOR Flash при накопиченні батчів

Збереження батчів в оперативній пам'яті (SRAM) загрожує втратою накопичених вимірювань у разі перезавантаження мікроконтролера сторожовим таймером (Watchdog) або просідання напруги. Проте наївне збереження кожного знімка в зовнішню енергонезалежну флеш-пам'ять (SPI Flash / EEPROM) створює ризик швидкого фізичного зносу комірок.

Якщо записувати батч у фіксований сектор Flash кожні 5 хвилин, ліміт у 100 000 циклів стирання буде вичерпано за:

```text
100 000 циклів / (12 записів/год · 24 год · 365 днів) ≈ 0.95 року
```

Через 11 місяців плата вийде з ладу в полі, спричинивши гарантійну заміну пристрою (RMA). 

Для запобігання деградації застосовують дві взаємопов'язані техніки:
1. **Накопичення в SRAM із живленням від резервного домену (Backup Battery / RTC SRAM)**: дані зберігаються в ОЗП до повного заповнення 32 точок і записуються у Flash єдиним блоком лише перед відключенням або раз на кілька годин;
2. **Кільцевий журнал із вирівнюванням зносу (Wear-Leveling Ring Log)**: виділяється пул із 16–32 секторів Flash (наприклад, 128 КБ). Нові записи додаються послідовно в кінець поточного сектора без його стирання (використовуючи властивість Flash змінювати біти з `1` на `0`), а очищення сектора виконується лише тоді, коли весь пул заповнено по колу. Це збільшує термін служби флеш-пам'яті до 25–30 років безперервної експлуатації.
