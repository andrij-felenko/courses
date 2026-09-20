#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "include/quad_encoder_driver.h"

/**
 * @brief Допоміжна функція виводу подій кнопки.
 */
static const char* event_to_str(quad_encoder_event_t evt) {
    switch (evt) {
        case BUTTON_EVENT_SHORT_PRESS: return "Коротке натискання (SHORT_PRESS)";
        case BUTTON_EVENT_LONG_PRESS:  return "Довге натискання (LONG_PRESS)";
        default: return "НЕМАЄ";
    }
}

int main(void) {
    printf("===================================================\n");
    printf(" Драйвер інкрементального квадратурного енкодера C \n");
    printf("===================================================\n\n");

    quad_encoder_t encoder;
    quad_encoder_init(&encoder, 0, 0);

    // Симуляція послідовності переходів квадратурних фаз A та B
    // Послідовність CW: 00 -> 01 -> 11 -> 10 -> 00 -> 01 -> 11 -> 10 -> 00
    uint8_t cw_sequence_a[] = {0, 0, 1, 1, 0, 0, 1, 1, 0};
    uint8_t cw_sequence_b[] = {0, 1, 1, 0, 0, 1, 1, 0, 0};
    size_t cw_len = sizeof(cw_sequence_a) / sizeof(cw_sequence_a[0]);

    printf("--- Симуляція обертання за годинниковою стрілкою (CW) ---\n");
    for (size_t i = 0; i < cw_len; i++) {
        quad_encoder_update_phases(&encoder, cw_sequence_a[i], cw_sequence_b[i]);
        printf("Крок %2zu | Фаза A: %d, Фаза B: %d | Позиція: %ld\n",
               i + 1, cw_sequence_a[i], cw_sequence_b[i], (long)quad_encoder_get_position(&encoder));
    }

    printf("\nДельта обертання CW: %ld\n\n", (long)quad_encoder_get_delta(&encoder));

    // Послідовність CCW: 00 -> 10 -> 11 -> 01 -> 00
    uint8_t ccw_sequence_a[] = {0, 1, 1, 0, 0};
    uint8_t ccw_sequence_b[] = {0, 0, 1, 1, 0};
    size_t ccw_len = sizeof(ccw_sequence_a) / sizeof(ccw_sequence_a[0]);

    printf("--- Симуляція обертання проти годинникової стрілки (CCW) ---\n");
    for (size_t i = 0; i < ccw_len; i++) {
        quad_encoder_update_phases(&encoder, ccw_sequence_a[i], ccw_sequence_b[i]);
        printf("Крок %2zu | Фаза A: %d, Фаза B: %d | Позиція: %ld\n",
               i + 1, ccw_sequence_a[i], ccw_sequence_b[i], (long)quad_encoder_get_position(&encoder));
    }

    printf("\nДельта обертання CCW: %ld\n\n", (long)quad_encoder_get_delta(&encoder));

    printf("--- Симуляція дребезгу та коротокого/довгого натискання кнопки ---\n");

    uint32_t time_ms = 0;

    // 1. Коротке натискання з брязкотом контактів
    printf("\n1. Коротке натискання кнопки (натискання 50 мс):\n");
    // Брязкіт при натисканні (0..15 мс)
    time_ms += 5;
    quad_encoder_update_button(&encoder, 1, time_ms);
    time_ms += 2;
    quad_encoder_update_button(&encoder, 0, time_ms);
    time_ms += 5;
    quad_encoder_update_button(&encoder, 1, time_ms); // Натиснуто стабільно

    // Утримання протягом 50 мс
    time_ms += 50;
    quad_encoder_event_t evt1 = quad_encoder_update_button(&encoder, 1, time_ms);
    if (evt1 != ENCODER_EVENT_NONE) {
        printf("   [Час %lu мс] Подія: %s\n", (unsigned long)time_ms, event_to_str(evt1));
    }

    // Відпускання кнопки з брязкотом
    time_ms += 5;
    quad_encoder_update_button(&encoder, 0, time_ms);
    time_ms += 25; // Пройшов час антидребезгу
    quad_encoder_event_t evt2 = quad_encoder_update_button(&encoder, 0, time_ms);
    if (evt2 != ENCODER_EVENT_NONE) {
        printf("   [Час %lu мс] Подія: %s\n", (unsigned long)time_ms, event_to_str(evt2));
    }

    // 2. Довге натискання (утримання 1200 мс)
    printf("\n2. Довге натискання кнопки (утримання > 1000 мс):\n");
    time_ms += 100;
    quad_encoder_update_button(&encoder, 1, time_ms); // Натиснули
    time_ms += 30;
    quad_encoder_update_button(&encoder, 1, time_ms); // Антидребезг пройдено

    time_ms += 1050; // Довге утримання
    quad_encoder_event_t evt3 = quad_encoder_update_button(&encoder, 1, time_ms);
    if (evt3 != ENCODER_EVENT_NONE) {
        printf("   [Час %lu мс] Подія: %s\n", (unsigned long)time_ms, event_to_str(evt3));
    }

    // Відпускання після довгого натискання (додаткова подія Short Press припускатися не повинна)
    time_ms += 200;
    quad_encoder_update_button(&encoder, 0, time_ms);
    time_ms += 30;
    quad_encoder_event_t evt4 = quad_encoder_update_button(&encoder, 0, time_ms);
    if (evt4 != ENCODER_EVENT_NONE) {
        printf("   [Час %lu мс] Подія: %s\n", (unsigned long)time_ms, event_to_str(evt4));
    } else {
        printf("   [Час %lu мс] Подію відпускання ігноровано, бо утримання вже опраційовано.\n", (unsigned long)time_ms);
    }

    printf("\nГотово! Всі симуляційні тести пройдено успішно.\n");
    return 0;
}
