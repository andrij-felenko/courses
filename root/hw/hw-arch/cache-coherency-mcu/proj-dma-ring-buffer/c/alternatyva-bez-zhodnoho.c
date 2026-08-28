// Буфери у СПЕЦІАЛЬНІЙ секції, яку скрипт лінкера кладе в некешовану ділянку SRAM
// (MPU налаштовано оголосити цю ділянку Non-cacheable ще до старту периферії).
static uint8_t rx_buf[64] __attribute__((section(".dma_noncacheable"), aligned(32)));

// Обробник спрощується до безкешової прошивки: читай напряму, кеш тут ні до чого.
void DMA1_Stream0_IRQHandler(void)
{
    if (dma_rx_complete_flag()) {
        dma_rx_clear_flags();
        process_packet(rx_buf, sizeof(rx_buf));   // SRAM некешована — завжди свіжа
    }
}
