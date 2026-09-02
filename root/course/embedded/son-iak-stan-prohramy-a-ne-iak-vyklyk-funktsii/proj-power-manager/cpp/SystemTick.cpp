#include "SystemTick.hpp"
#include "stm32l4xx.h"

namespace emb::hal {

using std::chrono::milliseconds;

void SystemTick::init(std::uint32_t sysclkHz) noexcept
{
    s_ms = 0;
    SysTick_Config(sysclkHz / 1000u);
}

milliseconds SystemTick::now() noexcept
{
    return milliseconds{s_ms};
}

void SystemTick::suspend() noexcept
{
    SysTick->CTRL &= ~(SysTick_CTRL_TICKINT_Msk | SysTick_CTRL_ENABLE_Msk);
    // Прапорець, що встиг звестися до вимкнення, інакше вистрелить після сну.
    SCB->ICSR = SCB_ICSR_PENDSTCLR_Msk;
}

void SystemTick::resume(milliseconds slept) noexcept
{
    s_ms += static_cast<std::uint32_t>(slept.count());
    SysTick->VAL   = 0;
    SysTick->CTRL |= SysTick_CTRL_TICKINT_Msk | SysTick_CTRL_ENABLE_Msk;
}

milliseconds SystemTick::until(milliseconds deadline) noexcept
{
    const auto left = static_cast<std::int32_t>(
        static_cast<std::uint32_t>(deadline.count()) - s_ms);
    return milliseconds{left > 0 ? left : 0};
}

} // namespace emb::hal

extern "C" void SysTick_Handler(void)
{
    emb::hal::SystemTick::onTick();
}
