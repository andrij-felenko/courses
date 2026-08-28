#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <string_view>

namespace warranty {

inline constexpr uint32_t kMagic = 0x52524157U; // "WARR"
inline constexpr uint16_t kSchemaVersion = 0x0002U;
inline constexpr size_t kMaxViolationRecords = 16;

enum class ViolationFlags : uint32_t {
    None             = 0,
    LiquidIngress    = 1U << 0,
    OvervoltageEos   = 1U << 1,
    Overheat         = 1U << 2,
    MechanicalShock  = 1U << 3,
    TamperOpen       = 1U << 4,
    FirmwareUnauth   = 1U << 5,
    ReversePolarity  = 1U << 6
};

[[nodiscard]] constexpr ViolationFlags operator|(ViolationFlags a, ViolationFlags b) noexcept {
    return static_cast<ViolationFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(ViolationFlags value, ViolationFlags flag) noexcept {
    return (static_cast<uint32_t>(value) & static_cast<uint32_t>(flag)) != 0;
}

enum class RmaVerdict : uint8_t {
    ApprovedWarranty,
    RejectedExpired,
    RejectedLiquid,
    RejectedElectricalAbuse,
    RejectedThermalAbuse,
    RejectedTamperModified,
    RejectedIntegrityCorrupt
};

#pragma pack(push, 1)

struct ViolationRecord {
    uint32_t timestamp_poh{0};
    uint16_t event_type{0};
    int16_t  peak_temperature{0};
    uint32_t peak_voltage_mv{0};
    uint16_t peak_shock_deci_g{0};
    uint8_t  sensor_flags{0};
    uint8_t  reserved{0};
    uint32_t record_crc32{0};
};

struct WarrantyLogHeader {
    uint32_t magic{kMagic};
    uint16_t schema_version{kSchemaVersion};
    uint16_t header_len{sizeof(WarrantyLogHeader)};
    std::array<uint8_t, 16> device_uuid{};
    uint32_t power_on_hours{0};
    uint32_t boot_count{0};
    uint32_t thermal_cycles{0};
    ViolationFlags violation_flags{ViolationFlags::None};
    int16_t  max_recorded_temp{0};
    uint32_t max_recorded_voltage{0};
    uint16_t max_recorded_shock{0};
    uint16_t record_count{0};
    uint32_t header_crc32{0};
};

struct WarrantyStorage {
    WarrantyLogHeader header;
    std::array<ViolationRecord, kMaxViolationRecords> records;
};

#pragma pack(pop)

struct PolicyLimits {
    uint32_t max_allowed_poh{17520};      // 2 роки безперервної роботи (годин)
    int16_t  limit_temp_deci_c{850};      // 85.0 °C
    uint32_t limit_voltage_mv{28000};     // 28.0 В (для 24 В шини)
    uint16_t limit_shock_deci_g{500};     // 50.0 g
};

// Обчислення CRC32 у constexpr стилі
[[nodiscard]] constexpr uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint32_t>(byte);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc = (crc >> 1);
            }
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

class WarrantyAuditor {
public:
    [[nodiscard]] static std::expected<RmaVerdict, RmaVerdict> evaluate(
        const WarrantyStorage& storage,
        const PolicyLimits& limits
    ) noexcept {
        const auto& hdr = storage.header;

        // 1. Перевірка магічного підпису та формату
        if (hdr.magic != kMagic || hdr.schema_version != kSchemaVersion) {
            return std::unexpected(RmaVerdict::RejectedIntegrityCorrupt);
        }

        // 2. Перевірка контрольної суми заголовка
        constexpr size_t kCrcSpanSize = sizeof(WarrantyLogHeader) - sizeof(uint32_t);
        const auto header_bytes = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&hdr), kCrcSpanSize
        );
        if (hdr.header_crc32 != compute_crc32(header_bytes)) {
            return std::unexpected(RmaVerdict::RejectedIntegrityCorrupt);
        }

        // 3. Перевірка строку служби
        if (hdr.power_on_hours > limits.max_allowed_poh) {
            return RmaVerdict::RejectedExpired;
        }

        // 4. Перевірка критичних порушень експлуатації
        if (has_flag(hdr.violation_flags, ViolationFlags::LiquidIngress)) {
            return RmaVerdict::RejectedLiquid;
        }

        if (has_flag(hdr.violation_flags, ViolationFlags::TamperOpen) ||
            has_flag(hdr.violation_flags, ViolationFlags::FirmwareUnauth)) {
            return RmaVerdict::RejectedTamperModified;
        }

        if (has_flag(hdr.violation_flags, ViolationFlags::OvervoltageEos) ||
            has_flag(hdr.violation_flags, ViolationFlags::ReversePolarity) ||
            hdr.max_recorded_voltage > limits.limit_voltage_mv) {
            return RmaVerdict::RejectedElectricalAbuse;
        }

        if (has_flag(hdr.violation_flags, ViolationFlags::Overheat) ||
            hdr.max_recorded_temp > limits.limit_temp_deci_c) {
            return RmaVerdict::RejectedThermalAbuse;
        }

        return RmaVerdict::ApprovedWarranty;
    }
};

} // namespace warranty
