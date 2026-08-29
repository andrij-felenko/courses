#ifndef DEADMAN_H
#define DEADMAN_H

/* Кнопка мертвої руки: кінематика 3-позиційного перемикача за IEC 60947-5-8
   і циклічний контроль пильності з ескалацією тривоги. */

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    GRIP_RELEASED = 0,   /* Позиція 1 */
    GRIP_ENABLED,        /* Позиція 2 */
    GRIP_PANIC,          /* Позиція 3 або блокування після неї */
    GRIP_DOZED,          /* пильність не підтверджено — дозвіл знято */
    GRIP_FAULT           /* контакти дозволу розійшлися: залипає */
} grip_t;

typedef struct {
    grip_t   grip;
    bool     panic_latch;     /* Позиція 3 блокує дозвіл до повного відпускання */
    bool     contacts_split;  /* канали A і B не збігаються просто зараз */
    uint32_t split_ms;

    uint32_t idle_ms;         /* час без дій оператора */
    bool     ack_prev;
    bool     lamp;
    bool     buzzer;
} deadman_t;

void   deadman_init(deadman_t *d);
void   deadman_update(deadman_t *d, uint32_t dt_ms);

/* true — рух приводів дозволено: Позиція 2, контакти збігаються,
   пильність підтверджено. */
bool   deadman_ready(const deadman_t *d);
grip_t deadman_grip(const deadman_t *d);

#endif /* DEADMAN_H */
