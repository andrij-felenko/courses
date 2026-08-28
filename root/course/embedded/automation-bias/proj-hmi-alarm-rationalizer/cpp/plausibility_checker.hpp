#pragma once

#include "alarm_rationalizer.hpp"
#include <concepts>
#include <cmath>
#include <span>

namespace isa18_2 {

enum class PlausibilityStatus : uint8_t {
    Valid = 0,      ///< Фізично узгоджено, висока довіра
    Degraded,       ///< Підвищена дисперсія шуму, помірна невизначеність
    Suspect,        ///< Суттєва розбіжність датчиків, потрібна перевірка
    Failed          ///< Фізична неможливість, повна втрата достовірності
};

/**
 * @brief Оцінка сенсорного вимірювання з довірчими інтервалами для інтерфейсу оператора.
 */
struct SensorConfidenceEstimate {
    float estimated_value{0.0f};
    float confidence_bound_95{0.0f};    ///< 95% довірчий інтервал (+/- 1.96 * sigma)
    float variance{0.0f};
    float residual{0.0f};
    float confidence_score{1.0f};       ///< 0.0 .. 1.0
    PlausibilityStatus status{PlausibilityStatus::Valid};
};

struct PlausibilityConfig {
    float max_allowed_accel_jerk{15.0f};
    float max_kinematic_residual{3.5f};
    float max_power_residual_w{45.0f};
    float min_confidence_alarm_threshold{0.50f};
    uint16_t diagnostic_alarm_id{0};
};

class PlausibilityChecker {
public:
    explicit PlausibilityChecker(const PlausibilityConfig& config) noexcept;

    /**
     * @brief Крос-валідація потрійного надлишкового сенсора (2-out-of-3 quorum).
     */
    [[nodiscard]] static SensorConfidenceEstimate evaluate_triple_redundancy(
        float s1, float s2, float s3, float noise_sigma, float max_spread) noexcept;

    /**
     * @brief Перевірка кінематичної узгодженості між акселерометром IMU та GNSS одометрією.
     */
    void check_kinematics(float imu_accel_x, float gnss_vel_x, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Перевірка енергетичного балансу електричної силової установки.
     */
    void check_battery_power(float voltage, float current, float expected_power_w, std::chrono::milliseconds now) noexcept;

    /**
     * @brief Передача діагностичних статусів достовірності до раціоналізатора тривог ISA-18.2.
     */
    void sync_to_rationalizer(AlarmRationalizer& ar, std::chrono::milliseconds now) const noexcept;

    [[nodiscard]] const SensorConfidenceEstimate& battery_confidence() const noexcept { return battery_confidence_; }
    [[nodiscard]] const SensorConfidenceEstimate& nav_velocity_confidence() const noexcept { return nav_velocity_confidence_; }

private:
    PlausibilityConfig config_;
    SensorConfidenceEstimate battery_confidence_{};
    SensorConfidenceEstimate nav_velocity_confidence_{};

    float last_imu_accel_x_{0.0f};
    float last_gnss_vel_x_{0.0f};
    std::chrono::milliseconds last_eval_time_{0ms};
};

} // namespace isa18_2
