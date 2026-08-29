#ifndef BSP_MCO_H
#define BSP_MCO_H

#include <stdint.h>

/*
 * Виведення тактового сигналу на пін PA8 (MCO1) для перевірки осцилографом.
 * Щуп на OSC_IN/OSC_OUT зриває генерацію — міряють саме тут.
 */

/* Джерело — вихід PLL, дільник /4: при SYSCLK 168 МГц на піні буде 42 МГц */
void mco1_enable_pll_div4(void);

/* Яку частоту має показати осцилограф при поточному тактуванні */
uint32_t mco1_expected_hz(void);

#endif /* BSP_MCO_H */
