#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"          // esp_rom_delay_us
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TRIG_GPIO GPIO_NUM_5
#define ECHO_GPIO GPIO_NUM_18
#define ECHO_TIMEOUT_US 30000     // ~5 м межі дальності
static const char *TAG = "range";
static RangeFilter rf;

// Один відлік: відстань за часом луни + сила (тут — проксі; реальну дає давач).
static Sample read_ranger(void) {
    Sample s = { 0 };                                   // valid = false, поки луни нема
    s.t_ms = (uint32_t)(esp_timer_get_time() / 1000);   // мітка часу САМОГО виміру
    gpio_set_level(TRIG_GPIO, 0); esp_rom_delay_us(2);
    gpio_set_level(TRIG_GPIO, 1); esp_rom_delay_us(10);
    gpio_set_level(TRIG_GPIO, 0);

    int64_t t0 = esp_timer_get_time();
    while (gpio_get_level(ECHO_GPIO) == 0)              // чекаємо фронт луни
        if (esp_timer_get_time() - t0 > ECHO_TIMEOUT_US) return s;
    int64_t rise = esp_timer_get_time();
    while (gpio_get_level(ECHO_GPIO) == 1)              // міряємо ширину імпульсу
        if (esp_timer_get_time() - rise > ECHO_TIMEOUT_US) return s;
    uint32_t us = (uint32_t)(esp_timer_get_time() - rise);

    s.dist_mm  = (uint16_t)(us * 343UL / 2000UL);   // мкс → мм за c = 343 м/с, шлях туди-й-назад
    s.strength = read_echo_strength();              // АЦП піка луни / signal-rate ToF-давача
    s.valid    = true;
    return s;
}

static void range_task(void *arg) {
    gpio_config_t io = { .pin_bit_mask = 1ULL << TRIG_GPIO, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&io);
    io.pin_bit_mask = 1ULL << ECHO_GPIO; io.mode = GPIO_MODE_INPUT;
    gpio_config(&io);
    rf_init(&rf, 1500, 200, 800);   // зближення ≤1.5 м/с; підлога/стеля сили — за калібруванням

    for (;;) {
        RangeResult r = rf_update(&rf, read_ranger());
        switch (r.status) {
            case RF_FRESH:   // r.med_mm → керування (край), r.mm → показ (гладко)
                ESP_LOGI(TAG, "d=%u мм | гладко %u | довіра %.2f", r.med_mm, r.mm, r.conf);
                break;
            case RF_HELD:
                ESP_LOGW(TAG, "тримаю %u мм (пропуск/викид)", r.mm);
                break;
            case RF_LOST:
                ESP_LOGE(TAG, "ВІДСТАНЬ НЕВІДОМА -> стоп/обережно");
                break;
        }
        vTaskDelay(pdMS_TO_TICKS(20));   // ~50 Гц; крок входить у ворота через мітку часу
    }
}

void app_main(void) {
    xTaskCreate(range_task, "range", 4096, NULL, 5, NULL);
}
