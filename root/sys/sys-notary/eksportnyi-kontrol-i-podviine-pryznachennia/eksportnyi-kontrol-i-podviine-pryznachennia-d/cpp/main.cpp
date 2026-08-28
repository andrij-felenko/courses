#include <cstdint>
#include <string_view>
#include <optional>

namespace notary::compliance {

enum class EccnCategory : uint8_t {
    Ear99,
    MassMarket5A992,
    DualUseCrypto5A002,
    HighPerfAdc3A001,
    PrecisionImu7A002,
    MilSpecRestricted
};

struct HardwareExportSpecs {
    uint32_t adc_sample_rate_sps{0};   // Частота вибірки АЦП (семплів/с)
    uint8_t  adc_resolution_bits{0};   // Роздільність АЦП (біт)
    int16_t  temp_min_celsius{0};      // Мінімальна температура (°C)
    int16_t  temp_max_celsius{0};      // Максимальна температура (°C)
    uint32_t crypto_key_bits{0};       // Довжина ключа шифрування (біт)
    bool     has_custom_crypto{false}; // Нестандартний криптоалгоритм
    uint32_t imu_bias_drift_mdeg_h{0}; // Дрейф гіроскопа (міліградуси/год)
    uint32_t rad_hardness_krad{0};     // Радіаційна стійкість (крад Si)
};

struct ClassificationReport {
    EccnCategory     category{EccnCategory::Ear99};
    std::string_view eccn_code{"EAR99"};
    bool             requires_individual_license{false};
};

class ExportAuditEngine {
public:
    [[nodiscard]] static constexpr ClassificationReport evaluate(const HardwareExportSpecs& specs) noexcept {
        // 1. Радіаційна стійкість (TID >= 500 krad Si)
        if (specs.rad_hardness_krad >= 500) {
            return {EccnCategory::MilSpecRestricted, "3A001.a.1", true};
        }

        // 2. Точність гіроскопа (дрейф <= 0.5 °/год = 500 міліградусів/год)
        if (specs.imu_bias_drift_mdeg_h > 0 && specs.imu_bias_drift_mdeg_h <= 500) {
            return {EccnCategory::PrecisionImu7A002, "7A002", true};
        }

        // 3. Швидкодія АЦП (>= 1 GSPS при >= 10 біт)
        if (specs.adc_resolution_bits >= 10 && specs.adc_sample_rate_sps >= 1'000'000'000U) {
            return {EccnCategory::HighPerfAdc3A001, "3A001.a.5", true};
        }

        // 4. Військовий температурний діапазон (-55..+125 °C)
        if (specs.temp_min_celsius <= -55 && specs.temp_max_celsius >= 125) {
            return {EccnCategory::MilSpecRestricted, "3A001.a.2", true};
        }

        // 5. Криптографічні параметри
        if (specs.crypto_key_bits > 56) {
            if (specs.has_custom_crypto) {
                return {EccnCategory::DualUseCrypto5A002, "5A002.a.1", true};
            }
            return {EccnCategory::MassMarket5A992, "5A992.c", false};
        }

        return {EccnCategory::Ear99, "EAR99", false};
    }
};

} // namespace notary::compliance
