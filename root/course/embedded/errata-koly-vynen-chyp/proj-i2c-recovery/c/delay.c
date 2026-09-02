#include "delay.h"

#include "stm32f10x.h"

static uint32_t s_cycles_per_us = 72U;
static uint8_t  s_dwt_alive = 0U;

void delay_init(void) {
    SystemCoreClockUpdate();
    s_cycles_per_us = SystemCoreClock / 1000000U;
    if (s_cycles_per_us == 0U) {
        s_cycles_per_us = 1U;
    }

    /* Без TRCENA блок трасування знеструмлений і CYCCNT не рахує взагалі */
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0U;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    /* На частині кристалів DWT лишається мертвим, поки не під'єднано
       налагоджувач. Перевіряємо це один раз, а не зависаємо в delay_us
       назавжди, чекаючи на лічильник, який ніколи не зрушить. */
    {
        const uint32_t before = DWT->CYCCNT;
        volatile int spin;
        for (spin = 0; spin < 8; ++spin) {
        }
        s_dwt_alive = (DWT->CYCCNT != before) ? 1U : 0U;
    }
}

void delay_us(uint32_t us) {
    if (s_dwt_alive) {
        const uint32_t start = DWT->CYCCNT;
        const uint32_t ticks = us * s_cycles_per_us;
        /* Різниця беззнакових лишається правильною і на обгортанні лічильника
           (при 72 МГц воно трапляється кожні ~59 секунд) */
        while ((DWT->CYCCNT - start) < ticks) {
        }
        return;
    }

    /* Запасний шлях: тіло циклу на Cortex-M3 коштує близько трьох тактів.
       Пауза виходить довшою за замовлену — для відновлення шини це безпечно. */
    {
        volatile uint32_t loops = us * (s_cycles_per_us / 3U + 1U);
        while (loops-- > 0U) {
            __NOP();
        }
    }
}
