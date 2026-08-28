#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>
#include <cstdio>

namespace gcs::ui {

// Типізовані семантичні кольори RGB565
enum class ColorRGB565 : uint16_t {
    Green       = 0x2560, // Норма: #27ae60
    Yellow      = 0xFCC0, // Увага / Деградація: #f39c12
    Red         = 0xC1C5, // Критична відмова: #c0392b
    Gray        = 0x7BEF, // Застарілі дані: #7f8c8d
    White       = 0xFFFF, // Основний контрастний текст
    Black       = 0x0000  // Контур / Тінь / Фон
};

enum class Severity : uint8_t {
    Normal = 0,
    Warning,
    Critical,
    Stale
};

enum class FlightMode : uint8_t {
    Manual = 0,
    AltHold,
    PosHold,
    AutoMission,
    Guided,
    FailsafeRTL
};

struct SpatialState {
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    float altitude_amsl_m{0.0f};
    float altitude_agl_m{0.0f};
    float ground_speed_mps{0.0f};
    float vertical_speed_mps{0.0f};
};

struct PowerHealth {
    uint16_t voltage_mv{16800};
    int16_t  current_cda{0};     // 0.01 A
    uint16_t consumed_mah{0};
    uint8_t  battery_soc_pct{100};
    int8_t   esc_temperature_c{35};
};

struct LinkQuality {
    int8_t   rssi_dbm{-65};
    int8_t   snr_db{18};
    uint8_t  link_quality_pct{100};
    uint16_t round_trip_time_ms{25};
};

struct TelemetryFrame {
    SpatialState state{};
    FlightMode   mode{FlightMode::Manual};
    bool         is_armed{false};
    PowerHealth  power{};
    LinkQuality  link{};
    uint32_t     timestamp_ms{0};
};

// Фіксований буфер форматування без динамічної пам'яті
template <size_t Capacity>
class FixedString {
public:
    constexpr FixedString() noexcept { buffer_[0] = '\0'; }

    template <typename... Args>
    void format(const char* fmt, Args... args) noexcept {
        std::snprintf(buffer_.data(), buffer_.size(), fmt, args...);
    }

    [[nodiscard]] constexpr std::string_view view() const noexcept {
        return std::string_view(buffer_.data());
    }

    [[nodiscard]] constexpr const char* c_str() const noexcept {
        return buffer_.data();
    }

private:
    std::array<char, Capacity> buffer_{};
};

class StatusBarPresenter {
public:
    static constexpr uint32_t kStaleWarnTimeoutMs   = 1000;
    static constexpr uint32_t kStaleCritTimeoutMs   = 3000;
    static constexpr uint16_t kHysteresisVoltageMv  = 250;
    static constexpr uint32_t kHysteresisDebounceMs = 1500;
    static constexpr uint16_t kVoltageWarnThreshMv  = 14800; // 14.8 В
    static constexpr uint16_t kVoltageCritThreshMv  = 14000; // 14.0 В

    void update(const TelemetryFrame& frame, uint32_t now_ms) noexcept {
        const uint32_t age_ms = now_ms - frame.timestamp_ms;

        // 1. Оцінка актуальності каналу зв'язку
        if (age_ms >= kStaleCritTimeoutMs) {
            link_severity_ = Severity::Critical;
            link_text_.format("[X LOST: %.1fs]", static_cast<float>(age_ms) / 1000.0f);
        } else if (age_ms >= kStaleWarnTimeoutMs) {
            link_severity_ = Severity::Stale;
            link_text_.format("[⧗ STALE: %.1fs]", static_cast<float>(age_ms) / 1000.0f);
        } else {
            if (frame.link.link_quality_pct < 50 || frame.link.rssi_dbm < -100) {
                link_severity_ = Severity::Warning;
                link_text_.format("[! LQ:%u%% %ddBm]", frame.link.link_quality_pct, frame.link.rssi_dbm);
            } else {
                link_severity_ = Severity::Normal;
                link_text_.format("[OK LQ:%u%% %ddBm]", frame.link.link_quality_pct, frame.link.rssi_dbm);
            }
        }

        // 2. Оцінка стану батареї з гістерезисом
        evaluate_power(frame.power.voltage_mv, now_ms);
        const float volt_f = static_cast<float>(frame.power.voltage_mv) / 1000.0f;
        const float curr_f = static_cast<float>(frame.power.current_cda) / 100.0f;

        if (power_severity_ == Severity::Critical) {
            power_text_.format("[X CRIT %.1fV %.1fA]", volt_f, curr_f);
        } else if (power_severity_ == Severity::Warning) {
            power_text_.format("[! LOW %.1fV %.1fA]", volt_f, curr_f);
        } else {
            power_text_.format("[OK %.1fV %u%%]", volt_f, frame.power.battery_soc_pct);
        }

        // 3. Анонсатор автопілотного режиму
        mode_text_.format("%s", format_mode(frame.mode, frame.is_armed).data());

        // 4. Просторовий стан
        state_text_.format("H:%.0fm GS:%.1fm/s VSI:%+.1f",
                           frame.state.altitude_agl_m,
                           frame.state.ground_speed_mps,
                           frame.state.vertical_speed_mps);

        // Розрахунок глобального рівня деградації
        if (link_severity_ == Severity::Critical || power_severity_ == Severity::Critical || frame.mode == FlightMode::FailsafeRTL) {
            overall_severity_ = Severity::Critical;
        } else if (link_severity_ == Severity::Warning || link_severity_ == Severity::Stale || power_severity_ == Severity::Warning) {
            overall_severity_ = Severity::Warning;
        } else {
            overall_severity_ = Severity::Normal;
        }
    }

    [[nodiscard]] constexpr Severity overall_severity() const noexcept { return overall_severity_; }
    [[nodiscard]] constexpr Severity power_severity() const noexcept   { return power_severity_; }
    [[nodiscard]] constexpr Severity link_severity() const noexcept    { return link_severity_; }

    [[nodiscard]] constexpr std::string_view mode_str() const noexcept  { return mode_text_.view(); }
    [[nodiscard]] constexpr std::string_view power_str() const noexcept { return power_text_.view(); }
    [[nodiscard]] constexpr std::string_view link_str() const noexcept  { return link_text_.view(); }
    [[nodiscard]] constexpr std::string_view state_str() const noexcept { return state_text_.view(); }

    [[nodiscard]] static constexpr ColorRGB565 to_color(Severity sev) noexcept {
        switch (sev) {
            case Severity::Normal:   return ColorRGB565::Green;
            case Severity::Warning:  return ColorRGB565::Yellow;
            case Severity::Critical: return ColorRGB565::Red;
            case Severity::Stale:    return ColorRGB565::Gray;
        }
        return ColorRGB565::White;
    }

private:
    void evaluate_power(uint16_t v_mv, uint32_t now_ms) noexcept {
        if (v_mv < kVoltageCritThreshMv) {
            power_severity_ = Severity::Critical;
            last_warn_time_ms_ = now_ms;
            return;
        }

        if (v_mv < kVoltageWarnThreshMv) {
            if (power_severity_ == Severity::Critical) {
                if (v_mv >= (kVoltageCritThreshMv + kHysteresisVoltageMv)) {
                    power_severity_ = Severity::Warning;
                }
            } else {
                power_severity_ = Severity::Warning;
            }
            last_warn_time_ms_ = now_ms;
            return;
        }

        if (power_severity_ == Severity::Warning) {
            if (v_mv >= (kVoltageWarnThreshMv + kHysteresisVoltageMv) &&
                (now_ms - last_warn_time_ms_ >= kHysteresisDebounceMs)) {
                power_severity_ = Severity::Normal;
            }
        } else {
            power_severity_ = Severity::Normal;
        }
    }

    [[nodiscard]] static constexpr std::string_view format_mode(FlightMode mode, bool armed) noexcept {
        if (!armed) return "DISARMED";
        switch (mode) {
            case FlightMode::Manual:      return "ARM: MANUAL";
            case FlightMode::AltHold:     return "ARM: ALTHOLD";
            case FlightMode::PosHold:     return "ARM: POSHOLD";
            case FlightMode::AutoMission: return "ARM: AUTO";
            case FlightMode::Guided:      return "ARM: GUIDED";
            case FlightMode::FailsafeRTL: return "FAILSAFE: RTL";
        }
        return "ARM: UNKNOWN";
    }

    Severity overall_severity_{Severity::Normal};
    Severity power_severity_{Severity::Normal};
    Severity link_severity_{Severity::Normal};
    uint32_t last_warn_time_ms_{0};

    FixedString<24> mode_text_{};
    FixedString<28> power_text_{};
    FixedString<28> link_text_{};
    FixedString<36> state_text_{};
};

} // namespace gcs::ui
