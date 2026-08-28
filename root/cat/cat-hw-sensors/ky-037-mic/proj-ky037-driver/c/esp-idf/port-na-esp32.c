#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdbool.h>

#define PIN_SOUND  GPIO_NUM_27         // DO — будь-який GPIO (gpio_get_level, не АЦП)
#define MIC_UNIT   ADC_UNIT_1          // AO — ТІЛЬКИ АЦП1: АЦП2 забирає Wi-Fi
#define MIC_CH     ADC_CHANNEL_6       // ADC1_CH6 = GPIO 34
#define DEAF_MS    250
#define WINDOW_MS  50

static const char *TAG = "clap";
static adc_oneshot_unit_handle_t s_adc1;

static int     g_idle;
static bool    g_wasLoud  = false;
static int64_t g_lastClap = 0;
static bool    g_lightOn  = false;

static inline int64_t now_ms(void) { return esp_timer_get_time() / 1000; }
static inline bool isLoud(void) { return gpio_get_level(PIN_SOUND) != g_idle; }

static int measure_peak_to_peak(void) {
    int64_t t0 = now_ms();
    int hi = 0, lo = 4095, v = 0;      // 12-бітний АЦП ESP32: діапазон 0..4095
    while (now_ms() - t0 < WINDOW_MS) {
        if (adc_oneshot_read(s_adc1, MIC_CH, &v) != ESP_OK) continue;
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    return hi - lo;
}

static void clap_task(void *arg) {
    int64_t lastPrint = 0;
    for (;;) {
        // --- подія оплеску (фронт + гістерезис) ---
        bool loud = isLoud();
        bool rising = loud && !g_wasLoud;
        g_wasLoud = loud;
        if (rising && now_ms() - g_lastClap >= DEAF_MS) {
            g_lastClap = now_ms();
            g_lightOn = !g_lightOn;
            ESP_LOGI(TAG, "%s", g_lightOn ? "оплеск → УВІМКНЕНО" : "оплеск → вимкнено");
        }

        // --- рівень гучності вікном (нечасто, щоб не забивати лог) ---
        if (now_ms() - lastPrint >= 300) {
            lastPrint = now_ms();
            ESP_LOGI(TAG, "рівень = %d", measure_peak_to_peak());
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

void app_main(void) {
    gpio_config_t in = { .pin_bit_mask = 1ULL << PIN_SOUND, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_DISABLE, .pull_down_en = GPIO_PULLDOWN_DISABLE,
                         .intr_type = GPIO_INTR_DISABLE };
    ESP_ERROR_CHECK(gpio_config(&in));

    adc_oneshot_unit_init_cfg_t unit = { .unit_id = MIC_UNIT };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &s_adc1));
    adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_12 };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc1, MIC_CH, &ch));

    vTaskDelay(pdMS_TO_TICKS(50));
    g_idle = gpio_get_level(PIN_SOUND);
    ESP_LOGI(TAG, "Спокій DO = %s", g_idle ? "HIGH" : "LOW");
    ESP_LOGI(TAG, "Плесни для перемикання; заодно друкую рівень гучності.");

    xTaskCreate(clap_task, "clap", 4096, NULL, 5, NULL);
}
