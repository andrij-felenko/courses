#include "stm32f10x.h"

void release_swd_pins_to_gpio(void) {
    // Вмикаємо тактування альтернативних функцій
    RCC->APB2ENR |= RCC_APB2ENR_AFIOEN;
    
    // SWJ_CFG = 0b100: Повне вимкнення JTAG-DP та SW-DP
    // Усі виводи (PA13, PA14, PA15, PB3, PB4) звільняються під GPIO
    AFIO->MAPR = (AFIO->MAPR & ~AFIO_MAPR_SWJ_CFG) | AFIO_MAPR_SWJ_CFG_DISABLE;
}
