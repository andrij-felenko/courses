#include <stdint.h>

// низькорівневі примітиви платформи (HAL)
void cs_low(void);   void cs_high(void);     // вибір кристала
void dc_command(void); void dc_data(void);   // рівень ніжки DC
void spi_write(const uint8_t *buf, uint32_t n);

static void wr_cmd(uint8_t c)  { dc_command(); spi_write(&c, 1); }
static void wr_data(const uint8_t *b, uint32_t n) { dc_data(); spi_write(b, n); }

void draw_pixel(uint16_t x, uint16_t y, uint16_t color) {
    uint8_t win[4];
    cs_low();

    wr_cmd(0x2A);                                   // CASET: x..x
    win[0] = x >> 8; win[1] = x; win[2] = x >> 8; win[3] = x;
    wr_data(win, 4);

    wr_cmd(0x2B);                                   // RASET: y..y
    win[0] = y >> 8; win[1] = y; win[2] = y >> 8; win[3] = y;
    wr_data(win, 4);

    wr_cmd(0x2C);                                   // RAMWR: писати в пам'ять
    uint8_t px[2] = { color >> 8, color };          // RGB565, старший байт уперед
    wr_data(px, 2);

    cs_high();
}
