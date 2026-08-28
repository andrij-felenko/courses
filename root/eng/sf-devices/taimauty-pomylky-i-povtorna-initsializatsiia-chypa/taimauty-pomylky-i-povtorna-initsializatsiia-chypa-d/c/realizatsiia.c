#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef struct {
    uint32_t start_cycles;
    uint32_t timeout_cycles;
} timeout_dwt_t;

static inline void timeout_dwt_start(timeout_dwt_t *t, uint32_t timeout_us, uint32_t cpu_freq_hz) {
    t->start_cycles = DWT->CYCCNT;
    // Обчислення тактів із захистом від переповнення при множенні: (us * freq) / 1000000
    t->timeout_cycles = (uint32_t)(((uint64_t)timeout_us * cpu_freq_hz) / 1000000ULL);
}

static inline bool timeout_dwt_is_expired(const timeout_dwt_t *t) {
    uint32_t elapsed = (uint32_t)(DWT->CYCCNT - t->start_cycles);
    return elapsed >= t->timeout_cycles;
}

// Універсальна функція очікування стану бітової маски в регістрі
int bus_wait_register_mask(volatile uint32_t *reg, uint32_t mask, bool wait_for_set, uint32_t timeout_us) {
    timeout_dwt_t timer;
    timeout_dwt_start(&timer, timeout_us, SystemCoreClock);

    while (1) {
        bool bit_is_set = (*reg & mask) != 0;
        if (bit_is_set == wait_for_set) {
            return 0; // Успіх: умова виконана
        }
        if (timeout_dwt_is_expired(&timer)) {
            return -1; // Помилка: таймаут вичерпано
        }
    }
}
