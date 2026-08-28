typedef struct {
    void (*spi_select)(bool select);
    void (*spi_transmit)(const uint8_t *data, size_t len);
} health_fram_driver_t;

#define FRAM_CMD_WREN  0x06
#define FRAM_CMD_WRITE 0x02

void health_fram_write_entry(const health_fram_driver_t *driver, 
                             uint32_t address, 
                             const health_blackbox_entry_t *entry) {
    if (!driver || !driver->spi_select || !driver->spi_transmit || !entry) {
        return;
    }

    // 1. Дозвіл запису (WREN)
    uint8_t wren = FRAM_CMD_WREN;
    driver->spi_select(true);
    driver->spi_transmit(&wren, 1);
    driver->spi_select(false);

    // 2. Команда запису з 24-бітною адресою
    uint8_t cmd_hdr[4] = {
        FRAM_CMD_WRITE,
        (uint8_t)((address >> 16) & 0xFF),
        (uint8_t)((address >> 8) & 0xFF),
        (uint8_t)(address & 0xFF)
    };

    driver->spi_select(true);
    driver->spi_transmit(cmd_hdr, sizeof(cmd_hdr));
    driver->spi_transmit((const uint8_t *)entry, sizeof(health_blackbox_entry_t));
    driver->spi_select(false);
}
