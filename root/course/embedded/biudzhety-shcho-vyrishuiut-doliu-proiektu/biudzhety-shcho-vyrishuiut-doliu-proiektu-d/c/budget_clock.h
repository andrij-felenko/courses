#ifndef BUDGET_CLOCK_H
#define BUDGET_CLOCK_H

/*
 * Мікросекундна часова база аудиту.
 *
 * На платі її дає лічильник циклів ядра (DWT->CYCCNT на Cortex-M) або вільно
 * біжучий таймер; на хості — стандартний timespec_get. Джерело підмінюється
 * прив'язкою, щоб модулі вимірювання не залежали від конкретного заліза.
 */

#include <stdint.h>

typedef uint64_t (*budget_clock_fn)(void);

/* Прив'язує апаратне джерело часу. NULL повертає типову реалізацію. */
void budget_clock_bind(budget_clock_fn source);

/* Монотонний лічильник мікросекунд від довільної точки відліку. */
uint64_t budget_clock_us(void);

#endif /* BUDGET_CLOCK_H */
