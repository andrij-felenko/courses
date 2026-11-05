#pragma once

#include "VibrationTelemetry.hpp"
#include <string_view>

/**
 * @brief Діагностичний знімок стану віброізоляції.
 */
struct HealthStatus {
    double transmissibility;
    double frame_rms_g;
    double payload_rms_g;
    double peak_shock_g;
    bool resonance_detected;
    bool shock_exceeded;
};

/**
 * @brief Монітор ефективності віброізоляції та діагностики стану підвісу.
 */
class VibrationMonitor {
public:
    explicit VibrationMonitor(double max_allowable_g = 12.0, double resonance_threshold = 2.5);

    void recordFrameSample(double t_s, double ax, double ay, double az);
    void recordPayloadSample(double t_s, double ax, double ay, double az);

    [[nodiscard]] HealthStatus evaluateHealth() const noexcept;
    [[nodiscard]] double calculateLogarithmicDecrement() const noexcept;
    [[nodiscard]] std::string_view getDiagnosticSummary() const noexcept;

    void printTelemetryReport() const;

private:
    double max_allowable_g_;
    double resonance_threshold_;
    TelemetryBuffer frame_buffer_;
    TelemetryBuffer payload_buffer_;
};
