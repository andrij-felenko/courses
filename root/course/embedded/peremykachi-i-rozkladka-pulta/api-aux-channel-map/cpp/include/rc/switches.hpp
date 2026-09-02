#pragma once

#include <cstdint>
#include <string_view>

// Дискретне декодування допоміжних каналів: тумблери з гістерезисом
// і 6-позиційний селектор режимів польоту.
namespace rc {

enum class SwitchPosition : std::uint8_t { Low = 0, Center, High };

[[nodiscard]] std::string_view name(SwitchPosition pos) noexcept;

inline constexpr std::uint16_t kSwitchRiseUs = 1350;  // нижче -> вище
inline constexpr std::uint16_t kSwitchFallUs = 1650;  // вище -> нижче

class TwoPositionSwitch {
public:
    SwitchPosition update(std::uint16_t us) noexcept;
    [[nodiscard]] SwitchPosition position() const noexcept { return pos_; }
    [[nodiscard]] unsigned transitions() const noexcept { return transitions_; }

private:
    SwitchPosition pos_{SwitchPosition::Low};
    unsigned transitions_{0};
};

class ThreePositionSwitch {
public:
    SwitchPosition update(std::uint16_t us) noexcept;
    [[nodiscard]] SwitchPosition position() const noexcept { return pos_; }

private:
    SwitchPosition pos_{SwitchPosition::Low};
};

enum class FlightMode : std::uint8_t { Stabilize = 0, AltHold, Loiter, Auto, Rtl, Land };
inline constexpr std::size_t kFlightModeCount = 6;

// Вікна декодування селектора FLTMODE_CH
[[nodiscard]] FlightMode modeFromUs(std::uint16_t us) noexcept;
[[nodiscard]] std::uint16_t nominalUs(FlightMode mode) noexcept;
[[nodiscard]] std::string_view name(FlightMode mode) noexcept;
[[nodiscard]] bool requiresGnss(FlightMode mode) noexcept;
[[nodiscard]] std::uint16_t modeFlags(FlightMode mode) noexcept;

}  // namespace rc
