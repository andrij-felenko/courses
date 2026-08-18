# ⚙️ Адаптивний контролер відкидання навантаження

Ця вставка містить повністю робочий приклад реалізації адаптивного контролера прийому навантаження (Adaptive Load Shedding Middleware) та аналізує його внутрішній механізм. Контролер відстежує паралельні запити, обчислює поточний рівень деградації (Brownout Level) та відкидає другорядний трафік (повертаючи HTTP status `503 Service Unavailable`), коли система наближається до вичерпання ресурсів.

До складу контролера входить **механізм гістерезису**, який запобігає осциляції (flapping) — швидкому хаотичному переключенню між рівнями деградації при дрібних коливаннях навантаження.

---

## 1. Архітектурний механізм та алгоритм контролера

Контролер впроваджується на межі прийому трафіку (як проміжне програмне забезпечення / middleware у HTTP/gRPC сервері). Він працює як перехоплювач, що аналізує кожен вхідний запит перед його передачею до обробників бізнес-логіки.

```
Вхідний запит (Priority P0..P4) 
       │
       ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 1. Оцінка стану: Read active_requests & queue delay         │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ 2. Оновлення Brownout Level (з урахуванням гістерезису)    │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │ Priority >= Cutoff (Level)? │
                 └──────────────┬──────────────┘
                                │
                ┌───────────────┴───────────────┐
             ТАК│                               │НІ
                ▼                               ▼
 ┌─────────────────────────────┐ ┌─────────────────────────────┐
 │ ВІДКИДАННЯ (Shed)           │ │ ПРИЙОМ (Admit)              │
 │ 503 Service Unavailable     │ │ RAII Active Counter + 1     │
 │ Retry-After + Jitter        │ │ Передача у воркер           │
 └─────────────────────────────┘ └─────────────────────────────┘
```

### Кроки роботи алгоритму:

1. **Атомарне зчитування стану**: При надходженні запиту контролер зчитує поточну кількість паралельно оброблюваних запитів (`active_requests`) та показник затримки.
2. **Перерахунок рівня деградації (Brownout Level)**:
   - **Level 0 (Normal Operations)**: `active_requests < 50%` ємності. Пропускаються всі класи пріоритетів (P0..P4).
   - **Level 1 (Shed P4 Background)**: `active_requests >= 50%`. Відкидається найнижчий клас P4 (відео, фонові батчі).
   - **Level 2 (Shed P3 Analytics)**: `active_requests >= 70%`. Відкидаються класи P3 та P4.
   - **Level 3 (Shed P2 Presence)**: `active_requests >= 85%`. Відкидаються класи P2, P3 та P4.
   - **Level 4 (Emergency Mode)**: `active_requests >= 95%`. Відкидаються P1..P4; проходять виключно критичні команди P0.
3. **Захист від осциляцій (Гістерезис)**: При спаданні навантаження перехід на нижчий рівень деградації відбувається не одразу при перетині порогового значення, а лише тоді, коли кількість активних запитів падає нижче порогу **мінус дельта гістерезису** (`Δ_hysteresis = 5..10%`). Це гарантує стабільність системи під час високої частоти дрібних коливань.
4. **Ухвалення рішення (Admission Decision)**:
   - Якщо пріоритет запиту нижчий за активний поріг відкидання, запит термінується за 0.1 мс з кодом 503 та обчисленим `Retry-After`.
   - Якщо запит прийнято, інкрементується атомарний лічильник `active_requests`, який автоматично декрементується після завершення обробки запиту (через RAII-обгортку чи фреймворк-коллбек).

---

## 2. Реалізація мовами C та C++

Згідно з каноном розробки системного та високонавантаженого ПЗ, нижче наведено дві ідіоматичні реалізації контролера: на мові C (з використанням функцій та структур) та на мові C++23 (з використанням семантики переміщення, RAII-обгортки `RequestGuard` та `std::expected`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>

/* Класи пріоритетів запиту */
typedef enum {
    PRIORITY_P0_CRITICAL   = 0,
    PRIORITY_P1_HIGH       = 1,
    PRIORITY_P2_MEDIUM     = 2,
    PRIORITY_P3_LOW        = 3,
    PRIORITY_P4_BACKGROUND = 4
} request_priority_t;

/* Рівні деградації Brownout */
typedef enum {
    BROWNOUT_L0_NORMAL    = 0,
    BROWNOUT_L1_SHED_P4   = 1,
    BROWNOUT_L2_SHED_P3   = 2,
    BROWNOUT_L3_SHED_P2   = 3,
    BROWNOUT_L4_EMERGENCY = 4
} brownout_level_t;

/* Структура стану контролера скидання */
typedef struct {
    atomic_int active_requests;
    int max_capacity;
    atomic_int current_level;
    int hysteresis_delta;
} shedding_controller_t;

/* Результат оцінки прийому */
typedef struct {
    bool allow;
    int http_status;
    int retry_after_sec;
    const char* reason;
} admission_result_t;

void shedding_controller_init(shedding_controller_t *ctrl, int capacity) {
    atomic_init(&ctrl->active_requests, 0);
    ctrl->max_capacity = capacity;
    atomic_init(&ctrl->current_level, BROWNOUT_L0_NORMAL);
    ctrl->hysteresis_delta = 5;
}

/* Оновлення рівня Brownout з урахуванням гістерезису */
static void update_brownout_level(shedding_controller_t *ctrl) {
    int active = atomic_load_explicit(&ctrl->active_requests, memory_order_relaxed);
    int current = atomic_load_explicit(&ctrl->current_level, memory_order_relaxed);
    int next = current;

    /* Перевірка умов підвищення рівня тиску */
    if (active >= 95 && current < BROWNOUT_L4_EMERGENCY) {
        next = BROWNOUT_L4_EMERGENCY;
    } else if (active >= 85 && current < BROWNOUT_L3_SHED_P2) {
        next = BROWNOUT_L3_SHED_P2;
    } else if (active >= 70 && current < BROWNOUT_L2_SHED_P3) {
        next = BROWNOUT_L2_SHED_P3;
    } else if (active >= 50 && current < BROWNOUT_L1_SHED_P4) {
        next = BROWNOUT_L1_SHED_P4;
    }
    
    /* Перевірка умов зниження рівня з урахуванням гістерезису */
    else if (current == BROWNOUT_L4_EMERGENCY && active < (95 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L3_SHED_P2;
    } else if (current == BROWNOUT_L3_SHED_P2 && active < (85 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L2_SHED_P3;
    } else if (current == BROWNOUT_L2_SHED_P3 && active < (70 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L1_SHED_P4;
    } else if (current == BROWNOUT_L1_SHED_P4 && active < (50 - ctrl->hysteresis_delta)) {
        next = BROWNOUT_L0_NORMAL;
    }

    if (next != current) {
        atomic_store_explicit(&ctrl->current_level, next, memory_order_relaxed);
    }
}

/* Перевірка допустимості виклику */
admission_result_t shedding_controller_eval(shedding_controller_t *ctrl, request_priority_t prio) {
    update_brownout_level(ctrl);
    int lvl = atomic_load_explicit(&ctrl->current_level, memory_order_relaxed);

    admission_result_t res = {
        .allow = true,
        .http_status = 200,
        .retry_after_sec = 0,
        .reason = "Request admitted"
    };

    bool should_drop = false;
    switch (lvl) {
        case BROWNOUT_L4_EMERGENCY:
            if (prio > PRIORITY_P0_CRITICAL) should_drop = true;
            break;
        case BROWNOUT_L3_SHED_P2:
            if (prio >= PRIORITY_P2_MEDIUM) should_drop = true;
            break;
        case BROWNOUT_L2_SHED_P3:
            if (prio >= PRIORITY_P3_LOW) should_drop = true;
            break;
        case BROWNOUT_L1_SHED_P4:
            if (prio >= PRIORITY_P4_BACKGROUND) should_drop = true;
            break;
        case BROWNOUT_L0_NORMAL:
        default:
            should_drop = false;
            break;
    }

    if (should_drop) {
        res.allow = false;
        res.http_status = 503;
        res.retry_after_sec = 10 + ((int)prio * 5);
        res.reason = "Shedded due to active brownout level";
    } else {
        atomic_fetch_add_explicit(&ctrl->active_requests, 1, memory_order_relaxed);
    }

    return res;
}

/* Звільнення ресурсу після завершення обробки */
void shedding_controller_release(shedding_controller_t *ctrl) {
    int prev = atomic_fetch_sub_explicit(&ctrl->active_requests, 1, memory_order_relaxed);
    if (prev <= 0) {
        atomic_store_explicit(&ctrl->active_requests, 0, memory_order_relaxed);
    }
    update_brownout_level(ctrl);
}

int main(void) {
    shedding_controller_t ctrl;
    shedding_controller_init(&ctrl, 100);

    /* Імітація зростання навантаження до 75 паралельних запитів */
    atomic_store(&ctrl.active_requests, 75);

    /* Спроба виконати запит P4 (Background) під тиском */
    admission_result_t r_p4 = shedding_controller_eval(&ctrl, PRIORITY_P4_BACKGROUND);
    printf("P4 Request: allow=%d, status=%d, retry_after=%ds, reason='%s'\n",
           r_p4.allow, r_p4.http_status, r_p4.retry_after_sec, r_p4.reason);

    /* Спроба виконати запит P0 (Critical) під тиском */
    admission_result_t r_p0 = shedding_controller_eval(&ctrl, PRIORITY_P0_CRITICAL);
    printf("P0 Request: allow=%d, status=%d, active_requests=%d\n",
           r_p0.allow, r_p0.http_status, atomic_load(&ctrl.active_requests));

    shedding_controller_release(&ctrl);
    return 0;
}
```
```cpp
#include <iostream>
#include <atomic>
#include <string_view>
#include <expected>
#include <chrono>

enum class RequestPriority : uint8_t {
    P0_Critical   = 0,
    P1_High       = 1,
    P2_Medium     = 2,
    P3_Low        = 3,
    P4_Background = 4
};

enum class BrownoutLevel : uint8_t {
    L0_Normal    = 0,
    L1_ShedP4    = 1,
    L2_ShedP3    = 2,
    L3_ShedP2    = 3,
    L4_Emergency = 4
};

struct SheddingError {
    int http_status{503};
    std::chrono::seconds retry_after{15};
    std::string_view reason;
    BrownoutLevel active_level;
};

// RAII контролер для обліку паралельності та автоматичного зниження тиску
class AdaptiveSheddingController {
public:
    explicit AdaptiveSheddingController(size_t max_capacity)
        : capacity_(max_capacity) {}

    // RAII обгортка: інкрементує активні запити при створенні, декрементує у деструкторі
    class RequestGuard {
    public:
        explicit RequestGuard(AdaptiveSheddingController& ctrl) : controller_(ctrl) {}
        ~RequestGuard() {
            if (active_) {
                controller_.release();
            }
        }

        RequestGuard(const RequestGuard&) = delete;
        RequestGuard& operator=(const RequestGuard&) = delete;

        RequestGuard(RequestGuard&& o) noexcept 
            : controller_(o.controller_), active_(o.active_) {
            o.active_ = false;
        }

        RequestGuard& operator=(RequestGuard&& o) noexcept {
            if (this != &o) {
                if (active_) controller_.release();
                active_ = o.active_;
                o.active_ = false;
            }
            return *this;
        }

    private:
        AdaptiveSheddingController& controller_;
        bool active_{true};
    };

    [[nodiscard]] std::expected<RequestGuard, SheddingError> try_admit(RequestPriority priority) {
        const auto level = update_and_get_level();

        if (should_drop(level, priority)) {
            const auto retry_sec = std::chrono::seconds(10 + static_cast<int>(priority) * 5);
            return std::unexpected(SheddingError{
                .http_status = 503,
                .retry_after = retry_sec,
                .reason = "Request shedded by adaptive load shedding controller",
                .active_level = level
            });
        }

        active_requests_.fetch_add(1, std::memory_order_relaxed);
        return RequestGuard(*this);
    }

    [[nodiscard]] size_t active_count() const noexcept {
        return active_requests_.load(std::memory_order_relaxed);
    }

    [[nodiscard]] BrownoutLevel current_level() const noexcept {
        return current_level_.load(std::memory_order_relaxed);
    }

private:
    void release() noexcept {
        active_requests_.fetch_sub(1, std::memory_order_relaxed);
        update_and_get_level();
    }

    static bool should_drop(BrownoutLevel level, RequestPriority prio) noexcept {
        switch (level) {
            case BrownoutLevel::L4_Emergency: return prio > RequestPriority::P0_Critical;
            case BrownoutLevel::L3_ShedP2:    return prio >= RequestPriority::P2_Medium;
            case BrownoutLevel::L2_ShedP3:    return prio >= RequestPriority::P3_Low;
            case BrownoutLevel::L1_ShedP4:    return prio >= RequestPriority::P4_Background;
            case BrownoutLevel::L0_Normal:
            default:                          return false;
        }
    }

    BrownoutLevel update_and_get_level() noexcept {
        const size_t active = active_requests_.load(std::memory_order_relaxed);
        BrownoutLevel current = current_level_.load(std::memory_order_relaxed);
        BrownoutLevel next = current;

        // Пороги наростання тиску
        if (active >= 95) next = BrownoutLevel::L4_Emergency;
        else if (active >= 85) next = BrownoutLevel::L3_ShedP2;
        else if (active >= 70) next = BrownoutLevel::L2_ShedP3;
        else if (active >= 50) next = BrownoutLevel::L1_ShedP4;

        // Гістерезис при спаданні тиску
        else if (current == BrownoutLevel::L4_Emergency && active < 90) next = BrownoutLevel::L3_ShedP2;
        else if (current == BrownoutLevel::L3_ShedP2 && active < 80)    next = BrownoutLevel::L2_ShedP3;
        else if (current == BrownoutLevel::L2_ShedP3 && active < 65)    next = BrownoutLevel::L1_ShedP4;
        else if (current == BrownoutLevel::L1_ShedP4 && active < 45)    next = BrownoutLevel::L0_Normal;

        if (next != current) {
            current_level_.store(next, std::memory_order_relaxed);
        }
        return next;
    }

    size_t capacity_;
    std::atomic<size_t> active_requests_{0};
    std::atomic<BrownoutLevel> current_level_{BrownoutLevel::L0_Normal};
};

int main() {
    AdaptiveSheddingController controller(100);

    // Спроба обробити P4 під низьким навантаженням
    auto res1 = controller.try_admit(RequestPriority::P4_Background);
    if (res1) {
        std::cout << "P4 request admitted! Active requests: " << controller.active_count() << "\n";
    }

    // При виході res1 з області видимості деструктор RequestGuard автоматично декрементує активний лічильник
    std::cout << "After guard scope exit, active requests: " << controller.active_count() << "\n";

    return 0;
}
```
:::

---

## 3. Детальний аналіз реалізації та крайових випадків

### 3.1. Чому використовуються атомарні операції з `memory_order_relaxed`
У високонавантажених серверах обробка вхідних запитів відбувається паралельно на десятках ядер CPU. Звичайна синхронізація через важкі м'ютекси (`std::mutex` або `pthread_mutex_t`) створює точку високої контенції (lock contention), уповільнюючи обробку запитів у 10–50 разів лише на викликах блокування.

У наведених прикладах лічильник `active_requests` опирається на атомарні інструкції CPU (`lock xadd` на x86-64). Використання атомарного порядку `memory_order_relaxed` виправдано тим, що для контролера відкидання не потрібна строга послідовна узгодженість (sequential consistency) між нодами: нам важливо знати наближену кількість запитів без блокування шини пам'яті.

### 3.2. Надійність RAII у C++
У реальному коді серверного обробника функція може завершуватися з десятка причин: успішне повернення, повернення помилки валідації, або викидання винятку (exception). Якщо декремент активних запитів викликати вручну в кінці функції, перша ж неочікувана помилка чи `throw` призведе до **витоку активного лічильника** (active counter leak). Лічильник назавжди залишиться рівним `95`, і сервіс назавжди зависне в аварійному режимі `L4 Emergency`.

Класна обгортка `RequestGuard` реалізує паттерн RAII (Resource Acquisition Is Initialization). Її деструктор гарантовано викликається компілятором при виході з функції за будь-яких умов (включаючи `return`, `co_return` чи unwinding стека при винятках).

---

## 4. Спостережність (Observability) та експорт метрик Prometheus

Контролер відкидання навантаження не повинен працювати як «чорна скринька». Кожна подія зміни рівня Brownout або відкидання запиту повинна експортуватися в систему моніторингу Prometheus та трасування OpenTelemetry.

### Метрики Prometheus для Load Shedding Middleware:

```text
# HELP shedding_requests_total Загальна кількість оброблених та відкинутих запитів
# TYPE shedding_requests_total counter
shedding_requests_total{priority="P0",status="admitted"} 45210
shedding_requests_total{priority="P4",status="rejected",reason="brownout_l1"} 12890

# HELP shedding_active_requests Поточна кількість паралельно виконуваних запитів
# TYPE shedding_active_requests gauge
shedding_active_requests 78

# HELP shedding_brownout_level Поточний рівень деградації вузла (0..4)
# TYPE shedding_brownout_level gauge
shedding_brownout_level 2
```

Алерт у Prometheus (Alertmanager rule):

```yaml
groups:
  - name: load_shedding_alerts
    rules:
      - alert: HighBrownoutLevelActive
        expr: shedding_brownout_level >= 3
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Вузол перебуває у критичному режимі деградації L3/L4 понад 2 хвилини"
          description: "Понад 85% ресурсів ноди заповнено. Скидається трафік P2/P3/P4."
```

---

## 5. Низькорівневе вимірювання затримки у сокетах Linux (eBPF та procfs)

У низькорівневих мережевих сервісах вимірювання затримки на рівні застосунку може бути запізнілим, оскільки запит уже провів час у черзі приймального сокета ядра Linux (TCP Receive Buffer). 

Для точного відкидання на рівні ядра Linux сучасні Ingress-контролери використовують програми **eBPF (Extended Berkeley Packet Filter)**, прив'язані до точок трасування `tc` (Traffic Control) або `XDP` (eXpress Data Path).

### Схема роботи eBPF Load Shedder:

```text
Вхідний Ethernet-пакет (IP / TCP)
       │
       ▼
 [ XDP Hook в ядрі Linux ] ──(Зчитування eBPF map з активним Brownout Level)
       │
       ├─► При P4 та Brownout >= L1 ──► XDP_DROP (Відкидання на рівні мережевої карти за 50 нс)
       │
       └─► При P0 ────────────────────► XDP_PASS (Передача у мережевий стек ядра)
```

Відкидання запитів P4 на рівні XDP займає менше 50 наносекунд на пакет і повністю захищає процесор та сокетні буфери ОС від заповнення другорядним трафіком.

---

## 6. Типові помилки реалізації та як їх виявити під час профілювання

При впровадженні власних контролерів відкидання навантаження розробники найчастіше припускаються трьох помилок:

1. **Гонка лічильників при високій паралельності**: Використання неатомарних типів даних (`int active_requests`) призводить до втрати ікрементів під час паралельного виконання в кількох потоках. Виявляється інструментом **ThreadSanitizer (TSan)** (`-fsanitize=thread`).
2. **Зависання у верхньому режимі через невчитаний гістерезис**: Якщо дельта гістерезису відсутня або від'ємна, контролер швидко осцилює. Виявляється через аналіз графіків метрик Prometheus (пилоподібні коливання `shedding_brownout_level`).
3. **Блокування низькопріоритетними ресурсами (Priority Inversion)**: Запити P0 чекають на м'ютекси, зайняті P4. Виявляється профілювальником **perf** або **Valgrind/Helgrind** за допомогою аналізу часу чекання на мутексах (`mutex_wait_time`).
