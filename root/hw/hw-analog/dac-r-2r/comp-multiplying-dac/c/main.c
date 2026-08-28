/* Запис коду в множильний ЦАП: 12 біт даних, 16-бітний кадр, SPI MSB-first.
   Дані фіксуються по фронту SYNC, ключі рухаються по спаду LDAC. */
static void mdac_write(uint16_t code12)
{
    uint16_t frame = code12 & 0x0FFF;   /* старші 4 біти кадру — нулі */

    gpio_clear(PIN_SYNC);               /* кадр почався */
    spi_transfer16(frame);              /* код лягає у вхідний зсувний регістр */
    gpio_set(PIN_SYNC);                 /* кадр завершено, код у вхідному регістрі */

    gpio_clear(PIN_LDAC);               /* і лише тепер він доходить до ключів */
    delay_ns(50);                       /* тривалість імпульсу за даташитом */
    gpio_set(PIN_LDAC);
}
