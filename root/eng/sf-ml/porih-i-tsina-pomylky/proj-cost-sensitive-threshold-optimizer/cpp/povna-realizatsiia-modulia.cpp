#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <algorithm>
#include <span>

namespace embedded::ml {

enum class CalibrationMode {
    Platt,
    Temperature,
    IsotonicTable
};

struct CalibPoint {
    float raw_score{0.0f};
    float calibrated_prob{0.0f};
};

struct CalibratorConfig {
    CalibrationMode mode{CalibrationMode::Platt};
    float platt_a{1.0f};
    float platt_b{0.0f};
    float temperature{1.0f};
    std::array<CalibPoint, 16> table{};
    std::size_t table_size{0};

    [[nodiscard]] float calibrate(float raw_score) const noexcept {
        if (mode == CalibrationMode::Temperature) {
            float temp = (temperature > 1e-4f) ? temperature : 1.0f;
            float clamped = std::clamp(raw_score / temp, -85.0f, 85.0f);
            return 1.0f / (1.0f + std::exp(-clamped));
        }

        if (mode == CalibrationMode::Platt) {
            float z = -(platt_a * raw_score + platt_b);
            float clamped = std::clamp(z, -85.0f, 85.0f);
            return 1.0f / (1.0f + std::exp(-clamped));
        }

        if (mode == CalibrationMode::IsotonicTable && table_size >= 2) {
            if (raw_score <= table[0].raw_score) return table[0].calibrated_prob;
            if (raw_score >= table[table_size - 1].raw_score) return table[table_size - 1].calibrated_prob;

            std::span<const CalibPoint> active_span(table.data(), table_size);
            auto it = std::lower_bound(
                active_span.begin(), active_span.end(), raw_score,
                [](const CalibPoint& pt, float val) noexcept {
                    return pt.raw_score < val;
                }
            );

            if (it == active_span.begin()) return it->calibrated_prob;
            auto prev_it = it - 1;

            float z0 = prev_it->raw_score;
            float z1 = it->raw_score;
            float p0 = prev_it->calibrated_prob;
            float p1 = it->calibrated_prob;

            float dz = z1 - z0;
            if (std::abs(dz) < 1e-6f) return p0;

            float t = (raw_score - z0) / dz;
            return p0 + t * (p1 - p0);
        }

        float clamped = std::clamp(raw_score, -85.0f, 85.0f);
        return 1.0f / (1.0f + std::exp(-clamped));
    }
};

struct CostMatrix {
    float cost_tp{0.0f};  // True Positive
    float cost_fp{1.0f};  // False Positive
    float cost_tn{0.0f};  // True Negative
    float cost_fn{10.0f}; // False Negative

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (cost_fn > cost_tp) && (cost_fp > cost_tn);
    }
};

struct AdaptiveContext {
    float battery_ratio{1.0f}; // 0.0 .. 1.0
    float speed_mps{0.0f};      // м/с
    float queue_ratio{0.0f};    // 0.0 .. 1.0
    float sensor_noise{0.0f};   // дисперсія шуму
};

struct AdapterConfig {
    float beta_battery{3.0f};
    float crit_battery{0.20f};
    float beta_speed{2.0f};
    float max_speed_mps{30.0f};
    float beta_queue{4.0f};
    float ema_alpha{0.15f};
    float base_hyst_width{0.03f};
    float noise_hyst_gain{0.10f};
};

struct DecisionResult {
    bool decision{false};
    float calibrated_prob{0.0f};
    float active_threshold{0.5f};
    float expected_risk{0.0f};
    float confidence_margin{0.0f};
};

enum class OptimizerError {
    InvalidCostMatrix,
    InvalidPrior,
    InvalidConfig
};

class CostSensitiveThresholdOptimizer {
public:
    static std::expected<CostSensitiveThresholdOptimizer, OptimizerError> create(
        CostMatrix base_costs,
        CalibratorConfig calibrator,
        AdapterConfig config,
        float prior_positive
    ) noexcept {
        if (!base_costs.is_valid()) {
            return std::unexpected(OptimizerError::InvalidCostMatrix);
        }
        if (prior_positive <= 0.0f || prior_positive >= 1.0f) {
            return std::unexpected(OptimizerError::InvalidPrior);
        }
        if (config.ema_alpha <= 0.0f || config.ema_alpha > 1.0f || config.max_speed_mps <= 0.0f) {
            return std::unexpected(OptimizerError::InvalidConfig);
        }

        float num = base_costs.cost_fp - base_costs.cost_tn;
        float den = (base_costs.cost_fp - base_costs.cost_tn) + (base_costs.cost_fn - base_costs.cost_tp);
        float init_threshold = num / den;

        return CostSensitiveThresholdOptimizer(base_costs, calibrator, config, prior_positive, init_threshold);
    }

    void update_context(const AdaptiveContext& ctx) noexcept {
        float batt_deficit = 0.0f;
        if (ctx.battery_ratio < config_.crit_battery) {
            batt_deficit = (config_.crit_battery - ctx.battery_ratio) / config_.crit_battery;
        }
        float k_batt = 1.0f + config_.beta_battery * batt_deficit;

        float speed_ratio = std::clamp(ctx.speed_mps / config_.max_speed_mps, 0.0f, 2.0f);
        float k_speed = 1.0f + config_.beta_speed * (speed_ratio * speed_ratio);

        float q_ratio = std::clamp(ctx.queue_ratio, 0.0f, 1.0f);
        float k_queue = 1.0f + config_.beta_queue * (q_ratio * q_ratio);

        current_costs_.cost_fp = base_costs_.cost_fp * k_batt * k_queue;
        current_costs_.cost_fn = base_costs_.cost_fn * k_speed;
        current_costs_.cost_tp = base_costs_.cost_tp;
        current_costs_.cost_tn = base_costs_.cost_tn;

        float num = current_costs_.cost_fp - current_costs_.cost_tn;
        float den = (current_costs_.cost_fp - current_costs_.cost_tn) + 
                    (current_costs_.cost_fn - current_costs_.cost_tp);
        float raw_target = std::clamp(num / den, 0.001f, 0.999f);

        current_threshold_ = config_.ema_alpha * raw_target + (1.0f - config_.ema_alpha) * current_threshold_;
        current_hyst_width_ = config_.base_hyst_width + config_.noise_hyst_gain * ctx.sensor_noise;
    }

    [[nodiscard]] DecisionResult process_sample(float raw_score) noexcept {
        float prob = calibrator_.calibrate(raw_score);
        float prob_neg = 1.0f - prob;

        float half_hyst = current_hyst_width_ * 0.5f;
        float switch_thresh = previous_decision_ ? (current_threshold_ - half_hyst) 
                                                : (current_threshold_ + half_hyst);

        bool decision = (prob >= switch_thresh);
        previous_decision_ = decision;

        float risk_pos = prob * current_costs_.cost_tp + prob_neg * current_costs_.cost_fp;
        float risk_neg = prob * current_costs_.cost_fn + prob_neg * current_costs_.cost_tn;

        return DecisionResult{
            .decision = decision,
            .calibrated_prob = prob,
            .active_threshold = current_threshold_,
            .expected_risk = decision ? risk_pos : risk_neg,
            .confidence_margin = std::abs(prob - current_threshold_)
        };
    }

    [[nodiscard]] constexpr float current_threshold() const noexcept { return current_threshold_; }
    [[nodiscard]] constexpr const CostMatrix& current_costs() const noexcept { return current_costs_; }

private:
    constexpr CostSensitiveThresholdOptimizer(
        CostMatrix base_costs,
        CalibratorConfig calibrator,
        AdapterConfig config,
        float prior_pos,
        float init_threshold
    ) noexcept
        : base_costs_(base_costs),
          current_costs_(base_costs),
          calibrator_(calibrator),
          config_(config),
          prior_positive_(prior_pos),
          current_threshold_(init_threshold),
          current_hyst_width_(config.base_hyst_width) {}

    CostMatrix base_costs_;
    CostMatrix current_costs_;
    CalibratorConfig calibrator_;
    AdapterConfig config_;
    float prior_positive_;
    float current_threshold_{0.5f};
    float current_hyst_width_{0.03f};
    bool previous_decision_{false};
};

} // namespace embedded::ml
