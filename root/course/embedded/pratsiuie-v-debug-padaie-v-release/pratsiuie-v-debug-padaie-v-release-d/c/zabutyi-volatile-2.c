// Небезпечно: компілятор не знає, що ISR викликається асинхронно
static bool packet_received = false;

void USART1_IRQHandler(void) {
    if (USART1->SR & USART_SR_RXNE) {
        packet_received = true;
        // Читання даних...
    }
}

void wait_for_data(void) {
    // В -O2 перетворюється на вічний цикл, якщо прапорець був false на старті
    while (!packet_received) {
        __NOP();
    }
}
