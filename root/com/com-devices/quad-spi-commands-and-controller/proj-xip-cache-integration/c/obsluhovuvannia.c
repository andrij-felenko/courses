/* Безпечне очікування завершення операції Flash з перезавантаженням IWDG (C) */
bool qspi_wait_busy_with_watchdog(uint32_t timeout_ms) {
    while (timeout_ms > 0) {
        /* Перезавантаження лічильника сторожового таймера */
        IWDG->KR = 0xAAAA;

        /* Перевірка прапорця зайнятості контролера або статусу Flash */
        if (!(QUADSPI->SR & QUADSPI_SR_BUSY)) {
            return true;
        }

        /* Затримка на 1 мілісекунду */
        for (volatile int i = 0; i < 40000; i++) { __NOP(); }
        timeout_ms--;
    }
    return false; // Тайм-аут операції Flash
}
