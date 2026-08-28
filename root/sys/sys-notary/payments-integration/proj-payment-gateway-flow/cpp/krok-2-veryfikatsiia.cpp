#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <expected>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <span>

// Функція для безпечного порівняння двох буферів за сталий час
bool constant_time_compare(std::span<const uint8_t> a, std::span<const uint8_t> b) {
    if (a.size() != b.size()) return false;
    uint8_t result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= a[i] ^ b[i];
    }
    return result == 0;
}

class WebhookSignatureVerifier {
private:
    std::string secret_;
    int64_t tolerance_seconds_;

public:
    explicit WebhookSignatureVerifier(std::string_view secret, int64_t tolerance = 300)
        : secret_(secret), tolerance_seconds_(tolerance) {}

    [[nodiscard]] std::expected<bool, std::string>
    verify_header(std::string_view raw_payload, std::string_view header, int64_t current_timestamp) const {
        std::string_view timestamp_str;
        std::string_view signature_hex;

        std::stringstream ss{std::string(header)};
        std::string item;
        while (std::getline(ss, item, ',')) {
            auto eq_pos = item.find('=');
            if (eq_pos != std::string::npos) {
                auto key = item.substr(0, eq_pos);
                auto val = item.substr(eq_pos + 1);
                if (key == "t") timestamp_str = val;
                if (key == "v1") signature_hex = val;
            }
        }

        if (timestamp_str.empty() || signature_hex.empty()) {
            return std::unexpected("Відсутні обов'язкові параметри t або v1 у заголовку");
        }

        int64_t event_time = std::stoll(std::string(timestamp_str));
        if (std::abs(current_timestamp - event_time) > tolerance_seconds_) {
            return std::unexpected("Мітка часу вебхука застаріла або з майбутнього");
        }

        return true;
    }
};
