#pragma once

// Типи даних аналізатора: кадр телеметрії та звіт про інцидент.

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <string_view>

namespace postmortem {

inline constexpr std::size_t kMotorCount = 4;
inline constexpr std::uint32_t kImuHealthyBit = 0x01u;

enum class Fault {
    None,
    MotorEscLoss,
    MagneticInterference,
    BrownoutVoltageSag,
    SensorBusLockup
};

[[nodiscard]] constexpr std::string_view to_string(Fault fault) noexcept
{
    switch (fault) {
    case Fault::None:                 return "FAULT_NONE";
    case Fault::MotorEscLoss:         return "FAULT_MOTOR_ESC_LOSS";
    case Fault::MagneticInterference: return "FAULT_MAGNETIC_INTERFERENCE";
    case Fault::BrownoutVoltageSag:   return "FAULT_BROWNOUT_VOLTAGE_SAG";
    case Fault::SensorBusLockup:      return "FAULT_SENSOR_BUS_LOCKUP";
    }
    return "FAULT_UNKNOWN";
}

// Один синхронізований кадр: зведені на спільну часову сітку потоки
// IMU, EKF, BAT і RCOU з ULog або DataFlash.
struct Frame {
    std::uint64_t timestamp_us{0};
    float roll_des_deg{0.0f};
    float roll_deg{0.0f};
    float yaw_des_deg{0.0f};
    float yaw_deg{0.0f};
    std::array<float, kMotorCount> motor{};
    float bat_voltage_v{0.0f};
    float bat_current_a{0.0f};
    float mag_innov{0.0f};
    float gyro_x_rads{0.0f};
    std::uint32_t sensor_status{kImuHealthyBit};

    // У сирому записі трапляється NaN: журнал почався до ініціалізації EKF,
    // або в кадрі не було потрібного повідомлення. Такий кадр не судимо.
    [[nodiscard]] bool finite() const noexcept
    {
        const bool motors_ok = std::ranges::all_of(
            motor, [](float v) { return std::isfinite(v); });
        return motors_ok && std::isfinite(roll_des_deg) && std::isfinite(roll_deg) &&
               std::isfinite(yaw_des_deg) && std::isfinite(yaw_deg) &&
               std::isfinite(bat_voltage_v) && std::isfinite(bat_current_a) &&
               std::isfinite(mag_innov) && std::isfinite(gyro_x_rads);
    }
};

// Звіт. Крім сигнатури тут лежать «контекстні мітки» — події, які детектори
// свідомо відкинули як не-першопричину, але про які інженерові треба знати.
struct Report {
    Fault fault{Fault::None};
    std::uint64_t timestamp_us{0};
    float confidence{0.0f};
    std::string_view description{"Інцидентів не виявлено: параметри в межах норми"};

    std::optional<std::uint64_t> impact_us;      // зіткнення з перешкодою
    std::optional<std::uint64_t> environment_us; // магнітна аномалія середовища
    std::optional<std::uint64_t> depletion_us;   // плавне вичерпання заряду

    std::size_t frames_used{0};
    std::size_t frames_skipped{0};
};

} // namespace postmortem
