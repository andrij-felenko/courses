#include <stdint.h>
#include "stm32f4xx.h"   /* CMSIS: CoreDebug, DWT, DWT_CTRL_CYCCNTENA_Msk */

/* Увімкнути лічильник тактів DWT один раз на старті. */
static void cyccnt_enable(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   /* глобальний дозвіл DWT */
    DWT->CYCCNT = 0;                                   /* скинути лічильник */
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;             /* пуск: рахує щотакту */
}

/* Найгірша затримка, а не середня: тримаємо МАКСИМУМ за весь час роботи. */
volatile uint32_t latency_worst;      /* найгірше, тактів */
volatile uint32_t latency_last;       /* останнє, тактів (для контролю) */

/* Момент фізичної події фіксуємо якнайраніше — просто в обробнику входу.
   Ідеально — захоплення таймером; тут спрощено: мітку ставить сам фронт. */
volatile uint32_t t_event;            /* мітка часу події, тактів DWT */

void EXTI_IRQHandler(void) {          /* спрацював фронт на вході */
    uint32_t now  = DWT->CYCCNT;      /* коли ядро дісталося обробника */
    uint32_t took = now - t_event;    /* різниця коректна навіть при переповненні:
                                         беззнакове віднімання «обгортається» само */
    latency_last = took;
    if (took > latency_worst)         /* НЕ середнє: оновлюємо лише максимум */
        latency_worst = took;

    /* ... корисна робота обробника ... */
}
