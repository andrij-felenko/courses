#include <stddef.h>

#include "encoder.h"

/* Таблиця переходів коду Грея, індекс = (prev << 2) | curr.
   Рядок — попередній стан [A B], стовпець — поточний.
   Нуль означає «руху немає» (той самий стан) або «так не буває»
   (обидва біти змінилися одразу: 00↔11, 01↔10). */
static const int8_t ENCODER_LUT[16] = {
/*  curr:      00   01   10   11 */
/* prev 00 */   0,  +1,  -1,   0,
/* prev 01 */  -1,   0,   0,  +1,
/* prev 10 */  +1,   0,   0,  -1,
/* prev 11 */   0,  -1,  +1,   0
};

static bool emit(event_queue_t *q, uint8_t id, event_type_t type) {
    input_event_t evt;
    evt.id = id;
    evt.type = type;
    evt.duration_ms = 1;  /* один клац фіксатора */
    return queue_push(q, evt);
}

bool encoder_init(encoder_t *enc, uint8_t id, phase_read_fn read_a, phase_read_fn read_b) {
    if (enc == NULL || read_a == NULL || read_b == NULL) {
        return false;
    }
    enc->id = id;
    enc->read_phase_a = read_a;
    enc->read_phase_b = read_b;

    /* Стартовий стан читаємо з живих пінів: якщо вал стоїть між клацами,
       перший же тік не має вигадати неіснуючий крок. */
    const uint8_t a = read_a() ? 1u : 0u;
    const uint8_t b = read_b() ? 1u : 0u;
    enc->prev_state = (uint8_t)((a << 1) | b);
    enc->sub_step = 0;
    enc->glitches = 0;
    return true;
}

void encoder_process_tick(encoder_t *enc, event_queue_t *q) {
    if (enc == NULL || q == NULL) {
        return;
    }

    const uint8_t a = enc->read_phase_a() ? 1u : 0u;
    const uint8_t b = enc->read_phase_b() ? 1u : 0u;
    const uint8_t curr = (uint8_t)((a << 1) | b);

    if (curr == enc->prev_state) {
        return;  /* вал стоїть — найчастіший випадок, виходимо першим ділом */
    }

    const uint8_t code = (uint8_t)((enc->prev_state << 2) | curr);
    const int8_t step = ENCODER_LUT[code];
    enc->prev_state = curr;

    if (step == 0) {
        /* Обидва біти змінилися між вибірками: або сильний брязкіт, або вал
           крутнули швидше за темп опитування. Напрямок невідомий — краще
           втратити крок, ніж додати хибний. */
        if (enc->glitches < UINT16_MAX) {
            enc->glitches++;
        }
        return;
    }

    /* Зміна напрямку посеред клацу: недокручені чверті вже нічого не значать. */
    if ((step > 0 && enc->sub_step < 0) || (step < 0 && enc->sub_step > 0)) {
        enc->sub_step = 0;
    }
    enc->sub_step = (int8_t)(enc->sub_step + step);

    if (enc->sub_step >= ENCODER_STEPS_PER_DETENT) {
        enc->sub_step = 0;
        emit(q, enc->id, EVENT_ENCODER_CW);
    } else if (enc->sub_step <= -ENCODER_STEPS_PER_DETENT) {
        enc->sub_step = 0;
        emit(q, enc->id, EVENT_ENCODER_CCW);
    }
}

uint16_t encoder_glitches(const encoder_t *enc) {
    return (enc == NULL) ? 0u : enc->glitches;
}
