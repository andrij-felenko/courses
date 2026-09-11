#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "driver/ledc.h"

#define SERVO_LEDC_TIMER       LEDC_TIMER_0
#define SERVO_LEDC_MODE        LEDC_LOW_SPEED_MODE
#define SERVO_LEDC_CHANNEL     LEDC_CHANNEL_0
#define SERVO_MIN_US           500
#define SERVO_MAX_US           2400

typedef struct {
    float current_angle;
    float start_angle;
    float target_angle;
    uint32_t total_duration_ms;
    int64_t start_time_us;
    bool is_moving;
} mg90s_profile_t;

static mg90s_profile_t g_servo_profile;

// Апаратне встановлення ширини імпульсу через LEDC (14 біт, період 20 мс)
static void servo_set_angle_hardware(float angle) {
    if (angle < 0.0f) angle = 0.0f;
    if (angle > 180.0f) angle = 180.0f;

    float pulse_us = SERVO_MIN_US + (angle / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US);
    // Коефіцієнт заповнення для 14 біт: 16384 рівнів на 20000 мкс
    uint32_t duty = (uint32_t)((pulse_us / 20000.0f) * 16384.0f);
    ledc_set_duty(SERVO_LEDC_MODE, SERVO_LEDC_CHANNEL, duty);
    ledc_update_duty(SERVO_LEDC_MODE, SERVO_LEDC_CHANNEL);
}

void mg90s_move_to_s_curve(float target_deg, uint32_t duration_ms) {
    g_servo_profile.start_angle = g_servo_profile.current_angle;
    g_servo_profile.target_angle = target_deg;
    g_servo_profile.total_duration_ms = (duration_ms < 20) ? 20 : duration_ms;
    g_servo_profile.start_time_us = esp_timer_get_time();
    g_servo_profile.is_moving = true;
}

// Функція кроку профілю (викликається таймером або таскою кожні 20 мс)
void mg90s_profile_update(void) {
    if (!g_servo_profile.is_moving) return;

    int64_t now_us = esp_timer_get_time();
    int64_t elapsed_us = now_us - g_servo_profile.start_time_us;
    float elapsed_ms = (float)elapsed_us / 1000.0f;

    if (elapsed_ms >= (float)g_servo_profile.total_duration_ms) {
        g_servo_profile.current_angle = g_servo_profile.target_angle;
        g_servo_profile.is_moving = false;
    } else {
        float tau = elapsed_ms / (float)g_servo_profile.total_duration_ms;
        float tau3 = tau * tau * tau;
        float tau4 = tau3 * tau;
        float tau5 = tau4 * tau;
        float s = 10.0f * tau3 - 15.0f * tau4 + 6.0f * tau5;

        g_servo_profile.current_angle = g_servo_profile.start_angle + 
            (g_servo_profile.target_angle - g_servo_profile.start_angle) * s;
    }

    servo_set_angle_hardware(g_servo_profile.current_angle);
}
