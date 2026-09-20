#include <stdio.h>
#include <stdbool.h>
#include "thumbwheel_74hc165.h"

/**
 * @file main.c
 * @brief Приклад застосування драйвера опитування BCD-перемикачів 74HC165.
 */

int main(void) {
    printf("=== Драйвер декадних барабанних BCD-перемикачів (74HC165) ===\n");

    /* Конфігурація GPIO пінів для 74HC165 */
    thumbwheel_config_t tw_config = {
        .pin_pl = 4,        /* Parallel Load (PL) */
        .pin_clk = 5,       /* Clock (CLK) */
        .pin_q7 = 6,        /* Serial Data Out (Q7) */
        .debounce_ms = 50   /* Фільтрація брязкоту 50 мс */
    };

    thumbwheel_result_t tw_result;

    /* Ініціалізація апаратних ресурсів */
    thumbwheel_init(&tw_config);

    printf("Ініціалізацію успішно завершено. Початок зчитування...\n\n");

    /* Симуляція прямого зчитування */
    thumbwheel_status_t status = thumbwheel_read(&tw_config, &tw_result);

    if (status == THUMBWHEEL_OK) {
        printf("[Опитування OK] Зчитане 4-значне число: %04u\n", tw_result.value);
        printf("Розряди: [%u] [%u] [%u] [%u]\n",
               tw_result.digits[0], tw_result.digits[1],
               tw_result.digits[2], tw_result.digits[3]);
    } else if (status == THUMBWHEEL_ERR_INVALID_BCD) {
        printf("[Помилка BCD] Виявлено невалідний BCD-код у розряді %u!\n",
               tw_result.invalid_digit_index);
    }

    /* Симуляція неблокуючого циклу зчитування з обробкою брязкоту */
    printf("\n--- Симуляція неблокуючого циклу (Debouncing) ---\n");
    for (uint32_t ms = 0; ms <= 100; ms += 25) {
        bool updated = thumbwheel_update_nonblocking(&tw_config, ms, &tw_result);
        if (updated) {
            printf("Час %3u мс: [Оновлено] Стан стабільний, значення = %04u\n", ms, tw_result.value);
        } else {
            printf("Час %3u мс: [Фільтрація] Стабільний стан очікується...\n", ms);
        }
    }

    return 0;
}
