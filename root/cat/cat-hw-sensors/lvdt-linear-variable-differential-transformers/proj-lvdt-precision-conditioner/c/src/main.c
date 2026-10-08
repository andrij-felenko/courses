/**
 * @file main.c
 * @brief Демонстрація використання LVDT-драйвера вбудованої системи.
 *
 * Демонструється ініціалізація периферії АЦП, конфігурація параметрів LVDT,
 * виконання автокалібрування нуля, обробка потоку вибірок із застосуванням
 * EMA-фільтрації та діагностика виходу за межі і обриву лінії.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "adc_hal.h"
#include "lvdt.h"

/* Зовнішній прототип із замиканням на функцію емуляції фізичної напруги LVDT */
extern void adc_hal_set_simulated_voltage(float voltage_v);

/**
 * @brief Допоміжна функція виводу опису статусу вимірювання
 */
static const char* status_to_string(lvdt_status_t status)
{
    switch (status) {
        case LVDT_OK:                    return "OK (В нормі)";
        case LVDT_WARN_OUT_OF_RANGE_MIN: return "ПОПЕРЕДЖЕННЯ: Вихід нижче Min межі";
        case LVDT_WARN_OUT_OF_RANGE_MAX: return "ПОПЕРЕДЖЕННЯ: Вихід вище Max межі";
        case LVDT_ERROR_SIGNAL_FAULT:    return "ПОМИЛКА: Аварія сигналу (Обрив/КЗ)";
        case LVDT_ERROR_ADC:             return "ПОМИЛКА: Збій АЦП";
        case LVDT_ERROR_NULL_POINTER:    return "ПОМИЛКА: Нульовий вказівник";
        case LVDT_ERROR_INVALID_PARAM:   return "ПОМИЛКА: Некоректний параметр";
        case LVDT_ERROR_NOT_INITIALIZED: return "ПОМИЛКА: Не ініціалізовано";
        default:                         return "НЕВІДОМИЙ СТАТУС";
    }
}

int main(void)
{
    printf("=== Система вимірювання лінійного переміщення LVDT ===\n");

    /* 1. Налаштування структури конфігурації LVDT */
    lvdt_config_t lvdt_cfg = {
        .adc_channel = ADC_CHANNEL_0,
        .adc_resolution = ADC_RES_12BIT,
        .sample_time = ADC_SAMPLETIME_239_5_CYCLES,
        .vref_volts = 3.3f,                 /* Опорна напруга 3.3В */
        .sensitivity_mm_per_v = 20.0f,      /* Чутливість: 20 мм на 1 Вольт зміщення */
        .min_displacement_mm = -25.0f,      /* Робочий хід: від -25.0 мм */
        .max_displacement_mm = 25.0f,       /* Робочий хід: до +25.0 мм */
        .min_valid_voltage_v = 0.10f,       /* Сигнал нижче 0.10В вважається обривом */
        .max_valid_voltage_v = 3.20f,       /* Сигнал вище 3.20В вважається насиченням/КЗ */
        .filter_alpha = 0.20f               /* EMA коефіцієнт згладжування */
    };

    /* 2. Ініціалізація екземпляра LVDT */
    lvdt_t lvdt_dev;
    lvdt_status_t status = lvdt_init(&lvdt_dev, &lvdt_cfg);
    if (status != LVDT_OK) {
        printf("Помилка ініціалізації LVDT: %d\n", status);
        return -1;
    }
    printf("Драйвер LVDT успішно ініціалізовано.\n");

    /* 3. Автокалібрування нуля при нульовому положенні сердечника (1.65В) */
    adc_hal_set_simulated_voltage(1.65f);
    printf("\nВиконання автокалібрування нульового положення (Zero Calibration)...\n");
    status = lvdt_calibrate_zero(&lvdt_dev, LVDT_DEFAULT_CALIB_SAMPLES);
    if (status == LVDT_OK) {
        printf("Калібрування нуля успішне! V_zero = %.4f V\n", lvdt_dev.zero_offset_volts);
    } else {
        printf("Помилка калібрування нуля: %s\n", status_to_string(status));
        return -1;
    }

    /* 4. Тестовий сценарій: симуляція зміни положення сердечника */
    float test_voltages[] = {
        1.65f,  /* Нульова позиція (0.0 мм) */
        1.90f,  /* Переміщення в плюс (1.90V - 1.65V = +0.25V -> +5.0 мм) */
        2.41f,  /* Переміщення в плюс (2.41V - 1.65V = +0.76V -> +15.2 мм) */
        2.875f, /* Переміщення в плюс (2.875V - 1.65V = +1.225V -> +24.5 мм) */
        3.10f,  /* Перевищення робочого ходу (+29.0 мм > +25.0 мм) */
        1.15f,  /* Переміщення в мінус (1.15V - 1.65V = -0.50V -> -10.0 мм) */
        0.63f,  /* Переміщення в мінус (0.63V - 1.65V = -1.02V -> -20.4 мм) */
        0.05f   /* Аварійний стан: обрив сигнального дроту (< 0.10V) */
    };

    size_t num_tests = sizeof(test_voltages) / sizeof(test_voltages[0]);

    printf("\n--- Запуск обробки вибірок LVDT ---\n");
    printf("%-5s | %-8s | %-8s | %-8s | %-12s | %-30s\n",
           "Крок", "V_in (В)", "V_ema(В)", "ADC raw", "Зсув (мм)", "Статус");
    printf("-----------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < num_tests; i++) {
        /* Встановлюємо симуляцію напруги з аналогового кондиціонера */
        adc_hal_set_simulated_voltage(test_voltages[i]);

        /* Для спостереження за роботу EMA виконуємо кілька ітерацій згладжування */
        lvdt_reading_t reading;
        for (int step = 0; step < 5; step++) {
            lvdt_process_sample(&lvdt_dev, &reading);
        }

        printf("[%2zu]  | %-8.3f | %-8.3f | %-8u | %-12.2f | %-30s\n",
               i + 1,
               reading.raw_voltage_v,
               reading.filtered_voltage_v,
               reading.raw_adc,
               reading.displacement_mm,
               status_to_string(reading.status));
    }

    printf("===================================================================\n");
    printf("Демонстрацію роботи LVDT успішно завершено.\n");

    return 0;
}
