#include <stdio.h>
#include "lvc_buffer.h"

/**
 * @file main.c
 * @brief Демонстраційний приклад ініціалізації двох буферів 74LVC1G125 та безпечної комутації.
 */

/* Імітація апаратних пінів GPIO для демонстрації */
static bool gpio_oe_buf1_level = true;
static bool gpio_oe_buf2_level = true;

static void set_oe_buf1(bool high) {
    gpio_oe_buf1_level = high;
    printf("[GPIO] Буфер 1 /OE встановлено у стан: %s (%s)\n", 
           high ? "HIGH" : "LOW", 
           high ? "Hi-Z (вимкнено)" : "ACTIVE (передає)");
}

static void set_oe_buf2(bool high) {
    gpio_oe_buf2_level = high;
    printf("[GPIO] Буфер 2 /OE встановлено у стан: %s (%s)\n", 
           high ? "HIGH" : "LOW", 
           high ? "Hi-Z (вимкнено)" : "ACTIVE (передає)");
}

/* Реалізація платформної затримки */
void platform_delay_us(uint32_t us) {
    printf("[DELAY] Затримка break-before-make: %u мкс (шинна ізоляція)\n", (unsigned int)us);
}

int main(void) {
    printf("=== Демонстрація роботи шинного буфера 74LVC1G125 (Break-Before-Make) ===\n\n");

    lvc_buffer_t buffer1;
    lvc_buffer_t buffer2;

    lvc_buffer_config_t config1 = {
        .set_oe_pin = set_oe_buf1,
        .delay_us = 2UL /* 2 мікросекунди захисного інтервалу */
    };

    lvc_buffer_config_t config2 = {
        .set_oe_pin = set_oe_buf2,
        .delay_us = 2UL
    };

    /* Ініціалізація обох буферів */
    if (!lvc_buffer_init(&buffer1, &config1) || !lvc_buffer_init(&buffer2, &config2)) {
        printf("Помилка ініціалізації буферів!\n");
        return -1;
    }

    printf("\n--- Крок 1: Увімкнення першого буфера на спільну шину ---\n");
    lvc_buffer_enable(&buffer1);

    printf("\n--- Крок 2: Безпечне перемикання з Буфера 1 на Буфер 2 (Break-Before-Make) ---\n");
    lvc_buffer_switch_channel(&buffer1, &buffer2);

    printf("\n--- Крок 3: Безпечне перемикання назад з Буфера 2 на Буфер 1 ---\n");
    lvc_buffer_switch_channel(&buffer2, &buffer1);

    printf("\n--- Крок 4: Вимкнення активного буфера ---\n");
    lvc_buffer_disable(&buffer1);

    printf("\nРоботу демонстрації завершено успішно.\n");
    return 0;
}
