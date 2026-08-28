#include "driver/spi_master.h"
#include "esp_log.h"
// CS# драйвер опускає й піднімає сам на час транзакції
uint8_t tx[4] = { 0x9F, 0, 0, 0 };  // команда «назвись» + три байти-пустушки
uint8_t rx[4] = { 0 };
spi_transaction_t t = {
    .length    = 8 * sizeof(tx),    // довжина в БІТАХ, не байтах
    .tx_buffer = tx,
    .rx_buffer = rx,
};
ESP_ERROR_CHECK(spi_device_polling_transmit(flash, &t));   // flash — spi_device_handle_t
ESP_LOGI(TAG, "JEDEC ID: %02X %02X %02X", rx[1], rx[2], rx[3]);  // виробник, тип, об'єм
