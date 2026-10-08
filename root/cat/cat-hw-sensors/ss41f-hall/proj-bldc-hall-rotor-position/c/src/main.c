#include <stdio.h>
#include "ss41f_hall.h"
#include "stm32_gpio_exti.h"

/**
 * @brief Обробник зміни електричного сектора ротора.
 */
static void on_sector_changed(hall_sector_t new_sector, hall_sector_t old_sector, uint8_t raw_code) {
    printf("[HALL LOG] Перехід сектора: %d -> %d | Код: %d%d%d (0x%02X)\n",
           (int)old_sector,
           (int)new_sector,
           (raw_code >> 2) & 1,
           (raw_code >> 1) & 1,
           raw_code & 1,
           raw_code);
}

/**
 * @brief Обробник апаратних та логічних помилок давачів Холла.
 */
static void on_hall_error(hall_error_t error, uint8_t raw_code) {
    switch (error) {
        case HALL_ERR_INVALID_CODE_000:
            printf("[HALL ERROR] Заборонений код 000! Обрив VCC/GND або сигнальних ліній.\n");
            break;
        case HALL_ERR_INVALID_CODE_111:
            printf("[HALL ERROR] Заборонений код 111! Коротке замикання на VCC або обрив ліній з pull-up.\n");
            break;
        case HALL_ERR_ILLEGAL_TRANSITION:
            printf("[HALL ERROR] Неприпустимий фазовий перехід! Сигнальний код: 0x%02X\n", raw_code);
            break;
        default:
            printf("[HALL ERROR] Невідома помилка: %d\n", (int)error);
            break;
    }
}

/**
 * @brief Зворотний виклик переривання EXTI для обробки змін на лініях GPIO.
 */
static void on_exti_trigger(uint8_t raw_code) {
    hall_process_state(raw_code);
}

int main(void) {
    printf("=== Старт системи моніторингу BLDC на давачах SS41F ===\n");

    /* 1. Ініціалізація драйвера давачів Холла */
    hall_init();
    hall_register_sector_callback(on_sector_changed);
    hall_register_error_callback(on_hall_error);

    /* 2. Ініціалізація модуля EXTI переривань STM32 */
    stm32_exti_register_callback(on_exti_trigger);
    stm32_gpio_exti_init();

    /* 3. Первинне зчитування початкового стану ротора */
    uint8_t initial_code = stm32_gpio_read_hall_pins();
    printf("Початковий стан ліній Hall (A, B, C): 0x%02X\n", initial_code);
    hall_process_state(initial_code);

    /* 4. Симуляція послідовності фазових переходів ротора BLDC (CW обертання) */
    printf("\n--- Симуляція нормального обертання ротора (CW) ---\n");
    const uint8_t cw_sequence[] = { 0b001, 0b011, 0b010, 0b110, 0b100, 0b101, 0b001 };
    for (size_t i = 0; i < sizeof(cw_sequence)/sizeof(cw_sequence[0]); i++) {
        hall_process_state(cw_sequence[i]);
    }

    /* 5. Симуляція апаратного збою (заборонений код 000) */
    printf("\n--- Симуляція апаратного збою (обрив живлення 000) ---\n");
    hall_process_state(0b000);

    /* 6. Симуляція забороненого коду (111) */
    printf("\n--- Симуляція апаратного збою (коротке замикання 111) ---\n");
    hall_process_state(0b111);

    /* 7. Отримання та виведення підсумкової телеметрії */
    hall_telemetry_t telemetry;
    hall_get_telemetry(&telemetry);

    printf("\n=== Підсумкова телеметрія драйвера ===\n");
    printf("Поточний сектор:      %d\n", (int)telemetry.current_sector);
    printf("Напрямок обертання:   %s\n", telemetry.direction == HALL_DIR_CW ? "CW" : 
                                         (telemetry.direction == HALL_DIR_CCW ? "CCW" : "UNKNOWN"));
    printf("Кількість переходів:  %lu\n", (unsigned long)telemetry.transition_count);
    printf("Кількість помилок:    %lu\n", (unsigned long)telemetry.error_count);
    printf("Остання помилка:      %d\n", (int)telemetry.last_error);

    return 0;
}
