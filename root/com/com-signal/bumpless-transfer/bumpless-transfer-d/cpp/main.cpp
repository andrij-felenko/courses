#include <algorithm>

enum class PidMode {
    Manual,
    Tracking,
    Auto
};

class BumplessPidController {
public:
    struct Config {
        float kp{1.0f};
        float ki{0.1f};
        float kd{0.05f};
        float kt{1.0f};          // Коефіцієнт стеження (1 / Tt)
        float b_weight{1.0f};    // Вага уставки в P-складовій
        float tf_d{0.01f};       // Стала часу ФНЧ похідної
        float u_min{-100.0f};
        float u_max{100.0f};
        float ramp_rate{50.0f};  // Максимальна швидкість зміни уставки
    };

    explicit BumplessPidController(const Config& cfg) : cfg_(cfg) {}

    // Безударна зміна коефіцієнта Kp під час роботи
    void set_kp(float new_kp, float current_error) noexcept {
        if (mode_ == PidMode::Auto) {
            // Компенсація стану: I_new = I_old - ΔKp * e
            integrator_ -= (new_kp - cfg_.kp) * current_error;
        }
        cfg_.kp = new_kp;
    }

    void set_mode(PidMode new_mode) noexcept {
        mode_ = new_mode;
    }

    [[nodiscard]] PidMode mode() const noexcept {
        return mode_;
    }

    // Один дискретний крок обчислення
    float step(float r_raw, float y, float u_manual, float dt) noexcept {
        // 1. Профілювання уставки (Setpoint Ramping)
        const float max_delta_r = cfg_.ramp_rate * dt;
        const float delta_r = r_raw - r_filtered_;
        r_filtered_ += std::clamp(delta_r, -max_delta_r, max_delta_r);

        const float e = r_filtered_ - y;

        // 2. D-складова від виміру з аперіодичним фільтром
        const float dy = (y - y_prev_) / dt;
        const float alpha_d = dt / (dt + cfg_.tf_d);
        deriv_filtered_ += alpha_d * (-dy - deriv_filtered_);
        y_prev_ = y;

        // 3. Режими ручного керування та узгодження (Manual / Tracking)
        if (mode_ == PidMode::Manual || mode_ == PidMode::Tracking) {
            const float u_act = std::clamp(u_manual, cfg_.u_min, cfg_.u_max);
            const float u_p = cfg_.kp * (cfg_.b_weight * r_filtered_ - y);
            const float u_d = cfg_.kd * deriv_filtered_;

            // Зворотний перерахунок інтегратора під фактичне положення актуатора
            integrator_ = u_act - u_p - u_d;
            return u_act;
        }

        // 4. Автоматичний режим (2-DoF PID)
        const float u_p = cfg_.kp * (cfg_.b_weight * r_filtered_ - y);
        const float u_d = cfg_.kd * deriv_filtered_;
        const float u_calc = u_p + integrator_ + u_d;

        const float u_act = std::clamp(u_calc, cfg_.u_min, cfg_.u_max);

        // 5. Інтегрування з корекцією насичення (Back-calculation)
        const float tracking_err = u_act - u_calc;
        integrator_ += (cfg_.ki * e + cfg_.kt * tracking_err) * dt;

        return u_act;
    }

private:
    Config cfg_;
    PidMode mode_{PidMode::Manual};
    float integrator_{0.0f};
    float y_prev_{0.0f};
    float deriv_filtered_{0.0f};
    float r_filtered_{0.0f};
};
