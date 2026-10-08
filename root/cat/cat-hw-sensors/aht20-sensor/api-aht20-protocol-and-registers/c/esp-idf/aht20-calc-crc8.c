#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c.h"

#define AHT20_I2C_ADDR       0x38
#define AHT20_CMD_INIT       0xBE
#define AHT20_CMD_TRIGGER    0xAC
#define AHT20_CMD_SOFT_RESET 0xBA

#define AHT20_STATUS_BUSY    (1 << 7)
#define AHT20_STATUS_CALIBR  (1 << 3)

// Обчислення CRC8 для перевірки цілісності кадру AHT20
uint8_t aht20_calc_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

// Ініціалізація давача AHT20
esp_err_t aht20_init(i2c_port_t i2c_num) {
    uint8_t status = 0;
    esp_err_t err = i2c_master_write_read_device(i2c_num, AHT20_I2C_ADDR, NULL, 0, &status, 1, pdMS_TO_TICKS(100));
    if (err != ESP_OK) return err;

    // Перевірка прапорця калібрування
    if ((status & AHT20_STATUS_CALIBR) == 0) {
        uint8_t init_cmd[3] = {AHT20_CMD_INIT, 0x08, 0x00};
        err = i2c_master_write_to_device(i2c_num, AHT20_I2C_ADDR, init_cmd, 3, pdMS_TO_TICKS(100));
        if (err != ESP_OK) return err;
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    return ESP_OK;
}

// Прочитати вимірювання відносної вологості та температури
esp_err_t aht20_read_data(i2c_port_t i2c_num, float *humidity, float *temperature) {
    uint8_t trigger_cmd[3] = {AHT20_CMD_TRIGGER, 0x33, 0x00};
    esp_err_t err = i2c_master_write_to_device(i2c_num, AHT20_I2C_ADDR, trigger_cmd, 3, pdMS_TO_TICKS(100));
    if (err != ESP_OK) return err;

    // Регламентована затримка виконання вимірювання
    vTaskDelay(pdMS_TO_TICKS(80));

    // Опитування біта Busy з таймаутом
    uint8_t buffer[7] = {0};
    int retries = 10;
    while (retries--) {
        err = i2c_master_read_from_device(i2c_num, AHT20_I2C_ADDR, buffer, 7, pdMS_TO_TICKS(100));
        if (err == ESP_OK && (buffer[0] & AHT20_STATUS_BUSY) == 0) {
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }

    if (buffer[0] & AHT20_STATUS_BUSY) {
        return ESP_ERR_TIMEOUT;
    }

    // Перевірка контрольної суми CRC8
    uint8_t calculated_crc = aht20_calc_crc8(buffer, 6);
    if (calculated_crc != buffer[6]) {
        return ESP_ERR_INVALID_CRC;
    }

    // Розпакування 20-бітних полів
    uint32_t raw_humidity = ((uint32_t)buffer[1] << 12) | ((uint32_t)buffer[2] << 4) | ((uint32_t)buffer[3] >> 4);
    uint32_t raw_temperature = (((uint32_t)buffer[3] & 0x0F) << 16) | ((uint32_t)buffer[4] << 8) | (uint32_t)buffer[5];

    // Переведення в фізичні величини
    *humidity = ((float)raw_humidity / 1048576.0f) * 100.0f;
    *temperature = ((float)raw_temperature / 1048576.0f) * 200.0f - 50.0f;

    return ESP_OK;
}
