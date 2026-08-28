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
