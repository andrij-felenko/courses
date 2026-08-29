/* Проміжна черга в RAM для записів із обробників переривань.
 *
 * Писати у SPI Flash із переривання не можна: Page Program триває 0.7–3.0 мс,
 * а обробник мусить укластися в одиниці мікросекунд. Тому ISR кладе в цю чергу
 * рівно 12 байтів і виходить, а фонова задача з найнижчим пріоритетом переносить
 * їх у Flash.
 *
 * Черга розрахована на ОДНОГО виробника й ОДНОГО споживача. Якщо джерел
 * переривань кілька, вони мусять або йти через одне переривання найвищого
 * пріоритету, або штовхати кадр із вимкненими перериваннями: два ISR, що
 * одночасно рухають head, зіпсують чергу. */

#ifndef ISR_STAGE_H
#define ISR_STAGE_H

#include <stdatomic.h>

#include "flash_logger.h"

/* Ємність мусить бути степенем двійки: індекс береться маскою, а лічильники
 * рахують монотонно й переповнюються без наслідків. */
#define ISR_STAGE_CAPACITY 32u

/* Кадр рівно на 12 байтів: 1 + 1 + 2 + 4 + 4. Довшого навантаження в ISR
 * не буває — туди їде код події й одне число. */
typedef struct {
    uint8_t  level;
    uint8_t  module_id;
    uint16_t arg16;        /* єдиний аргумент події */
    uint32_t timestamp_ms;
    uint32_t token_id;
} isr_frame_t;

typedef struct {
    isr_frame_t  slots[ISR_STAGE_CAPACITY];
    atomic_uint  head;     /* рухає лише ISR */
    atomic_uint  tail;     /* рухає лише фонова задача */
    atomic_uint  dropped;  /* скільки кадрів згоріло на переповненні */
} isr_stage_t;

void isr_stage_init(isr_stage_t *stage);

/* Викликається з переривання. false — черга повна, кадр утрачено. */
bool isr_stage_push(isr_stage_t *stage, const isr_frame_t *frame);

/* Викликається з задачі. false — черга порожня. */
bool isr_stage_pop(isr_stage_t *stage, isr_frame_t *frame);

/* Забирає й обнуляє лічильник утрачених кадрів. */
uint32_t isr_stage_take_dropped(isr_stage_t *stage);

/* Переносить усе накопичене у Flash. Повертає кількість записаних кадрів.
 * Якщо кадри губилися — додає окремий запис WARN із їх кількістю: мовчазна
 * діра в журналі гірша за визнану втрату. */
uint32_t isr_stage_drain(isr_stage_t *stage, flash_logger_t *logger);

#endif /* ISR_STAGE_H */
