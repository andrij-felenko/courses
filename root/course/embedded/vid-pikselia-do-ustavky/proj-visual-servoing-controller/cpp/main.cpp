#include <array>
#include <chrono>
#include <cmath>
#include <concepts>
#include <cstdint>
#include <optional>

namespace guidance {

using Microseconds = std::chrono::microseconds;
using SecondsF = std::chrono::duration<float>;

/* ── Параметри камери та калібрування ───────────────────────────────────── */
struct CameraIntrinsics {
    float fx{800.0f};
    float fy{800.0f};
    float cx{320.0f};
    float cy{240.0f};
    float img_width{640.0f};
    float img_height{480.0f};
};

/* ── Вимірювання від детектора ──────────────────────────────────────────── */
struct TargetDetection {
    float u{0.0f};
    float v{0.0f};
    float width{0.0f};
    float height{0.0f};
    Microseconds timestamp{0};
    bool valid{false};

    [[nodiscard]] constexpr float scale() const noexcept {
        return std::sqrt(width * height);
    }
};

/* ── Вихідні уставки для автопілота ──────────────────────────────────────── */
struct GuidanceSetpoints {
    float yaw_rate_rad_s{0.0f};
    float pitch_rate_rad_s{0.0f};
    float forward_vel_m_s{0.0f};
    bool target_acquired{false};
};

/* ── 1D Фільтр Калмана з компенсацією власного обертання ─────────────────── */
class KalmanAxisTracker {
public:
    constexpr KalmanAxisTracker(float q_angle = 0.01f, float q_rate = 0.5f, float r_meas = 0.005f) noexcept
        : q_angle_(q_angle), q_rate_(q_rate), r_meas_(r_meas) {}

    void predict(float dt, float gyro_rate_rad_s) noexcept {
        if (dt <= 0.0f || dt > 1.0f) return;

        /* Динаміка відносного руху */
        const float apparent_rate = rate_ - gyro_rate_rad_s;
        angle_ += apparent_rate * dt;

        /* Оновлення коваріації P = F * P * F^T + Q */
        const float p00 = P_[0][0] + dt * (P_[1][0] + P_[0][1]) + dt * dt * P_[1][1] + q_angle_ * dt;
        const float p01 = P_[0][1] + dt * P_[1][1];
        const float p10 = P_[1][0] + dt * P_[1][1];
        const float p11 = P_[1][1] + q_rate_ * dt;

        P_[0][0] = p00;
        P_[0][1] = p01;
        P_[1][0] = p10;
        P_[1][1] = p11;
    }

    void update(float measured_angle) noexcept {
        const float y = measured_angle - angle_;
        const float s = P_[0][0] + r_meas_;
        if (std::abs(s) < 1e-6f) return;

        const float k0 = P_[0][0] / s;
        const float k1 = P_[1][0] / s;

        angle_ += k0 * y;
        rate_  += k1 * y;

        const float p00_new = (1.0f - k0) * P_[0][0];
        const float p01_new = (1.0f - k0) * P_[0][1];
        const float p10_new = P_[1][0] - k1 * P_[0][0];
        const float p11_new = P_[1][1] - k1 * P_[0][1];

        P_[0][0] = p00_new;
        P_[0][1] = p01_new;
        P_[1][0] = p10_new;
        P_[1][1] = p11_new;
    }

    [[nodiscard]] std::pair<float, float> extrapolate(float latency_s) const noexcept {
        return {angle_ + rate_ * latency_s, rate_};
    }

    [[nodiscard]] float angle() const noexcept { return angle_; }
    [[nodiscard]] float rate() const noexcept { return rate_; }

private:
    float angle_{0.0f};
    float rate_{0.0f};
    std::array<std::array<float, 2>, 2> P_{{{0.1f, 0.0f}, {0.0f, 1.0f}}};
    float q_angle_;
    float q_rate_;
    float r_meas_;
};

/* ── ПІД-регулятор із захистом від насичення (Anti-Windup) ────────────────── */
class ServoingPID {
public:
    struct Config {
        float kp{1.8f};
        float ki{0.1f};
        float kd{0.15f};
        float max_output{1.0f};
        float max_integral{0.3f};
        float deadband{0.008f};
    };

    explicit ServoingPID(const Config& cfg) noexcept : cfg_(cfg) {}

    float update(float error, float measured_val, float dt) noexcept {
        if (dt <= 0.0f) return 0.0f;

        if (std::abs(error) < cfg_.deadband) {
            error = 0.0f;
        }

        const float p_term = cfg_.kp * error;

        integral_ = std::clamp(integral_ + error * dt, -cfg_.max_integral, cfg_.max_integral);
        const float i_term = cfg_.ki * integral_;

        float d_term = 0.0f;
        if (initialized_) {
            const float d_meas = (measured_val - prev_meas_) / dt;
            d_term = -cfg_.kd * d_meas;
        } else {
            initialized_ = true;
        }
        prev_meas_ = measured_val;

        return std::clamp(p_term + i_term + d_term, -cfg_.max_output, cfg_.max_output);
    }

    void reset() noexcept {
        integral_ = 0.0f;
        prev_meas_ = 0.0f;
        initialized_ = false;
    }

private:
    Config cfg_;
    float integral_{0.0f};
    float prev_meas_{0.0f};
    bool initialized_{false};
};

/* ── Головний клас візуального наведення ──────────────────────────────────── */
class VisualServoingController {
public:
    explicit VisualServoingController(CameraIntrinsics camera) noexcept
        : camera_(camera),
          pid_yaw_({.kp = 1.8f, .ki = 0.1f, .kd = 0.15f, .max_output = 1.0f, .max_integral = 0.3f, .deadband = 0.008f}),
          pid_pitch_({.kp = 1.8f, .ki = 0.1f, .kd = 0.15f, .max_output = 0.8f, .max_integral = 0.2f, .deadband = 0.008f}),
          pid_forward_({.kp = 0.02f, .ki = 0.001f, .kd = 0.005f, .max_output = 3.0f, .max_integral = 0.5f, .deadband = 2.0f}) {}

    void onDetection(const TargetDetection& det) noexcept {
        if (!det.valid) {
            tracked_ = false;
            return;
        }

        /* Перехід до кутових похибок за моделлю камери-обскури */
        const float norm_x = (det.u - camera_.cx) / camera_.fx;
        const float norm_y = (det.v - camera_.cy) / camera_.fy;

        kf_yaw_.update(std::atan(norm_x));
        kf_pitch_.update(std::atan(norm_y));

        last_frame_time_ = det.timestamp;
        current_scale_ = det.scale();
        tracked_ = true;
    }

    GuidanceSetpoints update(Microseconds current_time,
                              float gyro_yaw_rad_s,
                              float gyro_pitch_rad_s) noexcept {
        if (!tracked_ || last_exec_time_.count() == 0) {
            last_exec_time_ = current_time;
            return {};
        }

        const float dt = std::chrono::duration<float>(current_time - last_exec_time_).count();
        last_exec_time_ = current_time;

        /* 1. Прогноз стану за моделлю руху та гіроскопами */
        kf_yaw_.predict(dt, gyro_yaw_rad_s);
        kf_pitch_.predict(dt, gyro_pitch_rad_s);

        /* 2. Компенсація повної латентності контуру */
        const float latency_s = std::chrono::duration<float>(current_time - last_frame_time_).count();
        if (latency_s > 0.5f) {
            tracked_ = false;
            return {};
        }

        const auto [est_yaw_angle, est_yaw_rate] = kf_yaw_.extrapolate(latency_s);
        const auto [est_pitch_angle, est_pitch_rate] = kf_pitch_.extrapolate(latency_s);

        /* 3. Формування уставок кутових швидкостей */
        GuidanceSetpoints sp{};
        sp.yaw_rate_rad_s = pid_yaw_.update(est_yaw_angle, est_yaw_angle, dt);
        sp.pitch_rate_rad_s = -pid_pitch_.update(est_pitch_angle, est_pitch_angle, dt);

        /* 4. Формування поздовжньої швидкості за масштабом рамки */
        if (current_scale_ > 5.0f) {
            const float err_scale = desired_scale_ - current_scale_;
            sp.forward_vel_m_s = pid_forward_.update(err_scale, current_scale_, dt);
        }

        sp.target_acquired = true;
        return sp;
    }

    void setDesiredScale(float scale_px) noexcept { desired_scale_ = scale_px; }
    [[nodiscard]] bool isTracking() const noexcept { return tracked_; }

private:
    CameraIntrinsics camera_;
    KalmanAxisTracker kf_yaw_{0.01f, 0.5f, 0.005f};
    KalmanAxisTracker kf_pitch_{0.01f, 0.5f, 0.005f};
    ServoingPID pid_yaw_;
    ServoingPID pid_pitch_;
    ServoingPID pid_forward_;

    float desired_scale_{80.0f};
    float current_scale_{0.0f};
    Microseconds last_frame_time_{0};
    Microseconds last_exec_time_{0};
    bool tracked_{false};
};

} // namespace guidance
