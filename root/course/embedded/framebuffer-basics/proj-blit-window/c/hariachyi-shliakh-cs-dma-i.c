/* Гарячий шлях заливки одним блоком: CS вниз, DMA жене буфер, HW-swap у SPI.
   spi_* — обгортки над периферією вашої платформи. */
static void fill_rect_fast(uint16_t x0, uint16_t y0,
                           uint16_t x1, uint16_t y1, uint16_t color)
{
    set_window(x0, y0, x1, y1);
    uint32_t count = (uint32_t)(x1 - x0 + 1) * (y1 - y0 + 1);

    /* колір готуємо РАЗ; апаратний swap у SPI зробить big-endian сам,
       тож у буфер кладемо звичайний color, без ручного swap16 */
    static uint16_t block[512];
    for (int i = 0; i < 512; i++) block[i] = color;

    spi_cs_low();                                // CS ↓ один раз на весь блок
    while (count) {
        uint32_t k = (count < 512) ? count : 512;
        spi_write_dma((const uint8_t *)block, k * 2);  // DMA жене, CPU вільний
        count -= k;
    }
    spi_cs_high();                               // CS ↑ після всього блоку
}
