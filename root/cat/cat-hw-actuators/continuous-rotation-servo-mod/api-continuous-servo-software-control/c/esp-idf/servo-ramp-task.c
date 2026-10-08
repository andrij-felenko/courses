#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
    mcpwm_unit_t unit;
    mcpwm_timer_t timer;
    volatile uint16_t current_us;
    volatile uint16_t target_us;
    uint16_t step_us;
} ramped_servo_t;

void servo_ramp_task(void *pvParameters) {
    ramped_servo_t *servo = (ramped_servo_t *)pvParameters;
    const TickType_t xDelay = pdMS_TO_TICKS(20); // Оновлення кожні 20 мс

    while (1) {
        if (servo->current_us < servo->target_us) {
            servo->current_us += servo->step_us;
            if (servo->current_us > servo->target_us) servo->current_us = servo->target_us;
        } else if (servo->current_us > servo->target_us) {
            servo->current_us -= servo->step_us;
            if (servo->current_us < servo->target_us) servo->current_us = servo->target_us;
        }

        mcpwm_set_us(servo->unit, servo->timer, MCPWM_OPR_A, servo->current_us);
        vTaskDelay(xDelay);
    }
}
