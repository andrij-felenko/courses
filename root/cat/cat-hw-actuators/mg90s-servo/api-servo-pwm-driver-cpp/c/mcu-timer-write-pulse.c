#include "servo_driver.h"
#include <stdio.h>

// Приклад адаптера для запису в регістри CCR мікроконтролера
void mcu_timer_write_pulse(void *timer_instance, uint32_t channel, uint16_t pulse_us) {
    // У реальному коді для STM32:
    // TIM_TypeDef *tim = (TIM_TypeDef *)timer_instance;
    // switch(channel) { case 1: tim->CCR1 = pulse_us; break; ... }
    (void)timer_instance;
    (void)channel;
    (void)pulse_us;
}

void mcu_timer_set_enabled(void *timer_instance, uint32_t channel, bool enable) {
    // У реальному коді: TIM_CCxChannelCmd((TIM_TypeDef *)timer_instance, channel, enable ? TIM_CCx_Enable : TIM_CCx_Disable);
    (void)timer_instance;
    (void)channel;
    (void)enable;
}

#define NUM_SERVOS 3

typedef enum {
    AXIS_BASE = 0,
    AXIS_SHOULDER = 1,
    AXIS_WRIST = 2
} manipulator_axis_t;

int main(void) {
    // 1. Створюємо таблицю апаратних функцій
    servo_hal_ops_t hal_ops = {
        .write_pulse = mcu_timer_write_pulse,
        .set_enabled = mcu_timer_set_enabled
    };

    // 2. Масив дескрипторів для кожного привода
    servo_t manipulator[NUM_SERVOS];

    // 3. Ініціалізація кожного сервопривода з індивідуальним калібруванням
    // Основа: діапазон 560–2480 мкс, 180°
    servo_init(&manipulator[AXIS_BASE], (void*)0x40000000, 1, &hal_ops, 560, 2480, 180.0f);
    // Плече: діапазон 540–2420 мкс, 180°
    servo_init(&manipulator[AXIS_SHOULDER], (void*)0x40000000, 2, &hal_ops, 540, 2420, 180.0f);
    // Зап'ясток: діапазон 580–2500 мкс, 180°
    servo_init(&manipulator[AXIS_WRIST], (void*)0x40000000, 3, &hal_ops, 580, 2500, 180.0f);

    // 4. Безпечне підключення живлення та ініціалізація вихідного положення
    for (int i = 0; i < NUM_SERVOS; ++i) {
        servo_attach(&manipulator[i]);
    }

    // 5. Завдання нової просторової позиції з різними швидкостями осей
    servo_set_target_angle(&manipulator[AXIS_BASE], 90.0f, 60.0f);      // 60 град/с для важкої основи
    servo_set_target_angle(&manipulator[AXIS_SHOULDER], 45.0f, 40.0f);  // 40 град/с для плеча
    servo_set_target_angle(&manipulator[AXIS_WRIST], 135.0f, 120.0f);   // 120 град/с для легкого зап'ястка

    // 6. Періодичний робочий цикл оновлення (наприклад, у тасці FreeRTOS з періодом 20 мс)
    const uint32_t loop_period_ms = 20;
    bool all_axes_reached = false;

    while (!all_axes_reached) {
        all_axes_reached = true;

        for (int i = 0; i < NUM_SERVOS; ++i) {
            bool reached = servo_update(&manipulator[i], loop_period_ms);
            if (!reached) {
                all_axes_reached = false;
            }
        }

        // Тут викликається системна затримка vTaskDelayUntil(&last_wake_time, pdMS_TO_TICKS(20))
        // для точного витримування 20-мілісекундної сітки квантування
    }

    // 7. Переведення приводів у режим очікування для зняття струму утримання
    for (int i = 0; i < NUM_SERVOS; ++i) {
        servo_detach(&manipulator[i]);
    }

    return 0;
}
