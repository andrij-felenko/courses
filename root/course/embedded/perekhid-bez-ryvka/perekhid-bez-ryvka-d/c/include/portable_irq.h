#ifndef PORTABLE_IRQ_H
#define PORTABLE_IRQ_H

#include <stdbool.h>

/*
 * Критична секція перемикання режиму.
 *
 * На Cortex-M це PRIMASK (__get_PRIMASK/__disable_irq/__set_PRIMASK), на RTOS —
 * м'ютекс контексту регулятора. Тут — лічильник глибини: він дає задачам
 * керування чесно спитати «чи не йде зараз транзакція?» і відкласти свій такт.
 */

typedef unsigned irq_state_t;

irq_state_t irq_lock(void);
void irq_unlock(irq_state_t saved);
bool irq_locked(void);

/* Скільки разів критичну секцію було взято — доказ атомарності в звіті. */
unsigned irq_lock_events(void);

/* Швидкий контур, що застав замок узятим, рахує собі відкладений такт. */
void irq_note_deferred_tick(void);
unsigned irq_deferred_ticks(void);
void irq_reset_counters(void);

#endif /* PORTABLE_IRQ_H */
