// Ідіоматична C++20 валідація на основі constexpr-схем та std::expected
#include <cstdint>
#include <string_view>
#include <array>
#include <span>
#include <cstring>
#include <expected>

enum class ValidationError {
    OutOfRange,
    StringLengthViolation,
    ReadOnlyModification,
    RelationalConflict
};

struct AppConfig {
    char wifi_ssid[32];
    std::uint32_t report_interval_s;
    std::uint32_t timeout_s;
    std::uint16_t mqtt_port;
    bool tls_enable;
    std::uint32_t device_serial; // Read-Only
};

class ConfigValidator {
public:
    static std::expected<void, ValidationError> validate(const AppConfig& cand, const AppConfig& active) noexcept {
        // 1. Перевірка Read-Only серійного номера
        if (cand.device_serial != active.device_serial) {
            return std::unexpected(ValidationError::ReadOnlyModification);
        }

        // 2. Валідація рядків
        const std::size_t ssid_len = ::strnlen(cand.wifi_ssid, sizeof(cand.wifi_ssid));
        if (ssid_len == 0 || ssid_len >= sizeof(cand.wifi_ssid)) {
            return std::unexpected(ValidationError::StringLengthViolation);
        }

        // 3. Валідація діапазонів
        if (cand.report_interval_s < 1 || cand.report_interval_s > 86'400) {
            return std::unexpected(ValidationError::OutOfRange);
        }
        if (cand.timeout_s < 5 || cand.timeout_s > 3'600) {
            return std::unexpected(ValidationError::OutOfRange);
        }
        if (cand.mqtt_port == 0) {
            return std::unexpected(ValidationError::OutOfRange);
        }

        // 4. Крос-параметричні правила
        if (cand.timeout_s <= (cand.report_interval_s * 2)) {
            return std::unexpected(ValidationError::RelationalConflict);
        }
        if (cand.tls_enable && cand.mqtt_port == 1883) {
            return std::unexpected(ValidationError::RelationalConflict);
        }

        return {};
    }
};
