#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "i2c_bus.h"
#include "aht20.h"

/**
 * @file main.c
 * @brief Приклад практичного використання C-драйвера AHT20 на вбудованій системі.
 * 
 * Демонструє ініціалізацію шини I2C та сенсора AHT20, періодичне вимірювальне
 * опитування з витримкою затримок АЦП-перетворення, перевірку контрольної суми CRC-8,
 * розпакування 20-бітних даних та обробку збоїв зв'язку.
 */

/* Симуляційне середовище апаратного забезпечення для демонстрації */
static uint32_t g_system_ticks_ms = 0;
static bool g_sensor_measurement_triggered = false;
static uint32_t g_measurement_start_time = 0;
static bool g_simulate_crc_error_once = false;

static void mock_delay_ms(uint32_t ms) {
    g_system_ticks_ms += ms;
}

static uint32_t mock_get_ticks_ms(void) {
    return g_system_ticks_ms;
}

/* Симулятор запису на шину I2C */
static i2c_status_t mock_i2c_write(uint8_t addr, const uint8_t *data, size_t len) {
    if (addr != AHT20_I2C_ADDR || !data || len == 0) {
        return I2C_ERR_PARAM;
    }

    /* Запис команди ініціалізації 0xBE */
    if (data[0] == AHT20_CMD_INIT) {
        printf("  [I2C TX -> 0x%02X]: Команда ініціалізації 0xBE (arg1=0x%02X, arg2=0x%02X)\n",
               addr, (len > 1) ? data[1] : 0, (len > 2) ? data[2] : 0);
        return I2C_SUCCESS;
    }

    /* Запис команди тригера вимірювання 0xAC */
    if (data[0] == AHT20_CMD_TRIGGER_MEASURE) {
        printf("  [I2C TX -> 0x%02X]: Тригер АЦП-вимірювання 0xAC (0x%02X, 0x%02X)\n",
               addr, (len > 1) ? data[1] : 0, (len > 2) ? data[2] : 0);
        g_sensor_measurement_triggered = true;
        g_measurement_start_time = g_system_ticks_ms;
        return I2C_SUCCESS;
    }

    /* Запис команди м'якого скидання 0xBA */
    if (data[0] == AHT20_CMD_SOFT_RESET) {
        printf("  [I2C TX -> 0x%02X]: Команда м'якого скидання 0xBA\n", addr);
        g_sensor_measurement_triggered = false;
        return I2C_SUCCESS;
    }

    return I2C_SUCCESS;
}

/* Симулятор зчитування з шини I2C */
static i2c_status_t mock_i2c_read(uint8_t addr, uint8_t *data, size_t len) {
    if (addr != AHT20_I2C_ADDR || !data || len == 0) {
        return I2C_ERR_PARAM;
    }

    /* Зчитування 1 байта статусу */
    if (len == 1) {
        uint8_t status = AHT20_STATUS_CALIBRATED_MASK; /* За замовчуванням відкалібрований (0x08) */
        
        if (g_sensor_measurement_triggered) {
            /* Опитування прапорця Busy: зайнятий перші 80 мс після тригера */
            if ((g_system_ticks_ms - g_measurement_start_time) < AHT20_DELAY_MEASUREMENT_MS) {
                status |= AHT20_STATUS_BUSY_MASK; /* Встановлюємо біт 7 (0x80) */
            } else {
                g_sensor_measurement_triggered = false;
            }
        }
        data[0] = status;
        return I2C_SUCCESS;
    }

    /* Зчитування 7-байтового пакета даних (статус + 5 байтів АЦП + CRC-8) */
    if (len == 7) {
        /*
         * Задаємо еталонні фізичні показання для симулятора:
         * Вологість RH = 58.5%
         * Температура T = 24.2°C
         */
        float target_rh = 58.5f;
        float target_temp = 24.2f;

        /* Перерахунок у сирі 20-бітні значення за оберненими формулами AHT20 */
        uint32_t raw_humidity = (uint32_t)((target_rh / 100.0f) * 1048576.0f);
        uint32_t raw_temp = (uint32_t)(((target_temp + 50.0f) / 200.0f) * 1048576.0f);

        /* Байт 0: Статус (відкалібрований 0x08, не зайнятий) */
        data[0] = AHT20_STATUS_CALIBRATED_MASK;

        /* Упаковка 20-бітного raw_humidity у байти 1..3 */
        data[1] = (uint8_t)((raw_humidity >> 12) & 0xFF);
        data[2] = (uint8_t)((raw_humidity >> 4) & 0xFF);

        /* Байт 3: старші 4 біти вологості + старші 4 біти температури */
        data[3] = (uint8_t)(((raw_humidity & 0x0F) << 4) | ((raw_temp >> 16) & 0x0F));

        /* Упаковка 20-бітного raw_temp у байти 4..5 */
        data[4] = (uint8_t)((raw_temp >> 8) & 0xFF);
        data[5] = (uint8_t)(raw_temp & 0xFF);

        /* Байт 6: Обчислення точної контрольної суми CRC-8 */
        data[6] = aht20_calc_crc8(data, 6);

        /* Імітація спотворення CRC для демонстрації обробки помилок */
        if (g_simulate_crc_error_once) {
            data[6] ^= 0xFF;
            g_simulate_crc_error_once = false;
            printf("  [СИМУЛЯЦІЯ]: Навмисне спотворення контрольної суми CRC-8 у пакеті!\n");
        }

        return I2C_SUCCESS;
    }

    return I2C_ERR_PARAM;
}

int main(void) {
    printf("=====================================================================\n");
    printf("  МОДУЛЬНИЙ C-ДРАЙВЕР ЦИФРОВОГО ДАВАЧА AHT20 (I2C + CRC-8)\n");
    printf("=====================================================================\n\n");

    /* КРОК 1: Налаштування приземленої абстракції апаратної шини I2C */
    i2c_bus_t i2c_bus = {
        .write = mock_i2c_write,
        .read = mock_i2c_read,
        .delay_ms = mock_delay_ms,
        .get_ticks_ms = mock_get_ticks_ms
    };

    /* КРОК 2: Ініціалізація C-драйвера AHT20 */
    printf("[ІНІЦІАЛІЗАЦІЯ] Перевірка живлення та стану калібрування AHT20...\n");
    aht20_t dev;
    aht20_err_t err = aht20_init(&dev, &i2c_bus);

    if (err != AHT20_OK) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати AHT20: %s\n", aht20_err_to_string(err));
        return EXIT_FAILURE;
    }
    printf("[УСПІХ] Давач AHT20 успішно ініціалізовано та відкалібровано.\n\n");

    /* КРОК 3: Виконання серії зчитувань у циклі опитування */
    printf("[ЦИКЛ ОПИТУВАННЯ] Запуск 3 вимірювальних циклів із верифікацією CRC-8:\n");
    for (int cycle = 1; cycle <= 3; cycle++) {
        printf("\n--- Вимірювання #%d ---\n", cycle);

        aht20_data_t sensor_data;
        err = aht20_read_data(&dev, &sensor_data);

        if (err == AHT20_OK) {
            printf("  [СИРІ ДАНІ АЦП]: Raw Humidity = 0x%05X (%u), Raw Temp = 0x%05X (%u)\n",
                   sensor_data.raw_humidity, sensor_data.raw_humidity,
                   sensor_data.raw_temp, sensor_data.raw_temp);
            printf("  [CRC-8]: ВАЛІДНИЙ (OK)\n");
            printf("  [ФІЗИЧНІ ВЕЛІЧИНИ]:\n");
            printf("    -> Відносна вологість: %.2f %% RH\n", sensor_data.humidity_rh);
            printf("    -> Температура:       %.2f °C\n", sensor_data.temperature_c);
        } else {
            printf("  [ПОМИЛКА ВИМІРЮВАННЯ]: %s\n", aht20_err_to_string(err));
        }

        i2c_bus.delay_ms(500);
    }

    /* КРОК 4: Демонстрація перевірки захисту від збоїв (симуляція помилки CRC-8) */
    printf("\n[ТЕСТ ЦІЛІСНОСТІ] Імітація збою CRC-8 під час транзакції I2C...\n");
    g_simulate_crc_error_once = true;

    aht20_data_t crc_test_data;
    err = aht20_read_data(&dev, &crc_test_data);
    if (err == AHT20_ERR_CRC) {
        printf("[УСПІХ ТЕСТУ] Драйвер виявив збій цілісності: %s\n", aht20_err_to_string(err));
    } else {
        printf("[ПОМИЛКА ТЕСТУ] Очікувалася помилка AHT20_ERR_CRC, але отримано %d\n", err);
    }

    /* КРОК 5: Демонстрація м'якого скидання давача (Soft Reset 0xBA) */
    printf("\n[SOFT RESET] Надсилання команди м'якого скидання AHT20 (0xBA)...\n");
    err = aht20_soft_reset(&dev);
    if (err == AHT20_OK) {
        printf("[УСПІХ] М'яке скидання виконано, регістри AHT20 відновлено.\n");
    } else {
        printf("[ПОМИЛКА] Сбой Soft Reset: %s\n", aht20_err_to_string(err));
    }

    printf("\n=====================================================================\n");
    printf("  ДЕМОНСТРАЦІЮ РОБОТИ C-ДРАЙВЕРА AHT20 ЗАВЕРШЕНО УСПІШНО\n");
    printf("=====================================================================\n");

    return EXIT_SUCCESS;
}
