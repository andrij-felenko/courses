#include <cstdint>
#include <string_view>
#include <expected>
#include <array>
#include <algorithm>

enum class UpdateSeverity : uint8_t {
    Feature = 1,
    Maintenance = 2,
    SecurityStandard = 3,
    CriticalSecurity = 4
};

enum class DeviceOperatingState : uint8_t {
    Shutdown = 0,
    Idle = 1,
    Standby = 2,
    ActiveMission = 3,
    Emergency = 4
};

enum class NetworkBearer : uint32_t {
    Ethernet = (1 << 0),
    Wifi = (1 << 1),
    CellularUnmetered = (1 << 2),
    CellularMetered = (1 << 3)
};

constexpr NetworkBearer operator|(NetworkBearer a, NetworkBearer b) noexcept {
    return static_cast<NetworkBearer>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_flag(NetworkBearer mask, NetworkBearer flag) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(flag)) != 0;
}

enum class PolicyRejection : uint8_t {
    HwFamilyMismatch = 10,
    HwRevUnsupported = 11,
    AntiRollback = 12,
    BatteryLow = 13,
    TemperatureLimit = 14,
    BearerDisallowed = 15
};

enum class PostponeReason : uint8_t {
    BusyState = 1,
    OutsideWindow = 2
};

struct PolicyManifest {
    std::string_view hardware_family;
    uint32_t hardware_revision_mask{};
    uint32_t security_version{};
    UpdateSeverity severity{UpdateSeverity::Maintenance};
    uint8_t min_battery_soc_pct{50};
    uint16_t min_battery_voltage_mv{3600};
    int8_t temp_min_c{-10};
    int8_t temp_max_c{55};
    NetworkBearer allowed_bearers{NetworkBearer::Ethernet | NetworkBearer::Wifi};
    uint8_t max_postpones{3};
};

struct DeviceTelemetry {
    std::string_view hardware_family;
    uint32_t hardware_revision_bit{1};
    uint32_t current_security_version{1};
    DeviceOperatingState operating_state{DeviceOperatingState::Idle};
    uint8_t battery_soc_pct{100};
    uint16_t battery_voltage_mv{4100};
    int8_t board_temperature_c{25};
    NetworkBearer current_bearer{NetworkBearer::Wifi};
    bool is_in_maintenance_window{true};
    uint8_t current_postpone_count{0};
};

class UpdatePolicyEngine {
public:
    [[nodiscard]] static std::expected<void, std::expected<PostponeReason, PolicyRejection>>
    evaluate(const PolicyManifest& manifest, const DeviceTelemetry& telemetry) noexcept {
        
        // 1. Апаратна ідентифікація
        if (manifest.hardware_family != telemetry.hardware_family) {
            return std::unexpected(std::unexpected(PolicyRejection::HwFamilyMismatch));
        }

        if ((manifest.hardware_revision_mask & telemetry.hardware_revision_bit) == 0) {
            return std::unexpected(std::unexpected(PolicyRejection::HwRevUnsupported));
        }

        // 2. Захист від відкату (Anti-Rollback)
        if (manifest.security_version < telemetry.current_security_version) {
            return std::unexpected(std::unexpected(PolicyRejection::AntiRollback));
        }

        // 3. Мережевий канал
        if (!has_flag(manifest.allowed_bearers, telemetry.current_bearer)) {
            return std::unexpected(std::unexpected(PolicyRejection::BearerDisallowed));
        }

        // 4. Енергетичні та температурні обмеження
        uint8_t effective_soc = manifest.min_battery_soc_pct;
        uint16_t effective_volt = manifest.min_battery_voltage_mv;

        if (manifest.severity == UpdateSeverity::CriticalSecurity) {
            effective_soc = std::min<uint8_t>(effective_soc, 30);
            effective_volt = std::min<uint16_t>(effective_volt, 3500);
        }

        if (telemetry.battery_soc_pct < effective_soc ||
            telemetry.battery_voltage_mv < effective_volt) {
            return std::unexpected(std::unexpected(PolicyRejection::BatteryLow));
        }

        if (telemetry.board_temperature_c < manifest.temp_min_c ||
            telemetry.board_temperature_c > manifest.temp_max_c) {
            return std::unexpected(std::unexpected(PolicyRejection::TemperatureLimit));
        }

        // 5. Операційний стан і регламентне вікно
        const bool is_emergency = (manifest.severity == UpdateSeverity::CriticalSecurity);

        if (telemetry.operating_state == DeviceOperatingState::ActiveMission ||
            telemetry.operating_state == DeviceOperatingState::Emergency) {
            return std::unexpected(std::expected<PostponeReason, PolicyRejection>(PostponeReason::BusyState));
        }

        if (!is_emergency) {
            const bool postpone_exhausted = (telemetry.current_postpone_count >= manifest.max_postpones);
            if (!telemetry.is_in_maintenance_window && !postpone_exhausted) {
                return std::unexpected(std::expected<PostponeReason, PolicyRejection>(PostponeReason::OutsideWindow));
            }
        }

        return {}; // Успішно схвалено до встановлення
    }
};
