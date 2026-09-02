#include "Mcu.hpp"

namespace emb::hal {
namespace {

// Тактування після STOP іде від MSI 4 МГц, таймбейсу ще немає —
// лишається рахувати оберти циклу.
constexpr std::uint32_t kSpins = 200'000;

[[nodiscard]] bool spinUntilSet(volatile std::uint32_t& reg, std::uint32_t mask) noexcept
{
    for (std::uint32_t i = 0; i < kSpins; ++i) {
        if ((reg & mask) != 0u) {
            return true;
        }
    }
    return false;
}

} // namespace

bool SystemClock::tryRestore() noexcept
{
    if ((RCC->CFGR & RCC_CFGR_SWS) == RCC_CFGR_SWS_PLL) {
        return true; // дерево не падало
    }

    // Затримку читання Flash піднімаємо до частоти, а не після неї.
    FLASH->ACR = (FLASH->ACR & ~FLASH_ACR_LATENCY) | FLASH_ACR_LATENCY_4WS;

    RCC->CR |= RCC_CR_HSEON;
    if (!spinUntilSet(RCC->CR, RCC_CR_HSERDY)) {
        RCC->CR &= ~RCC_CR_HSEON;
        return false;
    }

    // Коефіцієнти PLLCFGR переживають STOP разом із доменом VCORE.
    RCC->CR |= RCC_CR_PLLON;
    if (!spinUntilSet(RCC->CR, RCC_CR_PLLRDY)) {
        RCC->CR &= ~(RCC_CR_PLLON | RCC_CR_HSEON);
        return false;
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
    for (std::uint32_t i = 0; i < kSpins; ++i) {
        if ((RCC->CFGR & RCC_CFGR_SWS) == RCC_CFGR_SWS_PLL) {
            return true;
        }
    }
    return false;
}

ClockSource SystemClock::restoreAfterStop() noexcept
{
    if (tryRestore()) {
        return ClockSource::Pll;
    }
    ++s_faults;
    if (tryRestore()) {
        return ClockSource::Pll; // кварц інколи піднімається довше за розрахунок
    }

    // Периферія налаштована на 80 МГц, а шина йде від MSI 4 МГц: усі швидкості
    // обміну биті. Чесний перезапуск кращий за мовчазно спотворені дані.
    NVIC_SystemReset();
    return ClockSource::Msi; // недосяжно, але компілятор має бачити повернення
}

} // namespace emb::hal
