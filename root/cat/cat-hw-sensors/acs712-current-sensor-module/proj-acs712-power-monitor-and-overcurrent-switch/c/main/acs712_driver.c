#include "acs712_driver.h"
#include <math.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "ACS712_DRIVER";

esp_err_t acs712_init(acs712_handle_t *handle, const acs712_config_t *config) {
    if (!handle || !config) return ESP_ERR_INVALID_ARG;

    handle->adc_channel = config->adc_channel;
    handle->relay_gpio = config->relay_gpio;
    handle->overcurrent_limit_a = config->overcurrent_limit_a;
    handle->hysteresis_a = config->hysteresis_a;
    handle->zero_voltage = config->vcc / 2.0f;
    handle->relay_state = false;

    switch (config->type) {
        case ACS712_TYPE_05B:
            handle->sensitivity_v_a = 0.185f;
            break;
        case ACS712_TYPE_20A:
            handle->sensitivity_v_a = 0.100f;
            break;
        case ACS712_TYPE_30A:
            handle->sensitivity_v_a = 0.066f;
            break;
        default:
            return ESP_ERR_INVALID_ARG;
    }

    adc_oneshot_unit_init_cfg_t init_config1 = {
        .unit_id = ADC_UNIT_1,
    };
    esp_err_t ret = adc_oneshot_new_unit(&init_config1, &handle->adc_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка створення юніта АЦП: %s", esp_err_to_name(ret));
        return ret;
    }

    adc_oneshot_chan_cfg_t chan_config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12,
    };
    ret = adc_oneshot_config_channel(handle->adc_handle, config->adc_channel, &chan_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка конфігурації каналу АЦП: %s", esp_err_to_name(ret));
        return ret;
    }

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << config->relay_gpio),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);
    gpio_set_level(config->relay_gpio, 0);

    return ESP_OK;
}

esp_err_t acs712_calibrate_zero(acs712_handle_t *handle, int num_samples) {
    if (!handle || num_samples <= 0) return ESP_ERR_INVALID_ARG;

    int sum_raw = 0;
    for (int i = 0; i < num_samples; i++) {
        int raw_val = 0;
        esp_err_t ret = adc_oneshot_read(handle->adc_handle, handle->adc_channel, &raw_val);
        if (ret != ESP_OK) return ret;
        sum_raw += raw_val;
        vTaskDelay(pdMS_TO_TICKS(2));
    }

    float avg_raw = (float)sum_raw / (float)num_samples;
    handle->zero_voltage = (avg_raw / 4095.0f) * 3.3f;
    ESP_LOGI(TAG, "Калібрування нуля завершено: V_zero = %.3f В", handle->zero_voltage);

    return ESP_OK;
}

esp_err_t acs712_read_current_dc(acs712_handle_t *handle, float *out_current) {
    if (!handle || !out_current) return ESP_ERR_INVALID_ARG;

    int raw_val = 0;
    esp_err_t ret = adc_oneshot_read(handle->adc_handle, handle->adc_channel, &raw_val);
    if (ret != ESP_OK) return ret;

    float voltage = ((float)raw_val / 4095.0f) * 3.3f;
    *out_current = (voltage - handle->zero_voltage) / handle->sensitivity_v_a;

    return ESP_OK;
}

esp_err_t acs712_read_current_rms(acs712_handle_t *handle, float frequency_hz, float *out_rms) {
    if (!handle || !out_rms || frequency_hz <= 0.0f) return ESP_ERR_INVALID_ARG;

    uint32_t period_us = (uint32_t)(1000000.0f / frequency_hz);
    int64_t start_time = esp_timer_get_time();

    double sum_squares = 0.0;
    int samples = 0;

    while ((esp_timer_get_time() - start_time) < period_us) {
        int raw_val = 0;
        if (adc_oneshot_read(handle->adc_handle, handle->adc_channel, &raw_val) == ESP_OK) {
            float voltage = ((float)raw_val / 4095.0f) * 3.3f;
            float current = (voltage - handle->zero_voltage) / handle->sensitivity_v_a;
            sum_squares += current * current;
            samples++;
        }
        esp_rom_delay_us(200);
    }

    if (samples == 0) return ESP_ERR_INVALID_STATE;
    *out_rms = sqrt((float)(sum_squares / samples));

    return ESP_OK;
}

esp_err_t acs712_check_protection(acs712_handle_t *handle, float current_rms) {
    if (!handle) return ESP_ERR_INVALID_ARG;

    if (!handle->relay_state && current_rms >= handle->overcurrent_limit_a) {
        handle->relay_state = true;
        gpio_set_level(handle->relay_gpio, 1);
        ESP_LOGW(TAG, "СПРАЦЮВАВ ЗАХИСТ: Струм %.2f A перевищив поріг %.2f A", current_rms, handle->overcurrent_limit_a);
    } else if (handle->relay_state && current_rms < (handle->overcurrent_limit_a - handle->hysteresis_a)) {
        handle->relay_state = false;
        gpio_set_level(handle->relay_gpio, 0);
        ESP_LOGI(TAG, "ВІДНОВЛЕННЯ ЖИВЛЕННЯ: Струм %.2f A впав нижче порогу з гістерезисом", current_rms);
    }

    return ESP_OK;
}
