#include <cstdint>
#include <algorithm>
#include <cmath>

namespace embedded {

enum class ArbitrationMode : uint8_t {
    Blending = 0,
    Ramping,
    WinnerTakeAll
};

struct ControlCommand {
    float command{0.0f};
    uint32_t timestamp_ms{0};
    bool valid{false};
};

struct ArbiterConfig {
    float min_output{-1.0f};
    float max_output{1.0f};
    float max_slew_rate{5.0f}; // Одиниці зміни в секунду
    float s_low{0.2f};
    float s_high{0.8f};
    float s_emergency{0.1f};
    float s_hysteresis{0.05f};
    uint32_t timeout_ms{50};
};

class ControlArbitrator {
public:
    explicit ControlArbitrator(const ArbiterConfig& config) noexcept
        : config_(config), current_mode_(ArbitrationMode::Blending), prev_output_(0.0f) {}

    float process(const ControlCommand& human,
                  const ControlCommand& auto_ctrl,
                  const ControlCommand& safety,
                  float safety_distance,
                  uint32_t current_time_ms,
                  float dt_sec) noexcept {
        
        const bool human_valid = is_valid(human, current_time_ms);
        const bool auto_valid  = is_valid(auto_ctrl, current_time_ms);
        const bool safety_valid = is_valid(safety, current_time_ms);

        // Гістерезисний автомат режимів
        if (current_mode_ == ArbitrationMode::WinnerTakeAll) {
            if (safety_distance > (config_.s_emergency + config_.s_hysteresis)) {
                current_mode_ = ArbitrationMode::Ramping;
            }
        } else {
            if (safety_valid && (safety_distance < config_.s_emergency)) {
                current_mode_ = ArbitrationMode::WinnerTakeAll;
            }
        }

        float raw_target = 0.0f;

        if (current_mode_ == ArbitrationMode::WinnerTakeAll) {
            raw_target = safety_valid ? safety.command : 0.0f;
        } else {
            if (human_valid && auto_valid) {
                const float w_auto = calculate_auto_weight(safety_distance);
                const float w_human = 1.0f - w_auto;
                raw_target = w_human * human.command + w_auto * auto_ctrl.command;
            } else if (human_valid) {
                raw_target = human.command;
            } else if (auto_valid) {
                raw_target = auto_ctrl.command;
            } else if (safety_valid) {
                raw_target = safety.command;
            }
        }

        // Slew rate limiting & Safety Clamping
        const float max_delta = config_.max_slew_rate * dt_sec;
        const float delta = std::clamp(raw_target - prev_output_, -max_delta, max_delta);
        prev_output_ = std::clamp(prev_output_ + delta, config_.min_output, config_.max_output);

        return prev_output_;
    }

    [[nodiscard]] ArbitrationMode mode() const noexcept {
        return current_mode_;
    }

private:
    [[nodiscard]] bool is_valid(const ControlCommand& cmd, uint32_t now) const noexcept {
        return cmd.valid && ((now - cmd.timestamp_ms) <= config_.timeout_ms);
    }

    [[nodiscard]] float calculate_auto_weight(float dist) const noexcept {
        if (dist <= config_.s_low) return 1.0f;
        if (dist >= config_.s_high) return 0.0f;
        const float ds = config_.s_high - config_.s_low;
        const float norm = (config_.s_high - dist) / ds;
        return norm * norm * (3.0f - 2.0f * norm);
    }

    ArbiterConfig config_;
    ArbitrationMode current_mode_;
    float prev_output_;
};

} // namespace embedded
