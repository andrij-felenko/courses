#include "driver/i2c.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define AHT20_I2C_ADDR       0x38
#define AHT20_CMD_INIT       0xBE
#define AHT20_CMD_TRIGGER    0xAC
#define AHT20_CMD_SOFTRESET  0xBA

// Обчислення контрольної суми CRC-8 за поліномом 0x31 (початкове значення 0xFF)
static uint8_t aht20_calculate_crc8(const uint8_t *data, size_t len) {
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

esp_err_t aht20_read_data(i2c_port_t i2c_num, float *humidity, float *temperature) {
    // 1. Відправка тригера вимірювання: 0xAC, 0x33, 0x00
    uint8_t trigger_cmd[3] = {AHT20_CMD_TRIGGER, 0x33, 0x00};
    esp_err_t ret = i2c_master_write_to_device(i2c_num, AHT20_I2C_ADDR, trigger_cmd, sizeof(trigger_cmd), pdMS_TO_TICKS(100));
    if (ret != ESP_OK) {
        return ret;
    }

    // 2. Пауза 80 мс на виконання перетворення АЦП
    vTaskDelay(pdMS_TO_TICKS(80));

    // 3. Зчитування 7 байтів (статус + 5 байтів даних + CRC-8)
    uint8_t data[7] = {0};
    ret = i2c_master_read_from_device(i2c_num, AHT20_I2C_ADDR, data, sizeof(data), pdMS_TO_TICKS(100));
    if (ret != ESP_OK) {
        return ret;
    }

    // 4. Перевірка статусного байта (Busy bit[7] та Calibrated bit[3])
    uint8_t status = data[0];
    if (status & 0x80) { // Busy bit[7] == 1
        ESP_LOGE("AHT20", "Давач зайнятий вимірюванням");
        return ESP_ERR_INVALID_STATE;
    }
    if (!(status & 0x08)) { // Calibrated bit[3] == 0
        ESP_LOGW("AHT20", "Давач не відкалібрований, потрібна ініціалізація 0xBE");
        return ESP_ERR_INVALID_STATE;
    }

    // 5. Валідація контрольної суми CRC-8 по перших 6 байтах
    uint8_t calc_crc = aht20_calculate_crc8(data, 6);
    if (calc_crc != data[6]) {
        ESP_LOGE("AHT20", "Помилка CRC-8: зчитано 0x%02X, обчислено 0x%02X", data[6], calc_crc);
        return ESP_ERR_INVALID_CRC;
    }

    // 6. Перетворення 20-бітних даних у фізичні значення
    uint32_t raw_humidity = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | (data[3] >> 4);
    uint32_t raw_temp = (((uint32_t)data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];

    *humidity = ((float)raw_humidity / 1048576.0f) * 100.0f;
    *temperature = ((float)raw_temp / 1048576.0f) * 200.0f - 50.0f;

    return ESP_OK;
}
