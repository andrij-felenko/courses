#include <charconv>

struct GpsCoordinates {
    int32_t lat_microdegrees{0};
    int32_t lon_microdegrees{0};
    int32_t altitude_mm{0};
};

std::optional<GpsCoordinates> parse_gps_text(std::string_view text) noexcept {
    // Вхідний формат: "LAT:48450100,LON:35012300,ALT:120500"
    if (!text.starts_with("LAT:")) return std::nullopt;
    text.remove_prefix(4);

    GpsCoordinates coords{};

    // 1. Парсинг широти
    auto res_lat = std::from_chars(text.data(), text.data() + text.size(), coords.lat_microdegrees);
    if (res_lat.ec != std::errc{}) return std::nullopt;
    text.remove_prefix(res_lat.ptr - text.data());

    if (text.empty() || text.front() != ',') return std::nullopt;
    text.remove_prefix(1);

    // 2. Парсинг довготи
    if (!text.starts_with("LON:")) return std::nullopt;
    text.remove_prefix(4);
    auto res_lon = std::from_chars(text.data(), text.data() + text.size(), coords.lon_microdegrees);
    if (res_lon.ec != std::errc{}) return std::nullopt;
    text.remove_prefix(res_lon.ptr - text.data());

    if (text.empty() || text.front() != ',') return std::nullopt;
    text.remove_prefix(1);

    // 3. Парсинг висоти
    if (!text.starts_with("ALT:")) return std::nullopt;
    text.remove_prefix(4);
    auto res_alt = std::from_chars(text.data(), text.data() + text.size(), coords.altitude_mm);
    if (res_alt.ec != std::errc{}) return std::nullopt;

    return coords;
}
