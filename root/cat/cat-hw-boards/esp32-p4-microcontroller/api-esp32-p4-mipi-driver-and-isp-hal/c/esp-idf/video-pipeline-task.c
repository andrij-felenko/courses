#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_ppa.h"
#include "esp_lcd_mipi_dsi.h"

static const char *TAG = "pipeline_sync";

typedef struct {
    SemaphoreHandle_t sem_csi_eof;
    SemaphoreHandle_t sem_ppa_done;
    SemaphoreHandle_t sem_vsync;
    ppa_client_handle_t ppa_client;
    esp_lcd_panel_handle_t dpi_panel;
} pipeline_ctx_t;

// Задача управління відеоконвеєром
void video_pipeline_task(void *pvParameters) {
    pipeline_ctx_t *ctx = (pipeline_ctx_t *)pvParameters;
    esp_err_t err;

    while (1) {
        // 1. Очікування завершення захоплення кадру з камери (EOF)
        if (xSemaphoreTake(ctx->sem_csi_eof, pdMS_TO_TICKS(100)) != pdTRUE) {
            ESP_LOGW(TAG, "Таймаут очікування кадру з камери (CSI EOF)");
            continue;
        }

        // 2. Запуск асинхронного масштабування та блендингу PPA
        err = esp_ppa_do_srm(ctx->ppa_client, NULL); // Використовуємо попередньо налаштований SRM
        if (err != ESP_OK) {
            if (err == ESP_ERR_INVALID_STATE) {
                ESP_LOGE(TAG, "PPA зайнятий попередньою транзакцією");
            } else {
                ESP_LOGE(TAG, "Збій PPA: %s", esp_err_to_name(err));
            }
            continue;
        }

        // 3. Очікування завершення PPA
        if (xSemaphoreTake(ctx->sem_ppa_done, pdMS_TO_TICKS(50)) != pdTRUE) {
            ESP_LOGE(TAG, "Таймаут обробки PPA DMA");
            continue;
        }

        // 4. Очікування фази кадрового гасіння VSYNC для безпечного переключення буфера
        if (xSemaphoreTake(ctx->sem_vsync, pdMS_TO_TICKS(50)) == pdTRUE) {
            // Безпечна зміна покажчиків кадрового буфера дисплея без розривів
            ESP_LOGD(TAG, "Кадр успішно оновлено під час VSYNC");
        }
    }
}
