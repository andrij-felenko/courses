#include "driver/spi_master.h"

void configure_spi_device(spi_device_handle_t *handle) {
    spi_device_interface_config_t devcfg = {
        .command_bits = 8,
        .address_bits = 24,
        .dummy_bits = 8,                // Холості такти Dummy для компенсації t_V
        .mode = 0,                      // SPI Mode 0 (CPOL=0, CPHA=0)
        .clock_speed_hz = 20 * 1000 * 1000, // 20 МГц
        .input_delay_ns = 15,           // Очікувана кругова затримка MISO (Round-Trip)
        .spics_io_num = 15,             // Вивід CS
        .flags = SPI_DEVICE_NO_DUMMY,   // Прапорці керування
        .queue_size = 7,
    };
    spi_bus_add_device(SPI2_HOST, &devcfg, handle);
}
