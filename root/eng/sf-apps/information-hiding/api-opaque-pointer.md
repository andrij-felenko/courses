# 📋 Неповні типи та Opaque Pointer: контракт приховування на рівні ABI

У системному та низькорівневому програмуванні на C та C++ принцип приховування інформації часто стикається з фізичною природою роботи компілятора. Якщо розміри, зміщення полів та внутрішні структури даних модуля оголошені у відкритому заголовному файлі (`.h` або `.hpp`), кожна одиниця трансляції, яка підключає цей заголовок через директиву `#include`, стає жорстко прив'язаною до конкретного бінарного представлення структури в оперативній пам'яті.

Будь-яка зміна внутрішнього поля — зміна типу змінної з `uint16_t` на `uint32_t`, додавання прапорця стану, зміна порядку полів для оптимізації вирівнювання або заміна типу внутрішнього буфера — автоматично змінює розмір структури (`sizeof`) та зміщення окремих полів (`offsetof`). Як наслідок, усі залежні клієнтські файли змушені проходити повну перекомпіляцію, а бінарна сумісність динамічних бібліотек незворотно руйнується.

Патерн непрозорого покажчика (англ. *Opaque Pointer*, *Handle* або *Incomplete Type*) створює непорушний компіляційний бар'єр: клієнтський код оперує виключно покажчиком на неповний тип, розмір якого компілятору відомий заздалегідь (4 байти на 32-бітних або 8 байтів на 64-бітних платформах), тоді як повне визначення структури залишається абсолютно прихованим усередині єдиного файлу реалізації (`.c` або `.cpp`).

Нижче наведено еталонну специфікацію публічного контракту та внутрішньої реалізації для модуля обробки телеметрії давачів, що ілюструє побудову такого компіляційного бар'єра на рівні мови та таблиць символів компілятора.

## Публічний інтерфейс: заголовок модуля

Клієнтський код взаємодіє з модулем виключно через публічний заголовок. Заголовок містить лише попереднє оголошення типу (`typedef struct telemetry_engine telemetry_engine_t;`), конфігураційні структури, коди результатів та сигнатури функцій.

Оскільки компілятор клієнта не бачить внутрішніх полів структури, спроба звернутися до `engine->sample_rate_hz` напряму згенерує помилку компіляції («dereferencing pointer to incomplete type»). Єдиний спосіб виконати операцію над модулем — викликати надану функцію публічного API.

:::tabs
```c
/* telemetry_engine.h — публічний контракт модуля */
#ifndef TELEMETRY_ENGINE_H
#define TELEMETRY_ENGINE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Неповний тип: компілятор знає лише про існування імені типу */
typedef struct telemetry_engine telemetry_engine_t;

/* Коди результату виконання операцій (статус-контракт) */
typedef enum {
    TE_OK              =  0,
    TE_ERR_INVALID_ARG = -1,
    TE_ERR_NO_MEMORY   = -2,
    TE_ERR_OVERFLOW    = -3,
    TE_ERR_HARDWARE_IO = -4
} te_status_t;

/* Публічна конфігурація для створення екземпляра */
typedef struct {
    uint32_t sample_rate_hz;
    size_t   max_channels;
} te_config_t;

/* =========================================================================
 * Керування життєвим циклом (Lifecycle)
 * ========================================================================= */

/**
 * Створює новий екземпляр модуля телеметрії.
 * Виділяє пам'ять під повну структуру всередині файлу реалізації.
 * Повертає покажчик на екземпляр або NULL при нестачі пам'яті / некоректних параметрах.
 */
telemetry_engine_t* te_create(const te_config_t *config);

/**
 * Знищує екземпляр, звільняє всі внутрішні ресурси та пам'ять.
 * Безпечно приймати NULL (операція no-op).
 */
void te_destroy(telemetry_engine_t *engine);

/* =========================================================================
 * Публічні операції над станом (Operations)
 * ========================================================================= */

/**
 * Записує виміряне значення у вказаний канал телеметрії.
 * Передумови: engine != NULL, channel_id < max_channels.
 * Постумова: значення додано у внутрішній кільцевий буфер, оновлено суму.
 */
te_status_t te_push_sample(telemetry_engine_t *engine, uint16_t channel_id, float value);

/**
 * Обчислює поточне ковзне середнє для вказаного каналу.
 * Результат записується у *out_mean.
 */
te_status_t te_get_channel_mean(const telemetry_engine_t *engine, uint16_t channel_id, float *out_mean);

/**
 * Скидає накопичену історію всіх каналів без перерозподілу пам'яті.
 */
te_status_t te_reset(telemetry_engine_t *engine);

#ifdef __cplusplus
}
#endif

#endif /* TELEMETRY_ENGINE_H */
```
```cpp
/* telemetry_engine.hpp — ідіоматичний PIMPL-інтерфейс для C++20 */
#pragma once

#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <cstdint>

enum class TelemetryError {
    InvalidArg,
    NoMemory,
    Overflow,
    HardwareIo
};

struct TelemetryConfig {
    uint32_t sample_rate_hz{100};
    size_t   max_channels{16};
};

class TelemetryEngine {
public:
    explicit TelemetryEngine(const TelemetryConfig &config);
    ~TelemetryEngine();

    /* Заборона небезпечного копіювання, дозвіл переміщення ресурсу (RAII) */
    TelemetryEngine(const TelemetryEngine &) = delete;
    TelemetryEngine &operator=(const TelemetryEngine &) = delete;
    TelemetryEngine(TelemetryEngine &&) noexcept;
    TelemetryEngine &operator=(TelemetryEngine &&) noexcept;

    /* Публічні операції з типізованою обробкою результатів через std::expected */
    [[nodiscard]] std::expected<void, TelemetryError> 
    push_sample(uint16_t channel_id, float value) noexcept;

    [[nodiscard]] std::expected<float, TelemetryError> 
    get_channel_mean(uint16_t channel_id) const noexcept;

    void reset() noexcept;

private:
    /* Неповний тип внутрішньої реалізації (Pointer to Implementation) */
    struct Impl;
    std::unique_ptr<Impl> pimpl_;
};
```
:::

---

## Внутрішня реалізація: повне визначення структури

Повне визначення структури розміщене виключно у файлі реалізації (`telemetry_engine.c` або `telemetry_engine.cpp`). Тут зосереджені всі приватні деталі: масиви відліків, внутрішні лічильники, алгоритми оновлення ковзної суми та захисні інваріанти.

Будь-які зміни внутрішнього представлення (наприклад, перехід від фіксованого буфера розміром 64 до динамічного або фільтра Калмана) не змінюють жодного байта у публічному файлі заголовка.

:::tabs
```c
/* telemetry_engine.c — прихована реалізація модуля */
#include "telemetry_engine.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define RING_BUFFER_SIZE 64

/* ПРИВАТНЕ представлення окремого каналу вимірювань */
typedef struct {
    float  samples[RING_BUFFER_SIZE];
    size_t head;
    size_t count;
    float  running_sum;
} channel_state_t;

/* ПОВНЕ визначення структури — головна таємниця модуля */
struct telemetry_engine {
    uint32_t         sample_rate_hz;
    size_t           channel_count;
    channel_state_t *channels;
    uint32_t         total_samples_processed;
};

/* Приватна допоміжна функція валідації стану (внутрішній інваріант) */
static inline bool te_is_valid(const telemetry_engine_t *e) {
    return (e != NULL && e->channels != NULL && e->channel_count > 0);
}

telemetry_engine_t* te_create(const te_config_t *config) {
    if (!config || config->max_channels == 0) return NULL;

    telemetry_engine_t *e = (telemetry_engine_t*)malloc(sizeof(telemetry_engine_t));
    if (!e) return NULL;

    e->sample_rate_hz = config->sample_rate_hz;
    e->channel_count = config->max_channels;
    e->total_samples_processed = 0;

    e->channels = (channel_state_t*)calloc(e->channel_count, sizeof(channel_state_t));
    if (!e->channels) {
        free(e);
        return NULL;
    }

    return e;
}

void te_destroy(telemetry_engine_t *engine) {
    if (!engine) return;
    free(engine->channels);
    free(engine);
}

te_status_t te_push_sample(telemetry_engine_t *engine, uint16_t channel_id, float value) {
    if (!te_is_valid(engine)) return TE_ERR_INVALID_ARG;
    if (channel_id >= engine->channel_count) return TE_ERR_INVALID_ARG;

    channel_state_t *ch = &engine->channels[channel_id];
    
    if (ch->count == RING_BUFFER_SIZE) {
        ch->running_sum -= ch->samples[ch->head];
    } else {
        ch->count++;
    }

    ch->samples[ch->head] = value;
    ch->running_sum += value;
    ch->head = (ch->head + 1) % RING_BUFFER_SIZE;
    
    engine->total_samples_processed++;
    return TE_OK;
}

te_status_t te_get_channel_mean(const telemetry_engine_t *engine, uint16_t channel_id, float *out_mean) {
    if (!te_is_valid(engine) || !out_mean) return TE_ERR_INVALID_ARG;
    if (channel_id >= engine->channel_count) return TE_ERR_INVALID_ARG;

    const channel_state_t *ch = &engine->channels[channel_id];
    if (ch->count == 0) {
        *out_mean = 0.0f;
        return TE_OK;
    }

    *out_mean = ch->running_sum / (float)ch->count;
    return TE_OK;
}

te_status_t te_reset(telemetry_engine_t *engine) {
    if (!te_is_valid(engine)) return TE_ERR_INVALID_ARG;
    memset(engine->channels, 0, engine->channel_count * sizeof(channel_state_t));
    engine->total_samples_processed = 0;
    return TE_OK;
}
```
```cpp
/* telemetry_engine.cpp — прихована реалізація PIMPL */
#include "telemetry_engine.hpp"
#include <vector>
#include <numeric>
#include <array>

struct ChannelData {
    static constexpr size_t kCapacity = 64;
    std::array<float, kCapacity> ring{};
    size_t head{0};
    size_t count{0};
    double sum{0.0};

    void push(float val) noexcept {
        if (count == kCapacity) {
            sum -= ring[head];
        } else {
            ++count;
        }
        ring[head] = val;
        sum += val;
        head = (head + 1) % kCapacity;
    }

    [[nodiscard]] float mean() const noexcept {
        return count == 0 ? 0.0f : static_cast<float>(sum / count);
    }

    void reset() noexcept {
        ring.fill(0.0f);
        head = count = 0;
        sum = 0.0;
    }
};

struct TelemetryEngine::Impl {
    uint32_t rate_hz;
    std::vector<ChannelData> channels;

    explicit Impl(const TelemetryConfig &cfg)
        : rate_hz(cfg.sample_rate_hz), channels(cfg.max_channels) {}
};

TelemetryEngine::TelemetryEngine(const TelemetryConfig &config)
    : pimpl_(std::make_unique<Impl>(config)) {}

TelemetryEngine::~TelemetryEngine() = default;
TelemetryEngine::TelemetryEngine(TelemetryEngine &&) noexcept = default;
TelemetryEngine &TelemetryEngine::operator=(TelemetryEngine &&) noexcept = default;

std::expected<void, TelemetryError> 
TelemetryEngine::push_sample(uint16_t channel_id, float value) noexcept {
    if (!pimpl_ || channel_id >= pimpl_->channels.size()) {
        return std::unexpected(TelemetryError::InvalidArg);
    }
    pimpl_->channels[channel_id].push(value);
    return {};
}

std::expected<float, TelemetryError> 
TelemetryEngine::get_channel_mean(uint16_t channel_id) const noexcept {
    if (!pimpl_ || channel_id >= pimpl_->channels.size()) {
        return std::unexpected(TelemetryError::InvalidArg);
    }
    return pimpl_->channels[channel_id].mean();
}

void TelemetryEngine::reset() noexcept {
    if (!pimpl_) return;
    for (auto &ch : pimpl_->channels) {
        ch.reset();
    }
}
```
:::

---

## Матриця стабільності ABI та компіляційний бар'єр

Застосування непрозорих типів забезпечує довготривалу бінарну стабільність інтерфейсу прикладного двійкового рівня (ABI — англ. *Application Binary Interface*). 

Таблиця нижче демонструє, як різні класи внутрішніх змін впливають на клієнтський код і процес компіляції:

| Характер зміни у внутрішньому коді | Вплив на бінарний ABI | Чи потрібна перекомпіляція клієнта? | Технічний механізм |
| :--- | :--- | :--- | :--- |
| Додавання нового приватного поля у структуру | **Відсутній** | **Ні** | Розмір структури виділяється всередині `te_create`, зміщення полів клієнту невідомі |
| Зміна розміру внутрішніх буферів чи масивів | **Відсутній** | **Ні** | Константи буферів ізольовані у файлі реалізації |
| Заміна алгоритму (наприклад, ковзного середнього на фільтр Калмана) | **Відсутній** | **Ні** | Поведінковий контракт операцій залишається незмінним |
| Додавання нової функції до заголовного файлу | **Відсутній** | Лише для клієнтів, що кличуть нову функцію | Старі бінарні файли продовжують працювати без перескладання |
| Зміна сигнатури існуючої функції (типи параметрів) | **Критичний** | **ТАК** | Зміна правил передачі параметрів через регістри або стек |
| Зміна семантики поверненого значення | **Критичний** | **ТАК** | Порушення логічного контракту обробки помилок |

---

## Варіації реалізації для систем без динамічної пам'яті

У жорстких системах реального часу та вбудованих мікроконтролерах (Bare-Metal або MISRA C) динамічне виділення пам'яті через `malloc` або `new` часто суворо заборонене через ризик фрагментації купи та непередбачуваний час виконання.

У таких умовах патерн непрозорого покажчика адаптують через статичний пул екземплярів, що живе у секції BSS модуля:

:::tabs
```c
/* telemetry_static_pool.c — виділення без використання купи */
#include "telemetry_engine.h"

#define MAX_STATIC_ENGINES 4
#define STATIC_MAX_CHANNELS 8

static telemetry_engine_t g_engine_pool[MAX_STATIC_ENGINES];
static channel_state_t   g_channel_pool[MAX_STATIC_ENGINES][STATIC_MAX_CHANNELS];
static bool               g_engine_in_use[MAX_STATIC_ENGINES] = {false};

telemetry_engine_t* te_create(const te_config_t *config) {
    if (!config || config->max_channels > STATIC_MAX_CHANNELS) return NULL;

    for (size_t i = 0; i < MAX_STATIC_ENGINES; i++) {
        if (!g_engine_in_use[i]) {
            g_engine_in_use[i] = true;
            telemetry_engine_t *e = &g_engine_pool[i];
            e->sample_rate_hz = config->sample_rate_hz;
            e->channel_count = config->max_channels;
            e->total_samples_processed = 0;
            e->channels = g_channel_pool[i];
            memset(e->channels, 0, sizeof(channel_state_t) * config->max_channels);
            return e;
        }
    }
    return NULL; /* Пул переповнений */
}

void te_destroy(telemetry_engine_t *engine) {
    if (!engine) return;
    for (size_t i = 0; i < MAX_STATIC_ENGINES; i++) {
        if (&g_engine_pool[i] == engine) {
            g_engine_in_use[i] = false;
            return;
        }
    }
}
```
```cpp
/* telemetry_static_pool.cpp — статичний пул у C++ */
#include "telemetry_engine.hpp"
#include <array>
#include <vector>

namespace {
    constexpr size_t kMaxStaticEngines = 4;
    std::array<bool, kMaxStaticEngines> g_in_use{false};
}

class StaticTelemetryPool {
public:
    static std::unique_ptr<TelemetryEngine> acquire(const TelemetryConfig &cfg) {
        for (size_t i = 0; i < kMaxStaticEngines; ++i) {
            if (!g_in_use[i]) {
                g_in_use[i] = true;
                return std::make_unique<TelemetryEngine>(cfg);
            }
        }
        return nullptr;
    }
};
```
:::

Такий підхід повністю зберігає публічний контракт модуля `telemetry_engine.h`, гарантує приховування інформації та забезпечує детермінований час виконання операцій `O(1)` без звернення до системної купи.

---

## Порівняльний аналіз механізмів ізоляції в C та C++

У сучасній розробці інженер може обрати один із кількох способів побудови межі приховування інформації. Вибір залежить від вимог до динамічного поліморфізму, швидкості виконання та сумісності з мовою C:

1. **Неповна структура (C Incomplete Struct):** Найпростіший та найефективніший механізм для системних бібліотек. Не потребує віртуальних таблиць методів (vtable), забезпечує повну сумісність із сирим C ABI та легко обгортається в інтерфейси інших мов програмування (FFI у Rust, Python, Go).
2. **PIMPL (C++ Pointer to Implementation):** Класичний патерн для багатих C++ бібліотек із підтримкою RAII. Повністю приховує внутрішні `#include` із заголовка, автоматично керує викликом деструкторів, але вимагає додаткового виділення пам'яті для об'єкта реалізації та розіменування розумного покажчика.
3. **Чисті абстрактні інтерфейси (Pure Abstract Interfaces):** Використання структури з суто віртуальними методами (`struct ITelemetryEngine`). Дозволяє підміняти реалізацію під час виконання (наприклад, для юніт-тестування або моків), проте вносить накладні витрати на непрямі виклики через vtable та ускладнює керування бінарною сумісністю між різними версіями компіляторів.

---

## Типові помилки та пастки при роботі з дескрипторами

1. **Невідповідність алокаторів пам'яті (Cross-CRT Allocations):** У середовищі Windows динамічна бібліотека (`.dll`) та додаток, що її викликає, можуть використовувати різні версії бібліотеки часу виконання C (C Runtime / CRT). Якщо пам'ять під дескриптор виділена через `malloc` всередині DLL, а клієнтський код спробує звільнити її через власний `free()`, програма зазнає аварійного завершення. Саме тому модуль з Opaque Pointer **зобов'язаний** надавати власну парну функцію знищення `te_destroy()`, яка викликає `free()` у тому самому адресному контексті CRT.
2. **Використання після звільнення (Use-After-Free):** Якщо клієнт викликав `te_destroy(engine)`, але зберіг покажчик і згодом передав його у `te_push_sample`, модуль спробує прочитати звільнену пам'ять. Для захисту від таких помилок рекомендується обнуляти покажчик клієнта після звільнення або використовувати внутрішні «магічні числа» (magic numbers) у повному визначенні структури, які зануляються перед викликом `free()` та перевіряються assert-ом у кожній публічній функції.
3. **Втрата інлайнінгу (Inlining Penalty):** Оскільки тіло функції невидиме клієнту на етапі компіляції, компілятор генерує повноцінну інструкцію виклику `call` замість прямого звернення до пам'яті. У критичних до продуктивності шляхах (наприклад, обробка мільйонів пакетів за секунду) це вирішується або групуванням викликів у пакети (batch processing), або увімкненням оптимізації LTO (Link-Time Optimization) у системі збирання.
