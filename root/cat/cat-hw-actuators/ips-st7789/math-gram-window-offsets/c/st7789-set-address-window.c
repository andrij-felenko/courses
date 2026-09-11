#include <stdint.h>

/* Апаратні зсуви для нульової орієнтації модуля */
static const uint16_t COL_OFFSET = 0;
static const uint16_t ROW_OFFSET = 0;

/* Низькорівневі виклики інтерфейсу SPI */
void spi_write_command(uint8_t cmd);
void spi_write_data(uint8_t data);

/* Встановлення прямокутного вікна оновлення в GRAM */
void st7789_set_address_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
    /* Трансляція логічних координат програми у фізичні адреси пам'яті */
    uint16_t xs = x1 + COL_OFFSET;
    uint16_t xe = x2 + COL_OFFSET;
    uint16_t ys = y1 + ROW_OFFSET;
    uint16_t ye = y2 + ROW_OFFSET;

    /* Встановлення меж стовпчиків (CASET) */
    spi_write_command(0x2A);
    spi_write_data((uint8_t)(xs >> 8));
    spi_write_data((uint8_t)(xs & 0xFF));
    spi_write_data((uint8_t)(xe >> 8));
    spi_write_data((uint8_t)(xe & 0xFF));

    /* Встановлення меж рядків (RASET) */
    spi_write_command(0x2B);
    spi_write_data((uint8_t)(ys >> 8));
    spi_write_data((uint8_t)(ys & 0xFF));
    spi_write_data((uint8_t)(ye >> 8));
    spi_write_data((uint8_t)(ye & 0xFF));

    /* Підготовка до прийому пікселів (RAMWR) */
    spi_write_command(0x2C);
}
