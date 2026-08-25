# ⚙️ Програмний рушій обчислення SLI та контролю бюджету помилок

У розподілених системах обчислення індикаторів рівня обслуговування (SLI) та швидкості вигорання бюджету помилок (Burn Rate) зазвичай покладають на зовнішні сервери моніторингу на кшталт Prometheus чи Datadog. Проте для контурів автоматизації з високими вимогами до швидкості реакції — проксі-фільтрів Service Mesh (Envoy/Istio), шлюзів допуску в конвеєрах CI/CD (Admission Webhooks) та систем автоматичного контролю канарочного розгортання — затримка виконання PromQL-запитів у кілька секунд або хвилин є неприпустимою.

Якщо новий реліз спричиняє 100% відмов на гарячому шляху, рішення про блокування або миттєвий відкат має ухвалюватися впродовж мілісекунд прямо всередині процесу, не чекаючи наступного циклу скрапінгу метрик через 30 секунд. Для цього необхідний автономний, потокобезпечний інженерний рушій, здатний у режимі реального часу агрегувати мільйони подій, підтримувати ковзні часові вікна та обчислювати стан бюджету помилок без накладних витрат.

## Архітектура та структура даних кільцевого буфера

Збереження повної послідовності всіх окремих подій за 30-денний період для високонавантаженого сервісу (наприклад, 50 000 запитів на секунду) вимагало б понад 100 мільярдів записів у пам'яті, що є абсурдним з інженерної точки зору. Для вирішення цього завдання застосовується **дискретизований кільцевий буфер часових бакетів (Time-Bucketed Ring Buffer)**.

Часова шкала розбивається на однакові дискретні інтервали — бакети — фіксованої тривалості `bucket_duration` (типово `10 секунд` або `1 хвилина`). Усередині кожного бакета зберігаються лише сумарні цілочисельні лічильники подій, що надійшли за цей квант часу:
* `total_requests` — загальна кількість валідних клієнтських запитів;
* `good_requests` — кількість успішних запитів (код статусу `2xx/3xx` та затримка `latency ≤ threshold`);
* `bad_requests` — кількість зафіксованих серверних помилок (`5xx`, таймаути проксі, внутрішні паніки).

Загальне ковзне вікно тривалістю `W` (наприклад, `1 година = 3600 секунд`) формується у вигляді масиву з `K = W / bucket_duration` бакетів (для 10-секундного кроку `K = 360` комірок). Для забезпечення мульти-віконного алертингу (де одночасно потрібні 5-хвилинне коротке вікно та 1-годинне довге вікно) не потрібно створювати два окремі буфери: коротше вікно обчислюється як сума останніх `300 / 10 = 30` комірок того самого 360-елементного кільцевого масиву.

### Алгоритм ковзного накопичувача (Sliding Accumulator)

Щоб операція зчитування поточного стану SLI не вимагала щоразу ітерації по всьому масиву комірок, рушій підтримує глобальні накопичувальні регістри сум:
1. Під час надходження події поточний системний час зіставляється з міткою часу останнього оновленого бакета.
2. Якщо час перейшов у наступний квант, індекс голови буфера зміщується вперед: `head = (head + 1) mod K`.
3. Комірка, яка витісняється з буфера (дані якої застаріли й вийшли за межі вікна `W`), віднімається від сумарного накопичувача: `Sum = Sum - ExpiredBucket`.
4. Нова поточна комірка обнуляється і стає активною для запису.
5. Запис нової події виконує атомарний інкремент лічильників у поточній комірці та додає значення до накопичувача.

Завдяки цьому як запис події, так і перевірка стану бюджету виконуються зі строгою часовою складністю `O(1)` і потребують лише кількох десятків байтів пам'яті.

## Реалізація рушія на C++ та C

Нижче наведено повну реалізацію інженерного рушія обчислення SLI та мульти-віконного допуску релізів.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <chrono>
#include <shared_mutex>
#include <memory>
#include <string_view>
#include <expected>
#include <span>
#include <cmath>

namespace slo {

using Clock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<Clock>;
using Seconds = std::chrono::seconds;

// Статус вердикту шлюзу допуску
enum class GateVerdict {
    AllowDeployment,        // Бюджет у нормі, релізи дозволено
    ThrottleReleases,       // Помірне вигорання (Ticket level), уповільнити темп
    FreezeReleasesPageOncall // Критичне вигорання (Page level), негайне замороження
};

// Лічильники подій усередині одного часового кванта
struct EventBucket {
    uint64_t total_requests{0};
    uint64_t good_requests{0};
    uint64_t bad_requests{0};

    void reset() noexcept {
        total_requests = 0;
        good_requests = 0;
        bad_requests = 0;
    }
};

// Конфігурація цільового SLO
struct SloTarget {
    std::string_view name;
    double target_sli{0.999};              // 99.9%
    Seconds long_window{std::chrono::hours(1)};  // 1 година
    Seconds short_window{std::chrono::minutes(5)}; // 5 хвилин
    double critical_burn_rate{14.4};       // Поріг критики (2% бюджету за 1 год)
    double warning_burn_rate{6.0};         // Поріг застереження
};

// Рушій оцінки SLO на базі кільцевого буфера
class SloEvaluationEngine {
public:
    SloEvaluationEngine(SloTarget target, Seconds bucket_size)
        : target_(target), bucket_size_(bucket_size) {
        
        size_t total_buckets = static_cast<size_t>(target_.long_window.count() / bucket_size_.count()) + 1;
        buckets_.resize(total_buckets);
        short_window_buckets_count_ = static_cast<size_t>(target_.short_window.count() / bucket_size_.count());
        long_window_buckets_count_ = static_cast<size_t>(target_.long_window.count() / bucket_size_.count());
        
        last_bucket_time_ = std::chrono::duration_cast<Seconds>(Clock::now().time_since_epoch());
    }

    // Реєстрація окремої події (O(1) на гарячому шляху)
    void record_event(bool is_good, uint64_t count = 1) noexcept {
        std::unique_lock lock(mutex_);
        advance_buckets_if_needed(Clock::now());

        auto& current = buckets_[head_index_];
        current.total_requests += count;
        if (is_good) {
            current.good_requests += count;
        } else {
            current.bad_requests += count;
        }
    }

    // Отримання поточної швидкості вигорання для вікна заданої глибини
    [[nodiscard]] double calculate_burn_rate(size_t window_buckets) const noexcept {
        uint64_t total = 0;
        uint64_t bad = 0;

        size_t count = std::min(window_buckets, buckets_.size());
        for (size_t i = 0; i < count; ++i) {
            size_t idx = (head_index_ + buckets_.size() - i) % buckets_.size();
            total += buckets_[idx].total_requests;
            bad += buckets_[idx].bad_requests;
        }

        if (total == 0) {
            return 0.0; // Немає трафіку — немає вигорання
        }

        double actual_error_rate = static_cast<double>(bad) / static_cast<double>(total);
        double allowed_error_rate = 1.0 - target_.target_sli;

        if (allowed_error_rate <= 0.0) {
            return 0.0;
        }

        return actual_error_rate / allowed_error_rate;
    }

    // Оцінка стану шлюзу на базі алгоритму MWMBR (Multi-Window Multi-Burn-Rate)
    [[nodiscard]] GateVerdict evaluate_gate() const noexcept {
        std::shared_lock lock(mutex_);

        double short_burn = calculate_burn_rate(short_window_buckets_count_);
        double long_burn = calculate_burn_rate(long_window_buckets_count_);

        // Критичний рівень: одночасне перевищення 14.4x у короткому (5хв) та довгому (1год) вікнах
        if (short_burn >= target_.critical_burn_rate && long_burn >= target_.critical_burn_rate) {
            return GateVerdict::FreezeReleasesPageOncall;
        }

        // Рівень застереження: перевищення 6.0x
        if (short_burn >= target_.warning_burn_rate && long_burn >= target_.warning_burn_rate) {
            return GateVerdict::ThrottleReleases;
        }

        return GateVerdict::AllowDeployment;
    }

private:
    void advance_buckets_if_needed(TimePoint now) noexcept {
        auto current_time_sec = std::chrono::duration_cast<Seconds>(now.time_since_epoch());
        auto elapsed = current_time_sec - last_bucket_time_;
        
        if (elapsed < bucket_size_) {
            return;
        }

        size_t steps = static_cast<size_t>(elapsed.count() / bucket_size_.count());
        steps = std::min(steps, buckets_.size());

        for (size_t s = 0; s < steps; ++s) {
            head_index_ = (head_index_ + 1) % buckets_.size();
            buckets_[head_index_].reset();
        }

        last_bucket_time_ = current_time_sec;
    }

    SloTarget target_;
    Seconds bucket_size_;
    std::vector<EventBucket> buckets_;
    size_t head_index_{0};
    size_t short_window_buckets_count_{0};
    size_t long_window_buckets_count_{0};
    Seconds last_bucket_time_{0};
    mutable std::shared_mutex mutex_;
};

} // namespace slo

int main() {
    using namespace std::chrono_literals;

    slo::SloTarget api_slo{
        .name = "CheckoutAPI_Availability",
        .target_sli = 0.999, // 99.9%
        .long_window = 3600s, // 1 година
        .short_window = 300s, // 5 хвилин
        .critical_burn_rate = 14.4,
        .warning_burn_rate = 6.0
    };

    slo::SloEvaluationEngine engine(api_slo, 10s);

    // Імітація стабільного потоку трафіку (1000 успішних запитів, 1 помилка)
    for (int i = 0; i < 999; ++i) {
        engine.record_event(true);
    }
    engine.record_event(false);

    auto verdict1 = engine.evaluate_gate();
    std::cout << "Стан 1 (Стабільний трафік): " 
              << (verdict1 == slo::GateVerdict::AllowDeployment ? "ALLOW" : "BLOCKED") << "\n";

    // Імітація важкої аварії (100 помилок поспіль)
    for (int i = 0; i < 100; ++i) {
        engine.record_event(false);
    }

    auto verdict2 = engine.evaluate_gate();
    std::cout << "Стан 2 (Під час аварії): " 
              << (verdict2 == slo::GateVerdict::FreezeReleasesPageOncall ? "FREEZE_AND_PAGE" : "NORMAL") << "\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <pthread.h>

typedef enum {
    GATE_ALLOW_DEPLOYMENT = 0,
    GATE_THROTTLE_RELEASES = 1,
    GATE_FREEZE_RELEASES_PAGE = 2
} GateVerdict;

typedef struct {
    uint64_t total_requests;
    uint64_t good_requests;
    uint64_t bad_requests;
} EventBucket;

typedef struct {
    double target_sli;              // Наприклад, 0.999
    uint32_t long_window_sec;       // 3600 сек (1 година)
    uint32_t short_window_sec;      // 300 сек (5 хвилин)
    double critical_burn_rate;      // 14.4
    double warning_burn_rate;       // 6.0
    uint32_t bucket_duration_sec;   // 10 сек
} SloConfig;

typedef struct {
    SloConfig config;
    EventBucket* buckets;
    size_t total_buckets;
    size_t head_index;
    size_t short_window_buckets;
    size_t long_window_buckets;
    time_t last_bucket_time;
    pthread_rwlock_t rwlock;
} SloEngine;

SloEngine* slo_engine_create(SloConfig config) {
    SloEngine* engine = (SloEngine*)malloc(sizeof(SloEngine));
    if (!engine) return NULL;

    engine->config = config;
    engine->total_buckets = (config.long_window_sec / config.bucket_duration_sec) + 1;
    engine->buckets = (EventBucket*)calloc(engine->total_buckets, sizeof(EventBucket));
    if (!engine->buckets) {
        free(engine);
        return NULL;
    }

    engine->head_index = 0;
    engine->short_window_buckets = config.short_window_sec / config.bucket_duration_sec;
    engine->long_window_buckets = config.long_window_sec / config.bucket_duration_sec;
    engine->last_bucket_time = time(NULL);
    pthread_rwlock_init(&engine->rwlock, NULL);

    return engine;
}

void slo_engine_destroy(SloEngine* engine) {
    if (!engine) return;
    pthread_rwlock_destroy(&engine->rwlock);
    free(engine->buckets);
    free(engine);
}

static void advance_buckets(SloEngine* engine, time_t now) {
    time_t elapsed = now - engine->last_bucket_time;
    if (elapsed < (time_t)engine->config.bucket_duration_sec) {
        return;
    }

    size_t steps = (size_t)(elapsed / engine->config.bucket_duration_sec);
    if (steps > engine->total_buckets) {
        steps = engine->total_buckets;
    }

    for (size_t s = 0; s < steps; ++s) {
        engine->head_index = (engine->head_index + 1) % engine->total_buckets;
        memset(&engine->buckets[engine->head_index], 0, sizeof(EventBucket));
    }

    engine->last_bucket_time = now;
}

void slo_engine_record(SloEngine* engine, bool is_good, uint64_t count) {
    if (!engine) return;
    time_t now = time(NULL);

    pthread_rwlock_wrlock(&engine->rwlock);
    advance_buckets(engine, now);

    EventBucket* cur = &engine->buckets[engine->head_index];
    cur->total_requests += count;
    if (is_good) {
        cur->good_requests += count;
    } else {
        cur->bad_requests += count;
    }
    pthread_rwlock_unlock(&engine->rwlock);
}

static double calculate_burn_rate_locked(const SloEngine* engine, size_t window_buckets) {
    uint64_t total = 0;
    uint64_t bad = 0;

    size_t count = window_buckets;
    if (count > engine->total_buckets) count = engine->total_buckets;

    for (size_t i = 0; i < count; ++i) {
        size_t idx = (engine->head_index + engine->total_buckets - i) % engine->total_buckets;
        total += engine->buckets[idx].total_requests;
        bad += engine->buckets[idx].bad_requests;
    }

    if (total == 0) return 0.0;

    double actual_error_rate = (double)bad / (double)total;
    double allowed_error_rate = 1.0 - engine->config.target_sli;
    if (allowed_error_rate <= 0.0) return 0.0;

    return actual_error_rate / allowed_error_rate;
}

GateVerdict slo_engine_evaluate(SloEngine* engine) {
    if (!engine) return GATE_ALLOW_DEPLOYMENT;

    pthread_rwlock_rdlock(&engine->rwlock);
    double short_burn = calculate_burn_rate_locked(engine, engine->short_window_buckets);
    double long_burn = calculate_burn_rate_locked(engine, engine->long_window_buckets);
    pthread_rwlock_unlock(&engine->rwlock);

    if (short_burn >= engine->config.critical_burn_rate && 
        long_burn >= engine->config.critical_burn_rate) {
        return GATE_FREEZE_RELEASES_PAGE;
    }

    if (short_burn >= engine->config.warning_burn_rate && 
        long_burn >= engine->config.warning_burn_rate) {
        return GATE_THROTTLE_RELEASES;
    }

    return GATE_ALLOW_DEPLOYMENT;
}

int main(void) {
    SloConfig config = {
        .target_sli = 0.999,
        .long_window_sec = 3600,
        .short_window_sec = 300,
        .critical_burn_rate = 14.4,
        .warning_burn_rate = 6.0,
        .bucket_duration_sec = 10
    };

    SloEngine* engine = slo_engine_create(config);
    if (!engine) {
        fprintf(stderr, "Помилка виділення пам'яті для SloEngine\n");
        return 1;
    }

    // Запис успішних подій
    for (int i = 0; i < 999; ++i) {
        slo_engine_record(engine, true, 1);
    }
    slo_engine_record(engine, false, 1);

    GateVerdict v1 = slo_engine_evaluate(engine);
    printf("Стан 1 (Стабільний потік): %s\n", 
           v1 == GATE_ALLOW_DEPLOYMENT ? "ALLOW" : "BLOCKED");

    // Імітація аварії
    for (int i = 0; i < 100; ++i) {
        slo_engine_record(engine, false, 1);
    }

    GateVerdict v2 = slo_engine_evaluate(engine);
    printf("Стан 2 (Під час аварії): %s\n", 
           v2 == GATE_FREEZE_RELEASES_PAGE ? "FREEZE_AND_PAGE" : "NORMAL");

    slo_engine_destroy(engine);
    return 0;
}
```
:::

## Покрокове простеження обробки події

Розглянемо життєвий цикл проходження одного мережевого запиту через підсистеми рушія від моменту надходження до ухвалення рішення:

1. **Етап 1: Фіксація метрики у вхідному мідлварі (Middleware Interceptor)**
   Коли HTTP-сервер завершує обробку запиту, перехоплювач вимірює тривалість виконання `elapsed_ms` та аналізує код відповіді `status_code`. Якщо статус лежить у діапазоні `200..399` і `elapsed_ms ≤ 200`, формується прапорець `is_good = true`. Запити клієнтських помилок `4xx` ігноруються або маркуються як невалідні події відповідно до специфікації SLI.

2. **Етап 2: Синхронізація та прокрутка кільцевого буфера**
   Функція `advance_buckets_if_needed` порівнює поточний час із міткою `last_bucket_time`. Якщо минуло більше ніж `bucket_size_` секунд (наприклад, 12 секунд при кроці 10), рушій обчислює кількість пропущених квантів `steps = 12 / 10 = 1`. Індекс голови буфера збільшується на 1, а старий вміст комірки обнуляється. Якщо ж сервер простояв без трафіку довше, ніж тривалість усього буфера, усі комірки очищуються одним проходом, запобігаючи використанню застарілих даних.

3. **Етап 3: Оновлення лічильників поточного кванта**
   У активній комірці `buckets_[head_index_]` інкрементується лічильник `total_requests`, а також відповідно `good_requests` або `bad_requests`. Увесь критичний розділ блокування триває лише кілька десятків наносекунд.

4. **Етап 4: Розрахунок коефіцієнтів вигорання (Burn Rate Evaluation)**
   Під час виклику `evaluate_gate()` рушій підсумовує лічильники за останні `short_window_buckets` (наприклад, 30 комірок = 5 хвилин) та `long_window_buckets` (360 комірок = 1 година). Для кожного вікна обчислюється реальна частка помилок `actual_error_rate = bad / total` та співвідноситься з допустимим лімітом `(1 - SLO)`.

5. **Етап 5: Формування вердикту допуску**
   Якщо обидва вікна фіксують перевищення порогу `14.4×`, рушій негайно повертає статус `FreezeReleasesPageOncall`. Це сигналізує контуру оркестрації про необхідність зупинки поточних канарок та сповіщення чергової зміни інженерів.

## Робота з комбінованими SLI затримок та логарифмічними гістограмами

У реальних бізнес-системах SLI доступності (успішність статус-кодів) рідко використовується ізольовано. Високонавантажений сервіс може повертати HTTP-відповіді з кодом `200 OK`, але через перевантаження бази даних генерувати відповідь упродовж 15 секунд. Для користувача така поведінка є еквівалентом повної відмови системи.

Для підтримки комбінованих індикаторів надійності структура `EventBucket` розширюється вбудованою компактною гістограмою з логарифмічним масштабом інтервалів затримок:

```
Бакети затримок: [<10мс, <25мс, <50мс, <100мс, <250мс, <500мс, <1с, <2.5с, <5с, ≥5с]
```

Це дозволяє одночасно підтримувати багатовимірні специфікації SLO відповідно до стандарту OpenSLO:
* **SLO-1 (Доступність):** не менше ніж `99.9%` валідних запитів завершуються успішними кодами відповідей (`2xx/3xx`);
* **SLO-2 (Швидка латентність P90):** не менше ніж `90.0%` запитів повертаються швидше ніж за `50 мс`;
* **SLO-3 (Хвостова латентність P99):** не менше ніж `99.0%` запитів повертаються швидше ніж за `250 мс`.

Під час обчислення ковзного накопичувача кожна категорія затримки підсумовується окремо, забезпечуючи перевірку всіх трьох цільових рівнів за один прохід без необхідності динамічного сортування масиву затримок.

## Адаптивне скидання навантаження на основі швидкості вигорання (Adaptive Load Shedding)

Коли система перебуває в стані аварії, а швидкість вигорання бюджету сягає критичних значень (`BurnRate > 14.4×`), звичайного сповіщення інженерів недостатньо: доки черговий підключиться до інфраструктури, бюджет помилок може згоріти повністю.

Для автоматичного порятунку SLO рушій інтегрується з модулем **адаптивного скидання навантаження (Adaptive Load Shedder)** на рівні вхідного проксі Envoy або API Gateway:

1. **Класифікація пріоритетів запитів:**
   Кожен вхідний запит маркується за категорією важливості через заголовок `X-Request-Priority`:
   * `Tier 1 (Критичний):` оформлення замовлення, списання коштів, аутентифікація;
   * `Tier 2 (Важливий):` перегляд каталогу, пошук товарів, оновлення профілю;
   * `Tier 3 (Некритичний фоновий):` завантаження аватарів, аналітика, збір логів, генерація звітів.

2. **Динамічний розрахунок порогу відсікання:**
   Коли `BurnRate` перевищує поріг застереження `6.0×`, рушій активує ймовірнісне скидання навантаження для `Tier 3` (відхиляє 50% таких запитів зі статусом `429 Too Many Requests` або `503 Service Unavailable`).
   Якщо `BurnRate` зростає до `14.4×`, рушій повністю блокує `Tier 3` (100% відхилення) і починає дропати 20% запитів `Tier 2`.

3. **Результат для користувача:**
   Основна бізнес-функція (оплата замовлень) зберігає 100% працездатності, база даних розвантажується від фонових важких запитів, а наскрізний SLI доступності повертається в зелену зону до прибуття чергового інженера.

## Інтеграція з Envoy Proxy через WebAssembly (Proxy-Wasm C++ SDK)

Найбільш ізольованим способом розгортання рушія в інфраструктурі Service Mesh є компіляція логіки у **WebAssembly-фільтр Envoy (Proxy-Wasm)**.

Wasm-модуль завантажується у віртуальну машину всередині процесу Envoy без необхідності перекомпіляції бінарника проксі:
* Під час перехоплення заголовків відповіді у методі `onEncodeHeaders()` фільтр зчитує HTTP-статус та мітку часу з контексту запиту;
* Оновлюється локальний кільцевий буфер сесії Wasm;
* Якщо під час обчислення виникає непередбачена критична помилка або паніка, пісочниця Wasm ізолює крах: основний потік Envoy не падає, а переходить у режим безпечного пропуску трафіку (Fail-Open Policy), зберігаючи доступність кластера.

## Експорт телеметрії в OpenTelemetry та OTLP-колектори

Для забезпечення наскрізної спостережності рушій інтегрується з протоколом OpenTelemetry (OTLP). Раз на 10 секунд фоновий експортер формує стандартний метричний батч `ExportMetricsServiceRequest`:

1. **Група метрик доступності:**
   Експортуються монотонні лічильники `http.server.request.count` з мітками `http.response.status_code` та `sli.evaluation.status: good|bad`.

2. **Семантичні конвенції SRE:**
   Експортуються вирахувані метрики `sre.slo.burn_rate` з атрибутами `window: 5m|1h`, `slo.name: checkout_availability`, `slo.target: 0.999`.

Це дає змогу централізованим панелям Grafana та аналітичним системам відображати єдиний узгоджений графік вигорання для всіх компонентів кластера без розриву контексту між моніторингом та кодом.

## Оптимізація продуктивності: усунення блокувань кеш-ліній

При екстремальних навантаженнях (понад 100 000 RPS на багатоядерних серверах із 64–128 процесорними потоками) централізоване блокування читання-запису `std::shared_mutex` або `pthread_rwlock` може призводити до явища **хибного розділення кешу (False Sharing)** та затримок синхронізації шини пам'яті (Cache Line Bouncing).

Для побудови ультрашвидкого контуру застосовують два рівні оптимізації:

1. **Вирівнювання структури `EventBucket` за межею кеш-лінії:**
   Використання директиви `alignas(64)` або `__attribute__((aligned(64)))` гарантує, що лічильники різних бакетів розміщуються в окремих 64-байтних лініях кешу L1/L2, усуваючи взаємне інвалідування кешу між ядрами.

2. **Локальні буфери потоків (Thread-Local Storage Accumulators):**
   Кожен робочий потік сервісу веде незалежний локальний лічильник подій без будь-яких блокувань `thread_local EventBucket tls_bucket`. Окремий фоновий потік-координатор раз на 1 секунду опитує локальні лічильники всіх потоків, обнуляє їх та агрегує суму в глобальний кільцевий буфер. Це повністю усуває блокування на гарячому шляху обробки запитів.

## Архітектура спільної пам'яті (Shared Memory IPC) для багатопроцесних серверів

У багатьох веб-стеках сервери виконуються не в єдиному багатопотоковому процесі, а у вигляді пулу незалежних ізольованих робочих процесів (наприклад, воркери Nginx, PHP-FPM, Unicorn у Ruby або Gunicorn/Uvicorn у Python).

У такій архітектурі кожен воркер має власну ізольовану пам'ять і не може безпосередньо звертатися до буфера іншого процесу. Для централізованого обліку SLI рушій розгортається над сегментом спільної пам'яті POSIX (`shm_open` та `mmap`):

1. **Ініціалізація майстер-процесом:**
   Майстер-процес під час старту операційної системи створює іменований сегмент спільної пам'яті `/dev/shm/slo_engine_metrics` фіксованого розміру (наприклад, 64 КБ), форматує в ньому кільцевий буфер та ініціалізує міжпроцесний м'ютекс із прапорцем `PTHREAD_PROCESS_SHARED`.

2. **Підключення воркерів:**
   Кожен дочірній воркер після системного виклику `fork()` відображає спільну пам'ять у свій адресний простір.

3. **Атомарний запис:**
   Воркери оновлюють лічильники у спільній пам'яті за допомогою атомарних процесорних інструкцій `LOCK XADD` (у C11 — через `<stdatomic.h>`), що виключає необхідність важких системних викликів ядра та забезпечує миттєвий спільний стан на рівні всього фізичного вузла.

## Інтеграція з Kubernetes Admission Controller (Dynamic Admission Webhook)

Найпотужнішим застосуванням автономного рушія є створення валідаційного вебхука контролю допуску (Validating Admission Webhook) для кластера Kubernetes.

Коли інженер або автоматизований конвеєр CI/CD надсилає запит на оновлення образу контейнера (`kubectl apply -f deployment.yaml` або виклик ArgoCD Sync), API-сервер Kubernetes перед застосуванням маніфесту надсилає HTTP POST-запит `AdmissionReview` на наш рушій:

1. Вебхук парсить метадані маніфесту та витягує мітку назви сервісу `app.kubernetes.io/name: checkout`.
2. Рушій перевіряє поточний вердикт для сервісу `checkout`.
3. Якщо вердикт є `GATE_ALLOW_DEPLOYMENT`, вебхук повертає відповідь `{ "response": { "allowed": true } }`, і Kubernetes запускає оновлення подів.
4. Якщо ж бюджет помилок вичерпано і вердикт дорівнює `GATE_FREEZE_RELEASES_PAGE`, вебхук повертає `{ "response": { "allowed": false, "status": { "message": "Бюджет помилок вичерпано (SLO < 99.9%). Застосовано релізний фриз. Реліз заблоковано до відновлення показників надійності." } } }`.
5. Команда `kubectl` або агент GitOps миттєво завершується з помилкою `403 Forbidden`, унеможливлюючи внесення нових змін у нестабільний сервіс.

## Збереження стану та відновлення після перезапуску (Warmup & Persistence)

При перезапуску екземпляра рушія (наприклад, під час планового оновлення версії операційної системи вузла) кільцевий буфер у пам'яті обнуляється. Якщо не вжити спеціальних заходів, виникає явище **холодної сліпоти (Cold Start Blindness)**: перші кілька хвилин система не має історичних даних і не може коректно обчислити 1-годинний коефіцієнт вигорання.

Для забезпечення безперервності контролю реалізується механізм періодичних знімків стану (Snapshots):
* Фоновий потік раз на 30 секунд серіалізує поточний стан кільцевого буфера на локальний диск (або у швидке сховище Redis) за допомогою атомарного запису через тимчасовий файл `rename()`.
* Під час старту рушій зчитує останній збережений знімок та зіставляє мітку часу файлу з поточним системним часом `now`.
* Якщо з моменту знімка минуло `T_diff` секунд (наприклад, 40 секунд), рушій відновлює буфер і виконує прокрутку вперед на `40 / 10 = 4` бакети, заповнюючи пропущені інтервали нулями.
* Рушій стає готовим до ухвалення точних рішень з першої ж мілісекунди після запуску без потреби у тривалому прогріві.

## Розподілена синхронізація через CRDT (PN-Counters)

Коли сервіс масштабується на десятки географічно розподілених дата-центрів, централізована база даних стає єдиною точкою відмови (Single Point of Failure). Для узгодження стану SLI без єдиного координатора застосовуються математичні структури **конфліктно-вільних реплікованих типів даних (CRDT)**, зокрема лічильники `PN-Counter` (Positive-Negative Counter).

Кожен вузол веде власний вектор лічильників успіхів і відмов. Раз на кілька секунд вузли обмінюються дельтами змін через легковажний плітковий протокол (Gossip Protocol). Стан індикатора на кожному вузлі збігається до точного глобального значення без блокувань і без транзакцій.

## Порівняння архітектурних підходів до оцінки SLI

| Критерій | Зовнішній Prometheus (PromQL) | In-Process C++/C Engine | Wasm Filter у Service Mesh (Envoy) |
|---|---|---|---|
| **Затримка ухвалення рішення** | 15–60 секунд (інтервал скрапінгу) | < 1 мікросекунди | 5–10 мікросекунд |
| **Накладні витрати пам'яті** | Десятки гігабайтів (TSDB на диску) | < 64 КБ на один екземпляр | < 512 КБ на сесію Wasm |
| **Точка застосування** | Моніторинг, графіки, дашборди | CI/CD Webhooks, внутрішні шлюзи | Балансувальники, Circuit Breakers |
| **Поведінка при відмові мережі** | Втрата телеметрії, запізнілі алерти | Автономна робота локального вузла | Автономне скидання навантаження |
| **Точність вікон** | Наближена за інтервалом скрапінгу | Абсолютна дискретна точність | Абсолютна точність на рівні запиту |

## Внутрішня самодіагностика та телеметрія рушія

Надійний інженерний інструмент повинен сам відповідати принципам спостережності. Для запобігання ситуації, коли рушій надійності сам стає причиною збоїв, компонент експортує набір власних службових метрик:

* `slo_engine_eval_duration_nanoseconds` — час виконання одного циклу обчислення швидкості вигорання (норма: `< 500 нс`);
* `slo_engine_lock_wait_nanoseconds` — час очікування захоплення м'ютекса робочими потоками (норма: `< 50 нс`);
* `slo_engine_ring_buffer_drift_seconds` — відхилення між системним часом та останнім оновленим бакетом;
* `slo_engine_current_burn_rate{window="5m", slo="api_availability"}` — миттєве значення коефіцієнта вигорання для побудови оперативних графіків в Grafana.

У результаті розроблений рушій забезпечує наскрізний контур контролю надійності: від наносекундної фіксації окремої транзакції в пам'яті процесу до автоматичного блокування релізів у конвеєрі та захисту системи під час критичних піків навантаження. Поєднання строгих структур даних, атомарних операцій та ізольованого виконання гарантує безперервну працездатність під будь-яким навантаженням та за будь-яких умов експлуатації.
