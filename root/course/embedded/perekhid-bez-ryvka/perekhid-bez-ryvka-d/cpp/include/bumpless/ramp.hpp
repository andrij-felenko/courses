#pragma once

namespace bumpless {

// Генератори траєкторій: усе, що стоїть МІЖ ціллю місії та входом контуру.

// Метод 1: обмежувач швидкості наростання. max_step = rate_max * dt;
// max_step <= 0 означає «ремпінг вимкнено».
[[nodiscard]] float slew_step(float current, float target, float max_step) noexcept;

// Метод 2: фільтр нижніх частот першого порядку, alpha = dt / (dt + tau).
[[nodiscard]] float lpf_step(float current, float target, float dt, float tau) noexcept;

// Метод 3: мінімально-ривковий поліном 5-го порядку
//     s(x) = 10x^3 - 15x^4 + 6x^5,  x = t / T,
// у якого обмежені всі три похідні:
//     max|s'| = 1.875*D/T,  max|s''| = 10/sqrt(3)*D/T^2,  max|s'''| = 60*D/T^3.
// Тривалість T беремо найбільшу з трьох — інакше одна з меж порушиться.
class SCurve {
public:
    SCurve(float start, float goal, float v_max, float a_max, float j_max) noexcept;

    // Повертає true, поки профіль триває.
    bool step(float dt) noexcept;

    [[nodiscard]] float position() const noexcept { return position_; }
    [[nodiscard]] float velocity() const noexcept { return velocity_; }
    [[nodiscard]] float acceleration() const noexcept { return acceleration_; }
    [[nodiscard]] float duration() const noexcept { return duration_; }
    [[nodiscard]] bool active() const noexcept { return active_; }

private:
    float start_{0.0f};
    float delta_{0.0f};
    float duration_{0.0f};
    float t_{0.0f};
    float position_{0.0f};
    float velocity_{0.0f};
    float acceleration_{0.0f};
    bool active_{false};
};

} // namespace bumpless
