#include <stdio.h>
#include "esp_ppa.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static const char *TAG = "ppa_pipeline";

// Зворотний виклик завершення транзакції PPA з переривання
static bool IRAM_ATTR ppa_trans_done_cb(ppa_client_handle_t ppa_client, const ppa_event_data_t *event_data, void *user_ctx) {
    BaseType_t high_task_awoken = pdFALSE;
    SemaphoreHandle_t sem = (SemaphoreHandle_t)user_ctx;
    xSemaphoreGiveFromISR(sem, &high_task_awoken);
    return high_task_awoken == pdTRUE;
}

esp_err_t process_frame_with_ppa(ppa_client_handle_t ppa_client, 
                                 void *src_yuv_buf, void *overlay_ui_buf, void *dst_rgb_buf,
                                 SemaphoreHandle_t done_sem) {
    // 1. Конфігурація операції SRM (масштабування та перетворення колірного простору)
    ppa_srm_oper_config_t srm_config = {
        .in = {
            .buffer = src_yuv_buf,
            .pic_w = 1280,
            .pic_h = 720,
            .block_w = 1280,
            .block_h = 720,
            .block_offset_x = 0,
            .block_offset_y = 0,
            .srm_cm = PPA_SRM_COLOR_MODE_YUV420P,
        },
        .out = {
            .buffer = dst_rgb_buf,
            .buffer_size = 800 * 480 * 2,
            .pic_w = 800,
            .pic_h = 480,
            .block_offset_x = 0,
            .block_offset_y = 0,
            .srm_cm = PPA_SRM_COLOR_MODE_RGB565,
        },
        .rotation = PPA_SRM_ROT_ANGLE_0,
        .scale_x = 800.0f / 1280.0f,
        .scale_y = 480.0f / 720.0f,
        .mode = PPA_TRANS_MODE_NON_BLOCKING,
    };

    // 2. Реєстрація callback події
    ppa_event_callbacks_t cbs = {
        .on_trans_done = ppa_trans_done_cb,
    };
    ESP_ERROR_CHECK(esp_ppa_register_event_callbacks(ppa_client, &cbs, done_sem));

    // 3. Запуск асинхронного масштабування через DMA
    esp_err_t ret = esp_ppa_do_srm(ppa_client, &srm_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запуску PPA SRM: %s", esp_err_to_name(ret));
        return ret;
    }

    return ESP_OK;
}
