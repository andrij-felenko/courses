/* Контракт із компонувальником: секція .ramfunc виконується з SRAM.
 * VMA секції — в RAM, LMA — у Flash (див. фрагмент .ld у статті),
 * тому перед першим викликом будь-якої RAM_FUNC її треба скопіювати.
 */
#ifndef RAMFUNC_H
#define RAMFUNC_H

#include <stdint.h>
#include "stm32f4xx.h"

/* noinline обов'язковий: без нього компілятор має право вставити тіло
   функції у виклик, що лежить у Flash, і вся вигода зникає. */
#define RAM_FUNC __attribute__((section(".ramfunc"), noinline))

/* Символи, які оголошує скрипт компонувальника. */
extern uint32_t _sramfunc;   /* початок секції в SRAM (VMA) */
extern uint32_t _eramfunc;   /* кінець секції в SRAM */
extern uint32_t _siramfunc;  /* образ секції у Flash (LMA) */

/* Копіювання секції з Flash у SRAM. Викликається з main() найпершим —
   до цього моменту жодну RAM_FUNC чіпати не можна. */
static inline void ramfunc_copy(void)
{
    const uint32_t *src = (const uint32_t *)&_siramfunc;
    uint32_t *dst = &_sramfunc;

    while (dst < &_eramfunc) {
        *dst++ = *src++;
    }

    /* DSB: усі записи справді дійшли до SRAM.
       ISB: конвеєр скинуто, наступні вибірки підуть за новими адресами. */
    __DSB();
    __ISB();
}

#endif /* RAMFUNC_H */
