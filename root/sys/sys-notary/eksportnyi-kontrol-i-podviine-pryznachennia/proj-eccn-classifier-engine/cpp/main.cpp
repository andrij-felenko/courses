#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>

namespace notary::compliance {

enum class ExportMode : uint8_t {
    NoLicenseRequired,
    LicenseExceptionEnc,
    LicenseRequired,
    ProhibitedEmbargo
};

struct ProductExportSpec {
    uint32_t         adc_sample_rate_sps{0};
    uint8_t          adc_resolution_bits{0};
    int16_t          temp_min_celsius{0};
    int16_t          temp_max_celsius{0};
    uint32_t         crypto_key_bits{0};
    bool             has_custom_crypto{false};
    uint32_t         imu_bias_drift_mdeg_h{0};
    uint32_t         rad_hardness_krad{0};
    uint32_t         us_origin_cost_cents{0};
    uint32_t         total_product_cost_cents{0};
    std::string_view dest_country_iso{"UA"};
    bool             is_military_end_user{false};
};

struct ExportComplianceReport {
    std::string_view eccn_code{"EAR99"};
    ExportMode       mode{ExportMode::NoLicenseRequired};
    uint8_t          de_minimis_percent{0};
    std::string_view primary_control_reason{"None (Commercial EAR99)"};
};

class EccnClassifierEngine {
private:
    static constexpr std::array<std::string_view, 6> EMBARGO_COUNTRIES = {
        "CU", "IR", "KP", "SY", "RU", "BY"
    };

    [[nodiscard]] static constexpr bool is_embargoed(std::string_view iso) noexcept {
        return std::ranges::any_of(EMBARGO_COUNTRIES, [iso](std::string_view entry) {
            return entry == iso;
        });
    }

    [[nodiscard]] static constexpr uint8_t calculate_de_minimis(uint32_t us_cost, uint32_t total_cost) noexcept {
        if (total_cost == 0) {
            return 0;
        }
        const uint64_t percent = (static_cast<uint64_t>(us_cost) * 100ULL) / total_cost;
        return static_cast<uint8_t>(std::min<uint64_t>(percent, 100ULL));
    }

public:
    [[nodiscard]] static constexpr ExportComplianceReport evaluate(const ProductExportSpec& spec) noexcept {
        ExportComplianceReport report{};
        report.de_minimis_percent = calculate_de_minimis(spec.us_origin_cost_cents, spec.total_product_cost_cents);

        // 1. Аналіз технічних характеристик
        if (spec.rad_hardness_krad >= 500) {
            report.eccn_code = "3A001.a.1";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Radiation Hardness >= 500 krad(Si)";
        } else if (spec.imu_bias_drift_mdeg_h > 0 && spec.imu_bias_drift_mdeg_h <= 500) {
            report.eccn_code = "7A002";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Navigation-Grade Gyro Drift <= 0.5 deg/hr";
        } else if (spec.adc_resolution_bits >= 10 && spec.adc_sample_rate_sps >= 1'000'000'000U) {
            report.eccn_code = "3A001.a.5";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "High-Speed ADC >= 1 GSPS at >= 10-bit";
        } else if (spec.temp_min_celsius <= -55 && spec.temp_max_celsius >= 125) {
            report.eccn_code = "3A001.a.2";
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Military Temp Range (-55C to +125C)";
        } else if (spec.crypto_key_bits > 56) {
            if (spec.has_custom_crypto) {
                report.eccn_code = "5A002.a.1";
                report.mode = ExportMode::LicenseRequired;
                report.primary_control_reason = "Dual-Use Proprietary Cryptography";
            } else {
                report.eccn_code = "5A992.c";
                report.mode = ExportMode::LicenseExceptionEnc;
                report.primary_control_reason = "Mass Market Cryptography (Note 4)";
            }
        }

        // 2. Аналіз географічних та кінцевих обмежень
        if (is_embargoed(spec.dest_country_iso)) {
            report.mode = ExportMode::ProhibitedEmbargo;
            report.primary_control_reason = "Sanctioned/Embargoed Destination";
        } else if (spec.is_military_end_user && report.mode != ExportMode::LicenseRequired) {
            report.mode = ExportMode::LicenseRequired;
            report.primary_control_reason = "Military End-User (MEU) Restriction";
        }

        return report;
    }
};

} // namespace notary::compliance
