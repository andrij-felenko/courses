/* Безпечне оновлення сектору Flash із коду в RAM (C) */
__attribute__((section(".ramfunc"), noinline))
void safe_flash_sector_erase(uint32_t sector_address) {
    __disable_irq(); // Забороняємо вибірку обробників переривань з QSPI

    /* 1. Вихід із режиму Memory-Mapped */
    QUADSPI->CR |= QUADSPI_CR_ABORT;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 2. Скидання режиму Continuous Read надсиланням байта 0xFF */
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | 0xFF;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 3. Дозвіл запису */
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | W25Q_CMD_WRITE_ENABLE;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 4. Стирання сектора 4 КБайт (команда 0x20) */
    QUADSPI->AR = sector_address;
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (2U << QUADSPI_CCR_ADSIZE_Pos) |
                   (1U << QUADSPI_CCR_ADMODE_Pos)| (1U << QUADSPI_CCR_IMODE_Pos) | 0x20;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 5. Очікування завершення внутрішнього циклу стирання */
    qspi_auto_poll_busy(10000000);

    /* 6. Повернення в режим Memory-Mapped XIP (0-4-4) */
    qspi_init_xip();

    /* 7. Обов'язкова інвалідація кешу процесора для завантаження нових даних */
    SCB_InvalidateICache();
    SCB_InvalidateDCache();

    __enable_irq(); // Дозволяємо переривання
}
