#include <stdio.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_log.h"

#define RELAY_GPIO           GPIO_NUM_18
#define ACS712_ADC_CHANNEL   ADC_CHANNEL_6 // GPIO34 на ESP32
#define SENSITIVITY_V_PER_A  0.185f        // 185 мВ/А для модифікації 5A
#define DIVIDER_RATIO        1.5f          // Коефіцієнт дільника 3.3V / 2.2V
#define OVERCURRENT_LIMIT    4.5f          // Поріг захисного відсікання в Амперах
#define CALIB_SAMPLES        100           // Кількість вибірок у спокої при старті
#define RMS_SAMPLES          200           // Кількість вибірок за вікно 20 мс (1 період 50 Гц)

static const char *TAG = "ACS712_MONITOR";
static float g_v_zero_calib = 1.65f;

static void init_relay_gpio(void)
{
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << RELAY_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(RELAY_GPIO, 1); // Реле увімкнено (живлення подано)
}

static void calibrate_zero_offset(adc_oneshot_unit_handle_t adc_handle)
{
    int raw_sum = 0;
    int raw_val = 0;

    ESP_LOGI(TAG, "Калібрування нуля спокою (переконайтеся у відсутності струму)...");
    for (int i = 0; i < CALIB_SAMPLES; i++) {
        adc_oneshot_read(adc_handle, ACS712_ADC_CHANNEL, &raw_val);
        raw_sum += raw_val;
        vTaskDelay(pdMS_TO_TICKS(2));
    }

    float avg_raw = (float)raw_sum / CALIB_SAMPLES;
    float v_pin = (avg_raw / 4095.0f) * 3.3f;
    g_v_zero_calib = v_pin * DIVIDER_RATIO;

    ESP_LOGI(TAG, "Калібрування завершено: V_zero = %.3f В (raw avg = %.1f)", g_v_zero_calib, avg_raw);
}

static float measure_rms_current(adc_oneshot_unit_handle_t adc_handle)
{
    float sum_sq = 0.0f;
    int raw_val = 0;

    for (int i = 0; i < RMS_SAMPLES; i++) {
        adc_oneshot_read(adc_handle, ACS712_ADC_CHANNEL, &raw_val);
        float v_pin = (raw_val / 4095.0f) * 3.3f;
        float v_out = v_pin * DIVIDER_RATIO;
        float i_inst = (v_out - g_v_zero_calib) / SENSITIVITY_V_PER_A;

        sum_sq += i_inst * i_inst;
        esp_rom_delay_us(100);
    }

    float mean_sq = sum_sq / RMS_SAMPLES;
    return sqrtf(mean_sq);
}

void app_main(void)
{
    init_relay_gpio();

    adc_oneshot_unit_handle_t adc1_handle;
    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1,
    };
    adc_oneshot_new_unit(&init_config1, &adc1_handle);

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_12,
        .atten = ADC_ATTEN_DB_12,
    };
    adc_oneshot_config_channel(adc1_handle, ACS712_ADC_CHANNEL, &config);

    calibrate_zero_offset(adc1_handle);

    ESP_LOGI(TAG, "Запуск моніторингу струму...");

    while (1) {
        float i_rms = measure_rms_current(adc1_handle);
        ESP_LOGI(TAG, "Виміряний струм RMS: %.3f A", i_rms);

        if (i_rms > OVERCURRENT_LIMIT) {
            gpio_set_level(RELAY_GPIO, 0); // Розмикання реле
            ESP_LOGE(TAG, "АВАРІЯ: Перевищення струму (%.3f A > %.1f A)! Навантаження відключено!",
                     i_rms, OVERCURRENT_LIMIT);
            break;
        }

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
