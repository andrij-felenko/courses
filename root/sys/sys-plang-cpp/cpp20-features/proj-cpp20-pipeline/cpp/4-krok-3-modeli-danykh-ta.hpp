#include <format>
#include <string>

struct ThermalReading {
    std::uint64_t timestamp_ms{0};
    std::string   sensor_id{};
    double        raw_value{0.0}; // Температура в Кельвінах
    bool          calibrated{true};

    [[nodiscard]] bool is_valid() const noexcept {
        return calibrated && raw_value > 0.0;
    }
};

// Спеціалізація std::formatter для ThermalReading
template<>
struct std::formatter<ThermalReading> : std::formatter<std::string_view> {
    auto format(const ThermalReading& r, std::format_context& ctx) const {
        std::string temp_buf = std::format(
            "[{:>8} ms] Сенсор: {:<8} | Сире: {:6.2f} K | Стан: {}",
            r.timestamp_ms,
            r.sensor_id,
            r.raw_value,
            r.calibrated ? "OK" : "ПОМИЛКА"
        );
        return std::formatter<std::string_view>::format(temp_buf, ctx);
    }
};

// Структура обробленого сигналу тривоги
struct ProcessedAlarm {
    std::uint64_t timestamp_ms;
    std::string   sensor_id;
    double        celsius;
};

template<>
struct std::formatter<ProcessedAlarm> : std::formatter<std::string_view> {
    auto format(const ProcessedAlarm& a, std::format_context& ctx) const {
        std::string buf = std::format(
            "🚨 ТРИВОГА [{:>8} ms] {} -> {:6.2f} °C",
            a.timestamp_ms,
            a.sensor_id,
            a.celsius
        );
        return std::formatter<std::string_view>::format(buf, ctx);
    }
};
