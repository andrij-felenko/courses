#include "stm32f4xx.h"   // CMSIS: визначення CoreDebug, DWT, *_Msk

// Вмикаємо лічильник тактів DWT->CYCCNT. Викликати ОДИН раз при старті.
static void cycle_counter_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   // дозволити трасування (біт 24)
#ifdef DWT_LAR_KEY
    DWT->LAR = 0xC5ACCE55;                             // M7: відімкнути замок DWT
#endif
    DWT->CYCCNT = 0;                                   // обнулити лічильник
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;             // увімкнути (біт 0)
}
