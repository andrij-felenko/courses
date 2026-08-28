// telemetry_budget.cpp — Оцінка бюджетного навантаження телеметрії на мові C++20
#include <iostream>
#include <expected>

namespace dh::budget {

constexpr double kMaxAllowedUnitCostUsd = 0.015;
constexpr double kFleetHomesCount = 5'000'000.0;

struct TelemetryParam {
    std::size_t payload_bytes{100};
    int polling_interval_sec{5};
    double delta_filter_efficiency{0.90};
};

struct BudgetCheckResult {
    double unit_cost_usd;
    bool is_passed;
};

class BudgetGuard {
public:
    [[nodiscard]] static BudgetCheckResult evaluate(const TelemetryParam& param) noexcept {
        const double raw_msgs = (2592000.0 / param.polling_interval_sec) * 20.0;
        const double actual_msgs = raw_msgs * (1.0 - param.delta_filter_efficiency);
        
        const double broker_cost = (actual_msgs * kFleetHomesCount / 1'000'000.0) * 0.05;
        const double total_bytes = actual_msgs * (param.payload_bytes + 78) * kFleetHomesCount;
        const double storage_gb = total_bytes / (1024.0 * 1024.0 * 1024.0);
        const double storage_cost = storage_gb * 0.015;
        
        const double total_cost = broker_cost + storage_cost;
        const double unit_cost = total_cost / kFleetHomesCount;
        
        return BudgetCheckResult{
            .unit_cost_usd = unit_cost,
            .is_passed = (unit_cost <= kMaxAllowedUnitCostUsd)
        };
    }
};

} // namespace dh::budget
