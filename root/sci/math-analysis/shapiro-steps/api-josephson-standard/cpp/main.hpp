#ifndef JVS_STANDARD_HPP
#ifndef JVS_STANDARD_H // Захист від подвійного включення C/C++ заголовочних файлів
#define JVS_STANDARD_HPP

#include <string>
#include <vector>
#include <expected>
#include <cstdint>

namespace metrology::jvs {

constexpr double JOSEPHSON_CONSTANT_KJ = 483597.8484e9; // Гц / В
constexpr double PLANCK_CONSTANT_H = 6.62607015e-34;    // Дж·с
constexpr double ELEMENTARY_CHARGE_E = 1.602176634e-19; // Кл

enum class ErrorCode {
    RfUnlocked,
    StepTripped,
    TemperatureExceeded,
    InvalidVoltage,
    CommunicationTimeout
};

struct SystemStatus {
    double target_voltage_v{0.0};
    double actual_rf_frequency_hz{0.0};
    double cryo_temperature_k{4.2};
    std::size_t active_junctions{0};
    bool is_step_locked{false};
};

class JosephsonVoltageStandard {
public:
    explicit JosephsonVoltageStandard(std::string resource_name);
    ~JosephsonVoltageStandard();

    [[nodiscard]] std::expected<void, ErrorCode> initialize();
    [[nodiscard]] std::expected<void, ErrorCode> set_frequency(double frequency_hz);
    [[nodiscard]] std::expected<SystemStatus, ErrorCode> set_voltage(double target_volts);
    [[nodiscard]] std::expected<std::pair<double, double>, ErrorCode> measure_voltage() const;

private:
    std::string resource_name_;
    double current_frequency_hz_{70.0e9};
    bool is_initialized_{false};
};

} // namespace metrology::jvs

#endif
#endif
