/* Безпечне оновлення сектору Flash із коду в RAM (C++20 RAII) */
[[gnu::section(".ramfunc"), gnu::noinline]]
void safe_flash_sector_erase(uint32_t sector_address) noexcept {
    struct IrqGuard {
        IrqGuard() noexcept { __disable_irq(); }
        ~IrqGuard() noexcept { __enable_irq(); }
    } guard;

    QUADSPI->CR |= QUADSPI_CR_ABORT;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | 0xFF;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | W25Q_CMD_WRITE_ENABLE;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    QUADSPI->AR = sector_address;
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (2U << QUADSPI_CCR_ADSIZE_Pos) |
                   (1U << QUADSPI_CCR_ADMODE_Pos)| (1U << QUADSPI_CCR_IMODE_Pos) | 0x20;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    qspi_auto_poll_busy(10'000'000);
    qspi_init_xip();

    SCB_InvalidateICache();
    SCB_InvalidateDCache();
}
