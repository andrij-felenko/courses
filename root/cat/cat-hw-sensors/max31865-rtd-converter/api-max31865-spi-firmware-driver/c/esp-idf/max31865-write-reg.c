#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_err.h"
#include "esp_log.h"

#define MAX31865_REG_CONFIG       0x00
#define MAX31865_REG_RTD_MSB      0x01
#define MAX31865_REG_RTD_LSB      0x02
#define MAX31865_REG_FAULT_STATUS 0x07

#define MAX31865_CONFIG_VBIAS     (1 << 7)
#define MAX31865_CONFIG_1SHOT     (1 << 5)
#define MAX31865_CONFIG_3WIRE     (1 << 4)
#define MAX31865_CONFIG_FAULT_CLR (1 << 1)
#define MAX31865_CONFIG_FILTER_50 (1 << 0)

static const char *TAG = "MAX31865";

// Запис байта в регістр MAX31865
esp_err_t max31865_write_reg(spi_device_handle_t spi, uint8_t reg, uint8_t value) {
    uint8_t tx_buf[2] = { reg | 0x80, value }; // A7 = 1 для запису
    spi_transaction_t t = {
        .length = 16,
        .tx_buffer = tx_buf
    };
    return spi_device_transmit(spi, &t);
}

// Пакетне зчитування регістрів (Burst Read)
esp_err_t max31865_read_regs(spi_device_handle_t spi, uint8_t start_reg, uint8_t *rx_buf, size_t len) {
    uint8_t tx_buf[1] = { start_reg & 0x7F }; // A7 = 0 для читання
    spi_transaction_t t_addr = {
        .length = 8,
        .tx_buffer = tx_buf,
        .flags = SPI_TRANS_CS_KEEP_ACTIVE
    };
    esp_err_t ret = spi_device_transmit(spi, &t_addr);
    if (ret != ESP_OK) return ret;

    spi_transaction_t t_data = {
        .length = len * 8,
        .rx_buffer = rx_buf
    };
    return spi_device_transmit(spi, &t_data);
}

// Запуск одноразового вимірювання та зчитування 15-бітного коду
esp_err_t max31865_read_raw(spi_device_handle_t spi, uint16_t *rtd_code, bool *fault) {
    // 1. Увімкнення VBIAS та запуск 1-Shot
    uint8_t cfg = MAX31865_CONFIG_VBIAS | MAX31865_CONFIG_1SHOT;
    esp_err_t ret = max31865_write_reg(spi, MAX31865_REG_CONFIG, cfg);
    if (ret != ESP_OK) return ret;

    // 2. Очікування завершення конверсії (25 мс для фільтра 60 Гц)
    vTaskDelay(pdMS_TO_TICKS(25));

    // 3. Зчитування MSB та LSB за один burst-сеанс
    uint8_t raw_bytes[2] = {0};
    ret = max31865_read_regs(spi, MAX31865_REG_RTD_MSB, raw_bytes, 2);
    if (ret != ESP_OK) return ret;

    uint16_t raw_16 = ((uint16_t)raw_bytes[0] << 8) | raw_bytes[1];
    *rtd_code = raw_16 >> 1;
    *fault = (raw_16 & 0x01) != 0;

    return ESP_OK;
}

// Перевірка та розшифровка прапорців помилок
void max31865_check_and_clear_fault(spi_device_handle_t spi) {
    uint8_t fault_status = 0;
    max31865_read_regs(spi, MAX31865_REG_FAULT_STATUS, &fault_status, 1);

    if (fault_status != 0) {
        ESP_LOGE(TAG, "Виявлено апаратний збій! Fault Register 0x07: 0x%02X", fault_status);
        if (fault_status & (1 << 7)) ESP_LOGE(TAG, " - Перевищено верхній поріг (High Threshold)");
        if (fault_status & (1 << 6)) ESP_LOGE(TAG, " - Перевищено нижній поріг (Low Threshold)");
        if (fault_status & (1 << 5)) ESP_LOGE(TAG, " - REFIN- > 0.85*VBIAS (обрив FORCE-)");
        if (fault_status & (1 << 4)) ESP_LOGE(TAG, " - REFIN- < 0.85*VBIAS (дефект Rref)");
        if (fault_status & (1 << 3)) ESP_LOGE(TAG, " - RTDIN- < 0.85*VBIAS (обрив RTD)");
        if (fault_status & (1 << 2)) ESP_LOGE(TAG, " - Перенапруга / Знижена напруга (Over/Under Voltage)");

        // Очищення прапорців помилки
        max31865_write_reg(spi, MAX31865_REG_CONFIG, MAX31865_CONFIG_FAULT_CLR);
    }
}
