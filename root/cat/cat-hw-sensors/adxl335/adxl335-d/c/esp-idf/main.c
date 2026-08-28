#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Осі X/Y/Z на каналах ADC1 (у класичного ESP32 це GPIO32/33/34)
#define AX ADC_CHANNEL_4
#define AY ADC_CHANNEL_5
#define AZ ADC_CHANNEL_6

// Тут опора АЦП — НЕ живлення: усередині 1.1 В плюс атенюатор, тож повна
// шкала при 12 дБ ≈ 3.1 В. Ратіометричність не рятує — калібруйте самі.
static const float FULL = 3.10f;    // вольтів на верхньому коді
static const float BIAS = 1.65f;    // 0g при 3.3 В ≈ половина живлення
static const float SENS = 0.330f;   // чутливість при 3.3 В ≈ 330 мВ/g

static const char *TAG = "adxl335";
static adc_oneshot_unit_handle_t adc;

static float read_axis_g(adc_channel_t ch)
{
    int raw = 0;
    ESP_ERROR_CHECK(adc_oneshot_read(adc, ch, &raw));   // 0..4095 (12 біт)
    float u = raw * FULL / 4095.0f;                     // код → вольти
    return (u - BIAS) / SENS;                           // вольти → g
}

static void adxl_task(void *arg)
{
    while (1) {
        ESP_LOGI(TAG, "%.2f\t%.2f\t%.2f",
                 read_axis_g(AX), read_axis_g(AY), read_axis_g(AZ));
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void app_main(void)
{
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc));

    adc_oneshot_chan_cfg_t cfg = {
        .atten    = ADC_ATTEN_DB_12,        // до ESP-IDF 5.2 звалося ADC_ATTEN_DB_11
        .bitwidth = ADC_BITWIDTH_DEFAULT,   // на ESP32 — 12 біт
    };
    for (adc_channel_t ch = AX; ch <= AZ; ch++)
        ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, ch, &cfg));

    xTaskCreate(adxl_task, "adxl", 3072, NULL, 5, NULL);
}
