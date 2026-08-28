#include <cerrno>
#include <climits>
#include <cstdlib>
#include <expected>
#include <string_view>

enum class ParseError {
    NoDigits,
    OutOfRange,
    InvalidData
};

[[nodiscard]] std::expected<long, ParseError>
parse_config_value(std::string_view s) noexcept {
    if (s.empty()) {
        return std::unexpected(ParseError::NoDigits);
    }

    char *endptr = nullptr;
    errno = 0; // ОБОВ'ЯЗКОВО: скидаємо стан перед викликом

    long val = std::strtol(s.data(), &endptr, 10);

    if (errno == ERANGE) {
        return std::unexpected(ParseError::OutOfRange);
    }
    if (errno != 0) {
        return std::unexpected(ParseError::InvalidData);
    }
    if (endptr == s.data()) {
        return std::unexpected(ParseError::NoDigits);
    }

    return val;
}
