#include "driver/spi_master.h"
#include "driver/gpio.h"

#define PIN_NUM_MOSI 23
#define PIN_NUM_CLK  18
#define PIN_NUM_CS   5
#define PIN_NUM_DC   2

static spi_device_handle_t spi_display;

// Ініціалізація шини SPI та реєстрація дисплея з частотою 40 МГц
void st7789_spi_init(void)
{
    // Налаштування виводу керування режимом DC (команда/дані)
    gpio_config_t dc_io_conf = {
        .pin_bit_mask = (1ULL << PIN_NUM_DC),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&dc_io_conf);

    spi_bus_config_t buscfg = {
        .miso_io_num = -1,
        .mosi_io_num = PIN_NUM_MOSI,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 240 * 240 * 2,
    };

    // Налаштування пристрою: режим 0 (CPOL=0, CPHA=0), тактова частота 40 МГц
    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 40 * 1000 * 1000, // 40 МГц — стабільна межа для друкованої плати
        .mode = 0,                          // Mode 0: вибірка на наростаючому фронті SCL
        .spics_io_num = PIN_NUM_CS,         // Вивід CS (-1 для модулів із заземленим CS)
        .queue_size = 7,
        .cs_ena_pretrans = 1,               // Апаратне випередження CS перед початком тактування
    };

    spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO);
    spi_bus_add_device(SPI2_HOST, &devcfg, &spi_display);
}

// Передача байта команди дисплею
void st7789_write_command(uint8_t cmd)
{
    // Лінія DC виставляється в 0 заздалегідь, гарантуючи t_ast >= 10 нс
    gpio_set_level(PIN_NUM_DC, 0);

    spi_transaction_t transaction = {
        .length = 8,
        .tx_buffer = &cmd,
    };
    spi_device_polling_transmit(spi_display, &transaction);
}

// Передача масиву піксельних даних у відеопам'ять
void st7789_write_data(const uint8_t *data, size_t length)
{
    // Лінія DC виставляється в 1 перед початком тактування даних
    gpio_set_level(PIN_NUM_DC, 1);

    spi_transaction_t transaction = {
        .length = length * 8,
        .tx_buffer = data,
    };
    spi_device_polling_transmit(spi_display, &transaction);
}
