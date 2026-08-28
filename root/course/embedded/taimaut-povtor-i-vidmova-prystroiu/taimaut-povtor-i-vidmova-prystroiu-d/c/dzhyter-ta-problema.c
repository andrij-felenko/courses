#include <stdint.h>
#include <stdbool.h>

/* Простий вбудований генератор псевдовипадкових чисел (LCG) */
static uint32_t fast_rand(uint32_t *seed) {
    *seed = (*seed * 1664525UL + 1013904223UL);
    return *seed;
}

typedef struct {
    uint8_t  max_attempts;    /* Максимальна кількість спроб (зазвичай 3–5) */
    uint32_t base_delay_us;   /* Базова затримка у мікросекундах */
    uint32_t max_delay_us;    /* Максимальна затримка */
    uint32_t rand_seed;       /* Стан генератора випадкових чисел */
} retry_policy_t;

/* Обчислення паузи для поточної спроби k (від 1 до max_attempts) */
uint32_t retry_calculate_delay_us(retry_policy_t *p, uint8_t attempt) {
    if (attempt == 0) return 0;
    
    /* 1 << (attempt - 1) реалізує 2^(k-1) */
    uint32_t shift = (attempt > 10) ? 10 : (attempt - 1);
    uint32_t exp_delay = p->base_delay_us * (1UL << shift);
    
    if (exp_delay > p->max_delay_us) {
        exp_delay = p->max_delay_us;
    }
    
    /* Додаємо джитер: випадкове значення в інтервалі [0.5 * exp_delay ... exp_delay] */
    uint32_t half = exp_delay / 2;
    uint32_t jitter = fast_rand(&p->rand_seed) % (half + 1);
    
    return half + jitter;
}
