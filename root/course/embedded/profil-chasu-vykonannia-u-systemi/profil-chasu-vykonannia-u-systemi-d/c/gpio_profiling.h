/* gpio_profiling.h - Атомарне стробування виводів на C */
#ifndef GPIO_PROFILING_H
#define GPIO_PROFILING_H

#include <stdint.h>

/* Базові адреси порту GPIOB (приклад STM32F4) */
#define GPIOB_BSRR (*(volatile uint32_t*)0x40020418U)

#define PROF_PIN_ISR    (1U << 0) /* PB0: Індикатор виконання ISR */
#define PROF_PIN_PENDSV (1U << 1) /* PB1: Індикатор перемикання контексту */
#define PROF_PIN_TASK1  (1U << 2) /* PB2: Задача високого пріоритету */
#define PROF_PIN_TASK2  (1U << 3) /* PB3: Задача низького пріоритету */

static inline void prof_pin_high(uint32_t pin_mask) {
    GPIOB_BSRR = pin_mask; /* Встановлення логічної 1 у молодші 16 біт */
}

static inline void prof_pin_low(uint32_t pin_mask) {
    GPIOB_BSRR = (pin_mask << 16); /* Скидання в 0 через старші 16 біт */
}

#endif /* GPIO_PROFILING_H */
