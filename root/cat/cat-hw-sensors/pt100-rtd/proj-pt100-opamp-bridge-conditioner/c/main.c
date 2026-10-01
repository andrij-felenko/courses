#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "pt100.h"

/*
 * Демонстраційна функція симуляції зчитування АЦП мікроконтролера.
 * В реальній системі тут буде виклик HAL_ADC_GetValue() або аналоги.
 */
static uint32_t read_hardware_adc(void)
{
    static uint32_t simulated_adc_values[] = {
        0U,     /*  0.00 В ->  0.0 °C (нижня межа) */
        1024U,  /*  1.25 В -> 25.0 °C (кімнатна температура) */
        1500U,  /*  1.83 В -> 36.6 °C (нормальна температура тіла) */
        2048U,  /*  2.50 В -> 50.0 °C (середина шкали) */
        4095U   /*  5.00 В -> 100.0 °C (верхня межа) */
    };
    static size_t sample_index = 0U;
    size_t count = sizeof(simulated_adc_values) / sizeof(simulated_adc_values[0]);

    uint32_t val = simulated_adc_values[sample_index];
    sample_index = (sample_index + 1U) % count;

    return val;
}

int main(void)
{
    printf("=== Системна обробка сигналу платинового термоопору PT100 ===\n\n");

    pt100_config_t sensor;

    /*
     * Ініціалізація конфігурації:
     * - АЦП: 12 біт (0..4095 рівнів)
     * - Опорна напруга: 5.0 В
     * - Діапазон вимірювального нормувача: 0.0 °C (при 0 В) ... 100.0 °C (при 5 В)
     */
    if (!pt100_init_config(&sensor, 12U, 5.0f, 0.0f, 100.0f)) {
        printf("Помилка ініціалізації конфігурації датчика!\n");
        return 1;
    }

    printf("Параметри вимірювача:\n");
    printf("  Розрядність АЦП: %u біт\n", sensor.adc_bits);
    printf("  Опорна напруга Vref: %.2f В\n", sensor.vref_v);
    printf("  Діапазон температур: %.1f °C ... %.1f °C\n\n", sensor.temp_min, sensor.temp_max);

    /*
     * Двохточкове калібрування аналогового тракту:
     * Симуляція апаратного розкиду реальної плати.
     * Точка 1 (0 °C):  Еталон = 0.00 В, реальний виміряний сирий АЦП показує 0.04 В (зсув +40 мВ).
     * Точка 2 (100 °C): Еталон = 5.00 В, реальний виміряний сирий АЦП показує 4.90 В (похибка підсилення).
     */
    float v_meas1 = 0.04f; /* Виміряно при 0 °C */
    float v_ref1  = 0.00f; /* Істинний еталон */
    float v_meas2 = 4.90f; /* Виміряно при 100 °C */
    float v_ref2  = 5.00f; /* Істинний еталон */

    if (pt100_calc_calibration(v_meas1, v_ref1, v_meas2, v_ref2, &sensor.calib)) {
        printf("Розраховано двохточкові калібрувальні коефіцієнти:\n");
        printf("  gain   = %.6f\n", sensor.calib.gain);
        printf("  offset = %.6f В\n\n", sensor.calib.offset);
    } else {
        printf("Помилка розрахунку калібрувальних коефіцієнтів!\n");
        return 1;
    }

    printf("Розпочинаємо цикл вимірювання температури у суперциклі МК:\n");
    printf("--------------------------------------------------------------------------------\n");
    printf("|  Код АЦП  | Сира напруга | Скоригована напруга | Розрахована темп. | Статус |\n");
    printf("--------------------------------------------------------------------------------\n");

    /* Демонстраційний суперцикл (Super-Loop) мікроконтролера */
    for (int cycle = 0; cycle < 10; ++cycle) {
        uint32_t adc_raw = read_hardware_adc();

        /* Окремі проміжні кроки для наочності обробки */
        float v_raw  = pt100_adc_to_voltage(adc_raw, &sensor);
        float v_corr = pt100_correct_voltage(v_raw, &sensor.calib);

        float temperature = 0.0f;
        bool status = pt100_process_sample(adc_raw, &sensor, &temperature);

        printf("|   %5u   |   %6.4f В   |     %6.4f В      |    %6.2f °C     |   %s   |\n",
               adc_raw,
               v_raw,
               v_corr,
               temperature,
               status ? " OK " : "ERR ");
    }

    printf("--------------------------------------------------------------------------------\n");
    printf("Обробку успішно завершено.\n");

    return 0;
}
