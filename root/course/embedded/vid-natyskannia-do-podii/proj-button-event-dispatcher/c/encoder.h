#ifndef ENCODER_H
#define ENCODER_H

#include <stdbool.h>
#include <stdint.h>

#include "event_queue.h"

/* Скільки чвертей періоду припадає на один клац фіксатора. У більшості
   механічних енкодерів із детентом — чотири; є моделі з двома. */
#define ENCODER_STEPS_PER_DETENT 4

/* Повертає сирий рівень фази: 1 — високий, 0 — низький. */
typedef uint8_t (*phase_read_fn)(void);

typedef struct {
    uint8_t       id;
    phase_read_fn read_phase_a;
    phase_read_fn read_phase_b;
    uint8_t       prev_state;  /* 2-бітний код [A B] минулої вибірки */
    int8_t        sub_step;    /* накопичувач чвертей до повного клацу */
    uint16_t      glitches;    /* заборонені переходи: брязкіт або пропуск вибірки */
} encoder_t;

bool     encoder_init(encoder_t *enc, uint8_t id, phase_read_fn read_a, phase_read_fn read_b);
void     encoder_process_tick(encoder_t *enc, event_queue_t *q);
uint16_t encoder_glitches(const encoder_t *enc);

#endif /* ENCODER_H */
