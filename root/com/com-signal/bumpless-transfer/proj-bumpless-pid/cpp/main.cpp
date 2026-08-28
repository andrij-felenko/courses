#include <algorithm>
#include <cstdint>
#include <span>

enum class ControllerMode : uint8_t {
    Manual,
    Tracking,
    Auto
};

struct PidGains {
    float kp{1.0f};
    float ki{0.1f};
    float kd{0.05f};
    float kt{1.0f};          // Коефіцієнт узгодження інтегратора (1 / Tt)
    float b_weight{1.0f};    // Вага уставки в P-каналі (0.0 ... 1.0)
    float tf_deriv{0.01f};   // Стала часу фільтра похідної
};

struct ActuatorLimits {
    float u_min{-100.0f};
    float u_max{100.0f};
    float ramp_rate_max{50.0f}; // Максимальна швидкість наростання уставки
};

class BumplessPid {
public:
    BumplessPid(PidGains gains, ActuatorLimits limits, float initial_y = 0.0f) noexcept
        : gains_(gains), limits_(limits), y_prev_(initial_y), r_filt_(initial_y) {}

    // Безударне оновлення коефіцієнтів (Gain Scheduling)
    void update_gains(float new_kp, float new_ki, float new_kd) noexcept {
        if (mode_ == ControllerMode::Auto) {
            const float current_error = r_filt_ - y_prev_;
            const float delta_kp = new_kp - gains_.kp;
            // Зміщення стану інтегратора для усунення стрибка
            integrator_ -= delta_kp * current_error;
        }
        gains_.kp = new_kp;
        gains_.ki = new_ki;
        gains_.kd = new_kd;
    }

    void set_mode(ControllerMode mode) noexcept {
        mode_ = mode;
    }

    [[nodiscard]] ControllerMode mode() const noexcept {
        return mode_;
    }

    [[nodiscard]] float last_output() const noexcept {
        return u_last_;
    }

    [[nodiscard]] float filtered_setpoint() const noexcept {
        return r_filt_;
    }

    // Один дискретний крок обчислення
    float step(float r_target, float y_meas, float u_manual, float dt) noexcept {
        if (dt <= 0.0f) return u_last_;

        // 1. Профілювання уставки (Setpoint Slew-rate limit)
        const float max_step = limits_.ramp_rate_max * dt;
        const float delta_r = r_target - r_filt_;
        r_filt_ += std::clamp(delta_r, -max_step, max_step);

        const float e = r_filt_ - y_meas;

        // 2. D-складова від виміру з аперіодичним фільтром низьких частот
        const float dy = (y_meas - y_prev_) / dt;
        const float alpha_d = dt / (dt + gains_.tf_deriv);
        deriv_filt_ += alpha_d * (-dy - deriv_filt_);
        y_prev_ = y_meas;

        // 3. Обробка ручного режиму та режиму стеження (Manual / Tracking)
        if (mode_ == ControllerMode::Manual || mode_ == ControllerMode::Tracking) {
            const float u_act = std::clamp(u_manual, limits_.u_min, limits_.u_max);
            const float u_p = gains_.kp * (gains_.b_weight * r_filt_ - y_meas);
            const float u_d = gains_.kd * deriv_filt_;

            // Зворотне узгодження інтегратора: I = u_act - u_P - u_D
            integrator_ = u_act - u_p - u_d;

            u_last_ = u_act;
            return u_act;
        }

        // 4. Автоматичний режим (2-DoF PID)
        const float u_p = gains_.kp * (gains_.b_weight * r_filt_ - y_meas);
        const float u_d = gains_.kd * deriv_filt_;
        const float u_calc = u_p + integrator_ + u_d;

        // 5. Затиск виходу межами приводу
        const float u_act = std::clamp(u_calc, limits_.u_min, limits_.u_max);

        // 6. Інтегральне накопичення з контуром Back-calculation Anti-windup
        const float tracking_diff = u_act - u_calc;
        integrator_ += (gains_.ki * e + gains_.kt * tracking_diff) * dt;

        u_last_ = u_act;
        return u_act;
    }

private:
    PidGains gains_;
    ActuatorLimits limits_;
    ControllerMode mode_{ControllerMode::Manual};

    float integrator_{0.0f};
    float y_prev_{0.0f};
    float deriv_filt_{0.0f};
    float r_filt_{0.0f};
    float u_last_{0.0f};
};
