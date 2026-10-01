#include <stdio.h>
#include <stdint.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "spi_safe_init";

// Маска заблокованих виводів GPIO (GPIO30..GPIO37 для Octal SPI Flash/PSRAM)
#define OCTAL_SPI_BLOCKED_GPIO_MASK ((1ULL << 30) | (1ULL << 31) | (1ULL << 32) | \
                                     (1ULL << 33) | (1ULL << 34) | (1ULL << 35) | \
                                     (1ULL << 36) | (1ULL << 37))

static bool is_gpio_blocked_for_octal_spi(int gpio_num)
{
    if (gpio_num < 0) return false; // Непризначений вивід (-1)
    return (OCTAL_SPI_BLOCKED_GPIO_MASK & (1ULL << gpio_num)) != 0;
}

esp_err_t safe_spi_bus_initialize(spi_host_device_t host, int mosi, int miso, int sclk, int cs)
{
    if (is_gpio_blocked_for_octal_spi(mosi) || is_gpio_blocked_for_octal_spi(miso) ||
        is_gpio_blocked_for_octal_spi(sclk) || is_gpio_blocked_for_octal_spi(cs)) {
        ESP_LOGE(TAG, "Помилка: Спроба залучити заблокований вивід Octal SPI (GPIO30..37)!");
        return ESP_ERR_INVALID_ARG;
    }

    spi_bus_config_t buscfg = {
        .mosi_io_num = mosi,
        .miso_io_num = miso,
        .sclk_io_num = sclk,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4092
    };

    return spi_bus_initialize(host, &buscfg, SPI_DMA_CH_AUTO);
}
