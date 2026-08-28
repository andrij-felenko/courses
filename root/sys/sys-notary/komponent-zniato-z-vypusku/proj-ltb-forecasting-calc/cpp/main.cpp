#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cmath>
#include <random>
#include <chrono>
#include <concepts>
#include <span>
#include <expected>
#include <iomanip>
#include <limits>

namespace obsolescence::forecasting {

/* Конфігурація моделі прогнозування LTB */
struct LtbConfig {
    uint32_t horizon_quarters{12};
    double   quarterly_demand_mean{2500.0};
    double   quarterly_demand_std{350.0};
    double   smt_scrap_rate{0.015};
    uint32_t feeder_setup_loss{30};

    uint32_t active_installed_base{40000};
    double   weibull_beta{1.4};
    double   weibull_eta_quarters{80.0};
    uint32_t warranty_years{5};

    double   unit_cost_usd{12.50};
    double   holding_cost_rate_yr{0.18};
    double   shortage_penalty_usd{120.00};
    double   salvage_value_usd{1.00};

    uint32_t mc_iterations{10000};
};

/* Результати стохастичного аналізу */
struct SimulationReport {
    double   mean_units{0.0};
    double   std_dev_units{0.0};
    double   min_units{0.0};
    double   max_units{0.0};
    double   percentile_50{0.0};
    double   percentile_80{0.0};
    double   percentile_95{0.0};
    double   percentile_99{0.0};

    uint32_t optimal_order_qty{0};
    double   direct_purchase_cost{0.0};
    double   expected_holding_cost{0.0};
    double   expected_shortage_penalty{0.0};
    double   expected_scrap_loss{0.0};
    double   total_expected_cost{0.0};
};

enum class SimError {
    InvalidHorizon,
    InvalidIterationCount,
    AllocationFailure
};

/* Концепт для генераторів випадкових чисел */
template <typename G>
concept RandomNumberEngine = requires(G g) {
    { g() } -> std::unsigned_integral;
    { G::min() } -> std::same_as<typename G::result_type>;
    { G::max() } -> std::same_as<typename G::result_type>;
};

template <RandomNumberEngine Engine = std::mt19937_64>
class LtbMonteCarloEngine {
public:
    explicit LtbMonteCarloEngine(uint64_t seed = 42) : rng_{seed} {}

    [[nodiscard]] std::expected<SimulationReport, SimError> 
    run(const LtbConfig& cfg) {
        if (cfg.horizon_quarters == 0) return std::unexpected(SimError::InvalidHorizon);
        if (cfg.mc_iterations < 100) return std::unexpected(SimError::InvalidIterationCount);

        std::vector<double> demands(cfg.mc_iterations);
        std::normal_distribution<double> norm_dist(cfg.quarterly_demand_mean, cfg.quarterly_demand_std);
        std::weibull_distribution<double> weib_dist(cfg.weibull_beta, cfg.weibull_eta_quarters);

        const double q_holding_rate = cfg.holding_cost_rate_yr / 4.0;
        double sum_demands = 0.0;
        double sum_sq = 0.0;

        for (uint32_t iter = 0; iter < cfg.mc_iterations; ++iter) {
            double total_iter_demand = 0.0;

            /* 1. Виробничий попит */
            for (uint32_t q = 0; q < cfg.horizon_quarters; ++q) {
                const double q_prod = std::max(0.0, norm_dist(rng_));
                const double q_scrap = (q_prod * cfg.smt_scrap_rate) + static_cast<double>(cfg.feeder_setup_loss);
                total_iter_demand += (q_prod + q_scrap);
            }

            /* 2. Сервісна надійність за Вейбуллом */
            const uint32_t service_quarters = cfg.warranty_years * 4;
            const double active_base = static_cast<double>(cfg.active_installed_base);

            for (uint32_t sq = 0; sq < service_quarters; ++sq) {
                const double t0 = static_cast<double>(sq);
                const double t1 = static_cast<double>(sq + 1);

                const double f0 = 1.0 - std::exp(-std::pow(t0 / cfg.weibull_eta_quarters, cfg.weibull_beta));
                const double f1 = 1.0 - std::exp(-std::pow(t1 / cfg.weibull_eta_quarters, cfg.weibull_beta));

                double fail_rate = 0.0;
                if (f0 < 0.9999) {
                    fail_rate = (f1 - f0) / (1.0 - f0);
                }
                total_iter_demand += (active_base * fail_rate);
            }

            demands[iter] = total_iter_demand;
            sum_demands += total_iter_demand;
            sum_sq += (total_iter_demand * total_iter_demand);
        }

        std::sort(demands.begin(), demands.end());

        const double mean = sum_demands / cfg.mc_iterations;
        const double variance = std::max(0.0, (sum_sq / cfg.mc_iterations) - (mean * mean));
        const double std_dev = std::sqrt(variance);

        SimulationReport rep;
        rep.mean_units    = mean;
        rep.std_dev_units = std_dev;
        rep.min_units     = demands.front();
        rep.max_units     = demands.back();
        rep.percentile_50 = demands[static_cast<size_t>(cfg.mc_iterations * 0.50)];
        rep.percentile_80 = demands[static_cast<size_t>(cfg.mc_iterations * 0.80)];
        rep.percentile_95 = demands[static_cast<size_t>(cfg.mc_iterations * 0.95)];
        rep.percentile_99 = demands[static_cast<size_t>(cfg.mc_iterations * 0.99)];

        /* 3. Оптимізація вартості володіння */
        const uint32_t min_q = static_cast<uint32_t>(rep.percentile_50 * 0.75);
        const uint32_t max_q = static_cast<uint32_t>(rep.percentile_99 * 1.25);
        const uint32_t step = std::max(1u, (max_q - min_q) / 100u);

        double best_tco = std::numeric_limits<double>::infinity();

        for (uint32_t cand = min_q; cand <= max_q; cand += step) {
            double h_cost = 0.0, s_cost = 0.0, scr_cost = 0.0;

            for (double d : demands) {
                if (cand >= d) {
                    const double surplus = static_cast<double>(cand) - d;
                    scr_cost += surplus * (cfg.unit_cost_usd - cfg.salvage_value_usd);
                    h_cost += (static_cast<double>(cand) + d) * 0.5 * q_holding_rate * 
                              cfg.horizon_quarters * cfg.unit_cost_usd;
                } else {
                    const double short_qty = d - static_cast<double>(cand);
                    s_cost += short_qty * cfg.shortage_penalty_usd;
                    h_cost += static_cast<double>(cand) * 0.5 * q_holding_rate * 
                              (cfg.horizon_quarters / 2.0) * cfg.unit_cost_usd;
                }
            }

            h_cost /= cfg.mc_iterations;
            s_cost /= cfg.mc_iterations;
            scr_cost /= cfg.mc_iterations;

            const double direct_cost = static_cast<double>(cand) * cfg.unit_cost_usd;
            const double current_tco = direct_cost + h_cost + s_cost + scr_cost;

            if (current_tco < best_tco) {
                best_tco = current_tco;
                rep.optimal_order_qty         = cand;
                rep.direct_purchase_cost      = direct_cost;
                rep.expected_holding_cost     = h_cost;
                rep.expected_shortage_penalty = s_cost;
                rep.expected_scrap_loss       = scr_cost;
                rep.total_expected_cost       = current_tco;
            }
        }

        return rep;
    }

private:
    Engine rng_;
};

} // namespace obsolescence::forecasting

int main() {
    using namespace obsolescence::forecasting;

    const LtbConfig config{};
    LtbMonteCarloEngine engine{20260828};

    std::cout << "Запуск стохастичного аналізу LTB у C++20...\n";
    auto result = engine.run(config);

    if (!result) {
        std::cerr << "Помилка виконання симуляції!\n";
        return 1;
    }

    const auto& r = *result;
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "\n=======================================================\n";
    std::cout << "   СТОХАСТИЧНИЙ ЗВІТ ОЦІНКИ ЗАПАСУ LTB ТА РИЗИКІВ TCO  \n";
    std::cout << "=======================================================\n";
    std::cout << "Очікувана середня потреба: " << std::setw(8) << r.mean_units << " шт. (±" << r.std_dev_units << ")\n";
    std::cout << "Медіанна потреба (P50):    " << std::setw(8) << r.percentile_50 << " шт.\n";
    std::cout << "Квантиль P95 (ризик 5%):   " << std::setw(8) << r.percentile_95 << " шт.\n";
    std::cout << "Квантиль P99 (ризик 1%):   " << std::setw(8) << r.percentile_99 << " шт.\n";
    std::cout << "-------------------------------------------------------\n";
    std::cout << "ОПТИМАЛЬНА ЕКОНОМІЧНА ПАРТІЯ: " << std::setw(6) << r.optimal_order_qty << " шт.\n";
    std::cout << "• Пряма вартість закупівлі:  " << std::setw(10) << r.direct_purchase_cost << " USD\n";
    std::cout << "• Очікуване утримання на N2: " << std::setw(10) << r.expected_holding_cost << " USD\n";
    std::cout << "• Ризик штрафу за дефіцит:   " << std::setw(10) << r.expected_shortage_penalty << " USD\n";
    std::cout << "• Ризик втрат від списання:  " << std::setw(10) << r.expected_scrap_loss << " USD\n";
    std::cout << "• МІНІМУМ СУКУПНИХ ВИТРАТ:   " << std::setw(10) << r.total_expected_cost << " USD\n";
    std::cout << "=======================================================\n";

    return 0;
}
