// ── Керування сервами на UBEC-шині. ESP-IDF (ESP32, driver/ledc.h) ──
// Свій сигнал 50 Гц робимо апаратним LEDC; ширину рахуємо в скважність.
// 16 біт роздільності → плавний кут (~3277 сходинок на робочий діапазон).
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/ledc.h"

#define N 4
#define PERIOD_US 20000u                       // 1/50 Гц у мікросекундах
#define DUTY_MAX  ((1u << 16) - 1u)            // 16-бітна скважність

static const int PIN[N] = {25, 26, 27, 14};    // будь-які GPIO-виходи
static const ledc_channel_t CH[N] = {LEDC_CHANNEL_0, LEDC_CHANNEL_1,
                                     LEDC_CHANNEL_2, LEDC_CHANNEL_3};
static const uint16_t US_MIN = 1000, US_MID = 1500, US_MAX = 2000;

// мікросекунди ширини → відлік скважності LEDC
static uint32_t us_to_duty(uint16_t us) { return (uint32_t)us * DUTY_MAX / PERIOD_US; }

static uint16_t angle_to_us(uint8_t deg) {
    if (deg > 180) deg = 180;
    return US_MIN + (uint32_t)(US_MAX - US_MIN) * deg / 180;
}

void servo_init(void) {
    ledc_timer_config_t tim = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_16_BIT,
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = 50,                 // 20-мс кадр
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tim));
    for (int i = 0; i < N; i++) {
        ledc_channel_config_t ch = {
            .gpio_num   = PIN[i],
            .speed_mode = LEDC_LOW_SPEED_MODE,
            .channel    = CH[i],
            .intr_type  = LEDC_INTR_DISABLE,
            .timer_sel  = LEDC_TIMER_0,
            .duty       = us_to_duty(US_MID),  // старт із центру — безпечний кут
            .hpoint     = 0,
        };
        ESP_ERROR_CHECK(ledc_channel_config(&ch));
    }
}

// Повернути одне серво в кут. Ширину жене таймер, ми лише задаємо число.
void servo_write(uint8_t i, uint8_t deg) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, CH[i], us_to_duty(angle_to_us(deg)));
    ledc_update_duty(LEDC_LOW_SPEED_MODE, CH[i]);
}

void app_main(void) {
    servo_init();
    for (;;) {
        servo_write(0, 45);   // приклад: розкидати серва по кутах
        servo_write(1, 135);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
