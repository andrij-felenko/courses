#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <expected>
#include <algorithm>

struct SecurityTxt {
    std::vector<std::string> contacts;
    std::string encryption;
    std::string policy;
    std::string canonical;
    std::chrono::system_clock::time_point expires;
};

enum class ParseError {
    NoContactFound,
    NoExpiresFound,
    FileExpired,
    InvalidDateFormat,
    MalformedContent
};

class SecurityTxtParser {
public:
    static std::expected<SecurityTxt, ParseError> parse(std::string_view content) {
        SecurityTxt result;
        bool has_expires = false;

        std::istringstream stream{std::string(content)};
        std::string line;

        while (std::getline(stream, line)) {
            std::string_view sv = trim(line);
            if (sv.empty() || sv.starts_with('#')) {
                continue;
            }

            auto colon_pos = sv.find(':');
            if (colon_pos == std::string_view::npos) {
                continue;
            }

            auto field = trim(sv.substr(0, colon_pos));
            auto val   = trim(sv.substr(colon_pos + 1));

            if (iequals(field, "Contact")) {
                result.contacts.emplace_back(val);
            } else if (iequals(field, "Expires")) {
                auto tp = parse_rfc3339(val);
                if (!tp) {
                    return std::unexpected(ParseError::InvalidDateFormat);
                }
                result.expires = *tp;
                has_expires = true;
            } else if (iequals(field, "Encryption")) {
                result.encryption = std::string(val);
            } else if (iequals(field, "Policy")) {
                result.policy = std::string(val);
            } else if (iequals(field, "Canonical")) {
                result.canonical = std::string(val);
            }
        }

        if (result.contacts.empty()) {
            return std::unexpected(ParseError::NoContactFound);
        }
        if (!has_expires) {
            return std::unexpected(ParseError::NoExpiresFound);
        }

        const auto now = std::chrono::system_clock::now();
        if (result.expires < now) {
            return std::unexpected(ParseError::FileExpired);
        }

        return result;
    }

private:
    static std::string_view trim(std::string_view s) {
        while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) {
            s.remove_prefix(1);
        }
        while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back()))) {
            s.remove_suffix(1);
        }
        return s;
    }

    static bool iequals(std::string_view a, std::string_view b) {
        return std::ranges::equal(a, b, [](char c1, char c2) {
            return std::tolower(static_cast<unsigned char>(c1)) ==
                   std::tolower(static_cast<unsigned char>(c2));
        });
    }

    static std::optional<std::chrono::system_clock::time_point> parse_rfc3339(std::string_view date_str) {
        std::tm tm_buf{};
        std::istringstream ss{std::string(date_str)};
        ss >> std::get_time(&tm_buf, "%Y-%m-%dT%H:%M:%S");
        if (ss.fail()) {
            return std::nullopt;
        }

#if defined(_WIN32)
        std::time_t tt = _mkgmtime(&tm_buf);
#else
        std::time_t tt = timegm(&tm_buf);
#endif
        if (tt == -1) return std::nullopt;

        return std::chrono::system_clock::from_time_t(tt);
    }
};
