#include <stdio.h>
#include "../include/stick_drift_filter.h"

int main(void) {
    printf("=================================================================\n");
    printf("  КОМПЕНСАЦІЯ ДРЕЙФУ НУЛЯ ТА РАДІАЛЬНА МЕРТВА ЗОНА СТИКА (C)\n");
    printf("=================================================================\n\n");

    /* 1. Ініціалізація стандартних калібрувальних даних для 12-бітного АЦП (0..4095) */
    stick_calibration_t cal = {
        .center_x = 2048, /* Еталонна центральна точка X */
        .center_y = 2048, /* Еталонна центральна точка Y */
        .min_x = 100,     /* Крайній лівий відлік */
        .max_x = 4000,    /* Крайній правий відлік */
        .min_y = 100,     /* Крайній нижній відлік */
        .max_y = 4000     /* Крайній верхній відлік */
    };

    /* 2. Симуляція процедури калібрування центральної точки при старті системи */
    uint16_t init_samples_x[5] = { 2070, 2065, 2072, 2068, 2075 }; /* Реальний дрейф центра АЦП */
    uint16_t init_samples_y[5] = { 2030, 2025, 2028, 2032, 2035 };

    printf(">>> Калібрування нейтральної точки АЦП...\n");
    if (stick_calibrate_center(&cal, init_samples_x, init_samples_y, 5)) {
        printf("Зміщена нейтраль зафіксована: CenterX = %u, CenterY = %u\n\n", cal.center_x, cal.center_y);
    }

    /* 3. Ініціалізація дескриптора фільтра (10% inner deadzone, 95% outer threshold, EMA alpha = 0.3) */
    stick_filter_t filter;
    if (!stick_filter_init(&filter, &cal, 0.10f, 0.95f, 0.30f)) {
        printf("ПОМИЛКА: Некоректні параметри ініціалізації фільтра!\n");
        return 1;
    }

    /* 4. Потік вимірювань для перевірки робочих режимів */
    struct {
        uint16_t raw_x;
        uint16_t raw_y;
        const char *description;
    } test_stream[] = {
        { 2070, 2030, "Нейтральний стан у межах мертвої зони (дрейф нуля)" },
        { 2075, 2025, "Дрібне тремтіння важеля у центрі" },
        { 2300, 2030, "Легке відхилення праворуч (початок виходу з мертвої зони)" },
        { 3000, 3000, "Діагональне відхилення у 45 градусів (півсили)" },
        { 3980, 3980, "Повне відхилення важеля у крайній кут (зона насичення)" },
        { 2070, 2030, "Повернення важеля у нейтральний стан" }
    };

    size_t stream_size = sizeof(test_stream) / sizeof(test_stream[0]);

    printf("--- Початок обробки потоку аналогових даних ---\n");
    for (size_t i = 0; i < stream_size; i++) {
        stick_output_t out;
        stick_filter_process(&filter, test_stream[i].raw_x, test_stream[i].raw_y, &out);

        printf("Тест %u: %s\n", (unsigned int)(i + 1), test_stream[i].description);
        printf("  Сирі АЦП:   X = %4u, Y = %4u\n", test_stream[i].raw_x, test_stream[i].raw_y);
        printf("  Вихід фільтра: X = %6.3f, Y = %6.3f | Довжина вектора R = %.3f\n\n",
               out.x, out.y, out.magnitude);
    }

    printf("Обробку даних завершено успішно.\n");
    return 0;
}
