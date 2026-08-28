#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <optional>
#include <cmath>
#include <cstdint>

namespace postmortem {

struct LogEntry {
    std::uint32_t time_ms{0};
    float setpoint_roll{0.0f};
    float gyro_roll{0.0f};
    std::array<float, 4> motor_pwm{0.0f, 0.0f, 0.0f, 0.0f};
    float vbat{0.0f};
};

struct DiagnosticReport {
    std::uint32_t trigger_time_ms{0};
    int failed_motor_index{-1};
    std::string_view root_cause;
};

class CrashAnalyzer {
public:
    [[nodiscard]] static std::optional<DiagnosticReport> analyze(std::span<const LogEntry> log) noexcept {
        if (log.size() < 5) {
            return std::nullopt;
        }

        std::array<std::uint32_t, 4> desync_duration_ms{0, 0, 0, 0};

        for (std::size_t i = 1; i < log.size(); ++i) {
            const auto& prev = log[i - 1];
            const auto& curr = log[i];

            const float dt = static_cast<float>(curr.time_ms - prev.time_ms) * 0.001f;
            if (dt <= 0.0f) {
                continue;
            }

            /* 1. Детектування аварійного просідання батареї */
            if (curr.vbat < 6.0f) {
                return DiagnosticReport{
                    .trigger_time_ms = curr.time_ms,
                    .failed_motor_index = -1,
                    .root_cause = "CRITICAL_BROWNOUT_VOLTAGE_COLLAPSE"
                };
            }

            /* 2. Обчислення розбіжності та кутового прискорення */
            const float err_roll = std::abs(curr.setpoint_roll - curr.gyro_roll);
            const float alpha_roll = (curr.gyro_roll - prev.gyro_roll) / dt;

            /* 3. Перевірка насичення та відсутності тяги */
            for (std::size_t m = 0; m < curr.motor_pwm.size(); ++m) {
                if (curr.motor_pwm[m] >= 0.98f) {
                    const bool is_opposing = (m == 3 && alpha_roll < -30.0f) ||
                                             (m == 1 && alpha_roll > 30.0f);

                    if (is_opposing && err_roll > 40.0f) {
                        desync_duration_ms[m] += (curr.time_ms - prev.time_ms);
                        if (desync_duration_ms[m] >= 25) {
                            return DiagnosticReport{
                                .trigger_time_ms = curr.time_ms - desync_duration_ms[m],
                                .failed_motor_index = static_cast<int>(m),
                                .root_cause = "ESC_MOTOR_DESYNCHRONIZATION"
                            };
                        }
                    }
                } else {
                    desync_duration_ms[m] = 0;
                }
            }
        }

        return std::nullopt;
    }
};

} // namespace postmortem
