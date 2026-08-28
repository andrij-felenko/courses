#include <cstdint>
#include <string_view>
#include <vector>
#include <expected>
#include <format>
#include <span>

namespace avr::fuses {

enum class Severity {
    Info,
    Warning,
    CriticalBrickRisk
};

struct FuseIssue {
    Severity severity;
    std::string_view message;
};

struct FuseConfig {
    std::uint8_t low{0x62};
    std::uint8_t high{0xD9};
    std::uint8_t extended{0xFF};
    std::uint8_t lock{0xFF};

    // Маски старшого байта
    static constexpr std::uint8_t rstdisbl_mask = 1U << 7;
    static constexpr std::uint8_t dwen_mask     = 1U << 6;
    static constexpr std::uint8_t spien_mask    = 1U << 5;
    static constexpr std::uint8_t wdton_mask    = 1U << 4;
    
    // Маски молодшого та розширеного байтів
    static constexpr std::uint8_t cksel_mask    = 0x0FU;
    static constexpr std::uint8_t bodlevel_mask = 0x07U;

    [[nodiscard]] constexpr bool is_reset_disabled() const noexcept {
        return (high & rstdisbl_mask) == 0;
    }

    [[nodiscard]] constexpr bool is_isp_disabled() const noexcept {
        return (high & spien_mask) != 0;
    }

    [[nodiscard]] constexpr bool is_debugwire_enabled() const noexcept {
        return (high & dwen_mask) == 0;
    }

    [[nodiscard]] constexpr bool is_bod_disabled() const noexcept {
        return (extended & bodlevel_mask) == 0x07U;
    }
};

class FuseAuditor {
public:
    [[nodiscard]] static std::expected<std::vector<FuseIssue>, std::string_view> 
    audit(const FuseConfig& config) noexcept {
        std::vector<FuseIssue> issues;

        if (config.is_reset_disabled()) {
            issues.push_back({
                Severity::CriticalBrickRisk,
                "КРИТИЧНО: RSTDISBL активний. Пін Reset переведено в GPIO. ISP доступ буде втрачено."
            });
        }

        if (config.is_isp_disabled()) {
            issues.push_back({
                Severity::CriticalBrickRisk,
                "КРИТИЧНО: SPIEN не встановлений. Послідовне програмування вимкнено (потрібен HVPP)."
            });
        }

        if (config.is_debugwire_enabled()) {
            issues.push_back({
                Severity::Warning,
                "УВАГА: debugWIRE активовано (DWEN=0). Потрібен апаратний емулятор для скидання."
            });
        }

        if ((config.low & FuseConfig::cksel_mask) == 0x00U) {
            issues.push_back({
                Severity::Warning,
                "УВАГА: Режим External Clock. Потребує активного тактового сигналу на вході XTAL1."
            });
        }

        if (config.is_bod_disabled()) {
            issues.push_back({
                Severity::Warning,
                "ПОПЕРЕДЖЕННЯ: BOD деактивовано. Можливе пошкодження Flash при падінні напруги."
            });
        }

        return issues;
    }

    [[nodiscard]] static std::string generate_avrdude_args(const FuseConfig& config, std::string_view part) {
        return std::format("-c usbasp -p {} -U lfuse:w:0x{:02X}:m -U hfuse:w:0x{:02X}:m -U efuse:w:0x{:02X}:m -U lock:w:0x{:02X}:m",
                           part, config.low, config.high, config.extended, config.lock);
    }
};

} // namespace avr::fuses
