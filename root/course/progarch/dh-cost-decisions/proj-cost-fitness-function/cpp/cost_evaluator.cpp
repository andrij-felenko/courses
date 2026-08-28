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
