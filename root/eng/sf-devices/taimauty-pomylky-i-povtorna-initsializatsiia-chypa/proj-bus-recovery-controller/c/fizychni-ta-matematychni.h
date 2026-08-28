#ifndef DWT_TIMEOUT_H
#define DWT_TIMEOUT_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef struct {
    uint32_t start_cycles;
    uint32_t duration_cycles;
} dwt_timer_t;

// Ініціалізація лічильника DWT
static inline void dwt_timer_global_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// Запуск таймера на задану кількість мікросекунд
static inline void dwt_timer_start_us(dwt_timer_t *timer, uint32_t duration_us) {
    timer->start_cycles = DWT->CYCCNT;
    timer->duration_cycles = (uint32_t)(((uint64_t)duration_us * SystemCoreClock) / 1000000ULL);
}

// Запуск таймера на задану кількість мілісекунд
static inline void dwt_timer_start_ms(dwt_timer_t *timer, uint32_t duration_ms) {
    timer->start_cycles = DWT->CYCCNT;
    timer->duration_cycles = (uint32_t)(((uint64_t)duration_ms * SystemCoreClock) / 1000ULL);
}

// Перевірка завершення таймауту за модулем 2^32
static inline bool dwt_timer_is_expired(const dwt_timer_t *timer) {
    uint32_t elapsed = (uint32_t)(DWT->CYCCNT - timer->start_cycles);
    return elapsed >= timer->duration_cycles;
}

// Блокуюча мікросекундна затримка
static inline void dwt_delay_us(uint32_t us) {
    dwt_timer_t t;
    dwt_timer_start_us(&t, us);
    while (!dwt_timer_is_expired(&t));
}

// Блокуюча мілісекундна затримка
static inline void dwt_delay_ms(uint32_t ms) {
    for (uint32_t i = 0; i < ms; i++) {
        dwt_delay_us(1000);
    }
}

// Очікування прапорця в регістрі з таймаутом
static inline int dwt_wait_register_bit(volatile uint32_t *reg, uint32_t mask, bool expected_state, uint32_t timeout_us) {
    dwt_timer_t timer;
    dwt_timer_start_us(&timer, timeout_us);

    while (1) {
        bool current_state = (*reg & mask) != 0;
        if (current_state == expected_state) {
            return 0; // Успіх
        }
        if (dwt_timer_is_expired(&timer)) {
            return -1; // Помилка таймауту
        }
    }
}

#endif // DWT_TIMEOUT_H
