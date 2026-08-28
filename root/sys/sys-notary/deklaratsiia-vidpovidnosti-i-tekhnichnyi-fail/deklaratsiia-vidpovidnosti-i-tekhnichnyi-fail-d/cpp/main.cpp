#include <cstdint>
#include <string_view>
#include <array>

namespace notary {

struct ComplianceProfile {
    uint32_t         magic_header;
    std::string_view model_name;
    std::string_view hw_revision;
    std::string_view certified_fw;
    int8_t           max_tx_power_dbm;
    uint16_t         allowed_bands_mask;
    uint32_t         doc_manifest_crc32;
};

// Незмінна конфігурація згідно з Технічним файлом
constexpr ComplianceProfile EU_CERTIFIED_PROFILE {
    .magic_header = 0x54444631,
    .model_name = "GW-100-PRO",
    .hw_revision = "HW_REV_C",
    .certified_fw = "FW_v2.4.0",
    .max_tx_power_dbm = 20,       // Ліміт 100 мВт EIRP
    .allowed_bands_mask = 0x1FFF, // Канали 1..13
    .doc_manifest_crc32 = 0x8A4F91C2
};

class ComplianceGuard {
public:
    [[nodiscard]] static constexpr bool is_compliant(int8_t requested_power, uint8_t channel) noexcept {
        if (requested_power > EU_CERTIFIED_PROFILE.max_tx_power_dbm) {
            return false;
        }
        if (channel < 1 || channel > 13) {
            return false;
        }
        return true;
    }
};

} // namespace notary
