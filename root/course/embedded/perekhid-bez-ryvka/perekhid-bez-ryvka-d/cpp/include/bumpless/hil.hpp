#pragma once

namespace bumpless {

// Три тести чеклиста валідації безривкового переходу на HIL-стенді.
struct HilReport {
    // 1. Тест нульового стрибка
    unsigned switch_count{0u};
    float glitch_worst{0.0f};
    float glitch_limit{1e-4f};
    bool glitch_pass{false};

    // 2. Тест насиченого передзавантаження
    float saturated_residual{0.0f};      // зрізана передзавантаженням частина
    float saturated_first_delta{0.0f};   // приріст виходу за перші такти
    float saturated_integral_drop{0.0f}; // наскільки інтеграл зійшов з межі
    bool saturated_pass{false};

    // 3. Тест темпу наростання
    float ramp_peak_setpoint_step{0.0f};
    float ramp_allowed_setpoint_step{0.0f};
    float ramp_peak_load_g{1.0f};
    float ramp_min_load_g{1.0f};
    unsigned ramp_max_saturated_run{0u}; // найдовша серія тактів на упорі газу
    bool ramp_pass{false};

    [[nodiscard]] bool all_passed() const noexcept
    {
        return glitch_pass && saturated_pass && ramp_pass;
    }
};

[[nodiscard]] HilReport run_hil_suite();

} // namespace bumpless
