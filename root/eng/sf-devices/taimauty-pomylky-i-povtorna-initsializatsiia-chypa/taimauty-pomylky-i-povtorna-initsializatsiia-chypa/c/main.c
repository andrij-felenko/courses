#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

void dwt_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

bool wait_flag_timeout(volatile uint32_t *reg, uint32_t mask, bool wait_set, uint32_t timeout_us) {
    uint32_t start_cycles = DWT->CYCCNT;
    uint32_t max_cycles = timeout_us * (SystemCoreClock / 1000000U);

    while (true) {
        bool condition = (*reg & mask) != 0;
        if (condition == wait_set) {
            return true;
        }
        if ((uint32_t)(DWT->CYCCNT - start_cycles) >= max_cycles) {
            return false; // Вичерпано ліміт часу
        }
    }
}
