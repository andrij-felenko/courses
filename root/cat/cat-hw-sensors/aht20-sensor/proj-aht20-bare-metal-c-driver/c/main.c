#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "aht20.h"

/**
 * @file main.c
 * @brief Приклад використання драйвера AHT20 у неблокуючому циклі мікроконтролера.
 */

// Симуляція системного часу мікроконтролера в мілісекундах
static uint32_t sys_tick_ms = 0;

// Буфер імітації відповідей шини I2C
static uint8_t mock_i2c_response[7] = {0};

/**
 * @brief Імітація системного часу (HAL).
 */
static uint32_t hal_get_tick_ms(void) {
    return sys_tick_ms;
}

/**
 * @brief Імітація системної затримки.
 */
static void hal_delay_ms(uint32_t ms) {
    sys_tick_ms += ms;
}

/**
 * @brief Заглушка апаратно-залежного читання I2C.
 */
static bool hal_i2c_read(uint8_t dev_addr, uint8_t *data, size_t len, void *user_data) {
    (void)dev_addr;
    (void)user_data;

    if (len == 1) {
        // Статус: біт 3 (0x08) — відкалібровано, біт 7 (0x00) — не зайнятий
        data[0] = AHT20_STATUS_CALIBRATED_BIT;
        return true;
    }

    if (len == 7) {
        // Копіюємо згенеровані тестові дані
        for (size_t i = 0; i < 7; i++) {
            data[i] = mock_i2c_response[i];
        }
        return true;
    }

    return false;
}

/**
 * @brief Заглушка апаратно-залежного запису I2C.
 */
static bool hal_i2c_write(uint8_t dev_addr, const uint8_t *data, size_t len, void *user_data) {
    (void)dev_addr;
    (void)user_data;

    // Перевіряємо команду тригера вимірювання (0xAC)
    if (len == 3 && data[0] == AHT20_CMD_TRIGGER) {
        // Формуємо фіктивний пакет даних для 25.5 C та 60.0% RH
        // 60% вологості = 0.60 * 1048576 = 629145 (0x99999)
        // 25.5 C = ((25.5 + 50) / 200) * 1048576 = 395837 (0x609ED)

        uint32_t raw_h = 629145;
        uint32_t raw_t = 395837;

        mock_i2c_response[0] = AHT20_STATUS_CALIBRATED_BIT; // Готовий, калібрований
        mock_i2c_response[1] = (uint8_t)(raw_h >> 12);
        mock_i2c_response[2] = (uint8_t)(raw_h >> 4);
        mock_i2c_response[3] = (uint8_t)(((raw_h & 0x0F) << 4) | ((raw_t >> 16) & 0x0F));
        mock_i2c_response[4] = (uint8_t)(raw_t >> 8);
        mock_i2c_response[5] = (uint8_t)(raw_t);
        mock_i2c_response[6] = aht20_calculate_crc8(mock_i2c_response, 6);
    }

    return true;
}

int main(void) {
    printf("=== Драйвер давача AHT20 (C99) ===\n");

    aht20_t sensor;
    aht20_status_t status = aht20_init(&sensor,
                                       AHT20_I2C_ADDR_DEFAULT,
                                       hal_i2c_read,
                                       hal_i2c_write,
                                       hal_get_tick_ms,
                                       NULL);

    if (status != AHT20_OK) {
        printf("Помилка ініціалізації давача AHT20: %d\n", status);
        return 1;
    }

    printf("Ініціалізація давача AHT20 успішна!\n");

    // 1. Демонстрація неблокуючого вимірювання через автомат станів
    printf("\n--- Неблокуючий режим вимірювання ---\n");
    status = aht20_start_measurement(&sensor);
    if (status != AHT20_OK) {
        printf("Помилка запуску вимірювання: %d\n", status);
        return 1;
    }

    aht20_data_t sensor_data;
    bool measurement_done = false;

    // Головний неблокуючий цикл
    while (!measurement_done) {
        // Оновлюємо автомат станів
        status = aht20_update(&sensor, &sensor_data);

        if (status == AHT20_OK) {
            printf("Вимірювання завершено успішно!\n");
            printf("Вологість: %.2f %%\n", sensor_data.humidity);
            printf("Температура: %.2f C\n", sensor_data.temperature);
            measurement_done = true;
        } else if (status == AHT20_BUSY) {
            // Симуляція виконання інших завдань мікроконтролером
            printf("Очікування даних (час: %u мс)...\n", sys_tick_ms);
            hal_delay_ms(20); // Крок у 20 мс
        } else {
            printf("Помилка вимірювання: %d\n", status);
            break;
        }
    }

    // 2. Демонстрація блокуючого режиму читання
    printf("\n--- Блокуючий режим вимірювання ---\n");
    status = aht20_read_blocking(&sensor, &sensor_data, hal_delay_ms);
    if (status == AHT20_OK) {
        printf("Вологість: %.2f %%\n", sensor_data.humidity);
        printf("Температура: %.2f C\n", sensor_data.temperature);
    } else {
        printf("Помилка блокуючого зчитування: %d\n", status);
    }

    return 0;
}
