#include <iostream>
#include <string_view>
#include <format>
#include <expected>
#include <array>

namespace timing {

struct TransmitterSpec {
    double t_co_min_ns;  // Fast-corner output delay
    double t_co_max_ns;  // Slow-corner output delay
};

struct ReceiverSpec {
    double t_setup_ns;   // Required input setup time
    double t_hold_ns;    // Required input hold time
};

struct InterconnectSpec {
    double trace_length_mm{50.0};
    double ps_per_mm{6.5};       // FR-4 microstrip delay: ~6.5 ps/mm
    double clock_freq_mhz{50.0};
    double clock_skew_ns{0.3};
    double clock_jitter_ns{0.2};
};

struct ValidationReport {
    double flight_time_ns;
    double setup_slack_ns;
    double hold_slack_ns;
    double max_safe_freq_mhz;
    bool setup_ok;
    bool hold_ok;
};

enum class TimingError {
    InvalidFrequency,
    NegativeDelayParameter
};

class BusTimingValidator {
public:
    [[nodiscard]] static constexpr std::expected<ValidationReport, TimingError> validate(
        const TransmitterSpec& tx,
        const ReceiverSpec& rx,
        const InterconnectSpec& bus
    ) noexcept {
        if (bus.clock_freq_mhz <= 0.0) {
            return std::unexpected(TimingError::InvalidFrequency);
        }
        if (tx.t_co_min_ns < 0.0 || tx.t_co_max_ns < 0.0 || 
            rx.t_setup_ns < 0.0 || rx.t_hold_ns < 0.0) {
            return std::unexpected(TimingError::NegativeDelayParameter);
        }

        const double t_period_ns = 1000.0 / bus.clock_freq_mhz;
        const double t_flight_ns = (bus.trace_length_mm * bus.ps_per_mm) / 1000.0;

        // Бюджет встановлення (Setup Budget)
        const double total_setup_path = tx.t_co_max_ns + t_flight_ns + rx.t_setup_ns 
                                      + bus.clock_skew_ns + bus.clock_jitter_ns;
        const double setup_slack = t_period_ns - total_setup_path;

        // Бюджет утримання (Hold Budget)
        const double min_arrival = tx.t_co_min_ns + t_flight_ns;
        const double hold_required = rx.t_hold_ns + bus.clock_skew_ns;
        const double hold_slack = min_arrival - hold_required;

        const double max_freq = (total_setup_path > 0.0) ? (1000.0 / total_setup_path) : 0.0;

        return ValidationReport{
            .flight_time_ns = t_flight_ns,
            .setup_slack_ns = setup_slack,
            .hold_slack_ns = hold_slack,
            .max_safe_freq_mhz = max_freq,
            .setup_ok = (setup_slack >= 0.0),
            .hold_ok = (hold_slack >= 0.0)
        };
    }
};

} // namespace timing

int main() {
    using namespace timing;

    constexpr TransmitterSpec flash_tx{
        .t_co_min_ns = 1.5,
        .t_co_max_ns = 7.0
    };

    constexpr ReceiverSpec mcu_rx{
        .t_setup_ns = 3.5,
        .t_hold_ns = 1.0
    };

    constexpr InterconnectSpec pcb{
        .trace_length_mm = 80.0,
        .ps_per_mm = 6.5,
        .clock_freq_mhz = 60.0,
        .clock_skew_ns = 0.4,
        .clock_jitter_ns = 0.3
    };

    const auto result = BusTimingValidator::validate(flash_tx, mcu_rx, pcb);

    if (!result) {
        std::cerr << "Помилка валідації параметрів шини!\n";
        return 1;
    }

    const auto& report = *result;
    std::cout << "=== ВАЛІДАЦІЯ ЧАСОВОГО БЮДЖЕТУ ШИНИ (C++20) ===\n";
    std::cout << std::format("Затримка траси плати:       {:.3f} нс\n", report.flight_time_ns);
    std::cout << std::format("Запас Setup (встановлення): {:.3f} нс [{}]\n", 
                             report.setup_slack_ns, report.setup_ok ? "PASS" : "FAIL");
    std::cout << std::format("Запас Hold (утримання):     {:.3f} нс [{}]\n", 
                             report.hold_slack_ns, report.hold_ok ? "PASS" : "FAIL");
    std::cout << std::format("Максимальна частота шини:   {:.2f} МГц\n", report.max_safe_freq_mhz);

    return 0;
}
