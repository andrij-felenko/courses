#include <array>
#include <span>
#include <cmath>
#include <cstdint>
#include <optional>

namespace robotics::sensing {

constexpr size_t WrenchDimensions = 6;

struct Wrench6D {
    float fx{0.0f};
    float fy{0.0f};
    float fz{0.0f};
    float mx{0.0f};
    float my{0.0f};
    float mz{0.0f};

    [[nodiscard]] constexpr float force_norm() const noexcept {
        return std::sqrt(fx * fx + fy * fy + fz * fz);
    }
};

/* Клас обробки 6-осьового силомоментного давача на базі C++20 */
class ForceTorqueSensor {
public:
    using Matrix6x6 = std::array<std::array<float, WrenchDimensions>, WrenchDimensions>;
    using RawChannels = std::array<int32_t, WrenchDimensions>;

    constexpr ForceTorqueSensor(const Matrix6x6& calib_matrix, float counts_to_volts) noexcept
        : calib_matrix_{calib_matrix}, counts_to_volts_{counts_to_volts} {}

    void tare(const RawChannels& raw_adc) noexcept {
        for (size_t i = 0; i < WrenchDimensions; ++i) {
            tare_offset_[i] = static_cast<float>(raw_adc[i]) * counts_to_volts_;
        }
        is_tared_ = true;
    }

    [[nodiscard]] Wrench6D process(const RawChannels& raw_adc) const noexcept {
        std::array<float, WrenchDimensions> v_diff{};
        for (size_t i = 0; i < WrenchDimensions; ++i) {
            const float v = static_cast<float>(raw_adc[i]) * counts_to_volts_;
            v_diff[i] = is_tared_ ? (v - tare_offset_[i]) : v;
        }

        std::array<float, WrenchDimensions> wrench_raw{};
        for (size_t row = 0; row < WrenchDimensions; ++row) {
            for (size_t col = 0; col < WrenchDimensions; ++col) {
                wrench_raw[row] += calib_matrix_[row][col] * v_diff[col];
            }
        }

        return Wrench6D{
            .fx = wrench_raw[0],
            .fy = wrench_raw[1],
            .fz = wrench_raw[2],
            .mx = wrench_raw[3],
            .my = wrench_raw[4],
            .mz = wrench_raw[5]
        };
    }

private:
    Matrix6x6 calib_matrix_{};
    std::array<float, WrenchDimensions> tare_offset_{};
    float counts_to_volts_{1.0f};
    bool is_tared_{false};
};

/* Клас спостерігача узагальненого імпульсу та детектування зіткнень */
template <size_t JointsCount>
class MomentumCollisionObserver {
public:
    using JointArray = std::array<float, JointsCount>;
    using MassMatrix = std::array<std::array<float, JointsCount>, JointsCount>;

    struct Config {
        JointArray gains;
        JointArray base_thresholds;
        JointArray vel_threshold_gains;
    };

    explicit MomentumCollisionObserver(const Config& config) noexcept : cfg_{config} {
        integral_state_.fill(0.0f);
        residuals_.fill(0.0f);
    }

    struct UpdateResult {
        JointArray estimated_ext_torque;
        bool collision_triggered;
    };

    [[nodiscard]] UpdateResult update(std::span<const float, JointsCount> q_vel,
                                     std::span<const float, JointsCount> tau_cmd,
                                     const MassMatrix& mass_matrix,
                                     std::span<const float, JointsCount> coriolis_gravity,
                                     float dt) noexcept {
        JointArray p_current{};
        for (size_t i = 0; i < JointsCount; ++i) {
            for (size_t j = 0; j < JointsCount; ++j) {
                p_current[i] += mass_matrix[i][j] * q_vel[j];
            }
        }

        bool collision = false;
        for (size_t i = 0; i < JointsCount; ++i) {
            const float integrand = tau_cmd[i] + coriolis_gravity[i] + residuals_[i];
            integral_state_[i] += integrand * dt;
            residuals_[i] = cfg_.gains[i] * (p_current[i] - integral_state_[i]);

            const float dynamic_thr = cfg_.base_thresholds[i] +
                                      cfg_.vel_threshold_gains[i] * std::abs(q_vel[i]);

            if (std::abs(residuals_[i]) > dynamic_thr) {
                collision = true;
            }
        }

        return UpdateResult{
            .estimated_ext_torque = residuals_,
            .collision_triggered = collision
        };
    }

    void reset() noexcept {
        integral_state_.fill(0.0f);
        residuals_.fill(0.0f);
    }

private:
    Config cfg_;
    JointArray integral_state_{};
    JointArray residuals_{};
};

} // namespace robotics::sensing
