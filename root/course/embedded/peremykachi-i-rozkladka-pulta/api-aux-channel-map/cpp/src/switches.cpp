#include "rc/switches.hpp"

#include <array>
#include <utility>

namespace rc {
namespace {

struct ModeWindow {
    std::uint16_t loUs;
    std::uint16_t hiUs;
    std::uint16_t nominalUs;
    std::string_view name;
    bool needsGnss;
};

constexpr std::array<ModeWindow, kFlightModeCount> kWindows{{
    { 988, 1230, 1165, "STABILIZE", false},
    {1231, 1360, 1295, "ALT_HOLD",  false},
    {1361, 1490, 1425, "LOITER",    true },
    {1491, 1620, 1555, "AUTO",      true },
    {1621, 1749, 1685, "RTL",       true },
    {1750, 2012, 1815, "LAND",      false},
}};

constexpr std::uint16_t kThreeLowHiUs    = 1300;
constexpr std::uint16_t kThreeCenterLoUs = 1350;
constexpr std::uint16_t kThreeCenterHiUs = 1650;
constexpr std::uint16_t kThreeHighLoUs   = 1700;

}  // namespace

std::string_view name(SwitchPosition pos) noexcept
{
    switch (pos) {
    case SwitchPosition::Low:    return "нижня";
    case SwitchPosition::Center: return "центральна";
    case SwitchPosition::High:   return "верхня";
    }
    return "?";
}

SwitchPosition TwoPositionSwitch::update(std::uint16_t us) noexcept
{
    const SwitchPosition before = pos_;

    // Смуга 1350..1650 нічого не змінює — саме вона гасить брязкіт тумблера
    if (pos_ == SwitchPosition::Low) {
        if (us > kSwitchRiseUs) {
            pos_ = SwitchPosition::High;
        }
    } else if (us < kSwitchFallUs) {
        pos_ = SwitchPosition::Low;
    }

    if (pos_ != before) {
        ++transitions_;
    }
    return pos_;
}

SwitchPosition ThreePositionSwitch::update(std::uint16_t us) noexcept
{
    if (us <= kThreeLowHiUs) {
        pos_ = SwitchPosition::Low;
    } else if (us >= kThreeCenterLoUs && us <= kThreeCenterHiUs) {
        pos_ = SwitchPosition::Center;
    } else if (us >= kThreeHighLoUs) {
        pos_ = SwitchPosition::High;
    }
    // Проміжок між вікнами — позиція утримується
    return pos_;
}

FlightMode modeFromUs(std::uint16_t us) noexcept
{
    for (std::size_t i = 0; i < kWindows.size(); ++i) {
        if (us <= kWindows[i].hiUs) {
            return static_cast<FlightMode>(i);
        }
    }
    // Вище за 2012 мкс — остання позиція селектора
    return FlightMode::Land;
}

std::uint16_t nominalUs(FlightMode mode) noexcept
{
    return kWindows[std::to_underlying(mode)].nominalUs;
}

std::string_view name(FlightMode mode) noexcept
{
    return kWindows[std::to_underlying(mode)].name;
}

bool requiresGnss(FlightMode mode) noexcept
{
    return kWindows[std::to_underlying(mode)].needsGnss;
}

std::uint16_t modeFlags(FlightMode mode) noexcept
{
    return static_cast<std::uint16_t>(1u << std::to_underlying(mode));
}

}  // namespace rc
