#include "driver/spi_master.h"

static spi_device_handle_t dev;

void spi_init(void) {
  spi_bus_config_t bus = {
    .sclk_io_num = 12, .miso_io_num = 13, .mosi_io_num = 11,   // свої ноги
    .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 4096,
  };
  ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));

  spi_device_interface_config_t devcfg = {
    .clock_speed_hz = 10 * 1000 * 1000,   // 10 МГц
    .mode = 0,                            // CPOL=0, CPHA=0 — те саме, що SPI_MODE0
    .spics_io_num = 10,                   // CS смикає сам драйвер
    .queue_size = 1,
  };
  ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &dev));
}

// один обмін байтом з веденим пристроєм
uint8_t spi_exchange(uint8_t out) {
  uint8_t in = 0;
  spi_transaction_t t = { .length = 8, .tx_buffer = &out, .rx_buffer = &in };
  ESP_ERROR_CHECK(spi_device_transmit(dev, &t));   // одночасно шлемо out і читаємо in
  return in;
}
