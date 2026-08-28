#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>
#include <optional>

namespace safety {

constexpr size_t kMaxClasses = 8;
constexpr size_t kWindowSize = 5;
constexpr uint16_t kRecoveryTicks = 50;

enum class SupervisorState : uint8_t {
    NominalMl,
    DegradedHold,
    RuleFallback,
    EmergencySafe
};

struct SupervisorConfig {
    float max_allowed_entropy{1.2f};
    float min_confidence_threshold{0.65f};
    uint32_t deadline_timeout_ms{25};
    uint8_t fault_threshold_n{3};
    float max_slew_rate_deg_per_s{120.0f};
    float loop_dt_s{0.02f};
    float kp{1.5f};
    float ki{0.4f};
    float kd{0.08f};
};

struct InferenceFrame {
    float u_cmd{0.0f};
    float confidence{0.0f};
    std::array<float, kMaxClasses> class_probs{};
    uint8_t num_classes{0};
    uint32_t timestamp_ms{0};
    bool is_fresh{false};
};

struct PlantFeedback {
    float current_state{0.0f};
    float target_state{0.0f};
    float current_rate{0.0f};
};

class SafeSupervisor {
public:
    explicit SafeSupervisor(const SupervisorConfig& cfg) noexcept
        : cfg_{cfg} {}

    [[nodiscard]] SupervisorState state() const noexcept { return state_; }
    [[nodiscard]] float last_output() const noexcept { return last_actuator_output_; }

    [[nodiscard]] float step(const InferenceFrame& ml_frame,
                             const PlantFeedback& fb,
                             uint32_t current_time_ms) noexcept {
        // 1. Моніторинг здоров'я
        const bool timing_fault = (current_time_ms - ml_frame.timestamp_ms) > cfg_.deadline_timeout_ms;
        const bool freshness_fault = !ml_frame.is_fresh;
        const float entropy = calculate_entropy(std::span{ml_frame.class_probs.data(), ml_frame.num_classes});
        const bool entropy_fault = (entropy > cfg_.max_allowed_entropy);
        const bool conf_fault = (ml_frame.confidence < cfg_.min_confidence_threshold);

        const bool frame_fault = timing_fault || freshness_fault || entropy_fault || conf_fault;
        const bool persistent_fault = update_fault_filter(frame_fault);

        if (!frame_fault) {
            last_valid_frame_ms_ = current_time_ms;
        }

        // 2. Детермінований класичний контур (PID)
        const float error = fb.target_state - fb.current_state;
        const float p_term = cfg_.kp * error;
        const float d_term = -cfg_.kd * fb.current_rate;
        float u_rule = p_term + pid_integrator_ + d_term;

        // 3. Автомат станів
        switch (state_) {
        case SupervisorState::NominalMl:
            if (persistent_fault) {
                state_ = SupervisorState::RuleFallback;
                recovery_counter_ = 0;
                transition_alpha_ = 0.0f;
            } else if (frame_fault) {
                state_ = SupervisorState::DegradedHold;
            } else {
                // Shadow tracking інтегратора під команду моделі
                if (cfg_.ki > 1e-5f) {
                    pid_integrator_ = ml_frame.u_cmd - p_term - d_term;
                }
            }
            break;

        case SupervisorState::DegradedHold:
            if (persistent_fault) {
                state_ = SupervisorState::RuleFallback;
                recovery_counter_ = 0;
                transition_alpha_ = 0.0f;
            } else if (!frame_fault) {
                state_ = SupervisorState::NominalMl;
            }
            break;

        case SupervisorState::RuleFallback:
            pid_integrator_ += cfg_.ki * error * cfg_.loop_dt_s;

            if (!frame_fault) {
                if (++recovery_counter_ >= kRecoveryTicks) {
                    state_ = SupervisorState::NominalMl;
                    recovery_counter_ = 0;
                }
            } else {
                recovery_counter_ = 0;
            }

            if (current_time_ms - last_valid_frame_ms_ > 10000 && std::abs(error) > 45.0f) {
                state_ = SupervisorState::EmergencySafe;
            }
            break;

        case SupervisorState::EmergencySafe:
            u_rule = 0.0f;
            break;
        }

        // 4. Безударний перехід та генерація цільового значення
        float raw_target = 0.0f;
        if (state_ == SupervisorState::NominalMl) {
            raw_target = ml_frame.u_cmd;
        } else if (state_ == SupervisorState::DegradedHold) {
            raw_target = last_actuator_output_;
        } else if (state_ == SupervisorState::RuleFallback) {
            if (transition_alpha_ < 1.0f) {
                transition_alpha_ = std::min(1.0f, transition_alpha_ + cfg_.loop_dt_s / 0.25f);
            }
            raw_target = (1.0f - transition_alpha_) * last_actuator_output_ + transition_alpha_ * u_rule;
        } else {
            raw_target = 0.0f;
        }

        // 5. Slew-rate обмеження швидкості наростання
        const float max_delta = cfg_.max_slew_rate_deg_per_s * cfg_.loop_dt_s;
        const float delta = std::clamp(raw_target - last_actuator_output_, -max_delta, max_delta);

        last_actuator_output_ += delta;
        last_error_ = error;

        return last_actuator_output_;
    }

private:
    [[nodiscard]] static float calculate_entropy(std::span<const float> probs) noexcept {
        if (probs.size() <= 1) return 0.0f;
        float h = 0.0f;
        for (float p : probs) {
            if (p > 1e-6f) {
                h -= p * std::log2(p);
            }
        }
        return h;
    }

    [[nodiscard]] bool update_fault_filter(bool current_fault) noexcept {
        fault_history_[fault_history_idx_] = current_fault ? 1 : 0;
        fault_history_idx_ = (fault_history_idx_ + 1) % kWindowSize;

        uint8_t count = 0;
        for (uint8_t val : fault_history_) {
            count += val;
        }
        return count >= cfg_.fault_threshold_n;
    }

    SupervisorConfig cfg_;
    SupervisorState state_{SupervisorState::NominalMl};
    uint32_t last_valid_frame_ms_{0};
    std::array<uint8_t, kWindowSize> fault_history_{};
    size_t fault_history_idx_{0};
    uint16_t recovery_counter_{0};

    float pid_integrator_{0.0f};
    float last_error_{0.0f};
    float last_actuator_output_{0.0f};
    float transition_alpha_{1.0f};
};

} // namespace safety
