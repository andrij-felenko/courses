#ifndef NVIC_PRIORITY_H
#define NVIC_PRIORITY_H

/*
 * Кодування пріоритету для BASEPRI та конфігурація групування NVIC.
 *
 * «Людський» пріоритет (0..15 на STM32) і «апаратний» байт пріоритету — це
 * різні числа. NVIC_SetPriority() зсуває значення сам, а BASEPRI — ні:
 * у нього кладуть уже готовий байт, вирівняний за лівим краєм.
 */

#include "stm32f4xx.h"   /* тягне core_cm4.h: __NVIC_PRIO_BITS, SCB, NVIC_* */

#include <stdbool.h>
#include <stdint.h>

#ifndef __NVIC_PRIO_BITS
#error "Заголовок пристрою не оголосив __NVIC_PRIO_BITS"
#endif

/* Скільки молодших бітів байта пріоритету апаратно зафіксовано в нуль. */
#define NVIC_PRIO_SHIFT   (8U - (uint32_t)__NVIC_PRIO_BITS)
#define NVIC_PRIO_LEVELS  (1U << (uint32_t)__NVIC_PRIO_BITS)
#define NVIC_PRIO_LOWEST  (NVIC_PRIO_LEVELS - 1U)

/* Пріоритет -> значення для запису в BASEPRI. */
#define NVIC_BASEPRI(prio) \
    ((uint32_t)(((uint32_t)(prio) << NVIC_PRIO_SHIFT) & 0xFFU))

#if (__NVIC_PRIO_BITS == 4)
_Static_assert(NVIC_BASEPRI(5U) == 0x50U,
               "Пріоритет 5 при 4 бітах NVIC — це байт 0x50, а не 0x05");
_Static_assert(NVIC_BASEPRI(15U) == 0xF0U, "Найнижчий пріоритет — 0xF0");
#endif

/*
 * Пастка, на якій ловляться всі: BASEPRI == 0 означає «фільтр вимкнено».
 * Тому пріоритет 0 закодувати НЕМОЖЛИВО — переривання найвищого рівня
 * порогом не маскується взагалі, для нього існує лише PRIMASK.
 * Функція повертає 0 як ознаку «цей пріоритет порогом не закривається».
 */
static inline uint32_t nvic_basepri_from_priority(uint32_t priority)
{
    if ((priority == 0U) || (priority > NVIC_PRIO_LOWEST)) {
        return 0U;
    }
    return NVIC_BASEPRI(priority);
}

/* Зворотне перетворення — знадобиться під час читання регістра в зневаднику. */
static inline uint32_t nvic_priority_from_basepri(uint32_t basepri)
{
    return (basepri & 0xFFU) >> NVIC_PRIO_SHIFT;
}

/*
 * Скільки бітів пріоритету зараз віддано під витіснення (Preempt).
 * PRIGROUP визначає двійкову крапку: preempt = 7 - PRIGROUP, обрізане
 * зверху кількістю реалізованих бітів.
 */
static inline uint32_t nvic_preempt_bits(void)
{
    const uint32_t prigroup = NVIC_GetPriorityGrouping();
    const uint32_t preempt = (prigroup >= 7U) ? 0U : (7U - prigroup);
    return (preempt > (uint32_t)__NVIC_PRIO_BITS) ? (uint32_t)__NVIC_PRIO_BITS
                                                  : preempt;
}

/*
 * «Пласке» групування: усі реалізовані біти — витісняючі, підпріоритету немає.
 * BASEPRI ігнорує PRIGROUP і порівнює повний байт, тому будь-яке змішане
 * групування робить поведінку порогу неочевидною для читача коду (і саме
 * цього вимагає configASSERT() у FreeRTOS).
 */
static inline void nvic_priority_use_flat_grouping(void)
{
    NVIC_SetPriorityGrouping(7U - (uint32_t)__NVIC_PRIO_BITS);
}

static inline bool nvic_priority_grouping_is_flat(void)
{
    return nvic_preempt_bits() == (uint32_t)__NVIC_PRIO_BITS;
}

#endif /* NVIC_PRIORITY_H */
