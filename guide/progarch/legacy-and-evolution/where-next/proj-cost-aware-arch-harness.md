# ⚙️ Практичний харнес для вартісно-свідомого розподілу ресурсів

Практична реалізація вартісно-свідомого обмежувача ресурсів (Cost-Aware Infrastructure Rate Limiter & Allocator) розраховує юніт-економіку обробки запитів, обмежує витрати хмари та запобігає перерозходу бюджету під час пікових навантажень.

## 1. Задача та обчислювальна модель вартісно-свідомого обмеження

У сучасних хмарних і розподілених архітектурах обробка кожного запиту має конкретну вимірювану фінансову вартість. Ця вартість складається з обчислювального часу центрального процесора (CPU execution time), обсягу виділеної оперативної пам'яті (RAM allocation), кількості операцій зчитування й запису до дискового або розподіленого сховища (I/O operations), трафіку між зонами доступності (Cross-AZ traffic) та викликів зовнішніх платних API або генеративних нейромережевих моделей (GPU/LLM inference).

Без вартісно-свідомого контролю (Cost-Aware Gatekeeper) аномальний сплеск трафіку, помилка у циклі повторних викликів клієнта (retry storm) або цілеспрямована DDoS-атака здатні вичерпати місячний інфраструктурний бюджет компанії за кілька годин.

### Математична модель оцінки вартості запиту

Загальна вартість `TotalCost` для кожного запиту обчислюється як сума базової тарифної ставки домену та змінної складової, пропорційної фактично спожитим ресурсам:

```
TotalCost = BaseCost(Tier) + CPU_Cost + Storage_Cost + Network_Cost

де:
  BaseCost(Tier)   = фіксований тариф для класу складності (Light, Medium, Heavy, GPU)
  CPU_Cost         = ExecutionTimeMs × CostPerCpuMs
  Storage_Cost     = ReadWriteOperations × CostPerOp
  Network_Cost     = TransferredBytes × CostPerByte
```

Харнес реалізує обмежувач із ковзним часовим вікном (Sliding Time Window Budget Allocator), який перевіряє поточний стан вигорання бюджету (Burn Rate) та динамічно застосовує рівні деградації обслуговування (SLA Degradation): від відмови у важких аналітичних обчисленнях до повернення кешованих відповідей або відмови з HTTP-кодом `429 Too Many Requests`.

## 2. Анатомія алгоритму та механізм градієнтної деградації

Алгоритм вартісно-свідомого обмежувача працює за наступним причинно-наслідковим ланцюгом:

```
[Запит прибув] ──► [Розрахунок ваги TotalCost] ──► [Перевірка залишкового бюджету]
                                                           │
                        ┌──────────────────────────────────┴──────────────────────────────────┐
                        ▼                                                                     ▼
             [Бюджет дозволяє]                                                      [Бюджет вичерпано]
                        │                                                                     │
                        ▼                                                                     ▼
          [Виконати запит & списати]                                             [Застосувати SLA Degradation]
                                                                                              │
                                                                          ┌───────────────────┼───────────────────┐
                                                                          ▼                   ▼                   ▼
                                                                  [Кешована відповідь]  [Легкий фолбек]    [HTTP 429 Retry-After]
```

Принцип градієнтної деградації полягає у тому, що при досягненні 80% ліміту бюджету секунди система перестає приймати важкі запити класу `GPU` та `Heavy`, зберігаючи можливість обробляти легкі запити `Light` з кешу. Це запобігає повному відключенню сервісу для користувачів під час фінансового голодування.

### Порівняння алгоритмів обмеження: Token Bucket vs Sliding Window Log

У практиці впровадження обмежувачів застосовують три основні алгоритми:
1. **Фіксоване вікно (Fixed Window Counter):** Найпростіший підхід, який скидає лічильник на початку кожної секунди. Головна пастка — сплеск трафіку на межі секунд (boundary burst), який може пропустити подвійне навантаження.
2. **Маркерний кошик (Token Bucket):** Токени додаються до кошика з постійною швидкістю. Запит споживає токени. Алгоритм чудово підходить для згладжування сплесків, але не враховує гетерогенну вартість різних типів запитів.
3. **Ковзне часове вікно (Sliding Window Log / Counter):** Зважена оцінка витрат за останні N мілісекунд. Забезпечує найточніший контроль фінансового бюджету в умовах змінної вартості ресурсів.

## 3. Реалізація мовами C та C++

Наведена нижче реалізація демонструє робочий обмежувач ресурсів мовами C (з явним керуванням пам'яттю, структурами та підрахунком метрик) та C++23 (із використанням RAII, концептів, `std::expected` та типів без витоків пам'яті).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_TIERS 4

typedef enum {
    COST_TIER_LIGHT = 0,    // Просте читання з кешу
    COST_TIER_MEDIUM = 1,   // Запит до бази даних
    COST_TIER_HEAVY = 2,    // Складна аналітика / транзакція
    COST_TIER_GPU = 3       // ML-інференс / GPU
} ResourceCostTier;

typedef struct {
    double cpu_cost_per_ms;
    double storage_cost_per_op;
    double net_cost_per_byte;
    double max_budget_per_sec;
    double degradation_threshold; // Поріг деградації (наприклад 0.80 = 80%)
} CostModelConfig;

typedef struct {
    CostModelConfig config;
    double current_spent_sec;
    uint64_t total_requests;
    uint64_t rejected_requests;
    uint64_t degraded_requests;
} CostLimiter;

static const double TIER_BASE_COSTS[MAX_TIERS] = {
    0.0001,   // LIGHT: $0.0001
    0.0010,   // MEDIUM: $0.001
    0.0100,   // HEAVY: $0.01
    0.0500    // GPU: $0.05
};

void cost_limiter_init(CostLimiter *limiter, double max_budget_per_sec) {
    if (!limiter) return;
    limiter->config.cpu_cost_per_ms = 0.00002;
    limiter->config.storage_cost_per_op = 0.0001;
    limiter->config.net_cost_per_byte = 0.00000005;
    limiter->config.max_budget_per_sec = max_budget_per_sec;
    limiter->config.degradation_threshold = 0.80; // 80% бюджету
    limiter->current_spent_sec = 0.0;
    limiter->total_requests = 0;
    limiter->rejected_requests = 0;
    limiter->degraded_requests = 0;
}

double cost_limiter_calculate_cost(const CostLimiter *limiter, ResourceCostTier tier,
                                   uint32_t cpu_time_ms, uint32_t storage_ops, uint32_t net_bytes) {
    if (!limiter || tier >= MAX_TIERS) return 0.0;
    
    double base_cost = TIER_BASE_COSTS[tier];
    double variable_cost = (cpu_time_ms * limiter->config.cpu_cost_per_ms) +
                           (storage_ops * limiter->config.storage_cost_per_op) +
                           (net_bytes * limiter->config.net_cost_per_byte);
    return base_cost + variable_cost;
}

bool cost_limiter_try_consume(CostLimiter *limiter, ResourceCostTier tier,
                              uint32_t cpu_time_ms, uint32_t storage_ops, uint32_t net_bytes,
                              double *out_cost, bool *out_degraded) {
    if (!limiter) return false;
    
    limiter->total_requests++;
    double cost = cost_limiter_calculate_cost(limiter, tier, cpu_time_ms, storage_ops, net_bytes);
    double budget = limiter->config.max_budget_per_sec;
    double spent_ratio = limiter->current_spent_sec / budget;

    // Якщо спожито понад 80% бюджету, відхиляємо важкі та GPU запити
    if (spent_ratio >= limiter->config.degradation_threshold && (tier == COST_TIER_HEAVY || tier == COST_TIER_GPU)) {
        limiter->degraded_requests++;
        limiter->rejected_requests++;
        if (out_cost) *out_cost = cost;
        if (out_degraded) *out_degraded = true;
        return false;
    }

    if (limiter->current_spent_sec + cost > budget) {
        limiter->rejected_requests++;
        if (out_cost) *out_cost = cost;
        if (out_degraded) *out_degraded = false;
        return false;
    }
    
    limiter->current_spent_sec += cost;
    if (out_cost) *out_cost = cost;
    if (out_degraded) *out_degraded = false;
    return true;
}

void cost_limiter_reset_window(CostLimiter *limiter) {
    if (limiter) {
        limiter->current_spent_sec = 0.0;
    }
}

int main(void) {
    CostLimiter limiter;
    cost_limiter_init(&limiter, 0.10); // Бюджет $0.10 на секунду

    printf("=== Cost-Aware Infrastructure Allocator (C) ===\n");

    for (int i = 1; i <= 6; i++) {
        double cost = 0.0;
        bool degraded = false;
        bool allowed = cost_limiter_try_consume(&limiter, COST_TIER_HEAVY, 15, 2, 4096, &cost, &degraded);
        printf("Request #%d [HEAVY]: Allowed=%s, Degraded=%s, Cost=$%.5f, TotalSpent=$%.5f\n",
               i, allowed ? "YES" : "NO ", degraded ? "YES" : "NO ", cost, limiter.current_spent_sec);
    }

    printf("Summary: Total=%lu, Rejected=%lu, Degraded=%lu\n",
           (unsigned long)limiter.total_requests,
           (unsigned long)limiter.rejected_requests,
           (unsigned long)limiter.degraded_requests);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string_view>
#include <array>
#include <numeric>
#include <expected>

enum class ResourceCostTier : std::size_t {
    Light = 0,    // Просте читання з кешу
    Medium = 1,   // Запит до бази даних
    Heavy = 2,    // Складна аналітика / транзакція
    Gpu = 3       // ML-інференс / GPU
};

struct RequestMetrics {
    ResourceCostTier tier;
    std::uint32_t cpu_time_ms;
    std::uint32_t storage_ops;
    std::uint32_t net_bytes;
};

struct CostModelConfig {
    double cpu_cost_per_ms{0.00002};
    double storage_cost_per_op{0.0001};
    double net_cost_per_byte{0.00000005};
    double max_budget_per_sec{0.10};
    double degradation_threshold{0.80};
};

struct AllocationFailure {
    double cost;
    bool is_degraded;
};

class CostLimiter {
public:
    explicit CostLimiter(CostModelConfig config) : config_(std::move(config)) {}

    [[nodiscard]] double calculate_cost(const RequestMetrics& metrics) const noexcept {
        constexpr std::array<double, 4> tier_base_costs{0.0001, 0.0010, 0.0100, 0.0500};
        const double base = tier_base_costs[static_cast<std::size_t>(metrics.tier)];
        const double variable = (metrics.cpu_time_ms * config_.cpu_cost_per_ms) +
                                (metrics.storage_ops * config_.storage_cost_per_op) +
                                (metrics.net_bytes * config_.net_cost_per_byte);
        return base + variable;
    }

    [[nodiscard]] std::expected<double, AllocationFailure> try_consume(const RequestMetrics& metrics) noexcept {
        total_requests_++;
        const double cost = calculate_cost(metrics);
        const double spent_ratio = current_spent_sec_ / config_.max_budget_per_sec;

        const bool is_heavy = (metrics.tier == ResourceCostTier::Heavy || metrics.tier == ResourceCostTier::Gpu);
        if (spent_ratio >= config_.degradation_threshold && is_heavy) {
            degraded_requests_++;
            rejected_requests_++;
            return std::unexpected(AllocationFailure{cost, true});
        }

        if (current_spent_sec_ + cost > config_.max_budget_per_sec) {
            rejected_requests_++;
            return std::unexpected(AllocationFailure{cost, false});
        }

        current_spent_sec_ += cost;
        return cost;
    }

    void reset_window() noexcept {
        current_spent_sec_ = 0.0;
    }

    [[nodiscard]] double current_spent() const noexcept { return current_spent_sec_; }
    [[nodiscard]] std::uint64_t total_requests() const noexcept { return total_requests_; }
    [[nodiscard]] std::uint64_t rejected_requests() const noexcept { return rejected_requests_; }
    [[nodiscard]] std::uint64_t degraded_requests() const noexcept { return degraded_requests_; }

private:
    CostModelConfig config_;
    double current_spent_sec_{0.0};
    std::uint64_t total_requests_{0};
    std::uint64_t rejected_requests_{0};
    std::uint64_t degraded_requests_{0};
};

int main() {
    CostModelConfig config{.max_budget_per_sec = 0.10, .degradation_threshold = 0.80};
    CostLimiter limiter(config);

    std::cout << "=== Cost-Aware Infrastructure Allocator (C++23) ===\n";

    const std::vector<RequestMetrics> requests{
        {ResourceCostTier::Heavy, 15, 2, 4096},
        {ResourceCostTier::Heavy, 15, 2, 4096},
        {ResourceCostTier::Heavy, 15, 2, 4096},
        {ResourceCostTier::Heavy, 15, 2, 4096},
        {ResourceCostTier::Heavy, 15, 2, 4096},
        {ResourceCostTier::Heavy, 15, 2, 4096}
    };

    for (std::size_t i = 0; const auto& req : requests) {
        i++;
        if (auto result = limiter.try_consume(req); result.has_value()) {
            std::cout << "Request #" << i << " [HEAVY]: Allowed=YES, Cost=$" 
                      << *result << ", TotalSpent=$" << limiter.current_spent() << "\n";
        } else {
            const auto& err = result.error();
            std::cout << "Request #" << i << " [HEAVY]: Allowed=NO , Cost=$" 
                      << err.cost << " (Degraded=" << (err.is_degraded ? "YES" : "NO") << ")\n";
        }
    }

    std::cout << "Summary: Total=" << limiter.total_requests()
              << ", Rejected=" << limiter.rejected_requests()
              << ", Degraded=" << limiter.degraded_requests() << "\n";

    return 0;
}
```
:::

## 4. Аналіз покрокового виконання та інженерні крайові випадки

### Покроковий розбір виконання

1. **Ініціалізація моделей тарифів:** Конфігурація задає вартість мілісекунди обчислювального часу CPU ($0.00002), операції зчитування диска ($0.0001) та байта мережевого трафіку ($0.00000005). Бюджет секунди обмежено сумою $0.10.
2. **Обчислення вартості запиту `HEAVY`:** Для 15 мс CPU, 2 операцій I/O та 4 КБ мережевого трафіку базова вартість становить $0.0100. Змінна вартість розраховується як `(15 × 0.00002) + (2 × 0.0001) + (4096 × 0.00000005) = 0.00030 + 0.00020 + 0.00020 = 0.00070`. Загальна вартість одного запиту становить `$0.01070`.
3. **Обробка потоку запитів:** Запити 1-7 проходять успішно, накопичуючи витрати до `$0.07490`.
4. **Спрацювання порогу деградації:** Запит 8 збільшує витрати до `$0.08560`, що перевищує поріг деградації у 80% ($0.0800). Далі система автоматично відхиляє наступні важкі запити `HEAVY` з позначкою `Degraded=YES`, зберігаючи решту 20% бюджету ($0.01440) для легких запитів `LIGHT`.

### Простеження викликів та моніторинг у Prometheus

Для того щоб вартісно-свідомий обмежувач не працював як непрозорий «чорний ящик», кожна операція споживання бюджету супроводжується моніторинговими метриками. У виробничих системах обмежувач експортує наступні три ключові показники:

- `infrastructure_cost_dollars_total`: Лічильник (Counter), який підсумовує загальну фінансову вартість виконаних запитів з розбиттям за мітками `tier` та `service`.
- `infrastructure_budget_burn_ratio`: Гейдж (Gauge), що відображає поточний відсоток використання бюджету секунди (`current_spent_sec / max_budget_per_sec`).
- `infrastructure_degraded_requests_total`: Лічильник заблокованих або відхилених запитів у режимі захисту бюджету.

Приклад вигрузки метрик у форматі OpenMetrics/Prometheus:

```text
# HELP infrastructure_cost_dollars_total Total accumulated infrastructure cost in USD.
# TYPE infrastructure_cost_dollars_total counter
infrastructure_cost_dollars_total{tier="heavy",service="analytics"} 0.08560

# HELP infrastructure_budget_burn_ratio Current budget burn ratio (0.0 to 1.0).
# TYPE infrastructure_budget_burn_ratio gauge
infrastructure_budget_burn_ratio{window="1s"} 0.856

# HELP infrastructure_degraded_requests_total Total requests rejected due to SLA degradation.
# TYPE infrastructure_degraded_requests_total counter
infrastructure_degraded_requests_total{tier="heavy"} 1
```

### Архітектура інтеграції з API Gateway (Envoy / NGINX Filter)

У реальній хмарній інфраструктурі вартісно-свідомий обмежувач виноситься на рівень **API Gateway** (наприклад у формі WebAssembly-плагіна для Envoy Proxy або Lua-модуля для NGINX). Це дозволяє відсікати занадто дорогі запити ще до того, як вони досягнуть внутрішніх мікросервісів та витратять процесорний час бекенду.

Схема інтеграції на шлюзі:

```
[Клієнтський HTTP-запит] ──► [API Gateway (Envoy + WASM Filter)]
                                        │
                                        ▼ (Перевірка розрахованого тагового ліміту)
                             ┌───────────────────────┐
                             │ CostLimiter Check     │
                             └──────────┬────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
          [Дозволено]                                   [Перевищено бюджет]
                 │                                             │
                 ▼                                             ▼
    [Маршрутизація у сервіс]                      [Відповідь HTTP 429 Retry-After]
```

### Пастки реалізації у високонавантажених системах

1. **Неатомарність оновлення лічильників у багатопоточному середовищі:** У реальному сервері декілька робочих потоків (worker threads) одночасно звертаються до `limiter.current_spent_sec`. Використання звичайного дійсного числа `double` без атомарних операцій (`std::atomic<double>`) або м'ютекса призводить до race condition і перевищення бюджету.
2. **Оверхед самих вимірювань:** Якщо розраховувати вартість запиту на кожному етапі його проходження крізь 10 мікросервісів, обчислювальні витрати на сам облік можуть перевищити корисну роботу. Для високонавантажених систем застосовують імовірнісне семплювання метрик (probabilistic sampling).
3. **Жорстке відключення замість м'якого повернення:** Якщо обмежувач повертає голий `500 Internal Server Error`, клієнтські бібліотеки починають алігаторські повторні спроби (aggressive retries), що збільшує навантаження. Обмежувач мусить повертати заголовок `Retry-After: <seconds>` та статус `429 Too Many Requests`.
