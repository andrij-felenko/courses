#include <cmath>
#include <algorithm>
#include <numbers>

class RatePidController {
public:
    RatePidController(float kp, float ki, float kd, float kff,
                      float cutoff_hz, float loop_rate_hz)
        : kp_{kp}, ki_{ki}, kd_{kd}, kff_{kff} {
        const float dt = 1.0f / loop_rate_hz;
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
        dterm_lpf_alpha_ = dt / (rc + dt);
    }

    void reset() noexcept {
        integrator_ = 0.0f;
        prev_gyro_ = 0.0f;
        prev_setpoint_ = 0.0f;
        dterm_filtered_ = 0.0f;
    }

    float update(float setpoint_dps, float gyro_dps, float dt, bool enable_i) noexcept {
        // 1. Помилка кутової швидкості
        const float error = setpoint_dps - gyro_dps;

        // 2. Пропорційна складова
        const float p_out = kp_ * error;

        // 3. Диференціювання за виміром (Derivative on Measurement)
        const float gyro_delta = (gyro_dps - prev_gyro_) / dt;
        prev_gyro_ = gyro_dps;

        const float raw_dterm = -kd_ * gyro_delta;
        dterm_filtered_ += dterm_lpf_alpha_ * (raw_dterm - dterm_filtered_);

        // 4. Прямий зв'язок Feedforward
        const float sp_delta = (setpoint_dps - prev_setpoint_) / dt;
        prev_setpoint_ = setpoint_dps;
        const float ff_out = kff_ * sp_delta;

        // 5. Інтегрування з обмеженням (Anti-Windup)
        if (enable_i) {
            integrator_ += ki_ * error * dt;
            integrator_ = std::clamp(integrator_, -i_limit_, i_limit_);
        } else {
            integrator_ *= 0.95f;
        }

        // 6. Сумарний вихідний момент на мікшер
        const float total_out = p_out + integrator_ + dterm_filtered_ + ff_out;
        return std::clamp(total_out, out_min_, out_max_);
    }

private:
    float kp_{0.0f};
    float ki_{0.0f};
    float kd_{0.0f};
    float kff_{0.0f};

    float integrator_{0.0f};
    float prev_gyro_{0.0f};
    float prev_setpoint_{0.0f};
    float dterm_filtered_{0.0f};

    float dterm_lpf_alpha_{0.1f};
    float out_min_{-1.0f};
    float out_max_{1.0f};
    float i_limit_{0.35f};
};
