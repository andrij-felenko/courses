/**
 * @file main.c
 * @brief Головний модуль програми демонстрації роботи з ІЧ-далекоміром Sharp GP2Y0A21YK0F.
 *
 * Демонструє налаштування системної периферії АЦП, ініціалізацію C-драйвера сенсора,
 * виконання періодичних вимірювань відстані з медіанною фільтрацією та обробку
 * виходу об'єкта за межі робочої зони (10–80 см).
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "adc_hal.h"
#include "gp2y0a21.h"

/**
 * @brief Імітація передачі телеметрії через послідовний порт UART
 */
static void uart_send_telemetry(const gp2y0a21_reading_t *reading)
{
    printf("[TELEMETRY] ADC: %4u | Vout: %.3f V | ", reading->raw_adc_median, reading->voltage_v);

    switch (reading->status) {
        case GP2Y0A21_OK:
            printf("Dist: %5.2f cm [STATUS: OK]\n", reading->distance_cm);
            break;
        case GP2Y0A21_OUT_OF_BOUNDS_TOO_CLOSE:
            printf("Dist: %5.2f cm [STATUS: WARN - TOO CLOSE (<10cm)]\n", reading->distance_cm);
            break;
        case GP2Y0A21_OUT_OF_BOUNDS_TOO_FAR:
            printf("Dist: %5.2f cm [STATUS: WARN - TOO FAR (>80cm)]\n", reading->distance_cm);
            break;
        default:
            printf("[STATUS: ERROR %d]\n", reading->status);
            break;
    }
}

int main(void)
{
    printf("=== Sharp GP2Y0A21YK0F IR Distance Sensor Driver Demo ===\n\n");

    /* Крок 1: Конфігурація аналогового каналу АЦП мікроконтролера */
    adc_channel_t sensor_adc_channel = 0;
    adc_config_t adc_cfg = {
        .channel_id = sensor_adc_channel,
        .resolution = ADC_RES_12BIT,
        .sampling_time = ADC_SAMPLETIME_LONG, /* Довга вибірка через вихідний імпеданс сенсора */
        .vref_volts = 3.3f,
        .gpio_pin = 15
    };

    if (adc_hal_init(sensor_adc_channel, &adc_cfg) != ADC_OK) {
        printf("Error: Failed to initialize ADC HAL.\n");
        return 1;
    }

    /* Крок 2: Конфігурація C-драйвера Sharp GP2Y0A21YK0F */
    gp2y0a21_config_t sensor_cfg = {
        .adc_channel = sensor_adc_channel,
        .sample_count = GP2Y0A21_DEFAULT_SAMPLE_COUNT, /* 5 вибірок для медіанного фільтра */
        .coeff_a = GP2Y0A21_DEFAULT_COEFF_A,
        .coeff_b = GP2Y0A21_DEFAULT_COEFF_B,
        .min_distance_cm = GP2Y0A21_MIN_DISTANCE_CM,
        .max_distance_cm = GP2Y0A21_MAX_DISTANCE_CM
    };

    gp2y0a21_t distance_sensor;
    gp2y0a21_status_t status = gp2y0a21_init(&distance_sensor, &sensor_cfg, ADC_RES_12BIT, 3.3f);
    if (status != GP2Y0A21_OK) {
        printf("Error: Failed to initialize GP2Y0A21 sensor driver (code %d).\n", status);
        return 1;
    }

    printf("GP2Y0A21 driver initialized. Operational range: %.0f - %.0f cm.\n\n",
           sensor_cfg.min_distance_cm, sensor_cfg.max_distance_cm);

    /* Крок 3: Цикл вимірювання відстані та виводу телеметрії */
    gp2y0a21_reading_t reading;
    
    for (int cycle = 1; cycle <= 5; cycle++) {
        printf("Cycle %d: ", cycle);
        status = gp2y0a21_read_distance(&distance_sensor, &reading);
        uart_send_telemetry(&reading);
    }

    printf("\nExecution completed successfully.\n");
    return 0;
}
