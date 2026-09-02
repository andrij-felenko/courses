#pragma once

#include "stm32f10x.h"

#include <chrono>
#include <cstdint>

namespace bsp {

using namespace std::chrono_literals;

/* Джерело часу — лічильник тактів ядра DWT: не займає жодного таймера й не
   залежить від того, скільки інструкцій компілятор залишив у порожньому циклі. */
inline std::uint32_t cycles_per_us = 72U;
inline bool cycle_counter_alive = false;

inline void init_timing() noexcept {
    SystemCoreClockUpdate();
    cycles_per_us = SystemCoreClock / 1'000'000U;
    if (cycles_per_us == 0U) {
        cycles_per_us = 1U;
    }

    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   /* без цього блок знеструмлений */
    DWT->CYCCNT = 0U;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    /* На частині кристалів DWT мовчить, поки не під'єднано налагоджувач.
       Перевіряємо один раз тут, щоб потім не зависнути назавжди в delay(). */
    const std::uint32_t before = DWT->CYCCNT;
    for (volatile int spin = 0; spin < 8; ++spin) {
    }
    cycle_counter_alive = (DWT->CYCCNT != before);
}

inline void delay(std::chrono::microseconds duration) noexcept {
    const auto us = duration.count() > 0 ? static_cast<std::uint32_t>(duration.count()) : 0U;

    if (cycle_counter_alive) {
        const std::uint32_t start = DWT->CYCCNT;
        const std::uint32_t ticks = us * cycles_per_us;
        /* Різниця беззнакових правильна й на обгортанні лічильника (~59 с при 72 МГц) */
        while ((DWT->CYCCNT - start) < ticks) {
        }
        return;
    }

    /* Запасний шлях: ітерація коштує близько трьох тактів. Пауза виходить довшою
       за замовлену, і для відновлення шини це нешкідливо. */
    volatile std::uint32_t loops = us * (cycles_per_us / 3U + 1U);
    while (loops-- > 0U) {
        __NOP();
    }
}

/* Очікування умови з межею часу — замість трьох однакових циклів із лічильником
   у кожній процедурі. Повертає false, якщо умова так і не настала. */
template <class Ready>
[[nodiscard]] inline bool wait_until(Ready&& ready, std::chrono::microseconds timeout) noexcept {
    for (auto waited = 0us; waited <= timeout; waited += 1us) {
        if (ready()) {
            return true;
        }
        delay(1us);
    }
    return false;
}

} // namespace bsp
