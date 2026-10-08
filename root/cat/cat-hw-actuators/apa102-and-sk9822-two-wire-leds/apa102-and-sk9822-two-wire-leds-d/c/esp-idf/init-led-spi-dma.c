#include "driver/spi_master.h"
#include "esp_err.h"

// Ініціалізація апаратної шини SPI з підтримкою DMA для світлодіодів APA102/SK9822
esp_err_t init_led_spi_dma(spi_device_handle_t *spi_handle) {
    spi_bus_config_t buscfg = {
        .mosi_io_num = 23,       // Підключення до лінії SDI (MOSI)
        .miso_io_num = -1,       // Зчитування MISO не використовується
        .sclk_io_num = 18,       // Підключення до лінії CKI (SCLK)
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4096  // Максимальний розмір буфера DMA в байтах
    };
    
    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 10 * 1000 * 1000, // Тактова частота шини 10 МГц
        .mode = 0,                           // Режим SPI 0 (CPOL=0, CPHA=0)
        .spics_io_num = -1,                  // Лінія Chip Select не потрібна
        .queue_size = 7                      // Глибина черги транзакцій
    };
    
    // Ініціалізація шини SPI з автоматичним вибором каналу DMA
    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) return ret;
    
    return spi_bus_add_device(SPI2_HOST, &devcfg, spi_handle);
}
