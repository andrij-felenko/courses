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
