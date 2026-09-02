/*
 * Атомарні операції без вимкнення переривань: монітор ексклюзивності ядра й
 * пара LDREX/STREX. Жоден обробник не дістає ані такту зайвої затримки —
 * замість блокування фон просто повторює спробу.
 */
#ifndef ATOMIC_ARM_H
#define ATOMIC_ARM_H

#include "critical_section.h"

#if CORTEXM_HAS_EXCLUSIVE

/* Повертає значення ДО додавання — як atomic_fetch_add зі stdatomic.h. */
static inline uint32_t atomic_fetch_add_u32(volatile uint32_t *ptr, uint32_t value)
{
    uint32_t old_value;
    uint32_t store_failed;

    do {
        old_value = __LDREXW(ptr);                       /* читаємо й зводимо монітор */
        store_failed = __STREXW(old_value + value, ptr); /* 0 — записали, 1 — монітор збито */
    } while (store_failed != 0U);                        /* переривання втрутилося — ще раз */

    return old_value;
}

static inline uint32_t atomic_fetch_or_u32(volatile uint32_t *ptr, uint32_t bits)
{
    uint32_t old_value;
    uint32_t store_failed;

    do {
        old_value = __LDREXW(ptr);
        store_failed = __STREXW(old_value | bits, ptr);
    } while (store_failed != 0U);

    return old_value;
}

/* Обмін за умовою. Якщо значення вже не те, монітор ОБОВʼЯЗКОВО знімаємо
 * вручну: покинутий у стані Exclusive, він псує наступну транзакцію. */
static inline int atomic_compare_exchange_u32(volatile uint32_t *ptr, uint32_t expected,
                                              uint32_t desired)
{
    const uint32_t actual = __LDREXW(ptr);

    if (actual != expected) {
        __CLREX();
        return 0;
    }
    return __STREXW(desired, ptr) == 0U;
}

#else /* ARMv6-M: монітора ексклюзивності немає */

/* На Cortex-M0/M0+ ті самі операції доводиться робити старим способом — під
 * повним вимкненням переривань. Інтерфейс лишається той самий, ціна — інша. */
static inline uint32_t atomic_fetch_add_u32(volatile uint32_t *ptr, uint32_t value)
{
    const irq_state_t saved = irq_lock();
    const uint32_t old_value = *ptr;
    *ptr = old_value + value;
    irq_unlock(saved);
    return old_value;
}

static inline uint32_t atomic_fetch_or_u32(volatile uint32_t *ptr, uint32_t bits)
{
    const irq_state_t saved = irq_lock();
    const uint32_t old_value = *ptr;
    *ptr = old_value | bits;
    irq_unlock(saved);
    return old_value;
}

static inline int atomic_compare_exchange_u32(volatile uint32_t *ptr, uint32_t expected,
                                              uint32_t desired)
{
    const irq_state_t saved = irq_lock();
    const int matched = (*ptr == expected);
    if (matched) {
        *ptr = desired;
    }
    irq_unlock(saved);
    return matched;
}

#endif /* CORTEXM_HAS_EXCLUSIVE */

#endif /* ATOMIC_ARM_H */
