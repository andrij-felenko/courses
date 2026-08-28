/* Приклад мінімального стробування GPIO на чистому C */
#include "stm32f4xx.h"

#define DEBUG_PIN_MASK (1U << 5) /* Порт GPIOB, пін 5 */

static inline void debug_pin_set_high(void) {
    GPIOB->BSRR = DEBUG_PIN_MASK; /* 1 такт: встановлення логічної 1 */
}

static inline void debug_pin_set_low(void) {
    GPIOB->BSRR = (DEBUG_PIN_MASK << 16); /* 1 такт: скидання в логічний 0 */
}

void TIM2_IRQHandler(void) {
    debug_pin_set_high(); /* Підйом фронту для осцилографа */

    /* Досліджуваний критичний код: наприклад, розрахунок фільтра */
    execute_control_loop_iteration();

    debug_pin_set_low();  /* Спад фронту: ширина імпульсу показує час */
    
    TIM2->SR = ~TIM_SR_UIF; /* Квитування переривання */
}
