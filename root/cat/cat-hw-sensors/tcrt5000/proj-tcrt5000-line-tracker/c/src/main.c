/**
 * @file main.c
 * @brief Приклад використання драйвера масиву ІЧ-відбивальних давачів TCRT5000.
 */

#include <stdio.h>
#include <stdbool.h>
#include "../include/tcrt5000.h"

#define SENSOR_COUNT 5

static void print_sensor_state(const tcrt5000_reading_t *reading,
                              const tcrt5000_motor_speed_t *speeds,
                              tcrt5000_status_t status) {
    printf("--- Стан масиву TCRT5000 --- \n");
    printf("Сирі АЦП:   [ ");
    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        printf("%4u ", reading->raw_adc[i]);
    }
    printf("]\n");

    printf("Нормовані:  [ ");
    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        printf("%4u ", reading->normalized[i]);
    }
    printf("]\n");

    printf("Позиція лінії: %ld (Центр: %ld, Помилка: %ld)\n",
           (long)reading->line_position,
           (long)reading->center_position,
           (long)reading->position_error);

    printf("Виявлення лінії: %s | Статус: %d\n",
           reading->line_detected ? "ТАК" : "НІ (ВТРАЧЕНО)", status);

    printf("Мотори (L / R): %d / %d\n\n",
           speeds->left_motor_speed, speeds->right_motor_speed);
}

int main(void) {
    printf("=== Ініціалізація драйвера TCRT5000 (5 давачів) ===\n\n");

    tcrt5000_config_t config = {
        .sensor_count = SENSOR_COUNT,
        .use_analog = true,
        .adc_oversample = 4,
        .adc_channels = {
            {.channel_id = 0, .sample_time = 15},
            {.channel_id = 1, .sample_time = 15},
            {.channel_id = 2, .sample_time = 15},
            {.channel_id = 3, .sample_time = 15},
            {.channel_id = 4, .sample_time = 15}
        },
        .gpio_pins = {
            {.port_id = 0, .pin_num = 0},
            {.port_id = 0, .pin_num = 1},
            {.port_id = 0, .pin_num = 2},
            {.port_id = 0, .pin_num = 3},
            {.port_id = 0, .pin_num = 4}
        }
    };

    tcrt5000_status_t status = tcrt5000_init(&config);
    if (status != TCRT5000_OK) {
        printf("Помилка ініціалізації периферії: %d\n", status);
        return 1;
    }

    tcrt5000_calibration_t calib;
    tcrt5000_calibration_reset(&calib, SENSOR_COUNT);

    /* Симуляція встановлення калібрувальних значень:
     * Біла поверхня (мінімум відбиття): ADC ~ 300
     * Чорна лінія (максимум відбиття): ADC ~ 3500 */
    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        calib.min_raw[i] = 300 + (i * 10);
        calib.max_raw[i] = 3500 - (i * 10);
    }
    tcrt5000_calibration_finalize(&calib, SENSOR_COUNT);

    tcrt5000_pd_controller_t pd = {
        .kp = 0.12f,
        .kd = 0.65f,
        .last_error = 0,
        .base_speed = 200,
        .max_speed = 255
    };

    tcrt5000_reading_t reading;
    tcrt5000_motor_speed_t speeds;

    /* Сценарій 1: Лінія по центру (найсильніший сигнал на давачі index=2) */
    reading.raw_adc[0] = 400;  /* Нормоване ~ 31 */
    reading.raw_adc[1] = 1200; /* Нормоване ~ 281 */
    reading.raw_adc[2] = 3400; /* Нормоване ~ 968 */
    reading.raw_adc[3] = 1200; /* Нормоване ~ 281 */
    reading.raw_adc[4] = 400;  /* Нормоване ~ 31 */

    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        uint32_t range = calib.max_raw[i] - calib.min_raw[i];
        reading.normalized[i] = (uint16_t)(((uint32_t)(reading.raw_adc[i] - calib.min_raw[i]) * 1000) / range);
    }

    reading.line_position = tcrt5000_calculate_weighted_position(reading.normalized,
                                                                   SENSOR_COUNT,
                                                                   &reading.line_detected);
    reading.center_position = (int32_t)(((SENSOR_COUNT - 1) * TCRT5000_WEIGHT_STEP) / 2);
    reading.position_error = reading.line_position - reading.center_position;

    tcrt5000_compute_motor_speeds(&pd, reading.position_error, &speeds);
    printf("Сценарій 1: Лінія по центру (index 2)\n");
    print_sensor_state(&reading, &speeds, TCRT5000_OK);

    /* Сценарій 2: Відхилення вправо (лінія на давачах 3 та 4) */
    reading.raw_adc[0] = 310;
    reading.raw_adc[1] = 400;
    reading.raw_adc[2] = 1000;
    reading.raw_adc[3] = 3200;
    reading.raw_adc[4] = 2800;

    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        uint32_t range = calib.max_raw[i] - calib.min_raw[i];
        uint16_t raw = reading.raw_adc[i];
        if (raw <= calib.min_raw[i]) {
            reading.normalized[i] = 0;
        } else {
            reading.normalized[i] = (uint16_t)(((uint32_t)(raw - calib.min_raw[i]) * 1000) / range);
        }
    }

    reading.line_position = tcrt5000_calculate_weighted_position(reading.normalized,
                                                                   SENSOR_COUNT,
                                                                   &reading.line_detected);
    reading.position_error = reading.line_position - reading.center_position;

    tcrt5000_compute_motor_speeds(&pd, reading.position_error, &speeds);
    printf("Сценарій 2: Зміщення лінії вправо (сенсори 3, 4)\n");
    print_sensor_state(&reading, &speeds, TCRT5000_OK);

    /* Сценарій 3: Лінію втрачено (усі давачі бачать білу поверхню) */
    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        reading.raw_adc[i] = 310;
        reading.normalized[i] = 3;
    }
    reading.line_position = tcrt5000_calculate_weighted_position(reading.normalized,
                                                                   SENSOR_COUNT,
                                                                   &reading.line_detected);
    reading.position_error = reading.line_position - reading.center_position;

    tcrt5000_compute_motor_speeds(&pd, reading.position_error, &speeds);
    printf("Сценарій 3: Лінію втрачено\n");
    print_sensor_state(&reading, &speeds, TCRT5000_WARN_LINE_LOST);

    /* Демонстрація дискретного читання GPIO */
    tcrt5000_config_t config_dig = config;
    config_dig.use_analog = false;
    tcrt5000_init(&config_dig);
    tcrt5000_read_digital(&config_dig, &reading);
    printf("Дискретне читання компараторів LM393 (GPIO): [ ");
    for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
        printf("%d ", reading.digital_bits[i] ? 1 : 0);
    }
    printf("]\n");

    return 0;
}
