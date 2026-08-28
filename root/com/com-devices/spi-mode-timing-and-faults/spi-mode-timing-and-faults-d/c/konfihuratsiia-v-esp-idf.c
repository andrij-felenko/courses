#include "driver/spi_master.h"

spi_device_handle_t spi_dev;
spi_device_interface_config_t devcfg = {
    .clock_speed_hz = 10 * 1000 * 1000, // Тактова частота 10 МГц
    .mode = 0,                          // Mode 0 (CPOL=0, CPHA=0)
    .spics_io_num = 5,                  // Вивід Chip Select (GPIO 5)
    .queue_size = 7,
};
// Реєстрація пристрою на шині SPI2_HOST
spi_bus_add_device(SPI2_HOST, &devcfg, &spi_dev);
