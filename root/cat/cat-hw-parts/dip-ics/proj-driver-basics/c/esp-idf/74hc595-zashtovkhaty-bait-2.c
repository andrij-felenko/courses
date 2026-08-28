// Той самий 74HC595, але байт жене апаратний SPI — швидко.
// DS(14)→MOSI (GPIO23), SHCP(11)→SCK (GPIO18), STCP(12)→GPIO5 (засувка вручну).
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LATCH  GPIO_NUM_5           // STCP смикаємо вручну; MOSI та SCK бере на себе SPI
static spi_device_handle_t sr;

static void write_byte(uint8_t value) {
    spi_transaction_t t = { .length = 8,              // довжина в БІТАХ
                            .flags = SPI_TRANS_USE_TXDATA, .tx_data = { value } };
    gpio_set_level(LATCH, 0);
    spi_device_polling_transmit(sr, &t);              // весь байт одним апаратним пострілом
    gpio_set_level(LATCH, 1);
}

void app_main(void) {
    gpio_config_t io = { .pin_bit_mask = 1ULL << LATCH, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&io);

    spi_bus_config_t bus = { .mosi_io_num = 23, .miso_io_num = -1, .sclk_io_num = 18,
                             .quadwp_io_num = -1, .quadhd_io_num = -1 };
    spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);

    spi_device_interface_config_t dev = {
        .clock_speed_hz = 8 * 1000 * 1000,   // 8 МГц
        .mode = 0,                            // SPI-режим 0, як і треба 595-му
        .spics_io_num = -1,                   // CS не потрібен: у 595 його роль грає засувка
        .queue_size = 1,
    };
    spi_bus_add_device(SPI2_HOST, &dev, &sr);

    while (1) {
        write_byte(0b10101010);  vTaskDelay(pdMS_TO_TICKS(300));   // ввімкнули парні виходи
        write_byte(0b01010101);  vTaskDelay(pdMS_TO_TICKS(300));   // непарні
    }
}
