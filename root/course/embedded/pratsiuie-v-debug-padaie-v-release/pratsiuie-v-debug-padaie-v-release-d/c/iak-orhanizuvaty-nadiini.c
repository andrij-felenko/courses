#include "stm32f4xx.h"

// Варіант 1: Апаратний лічильник DWT (Data Watchpoint and Trace)
void dwt_delay_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void dwt_delay_us(uint32_t us) {
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = us * (SystemCoreClock / 1000000);
    while ((DWT->CYCCNT - start) < ticks) {
        // DWT->CYCCNT оголошений як volatile uint32_t, тому не кешується!
    }
}

// Варіант 2: Запобігання видаленню циклу через асемблерний бар'єр
void busy_delay_cycles(uint32_t count) {
    while (count--) {
        __asm__ volatile ("nop"); // Інструкція NOP з прапорцем volatile
    }
}
