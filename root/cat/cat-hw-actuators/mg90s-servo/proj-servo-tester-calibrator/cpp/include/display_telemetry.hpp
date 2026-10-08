#ifndef DISPLAY_TELEMETRY_HPP
#define DISPLAY_TELEMETRY_HPP

#include "servo_calibrator.hpp"
#include "servo_pwm.hpp"
#include "current_monitor.hpp"
#include <array>
#include <cstddef>
#include <string_view>

namespace actuators {

/// @brief Кадр даних телеметрії для відмальовування на дисплеї.
struct TelemetryFrame {
    CalibratorMode mode{CalibratorMode::Disabled};
    float current_angle_deg{0.0f};
    uint16_t pulse_width_us{0};
    float current_ma{0.0f};
    float peak_current_ma{0.0f};
    bool is_stall_alert{false};
    float min_limit_deg{0.0f};
    float max_limit_deg{0.0f};
};

/// @brief Клас для форматування та відображення телеметричних даних сервосистем.
class DisplayTelemetry {
public:
    static constexpr size_t BUFFER_SIZE = 512;
    static constexpr size_t LINE_SIZE = 128;

    DisplayTelemetry() = default;

    /// @brief Збір кадру телеметрії з усіх модулів системи.
    TelemetryFrame capture_frame(const ServoCalibrator& calibrator,
                                const ServoPwmGenerator& pwm,
                                const CurrentMonitor& monitor) const;

    /// @brief Форматування повного графічного/текстового екрану статусу.
    std::string_view format_status_screen(const TelemetryFrame& frame);

    /// @brief Форматування компактного рядка логу для послідовного порту.
    std::string_view format_compact_log(const TelemetryFrame& frame);

    /// @brief Вивід екрану статусу у консоль або графічний дисплей.
    void render_screen(const TelemetryFrame& frame);

    /// @brief Вивід рядка логу.
    void render_log_line(const TelemetryFrame& frame);

private:
    std::array<char, BUFFER_SIZE> screen_buffer_{};
    std::array<char, LINE_SIZE> line_buffer_{};
};

} // namespace actuators

#endif // DISPLAY_TELEMETRY_HPP
