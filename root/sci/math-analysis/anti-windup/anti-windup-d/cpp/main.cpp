// Цифровий ПІД-регулятор із контуром зворотного перерахунку Back-Calculation (C++20)

#include <algorithm>
#include <cmath>
#include <concepts>

struct PidParameters {
    float kp{1.0f};          // Пропорційний коефіцієнт
    float ti{1.0f};          // Стала часу інтегрування (с)
    float td{0.0f};          // Стала часу диференціювання (с)
    float tt{1.0f};          // Стала часу стеження anti-windup (с)
    float nd{10.0f};         // Коефіцієнт фільтра D-члена
    float ts{0.01f};         // Період дискретизації (с)
    float u_min{0.0f};       // Нижня межа насичення
    float u_max{100.0f};     // Верхня межа насичення
};

class PidController {
public:
    explicit constexpr PidController(PidParameters params) noexcept
        : p_{sanitize(params)} {}

    void reset(float initial_pv = 0.0f) noexcept {
        integrator_state_ = 0.0f;
        filter_d_state_ = 0.0f;
        prev_pv_ = initial_pv;
        prev_u_unsat_ = 0.0f;
        prev_u_sat_ = 0.0f;
    }

    [[nodiscard]] float step(float setpoint, float process_val) noexcept {
        const float error = setpoint - process_val;

        // 1. Пропорційний канал
        const float p_term = p_.kp * error;

        // 2. Диференціювання за вимірюванням з аперіодичною фільтрацією
        float d_term = 0.0f;
        if (p_.td > 0.0f) {
            const float denom = p_.td + p_.nd * p_.ts;
            const float alpha = p_.td / denom;
            const float beta  = (p_.kp * p_.td * p_.nd) / denom;
            const float delta_pv = process_val - prev_pv_;

            filter_d_state_ = alpha * filter_d_state_ - beta * delta_pv;
            d_term = filter_d_state_;
        }

        // 3. Інтегральний канал з корекцією Back-Calculation
        const float tracking_error = prev_u_sat_ - prev_u_unsat_;
        const float tracking_corr  = (p_.ts / p_.tt) * tracking_error;
        const float ki_step        = (p_.kp / p_.ti) * p_.ts * error;

        integrator_state_ += ki_step + tracking_corr;

        // 4. Повний розрахунковий вихід
        const float u_unsat = p_term + integrator_state_ + d_term;

        // 5. Оператор фізичного насичення sat(u)
        const float u_sat = std::clamp(u_unsat, p_.u_min, p_.u_max);

        // Збереження історії
        prev_pv_ = process_val;
        prev_u_unsat_ = u_unsat;
        prev_u_sat_ = u_sat;

        return u_sat;
    }

    [[nodiscard]] float integrator_state() const noexcept { return integrator_state_; }

private:
    static constexpr PidParameters sanitize(PidParameters p) noexcept {
        if (p.ti <= 0.0f) p.ti = 1e-3f;
        if (p.td < 0.0f)  p.td = 0.0f;
        if (p.tt <= 0.0f) p.tt = p.ti;
        if (p.nd <= 0.0f) p.nd = 10.0f;
        if (p.ts <= 0.0f) p.ts = 0.01f;
        return p;
    }

    PidParameters p_;
    float integrator_state_{0.0f};
    float filter_d_state_{0.0f};
    float prev_pv_{0.0f};
    float prev_u_unsat_{0.0f};
    float prev_u_sat_{0.0f};
};
