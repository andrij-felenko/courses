// Апаратна частина стенда: тактування, трифазний ШІМ і АЦП, який запускає
// сам таймер. Помилки пуску повертаються значенням, а не кодом -1:
// пропустити std::expected мовчки компілятор не дасть.
#pragma once

#include <cstdint>
#include <expected>

#include "foc.hpp"
#include "stm32f4xx.h"

namespace inverter {

inline constexpr std::uint32_t kSysclkMhz = 168U;
inline constexpr std::uint32_t kPwmHz = 20000U;
// Центрований лічильник проходить період двічі: 168e6 / (2 * 4200) = 20 кГц.
inline constexpr std::uint32_t kPwmArr = 4200U;
// Шунт 10 мОм, підсилювач x20, опора 3.3 В, 12 біт.
inline constexpr float kAdcToAmp = 3.3f / 4096.0f / (0.01f * 20.0f);
// Дедлайн контуру — половина періоду ШІМ.
inline constexpr std::uint32_t kDeadlineCycles = kSysclkMhz * 25U;

enum class BringUpError { HseTimeout, PllTimeout, ClockSwitch };

struct RawCurrents {
    std::uint32_t a{0};
    std::uint32_t b{0};
};

[[nodiscard]] std::expected<void, BringUpError> bring_up() noexcept;

[[nodiscard]] constexpr const char* describe(BringUpError e) noexcept
{
    switch (e) {
        case BringUpError::HseTimeout: return "кварц HSE не завівся";
        case BringUpError::PllTimeout: return "PLL не захопив частоту";
        case BringUpError::ClockSwitch: return "ядро не перейшло на PLL";
    }
    return "невідома помилка пуску";
}

inline void set_duties(const foc::Duties& d) noexcept
{
    // Значення вже затиснуті в [0.02; 0.98]; регістри з попереднім
    // завантаженням наберуть чинності разом, на події оновлення.
    const float arr = static_cast<float>(kPwmArr);
    TIM1->CCR1 = static_cast<std::uint32_t>(d.a * arr);
    TIM1->CCR2 = static_cast<std::uint32_t>(d.b * arr);
    TIM1->CCR3 = static_cast<std::uint32_t>(d.c * arr);
}

[[nodiscard]] inline RawCurrents raw_currents() noexcept
{
    return RawCurrents{ADC1->JDR1, ADC1->JDR2};
}

inline void ack_conversion() noexcept
{
    ADC1->SR = ~static_cast<std::uint32_t>(ADC_SR_JEOC | ADC_SR_JSTRT);
}

inline void trip() noexcept
{
    TIM1->BDTR &= ~TIM_BDTR_MOE;   // аварійно зняти напругу з мосту
}

}  // namespace inverter
