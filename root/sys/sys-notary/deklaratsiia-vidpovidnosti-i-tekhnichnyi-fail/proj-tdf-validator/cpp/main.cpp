#include <cstdint>
#include <string_view>
#include <array>
#include <optional>

namespace compliance {

enum class Domain : uint8_t {
    EU_ETSI = 0x01,
    US_FCC  = 0x02
};

struct RegulatoryLimits {
    Domain   domain;
    int8_t   max_tx_power_dbm;
    uint16_t min_freq_mhz;
    uint16_t max_freq_mhz;
    uint8_t  max_duty_cycle_pct;
    uint16_t allowed_channel_mask;
};

// Нормативи ETSI EN 300 328 для діапазону 2.4 ГГц
constexpr RegulatoryLimits ETSI_LIMITS {
    .domain = Domain::EU_ETSI,
    .max_tx_power_dbm = 20,       // 20 dBm (100 mW EIRP)
    .min_freq_mhz = 2400,
    .max_freq_mhz = 2483,
    .max_duty_cycle_pct = 100,
    .allowed_channel_mask = 0x1FFF // Канали 1..13
};

struct ComplianceConfig {
    std::string_view hw_revision;
    std::string_view fw_version;
    Domain           active_domain;
    int8_t           configured_power_dbm;
    uint16_t         channel_mask;
    uint32_t         cal_crc32;
};

class ComplianceValidator {
public:
    explicit constexpr ComplianceValidator(uint32_t expected_crc) noexcept
        : expected_crc_{expected_crc} {}

    [[nodiscard]] std::optional<std::string_view> validate(const ComplianceConfig& cfg) const noexcept {
        // 1. Контроль цілісності калібрувальної таблиці
        if (cfg.cal_crc32 != expected_crc_) {
            return "ERR_CALIBRATION_CRC_MISMATCH";
        }

        // 2. Перевірка дотримання європейських директив
        if (cfg.active_domain == Domain::EU_ETSI) {
            if (cfg.configured_power_dbm > ETSI_LIMITS.max_tx_power_dbm) {
                return "ERR_ETSI_TX_POWER_EXCEEDED";
            }
            if ((cfg.channel_mask & ~ETSI_LIMITS.allowed_channel_mask) != 0) {
                return "ERR_UNAUTHORIZED_FREQUENCY_CHANNEL";
            }
        } else {
            return "ERR_UNSUPPORTED_OR_INVALID_DOMAIN";
        }

        return std::nullopt; // Валідація успішна, порушень не виявлено
    }

private:
    uint32_t expected_crc_;
};

} // namespace compliance
