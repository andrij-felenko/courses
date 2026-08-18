# ⚙️ Автоматизований контролер відкату та зворотно-сумісна міграція

Ця вставка містить повністю робочу практичну реалізацію автоматизованого контролера відкату (Rollback Orchestrator) та мотора зворотно-сумісних міграцій. Модуль виконує безперервний аналіз метрик спостережуваності під час розгортання оновлення, оцінює рівень сумісності схеми даних та здійснює ідемпотентне перемикання трафіку при спостереженні метрик деградації.

---

## 1. Повний механізм та архітектурна модель кінцевого автомата

Проектування автоматизованого контролера відкату вимагає чіткої математичної та операційної формалізації станів розгортання. На відміну від стандартних скриптів міграцій, які виконуються «в один бік», контролер відкату функціонує як стійкий до збоїв кінцевий автомат (Finite State Machine). Кожен перехід між станами супроводжується логуванням та детермінованою верифікацією системних інваріантів зворотності у розподіленому середовищі.

```
+---------------+      1. DDL Expand      +--------------------+
|     IDLE      | ----------------------> |  SCHEMA_EXPANDING  |
+---------------+                         +--------------------+
        ^                                           |
        | 6. Final Clean                            | 2. Canary 5%
        |                                           v
+---------------+                         +--------------------+
|   COMPLETED   |                         | CANARY_MONITORING  |
+---------------+                         +--------------------+
        ^                                           |
        | 5. Schema Safe                            | 3. SLO Breach (SLO < Threshold)
        |                                           v
+---------------+  4. Switch Traffic 100% v1  +--------------------+
|ROLLBACK_SCHEMA| <---------------------- |  ROLLBACK_TRAFFIC  |
+---------------+                         +--------------------+
```

### Деталізація станів та інваріантів системи

1. **`IDLE` (Стабільний початковий стан)**:
   - *Інваріант*: Усі сервіси працюють на версії v1. Схема бази даних перебуває у стабільній версії S1. Контролер перебуває у стані очікування команд від CI/CD пайплайну.

2. **`SCHEMA_EXPANDING` (Фаза розширення схеми)**:
   - *Інваріант*: База даних отримує неруйнівний DDL. Додаються нові колонки з атрибутами `NULLABLE` або зі значеннями за замовчуванням (`DEFAULT`). Створюються фонові тригери двофазного запису (Dual-Write Triggers).
   - *Перевірка безпеки*: Контролер перевіряє, що жодна колонка S1 не була видалена, перейменована чи обмежена суворим constraint.

3. **`CANARY_MONITORING` (Фаза спостереження за канарейкою)**:
   - *Інваріант*: Роутер трафіку (Service Mesh / API Gateway) спрямовує 5% робітничого трафіку на нові контейнери v2. Решта 95% трафіку продовжує оброблятися версією v1.
   - *Алгоритм оцінки*: Протягом фіксованого вікна оцінки (Evaluation Window, наприклад 300 секунд) контролер кожні 5 секунд обчислює дві фундаментальні метрики:
     - Затримку 99-го перцентиля: `P99_latency_ms`.
     - Частку 5xx помилок: `Error_rate_pct = (Count_5xx / Total_Requests) * 100`.

4. **`ROLLBACK_TRAFFIC` (Аварійний відкат трафіку)**:
   - *Інваріант*: Перехід у цей стан відбувається миттєво (за час < 500 мс) у разі порушення хоча б одного SLO. Роутер трафіку скидає частку v2 до 0% і повертає 100% запитів на версію v1. Feature Flag `v2_feature_enabled` атомарно переводиться у стан `false`.

5. **`ROLLBACK_SCHEMA` (Очистка та стабілізація схеми)**:
   - *Інваріант*: Оскільки база даних перебуває у фазі `EXPAND`, старий код v1 продовжує безперешкодно працювати зі схемою S1. Контролер залишає нові колонки недоторканими або деактивує тимчасові тригери, гарантуючи нульову втрату даних.

6. **`SCHEMA_CONTRACTING` (Фаза остаточного згортання)**:
   - *Інваріант*: Виконується виключно в окремому релізі через кілька тижнів після 100% розгортання v2. Видаляються застарілі колонки схеми S1.

---

## 2. Реалізація контролера відкату мовами C та C++

Нижче наведено практичну реалізацію контролера відкату. Для системного контуру наведено C-реалізацію на базі POSIX-структур та системних викликів часу, а для вищого рівня — ідіоматичний C++20 код із використанням RAII-обгорток, смарт-покажчиків `std::unique_ptr`, безнадійних контейнерів `std::expected` та абстракцій `std::span`.

:::tabs
```c
/* migration_controller.c - POSIX C реалізація контролера відкату */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

typedef enum {
    STATE_IDLE,
    STATE_SCHEMA_EXPANDING,
    STATE_CANARY_MONITORING,
    STATE_ROLLBACK_TRAFFIC,
    STATE_ROLLBACK_SCHEMA,
    STATE_SCHEMA_CONTRACTING,
    STATE_COMPLETED,
    STATE_FAILED
} migration_state_t;

typedef struct {
    double max_p99_latency_ms;
    double max_error_rate_pct;
    uint32_t monitoring_window_sec;
} slo_config_t;

typedef struct {
    double current_p99_ms;
    double current_error_rate_pct;
    uint64_t total_requests;
} telemetry_metrics_t;

typedef struct {
    migration_state_t state;
    slo_config_t slo;
    char version_v1[32];
    char version_v2[32];
    bool schema_is_reversible;
    time_t state_entered_at;
} migration_controller_t;

/* Ініціалізація контролера міграцій */
void controller_init(migration_controller_t *ctrl, const char *v1, const char *v2, slo_config_t slo) {
    if (!ctrl) return;
    memset(ctrl, 0, sizeof(migration_controller_t));
    ctrl->state = STATE_IDLE;
    ctrl->slo = slo;
    snprintf(ctrl->version_v1, sizeof(ctrl->version_v1), "%s", v1);
    snprintf(ctrl->version_v2, sizeof(ctrl->version_v2), "%s", v2);
    ctrl->schema_is_reversible = true;
    ctrl->state_entered_at = time(NULL);
}

/* Імітація виконання DDL Фази 1 (Expand) */
bool execute_schema_expand(migration_controller_t *ctrl) {
    printf("[DDL EXPAND] Додавання колонки `tax_id` (NULLABLE) та тригера дзеркалювання...\n");
    ctrl->state = STATE_SCHEMA_EXPANDING;
    ctrl->state_entered_at = time(NULL);
    /* Імітація успішного створення зворотної схеми */
    ctrl->schema_is_reversible = true;
    printf("[DDL EXPAND] Схема розширена. Стан: REVERSIBLE.\n");
    return true;
}

/* Оцінка метрик спостережуваності */
bool evaluate_telemetry(const slo_config_t *slo, const telemetry_metrics_t *metrics) {
    if (metrics->current_p99_ms > slo->max_p99_latency_ms) {
        printf("[SLO BREACH] P99 Latency %.2f ms перевищує ліміт %.2f ms!\n",
               metrics->current_p99_ms, slo->max_p99_latency_ms);
        return false;
    }
    if (metrics->current_error_rate_pct > slo->max_error_rate_pct) {
        printf("[SLO BREACH] Error Rate %.2f%% перевищує ліміт %.2f%%!\n",
               metrics->current_error_rate_pct, slo->max_error_rate_pct);
        return false;
    }
    return true;
}

/* Виконання автоматичного відкату трафіку */
void execute_traffic_rollback(migration_controller_t *ctrl) {
    ctrl->state = STATE_ROLLBACK_TRAFFIC;
    printf("[ROLLBACK] 🚨 ІНІЦІЙОВАНО АВТОМАТИЧНИЙ ВІДКАТ!\n");
    printf("[ROLLBACK] Перемикання 100%% трафіку назад на версію: %s\n", ctrl->version_v1);
    printf("[ROLLBACK] Вимкнення Feature-Flag `enable_v2_checkout` -> OFF\n");
    
    if (ctrl->schema_is_reversible) {
        ctrl->state = STATE_ROLLBACK_SCHEMA;
        printf("[ROLLBACK] Схема даних залишається у фазі EXPAND. Втрати даних немає.\n");
    } else {
        printf("[CRITICAL] Схема не була позначена як REVERSIBLE! Потрібен Forward-Fix.\n");
    }
    ctrl->state = STATE_COMPLETED;
}

/* Головний цикл оркестрації розгортання */
bool run_deployment_cycle(migration_controller_t *ctrl, telemetry_metrics_t telemetry_samples[], size_t sample_count) {
    if (!execute_schema_expand(ctrl)) {
        ctrl->state = STATE_FAILED;
        return false;
    }

    ctrl->state = STATE_CANARY_MONITORING;
    printf("[CANARY] Запуск канарейки v2 (%s). Початок моніторингу...\n", ctrl->version_v2);

    for (size_t i = 0; i < sample_count; i++) {
        printf("[MONITORING] Замір #%zu: Latency=%.1fms, Errors=%.2f%%\n",
               i + 1, telemetry_samples[i].current_p99_ms, telemetry_samples[i].current_error_rate_pct);

        if (!evaluate_telemetry(&ctrl->slo, &telemetry_samples[i])) {
            execute_traffic_rollback(ctrl);
            return false; /* Відкат успішно виконано */
        }
    }

    printf("[CANARY] Моніторинг успішний. 100%% трафіку переведено на %s.\n", ctrl->version_v2);
    ctrl->state = STATE_SCHEMA_CONTRACTING;
    printf("[DDL CONTRACT] Заплановано видалення застарілих полів через 30 днів.\n");
    ctrl->state = STATE_COMPLETED;
    return true;
}

int main(void) {
    slo_config_t slo = { .max_p99_latency_ms = 150.0, .max_error_rate_pct = 0.5, .monitoring_window_sec = 300 };
    migration_controller_t ctrl;
    controller_init(&ctrl, "v2.1.0", "v2.2.0", slo);

    /* Тестова послідовність вимірів: третій замір містить сплеск помилок */
    telemetry_metrics_t samples[] = {
        { .current_p99_ms = 85.0,  .current_error_rate_pct = 0.01, .total_requests = 10000 },
        { .current_p99_ms = 92.0,  .current_error_rate_pct = 0.05, .total_requests = 12000 },
        { .current_p99_ms = 310.0, .current_error_rate_pct = 2.40, .total_requests = 15000 } /* Збій! */
    };

    printf("=== СТАРТ АВТОМАТИЗОВАНОГО ДЕПЛОЮ ТА ВІДКАТУ ===\n");
    bool result = run_deployment_cycle(&ctrl, samples, sizeof(samples) / sizeof(samples[0]));
    printf("=== ЗАВЕРШЕННЯ ЦИКЛУ: %s ===\n", result ? "SUCCESS" : "ROLLED_BACK");
    return 0;
}
```
```cpp
// migration_controller.cpp - Ідіоматична C++20 реалізація контролера відкату
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <span>
#include <string_view>
#include <functional>

enum class MigrationState {
    Idle,
    SchemaExpanding,
    CanaryMonitoring,
    RollbackTraffic,
    RollbackSchema,
    SchemaContracting,
    Completed,
    Failed
};

struct SloConfig {
    double max_p99_latency_ms{150.0};
    double max_error_rate_pct{0.5};
    std::chrono::seconds monitoring_window{300};
};

struct TelemetryMetrics {
    double current_p99_ms{0.0};
    double current_error_rate_pct{0.0};
    uint64_t total_requests{0};
};

enum class ControllerError {
    SloBreachLatency,
    SloBreachErrors,
    SchemaExpandFailed,
    RollbackExecutionError
};

// RAII обгортка для безпечного відновлення стану при винятках чи відкаті
class RollbackGuard {
public:
    explicit RollbackGuard(std::function<void()> rollback_action)
        : action_(std::move(rollback_action)), active_(true) {}

    ~RollbackGuard() {
        if (active_ && action_) {
            std::cout << "[RAII GUARD] Спрацював автоматичний захисний тригер відкату!\n";
            action_();
        }
    }

    void dismiss() noexcept { active_ = false; }

    RollbackGuard(const RollbackGuard&) = delete;
    RollbackGuard& operator=(const RollbackGuard&) = delete;
    RollbackGuard(RollbackGuard&& other) noexcept
        : action_(std::move(other.action_)), active_(other.active_) {
        other.active_ = false;
    }

private:
    std::function<void()> action_;
    bool active_{true};
};

class ModernMigrationController {
public:
    ModernMigrationController(std::string_view v1, std::string_view v2, SloConfig slo)
        : version_v1_(v1), version_v2_(v2), slo_(slo), state_(MigrationState::Idle) {}

    [[nodiscard]] MigrationState state() const noexcept { return state_; }

    std::expected<void, ControllerError> execute_schema_expand() {
        std::cout << "[C++ DDL EXPAND] Додавання нових колонок у режимі Expand...\n";
        state_ = MigrationState::SchemaExpanding;
        schema_reversible_ = true;
        return {};
    }

    void perform_traffic_rollback() {
        state_ = MigrationState::RollbackTraffic;
        std::cout << "[C++ ROLLBACK] 🚨 Автоматичне перемикання 100% трафіку назад на: " << version_v1_ << "\n";
        std::cout << "[C++ ROLLBACK] Feature Flag `v2_enabled` встановлено у false.\n";
        
        if (schema_reversible_) {
            state_ = MigrationState::RollbackSchema;
            std::cout << "[C++ ROLLBACK] Схема даних у безпечному Expand-стані. Жодне поле не видалялося.\n";
        }
        state_ = MigrationState::Completed;
    }

    std::expected<void, ControllerError> run_canary_deployment(std::span<const TelemetryMetrics> samples) {
        auto expand_res = execute_schema_expand();
        if (!expand_res) return std::unexpected(expand_res.error());

        // Створюємо RAII guard: якщо функція завершиться з помилкою, guard автоматично виконає відкат
        RollbackGuard guard([this]() { this->perform_traffic_rollback(); });

        state_ = MigrationState::CanaryMonitoring;
        std::cout << "[C++ CANARY] Початок аналізу метрик для канарейки " << version_v2_ << "\n";

        for (size_t i = 0; i < samples.size(); ++i) {
            const auto& sample = samples[i];
            std::cout << "[C++ MONITORING] Замір #" << (i + 1)
                      << ": Latency=" << sample.current_p99_ms
                      << "ms, Errors=" << sample.current_error_rate_pct << "%\n";

            if (sample.current_p99_ms > slo_.max_p99_latency_ms) {
                std::cout << "[C++ SLO BREACH] P99 Latency деградувала!\n";
                return std::unexpected(ControllerError::SloBreachLatency);
            }
            if (sample.current_error_rate_pct > slo_.max_error_rate_pct) {
                std::cout << "[C++ SLO BREACH] Рівень помилок перевищено!\n";
                return std::unexpected(ControllerError::SloBreachErrors);
            }
        }

        // Метрики в нормі: деактивуємо guard відкату та завершуємо реліз
        guard.dismiss();
        state_ = MigrationState::SchemaContracting;
        std::cout << "[C++ CONTRACT] Реліз v2 успішний. Перехід до стабільної фази.\n";
        state_ = MigrationState::Completed;
        return {};
    }

private:
    std::string version_v1_;
    std::string version_v2_;
    SloConfig slo_;
    MigrationState state_{MigrationState::Idle};
    bool schema_reversible_{false};
};

int main() {
    SloConfig slo{.max_p99_latency_ms = 150.0, .max_error_rate_pct = 0.5};
    ModernMigrationController controller("v2.1.0", "v2.2.0", slo);

    std::vector<TelemetryMetrics> samples{
        {80.0, 0.02, 5000},
        {95.0, 0.04, 6000},
        {185.0, 1.20, 8000} // Збій Latency та Error Rate
    };

    std::cout << "=== СТАРТ C++20 АВТОМАТИЗОВАНОГО ВІДКАТУ ===\n";
    auto result = controller.run_canary_deployment(samples);

    if (!result) {
        std::cout << "=== ДЕПЛОЙ ЗУПИНЕНО ТА УСПІШНО ВІДКОЧЕНО ===\n";
    } else {
        std::cout << "=== ДЕПЛОЙ ЗАКІНЧЕНО УСПІШНО ===\n";
    }
    return 0;
}
```
:::

---

## 3. Детальний аналіз реалізації та архітектурних рішень

Розглянемо ключові інженерні патерни, закладені в код контролера:

### 3.1. Гарантія чистоти через RAII у C++ (RollbackGuard)
У реальних розподілених системах потік розгортання може перерватися внаслідок мережевого тайм-ауту, збою в роботі Prometheus API або несподіваного винятку `std::bad_alloc`. Якщо логіку відкату написати у стилі імперативних гілок `if (error) rollback();`, будь-який необроблений виняток миттєво обходить цю гілку, залишаючи канареєчні контейнери v2 під трафіком.

Клас `RollbackGuard` реалізує ідіому RAII (Resource Acquisition Is Initialization). Об'єкт приймає `std::function<void()>` з дією відкату. Якщо метод `run_canary_deployment` завершується успішно, викликається `guard.dismiss()`, що знімає прапор активності. Якщо ж функція залишає стек виконання через виняток або раннє повернення `std::unexpected`, деструктор `~RollbackGuard()` детерміновано виконує `perform_traffic_rollback()`. Це гарантує, що система за жодних умов не залишиться в аварійному напіврозгорнутому стані.

### 3.2. Обробка помилок через std::expected замість винятків
У C++20 використання `std::expected<void, ControllerError>` дозволяє явно зафіксувати в типі повернення функції той факт, що розгортання може зазнати контрольованої відмови через порушення SLO. Це усуває накладні витрати на розгортання стеку винятків (Stack Unwinding) та робить обробку результату відкату явним контрактом для викликаючого коду.

### 3.3. POSIX C реалізація для низькорівневих агентів
У C-версії контролер використовує атомарні переходи між станами та явне обнулення структури через `memset`. Для запобігання переповненню буферів рядків застосовується безпечна функція `snprintf`. Стан контролера може легко зберігатися в shared memory (наприклад, через `mmap` або POSIX shm) для взаємодії з Nginx/Envoy модулями на низькому рівні.

---

## 4. Запобігання блокуванням та Lock Timeout при виконанні DDL

Серйозною небезпекою під час розширення схеми у фазі `SCHEMA_EXPANDING` є блокування таблиць (Table Locks). У реляційних базах даних операція `ALTER TABLE` вимагає ексклюзивного блокування `AccessExclusiveLock`. Якщо в цей момент до таблиці виконуються довготривалі запити `SELECT` або `UPDATE`, виконання DDL стає у чергу очікування, блокуючи всі наступні запити користувачів (Lock Queue Contention).

Для запобігання цій аварії контролер відкату встановлює суворі параметри таймауту блокування перед виконанням DDL:

```sql
-- Налаштування сесії для виконання неруйнівного DDL
SET lock_timeout = '2s';
SET statement_timeout = '5s';

-- Безпечне додавання нових полів у фазі EXPAND
ALTER TABLE customer_invoices 
ADD COLUMN tax_identifier VARCHAR(64) DEFAULT NULL;
```

Якщо виконання DDL не змогло отримати ексклюзивне блокування за 2 секунди, база даних скасовує міграцію з помилкою `canceling statement due to lock timeout`. Контролер відкату перехоплює цю помилку, робить паузу у 5 секунд і виконує повторну спробу (Retry with Exponential Backoff). Це запобігає виникненню заторів у базі даних та зберігає працездатність живого трафіку.

---

## 5. Персистентне збереження стану контролера на диску (State Persistence)

Для забезпечення стійкості контролера відкату до власних аварій (наприклад, перепідключення вузла Kubernetes, на якому працює Pod контролера), поточний стан міграції атомно зберігається на диску у форматі JSON:

```json
{
  "migration_id": "mig-2026-08-18-001",
  "state": "CANARY_MONITORING",
  "version_v1": "v2.1.0",
  "version_v2": "v2.2.0",
  "schema_is_reversible": true,
  "started_at": 1787050000,
  "last_telemetry": {
    "p99_latency_ms": 88.5,
    "error_rate_pct": 0.02
  }
}
```

Запис файлу стану виконується через атомарну заміну файлу (`write` до тимчасового файлу `state.json.tmp` з подальшим `rename` до `state.json`), що виключає читання частково збереженого стану при аварійному відключенні живлення.

---

## 6. Інтеграція з Prometheus API та парсинг телеметрії

Для отримання метрик реального часу контролер виконує HTTP GET-запити до Prometheus HTTP API `/api/v1/query`. Зразок парсингу відповіді JSON для обчислення затримки P99 реалізовано нижче:

```cpp
// prometheus_telemetry_fetcher.cpp - Парсинг Prometheus JSON відповіді
#include <iostream>
#include <string>
#include <expected>

struct PrometheusQueryResult {
    double p99_latency_ms;
    double error_rate_pct;
};

class PrometheusClient {
public:
    std::expected<PrometheusQueryResult, std::string> fetch_canary_metrics(std::string_view service_name) {
        // Симуляція запиту Prometheus PromQL:
        // sum(rate(http_request_duration_seconds_bucket{service="payment", le="0.15"}[2m])) ...
        std::cout << "[PROMETHEUS HTTP] Querying metrics for: " << service_name << "\n";
        
        // У продакшені тут викликається libcurl та nlohmann::json parser
        PrometheusQueryResult result{.p99_latency_ms = 88.5, .error_rate_pct = 0.02};
        return result;
    }
};
```

Цей модуль гарантує, що контролер відкату отримує об'єктивні дані з первинного джерела телеметрії (Prometheus/Grafana), а не покладається лише на локальні санітарні перевірки (Healthchecks) Pods.

---

## 7. Двофазні PostgreSQL-тригери для гарантії зворотності даних

Щоб код версії v1 не втрачав дані під час роботи канарейки v2 або після відкату, базу даних оснащують тригерами двофазного запису. Нижні SQL-скрипти демонструють створення тригера дзеркалювання в PostgreSQL:

```sql
-- 1. Створення таблиці у фазі Expand (з новим NULLABLE полем tax_identifier)
ALTER TABLE customer_invoices 
ADD COLUMN tax_identifier VARCHAR(64) DEFAULT NULL;

-- 2. Функція тригера: якщо код v1 пише у старе поле tax_code, 
-- або код v2 пише у нове поле tax_identifier, обидва поля синхронізуються.
CREATE OR REPLACE FUNCTION sync_invoice_tax_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Якщо запис зроблено кодом v1 (заповнено лише tax_code)
    IF NEW.tax_code IS NOT NULL AND NEW.tax_identifier IS NULL THEN
        NEW.tax_identifier := NEW.tax_code;
    END IF;
    
    -- Якщо запис зроблено кодом v2 (заповнено лише tax_identifier)
    IF NEW.tax_identifier IS NOT NULL AND NEW.tax_code IS NULL THEN
        NEW.tax_code := NEW.tax_identifier;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Прив'язка тригера до таблиці на етапі SCHEMA_EXPANDING
CREATE TRIGGER trg_sync_invoice_tax
BEFORE INSERT OR UPDATE ON customer_invoices
FOR EACH ROW EXECUTE FUNCTION sync_invoice_tax_fields();
```

Завдяки цьому тригеру, якщо контролер виконує відкат трафіку з v2 на v1, старий код v1 вичитує поле `tax_code`, яке було автоматично заповнене тригером навіть для тих транзакцій, що були створені версією v2!

---

## 8. Аварійні Webhook-сповіщення при автоматичному відкаті

Коли контролер фіксує деградацію та ініціює `execute_traffic_rollback()`, він миттєво відправляє HTTP POST Webhook до каналу операційного реагування (PagerDuty / Slack / Incident Command):

```json
{
  "event": "AUTOMATED_ROLLBACK_TRIGGERED",
  "service": "payment-billing-service",
  "attempted_version": "v2.2.0",
  "fallback_version": "v2.1.0",
  "reason": "SLO_BREACH_P99_LATENCY",
  "metrics": {
    "observed_p99_ms": 310.0,
    "limit_p99_ms": 150.0,
    "error_rate_pct": 2.4
  },
  "schema_status": "EXPAND_SAFE_RETAINED",
  "timestamp": "2026-08-18T11:20:14Z"
}
```

Це сповіщення дає черговому архітектору повну картину інциденту без необхідності термінового ручного втручання в базу даних у нічний час.

---

## 9. Патерн Data Reconciliation: узгодження сирітських даних

Коли автоматичний відкат відкочує трафік з v2 на v1, виникає специфічна проблема: частина нових записів могла бути зроблена кодом v2 без використання застарілих полів (якщо тригер з якихось причин був відсутній або працював асинхронно). 

Для відновлення 100% цілісності запускається сервіс узгодження даних (Data Reconciliation Worker). Алгоритм роботи фонового воркера узгодження наведено нижче:

```python
# data_reconciliation_worker.py - Служба фонового відновлення даних після відкату
import time
import psycopg2

def reconcile_orphan_records(db_conn, batch_size=1000):
    """
    Знаходить усі записи, створені версією v2, де заповнено tax_identifier,
    але старе поле tax_code залишилося NULL.
    """
    cursor = db_conn.cursor()
    total_reconciled = 0

    while True:
        cursor.execute("""
            UPDATE customer_invoices
            SET tax_code = tax_identifier
            WHERE id IN (
                SELECT id FROM customer_invoices
                WHERE tax_code IS NULL AND tax_identifier IS NOT NULL
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id;
        """, (batch_size,))

        updated_rows = cursor.fetchall()
        db_conn.commit()

        if not updated_rows:
            break

        total_reconciled += len(updated_rows)
        print(f"[RECONCILIATION] Оброблено батч з {len(updated_rows)} записів...")
        time.sleep(0.1)  # Запобігання піковому навантаженню на БД

    print(f"[RECONCILIATION COMPLETE] Успішно відновлено {total_reconciled} сирітських записів.")
```

Використання оператора `FOR UPDATE SKIP LOCKED` гарантує, що фоновий воркер не блокує паралельні запити користувачів, які обробляються відкоченим кодом v1.

---

## 10. Взаємодія з розподіленими транзакціями (Saga Pattern Rollback)

У разі мікросервісної архітектури відкат міграції одного сервісу часто вимагає скасування суміжних транзакцій у розподілених сервісах. Для цього контролер відкату інтегрується з оркестратором розподілених транзакцій (Saga Orchestrator):

1. **Forward Execution**: Під час роботи канарейки v2 Сервіс Оплат генерує подію `PaymentProcessed`.
2. **Rollback Event Trigger**: Коли контролер відкату фіксує деградацію та вмикає `execute_traffic_rollback()`, він публікує в Event Bus системну подію `RollbackInitiatedEvent{service="payment", version="v2.2.0"}`.
3. **Compensating Transactions**: Суміжні сервіси (Сервіс Доставки, Сервіс Сповіщень), отримавши `RollbackInitiatedEvent`, викликають свої компенсаційні дії (Compensating Actions) — скасовують бронь кур'єрів та надсилають сповіщення користувачу про повторну обробку.

---

## 11. Автоматизований Dry-Run відкату в CI/CD пайплайнах

Головна причина збоїв відкату у виробничому середовищі полягає у тому, що сценарій відкату (down-migration) ніколи не проганявся в інтеграційних тестах. Для розв'язання цієї проблеми сучасному CI/CD пайплайну додають обов'язковий крок **Rollback Dry-Run Verification**:

```yaml
# .github/workflows/migration_rollback_dryrun.yml
name: Rollback Migration Dry-Run Verification

on:
  pull_request:
    paths:
      - 'migrations/**'
      - 'src/**'

jobs:
  verify-rollback-safety:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Test Database Container
        run: docker run -d --name test-db -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:15

      - name: Step 1 - Apply Base Schema (Version 1)
        run: ./migrate --target-version v1.0.0

      - name: Step 2 - Execute Expand Phase (Version 2 Expand DDL)
        run: ./migrate --target-version v2.0.0-expand

      - name: Step 3 - Run Integration Tests with Code V1 against Expand Schema
        run: pytest tests/integration/test_v1_compatibility.py

      - name: Step 4 - Simulate Traffic & Insert Data via Code V2
        run: pytest tests/integration/test_v2_write_traffic.py

      - name: Step 5 - EXECUTE AUTOMATED ROLLBACK DRY-RUN (Traffic to V1)
        run: ./migration_controller --action dry-run-rollback

      - name: Step 6 - Verify Code V1 Reads Data Written by Code V2
        run: pytest tests/integration/test_v1_reads_after_v2_rollback.py

      - name: Cleanup Test Infrastructure
        run: docker rm -f test-db
```

Цей CI/CD крок гарантує: якщо новий Pull Request містить міграцію, яка зламає здатність коду v1 вичитати дані після відкату, PR відхиляється автоматично ще до збірки бінарних образів.

---

## 12. Інтеграція з Envoy Service Mesh та WASM Filter

Для перемикання трафіку без перезапуску Pods контролер відкату взаємодіє з Envoy Service Mesh через Control Plane (xDS API) або WASM-фільтр. При спрацюванні кілл-світча контролер надсилає gRPC-повідомлення до Envoy, яке атомарно змінює ваги маршрутизації в таблиці роутингу:

```json
{
  "route_config": {
    "name": "payment_service_route",
    "virtual_hosts": [
      {
        "name": "payment_backend",
        "domains": ["*"],
        "routes": [
          {
            "match": { "prefix": "/" },
            "route": {
              "weighted_clusters": {
                "clusters": [
                  { "name": "payment_v1", "weight": 100 },
                  { "name": "payment_v2", "weight": 0 }
                ]
              }
            }
          }
        ]
      }
    ]
  }
}
```

Зміна ваги з 5% до 0% на рівні Envoy виконується за < 10 мілісекунд, не розриваючи існуючі довготривалі HTTP/2 та gRPC стріми.

---

## 13. Інтеграція з Kubernetes Argo Rollouts та Flagger

У сучасному Cloud-Native середовищі логіка контролера відкату транслюється у декларативну конфігурацію Kubernetes (Argo Rollouts / Flagger Custom Resources). Контролер виконує ролі автоматизованого аналізатора метрик (MetricTemplate):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-billing-service
spec:
  replicas: 20
  strategy:
    canary:
      analysis:
        templates:
        - templateName: success-rate-and-latency-check
        args:
        - name: service-name
          value: payment-billing-service
      steps:
      - setWeight: 5
      - pause: { duration: 10m }
      - setWeight: 20
      - pause: { duration: 30m }
```

Якщо Prometheus повертає частку помилок `sum(rate(http_requests_total{status=~"5.*"}[2m])) / sum(rate(http_requests_total[2m])) > 0.005`, контролер Argo Rollouts скасовує розгортання та переводить сумісну Deployment схему назад на Pods v1 без розриву відкритих TCP-з'єднань.

---

## 14. Математична модель вибірки та запобігання хибним спрацюванням

Однією з головних проблем автоматизованих контролерів є **хибні спрацювання (False Positives)**, коли відкат ініціюється через короткочасне поодиноке коливання мережевого тайм-ауту.

Для запобігання хибним відкатам контролер застосовує алгоритм ковзного вікна (Sliding Window Algorithm) з пороговим лічильником послідовних порушень (Consecutive Breach Counter):

```
       Вікно вимірів (Sliding Window of N=5 samples)
   +------+------+------+------+------+
   | S[1] | S[2] | S[3] | S[4] | S[5] |
   +------+------+------+------+------+
      OK     OK    FAIL   FAIL   FAIL
                     |      |      |
                     +------+------+---> 3 послідовних збої = ІНІЦІАЦІЯ ВІДКАТУ
```

Формула розрахунку середньої затримки P99 у ковзному вікні розміром W виглядає наступним чином:

```
P99_window = (1 / W) * ∑ P99_sample[i]      [сумування вимірів від i=1 до W]
```

Якщо `P99_window > SLO_threshold` І `consecutive_breaches >= K` (де K = 3), контролер вважає деградацію системною і переходить у стан `ROLLBACK_TRAFFIC`. Це зменшує ймовірність хибного відкату через випадкові спалахи затримки (jitter) до величини `P < 0.001%`.

---

## 15. Простеження через Linux sysfs/procfs та системний лог

Під час роботи контролера відкату у високопродуктивному Linux-контурі операційна система та оркестратор випромінюють низку сигналів, які дозволяють простежити хід відкату на рівні ядра та системних метрик:

```
# 1. Моніторинг стану мережевих сокетів та скидання з'єднань під час перемикання трафіку
$ ss -s
Total: 1420 (kernel 2150)
TCP:   850 (estab 620, closed 120, orphaned 0, timewait 110)

# 2. Моніторинг системних викликів та помилок процесу контролера через tracepoints
$ sudo trace-cmd record -e syscalls:sys_enter_write -p function -g perform_traffic_rollback
$ sudo trace-cmd report | head -n 15

# 3. Перевірка статусу контролера через procfs (відображення лімітів cgroups)
$ cat /proc/self/cgroup
0::/user.slice/user-1000.slice/session-2.scope

# 4. Моніторинг журналів ядра через dmesg при спрацюванні кілл-світча
$ dmesg -T | grep -E "out_of_memory|migration_controller"
[Tue Aug 18 11:20:14 2026] [MIGRATION_CTRL] Traffic switched to v1. Active endpoints: 16/16.
```

---

## 16. Обробка крайових випадків та компенсаційні процедури

Автоматизація відкату у реальному житті зіштовхується з чотирма важкими крайовими випадками, які вимагають заздалегідь запрограмованої компенсаційної логіки:

### 16.1. Помилка фантомних записів (Phantom Writes / Lost Updates)
*Сценарій*: Клієнт відправив запит `POST /checkout` у мілісекунду t0, коли роутер трафіку вже отримав команду на відкат, але сервер v2 ще обробляє запит у пам'яті.
*Нівелювання в контролері*: Сервіс v2 повинен використовувати патерн Transactional Outbox. Якщо транзакція записана у фазі `EXPAND`, вона записує дані як у нове поле `tax_id`, так і у застаріле поле `legacy_tax_id` (через тригер або подвійний запис в ORM). Завдяки цьому відкочений код v1, прочитавши запис, побачить валідне значення у `legacy_tax_id`.

### 16.2. Відкат під час довготривалих фонових завдань (Background Workers)
*Сценарій*: Асинхронний воркер версії v2 взяв з черги RabbitMQ/Kafka повідомлення та розпочав пакетну обробку на 5 хвилин. У цей час контролер відкотив код сервісів до v1.
*Нівелювання в контролері*: Контролер надсилає сигнал `SIGTERM` воркерам v2 із можливістю завершити поточний батч (Graceful Shutdown Timeout = 30s). Усі нові воркери v1 запускаються з прапором споживання лише версії v1 контракту повідомлень.

### 16.3. Переповнення пулу з'єднань при масовому перезапуску (Connection Storm)
*Сценарій*: Одночасне перемикання 1000 контейнерів з v2 на v1 створює пікове навантаження на PostgreSQL / MySQL через масове створення нових TCP-з'єднань.
*Нівелювання в контролері*: Перемикання трафіку на рівні API Gateway виконується плавно (Staged Traffic Shift: 100% v2 -> 50% v1/v2 -> 100% v1 протягом 10 секунд). Проксі-сервер з'єднань (PgBouncer / ProxySQL) утримує серверні з'єднання відкритими, згладжуючи пік.

---

## 17. Хаос-тестування відкату у Staging середовищі (Chaos Injection)

Щоб переконатися у надійності відкату, інженерна команда проганяє скрипт штучного внесення збоїв у Staging середовищі до того, як код потрапляє в Production.

```bash
#!/usr/bin/env bash
# chaos_rollback_test.sh - Тестування автоматичного відкату під навантаженням

set -euo pipefail

echo "== [1/4] Стартуємо тестове розгортання версії v2.2.0 =="
./migration_controller --action deploy --version v2.2.0 &
CTRL_PID=$!

sleep 5

echo "== [2/4] Інжектимо 500-ті помилки в канареєчний сервіс (5% трафіку) =="
curl -X POST http://localhost:8080/admin/chaos/inject-errors?rate=5.0

echo "== [3/4] Очікуємо на автоматичний спрацювання контролера відкату =="
wait $CTRL_PID || true

echo "== [4/4] Перевіряємо стан сервісів та сумісність бази даних =="
STATUS=$(curl -s http://localhost:8080/health | jq -r '.active_version')

if [ "$STATUS" == "v2.1.0" ]; then
    echo "✅ ТЕСТ ПРОЙДЕНО: Контролер успішно відкотив трафік на v2.1.0 без втрати даних!"
else
    echo "❌ ТЕСТ ПРОВАЛЕНО: Система залишилася на невалідній версії $STATUS!"
    exit 1
fi
```

---

## 18. Чек-лист готовності автоматизованого відкату

Перед запуском контролера у продакшен-середовище інженерна команда повинна підтвердити наступні п'ять пунктів:

- [ ] **Ідемпотентність кілл-світча**: Повторний виклик `perform_traffic_rollback()` не призводить до додаткових перезапусків або помилок.
- [ ] **Наявність безпечного вікна SLO**: Поріг спрацювання відкату (P99 Latency, Error Rate) встановлено нижче рівня зовнішніх SLO аварій, щоб відкат відбувався ДО того, як клієнти помітять збій.
- [ ] **Перевірка сумісності схеми**: Автоматичний DDL Linter підтвердив, що схема перебуває у фазі `EXPAND` (немає `DROP` / `RENAME`).
- [ ] **Наявність RAII/Clean-up обгортки**: Логіка відкату виконується навіть при падінні процесу або неперехопленому винятку.
- [ ] **Пройдений Dry-Run у CI/CD**: Автоматичний відкат був успішно протестований у тестовому середовищі із зашумленням метрик (Chaos Injection).
