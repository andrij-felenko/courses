#include <stdio.h>
#include "hall_gimbal.h"

int main(void) {
    printf("=== Драйвер джойстика на сенсорах Холла (C) ===\n\n");

    // Налаштування калібрувальних даних для 12-бітного АЦП (0..4095, центр ~2048)
    hall_gimbal_config_t config = {
        .axis_x = { .min_raw = 200, .center_raw = 2048, .max_raw = 3900 },
        .axis_y = { .min_raw = 200, .center_raw = 2048, .max_raw = 3900 },
        .deadzone_radial = 0.08f, // 8% мертва зона
        .alpha_ema = 0.25f        // Коефіцієнт згладжування EMA
    };

    hall_gimbal_t gimbal;
    if (hall_gimbal_init(&gimbal, &config) != HALL_GIMBAL_OK) {
        printf("Помилка ініціалізації джойстика!\n");
        return 1;
    }

    printf("Ініціалізація успішна. Початок опитування АЦП...\n\n");

    // Таблиця тестових відліків АЦП для двох осей X та Y
    struct {
        uint16_t raw_x;
        uint16_t raw_y;
        const char *desc;
    } test_samples[] = {
        { 2048, 2048, "Нейтральний стан (центр)" },
        { 2060, 2040, "Невелике зміщення в межах мертвої зони" },
        { 3900, 2048, "Повний відхил осі X вправо" },
        { 2048, 200,  "Повний відхил осі Y вниз" },
        { 3900, 3900, "Діагональний відхил (X=max, Y=max)" },
        { 10,   2048, "Апаратна помилка: обрив лінії Холла ( raw_x = 10 )" }
    };

    size_t sample_count = sizeof(test_samples) / sizeof(test_samples[0]);

    for (size_t i = 0; i < sample_count; i++) {
        printf("[Тест %zu] %s:\n", i + 1, test_samples[i].desc);
        printf("  Вхід АЦП: Raw X = %u, Raw Y = %u\n", test_samples[i].raw_x, test_samples[i].raw_y);

        // Симуляція кількох ітерацій фільтрації EMA
        hall_gimbal_output_t out;
        for (int step = 0; step < 5; step++) {
            out = hall_gimbal_process(&gimbal, test_samples[i].raw_x, test_samples[i].raw_y);
        }

        if (out.status == HALL_GIMBAL_OK) {
            printf("  Вихід: Norm X = %+.3f, Norm Y = %+.3f (Статус: ОК)\n\n", out.x, out.y);
        } else if (out.status == HALL_GIMBAL_ERR_OUT_OF_RANGE) {
            printf("  Вихід: ПРИЗПИНЕНО! Виявлено вихід за межі (Out of Range)\n\n");
        } else {
            printf("  Вихід: Помилка конфігурації калібрування!\n\n");
        }
    }

    return 0;
}
