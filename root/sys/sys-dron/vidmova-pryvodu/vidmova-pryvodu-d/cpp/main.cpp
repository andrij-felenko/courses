#include <array>
#include <cmath>
#include <cstdint>
#include <span>
#include <algorithm>

class FaultToleranceManager {
public:
    static constexpr size_t kMaxActuators = 8;
    static constexpr float kFdiResidualThresh = 12.5f; // рад/с²
    static constexpr uint32_t kRpmTimeoutMs = 80;

    struct EscTelemetry {
        float rpm{0.0f};
        float current{0.0f};
        float temperature{0.0f};
        uint32_t last_update_ms{0};
        uint8_t error_flags{0};
    };

    FaultToleranceManager(size_t count,
                          std::array<float, 3> inertia,
                          const std::array<std::array<float, kMaxActuators>, 3>& b_moment)
        : actuator_count_(std::min(count, kMaxActuators)),
          inertia_(inertia),
          b_moment_(b_moment) {}

    uint8_t update(std::span<const float, 3> gyro,
                   std::span<const float, 3> gyro_prev,
                   float dt,
                   std::span<const float> actuator_cmd,
                   std::span<const EscTelemetry> telemetry,
                   uint32_t now_ms) noexcept {
        if (dt <= 0.0001f) return failed_mask_;

        // 1. Виміряне кутове прискорення
        std::array<float, 3> alpha_meas{};
        for (size_t i = 0; i < 3; ++i) {
            alpha_meas[i] = (gyro[i] - gyro_prev[i]) / dt;
        }

        // 2. Гіроскопічний момент: w x (J * w)
        const std::array<float, 3> gyro_cross_jw{
            (inertia_[2] - inertia_[1]) * gyro[1] * gyro[2],
            (inertia_[0] - inertia_[2]) * gyro[0] * gyro[2],
            (inertia_[1] - inertia_[0]) * gyro[0] * gyro[1]
        };

        // Модельний момент від активних приводів
        std::array<float, 3> expected_moment{0.0f, 0.0f, 0.0f};
        for (size_t ax = 0; ax < 3; ++ax) {
            for (size_t i = 0; i < actuator_count_; ++i) {
                if (!(failed_mask_ & (1U << i))) {
                    expected_moment[ax] += b_moment_[ax][i] * actuator_cmd[i];
                }
            }
        }

        // Оновлення фільтрованої нев'язки r(t)
        for (size_t i = 0; i < 3; ++i) {
            const float alpha_model = (expected_moment[i] - gyro_cross_jw[i]) / inertia_[i];
            const float r = alpha_meas[i] - alpha_model;
            residual_acc_[i] = 0.85f * residual_acc_[i] + 0.15f * r;
        }

        // 3. Апаратна перевірка DShot телеметрії
        for (size_t i = 0; i < actuator_count_; ++i) {
            if (failed_mask_ & (1U << i)) continue;

            const bool cmd_active = (actuator_cmd[i] > 0.15f);
            const bool rpm_zero = (telemetry[i].rpm < 50.0f);
            const bool timed_out = (now_ms - telemetry[i].last_update_ms > kRpmTimeoutMs);

            if ((cmd_active && rpm_zero) || timed_out || (telemetry[i].error_flags & 0x01)) {
                failed_mask_ |= static_cast<uint8_t>(1U << i);
            }
        }

        // 4. Ізоляція відмови за скалярним добутком нев'язки
        const float res_norm = std::sqrt(residual_acc_[0] * residual_acc_[0] +
                                         residual_acc_[1] * residual_acc_[1] +
                                         residual_acc_[2] * residual_acc_[2]);

        if (res_norm > kFdiResidualThresh) {
            int best_motor = -1;
            float best_correlation = -1.0f;

            for (size_t i = 0; i < actuator_count_; ++i) {
                if (failed_mask_ & (1U << i)) continue;

                std::array<float, 3> def_vec{};
                float def_norm_sq = 0.0f;
                for (size_t ax = 0; ax < 3; ++ax) {
                    def_vec[ax] = -b_moment_[ax][i] * actuator_cmd[i] / inertia_[ax];
                    def_norm_sq += def_vec[ax] * def_vec[ax];
                }
                const float def_norm = std::sqrt(def_norm_sq);
                if (def_norm < 0.001f) continue;

                const float dot = (residual_acc_[0] * def_vec[0] +
                                   residual_acc_[1] * def_vec[1] +
                                   residual_acc_[2] * def_vec[2]) / (res_norm * def_norm);

                if (dot > best_correlation && dot > 0.75f) {
                    best_correlation = dot;
                    best_motor = static_cast<int>(i);
                }
            }

            if (best_motor >= 0) {
                failed_mask_ |= static_cast<uint8_t>(1U << best_motor);
            }
        }

        if (actuator_count_ == 6 && failed_mask_ != 0) {
            yaw_relaxed_ = true;
        }

        return failed_mask_;
    }

    [[nodiscard]] uint8_t failed_mask() const noexcept { return failed_mask_; }
    [[nodiscard]] bool is_yaw_relaxed() const noexcept { return yaw_relaxed_; }

private:
    size_t actuator_count_{0};
    std::array<float, 3> inertia_{};
    std::array<std::array<float, kMaxActuators>, 3> b_moment_{};
    uint8_t failed_mask_{0};
    bool yaw_relaxed_{false};
    std::array<float, 3> residual_acc_{0.0f, 0.0f, 0.0f};
};
