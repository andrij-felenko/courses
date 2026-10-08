#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "i2c_hal.h"
#include "bme280.h"

/**
 * @file main.c
 * @brief Приклад застосування C-драйвера BME280 в циклограмі автономної системи моніторингу довкілля.
 * 
 * Демонструє ініціалізацію I2C та системного таймера, зчитування NVM-калібрування BME280,
 * виконання періодичних поодиноких вимірювань у режимі Forced Mode, зчитування сирих вибірок АЦП,
 * розрахунок фізичних величин (°C, Па, %RH) та переведення мікроконтролера в режим сну між замірами.
 */

int main(void) {
    printf("=====================================================================\n");
    printf("  НИЗЬКОРІВНЕВИЙ C-ДРАЙВЕР ДАВАЧА BOSCH BME280 (I2C FORCED MODE)\n");
    printf("=====================================================================\n\n");

    /* КРОК 1: Ініціалізація апаратного модуля I2C Master (100 кГц Standard Mode) */
    printf("[1] Ініціалізація шини I2C Master (100 кГц)... ");
    i2c_hal_err_t hal_err = i2c_hal_init(100000);
    if (hal_err != I2C_HAL_OK) {
        printf("ПОМИЛКА: %s\n", i2c_hal_err_to_str(hal_err));
        return EXIT_FAILURE;
    }
    printf("ОК\n");

    /* КРОК 2: Ініціалізація дескриптора давача BME280 за адресою 0x76 */
    bme280_t bme_sensor;
    printf("[2] Підключення до BME280 за I2C адресою 0x%02X...\n", BME280_I2C_ADDR_PRIM);
    bme280_err_t bme_err = bme280_init(&bme_sensor, BME280_I2C_ADDR_PRIM);
    if (bme_err != BME280_OK) {
        printf("    ПОМИЛКА ініціалізації BME280: %s\n", bme280_err_to_str(bme_err));
        return EXIT_FAILURE;
    }
    printf("    [УСПІХ] Зчитано Chip ID = 0x60, програмне скидання та NVM-калібрування завантажено.\n");

    /* Друк прочитаних з NVM калібрувальних коефіцієнтів */
    printf("\n--- Зчитані фабричні калібрувальні коефіцієнти NVM ---\n");
    printf("  Температура: dig_T1=%u, dig_T2=%d, dig_T3=%d\n",
           bme_sensor.calib.dig_T1, bme_sensor.calib.dig_T2, bme_sensor.calib.dig_T3);
    printf("  Тиск: dig_P1=%u, dig_P2=%d, dig_P3=%d, dig_P4=%d, dig_P5=%d, dig_P6=%d, dig_P7=%d, dig_P8=%d, dig_P9=%d\n",
           bme_sensor.calib.dig_P1, bme_sensor.calib.dig_P2, bme_sensor.calib.dig_P3,
           bme_sensor.calib.dig_P4, bme_sensor.calib.dig_P5, bme_sensor.calib.dig_P6,
           bme_sensor.calib.dig_P7, bme_sensor.calib.dig_P8, bme_sensor.calib.dig_P9);
    printf("  Вологість: dig_H1=%u, dig_H2=%d, dig_H3=%u, dig_H4=%d, dig_H5=%d, dig_H6=%d\n\n",
           bme_sensor.calib.dig_H1, bme_sensor.calib.dig_H2, bme_sensor.calib.dig_H3,
           bme_sensor.calib.dig_H4, bme_sensor.calib.dig_H5, bme_sensor.calib.dig_H6);

    /* КРОК 3: Конфігурування оверсемплінгу (Температура x2, Тиск x16, Вологість x1) */
    printf("[3] Налаштування профілю оверсемплінгу (T=2x, P=16x, H=1x)...\n");
    bme_err = bme280_set_oversampling(&bme_sensor,
                                      BME280_OVERSAMPLING_2X,
                                      BME280_OVERSAMPLING_16X,
                                      BME280_OVERSAMPLING_1X);
    if (bme_err != BME280_OK) {
        printf("    ПОМИЛКА конфігурації оверсемплінгу: %s\n", bme280_err_to_str(bme_err));
        return EXIT_FAILURE;
    }

    /* КРОК 4: Запуск циклограми періодичного енергоефективного моніторингу */
    printf("\n=====================================================================\n");
    printf("  ЗАПУСК ЦИКЛОГРАМИ СТАНЦІЇ МОНІТОРИНГУ ДОВКІЛЛЯ (FORCED MODE)\n");
    printf("=====================================================================\n\n");

    const int TOTAL_MEASUREMENT_CYCLES = 3;

    for (int cycle = 1; cycle <= TOTAL_MEASUREMENT_CYCLES; cycle++) {
        uint32_t timestamp = i2c_hal_get_ticks_ms();
        printf("[%u мс] --- Цикл заміру #%d ---\n", timestamp, cycle);

        /* 4.1 Тригерування заміру в режимі Forced Mode (давач робить 1 замір і лягає в сон) */
        printf("  -> Тригерування Forced Mode (ctrl_hum=0x%02X, ctrl_meas=0x%02X)...\n",
               bme_sensor.osrs_h, (bme_sensor.osrs_t << 5) | (bme_sensor.osrs_p << 2) | BME280_MODE_FORCED);

        bme280_data_t env_data;
        bme_err = bme280_perform_forced_measurement(&bme_sensor, &env_data);
        if (bme_err != BME280_OK) {
            printf("  [ПОМИЛКА] Збій виконання вимірювання: %s\n", bme_err_to_str(bme_err));
            continue;
        }

        /* 4.2 Друк результатів цілочисельної компенсації та проміжної величини t_fine */
        printf("  -> Оцифровано! Проміжна величина t_fine = %d\n", bme_sensor.t_fine);
        printf("  -> Фізичні параметри довкілля:\n");
        printf("     * Температура : %.2f °C (цілочисельне значення: %d x 0.01 °C)\n",
               env_data.temperature_degc, env_data.temperature_degc_x100);
        printf("     * Атм. тиск   : %.2f гПа / %.0f Па (цілочисельне: %u Па)\n",
               env_data.pressure_hpa, (double)env_data.pressure_pa, env_data.pressure_pa);
        printf("     * Відн. вологість : %.2f %%RH (цілочисельне Q22.10: %u)\n",
               env_data.humidity_rh, env_data.humidity_rh_x1024);

        /* 4.3 Симуляція переведення мікроконтролера в режим сну (Deep Sleep) між вимірами */
        printf("  -> Давач повернувся в Sleep Mode. Перехід MCU в Deep Sleep на 2000 мс...\n\n");
        i2c_hal_delay_ms(2000);
    }

    printf("=====================================================================\n");
    printf("  АВТОНОМНУ ЦИКЛОГРАМУ МОНІТОРИНГУ УСПІШНО ВИКОНАНО\n");
    printf("=====================================================================\n");

    return EXIT_SUCCESS;
}
