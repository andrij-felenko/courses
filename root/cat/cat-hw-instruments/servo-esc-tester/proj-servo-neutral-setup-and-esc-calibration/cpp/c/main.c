#include <stdio.h>
#include "servo_tester.h"

/* Емуляція системи вимірювання часу мікроконтролера */
static uint32_t system_millis = 0;

static uint32_t get_system_ms(void) {
    return system_millis;
}

/* Симуляція оновлення значення регістра порівняння таймера ШІМ (CCR) */
static void mcu_timer_set_compare_us(uint16_t pulse_us) {
    /* На апаратному мікроконтролері (наприклад, STM32 або AVR):
     * TIM2->CCR1 = pulse_us;
     */
    (void)pulse_us;
}

int main(void) {
    servo_tester_t tester;
    servo_tester_init(&tester);

    printf("=== Тестер серво та ESC (C-реалізація) ===\n");
    printf("Початковий режим: NEUTRAL (1500 мкс)\n");

    /* Імітація кількох ітерацій головного керуючого циклу */
    uint16_t simulated_adc_pot = 2048U; /* Середнє положення потенціометра */
    bool simulated_button = false;

    for (int i = 0; i < 20; ++i) {
        system_millis += 10; /* Крок 10 мс */

        /* Обробка натискання кнопки на 30 мс та 120 мс */
        simulated_button = (system_millis >= 30 && system_millis <= 50) ||
                           (system_millis >= 120 && system_millis <= 140);

        servo_tester_process_button(&tester, simulated_button, get_system_ms());

        /* Оновлення в залежності від поточного режиму */
        if (tester.mode == SERVO_MODE_MANUAL) {
            servo_tester_update_manual(&tester, simulated_adc_pot);
        } else if (tester.mode == SERVO_MODE_AUTO_SWEEP) {
            servo_tester_update_sweep(&tester, get_system_ms());
        }

        servo_tester_update_esc_calibration(&tester, get_system_ms());

        /* Оновлення апаратного регістра ШІМ */
        mcu_timer_set_compare_us(tester.current_pulse_us);

        printf("[%4lu мс] Режим: %d | Імпульс ШІМ: %u мкс\n",
               (unsigned long)system_millis,
               tester.mode,
               tester.current_pulse_us);
    }

    return 0;
}
