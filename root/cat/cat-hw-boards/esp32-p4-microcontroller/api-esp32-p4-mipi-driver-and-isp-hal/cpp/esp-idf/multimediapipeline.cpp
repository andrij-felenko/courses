#include <cstdio>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_ppa.h"

static const char *TAG = "pipeline_cpp";

class MultimediaPipeline {
private:
    SemaphoreHandle_t csi_sem_ = nullptr;
    SemaphoreHandle_t ppa_sem_ = nullptr;
    SemaphoreHandle_t vsync_sem_ = nullptr;
    ppa_client_handle_t ppa_client_ = nullptr;

public:
    MultimediaPipeline() {
        csi_sem_ = xSemaphoreCreateBinary();
        ppa_sem_ = xSemaphoreCreateBinary();
        vsync_sem_ = xSemaphoreCreateBinary();
    }

    esp_err_t run_cycle(TickType_t timeout_ticks) {
        if (xSemaphoreTake(csi_sem_, timeout_ticks) != pdTRUE) {
            ESP_LOGW(TAG, "Помилка: таймаут камери");
            return ESP_ERR_TIMEOUT;
        }

        esp_err_t ret = esp_ppa_do_srm(ppa_client_, nullptr);
        if (ret != ESP_OK) {
            ESP_LOGE(TAG, "Критична помилка PPA: %s", esp_err_to_name(ret));
            return ret;
        }

        if (xSemaphoreTake(ppa_sem_, timeout_ticks) != pdTRUE) {
            ESP_LOGE(TAG, "Помилка: таймаут DMA PPA");
            return ESP_ERR_TIMEOUT;
        }

        if (xSemaphoreTake(vsync_sem_, timeout_ticks) == pdTRUE) {
            ESP_LOGI(TAG, "Успішна синхронізація кадру VSYNC");
        }
        return ESP_OK;
    }
};
