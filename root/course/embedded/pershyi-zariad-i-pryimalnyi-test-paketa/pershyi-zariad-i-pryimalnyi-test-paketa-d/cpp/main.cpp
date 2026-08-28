#include <cstdint>
#include <vector>
#include <span>
#include <expected>
#include <algorithm>
#include <numeric>

struct PackMetrics {
    std::vector<uint16_t> cell_voltage_mv;
    std::vector<int16_t>  temperature_c;
    int32_t               pack_current_ma{0};
};

struct SafetyLimits {
    uint16_t max_allowed_imbalance_mv{25};
    uint16_t cell_ovp_threshold_mv{4250};
    uint16_t cell_uvp_threshold_mv{2800};
    int16_t  max_charge_temp_c{45};
    int16_t  min_charge_temp_c{0};
    int16_t  max_temp_gradient_c{5};
};

enum class PackFault {
    EmptyConfiguration,
    OvervoltageViolation,
    UndervoltageViolation,
    ImbalanceExceeded,
    OvertemperatureViolation,
    UndertemperatureViolation,
    ThermalGradientExceeded
};

struct ValidationResult {
    bool     charge_allowed{false};
    bool     discharge_allowed{false};
    bool     balance_needed{false};
    uint16_t max_imbalance_mv{0};
    int16_t  max_gradient_c{0};
    size_t   highest_cell_idx{0};
    size_t   lowest_cell_idx{0};
};

class PackSafetyEvaluator {
public:
    [[nodiscard]] static std::expected<ValidationResult, PackFault> 
    evaluate(const PackMetrics& metrics, const SafetyLimits& limits) {
        if (metrics.cell_voltage_mv.empty()) {
            return std::unexpected(PackFault::EmptyConfiguration);
        }

        const auto [min_it, max_it] = std::minmax_element(
            metrics.cell_voltage_mv.begin(), metrics.cell_voltage_mv.end());

        const uint16_t v_min = *min_it;
        const uint16_t v_max = *max_it;

        if (v_max > limits.cell_ovp_threshold_mv) {
            return std::unexpected(PackFault::OvervoltageViolation);
        }
        if (v_min < limits.cell_uvp_threshold_mv) {
            return std::unexpected(PackFault::UndervoltageViolation);
        }

        const uint16_t imbalance = static_cast<uint16_t>(v_max - v_min);
        if (imbalance > limits.max_allowed_imbalance_mv) {
            return std::unexpected(PackFault::ImbalanceExceeded);
        }

        int16_t gradient = 0;
        if (!metrics.temperature_c.empty()) {
            const auto [t_min_it, t_max_it] = std::minmax_element(
                metrics.temperature_c.begin(), metrics.temperature_c.end());
            
            if (*t_max_it > limits.max_charge_temp_c) {
                return std::unexpected(PackFault::OvertemperatureViolation);
            }
            if (*t_min_it < limits.min_charge_temp_c) {
                return std::unexpected(PackFault::UndertemperatureViolation);
            }

            gradient = static_cast<int16_t>(*t_max_it - *t_min_it);
            if (gradient > limits.max_temp_gradient_c) {
                return std::unexpected(PackFault::ThermalGradientExceeded);
            }
        }

        ValidationResult res;
        res.charge_allowed = true;
        res.discharge_allowed = (v_min >= limits.cell_uvp_threshold_mv);
        res.balance_needed = (imbalance > 15 && v_max >= 4150);
        res.max_imbalance_mv = imbalance;
        res.max_gradient_c = gradient;
        res.lowest_cell_idx = static_cast<size_t>(std::distance(metrics.cell_voltage_mv.begin(), min_it));
        res.highest_cell_idx = static_cast<size_t>(std::distance(metrics.cell_voltage_mv.begin(), max_it));

        return res;
    }
};
