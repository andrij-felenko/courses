static fifo_t rx_fifo;

// Викликається апаратним перериванням: прилетів байт.
void USART_IRQHandler(void)
{
    uint8_t b = (uint8_t)UART_DR;   // забрати з регістра приймача
    if (!fifo_put(&rx_fifo, b)) {
        // черга переповнена — свідомо вирішуємо, що робити:
        // тут лічимо втрату, а не мовчимо про неї
        rx_overflow_count++;
    }
}

// Головний цикл: обробляємо все, що встигло накопичитись.
void main_loop(void)
{
    uint8_t b;
    while (fifo_get(&rx_fifo, &b)) {
        process_byte(b);            // розбір протоколу, збирання рядка тощо
    }
    // ... інша робота циклу ...
}
