#include <span>
#include <algorithm>
#include <cmath>

namespace postmortem {

class BlackboxAnalyzer {
public:
    explicit BlackboxAnalyzer(AnalyzerConfig config) noexcept
        : config_{config} {}

    [[nodiscard]] std::optional<CrashIncidentReport> process(
        std::span<const BlackboxFrame> frames) const noexcept {
        if (frames.size() < 2) {
            return std::nullopt;
        }

        CrashIncidentReport report{};
        std::array<std::uint64_t, MaxMotors> desync_start_time{};
        std::uint64_t tracking_loss_start_time{0};
        bool in_incident{false};

        for (std::size_t i = 1; i < frames.size(); ++i) {
            const auto& prev = frames[i - 1];
            const auto& curr = frames[i];

            const float dt = static_cast<float>(curr.timestamp_us - prev.timestamp_us) * 1e-6f;
            if (dt <= 0.0f || dt > 0.05f) {
                continue;
            }

            report.min_vbat_v = std::min(report.min_vbat_v, curr.vbat_v);

            /* 1. Аналіз аварійного просідання напруги */
            if (curr.vbat_v < config_.brownout_voltage_threshold_v) {
                report.flags = report.flags | AnomalyType::Brownout;
                if (!in_incident) {
                    report.start_time_us = curr.timestamp_us;
                    in_incident = true;
                }
                report.end_time_us = curr.timestamp_us;
            }

            /* 2. Оцінка похибки регулювання */
            const float err_roll = std::abs(curr.setpoint_rate[0] - curr.gyro_rate[0]);
            const float err_pitch = std::abs(curr.setpoint_rate[1] - curr.gyro_rate[1]);
            const float total_err = std::hypot(err_roll, err_pitch);

            report.max_error_deg = std::max(report.max_error_deg, total_err);

            if (total_err > config_.tracking_error_threshold_deg) {
                if (tracking_loss_start_time == 0) {
                    tracking_loss_start_time = curr.timestamp_us;
                } else if (curr.timestamp_us - tracking_loss_start_time >= config_.min_anomaly_duration_us) {
                    report.flags = report.flags | AnomalyType::TrackingLoss;
                    if (!in_incident) {
                        report.start_time_us = tracking_loss_start_time;
                        in_incident = true;
                    }
                    report.end_time_us = curr.timestamp_us;
                }
            } else {
                tracking_loss_start_time = 0;
            }

            /* 3. Детектування моторного десинхрону */
            const float alpha_roll = (curr.gyro_rate[0] - prev.gyro_rate[0]) / dt;

            for (std::size_t m = 0; m < MaxMotors; ++m) {
                if (curr.motor_output[m] >= config_.desync_motor_min_throttle) {
                    bool opposing_accel = false;
                    if (m == 3 && alpha_roll < -50.0f) opposing_accel = true;
                    if (m == 1 && alpha_roll > 50.0f)  opposing_accel = true;

                    if (opposing_accel) {
                        if (desync_start_time[m] == 0) {
                            desync_start_time[m] = curr.timestamp_us;
                        } else if (curr.timestamp_us - desync_start_time[m] >= config_.min_anomaly_duration_us) {
                            report.flags = report.flags | AnomalyType::MotorDesync;
                            report.failed_motor_index = m;
                            if (!in_incident) {
                                report.start_time_us = desync_start_time[m];
                                in_incident = true;
                            }
                            report.end_time_us = curr.timestamp_us;
                        }
                    }
                } else {
                    desync_start_time[m] = 0;
                }
            }
        }

        return in_incident ? std::make_optional(report) : std::nullopt;
    }

private:
    AnalyzerConfig config_;
};

} // namespace postmortem
