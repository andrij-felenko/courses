#include "isr/timer.hpp"

#include "isr/critical_section.hpp"

#include "stm32f4xx.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_tim.h"

namespace isr {

std::atomic<std::uint32_t> Timer::ticks_{0};
std::atomic<std::uint32_t> Timer::wraps_{0};
std::atomic<std::uint32_t> Timer::spurious_{0};

namespace {

// Корисна дія: два записи в регістри й нічого більше.
void do_fast_action() noexcept
{
    LL_GPIO_TogglePin(GPIOD, LL_GPIO_PIN_12);
}

} // namespace

void Timer::handle_irq() noexcept
{
    if (!LL_TIM_IsActiveFlag_UPDATE(TIM2)) {
        // Прапорця немає, а ми тут. Це помилковий повторний вхід:
        // попереднє квитування ще їхало шиною APB, коли ядро вже вийшло
        // з обробника, і NVIC побачив лінію активною.
        spurious_.fetch_add(1, std::memory_order_relaxed);
        return;
    }

    // 1. Квитування ПЕРШИМ кроком — щоб запис устиг доїхати, поки
    //    виконується корисна дія.
    LL_TIM_ClearFlag_UPDATE(TIM2);

    // 2. Власне робота.
    const std::uint32_t next = ticks_.fetch_add(1, std::memory_order_relaxed) + 1;
    if (next == 0) {
        wraps_.fetch_add(1, std::memory_order_relaxed);
    }
    do_fast_action();

    // 3. Страховка: DSB не дає ядру дійти до BX LR, доки буфер запису
    //    не спорожнів. Без неї корисна дія з двох інструкцій ефекту
    //    затримки не дає, і повторний вхід повертається.
    __DSB();
}

std::uint64_t Timer::ms_since_boot() noexcept
{
    // Пріоритет маскування дорівнює пріоритету TIM2: на час зняття пари
    // слів цей обробник не втрутиться, а аварійні лінії вище — втрутяться.
    const BasepriGuard guard{5};

    const std::uint32_t low = ticks_.load(std::memory_order_relaxed);
    const std::uint32_t high = wraps_.load(std::memory_order_relaxed);
    return (static_cast<std::uint64_t>(high) << 32) | low;
}

std::uint32_t Timer::spurious_entries() noexcept
{
    return spurious_.load(std::memory_order_relaxed);
}

} // namespace isr

extern "C" void TIM2_IRQHandler()
{
    isr::Timer::handle_irq();
}
