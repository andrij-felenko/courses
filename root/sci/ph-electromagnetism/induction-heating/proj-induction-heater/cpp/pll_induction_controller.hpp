// pll_induction_controller.hpp — Ідіоматична C++17 реалізація
// контролера резонансного інвертора з RAII та шаблонами типу

#pragma once
#include <cmath>
#include <algorithm>
#include <numbers>
#include <cstdint>

namespace Induction {

struct PllConfig {
    float f_min_hz{20000.0f};
    float f_max_hz{100000.0f};
    float target_phase_rad{0.1f}; // ~5.7 град індуктивного зсуву для ZVS
    float kp{150.0f};
    float ki{2500.0f};
    float dt_sec{0.0001f};        // 100 мкс цикл
    float mcu_clock_hz{160000000.0f};
};

class ResonantPllTracker {
public:
    explicit ResonantPllTracker(const PllConfig& config, float initial_freq_hz = 30000.0f)
        : config_(config),
          current_freq_hz_(std::clamp(initial_freq_hz, config.f_min_hz, config.f_max_hz)) {
        update_timer_ticks();
    }

    // Оновлення стану резонансного фазового автоналаштування
    void process_sample(float delta_t_sec) noexcept {
        const float measured_phase = normalize_phase(2.0f * std::numbers::pi_v<float> * current_freq_hz_ * delta_t_sec);
        phase_error_rad_ = config_.target_phase_rad - measured_phase;

        const float p_term = config_.kp * phase_error_rad_;
        
        // Інтегрування з обмеженням переповнення (Anti-windup)
        integrator_sum_ += config_.ki * phase_error_rad_ * config_.dt_sec;
        const float max_integrator = (config_.f_max_hz - config_.f_min_hz) * 0.5f;
        integrator_sum_ = std::clamp(integrator_sum_, -max_integrator, max_integrator);

        const float freq_delta = p_term + integrator_sum_;
        current_freq_hz_ = std::clamp(current_freq_hz_ + freq_delta, config_.f_min_hz, config_.f_max_hz);

        update_timer_ticks();
    }

    [[nodiscard]] float current_frequency() const noexcept { return current_freq_hz_; }
    [[nodiscard]] float phase_error_deg() const noexcept { return phase_error_rad_ * (180.0f / std::numbers::pi_v<float>); }
    [[nodiscard]] uint32_t timer_arr_ticks() const noexcept { return timer_period_ticks_; }
    [[nodiscard]] bool is_zvs_locked() const noexcept { return std::abs(phase_error_deg()) < 2.0f; }

private:
    static float normalize_phase(float rad) noexcept {
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        while (rad > std::numbers::pi_v<float>)  rad -= two_pi;
        while (rad < -std::numbers::pi_v<float>) rad += two_pi;
        return rad;
    }

    void update_timer_ticks() noexcept {
        timer_period_ticks_ = static_cast<uint32_t>(config_.mcu_clock_hz / (2.0f * current_freq_hz_));
    }

    PllConfig config_;
    float current_freq_hz_{30000.0f};
    float integrator_sum_{0.0f};
    float phase_error_rad_{0.0f};
    uint32_t timer_period_ticks_{0};
};

} // namespace Induction
