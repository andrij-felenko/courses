#include <cstdint>
#include <cmath>
#include <algorithm>
#include <numbers>

class PztPllController {
public:
    PztPllController(float init_freq_hz, float min_f_hz, float max_f_hz) noexcept
        : current_freq_hz_(init_freq_hz),
          min_freq_hz_(min_f_hz),
          max_freq_hz_(max_f_hz) {}

    // Оновлення частоти за виміряним фазовим зсувом (в радіанах)
    [[nodiscard]] float update(float measured_phase_rad, float dt_sec) noexcept {
        if (dt_sec <= 0.0f) return current_freq_hz_;

        const float error = target_phase_rad_ - measured_phase_rad;
        
        integral_sum_ += error * dt_sec;
        integral_sum_ = std::clamp(integral_sum_, -200.0f, 200.0f);

        const float derivative = (error - prev_error_) / dt_sec;
        prev_error_ = error;

        const float freq_delta = (kp_ * error) + (ki_ * integral_sum_) + (kd_ * derivative);
        current_freq_hz_ = std::clamp(current_freq_hz_ + freq_delta, min_freq_hz_, max_freq_hz_);

        return current_freq_hz_;

    }

    [[nodiscard]] float current_frequency() const noexcept { return current_freq_hz_; }

    // Розрахунок компенсаційної індуктивності L_comp
    [[nodiscard]] static constexpr float calculate_l_comp(float static_cap_farad, float resonant_freq_hz) noexcept {
        if (static_cap_farad <= 0.0f || resonant_freq_hz <= 0.0f) return 0.0f;
        const float omega = 2.0f * std::numbers::pi_v<float> * resonant_freq_hz;
        return 1.0f / (omega * omega * static_cap_farad);
    }

private:
    float target_phase_rad_{0.0f};
    float kp_{25.0f};
    float ki_{4.5f};
    float kd_{0.5f};
    float current_freq_hz_;
    float min_freq_hz_;
    float max_freq_hz_;
    float integral_sum_{0.0f};
    float prev_error_{0.0f};
};
