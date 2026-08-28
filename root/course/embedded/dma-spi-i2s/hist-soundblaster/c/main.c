/* Ініціалізація DMA-каналу 1 для Sound Blaster */
void sb_dma_start(uint8_t *buf, uint16_t len) {
    uint32_t phys = (uint32_t)buf;   /* реальна фізична адреса у DOS */

    /* 1. Маскуємо канал 1 під час налаштування */
    outp(0x0A, 0x05);               /* маска: канал 1 */

    /* 2. Скидаємо flip-flop адреси/лічильника */
    outp(0x0C, 0x00);

    /* 3. Режим: одноциклова передача, читання, канал 1 */
    outp(0x0B, 0x49);

    /* 4. Адреса: молодший + старший байт */
    outp(0x02, phys & 0xFF);
    outp(0x02, (phys >> 8) & 0xFF);

    /* 5. Сторінковий регістр (біти 16–23) */
    outp(0x83, (phys >> 16) & 0xFF);

    /* 6. Лічильник довжини (len - 1) */
    outp(0x03, (len - 1) & 0xFF);
    outp(0x03, ((len - 1) >> 8) & 0xFF);

    /* 7. Знімаємо маску — DMA готовий */
    outp(0x0A, 0x01);

    /* 8. Командуємо Sound Blaster почати DMA-відтворення */
    sb_write(0x14);                 /* команда «8-bit DMA output» */
    sb_write((len - 1) & 0xFF);
    sb_write((len - 1) >> 8);
}
