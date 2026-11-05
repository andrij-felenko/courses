#include <stdint.h>
#include <stdbool.h>
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"

#define SLEW_MAX_PPM          500LL  // Максимальна швидкість коригування (500 PPM = 0.05%)
#define SLEW_TARGET_TIME_US   10000000LL // Базовий час згладжування (10 сек)

typedef struct {
    int64_t base_offset_us;     // Базовий зсув часу
    int64_t error_remaining_us; // Залишкова похибка для slewing
    int64_t last_update_uptime; // Uptime останнього розрахунку slewing
    portMUX_TYPE lock;          // Спінлок для атомарності
} clock_slewer_t;

static clock_slewer_t g_slewer = {
    .base_offset_us = 0,
    .error_remaining_us = 0,
    .last_update_uptime = 0,
    .lock = portMUX_INITIALIZER_UNLOCKED
};

// Ініціалізація або ступенневе встановлення часу при великому розходженні
void clock_set_time_stepping(int64_t target_wall_us) {
    int64_t now_uptime = esp_timer_get_time();
    taskENTER_CRITICAL(&g_slewer.lock);
    g_slewer.base_offset_us = target_wall_us - now_uptime;
    g_slewer.error_remaining_us = 0;
    g_slewer.last_update_uptime = now_uptime;
    taskEXIT_CRITICAL(&g_slewer.lock);
}

// Запуск плавного підлаштування (slewing) при невеликому дрейфі
void clock_adjust_slewing(int64_t error_us) {
    taskENTER_CRITICAL(&g_slewer.lock);
    g_slewer.error_remaining_us += error_us;
    g_slewer.last_update_uptime = esp_timer_get_time();
    taskEXIT_CRITICAL(&g_slewer.lock);
}

// Зчитування поточного скоригованого календарного часу
int64_t clock_get_wall_time_us(void) {
    int64_t now_uptime = esp_timer_get_time();
    taskENTER_CRITICAL(&g_slewer.lock);
    
    int64_t dt = now_uptime - g_slewer.last_update_uptime;
    if (dt > 0 && g_slewer.error_remaining_us != 0) {
        // Обчислення допустимого зсуву за проміжок dt
        int64_t max_slew_delta = (dt * SLEW_MAX_PPM) / 1000000LL;
        int64_t apply_slew = 0;
        
        if (g_slewer.error_remaining_us > 0) {
            apply_slew = (g_slewer.error_remaining_us < max_slew_delta) ? g_slewer.error_remaining_us : max_slew_delta;
        } else {
            apply_slew = (g_slewer.error_remaining_us > -max_slew_delta) ? g_slewer.error_remaining_us : -max_slew_delta;
        }
        
        g_slewer.base_offset_us += apply_slew;
        g_slewer.error_remaining_us -= apply_slew;
        g_slewer.last_update_uptime = now_uptime;
    }
    
    int64_t wall_time = now_uptime + g_slewer.base_offset_us;
    taskEXIT_CRITICAL(&g_slewer.lock);
    return wall_time;
}
