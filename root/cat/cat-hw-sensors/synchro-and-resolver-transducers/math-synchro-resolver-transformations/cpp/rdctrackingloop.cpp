#include <cmath>
#include <numbers>

class RdcTrackingLoop {
public:
    RdcTrackingLoop(float kp, float ki, float sample_time_sec)
        : kp_(kp), ki_(ki), ts_(sample_time_sec) {}

    void update(float v_sin, float v_cos) {
        // Сигнал тригонометричної неузгодженості
        const float error = v_sin * std::cos(theta_hat_) - v_cos * std::sin(theta_hat_);

        // Пропорційно-інтегральний фільтр контуру
        integrator_state_ += ki_ * ts_ * error;
        omega_hat_ = kp_ * error + integrator_state_;

        // Оновлення оцінки кутового положення
        theta_hat_ += ts_ * omega_hat_;

        // Приведення кута до діапазону [0, 2π)
        constexpr float two_pi = 2.0f * std::numbers::pi_v<float>;
        if (theta_hat_ >= two_pi) {
            theta_hat_ -= two_pi;
        } else if (theta_hat_ < 0.0f) {
            theta_hat_ += two_pi;
        }
    }

    [[nodiscard]] float get_angle() const noexcept { return theta_hat_; }
    [[nodiscard]] float get_velocity() const noexcept { return omega_hat_; }

private:
    float kp_{0.0f};
    float ki_{0.0f};
    float ts_{0.001f};
    float theta_hat_{0.0f};
    float omega_hat_{0.0f};
    float integrator_state_{0.0f};
};
