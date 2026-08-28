#include <cstdint>
#include <array>
#include <string_view>
#include <expected>

namespace field_guard {

enum class ResetCause : uint8_t {
    Unknown     = 0x00,
    PowerOn     = 0x01,
    Brownout    = 0x02,
    Watchdog    = 0x03,
    ThermalLock = 0x04
};

struct Telemetry {
    float temperature_c       { 25.0f };
    float supply_voltage_v    { 3.30f };
    uint32_t brownout_count   { 0 };
    bool throttling_active    { false };
    bool heater_active        { false };
};

class EnvironmentalSupervisor {
public:
    constexpr EnvironmentalSupervisor() noexcept = default;

    [[nodiscard]] ResetCause diagnose_boot_flags(uint32_t raw_flags) noexcept {
        ResetCause cause = ResetCause::Unknown;

        if (raw_flags & (1U << 3)) {
            cause = ResetCause::Brownout;
        } else if (raw_flags & (1U << 2)) {
            cause = ResetCause::Watchdog;
        } else if (raw_flags & (1U << 0)) {
            cause = ResetCause::PowerOn;
        }

        current_cause_ = cause;
        return cause;
    }

    void evaluate_state(Telemetry& telemetry) noexcept {
        // 1. Адаптивне керування теплом при переході межі +80 °C
        if (telemetry.temperature_c >= 80.0f) {
            if (!telemetry.throttling_active) {
                apply_thermal_throttling(true);
                telemetry.throttling_active = true;
            }
        } else if (telemetry.temperature_c <= 65.0f && telemetry.throttling_active) {
            apply_thermal_throttling(false);
            telemetry.throttling_active = false;
        }

        // 2. Захист від точки роси та замерзання нижче -10 °C
        telemetry.heater_active = (telemetry.temperature_c < -10.0f);

        // 3. Запобігання аварійному скиданню при просадці шини
        if (telemetry.supply_voltage_v < 3.10f) {
            emergency_shed_load();
        }
    }

    [[nodiscard]] constexpr ResetCause last_cause() const noexcept {
        return current_cause_;
    }

private:
    ResetCause current_cause_{ ResetCause::Unknown };

    static void apply_thermal_throttling(bool enable) noexcept {
        // Зниження частоти ядра та вимкнення радіомодуля
    }

    static void emergency_shed_load() noexcept {
        // Миттєве скидання енергоємного навантаження
    }
};

} // namespace field_guard
