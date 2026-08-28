static volatile bool frame_done;     /* виставляє таймер, скидає головний цикл */
static uint16_t      rx_crc;         /* чіпає ТІЛЬКИ обробник UART */
static uint16_t      rx_len;

void USART1_IRQHandler(void) {                       /* прийшов байт */
    uint8_t b = (uint8_t)USART1->RDR;
    if (rx_len == 0U)
        rx_crc = 0xFFFFU;                            /* старт кадру — рівно один раз */
    ring_put(b);
    rx_crc = crc16_modbus_update(rx_crc, &b, 1);     /* ~16 інструкцій на байт */
    rx_len++;
    timer_restart(T35);                              /* кожен байт відсуває межу кадру */
}

void TIM6_IRQHandler(void) {                         /* тиша 3.5 символу — кадр скінчився */
    frame_done = true;                               /* лише тепер rx_crc можна читати ззовні */
}
