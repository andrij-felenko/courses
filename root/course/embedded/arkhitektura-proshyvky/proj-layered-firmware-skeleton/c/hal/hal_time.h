// hal/hal_time.h — джерело часу. Без нього шар HAL не вміє обмежити очікування
// прапорця, а служба живлення — витримати паузу між вимкненням і вмиканням давачів.
#ifndef HAL_TIME_H
#define HAL_TIME_H

#include <stdint.h>
#include <stdbool.h>

typedef struct hal_time_ops {
    uint32_t (*now_ms)(void* context);              // Монотонний лічильник мілісекунд
    void (*delay_ms)(void* context, uint32_t ms);   // Активне або сонне очікування
} hal_time_ops_t;

typedef struct hal_time {
    const hal_time_ops_t* ops;
    void* context;
} hal_time_t;

static inline uint32_t hal_time_now_ms(const hal_time_t* t)
{
    if (!t || !t->ops || !t->ops->now_ms) return 0u;
    return t->ops->now_ms(t->context);
}

static inline void hal_time_delay_ms(const hal_time_t* t, uint32_t ms)
{
    if (!t || !t->ops || !t->ops->delay_ms) return;
    t->ops->delay_ms(t->context, ms);
}

// Різниця в мілісекундах, стійка до переповнення 32-бітного лічильника
// (через 49.7 доби безперервної роботи он воно й трапляється).
static inline uint32_t hal_time_elapsed_ms(const hal_time_t* t, uint32_t since_ms)
{
    return (uint32_t)(hal_time_now_ms(t) - since_ms);
}

#endif  // HAL_TIME_H
