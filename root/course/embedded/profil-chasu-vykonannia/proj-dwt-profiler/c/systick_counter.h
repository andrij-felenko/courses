/* systick_counter.h — запасне джерело тактів для ядер без DWT
 * (Cortex-M0/M0+: STM32F0, STM32L0, RP2040).
 *
 * SysTick рахує ВНИЗ від LOAD до нуля, розрядність 24 біти. Прапорець
 * COUNTFLAG зводиться при переході через нуль і скидається читанням CTRL,
 * тож один оберт за час заміру ми бачимо, а другий — уже ні.
 */
#ifndef SYSTICK_COUNTER_H
#define SYSTICK_COUNTER_H

#include <stdint.h>

#define SYSTICK_CTRL (*(volatile uint32_t *)0xE000E010U)
#define SYSTICK_LOAD (*(volatile uint32_t *)0xE000E014U)
#define SYSTICK_VAL  (*(volatile uint32_t *)0xE000E018U)

#define SYSTICK_ENABLE    (1UL << 0)
#define SYSTICK_TICKINT   (1UL << 1)
#define SYSTICK_CLKSOURCE (1UL << 2)  /* 1 — від HCLK, без ділення на 8 */
#define SYSTICK_COUNTFLAG (1UL << 16)
#define SYSTICK_MAX_LOAD  0x00FFFFFFUL

/**
 * Пускає SysTick у вільний біг на повну 24-бітну глибину.
 * УВАГА: забирає таймер у HAL/RTOS — системний тік на час профілювання стане.
 */
void systick_counter_init(void);

/** Поточний показ спадного лічильника. */
uint32_t systick_get_value(void);

/** Такти від start_val до цієї миті, з урахуванням одного обертання. */
uint32_t systick_elapsed_cycles(uint32_t start_val);

/** Накладні витрати пари читань, у тактах. */
uint32_t systick_counter_overhead(void);

#endif /* SYSTICK_COUNTER_H */
