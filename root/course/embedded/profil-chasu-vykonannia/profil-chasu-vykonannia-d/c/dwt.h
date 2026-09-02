/* Лічильник тактів ядра DWT->CYCCNT: 1 такт роздільної здатності,
 * на 168 МГц це 5.95 нс. Повний інструмент зі статистикою й калібруванням
 * власного оверхеду — окремий модуль; тут рівно те, що потрібно ISR.
 */
#ifndef DWT_H
#define DWT_H

#include <stdbool.h>
#include <stdint.h>
#include "stm32f4xx.h"

/* Розблоковує трасування й перевіряє, що лічильник СПРАВДІ пішов.
   Повертає false на кристалах без CYCCNT і коли блок трасування замкнено. */
bool dwt_init(void);

static inline uint32_t dwt_now(void)
{
    /* Бар'єри компілятора: заборона переставляти читання лічильника
       відносно вимірюваного коду. Апаратних бар'єрів тут не треба —
       CYCCNT читається однією інструкцією LDR з рівня Device. */
    __asm__ volatile("" ::: "memory");
    const uint32_t cycles = DWT->CYCCNT;
    __asm__ volatile("" ::: "memory");
    return cycles;
}

/* Різниця правильна навіть через переповнення: арифметика uint32_t за модулем 2^32. */
static inline uint32_t dwt_since(uint32_t start)
{
    return dwt_now() - start;
}

/* Такти -> сотi частки мікросекунди (цілочислово, без плаваючої коми у звіті). */
static inline uint32_t dwt_us_x100(uint32_t cycles, uint32_t f_cpu_mhz)
{
    return (uint32_t)(((uint64_t)cycles * 100ULL) / (uint64_t)f_cpu_mhz);
}

#endif /* DWT_H */
