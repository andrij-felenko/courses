void background_set_speed(uint16_t rpm)
{
    // Заборонити лише фонові переривання; критичний таймер (0) — НЕ чіпаємо.
    // Поріг 1: глушить усе з пріоритетом ≥ 1, тобто весь фон.
    uint32_t saved = enter_critical_upto(1);

    spi_select(DRIVE);
    spi_write(REG_SPEED, rpm);     // неподільна транзакція до драйвера
    spi_deselect(DRIVE);

    exit_critical(saved);          // фон знову витісняємо
}
