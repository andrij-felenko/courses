#include <string_view>
#include <optional>
#include <cstdint>

namespace timing {

/* Безпечний і швидкий розбір ISO-8601 / RFC 3339 у C++20 */
[[nodiscard]] constexpr std::optional<int64_t> parse_rfc3339_fast(std::string_view str) noexcept {
    if (str.size() < 20) return std::nullopt;
    if (str[4] != '-' || str[7] != '-' || (str[10] != 'T' && str[10] != 't') ||
        str[13] != ':' || str[16] != ':') {
        return std::nullopt;
    }

    auto parse_2 = [&](size_t idx) -> int {
        return (str[idx] - '0') * 10 + (str[idx + 1] - '0');
    };

    int year = (str[0] - '0') * 1000 + (str[1] - '0') * 100 + 
               (str[2] - '0') * 10 + (str[3] - '0');
    int month = parse_2(5);
    int day = parse_2(8);
    int hour = parse_2(11);
    int min = parse_2(14);
    int sec = parse_2(17);

    if (month < 1 || month > 12 || day < 1 || day > 31 ||
        hour > 23 || min > 59 || sec > 60) {
        return std::nullopt;
    }

    int y = year - (month <= 2 ? 1 : 0);
    int m = month <= 2 ? month + 9 : month - 3;
    int era = (y >= 0 ? y : y - 399) / 400;
    unsigned yoe = static_cast<unsigned>(y - era * 400);
    unsigned doy = (153 * static_cast<unsigned>(m) + 2) / 5 + static_cast<unsigned>(day) - 1;
    unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    int64_t days = static_cast<int64_t>(era) * 146097 + static_cast<int64_t>(doe) - 719468;

    return days * 86400LL + hour * 3600LL + min * 60LL + sec;
}

} // namespace timing
