#include <string>
#include <string_view>
#include <optional>
#include <expected>
#include <algorithm>

namespace web {

inline constexpr size_t MaxSsidLength = 32;
inline constexpr size_t MaxPassphraseLength = 64;

struct WifiConfigPayload {
    std::string ssid;
    std::string password;
};

enum class HttpError {
    BadRequest = 400,
    UnprocessableEntity = 422,
    InternalError = 500
};

class WifiConfigHttpHandler {
public:
    static std::expected<WifiConfigPayload, HttpError> parse_request_body(std::string_view body) noexcept {
        if (body.empty()) {
            return std::unexpected(HttpError::BadRequest);
        }

        auto ssid = extract_field(body, "ssid");
        if (!ssid || ssid->empty() || ssid->length() > MaxSsidLength) {
            return std::unexpected(HttpError::UnprocessableEntity);
        }

        auto password = extract_field(body, "password").value_or("");
        if (password.length() > MaxPassphraseLength) {
            return std::unexpected(HttpError::UnprocessableEntity);
        }

        return WifiConfigPayload{
            .ssid = std::string(*ssid),
            .password = std::string(password)
        };
    }

    static std::string_view generate_response(bool success) noexcept {
        if (success) {
            return "{\"status\":\"accepted\",\"message\":\"Connecting to station...\"}";
        }
        return "{\"status\":\"error\",\"message\":\"Invalid credentials payload\"}";
    }

private:
    static std::optional<std::string_view> extract_field(std::string_view json, std::string_view key) noexcept {
        std::string pattern = "\"" + std::string(key) + "\":\"";
        auto pos = json.find(pattern);
        if (pos == std::string_view::npos) {
            return std::nullopt;
        }

        pos += pattern.length();
        auto end_pos = json.find('"', pos);
        if (end_pos == std::string_view::npos) {
            return std::nullopt;
        }

        return json.substr(pos, end_pos - pos);
    }
};

} // namespace web
