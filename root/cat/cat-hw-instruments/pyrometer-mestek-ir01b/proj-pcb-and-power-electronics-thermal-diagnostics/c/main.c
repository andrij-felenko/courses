#include <stdio.h>
#include "pyrometer.h"

static void print_reading_info(size_t step, const pyro_reading_t *reading) {
    printf("[%02zu] V_sensor = %6.3f мВ | T_amb = %5.1f °C | T_obj = %6.2f °C | Статус: ",
           step, reading->raw_voltage_mv, reading->ambient_temp_celsius, reading->object_temp_celsius);

    switch (reading->status) {
        case PYRO_OK:
            printf("ОК (в межах норми)");
            break;
        case PYRO_WARN_HIGH_ALARM:
            printf("УВАГА: Перевищення HAL!");
            break;
        case PYRO_WARN_LOW_ALARM:
            printf("УВАГА: Падіння нижче LAL!");
            break;
        case PYRO_ERR_OUT_OF_RANGE_LOW:
            printf("ПОХИБКА: Нижче ніж -50 °C!");
            break;
        case PYRO_ERR_OUT_OF_RANGE_HIGH:
            printf("ПОХИБКА: Вище ніж +550 °C!");
            break;
        case PYRO_ERR_INVALID_EMISSIVITY:
            printf("ПОХИБКА: Некоректний коефіцієнт емісії ε!");
            break;
        default:
            printf("АВАРІЯ: Несправність сенсора!");
            break;
    }

    if (reading->high_alarm_active) {
        printf(" [ТРИВОГА HI АКТИВНА]");
    }
    if (reading->low_alarm_active) {
        printf(" [ТРИВОГА LOW АКТИВНА]");
    }
    printf("\n");
}

int main(void) {
    printf("=== Демонстрація роботи драйвера пірометра MESTEK IR01B ===\n\n");

    pyro_config_t config;
    pyro_reading_t reading = {0};

    if (pyro_init_config(&config) != PYRO_OK) {
        printf("Помилка ініціалізації конфігурації пірометра!\n");
        return 1;
    }

    config.emissivity = 0.95f;          /* Емісивність цегли/окропу */
    config.bg_temp_celsius = 22.0f;     /* Температура фону 22 °C */
    config.high_alarm_celsius = 80.0f;  /* Поріг перегріву 80 °C */
    config.low_alarm_celsius = 5.0f;    /* Поріг заморожування 5 °C */
    config.hysteresis_celsius = 2.0f;   /* Гістерезис 2.0 °C */

    printf("Конфігурація: ε = %.2f, T_bg = %.1f °C, HAL = %.1f °C, LAL = %.1f °C, Гістерезис = %.1f °C\n\n",
           config.emissivity, config.bg_temp_celsius, config.high_alarm_celsius,
           config.low_alarm_celsius, config.hysteresis_celsius);

    typedef struct {
        float v_sensor;
        float t_amb;
    } sim_sample_t;

    sim_sample_t samples[] = {
        { 0.0000e-3f, 25.0f },
        { 0.8500e-3f, 25.0f },
        { 1.8500e-3f, 25.0f },
        { 2.0500e-3f, 25.0f },
        { 1.9000e-3f, 25.0f },
        { 1.7000e-3f, 25.0f },
        {-0.7200e-3f, 25.0f },
        { 0.0000e-3f, 25.0f }
    };

    size_t num_samples = sizeof(samples) / sizeof(samples[0]);

    printf("--- Цикл зчитування вимірювань та гістерезисного контролю ---\n");
    for (size_t i = 0; i < num_samples; i++) {
        pyro_calculate_temperature(&config, samples[i].v_sensor, samples[i].t_amb, &reading);
        print_reading_info(i + 1, &reading);
    }

    printf("\n--- Тест компенсації емісивності для низькоетапних поверхонь (алюміній ε = 0.15) ---\n");
    config.emissivity = 0.15f;
    config.bg_temp_celsius = 30.0f;
    float v_alum = 0.2000e-3f;

    pyro_calculate_temperature(&config, v_alum, 25.0f, &reading);
    printf("Поверхня з ε = 0.15 при фоні T_bg = 30 °C: Розрахована температура = %.2f °C\n",
           reading.object_temp_celsius);

    return 0;
}
