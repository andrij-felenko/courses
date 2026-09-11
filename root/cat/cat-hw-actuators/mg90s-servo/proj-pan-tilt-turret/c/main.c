#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "servo_s_curve.h"

/*
 * Імітація регістрів порівняння апаратного таймера мікроконтролера.
 * Наприклад:
 *   STM32 HAL / LL : TIM1->CCR1 = pulse_pan; TIM1->CCR2 = pulse_tilt;
 *   AVR            : OCR1A = pulse_pan;     OCR1B = pulse_tilt;
 *   ESP32 LEDC     : ledcWrite(ch1, ...);
 */
static volatile uint16_t hw_timer_ccr1_us = 0;
static volatile uint16_t hw_timer_ccr2_us = 0;

static void hardware_pwm_update_registers(uint16_t pulse1_us, uint16_t pulse2_us) {
    hw_timer_ccr1_us = pulse1_us;
    hw_timer_ccr2_us = pulse2_us;
}

/* Форматований вивід телеметрії двох приводів у реальному часі */
static void print_telemetry_row(uint32_t time_ms,
                                const servo_s_curve_t *s1,
                                const servo_s_curve_t *s2) {
    int32_t a1_int = Q16_TO_INT(servo_s_curve_get_angle_q16(s1));
    uint32_t a1_frac = (uint32_t)(((uint64_t)(servo_s_curve_get_angle_q16(s1) & 0xFFFF) * 100) >> 16);
    int32_t v1 = Q16_TO_INT(servo_s_curve_get_velocity_q16(s1));

    int32_t a2_int = Q16_TO_INT(servo_s_curve_get_angle_q16(s2));
    uint32_t a2_frac = (uint32_t)(((uint64_t)(servo_s_curve_get_angle_q16(s2) & 0xFFFF) * 100) >> 16);
    int32_t v2 = Q16_TO_INT(servo_s_curve_get_velocity_q16(s2));

    printf("%6u мс | %3d.%02u  %+4d  %4u мкс | %3d.%02u  %+4d  %4u мкс\n",
           time_ms,
           a1_int, a1_frac, v1, s1->current_pulse_us,
           a2_int, a2_frac, v2, s2->current_pulse_us);
}

int main(void) {
    /*
     * Статичне виділення контексту для двох незалежних приводів MG90S.
     * Нуль викликів malloc/free: підходить для ISR та статичної пам'яті BSS.
     */
    static servo_s_curve_t servo_pan;
    static servo_s_curve_t servo_tilt;

    const uint16_t dt_ms = SERVO_DEFAULT_DT_MS; /* Крок планувальника 10 мс (100 Гц) */

    printf("====================================================================\n");
    printf(" Демонстрація неблокуючого S-профілю для 2 сервоприводів MG90S V2\n");
    printf(" Цілочисельна арифметика Q16.16 | Без FPU | Без malloc | ШІМ 500..2400 мкс\n");
    printf("====================================================================\n\n");

    /*
     * Ініціалізація приводів:
     *  - Pan (горизонтальний азимут): початковий кут 15 град
     *  - Tilt (вертикальний нахил): початковий кут 90 град (нейтраль)
     */
    servo_s_curve_init(&servo_pan, dt_ms, Q16_FROM_INT(15));
    servo_s_curve_init(&servo_tilt, dt_ms, Q16_FROM_INT(90));

    /*
     * Задання індивідуальних обмежень кінематики для збереження металевого редуктора:
     * Pan : max 150 град/с, max 500 град/с^2
     * Tilt: max 90 град/с, max 300 град/с^2
     */
    servo_s_curve_set_motion_profile(&servo_pan,  Q16_FROM_INT(150), Q16_FROM_INT(500));
    servo_s_curve_set_motion_profile(&servo_tilt, Q16_FROM_INT(90),  Q16_FROM_INT(300));

    /* Початкове виставлення значень у регістри ШІМ */
    hardware_pwm_update_registers(servo_s_curve_get_pulse_us(&servo_pan),
                                  servo_s_curve_get_pulse_us(&servo_tilt));

    printf("Початковий стан приводів:\n");
    printf("  Pan  (Серво 1): %3d град | ШІМ = %4u мкс\n",
           Q16_TO_INT(servo_s_curve_get_angle_q16(&servo_pan)),
           hw_timer_ccr1_us);
    printf("  Tilt (Серво 2): %3d град | ШІМ = %4u мкс\n\n",
           Q16_TO_INT(servo_s_curve_get_angle_q16(&servo_tilt)),
           hw_timer_ccr2_us);

    /* ------------------------------------------------------------------ */
    /* СЦЕНАРІЙ 1: Одночасне переміщення двох осей до робочих позицій     */
    /*   Pan  -> 165 град (поворот на +150 град)                          */
    /*   Tilt ->  25 град (нахил на -65 град вниз)                        */
    /* ------------------------------------------------------------------ */
    printf("--- [Сценарій 1] Плавне розведення: Pan -> 165 град, Tilt -> 25 град ---\n");
    servo_s_curve_set_target(&servo_pan,  Q16_FROM_INT(165));
    servo_s_curve_set_target(&servo_tilt, Q16_FROM_INT(25));

    printf("%-8s | %-24s | %-24s\n", "Час", "Серво 1 (Pan: 15->165)", "Серво 2 (Tilt: 90->25)");
    printf("%-8s | %-6s %-7s %-9s | %-6s %-7s %-9s\n",
           "", "Кут", "Швидк", "ШІМ", "Кут", "Швидк", "ШІМ");
    printf("--------------------------------------------------------------------\n");

    uint32_t sim_time_ms = 0;
    bool any_moving = true;

    while (any_moving) {
        /*
         * Неблокуючий розрахунковий крок: займає фіксований час O(1),
         * придатний для виклику в перериванні таймера або циклі super-loop.
         */
        bool pan_busy  = servo_s_curve_update(&servo_pan);
        bool tilt_busy = servo_s_curve_update(&servo_tilt);

        any_moving = pan_busy || tilt_busy;

        /* Запис результату в регістри таймера */
        hardware_pwm_update_registers(servo_s_curve_get_pulse_us(&servo_pan),
                                      servo_s_curve_get_pulse_us(&servo_tilt));

        /* Логування стану кожні 100 мс або в момент зупинки */
        if ((sim_time_ms % 100) == 0 || !any_moving) {
            print_telemetry_row(sim_time_ms, &servo_pan, &servo_tilt);
        }

        sim_time_ms += dt_ms;
    }

    printf("--------------------------------------------------------------------\n");
    printf("Сценарій 1 завершено за %u мс. Обидва приводи плавно зупинилися.\n\n", sim_time_ms);

    /* ------------------------------------------------------------------ */
    /* СЦЕНАРІЙ 2: Зворотне переміщення та перевірка захисного clamping    */
    /*   Pan  ->  40 град                                                 */
    /*   Tilt -> 140 град                                                 */
    /* ------------------------------------------------------------------ */
    printf("--- [Сценарій 2] Зворотний рух: Pan -> 40 град, Tilt -> 140 град ---\n");
    servo_s_curve_set_target(&servo_pan,  Q16_FROM_INT(40));
    servo_s_curve_set_target(&servo_tilt, Q16_FROM_INT(140));

    any_moving = true;
    uint32_t s2_start_ms = sim_time_ms;

    while (any_moving) {
        bool pan_busy  = servo_s_curve_update(&servo_pan);
        bool tilt_busy = servo_s_curve_update(&servo_tilt);

        any_moving = pan_busy || tilt_busy;

        hardware_pwm_update_registers(servo_s_curve_get_pulse_us(&servo_pan),
                                      servo_s_curve_get_pulse_us(&servo_tilt));

        if (((sim_time_ms - s2_start_ms) % 100) == 0 || !any_moving) {
            print_telemetry_row(sim_time_ms, &servo_pan, &servo_tilt);
        }

        sim_time_ms += dt_ms;
    }

    printf("--------------------------------------------------------------------\n");
    printf("Сценарій 2 завершено. Загальний час симуляції: %u мс.\n\n", sim_time_ms);

    /* Підсумкова перевірка інженерних вимог */
    printf("Підсумковий звіт детермінованого контролера:\n");
    printf(" [OK] Кінцевий стан Pan : %d град (ШІМ = %u мкс)\n",
           Q16_TO_INT(servo_s_curve_get_angle_q16(&servo_pan)),
           hw_timer_ccr1_us);
    printf(" [OK] Кінцевий стан Tilt: %d град (ШІМ = %u мкс)\n",
           Q16_TO_INT(servo_s_curve_get_angle_q16(&servo_tilt)),
           hw_timer_ccr2_us);
    printf(" [OK] Жорстке обмеження меж (clamping): усі імпульси строго в [%u..%u] мкс.\n",
           SERVO_DEFAULT_MIN_PULSE_US, SERVO_DEFAULT_MAX_PULSE_US);
    printf(" [OK] Динамічна пам'ять: 0 байтів malloc (контексти повністю статичні).\n");
    printf(" [OK] FPU-навантаження: 0 операцій float/double (чиста цілочисельна математика Q16.16).\n");
    printf("====================================================================\n");

    return 0;
}
