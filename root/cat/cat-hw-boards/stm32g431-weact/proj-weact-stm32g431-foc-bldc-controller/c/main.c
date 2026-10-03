#include "mcu_periph.h"
#include "foc.h"
#include <stdio.h>
#include <stdbool.h>

// Статичний екземпляр ядра векторного керування
static foc_state_t g_foc_controller;

int main(void) {
    // 1. Конфігурація периферійних вузлів STM32G431
    mcu_periph_config_t periph_cfg = {
        .pwm_frequency_hz   = 20000,   // Частота ШІМ 20 кГц
        .dead_time_ns       = 1000,    // Мертвий час 1 мкс для захисту силових ключів
        .shunt_resistor_ohm = 0.010f,  // Опір фазних шунтів 10 мОм
        .opamp_gain         = 16.0f,   // Коефіцієнт підсилення вбудованих OPAMP x16
        .adc_vref           = 3.3f     // Опорна напруга АЦП 3.3 В
    };

    if (!mcu_periph_init(&periph_cfg)) {
        // Помилка ініціалізації периферії
        return -1;
    }

    // 2. Виконання автоматичного калібрування нуля струмових підсилювачів OPAMP
    mcu_periph_calibrate_current_offsets();

    // 3. Ініціалізація векторного контролера (FOC)
    uint16_t pwm_period = mcu_periph_get_pwm_period();
    foc_init(&g_foc_controller, 24.0f, pwm_period); // Силова шина 24 В

    // Встановлення заданої швидкості обертання двигуна (100 радіан/с)
    g_foc_controller.target_speed = 100.0f;

    // 4. Ввімкнення силого ШІМ-виходу таймера TIM1 (активація біта MOE)
    mcu_periph_enable_pwm(true);

    // Періоди квантування контурів керування
    const float dt_current = 0.00005f; // 20 кГц (50 мкс)
    const float dt_speed   = 0.001f;   // 1 кГц (1 мс)

    float speed_loop_timer = 0.0f;
    float telemetry_timer  = 0.0f;

    // 5. Головний неблокувальний цикл обробки
    while (1) {
        // Швидкий контур струмів (викликається в ISR АЦП у реальній системі)
        foc_update_current_loop(&g_foc_controller, dt_current);

        // Імітація обертання ротора та зміни електричного кута
        g_foc_controller.electrical_angle += g_foc_controller.measured_speed * dt_current;
        if (g_foc_controller.electrical_angle > 6.28318530718f) {
            g_foc_controller.electrical_angle -= 6.28318530718f;
        }

        // Повільний контур регулювання швидкості (1 кГц)
        speed_loop_timer += dt_current;
        if (speed_loop_timer >= dt_speed) {
            speed_loop_timer = 0.0f;
            // Динамічна імітація розгону двигуна від момента моменту Iq
            g_foc_controller.measured_speed += (g_foc_controller.i_q * 2.0f - 0.1f * g_foc_controller.measured_speed) * dt_speed;
            foc_update_speed_loop(&g_foc_controller, dt_speed);
        }

        // Неблокувальне виведення відлагоджувальної телеметрії
        telemetry_timer += dt_current;
        if (telemetry_timer >= 0.1f) {
            telemetry_timer = 0.0f;
            // Телеметрична індикація стану приводу
        }
    }

    return 0;
}
