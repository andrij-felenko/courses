/* timer.h — таймер TIM2 як періодичне джерело переривань 1 кГц.
 *
 * Увесь модуль — це чотири кроки методики читання Reference Manual,
 * записані мовою C: тактування → конфігурація при вимкненому блоці →
 * активація → робота з прапорцями стану.
 */
#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>

typedef enum {
    TIMER_OK = 0,
    TIMER_ERR_CLOCK_TOO_SLOW,   /* із такої частоти 1 мкс не набрати       */
    TIMER_ERR_CLOCK_NOT_EXACT,  /* предільник дав би дробове значення      */
    TIMER_ERR_PRESCALER_RANGE,  /* PSC не влазить у 16 біт                 */
} timer_status_t;

/* timer_clock_hz — частота, що приходить на сам таймер, а не частота шини:
 * коли дільник APB1 не одиничний, RM0090 подвоює тактову таймерів
 * (на STM32F407 при PCLK1 = 42 МГц таймер бачить 84 МГц). */
timer_status_t timer_1khz_start(uint32_t timer_clock_hz);

/* Зупинити лічильник і зняти дозвіл переривання. */
void timer_stop(void);

/* Кількість переповнень від старту, тобто мілісекунди. */
uint32_t timer_ticks(void);

/* Вектор переривання TIM2 — ім'я збігається з таблицею векторів у startup. */
void TIM2_IRQHandler(void);

#endif /* TIMER_H */
