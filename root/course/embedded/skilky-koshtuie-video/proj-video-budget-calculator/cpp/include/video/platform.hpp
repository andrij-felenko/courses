#pragma once

#include <span>
#include <string_view>

#include "video/budget.hpp"

namespace video {

// Чи вміщується порахований бюджет у конкретне залізо. Пропускна здатність —
// ПРАКТИЧНА (з накладними витратами контролера й refresh), а не піковий
// добуток частоти на розрядність із рекламного аркуша.
struct Platform {
    std::string_view name;
    double busMBps;  // практична пропускна здатність шини пам'яті
    double ramMB;    // пам'ять, доступна під кадрові буфери
};

enum class Fit {
    Ok,            // трафік у межах безпечної частки шини
    Risky,         // понад 60 % шини: черги голодують на піках
    BusOverload,   // трафік більший за саму шину
    NotEnoughRam   // пул буферів не вміщується взагалі
};

struct FitReport {
    Fit    verdict{Fit::Ok};
    double busLoadPercent{};
    double ramLoadPercent{};
};

// Понад цю частку шини кадрові FIFO переповнюються на піках трафіку: запас
// потрібен під refresh, конкуренцію з CPU і сплески кодека.
inline constexpr double kBusSafePercent = 60.0;

[[nodiscard]] std::span<const Platform> catalogue() noexcept;
[[nodiscard]] FitReport check(const Platform& platform, const Budget& budget) noexcept;
[[nodiscard]] std::string_view describe(Fit fit) noexcept;

}  // namespace video
