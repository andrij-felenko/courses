#include <cstdint>
#include <string_view>
#include <span>
#include <optional>
#include <array>
#include <cmath>
#include <cstring>
#include <algorithm>

namespace sys_notary {

/* Типізована бітова маска дозволів згідно з GDPR/CCPA */
enum class ConsentFlags : uint32_t {
    None             = 0,
    DiagnosticsBasic = 1U << 0, // Рівень 1: напруга, heap, збої
    AnalyticsUsage   = 1U << 1, // Рівень 2: лічильники функцій
    LocationCoarse   = 1U << 2, // Рівень 2: огрублені координати (~1.1 км)
    LocationPrecise  = 1U << 3, // Рівень 3: точний GNSS
    NetworkTopology  = 1U << 4, // Рівень 3: Wi-Fi BSSID / IP
    UserProfile      = 1U << 5  // Рівень 3: персональні дані
};

constexpr ConsentFlags operator|(ConsentFlags a, ConsentFlags b) noexcept {
    return static_cast<ConsentFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr ConsentFlags operator&(ConsentFlags a, ConsentFlags b) noexcept {
    return static_cast<ConsentFlags>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

constexpr bool has_flag(ConsentFlags mask, ConsentFlags flag) noexcept {
    return (mask & flag) == flag;
}

/* Сирі телеметричні дані датчиків та мікроконтролера */
struct RawTelemetryData {
    uint32_t         timestamp_utc{0};
    float            battery_voltage{0.0f};
    uint32_t         free_heap_bytes{0};
    uint16_t         crash_count{0};
    uint32_t         button_press_count{0};
    double           gnss_latitude{0.0};
    double           gnss_longitude{0.0};
    std::string_view device_serial{};
    std::string_view wifi_bssid{};
};

/* Відфільтроване та анонімізоване корисне навантаження */
struct FilteredTelemetryPayload {
    uint32_t                      timestamp_utc{0};
    float                         battery_voltage{0.0f};
    uint32_t                      free_heap_bytes{0};
    uint16_t                      crash_count{0};
    std::optional<uint32_t>       button_press_count{std::nullopt};
    std::optional<std::pair<double, double>> coordinates{std::nullopt};
    std::array<char, 32>          anonymized_id{};
};

/* Клас керування політикою приватності на пристрої */
class PrivacyGuard {
public:
    constexpr PrivacyGuard() noexcept = default;

    void set_consent(ConsentFlags flags, uint16_t terms_version) noexcept {
        consent_mask_ = flags;
        terms_version_ = terms_version;
        opt_out_pending_ = false;
    }

    void trigger_opt_out() noexcept {
        consent_mask_ = ConsentFlags::None;
        opt_out_pending_ = true;
    }

    [[nodiscard]] bool is_opt_out_active() const noexcept {
        return opt_out_pending_ || consent_mask_ == ConsentFlags::None;
    }

    [[nodiscard]] std::optional<FilteredTelemetryPayload> filter(const RawTelemetryData& raw) const noexcept {
        if (is_opt_out_active()) {
            return std::nullopt;
        }

        FilteredTelemetryPayload payload{};

        // Базова технічна діагностика (Рівень 1)
        if (has_flag(consent_mask_, ConsentFlags::DiagnosticsBasic)) {
            payload.timestamp_utc = raw.timestamp_utc;
            payload.battery_voltage = raw.battery_voltage;
            payload.free_heap_bytes = raw.free_heap_bytes;
            payload.crash_count = raw.crash_count;
        }

        // Функціональна аналітика (Рівень 2)
        if (has_flag(consent_mask_, ConsentFlags::AnalyticsUsage)) {
            payload.button_press_count = raw.button_press_count;
        }

        // Обробка координат із захистом приватності
        if (has_flag(consent_mask_, ConsentFlags::LocationPrecise)) {
            payload.coordinates = std::make_pair(raw.gnss_latitude, raw.gnss_longitude);
        } else if (has_flag(consent_mask_, ConsentFlags::LocationCoarse)) {
            payload.coordinates = std::make_pair(
                coarsen(raw.gnss_latitude),
                coarsen(raw.gnss_longitude)
            );
        }

        // Обробка ідентифікатора
        if (has_flag(consent_mask_, ConsentFlags::UserProfile) && !raw.device_serial.empty()) {
            const auto len = std::min(raw.device_serial.size(), payload.anonymized_id.size() - 1);
            std::memcpy(payload.anonymized_id.data(), raw.device_serial.data(), len);
            payload.anonymized_id[len] = '\0';
        } else {
            payload.anonymized_id[0] = '\0';
        }

        return payload;
    }

private:
    static constexpr double coarsen(double coord) noexcept {
        const double scaled = std::round(coord * 100.0);
        return scaled / 100.0;
    }

    ConsentFlags consent_mask_{ConsentFlags::None};
    uint16_t     terms_version_{1};
    bool         opt_out_pending_{false};
};

} // namespace sys_notary
