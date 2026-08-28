/* STROBE — один вивід на дві ролі: знімок для 165 і показ для роздавача.
   У спокої STROBE = 1; такт у режимі 0 стоїть низьким. */
void io_cycle(const uint8_t *out, uint8_t *in, int n)
{
    gpio_write(PIN_STROBE, 0);   /* 165: знімок відкрито */
    delay_ns(200);
    gpio_write(PIN_STROBE, 1);   /* 165: знімок закрито; виходи показали минулий байт */

    for (int i = 0; i < n; i++)
        in[i] = spi_transfer(out[i]);   /* віддали біт — забрали біт, за один такт */
}
