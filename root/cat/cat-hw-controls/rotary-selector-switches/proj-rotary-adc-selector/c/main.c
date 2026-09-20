#include <stdio.h>
#include "include/rotary_adc_selector.h"

/**
 * @brief Допоміжна функція друку результату опитування
 */
static void print_poll_result(uint16_t raw_adc, int8_t pos, rotary_status_t status) {
    printf("АЦП: %4u | ", raw_adc);

    switch (status) {
        case ROTARY_STATUS_OK:
            printf("СТАН: НОРМА   | Позиція: %2d\n", pos);
            break;
        case ROTARY_STATUS_ERR_SHORT_GND:
            printf("СТАН: АВАРІЯ  | Коротке замикання на Землю (GND)!\n");
            break;
        case ROTARY_STATUS_ERR_OPEN_CIRCUIT:
            printf("СТАН: АВАРІЯ  | Обрив шлейфу / Замикання на VCC!\n");
            break;
        case ROTARY_STATUS_ERR_OUT_OF_RANGE:
            printf("СТАН: ПОМИЛКА | Невизначений рівень напруги!\n");
            break;
        default:
            printf("СТАН: НЕВІДОМИЙ СТАН!\n");
            break;
    }
}

int main(void) {
    printf("=================================================================\n");
    printf("  Драйвер 12-позиційного аналогового галетного перемикача (C)\n");
    printf("=================================================================\n\n");

    /* 1. Задання конфігурації еталонних рівнів для 12-бітного АЦП (0..4095) */
    rotary_config_t config = {
        .reference_levels = {
            250,   /* Позиція 0 */
            577,   /* Позиція 1 */
            904,   /* Позиція 2 */
            1231,  /* Позиція 3 */
            1558,  /* Позиція 4 */
            1885,  /* Позиція 5 */
            2212,  /* Позиція 6 */
            2539,  /* Позиція 7 */
            2866,  /* Позиція 8 */
            3193,  /* Позиція 9 */
            3520,  /* Позиція 10 */
            3847   /* Позиція 11 */
        },
        .hysteresis_window = 60,    /* Вікно гістерезису ±60 відліків */
        .min_valid_adc = 100,       /* Нижчий рівень — коротке замикання GND */
        .max_valid_adc = 4000       /* Вищий рівень — обрив лінії VCC */
    };

    rotary_selector_t selector;
    rotary_status_t init_res = rotary_selector_init(&selector, &config);

    if (init_res != ROTARY_STATUS_OK) {
        printf("Помилка ініціалізації драйвера: %d\n", init_res);
        return 1;
    }

    printf("Драйвер успішно ініціалізовано.\n\n");

    /* 2. Набір тестових вимірювань (симуляція АЦП) */
    const uint16_t test_adc_stream[] = {
        /* Фаза 1: Установка та стабілізація на Позиції 0 */
        250, 252, 248,

        /* Фаза 2: Перемикання на Позицію 2 */
        900, 905, 904,

        /* Фаза 3: Перемикання на Позицію 5 із високою імпульсною завадою (СПАЙК) */
        1880, 4000, 1885, /* Значення 4000 — одинична завада, яку має відсікти медіанний фільтр */

        /* Фаза 4: Тест цифрового гістерезису біля Позиції 5 (невеликий омічний дрейф) */
        1930, 1935, 1925,

        /* Фаза 5: Симуляція короткого замикання шлейфу на Землю (GND) */
        30, 25, 20,

        /* Фаза 6: Відновлення роботи на Позиції 7 */
        2540, 2538, 2542,

        /* Фаза 7: Симуляція обриву кабельного шлейфу (напруга підтягується до VCC) */
        4085, 4090, 4095
    };

    size_t num_samples = sizeof(test_adc_stream) / sizeof(test_adc_stream[0]);

    printf("--- Початок циклу неблокуючого опитування АЦП ---\n");

    for (size_t i = 0; i < num_samples; i++) {
        uint16_t raw = test_adc_stream[i];
        int8_t current_pos = -1;

        rotary_status_t status = rotary_selector_update(&selector, raw, &current_pos);
        print_poll_result(raw, current_pos, status);
    }

    printf("\nТестування C-драйвера галетного перемикача завершено успішно.\n");
    return 0;
}
