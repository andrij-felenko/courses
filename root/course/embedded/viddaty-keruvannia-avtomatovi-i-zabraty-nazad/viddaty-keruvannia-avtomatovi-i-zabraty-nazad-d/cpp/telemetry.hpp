#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <string_view>

#include "authority.hpp"
#include "types.hpp"

namespace fc {

// Сповіщення про перехоплення: STATUSTEXT на подію, HEARTBEAT раз на секунду
// й потокове значення α. Пульт (EdgeTX) сам розіграє вібро й озвучку за
// отриманим STATUSTEXT — на борту ми формуємо тільки повідомлення.

inline constexpr std::uint8_t kSeverityCritical = 2;
inline constexpr std::uint8_t kSeverityWarning = 4;
inline constexpr std::uint8_t kSeverityInfo = 6;

inline constexpr std::uint8_t kModeFlagCustomModeEnabled = 1;
inline constexpr std::uint8_t kModeFlagAutoEnabled = 4;
inline constexpr std::uint8_t kModeFlagStabilizeEnabled = 16;
inline constexpr std::uint8_t kModeFlagManualInputEnabled = 64;
inline constexpr std::uint8_t kModeFlagSafetyArmed = 128;

// STATUSTEXT.text — рівно 50 байтів; якщо текст займає всі 50, завершального
// нуля в полі немає. Так само name[10] у NAMED_VALUE_FLOAT.
struct StatusText {
    std::uint8_t severity{kSeverityInfo};
    std::array<char, 50> text{};
};

struct Heartbeat {
    std::uint8_t base_mode{};
    std::uint32_t custom_mode{};
};

struct NamedValueFloat {
    std::array<char, 10> name{};
    float value{};
    std::uint32_t time_boot_ms{};
};

class Telemetry {
public:
    void report(std::span<const Event> events, Seconds now);
    void stream(const Status& st, Seconds now);

private:
    static constexpr Seconds kHeartbeatPeriod{1.0f};
    static constexpr Seconds kNamedValuePeriod{0.1f};

    Seconds last_heartbeat_{0.0f};
    Seconds last_named_{0.0f};
    bool started_{false};
};

} // namespace fc
