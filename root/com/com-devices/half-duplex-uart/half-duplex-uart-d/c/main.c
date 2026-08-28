#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define DE_PORT GPIOA
#define DE_PIN  (1 << 4)

// Пряме керування бітовими регістрами атомарного запису
static inline void rs485_set_tx_mode(void) {
    DE_PORT->BSRR = DE_PIN; // Підняти DE у високий рівень
}

static inline void rs485_set_rx_mode(void) {
    DE_PORT->BSRR = (DE_PIN << 16); // Опустити DE в низький рівень
}

// Блокувальна, але строго безпечна передача кадру
bool rs485_transmit_blocking(USART_TypeDef *usart, const uint8_t *data, size_t length) {
    if (data == NULL || length == 0) {
        return false;
    }

    // 1. Перемикаємо трансивер у режим передачі
    rs485_set_tx_mode();

    // 2. Послідовна видача байтів у буфер
    for (size_t i = 0; i < length; ++i) {
        // Очікуємо звільнення буфера даних TDR
        while (!(usart->ISR & USART_ISR_TXE_TXFNF)) {}
        usart->TDR = data[i];
    }

    // 3. Критичний крок: чекаємо завершення передачі останнього СТОП-біта (TC)
    while (!(usart->ISR & USART_ISR_TC)) {}

    // 4. Очищаємо прапорець TC
    usart->ICR = USART_ICR_TCCF;

    // 5. Повертаємо трансивер у режим прийому
    rs485_set_rx_mode();
    return true;
}
