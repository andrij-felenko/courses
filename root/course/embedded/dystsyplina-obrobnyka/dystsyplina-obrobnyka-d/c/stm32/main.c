#include "stm32f4xx_ll_usart.h"
#include "stm32f4xx_ll_bus.h"

/* Статичний кільцевий буфер */
#define RX_BUF_SIZE 128
#define RX_BUF_MASK (RX_BUF_SIZE - 1)

static volatile uint8_t rx_buffer[RX_BUF_SIZE];
static volatile uint32_t rx_head = 0;
static volatile uint32_t rx_tail = 0;
static volatile bool rx_overrun_flag = false;

/* Дисциплінований обробник переривання USART1 */
void USART1_IRQHandler(void) {
    /* Перевіряємо прапорець наявності отриманого байта */
    if (LL_USART_IsActiveFlag_RXNE(USART1) && LL_USART_IsEnabledIT_RXNE(USART1)) {
        /* Читання регістра RDR автоматично скидає прапорець RXNE */
        uint8_t byte = LL_USART_ReceiveData8(USART1);

        uint32_t next_head = (rx_head + 1) & RX_BUF_MASK;
        if (next_head != rx_tail) {
            rx_buffer[rx_head] = byte;
            __asm volatile ("dmb" ::: "memory");
            rx_head = next_head;
        } else {
            /* Буфер повний: фіксуємо помилку без зависання */
            rx_overrun_flag = true;
        }
    }

    /* Перевірка та очищення апаратної помилки переповнення (ORE) */
    if (LL_USART_IsActiveFlag_ORE(USART1)) {
        LL_USART_ClearFlag_ORE(USART1);
        rx_overrun_flag = true;
    }
}
