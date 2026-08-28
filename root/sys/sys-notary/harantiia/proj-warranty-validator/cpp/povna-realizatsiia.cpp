#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <string>
#include <string_view>
#include <expected>
#include <algorithm>

namespace warranty_validator {

inline constexpr uint32_t kMagic = 0x52524157U; // "WARR"
inline constexpr uint16_t kSchemaV2 = 0x0002U;
inline constexpr size_t kMaxRecords = 32;

enum class ViolationFlag : uint32_t {
    None             = 0,
    LiquidIngress    = 1U << 0,
    OvervoltageEos   = 1U << 1,
    Overheat         = 1U << 2,
    MechanicalShock  = 1U << 3,
    TamperOpen       = 1U << 4,
    FirmwareUnauth   = 1U << 5,
    ReversePolarity  = 1U << 6
};

[[nodiscard]] constexpr ViolationFlag operator|(ViolationFlag a, ViolationFlag b) noexcept {
    return static_cast<ViolationFlag>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(ViolationFlag value, ViolationFlag flag) noexcept {
    return (static_cast<uint32_t>(value) & static_cast<uint32_t>(flag)) != 0;
}

enum class RmaVerdict : uint8_t {
    ApprovedWarranty,
    RejectedExpired,
    RejectedLiquid,
    RejectedElectrical,
    RejectedThermal,
    RejectedMechanical,
    RejectedTamper,
    RejectedCorrupted
};

#pragma pack(push, 1)

struct SensorViolationEntry {
    uint32_t timestamp_poh{0};
    uint16_t event_type{0};
    int16_t  peak_temperature_deci_c{0};
    uint32_t peak_voltage_mv{0};
    uint16_t peak_shock_deci_g{0};
    uint8_t  sensor_flags{0};
    uint8_t  reserved{0};
    uint32_t record_crc32{0};
};

struct WarrantyImageHeader {
    uint32_t magic{kMagic};
    uint16_t schema_version{kSchemaV2};
    uint16_t header_len{sizeof(WarrantyImageHeader)};
    std::array<uint8_t, 16> device_uuid{};
    uint32_t power_on_hours{0};
    uint32_t boot_count{0};
    uint32_t thermal_cycles{0};
    ViolationFlag violation_flags{ViolationFlag::None};
    int16_t  max_recorded_temp_deci_c{0};
    uint32_t max_recorded_voltage_mv{0};
    uint16_t max_recorded_shock_deci_g{0};
    uint16_t record_count{0};
    uint32_t header_crc32{0};
};

struct WarrantyEepromImage {
    WarrantyImageHeader header;
    std::array<SensorViolationEntry, kMaxRecords> records{};
};

#pragma pack(pop)

struct PolicyConfig {
    uint32_t max_allowed_poh{17520};          // 2 роки
    int16_t  max_allowed_temp_deci_c{850};     // 85.0 °C
    uint32_t max_allowed_voltage_mv{28000};    // 28.0 В
    uint16_t max_allowed_shock_deci_g{500};    // 50.0 g
    uint32_t max_thermal_dose_allowed{2000};   // Градусо-годин перегріву
};

struct AuditReport {
    RmaVerdict verdict{RmaVerdict::RejectedCorrupted};
    ViolationFlag active_violations{ViolationFlag::None};
    uint32_t valid_records_parsed{0};
    uint32_t calculated_thermal_dose{0};
    std::string details{};
};

[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (const uint8_t byte : data) {
        crc ^= static_cast<uint32_t>(byte);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 1U) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
        }
    }
    return crc ^ 0xFFFFFFFFU;
}

class WarrantyValidatorEngine {
public:
    [[nodiscard]] static AuditReport evaluate(
        const WarrantyEepromImage& image,
        const PolicyConfig& policy
    ) noexcept {
        AuditReport report{};
        const auto& hdr = image.header;

        // 1. Перевірка магічного підпису та схеми
        if (hdr.magic != kMagic || hdr.schema_version != kSchemaV2) {
            report.verdict = RmaVerdict::RejectedCorrupted;
            report.details = "Invalid EEPROM image signature or unsupported schema version";
            return report;
        }

        // 2. Перевірка CRC32 заголовка
        constexpr size_t kHeaderCrcSize = sizeof(WarrantyImageHeader) - sizeof(uint32_t);
        const auto header_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&hdr), kHeaderCrcSize
        );
        if (hdr.header_crc32 != calculate_crc32(header_span)) {
            report.verdict = RmaVerdict::RejectedCorrupted;
            report.details = "Header CRC32 integrity checksum mismatch";
            return report;
        }

        report.active_violations = hdr.violation_flags;

        // 3. Аналіз записів подій
        const uint16_t records_to_parse = std::min<uint16_t>(hdr.record_count, kMaxRecords);
        uint32_t total_thermal_dose = 0;

        for (size_t i = 0; i < records_to_parse; ++i) {
            const auto& rec = image.records[i];
            constexpr size_t kRecCrcSize = sizeof(SensorViolationEntry) - sizeof(uint32_t);
            const auto rec_span = std::span<const uint8_t>(
                reinterpret_cast<const uint8_t*>(&rec), kRecCrcSize
            );

            if (rec.record_crc32 == calculate_crc32(rec_span)) {
                report.valid_records_parsed++;
                if (rec.peak_temperature_deci_c > policy.max_allowed_temp_deci_c) {
                    total_thermal_dose += static_cast<uint32_t>(rec.peak_temperature_deci_c - policy.max_allowed_temp_deci_c);
                }
            }
        }
        report.calculated_thermal_dose = total_thermal_dose;

        // 4. Оцінка політик відповідності
        if (has_flag(hdr.violation_flags, ViolationFlag::LiquidIngress)) {
            report.verdict = RmaVerdict::RejectedLiquid;
            report.details = "Liquid Contact Indicator (LCI) or moisture sensor triggered";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::TamperOpen) ||
            has_flag(hdr.violation_flags, ViolationFlag::FirmwareUnauth)) {
            report.verdict = RmaVerdict::RejectedTamper;
            report.details = "Tamper switch open event or unauthorized firmware signature";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::OvervoltageEos) ||
            has_flag(hdr.violation_flags, ViolationFlag::ReversePolarity) ||
            hdr.max_recorded_voltage_mv > policy.max_allowed_voltage_mv) {
            report.verdict = RmaVerdict::RejectedElectrical;
            report.details = "Electrical overstress: voltage exceeded maximum ratings";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::Overheat) ||
            hdr.max_recorded_temp_deci_c > policy.max_allowed_temp_deci_c ||
            total_thermal_dose > policy.max_thermal_dose_allowed) {
            report.verdict = RmaVerdict::RejectedThermal;
            report.details = "Thermal abuse: temperature limit or cumulative thermal dose exceeded";
            return report;
        }

        if (has_flag(hdr.violation_flags, ViolationFlag::MechanicalShock) ||
            hdr.max_recorded_shock_deci_g > policy.max_allowed_shock_deci_g) {
            report.verdict = RmaVerdict::RejectedMechanical;
            report.details = "Mechanical shock peak exceeded drop-impact threshold";
            return report;
        }

        if (hdr.power_on_hours > policy.max_allowed_poh) {
            report.verdict = RmaVerdict::RejectedExpired;
            report.details = "Total operating hours exceeded contractual warranty limit";
            return report;
        }

        report.verdict = RmaVerdict::ApprovedWarranty;
        report.details = "Device operated strictly within specified limits. Warranty approved.";
        return report;
    }
};

void display_report(const AuditReport& report, const WarrantyImageHeader& hdr) {
    std::cout << "================ RMA DIAGNOSTIC REPORT ================\n";
    std::cout << "Device UUID: ";
    for (const uint8_t byte : hdr.device_uuid) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    std::cout << std::dec << "\n";
    std::cout << "POH: " << hdr.power_on_hours << " h | Boot Count: " << hdr.boot_count << "\n";
    std::cout << "Max Temp: " << (hdr.max_recorded_temp_deci_c / 10.0) << " C | "
              << "Max Voltage: " << hdr.max_recorded_voltage_mv << " mV | "
              << "Max Shock: " << (hdr.max_recorded_shock_deci_g / 10.0) << " g\n";
    std::cout << "Valid Records: " << report.valid_records_parsed
              << " | Thermal Dose: " << report.calculated_thermal_dose << "\n";
    std::cout << "-------------------------------------------------------\n";

    switch (report.verdict) {
        case RmaVerdict::ApprovedWarranty:
            std::cout << "VERDICT: [APPROVED] Free Warranty Repair\n";
            break;
        case RmaVerdict::RejectedLiquid:
            std::cout << "VERDICT: [REJECTED] Liquid Damage\n";
            break;
        case RmaVerdict::RejectedElectrical:
            std::cout << "VERDICT: [REJECTED] Electrical Overstress (EOS)\n";
            break;
        case RmaVerdict::RejectedThermal:
            std::cout << "VERDICT: [REJECTED] Thermal Excursion\n";
            break;
        case RmaVerdict::RejectedMechanical:
            std::cout << "VERDICT: [REJECTED] Mechanical Impact Damage\n";
            break;
        case RmaVerdict::RejectedTamper:
            std::cout << "VERDICT: [REJECTED] Tamper / Unauthorized Modification\n";
            break;
        case RmaVerdict::RejectedExpired:
            std::cout << "VERDICT: [REJECTED] Warranty Term Expired\n";
            break;
        case RmaVerdict::RejectedCorrupted:
            std::cout << "VERDICT: [REJECTED] Corrupted Log Image\n";
            break;
    }
    std::cout << "Details: " << report.details << "\n";
    std::cout << "=======================================================\n";
}

} // namespace warranty_validator
