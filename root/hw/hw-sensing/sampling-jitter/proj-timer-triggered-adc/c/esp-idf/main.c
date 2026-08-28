/*
 * Реалізація для ESP-IDF (ESP32)
 * Неперервне зчитування ADC Continuous Driver через DMA + Hardware Timer
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_continuous.h"
#include "esp_log.h"

#define EXAMPLE_READ_LEN    1024
#define SAMPLE_FREQ_HZ      100000  /* 100 кГц апаратний тактовий запуск */

static const char *TAG = "ADC_TIMER_DMA";
static adc_continuous_handle_t s_adc_handle = NULL;

static bool IRAM_ATTR s_conv_done_cb(adc_continuous_handle_t handle, 
                                     const adc_continuous_evt_data_t *edata, 
                                     void *user_data) {
    BaseType_t must_yield = pdFALSE;
    TaskHandle_t task_to_notify = (TaskHandle_t)user_data;
    vTaskNotifyGiveFromISR(task_to_notify, &must_yield);
    return (must_yield == pdTRUE);
}

void app_main(void) {
    TaskHandle_t main_task = xTaskGetCurrentTaskHandle();

    /* 1. Конфігурація неперервного драйвера АЦП на базі апаратного таймера/I2S-DMA */
    adc_continuous_handle_cfg_t adc_config = {
        .max_store_buf_size = 4096,
        .conv_frame_size = EXAMPLE_READ_LEN,
    };
    ESP_ERROR_CHECK(adc_continuous_new_handle(&adc_config, &s_adc_handle));

    /* 2. Налаштування шаблону сканування та апаратної частоти вибірки */
    adc_continuous_config_t dig_cfg = {
        .sample_freq_hz = SAMPLE_FREQ_HZ,
        .conv_mode = ADC_CONV_SINGLE_UNIT_1,
        .format = ADC_DIGI_OUTPUT_FORMAT_TYPE1,
    };

    adc_digi_pattern_config_t adc_pattern = {
        .atten = ADC_ATTEN_DB_12,
        .channel = ADC_CHANNEL_0,
        .unit = ADC_UNIT_1,
        .bit_width = ADC_BITWIDTH_12,
    };
    dig_cfg.pattern_num = 1;
    dig_cfg.adc_pattern = &adc_pattern;
    ESP_ERROR_CHECK(adc_continuous_config(s_adc_handle, &dig_cfg));

    /* 3. Реєстрація ISR колбеку завершення кадру DMA */
    adc_continuous_evt_cbs_t cbs = {
        .on_conv_done = s_conv_done_cb,
    };
    ESP_ERROR_CHECK(adc_continuous_register_event_callbacks(s_adc_handle, &cbs, (void*)main_task));

    /* 4. Апаратний старт перетворень */
    ESP_ERROR_CHECK(adc_continuous_start(s_adc_handle));
    ESP_LOGI(TAG, "ADC hardware DMA acquisition started at %d Hz", SAMPLE_FREQ_HZ);

    uint8_t result_bytes[EXAMPLE_READ_LEN];
    uint32_t ret_num = 0;

    while (1) {
        /* Чекаємо апаратного сповіщення від DMA ISR без навантаження CPU */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        esp_err_t ret = adc_continuous_read(s_adc_handle, result_bytes, EXAMPLE_READ_LEN, &ret_num, 0);
        if (ret == ESP_OK) {
            /* Опрацювання готового блоку відліків у фоновому потоці */
        }
    }
}
