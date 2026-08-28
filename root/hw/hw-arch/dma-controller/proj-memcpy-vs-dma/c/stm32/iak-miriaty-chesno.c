#include "stm32f4xx_hal.h"
#include <string.h>

/* Буфери — 4-байтово вирівняні (копіювальник іде словами, не байтами) */
static uint8_t src[4096] __attribute__((aligned(4)));
static uint8_t dst[4096] __attribute__((aligned(4)));

/* На Cortex-M3/M4/M7 цикловий лічильник — це DWT->CYCCNT з блока налагодження;
   на відміну від ESP32 його треба ввімкнути руками, один раз при старті */
static void cyc_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;
}

static inline uint32_t cyc(void) {
    return DWT->CYCCNT;
}

/* Повертає кількість тактів, потрачених на memcpy(d, s, n) */
uint32_t bench_memcpy(void *d, const void *s, size_t n) {
    uint32_t t0 = cyc();
    memcpy(d, s, n);
    uint32_t t1 = cyc();
    return t1 - t0;   /* різниця тактів; про обгортання лічильника — нижче */
}
