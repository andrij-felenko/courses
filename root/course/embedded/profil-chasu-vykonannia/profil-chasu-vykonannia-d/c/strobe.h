/* Стробування виводу GPIO — єдиний спосіб побачити час обробника осцилографом.
 * Запис іде в BSRR: атомарна установка/скидання за одне звернення до шини.
 * GPIOB->ODR ^= MASK заборонено — це LDR+EOR+STR (3-4 такти) плюс гонитва
 * із сусіднім піном того самого порту, якщо втрутиться інше переривання.
 */
#ifndef STROBE_H
#define STROBE_H

#include <stdint.h>
#include "stm32f4xx.h"

#define STROBE_PORT    GPIOB
#define STROBE_PIN     5U   /* канал 1 осцилографа: ширина імпульсу = час роботи */
#define STROBE_MARKER  4U   /* канал 2: голка на вході в ISR = латентність */

static inline void strobe_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    (void)RCC->AHB1ENR;   /* затримка на синхронізацію шини після дозволу тактування */

    const uint32_t pins[2] = { STROBE_PIN, STROBE_MARKER };
    for (uint32_t i = 0U; i < 2U; ++i) {
        const uint32_t p = pins[i];
        STROBE_PORT->MODER = (STROBE_PORT->MODER & ~(3U << (p * 2U))) | (1U << (p * 2U));
        STROBE_PORT->OTYPER &= ~(1U << p);                  /* двотактний вихід */
        STROBE_PORT->OSPEEDR |= (3U << (p * 2U));           /* найкрутіший фронт */
        STROBE_PORT->PUPDR &= ~(3U << (p * 2U));
        STROBE_PORT->BSRR = (1U << (p + 16U));              /* стартовий рівень 0 */
    }
}

static inline void strobe_high(void)
{
    STROBE_PORT->BSRR = (1U << STROBE_PIN);
}

static inline void strobe_low(void)
{
    STROBE_PORT->BSRR = (1U << (STROBE_PIN + 16U));
}

/* Коротка голка: фіксує на екрані сам момент входу в обробник, не спотворюючи
   вимірювання ширини основного імпульсу. Два NOP — щоб фронт було видно. */
static inline void strobe_marker(void)
{
    STROBE_PORT->BSRR = (1U << STROBE_MARKER);
    __NOP();
    __NOP();
    STROBE_PORT->BSRR = (1U << (STROBE_MARKER + 16U));
}

#endif /* STROBE_H */
