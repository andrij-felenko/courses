/* dwt_timer.h - Базовий драйвер лічильника DWT на C */
#ifndef DWT_TIMER_H
#define DWT_TIMER_H

#include <stdint.h>
#include <stdbool.h>

#define CORE_DEBUG_DEMCR        (*(volatile uint32_t*)0xE000EDFCU)
#define CORE_DEBUG_DEMCR_TRCENA (1U << 24)

#define DWT_CTRL                (*(volatile uint32_t*)0xE0001000U)
#define DWT_CTRL_CYCCNTENA      (1U << 0)
#define DWT_CYCCNT              (*(volatile uint32_t*)0xE0001004U)

static inline bool dwt_init(void) {
    /* 1. Дозвіл трасування в блоці CoreDebug */
    CORE_DEBUG_DEMCR |= CORE_DEBUG_DEMCR_TRCENA;
    
    /* 2. Скидання лічильника */
    DWT_CYCCNT = 0U;
    
    /* 3. Активація лічильника */
    DWT_CTRL |= DWT_CTRL_CYCCNTENA;
    
    /* Перевірка, чи запустився лічильник */
    return (DWT_CTRL & DWT_CTRL_CYCCNTENA) != 0U;
}

static inline uint32_t dwt_get_cycles(void) {
    return DWT_CYCCNT;
}

static inline uint32_t dwt_delta_cycles(uint32_t start, uint32_t stop) {
    /* Беззнакова модульна арифметика коректно обробляє переповнення 32 біт */
    return stop - start;
}

static inline uint32_t dwt_cycles_to_us(uint32_t cycles, uint32_t cpu_freq_hz) {
    return (uint32_t)(((uint64_t)cycles * 1000000ULL) / cpu_freq_hz);
}

#endif /* DWT_TIMER_H */
