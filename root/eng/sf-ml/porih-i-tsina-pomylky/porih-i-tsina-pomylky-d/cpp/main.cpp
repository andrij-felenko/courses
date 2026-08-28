#include <array>
#include <cmath>
#include <expected>
#include <optional>
#include <algorithm>

namespace ml::decision {

struct CostMatrix {
    float cost_tp{0.0f};  // Вартість True Positive
    float cost_fp{1.0f};  // Вартість False Positive
    float cost_tn{0.0f};  // Вартість True Negative
    float cost_fn{10.0f}; // Вартість False Negative
    
    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return (cost_fn > cost_tp) && (cost_fp > cost_tn);
    }
};

struct ClassificationResult {
    bool decision{false};       // true = Positive (1), false = Negative (0)
    float expected_loss{0.0f};  // Очікуваний байєсівський ризик
    float confidence_margin{0.0f};
};

enum class EngineError {
    InvalidCostMatrix,
    InvalidPriorProbability
};

class ThresholdEngine {
public:
    static std::expected<ThresholdEngine, EngineError> create(
        CostMatrix costs, 
        float prior_positive
    ) noexcept {
        if (prior_positive <= 0.0f || prior_positive >= 1.0f) {
            return std::unexpected(EngineError::InvalidPriorProbability);
        }
        if (!costs.is_valid()) {
            return std::unexpected(EngineError::InvalidCostMatrix);
        }
        
        float num = costs.cost_fp - costs.cost_tn;
        float den = (costs.cost_fp - costs.cost_tn) + (costs.cost_fn - costs.cost_tp);
        float threshold = num / den;
        
        return ThresholdEngine(costs, prior_positive, threshold);
    }

    [[nodiscard]] ClassificationResult classify(float probability) const noexcept {
        float p = std::clamp(probability, 0.0f, 1.0f);
        float p_neg = 1.0f - p;
        
        float risk_action = p * costs_.cost_tp + p_neg * costs_.cost_fp;
        float risk_inaction = p * costs_.cost_fn + p_neg * costs_.cost_tn;
        
        bool decision = (p >= optimal_threshold_);
        float selected_loss = decision ? risk_action : risk_inaction;
        float margin = std::abs(p - optimal_threshold_);
        
        return ClassificationResult{
            .decision = decision,
            .expected_loss = selected_loss,
            .confidence_margin = margin
        };
    }

    [[nodiscard]] constexpr float threshold() const noexcept {
        return optimal_threshold_;
    }

private:
    constexpr ThresholdEngine(CostMatrix costs, float prior_pos, float threshold) noexcept
        : costs_(costs), prior_positive_(prior_pos), optimal_threshold_(threshold) {}

    CostMatrix costs_;
    float prior_positive_;
    float optimal_threshold_;
};

} // namespace ml::decision
