/* Безпечне очікування завершення операції Flash з перезавантаженням IWDG (C++) */
[[nodiscard]] bool qspi_wait_busy_with_watchdog(uint32_t timeout_ms) noexcept {
    while (timeout_ms > 0) {
        IWDG->KR = 0xAAAA; // Перезавантаження watchdog
        if (!(QUADSPI->SR & QUADSPI_SR_BUSY)) {
            return true;
        }
        for (volatile int i = 0; i < 40000; ++i) { __NOP(); }
        --timeout_ms;
    }
    return false;
}
