#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "estop_diag.h"

/* Симуляція стану фізичної вхідної GPIO-лінії (0 - замкнено / Норма, 1 - розімкнено / Аварія) */
static bool sim_gpio_level = false;

static bool read_estop_gpio(void)
{
    return sim_gpio_level;
}

int main(void)
{
    printf("=== Неблокувальний драйвер кнопки аварійної зупинки (E-Stop) ===\n");

    estop_diag_t estop;
    estop_diag_init(&estop, read_estop_gpio, 20U);

    uint32_t system_millis = 0U;

    printf("[T=0 ms] Система запущена. Стан: %s\n",
           estop_diag_is_tripped(&estop) ? "АВАРІЯ" : "НОРМА");

    /* Цикл симуляції роботи системи протягом 150 мс */
    while (system_millis <= 150U) {
        /* Симуляція дій оператора: натискання кнопки грибка на 30-й мілісекунді */
        if (system_millis == 30U) {
            printf("\n--- [T=%u ms] ПОДІЯ: Фізичне натискання кнопки аварійного стопу! ---\n", system_millis);
            sim_gpio_level = true;
        }

        /* Симуляція відтискання грибка (повернення в норму) на 100-й мілісекунді */
        if (system_millis == 100U) {
            printf("\n--- [T=%u ms] ПОДІЯ: Повернення кнопки грибка в початковий стан ---\n", system_millis);
            sim_gpio_level = false;
        }

        /* Неблокувальне оновлення кінцевого автомата станів */
        estop_event_t event = estop_diag_update(&estop, system_millis);

        if (event == ESTOP_EVENT_TRIPPED) {
            printf("[T=%u ms] >>> УВАГА: Аварійне зупинення зафіксовано! Спрацювань: %u <<<\n",
                   system_millis, estop.total_trips_count);
        } else if (event == ESTOP_EVENT_RESET) {
            printf("[T=%u ms] >>> ІНФО: Контур безпеки відновлено. Готовий до роботи. <<<\n",
                   system_millis);
        }

        /* Крок системного таймера (симуляція основного циклу 5 мс) */
        system_millis += 5U;
    }

    printf("\n=== Завершення роботи симулятора ===\n");
    return 0;
}
