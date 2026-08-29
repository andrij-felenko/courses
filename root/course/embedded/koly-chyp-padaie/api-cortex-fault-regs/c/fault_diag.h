/* fault_diag.h — налаштування діагностичного середовища ядра Cortex-M
 * і розбір регістрів збою після аварії.
 */
#ifndef FAULT_DIAG_H
#define FAULT_DIAG_H

#include <stdint.h>
#include <stdbool.h>

/* Базовий кадр, який апаратура кладе на стек при вході у виняток.
 * Порядок слів заданий архітектурою і змінам не підлягає. */
struct exception_frame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;    /* адреса повернення того, хто впав */
    uint32_t pc;    /* інструкція, на якій стався збій (для ТОЧНИХ помилок) */
    uint32_t psr;
};

enum fault_source {
    FAULT_SOURCE_HARD      = 0,
    FAULT_SOURCE_MEMMANAGE = 1,
    FAULT_SOURCE_BUS       = 2,
    FAULT_SOURCE_USAGE     = 3,
};

/* Увімкнути роздільні обробники, апаратні пастки й точні помилки шини.
 * Викликати якнайраніше в main(), до першого власного коду. */
void fault_diag_init(void);

/* Спільна точка входу всіх обробників збоїв. Викликається з naked-заглушок
 * у fault_handlers.c: frame — кадр із MSP або PSP (вибір за бітом 2 у LR),
 * exc_return — сире значення LR при вході, source — який саме виняток. */
void fault_report_entry(const struct exception_frame *frame,
                        uint32_t exc_return,
                        uint32_t source) __attribute__((noreturn));

#endif /* FAULT_DIAG_H */
