#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "aht20_bmp280.h"

/**
 * @file main.c
 * @brief Демонстраційний приклад роботи неблокувального драйвера AHT20 + BMP280.
 */

/* Симуляція калібрувальних коефіцієнтів BMP280 */
static uint8_t g_mock_bmp_calib[24] = {
    0x70, 0x6D, 0xC0, 0x65, 0x32, 0x00, 0x50, 0x90,
    0xD0, 0xD6, 0x55, 0x0B, 0x2A, 0x00, 0xF9, 0xFF,
    0xAC, 0x26, 0x0A, 0x00, 0xBD, 0x8C, 0x05, 0x9C
};
static uint8_t g_mock_bmp_data[6] = {0x50, 0x00, 0x00, 0x80, 0x00, 0x00};

/* Симуляція низькорівневої адаптерної функції I2C Read */
static sensor_status_t mock_i2c_read(uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, size_t len) {
    (void)reg_addr;
    if (dev_addr == AHT20_I2C_ADDR) {
        /* Симуляція сирого відліку AHT20 та обчислення дійсного CRC-8 */
        data[0] = 0x18; /* Status (calibrated, not busy) */
        data[1] = 0x80; /* Humidity MSB */
        data[2] = 0x00; /* Humidity LSB */
        data[3] = 0x06; /* Hum/Temp mid */
        data[4] = 0x66; /* Temp MSB */
        data[5] = 0x66; /* Temp LSB */

        /* Динамічний обчислювач CRC для коректного проходження перевірки */
        uint8_t crc = 0xFF;
        for (size_t i = 0; i < 6; i++) {
            crc ^= data[i];
            for (uint8_t b = 0; b < 8; b++) {
                if (crc & 0x80) crc = (crc << 1) ^ 0x31;
                else crc <<= 1;
            }
        }
        data[6] = crc;
        return SENSOR_OK;
    } else if (dev_addr == BMP280_I2C_ADDR) {
        if (reg_addr == BMP280_REG_CHIP_ID) {
            data[0] = BMP280_CHIP_ID_VALUE;
            return SENSOR_OK;
        } else if (reg_addr == BMP280_REG_CALIB_START && len == 24) {
            memcpy(data, g_mock_bmp_calib, 24);
            return SENSOR_OK;
        } else if (reg_addr == BMP280_REG_STATUS) {
            data[0] = 0x00; /* Measuring finished */
            return SENSOR_OK;
        } else if (reg_addr == BMP280_REG_PRESS_MSB && len == 6) {
            memcpy(data, g_mock_bmp_data, 6);
            return SENSOR_OK;
        }
    }
    return SENSOR_OK;
}

/* Симуляція низькорівневої адаптерної функції I2C Write */
static sensor_status_t mock_i2c_write(uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, size_t len) {
    (void)dev_addr;
    (void)reg_addr;
    (void)data;
    (void)len;
    return SENSOR_OK;
}

int main(void) {
    printf("=== Запуск неблокувального драйвера AHT20 + BMP280 ===\n");

    sensor_driver_t climate_sensor;
    uint32_t simulated_sys_time_ms = 0;

    /* Ініціалізація драйвера з інтервалом опитування 1000 мс */
    sensor_status_t status = sensor_driver_init(&climate_sensor,
                                                mock_i2c_read,
                                                mock_i2c_write,
                                                1000);
    if (status != SENSOR_OK) {
        printf("Помилка ініціалізації драйвера сенсорів! Код: %d\n", status);
        return 1;
    }

    printf("Драйвер успішно ініціалізовано. Старт головного неблокувального циклу.\n");

    /* Імітація головного неблокувального суперциклу мікроконтролера */
    for (int cycle = 0; cycle < 3500; cycle += 10) {
        simulated_sys_time_ms += 10; /* Імітація кроку системного таймера Systick 10 мс */

        /* 1. Періодичний виклик FSM драйвера без затримки циклу execution */
        sensor_driver_update_fsm(&climate_sensor, simulated_sys_time_ms);

        /* 2. Обробка готовності нових метеоданих */
        climate_data_t climate;
        if (sensor_driver_get_climate(&climate_sensor, &climate)) {
            printf("[%06u мс] Дані оновлено: T = %.2f °C | H = %.2f %% | P = %.2f гПа (Статус: %s)\n",
                   climate.timestamp_ms,
                   climate.temperature_c,
                   climate.humidity_percent,
                   climate.pressure_hpa,
                   climate.valid ? "OK" : "ПОМИЛКА");
        }

        /* У реальній системі тут виконуються інші задачі (дисплей, кнопка, мережа тощо) */
    }

    printf("=== Завершення демонстраційного прогону ===\n");
    return 0;
}
