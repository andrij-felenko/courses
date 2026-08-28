/* main_c99.c — Тестування C99 заголовка */
#include "device_c99.h"
#include <stdbool.h>

void usart_init_c99(void) {
    /* Налаштування регістра керування CR1 */
    USART1->CR1 |= USART_CR1_UE | USART_CR1_M_M_8BIT;

    /* Очікування готовності передавача */
    while (!(USART1->SR & USART_SR_TXE)) {
        /* Опитування прапорця статусу */
    }

    /* Відправка байта */
    USART1->DR = (0x55U & 0x1FFU);
}

int main(void) {
    usart_init_c99();
    return 0;
}
