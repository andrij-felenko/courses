#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "servo_cr_pwm.h"
#include "servo_calibration.h"

/**
 * @file main.c
 * @brief Головний модуль демонстрації низькорівневого керування сервоприводом постійного обертання.
 *
 * Демонструє ініціалізацію регістрів таймера, встановлення триммінгу нейтралі,
 * обробку зони нечутливості (Deadband) та плавну зміну швидкості й напрямку обертання.
 */

/* Імітація апаратних регістрів таймера МК у оперативній пам'яті */
static TIM_TypeDef g_hardware_timer_sim;

/**
 * @brief Допоміжна функція виведення поточного стану регістрів та сервоприводу.
 */
static void print_servo_status(const char *phase_description, const servo_calibration_params_t *cal_params)
{
    uint16_t current_ccr = (uint16_t)g_hardware_timer_sim.CCR1;
    float current_speed = servo_cr_pwm_get_speed();
    bool in_deadband = servo_calibration_is_in_deadband(cal_params, current_ccr);

    printf("[%s]\n", phase_description);
    printf("  -> CCR1 (Ширина імпульсу): %u мкс\n", current_ccr);
    printf("  -> Розрахована швидкість: %.1f%%\n", current_speed);
    printf("  -> Стан спокою (Deadband): %s\n\n", in_deadband ? "ТАК (Зупинено)" : "НІ (Обертається)");
}

int main(void)
{
    printf("====================================================================\n");
    printf("  Керування сервоприводом постійного обертання (Continuous Servo)  \n");
    printf("====================================================================\n\n");

    /* 1. Налаштування апаратного таймера (наприклад, STM32 TIM1 / TIM2 на частоті 72 МГц) */
    servo_cr_pwm_config_t timer_cfg = {
        .timer_instance = &g_hardware_timer_sim,
        .timer_clock_hz = 72000000U,         /* 72 МГц тактування периферії */
        .initial_pulse_us = SERVO_CR_PULSE_NEUTRAL_US, /* 1500 мкс */
        .invert_direction = false
    };

    printf("1. Ініціалізація апаратного таймера ШІМ...\n");
    if (servo_cr_pwm_init(&timer_cfg) != 0) {
        printf("ПОМИЛКА: Не вдалося ініціалізувати апаратний таймер ШІМ!\n");
        return -1;
    }

    printf("  - Prescaler (PSC): %u (тактування 1 МГц / 1 мкс тік)\n", (unsigned int)g_hardware_timer_sim.PSC);
    printf("  - Auto-reload (ARR): %u (період %u мкс = 50 Гц)\n",
           (unsigned int)g_hardware_timer_sim.ARR,
           (unsigned int)(g_hardware_timer_sim.ARR + 1U));
    printf("  - CCR1 початковий: %u мкс\n\n", (unsigned int)g_hardware_timer_sim.CCR1);

    /* 2. Ініціалізація та налаштування модуля калібрування */
    servo_calibration_params_t cal_params;
    servo_calibration_init_default(&cal_params);

    /* Компенсуємо апаратне зміщення внутрішнього потенціометра сервоприводу (+15 мкс) */
    servo_calibration_set_trim(&cal_params, 15);

    /* Встановлюємо півширину мертвої зони в 25 мкс для гарантованої відсутності дрейфу */
    servo_calibration_set_deadband(&cal_params, 25);

    printf("2. Налаштування програмного калібрування:\n");
    printf("  - Зсув нуля (Trim offset): %+d мкс\n", cal_params.trim_offset_us);
    printf("  - Мертва зона (Deadband): +/- %u мкс\n", cal_params.deadband_us);
    printf("  - Калібрована нейтраль: %d мкс\n\n", SERVO_CR_PULSE_NEUTRAL_US + cal_params.trim_offset_us);

    /* 3. Демонстрація роботи: Перевірка стану спокою (0% швидкості) */
    uint16_t pulse = servo_calibration_apply(&cal_params, 0.0f);
    servo_cr_pwm_set_pulse_us(pulse);
    print_servo_status("Етап 1: Зупинка в нейтральній зоні (0.0% швидкості)", &cal_params);

    /* 4. Обертання за годинниковою стрілкою (Прямий хід) */
    float speed_steps_fwd[] = { 15.0f, 50.0f, 100.0f };
    for (size_t i = 0; i < sizeof(speed_steps_fwd)/sizeof(speed_steps_fwd[0]); ++i) {
        char msg[80];
        snprintf(msg, sizeof(msg), "Етап 2: Обертання за годинниковою стрілкою (+%.1f%%)", speed_steps_fwd[i]);
        
        pulse = servo_calibration_apply(&cal_params, speed_steps_fwd[i]);
        servo_cr_pwm_set_pulse_us(pulse);
        print_servo_status(msg, &cal_params);
    }

    /* 5. Перевірка придушення малого шуму у межах мертвої зони (Deadband Filtering) */
    pulse = servo_calibration_apply(&cal_params, 2.0f); /* 2% швидкості занадто малі та попадають у мертву зону */
    servo_cr_pwm_set_pulse_us(pulse);
    print_servo_status("Етап 3: Спроба задання мікрокоманди +2.0% (Придушення Deadband)", &cal_params);

    /* 6. Обертання проти годинникової стрілки (Реверс) */
    float speed_steps_rev[] = { -25.0f, -75.0f, -100.0f };
    for (size_t i = 0; i < sizeof(speed_steps_rev)/sizeof(speed_steps_rev[0]); ++i) {
        char msg[80];
        snprintf(msg, sizeof(msg), "Етап 4: Обертання проти годинникової стрілки (%.1f%%)", speed_steps_rev[i]);
        
        pulse = servo_calibration_apply(&cal_params, speed_steps_rev[i]);
        servo_cr_pwm_set_pulse_us(pulse);
        print_servo_status(msg, &cal_params);
    }

    /* 7. Безпечна зупинка приводу */
    servo_cr_pwm_stop();
    print_servo_status("Етап 5: Завершення роботи та повна зупинка (servo_cr_pwm_stop)", &cal_params);

    printf("Демонстрацію успішно завершено.\n");
    return 0;
}
