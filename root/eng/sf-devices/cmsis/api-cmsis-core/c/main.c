#include "stm32f4xx.h"          /* тягне core_cm4.h і cmsis_compiler.h */

static volatile uint64_t ticks_ms;      /* 64 біти — читається двома командами */
static volatile uint32_t pinged;

void SysTick_Handler(void)              /* ім'я з таблиці векторів пристрою */
{
    ticks_ms++;                         /* єдиний, хто пише */
}

void TIM2_IRQHandler(void)              /* запит знімає саме входження у виняток */
{
    pinged++;
}

static uint64_t uptime_ms(void)
{
    uint32_t primask = __get_PRIMASK(); /* як було до нас */
    __disable_irq();
    uint64_t t = ticks_ms;              /* два читання поспіль — без розриву */
    __set_PRIMASK(primask);             /* відновити, а не ввімкнути наосліп */
    return t;
}

int main(void)
{
    SystemCoreClockUpdate();            /* після налаштування тактування */

    if (SysTick_Config(SystemCoreClock / 1000U) != 0U) {
        for (;;) { __BKPT(0); }         /* дільник не вліз у 24 біти */
    }

    NVIC_SetPriority(TIM2_IRQn, 3U);    /* логічний рівень; зсув — усередині */
    NVIC_EnableIRQ(TIM2_IRQn);
    NVIC_SetPendingIRQ(TIM2_IRQn);      /* сам таймер не заведено — будимо лінію програмно */

    for (;;) {
        if (uptime_ms() >= 60000U) {
            NVIC_SystemReset();         /* не повертається */
        }
        __WFI();                        /* спати до наступного переривання */
    }
}
