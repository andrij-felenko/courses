#include <string_view>

void parse_nmea_sentence(std::string_view nmea) {
    // Вхід: "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47"
    if (!nmea.starts_with("$GPGGA")) {
        return;
    }

    // Видаляємо префікс "$GPGGA," (7 символів) без копіювання за O(1)
    nmea.remove_prefix(7);

    // Знаходимо першу кому
    std::size_t comma_pos = nmea.find(',');
    if (comma_pos != std::string_view::npos) {
        std::string_view time_field = nmea.substr(0, comma_pos); // "123519"
        // time_field дивиться прямо у вхідний буфер!
        (void)time_field;
    }
}
