#include <array>
#include <chrono>
#include <cmath>
#include <span>

class MotorFaultDetector {
public:
    static constexpr size_t kNumMotors = 4;
    static constexpr float kResidualThreshold = 15.0f; // рад/с^2
    static constexpr std::chrono::milliseconds kFaultDurationThreshold{100};

    MotorFaultDetector(float inertia_xx, float inertia_yy)
        : inertia_xx_(inertia_xx), inertia_yy_(inertia_yy) {
        fault_counters_.fill(std::chrono::milliseconds::zero());
        motor_failed_.fill(false);
    }

    void update(float tau_roll_cmd,
                float tau_pitch_cmd,
                float gyro_dot_roll,
                float gyro_dot_pitch,
                std::span<const float, kNumMotors> motor_thrusts,
                std::chrono::milliseconds dt) noexcept {
        const float alpha_roll_exp = tau_roll_cmd / inertia_xx_;
        const float alpha_pitch_exp = tau_pitch_cmd / inertia_yy_;

        const float err_roll = std::abs(alpha_roll_exp - gyro_dot_roll);
        const float err_pitch = std::abs(alpha_pitch_exp - gyro_dot_pitch);

        std::array<bool, kNumMotors> suspect{ false, false, false, false };

        if (err_roll > kResidualThreshold || err_pitch > kResidualThreshold) {
            if (gyro_dot_roll < alpha_roll_exp && gyro_dot_pitch > alpha_pitch_exp) suspect[0] = true;
            if (gyro_dot_roll > alpha_roll_exp && gyro_dot_pitch > alpha_pitch_exp) suspect[1] = true;
            if (gyro_dot_roll > alpha_roll_exp && gyro_dot_pitch < alpha_pitch_exp) suspect[2] = true;
            if (gyro_dot_roll < alpha_roll_exp && gyro_dot_pitch < alpha_pitch_exp) suspect[3] = true;
        }

        for (size_t i = 0; i < kNumMotors; ++i) {
            if (suspect[i] && motor_thrusts[i] > 0.2f) {
                fault_counters_[i] += dt;
                if (fault_counters_[i] >= kFaultDurationThreshold) {
                    motor_failed_[i] = true;
                }
            } else {
                if (fault_counters_[i] > std::chrono::milliseconds::zero()) {
                    fault_counters_[i] -= dt;
                }
            }
        }
    }

    [[nodiscard]] bool is_motor_failed(size_t motor_idx) const noexcept {
        return motor_idx < kNumMotors ? motor_failed_[motor_idx] : false;
    }

    [[nodiscard]] bool has_any_failure() const noexcept {
        for (bool f : motor_failed_) if (f) return true;
        return false;
    }

private:
    float inertia_xx_;
    float inertia_yy_;
    std::array<std::chrono::milliseconds, kNumMotors> fault_counters_;
    std::array<bool, kNumMotors> motor_failed_;
};
