#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "dc_motor_130.h"

/**
 * @file main.c
 * @brief Приклад практичного застосування C-драйвера для колекторного двигуна типорозміру 130.
 * 
 * Програма демонструє:
 * 1. Ініціалізацію апаратури MCU (GPIO IN1/IN2, ШІМ 20 кГц) та конфігурацію Dead Time 200 мкс.
 * 2. Плавний розгін двигуна від 0% до 100% заповнення ШІМ.
 * 3. Безпечний реверс напрямку обертання з обов'язковим програмним Dead Time.
 * 4. Порівняльний аналіз режимів зупинки: Інерційний вибіг (COAST) vs Активне гальмування (BRAKE).
 * 5. Обробку помилок передачі параметрів та аварійне вимкнення.
 */

/* Допоміжна функція для друку поточного стану двигуна у консоль */
static void print_motor_status(const dc_motor_t *motor, const char *step_description) {
    printf("[%s]\n", step_description);
    printf("  Напрямок : %s\n", dc_motor_dir_to_string(motor->direction));
    printf("  Швидкість: %d%%\n", motor->duty_cycle);
    printf("  Режим stop: %s\n", dc_motor_stop_mode_to_string(motor->stop_mode));
    printf("  Стан драйвера: ");
    switch (motor->state) {
        case DC_MOTOR_STATE_IDLE:      printf("IDLE (Вимкнено)\n"); break;
        case DC_MOTOR_STATE_RUNNING:   printf("RUNNING (Обертання)\n"); break;
        case DC_MOTOR_STATE_DEAD_TIME: printf("DEAD_TIME (Захисна пауза)\n"); break;
        case DC_MOTOR_STATE_BRAKING:   printf("BRAKING (Активне гальмування)\n"); break;
        default:                       printf("НЕВІДОМИЙ\n"); break;
    }
    printf("---------------------------------------------------------------\n");
}

int main(void) {
    printf("===============================================================\n");
    printf("  МОДУЛЬНИЙ C-ДРАЙВЕР КОЛЕКТОРНОГО ДВИГУНА ТИПОРОЗМІРУ 130\n");
    printf("===============================================================\n\n");

    /* КРОК 1: Налаштування структури конфігурації периферії H-моста */
    dc_motor_config_t motor_cfg = {
        .pin_in1 = 4,                   /* GPIO 4 для керування IN1 */
        .pin_in2 = 5,                   /* GPIO 5 для керування IN2 */
        .pwm_channel = 1,               /* Канал 1 ШІМ-таймера для Enable (EN) */
        .pwm_frequency_hz = 20000,      /* Частота ШІМ 20 кГц (вище порогу чутності) */
        .dead_time_us = 200,            /* Захисний Dead Time 200 мкс при реверсі */
        .default_stop = DC_MOTOR_STOP_COAST
    };

    dc_motor_t motor;

    /* КРОК 2: Ініціалізація C-драйвера двигуна */
    printf("[ІНІЦІАЛІЗАЦІЯ] Налаштування периферії MCU та H-моста...\n");
    dc_motor_err_t err = dc_motor_init(&motor, &motor_cfg);
    if (err != DC_MOTOR_OK) {
        printf("[ПОМИЛКА] Збій ініціалізації мотора: %s\n", dc_motor_err_to_string(err));
        return EXIT_FAILURE;
    }
    printf("[УСПІХ] Драйвер ініціалізовано. Dead Time встанолено на %u мкс.\n\n", motor_cfg.dead_time_us);
    print_motor_status(&motor, "Стан після ініціалізації");

    /* КРОК 3: Плавний розгін двигуна в прямому напрямку (FORWARD) */
    printf("[РОЗГІН] Плавне нарощування швидкості в напрямку FORWARD...\n");
    dc_motor_set_direction(&motor, DC_MOTOR_DIR_FORWARD);
    
    uint8_t speed_steps[] = {25, 50, 75, 100};
    for (size_t i = 0; i < sizeof(speed_steps)/sizeof(speed_steps[0]); i++) {
        uint8_t speed = speed_steps[i];
        dc_motor_set_speed(&motor, speed);
        printf("  Коригування ШІМ -> %d%%\n", speed);
    }
    printf("\n");
    print_motor_status(&motor, "Максимальна швидкість FORWARD (100%)");

    /* КРОК 4: Демонстрація безпечного реверсу з витриманням Dead Time */
    printf("[РЕВЕРС] Запит на зміну напрямку FORWARD -> REVERSE при 80%% ШІМ...\n");
    printf("  [DEAD TIME]: Драйвер відключає IN1/IN2 та чекає %u мкс для усунення наскрізних струмів...\n", motor_cfg.dead_time_us);
    err = dc_motor_drive(&motor, DC_MOTOR_DIR_REVERSE, 80);
    if (err != DC_MOTOR_OK) {
        printf("[ПОМИЛКА] Не вдалося виконати реверс: %s\n", dc_motor_err_to_string(err));
    }
    printf("\n");
    print_motor_status(&motor, "Після безпечного реверсу (REVERSE 80%)");

    /* КРОК 5: Демонстрація режиму 1 — Інерційний вибіг (COAST STOP) */
    printf("[ЗУПИНКА] Виконання зупинки в режимі ІНЕРЦІЙНОГО ВИБІГУ (COAST)...\n");
    printf("  [ПОЯСНЕННЯ]: Ключі H-моста розмикаються (IN1=0, IN2=0, EN=0). Вал зупиняється природно.\n");
    dc_motor_stop(&motor, DC_MOTOR_STOP_COAST);
    printf("\n");
    print_motor_status(&motor, "Зупинка COAST (Інерційний вибіг)");

    /* КРОК 6: Повторний запуск та демонстрація режиму 2 — Активне гальмування (BRAKE STOP) */
    printf("[АКТИВАЦІЯ] Запуск мотора FORWARD 70%% для демонстрації активного гальмування...\n");
    dc_motor_drive(&motor, DC_MOTOR_DIR_FORWARD, 70);
    print_motor_status(&motor, "Рух перед активним гальмуванням");

    printf("[ЗУПИНКА] Виконання АКТИВНОГО РЕВЕРСИВНОГО ГАЛЬМУВАННЯ (BRAKE)...\n");
    printf("  [ПОЯСНЕННЯ]: Обмотки мотора коротко замикаються (IN1=1, IN2=1, EN=100%%).\n");
    printf("               Виникає гальмівний момент від проти-ЕРС для швидкої зупинки вала.\n");
    dc_motor_stop(&motor, DC_MOTOR_STOP_BRAKE);
    printf("\n");
    print_motor_status(&motor, "Зупинка BRAKE (Активне гальмування)");

    /* КРОК 7: Демонстрація перевірки та обробки помилок */
    printf("[ОБРОБКА ПОМИЛОК] Спроба встановлення неприпустимої швидкості (150%%)...\n");
    err = dc_motor_set_speed(&motor, 150);
    printf("  Результат перевірки: %s (код: %d)\n\n", dc_motor_err_to_string(err), err);

    /* КРОК 8: Аварійна зупинка */
    printf("[АВАРІЯ] Симуляція аварійної зупинки emergency_stop()...\n");
    dc_motor_emergency_stop(&motor);
    print_motor_status(&motor, "Стан після emergency_stop()");

    printf("===============================================================\n");
    printf("  ДЕМОНСТРАЦІЮ C-ДРАЙВЕРА МОТОРА 130 УСПІШНО ЗАВЕРШЕНО\n");
    printf("===============================================================\n");

    return EXIT_SUCCESS;
}
