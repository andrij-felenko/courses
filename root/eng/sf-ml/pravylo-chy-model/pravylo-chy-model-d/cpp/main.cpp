#include <cstdint>
#include <algorithm>
#include <cmath>
#include <span>
#include <expected>

namespace embedded::control {

struct Telemetry {
    float speed_rad_s{0.0f};
    float current_amps{0.0f};
    float temperature_c{0.0f};
};

struct MlProposal {
    float proposed_speed{0.0f};
    float confidence{0.0f};
    bool  inference_valid{false};
};

enum class DecisionSource : uint8_t {
    MlOptimal,
    RuleClamped,
    RuleFallback
};

struct ArbiterResult {
    float applied_speed{0.0f};
    DecisionSource source{DecisionSource::RuleFallback};
};

class HybridArbiter {
public:
    static constexpr float kMaxSpeedRadS{150.0f};
    static constexpr float kMaxAccelRadS2{300.0f};
    static constexpr float kMaxCurrentAmps{15.0f};
    static constexpr float kMaxTempCelsius{80.0f};
    static constexpr float kConfidenceThreshold{0.75f};

    constexpr HybridArbiter() noexcept = default;

    [[nodiscard]] ArbiterResult process_step(
        const Telemetry& telem,
        const MlProposal& ml,
        float dt_sec
    ) noexcept {
        // 1. Апаратний захист: безумовна перевірка критичних інваріантів
        if (telem.temperature_c >= kMaxTempCelsius || telem.current_amps >= kMaxCurrentAmps) {
            emergency_state_ = true;
            ++fallback_counter_;
            last_applied_speed_ = 0.0f;
            return {.applied_speed = 0.0f, .source = DecisionSource::RuleFallback};
        }

        // 2. Оцінка валідності пропозиції нейромережі
        const bool ml_valid = ml.inference_valid && 
                              (ml.confidence >= kConfidenceThreshold) && 
                              !emergency_state_;

        if (ml_valid) {
            // 3. Обмеження амплітуди та прискорення (Safety Envelope)
            const float clamped_target = std::clamp(ml.proposed_speed, -kMaxSpeedRadS, kMaxSpeedRadS);
            const float max_delta = kMaxAccelRadS2 * dt_sec;
            const float actual_delta = clamped_target - last_applied_speed_;

            if (std::abs(actual_delta) <= max_delta) {
                last_applied_speed_ = clamped_target;
                return {.applied_speed = clamped_target, .source = DecisionSource::MlOptimal};
            }

            const float adjusted_speed = last_applied_speed_ + std::clamp(actual_delta, -max_delta, max_delta);
            last_applied_speed_ = adjusted_speed;
            return {.applied_speed = adjusted_speed, .source = DecisionSource::RuleClamped};
        }

        // 4. Резервний детермінований контролер (Fail-safe Deceleration)
        ++fallback_counter_;
        const float max_delta = kMaxAccelRadS2 * dt_sec;
        if (last_applied_speed_ > max_delta) {
            last_applied_speed_ -= max_delta;
        } else if (last_applied_speed_ < -max_delta) {
            last_applied_speed_ += max_delta;
        } else {
            last_applied_speed_ = 0.0f;
        }

        return {.applied_speed = last_applied_speed_, .source = DecisionSource::RuleFallback};
    }

    [[nodiscard]] constexpr uint32_t fallback_count() const noexcept { return fallback_counter_; }
    constexpr void reset_emergency() noexcept { emergency_state_ = false; }

private:
    float last_applied_speed_{0.0f};
    uint32_t fallback_counter_{0};
    bool emergency_state_{false};
};

} // namespace embedded::control
