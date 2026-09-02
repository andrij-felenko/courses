#pragma once

// Статусний інтерфейс: маска відмов, арбітраж дії, кадр FAILSAFE_STATUS,
// сповіщення STATUSTEXT зі шкалою MAV_SEVERITY.

#include "params.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string>
#include <string_view>
#include <utility>

namespace autopilot::failsafe {

enum class Fault : std::uint32_t {
    None         = 0,
    RcLost       = 1u << 0,
    GcsLost      = 1u << 1,
    GnssHdop     = 1u << 2,
    GnssLost     = 1u << 3,
    EkfDiverged  = 1u << 4,
    BattLow      = 1u << 5,
    BattCrit     = 1u << 6,
    FenceRadius  = 1u << 7,
    FenceAlt     = 1u << 8,
    EscFail      = 1u << 9,
    AttitudeLost = 1u << 10,
};

constexpr Fault operator|(Fault a, Fault b) noexcept
{
    return static_cast<Fault>(std::to_underlying(a) | std::to_underlying(b));
}
constexpr Fault operator&(Fault a, Fault b) noexcept
{
    return static_cast<Fault>(std::to_underlying(a) & std::to_underlying(b));
}
constexpr Fault& operator|=(Fault& a, Fault b) noexcept { return a = a | b; }
constexpr bool has(Fault set, Fault f) noexcept { return (set & f) != Fault::None; }

inline constexpr std::array<Fault, 11> kAllFaults{
    Fault::RcLost, Fault::GcsLost, Fault::GnssHdop, Fault::GnssLost,
    Fault::EkfDiverged, Fault::BattLow, Fault::BattCrit,
    Fault::FenceRadius, Fault::FenceAlt, Fault::EscFail, Fault::AttitudeLost
};

// Коди дій упорядковані за суворістю: більший перекриває менший.
enum class Action : std::uint8_t { None = 0, Warn, AltHold, Rtl, Land, Terminate };
enum class Arbiter : std::uint8_t { None = 0, RcLink, Gcs, Navigation, Battery, Geofence, Propulsion };
enum class Severity : std::uint8_t {
    Emergency = 0, Alert = 1, Critical = 2, Error = 3, Warning = 4, Notice = 5, Info = 6
};

std::string_view toString(Fault f) noexcept;
std::string_view toString(Action a) noexcept;
std::string_view toString(Arbiter a) noexcept;
std::string_view toString(Severity s) noexcept;

struct TelemetryFrame {
    std::uint64_t timestamp_us{0};        // Час польотного контролера (мікросекунди)
    Fault         active_faults{Fault::None};  // Маска підтверджених відмов
    Action        active_action{Action::None}; // Поточний аварійний режим
    Arbiter       arbiter{Arbiter::None};      // Правило, що згенерувало дію
    std::uint16_t rc_valid_frames_sec{0};      // Валідних RC-пакетів за останню секунду
    float         gnss_hdop{0.0f};             // Поточний HDOP приймача
    float         batt_cell_min_v{0.0f};       // Мінімальна напруга серед комірок
    float         distance_to_fence_m{0.0f};   // Відстань до кордону геозони
};

inline constexpr std::size_t kFrameSize = 28;
enum class FrameError { TooShort, UnknownBits };

std::array<std::byte, kFrameSize>          pack(const TelemetryFrame& t) noexcept;
std::expected<TelemetryFrame, FrameError>  unpack(std::span<const std::byte> raw) noexcept;

struct Decision {
    Action  action{Action::None};
    Arbiter arbiter{Arbiter::None};
};

// Дія одного правила з урахуванням конфігурації та решти активних відмов.
Decision ruleFor(Fault fault, Fault active, const ParamBlock& p) noexcept;
// Арбітраж усіх активних відмов плюс деградація до виконуваної дії.
Decision decide(Fault active, const ParamBlock& p) noexcept;
Action   degrade(Action action, Fault active) noexcept;

Severity severityOf(Fault fault) noexcept;

struct Notice {
    Severity    severity{Severity::Info};
    std::string text;
};

Notice statusText(Fault fault, Fault active, const ParamBlock& p, const TelemetryFrame& t);
Notice recoveryNotice(const ParamBlock& p);

} // namespace autopilot::failsafe
