#include "driver/spi_master.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static spi_device_handle_t dev;
static const char *TAG = "spi";

// прочитати один регістр: шлемо адресу, приймаємо відповідь
static uint8_t spi_read_reg(uint8_t reg) {
    uint8_t tx[2] = { reg | 0x80, 0x00 };   // старший біт = «читання» (типово)
    uint8_t rx[2] = { 0 };
    spi_transaction_t t = { .length = 16, .tx_buffer = tx, .rx_buffer = rx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(dev, &t));  // CS смикає драйвер сам
    return rx[1];                           // відповідь прийшла в другому байті
}

void app_main(void) {
    const spi_bus_config_t bus = {
        .mosi_io_num = 23, .miso_io_num = 19, .sclk_io_num = 18,
        .quadwp_io_num = -1, .quadhd_io_num = -1,
    };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));

    // швидкість, режим і лінія вибору — з даташита пристрою:
    const spi_device_interface_config_t cfg = {
        .clock_speed_hz = 1000000, .mode = 0,   // MSB-first — типово
        .spics_io_num = 5, .queue_size = 1,
    };
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &cfg, &dev));

    while (1) {
        ESP_LOGI(TAG, "%02X", spi_read_reg(0x0F));   // умовний регістр «хто ти»
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
