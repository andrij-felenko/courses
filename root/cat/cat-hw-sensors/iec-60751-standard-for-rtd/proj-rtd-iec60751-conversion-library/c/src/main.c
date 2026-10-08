#include "rtd_iec60751.h"
#include "rtd_lut.h"
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

static void print_separator(void) {
    printf("--------------------------------------------------------------------------------\n");
}

int main(void) {
    printf("================================================================================\n");
    printf("      МОДУЛЬ ОБРОБКИ СИГНАЛІВ RTD (IEC 60751): Pt100 / Pt1000 ТА LUT-МЕТОД      \n");
    printf("================================================================================\n\n");

    /* 1. Ініціалізація конфігурацій давачів */
    rtd_config_t rtd_pt100_a;
    rtd_config_t rtd_pt1000_b;

    if (rtd_init(&rtd_pt100_a, RTD_TYPE_PT100, RTD_CLASS_A) != RTD_SUCCESS ||
        rtd_init(&rtd_pt1000_b, RTD_TYPE_PT1000, RTD_CLASS_B) != RTD_SUCCESS) {
        printf("Помилка ініціалізації RTD конфігурації!\n");
        return 1;
    }

    /* 2. Ініціалізація таблиці LUT для мікроконтролерів без FPU */
    rtd_lut_t lut_pt100;
    if (rtd_lut_init(&lut_pt100, RTD_TYPE_PT100) != RTD_SUCCESS) {
        printf("Помилка ініціалізації LUT таблиці!\n");
        return 1;
    }

    printf("1. ТЕСТУВАННЯ ПРЯМОГО ТА ЗВОРОТНОГО ПЕРЕТВОРЕННЯ (Pt100, Клас A)\n");
    print_separator();
    printf(" Контрольна T | Розрахований R | Обчислена T (NR) | Похибка (°C) | Ітерацій \n");
    print_separator();

    double test_temperatures[] = {-150.0, -50.0, 0.0, 25.0, 100.0, 400.0, 750.0};
    size_t num_tests = sizeof(test_temperatures) / sizeof(test_temperatures[0]);

    for (size_t i = 0; i < num_tests; i++) {
        double t_true = test_temperatures[i];
        double r_calc = 0.0;
        double t_nr = 0.0;
        size_t iter_used = 0;

        /* Пряме перетворення: Температура -> Опір */
        rtd_temperature_to_resistance(&rtd_pt100_a, t_true, &r_calc);

        /* Зворотне перетворення методом Ньютона — Рафсона: Опір -> Температура */
        rtd_status_t st = rtd_resistance_to_temperature_nr(&rtd_pt100_a, r_calc, 1e-6, 20, &t_nr, &iter_used);

        if (st == RTD_SUCCESS) {
            double err = fabs(t_nr - t_true);
            printf(" %12.2f | %14.4f | %16.6f | %12.2e | %8zu \n",
                   t_true, r_calc, t_nr, err, iter_used);
        } else {
            printf(" %12.2f | Помилка обчислення методом Н-Р!\n", t_true);
        }
    }
    print_separator();
    printf("\n");

    /* 3. Валідація класів допуску IEC 60751 */
    printf("2. ПЕРЕВІРКА ВІДПОВІДНОСТІ КЛАСАМ ДОПУСКУ IEC 60751\n");
    print_separator();
    printf(" Клас  | Задана T (°C) | Опір (Ом) | Допуск (±°C) | Відхилення (°C) | Статус \n");
    print_separator();

    rtd_class_t classes[] = {RTD_CLASS_AA, RTD_CLASS_A, RTD_CLASS_B, RTD_CLASS_C};
    const char *class_names[] = {"AA", "A ", "B ", "C "};

    double sample_temp = 100.0;
    /* Симуляція реального вимірювання опору з незначним зміщенням +0.08 Ом */
    double r_nominal = 0.0;
    rtd_temperature_to_resistance(&rtd_pt100_a, sample_temp, &r_nominal);
    double r_measured = r_nominal + 0.08; /* Невеликий зсув для перевірки допусків */

    for (size_t c = 0; c < 4; c++) {
        rtd_config_t cfg;
        rtd_init(&cfg, RTD_TYPE_PT100, classes[c]);

        bool is_valid = false;
        double dev_c = 0.0;
        double tol_c = 0.0;

        rtd_get_tolerance_c(classes[c], sample_temp, &tol_c);
        rtd_validate_tolerance(&cfg, r_measured, sample_temp, &is_valid, &dev_c);

        printf("  %s   | %13.2f | %9.4f | %12.4f | %15.4f | %s \n",
               class_names[c], sample_temp, r_measured, tol_c, dev_c,
               is_valid ? "ВІДПОВІДАЄ" : "ПЕРЕВИЩЕНО");
    }
    print_separator();
    printf("\n");

    /* 4. Порівняння точного методу (NR) та оптимізованого LUT (без FPU) */
    printf("3. ПОРІВНЯННЯ МЕТОДУ НЬЮТОНА — РАФСОНА ТА LUT-ІНТЕРПОЛЯЦІЇ (MCU Без FPU)\n");
    print_separator();
    printf(" T real (°C) | R (мОм)   | T NR (°C)   | T LUT (°C)  | Різниця (°C) | Примітка \n");
    print_separator();

    double lut_test_temps[] = {-185.3, -42.7, 12.4, 87.6, 234.5, 610.8};
    size_t num_lut_tests = sizeof(lut_test_temps) / sizeof(lut_test_temps[0]);

    for (size_t i = 0; i < num_lut_tests; i++) {
        double t_real = lut_test_temps[i];
        double r_ohm = 0.0;
        rtd_temperature_to_resistance(&rtd_pt100_a, t_real, &r_ohm);

        uint32_t r_mohm = (uint32_t)(r_ohm * 1000.0 + 0.5);

        double t_nr = 0.0;
        rtd_resistance_to_temperature_nr(&rtd_pt100_a, r_ohm, 1e-6, 20, &t_nr, NULL);

        int32_t t_lut_mc = 0;
        rtd_lut_lookup_temp_mc(&lut_pt100, r_mohm, &t_lut_mc);
        double t_lut = (double)t_lut_mc / 1000.0;

        double diff = fabs(t_nr - t_lut);

        printf(" %11.2f | %9u | %11.4f | %11.3f | %12.4f | %s \n",
               t_real, r_mohm, t_nr, t_lut, diff,
               (diff < 0.05) ? "Висока точність" : "Допустиме відхилення");
    }
    print_separator();
    printf("Примітка: Обчислення T LUT виконано суто цілочисельною арифметикою!\n");
    printf("================================================================================\n");

    return 0;
}
