# ⚙️ Реалізація контролера канаркової маршрутизації з автоматичним відкочуванням

Коли нова версія бекенду розгортається в продакшені за канарковою схемою, критично важливо мати програмний компонент на рівні шлюзу або балансувальника, який динамічно розподіляє трафік між стабільним пулом (v1) та канарковим пулом (v2), безперервно збирає статистику виконання запитів у ковзному часовому вікні й автоматично вимикає канарку при перевищенні допустимої частки помилок. Ручне відстеження графіків оператором займає хвилини, тоді як автоматичний контролер фіксує деградацію за частки секунди й самостійно зводить частку трафіку на новий сервіс до нуля.

Для високонавантажених сервісів неприпустимо використовувати зовнішні опитування моніторингу (наприклад, опитування Prometheus раз на 15 чи 30 секунд), оскільки за цей інтервал затримки канарковий вузол під навантаженням у 10 000 запитів на секунду встигне віддати понад 150 000 помилок реальним клієнтам. Контролер повинен виконувати аналіз безпосередньо всередині робочого процесу проксі або шлюзу (англ. *in-process traffic arbiter*), оперуючи мікросекундними затримками та гарантуючи нульовий оверхед на гарячому шляху маршрутизації.

## Архітектура та математична модель контролера

Контролер маршрутизації оперує двома пулами вузлів: **Baseline (v1, перевірене середовище)** та **Canary (v2, кандидат на підвищення)**.

```text
Вхідний запит ──> [ Селектор цілі ] ──┬──(100 - W)%──> [ Baseline Pool (v1) ] ──> Метрики Baseline
                                      │
                                      └──(W)%────────> [ Canary Pool (v2) ]   ──> [ Кільцевий буфер вікна ]
                                                                                            │
                                                                                            ▼
                                                                                 [ Оцінка помилок SLA ]
                                                                                            │
                                                                           ┌────────────────┴────────────────┐
                                                                     [ Err ≤ Porig ]                   [ Err > Porig ]
                                                                           │                                 │
                                                                           ▼                                 ▼
                                                                    Продовження кроку                 АВАРІЙНИЙ ВІДКІТ
                                                                    (Weight W -> W + Δ)               (Weight W = 0%)
```

### 1. Механіка зваженої селекції цільового вузла
Для кожного вхідного запиту контролер приймає рішення про вибір бекенду на основі сконфігурованого відсотка ваги `canary_weight_pct` (діапазон від `0` до `100`).

У найпростішому варіанті розподіл реалізується через генератор псевдовипадкових чисел. Якщо випадкове число в діапазоні `[0, 100)` строго менше за значення `canary_weight_pct`, запит надсилається на канарковий вузол; в іншому випадку — на базовий. У розподілених системах із сесійною прив'язкою (англ. *session affinity* або *sticky sessions*) замість генератора випадкових чисел обчислюється стабільний геш від ідентифікатора користувача, IP-адреси клієнта або сесійного cookie, що запобігає «мерехтінню» інтерфейсу між різними версіями застосунку під час послідовних кліків одного користувача.

### 2. Кільцевий буфер ковзного часового вікна (Sliding Window Bucket Ring)
Для уникнення накопичення застарілих помилок, які сталися годину тому, контролер обчислює якість роботи канарки виключно на короткому ковзному часовому інтервалі тривалістю `T_window = N_slots * T_slot` (наприклад, 10 слотів по 1 секунді, що утворює вікно глибиною 10 секунд).

Кожен слот представляє структуру даних, що містить мітку часу початку слота `timestamp_sec`, загальну кількість оброблених запитів `total_requests` та кількість зареєстрованих відмов `error_requests` (HTTP-статуси 5xx, обриви з'єднання, виходи за тайм-аут). Коли поточний час виходить за межі активного слота, вказівник поточного слота циклічно зміщується в кільцевому масиві, обнуляючи старі лічильники. Це дозволяє досягти константної складності `O(1)` за часом і пам'яттю для оновлення метрик без виділення динамічної пам'яті під час обробки запитів.

### 3. Формула оцінки частоти відмов та захист від статистичного шуму
У момент завершення кожного запиту контролер агрегує значення лічильників з усіх актуальних слотів кільця:

```text
W_total = ∑ canary_slots[i].total_requests   (де timestamp[i] ≥ now - T_window)
W_errors = ∑ canary_slots[i].error_requests   (де timestamp[i] ≥ now - T_window)
```

Частка помилок (англ. *error rate*) обчислюється як відношення:

```text
error_rate = W_errors / W_total
```

Критичним елементом алгоритму є бар'єр мінімального розміру вибірки (англ. *sample size guard*). Якщо за поточне часове вікно канарковий вузол обробив менше, ніж `min_sample_size` запитів (наприклад, менше 50 запитів при щойно виставленій вазі 1%), обчислення частки помилок блокується. Без цього захисту будь-який одиночний випадковий збій (наприклад, клієнт обірвав з'єднання в мобільному додатку) на вибірці з 2 запитів дав би `error_rate = 50%`, що призвело б до помилкового аварійного відкочування абсолютно здорової версії сервісу.

### 4. Автоматичний відкіт і механіка дренажу з'єднань
Якщо виконано одночасно дві умови:
1. `W_total >= min_sample_size`
2. `error_rate > max_allowed_error_rate` (наприклад, частка помилок перевищила 2.0% при базовому нульовому рівні)

Контролер виконує наступну атомарну послідовність дій:
* Переводить внутрішній стан скінченного автомата з `ACTIVE` в `ROLLED_BACK`.
* Атомарно встановлює `canary_weight_pct = 0`, що повністю припиняє маршрутизацію нових запитів на канарковий пул.
* Генерує структуровану подію аварійного оповіщення в підсистему телеметрії із зазначенням точної частки помилок, розміру вибірки та часового інтервалу.
* Переводить відкриті з'єднання до канарки в режим дренажу (англ. *graceful draining*), дозволяючи активним запитам добігти кінця, але примусово закриваючи TCP-канали після повернення відповіді за допомогою заголовка `Connection: close`.

## Скінченний автомат станів контролера

Поведінка маршрутизатора формалізується у вигляді детермінованого скінченного автомата (англ. *finite state machine*, FSM):

```text
       ┌───────────────┐
       │   INACTIVE    │ (Вага = 0%, канарковий пул відключений)
       └───────┬───────┘
               │ router_set_weight(W > 0)
               ▼
       ┌───────────────┐  Помилки > Порогу (вибірка ≥ N)
       │    ACTIVE     ├─────────────────────────────────────────┐
       └───────┬───────┘                                         │
               │                                                 │
               │ router_promote()                                │
               ▼                                                 ▼
       ┌───────────────┐                                 ┌───────────────┐
       │   PROMOTED    │                                 │  ROLLED_BACK  │
       │  (Вага 100%)  │                                 │   (Вага 0%)   │
       └───────────────┘                                 └───────────────┘
```

Таблиця перехідних станів:

| Початковий стан | Подія | Умова переходу | Новий стан | Дія системи |
| :--- | :--- | :--- | :--- | :--- |
| `INACTIVE` | `set_weight(W)` | `W > 0` | `ACTIVE` | Активація генерації випадкових зрізів трафіку |
| `ACTIVE` | `record_result()` | `err_rate > max_err && n >= min_n` | `ROLLED_BACK` | Миттєве скидання ваги до 0%, аварійний алерт |
| `ACTIVE` | `set_weight(W_new)`| `W_new <= 100` | `ACTIVE` | Плавна зміна пропорції трафіку (крок промоції) |
| `ACTIVE` | `promote()` | Завершення всіх етапів перевірки | `PROMOTED` | Встановлення ваги 100%, фіксація v2 як основного коду |
| `ROLLED_BACK` | `set_weight()` | Будь-яка спроба зміни ваги | `ROLLED_BACK` | Блокування змін до ручного втручання інженера |

## Робочий код контролера на мовах C та C++

Нижче наведено закінчену реалізацію контролера. Код спроєктовано для вбудовування в мережеві шлюзи, зворотні проксі-сервери або мікросервісні сайдкари.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define METRIC_SLOTS 10
#define SLOT_DURATION_SEC 1

typedef enum {
    CANARY_STATE_INACTIVE,
    CANARY_STATE_ACTIVE,
    CANARY_STATE_ROLLED_BACK,
    CANARY_STATE_PROMOTED
} CanaryState;

typedef enum {
    TARGET_BASELINE,
    TARGET_CANARY
} RoutingTarget;

typedef struct {
    uint64_t timestamp_sec;
    uint32_t total_requests;
    uint32_t error_requests;
} MetricSlot;

typedef struct {
    char baseline_addr[64];
    char canary_addr[64];
    uint32_t canary_weight_pct;      /* від 0 до 100 */
    double max_allowed_error_rate;    /* поріг помилок, наприклад 0.02 (2%) */
    uint32_t min_sample_size;         /* мінімальна вибірка для аналізу */
    CanaryState state;
    MetricSlot canary_slots[METRIC_SLOTS];
    size_t current_slot_idx;
    uint64_t last_slot_rotation_sec;
} DeploymentRouter;

static uint64_t get_current_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec;
}

void router_init(DeploymentRouter *r, const char *baseline, const char *canary,
                 uint32_t initial_weight, double max_err_rate, uint32_t min_samples) {
    memset(r, 0, sizeof(DeploymentRouter));
    strncpy(r->baseline_addr, baseline, sizeof(r->baseline_addr) - 1);
    strncpy(r->canary_addr, canary, sizeof(r->canary_addr) - 1);
    r->canary_weight_pct = (initial_weight <= 100) ? initial_weight : 0;
    r->max_allowed_error_rate = max_err_rate;
    r->min_sample_size = min_samples;
    r->state = (initial_weight > 0) ? CANARY_STATE_ACTIVE : CANARY_STATE_INACTIVE;
    r->last_slot_rotation_sec = get_current_time_sec();
}

static void router_rotate_slots_if_needed(DeploymentRouter *r, uint64_t now_sec) {
    uint64_t elapsed = now_sec - r->last_slot_rotation_sec;
    if (elapsed >= SLOT_DURATION_SEC) {
        uint64_t steps = elapsed / SLOT_DURATION_SEC;
        if (steps > METRIC_SLOTS) {
            steps = METRIC_SLOTS;
        }
        for (uint64_t i = 0; i < steps; ++i) {
            r->current_slot_idx = (r->current_slot_idx + 1) % METRIC_SLOTS;
            r->canary_slots[r->current_slot_idx].timestamp_sec = now_sec;
            r->canary_slots[r->current_slot_idx].total_requests = 0;
            r->canary_slots[r->current_slot_idx].error_requests = 0;
        }
        r->last_slot_rotation_sec = now_sec;
    }
}

RoutingTarget router_select_target(DeploymentRouter *r) {
    if (r->state != CANARY_STATE_ACTIVE || r->canary_weight_pct == 0) {
        return TARGET_BASELINE;
    }
    uint32_t roll = (uint32_t)(rand() % 100);
    if (roll < r->canary_weight_pct) {
        return TARGET_CANARY;
    }
    return TARGET_BASELINE;
}

void router_record_result(DeploymentRouter *r, RoutingTarget target, bool is_error) {
    if (target != TARGET_CANARY || r->state != CANARY_STATE_ACTIVE) {
        return;
    }

    uint64_t now_sec = get_current_time_sec();
    router_rotate_slots_if_needed(r, now_sec);

    MetricSlot *slot = &r->canary_slots[r->current_slot_idx];
    slot->total_requests++;
    if (is_error) {
        slot->error_requests++;
    }

    /* Агрегація метрик у межах активного ковзного вікна */
    uint32_t window_total = 0;
    uint32_t window_errors = 0;

    for (size_t i = 0; i < METRIC_SLOTS; ++i) {
        if (now_sec - r->canary_slots[i].timestamp_sec <= (METRIC_SLOTS * SLOT_DURATION_SEC)) {
            window_total += r->canary_slots[i].total_requests;
            window_errors += r->canary_slots[i].error_requests;
        }
    }

    /* Перевірка критерію аварійного відкочування */
    if (window_total >= r->min_sample_size) {
        double current_err_rate = (double)window_errors / (double)window_total;
        if (current_err_rate > r->max_allowed_error_rate) {
            r->state = CANARY_STATE_ROLLED_BACK;
            r->canary_weight_pct = 0;
            fprintf(stderr, "[АЛЕРТ] Аварійний відкіт канарки! Помилки: %.2f%% (поріг %.2f%%, вибірка %u)\n",
                    current_err_rate * 100.0, r->max_allowed_error_rate * 100.0, window_total);
        }
    }
}

void router_set_weight(DeploymentRouter *r, uint32_t new_weight) {
    if (r->state == CANARY_STATE_ROLLED_BACK) {
        fprintf(stderr, "[ПОПЕРЕДЖЕННЯ] Неможливо змінити вагу: канарка у стані відкочування.\n");
        return;
    }
    r->canary_weight_pct = (new_weight <= 100) ? new_weight : 100;
    r->state = (r->canary_weight_pct > 0) ? CANARY_STATE_ACTIVE : CANARY_STATE_INACTIVE;
    printf("[ІНФО] Встановлено нову вагу канарки: %u%%\n", r->canary_weight_pct);
}

void router_promote(DeploymentRouter *r) {
    r->state = CANARY_STATE_PROMOTED;
    r->canary_weight_pct = 100;
    printf("[ІНФО] Канарку успішно підвищено до 100%% основного трафіку.\n");
}

int main(void) {
    srand((unsigned int)time(NULL));
    DeploymentRouter router;
    router_init(&router, "10.0.0.1:8080", "10.0.0.2:8080", 20, 0.05, 50);

    printf("Ініціалізація маршрутизатора: Baseline=%s, Canary=%s (Вага=%u%%)\n",
           router.baseline_addr, router.canary_addr, router.canary_weight_pct);

    /* Симуляція живого потоку запитів */
    for (int i = 1; i <= 200; ++i) {
        RoutingTarget tgt = router_select_target(&router);
        bool is_err = false;

        if (tgt == TARGET_CANARY) {
            /* Симулюємо сплеск помилок на канарковому вузлі після 30 запитів */
            if (i > 30 && (rand() % 100 < 25)) {
                is_err = true;
            }
            router_record_result(&router, tgt, is_err);
        }

        if (router.state == CANARY_STATE_ROLLED_BACK) {
            printf("Запит #%d: Трафік на канарку повністю перекрито.\n", i);
            break;
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <random>
#include <cstdint>
#include <numeric>
#include <format>
#include <algorithm>

enum class CanaryState {
    Inactive,
    Active,
    RolledBack,
    Promoted
};

enum class RoutingTarget {
    Baseline,
    Canary
};

struct MetricSlot {
    std::chrono::steady_clock::time_point timestamp{};
    uint32_t total_requests{0};
    uint32_t error_requests{0};
};

class DeploymentRouter {
public:
    DeploymentRouter(std::string baseline_addr, std::string canary_addr,
                     uint32_t initial_weight_pct, double max_err_rate,
                     uint32_t min_samples)
        : baseline_addr_(std::move(baseline_addr)),
          canary_addr_(std::move(canary_addr)),
          canary_weight_pct_(std::min(initial_weight_pct, 100u)),
          max_allowed_error_rate_(max_err_rate),
          min_sample_size_(min_samples),
          state_(initial_weight_pct_ > 0 ? CanaryState::Active : CanaryState::Inactive),
          last_rotation_(std::chrono::steady_clock::now()),
          rng_(std::random_device{}()),
          dist_(0, 99) {
        slots_.fill(MetricSlot{last_rotation_, 0, 0});
    }

    [[nodiscard]] RoutingTarget select_target() {
        if (state_ != CanaryState::Active || canary_weight_pct_ == 0) {
            return RoutingTarget::Baseline;
        }
        return (static_cast<uint32_t>(dist_(rng_)) < canary_weight_pct_)
                   ? RoutingTarget::Canary
                   : RoutingTarget::Baseline;
    }

    void record_result(RoutingTarget target, bool is_error) {
        if (target != RoutingTarget::Canary || state_ != CanaryState::Active) {
            return;
        }

        const auto now = std::chrono::steady_clock::now();
        rotate_slots_if_needed(now);

        auto& current_slot = slots_[current_slot_idx_];
        current_slot.total_requests++;
        if (is_error) {
            current_slot.error_requests++;
        }

        evaluate_health(now);
    }

    void set_weight(uint32_t new_weight) {
        if (state_ == CanaryState::RolledBack) {
            std::cerr << "[ПОПЕРЕДЖЕННЯ] Неможливо змінити вагу: канарка у стані відкочування.\n";
            return;
        }
        canary_weight_pct_ = std::min(new_weight, 100u);
        state_ = (canary_weight_pct_ > 0) ? CanaryState::Active : CanaryState::Inactive;
        std::cout << std::format("[ІНФО] Встановлено нову вагу канарки: {}%\n", canary_weight_pct_);
    }

    void promote() noexcept {
        state_ = CanaryState::Promoted;
        canary_weight_pct_ = 100;
        std::cout << "[ІНФО] Канарку успішно підвищено до 100% основного трафіку.\n";
    }

    [[nodiscard]] CanaryState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t canary_weight() const noexcept { return canary_weight_pct_; }
    [[nodiscard]] std::string_view baseline_address() const noexcept { return baseline_addr_; }
    [[nodiscard]] std::string_view canary_address() const noexcept { return canary_addr_; }

private:
    static constexpr size_t kSlotCount = 10;
    static constexpr auto kSlotDuration = std::chrono::seconds(1);
    static constexpr auto kWindowDuration = kSlotCount * kSlotDuration;

    void rotate_slots_if_needed(std::chrono::steady_clock::time_point now) {
        const auto elapsed = now - last_rotation_;
        if (elapsed >= kSlotDuration) {
            const auto steps = std::min(
                static_cast<size_t>(elapsed / kSlotDuration),
                kSlotCount
            );
            for (size_t i = 0; i < steps; ++i) {
                current_slot_idx_ = (current_slot_idx_ + 1) % kSlotCount;
                slots_[current_slot_idx_] = MetricSlot{now, 0, 0};
            }
            last_rotation_ = now;
        }
    }

    void evaluate_health(std::chrono::steady_clock::time_point now) {
        uint32_t window_total = 0;
        uint32_t window_errors = 0;

        for (const auto& slot : slots_) {
            if (now - slot.timestamp <= kWindowDuration) {
                window_total += slot.total_requests;
                window_errors += slot.error_requests;
            }
        }

        if (window_total >= min_sample_size_) {
            const double current_error_rate = static_cast<double>(window_errors) / window_total;
            if (current_error_rate > max_allowed_error_rate_) {
                trigger_rollback(current_error_rate, window_total);
            }
        }
    }

    void trigger_rollback(double err_rate, uint32_t sample_size) {
        state_ = CanaryState::RolledBack;
        canary_weight_pct_ = 0;
        std::cerr << std::format(
            "[АЛЕРТ] Аварійний відкіт канарки! Помилки: {:.2f}% (поріг {:.2f}%, вибірка {})\n",
            err_rate * 100.0, max_allowed_error_rate_ * 100.0, sample_size
        );
    }

    std::string baseline_addr_;
    std::string canary_addr_;
    uint32_t canary_weight_pct_;
    double max_allowed_error_rate_;
    uint32_t min_sample_size_;
    CanaryState state_;

    std::array<MetricSlot, kSlotCount> slots_{};
    size_t current_slot_idx_{0};
    std::chrono::steady_clock::time_point last_rotation_;

    std::mt19937 rng_;
    std::uniform_int_distribution<int> dist_;
};

int main() {
    DeploymentRouter router("10.0.0.1:8080", "10.0.0.2:8080", 20, 0.05, 50);

    std::cout << std::format("Ініціалізація: Baseline={}, Canary={} (Вага={}%)\n",
                             router.baseline_address(), router.canary_address(),
                             router.canary_weight());

    std::mt19937 gen(1337);
    std::uniform_int_distribution<int> error_dist(0, 99);

    for (int i = 1; i <= 200; ++i) {
        const auto target = router.select_target();
        bool is_error = false;

        if (target == RoutingTarget::Canary) {
            if (i > 30 && error_dist(gen) < 25) {
                is_error = true;
            }
            router.record_result(target, is_error);
        }

        if (router.state() == CanaryState::RolledBack) {
            std::cout << std::format("Запит #{}: Трафік на канарку повністю перекрито.\n", i);
            break;
        }
    }

    return 0;
}
```
:::

## Поглиблений аналіз підсистем та оптимізація продуктивності

### 1. Організація пам'яті та уникнення Cache Line Bouncing
У багатопотокових середовищах, де сотні робочих потоків (англ. *worker threads*) одночасно обробляють запити на 64-ядерному сервері, звичайне інкрементування спільних змінних `total_requests` та `error_requests` призводить до фатальної деградації продуктивності через ефект помилкового розділення пам'яті (англ. *false sharing*). Коли одне процесорне ядро модифікує байт у кеш-лінії (розміром 64 байти в архітектурах x86-64 та ARM64), протокол когерентності кешів MESI змушений інвалідувати цю лінію у кешах L1/L2 всіх інших ядер.

Щоб контролер маршрутизації витримував мільйони запитів на секунду без взаємних блокувань ядер, застосовують архітектуру локальних лічильників потоків (англ. *Thread-Local Metric Storage*):
1. Кожен робочий потік оновлює виключно власний незалежний екземпляр кільцевого буфера, вирівняний за кордоном 64 байтів (`alignas(64)` у C++ або `__attribute__((aligned(64)))` у C).
2. Окремий фоновий потік-арбітр (англ. *arbiter daemon*) раз на 100 мілісекунд зчитує та підсумовує значення лічильників з усіх локальних масивів потоків, використовуючи неблокуючі атомарні операції з ослабленим порядком пам'яті `std::memory_order_relaxed`.
3. Завдяки цьому гарячий шлях виконання HTTP-запиту взагалі не містить операцій міжядерної синхронізації та системних викликів блокування.

### 2. Сесійна липкість через консистентне гешування
Якщо замість випадкового розподілу необхідно гарантувати, що конкретний користувач під час канаркового тестування завжди потрапляє на один і той самий бекенд, функція вибору цілі `select_target` адаптується під алгоритм консистентного гешування:

```text
uint32_t user_hash = murmur3_32(user_id_str, user_id_len, salt);
uint32_t bucket = user_hash % 100;
RoutingTarget target = (bucket < canary_weight_pct) ? TARGET_CANARY : TARGET_BASELINE;
```

Цей підхід забезпечує стабільність користувацького досвіду: якщо користувач потрапив у 5% вибірку канарки, він залишатиметься на новій версії v2 протягом усієї сесії оформлення кошика. Якщо вагу канарки згодом підвищують з 5% до 20%, перші 5% користувачів гарантовано не змінять свій цільовий вузол, а нові 15% будуть плавно додані до експерименту.

### 3. Оцінка затримок (Latency SLA) без виділення пам'яті в купі
Окрім підрахунку частоти помилок 5xx, сучасні промислові канаркові контролери відстежують хвостові перцентилі затримки (p95 та p99). Якщо нова версія не повертає помилок, але виконує запити за 1200 мілісекунд замість базових 45 мілісекунд, такий реліз також вважається аварійним і підлягає негайному відкочуванню.

Збереження точного списку всіх часових інтервалів у пам'яті потребувало б динамічного виділення пам'яті під кожен запит, що неприпустимо у високопродуктивних мережевих рушіях. Тому контролер розширюється фіксованим логарифмічним гістограмним масивом (англ. *fixed log-binned histogram*):
* Час відповіді розбивається на фіксовані кошики (наприклад, 32 бакети: `[0-1ms]`, `[1-2ms]`, `[2-4ms]`, `[4-8ms]`, ..., `[>10s]`).
* Завершення запиту потребує лише обчислення номера бакета через швидку бітову інструкцію підрахунку провідних нулів процесора (`__builtin_clz`) та інкременту відповідного лічильника.
* Перцентиль p99 обчислюється фоновим арбітром шляхом кумулятивного сканування 32 цілих чисел, що займає менше 5 наносекунд.

### 4. Динамічне крокування промоції (Adaptive Step Sizing)
У повністю автоматизованих пайплайнах перехід від початкового тестування до 100% трафіку відбувається за ступінчастим графіком. Замість лінійного додавання фіксованого відсотка контролер може використовувати експоненційну або адаптивну шкалу:

* **Початковий захисний бар'єр:** 1% або 2% трафіку протягом 10–15 хвилин для перевірки базової сумісності з типами запитів.
* **Сходинка навантаження:** 10% → 25% → 50% із витримкою на кожному етапі для аналізу затримок і споживання ресурсів процесора.
* **Фінальна промоція:** перехід на 100% та автоматичне виведення версії v1 з експлуатації.

На кожному кроці контролер скидає статистичні слоти ковзного вікна, щоб помилки з попереднього, менш навантаженого етапу не впливали на нове рішення арбітра.

### 5. Поєднання тіньового запуску (Dark Launch) з активною канаркою
Найбільш надійний виробничий патерн полягає у поєднанні темного запуску та канаркового контролера. Перед тим як надіслати перший живий відсоток користувачів на версію v2, контролер налаштовують на роботу в режимі тіньового дублювання (англ. *traffic shadowing*):
* Активна вага `canary_weight_pct = 0%`. Клієнти на 100% обслуговуються стабільним пулом v1.
* Мережевий шлюз асинхронно копіює 100% вхідних запитів і передає їх на канарковий пул v2.
* Контролер оцінює виключно внутрішні помилки (паніки, фатальні логи, падіння процесів) без повернення результатів клієнтам.
* Після 30 хвилин успішного тіньового прогону без збоїв контролер плавно перемикається в режим активної канарки з початковою вагою 5%. Це гарантує повний прогрів пулів з'єднань і кешів перед першим контактом з реальними користувачами, виключаючи деградацію холодного старту.

### 6. Розподілена синхронізація стану між екземплярами шлюзу
У горизонтально масштабованій інфраструктурі, де трафік приймають 20 незалежних L7-балансувальників або Ingress-контролерів, рішення про аварійний відкіт повинно синхронізуватися між усіма вузлами за мілісекунди:

* **Шина швидких подій (Redis Pub/Sub або NATS):** Коли локальний контролер одного з вузлів фіксує критичний сплеск помилок, він публікує подію `CANARY_EMERGENCY_ROLLBACK` у канал шини.
* **Реакція сусідніх пірів:** Усі інші 19 контролерів отримують подію через локальний фоновий сокет і миттєво обнуляють локальну вагу `canary_weight_pct = 0`, не чекаючи, поки на їхніх власних слотах накопичиться достатня вибірка помилок.
* **Автономний fallback:** Якщо мережева шина подій стає недоступною через локальний розділ мережі (англ. *network partition*), кожен вузол продовжує автономно приймати локальні рішення на основі власного кільцевого буфера, що виключає ризик зависання системи в єдиній точці відмови.

### 7. Інтеграція з динамічними площинами маршрутизації (Envoy, NGINX, HAProxy)
Описаний алгоритм може працювати як усередині бінарного файлу вебсервера, так і у вигляді зовнішнього керуючого контролера (англ. *control plane controller*), який передає інструкції мережевому проксі через його внутрішній API:

* **Envoy Proxy:** Контролер виступає сервером Dynamic Forwarding Discovery Service (xDS/RDS). При виявленні аномалії на канарці контролер генерує новий маршрутний конфіг `RouteConfiguration`, де вага кластера `canary_cluster` виставляється в 0, і надсилає його до Envoy по gRPC-каналу без перезапуску процесів.
* **HAProxy:** Контролер взаємодіє з керуючим сокетом HAProxy (англ. *Runtime API / UNIX socket*), надсилаючи команду `set weight backend_app/canary_node 0%`.
* **NGINX:** Зміна ваги здійснюється через модуль `ngx_http_upstream_module` за допомогою оновлення динамічної таблиці пірів у спільній пам'яті (англ. *shared memory zone*) або через інструкцію `split_clients`.

### 8. Порівняння рівнів реалізації канаркової маршрутизації

| Рівень реалізації | Переваги | Обмеження | Оверхед затримки | Складність інтеграції |
| :--- | :--- | :--- | :--- | :--- |
| **In-Process (у коді застосунку)** | Нульова мережева затримка, повний доступ до бізнес-контексту та сесій | Прив'язка до конкретної мови розробки | < 20 нс (в пам'яті) | Низька (бібліотека) |
| **L7 Reverse Proxy (Envoy / NGINX)** | Мовна нейтральність, централізоване керування для сотень сервісів | Необхідність налаштування xDS або динамічного оновлення конфігурації | 0.2–0.5 мс | Середня (деплой проксі) |
| **Service Mesh (Istio / Linkerd)** | Автоматичне шифрування mTLS, прозоре перехоплення трафіку сайдкаром | Значне споживання пам'яті (сотні сайдкарів), складний траблшутинг | 1.0–2.5 мс | Висока (інфраструктурний стек) |

### 9. Поведінка при нерівномірних затримках і розривах з'єднань (Connection Draining)
Миттєве скидання ваги канарки в `0%` вирішує проблему нових клієнтів, проте залишає відкритим питання запитів, які вже почали виконуватися на канарковому вузлі.

Якщо нова версія бекенду містить витік пам'яті або deadlock, тривале очікування завершення «завислих» запитів призведе до переповнення пулу з'єднань на балансувальнику. Тому перехід у стан `ROLLED_BACK` запускає таймер примусового дренажу (англ. *drain timeout*, типово від 5 до 15 секунд). Протягом цього вікна контролер очікує завершення обробки нормальних запитів. Якщо після закінчення таймера на канарковому вузлі залишаються активні відкриті дескриптори, контролер надсилає на сервер сигнал термінового закриття сокетів із надсиланням TCP-пакета `RST`, повністю звільняючи інфраструктурні ресурси.

### 10. Структуроване логування подій життєвого циклу канарки
Для інтеграції з системами централізованого аудиту та спостережуваності контролер генерує машиночитні події у форматі JSON під час кожної зміни внутрішнього стану:

```json
{
  "timestamp": "2026-08-20T14:32:01.450Z",
  "event": "CANARY_ROLLBACK_TRIGGERED",
  "baseline_target": "10.0.0.1:8080",
  "canary_target": "10.0.0.2:8080",
  "metrics_window_sec": 10,
  "sample_size": 142,
  "error_count": 9,
  "error_rate": 0.06338,
  "error_rate_threshold": 0.02000,
  "action_taken": "SET_WEIGHT_ZERO_AND_DRAIN",
  "operator_notified": true
}
```

Такий формат дозволяє автоматично зв'язувати події контролера з розподіленими трейсами в OpenTelemetry та фіксувати точний момент відсікання аномального трафіку в журналах постмортемів.

## Анатомія виробничого інциденту: автоматичне гасіння дефекту

Розглянемо покроковий сценарій роботи контролера під час реальної аварійної ситуації на високонавантаженому платіжному шлюзі:

1. **Таймкод 00:00 (Початок експерименту):** Контролер активує канарковий пул із вагою `canary_weight_pct = 5%`. На канарковий вузол v2 починає надходити 500 RPS із загального потоку 10 000 RPS. Протягом перших трьох секунд потік запитів успішно прогріває локальний JIT-компілятор та з'єднання до бази даних. Помилок немає, `error_rate = 0.00%`.
2. **Таймкод 00:15 (Прояв дефекту):** У версії v2 спрацьовує неопрацьований крайовий випадок у парсері JWT-токенів при отриманні специфічного формату авторизаційного заголовка від застарілих клієнтів. Кожен шостий запит до канарки завершується винятком `NullPointerException` та кодом відповіді HTTP 500.
3. **Таймкод 00:16 (Реакція арбітра):** Ковзне вікно фіксує 500 запитів, серед яких 84 завершилися помилкою. Обчислена частка помилок становить `84 / 500 = 16.8%`, що у понад 8 разів перевищує допустимий поріг `max_allowed_error_rate = 2.0%`.
4. **Таймкод 00:16.002 (Аварійний відкіт):** Контролер атомарно перемикає `canary_weight_pct` в `0%`. Час з моменту появи першої помилки до повного зняття трафіку з канарки склав лише 1.002 секунди.
5. **Підсумок інциденту:** З 10 000 користувачів системи збій відчули лише 84 клієнти, які потрапили у 5% вибірку канарки за одну секунду. Решта 9 916 користувачів продовжили безперебійно працювати зі стабільною версією v1, а інженери отримали точний структурований лог інциденту для швидкого усунення дефекту без простою системи.
