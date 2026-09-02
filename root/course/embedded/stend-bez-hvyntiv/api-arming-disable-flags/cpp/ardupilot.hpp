#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <string_view>
#include <vector>

namespace ap {

// ArduPilot тримає перелік передпольотних перевірок в одному
// цілочисельному параметрі ARMING_CHECK. Номер біта = номер перевірки;
// біт 0 (значення 1) зветься All і вмикає решту незалежно від них.
enum class Check : std::uint8_t {
    All = 0,
    Barometer,
    Compass,
    Gps,
    Ins,
    Parameters,
    RcChannels,
    BoardVoltage,
    BatteryLevel,
    Logging,
    HardwareSwitch,
    GpsConfig,
    System,
    Mission,
    Rangefinder,
    Count
};

inline constexpr std::size_t kCheckCount = static_cast<std::size_t>(Check::Count);

struct CheckInfo {
    std::string_view name;
    std::string_view failure;   // текст STATUSTEXT при відмові; залежить від версії
};

inline constexpr std::array<CheckInfo, kCheckCount> kCheckTable{{
    {"All", ""},
    {"Barometer", "PreArm: Baro not healthy"},
    {"Compass", "PreArm: Compass not calibrated"},
    {"GPS", "PreArm: Need 3D Fix"},
    {"INS", "PreArm: Accels not calibrated"},
    {"Parameters", "PreArm: Check FS_THR_VALUE"},
    {"RC Channels", "PreArm: RC not calibrated"},
    {"Board Voltage", "PreArm: Check board voltage"},
    {"Battery Level", "PreArm: Battery below minimum arming voltage"},
    {"Logging", "PreArm: Logging failed"},
    {"Hardware Switch", "PreArm: Safety Switch"},
    {"GPS Config", "PreArm: GPS 1 failing configuration checks"},
    {"System", "PreArm: Internal errors detected"},
    {"Mission", "PreArm: Mission is empty"},
    {"Rangefinder", "PreArm: Rangefinder 1: Not Detected"},
}};

[[nodiscard]] constexpr const CheckInfo& info(Check check) noexcept
{
    return kCheckTable[static_cast<std::size_t>(check)];
}

class CheckMask {
public:
    constexpr explicit CheckMask(std::int32_t value) noexcept : value_{value} {}

    [[nodiscard]] constexpr bool enabled(Check check) const noexcept
    {
        if (value_ < 0) {
            return true;                      // наземна станція пише −1 як «усі»
        }
        if ((value_ & 1) != 0) {
            return true;                      // біт All накриває решту
        }
        return ((value_ >> static_cast<int>(check)) & 1) != 0;
    }

    [[nodiscard]] constexpr std::int32_t value() const noexcept { return value_; }

private:
    std::int32_t value_;
};

enum class Severity : std::uint8_t {
    Emergency = 0, Alert, Critical, Error, Warning, Notice, Info, Debug
};

// Пакет MAVLink STATUSTEXT (#253): поле text — рівно 50 байтів,
// і завершального нуля в ньому може не бути.
class StatusText {
public:
    static constexpr std::size_t kTextLen = 50;

    StatusText(Severity severity, std::string_view text) noexcept;

    [[nodiscard]] Severity severity() const noexcept { return severity_; }
    [[nodiscard]] std::string_view text() const noexcept;

private:
    Severity severity_;
    std::array<char, kTextLen> text_{};
};

// Звіт про несправні підсистеми, чиї перевірки увімкнені в ARMING_CHECK.
[[nodiscard]] std::vector<StatusText> prearmReport(CheckMask enabled,
                                                   std::span<const Check> failing);

}  // namespace ap
