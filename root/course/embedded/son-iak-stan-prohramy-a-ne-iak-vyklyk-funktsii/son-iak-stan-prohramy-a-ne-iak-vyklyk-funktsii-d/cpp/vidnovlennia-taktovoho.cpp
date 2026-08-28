/* Відновлення тактування після виходу з режиму STOP (C++20) */
#include <cstdint>

namespace emb::sys {

struct ClockTree {
    static void restoreAfterStop() noexcept {
        // 1. Запуск зовнішнього кварцового резонатора HSE
        // RCC->CR |= RCC_CR_HSEON;
        // while (!(RCC->CR & RCC_CR_HSERDY)) {}

        // 2. Запуск помножувача частоти PLL
        // RCC->CR |= RCC_CR_PLLON;
        // while (!(RCC->CR & RCC_CR_PLLRDY)) {}

        // 3. Перемикання системного джерела тактування SYSCLK на вихід PLL
        // RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_PLL;
        // while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL) {}
    }
};

} // namespace emb::sys
