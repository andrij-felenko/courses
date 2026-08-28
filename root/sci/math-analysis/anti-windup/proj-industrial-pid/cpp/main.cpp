// Промисловий цифровий ПІД-регулятор з Anti-Windup (C++20)

#include <algorithm>
#include <cmath>
#include <concepts>
#include <cstdint>

enum class AntiWindupMode : uint8_t {
    None,
    Clamping,
    BackCalculation
};

struct PidGains {
    float kp{1.0f};          // Пропорційний коефіцієнт
    float ti{1.0f};          // Стала часу інтегрування (с)
    float td{0.0f};          // Стала часу диференціювання (с)
    float tt{1.0f};          // Стала часу стеження anti-windup (с)
    float nd{10.0f};         // Коефіцієнт фільтра D-члена (типово 10)
    float beta{1.0f};        // Ваговий коефіцієнт уставки P-члена (0..1)
};

struct PidLimits {
    float out_min{0.0f};
    float out_max{100.0f};
};

class PidController {
public:
    constexpr PidController(PidGains gains, PidLimits limits, float ts,
                            AntiWindupMode mode = AntiWindupMode::BackCalculation) noexcept
        : gains_{sanitize_gains(gains)},
          limits_{limits},
          ts_{ts > 0.0f ? ts : 0.01f},
          mode_{mode} {}

    void reset(float current_pv = 0.0f) noexcept {
        integrator_state_ = 0.0f;
        deriv_filter_state_ = 0.0f;
        prev_pv_ = current_pv;
        prev_unsat_out_ = 0.0f;
        prev_sat_out_ = 0.0f;
        is_manual_ = false;
    }

    void set_manual(float manual_output, float current_pv) noexcept {
        is_manual_ = true;
        prev_pv_ = current_pv;
        prev_sat_out_ = std::clamp(manual_output, limits_.out_min, limits_.out_max);
        prev_unsat_out_ = prev_sat_out_;

        // Безударний перехід: підгонка інтегратора під поточний вихід
        const float p_term = gains_.kp * (gains_.beta * current_pv - current_pv);
        integrator_state_ = prev_sat_out_ - p_term;
    }

    void set_auto() noexcept {
        is_manual_ = false;
    }

    [[nodiscard]] float update(float setpoint, float process_variable) noexcept {
        if (is_manual_) {
            return prev_sat_out_;
        }

        const float error = setpoint - process_variable;

        // 1. Пропорційний канал із вагою уставки
        const float p_term = gains_.kp * (gains_.beta * setpoint - process_variable);

        // 2. Диференціювання за вимірюванням з аперіодичним фільтром
        float d_term = 0.0f;
        if (gains_.td > 0.0f) {
            const float denom = gains_.td + gains_.nd * ts_;
            const float alpha = gains_.td / denom;
            const float beta_d = (gains_.kp * gains_.td * gains_.nd) / denom;
            const float delta_pv = process_variable - prev_pv_;

            deriv_filter_state_ = alpha * deriv_filter_state_ - beta_d * delta_pv;
            d_term = deriv_filter_state_;
        }

        // 3. Інтегральний канал із захистом Anti-Windup
        const float ki_gain = (gains_.kp / gains_.ti) * ts_;

        switch (mode_) {
            case AntiWindupMode::Clamping: {
                const bool saturated_high = (prev_unsat_out_ >= limits_.out_max);
                const bool saturated_low  = (prev_unsat_out_ <= limits_.out_min);
                const bool pushes_high    = (error > 0.0f);
                const bool pushes_low     = (error < 0.0f);

                const bool clamp = (saturated_high && pushes_high) || (saturated_low && pushes_low);
                if (!clamp) {
                    integrator_state_ += ki_gain * error;
                }
                break;
            }

            case AntiWindupMode::BackCalculation: {
                const float tracking_error = prev_sat_out_ - prev_unsat_out_;
                const float tracking_correction = (ts_ / gains_.tt) * tracking_error;
                integrator_state_ += ki_gain * error + tracking_correction;
                break;
            }

            case AntiWindupMode::None:
            default:
                integrator_state_ += ki_gain * error;
                break;
        }

        // 4. Повний ненасичений сигнал
        const float unsat_out = p_term + integrator_state_ + d_term;

        // 5. Фізичне насичення
        const float sat_out = std::clamp(unsat_out, limits_.out_min, limits_.out_max);

        // Оновлення збереженого стану
        prev_pv_ = process_variable;
        prev_unsat_out_ = unsat_out;
        prev_sat_out_ = sat_out;

        return sat_out;
    }

    [[nodiscard]] float integrator_state() const noexcept { return integrator_state_; }
    [[nodiscard]] bool is_saturated() const noexcept {
        return prev_unsat_out_ != prev_sat_out_;
    }

private:
    static constexpr PidGains sanitize_gains(PidGains g) noexcept {
        if (g.ti <= 0.0f) g.ti = 1e-3f;
        if (g.td < 0.0f)  g.td = 0.0f;
        if (g.tt <= 0.0f) g.tt = g.ti;
        if (g.nd <= 0.0f) g.nd = 10.0f;
        g.beta = std::clamp(g.beta, 0.0f, 1.0f);
        return g;
    }

    PidGains gains_;
    PidLimits limits_;
    float ts_{0.01f};
    AntiWindupMode mode_{AntiWindupMode::BackCalculation};

    float integrator_state_{0.0f};
    float deriv_filter_state_{0.0f};
    float prev_pv_{0.0f};
    float prev_unsat_out_{0.0f};
    float prev_sat_out_{0.0f};
    bool is_manual_{false};
};
