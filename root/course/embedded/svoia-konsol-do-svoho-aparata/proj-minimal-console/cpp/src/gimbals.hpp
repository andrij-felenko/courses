#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <utility>

#include "hal.hpp"

namespace console {

inline constexpr std::uint16_t kAxisCenter = 1024;
inline constexpr std::uint16_t kAxisMax = 2047;

enum class Axis : std::size_t { Roll = 0, Pitch = 1, Throttle = 2, Yaw = 3 };

// Причини, з яких пульт не має права виходити в ефір.
enum class Fault : std::uint8_t {
    None = 0,
    ThrottleUp = 1,
    ArmEngaged = 2,
    AxisDead = 4
};

constexpr Fault operator|(Fault a, Fault b) noexcept
{
    return static_cast<Fault>(std::to_underlying(a) | std::to_underlying(b));
}
constexpr Fault& operator|=(Fault& a, Fault b) noexcept { return a = a | b; }
constexpr bool operator&(Fault a, Fault b) noexcept
{
    return (std::to_underlying(a) & std::to_underlying(b)) != 0;
}
constexpr bool any(Fault f) noexcept { return f != Fault::None; }

struct AxisConfig {
    std::uint16_t min;
    std::uint16_t center;
    std::uint16_t max;
    std::uint16_t deadband;
    std::uint8_t expoPercent;   // частка кубічної складової кривої
    std::uint8_t alpha;         // вага свіжого відліку в IIR, 1/256
    bool unipolar;              // вісь без центра (газ)
};

class Gimbals {
public:
    [[nodiscard]] std::uint16_t processAxis(std::size_t channel, std::uint16_t raw) noexcept;

    [[nodiscard]] std::array<std::uint16_t, hal::kAxisCount> process(
        std::span<const std::uint16_t, hal::kAxisCount> raw) noexcept;

    [[nodiscard]] Fault safety(std::span<const std::uint16_t, hal::kAxisCount> scaled,
                               std::uint16_t switches) const noexcept;

    [[nodiscard]] std::uint8_t auxUpdate(std::uint16_t switches) noexcept;

private:
    [[nodiscard]] bool axisDead() const noexcept;

    // Заводське калібрування. На серійному пульті його читають із флеш-розділу
    // після процедури обертання стіків; тут це константи — тема про інше.
    std::array<AxisConfig, hal::kAxisCount> config_{{
        {320, 2048, 3780, 25, 30, 64, false},   // крен
        {330, 2050, 3770, 25, 30, 64, false},   // тангаж
        {310, 2048, 3790, 0, 0, 96, true},      // газ: без мертвої зони й експоненти
        {325, 2045, 3775, 25, 20, 64, false},   // рискання
    }};
    std::array<std::int32_t, hal::kAxisCount> filtered_{2048, 2050, 310, 2045};
    std::array<std::uint8_t, hal::kAxisCount> badSamples_{};
    std::uint8_t aux_{128};
    std::uint8_t auxDivider_{};
};

}   // namespace console
