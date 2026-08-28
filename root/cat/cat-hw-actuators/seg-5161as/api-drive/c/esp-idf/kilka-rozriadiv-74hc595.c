#include "driver/spi_master.h"

#define PIN_DATA   GPIO_NUM_11   // DS   (SER)   → пін 14 регістра, це MOSI
#define PIN_CLOCK  GPIO_NUM_12   // SHCP (SRCLK) → пін 11 регістра, це SCLK
#define PIN_LATCH  GPIO_NUM_10   // STCP (RCLK)  → пін 12 регістра, це CS

static spi_device_handle_t hc595;

static void hc595_begin(void) {
  spi_bus_config_t bus = {
    .mosi_io_num = PIN_DATA, .miso_io_num = -1, .sclk_io_num = PIN_CLOCK,
    .quadwp_io_num = -1, .quadhd_io_num = -1, .max_transfer_sz = 4,
  };
  ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_DISABLED));
  spi_device_interface_config_t dev = {
    .clock_speed_hz = 1000000,     // 1 МГц; 595 витримує значно більше
    .mode           = 0,           // біт міняється на спаді, читається на фронті
    .spics_io_num   = PIN_LATCH,   // CS підніметься після байта → «клац» засувки
    .queue_size     = 1,
  };
  ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &dev, &hc595));
}

static void show_mask_595(uint8_t mask) {
  spi_transaction_t t = {
    .flags    = SPI_TRANS_USE_TXDATA,
    .length   = 8,                 // ДОВЖИНА В БІТАХ, не в байтах
    .tx_data  = { mask },
  };
  ESP_ERROR_CHECK(spi_device_transmit(hc595, &t));
}

void app_main(void) {
  hc595_begin();
  while (true) {
    show_mask_595(SA|SB|SC|SD|SG);            // «3»
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}
