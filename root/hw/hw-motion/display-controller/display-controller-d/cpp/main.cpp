#include <stdint.h>

// низькорівневі примітиви платформи (HAL): тримають CS і D/C, женуть байти по SPI
void dc_command(void);          // D/C = 0  → далі йде команда
void dc_data(void);             // D/C = 1  → далі йдуть дані
void spi_write(const uint8_t *buf, uint32_t n);   // вилити n байтів у шину

static void send_cmd(uint8_t c) { dc_command(); spi_write(&c, 1); }

// задати вікно адрес: CASET (стовпці) + RASET (рядки)
static void set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    uint8_t buf[4];
    send_cmd(0x2A);                                  // CASET — діапазон стовпців
    buf[0] = x0 >> 8; buf[1] = x0; buf[2] = x1 >> 8; buf[3] = x1;
    dc_data(); spi_write(buf, 4);
    send_cmd(0x2B);                                  // RASET — діапазон рядків
    buf[0] = y0 >> 8; buf[1] = y0; buf[2] = y1 >> 8; buf[3] = y1;
    dc_data(); spi_write(buf, 4);
}

void fill_rect(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1, uint16_t color) {
    set_window(x0, y0, x1, y1);
    send_cmd(0x2C);                                  // RAMWR — писати в пам'ять
    uint8_t px[2] = { color >> 8, color };           // RGB565, старший байт уперед
    dc_data();
    uint32_t count = (uint32_t)(x1 - x0 + 1) * (y1 - y0 + 1);
    for (uint32_t i = 0; i < count; i++)
        spi_write(px, 2);                            // контролер сам розкладе по вікну
}
