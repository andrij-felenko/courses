#pragma once

#include "pipeline/ema_filter.hpp"
#include "pipeline/pid_controller.hpp"

#include <algorithm>
#include <cstdint>

namespace pipeline {

inline constexpr std::uint32_t kAdcMaxCode = 4095;
inline constexpr std::uint32_t kAdcVrefMv = 3300;
inline constexpr std::uint16_t kPwmMaxDuty = 65535;

/// Окремий тип для напруги: мілівольти й коди АЦП — різні величини, і
/// переплутати їх у виклику тепер не вийде.
struct Millivolts {
    std::int32_t value{0};

    friend constexpr bool operator==(Millivolts, Millivolts) noexcept = default;
};

/// Код АЦП у мілівольти. Код понад 4095 (збій DMA, чужий запис у комірку)
/// обрізаємо: у формулу має заходити лише те, що АЦП здатний видати.
constexpr Millivolts to_millivolts(std::uint16_t raw_code) noexcept
{
    const std::uint32_t code = std::min<std::uint32_t>(raw_code, kAdcMaxCode);
    // 4095 * 3300 = 13 513 500 — вміщується в 32 біти без переходу на 64.
    return Millivolts{static_cast<std::int32_t>(code * kAdcVrefMv / kAdcMaxCode)};
}

/// Наскрізний конвеєр: код АЦП -> мілівольти -> фільтр -> регулятор -> ШІМ.
/// Уся пам'ять — усередині об'єкта, жодного динамічного виділення.
template <std::uint8_t Shift>
class SignalPipeline {
public:
    constexpr SignalPipeline(Gains gains, Limits limits) noexcept : pid_{gains, limits} {}

    constexpr std::uint16_t step(std::uint16_t raw_code, Millivolts target) noexcept
    {
        const Millivolts measured{filter_.update(to_millivolts(raw_code).value)};
        const std::int32_t control = pid_.update(target.value, measured.value);

        // Межі регулятора вже лежать у діапазоні ШІМ, але в регістр іде
        // значення, а не сподівання: обрізаємо ще раз.
        last_measured_ = measured;
        last_duty_ = static_cast<std::uint16_t>(
            std::clamp<std::int32_t>(control, 0, kPwmMaxDuty));
        return last_duty_;
    }

    [[nodiscard]] constexpr Millivolts measured() const noexcept { return last_measured_; }
    [[nodiscard]] constexpr std::uint16_t duty() const noexcept { return last_duty_; }

    constexpr void reset() noexcept
    {
        filter_.reset();
        pid_.reset();
        last_measured_ = Millivolts{};
        last_duty_ = 0;
    }

private:
    EmaFilter<Shift> filter_{};
    PidController pid_;
    Millivolts last_measured_{};
    std::uint16_t last_duty_{0};
};

} // namespace pipeline
