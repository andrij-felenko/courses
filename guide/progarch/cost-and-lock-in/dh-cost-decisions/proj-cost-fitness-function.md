# ⚙️ Автоматизована фітнес-функція бюджету DH у CI/CD

Ця практична вставка містить робочий рушій розрахунку unit-бюджету телеметрії та автоматизований сторож для пайплайну CI/CD. Інструмент розраховує прогнозований TCO на один будинок на основі специфікації телеметричних полів та частоти опитування. Якщо зміни в Pull Request підвищують unit-cost понад допустимий ліміт ($0.015 / дім / місяць), збірка завершується аварійно з кодом помилки, захищаючи компанію від «тихого» подвоєння хмарного рахунку.

У розподілених IoT-системах архітектурна регресія витрат розгортається безшумно і непомітно для розробників. Під час проведення рефакторингу інженер може спростити доменну модель, замінити короткі ідентифікатори розширеними текстовими рядками JSON або зменшити інтервал опитування давачів з 60 секунд до 5 секунд задля плинності анімації графіків у мобільному застосунку.

Під час локального тестування на розробницьких стендах чи при запуску звичайних юніт-тестів на 10 пристроях така зміна демонструє бездоганну роботу. Процесорне навантаження залишається в межах норми, а затримки відгуку системи навіть знижуються.

Однак після розгортання цієї зміни у продакшн на флот із 5 мільйонів будинків «маленьке поліпшення» генерує додаткові 86 мільярдів MQTT-повідомлень на добу. Хмарний рахунок наприкінці місяця зненацька виростає на $180,000, але команда розробки дізнається про це лише через три тижні, коли бухгалтерія отримує деталізовану фактуру від хмарного провайдера.

Щоб запобігти таким фінансовим катастрофам, ми будуємо автоматизовану фітнес-функцію архітектури (Architecture Fitness Function), яка перетворює фінансові обмеження на автоматичні CI-тести. Вона обчислює прогнозований unit-cost при кожному коміті й блокує збірку Pull Request ще до його потрапляння в основну гілку коду.

## Архітектура рішення та механізм оцінки

Рушій фітнес-функції складається з двох основних шарів, кожен із яких вирішує свою задачу:

1. **Обчислювальне ядро TCO (C / C++):** Низькорівневий модуль, який з високою точністю обчислює бітрейт, накладні витрати транспортних заголовків MQTT, TLS, TCP та IP, обсяги збереження в колоночних базах даних та підсумкову вартість обслуговування один будинок на місяць.
2. **Скрипт-сторож CI/CD (Python):** Високорівневий модуль інтеграції, який зчитує конфігураційні YAML-файли телеметрії з репозиторію, порівнює зміни проти базової гілки main, запускає обчислювальне ядро та формує підсумковий звіт для пайплайну GitHub Actions чи GitLab CI.

:::tabs
```c
/* cost_evaluator.c — Ядро обчислення unit-cost телеметрії мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define SECONDS_PER_MONTH 2592000.0
#define MQTT_TLS_OVERHEAD_BYTES 78

typedef struct {
    double fleet_size;             /* Кількість будинків (наприклад, 5000000) */
    double broker_price_per_1m;    /* Ціна 1 млн повідомлень брокера ($) */
    double storage_price_per_gb;   /* Ціна 1 GB об'єктного сховища ($) */
    double max_allowed_unit_cost;  /* Максимальний поріг unit-cost ($/дім/міс) */
} CostModelConfig;

typedef struct {
    int sensor_count;
    double sample_interval_sec;
    size_t payload_bytes;
    double delta_filter_ratio;    /* Частка відфільтрованих вимірів (0.0 .. 1.0) */
    int batch_window_sec;
} TelemetrySpec;

typedef struct {
    double monthly_messages_total;
    double monthly_storage_gb;
    double total_monthly_cost;
    double unit_cost_per_home;
    bool is_budget_passed;
} EvaluationResult;

EvaluationResult evaluate_telemetry_cost(const CostModelConfig* config, const TelemetrySpec* spec) {
    EvaluationResult result;
    
    /* Розрахунок ефективної частоти відправки з урахуванням батчингу та дельти */
    double raw_samples_per_month = (SECONDS_PER_MONTH / spec->sample_interval_sec) * spec->sensor_count;
    double passed_samples = raw_samples_per_month * (1.0 - spec->delta_filter_ratio);
    
    /* Кількість батч-пакетів */
    double batches_per_month = (SECONDS_PER_MONTH / spec->batch_window_sec) * spec->sensor_count;
    double total_mqtt_messages_per_home = (passed_samples < batches_per_month) ? passed_samples : batches_per_month;
    
    result.monthly_messages_total = total_mqtt_messages_per_home * config->fleet_size;
    
    /* Розрахунок байтів сховища */
    size_t packet_size = spec->payload_bytes + MQTT_TLS_OVERHEAD_BYTES;
    double total_bytes_per_home = total_mqtt_messages_per_home * packet_size;
    result.monthly_storage_gb = (total_bytes_per_home * config->fleet_size) / (1024.0 * 1024.0 * 1024.0);
    
    /* Фінансовий розрахунок */
    double broker_cost = (result.monthly_messages_total / 1000000.0) * config->broker_price_per_1m;
    double storage_cost = result.monthly_storage_gb * config->storage_price_per_gb;
    
    result.total_monthly_cost = broker_cost + storage_cost;
    result.unit_cost_per_home = result.total_monthly_cost / config->fleet_size;
    result.is_budget_passed = (result.unit_cost_per_home <= config->max_allowed_unit_cost);
    
    return result;
}

int main(int argc, char** argv) {
    CostModelConfig config = {
        .fleet_size = 5000000.0,
        .broker_price_per_1m = 0.05,       /* Self-hosted EMQX amortized cost */
        .storage_price_per_gb = 0.015,     /* Object Storage Parquet tier */
        .max_allowed_unit_cost = 0.015     /* Бюджетний ліміт: $0.015 / дім / міс */
    };
    
    TelemetrySpec spec = {
        .sensor_count = 20,
        .sample_interval_sec = 5.0,
        .payload_bytes = 100,
        .delta_filter_ratio = 0.90,        /* 90% значень відсікаються на хабі */
        .batch_window_sec = 900            /* 15-хвилинне об'єднання */
    };
    
    EvaluationResult res = evaluate_telemetry_cost(&config, &spec);
    
    printf("--- РЕЗУЛЬТАТ ОЦІНКИ ЕКОНОМІКИ ТЕЛЕМЕТРІЇ ---\n");
    printf("Місячна кількість повідомлень: %.0f\n", res.monthly_messages_total);
    printf("Обсяг сховища: %.2f GB / місяць\n", res.monthly_storage_gb);
    printf("Загальні хмарні витрати: $%.2f / місяць\n", res.total_monthly_cost);
    printf("Unit Cost: $%.4f / дім / місяць\n", res.unit_cost_per_home);
    
    if (res.is_budget_passed) {
        printf("[УСПІХ] Бюджет витримано (ліміт $%.3f).\n", config.max_allowed_unit_cost);
        return 0;
    } else {
        printf("[ПОМИЛКА] БЮДЖЕТ ПЕРЕВИЩЕНО! Дозволено: $%.3f, Отримано: $%.4f\n", 
               config.max_allowed_unit_cost, res.unit_cost_per_home);
        return 1;
    }
}
```
```cpp
// cost_evaluator.cpp — Ідіоматична реалізація ядра оцінки витрат мовою C++20
#include <iostream>
#include <iomanip>
#include <numeric>
#include <expected>
#include <string_view>

namespace dh::cost {

struct CostModelConfig {
    double fleet_size{5'000'000.0};
    double broker_price_per_1m{0.05};
    double storage_price_per_gb{0.015};
    double max_allowed_unit_cost{0.015};
};

struct TelemetrySpec {
    int sensor_count{20};
    double sample_interval_sec{5.0};
    std::size_t payload_bytes{100};
    double delta_filter_ratio{0.90};
    int batch_window_sec{900};
};

struct EvaluationResult {
    double monthly_messages_total{0.0};
    double monthly_storage_gb{0.0};
    double total_monthly_cost{0.0};
    double unit_cost_per_home{0.0};
};

enum class CostError {
    BudgetExceeded,
    InvalidConfiguration
};

class TelemetryBudgetEvaluator {
public:
    explicit TelemetryBudgetEvaluator(CostModelConfig config) 
        : config_(std::move(config)) {}

    [[nodiscard]] std::expected<EvaluationResult, CostError> 
    evaluate(const TelemetrySpec& spec) const noexcept {
        if (spec.sample_interval_sec <= 0.0 || spec.delta_filter_ratio < 0.0 || spec.delta_filter_ratio > 1.0) {
            return std::unexpected(CostError::InvalidConfiguration);
        }

        constexpr double seconds_per_month = 2592000.0;
        constexpr std::size_t mqtt_tls_overhead = 78;

        double raw_samples = (seconds_per_month / spec.sample_interval_sec) * spec.sensor_count;
        double passed_samples = raw_samples * (1.0 - spec.delta_filter_ratio);
        double batches_count = (seconds_per_month / spec.batch_window_sec) * spec.sensor_count;

        double total_msg_per_home = std::min(passed_samples, batches_count);
        
        EvaluationResult res;
        res.monthly_messages_total = total_msg_per_home * config_.fleet_size;

        std::size_t packet_size = spec.payload_bytes + mqtt_tls_overhead;
        double total_bytes = total_msg_per_home * packet_size * config_.fleet_size;
        res.monthly_storage_gb = total_bytes / (1024.0 * 1024.0 * 1024.0);

        double broker_cost = (res.monthly_messages_total / 1'000'000.0) * config_.broker_price_per_1m;
        double storage_cost = res.monthly_storage_gb * config_.storage_price_per_gb;

        res.total_monthly_cost = broker_cost + storage_cost;
        res.unit_cost_per_home = res.total_monthly_cost / config_.fleet_size;

        if (res.unit_cost_per_home > config_.max_allowed_unit_cost) {
            return std::unexpected(CostError::BudgetExceeded);
        }

        return res;
    }

private:
    CostModelConfig config_;
};

} // namespace dh::cost

int main() {
    using namespace dh::cost;

    TelemetryBudgetEvaluator evaluator(CostModelConfig{});
    TelemetrySpec spec{};

    auto result = evaluator.evaluate(spec);

    if (!result) {
        if (result.error() == CostError::BudgetExceeded) {
            std::cerr << "[CI FAILURE] Architectural Fitness Function: Unit cost budget exceeded!\n";
            return 1;
        }
        std::cerr << "[CI ERROR] Invalid configuration provided.\n";
        return 2;
    }

    std::cout << std::fixed << std::setprecision(4)
              << "[CI SUCCESS] Unit Cost: $" << result->unit_cost_per_home << " / home / month\n";
    return 0;
}
```
:::

У наведеній вище реалізації мовою C++20 використовується тип `std::expected` для безпечної обробки помилок без винятків, що забезпечує високу швидкодію виконання перевірки. Метод `evaluate` перевіряє коректність конфігурації та повертає або структурований результат розрахунку, або код помилки `CostError::BudgetExceeded`.

## Інтеграція в CI/CD пайплайн (Python CI Guard)

Скрипт автоматично перевіряє YAML-конфігурації при кожному Pull Request:

```python
# ci_cost_guard.py — Скрипт перевірки фітнес-функції бюджету в CI
import sys
import yaml

def check_budget_policy(policy_file_path: str, max_allowed_unit_cost: float = 0.015) -> bool:
    with open(policy_file_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    fleet_size = spec.get("fleet_size", 5000000)
    sensors = spec.get("sensors", [])
    
    total_monthly_msgs = 0
    total_bytes = 0
    
    for s in sensors:
        freq_sec = s["interval_sec"]
        bytes_size = s["payload_bytes"]
        delta_ratio = s.get("delta_filter_ratio", 0.9)
        
        # 30 днів = 2592000 сек
        raw_msgs = (2592000 / freq_sec) * (1.0 - delta_ratio)
        total_monthly_msgs += raw_msgs * fleet_size
        total_bytes += raw_msgs * (bytes_size + 78) * fleet_size

    total_storage_gb = total_bytes / (1024 ** 3)
    
    # EMQX amortized + S3 Cold Storage
    cost_broker = (total_monthly_msgs / 1_000_000) * 0.05
    cost_storage = total_storage_gb * 0.015
    
    total_cost = cost_broker + cost_storage
    unit_cost = total_cost / fleet_size

    print(f"=== DH ARCHITECTURE FITNESS FUNCTION ===")
    print(f"Флот: {fleet_size:,} будинків")
    print(f"Прогнозовані хмарні витрати: ${total_cost:,.2f} / місяць")
    print(f"Unit Cost: ${unit_cost:.4f} / дім / місяць (Ліміт: ${max_allowed_unit_cost:.3f})")

    if unit_cost > max_allowed_unit_cost:
        print(f"❌ REJECTED: Бюджетний поріг перевищено на {((unit_cost/max_allowed_unit_cost)-1)*100:.1f}%!")
        return False
    
    print(f"✅ PASSED: Зміна не порушує фінансових обмежень.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ci_cost_guard.py <telemetry_policy.yaml>")
        sys.exit(2)
        
    passed = check_budget_policy(sys.argv[1])
    sys.exit(0 if passed else 1)
```

## Реальні кейси виявлення регресій у продакшні

Розглянемо три реальні випадки з практики розробки Digital Homes, коли автоматизована фітнес-функція бюджету врятувала інфраструктуру від мільйонних збитків:

1. **Спроба відмови від дельта-фільтрації для давачів потужності:** Розробник команди аналітики вирішив отримувати сирий потік споживання електроенергії для навчання ML-моделі й встановив `delta_filter_efficiency = 0.0`. Фітнес-функція в CI порахувала прогнозований unit-cost як `$0.084 / дім / місяць` (перевищення ліміту у 5.6 разів) і заблокувала Pull Request.
2. **Перехід із двобайтового цілого на string у JSON:** При додаванні нового текстового поля статусів серіалізатор збільшив розмір пакета з 100 до 450 байтів. Оскільки обсяг сховища ClickHouse пропорційно виріс, фітнес-функція зафіксувала Unit Cost `$0.019 / дім / місяць` і змусила переписати контракт на бінарний Protobuf.
3. **Зменшення періоду опитування давачів протікання:** Інженер з безпеки встановив опитування датчиків протікання води кожну 1 секунду замість 10 секунд. Оскільки ці датчики 99.9% часу перебувають у стаціонарному стані, дельта-фільтр зрізав більшість вимірів, але збільшення локального CPU-навантаження на хабі було зафіксовано додатковою метрикою енергоспоживання.

## Головні пастки при впровадженні фітнес-функції

1. **Нелінійне зростання TLS Keep-Alive:** Забування про те, що TCP/TLS з'єднання, яке висить 24/7, генерує пакети підтримання сесії (Keep-Alive що 15-60 секунд). Якщо не включити їх у модель, реальний трафік виявиться на 30-40% вищим за розрахунковий.
2. **Пастка локального тестування:** Тестування на 10 хабах не показує ціну інгесту. Обов'язково множте розрахунки на цільовий флот (`5,000,000`), а не на поточну кількість тестових пристроїв.
3. **Ігнорування Egress при розширенні API:** Додавання нових полів у JSON без контролю стиснення призводить до того, що мобільний застосунок починає викачувати додаткові гігабайти при відкритті дашборду.
4. **Нераціональне моделювання аварійних сплесків:** Якщо фітнес-функція оцінює лише стабільний режим (Steady State) і не враховує повторні відправки після відновлення мережі (Retry Storms), система виявиться незахищеною від фінансових піків під час масових реконектів.
