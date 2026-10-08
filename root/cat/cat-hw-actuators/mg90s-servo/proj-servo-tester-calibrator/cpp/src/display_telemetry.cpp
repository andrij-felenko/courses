#include "display_telemetry.hpp"
#include <cstdio>
#include <iostream>

namespace actuators {

TelemetryFrame DisplayTelemetry::capture_frame(const ServoCalibrator& calibrator,
                                              const ServoPwmGenerator& pwm,
                                              const CurrentMonitor& monitor) const {
    TelemetryFrame frame;
    frame.mode = calibrator.get_mode();
    frame.current_angle_deg = pwm.get_current_angle();
    frame.pulse_width_us = pwm.get_current_pulse_us();
    frame.current_ma = monitor.get_filtered_current_ma();
    frame.peak_current_ma = monitor.get_peak_current_ma();
    frame.is_stall_alert = monitor.is_stall_detected() || calibrator.is_emergency_stop();
    frame.min_limit_deg = calibrator.get_limits().min_angle_deg;
    frame.max_limit_deg = calibrator.get_limits().max_angle_deg;
    return frame;
}

std::string_view DisplayTelemetry::format_status_screen(const TelemetryFrame& frame) {
    const char* mode_str = "Unknown";
    switch (frame.mode) {
        case CalibratorMode::Disabled:      mode_str = "Disabled"; break;
        case CalibratorMode::Manual:        mode_str = "Manual"; break;
        case CalibratorMode::AutoScan:      mode_str = "AutoScan"; break;
        case CalibratorMode::EmergencyStop: mode_str = "EMERGENCY_STOP"; break;
    }

    const char* status_str = frame.is_stall_alert ? "FAULT: STALL DETECTED!" : "OK (Normal)";

    int written = std::snprintf(screen_buffer_.data(), screen_buffer_.size(),
        "========================================\n"
        "       MG90S V2 SERVO CALIBRATOR        \n"
        "========================================\n"
        " Mode          : %s\n"
        " Position      : %.1f deg (Limits: %.1f - %.1f)\n"
        " PWM Pulse     : %u us (50 Hz)\n"
        " Consumption   : %.1f mA (Peak: %.1f mA)\n"
        " Protection    : %s\n"
        "========================================\n",
        mode_str,
        frame.current_angle_deg,
        frame.min_limit_deg,
        frame.max_limit_deg,
        frame.pulse_width_us,
        frame.current_ma,
        frame.peak_current_ma,
        status_str
    );

    if (written < 0) {
        return std::string_view("");
    }

    size_t len = static_cast<size_t>(written);
    if (len >= screen_buffer_.size()) {
        len = screen_buffer_.size() - 1;
    }

    return std::string_view(screen_buffer_.data(), len);
}

std::string_view DisplayTelemetry::format_compact_log(const TelemetryFrame& frame) {
    const char* mode_str = "UNK";
    switch (frame.mode) {
        case CalibratorMode::Disabled:      mode_str = "OFF"; break;
        case CalibratorMode::Manual:        mode_str = "MAN"; break;
        case CalibratorMode::AutoScan:      mode_str = "SCN"; break;
        case CalibratorMode::EmergencyStop: mode_str = "STP"; break;
    }

    int written = std::snprintf(line_buffer_.data(), line_buffer_.size(),
        "[%s] Angle: %5.1f deg | Pulse: %4u us | I: %5.1f mA | Status: %s\n",
        mode_str,
        frame.current_angle_deg,
        frame.pulse_width_us,
        frame.current_ma,
        frame.is_stall_alert ? "STALL!" : "OK"
    );

    if (written < 0) {
        return std::string_view("");
    }

    size_t len = static_cast<size_t>(written);
    if (len >= line_buffer_.size()) {
        len = line_buffer_.size() - 1;
    }

    return std::string_view(line_buffer_.data(), len);
}

void DisplayTelemetry::render_screen(const TelemetryFrame& frame) {
    std::string_view view = format_status_screen(frame);
    std::cout << view;
}

void DisplayTelemetry::render_log_line(const TelemetryFrame& frame) {
    std::string_view view = format_compact_log(frame);
    std::cout << view;
}

} // namespace actuators
