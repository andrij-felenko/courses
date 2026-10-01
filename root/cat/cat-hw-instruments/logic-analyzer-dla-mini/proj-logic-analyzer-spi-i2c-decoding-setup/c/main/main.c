#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/spi_master.h"
#include "esp_log.h"

static const char *TAG = "DLA_TEST_GEN";

// Призначення виводів GPIO для шини I2C
#define I2C_MASTER_SCL_IO    22
#define I2C_MASTER_SDA_IO    21
#define I2C_MASTER_FREQ_HZ   100000
#define I2C_SLAVE_ADDR       0x3C

// Призначення виводів GPIO для шини SPI
#define SPI_MOSI_IO          23
#define SPI_MISO_IO          19
#define SPI_SCLK_IO          18
#define SPI_CS_IO            5
#define SPI_CLOCK_SPEED_HZ   1000000

static i2c_master_dev_handle_t dev_handle_i2c;
static spi_device_handle_t dev_handle_spi;

// Ініціалізація Master-шини I2C (драйвер ESP-IDF v5.x)
static esp_err_t init_i2c_master(void)
{
    i2c_master_bus_config_t bus_config = {
        .i2c_port = I2C_NUM_0,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };

    i2c_master_bus_handle_t bus_handle;
    esp_err_t ret = i2c_new_master_bus(&bus_config, &bus_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка створення I2C шини: %s", esp_err_to_name(ret));
        return ret;
    }

    i2c_device_config_t dev_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = I2C_SLAVE_ADDR,
        .scl_speed_hz = I2C_MASTER_FREQ_HZ,
    };

    ret = i2c_master_bus_add_device(bus_handle, &dev_config, &dev_handle_i2c);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка додавання пристрою I2C: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "Ініціалізація I2C (SCL: %d, SDA: %d, %d Гц) успішна",
             I2C_MASTER_SCL_IO, I2C_MASTER_SDA_IO, I2C_MASTER_FREQ_HZ);
    return ESP_OK;
}

// Ініціалізація Master-шини SPI
static esp_err_t init_spi_master(void)
{
    spi_bus_config_t bus_config = {
        .mosi_io_num = SPI_MOSI_IO,
        .miso_io_num = SPI_MISO_IO,
        .sclk_io_num = SPI_SCLK_IO,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 64,
    };

    esp_err_t ret = spi_bus_initialize(SPI2_HOST, &bus_config, SPI_DMA_CH_AUTO);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації шини SPI: %s", esp_err_to_name(ret));
        return ret;
    }

    spi_device_interface_config_t dev_config = {
        .clock_speed_hz = SPI_CLOCK_SPEED_HZ,
        .mode = 0,                             // CPOL=0, CPHA=0
        .spics_io_num = SPI_CS_IO,
        .queue_size = 7,
    };

    ret = spi_bus_add_device(SPI2_HOST, &dev_config, &dev_handle_spi);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка додавання пристрою SPI: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "Ініціалізація SPI (SCLK: %d, MOSI: %d, CS: %d) успішна",
             SPI_SCLK_IO, SPI_MOSI_IO, SPI_CS_IO);
    return ESP_OK;
}

// Періодична відправка тестових пакетів для захоплення логічним аналізатором
static void send_test_packets(void)
{
    uint8_t i2c_data[] = {0x00, 0xAA, 0x55, 0xFF};
    uint8_t spi_data[] = {0xDE, 0xAD, 0xBE, 0xEF};
    uint8_t spi_rx_buf[sizeof(spi_data)] = {0};

    // 1. Відправка через шину I2C
    esp_err_t ret = i2c_master_transmit(dev_handle_i2c, i2c_data, sizeof(i2c_data), 100);
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "I2C пакет відправлено успішно");
    } else {
        ESP_LOGW(TAG, "I2C транзакція завершена (без NACK підтвердження): %s", esp_err_to_name(ret));
    }

    // 2. Відправка через шину SPI
    spi_transaction_t t = {
        .length = sizeof(spi_data) * 8,
        .tx_buffer = spi_data,
        .rx_buffer = spi_rx_buf,
    };

    ret = spi_device_transmit(dev_handle_spi, &t);
    if (ret == ESP_OK) {
        ESP_LOGI(TAG, "SPI пакет [0xDE, 0xAD, 0xBE, 0xEF] передано успішно");
    } else {
        ESP_LOGE(TAG, "Помилка передачі SPI: %s", esp_err_to_name(ret));
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "Запуск генератора тестового цифрового трафіку для WeAct DLA Mini");

    if (init_i2c_master() != ESP_OK || init_spi_master() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка конфігурації периферії");
        return;
    }

    uint32_t packet_count = 0;
    while (1) {
        ESP_LOGI(TAG, "--- Пакет #%" PRIu32 " ---", ++packet_count);
        send_test_packets();
        vTaskDelay(pdMS_TO_TICKS(100)); // Затримка 100 мс між пакетами
    }
}
