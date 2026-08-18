# ⚙️ Автоматизований канареєчний контролер та аналізатор SLI

Автоматизоване канареєчне розгортання вимагає надійного та автономного компонента — канареєчного контролера (Canary Controller), який у реальному часі аналізує телеметрію між контрольною групою серверів (Baseline) та групою нового коду (Canary). Головне завдання контролера — усунути суб'єктивне оцінювання з боку людини, виявити аномальне вигорання бюджету помилок (Burn Rate) або стрибок затримки `p99` та прийняти автоматичне рішення про продовження деплою або його негайне відкочування (Rollback) за менш ніж 30 секунд.

У цьому проєктному розборі реалізовано обчислювальне ядро канареєчного аналізатора, яке порівнює метрики двох підмножин серверів за двома часовими вікнами (5 хвилин та 1 година) і застосовує математику вигорання бюджету помилок.

## 1. Архітектурна інтеграція контролера в конвеєр Progressive Delivery

Канареєчний контролер діє як центральний арбітр у конвеєрі розгортання (наприклад, Argo Rollouts, Flagger або власний контролер на основі Kubernetes Operator SDK). На кожному етапі прогресивного розгортання (наприклад, при передачі 1%, 5%, 25% трафіку) контролер здійснює циклічне опитування інфраструктури спостережуваності (Prometheus / VictoriaMetrics) та будує два набори скомплектованих метрик:

1. **Baseline Sample:** Набір метрик з екземплярів, що виконують поточну стабільну версію коду v1 під основним навантаженням.
2. **Canary Sample:** Набір метрик з екземплярів, що виконують нову версію коду v2, яка отримує тестову частку трафіку.

Для збору метрик контролер виконує PromQL-запити обчислення похибки та затримки:

```promql
# Запит помилок за 5 хвилин для канарейки (w_short):
sum(rate(http_requests_total{app="dh-service", env="canary", status=~"5.."}[5m]))
/
sum(rate(http_requests_total{app="dh-service", env="canary"}[5m]))

# Запит p99 затримки за 5 хвилин для канарейки:
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{app="dh-service", env="canary"}[5m])) by (le))
```

Обчислювальний модуль аналізує скомплектовані структури SLI за два вікна (`w_short = 5 хв` та `w_long = 1 год`) й оцінює наступні критерії:

1. **Error Rate Burn Rate:** Якщо короткострокове (`w_short`) та довгострокове (`w_long`) значення вигорання перевищують поріг `B ≥ 14.4` (що загрожує втратою 2% місячного бюджету за годину), контролер негайно віддає команду `ROLLBACK_BURN_RATE`.
2. **Latency Degradation (`p99`):** Якщо затримка `p99` канарейки перевищує baseline більше ніж на 25% при мінімальному обсязі запитів (≥ 1000), контролер повертає команду `ROLLBACK_LATENCY`.
3. **Успішне завершення:** Якщо протягом заданого інтервалу спостереження (наприклад, 15 хвилин) жодного відхилення не виявлено і статистична вибірка достатня, контролер віддає команду `PROMOTE`.

## 2. Реалізація обчислювального ядра

:::tabs
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <cmath>
#include <expected>
#include <optional>

enum class Decision {
    Continue,
    Promote,
    RollbackBurnRate,
    RollbackLatency
};

struct WindowMetrics {
    uint64_t total_requests{0};
    uint64_t error_requests{0};
    double latency_p99_ms{0.0};
};

struct CanarySample {
    WindowMetrics short_window; // 5 хвилин
    WindowMetrics long_window;  // 1 година
};

struct SystemConfig {
    double target_slo{0.9999};          // 99.99% SLO
    double max_burn_rate_short{14.4};   // 14.4x за 5m
    double max_burn_rate_long{14.4};    // 14.4x за 1h
    double max_latency_ratio{1.25};     // +25% до p99
    uint64_t min_sample_requests{1000}; // Мін. вибірка
};

class CanaryEvaluator {
public:
    explicit CanaryEvaluator(SystemConfig config) : config_(config) {}

    [[nodiscard]] std::expected<Decision, std::string_view> evaluate(
        const CanarySample& baseline,
        const CanarySample& canary) const noexcept 
    {
        if (canary.short_window.total_requests < config_.min_sample_requests) {
            return Decision::Continue; // Недостатньо даних
        }

        const double e_slo = 1.0 - config_.target_slo;
        if (e_slo <= 0.0) {
            return std::unexpected("Невалідний конфіг SLO");
        }

        // 1. Обчислення Burn Rate для канарейки
        const double canary_err_short = calc_error_rate(canary.short_window);
        const double canary_err_long  = calc_error_rate(canary.long_window);

        const double burn_short = canary_err_short / e_slo;
        const double burn_long  = canary_err_long / e_slo;

        if (burn_short >= config_.max_burn_rate_short && burn_long >= config_.max_burn_rate_long) {
            return Decision::RollbackBurnRate;
        }

        // 2. Порівняння p99 латентності з Baseline
        if (baseline.short_window.latency_p99_ms > 0.0) {
            const double latency_ratio = canary.short_window.latency_p99_ms / baseline.short_window.latency_p99_ms;
            if (latency_ratio > config_.max_latency_ratio) {
                return Decision::RollbackLatency;
            }
        }

        return Decision::Continue;
    }

private:
    SystemConfig config_;

    static double calc_error_rate(const WindowMetrics& m) noexcept {
        if (m.total_requests == 0) return 0.0;
        return static_cast<double>(m.error_requests) / static_cast<double>(m.total_requests);
    }
};

int main() {
    SystemConfig cfg{};
    CanaryEvaluator evaluator(cfg);

    CanarySample baseline{
        .short_window = { .total_requests = 50000, .error_requests = 1, .latency_p99_ms = 45.0 },
        .long_window  = { .total_requests = 600000, .error_requests = 10, .latency_p99_ms = 44.0 }
    };

    // Канарейка зі сплеском помилок (0.5% помилок = Burn Rate 50x)
    CanarySample bad_canary{
        .short_window = { .total_requests = 5000, .error_requests = 25, .latency_p99_ms = 48.0 },
        .long_window  = { .total_requests = 10000, .error_requests = 50, .latency_p99_ms = 47.0 }
    };

    auto res = evaluator.evaluate(baseline, bad_canary);
    if (res.has_value()) {
        if (res.value() == Decision::RollbackBurnRate) {
            std::cout << "[CRITICAL] Canary Rollback: Сплеск Burn Rate вище 14.4x!\n";
        }
    }
    return 0;
}
```

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    CANARY_CONTINUE = 0,
    CANARY_PROMOTE = 1,
    CANARY_ROLLBACK_BURN_RATE = 2,
    CANARY_ROLLBACK_LATENCY = 3,
    CANARY_ERROR_INVALID_CONFIG = -1
} canary_decision_t;

typedef struct {
    uint64_t total_requests;
    uint64_t error_requests;
    double latency_p99_ms;
} window_metrics_t;

typedef struct {
    window_metrics_t short_window;
    window_metrics_t long_window;
} canary_sample_t;

typedef struct {
    double target_slo;
    double max_burn_rate_short;
    double max_burn_rate_long;
    double max_latency_ratio;
    uint64_t min_sample_requests;
} system_config_t;

static double calculate_error_rate(const window_metrics_t* m) {
    if (m->total_requests == 0) return 0.0;
    return (double)m->error_requests / (double)m->total_requests;
}

canary_decision_t evaluate_canary(
    const system_config_t* config,
    const canary_sample_t* baseline,
    const canary_sample_t* canary)
{
    if (!config || !baseline || !canary) return CANARY_ERROR_INVALID_CONFIG;
    if (canary->short_window.total_requests < config->min_sample_requests) {
        return CANARY_CONTINUE;
    }

    double e_slo = 1.0 - config->target_slo;
    if (e_slo <= 0.0) return CANARY_ERROR_INVALID_CONFIG;

    double canary_err_short = calculate_error_rate(&canary->short_window);
    double canary_err_long  = calculate_error_rate(&canary->long_window);

    double burn_short = canary_err_short / e_slo;
    double burn_long  = canary_err_long / e_slo;

    if (burn_short >= config->max_burn_rate_short && burn_long >= config->max_burn_rate_long) {
        return CANARY_ROLLBACK_BURN_RATE;
    }

    if (baseline->short_window.latency_p99_ms > 0.0) {
        double ratio = canary->short_window.latency_p99_ms / baseline->short_window.latency_p99_ms;
        if (ratio > config->max_latency_ratio) {
            return CANARY_ROLLBACK_LATENCY;
        }
    }

    return CANARY_CONTINUE;
}

int main(void) {
    system_config_t cfg = {
        .target_slo = 0.9999,
        .max_burn_rate_short = 14.4,
        .max_burn_rate_long = 14.4,
        .max_latency_ratio = 1.25,
        .min_sample_requests = 1000
    };

    canary_sample_t baseline = {
        .short_window = {50000, 1, 45.0},
        .long_window  = {600000, 10, 44.0}
    };

    canary_sample_t bad_canary = {
        .short_window = {5000, 25, 48.0},
        .long_window  = {10000, 50, 47.0}
    };

    canary_decision_t res = evaluate_canary(&cfg, &baseline, &bad_canary);
    if (res == CANARY_ROLLBACK_ROLLBACK_BURN_RATE || res == CANARY_ROLLBACK_BURN_RATE) {
        printf("[CRITICAL] Canary Rollback Triggered: Burn Rate Exceeded!\n");
    }
    return 0;
}
```

```go
package main

import (
	"errors"
	"fmt"
)

type Decision int

const (
	Continue Decision = iota
	Promote
	RollbackBurnRate
	RollbackLatency
)

type WindowMetrics struct {
	TotalRequests uint64
	ErrorRequests uint64
	LatencyP99Ms  float64
}

type CanarySample struct {
	ShortWindow WindowMetrics
	LongWindow  WindowMetrics
}

type SystemConfig struct {
	TargetSLO         float64
	MaxBurnRateShort  float64
	MaxBurnRateLong   float64
	MaxLatencyRatio   float64
	MinSampleRequests uint64
}

func calcErrorRate(m WindowMetrics) float64 {
	if m.TotalRequests == 0 {
		return 0.0
	}
	return float64(m.ErrorRequests) / float64(m.TotalRequests)
}

func EvaluateCanary(cfg SystemConfig, baseline, canary CanarySample) (Decision, error) {
	if canary.ShortWindow.TotalRequests < cfg.MinSampleRequests {
		return Continue, nil
	}

	eSLO := 1.0 - cfg.TargetSLO
	if eSLO <= 0.0 {
		return Continue, errors.New("invalid SLO config")
	}

	errShort := calcErrorRate(canary.ShortWindow)
	errLong := calcErrorRate(canary.LongWindow)

	burnShort := errShort / eSLO
	burnLong := errLong / eSLO

	if burnShort >= cfg.MaxBurnRateShort && burnLong >= cfg.MaxBurnRateLong {
		return RollbackBurnRate, nil
	}

	if baseline.ShortWindow.LatencyP99Ms > 0.0 {
		ratio := canary.ShortWindow.LatencyP99Ms / baseline.ShortWindow.LatencyP99Ms
		if ratio > cfg.MaxLatencyRatio {
			return RollbackLatency, nil
		}
	}

	return Continue, nil
}

func main() {
	cfg := SystemConfig{
		TargetSLO:         0.9999,
		MaxBurnRateShort:  14.4,
		MaxBurnRateLong:   14.4,
		MaxLatencyRatio:   1.25,
		MinSampleRequests: 1000,
	}

	baseline := CanarySample{
		ShortWindow: WindowMetrics{TotalRequests: 50000, ErrorRequests: 1, LatencyP99Ms: 45.0},
		LongWindow:  WindowMetrics{TotalRequests: 600000, ErrorRequests: 10, LatencyP99Ms: 44.0},
	}

	badCanary := CanarySample{
		ShortWindow: WindowMetrics{TotalRequests: 5000, ErrorRequests: 25, LatencyP99Ms: 48.0},
		LongWindow:  WindowMetrics{TotalRequests: 10000, ErrorRequests: 50, LatencyP99Ms: 47.0},
	}

	decision, err := EvaluateCanary(cfg, baseline, badCanary)
	if err == nil && decision == RollbackBurnRate {
		fmt.Println("[CRITICAL] Canary Rollback: High Burn Rate Detected!")
	}
}
```
:::

## 3. Детальний розбір реалізацій та мовних ідіом

Представлені три варіанти реалізації обчислювального ядра ілюструють ідіоматичні підходи різних системних мов програмування при роботі з операційними контролерами:

1. **C++20 варіант:** Використовує сувору семантику типів `std::expected<Decision, std::string_view>` для безпечної обробки помилок конфігурації без використання винятків (`noexcept`). Поля структури розігріваються узагальненими значеннями за замовчуванням, а методи оцінки позначені як `[[nodiscard]]` для запобігання ігноруванню повернутого рішення. Конструктор класу бере конфігурацію за значенням і переміщує її в приватне поле.
2. **POSIX C варіант:** Дотримується строгого процедурного підходу, який застосовується у вбудованих агентах або ядрах високонавантажених проксі (типу Nginx модулів чи Envoy розширень). Повернення статусу виконується через цілочисельний enum `canary_decision_t`, а вхідні структури передаються за константними вказівниками для мінімізації копіювання на стеку. Перевірка нулевих вказівників та валідація конфігурації виконується явними перевірками перед виконанням будь-яких обчислень.
3. **Go варіант:** Використовує стандартну ідіому повернення пари `(Decision, error)`. Логіка розрахунків є повністю потокобезпечною та може виконуватися паралельно в декількох горутинах контролера оркестрації (Kubernetes Controller Reconcile Loop).

## 4. Простеження та аудиторське логування рішень (Audit Tracing)

Контролер канареєчного розгортання не повинен приймати рішення у вигляді «чорного ящика». Кожен аналітичний крок супроводжується генеруванням структурованого журналу у форматі JSON із прив'язкою до скрізного ідентифікатора простеження `traceparent`.

Журнал аудіту містить повні числові зрізи, які дозволяють SRE-інженерам відновити хід прийняття рішення у разі автоматичного відкочування:

```json
{
  "timestamp": "2026-08-18T10:30:00.102Z",
  "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "event": "canary_evaluation",
  "service": "dh-core-ledger",
  "canary_version": "v2.4.1",
  "metrics": {
    "baseline_p99_ms": 45.0,
    "canary_p99_ms": 48.0,
    "canary_burn_rate_5m": 50.0,
    "canary_burn_rate_1h": 25.0,
    "total_requests_5m": 5000
  },
  "thresholds": {
    "max_burn_rate_5m": 14.4,
    "max_burn_rate_1h": 14.4
  },
  "decision": "ROLLBACK_BURN_RATE",
  "action_taken": "k8s_patch_deployment_rollback_initiated"
}
```

Така журналізація дозволяє автоматично відправляти сповіщення в канал оперативності (Slack / PagerDuty) із вичерпними числовими доказиами: «Відкочування v2.4.1 здійснено через сплеск Burn Rate за 5 хвилин до 50.0x при порозі 14.4x».

## 5. Практичні пастки та граничні випадки експлуатації

При практичному розгортанні канареєчного контролера в кубернетес-кластерах інженери стикаються з чотирма поширеними операційними пастками:

1. **Пастка низької частоти (Low Traffic / Small N Problem):** На низькому або нічному трафіку (наприклад, 20 запитів за 5 хвилин) єдина помилка через мережевий таймаут дає `e(w) = 0.05` (5%). При `SLO = 99.99%` це викликає штучний стрибок `B = 500`. Без перевірки `min_sample_requests` контролер виконуватиме постійні хибні відкочування під час нічного зниження трафіку.
2. **Пастка відсутності розігріву (Cold Start Delay):** Перші 30 секунд після запуску канареєчного контейнера його CPU та затримка підвищені через ініціалізацію пулів з'єднань, створення Redis-сокетів та JIT-компіляцію. Вікно аналізу `w_short` має починатися строго після успішного завершення процедури розігріву (Warmup Healthcheck).
3. **Асинхронний лаг моніторингу (Prometheus Scrape Lag):** Prometheus збирає метрики з інтервалом (Scrape Interval) у 15–30 секунд. Контролер повинен закладати часову затримку у 1–2 інтервали збору перед прийняттям остаточного рішення, щоб аналізувати дійсно скомплектовані дані.
4. **Пастка шумного сусіда (Noisy Neighbor / Pod Skew):** Якщо канареєчний Pod потрапив на вузол Kubernetes із перевантаженим CPU, його латентність зросте не через баг у коді, а через збій локальної інфраструктури. Надійні контролери порівнюють метрики канарейки з контрольною групою Baseline, розташованій у тій самій зоні доступності (Availability Zone).
