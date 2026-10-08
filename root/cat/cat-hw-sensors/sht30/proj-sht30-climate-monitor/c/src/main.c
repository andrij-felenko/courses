#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "i2c_bus.h"
#include "sht30.h"

/**
 * @file main.c
 * @brief Приклад практичного застосування C-драйвера SHT30.
 */

/* Симуляція затримки мікроконтролера */
static void sys_delay_ms(uint32_t ms)
{
    /* На реальному мікроконтролері використовується HAL_Delay / vTaskDelay / busy-wait */
    (void)ms;
}

/* Реалізація програмного емулятора шини I2C для демонстрації роботи драйвера */
i2c_err_t i2c_bus_init(const i2c_bus_config_t *config)
{
    if (config == NULL) {
        return I2C_ERR_INVALID_ARG;
    }
    printf("[I2C BUS] Ініціалізація порту %u на частоті %u Гц успішна.\n",
           config->i2c_port, config->clock_speed_hz);
    return I2C_SUCCESS;
}

i2c_err_t i2c_bus_write(uint8_t dev_addr, const uint8_t *data, size_t len, uint32_t timeout_ms)
{
    (void)timeout_ms;
    if (data == NULL || len == 0) {
        return I2C_ERR_INVALID_ARG;
    }
    printf("[I2C BUS] Запис %zu байт на адресу 0x%02X: ", len, dev_addr);
    for (size_t i = 0; i < len; i++) {
        printf("0x%02X ", data[i]);
    }
    printf("\n");
    return I2C_SUCCESS;
}

i2c_err_t i2c_bus_read(uint8_t dev_addr, uint8_t *buffer, size_t len, uint32_t timeout_ms)
{
    (void)dev_addr;
    (void)timeout_ms;
    if (buffer == NULL || len == 0) {
        return I2C_ERR_INVALID_ARG;
    }
    return I2C_SUCCESS;
}

i2c_err_t i2c_bus_write_read(uint8_t dev_addr,
                             const uint8_t *tx_data, size_t tx_len,
                             uint8_t *rx_buffer, size_t rx_len,
                             uint32_t delay_ms, uint32_t timeout_ms)
{
    (void)timeout_ms;
    (void)delay_ms;
    if (tx_data == NULL || rx_buffer == NULL) {
        return I2C_ERR_INVALID_ARG;
    }

    uint16_t cmd = (uint16_t)(((uint16_t)tx_data[0] << 8) | tx_data[1]);
    (void)tx_len;

    /* Емуляція відповіді SHT30 для вимірювання температури й вологості */
    if ((cmd & 0xFF00) == 0x2C00 || (cmd & 0xFF00) == 0x2400 || (cmd & 0xFF00) == 0x2D00) {
        if (rx_len >= 6) {
            /* Фізичні значення: Temp = 24.5 °C, Humidity = 55.0% */
            /* Raw_T = ((24.5 + 45) / 175) * 65535 = 26041 (0x65B9) */
            /* Raw_RH = (55.0 / 100) * 65535 = 36044 (0x8CCD) */
            rx_buffer[0] = 0x65;
            rx_buffer[1] = 0xB9;
            rx_buffer[2] = sht30_calc_crc8(&rx_buffer[0]);

            rx_buffer[3] = 0x8C;
            rx_buffer[4] = 0xCD;
            rx_buffer[5] = sht30_calc_crc8(&rx_buffer[3]);
        }
    }
    /* Емуляція відповіді для читання регістру статусу */
    else if (cmd == SHT30_CMD_READ_STATUS) {
        if (rx_len >= 3) {
            rx_buffer[0] = 0x00;
            rx_buffer[1] = 0x00;
            rx_buffer[2] = sht30_calc_crc8(&rx_buffer[0]);
        }
    }

    printf("[I2C BUS] Транзакція write-read для 0x%02X виконана успішно.\n", dev_addr);
    return I2C_SUCCESS;
}

int main(void)
{
    printf("=== Запуск драйвера SHT30 для моніторингу мікроклімату ===\n\n");

    /* 1. Налаштування та ініціалізація шини I2C */
    i2c_bus_config_t i2c_cfg = {
        .i2c_port = 0,
        .clock_speed_hz = 100000,
        .timeout_ms = 500,
        .enable_clock_stretch = false
    };

    if (i2c_bus_init(&i2c_cfg) != I2C_SUCCESS) {
        printf("Помилка: не вдалося ініціалізувати шину I2C!\n");
        return EXIT_FAILURE;
    }

    /* 2. Ініціалізація драйвера SHT30 */
    sht30_t sht30_dev;
    if (sht30_init(&sht30_dev, SHT30_I2C_ADDR_A, sys_delay_ms) != SHT30_OK) {
        printf("Помилка: некоректні параметри ініціалізації SHT30!\n");
        return EXIT_FAILURE;
    }

    /* 3. Виконання апаратного скидання та очищення статусу */
    printf("\n--- Виконання Soft Reset та перевірка статусу ---\n");
    if (sht30_soft_reset(&sht30_dev) == SHT30_OK) {
        printf("Soft Reset успішно виконано.\n");
    }

    sht30_status_t status;
    if (sht30_read_status(&sht30_dev, &status) == SHT30_OK) {
        printf("Статус SHT30: Нагрівач=%s, Скидання=%s, Помилка CRC=%s\n",
               status.heater_active ? "Увімкнено" : "Вимкнено",
               status.system_reset ? "Так" : "Ні",
               status.checksum_failed ? "Так" : "Ні");
    }

    /* 4. Циклічне опитування сенсора в режимі низького енергоспоживання */
    printf("\n--- Цикл вимірювання параметрів довкілля (Single-Shot / Low Power) ---\n");
    for (int i = 1; i <= 3; i++) {
        printf("\nВимірювання #%d:\n", i);
        sht30_data_t data;
        sht30_err_t err = sht30_read_single_shot(&sht30_dev, &data);

        if (err == SHT30_OK) {
            printf("  Температура:        %.2f градуси C\n", data.temperature_c);
            printf("  Відносна вологість: %.2f %%\n", data.humidity_percent);
            printf("  Точка роси:         %.2f градуси C\n", data.dew_point_c);
            printf("  Цілісність CRC-8:   %s\n", data.is_crc_valid ? "УСПІШНО (OK)" : "ПОМИЛКА");

            /* Адаптивна сушка вбудованим підігрівачем у разі ризику конденсації */
            if (data.humidity_percent > 80.0f) {
                printf("  [УВАГА] Висока вологість (>80%%). Активація нагрівача для сушки...\n");
                sht30_set_heater(&sht30_dev, true);
                sys_delay_ms(100);
                sht30_set_heater(&sht30_dev, false);
                printf("  Сушка завершена, нагрівач вимкнено.\n");
            }
        } else {
            printf("  Помилка зчитування даних! Код помилки: %d\n", err);
        }

        /* Перехід сенсора в режим сну між вибірками для економії енергії */
        sys_delay_ms(1000);
    }

    printf("\n=== Демонстрацію роботи драйвера SHT30 завершено успішно ===\n");
    return EXIT_SUCCESS;
}
