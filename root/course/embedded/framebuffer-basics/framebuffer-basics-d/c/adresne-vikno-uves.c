#include <stdint.h>

/* низькорівневі примітиви драйвера (реалізація залежить від периферії):
   dc_low()/dc_high() смикають лінію D/C; spi_write() шле байти по SPI */
extern void dc_low(void);
extern void dc_high(void);
extern void spi_write(const uint8_t *buf, size_t n);

static void send_cmd(uint8_t cmd) { dc_low();  spi_write(&cmd, 1); }
static void send_dat(const uint8_t *d, size_t n) { dc_high(); spi_write(d, n); }

/* задати прямокутне вікно (x, y) розміром (w, h).
   КЛЮЧОВЕ: кінцеві координати INCLUSIVE → x1 = x + w − 1 (не x + w) */
static void set_window(uint16_t x, uint16_t y, uint16_t w, uint16_t h)
{
    uint16_t x1 = x + w - 1;                 /* включно! ширина w → останній стовпець x+w−1 */
    uint16_t y1 = y + h - 1;

    uint8_t c[4] = { x >> 8, x & 0xFF, x1 >> 8, x1 & 0xFF };   /* старший байт першим */
    send_cmd(0x2A); send_dat(c, 4);          /* CASET: стовпці x..x1 */

    uint8_t r[4] = { y >> 8, y & 0xFF, y1 >> 8, y1 & 0xFF };
    send_cmd(0x2B); send_dat(r, 4);          /* RASET: рядки y..y1 */

    send_cmd(0x2C);                          /* RAMWR: далі — потік пікселів у це вікно */
}
