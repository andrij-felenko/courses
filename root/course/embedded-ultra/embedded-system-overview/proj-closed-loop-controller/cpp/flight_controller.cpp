// =============================================================================
// flight_controller.cpp — Ідіоматична C++ реалізація без динамічної пам'яті
// =============================================================================
#include <array>
#include <algorithm>
#include <cstdint>
#include <span>

namespace flight {

// Фізичні та алгоритмічні константи часу компіляції
struct Config {
    static constexpr float loop_period_sec = 0.001f; // 1 кГц
    static constexpr float filter_alpha    = 0.98f;
    static constexpr uint16_t motor_min_pwm  = 1000;
    static constexpr uint16_t motor_max_pwm  = 2000;
    static constexpr uint16_t motor_idle_pwm = 1100;
    static constexpr float rad_to_deg      = 57.29578f;
};

// 3D-вектор з базовими операціями
struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3f operator+(const Vector3f& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3f operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
};

// Клас дискретного ПІД-регулятора із захистом від насичення
class PidController {
public:
    constexpr PidController(float kp, float ki, float kd, float out_limit, float int_limit) noexcept
        : kp_{kp}, ki_{ki}, kd_{kd}, out_limit_{out_limit}, int_limit_{int_limit} {}

    float update(float target, float current, float dt) noexcept {
        const float error = target - current;

        // Пропорційна ланка
        const float p_term = kp_ * error;

        // Інтегральна ланка з anti-windup обмеженням
        integral_ += error * dt;
        integral_ = std::clamp(integral_, -int_limit_, int_limit_);
        const float i_term = ki_ * integral_;

        // Диференціальна ланка
        float d_term = 0.0f;
        if (dt > 0.0f) {
            d_term = kd_ * ((error - prev_error_) / dt);
        }
        prev_error_ = error;

        // Насичення виходу
        return std::clamp(p_term + i_term + d_term, -out_limit_, out_limit_);
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_error_ = 0.0f;
    }

private:
    float kp_;
    float ki_;
    float kd_;
    float integral_{0.0f};
    float prev_error_{0.0f};
    float out_limit_;
    float int_limit_;
};

// Клас комплементарної оцінки орієнтації
class AttitudeEstimator {
public:
    void update(const Vector3f& gyro_dps, const Vector3f& accel_g, float dt) noexcept {
        const float accel_roll  = accel_g.y * Config::rad_to_deg;
        const float accel_pitch = -accel_g.x * Config::rad_to_deg;

        attitude_.x = Config::filter_alpha * (attitude_.x + gyro_dps.x * dt)
                    + (1.0f - Config::filter_alpha) * accel_roll;
        attitude_.y = Config::filter_alpha * (attitude_.y + gyro_dps.y * dt)
                    + (1.0f - Config::filter_alpha) * accel_pitch;
        attitude_.z += gyro_dps.z * dt;
    }

    [[nodiscard]] const Vector3f& attitude() const noexcept { return attitude_; }

private:
    Vector3f attitude_{};
};

// Мікшер моторів Quad-X
class MotorMixer {
public:
    using PwmOutputs = std::array<uint16_t, 4>;

    static PwmOutputs compute(float throttle, float roll, float pitch, float yaw, bool armed) noexcept {
        PwmOutputs outputs{};
        if (!armed) {
            outputs.fill(Config::motor_min_pwm);
            return outputs;
        }

        const float base = Config::motor_min_pwm
                         + throttle * (Config::motor_max_pwm - Config::motor_min_pwm);
        const float clamped_base = std::max(base, static_cast<float>(Config::motor_idle_pwm));

        const std::array<float, 4> raw = {
            clamped_base - roll + pitch + yaw, // M1
            clamped_base - roll - pitch - yaw, // M2
            clamped_base + roll - pitch + yaw, // M3
            clamped_base + roll + pitch - yaw  // M4
        };

        for (size_t i = 0; i < 4; ++i) {
            const float val = std::clamp(raw[i],
                                         static_cast<float>(Config::motor_idle_pwm),
                                         static_cast<float>(Config::motor_max_pwm));
            outputs[i] = static_cast<uint16_t>(val);
        }
        return outputs;
    }
};

// Інтерфейс драйверів апаратного рівня
class HardwareBridge {
public:
    virtual ~HardwareBridge() = default;
    virtual bool wait_tick() noexcept = 0;
    virtual void read_imu(Vector3f& gyro, Vector3f& accel) noexcept = 0;
    virtual void read_radio(Vector3f& target, float& throttle, bool& armed) noexcept = 0;
    virtual void write_motors(std::span<const uint16_t, 4> pwm) noexcept = 0;
    virtual void feed_watchdog() noexcept = 0;
};

// Головний контролер польоту (композиція компонентів)
class FlightController {
public:
    explicit FlightController(HardwareBridge& hw) noexcept
        : hw_{hw},
          pid_roll_{2.5f, 0.4f, 0.08f, 300.0f, 100.0f},
          pid_pitch_{2.5f, 0.4f, 0.08f, 300.0f, 100.0f},
          pid_yaw_{4.0f, 0.8f, 0.00f, 400.0f, 150.0f} {}

    void run() noexcept {
        Vector3f gyro{};
        Vector3f accel{};
        Vector3f target_angle{};
        float throttle{0.0f};
        bool armed{false};

        while (true) {
            if (!hw_.wait_tick()) {
                continue;
            }

            hw_.read_imu(gyro, accel);
            estimator_.update(gyro, accel, Config::loop_period_sec);
            hw_.read_radio(target_angle, throttle, armed);

            const auto& att = estimator_.attitude();
            const float roll_u  = pid_roll_.update(target_angle.x, att.x, Config::loop_period_sec);
            const float pitch_u = pid_pitch_.update(target_angle.y, att.y, Config::loop_period_sec);
            const float yaw_u   = pid_yaw_.update(target_angle.z, gyro.z, Config::loop_period_sec);

            const auto motors = MotorMixer::compute(throttle, roll_u, pitch_u, yaw_u, armed);
            hw_.write_motors(motors);

            hw_.feed_watchdog();
        }
    }

private:
    HardwareBridge& hw_;
    AttitudeEstimator estimator_{};
    PidController pid_roll_;
    PidController pid_pitch_;
    PidController pid_yaw_;
};

} // namespace flight
