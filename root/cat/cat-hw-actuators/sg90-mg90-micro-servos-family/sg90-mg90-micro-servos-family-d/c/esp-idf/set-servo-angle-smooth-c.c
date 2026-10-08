#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/mcpwm_prelude.h"

// Алгоритм плавного трапецеїдального розгону вала сервопривода
// Запобігає миттєвому пусковому сплеску струму (inrush current)
void set_servo_angle_smooth_c(mcpwm_cmpr_handle_t cmpr, int start_pulse_us, int target_pulse_us, int step_us, int delay_ms) {
    int current_pulse = start_pulse_us;
    
    if (target_pulse_us > start_pulse_us) {
        for (; current_pulse <= target_pulse_us; current_pulse += step_us) {
            mcpwm_comparator_set_compare_value(cmpr, current_pulse);
            vTaskDelay(pdMS_TO_TICKS(delay_ms));
        }
    } else {
        for (; current_pulse >= target_pulse_us; current_pulse -= step_us) {
            mcpwm_comparator_set_compare_value(cmpr, current_pulse);
            vTaskDelay(pdMS_TO_TICKS(delay_ms));
        }
    }
    // Фіксація кінцевого точного значення імпульсу
    mcpwm_comparator_set_compare_value(cmpr, target_pulse_us);
}
