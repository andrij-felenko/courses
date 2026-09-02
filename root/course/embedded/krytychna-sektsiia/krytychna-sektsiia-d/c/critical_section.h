/*
 * Критична секція, зібрана за єдиним правилом: зберегти маску на вході й
 * повернути САМЕ ЇЇ на виході. Вкладеність будь-якої глибини безпечна.
 */
#ifndef CRITICAL_SECTION_H
#define CRITICAL_SECTION_H

#include "cortexm.h"

/* Збережений стан маски. Його не можна тлумачити як «переривання були
 * увімкнені» — це непрозоре значення, яке просто повертають назад. */
typedef uint32_t irq_state_t;

static inline irq_state_t irq_lock(void)
{
    const irq_state_t saved = __get_PRIMASK();
    __disable_irq();
    COMPILER_BARRIER();
    return saved;
}

static inline void irq_unlock(irq_state_t saved)
{
    COMPILER_BARRIER();
    __set_PRIMASK(saved);
}

#if CORTEXM_HAS_BASEPRI
/* Поріг маскування: усе з пріоритетом 5 і нижче блокується, а 0..4 (аварія за
 * струмом, ШІМ, енкодер) працює й усередині секції. Пріоритет NVIC живе в
 * СТАРШИХ бітах байта, тому число зсунуте. */
#define MAX_SYSCALL_PRIORITY ((uint32_t)(5U << (8U - __NVIC_PRIO_BITS)))

static inline irq_state_t basepri_lock(void)
{
    const irq_state_t saved = __get_BASEPRI();
    __set_BASEPRI_MAX(MAX_SYSCALL_PRIORITY);
    COMPILER_BARRIER();
    return saved;
}

static inline void basepri_unlock(irq_state_t saved)
{
    COMPILER_BARRIER();
    __set_BASEPRI(saved);
}
#endif /* CORTEXM_HAS_BASEPRI */

#endif /* CRITICAL_SECTION_H */
