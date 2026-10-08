#include <stdio.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2c.h"
#include "esp_log.h"

#define I2C_MASTER_NUM         I2C_NUM_0
#define SHT30_I2C_ADDR         0x44
#define CMD_HEATER_ENABLE      0x306D
#define CMD_HEATER_DISABLE     0x3066
#define CMD_READ_STATUS        0xF32D

static const char *TAG = "SHT30_HEATER";

// Надсилання 16-бітної команди до давача SHT30 по шині I2C
static esp_err_t sht30_send_cmd(uint16_t cmd) {
    uint8_t buf[2] = { (uint8_t)(cmd >> 8), (uint8_t)(cmd & 0xFF) };
    return i2c_master_write_to_device(I2C_MASTER_NUM, SHT30_I2C_ADDR, buf, 2, pdMS_TO_TICKS(100));
}

// Перевірка стану мікронагрівача за регістром стану (біт 13)
static esp_err_t sht30_is_heater_active(bool *active) {
    uint8_t cmd[2] = { (uint8_t)(CMD_READ_STATUS >> 8), (uint8_t)(CMD_READ_STATUS & 0xFF) };
    uint8_t data[3]; // 2 байти стану + 1 байт CRC-8
    esp_err_t ret = i2c_master_write_read_device(I2C_MASTER_NUM, SHT30_I2C_ADDR, cmd, 2, data, 3, pdMS_TO_TICKS(100));
    if (ret == ESP_OK) {
        uint16_t status = ((uint16_t)data[0] << 8) | data[1];
        *active = (status & (1 << 13)) != 0;
    }
    return ret;
}

// Виконання процедури регенерації полімеру після конденсації
void sht30_dew_recovery_sequence(void) {
    ESP_LOGI(TAG, "Виявлено насичення вологою. Вмикаємо мікронагрівач...");
    if (sht30_send_cmd(CMD_HEATER_ENABLE) == ESP_OK) {
        vTaskDelay(pdMS_TO_TICKS(2000)); // Нагрів протягом 2 секунд
        
        bool active = false;
        if (sht30_is_heater_active(&active) == ESP_OK && active) {
            ESP_LOGI(TAG, "Статус регістра підтверджує активний нагрів кристала.");
        }

        ESP_LOGI(TAG, "Вимикаємо мікронагрівач...");
        sht30_send_cmd(CMD_HEATER_DISABLE);
        
        ESP_LOGI(TAG, "Пауза охолодження кристала (5 секунд)...");
        vTaskDelay(pdMS_TO_TICKS(5000)); // Затримка для вирівнювання температури
        ESP_LOGI(TAG, "Давач відновлено для штатного моніторингу.");
    }
}
