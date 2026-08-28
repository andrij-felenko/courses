#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <optional>
#include <array>
#include <cmath>
#include <cstring>
#include <algorithm>

namespace sys_notary {

/* ============================================================================
   1. ТИПІЗОВАНІ БІТОВІ МАСКИ ТА ПРАПОРЦІ ДОЗВОЛІВ
   ============================================================================ */
enum class ConsentFlags : uint32_t {
    None             = 0,
    DiagnosticsBasic = 1U << 0, // Рівень 1: напруга, heap, лічильники збоїв
    PerformanceStats = 1U << 1, // Рівень 2: завантаження CPU, тривалість задач
    AnalyticsUsage   = 1U << 2, // Рівень 2: лічильники натискань, сесії
    LocationCoarse   = 1U << 3, // Рівень 2: огрублені координати (~1.1 км)
    LocationPrecise  = 1U << 4, // Рівень 3: точні супутникові координати
    NetworkTopology  = 1U << 5, // Рівень 3: Wi-Fi BSSID, IP-адреси
    UserProfile      = 1U << 6  // Рівень 3: апаратний UID, серійний номер
};

[[nodiscard]] constexpr ConsentFlags operator|(ConsentFlags a, ConsentFlags b) noexcept {
    return static_cast<ConsentFlags>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr ConsentFlags operator&(ConsentFlags a, ConsentFlags b) noexcept {
    return static_cast<ConsentFlags>(static_cast<uint32_t>(a) & static_cast<uint32_t>(b));
}

[[nodiscard]] constexpr bool has_flag(ConsentFlags mask, ConsentFlags flag) noexcept {
    return (mask & flag) == flag;
}

/* ============================================================================
   2. СТРУКТУРИ ДАНИХ ТЕЛЕМЕТРІЇ
   ============================================================================ */
struct RawTelemetryFrame {
    uint32_t                   timestamp_utc{0};
    uint16_t                   vdd_voltage_mv{0};
    uint32_t                   free_heap_bytes{0};
    uint16_t                   crash_counter{0};
    uint8_t                    cpu_load_percent{0};
    uint32_t                   button_press_count{0};
    double                     gnss_latitude{0.0};
    double                     gnss_longitude{0.0};
    std::array<uint8_t, 12>    mcu_uid{};
    std::array<uint8_t, 6>     wifi_bssid{};
};

struct SanitizedTelemetryPayload {
    uint32_t                                 timestamp_utc{0};
    std::optional<uint16_t>                  vdd_voltage_mv{std::nullopt};
    std::optional<uint32_t>                  free_heap_bytes{std::nullopt};
    std::optional<uint16_t>                  crash_counter{std::nullopt};
    std::optional<uint8_t>                   cpu_load_percent{std::nullopt};
    std::optional<uint32_t>                  button_press_count{std::nullopt};
    std::optional<std::pair<double, double>> coordinates{std::nullopt};
    std::array<char, 17>                     pseudonym_id{};
};

/* ============================================================================
   3. RAII ЗАХИСНИК ОЧИЩЕННЯ ПАМ'ЯТІ ТА КЛАС МОДУЛЯ ПРИВАТНОСТІ
   ============================================================================ */
template <typename T>
class SecureZeroGuard {
public:
    explicit SecureZeroGuard(std::span<T> buffer) noexcept : buffer_(buffer) {}
    ~SecureZeroGuard() noexcept {
        volatile auto* p = reinterpret_cast<volatile uint8_t*>(buffer_.data());
        size_t len = buffer_.size_bytes();
        while (len--) {
            *p++ = 0U;
        }
    }
    SecureZeroGuard(const SecureZeroGuard&) = delete;
    SecureZeroGuard& operator=(const SecureZeroGuard&) = delete;
private:
    std::span<T> buffer_;
};

class TelemetryPrivacyGuard {
public:
    constexpr TelemetryPrivacyGuard() noexcept = default;

    void init(uint16_t terms_version, std::span<const uint8_t, 16> salt) noexcept {
        terms_version_ = terms_version;
        std::copy(salt.begin(), salt.end(), ephemeral_salt_.begin());
        consent_mask_ = ConsentFlags::None;
        opt_out_pending_ = false;
    }

    void set_consent(ConsentFlags mask) noexcept {
        consent_mask_ = mask;
        opt_out_pending_ = false;
    }

    void trigger_opt_out() noexcept {
        consent_mask_ = ConsentFlags::None;
        opt_out_pending_ = true;
        SecureZeroGuard guard(std::span{ephemeral_salt_});
    }

    [[nodiscard]] bool is_active() const noexcept {
        return !opt_out_pending_ && consent_mask_ != ConsentFlags::None;
    }

    [[nodiscard]] std::optional<SanitizedTelemetryPayload> filter(const RawTelemetryFrame& raw) const noexcept {
        if (!is_active()) {
            return std::nullopt;
        }

        SanitizedTelemetryPayload out{};
        out.timestamp_utc = raw.timestamp_utc;

        // 1. Технічна діагностика (Рівень 1)
        if (has_flag(consent_mask_, ConsentFlags::DiagnosticsBasic)) {
            out.vdd_voltage_mv = raw.vdd_voltage_mv;
            out.free_heap_bytes = raw.free_heap_bytes;
            out.crash_counter = raw.crash_counter;
        }

        // 2. Продуктивність (Рівень 2)
        if (has_flag(consent_mask_, ConsentFlags::PerformanceStats)) {
            out.cpu_load_percent = raw.cpu_load_percent;
        }

        // 3. Аналітика використання (Рівень 2)
        if (has_flag(consent_mask_, ConsentFlags::AnalyticsUsage)) {
            out.button_press_count = raw.button_press_count;
        }

        // 4. Геолокація
        if (has_flag(consent_mask_, ConsentFlags::LocationPrecise)) {
            out.coordinates = std::make_pair(raw.gnss_latitude, raw.gnss_longitude);
        } else if (has_flag(consent_mask_, ConsentFlags::LocationCoarse)) {
            out.coordinates = std::make_pair(
                coarsen_coordinate(raw.gnss_latitude),
                coarsen_coordinate(raw.gnss_longitude)
            );
        }

        // 5. Ідентифікатори
        if (has_flag(consent_mask_, ConsentFlags::UserProfile)) {
            format_hex_uid(raw.mcu_uid, out.pseudonym_id);
        } else if (has_flag(consent_mask_, ConsentFlags::AnalyticsUsage)) {
            generate_pseudonym(raw.mcu_uid, out.pseudonym_id);
        } else {
            out.pseudonym_id[0] = '\0';
        }

        return out;
    }

    bool crypto_shred() noexcept {
        trigger_opt_out();
        std::array<uint32_t, 8> mock_storage_keys{0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0};
        SecureZeroGuard guard(std::span{mock_storage_keys});
        return true;
    }

private:
    [[nodiscard]] static constexpr double coarsen_coordinate(double val) noexcept {
        const double sign = (val < 0.0) ? -1.0 : 1.0;
        const double abs_val = (val < 0.0) ? -val : val;
        const auto scaled = static_cast<uint32_t>(abs_val * 100.0 + 0.5);
        return sign * (static_cast<double>(scaled) / 100.0);
    }

    void generate_pseudonym(std::span<const uint8_t, 12> uid, std::span<char, 17> out) const noexcept {
        uint32_t hash = 2166136261U;
        for (uint8_t byte : uid) {
            hash = (hash ^ byte) * 16777619U;
        }
        for (uint8_t byte : ephemeral_salt_) {
            hash = (hash ^ byte) * 16777619U;
        }

        constexpr char hex[] = "0123456789ABCDEF";
        for (size_t i = 0; i < 8; ++i) {
            out[i] = hex[(hash >> (i * 4)) & 0x0F];
        }
        out[8] = '\0';
    }

    static void format_hex_uid(std::span<const uint8_t, 12> uid, std::span<char, 17> out) noexcept {
        constexpr char hex[] = "0123456789ABCDEF";
        for (size_t i = 0; i < 8; ++i) {
            out[i * 2]     = hex[(uid[i] >> 4) & 0x0F];
            out[i * 2 + 1] = hex[uid[i] & 0x0F];
        }
        out[16] = '\0';
    }

    ConsentFlags             consent_mask_{ConsentFlags::None};
    uint16_t                 terms_version_{1};
    std::array<uint8_t, 16>  ephemeral_salt_{};
    bool                     opt_out_pending_{false};
};

} // namespace sys_notary
