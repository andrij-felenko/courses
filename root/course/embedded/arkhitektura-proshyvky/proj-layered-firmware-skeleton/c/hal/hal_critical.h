// hal/hal_critical.h — коротка критична секція для структур, до яких дотягуються
// і головний цикл, і обробники переривань. Стан PRIMASK зберігається й відновлюється,
// тому вкладені секції не вмикають переривання достроково.
#ifndef HAL_CRITICAL_H
#define HAL_CRITICAL_H

#include <stdint.h>

typedef uint32_t hal_critical_state_t;

#if defined(__ARM_ARCH) && defined(__GNUC__)

static inline hal_critical_state_t hal_critical_enter(void)
{
    hal_critical_state_t primask;
    __asm__ volatile("mrs %0, primask" : "=r"(primask)::"memory");
    __asm__ volatile("cpsid i" ::: "memory");
    return primask;
}

static inline void hal_critical_exit(hal_critical_state_t state)
{
    // Переривання вмикаємо, лише якщо на вході вони справді були ввімкнені.
    if ((state & 1u) == 0u) {
        __asm__ volatile("cpsie i" ::: "memory");
    }
}

#else  // Хостова збірка: переривань немає, потрібен лише барʼєр компілятора.

static inline hal_critical_state_t hal_critical_enter(void)
{
#if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile("" ::: "memory");
#endif
    return 0u;
}

static inline void hal_critical_exit(hal_critical_state_t state)
{
    (void)state;
#if defined(__GNUC__) || defined(__clang__)
    __asm__ volatile("" ::: "memory");
#endif
}

#endif

#endif  // HAL_CRITICAL_H
