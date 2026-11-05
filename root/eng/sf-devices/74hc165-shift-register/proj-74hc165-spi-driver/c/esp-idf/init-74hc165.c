#include "driver/spi_master.h"
#include "driver/gpio.h"

#define PIN_PL 5
#define PIN_MISO 19
#define PIN_SCK 18

spi_device_handle_t spi;

void init_74hc165() {
    gpio_set_direction(PIN_PL, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_PL, 1);

    spi_bus_config_t buscfg = {
        .miso_io_num = PIN_MISO,
        .mosi_io_num = -1,
        .sclk_io_num = PIN_SCK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1
    };
    spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 1000000,
        .mode = 0,
        .spics_io_num = -1,
        .queue_size = 1
    };
    spi_bus_add_device(SPI2_HOST, &devcfg, &spi);
}

uint8_t read_74hc165() {
    gpio_set_level(PIN_PL, 0);
    gpio_set_level(PIN_PL, 1);

    uint8_t data = 0;
    spi_transaction_t t = {
        .length = 8,
        .rx_buffer = &data
    };
    spi_device_polling_transmit(spi, &t);
    return data;
}
