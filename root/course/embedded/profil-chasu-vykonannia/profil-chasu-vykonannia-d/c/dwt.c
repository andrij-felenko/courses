#include "dwt.h"

/* Регістр замка блоку трасування (ARMv7-M): на Cortex-M7 DWT після скидання
   замкнений, і запис у CTRL мовчки не діє, поки не подано ключ. */
#define DWT_LAR_ADDR  0xE0001FB0UL
#define DWT_UNLOCK    0xC5ACCE55UL

bool dwt_init(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   /* крок 1: увімкнути трасування */

#if defined(__CORTEX_M) && (__CORTEX_M == 7U)
    *(volatile uint32_t *)DWT_LAR_ADDR = DWT_UNLOCK;
#endif

    if ((DWT->CTRL & DWT_CTRL_NOCYCCNT_Msk) != 0U) {
        return false;   /* кремній без лічильника тактів — профілювати нічим */
    }

    DWT->CYCCNT = 0U;                                 /* крок 3: обнулити */
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;              /* крок 2: пустити лічильник */
    __DSB();

    /* Перевірка ділом: без під'єднаного налагоджувача TRCENA на частині
       кристалів не тримається, і CYCCNT назавжди лишається нулем. */
    const uint32_t first = DWT->CYCCNT;
    for (volatile uint32_t i = 0U; i < 8U; ++i) {
        __NOP();
    }
    return DWT->CYCCNT != first;
}
