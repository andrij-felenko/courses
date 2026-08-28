// battery_monitor.hpp — Ідіоматичний C++20 модуль діагностики живлення
#include <cstdint>
#include <concepts>
#include <chrono>
#include <expected>

enum class PowerDiagnosticError {
    DeviceDepleted,
    ExcessiveVoltageSag,
    HardwareInterfaceFault
};

struct PowerAssessment {
    std::uint32_t open_circuit_voltage_mv{0};
    std::uint32_t loaded_voltage_mv{0};
    float internal_impedance_ohm{0.0f};
    bool requires_depassivation{false};
};

template <typename HAL>
concept PlatformPowerHAL = requires(HAL hal, bool enable, std::chrono::microseconds us) {
    { hal.read_adc_millivolts() } -> std::same_as<std::uint32_t>;
    { hal.enable_test_load(enable) } -> std::same_as<void>;
    { hal.delay(us) } -> std::same_as<void>;
};

template <PlatformPowerHAL HAL>
class BatteryImpedanceAnalyzer {
public:
    static constexpr float TestLoadResistanceOhm = 68.0f;
    static constexpr std::uint32_t SafeVoltageThresholdMv = 2'800;
    static constexpr float MaxAllowedImpedanceOhm = 15.0f;

    explicit constexpr BatteryImpedanceAnalyzer(HAL& hal) noexcept : hal_(hal) {}

    [[nodiscard]] std::expected<PowerAssessment, PowerDiagnosticError> assess_pack_state() noexcept {
        PowerAssessment assessment{};

        // 1. Напруга холостого ходу
        hal_.enable_test_load(false);
        hal_.delay(std::chrono::microseconds(1000));
        assessment.open_circuit_voltage_mv = hal_.read_adc_millivolts();

        if (assessment.open_circuit_voltage_mv < SafeVoltageThresholdMv) {
            return std::unexpected(PowerDiagnosticError::DeviceDepleted);
        }

        // 2. Імпульсне навантаження (2 мс стабілізація + замір)
        hal_.enable_test_load(true);
        hal_.delay(std::chrono::microseconds(2000));
        assessment.loaded_voltage_mv = hal_.read_adc_millivolts();
        hal_.enable_test_load(false);

        if (assessment.loaded_voltage_mv < SafeVoltageThresholdMv) {
            return std::unexpected(PowerDiagnosticError::ExcessiveVoltageSag);
        }

        // 3. Розрахунок ESR
        const float delta_v = static_cast<float>(assessment.open_circuit_voltage_mv - assessment.loaded_voltage_mv);
        assessment.internal_impedance_ohm = (delta_v * TestLoadResistanceOhm) / static_cast<float>(assessment.loaded_voltage_mv);

        if (assessment.internal_impedance_ohm > MaxAllowedImpedanceOhm) {
            assessment.requires_depassivation = true;
        }

        return assessment;
    }

private:
    HAL& hal_;
};
