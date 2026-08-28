#include "stm32f4xx.h"   // або інший CMSIS-заголовок вашого МК

static inline void cyccnt_enable(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;   // увімкнути DWT/ITM
#ifdef DWT_LAR_KEY                                     // Cortex-M7: зняти замок
    DWT->LAR = 0xC5ACCE55;
#endif
    DWT->CYCCNT = 0;                                   // обнулити
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;              // пустити лічильник
}

static inline uint32_t cyccnt(void) { return DWT->CYCCNT; }
