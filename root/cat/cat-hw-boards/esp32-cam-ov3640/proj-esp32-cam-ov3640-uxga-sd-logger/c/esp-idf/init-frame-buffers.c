#include "esp_heap_caps.h"
#include "esp_log.h"

static const char *TAG = "CAM_MEM";

// Передвиділені покажчики на кадрові буфери
static uint8_t *s_dma_buffer = NULL;
static uint8_t *s_psram_buffer = NULL;

#define DMA_BUF_SIZE   (32 * 1024)   // 32 КБ для дескрипторів DMA у DRAM
#define PSRAM_BUF_SIZE (512 * 1024)  // 512 КБ під UXGA кадр у PSRAM

esp_err_t init_frame_buffers(void) {
    // Виділення DMA-буфера у внутрішній оперативній пам'яті DRAM
    s_dma_buffer = (uint8_t *)heap_caps_malloc(DMA_BUF_SIZE, MALLOC_CAP_DMA | MALLOC_CAP_INTERNAL);
    if (s_dma_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити DRAM буфер для DMA");
        return ESP_ERR_NO_MEM;
    }

    // Виділення великого кадрового буфера у зовнішній пам'яті PSRAM
    s_psram_buffer = (uint8_t *)heap_caps_malloc(PSRAM_BUF_SIZE, MALLOC_CAP_SPIRAM);
    if (s_psram_buffer == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити PSRAM буфер");
        heap_caps_free(s_dma_buffer);
        s_dma_buffer = NULL;
        return ESP_ERR_NO_MEM;
    }

    ESP_LOGI(TAG, "Буфери успішно передвиділені без ризику фрагментації");
    return ESP_OK;
}
