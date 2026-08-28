#include <cstdint>
#include <cstddef>
#include <cmath>
#include <span>
#include <vector>
#include <optional>
#include <array>

namespace postmortem {

constexpr std::size_t MaxMotors = 4;

enum class Axis : std::size_t {
    Roll = 0,
    Pitch = 1,
    Yaw = 2
};

struct BlackboxFrame {
    std::uint64_t timestamp_us{0};
    std::array<float, 3> setpoint_rate{0.0f, 0.0f, 0.0f}; /* deg/s */
    std::array<float, 3> gyro_rate{0.0f, 0.0f, 0.0f};     /* deg/s */
    std::array<float, 3> pid_p_term{0.0f, 0.0f, 0.0f};
    std::array<float, 3> pid_i_term{0.0f, 0.0f, 0.0f};
    std::array<float, 3> pid_d_term{0.0f, 0.0f, 0.0f};
    std::array<float, MaxMotors> motor_output{0.0f, 0.0f, 0.0f, 0.0f};
    float vbat_v{0.0f};
    float ibat_a{0.0f};
};

enum class AnomalyType : std::uint32_t {
    None             = 0,
    TrackingLoss    = (1 << 0),
    MixerSaturation = (1 << 1),
    MotorDesync     = (1 << 2),
    Brownout         = (1 << 3)
};

constexpr AnomalyType operator|(AnomalyType a, AnomalyType b) noexcept {
    return static_cast<AnomalyType>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr bool has_flag(AnomalyType val, AnomalyType flag) noexcept {
    return (static_cast<std::uint32_t>(val) & static_cast<std::uint32_t>(flag)) != 0;
}

struct AnalyzerConfig {
    float tracking_error_threshold_deg{45.0f};
    float desync_motor_min_throttle{0.95f};
    std::uint32_t min_anomaly_duration_us{20000};
    float brownout_voltage_threshold_v{6.0f};
};

struct CrashIncidentReport {
    std::uint64_t start_time_us{0};
    std::uint64_t end_time_us{0};
    AnomalyType flags{AnomalyType::None};
    std::optional<std::size_t> failed_motor_index{std::nullopt};
    float max_error_deg{0.0f};
    float min_vbat_v{100.0f};
};

} // namespace postmortem
