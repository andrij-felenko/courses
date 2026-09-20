#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "thumbwheel_74hc165.h"

// Модель станів апаратних GPIO-ліній для демонстрації
static bool sim_gpio_pl = true;
static bool sim_gpio_clk = false;
static uint16_t sim_shift_reg_data = 0x7359; // Емуляція BCD-коду 4 розрядів: '7', '3', '5', '9'
static uint8_t sim_shift_bit_count = 0;

// Симуляція колбеків керування GPIO-виводами
static void mcu_set_pl(bool level) {
    sim_gpio_pl = level;
    if (!level) {
        // При падінні PL паралельно завантажуємо BCD-коди у зсувний регістр
        sim_shift_bit_count = 0;
    }
}

static void mcu_set_clk(bool level) {
    bool rising_edge = (!sim_gpio_clk && level);
    sim_gpio_clk = level;

    if (rising_edge) {
        // По наростанню тактового сигналу зсуваємо регістр
        sim_shift_reg_data <<= 1;
        sim_shift_bit_count++;
    }
}

static bool mcu_read_q7(void) {
    // Зчитуємо старший біт emulated 16-бітного регістра
    return (sim_shift_reg_data & 0x8000) != 0;
}

static void mcu_delay_us(uint32_t us) {
    // У реальному МК тут викликається затримка таймера або nop-цикл
    (void)us;
}

int main(void) {
    printf("=== Промисловий C-драйвер зчитування BCD-перемикачів 74HC165 ===\n\n");

    // Конфігурація 4-розрядного блоку перемикачів
    thumbwheel_config_t config = {
        .set_pl = mcu_set_pl,
        .set_clk = mcu_set_clk,
        .read_q7 = mcu_read_q7,
        .delay_us = mcu_delay_us,
        .num_digits = 4,
        .active_low_logic = false // Комплементарний BCD (активна 1)
    };

    thumbwheel_driver_t driver;
    thumbwheel_status_t status = thumbwheel_init(&driver, &config);

    if (status != THUMBWHEEL_OK) {
        printf("Помилка ініціалізації драйвера: %d\n", status);
        return 1;
    }

    printf("Драйвер успішно ініціалізовано для %d розрядів.\n", config.num_digits);
    printf("Початок циклу опитування BCD-шини...\n\n");

    // Емуляція серії опитувань 4-розрядного блоку (значення 7359)
    for (int cycle = 1; cycle <= 7; cycle++) {
        // Відновлюємо симульований BCD-код 7359 у регістрі перед кожним кадром
        sim_shift_reg_data = 0x7359;

        uint32_t value = 0;
        status = thumbwheel_read_value(&driver, &value);

        if (status == THUMBWHEEL_OK) {
            printf("[Цикл %d] Валідне зчитане значення устави: %04u\n", cycle, value);
        } else if (status == THUMBWHEEL_ERR_TRANSIT_CODE) {
            printf("[Цикл %d] Проміжний транзитний стан! Попереднє підтверджене значення: %04u\n", cycle, value);
        } else {
            printf("[Цикл %d] Збій зчитування з кодом: %d\n", cycle, status);
        }
    }

    printf("\nОпитування завершено успішно.\n");
    return 0;
}
