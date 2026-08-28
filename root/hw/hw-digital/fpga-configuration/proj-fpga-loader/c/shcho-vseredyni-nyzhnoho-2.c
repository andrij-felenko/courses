#define BITSTREAM_FLASH_ADDR  0x000000u     // де у флеш лежить бітстрім
#define BITSTREAM_TOTAL_LEN   0x080000u     // його довжина в байтах (знаємо наперед)

static uint32_t f_addr = BITSTREAM_FLASH_ADDR;
static size_t   f_left = BITSTREAM_TOTAL_LEN;

// spi_flash_read — ваш драйвер: команда 0x03 + 24-бітна адреса, тоді читання.
extern void spi_flash_read(uint32_t addr, uint8_t *buf, size_t len);

static size_t bitstream_read(uint8_t *buf, size_t len)
{
    if (f_left == 0) return 0;
    size_t take = (f_left < len) ? f_left : len;
    spi_flash_read(f_addr, buf, take);
    f_addr += take;
    f_left -= take;
    return take;
}
