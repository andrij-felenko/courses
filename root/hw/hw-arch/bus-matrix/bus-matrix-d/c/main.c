#include <stdint.h>

/* Два РІЗНІ банки пам'яті — різні стовпці матриці шин */
static uint8_t buf_a[4096] __attribute__((section(".sram1")));  /* тут працює ядро */
static uint8_t buf_b[4096] __attribute__((section(".sram2")));  /* сюди возить DMA */

/* DMA залив нові дані у buf_b (стовпець SRAM2), поки ядро
   обробляє buf_a (стовпець SRAM1). Різні цілі → матриця веде
   обидві транзакції паралельно, без черги перед арбітром. */
uint32_t process(void) {
    uint32_t acc = 0;
    for (int i = 0; i < (int)sizeof buf_a; i++)
        acc += buf_a[i];          /* ядро → SRAM1 */
    return acc;                   /* тим часом DMA → SRAM2 незалежно */
}
