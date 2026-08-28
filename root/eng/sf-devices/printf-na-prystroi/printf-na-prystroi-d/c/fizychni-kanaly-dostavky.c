#include <stdint.h>

/* Базові адреси CMSIS для прямого запису в регістр ITM Stimulus Port 0 */
#define ITM_PORT0_U8  (*(volatile uint8_t*)0xE0000000UL)
#define ITM_PORT0_U32 (*(volatile uint32_t*)0xE0000000UL)
#define ITM_TER       (*(volatile uint32_t*)0xE0000E00UL)
#define ITM_TCR       (*(volatile uint32_t*)0xE0000E80UL)
#define DEMCR         (*(volatile uint32_t*)0xE000EDFCUL)

void itm_send_char_fast(uint8_t ch) {
    /* Перевіряємо, чи увімкнено модуль трасування налагоджувачем */
    if ((DEMCR & (1UL << 24)) && (ITM_TCR & (1UL << 0)) && (ITM_TER & (1UL << 0))) {
        /* Очікуємо готовності апаратного FIFO буфера порту 0 */
        while (ITM_PORT0_U32 == 0UL) {
            /* Пауза у разі заповнення апаратного буфера */
        }
        ITM_PORT0_U8 = ch;
    }
}
